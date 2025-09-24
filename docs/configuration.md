
## Configuration

- **Auth & headers**: Managed in `pipeline/voyager_client.py` and `pipeline/configuration/pipeline_conf.py`.
- **Endpoints & selectors**: Defined in `pipeline/configuration/endpoint_conf.py` under `endpoints`, `data_selectors`, `total_paths`, and `graphql_pagignator_config`.
- **dlt runtime**: Tunables in `.dlt/config.toml` (workers, normalization, logging, etc.).


## DLT Source: configuration and capabilities


The core of the repo is a dlt source defined in `pipeline/voyager_pipeline.py` as `linkedin_source(...)`. It builds resources dynamically from settings in `pipeline/configuration/endpoint_conf.py`.

- **Where it’s defined**: `pipeline/voyager_pipeline.py`
  - This file creates a LinkedIn DLT source to pull a series of data-points from LinkedIn via their Voyager API
  - Current Resources :
    - `followed_companies` - Pulls companies followed given a user profile
    - `jobs_by_company` - Pulls a list of all job postings from a set of companies (defaults to followed companies)
    - `job_description`- Pulls detailed information on jobs (title, description, salary range, etc.)

- **Configuring via `endpoint_conf.py`**:
  - **`endpoints`**: Defines the details of api endpoints behind each resource
    - `path`: `'graphql'` or `'voyagerJobsDashJobCards'`
    - `query`: Parameters/variables; include `start: '$start'` and `count: BATCH_SIZE` for pagination
    - `include_from_parent` (optional): Pass fields from parent to child (e.g., `company_id`, `job_urn_encoded`)
  - **`data_selectors`**: JSON-like selectors that pick result arrays from responses
  - **`mapppings`**: Pairs of `(column_name, nested_key)` to flatten nested fields into table columns
  - **`total_paths`**: Path to total result count for paginated endpoints
  - **`graphql_pagignator_config`**: Pagination knobs (`param_name`, `initial_value`, `value_step`, `maximum_value`)
  - **`BATCH_SIZE`** and **`API_BASE_URL`**: Control page size and base endpoint

- **Adding a new resource** (high level):
  1) Add its block to `endpoints` with `path`, `query`, and optional `include_from_parent`
  2) Add a selector in `data_selectors['your_resource']`
  3) Add `total_paths['your_resource']` if paginated
  4) Optionally add flattening rules under `mapppings['your_resource']`
  5) Wire it in by calling `graphql_source('your_resource')` inside `linkedin_source`
