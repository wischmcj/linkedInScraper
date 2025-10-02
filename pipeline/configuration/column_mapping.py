from __future__ import annotations

import logging
import re
from urllib.parse import quote

from dlt.common import jsonpath

logger = logging.getLogger(__name__)


def get_json_map(key: str, allow_list=False):
    """
    Extracts a json path from the response
      - Responses are similar to graphql responses,
        so they present as a deeply nested json.
      - We use jsonpaths to extract the data we need
    """

    def json_map(response):
        val = jsonpath.find_values(key, response)
        if isinstance(val, list) and not allow_list:
            # logger.warning(
            #     f"""list returned for {key=},
            #                         {val}"""
            # )
            if len(val) > 1:
                logger.warning(
                    f"""Multiple values found for {key=},
                                    {val}"""
                )
            val = val[0]
        return val

    return json_map


def get_json_map_nested(root_path: str, nested_keys: list[str]):
    def json_map_nested(response):
        val = jsonpath.find_values(root_path, response)

        def get_nested_vals(root_val):
            nested_resp = {}
            for nested_key, nested_path in nested_keys:
                try:
                    nested_resp[nested_key] = jsonpath.find_values(
                        nested_path, root_val
                    )
                except Exception as e:
                    print("error getting nested val", nested_key, nested_path, e)
                    nested_resp[nested_key] = None
            return nested_resp

        if isinstance(val, list):
            resp = [get_nested_vals(val_item) for val_item in val]
        else:
            resp = get_nested_vals(val)
        return resp

    return json_map_nested


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
        mapped_cols = mapping.get("mapped_cols", [])
        drop_list = mapping.get("drop_list", [])
        try:
            for col_name, custom_map_func in mapped_cols:
                response[col_name] = custom_map_func(response)
        except Exception as e:
            print("error mapping cols on column", col_name, e)

        if drop_list is not None:
            for col_name in drop_list:
                try:
                    response.pop(col_name)
                except KeyError as e:
                    print("error dropping col", col_name, e)
        return response

    return map_cols
