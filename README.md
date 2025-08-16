## LinkedIn Scraper

A practical LinkedIn data scraper and pipeline based on dlt (data load tool), DuckDB, and lightweight request clients. It focuses on extracting followed companies, job listings, and job details using the LinkedIn Voyager endpoints (GraphQL and REST-style) with cookie-based auth.

## Key Dependencies 
- DLT
- DuckDB
- Streamlit (optional)

### Basic capabilities
  - Easy extraction of data from LinkedIn via a DLT source/pipeline
  - Custom DLT source automatically handles REST requests, pagination, data extraction and relational DB storage
  - Predefined endpoints/available datasets include:
    - `get_companies`: scrape followed companies via GraphQL profile components
    - `get_job_urls`: fetch job cards per company
    - `get_descriptions`: fetch job descriptions and details
  - Easily extended to pull additional data 


## Set-up
See [docs/setup.md](docs/setup.md)


## Usage

The pipeline pulls in three phases depending on flags:
- **followed companies** → each company's **job listings** → each jobs **job details**

Use the built-in entrypoint in `pipeline/voyager_pipeline.py` or call `run_pipeline` directly.

### Quick start (default data)
```bash
python pipeline/voyager_pipeline.py
```

This default run in the `__main__` section fetches followed companies and their job listings. You can modify flags there or call programmatically:

```python
from pipeline.voyager_pipeline import run_pipeline

run_pipeline(
    db_name="linkedin.duckdb",
    one_at_a_time=False,
    get_companies=True,      # pull followed companies
    get_job_urls=True,       # pull jobs for those companies
    get_descriptions=False   # optionally pull job description details
)
```

Notes:
- The pipeline writes into DuckDB dataset `linkedin_data` inside `linkedin.duckdb`.
- The code uses a custom paginator to iterate Voyager responses responsibly (`avoid_ban`).
- If you encounter import path issues, ensure your working directory is the repository root and that Python can import the `pipeline` package (e.g., by setting `PYTHONPATH=$PWD`).

## Outputs

- **DuckDB**: `linkedin.duckdb` contains tables like:
  - `linkedin_data.followed_companies`
  - `linkedin_data.jobs_by_company`
  - `linkedin_data.job_description`

- **CSV exports**: Under `data/output/`, e.g. `all_jobs_YYYYMMDD.csv`, `software_jobs_YYYYMMDD.csv`, etc.
- **Raw responses**: Under `data/output/gql_responses/` by category.



## Analytics & Post-processing

Helpers in `pipeline/analytics/saved_queries.py` allow quick filtering and exports from DuckDB, for example:
- **`get_data_jobs(db_path)`**: Data-oriented roles
- **`get_software_jobs(db_path)`**: Software roles
- **`get_jobs_filtered(db_path, filter_str)`**: Custom DuckDB SQL filter

Additional utilities:
- **`gql_utils.py`**: Build LinkedIn Voyager GraphQL URLs and extract nested payload fragments
- **`nlp.py`**: Basic NLP helpers to enrich or score postings


## Ethics & Legal

Scraping LinkedIn may violate their Terms of Service and/or applicable laws. Use this project for personal research and educational purposes only. Respect robots.txt, rate limits, and user privacy. You are solely responsible for compliance.

## Troubleshooting
- **Auth issues**: Log out/in on the browser, clear “remembered devices”, and re-run if you hit repeated challenges.
- **Rate limiting**: Increase delays, reduce batch sizes, or limit scope.
- **Import errors**: Run from the repo root and set `PYTHONPATH=$PWD`. If needed, adjust imports to your environment.
- **Redis unavailable**: Cookie caching is optional; the client falls back gracefully.
