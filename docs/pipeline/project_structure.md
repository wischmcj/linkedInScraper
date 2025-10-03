
## Project Structure

```
linkedInScraper
│   README.md
│   requirements.txt
│   .envrc
│   linkedin.duckdb
│   linkedin_cache.sqlite
│   dump.rdb
│   venv/
│   *.csv (generated output files)
│
├───alt_scrape/
│   │   gql_analysis.py
│   │   nlp.py
│
├───data/
│   ├───browser_api_calls/ # .har network sessions + extracted json
│   │   ├───company/
│   │   ├───jobs/
│   │   ├───profile/
│   │   ├───schemata/
│   │   │   └──<endpoint>_schema.json
│   │   ├───extract_data_from_har.sh
│   │   └─── README.md
│   ├───endpoint_responses/  # example json responses
│   │   ├───companies/
│   │   ├───job_details/
│   │   ├───job_listings/
│   │   └───other/
│   └───example_output/
│       └───*.csv # landed job listings
├───docs/
│   ├───company_page_api_calls_summary.md
│   ├───component_urns.md
│   ├───configuration.md
│   ├───messages_endpoints.md
│   ├───organization_endpoints.md
│   ├───project_structure.md
│   └───setup.md
│
├───pipeline/
│   ├───analytics/
│   │   ├───gql_utils.py
│   │   ├───har_extract.py
│   │   └───saved_queries.py
│   ├───configuration/
│   │   ├───linkedin_source.schema.yaml
│   │   ├───column_mapping.py
│   │   ├───endpoint_conf.py
│   │   └───pipeline_conf.py
│   ├───captcha_if_you_can.py
│   ├───helpers.py
│   ├───voyager_client.py
│   └───voyager_pipeline.py
│
└───tests/
    ├───__init__.py
    ├───companies_voyagerIdentityDashProfileComponents.json
    ├───jobs_voyagerJobsDashJobCards.json
    ├───test_gql_functions.py
    └───test_url_to_config.py
```


- **`alt_scrape/`** (Alternative scraping approaches)
  - `gql_analysis.py`: GraphQL query analysis and URL parsing utilities
  - `nlp.py`: Natural language processing for job descriptions and skills analysis

- **`pipeline/`**
  - `voyager_pipeline.py`: Main pipeline orchestration and entrypoint
  - `voyager_client.py`: Cookie-based auth client for LinkedIn
  - `captcha_if_you_can.py`: Selenium-based captcha solver and session management
  - `helpers.py`: Utility classes including LinkedInPaginator and LoadInfoProcessor
  - `configuration/`
    - `endpoint_conf.py`: Endpoint definitions, selectors, pagination, mappings
    - `pipeline_conf.py`: Global settings, API base URLs, headers, batch sizes
    - `linkedin_source.schema.yaml`: dlt schema configuration
    - `column_mapping.py`: Data transformation and column mapping utilities
  - `analytics/`
    - `gql_utils.py`: Build GraphQL URLs and extract nested data
    - `saved_queries.py`: DuckDB query helpers (filters and CSV generation)
    - `har_extract.py`: Extract GraphQL examples from HAR files for analysis

- **`data/`**
  - `pipeline_output/`: Artifacts and outputs created by pipeline runs (*.csv files)
  - `browser_api_calls/`: Research artifacts for browser-captured requests
    - `company/`: Company page network calls and responses
    - `jobs/`: Job-related GraphQL queries and responses
    - `profile/`: Profile-related queries and responses
    - `schemata/`: JSON schemas for different page types
    - `extract_data_from_har.sh`: Shell script for HAR file processing
  - `endpoint_responses/`: Structured API response data
    - `companies/`: Company data responses
    - `job_details/`: Detailed job information responses
    - `job_listings/`: Job listing responses
  - `example_output/`: Sample CSV outputs for different job categories
  - `test_data/`: Sample payloads and fixtures used for development/tests

- **`tests/`**
  - `test_gql_functions.py`: Unit tests for query building and extraction
  - `test_url_to_config.py`: Tests for URL to configuration mapping
  - `companies_voyagerIdentityDashProfileComponents.json`: Sample company data
  - `jobs_voyagerJobsDashJobCards.json`: Sample job data

- **Root files**
  - `linkedin.duckdb`: Main DuckDB database (created/updated by the pipeline)
  - `linkedin_cache.sqlite`: SQLite cache database
  - `dump.rdb`: Redis database dump
  - `venv/`: Python virtual environment
  - `*.csv`: Generated output files (data_*, ml_*, rs_*, software_*, new_jobs_*)
  - `requirements.txt`, `.envrc`, `.gitignore`
