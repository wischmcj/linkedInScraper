from __future__ import annotations

import logging
import re
from urllib.parse import quote

from dlt.common import jsonpath

logger = logging.getLogger(__name__)


def get_json_map(key):
    """
    Extracts a json path from the response
      - Responses are similar to graphql responses,
        so they present as a deeply nested json.
      - We use jsonpaths to extract the data we need
    """

    def json_map(response):
        val = jsonpath.find_values(key, response)
        if isinstance(val, list):
            if len(val) > 1:
                logger.warning(
                    f"""Multiple values found for {key=} in {response=},
                                    {val}"""
                )
            val = val[0]
        return val

    return json_map


def get_replace_func(src_col, replace_list):
    def replace_func(response):
        cur_val = response[src_col]
        for target, replacement in replace_list:
            pat = re.compile(re.escape(target), re.IGNORECASE)
            cur_val = pat.sub(replacement, cur_val)
        return cur_val

    return replace_func


def encode_job_urn(response):
    return quote(response.get("jobPostingUrn"))


def get_map_func(mapping):
    """
    Combines all of the configured column
        mapping functions into a single function.
    Allows for the use of a list of tuples to map columns
        to the response json.z

    """

    def map_cols(response, *args, **kwargs):
        try:
            for col_name, custom_map_func in mapping:
                response[col_name] = custom_map_func(response)
        except Exception as e:
            print("error mapping cols", e)
        return response

    return map_cols
