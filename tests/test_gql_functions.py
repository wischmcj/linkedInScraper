import json
import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gql_utils import build_gql_url, get_gql_data, param_to_str


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
    
    


def test_followed_company_data_processing():
    with open('gql/companies/companies_voyagerIdentityDashProfileComponents.json', 'r') as f:
        data = json.load(f)
    paths = [['data','identityDashProfileComponentsByPagedListComponent','elements'],
             ['components','entityComponent','titleV2','text','attributesV2'],
             ['detailData','companyName']]
    data_keys = ['name','entityUrn','url']
    details,_ = get_gql_data(data, paths, data_keys)
    assert details == [{
            'name': 'Data Visualization', 'entityUrn': 'urn:li:fsd_company:92746146', 'url': 'https://www.linkedin.com/showcase/skills-data-visualization/'}, 
            {'name': 'MycoStories', 'entityUrn': 'urn:li:fsd_company:93143139', 'url': 'https://www.linkedin.com/company/mycostories/'},
            {'name': 'Nxt Gen Evolution Inc.', 'entityUrn': 'urn:li:fsd_company:93343470', 'url': 'https://www.linkedin.com/company/nxt-gen-evolution/'},
            {'name': 'Purple Squirrels', 'entityUrn': 'urn:li:fsd_company:93658339', 'url': 'https://www.linkedin.com/company/purple-squirrels/'},
            {'name': 'Ground Truth Analytics', 'entityUrn': 'urn:li:fsd_company:93805669', 'url': 'https://www.linkedin.com/company/ground-truth-analytics/'},
            {'name': 'able.digital', 'entityUrn': 'urn:li:fsd_company:96069207', 'url': 'https://www.linkedin.com/company/able-digital-us/'},
            {'name': 'Magpie Literacy', 'entityUrn': 'urn:li:fsd_company:96336011', 'url': 'https://www.linkedin.com/company/magpie-literacy/'},
            {'name': 'SHECO', 'entityUrn': 'urn:li:fsd_company:96882994', 'url': 'https://www.linkedin.com/company/sheco/'},
            {'name': 'thrively', 'entityUrn': 'urn:li:fsd_company:96927053', 'url': 'https://www.linkedin.com/company/thrivelytalent/'},
            {'name': 'Attis', 'entityUrn': 'urn:li:fsd_company:101159591', 'url': 'https://www.linkedin.com/company/attisglobal/'},
            {'name': 'International Barcode of Life Consortium', 'entityUrn': 'urn:li:fsd_company:101732077', 'url': 'https://www.linkedin.com/company/ibolconsortium/'},
            {'name': 'BluelightAI', 'entityUrn': 'urn:li:fsd_company:103417747', 'url': 'https://www.linkedin.com/company/bluelightai/'},
            {'name': 'NOAA Digital Coast', 'entityUrn': 'urn:li:fsd_company:104264349', 'url': 'https://www.linkedin.com/showcase/noaa-coastal-management/'},
            {'name': 'Bee Maps', 'entityUrn': 'urn:li:fsd_company:104400966', 'url': 'https://www.linkedin.com/company/bee-maps/'},
            {'name': 'Bruker Spatial Biology', 'entityUrn': 'urn:li:fsd_company:104441009', 'url': 'https://www.linkedin.com/company/bruker-spatial/'},
            {'name': 'Encode Biosciences', 'entityUrn': 'urn:li:fsd_company:104830284', 'url': 'https://www.linkedin.com/company/encode-bio/'},
            {'name': 'Levangie Laboratories', 'entityUrn': 'urn:li:fsd_company:105211267', 'url': 'https://www.linkedin.com/company/levlabs/'}]



def test_company_job_listing_processing():
    with open('tests/jobs_voyagerJobsDashJobCards.json', 'r') as f: data = json.load(f)
    # data_keys = ['jobPostingUrn','jobPostingTitle','primaryDescription','entityUrn']
    # paths = [['elements'],['jobCardUnion','jobPostingCard']]
    paths = [['elements'],['jobCardUnion','jobPostingCard']]
    data_keys = ['jobPostingUrn','jobPostingTitle',['primaryDescription', 'text'],'entityUrn']

    details = get_gql_data(data, paths, data_keys)
    breakpoint()
    assert details == ([{'jobPostingUrn': 'urn:li:fsd_jobPosting:4243875871', 'jobPostingTitle': 'Information Technology Manager', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'W. L. French Excavating Corporation', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243875871,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243888079', 'jobPostingTitle': 'Juniper Mist Travel Network Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Collyde, Inc.', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243888079,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241157147', 'jobPostingTitle': 'Quality Assurance Analyst [On-Site, Saint Paul, Minnesota]', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'CodeWeavers', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241157147,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243883166', 'jobPostingTitle': 'Director of Digital Media, Buying & Planning', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'DX', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243883166,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241158198', 'jobPostingTitle': 'Quality Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Tulavi', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241158198,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243876553', 'jobPostingTitle': 'Director of Business Development', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Laxxon Medical', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243876553,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243877178', 'jobPostingTitle': 'Bartender/Server', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'X-GOLF West Charlotte', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243877178,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241160407', 'jobPostingTitle': 'Lead Manufacturing Test Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Schweitzer Engineering Laboratories (SEL)', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241160407,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243878576', 'jobPostingTitle': 'Licensed Massage Therapist', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Hand & Stone Massage and Facial Spa', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243878576,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243878385', 'jobPostingTitle': 'Front Desk Receptionist', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Parr Law Firm', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243878385,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241158289', 'jobPostingTitle': 'Luxury Watch Sales Professional', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Zadok Jewelers', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241158289,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241157619', 'jobPostingTitle': 'Front Office Coordinator', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'All Play Inc.', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241157619,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243871639', 'jobPostingTitle': 'Experienced Automotive Technician', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': "Len's Auto Repair", 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243871639,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243877526', 'jobPostingTitle': 'Executive Assistant', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'CryoFuture', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243877526,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241155611', 'jobPostingTitle': 'eCommerce Optimization Specialist', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': "Mano's Wine", 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241155611,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4240085583', 'jobPostingTitle': 'Backend Engineer (Mid-Level) [32284]', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Stealth AI Startup', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4240085583,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241156454', 'jobPostingTitle': 'Human Resource Specialist', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Detroit Transportation Corporation', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241156454,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243860556', 'jobPostingTitle': 'Sous Chef', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'JonesCraft', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243860556,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243879287', 'jobPostingTitle': 'Senior Leadership Team', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Upstate Federal Credit Union', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243879287,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241146993', 'jobPostingTitle': 'Data Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Bamboo Crowd', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241146993,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243800752', 'jobPostingTitle': 'Data Engineer (USA)', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Lensa', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243800752,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243880819', 'jobPostingTitle': 'Software Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'TalentAlly', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243880819,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243873024', 'jobPostingTitle': 'Software Engineer II', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'NBME', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243873024,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243863806', 'jobPostingTitle': '𝗧𝗿𝘂𝗰𝗸 𝗗𝗿𝗶𝘃𝗲𝗿 / 𝗕𝗼𝗼𝗺 𝗠𝗼𝘄𝗲𝗿 𝗗𝗲𝗺𝗼 𝗗𝗿𝗶𝘃𝗲𝗿 for the US West Coast.', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'ATMAX Equipment Co.', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243863806,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241157182', 'jobPostingTitle': 'AI Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Intragen', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241157182,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243876712', 'jobPostingTitle': 'Finance Specialist', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Society of American Florists', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243876712,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243868651', 'jobPostingTitle': 'Veterinary Assistant and Veterinary Technician', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Nonantum Veterinary Clinic', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243868651,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4240079007', 'jobPostingTitle': 'Physical Therapist', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'St. Coletta of Greater Washington', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4240079007,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243869449', 'jobPostingTitle': 'Analytics Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Tort Experts', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4243869449,JOBS_SEARCH)'},
                        {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241150859', 'jobPostingTitle': 'Data Engineer', 'primaryDescription': {'textDirection': 'USER_LOCALE', '$recipeType': 'com.linkedin.voyager.dash.deco.common.text.TextViewModelV2', 'text': 'Waterleau', 'attributesV2': []}, 'entityUrn': 'urn:li:fsd_jobPostingCard:(4241150859,JOBS_SEARCH)'}], 30)


def test_company_job_listing_processing_nested_keys():
    with open('tests/jobs_voyagerJobsDashJobCards.json', 'r') as f: data = json.load(f)
    # data_keys = ['jobPostingUrn','jobPostingTitle','primaryDescription','entityUrn']
    # paths = [['elements'],['jobCardUnion','jobPostingCard']]
    paths = [['elements'],['jobCardUnion','jobPostingCard']]
    data_keys = ['jobPostingUrn','jobPostingTitle',
                 ['primaryDescription', 'text'],
                 ['secondaryDescription', 'text'],
                 ["jobPosting", "posterId"],
                 ["logo", "attributes", 0, "detailDataUnion","companyLogo"]]
    details,_ = get_gql_data(data, paths, data_keys)
    assert details == [{'jobPostingUrn': 'urn:li:fsd_jobPosting:4243875871', 'jobPostingTitle': 'Information Technology Manager', 'primaryDescription:text': 'W. L. French Excavating Corporation', 'secondaryDescription:text': 'North Billerica, MA (On-site)', 'jobPosting:posterId': '6354498', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:155997'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243888079', 'jobPostingTitle': 'Juniper Mist Travel Network Engineer', 'primaryDescription:text': 'Collyde, Inc.', 'secondaryDescription:text': 'United States (Remote)', 'jobPosting:posterId': '100697187', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:104556369'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241157147', 'jobPostingTitle': 'Quality Assurance Analyst [On-Site, Saint Paul, Minnesota]', 'primaryDescription:text': 'CodeWeavers', 'secondaryDescription:text': 'St Paul, MN (On-site)', 'jobPosting:posterId': '19289355', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:73516'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243883166', 'jobPostingTitle': 'Director of Digital Media, Buying & Planning', 'primaryDescription:text': 'DX', 'secondaryDescription:text': 'Edgewater, NJ (On-site)', 'jobPosting:posterId': {}, 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:764722'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241158198', 'jobPostingTitle': 'Quality Engineer', 'primaryDescription:text': 'Tulavi', 'secondaryDescription:text': 'Los Gatos, CA (Hybrid)', 'jobPosting:posterId': '454153920', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:73064613'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243876553', 'jobPostingTitle': 'Director of Business Development', 'primaryDescription:text': 'Laxxon Medical', 'secondaryDescription:text': 'New York, NY (On-site)', 'jobPosting:posterId': '3524513', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:75651692'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243877178', 'jobPostingTitle': 'Bartender/Server', 'primaryDescription:text': 'X-GOLF West Charlotte', 'secondaryDescription:text': 'Charlotte, NC (On-site)', 'jobPosting:posterId': '210156572', 'logo:attributes:0:detailDataUnion:companyLogo': {}},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241160407', 'jobPostingTitle': 'Lead Manufacturing Test Engineer', 'primaryDescription:text': 'Schweitzer Engineering Laboratories (SEL)', 'secondaryDescription:text': 'Pullman, WA (On-site)', 'jobPosting:posterId': '752311672', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:15544'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243878576', 'jobPostingTitle': 'Licensed Massage Therapist', 'primaryDescription:text': 'Hand & Stone Massage and Facial Spa', 'secondaryDescription:text': 'Greater Pittsburgh Region (On-site)', 'jobPosting:posterId': '630552098', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:404782'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243878385', 'jobPostingTitle': 'Front Desk Receptionist', 'primaryDescription:text': 'Parr Law Firm', 'secondaryDescription:text': 'Opelika, AL (On-site)', 'jobPosting:posterId': '645267303', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:107418682'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241158289', 'jobPostingTitle': 'Luxury Watch Sales Professional', 'primaryDescription:text': 'Zadok Jewelers', 'secondaryDescription:text': 'Austin, TX (On-site)', 'jobPosting:posterId': '171433443', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:608252'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241157619', 'jobPostingTitle': 'Front Office Coordinator', 'primaryDescription:text': 'All Play Inc.', 'secondaryDescription:text': 'Houston, TX (On-site)', 'jobPosting:posterId': '45738360', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:97205236'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243871639', 'jobPostingTitle': 'Experienced Automotive Technician', 'primaryDescription:text': "Len's Auto Repair", 'secondaryDescription:text': "O'Fallon, MO (On-site)", 'jobPosting:posterId': '258194203', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:2651289'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243877526', 'jobPostingTitle': 'Executive Assistant', 'primaryDescription:text': 'CryoFuture', 'secondaryDescription:text': 'Irvine, CA (On-site)', 'jobPosting:posterId': '182416278', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:86277663'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241155611', 'jobPostingTitle': 'eCommerce Optimization Specialist', 'primaryDescription:text': "Mano's Wine", 'secondaryDescription:text': 'Kansas City, MO (On-site)', 'jobPosting:posterId': '27107882', 'logo:attributes:0:detailDataUnion:companyLogo': {}},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4240085583', 'jobPostingTitle': 'Backend Engineer (Mid-Level) [32284]', 'primaryDescription:text': 'Stealth AI Startup', 'secondaryDescription:text': 'San Francisco Bay Area (Remote)', 'jobPosting:posterId': '581098852', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:96670793'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241156454', 'jobPostingTitle': 'Human Resource Specialist', 'primaryDescription:text': 'Detroit Transportation Corporation', 'secondaryDescription:text': 'Detroit, MI (Hybrid)', 'jobPosting:posterId': '59040559', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:631058'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243860556', 'jobPostingTitle': 'Sous Chef', 'primaryDescription:text': 'JonesCraft', 'secondaryDescription:text': 'Hilton Head Island, South Carolina Area (On-site)', 'jobPosting:posterId': '1023404321', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:59385454'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243879287', 'jobPostingTitle': 'Senior Leadership Team', 'primaryDescription:text': 'Upstate Federal Credit Union', 'secondaryDescription:text': 'Anderson, SC (On-site)', 'jobPosting:posterId': '661766513', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:5943188'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241146993', 'jobPostingTitle': 'Data Engineer', 'primaryDescription:text': 'Bamboo Crowd', 'secondaryDescription:text': 'United States (Remote)', 'jobPosting:posterId': '625771200', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:4999432'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243800752', 'jobPostingTitle': 'Data Engineer (USA)', 'primaryDescription:text': 'Lensa', 'secondaryDescription:text': 'Stamford, CT (On-site)', 'jobPosting:posterId': '251038915', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:5192530'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243880819', 'jobPostingTitle': 'Software Engineer', 'primaryDescription:text': 'TalentAlly', 'secondaryDescription:text': 'Richmond, VA (Hybrid)', 'jobPosting:posterId': '188807379', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:2043953'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243873024', 'jobPostingTitle': 'Software Engineer II', 'primaryDescription:text': 'NBME', 'secondaryDescription:text': 'Philadelphia, PA (On-site)', 'jobPosting:posterId': '992514996', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:21235'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243863806', 'jobPostingTitle': '𝗧𝗿𝘂𝗰𝗸 𝗗𝗿𝗶𝘃𝗲𝗿 / 𝗕𝗼𝗼𝗺 𝗠𝗼𝘄𝗲𝗿 𝗗𝗲𝗺𝗼 𝗗𝗿𝗶𝘃𝗲𝗿 for the US West Coast.', 'primaryDescription:text': 'ATMAX Equipment Co.', 'secondaryDescription:text': 'San Francisco, CA (Hybrid)', 'jobPosting:posterId': '25314858', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:42397047'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241157182', 'jobPostingTitle': 'AI Engineer', 'primaryDescription:text': 'Intragen', 'secondaryDescription:text': 'United Kingdom (Remote)', 'jobPosting:posterId': '1070867', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:117290'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243876712', 'jobPostingTitle': 'Finance Specialist', 'primaryDescription:text': 'Society of American Florists', 'secondaryDescription:text': 'Alexandria, VA (Hybrid)', 'jobPosting:posterId': '958730989', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:71455'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243868651', 'jobPostingTitle': 'Veterinary Assistant and Veterinary Technician', 'primaryDescription:text': 'Nonantum Veterinary Clinic', 'secondaryDescription:text': 'Landenberg, PA (On-site)', 'jobPosting:posterId': '593303413', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:9153228'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4240079007', 'jobPostingTitle': 'Physical Therapist', 'primaryDescription:text': 'St. Coletta of Greater Washington', 'secondaryDescription:text': 'Washington, DC (On-site)', 'jobPosting:posterId': '1300437148', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:1918455'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4243869449', 'jobPostingTitle': 'Analytics Engineer', 'primaryDescription:text': 'Tort Experts', 'secondaryDescription:text': 'United States (Remote)', 'jobPosting:posterId': '685378618', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:75557987'},
                    {'jobPostingUrn': 'urn:li:fsd_jobPosting:4241150859', 'jobPostingTitle': 'Data Engineer', 'primaryDescription:text': 'Waterleau', 'secondaryDescription:text': 'Porto, Portugal (Hybrid)', 'jobPosting:posterId': '1503389560', 'logo:attributes:0:detailDataUnion:companyLogo': 'urn:li:fsd_company:124114'}]

if __name__ == "__main__":
    test_company_job_listing_processing()