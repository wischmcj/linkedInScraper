
## Prerequisites
- Python 3.10+
- pip / venv (recommended)
- Optional: Redis running locally on port 7777 for cookie caching
- Optional: Chrome/Chromium for capturing HAR files (network research)

## Key Dependencies
- DLT
- DuckDB
- Streamlit (optional)

## Setup

1) Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
# optional for tests
pip install pytest
```


3) Configure environment variables
```bash
export LINKEDIN_USERNAME="your_email@example.com"
export LINKEDIN_PASSWORD="your_linkedIn_password"
```

- You can also use `direnv` with `.envrc` to auto-load environment vars (do not commit secrets).
- If using Redis for cookie caching, ensure it’s running on `localhost:7777`.


## Configuration
There are many configuration options available (See [docs/configuration.md](docs/configuration.md)), but the only required values are the two environment variables below
```bash
export LINKEDIN_USERNAME=**your-linedin-email-address**
export LINKEDIN_PASSWORD=**your-linkedin-password**
```
