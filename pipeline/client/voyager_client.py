from __future__ import annotations

import logging
import pickle
import time

import redis
import requests
from captcha_if_you_can import CaptchaIfYouCan
from configuration.pipeline_conf import (AUTH_BASE_URL, AUTH_REQUEST_HEADERS,
                                         REQUEST_HEADERS, SELENIUM_FALLBACK,
                                         USE_CACHED_COOKIES,
                                         USE_SELENIUM_LOGIN)

logger = logging.getLogger(__name__)
# Set up logger to log to command line (stdout)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.propagate = False


class CookieJar:
    def __init__(self):
        self.r_conn = self.try_redis()
        if self.r_conn is not None:
            self.get_func = self.redis_get
            self.get_func = self.redis_get
        else:
            self.get_func = self.file_get
            self.set_func = self.file_set
        self.validate = lambda x: x["JSESSIONID"] is not None

    def try_redis(self):
        r_conn = redis.Redis(host="localhost", port=7777)
        try:
            _ = r_conn.get("cookies")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Error connecting to Redis: {e}")
            r_conn = None
        return r_conn

    # Set
    def set_cached_cookies(self, cookies):
        self.set_func(cookies)

    def redis_set(self, cookies):
        self.r_conn.set("cookies", pickle.dumps(cookies))

    def file_set(self, cookies):
        with open("cookie_jar.pkl", "wb") as f:
            pickle.dump(cookies, f)

    # Get
    def get_cached_cookies(self):
        cookies = self.get_func()
        if not self.validate(cookies):
            logger.warning("Cached cookies are invalid, request new cookies")
            return None
        msg = (
            "Using cached cookies" if cookies is not None else "No cached cookies found"
        )
        logger.info(msg)
        return cookies

    def redis_get(self):
        cookies = self.r_conn.get("cookies")
        if cookies:
            cookies = pickle.loads(cookies)
        return cookies

    def file_get(self):
        try:
            with open("cookie_jar.pkl", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError as e:
            logger.warning(f"Error getting cookies from file: {e}.")
            return None


class CustomAuth:
    """
    Class to act as a client for the Linkedin API.
    """

    def __init__(
        self,
        username,
        password,
        debug=True,
        proxies={},
        login_with_selenium=USE_SELENIUM_LOGIN,
        use_cookie_cache=USE_CACHED_COOKIES,
    ):
        DEBUG = debug

        self.logger = logger
        if DEBUG:
            self.logger.setLevel(logging.DEBUG)

        self.username = username
        self.password = password
        requests.packages.urllib3.disable_warnings()
        # self.session = requests_cache.CachedSession('linkedin_cache', expire_after=timedelta(hours=1))
        self.session = requests.session()
        self.session.verify = not debug
        self.session.proxies.update(proxies)
        self.session.headers.update(REQUEST_HEADERS)
        self.login_with_selenium = login_with_selenium
        self.status = None
        self.cookie_jar = None

        if use_cookie_cache:
            self.cookie_jar = CookieJar()

    @property
    def cookies(self):
        return self.session.cookies

    def get_cookies(self, request=False):
        # If cache is available, use it
        cookies = None
        if self.cookie_jar is not None:
            cookies = self.cookie_jar.get_cached_cookies()
            if cookies is not None:
                if cookies.get("JSESSIONID") is None:
                    logger.info(
                        "No JSESSIONID found in cookies, requesting new cookies"
                    )
                    request = True
                else:
                    logger.info("Using cached cookies")

        if request:
            logger.info("Requesting new cookies")
            res = requests.get(
                f"{AUTH_BASE_URL}/uas/authenticate",
                headers=AUTH_REQUEST_HEADERS,
            )
            cookies = res.cookies
        return cookies

    def set_cookies(self, cookiejar: dict | requests.cookies.RequestsCookieJar = None):
        """
        Set cookies of the current session and save them to a file.
        """
        # used cookies passed if available
        if isinstance(cookiejar, dict):
            self.session.cookies.update(cookiejar)
        elif cookiejar is None:
            # if no cookies are passed, check cache or request new cookies
            cookiejar = self.get_cookies(request=True)
        self.session.cookies = cookiejar

        self.session.headers["csrf-token"] = self.session.cookies["JSESSIONID"].strip(
            '"'
        )
        if self.cookie_jar is not None:
            self.cookie_jar.set_cached_cookies(cookiejar)

    def check_credentials(self):
        try:
            assert self.username is not None
            assert self.password is not None
        except Exception as e:
            logger.error(
                """Error: no available username and password.
                                Please set environment variabeles LINKEDIN_USERNAME
                                and LINKEDIN_PASSWORD"""
            )
            raise e

    def authenticate(self):
        """
        Authenticate with Linkedin.

        Return a session object that is authenticated.
        """
        self.check_credentials()
        self.get_cookies(request=True)

        if self.login_with_selenium:
            return self.selenium_authenticate()
        else:
            return self.traditional_authenticate()

    def selenium_authenticate(self):
        captcha_if_you_can = CaptchaIfYouCan(self.username, self.password)
        session = captcha_if_you_can.selenium_login()
        self.session = session
        self.set_cookies(session.cookies)
        return session.cookies

    def traditional_authenticate(self):
        payload = {
            "session_key": self.username,
            "session_password": self.password,
            "JSESSIONID": self.session.cookies.get("JSESSIONID"),
        }

        res = requests.post(
            f"{AUTH_BASE_URL}/uas/authenticate",
            data=payload,
            cookies=self.session.cookies,
            headers=AUTH_REQUEST_HEADERS,
            verify=False,
        )

        data = res.json()

        if data and data["login_result"] != "PASS":
            chal_url = data["challenge_url"]
            chal_url_params = chal_url.split("&")
            for param in chal_url_params:
                key, value = param.split("=")
                if key == "csrfToken":
                    # new csrf token
                    self.challenge_token = value
                    break

            payload["_token"] = self.challenge_token
            logger.warning("challenge exception, re-authenticating")
            time.sleep(2)
            res = requests.post(
                f"{AUTH_BASE_URL}/uas/authenticate",
                data=payload,
                cookies=self.session.cookies,
                headers=AUTH_REQUEST_HEADERS,
                verify=False,
            )

        if res.status_code == 401:
            logger.error("Second challenge exception while authenticating.")
            if SELENIUM_FALLBACK:
                logger.error("Pausing then trying selenium login.")
                time.sleep(2)
                try:
                    return self.selenium_authenticate()
                except Exception as e:
                    logger.error(
                        """Your best chance at resolution is to log out
                                    and log back in on your browser. You may also need
                                    to delete all listed "Devices that remember your password"
                                    under Sign in & security."""
                    )
                    raise e
            res.raise_for_status()

        if res.status_code != 200:
            logger.error(
                f"Unknown exception while authenticating  {res.status_code}, {res.text}"
            )
            self.status = res.status_code
            raise res.raise_for_status()
        else:
            cookies = res.cookies
            self.set_cookies(cookies)

        return cookies
