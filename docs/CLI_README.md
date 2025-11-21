# LinkedIn Scraper CLI

A command-line interface for the LinkedIn scraper pipeline that provides easy access to LinkedIn data extraction with customizable configuration options.

## Quick Start

1. **Set up authentication** (choose one method):
   ```bash
   # Method 1: Environment variables
   export LINKEDIN_USERNAME="your_email@example.com"
   export LINKEDIN_PASSWORD="your_password"

   # Method 2: Command line arguments
   python cli.py --username "your_email@example.com" --password "your_password" --resources followed_companies
   ```

2. **Run basic scraping**:
   ```bash
   python cli.py --resources followed_companies jobs_by_company
   ```

## Available Resources

The CLI supports four main data resources:

| Resource | Description | Dependencies |
|----------|-------------|--------------|
| `followed_companies` | Companies followed by your LinkedIn profile | None |
| `company_details` | Detailed company information (industry, size, locations, etc.) | `followed_companies` |
| `jobs_by_company` | Job listings for followed companies | `followed_companies` |
| `job_description` | Detailed job descriptions and requirements | `jobs_by_company` |

## Command Line Options

### Required Arguments
- `--resources`: Specify which data resources to scrape (can specify multiple)

### Optional Arguments
- `--database`: DuckDB database file path (default: `linkedin.duckdb`)
- `--config`: Configuration file to override default settings (supports JSON and TOML formats)
- `--username`: LinkedIn username (overrides `LINKEDIN_USERNAME` env var)
- `--password`: LinkedIn password (overrides `LINKEDIN_PASSWORD` env var)
- `--inspect-response`: Inspect API responses for debugging
- `--verbose`, `-v`: Enable verbose output
- `--debug`: Enable debug mode with full tracebacks

## Usage Examples

### Basic Usage
```bash
# Scrape followed companies and their job listings
python cli.py --resources followed_companies jobs_by_company

# Scrape all available data
python cli.py --resources followed_companies company_details jobs_by_company job_description
```

### Advanced Usage
```bash
# Use custom database and inspect responses
python cli.py --database my_data.duckdb --resources jobs_by_company --inspect-response

# Debug mode with verbose output
python cli.py --resources followed_companies --verbose --debug

# Override configuration with custom settings (JSON or TOML)
python cli.py --config custom_config.json --resources followed_companies
python cli.py --config custom_config.toml --resources followed_companies
```

## Configuration Override

You can override default pipeline settings using JSON or TOML configuration files. See `config_example.json` and `config_example.toml` for complete examples.

### Configuration Structure

**JSON Format:**
```json
{
  "pipeline": {
    "batch_size": 50,
    "evade_time": 1.0,
    "search_limit": 200,
    "use_cookie_cache": false,
    "login_with_selenium": true,
    "selenium_fallback": true,
    "allow_manual_captcha": false,
    "api_base_url": "https://www.linkedin.com/voyager/api",
    "auth_base_url": "https://www.linkedin.com",
    "request_headers": {
      "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
      "accept-language": "en-US,en;q=0.9",
      "x-li-lang": "en_US",
      "x-restli-protocol-version": "2.0.0"
    },
    "auth_request_headers": {
      "X-Li-User-Agent": "LIAuthLibrary:3.2.4 com.linkedin.LinkedIn:8.8.1 iPhone:8.3",
      "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
      "X-User-Language": "en",
      "X-User-Locale": "en_US",
      "Accept-Language": "en-us"
    },
    "paginator": {
      "param_name": "start",
      "initial_value": 0,
      "value_step": 50,
      "maximum_value": 2000,
      "base_index": 0,
      "error_message_items": "errors",
      "single_page": false
    }
  },
  "pipeline_kwargs": {
    "inspect_response": false,
    "resource_data": {}
  }
}
```

**TOML Format:**
```toml
[pipeline]
batch_size = 50
evade_time = 1.0
search_limit = 200
use_cookie_cache = false
login_with_selenium = true
selenium_fallback = true
allow_manual_captcha = false
api_base_url = "https://www.linkedin.com/voyager/api"
auth_base_url = "https://www.linkedin.com"

# Request headers (single config value)
pipeline.request_headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
    "accept-language": "en-US,en;q=0.9",
    "x-li-lang": "en_US",
    "x-restli-protocol-version": "2.0.0"
}

# Auth request headers (single config value)
pipeline.auth_request_headers = {
    "X-Li-User-Agent": "LIAuthLibrary:3.2.4 com.linkedin.LinkedIn:8.8.1 iPhone:8.3",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
    "X-User-Language": "en",
    "X-User-Locale": "en_US",
    "Accept-Language": "en-us"
}

[pipeline.paginator]
param_name = "start"
initial_value = 0
value_step = 50
maximum_value = 2000
base_index = 0
error_message_items = "errors"
single_page = false

[pipeline_kwargs]
inspect_response = false
```

### Key Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `batch_size` | Number of items per API request | 25 |
| `evade_time` | Delay between requests (seconds) | 0.5 |
| `search_limit` | Maximum number of items to search | 100 |
| `use_cookie_cache` | Use cached authentication cookies | false |
| `login_with_selenium` | Use Selenium for authentication | true |
| `selenium_fallback` | Fallback to Selenium if auth fails | false |
| `allow_manual_captcha` | Enable manual captcha solving | true |
| `maximum_value` | Maximum pagination value | 1000 |

## Output

The CLI creates a DuckDB database with the following tables:
- `linkedin_data.followed_companies`
- `linkedin_data.company_details`
- `linkedin_data.jobs_by_company`
- `linkedin_data.job_description`

## Troubleshooting

### Authentication Issues
- Ensure your LinkedIn credentials are correct
- Try logging out and back into LinkedIn in your browser
- Clear "remembered devices" in LinkedIn settings
- Use `--debug` flag to see detailed error messages

### Rate Limiting
- Increase `evade_time` in configuration
- Reduce `batch_size` in configuration
- Limit the scope of resources being scraped

### Import Errors
- Run the CLI from the repository root directory
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Configuration Issues
- Validate your JSON configuration file syntax
- Check that all required fields are present
- Use `--verbose` flag to see configuration loading details

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LINKEDIN_USERNAME` | Your LinkedIn email/username | Yes |
| `LINKEDIN_PASSWORD` | Your LinkedIn password | Yes |

## Legal Notice

⚠️ **Important**: Scraping LinkedIn may violate their Terms of Service and/or applicable laws. Use this project for personal research and educational purposes only. Respect robots.txt, rate limits, and user privacy. You are solely responsible for compliance with all applicable laws and terms of service.
