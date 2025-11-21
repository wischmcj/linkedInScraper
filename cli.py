#!/usr/bin/env python3
"""
LinkedIn Scraper CLI

A command-line interface for the LinkedIn scraper pipeline that allows users to:
- Select which data resources to scrape
- Override configuration values
- Customize authentication settings
- Control output and debugging options
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the pipeline directory to the path
sys.path.insert(0, str(Path(__file__).parent / "pipeline"))

from configuration.endpoint_conf import dependencies, endpoints
from voyager_pipeline import run_pipeline

# Use the centralized logger
logger = logging.getLogger("linkedin_scraper.cli")


HELP_TEXT = f"""
Help Text:
    Examples:
    # Basic usage - scrape followed companies and their jobs
    python cli.py --resources followed_companies jobs_by_company

    # Scrape all available data
    python cli.py --resources followed_companies company_details jobs_by_company job_description

    # Use custom database and inspect responses
    python cli.py --database my_data.duckdb --resources jobs_by_company --inspect-response

    # Override configuration with custom settings (JSON or TOML)
    python cli.py --config custom_config.json --resources followed_companies
    python cli.py --config custom_config.toml --resources followed_companies

    # Debug mode with verbose output
    python cli.py --resources followed_companies --verbose --debug

    Available Resources:
    followed_companies  - Companies followed by the authenticated profile
    company_details    - Detailed company information (requires followed_companies)
    jobs_by_company    - Job listings for followed companies (requires followed_companies)
    job_description    - Detailed job descriptions (requires jobs_by_company)

    External Configuration File Formats:
    Providing a configuration file with the --config flag will override
        the default configuration **for the value of the supplied configuration options**.

    JSON Format:
    {{
        "pipeline": {{
        "batch_size": 50,
        "evade_time": 1.0,
        "search_limit": 200,
        "paginator": {{
            "maximum_value": 2000
        }}
        }},
        "pipeline_kwargs": {{
        "inspect_response": true
        }}
    }}

    TOML Format:
    [pipeline]
    batch_size = 50
    evade_time = 1.0
    search_limit = 200

    pipeline.request_headers = {
        "user-agent": "Mozilla/5.0...",
        "accept-language": "en-US,en;q=0.9"
    }

    pipeline.auth_request_headers = {
        "X-Li-User-Agent": "LIAuthLibrary:3.2.4...",
        "User-Agent": "Mozilla/5.0..."
    }

    [pipeline.paginator]
    maximum_value = 2000

    [pipeline_kwargs]
    inspect_response = true
        """


class LinkedInScraperCLI:
    """Command-line interface for the LinkedIn scraper pipeline."""

    def __init__(self):
        self.available_resources = list(endpoints.keys())
        self.resource_dependencies = dependencies

    def setup_logging(self, verbose: bool = False, debug: bool = False):
        """Configure logging based on verbosity level."""
        # Get the root linkedin_scraper logger
        root_logger = logging.getLogger("linkedin_scraper.cli")
        level = (
            logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
        )
        root_logger.setLevel(level)

    def validate_resources(self, resources: list[str]) -> list[str]:
        """Validate and resolve resource dependencies."""
        if not resources:
            raise ValueError("At least one resource must be specified")

        # Check if all requested resources exist
        invalid_resources = [r for r in resources if r not in self.available_resources]
        if invalid_resources:
            raise ValueError(
                f"Invalid resources: {invalid_resources}. "
                f"Available resources: {self.available_resources}"
            )

        # Resolve dependencies
        all_resources = set(resources)
        for resource in resources:
            deps = self.resource_dependencies.get(resource, [])
            all_resources.update(deps)

        return list(all_resources)

    def load_config_overrides(self, config_file: str | None):
        """Load configuration overrides from JSON or TOML file."""
        if not config_file:
            return {}
        # TODO: Implement config file loading (JSON/TOML)
        logger.info(f"Config file specified: {config_file}")
        return {}

    def check_authentication(
        self, username: str | None = None, password: str | None = None
    ):
        """Check if authentication credentials are available."""
        username = username or os.getenv("LINKEDIN_USERNAME")
        password = password or os.getenv("LINKEDIN_PASSWORD")

        if not username or not password:
            raise ValueError(
                "LinkedIn credentials not found. Please provide --username and --password "
                "or set LINKEDIN_USERNAME and LINKEDIN_PASSWORD environment variables."
            )
        return username, password

    def run(self, args):
        """Main CLI execution method."""
        try:
            # Setup logging
            self.setup_logging(args.verbose, args.debug)

            # Validate resources
            resources = self.validate_resources(args.resources)

            # Load and apply configuration overrides
            config_overrides = self.load_config_overrides(args.config)

            # Check authentication
            username, password = self.check_authentication(args.username, args.password)

            # Prepare pipeline arguments
            pipeline_kwargs = {
                "resources_requested": args.resources,  # Use original list, not resolved dependencies
                "inspect_response": args.inspect_response,
                "resource_data": {},
            }

            # Add any additional configuration from overrides
            if "pipeline_kwargs" in config_overrides:
                pipeline_kwargs.update(config_overrides["pipeline_kwargs"])

            print("Starting LinkedIn scraper pipeline...")
            print(f"Resources: {', '.join(args.resources)}")
            print(f"Database: {args.database}")

            if args.verbose:
                print(f"📋 Resolved dependencies: {', '.join(resources)}")
                print(f"⚙️  Configuration overrides: {len(config_overrides)} sections")

            # Run the pipeline
            load_info = run_pipeline(args.database, **pipeline_kwargs)

            print("✅ Pipeline completed successfully!")
            print(f"📈 Load info: {load_info}")

        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            if args.debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    # Get available resources dynamically
    try:
        available_resources = list(endpoints.keys())
    except NameError:
        # Fallback if modules can't be imported
        available_resources = [
            "followed_companies",
            "company_details",
            "jobs_by_company",
            "job_description",
        ]

    parser = argparse.ArgumentParser(
        description="LinkedIn Scraper CLI - Extract data from LinkedIn using the Voyager API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP_TEXT,
    )

    # Required arguments
    parser.add_argument(
        "--resources",
        nargs="+",
        required=True,
        choices=available_resources,
        help="Resources to scrape (can specify multiple)",
    )

    parser.add_argument(
        "--exclude",
        nargs="+",
        required=True,
        choices=available_resources,
        help="Resources to scrape (can specify multiple)",
    )

    # Optional arguments
    parser.add_argument(
        "--database",
        default="linkedin.duckdb",
        help="DuckDB database file path (default: linkedin.duckdb)",
    )

    parser.add_argument(
        "--config", help="TOML orJSON configuration file to override default settings"
    )

    parser.add_argument(
        "--username", help="LinkedIn username (overrides LINKEDIN_USERNAME env var)"
    )

    parser.add_argument(
        "--password", help="LinkedIn password (overrides LINKEDIN_PASSWORD env var)"
    )

    parser.add_argument(
        "--inspect-response",
        action="store_true",
        help="Inspect API responses for debugging",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with full tracebacks"
    )

    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    cli = LinkedInScraperCLI()
    cli.run(args)


if __name__ == "__main__":
    main()
