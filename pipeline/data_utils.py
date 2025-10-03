from __future__ import annotations

import logging

import duckdb

log = logging.getLogger(__name__)

from configuration.queries import (data_jobs_filter, ml_jobs_filter,
                                   rs_jobs_filter, software_jobs_filter)


def get_dependency_from_db(db_path, dependency):
    if dependency == "followed_companies":
        return db_followed_companies(db_path)
    elif dependency == "jobs_by_company":
        return jobs_by_company(db_path)
    else:
        raise ValueError(f"Dependency {dependency} not found")


# Company Data
def db_followed_companies(db_path, limit=None):
    db = duckdb.connect(db_path)
    select = "select * EXCLUDE(_dlt_valid_to, _dlt_valid_from,_dlt_load_id,_dlt_id,'_dlt_valid_from__v_text') from linkedin_data.followed_companies"
    if limit is not None:
        select = f"{select} limit {limit}"
    followed_companies = db.sql(select)
    return followed_companies.df().to_dict(orient="records")


# Job Postings
def jobs_by_company(db_path):
    db = duckdb.connect(db_path)
    followed_companies = db.sql(
        "select * EXCLUDE(_dlt_valid_to, _dlt_valid_from,_dlt_load_id,_dlt_id,'_dlt_valid_from__v_text') from linkedin_data.jobs_by_company"
    )
    return followed_companies.df()


def get_jobs_ids(db_path):
    db = duckdb.connect(db_path)
    followed_companies = db.sql(
        "select distinct REPLACE(job_posting_urn, 'urn:li:fsd_jobPosting:','') as job_id from linkedin_data.jobs_by_company where _dlt_valid_to is not null"
    )
    return followed_companies.df()["job_id"].to_list()


def log_current_jobs(db_path):
    db = duckdb.connect(db_path)
    _ = db.sql(
        """INSERT INTO linkedin_data.job_log (job_id, date_logged)  (
                        select DISTINCT jobs_by_company.job_id, jobs_by_company._dlt_valid_from as date_logged
                        from linkedin_data.jobs_by_company
                            LEFT JOIN linkedin_data.job_log
                                on job_log.job_id = jobs_by_company.job_id
                        where job_log.job_id is null
                        )"""
    )
    log.info("Logged current jobs to job_log table")


# Transforming job data
def get_filter_str(db_path, filter_str="1=1"):
    if filter_str == "data":
        filter_str = data_jobs_filter
    elif filter_str == "rs":
        filter_str = rs_jobs_filter
    elif filter_str == "software":
        filter_str = software_jobs_filter
    elif filter_str == "ml":
        filter_str = ml_jobs_filter
    elif filter_str == "all":
        filter_str = (
            data_jobs_filter
            + " OR "
            + rs_jobs_filter
            + " OR "
            + ml_jobs_filter
            + " OR "
            + software_jobs_filter
        )
    elif filter_str == "other":
        filter_str = (
            "NOT ( "
            + data_jobs_filter
            + " ) AND NOT ( "
            + rs_jobs_filter
            + " ) AND NOT ( "
            + rs_jobs_filter
            + " )  AND NOT ( "
            + software_jobs_filter
            + " )"
        )
    elif filter_str == "ml":
        filter_str = ml_jobs_filter
    elif filter_str == "new":
        filter_str = """ job_id  not in (
                SELECT job_id
                FROM linkedin_data.job_log)
                """
    return filter_str


def get_jobs_filtered(db_path, filter_str="'Data' in job_posting_title", new=False):
    db = duckdb.connect(db_path)
    new_filter = ""
    if new:
        new_filter = "where a.job_id not in (select job_id from linkedin_data.job_log)"
    jobs = db.sql(
        """
        select distinct a.job_posting_title,
                        b.company_name,
                        a.job_posting_urn,
                        a.location,
                        a.job_id,
                        a._dlt_valid_to,
                        a._dlt_valid_from,
                        case
                            when CONTAINS(lower(a.location),'remote') then 1
                            else 0
                        end as is_remote
        from (
                Select job_posting_urn,
                        LOWER(job_posting_title) as job_posting_title,
                        company_id,
                        secondary_description as location,
                        job_id,
                        _dlt_valid_to,
                        _dlt_valid_from
                FROM linkedin_data.jobs_by_company) as a
            left join (
                SELECT name as company_name, company_id
                FROM linkedin_data.followed_companies) as b
            on a.company_id=b.company_id

            """
        + new_filter
    )
    print("final")
    data_jobs = jobs.filter(filter_str)
    return data_jobs.df()


def write_new_jobs_to_csv(db_path):
    for filter_str in ["data", "rs", "software", "ml", "new"]:
        new_jobs_filter = get_filter_str(db_path, filter_str)
        new_jobs = get_jobs_filtered(db_path, new_jobs_filter, new=True)
        new_job_urls = generate_job_urls(
            new_jobs, f"new_{filter_str}_jobs", as_csv=True
        )
    return new_job_urls


def generate_job_urls(jobs, file_name="test", as_csv=False):
    jobs["job_id"] = jobs["job_posting_urn"].str.replace("urn:li:fsd_jobPosting:", "")
    jobs["job_urls"] = "https://www.linkedin.com/jobs/view/" + jobs["job_id"]
    job_urls = [
        (x, y) for x, y in zip(jobs["job_urls"], jobs["company_name"].to_list())
    ]
    print("jobs shape", jobs.shape)
    if as_csv:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d")
        jobs.to_csv(f"{file_name}_{timestamp}.csv", index=False)
    return job_urls


class LoadInfoProcessor:
    def __init__(
        self,
        load_info,
        destination="default",
        actions=[],
        alerts=["schema_changes", "new_items"],
    ):
        self.load_info = load_info
        self.actions_functions = [
            getattr(self, f"action_{action}") for action in actions
        ]
        self.alert_functions = [getattr(self, f"alert_{alert}") for alert in alerts]
        self.logger = logging.getLogger(f"{self.destination}")

    def alert_schema_changes(self, table_name, column_name, column):
        self.logger.info(
            f"\tTable updated: {table_name}: "
            f"Column changed: {column_name}: "
            f"{column['data_type']}"
        )

    def alert_new_items(self, table_name, column_name, column):
        self.logger.info(
            f"\tTable updated: {table_name}: "
            f"Column changed: {column_name}: "
            f"{column['data_type']}"
        )

    def loop_over_load_info(self):
        for package in self.load_info.load_packages:
            # Iterate over each table in the schema_update of the current package
            for table_name, table in package.schema_update.items():
                # Iterate over each column in the current table
                for column_name, column in table["columns"].items():
                    # Send a message to the Slack channel with the table
                    # and column update information
                    for action in self.actions_functions:
                        action(table_name, column_name, column)
                    for alert in self.alert_functions:
                        alert(table_name, column_name, column)
