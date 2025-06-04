import pytest
from rest_scraper import build_gql_url, param_to_str


companies_query_id = 'voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'
companies_paged_list_component = 'urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29'
companies_params = {
    "variables":{
        "pagedListComponent":companies_paged_list_component,
        "paginationToken":'null',
        "start":'$start',
        "count":30
    },
    "queryId":companies_query_id
}

nested_params = {
    "query": {
            "origin":"COMPANY_PAGE_JOBS_CLUSTER_EXPANSION",
            "locationUnion":{
                "geoId":92000000
            },
            "selectedFilters":{
                "company":[1371,332373,15079031,2536160,2478301,900243,48732,276625,2522926],
            },
            "spellCorrectionEnabled":"true"
        },
        'servedEventEnabled': False,
}

def test_build_param_str_not_nested():
    param_str = param_to_str(nested_params)
    assert param_str == 'query=(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:(company:List(1371,332373)),spellCorrectionEnabled:true)&servedEventEnabled=False'

    assert param_str == 'pagedListComponent:urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29,paginationToken:null,start:$start,count:30'

def test_build_param_str_single_nested():
    param_str = param_to_str(companies_params)
    assert param_str == 'variables=(pagedListComponent:urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29,paginationToken:null,start:$start,count:30)&queryId=voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'

def test_build_param_str_multi_nested():
    nested_params["other_params"] = {
        "paginationToken":'null',
        "start":'$start',
        "count":30
    }
    param_str = param_to_str(nested_params)
    assert param_str == 'query=(origin:COMPANY_PAGE_JOBS_CLUSTER_EXPANSION,locationUnion:(geoId:92000000),selectedFilters:(company:List(1371,332373)),spellCorrectionEnabled:true)&servedEventEnabled=False&other_params=(paginationToken:null,start:$start,count:30)'

def test_gql_url_builder_no_input():
    url_template = build_gql_url(companies_params)
    url = url_template.safe_substitute()

    assert url == 'https://www.linkedin.com/voyager/api/graphql?variables=(pagedListComponent:urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29,paginationToken:null,start:$start,count:30)&queryId=voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'
    
def test_gql_url_builder_w_input():
    url_template = build_gql_url(companies_params)
    
    url = url_template.safe_substitute(start=0)
    assert url == 'https://www.linkedin.com/voyager/api/graphql?variables=(pagedListComponent:urn%3Ali%3Afsd_profilePagedListComponent%3A%28ACoAABYqYDEBjEt38JrRJYPi-2_2t0yUvugdpmY%2CINTERESTS_VIEW_DETAILS%2Curn%3Ali%3Afsd_profileTabSection%3ACOMPANIES_INTERESTS%2CNONE%2Cen_US%29,paginationToken:null,start:0,count:30)&queryId=voyagerIdentityDashProfileComponents.1ad109a952e36585fdc2e7c2dedcc357'
    
    

    

    