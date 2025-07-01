import itertools
import os
import time 
import logging
import dlt
import json 

from dlt.sources.rest_api import RESTClient
from dlt.sources.helpers.rest_client.auth import HttpBasicAuth
import duckdb
import redis
# from graphql_query import Argument, Directive, Field, Operation, Query, Variable
from conf import API_BASE_URL, REQUEST_HEADERS, AUTH_BASE_URL, AUTH_REQUEST_HEADERS 
import urllib.parse as parse

from string import Template
logger = logging.getLogger(__name__)

def parse_gql_url(url:str):
    # url = 'https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(jobPostingDetailDescription_start:0,jobPostingDetailDescription_count:5,jobCardPrefetchQuery:(jobUseCase:JOB_DETAILS,prefetchJobPostingCardUrns:List(urn%3Ali%3Afsd_jobPostingCard%3A%284209649973%2CJOB_DETAILS%29)),count:5),jobDetailsContext:(isJobSearch:true))&queryId=voyagerJobsDashJobCards.d03169007e6d93bc819401ca11ca138a'
    # breakpoint()
    parsed = parse.urlparse(url)
    urllib_query = parse.parse_qs(parsed.query)
    
    def split_key_from_var(as_str:str):
        return (as_str.split(':')[0],':'.join(as_str.split(':')[1:]))

    variables = urllib_query.pop('variables')[0].split(',')
    variables = dict([split_key_from_var(v) for v in variables])

    addnl_params = {param:(vals[0]if len(vals)==1 else vals) for param,vals in urllib_query.items()}
    addnl_params['variables'] = variables
    return addnl_params

# def build_gql_query():
#     query = Query(name="__schema", fields=["types"])
#     operation = Operation(type="query", queries=[query])
    
#     print(operation.render())
# test = "query {\n  __schema {\n    types {\n      name\n    }\n  }\n}"

def param_to_str(params:dict,depth=0):
    sub_param_values = []
    if depth==0:
        sep = '&'
        eq = '='
    else:
        sep = ','
        eq = ':'
    depth+=1
    for k,v in params.items():
        if isinstance(v,list):
            sub_param_values.append(f'{k}{eq}List({",".join([str(item) for item in v])})')
        elif isinstance(v,dict):
            sub_param_values.append(f'{k}{eq}({param_to_str(v,depth=depth+1)})')
        else:
            sub_param_values.append(f'{k}{eq}{v}')
    sub_param_values = f'{sep}'.join(sub_param_values)
    return f'{sub_param_values}'


def build_gql_url(params: dict,base_url=None, endpoint='graphql'):
    if not base_url:
        base_url = f'{API_BASE_URL}'
    endpoint_url = f'{base_url}/{endpoint}'

    params_str = param_to_str(params)
    url_no_start = f'{endpoint_url}?{params_str}'
    url_template = Template(url_no_start)
    return url_template


def nested_get(data:dict, keys:list[str,list]):
    if len(keys)==0:
        return data
    if isinstance(data, list):
        data = [nested_get(item, keys) for item in data]
    else:
        for key in keys:
            if isinstance(key, list):
                data = nested_get(data, key)
            elif isinstance(key, int):
                data = data[key]
            else:
                data = data.get(key,{})
    return data

    

def get_gql_data(response_json:dict, paths:list, data_keys:str):
    elements = nested_get(response_json,paths[0])
    # Extract company info   
    for path in paths[1:]:
        # breakpoint()
        # each nested_get call returns a list of elements
        # if params are delivered properly
        elements = [nested_get(ele,path) for ele in elements]
    if len(elements)==0:
        breakpoint()
        logger.error(f"No elements found for {paths}, {response_json}")
        return [], 0
        # raise Exception("No elements found")
    if isinstance(elements[0], list):
        elements = itertools.chain.from_iterable(elements)
    to_return = []
    for element_detail in elements:
        data = {}
        for key in data_keys:
            if isinstance(key, list):
                data[':'.join([str(x) for x in key])] = nested_get(element_detail,key)
            else:
                data[key] = element_detail.get(key)
        to_return.append(data)
    return to_return, len(to_return)

def get_gql_schema(response:dict):
    if isinstance(response, list):
        from itertools import chain
        to_return = [get_gql_schema(resp) for resp in response]
        parsed_types, dist_types, keys  = zip(*to_return)
        parsed_types = list(chain.from_iterable(parsed_types))
        dist_types = list(chain.from_iterable(dist_types))
        keys = list(chain.from_iterable(keys))
        return parsed_types, dist_types, keys
    
    type_detail = response['microSchema']['types']

    keys = [k for k, v  in type_detail.items()]
    base_types = [v.get('baseType') for k, v  in type_detail.items() ]

    from itertools import chain
    field_types = list(chain.from_iterable([[ftype.get('type') for field, ftype in v.get('fields',{}).items()] for k, v  in type_detail.items() ]))
    
    types= []
    def process_type(field_type):   
        if isinstance(field_type,dict):
            if field_type.get('array'):
                process_type(field_type.get('array'))
            if field_type.get('union'):
                for ufield, ufield_type in field_type.get('union').items():
                    process_type(ufield_type)
        else:
            types.append(field_type)
    for ftype in field_types:
        process_type(ftype)
        
    dist_types = set(types)
    parsed_types = []
    for ftype in dist_types:
        if ftype in keys:
            parsed_types.append(type_detail.get(ftype, {}).get('baseType'))
        else:
            parsed_types.append(ftype)
    return parsed_types, dist_types, keys

def compare_schemata():
    with open('gql/my_jobs_page_schema.json','r') as f:
        response = json.load(f)
    jobs_parsed_types, jobs_dist_types, jobs_keys = get_gql_schema(response)

    with open('gql/schema.json','r') as f:
        response = json.load(f)
    profile_parsed_types, profile_dist_types, profile_keys = get_gql_schema(response)

    jobs_not_profile = set(jobs_dist_types) - set(profile_dist_types)
    profile_not_jobs = set(profile_dist_types) - set(jobs_dist_types)
    breakpoint()

if __name__ == "__main__":
    breakpoint()
    
    