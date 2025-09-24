
## Project Structure

```
linkedInScraper
│   README.md
│   requirements.txt
|   .envrc
|
└───data
|   |
│   └───browser_api_calls
│   └───test_data
|   └───pipeline_output
|         |
|         └───endpoint responses
|
└───docs
│   |   *.md
|
└───pipeline
|   |   voyager_client.py
|   |   voyager_pipeline.py
│   └───configuration
|   |     |   linkedin_source.schema.yaml
|   |     |   endpoint_conf.py
|   |     |   pipeine_conf.py
|   |
│   └───analytics
|         |   saved_queries.py
|         |   gql_utils.py
│
└───tests
```


- **`pipeline/`**
  - `voyager_pipeline.py`: Main pipeline orchestration and entrypoint
  - `voyager_client.py`: Cookie-based auth client for LinkedIn
  - `configuration/`
    - `endpoint_conf.py`: Endpoint definitions, selectors, pagination, mappings
    - `pipeline_conf.py`: Global settings, API base URLs, headers, batch sizes
    - `linkedin_source.schema.yaml`: dlt schema configuration
  - `analytics/`
    - `gql_utils.py`: Build GraphQL URLs and extract nested data
    - `saved_queries.py`: DuckDB query helpers (filters and CSV generation)

- **`data/`**
  - `pipeline_output/`: Artifacts and outputs created by pipeline runs
  - `browser_api_calls/`: Research artifacts for browser-captured requests
  - `test_data/`: Sample payloads and fixtures used for development/tests

- **`tests/`**
  - `test_gql_functions.py`: Unit tests for query building and extraction
  - Sample JSONs for jobs/companies

- **Root files**
  - `linkedin.duckdb`: Main DuckDB database (created/updated by the pipeline)
  - `.dlt/`: dlt runtime config (`config.toml`, optional `secrets.toml`)
  - `requirements.txt`, `.envrc`, `.gitignore`
