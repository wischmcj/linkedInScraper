import time
import logging

from analytics.gql_utils import build_gql_url
from dlt.sources.helpers.requests import Request
from dlt.sources.helpers.rest_client.paginators import RangePaginator


logger = logging.getLogger(__name__)

def avoid_ban(sleepy_time=.5):
    time.sleep(sleepy_time)


class LinkedInPaginator(RangePaginator):
    """
        This class is used to interface with the LinkedIn API
        In addition to paginating, it also encodes the url parameters
            in order to match the LinkedIn API's request format
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_template = None

    def encode_params(self, request):
        """
            Retrieves a url in the format accepted by 
                LinkedIn's Voyager API
        """
        params = request.json
        request.json = None
        endpoint = request.url.split('/')[-1]
        base_url = request.url.replace(f'/{endpoint}', '')
        self.url_template = build_gql_url(params,base_url,endpoint)

    def init_request(self, request: Request) -> None:
        """Generates a rest_li encoded url template based off of 
            the inputs passed via the requests json
        """
        self._has_next_page = True
        self.current_value = self.initial_value
        self.encode_params(request)
        self.update_request(request)

    def update_request(self, request: Request) -> None:
        """
            Runs before each request
            Insert url parameters (namely, start and page count) into url
        """
        request.url = self.url_template.substitute(**{self.param_name:self.current_value})
        print(request.url)

    def update_state(self, response, data):
        "Runs after each request"
        print(response.content)
        breakpoint()
        super().update_state(response, data)
        avoid_ban()

class LoadInfoProcessor():

    def __init__(self, 
                load_info,
                destination='default',
                actions = [],
                alerts = ['schema_changes',
                            'new_items']):
        self.load_info = load_info
        self.actions_functions = [getattr(self, f'action_{action}') for action in actions]
        self.alert_functions = [getattr(self, f'alert_{alert}') for alert in alerts]
        self.logger = logging.getLogger(f'{self.destination}')

    def alert_schema_changes(self, 
                             table_name,
                             column_name,
                             column):
        self.logger .info(
            f"\tTable updated: {table_name}: "
                f"Column changed: {column_name}: "
                f"{column['data_type']}"
            )

    def alert_new_items(self, 
                             table_name,
                             column_name,
                             column):
        self.logger .info(
            f"\tTable updated: {table_name}: "
                f"Column changed: {column_name}: "
                f"{column['data_type']}"
            )

    def loop_over_load_info(self):
        for package in self.load_info.load_packages:
            # Iterate over each table in the schema_update of the current package
            for table_name, table in package.schema_update.items():
                # Iterate over each column in the current table
                for column_name, column in table["columns"].items():
                    # Send a message to the Slack channel with the table
                                # and column update information
                    for action in self.actions_functions:
                        action(table_name, column_name, column)
                    for alert in self.alert_functions:
                        alert(table_name, column_name, column)
