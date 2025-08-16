
## Project Structure

- **`pipeline/`**
  - `voyager_pipeline.py`: Main pipeline orchestration and entrypoint
  - `voyager_client.py`: Cookie-based auth client for LinkedIn
  - `conf.py`: Endpoint definitions, selectors, request headers, pagination
  - `linkedin_source.schema.yaml`: dlt schema configuration
  - `analytics/`
    - `gql_utils.py`: Build GraphQL URLs and extract nested data
    - `nlp.py`: NLP utility functions for analysis (tags/categories)
    - `saved_queries.py`: DuckDB query helpers (filters and CSV generation)

- **`data/`**
  - `output/`: CSV exports and raw API captures
    - `gql_responses/`: Raw GraphQL responses organized by type
      - `companies/`, `job_listings/`, `job_details/`, `schemata/`
  - `network_traffic/`: HAR-based research + scripts
    - `README.md`, `extract_data_from_har.sh`, `*.json` query maps

- **`alt_scrape/`**
  - `rest_scraper.py`: Alternative REST-oriented scraper (experimental)
  - `rest_scraper_old.py`, `linked_in_scraper.py`: Legacy/alternate approaches

- **`tests/`**
  - `test_gql_functions.py`: Unit tests for query building and extraction
  - Sample JSONs for jobs/companies

- **Root files**
  - `linkedin.duckdb`: Main DuckDB database (created/updated by the pipeline)
  - `.dlt/`: dlt runtime config (`config.toml`, optional `secrets.toml`)
  - `requirements.txt`, `.envrc`, `.gitignore`
