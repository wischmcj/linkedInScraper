from __future__ import annotations

import logging
import time
from string import Template

logger = logging.getLogger(__name__)


def default_evade():
    time.sleep(20)


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
