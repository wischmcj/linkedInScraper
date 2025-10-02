from __future__ import annotations

import logging
import os

import duckdb
from voyager_client import CustomAuth

logger = logging.getLogger(__name__)

import json

import dlt
from analytics.saved_queries import db_followed_companies, generate_job_urls
from configuration.column_mapping import get_map_func
from configuration.endpoint_conf import (data_selectors, endpoints,
                                         graphql_pagignator_config, mappings,
                                         total_paths)
from configuration.pipeline_conf import API_BASE_URL
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig
from helpers import LinkedInPaginator

auth = CustomAuth(
    username=os.getenv("LINKEDIN_USERNAME"),
    password=os.getenv("LINKEDIN_PASSWORD"),
    use_cookie_cache=False,
)
auth.authenticate()


# Resource Creation Functions
# # These are config-driven resource generators


def as_resource(name, data, **kwargs):
    @dlt.resource(name=name, **kwargs)
    def data_resource():
        if isinstance(data, list):
            yield data
        else:
            yield [data]

    return data_resource


def graphql_resource(source_name):
    """
    Generates a dlt endpoint configuration based on
        the configuration details in endpoint_conf.py
    """
    endpoint = endpoints[source_name]
    query = endpoint["query"]
    path = endpoint["path"]
    include_from_parent = endpoint.get("include_from_parent", None)

    paginator_config = graphql_pagignator_config
    paginator_config["total_path"] = total_paths[source_name]

    mapping = mappings.get(source_name, [])

    resource_config = {
        "name": source_name,
        "max_table_nesting": 0,
        "endpoint": {
            "path": path,
            "json": query,
            "paginator": LinkedInPaginator(**paginator_config),
            "data_selector": data_selectors[source_name],
        },
        "processing_steps": [{"map": get_map_func(mapping)}],
    }
    if include_from_parent:
        resource_config["include_from_parent"] = include_from_parent
    return resource_config


@dlt.source
def test_source(
    source_name,
    session,
):
    resources = [graphql_resource(source_name)]
    config: RESTAPIConfig = {
        "client": {
            "base_url": f"{API_BASE_URL}",
            "session": session,
        },
        # There doesnt seem to be a way to set
        # write_disposition, merge strategy from the schema file
        "resource_defaults": {
            "write_disposition": {"disposition": "merge", "strategy": "scd2"}
        },
        "resources": resources,
    }
    resource_list = rest_api_resources(config)
    return resource_list


bucket_url = "file://Users/admin/Documents/csv_files"


def file_resource(
    file_name,
):
    with open(file_name) as f:
        data = json.load(f)
        recipies = []
        mappings = []
        all_fields_rows = []
        for recipie_id, datum in data.items():
            breakpoint()
            fields_details = datum["fields"]
            fields = datum["fields"].keys()
            recipie = [
                {
                    "table_name": "recipies",
                    "recipie_id": recipie_id,
                    "baseType": datum["baseType"],
                    "fields": list(fields),
                }
            ]
            fields_to_recipie = [
                {
                    "table_name": "fields_to_recipie",
                    "recipie_id": recipie_id,
                    "field": field,
                }
                for field in fields
            ]
            field_rows = []
            for field, details in fields_details.items():
                row = {"table_name": "fields", "field": field}
                for name, value in details.items():
                    row[name] = value
                field_rows.append(row)
            recipies.extend(recipie)
            mappings.extend(fields_to_recipie)
            all_fields_rows.extend(field_rows)

        return recipies, mappings, all_fields_rows


@dlt.source
def schemata_resources():
    import glob

    files = glob.glob("data/endpoint_responses/schemata/*.json")
    all_recipies = []
    all_mappings = []
    all_fields_rows = []
    for file in files:
        data = file_resource(file)
        recipies, mappings, fields_rows = data
        all_recipies.extend(recipies)
        all_mappings.extend(mappings)
        all_fields_rows.extend(fields_rows)

    resources = []
    kwargs = {"max_table_nesting": 0, "table_name": lambda row: row["table_name"]}
    kwargs["primary_key"] = "recipie_id"
    resources.append(as_resource("recipie_resource", all_recipies, **kwargs))
    _ = kwargs.pop("primary_key")
    resources.append(as_resource("mapping_resource", all_mappings, **kwargs))
    kwargs["primary_key"] = "field"
    resources.append(as_resource("field_resource", all_fields_rows, **kwargs))
    return resources


@dlt.source
def linkedin_source(
    session,
    db_name,
    get_companies=False,
    get_job_urls=False,
    get_descriptions=True,
    company_data=None,
    job_urls=None,
):
    """
    This function is used to create a source matching the parameters passed.

    Can pull:
        i. Companies followed by the configured profile
        ii. Job posting urls for all posted jobs
            - For either all followed companies or a list provided via company_data
        iii. Job description data for all job poscompany_datatings
            - For either all jobs returned in 'ii' or for a list provided via job_urls
    """
    resources = []

    # Create followed_companies resource
    if get_companies:
        followed_companies = graphql_resource("followed_companies")
    else:
        company_data = company_data or db_followed_companies(db_name)
        logger.info(f"Creating resource using companies from db: {company_data}")
        followed_companies = as_resource("company_resource", company_data)

    # Create job_urls resource if needed
    if get_job_urls:
        # If we dont need to get descriptions, then the resource isn't needed
        jobs_by_company = graphql_resource("jobs_by_company")
        resources.append(jobs_by_company)
    else:
        if get_descriptions:
            # If we dont need to get descriptions, then the resource isn't needed
            job_urls = job_urls or generate_job_urls(db_name)
            job_urls = as_resource("job_urls_resource", job_urls)
            logger.info(f"Creating resource using job urls from db: {job_urls}")

    # Create job_description resource if needed
    if get_descriptions:
        job_description = graphql_resource("job_description")
        resources.append(job_description)

    resources.append(followed_companies)
    config: RESTAPIConfig = {
        "client": {
            "base_url": f"{API_BASE_URL}",
            "session": session,
        },
        # There doesnt seem to be a way to set
        # write_disposition, merge strategy from the schema file
        "resource_defaults": {
            "write_disposition": {"disposition": "merge", "strategy": "scd2"}
        },
        "resources": resources,
    }
    resource_list = rest_api_resources(config)
    return resource_list


def run_pipeline(db_name, one_at_a_time=False, **kwargs):
    """
    Defines the pipeline and runs it incrementally or all at once
    """
    db = duckdb.connect(db_name)
    pipeline = dlt.pipeline(
        pipeline_name="linkedin",
        dataset_name="linkedin_data",
        destination=dlt.destinations.duckdb(db),
        import_schema_path="pipeline/configuration/",
        dev_mode=False,
    )
    if one_at_a_time:
        companies_from_db = db_followed_companies(db_name)
        # Allows for saving of data to db regularly
        for cid, company_details in enumerate(companies_from_db):
            li_source = linkedin_source(
                auth.session, db_name, company_data=dict(company_details), **kwargs
            )
            logger.info(f"Running pipeline for company: {company_details}")
            _ = pipeline.run(li_source)
    else:
        li_source = linkedin_source(auth.session, db_name, **kwargs)
        _ = pipeline.run(li_source)


if __name__ == "__main__":
    db_name = "linkedin.duckdb"
    # li_source = test_source("something", auth.session)

    # db = duckdb.connect(db_name)
    # pipeline = dlt.pipeline(
    #     pipeline_name="linkedin",
    #     dataset_name="linkedin_data",
    #     destination=dlt.destinations.duckdb(db),
    #     import_schema_path="pipeline/configuration/",
    #     dev_mode=False,
    # )
    # _ = pipeline.run(li_source)

    # db_name = "test.duckdb"
    # db = duckdb.connect(db_name)
    # # jobs = db.sql("select * from linkedin_data.jobs_by_company" )
    # pipeline = dlt.pipeline(pipeline_name="test", destination="duckdb")
    # file_source = schemata_resources()
    # load_info = pipeline.run(file_source)
    # print(load_info)
    # breakpoint()
