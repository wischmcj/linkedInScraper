import os
from urllib.request import Request
from dlt.sources.helpers.rest_client.paginators import RangePaginator

from dlt.common import jsonpath
from urllib.parse import quote


SEARCH_LIMIT = 100

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

API_BASE_URL = "https://www.linkedin.com/voyager/api"
REQUEST_HEADERS = {
    "user-agent": " ".join(
        [
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
            "AppleWebKit/537.36 (KHTML, like Gecko)",
            "Chrome/133.0.0.0 Mobile Safari/537.36",
        ]
    ),
    'accept-language': 'en-US,en;q=0.9',
    "x-li-lang": "en_US",
    "x-restli-protocol-version": "2.0.0",
    # "accept": "application/vnd.linkedin.normalized+json+2.1"
}
#Auth
AUTH_BASE_URL = "https://www.linkedin.com"
AUTH_REQUEST_HEADERS = {
    "X-Li-User-Agent": "LIAuthLibrary:3.2.4 \
                        com.linkedin.LinkedIn:8.8.1 \
                        iPhone:8.3",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
    "X-User-Language": "en",
    "X-User-Locale": "en_US",
    "Accept-Language": "en-us",
}

BATCH_SIZE = 25


client_defaults = {
    'base_url': API_BASE_URL,
}
resource_defaults = {
    'write_disposition': 'merge',
}

standalones = {
    ''
}

def map_cols(data):
    return data


card_types = ['INTERESTS_VIEW_DETAILS', 'INTERESTS']
profile_tabs = ['COMPANIES_INTERESTS']

query_id = 'voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'
# paged_list_component = 'urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29'
paged_list_component = 'urn:li:fsd_profilePagedListComponent:(ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY,INTERESTS_VIEW_DETAILS,urn:li:fsd_profileTabSection:COMPANIES_INTERESTS,NONE,en_US)'

component_type = 'urn:li:fsd_profilePagedListComponent'
profile_urn = 'ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY'
card_type = 'INTERESTS_VIEW_DETAILS'
card_tab_urn = 'urn:li:fsd_profileTabSection:COMPANIES_INTERESTS'
something = 'NONE' # styling?
language = 'en_US'

followed_companies_profile_component = f'{component_type}:({profile_urn},{card_type},{card_tab_urn},{something},{language})'

default_variables = {
                "count": BATCH_SIZE,
                "filters": "List()",
                # "origin": "GLOBAL_SEARCH_HEADER",
                "q": "all", #
                "start": '$start',
                # "queryContext": "List(spellCorrectionEnabled->true,relatedSearchesEnabled->false,kcardTypes->PROFILE|COMPANY)",
                "includeWebMetadata": "true",
}

endpoints = {
        'followed_companies': { #'profile_components': {
            'path': 'graphql',
            'query': {  
                'queryId': 'voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357',
                "variables":{
                    "pagedListComponent": quote(paged_list_component),
                    "paginationToken":'null',
                    'start': '$start',
                    'count': BATCH_SIZE
                },
            }
        },
        'jobs_by_company': {
            'path': 'voyagerJobsDashJobCards',
            'query': {  
                'decorationId': 'com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87',
                'q': 'jobSearch',
                'query': {
                    'origin':'COMPANY_PAGE_JOBS_CLUSTER_EXPANSION',
                    'locationUnion':{
                        'geoId': 92000000
                    },
                    'selectedFilters': {
                        'company': 'List({resources.followed_companies.company_id})'
                    },
                    'spellCorrectionEnabled': 'true',
                    'servedEventEnabled': 'False',
                },
                'start': '$start',
                'count': BATCH_SIZE
            },
            'include_from_parent': ['company_id']
        },
        'profile_experiences': {
            'path': 'graphql',
            'query': {  
                'query_id': 'voyagerIdentityDashProfileComponents.7af5d6f176f11583b382e37e5639e69e',
                "variables":{
                        "pagedListComponent": quote(paged_list_component),
                        "paginationToken":'null',
                },
            }
        },
        'job_search_history':{
            'path': 'graphql',
            'query': {  
                'query_id': 'voyagerJobsDashJobSearchHistories.220d01e7d55ec8363130acffb73298ff', 
                'query': {
                    'selectedFilters': '(company:List([3200474]))',
                },
                'variables':{
                    'count': 20,
                    'start': 0,
                    'jobSearchType': 'CLASSIC',
                }
            }
        },
        'search':{
            'path': 'graphql',
            'query': {  
                'query_id': 'voyagerSearchDashClusters.b0928897b71bd00a5a7291755dcd64f0',
                'variables':{
                    'origin': 'GLOBAL_SEARCH_HEADER',
                    # might need to encode the below with quote
                    'query': '(keywords:${keywords}, flagshipSearchIntent:SEARCH_SRP, queryParameters:${filters}, includeFiltersInResponse:false)',
                    'queryContext': 'List(spellCorrectionEnabled->true,relatedSearchesEnabled->true,kcardTypes->PROFILE|COMPANY)',
                    'includeWebMetadata': 'true',
                }
            }
        },
        'job_listings':{
            'path': 'graphql',
            'query': {  
                'query_id': 'voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc',
                'variables':{
                    'cardSectionTypes': 'List(BANNER_CARD)',
                    'jobPostingUrn': '$jobPostingUrn', #'urn:li:fsd_jobPosting:4209649973',
                    'includeSecondaryActionsV2': 'true',
                }
            }
        },
    
    }




total_paths = {
    'followed_companies': 'data.identityDashProfileComponentsByPagedListComponent.paging.total',
    'jobs_by_company': 'paging.total'
}
data_selectors = {
    'profile_components': 'data.identityDashProfileComponentsByPagedListComponent.elements',
    'followed_companies': 'data.identityDashProfileComponentsByPagedListComponent.elements.[*].components.entityComponent.titleV2.text.attributesV2.[*].detailData.companyName',
    'jobs_by_company': 'elements.[*].jobCardUnion.jobPostingCard' #.[jobPostingUrn, jobPostingTitle, "primaryDescription.text", "secondaryDescription.text", "jobPosting.posterId"]'
    #[*].name.entityUrn.url'
    # paths = [['data.identityDashProfileComponentsByPagedListComponent.elements.[*].components.entityComponent.titleV2.text.attributesV2.[*].detailData.companyName']
        # data_keys = ['name','entityUrn','url']
}

graphql_pagignator_config = {
    'param_name':'start',
    'initial_value':0,
    'value_step':BATCH_SIZE,
    'maximum_value':100,
    'base_index':0,
    # 'total_path':
    'error_message_items':"errors"
}

    # },
    # 'jobs_by_company': {
    #     'base_url': f'{API_BASE_URL}',
    #     'endpoint': {
    #         'path': 'voyagerJobsDashJobCards',
    #         'params': {
    #             "decorationId":"com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87",
    #             # "decorationId":"com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-219"
    #             "count":20,
    #             "q":"jobSearch",    
    #             "query": {
    #                 "origin":"COMPANY_PAGE_JOBS_CLUSTER_EXPANSION",
    #                 "locationUnion":{
    #                     "geoId":92000000
    #                 },
    #                 "selectedFilters":{
    #                     # "company":"List(1371,332373,15079031,2536160,2478301,900243,48732,276625,2522926)",
    #                     "company": '{resources.followed_companies.company_ids}',
    #                     # "originToLandingJobPostings":"List(4233122195,4241015234,4234495017,4224558509,4219661251,4234767155,4236889304,4242819782,4219660453)",
    #                 },
    #                 "spellCorrectionEnabled":"true"
    #             },
    #             'start': '$start'
    #         },
    #         'paths': [['elements'],['jobCardUnion','jobPostingCard']],
    #         'data_keys': ['jobPostingUrn','jobPostingTitle',
    #                     ['primaryDescription', 'text'],
    #                     ['secondaryDescription', 'text'],
    #                     ["jobPosting", "posterId"],
    #                     ["logo", "attributes", 0, "detailDataUnion","companyLogo"]],
    #     },
    # 'job_description': {
    #     'base_url': f'{API_BASE_URL}',
    #     'path': 'voyagerJobsDashJobCards',
    #     'parameters': {  
    #     "variables": {
    #         "jobPostingUrn": '{resources.jobs_by_company.job_urn}',
    #         "cardSectionTypes": ['JOB_DESCRIPTION_CARD'],
    #         "includeSecondaryActionsV2": True
    #         },
    #         "queryId": "voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc"
    #     },
    #     'paths': [['data','jobPostingDetailSections','elements'],],
    #     'data_keys': ['jobPostingDetailSections']
    #     },
    # }
# }
