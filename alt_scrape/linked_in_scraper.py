from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import redis 

r = redis.Redis(host='localhost', port=7777)

PROFILE_PAGE = "https://www.linkedin.com/in/collin-wischmeyer-b55659a4/"

# TODO: Context manager for driver and wait
def linkedin_login(driver, wait, email, password):
    # Go to LinkedIn login page
    wait = WebDriverWait(driver, timeout=20)
    driver.get("https://www.linkedin.com/login")

    # Enter email
    email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    email_input.clear()
    email_input.send_keys(email)

    # Enter password
    password_input = driver.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    return driver

# def collect_profile_data(driver, wait):
#     profile_card = driver.find_element(By.TAG_NAME, "section").get_attribute('data-member-id')

def get_profile_section(driver, wait, section_name, ):

    # Get interest section
    wait.until(EC.presence_of_element_located((By.ID, section_name)))
    interest_card = driver.find_element( By.ID,section_name).find_element(By.XPATH,"..")
    # Unhide companies content
    companies_btn = interest_card.find_element(By.XPATH,"//button/span[contains(text(),'Companies')]/..")
    companies_btn.click()
    return interest_card

def scroll_and_act(driver, action, wait_time=2, *args, **kwargs):
        # Scroll to load all companies
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        action(*args, **kwargs)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_time)   
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return args, kwargs

def get_company_elements(driver, total_links,*args, **kwargs):
    breakpoint()
    company_a = driver.find_elements(By.XPATH, "//li[contains(@class,'pvs-list__item--one-column')]/a")
    # Class is active_tab_companies_interests FWIW
    name = driver.find_element(By.XPATH,"//span").text
    company_a 
    for a in company_a:
        company_links = [a.get_attribute('href') for a in company_a]
        r.sadd('company_links', *company_links)
    
    total_links.extend(company_links)

def linkedin_login_and_get_followed_companies(email, password, headless=True):
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, timeout=20)

    try:
        driver = linkedin_login(driver, wait, email, password)

        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "profile-card")))
        profile_card = driver.find_element(By.CLASS_NAME, "profile-card")
        profile_url = profile_card.find_element(By.XPATH, "//a[contains(@href,'/in/')]").get_attribute('href')
        driver.get(profile_url)

        # Get interest section
        wait.until(EC.presence_of_element_located((By.ID, "interests")))
        interest_card = driver.find_element( By.ID,"interests").find_element(By.XPATH,"..")
        # Unhide companies content
        companies_btn = interest_card.find_element(By.XPATH,"//button/span[contains(text(),'Companies')]/..")
        companies_btn.click()
        # Click on the "See All Companies" link
        companies_href_class = "navigation-index-see-all-companies"
        companies_link = interest_card.find_element(By.ID,companies_href_class).get_attribute('href')
        companies_link.click()

        scroll_and_act(driver, get_company_elements, total_links=[])
        driver.get(companies_link)
        wait.until(EC.presence_of_element_located((By.ID, "scaffold-finite-scroll__content")))

        breakpoint()
        # Scroll to load all companies
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract followed companies
        companies = []
        company_elements = driver.find_elements(By.CSS_SELECTOR, "ul.reusable-search__entity-result-list li")
        for elem in company_elements:
            try:
                name_elem = elem.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a span[aria-hidden='true']")
                link_elem = elem.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a")
                company_name = name_elem.text.strip()
                company_url = link_elem.get_attribute("href")
                companies.append({"name": company_name, "url": company_url})
            except Exception:
                continue

        return companies

    finally:
        driver.quit()

if __name__ == "__main__":
    companies = linkedin_login_and_get_followed_companies(os.getenv("LINKEDIN_USERNAME"), os.getenv("LINKEDIN_PASSWORD"), headless=False)
    for company in companies:
        print(company["name"], company["url"])
