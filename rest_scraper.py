
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
        name = 'linkedin_data.followed_company_info',
        columns={"url": {"data_type": "text"},
                 "name": {"data_type": "text"},
                 "company_id": {"data_type": "text"},
                 "entity_urn": {"data_type": "text"}},
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
            for company in batch_data: 
                company['company_id'] = company['entityUrn'].split(':')[-1]
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

# @dlt.transformer
# def deal_scores(deal_item):
#     # obtain the score, deal_items contains data yielded by source.deals
#     score = model.predict(featurize(deal_item))
#     yield {"deal_id": deal_item, "score": score}

@dlt.resource(
        name = 'jobs',
        columns={"jobPostingUrn": {"data_type": "text"},
                 "jobPostingTitle": {"data_type": "text"},
                 "job_id": {"data_type": "text"},
                 "company_id": {"data_type": "text"},
                 "entity_urn": {"data_type": "text"}},
        primary_key="job_id",
        write_disposition="merge"
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

def get_job_description(auth, job_urn:str, cardSectionTypes:list= None):
    """Fetch data for a given LinkedIn job posting.

    :param job_id: LinkedIn job ID
    :type job_id: str

    :return: Job posting data
    :rtype: dict

    """
    # https://www.linkedin.com/voyager/api/graphql
    #   ?variables=(jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A4178609184)
    #   &queryId=voyagerTalentbrandDashTargetedContents.8b111cec5d5527ad575591979ba20fb2
    # https://www.linkedin.com/voyager/api/graphql
    #   ?variables=(cardSectionTypes:List(JOB_DESCRIPTION_CARD),
    #               jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A4209649973,
    #               includeSecondaryActionsV2:true)
    #   &queryId=voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc

    # https://www.linkedin.com/voyager/api/graphql
    # ?variables=(cardSectionTypes:List(BANNER_CARD),
    #   jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A4209649973,
    #   includeSecondaryActionsV2:true)&queryId=voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc
    # 
    # cardSectionTypes:
    # JOB_DESCRIPTION_CARD
    # JOB_SEGMENT_ATTRIBUTES_CARD
    # JOB_APPLICANT_INSIGHTS
    # BANNER_CARD
    # COMPANY_CARD
    # SALARY_CARD
    # BENEFITS_CARD
    # COMPANY_INSIGHTS_CARD
    # HOW_YOU_MATCH_CARD
    # TOP_CARD,HOW_YOU_FIT_CARD
    #INTERVIEW_PREP_CARD 
    # UPSELL_SECTION_CARD, RECOMMENDED_ACTIONS_CARD, JSERP_SEEKER_NEXT_BEST_ACTION_CARDS
    # HIRING_TEAM_CARD, CONNECTIONS_CARD

    session = auth.session
    # if not base_url:
    base_url = f'{API_BASE_URL}'
    endpoint = 'voyagerJobsDashJobCards'
    parameters = {  
        "variables": {
            "jobPostingUrn": job_urn,
            "cardSectionTypes": cardSectionTypes,
            # ["JOB_DESCRIPTION_CARD"],
            "includeSecondaryActionsV2": True
            },
            "queryId": "voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc"
    }
    paths= [['data','jobPostingDetailSections','elements'],]
    data_keys = ['jobPostingDetailSections']
    url_template = build_gql_url(parameters,base_url,endpoint)
    res = session.get(url_template)
    res_json = json.loads(res.content)
    breakpoint()
    batch_data, returned_batch_size = get_gql_data(res_json, paths, data_keys)
    return batch_data
    

def get_followed_company_jobs(auth):
    db = duckdb.connect("linkedin.db") 
    pipeline = dlt.pipeline(
        pipeline_name='linkedin',
        destination=dlt.destinations.duckdb(db),
        dataset_name='linkedin_data',
        dev_mode=False
        )
    res = pipeline.run(get_followed_company_info(auth, max_iters=30))
    print('companies done')
    # company_ids = [company['company_id'] for company in companies]
    test = db.sql("select distinct company_id from linkedin_data.followed_company_info")
    company_ids = test.df()['company_id']
    dobreak = True
    breakpoint()
    for company_ids_chunk in chunked(company_ids, 1):
        jobs = pipeline.run(get_jobs(auth,company_ids=company_ids_chunk))
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
    # test = db.sql("select distinct column_name from information_schema.columns where table_name = 'jobs'")
    # test = db.sql("select * from linkedin_data.jobs")
    # test = db.sql("select distinct company_id from linkedin_data.followed_company_info")
    test = db.sql("DESCRIBE;")

    breakpoint()
    pipeline = dlt.pipeline(
        pipeline_name='linkedin',
        destination=dlt.destinations.duckdb(db),
        dataset_name='linkedin_data',
        dev_mode=False
        )
    r_conn.flushall()
    logger.info(f"Authenticating with LinkedIn")
    auth = CustomAuth(username=os.getenv("LINKEDIN_USERNAME"), password=os.getenv("LINKEDIN_PASSWORD"))
    auth.authenticate()
    default_evade()
    res = pipeline.run(get_followed_company_info(auth, max_iters=2))
    res = pipeline.run( get_jobs(auth,company_ids=['3998']))
    # res = pipeline.run(get_job_description(auth, 
    #                                        job_urn="urn:li:fsd_jobPosting:4231156986", 
    #                                        cardSectionTypes=["JOB_DESCRIPTION_CARD", "SALARY_CARD"]))
    
    # breakpoint()

    breakpoint()
    get_job_description(auth, 
                        job_urn="urn:li:fsd_jobPosting:4231156986", 
                        cardSectionTypes=["JOB_DESCRIPTION_CARD", "SALARY_CARD"])
    breakpoint()