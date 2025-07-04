# LinkedIn Scraper

A comprehensive LinkedIn data extraction pipeline built with Python that leverages LinkedIn's Voyager API to collect job postings, company information, and profile data. This project provides a robust, scalable solution for gathering LinkedIn data for research, analysis, and business intelligence purposes.

## 🎯 Overview

This LinkedIn scraper is designed to extract structured data from LinkedIn using their internal Voyager API. It includes authentication handling, rate limiting, data processing, and storage capabilities. The pipeline is built using the Data Load Tool (DLT) framework for efficient data extraction and transformation.

## 🏗️ Architecture

The project is organized into several key components:

### Core Pipeline (`pipeline/`)
- **`voyager_pipeline.py`** - Main pipeline orchestration and DLT source configuration
- **`voyager_client.py`** - LinkedIn authentication and session management
- **`gql_utils.py`** - GraphQL query utilities and URL building functions
- **`conf.py`** - Configuration settings, API endpoints, and data mappings

### Data Processing (`pipeline/data/`)
- **`saved_queries.py`** - Database queries for data retrieval and filtering
- **`nlp.py`** - Natural language processing utilities for job descriptions

### GraphQL Schemas (`gql/`)
- **`profile_gql_queries.py`** - Profile-related GraphQL queries
- **`schema.json`** - LinkedIn API schema definitions
- **`job_gql_urls.txt`** - Job-related GraphQL endpoint URLs
- **`profile_query_ids.txt`** - Profile query identifiers

### Testing (`tests/`)
- **`test_gql_functions.py`** - Unit tests for GraphQL functionality
- Sample response files for testing

## 🚀 Key Features

### Authentication & Session Management
- **Cookie-based authentication** with Redis caching
- **Session persistence** to avoid repeated logins
- **Rate limiting** to prevent API bans
- **Challenge handling** for security verification

### Data Extraction Capabilities
- **Job postings** from followed companies
- **Company information** from user's followed companies
- **Job descriptions** with detailed metadata
- **Profile components** and interests
- **Pagination support** for large datasets

### Data Processing & Storage
- **DuckDB integration** for fast analytical queries
- **Data transformation** and mapping utilities
- **Filtering capabilities** for specific job types
- **Merge operations** to avoid duplicates

### GraphQL Integration
- **Dynamic query building** from configuration
- **URL encoding** for complex parameters
- **Response parsing** with JSONPath support
- **Schema introspection** capabilities

## 📋 Prerequisites

- Python 3.8+
- Redis server (for session caching)
- LinkedIn account credentials
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd linkedinScraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export LINKEDIN_USERNAME="your_linkedin_email"
   export LINKEDIN_PASSWORD="your_linkedin_password"
   ```

4. **Start Redis server:**
   ```bash
   redis-server --port 7777
   ```

## 🔧 Configuration

The main configuration is in `pipeline/conf.py`:

- **API endpoints** - LinkedIn Voyager API endpoints
- **Batch sizes** - Number of records per request
- **Data mappings** - Field mapping configurations
- **Query parameters** - GraphQL query configurations

## 📊 Data Schema

The pipeline extracts data into several main tables:

### `followed_companies`
- Company IDs and names from user's followed companies
- Used as a source for job searches

### `jobs_by_company`
- Job postings from followed companies
- Includes job titles, descriptions, and metadata

### `job_description`
- Detailed job descriptions and requirements
- Salary information and benefits

## 🔍 Usage Examples

### Basic Pipeline Execution
```python
from pipeline.voyager_pipeline import run_pipeline

# Run the complete pipeline
run_pipeline()
```

### Filtering Data Jobs
```python
from pipeline.data.saved_queries import get_data_jobs

# Get data-related jobs
data_jobs = get_data_jobs()
print(data_jobs)
```

### Custom Company Search
```python
from pipeline.voyager_pipeline import linkedin_source

# Search jobs for specific company
company_data = {"company_id": "12345", "name": "Example Corp"}
source = linkedin_source(session, company_data=company_data)
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📈 Data Analysis

The project includes utilities for analyzing extracted data:

- **Job filtering** by title, location, or company
- **Remote job identification**
- **Data science job classification**
- **Software engineering job filtering**

## 🔒 Security & Ethics

- **Rate limiting** to respect LinkedIn's terms of service
- **Session management** to minimize authentication requests
- **Data privacy** considerations for extracted information
- **Responsible scraping** practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is for educational and research purposes. Please ensure compliance with LinkedIn's Terms of Service and applicable data protection regulations.

## ⚠️ Disclaimer

This tool is provided as-is for educational purposes. Users are responsible for ensuring compliance with LinkedIn's Terms of Service and applicable laws regarding web scraping and data collection.

## 🔗 Dependencies

- **dlt** - Data Load Tool for pipeline orchestration
- **duckdb** - Analytical database for data storage
- **redis** - Session caching and persistence
- **requests** - HTTP client for API communication
- **toml** - Configuration file parsing

## 📞 Support

For issues, questions, or contributions, please open an issue on the repository or contact the maintainers. 