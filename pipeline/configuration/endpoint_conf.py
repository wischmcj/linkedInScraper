import re
from urllib.request import Request
from dlt.sources.helpers.rest_client.paginators import RangePaginator

from dlt.common import jsonpath
from urllib.parse import quote

from configuration.pipeline_conf import (
    BATCH_SIZE,
    API_BASE_URL,
    graphql_pagignator_config,
    endpoints,
    total_paths,
    data_selectors,
    mapppings
)

from configuration.column_mapping import get_replace_func, get_json_map, encode_job_urn

def map_cols(data):
    return data


## LinkedIn API fields

job_card_types=[ 'JOB_DESCRIPTION_CARD','SALARY_CARD'] #'JOB_DESCRIPTION_CARD,JOB_SEGMENT_ATTRIBUTES_CARD,JOB_APPLICANT_INSIGHTS,BANNER_CARD,COMPANY_CARD,SALARY_CARD,BENEFITS_CARD,COMPANY_INSIGHTS_CARD,HOW_YOU_MATCH_CARD,TOP_CARD,HOW_YOU_FIT_CARD']

### URL Parameter - defines a query to be made to the api
query_id = 'voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'

### URL Parameter - defines the strucuture of the data returned by the api
paged_list_component = 'urn:li:fsd_profilePagedListComponent:(ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY,INTERESTS_VIEW_DETAILS,urn:li:fsd_profileTabSection:COMPANIES_INTERESTS,NONE,en_US)'

### Components of the followed companies profile component
component_type = 'urn:li:fsd_profilePagedListComponent'
profile_urn = 'ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY'
card_type = 'INTERESTS_VIEW_DETAILS'
card_tab_urn = 'urn:li:fsd_profileTabSection:COMPANIES_INTERESTS'
something = 'NONE' # styling?
language = 'en_US'

followed_companies_profile_component = f'{component_type}:({profile_urn},{card_type},{card_tab_urn},{something},{language})'


## Endpoint Details

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
            },
            # IDK why this was included... but it was, so leaving it here for now
            # 'filter': {
            #     'company_id': 'List({resources.followed_companies.company_id})'
            # }
        },
        'jobs_by_company': {
            'path': 'voyagerJobsDashJobCards',
            'query': {  
                'decorationId': 'com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87',
                'q': 'jobSearch',
                'query': {
                    # Read in by LinkedInPaginator to build url
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
            'include_from_parent': ['company_id'] # Allows for 'query' to reference 'company_id'
        },
        'job_description':{
            'path': 'graphql',
            'query': {  
                'queryId': 'voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc',
                'variables':{
                    'cardSectionTypes': f'List({','.join(job_card_types)})',
                    # 'cardSectionTypes': 'List(JOB_DESCRIPTION_CARD,JOB_SEGMENT_ATTRIBUTES_CARD,JOB_APPLICANT_INSIGHTS,BANNER_CARD,COMPANY_CARD,SALARY_CARD,BENEFITS_CARD,COMPANY_INSIGHTS_CARD,HOW_YOU_MATCH_CARD,TOP_CARD,HOW_YOU_FIT_CARD)',
                    'jobPostingUrn': '{resources.jobs_by_company.job_urn_encoded}', #'urn:li:fsd_jobPosting:4209649973',
                    'includeSecondaryActionsV2': 'true',
                }
            },
            'include_from_parent': ['job_urn_encoded']
        },
        ### UNTESTED
        # 'profile_experiences': {
        #     'path': 'graphql',
        #     'query': {  
        #         'queryId': 'voyagerIdentityDashProfileComponents.7af5d6f176f11583b382e37e5639e69e',
        #         "variables":{
        #                 "pagedListComponent": quote(paged_list_component),
        #                 "paginationToken":'null',
        #         },
        #     }
        # },
        # 'job_search_history':{
        #     'path': 'graphql',
        #     'query': {  
        #         'queryId': 'voyagerJobsDashJobSearchHistories.220d01e7d55ec8363130acffb73298ff', 
        #         'query': {
        #             'selectedFilters': '(company:List([3200474]))',
        #         },
        #         'variables':{
        #             'count': 20,
        #             'start': 0,
        #             'jobSearchType': 'CLASSIC',
        #         }
        #     }
        # },
        # 'search':{
        #     'path': 'graphql',
        #     'query': {  
        #         'queryId': 'voyagerSearchDashClusters.b0928897b71bd00a5a7291755dcd64f0',
        #         'variables':{
        #             'origin': 'GLOBAL_SEARCH_HEADER',
        #             # might need to encode the below with quote
        #             'query': '(keywords:${keywords}, flagshipSearchIntent:SEARCH_SRP, queryParameters:${filters}, includeFiltersInResponse:false)',
        #             'queryContext': 'List(spellCorrectionEnabled->true,relatedSearchesEnabled->true,kcardTypes->PROFILE|COMPANY)',
        #             'includeWebMetadata': 'true',
        #         }
        #     }
        # },
    
    }


# used for extracting columns nested in the json
## returned by the data selectors
mapppings = {
    'followed_companies': [
        ('company_id',lambda resp: resp.get('entityUrn',':').split(':')[-1]),
    ],
    'jobs_by_company': [
        ('job_posting_title',get_json_map('jobPostingTitle')),
        ('entity_urn',get_json_map('jobPosting.entityUrn')),
        ('job_id',get_json_map('jobPosting.entityUrn')),
        ('company_logo_urn',get_json_map('logo.attributes.[0].detailDataUnion.companyLogo')),
        ('primary_description',get_json_map('primaryDescription.text')),
        ('secondary_description',get_json_map('secondaryDescription.text')),
        ('job_id',
            get_replace_func('entity_urn',[('urn:li:fsd_jobPosting:','')])),
        ('company_id', 
            get_replace_func('company_logo_urn',[('urn:li:fsd_company:','')])),
        ('location',
            get_replace_func('secondary_description',[('(On-site)',''),('(Hybrid)',''),('(Remote)','')])),
        ('company_name',
            get_replace_func('primary_description',[('','')])),
        ('is_remote',
            lambda resp: 'remote' in resp['secondary_description'].lower()),
        ('is_hybrid',
            lambda resp: 'hybrid' in resp['secondary_description'].lower()),
        ('job_urn_encoded',encode_job_urn),
        ],
    'job_description': [
        ('descriptionText',get_json_map('descriptionText.text')),
        ('description',get_json_map('jobPosting.description.text')),
        ('job_posting_urn', get_json_map('jobPosting.entityUrn'))
        ],
    
}

# Used to determine the total number of pages to scrape
total_paths = {
    'followed_companies': 'data.identityDashProfileComponentsByPagedListComponent.paging.total',
    'jobs_by_company': 'paging.total',
    'job_description': None
}

data_selectors = {
    'profile_components': 'data.identityDashProfileComponentsByPagedListComponent.elements',
    'followed_companies': 'data.identityDashProfileComponentsByPagedListComponent.elements.[*].components.entityComponent.titleV2.text.attributesV2.[*].detailData.companyName',
    'job_description': 'data.jobsDashJobPostingDetailSectionsByCardSectionTypes.elements.[*].jobPostingDetailSection.[*].jobDescription',
    'jobs_by_company': 'elements.[*].jobCardUnion.jobPostingCard', #.[jobPostingUrn, jobPostingTitle, "primaryDescription.text", "secondaryDescription.text", "jobPosting.posterId"]'
}

graphql_pagignator_config = {
    'param_name':'start',
    'initial_value':0,
    'value_step':BATCH_SIZE,
    'maximum_value':1000,
    'base_index':0,
    # 'total_path':
    'error_message_items':"errors"
}

        