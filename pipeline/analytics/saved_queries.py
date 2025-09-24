from __future__ import annotations

import duckdb

data_jobs_filter = """(
                    'data engineer' in job_posting_title
                    OR 'data scientist' in job_posting_title
                    OR 'scientific programmer' in job_posting_title
                    OR 'python' in job_posting_title
                    OR 'data' in job_posting_title)
                    AND 'manager' not in job_posting_title
                    AND 'analyst' not in job_posting_title
                    AND 'director' not in job_posting_title
                    AND 'head' not in job_posting_title
                    AND 'visualization' not in job_posting_title
                    AND 'Jobot' not in company_name
                    """
ml_jobs_filter = """('machine learning' in job_posting_title
                    OR
                    (   ('ml' in job_posting_title
                            OR 'ai' in job_posting_title
                            OR 'artificial intelligence' in job_posting_title
                            or 'machine learning' in job_posting_title
                            or 'cloud' in job_posting_title
                        )
                        AND
                        (   'engineer' in job_posting_title
                            OR 'developer' in job_posting_title
                            OR 'programmer' in job_posting_title
                        )
                    )
                    OR 'machine learning developer' in job_posting_title
                    OR 'machine learning programmer' in job_posting_title
                    OR 'machine learning' in job_posting_title)
                    """
rs_jobs_filter = """('lidar' in lower(job_posting_title)
                    OR 'lidar' in lower(job_posting_title)
                     OR 'geospatial' in lower(job_posting_title)
                     OR 'remote sensing' in lower(job_posting_title)
                    )
                    """
software_jobs_filter = """'software engineer' in job_posting_title
                        OR 'software developer' in job_posting_title
                        OR 'software' in job_posting_title
                        OR 'developer' in job_posting_title
                        OR 'programmer' in job_posting_title
                        """

get_no_job_companies = """SELECT  a.*
                            FROM followed_companies as a
                            left join jobs_by_company as b on a.company_id = b.company_id
                            where b.company_id is null"""

get_rows_from_load = """
                    SELECT *
                    FROM jobs_by_company
                    where job_id in (
                    SELECT job_id
                    FROM jobs_by_company
                    where _dlt_load_id  = '1758632600.1228921'
                    )
                    """

dedupe = """DELETE FROM jobs_by_company
            where _dlt_load_id = '1758247001.2527106' and job_id in (
                    SELECT job_id
                    FROM jobs_by_company
                    GROUP BY 1
                    HAVING COUNT(*)>1)"""


# Company Data
def db_followed_companies(db_path, limit=None):
    db = duckdb.connect(db_path)
    select = "select * from linkedin_data.followed_companies"
    select = f"{select} limit {limit}"
    followed_companies = db.sql(select)
    return followed_companies.df().to_dict(orient="records")


# Job Postings
def jobs_by_company(db_path):
    db = duckdb.connect(db_path)
    followed_companies = db.sql("select * from linkedin_data.jobs_by_company")
    return followed_companies.df()


def get_jobs_ids(db_path):
    db = duckdb.connect(db_path)
    followed_companies = db.sql(
        "select REPLACE(job_posting_urn, 'urn:li:fsd_jobPosting:','') as job_id from linkedin_data.jobs_by_company"
    )
    return followed_companies.df()["job_id"].to_list()


def get_jobs_filtered(db_path, filter_str="'Data' in job_posting_title"):
    db = duckdb.connect(db_path)
    jobs = db.sql(
        """
        select distinct a.job_posting_title,
                        b.company_name,
                        a.job_posting_urn,
                        a.location,
                        a.job_id,
                        case
                            when CONTAINS(lower(a.location),'remote') then 1
                            else 0
                        end as is_remote
        from (
                Select job_posting_urn,
                        LOWER(job_posting_title) as job_posting_title,
                        company_id,
                        secondary_description as location,
                        job_id
                FROM linkedin_data.jobs_by_company) as a
            left join (
                SELECT name as company_name, company_id
                FROM linkedin_data.followed_companies) as b
            on a.company_id=b.company_id
            """
    )
    data_jobs = jobs.filter(filter_str)
    return data_jobs.df()


def get_data_jobs(db_path):
    return get_jobs_filtered(db_path, data_jobs_filter)


def get_rs_jobs(db_path):
    test = get_jobs_filtered(db_path, rs_jobs_filter)
    return test


def get_software_jobs(db_path):
    return get_jobs_filtered(db_path, software_jobs_filter)


# Job Descriptions
def get_job_descs(db_path):
    db = duckdb.connect(db_path)
    job_descs = db.sql("select job_posting_urn from linkedin_data.job_description")
    return job_descs.df()["job_posting_urn"].to_list()


# Transforming job data
def generate_job_urls(db_path, filter_str="1=1", as_csv=False, create_table=False):
    orig_filter_str = filter_str
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

    jobs = get_jobs_filtered(db_path, filter_str)

    jobs["job_id"] = jobs["job_posting_urn"].str.replace("urn:li:fsd_jobPosting:", "")
    jobs["job_urls"] = "https://www.linkedin.com/jobs/view/" + jobs["job_id"]
    job_urls = [
        (x, y) for x, y in zip(jobs["job_urls"], jobs["company_name"].to_list())
    ]

    if as_csv:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d")
        if filter_str == orig_filter_str:
            orig_filter_str = "test"
        jobs.to_csv(f"jobs_matching_{orig_filter_str}_{timestamp}.csv", index=False)
    if create_table:
        db = duckdb.connect(db_path)
        db.sql("DROP TABLE linkedin_data.job_urls")
        db.sql(
            "CREATE TABLE IF NOT EXISTS linkedin_data.job_urls (url TEXT, company_name TEXT)"
        )
        _ = db.executemany(
            "INSERT INTO linkedin_data.job_urls (url, company_name) VALUES (?, ?)",
            job_urls,
        )

    return job_urls


def read_csvs():
    db_path = "linkedin.duckdb"
    import pandas as pd

    jobs_list = []
    for file_type in ["data", "rs", "software", "other", "test"]:
        file_name = f"jobs_matching_{file_type}_20250922.csv"
        jobs = pd.read_csv(file_name)
        job_ids = jobs["job_id"].to_list()
        jobs_list.extend(job_ids)

    existing_jobs = pd.DataFrame(jobs_list, columns=["job_id"], dtype=str)
    all_jobs = pd.DataFrame(get_jobs_ids(db_path), columns=["job_id"], dtype=str)

    outer_join = all_jobs.merge(existing_jobs, how="outer", indicator=True)
    # anti_join = outer_join[~(outer_join._merge == 'both')].drop('_merge', axis = 1)
    new_jobs = outer_join[outer_join._merge == "left_only"].drop("_merge", axis=1)

    db = duckdb.connect(db_path)
    db.sql("DROP TABLE linkedin_data.new_jobs")
    db.sql("CREATE TABLE IF NOT EXISTS linkedin_data.new_jobs (job_id TEXT)")
    _ = db.executemany(
        "INSERT INTO linkedin_data.new_jobs (job_id) VALUES (?)", new_jobs
    )


if __name__ == "__main__":
    # read_csvs()
    db_path = "linkedin.duckdb"
    # filters = ['data', 'rs', 'software', 'other']
    filters = [
        """ job_id  in (
    SELECT job_id
    FROM linkedin_data.new_jobs)
    and ( ("""
        + data_jobs_filter
        + ") OR ("
        + rs_jobs_filter
        + ") OR ("
        + ml_jobs_filter
        + ") OR ("
        + software_jobs_filter
        + ") )"
    ]
    for filter_str in filters:
        generate_job_urls(
            db_path, filter_str=filter_str, as_csv=True, create_table=False
        )
