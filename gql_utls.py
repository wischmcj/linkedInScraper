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

from conf import API_BASE_URL, REQUEST_HEADERS, AUTH_BASE_URL, AUTH_REQUEST_HEADERS 

from voyager_client import CustomAuth
from string import Template
logger = logging.getLogger(__name__)


def default_evade():
    time.sleep(20)

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

if __name__ == "__main__":
    

    r_conn.flushall()
    auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
    auth.authenticate()
    # test_auth = auth.session.get("https://www.linkedin.com/in/collin-wischmeyer-b55659a4/")
