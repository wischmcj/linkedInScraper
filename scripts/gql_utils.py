from __future__ import annotations

import logging
from string import Template

logger = logging.getLogger(__name__)

import json
from urllib.parse import parse_qs, urlparse


def decapsulate(input_vars):
    "Recursively remove surrounding parentheses"
    new_vars = input_vars
    if len(new_vars) == 0:
        return new_vars
    if new_vars[0] == "(" and new_vars[-1] == ")":
        new_vars = new_vars[1:-1]
        return decapsulate(new_vars)
    else:
        return new_vars


def split_key_from_var(as_str: str):
    return (as_str.split(":")[0], ":".join(as_str.split(":")[1:]))


def split_parenthetical(as_str: str):
    """Splits nested, comma delimited lists with elements
     grouped by parentheses. For example,
    '(key:value,key2:value2, key3:(key4:value4,key5:(1,2,3)))'
        -> ['key:value', 'key2:value2', 'key3:(key4:value4,key5:(1,2,3))']
    """
    elements = []
    open_cnt = 0
    close_cnt = 0
    word = ""
    # for v in var_list:
    #     if '(' in v:
    #         elements = []
    #         word = ''
    for char in as_str:
        if char == "(":
            open_cnt += 1
        elif char == ")":
            close_cnt += 1
        elif char == ",":
            if open_cnt == 0:
                print("word", word)
                elements.append(word)
                print("words_found", elements)
                word = ""
                open_cnt = 0
                close_cnt = 0
                continue

        word += char

        if open_cnt > 0:
            if open_cnt == close_cnt:
                elements.append(word)
                word = ""
                open_cnt = 0
                close_cnt = 0
    if word != "":
        elements.append(word)
    ele_tups = [split_key_from_var(ele) for ele in elements]
    print("words_found", elements)
    return ele_tups


def denest_vars(init_vars):
    print(f"denesting {init_vars}")
    input_vars = init_vars
    if input_vars == "()":
        return input_vars

    if isinstance(input_vars, list):
        if len(input_vars) == 1:
            input_vars = input_vars[0]
        else:
            return dict([denest_vars(v) for v in input_vars])

    is_list = False
    if input_vars[:4] == "List":
        is_list = True
        input_vars = input_vars[4:]

    # remove surrounding parentheses, if present
    input_vars = decapsulate(input_vars)

    if "," not in input_vars and ":" not in input_vars:
        return init_vars
    if "," in input_vars:
        split_vars = split_parenthetical(input_vars)
        ret = []
        if is_list:
            for k, v in split_vars:
                if v == "":
                    ret.append(k)
                else:
                    ret.append({k: denest_vars(v)})
        else:
            ret = {k: denest_vars(v) for k, v in split_vars}
        return ret
    else:
        k, v = split_key_from_var(input_vars)
        return {k: v}


def parse_gql_url(url: str):
    parsed = urlparse(url)
    urllib_query = parse_qs(parsed.query)

    variables = urllib_query.get("variables")
    split_vars = variables
    if variables:
        split_vars = denest_vars(variables[0])
    if isinstance(split_vars, tuple):
        split_vars = {split_vars[0]: split_vars[1]}

    addnl_params = {
        param: (vals[0] if len(vals) == 1 else vals)
        for param, vals in urllib_query.items()
    }
    if split_vars is not None:
        addnl_params["variables"] = split_vars
    return addnl_params


def url_to_config(urls: str):
    parsed_urls = []
    for url in urls:
        parsed = parse_gql_url(url)

        if "voyagerMessagingGraphQL" in url:
            endpoint = "voyagerMessagingGraphQL"

        ret = {
            "endpoint": "graphql" if "graphql" in url else "voyagerJobsDashJobCards",
            "json": parsed,
            "url": url,
        }
        print(ret)
        parsed_urls.append(ret)

    return parsed_urls


def param_to_str(params: dict, depth=0):
    sub_param_values = []
    if depth == 0:
        sep = "&"
        eq = "="
    else:
        sep = ","
        eq = ":"
    depth += 1
    for k, v in params.items():
        if isinstance(v, list):
            sub_param_values.append(
                f'{k}{eq}List({",".join([str(item) for item in v])})'
            )
        elif isinstance(v, dict):
            sub_param_values.append(f"{k}{eq}({param_to_str(v,depth=depth+1)})")
        else:
            sub_param_values.append(f"{k}{eq}{v}")
    sub_param_values = f"{sep}".join(sub_param_values)
    return f"{sub_param_values}"


def build_gql_url(
    params: dict,
    base_url="https://www.linkedin.com/voyager/api/graphql",
    endpoint="graphql",
):
    """
    Builds a gql url from a dictionary of parameters
    """
    endpoint_url = f"{base_url}/{endpoint}"

    params_str = param_to_str(params)
    url_no_start = f"{endpoint_url}?{params_str}"
    url_template = Template(url_no_start)
    return url_template


if __name__ == "__main__":
    with open("data/browser_api_calls/company_page_network_calls.har") as f:
        urls = json.load(f)
    file = "data/browser_api_calls/company_page_network_calls.har"
    urls = [
        "https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(query:(origin:JOB_SEARCH_PAGE_JOB_FILTER,locationUnion:(geoUrn:urn%3Ali%3Afsd_geo%3A92000000),selectedFilters:List((key:company,value:List(9414302,34610298))),spellCorrectionEnabled:true))&queryId=voyagerJobsDashJobCards.67b88a170c772f25e3791c583e63da26"
    ]
    urls = url_to_config(urls)
    breakpoint()
    with open("data/browser_api_calls/profile_gql_queries_decoded.json", "w") as f:
        json.dump(urls, f)
    breakpoint()

    base_url = "https://www.linkedin.com/voyager/api"
    with open("data/browser_api_calls/profile_gql_queries_decoded.json", "rb") as f:
        test_cases = json.load(f)

    # success_cases = []
    # fail_cases = []
    # for case in test_cases:
    #     expected_url = case["url"]
    #     params = case["json"]
    #     endpoint = case.get("endpoint", "graphql")

    #     if "voyagerMessagingGraphQL" in expected_url:
    #         endpoint = "voyagerMessagingGraphQL/graphql"
    #     # Compose the url using build_gql_url
    #     # Remove 'url' and 'endpoint' from parsed if presenttest_cases
    #     vars = params.get("variables", None)
    #     if vars is not None and isinstance(vars, dict):
    #         case["old_vars"] = copy(vars)
    #         try:
    #             for k, v in vars.items():
    #                 if isinstance(v, dict):
    #                     vars[k] = urlencode(v).replace("=", "%3A")
    #                 elif isinstance(v, str):
    #                     if "urn" in v:
    #                         vars[k] = v.replace(":", "%3A")
    #         except Exception as e:
    #             breakpoint()
    #             print(e)
    #         params["variables"] = vars

    #     url_template = build_gql_url(params, base_url=base_url, endpoint=endpoint)

    #     built_url = url_template.safe_substitute()
    #     case["built_url"] = built_url
    #     if expected_url == built_url:
    #         success_cases.append(case)
    #     else:
    #         fail_cases.append(case)

    # total_cases = len(success_cases) + len(fail_cases)

    # print(f"{len(success_cases)}/{total_cases} success")

    # with open("data/browser_api_calls/profile_gql_queries_success.json", "w") as f:
    #     json.dump(success_cases, f)

    # with open("data/browser_api_calls/profile_gql_queries_fail.json", "w") as f:
    #     json.dump(fail_cases, f)
