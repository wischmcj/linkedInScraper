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
    if limit:
        followed_companies = db.sql(f"select * from linkedin_data.followed_companies limit {limit}")
    else:
        followed_companies = db.sql("select * from linkedin_data.followed_companies")
    return followed_companies.df().to_dict(orient='records')

# Job Postings
def jobs_by_company(db_path):
    db = duckdb.connect(db_path) 
    followed_companies = db.sql("select * from linkedin_data.jobs_by_company")
    return followed_companies.df()

def get_jobs_ids(db_path):
    db = duckdb.connect(db_path) 
    followed_companies = db.sql("select job_posting_title from linkedin_data.jobs_by_company")
    return followed_companies.df()['job_id'].to_list()

def get_jobs_filtered(db_path, filter_str = "'Data' in job_posting_title" ):
    db = duckdb.connect(db_path)
    jobs = db.sql("""
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
            """)
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
    return job_descs.df()['job_posting_urn'].to_list()

# Transforming job data
def generate_job_urls(db_path,
                 filter_str = "1=1", 
                 as_csv=False,
                 create_table=False):
    orig_filter_str = filter_str
    if filter_str == 'data':
        filter_str = data_jobs_filter
    elif filter_str == 'rs':
        filter_str = rs_jobs_filter
    elif filter_str == 'software':
        filter_str = software_jobs_filter
    elif filter_str == 'ml':
        filter_str = ml_jobs_filter
    elif filter_str == 'all':
        filter_str = data_jobs_filter + ' OR ' + rs_jobs_filter + ' OR ' + ml_jobs_filter + ' OR ' + software_jobs_filter
    elif filter_str == 'other':
        filter_str = 'NOT ( ' + data_jobs_filter + ' ) AND NOT ( ' + rs_jobs_filter + ' ) AND NOT ( ' + rs_jobs_filter + ' )  AND NOT ( ' + software_jobs_filter + ' )'

    jobs = get_jobs_filtered(db_path, filter_str)

    jobs['job_id'] = jobs['job_posting_urn'].str.replace('urn:li:fsd_jobPosting:','')
    jobs['job_urls'] = 'https://www.linkedin.com/jobs/view/' + jobs['job_id']
    job_urls = [(x, y) for x, y in zip(jobs['job_urls'], jobs['company_name'].to_list())]

    if as_csv:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        jobs.to_csv(f'jobs_matching_test_{orig_filter_str}_{timestamp}.csv', index=False)
    if create_table:
        db = duckdb.connect(db_path) 
        db.sql("DROP TABLE linkedin_data.job_urls")
        db.sql("CREATE TABLE IF NOT EXISTS linkedin_data.job_urls (url TEXT, company_name TEXT)")
        _ = db.executemany("INSERT INTO linkedin_data.job_urls (url, company_name) VALUES (?, ?)", job_urls)   

    return job_urls

if __name__ == "__main__":
    db_path = "linkedin.duckdb"
    # filters = ['data', 'rs', 'software', 'other']
    filters = [''' job_id not in (
    SELECT job_id
    FROM linkedin_data.jobs_by_company 
    where _dlt_load_id = '1758247001.2527106')
    and ( (''' + data_jobs_filter + ') OR (' + rs_jobs_filter + ') OR (' + ml_jobs_filter + ') OR (' + software_jobs_filter + ') )']
    for filter_str in filters:
        generate_job_urls(db_path, filter_str = filter_str, as_csv=True, create_table=False)
#     breakpoint()
