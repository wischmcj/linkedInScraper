from __future__ import annotations

import logging
import time
from string import Template

from configuration.pipeline_conf import EVADE_TIME
from dlt.sources.helpers.requests import Request
from dlt.sources.helpers.rest_client.paginators import RangePaginator

logger = logging.getLogger(__name__)


def avoid_ban(sleepy_time=EVADE_TIME):
    time.sleep(sleepy_time)


class VoyagerEncoder:
    def __init__(self):
        self.url_template = None

    def param_to_str(self, params: dict, depth=0):
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
                sub_param_values.append(
                    f"{k}{eq}({self.param_to_str(v,depth=depth+1)})"
                )
            else:
                sub_param_values.append(f"{k}{eq}{v}")
        sub_param_values = f"{sep}".join(sub_param_values)
        return f"{sub_param_values}"

    def build_gql_url(
        self,
        params: dict,
        base_url="https://www.linkedin.com/voyager/api/graphql",
        endpoint="graphql",
    ):
        """
        Builds a gql url from a dictionary of parameters
        """
        endpoint_url = f"{base_url}/{endpoint}"

        params_str = self.param_to_str(params)
        url_no_start = f"{endpoint_url}?{params_str}"
        url_template = Template(url_no_start)
        return url_template

    def encode(self, request):
        """
        Retrieves a url in the format accepted by
            LinkedIn's Voyager API
        """
        params = request.json
        request.json = None
        endpoint = request.url.split("/")[-1]
        base_url = request.url.replace(f"/{endpoint}", "")
        self.url_template = self.build_gql_url(params, base_url, endpoint)


class LinkedInPaginator(RangePaginator):
    """
    This class is used to interface with the LinkedIn API
    In addition to paginating, it also encodes the url parameters
        in order to match the LinkedIn API's request format
    """

    def __init__(self, inspect_response, single_page=False, *args, **kwargs):
        logger.info("Initializing LinkedInPaginator")
        super().__init__(*args, **kwargs)
        self.inspect_response = inspect_response
        self.single_page = single_page
        self.encoder = VoyagerEncoder()

    def _stop_after_this_page(self, data) -> bool:
        return (self.stop_after_empty_page and not data) or self.single_page

    def init_request(self, request: Request) -> None:
        """Generates a rest_li encoded url template based off of
        the inputs passed via the requests json
        """
        self._has_next_page = True
        self.current_value = self.initial_value
        self.encoder.encode(request)
        self.update_request(request)

    def update_request(self, request: Request) -> None:
        """
        Runs before each request
        Insert url parameters (namely, start and page count) into url
        """
        url_template = self.url_encoder.url_template
        request.url = url_template.substitute(**{self.param_name: self.current_value})
        print(request.url)

    def update_state(self, response, data):
        "Runs after each request"
        if self.inspect_response:
            print(response.content)
        # Uses self.total_path to update pagination state
        super().update_state(response, data)
        if (
            "voyagerOrganizationDashCompanies.32a7cdaea60de8f9ce50df019654c45d"
            in self.url_template.safe_substitute()
        ):
            self._has_next_page = False
        avoid_ban()
