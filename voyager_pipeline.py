
import os
import time 
import logging
import json
from urllib.parse import quote 

import dlt
import duckdb
import redis

from conf import (
    API_BASE_URL, BATCH_SIZE, REQUEST_HEADERS,
      AUTH_BASE_URL, AUTH_REQUEST_HEADERS, SEARCH_LIMIT,
      graphql_pagignator_config,
      endpoints,
      total_paths,
      default_variables,
      data_selectors
)

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



auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
auth.authenticate()
def avoid_ban():
    time.sleep(4)


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
        avoid_ban()

def graphql_source(source_name):
    endpoint = endpoints[source_name]
    query = endpoint['query']
    path = endpoint['path']
    include_from_parent = endpoint.get('include_from_parent',None)
    # query['variables'].update(default_variables)
    # query['variables']['count'] = BATCH_SIZE
    # query['variables']['start'] = '$start'

    paginator_config = graphql_pagignator_config
    paginator_config['total_path'] = total_paths[source_name]
    
    resource_config = {
        'name': source_name,
        "max_table_nesting": 1,
        'endpoint': {
            'path': path,
            'json': query,
            'paginator': LinkedInPaginator(**paginator_config),
            'data_selector': data_selectors[source_name]
        },
        'processing_steps': [
            {
                'map': get_id
            }
        ],
    }
    if include_from_parent:
        resource_config['include_from_parent'] = include_from_parent
    return resource_config

def get_id(response):
    response['company_id'] = response.get('entityUrn','test:test').split(':')[-1]
    return response

@dlt.source
def linkedin_source(session):
    from conf import followed_companies_profile_component, query_id, paged_list_component
    followed_companies = graphql_source('followed_companies')
    jobs_by_company = graphql_source('jobs_by_company')
    
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
                followed_companies,    
                jobs_by_company,
                # graphql_source('profile_experiences'),
                # graphql_source('job_search_history'),
                # graphql_source('job_listings'),
            ],
        }
    resource_list = rest_api_resources(config)
    return resource_list
                       

def run_pipeline():
    # breakpoint()
    pipeline = dlt.pipeline(
        pipeline_name='linkedin',
        # destination=dlt.destinations.duckdb(db),
        dataset_name='linkedin_data',
        dev_mode=False
        )
    logger.info(f"Authenticating with LinkedIn")
    # auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
    # auth.authenticate()
    avoid_ban()
    # url = "https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(count:20,start:0,jobSearchType:CLASSIC)&queryId=voyagerJobsDashJobSearchHistories.220d01e7d55ec8363130acffb73298ff"
    li_source = linkedin_source(auth.session)

    res = pipeline.run(li_source)
    
    breakpoint()

if __name__ == "__main__":
    run_pipeline()
    breakpoint()