from __future__ import annotations

from urllib.parse import quote

from configuration.column_mapping import (encode_job_urn, get_json_map,
                                          get_json_map_nested,
                                          get_replace_func)
from configuration.pipeline_conf import BATCH_SIZE


def map_cols(data):
    return data


## LinkedIn API fields

job_card_types = [
    "JOB_DESCRIPTION_CARD",
    "SALARY_CARD",
]  #'JOB_DESCRIPTION_CARD,JOB_SEGMENT_ATTRIBUTES_CARD,JOB_APPLICANT_INSIGHTS,BANNER_CARD,COMPANY_CARD,SALARY_CARD,BENEFITS_CARD,COMPANY_INSIGHTS_CARD,HOW_YOU_MATCH_CARD,TOP_CARD,HOW_YOU_FIT_CARD']

### URL Parameter - defines the structure of the data returned by the api
paged_list_component = "urn:li:fsd_profilePagedListComponent:(ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY,INTERESTS_VIEW_DETAILS,urn:li:fsd_profileTabSection:COMPANIES_INTERESTS,NONE,en_US)"

default_variables = {
    "count": BATCH_SIZE,
    "filters": "List()",
    # "origin": "GLOBAL_SEARCH_HEADER",
    "q": "all",  #
    "start": "$start",
    # "queryContext": "List(spellCorrectionEnabled->true,relatedSearchesEnabled->false,kcardTypes->PROFILE|COMPANY)",
    "includeWebMetadata": "true",
}

## Endpoint Details

# Endpoints fall into one of 3 categories based on url structure:
# 1. Saved query endpoints
#   - These are endpoints using 'queries' (essential functions)
#      predefined by LinkedIn.
#   - Passes pagination variables and/or parameters for filtering the query
#   - e.g. followed companies, jobs_description
# 2. GraphQL query endpoints
#   - These are endpoints query certain data types (e.g. jobs) and pass
#      a list of parameters to filter data on, as well as a
#      decoration_id, specifying return data format
#   - e.g. jobs_by_company

# Determines what data needs to be read from the local db if not pulled in a requested run
dependencies = {
    "company_details": ["followed_companies"],
    "jobs_by_company": ["followed_companies"],
    "job_description": ["jobs_by_company"],
}

endpoints = {
    # "example": {
    #     "path": # Maps to endpoint
    #     "query": # This is mapped to request.json, then passed to build_gql_url
    #                 # along with the endpoint path
    # },
    # "something": {
    #     "path": "graphql",
    #     "query": {
    #         "includeWebMetadata": "true",
    #         "variables": {
    #             "profileUrn": "urn%3Ali%3Afsd_profile%3AACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY",
    #             "sectionType": "collapsible_browsemap_recommendation",
    #         },
    #         "queryId": "voyagerIdentityDashProfileCards.b3c966c096fa041c027327abceed369b",
    #     },
    # },
    "company_details": {
        "path": "graphql",
        #  https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=False&variables=(companyUrns:List(urn:li:fsd_company:9414302))&queryId=voyagerOrganizationDashCompanies.32a7cdaea60de8f9ce50df019654c45d
        # "https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(companyUrns:List(urn%3Ali%3Afsd_company%3A9414302))&queryId=voyagerOrganizationDashCompanies.32a7cdaea60de8f9ce50df019654c45d": {
        "json": {
            "includeWebMetadata": "false",
            # "variables": "companyUrns:List(urn:li:fsd_company:9414302)",
            "variables": {
                "companyUrns": "List(urn%3Ali%3Afsd_company%3A{resources.followed_companies.company_id})"
            },
            "queryId": "voyagerOrganizationDashCompanies.32a7cdaea60de8f9ce50df019654c45d",
        },
        "include_from_parent": ["company_id"],
    },
    "company_jobs": {
        "path": "graphql",
        "json": {
            "queryId": "voyagerJobsDashJobCards.67b88a170c772f25e3791c583e63da26",
            "includeWebMetadata": "true",
            "variables": {
                "query": {
                    "origin": "JOB_SEARCH_PAGE_JOB_FILTER",
                    "locationUnion": {"geoUrn": "urn%3Ali%3Afsd_geo%3A92000000"},
                    "selectedFilters": "List((key:company,value:List({resources.followed_companies.company_id})))",
                    "spellCorrectionEnabled": "true",
                }
            },
        },
        "include_from_parent": ["company_id"],
    },
    # IDK why this was included... but it was, so leaving it here for now
    # 'filter': {
    #     'company_id': 'List({resources.followed_companies.company_id})'
    # }
    "followed_companies": {  #'profile_components': {
        "path": "graphql",
        "json": {
            "queryId": "voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357",
            "variables": {
                "pagedListComponent": quote(paged_list_component),
                "paginationToken": "null",
                "start": "$start",
                "count": BATCH_SIZE,
            },
        },
        # IDK why this was included... but it was, so leaving it here for now
        # 'filter': {
        #     'company_id': 'List({resources.followed_companies.company_id})'
        # }
    },
    "jobs_by_company": {
        "path": "voyagerJobsDashJobCards",
        "json": {
            "decorationId": "com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollectionLite-87",
            "q": "jobSearch",
            "query": {
                # Read in by LinkedInPaginator to build url
                "origin": "COMPANY_PAGE_JOBS_CLUSTER_EXPANSION",
                "locationUnion": {"geoId": 92000000},
                "selectedFilters": {
                    "company": "List({resources.followed_companies.company_id})"
                },
                "spellCorrectionEnabled": "true",
                "servedEventEnabled": "False",
            },
            "start": "$start",
            "count": BATCH_SIZE,
        },
        "include_from_parent": [
            "company_id"
        ],  # Allows for 'query' to reference 'company_id'
    },
    "job_description": {
        "path": "graphql",
        "json": {
            "queryId": "voyagerJobsDashJobPostingDetailSections.3b2647d9e7ecb085c570a16f9e70d1cc",
            "variables": {
                "cardSectionTypes": f'List({','.join(job_card_types)})',
                # 'cardSectionTypes': 'List(JOB_DESCRIPTION_CARD,JOB_SEGMENT_ATTRIBUTES_CARD,JOB_APPLICANT_INSIGHTS,BANNER_CARD,COMPANY_CARD,SALARY_CARD,BENEFITS_CARD,COMPANY_INSIGHTS_CARD,HOW_YOU_MATCH_CARD,TOP_CARD,HOW_YOU_FIT_CARD)',
                "jobPostingUrn": "{resources.jobs_by_company.job_urn_encoded}",  #'urn:li:fsd_jobPosting:4209649973',
                "includeSecondaryActionsV2": "true",
            },
        },
        "include_from_parent": ["job_urn_encoded"],
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

## Determines where the array of data is located in the json response
data_selectors = {
    "profile_components": "data.identityDashProfileComponentsByPagedListComponent.elements",
    "followed_companies": "data.identityDashProfileComponentsByPagedListComponent.elements.[*].components.entityComponent.titleV2.text.attributesV2.[*].detailData.companyName",
    "job_description": "data.jobsDashJobPostingDetailSectionsByCardSectionTypes.elements.[*].jobPostingDetailSection.[*].jobDescription",
    "jobs_by_company": "elements.[*].jobCardUnion.jobPostingCard",  # .[jobPostingUrn, jobPostingTitle, "primaryDescription.text", "secondaryDescription.text", "jobPosting.posterId"]'
    "something": "",
    "company_details": "data.organizationDashCompaniesByIds[*]",
}

drop_columns = {
    "company_details": ["similar_organizations"],
}
## defines columns extracted from the json response
mappings = {
    "followed_companies": {
        "mapped_cols": [
            ("company_id", lambda resp: resp.get("entityUrn", ":").split(":")[-1]),
        ],
    },
    "jobs_by_company": {
        "mapped_cols": [
            ("job_posting_title", get_json_map("jobPostingTitle")),
            ("entity_urn", get_json_map("jobPosting.entityUrn")),
            ("job_id", get_json_map("jobPosting.entityUrn")),
            (
                "company_logo_urn",
                get_json_map("logo.attributes.[0].detailDataUnion.companyLogo"),
            ),
            ("primary_description", get_json_map("primaryDescription.text")),
            ("secondary_description", get_json_map("secondaryDescription.text")),
            (
                "job_id",
                get_replace_func("entity_urn", [("urn:li:fsd_jobPosting:", "")]),
            ),
            (
                "company_id",
                get_replace_func("company_logo_urn", [("urn:li:fsd_company:", "")]),
            ),
            (
                "location",
                get_replace_func(
                    "secondary_description",
                    [("(On-site)", ""), ("(Hybrid)", ""), ("(Remote)", "")],
                ),
            ),
            ("company_name", get_replace_func("primary_description", [("", "")])),
            (
                "is_remote",
                lambda resp: "remote" in resp["secondary_description"].lower(),
            ),
            (
                "is_hybrid",
                lambda resp: "hybrid" in resp["secondary_description"].lower(),
            ),
            ("job_urn_encoded", encode_job_urn),
        ],
    },
    "job_description": {
        "mapped_cols": [
            ("descriptionText", get_json_map("descriptionText.text")),
            ("description", get_json_map("jobPosting.description.text")),
            ("job_posting_urn", get_json_map("jobPosting.entityUrn")),
        ],
    },
    "company_details": {
        "mapped_cols": [
            ("company_id", lambda resp: resp.get("entityUrn", ":").split(":")[-1]),
            ("company_name", get_json_map("name")),
            (
                "locations",
                get_json_map_nested(
                    "groupedLocations.[*]",
                    [
                        ("name", "name"),
                        ("urn", "entityUrn"),
                        ("latitude", "latLong.latitude"),
                        ("longitude", "latLong.longitude"),
                        ("city", "city"),
                        ("country", "country"),
                    ],
                ),
            ),
            # ("locations_lat_long", get_json_map("groupedLocations.[*].latLong.latitude"), get_json_map("groupedLocations.[*].latLong.longitude"))),
            # ("website_call_to_action",get_json_map("$.callToAction.type[?(@.type == 'VIEW_WEBSITE')]")),
            ("size_range_min", get_json_map("employeeCountRange.start")),
            ("size_range_max", get_json_map("employeeCountRange.end")),
            (
                "similar_organizations",
                get_json_map_nested(
                    "similarOrganizations.elements.[*]",
                    [
                        ("name", "name"),
                        ("urn", "entityUrn"),
                        ("industry", "industry.name"),
                        ("industry_urn", "industry.entityUrn"),
                        ("url", "url"),
                    ],
                ),
            ),
            (
                "last_funding_data",
                get_json_map_nested(
                    "crunchbaseFundingData",
                    [
                        ("lead_investors", "lastFundingRound.leadInvestors.[*].name"),
                        ("money_raised", "lastFundingRound.moneyRaised.amount"),
                        ("funding_round_url", "lastFundingRound.fundingRoundUrl"),
                        ("announced_on_month", "lastFundingRound.announcedOn.month"),
                        ("announced_on_year", "lastFundingRound.announcedOn.year"),
                        (
                            "number_of_other_investors",
                            "lastFundingRound.numberOfOtherInvestors",
                        ),
                        ("investors_url", "lastFundingRound.investorsUrl"),
                        ("organization_url", "organizationUrl"),
                        ("funding_rounds_url", "fundingRoundsUrl"),
                    ],
                ),
            ),
            ("industry_urn", get_json_map("industry.[*].entityUrn", allow_list=True)),
            ("industry", get_json_map("industry.[*].name", allow_list=True)),
            ("hashtag", get_json_map("hashtag.[*].displayName", allow_list=True)),
            (
                "secondary_industry",
                get_json_map("industryV2Taxonomy.[*].name", allow_list=True),
            ),
            ("website", get_json_map("websiteUrl")),
            ("following", get_json_map("followingState.following")),
        ],
        "drop_list": [
            "viewerPermissions",
            "socialProofInsight",
            "lcpStaffingOrganization",
            "organizationalPage",
            "followingState",
            "croppedCoverImage",
            "coverImageCropInfo",
            "pageMailbox",
            "employeeCountRange",
            "affiliatedOrganizationsByEmployees",
            "memberTabs",
            "employeeExperienceSettings",
            "originalCoverImage",
            "affiliatedOrganizationsByShowcases",
            "headquarter",
            "industryV2Taxonomy",
            "foundedOn",
            "lixTreatments",
            "defaultLandingMemberTab",
            "affiliatedOrganizationsByJobs",
            "pageVerification",
            "logoResolutionResult",
            "crunchbaseFundingData",
        ],
    },
}

# Used when paginating to determine the total number of pages to scrape
total_paths = {
    "followed_companies": "data.identityDashProfileComponentsByPagedListComponent.paging.total",
    "jobs_by_company": "paging.total",
    "company_details": None,
}
