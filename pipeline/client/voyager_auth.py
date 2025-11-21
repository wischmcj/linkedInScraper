from __future__ import annotations

import logging
import pickle
import time

import redis
import requests
from client.captcha_if_you_can import CaptchaIfYouCan

# Use the centralized logger for this module
logger = logging.getLogger("linkedin_scraper.client.voyager_auth")


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
        login_with_selenium,
        use_cookie_cache,
        allow_manual_captcha,
        headless,
        auth_base_url,
        request_headers,
        auth_request_headers,
    ):
        self.status = None
        self.logger = logger

        self.username = username
        self.password = password
        self.login_with_selenium = login_with_selenium
        self.use_cookie_cache = use_cookie_cache
        self.allow_manual_captcha = allow_manual_captcha
        self.headless = headless

        proxies = {}
        requests.packages.urllib3.disable_warnings()
        self.session = requests.session()
        self.session.proxies.update(proxies)
        self.session.headers.update(request_headers)

        self.auth_base_url = auth_base_url
        self.auth_request_headers = auth_request_headers

        self.cookie_jar = None
        if self.use_cookie_cache:
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
                f"{self.auth_base_url}/uas/authenticate",
                headers=self.auth_request_headers,
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
        captcha_if_you_can = CaptchaIfYouCan(
            username=self.username,
            password=self.password,
            allow_manual_captcha=self.allow_manual_captcha,
            headless=self.headless,
        )
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
            f"{self.auth_base_url}/uas/authenticate",
            data=payload,
            cookies=self.session.cookies,
            headers=self.auth_request_headers,
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
                f"{self.auth_base_url}/uas/authenticate",
                data=payload,
                cookies=self.session.cookies,
                headers=self.auth_request_headers,
                verify=False,
            )

        if res.status_code == 401:
            logger.error("Second challenge exception while authenticating.")
            logger.error(
                """Your best chance at resolution is to log out
                                    and log back in on your browser. You may also need
                                    to delete all listed "Devices that remember your password"
                                    under Sign in & security."""
            )
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
