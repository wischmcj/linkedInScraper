from __future__ import annotations

import json

from gql_utils import url_to_config


def remove_null_keys(obj):
    """
    Recursively remove keys with value None from dictionaries and lists.
    """
    if isinstance(obj, dict):
        return {k: remove_null_keys(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [remove_null_keys(item) for item in obj]
    else:
        return obj


def extract_linkedin_gql_examples(
    har_path, output_path=None, filter_str="", limit=None
):
    """
    Extracts example LinkedIn GraphQL URLs, variables, queries, and example responses from a HAR file.

    Args:
        har_path (str): Path to the HAR file.
        output_path (str, optional): If provided, writes the extracted examples to this file as JSON.
        limit (int): Number of examples to extract.

    Returns:
        list: List of dicts with keys: url, variables, queryId, example_response.
    """
    with open(har_path, encoding="utf-8") as f:
        har = json.load(f)

    examples = {}
    entries = har.get("log", {}).get("entries", [])
    for entry in entries:
        req = entry.get("request", {})
        res = entry.get("response", {})
        url = req.get("url", "")

        if filter_str in url or filter_str == "":
            if "voyager/api/graphql" not in url:
                continue
            # Try to extract variables and queryId from URL
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            variables = None
            queryId = None
            if "variables" in qs:
                try:
                    # variables can be a stringified dict or tuple
                    variables_str = qs["variables"][0]
                    # Try to parse as JSON, fallback to raw string
                    try:
                        variables = json.loads(variables_str)
                    except Exception:
                        variables = variables_str
                except Exception:
                    variables = None
            if "queryId" in qs:
                queryId = qs["queryId"][0]

            params = url_to_config([url])[0]

            # Get example response from content.text
            content = res.get("content", {})
            example_response = None
            if "text" in content:
                try:
                    # Try to parse as JSON, fallback to raw string
                    example_response = json.loads(content["text"])
                except Exception:
                    example_response = content["text"]
                    break
                example_response = remove_null_keys(example_response)
                # example_response['meta'] = {}
                # if len(example_response['included']) >0 :

            # example = {
            #     "url": url,
            #     "params": params,
            #     "variables": variables,
            #     "queryId": queryId,
            #     "example_response": example_response,
            # }
            meta = example_response.get("meta")
            if meta is not None:
                types = meta.get("microSchema").get("types")
                examples.update(types)
        if limit is not None:
            if len(examples) >= limit:
                break

    breakpoint()
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2)

    return examples


# Example usage:

# examples = extract_linkedin_gql_examples("data/browser_api_calls/company_page_network_calls.har", limit=1)
# print(json.dumps(examples, indent=2))

if __name__ == "__main__":
    examples = extract_linkedin_gql_examples(
        "data/browser_api_calls/company/company_page_network_calls.har",
        output_path="data/browser_api_calls/company/company_page_network_calls_examples.json",
        #  filter_str = 'voyagerOrganizationDashCompanies'
    )
    # print(json.dumps(examples, indent=2))
