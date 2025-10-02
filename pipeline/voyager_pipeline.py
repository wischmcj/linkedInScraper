from __future__ import annotations

import logging
import os

import duckdb
from voyager_client import CustomAuth

logger = logging.getLogger(__name__)

import json

import dlt
from analytics.saved_queries import (db_followed_companies,
                                     get_dependency_from_db, log_current_jobs,
                                     write_new_jobs_to_csv)
from configuration.column_mapping import get_map_func
from configuration.endpoint_conf import (data_selectors, dependencies,
                                         endpoints, mappings, total_paths)
from configuration.pipeline_conf import API_BASE_URL, graphql_pagignator_config
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig
from helpers import LinkedInPaginator

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


def graphql_resource(source_name, inspect_response=False):
    """
    Generates a dlt endpoint configuration based on
        the configuration details in endpoint_conf.py
    """
    endpoint = endpoints[source_name]
    query = endpoint["json"]
    path = endpoint["path"]
    include_from_parent = endpoint.get("include_from_parent", None)

    paginator_total = total_paths.get(source_name)
    paginator_config = {}
    paginator_config.update(graphql_pagignator_config)
    paginator_config["total_path"] = paginator_total
    paginator_config["inspect_response"] = inspect_response

    if paginator_total is None:
        paginator_config["single_page"] = True

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
        # There doesn't seem to be a way to set
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
        recipes = []
        mappings = []
        all_fields_rows = []
        for recipe_id, datum in data.items():
            fields_details = datum["fields"]
            fields = datum["fields"].keys()
            recipe = [
                {
                    "table_name": "recipes",
                    "recipe_id": recipe_id,
                    "baseType": datum["baseType"],
                    "fields": list(fields),
                }
            ]
            fields_to_recipe = [
                {
                    "table_name": "fields_to_recipe",
                    "recipe_id": recipe_id,
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
            recipes.extend(recipe)
            mappings.extend(fields_to_recipe)
            all_fields_rows.extend(field_rows)

        return recipes, mappings, all_fields_rows


@dlt.source
def schemata_resources():
    import glob

    files = glob.glob("data/endpoint_responses/schemata/*.json")
    all_recipes = []
    all_mappings = []
    all_fields_rows = []
    for file in files:
        data = file_resource(file)
        recipes, mappings, fields_rows = data
        all_recipes.extend(recipes)
        all_mappings.extend(mappings)
        all_fields_rows.extend(fields_rows)

    resources = []
    kwargs = {"max_table_nesting": 0, "table_name": lambda row: row["table_name"]}
    kwargs["primary_key"] = "recipe_id"
    resources.append(as_resource("recipe_resource", all_recipes, **kwargs))
    _ = kwargs.pop("primary_key")
    resources.append(as_resource("mapping_resource", all_mappings, **kwargs))
    kwargs["primary_key"] = "field"
    resources.append(as_resource("field_resource", all_fields_rows, **kwargs))
    return resources


@dlt.source
def linkedin_source(
    session,
    db_name,
    resources_requested,
    resource_data: dict = {},
    inspect_response=False,
):
    """
    This function is used to create a source matching the parameters passed.

    Can pull:
        i. Companies followed by the configured profile
        ii. Job posting urls for all posted jobs
            - For either all followed companies or a list provided via company_data
        iii. Job description data for all job postings
            - For either all jobs returned in 'ii' or for a list provided via job_urls
    """
    # Created each resource and the resources on which it depends
    resources = []
    resource_dependencies = []
    for resource_name in resources_requested:
        actual_resource = graphql_resource(
            resource_name, inspect_response=inspect_response
        )
        resources.append(actual_resource)
        resource_dependencies.extend(dependencies.get(resource_name, []))

    for dependency in resource_dependencies:
        if dependency not in resources_requested:
            if dependency not in resource_data.keys():
                logger.info(f"Creating resource using {dependency} from db")
                dependency_data = get_dependency_from_db(db_name, dependency)
            else:
                logger.info(f"Creating resource using {dependency} from resource_data")
                dependency_data = resource_data[dependency]
            dependency_resource = as_resource(dependency, dependency_data)
            resources.append(dependency_resource)

    config: RESTAPIConfig = {
        "client": {
            "base_url": f"{API_BASE_URL}",
            "session": session,
        },
        # There doesn't seem to be a way to set
        # write_disposition, merge strategy from the schema file
        "resource_defaults": {
            "write_disposition": {"disposition": "merge", "strategy": "scd2"}
        },
        "resources": resources,
    }
    resource_list = rest_api_resources(config)
    return resource_list


def run_pipeline(db_name, **kwargs):
    """
    Defines the pipeline and runs it incrementally or all at once
    """
    db = duckdb.connect(db_name)
    log_current_jobs(db_name)
    pipeline = dlt.pipeline(
        pipeline_name="linkedin",
        dataset_name="linkedin_data",
        destination=dlt.destinations.duckdb(db),
        import_schema_path="pipeline/configuration/",
        dev_mode=False,
    )
    auth = CustomAuth(
        username=os.getenv("LINKEDIN_USERNAME"),
        password=os.getenv("LINKEDIN_PASSWORD"),
    )
    auth.authenticate()

    li_source = linkedin_source(auth.session, db_name, **kwargs)
    load_info = pipeline.run(li_source)
    _ = write_new_jobs_to_csv(db_name)
    return load_info


if __name__ == "__main__":
    db_path = "linkedin.duckdb"
    resources_requested = [
        "jobs_by_company",
        # "company_details",
        # 'job_description',
        # 'followed_companies'
    ]
    # db_path = "linkedin.duckdb"
    # db = duckdb.connect(db_path)
    resource_data = {
        "followed_companies": db_followed_companies(db_path)
        # 'job_description': get_job_description(db_path),
        # 'followed_companies': get_followed_companies(db_path),
    }

    new_job_urls = run_pipeline(
        db_path,
        resources_requested=resources_requested,
        inspect_response=False,
    )
