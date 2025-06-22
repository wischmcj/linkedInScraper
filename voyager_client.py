import requests
import pickle
import logging
import redis
import dlt

from conf import API_BASE_URL, REQUEST_HEADERS, AUTH_BASE_URL, AUTH_REQUEST_HEADERS 
logger = logging.getLogger(__name__)

try:
    r_conn = redis.Redis(host='localhost', port=7777)
except Exception as e:
    logger.error(f"Error connecting to Redis: {e}")
    r_conn = None

class CustomAuth():
    """
    Class to act as a client for the Linkedin API.
    """
    def __init__(self, username, password, debug=True, proxies={}, use_cookie_cache=True):
        DEBUG = debug

        self.logger = logger
        if DEBUG:
            self.logger.setLevel(logging.DEBUG)

        self.username = username
        self.password = password
        requests.packages.urllib3.disable_warnings()
        self.session = requests.session()
        self.session.verify = not debug
        self.session.proxies.update(proxies)
        self.session.headers.update(REQUEST_HEADERS)
        self._use_cookie_cache = use_cookie_cache

    ## TODO: expand caching with hset/hgetall
    def get_cached_cookies(self, url: str):
        cookies = None
        if r_conn:  
            cookies = r_conn.get('cookies')
            if cookies:
                cookies = pickle.loads(cookies)
        else:
            logger.warning("No Redis connection, not caching cookies")
        return cookies

    def set_cached_cookies(self, data: dict) -> None:
        if r_conn:
            cookies = pickle.dumps(data)
            r_conn.set('cookies', cookies)
        else:
            logger.warning("No Redis connection, not caching cookies")

    def _get_session_cookies(self):
        """
        Return a new set of session cookies as given by Linkedin.
        """
        self.logger.debug("Attempting to use cached cookies")
        cookies = self.get_cached_cookies(self.username)
        if cookies:
            return cookies
        else:
            self.logger.debug("Cached cookies not found. Requesting new cookies.")

        res = requests.get(
            f"{AUTH_BASE_URL}/uas/authenticate",
            headers=AUTH_REQUEST_HEADERS,
        )

        return res.cookies

    def _set_session_cookies(self, cookiejar):
        """
        Set cookies of the current session and save them to a file.
        """
        self.session.cookies = cookiejar
        self.session.headers["csrf-token"] = self.session.cookies["JSESSIONID"].strip(
            '"'
        )
        self.set_cached_cookies(cookiejar)

    @property
    def cookies(self):
        return self.session.cookies

    def fix_cookies(self):
        self._set_session_cookies(self._get_session_cookies())

    def authenticate(self):
        if self._use_cookie_cache:
            self.logger.debug("Attempting to use cached cookies")
            cookies = self.get_cached_cookies(self.username)
            if cookies:
                self.logger.debug("Using cached cookies")
                self._set_session_cookies(cookies)
                return

        self.authenticate_by_request()

    def authenticate_by_request(self):
        """
        Authenticate with Linkedin.

        Return a session object that is authenticated.
        """
        self._set_session_cookies(self._get_session_cookies())

        payload = {
            "session_key": self.username,
            "session_password": self.password,
            "JSESSIONID": self.session.cookies["JSESSIONID"],
        }

        res = requests.post(
            f"{AUTH_BASE_URL}/uas/authenticate",
            data=payload,
            cookies=self.session.cookies,
            headers=AUTH_REQUEST_HEADERS,
            verify=False
        )
        
        data = res.json()

        if data and data["login_result"] != "PASS":
            chal_url = data['challenge_url']
            chal_url_params = chal_url.split('&')
            for param in chal_url_params:
                key, value = param.split('=')
                if key == 'csrfToken':
                    # new csrf token
                    self.challenge_token = value
                    break

            payload['_token'] = self.challenge_token
            logger.warning('challenge exception, re-authenticating')
            res = requests.post(
                f"{AUTH_BASE_URL}/uas/authenticate",
                data=payload,
                cookies=self.session.cookies,
                headers=AUTH_REQUEST_HEADERS,
                verify=False
            )

        if res.status_code == 401:
            logger.error('Second challenge exception while authenticating')
            logger.error('''Your best chance at resolution is to log out 
                            and log back in on your browser. You may also need 
                            to delete all listed "Devices that remember your password"
                             under Sign in & security.''')
            raise res.raise_for_status()

        if res.status_code != 200:
            logger.error('unknown exception while authenticating')
            raise res.raise_for_status()

        self._set_session_cookies(res.cookies)

