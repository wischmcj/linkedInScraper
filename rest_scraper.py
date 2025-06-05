
import os
import time 
import logging
import json 

import dlt
import duckdb
import redis

from conf import API_BASE_URL, REQUEST_HEADERS, AUTH_BASE_URL, AUTH_REQUEST_HEADERS 

from gql_utls import build_gql_url, get_gql_data
from voyager_client import CustomAuth
from more_itertools import chunked

logger = logging.getLogger(__name__)


def default_evade():
    time.sleep(5)

@dlt.resource(
        name = 'followed_company_info',
        columns={"url": {"data_type": "string"},
                 "name": {"data_type": "string"},
                 "company_id": {"data_type": "string"},
                 "entity_urn": {"data_type": "string"}},
        primary_key="company_id",
        write_disposition="merge"
)
def get_followed_company_info(auth, start = 0, batch=30, max_iters = 10):
    session = auth.session

    reached_end=False
    query_id = 'voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'
    paged_list_component = 'urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29'
    params = {
        "variables":{
            "pagedListComponent":paged_list_component,
            "paginationToken":'null',
            "start":'$start',
            "count":batch
        },
        "queryId":query_id
    }
    url_template = build_gql_url(params)

    
    paths = [['data','identityDashProfileComponentsByPagedListComponent','elements'],
                ['components','entityComponent','titleV2','text','attributesV2'],
                ['detailData','companyName']]
    data_keys = ['name','entityUrn','url']
    batch_num=0
    to_return =[]
    while not reached_end:
        url = url_template.substitute(start=start)
        res = session.get(url)
        print(res)
        res_json = json.loads(res.content)
        batch_data, returned_batch_size = get_gql_data(res_json, paths, data_keys)
        if returned_batch_size==0:
            logger.info(f"No company data returned")
            reached_end =True
        else:
            for company in batch_data: company['company_id'] = company['entityUrn'].split(':')[-1]
            to_return.extend(batch_data)
            yield batch_data
            if batch_num>=max_iters:
                logger.info(f"Reached max iterations")
                reached_end =True
            else:
                start+=batch
                batch_num+=1
        # Avoid rate limiting
        default_evade()

@dlt.resource(
        name = 'jobs',
        # columns={"jobPostingUrn": {"data_type": "string"},
        #          "jobPostingTitle": {"data_type": "string"},
        #          "job_id": {"data_type": "string"},
        #          "company_id": {"data_type": "string"},
        #          "entity_urn": {"data_type": "string"}},
        primary_key="job_id",
        # write_disposition="merge"
)
def get_jobs(auth, company_ids:list, start = 0, batch=30, max_iters = None, save_resp=False):
    session = auth.session
    # if not base_url:
    base_url = f'{API_BASE_URL}'
    endpoint = 'voyagerJobsDashJobCards'
    # first call
    #  https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87&count=30&q=jobSearch&query=(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:(company:List([3200474])),                                                                                                    spellCorrectionEnabled:true)&servedEventEnabled=False&start=0'    
    #  https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87&count=7&q=jobSearch&query=(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:(company:List(1371,332373,15079031,2536160,2478301,900243,48732,276625,2522926),originToLandingJobPostings:List($company_id)),spellCorrectionEnabled:true)&servedEventEnabled=false&start=0
    # next page call
    # https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-219&count=25&q=jobSearch&query=(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:(company:List(1371,332373,15079031,2536160,2478301,900243,48732,276625,2522926),originToLandingJobPostings:List(4233122195,4241015234,4234495017,4224558509,4219661251,4234767155,4236889304,4242819782,4219660453)),spellCorrectionEnabled:true)&start=75
    # Maybe a call to cache?
    # https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(count:20,start:0,jobSearchType:CLASSIC)&queryId=voyagerJobsDashJobSearchHistories.220d01e7d55ec8363130acffb73298ff
    parameters = {
        "decorationId":"com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87",
        # "decorationId":"com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-219"
        "count":f'{batch}',
        "q":"jobSearch",    
        "query": {
            "origin":"COMPANY_PAGE_JOBS_CLUSTER_EXPANSION",
            "locationUnion":{
                "geoId":92000000
            },
            "selectedFilters":{
                # "company":"List(1371,332373,15079031,2536160,2478301,900243,48732,276625,2522926)",
                "company": company_ids,
                # "originToLandingJobPostings":"List(4233122195,4241015234,4234495017,4224558509,4219661251,4234767155,4236889304,4242819782,4219660453)",
            },
            "spellCorrectionEnabled":"true"
        },
        'servedEventEnabled': False,
        'start': '$start'
    }
    url_template = build_gql_url(parameters,base_url,endpoint)

    paths = [['elements'],['jobCardUnion','jobPostingCard']]
    data_keys = ['jobPostingUrn','jobPostingTitle',
                 ['primaryDescription', 'text'],
                 ['secondaryDescription', 'text'],
                 ["jobPosting", "posterId"],
                 ["logo", "attributes", 0, "detailDataUnion","companyLogo"]]

    batch_num=0
    to_return =[]
    reached_end = False
    has_max_iters = max_iters is not None
    while not reached_end:
        url = url_template.substitute(start=start)
        res = session.get(url)
        logger.debug(url)
        logger.info(res)
        res_json = json.loads(res.content)
        batch_data, returned_batch_size = get_gql_data(res_json, paths, data_keys)

        if returned_batch_size==0:
            logger.info(f"No company data returned")
            reached_end =True
        else:
            for job in batch_data:
                try:
                    job['job_id'] = job['jobPostingUrn'].split(':')[-1]
                    job['company_id'] = job['logo:attributes:0:detailDataUnion:companyLogo'].split(':')[-1]
                    job['company_name'] = job['primaryDescription:text']
                    job['subtitle'] = job['secondaryDescription:text']
                except Exception as e:
                    breakpoint()
                    logger.error(f"Error processing job: {e}")
            to_return.extend(batch_data)
            yield batch_data
            if has_max_iters:
                if batch_num>=max_iters:
                    logger.info(f"Reached max iterations")
                    reached_end =True
            else:
                start+=batch
                batch_num+=1
        logger.info(f'{returned_batch_size} jobs returned')
        logger.info(f'{len(set([job["jobPostingUrn"] for job in to_return]))} total jobs found')
        
        # Avoid rate limiting
        default_evade()

    return to_return

def get_job_description(auth, job_id: str):
    """Fetch data for a given LinkedIn job posting.

    :param job_id: LinkedIn job ID
    :type job_id: str

    :return: Job posting data
    :rtype: dict

    """ 
    # https://www.linkedin.com/voyager/api/graphql?variables=(jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A4178609184)&queryId=voyagerTalentbrandDashTargetedContents.8b111cec5d5527ad575591979ba20fb2
    # https://www.linkedin.com/voyager/api/graphql?variables=(cardSectionTypes:List(JOB_DESCRIPTION_CARD),jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A4209649973,includeSecondaryActionsV2:true)&queryId=voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc
    # https://www.linkedin.com/voyager/api/graphql?variables=(cardSectionTypes:List(BANNER_CARD),jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A4209649973,includeSecondaryActionsV2:true)&queryId=voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc
    # cardSectionTypes:
    # COMPANY_CARD
    # SALARY_CARD
    # BENEFITS_CARD
    #COMPANY_INSIGHTS_CARD
    # HOW_YOU_MATCH_CARD
    # https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87&count=7&q=jobSearch&query=(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:(company:List(1371,332373,15079031,2536160,2478301,900243,48732,276625,2522926),originToLandingJobPostings:List(4233122195,4241015234,4234495017,4224558509,4219661251,4234767155,4236889304,4242819782,4219660453)),spellCorrectionEnabled:true)&servedEventEnabled=False&start=0
    # https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(continuousDiscoveryQuery:(existingResultsCount:23,start:0,query:(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:List((key:company,value:List(2004)),(key:originToLandingJobPostings,value:List(4209649973,4222742534,4226832051,4202599090,4185035335,4207043209,4233173276,4202592745,4144052390))),spellCorrectionEnabled:true),referenceId:W%2B4czxVbiWuX0r6CGnDrIg%3D%3D))&queryId=voyagerJobsDashJobsFeed.b7af4c0bc3d800c9ebf51b46ed8fd44d
    pass
    

def get_followed_company_jobs(auth):
    companies = get_followed_company_info(auth, max_iters=20)
    print('companies done')
    breakpoint()
    company_ids = [company['entityUrn'].split(':')[-1] for company in companies]
    dobreak = True
    breakpoint()
    for company_ids_chunk in chunked(company_ids, 1):
        jobs = get_jobs(auth,company_ids=company_ids_chunk)
        with open(f'extracted/{company_ids_chunk}.json', 'w') as f:
            json.dump(jobs, f)
        if dobreak:
            breakpoint()
    return jobs
        
try:
    r_conn = redis.Redis(host='localhost', port=7777)
except Exception as e:
    logger.error(f"Error connecting to Redis: {e}")
    r_conn = None

if __name__ == "__main__":
    db = duckdb.connect("linkedin.db")  
    test = db.sql("select distinct column_name from information_schema.columns where table_name = 'jobs'")
    test = db.sql("select * from linkedin_data.jobs")
    breakpoint()
    pipeline = dlt.pipeline(
        pipeline_name='linkedin',
        destination=dlt.destinations.duckdb(db),
        dataset_name='linkedin_data',
        dev_mode=False
        )
    r_conn.flushall()
    auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
    auth.authenticate()
    default_evade()
    # breakpoint()

    # res = pipeline.run(get_followed_company_info(auth, max_iters=2))
    # res = pipeline.run( get_jobs(auth,company_ids=['3998']))
    
    # breakpoint()
    # test_auth = auth.session.get("https://www.linkedin.com/in/collin-wischmeyer-b55659a4/")

    jobs = get_followed_company_jobs(auth)
    breakpoint()