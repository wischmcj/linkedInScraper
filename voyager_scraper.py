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
            sub_param_values.append(f'{k}{eq}List({",".join(v)})')
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
if __name__ == "__main__":
    

    r_conn.flushall()
    auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
    auth.authenticate()
    # test_auth = auth.session.get("https://www.linkedin.com/in/collin-wischmeyer-b55659a4/")
