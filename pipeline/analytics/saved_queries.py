import duckdb

data_jobs_filter = """('data engineer' in job_posting_title
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
                        OR 'developer' in job_posting_title
                        """

# Company Data
def db_followed_companies(db_path):
    db = duckdb.connect(db_path) 
    followed_companies = db.sql("select * from linkedin_data.followed_companies" )
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
                        case 
                            when CONTAINS(lower(a.location),'remote') then 1
                            else 0
                        end as is_remote
        from (
                Select job_posting_urn, 
                        LOWER(job_posting_title) as job_posting_title, 
                        _followed_companies_company_id,
                        secondary_description as location
                FROM linkedin_data.jobs_by_company) as a 
            left join (
                SELECT name as company_name, company_id 
                FROM linkedin_data.followed_companies) as b 
            on a._followed_companies_company_id=b.company_id
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

    jobs = get_jobs_filtered(db_path, filter_str)

    jobs['job_id'] = jobs['job_posting_urn'].str.replace('urn:li:fsd_jobPosting:','')
    jobs['job_urls'] = 'https://www.linkedin.com/jobs/view/' + jobs['job_id']
    job_urls = [(x, y) for x, y in zip(jobs['job_urls'], jobs['company_name'].to_list())]

    if as_csv:
        jobs.to_csv(f'jobs_matching_{orig_filter_str}.csv', index=False)

    if create_table:
        db = duckdb.connect(db_path) 
        db.sql("DROP TABLE linkedin_data.job_urls")
        db.sql("CREATE TABLE IF NOT EXISTS linkedin_data.job_urls (url TEXT, company_name TEXT)")
        _ = db.executemany("INSERT INTO linkedin_data.job_urls (url, company_name) VALUES (?, ?)", job_urls)   

    return job_urls

if __name__ == "__main__":
    db_path = "linkedin.duckdb"
    for filter_str in ['data', 'rs', 'software']:
        generate_job_urls(db_path, filter_str = filter_str, as_csv=True, create_table=False)
#     breakpoint()
