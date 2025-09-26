import json
import os
import pytest

from pipeline.analytics.gql_utils import build_gql_url

base_url = "https://www.linkedin.com/voyager/api"
with open('data/browser_api_calls/profile_gql_queries_decoded.json','rb') as f:
    test_cases = json.load(f)

for case in test_cases:
    expected_url = case["url"]
    params = case["json"]
    endpoint = case.get("endpoint", "graphql")

    # Compose the url using build_gql_url
    # Remove 'url' and 'endpoint' from parsed if present
    url_template = build_gql_url(params, base_url=base_url, endpoint=endpoint)
    built_url = url_template.safe_substitute()
    case["built_url"] = built_url


with open('data/browser_api_calls/profile_gql_queries_tested.json','w') as f:
    json.dump(test_cases, f)



class TestBuildGqlUrlFromDecodedJson:

    @pytest.mark.parametrize("case", [
                            pytest.param(case, id=str(i)) for i, case in enumerate(
                                test_cases
                            )])
    def test_build_gql_url_matches_source(self, case):
        # The entry is a dict with keys: 'url', 'parsed', 'endpoint'
        expected_url = case["url"]
        params = case["json"]
        endpoint = case.get("endpoint", "graphql")

        # Compose the url using build_gql_url
        # Remove 'url' and 'endpoint' from parsed if present
        url_template = build_gql_url(params, base_url=base_url, endpoint=endpoint)
        built_url = url_template.safe_substitute()

            
        assert expected_url == built_url, f"\nExpected: {expected_url}\nGot:      {built_url}"


        # The built_url may not match exactly due to ordering of query params, so compare after parsing
        # from urllib.parse import urlparse, parse_qs

        # def normalize_url(u):
        #     parsed = urlparse(u)
        #     return (
        #         parsed.scheme,
        #         parsed.netloc,
        #         parsed.path,
        #         frozenset(parse_qs(parsed.query, keep_blank_values=True).items())
        #     )

        # assert normalize_url(built_url) == normalize_url(url), f"\nExpected: {url}\nGot:      {built_url}"
