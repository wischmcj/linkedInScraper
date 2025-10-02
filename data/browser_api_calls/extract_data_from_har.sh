#!bin/bash

#Get the value of the query id parameter in each url
grep -o -E ".*url.*queryId=.*" ~/data/browser_api_calls/company_page_network_calls.har | grep -o -E "url.*queryId=(.*)"

# Get all urls with a queryId in the parameters
grep -o -E ".*url.*queryId=(.*)" ~/Downloads/www.linkedin.com.har
            job_urls = get_job_url_resource(job_urls)
