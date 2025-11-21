from __future__ import annotations

import os

import dlt
import duckdb
from client.helpers import LinkedInPaginator
from client.voyager_client import CustomAuth
from column_mapping import get_map_func
from configuration.endpoint_conf import (data_selectors, dependencies,
                                         endpoints, mappings, total_paths)
from configuration.pipeline_conf import (API_BASE_URL,
                                         graphql_pagignator_config, logger)
from data_utils import get_dependency_from_db, write_current_jobs_to_csv
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig
from resources import as_resource

# Resource Creation Functions
# # These are config-driven resource generators


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


def run_pipeline(db_name, split_resources=False, resource_data={}, **kwargs):
    """
    Defines the pipeline and runs it incrementally or all at once
    """
    logger.info("Running pipeline...")
    db = duckdb.connect(db_name)
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
    logger.info("Authenticating...")
    auth.authenticate()
    if split_resources:
        logger.info("Running split resources pipeline...")
        load_infos = []
        for resource_name, resource_data_list in resource_data.items():
            for resource_datum in resource_data_list:
                resource_data_dict = {resource_name: resource_datum}
                li_source = linkedin_source(
                    auth.session, db_name, resource_data=resource_data_dict, **kwargs
                )
                load_info = pipeline.run(li_source)
                load_infos.append(load_info)
        logger.info("Split resources pipeline completed...")
        return load_infos
    else:
        logger.info("Running full resources pipeline...")
        li_source = linkedin_source(
            auth.session, db_name, resource_data=resource_data, **kwargs
        )
        load_info = pipeline.run(li_source)
        logger.info("Pipeline completed...")
        return load_info


if __name__ == "__main__":
    db_path = "linkedin.duckdb"
    db = duckdb.connect(db_path)
    resources_requested = [
        "jobs_by_company",
        # "company_details",
        # 'job_description',
        "followed_companies",
    ]
    # tables = db.sql("select DISTINCT company_id from linkedin_data.jobs_by_company where job_id not in (select job_id from linkedin_data.job_log)")
    # print(tables)
    # breakpoint()
    # _ = write_new_jobs_to_csv(db_path)

    # log_current_jobs(db_path)
    new_job_urls = run_pipeline(
        db_path,
        split_resources=False,
        resources_requested=resources_requested,
        inspect_response=False,
    )

    _ = write_current_jobs_to_csv(db_path)

    # _ = write_new_jobs_to_csv(db_path)
