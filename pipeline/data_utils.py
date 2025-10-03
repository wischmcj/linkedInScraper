from __future__ import annotations

import logging

import duckdb

log = logging.getLogger(__name__)


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
