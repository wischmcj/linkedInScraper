
import os
import time 
import logging
import json
from urllib.parse import quote 

import dlt
import duckdb
import redis

from pipeline.gql_utils import build_gql_url, get_gql_data, param_to_str
from voyager_client import CustomAuth
from more_itertools import chunked

logger = logging.getLogger(__name__)

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig
from dlt.sources.helpers.requests import Request

from urllib.request import Request
from dlt.sources.helpers.rest_client.paginators import RangePaginator

from dlt.common import jsonpath
from urllib.parse import quote

from pipeline.data.saved_queries import (
    db_followed_companies,
    get_finished_jobs,
    identified_jobs,
    delete_not_followed_company_jobs,
    get_jobs_filtered,
    db_job_urls
)

from pipeline.endpoint_conf import (
    API_BASE_URL,
      graphql_pagignator_config,
      endpoints,
      total_paths,
      data_selectors,
      mapppings
)

auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"), use_cookie_cache=False)
auth.authenticate()

def avoid_ban(sleepy_time=2):
    time.sleep(sleepy_time)

def get_filters():
    return "resultType->PEOPLE"

# Paginator Class

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

# Data Processing Functions

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

# Resource Creation Functions

def get_company_resource(company_data):
    @dlt.resource
    def followed_companies():
        if isinstance(company_data, list):
            yield company_data
        else:
            yield [company_data]
    return followed_companies

def get_job_url_resource(job_urls):
    @dlt.resource
    def job_urls():
        if isinstance(job_urls, list):
            yield job_urls
        else:
            yield [job_urls]
    return job_urls

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
    # if source_name == 'jobs_by_company':
    #     finished_jobs = get_finished_jobs()
    #     resource_config['processing_steps'].append({
    #         'filter': lambda x: x['job_id'] not in finished_jobs
    #     })
    return resource_config

@dlt.source
def linkedin_source(session,
                    db_name, 
                    get_companies=False,
                    get_job_urls=False,
                    get_descriptions=True,
                    company_data=None,
                    job_urls=None):
    """
    This function is used to create a source matching the parameters passed.

    Can pull:
        i. Companies followed by the configured profile
        ii. Job posting urls for all posted jobs 
            - For either all followed companies or a list provided via company_data
        iii. Job description data for all job postings 
            - For either all jobs returned in 'ii' or for a list provided via job_urls
    """
    resources = []

    # Create followed_companies resource
    if get_companies:  
        followed_companies = graphql_source('followed_companies')
        followed_companies['processing_steps'].append({'map': get_company_id})
    else:
        company_data = company_data or db_followed_companies(db_name)
        logger.info(f"Creating resource using companies from db: {company_data}")
        followed_companies = get_company_resource(company_data)

    # Create job_urls resource if needed
    if get_job_urls:
        # If we dont need to get descriptions, then the resource isnt needed
        jobs_by_company = graphql_source('jobs_by_company')
        jobs_by_company['processing_steps'].append({'map': encode_job_urn})
        resources.append(jobs_by_company)
    else:
        if get_descriptions:
            # If we dont need to get descriptions, then the resource isnt needed
            job_urls = job_urls or db_job_urls(db_name)
            job_urls = get_job_url_resource(job_urls)
            logger.info(f"Creating resource using job urls from db: {job_urls}")
  
            
    # Create job_description resource if needed
    if get_descriptions:
        job_description = linkedin_source('job_description')
        ## Below sets to pull only one page of jobs per company for testing
        # job_description['endpoint']['paginator'].maximum_value = 1 
        resources.append(job_description)

    resources.append(followed_companies)
    config: RESTAPIConfig = {
        "client": {        
            "base_url": f'{API_BASE_URL}',        
            "session": session,    
            },    
            "resource_defaults": {        
                "write_disposition": "merge"    
            },    
            "resources": resources,
        }
    resource_list = rest_api_resources(config)
    return resource_list

def run_pipeline(db_name,
                 one_at_a_time=False,
                 **kwargs):
    """
        Defines the pipeline and runs it incrementally or all at once
    """
    db = duckdb.connect(db_name) 
    pipeline = dlt.pipeline(
            pipeline_name='linkedin',
            dataset_name='linkedin_data',
            schema_file='pipeline/configuration/',
            dev_mode=False
            )
    if one_at_a_time:
        companies_from_db = db_followed_companies(db_name)
        # Allows for saving of data to db regularly
        for cid, company_details in enumerate(companies_from_db):
            li_source = linkedin_source(auth.session, db_name, company_data=dict(company_details), **kwargs)
            logger.info(f"Running pipeline for company: {company_details}")
            res = pipeline.run(li_source)
    else:
        li_source = linkedin_source(auth.session, db_name, **kwargs)
        res = pipeline.run(li_source)
    
    breakpoint()

if __name__ == "__main__":
    db_name = "linkedin.duckdb"
    # db = duckdb.connect(db_name) 
    # followed_companies = db.sql("select * from linkedin_data.followed_companies" )
    # res = get_followed_companies(db_name)
    # new_followed_companies = db.sql("select * from linkedin_data.followed_companies" )
    # breakpoint()
    run_pipeline(db_name,
                one_at_a_time=False,
                get_companies=True,
                get_job_urls=True,
                get_descriptions=False)
