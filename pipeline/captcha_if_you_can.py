from __future__ import annotations

import time

import requests
from configuration.pipeline_conf import MANUAL_CAPTCHA_IF_YOU_CAN
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CaptchaIfYouCan:
    def __init__(self, username, password, headless=False):
        self.username = username
        self.password = password
        self.driver = self.init_driver(headless)

    def init_driver(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--slowMo=15")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def transfer_session_to_selenium(self, driver):
        for cookie in self.session.cookies:
            driver.add_cookie(
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                }
            )
        headers = self.session.headers
        driver._client.set_header_overrides(headers=headers)

    def transfer_session_to_requests(self, driver):
        selenium_cookies = driver.get_cookies()
        selenium_user_agent = driver.execute_script("return navigator.userAgent;")

        sesh = requests.Session()
        sesh.headers.update({"User-Agent": selenium_user_agent})
        for cookie in selenium_cookies:
            sesh.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"])
        sesh.headers["csrf-token"] = sesh.cookies["JSESSIONID"].strip('"')
        self.session = sesh
        self.set_cookies(sesh.cookies)
        return sesh

    def selenium_login(self):
        self.driver = self.driver or webdriver.Chrome()
        driver = self.driver
        driver.get("https://www.linkedin.com/login")

        # Enter email
        wait = WebDriverWait(driver, timeout=3)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_input.clear()
        email_input.send_keys(self.username)
        # Enter password
        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)

        try:
            # Check for captcha iframe
            wait = WebDriverWait(driver, timeout=3)
            iframe1 = wait.until(
                EC.presence_of_element_located((By.ID, "captcha-internal"))
            )
        except TimeoutException:
            print("No captcha found, assuming no captcha is required")
            iframe1 = None

        if iframe1 is not None:
            # if a captcha iframe is found, try to solve it
            try:
                time.sleep(2)
                driver.switch_to.frame(iframe1)
                iframe2 = driver.find_element(
                    By.XPATH, "//iframe[contains(@title,'reCAPTCHA')]"
                )
                driver.switch_to.frame(iframe2)
                captcha_box = driver.find_element(By.ID, "recaptcha-anchor")
                captcha_box.click()
            except Exception as e:
                print(f"Captcha found, error solving: {e}")
                if MANUAL_CAPTCHA_IF_YOU_CAN:
                    print("Solve manually and type c, then press enter to continue")
                    breakpoint()  # noqa
                else:
                    raise e

        time.sleep(10)
        self.driver = driver
        session = self.transfer_session_to_requests(driver)
        self.session = session
        return session.cookies
