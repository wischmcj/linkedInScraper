#!bin/bash

#Get the value of the query id parameter in each url
grep -o -E ".*url.*queryId=.*" ~/Downloads/www.linkedin.com.har | grep -o -E "url.*queryId=(.*)"

# Get all urls with a queryId in the parameters
grep -o -E ".*url.*queryId=(.*)" ~/Downloads/www.linkedin.com.har
