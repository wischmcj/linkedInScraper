
import os
import time 
import logging
import json
from urllib.parse import quote 

import dlt
import duckdb
import redis

from gql_utils import build_gql_url, get_gql_data, param_to_str
from voyager_client import CustomAuth
from more_itertools import chunked

logger = logging.getLogger(__name__)

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig
from dlt.sources.helpers.rest_client.paginators import SinglePagePaginator
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.auth import HttpBasicAuth
from dlt.sources.helpers.requests import Response, Request

from urllib.request import Request
from dlt.sources.helpers.rest_client.paginators import RangePaginator

from dlt.common import jsonpath
from urllib.parse import quote

from data.saved_queries import (
    db_followed_companies,
    get_finished_jobs,
    identified_jobs,
    delete_not_followed_company_jobs,
    get_jobs_filtered,
    get_data_jobs,
    get_software_jobs
)

from conf import (
    API_BASE_URL, BATCH_SIZE, REQUEST_HEADERS,
      AUTH_BASE_URL, AUTH_REQUEST_HEADERS, SEARCH_LIMIT,
      graphql_pagignator_config,
      endpoints,
      total_paths,
      default_variables,
      data_selectors,
      mapppings,
      followed_companies_test_data
)

auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
auth.authenticate()
def avoid_ban(sleepy_time=2):
    time.sleep(sleepy_time)

def get_filters():
    return "resultType->PEOPLE"

class LinkedInPaginator(RangePaginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_template = None

    def encode_params(self, request):
        params = request.json
        request.json = None
        endpoint = request.url.split('/')[-1]
        base_url = request.url.replace(f'/{endpoint}', '')
        # breakpoint()
        self.url_template = build_gql_url(params,base_url,endpoint)

    def init_request(self, request: Request) -> None:
        """Generates a rest_li encoded url template based off of 
            the inputs passed via the requests json
        """
        self._has_next_page = True
        self.current_value = self.initial_value
        self.encode_params(request)
        self.update_request(request)

    def update_request(self, request: Request) -> None:
        request.url = self.url_template.substitute(**{self.param_name:self.current_value})
        print(request.url)

    def update_state(self, response, data):
        super().update_state(response, data)
        # with open('response.json','w') as f:
        #     json.dump(response.json(),f)
        avoid_ban()

def get_company_id(response):
    response['company_id'] = response.get('entityUrn','test:test').split(':')[-1]
    return response

def encode_job_urn(response):
    response['job_urn_encoded'] = quote(response.get('jobPostingUrn'))
    return response

def get_json_map(key):
    def json_map(response):
        return jsonpath.find_values(key,response)
    return json_map


def get_map_func(endpoint):
    mapping = mapppings.get(endpoint,{})
    def map_cols(response ,*args,**kwargs):
        try:
            for key, value in mapping:
                map_func = get_json_map(value)
                response[key] = map_func(response)
                if isinstance(response[key],list) and len(response[key])==1:
                    response[key] = response[key][0]
        except Exception as e:
            breakpoint()
        return response
    return map_cols

def graphql_source(source_name):
    endpoint = endpoints[source_name]
    query = endpoint['query']
    path = endpoint['path']
    include_from_parent = endpoint.get('include_from_parent',None)

    paginator_config = graphql_pagignator_config
    paginator_config['total_path'] = total_paths[source_name]

    
    resource_config = {
        'name': source_name,
        "max_table_nesting": 0,
        'endpoint': {
            'path': path,
            'json': query,
            'paginator': LinkedInPaginator(**paginator_config),
            'data_selector': data_selectors[source_name]
        },
        'processing_steps': [
            {
                'map': get_map_func(source_name)
            }
        ],
    }
    if include_from_parent:
        resource_config['include_from_parent'] = include_from_parent
    if source_name == 'jobs_by_company':
        finished_jobs = get_finished_jobs()
        resource_config['processing_steps'].append({
            'filter': lambda x: x['job_id'] not in finished_jobs
        })
    return resource_config

def get_single_company_resource(company_data):
    @dlt.resource
    def followed_companies():
        yield [company_data]
    return followed_companies

@dlt.source
def linkedin_source(session,
                        company_data=None):
    
    jobs_by_company = graphql_source('jobs_by_company')
    jobs_by_company['processing_steps'].append({'map': encode_job_urn})
    job_description = graphql_source('job_description')
    job_description['endpoint']['paginator'].maximum_value = 1

    if company_data is None:  
        followed_companies = graphql_source('followed_companies')
        followed_companies['processing_steps'].append({'map': get_company_id})
    else:
        followed_companies = get_single_company_resource(company_data)
    
    # breakpoint()
    config: RESTAPIConfig = {
        "client": {        
            "base_url": f'{API_BASE_URL}',        
            "session": session,    
            },    
            "resource_defaults": {        
                "write_disposition": "merge"    
            },    
            "resources": [    
                #'https://www.linkedin.com/voyager/api/graphql?variables=(pagedListComponent:urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29,paginationToken:null,start:0,count:25)&queryId=voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'    
                jobs_by_company,
                job_description,
                followed_companies,  
            ],
        }
    resource_list = rest_api_resources(config)
    return resource_list
                       

def run_pipeline(one_at_a_time=False):
    db = duckdb.connect("linkedin.duckdb") 
    pipeline = dlt.pipeline(
        pipeline_name='linkedin',
        dataset_name='linkedin_data',
        dev_mode=False
        )
    if one_at_a_time:
        companies = db_followed_companies()
        for cid, company_details in companies.iterrows():
            li_source = linkedin_source(auth.session, dict(company_details))
            res = pipeline.run(li_source)
    else:
        li_source = linkedin_source(auth.session)
        res = pipeline.run(li_source)
    
    breakpoint()

if __name__ == "__main__":
    run_pipeline()