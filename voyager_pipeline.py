
import os
import time 
import logging
import json
from urllib.parse import quote 

import dlt
import duckdb
import redis

from conf import API_BASE_URL, BATCH_SIZE, REQUEST_HEADERS, AUTH_BASE_URL, AUTH_REQUEST_HEADERS, SEARCH_LIMIT

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



def avoid_ban():
    time.sleep(4)


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
        # breakpoint()

    def update_state(self, response, data):
        super().update_state(response, data)
        # breakpoint()

    
@dlt.source
def linkedin_source(session):
    from conf import followed_companies_profile_component, query_id, paged_list_component
    config: RESTAPIConfig = {
        "client": {
            "base_url": f'{API_BASE_URL}',
            "session": session,
        },
        "resource_defaults": {
            "write_disposition": "merge"
        },
        "resources": [
            {
                "name": "followed_companies",
                "max_table_nesting": 1,
                'endpoint': {
                    'path': 'graphql',
                    'json': {
                        "variables":{
                            "pagedListComponent": quote(paged_list_component),
                            "paginationToken":'null',
                            "start":'$start',
                            "count": BATCH_SIZE
                        },
                        "queryId":query_id
                    },
                    'paginator': LinkedInPaginator(
                                    param_name='start',
                                    initial_value=0,
                                    value_step=BATCH_SIZE,
                                    maximum_value=100,
                                    base_index=0,
                                    total_path='data.identityDashProfileComponentsByPagedListComponent.paging.total',
                                    error_message_items="errors"),
                    'data_selector': 'data.identityDashProfileComponentsByPagedListComponent.elements',
                },
            }
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
    auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
    auth.authenticate()
    avoid_ban()

    li_source = linkedin_source(auth.session)

    res = pipeline.run(li_source)
    
    breakpoint()
    res = pipeline.run(get_followed_company_info(auth, max_iters=2))
    res = pipeline.run(get_jobs(auth,company_ids=['3998']))
    # res = pipeline.run(get_job_description(auth, 
    #                                        job_urn="urn:li:fsd_jobPosting:4231156986", 
    #                                        cardSectionTypes=["JOB_DESCRIPTION_CARD", "SALARY_CARD"]))
    
    # breakpoint()

    breakpoint()
    get_job_description(auth, 
                        job_urn="urn:li:fsd_jobPosting:4231156986", 
                        cardSectionTypes=["JOB_DESCRIPTION_CARD", "SALARY_CARD"])
    breakpoint()
    # test = db.sql("select distinct column_name from information_schema.columns where table_name = 'jobs'")
    # test = db.sql("select * from linkedin_data.jobs")
    # test = db.sql("select distinct company_id from linkedin_data.followed_company_info")
    # test = db.sql("DESCRIBE;")

if __name__ == "__main__":
    # get_followed_company_info()
    # run_pipeline()
    import urllib.parse as parse
    url = 'https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(jobPostingDetailDescription_start:0,jobPostingDetailDescription_count:5,jobCardPrefetchQuery:(jobUseCase:JOB_DETAILS,prefetchJobPostingCardUrns:List(urn%3Ali%3Afsd_jobPostingCard%3A%284209649973%2CJOB_DETAILS%29)),count:5),jobDetailsContext:(isJobSearch:true))&queryId=voyagerJobsDashJobCards.d03169007e6d93bc819401ca11ca138a'
    breakpoint()
    parsed = parse.urlparse(url)
    urllib_query = parse.parse_qs(parsed.query)
    
    def split_key_from_var(as_str:str):
        return (as_str.split(':')[0],':'.join(as_str.split(':')[1:]))

    variables = urllib_query.pop('variables')[0].split(',')
    variables = dict([split_key_from_var(v) for v in variables])

    addnl_params = {param:(vals[0]if len(vals)==1 else vals) for param,vals in urllib_query.items()}

    [v.split(':')[-1] for v in variables]
    breakpoint()


    breakpoint()
    # url = f'{base_url}/jobs/jobPostings/{job_urn.split(":")[-1]}?'
    # res = session.get(url)
    # res_json = json.loads(res.content)