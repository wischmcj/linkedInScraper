import duckdb



# @dlt.resource
def db_followed_companies(db_path):
    db = duckdb.connect(db_path) 
    followed_companies = db.sql("select * from linkedin_data.followed_companies" )
    return followed_companies.df().to_dict(orient='records')

def db_job_urls(db_path):
    db = duckdb.connect(db_path) 
    job_urls = db.sql("select * from linkedin_data.job_urls")
    return job_urls.df().to_dict(orient='records')

def get_finished_jobs(db_path):
    db = duckdb.connect(db_path) 
    job_descs = db.sql("select job_posting_urn from linkedin_data.job_description")
    return job_descs.df()['job_posting_urn'].to_list()

def identified_jobs(db_path):
    db = duckdb.connect(db_path) 
    followed_companies = db.sql("select job_posting_title from linkedin_data.jobs_by_company")
    return followed_companies.df()['job_id'].to_list()

def delete_not_followed_company_jobs():
    jobs = db.sql("""
        DELETE FROM linkedin_data.jobs_by_company
        WHERE job_posting_urn in (
            select distinct a.job_posting_urn
            from (
                    Select job_posting_urn, 
                            job_posting_title, 
                            _followed_companies_company_id 
                    FROM linkedin_data.jobs_by_company) as a 
                left join (
                    SELECT name as company_name, company_id 
                    FROM linkedin_data.followed_companies) as b 
                on a._followed_companies_company_id=b.company_id
            Where company_name is null
            )""")
    
def get_jobs_filtered(db_path, filter_str = "'Data' in job_posting_title" ):
    db = duckdb.connect(db_path)
    jobs = db.sql("""
        select distinct a.job_posting_title, 
                        b.company_name, 
                        a.job_posting_urn,
                        c.description
                        a.location,
        from (
                Select job_posting_urn, 
                        LOWER(job_posting_title) as job_posting_title, 
                        _followed_companies_company_id 
                FROM linkedin_data.jobs_by_company) as a 
            left join (
                SELECT name as company_name, company_id 
                FROM linkedin_data.followed_companies) as b 
            on a._followed_companies_company_id=b.company_id
            """)
    # left join (
    #             SELECT job_posting_urn, description_text as description
    #             FROM linkedin_data.job_description) as c 
    #         on a.job_posting_urn=c.job_posting_urn
    data_jobs = jobs.filter(filter_str)
    return data_jobs.df()
    
def get_data_jobs(db_path):
    filter_str = """('data engineer' in job_posting_title
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
    return get_jobs_filtered(db_path, filter_str)

def get_rs_jobs(db_path):
    filter_str = """('lidar' in lower(job_posting_title)
                    OR 'lidar' in lower(job_posting_title)
                     OR 'geospatial' in lower(job_posting_title)
                     OR 'remote sensing' in lower(job_posting_title)
                    )
                    """
    test = get_jobs_filtered(db_path, filter_str)
    breakpoint()
    return test

def get_software_jobs(db_path):
    filter_str = """'software engineer' in job_posting_title
                    OR 'software developer' in job_posting_title
                    OR 'software' in job_posting_title
                    OR 'developer' in job_posting_title
                    OR 'developer' in job_posting_title
                    """
    return get_jobs_filtered(db_path, filter_str)

def jobs_by_company(db_path):
    db = duckdb.connect(db_path) 
    followed_companies = db.sql("select * from linkedin_data.jobs_by_company")
    return followed_companies.df()

def get_job_urls(db_path):
    # jobs = get_rs_jobs()
    filter_str = """1=1"""
    jobs = get_jobs_filtered(db_path, filter_str)
    # jobs = get_rs_jobs(db_path)

    # remote_jobs = jobs[jobs['location'].str.contains('Remote')]
    jobs['job_id'] = jobs['job_posting_urn'].str.replace('urn:li:fsd_jobPosting:','')
    jobs['job_urls'] = 'https://www.linkedin.com/jobs/view/' + jobs['job_id']
    job_urls = [(x, y) for x, y in zip(jobs['job_urls'], jobs['company_name'].to_list())]
    jobs.to_csv('all_jobs_20250803.csv', index=False)
    # jobs_not_to_push = ['https://www.linkedin.com/jobs/view/4257497407/']

    # # breakpoint()
    # db = duckdb.connect("linkedin.duckdb") 
    # res = db.sql("SELECT url FROM linkedin_data.job_urls").df().to_list()

    followed_companies = db_followed_companies(db_path)
    # db.sql("DROP TABLE linkedin_data.job_urls")
    # db.sql("CREATE TABLE linkedin_data.job_urls (url TEXT, company_name TEXT)")

    # res = db.executemany("INSERT INTO linkedin_data.job_urls (url, company_name) VALUES (?, ?)", job_urls)

    return followed_companies

def get_column_info(col):
    info = f'{col} TEXT'
    if '_dlt' in col:
        info = f'{col} TEXT NOT NULL'
    return info


def generate_insert_query(columns):
    return f"INSERT INTO linkedin_data.followed_companies ({', '.join(columns)}) VALUES ({', '.join([f'?' for _ in columns])})"

def populate_new_company_db(new_db_path, old_db_path):  
    company_data = db_followed_companies(old_db_path)
    columns =  ['name', '_type', '_recipe_type', 'entity_urn', 'url', 'company_id', '_dlt_load_id', '_dlt_id']
    to_insert = [[row[col] for col in columns] for row in company_data]

    # create schema if not exists
    db = duckdb.connect(new_db_path)
    db.sql("CREATE SCHEMA IF NOT EXISTS linkedin_data")
    db.sql(f"CREATE OR REPLACE TABLE linkedin_data.followed_companies ({', '.join([get_column_info(c) for c in columns])})")
    
    expected_insert_query = "INSERT INTO linkedin_data.followed_companies (name, _type, _recipe_type, entity_urn, url, company_id) VALUES (?, ?, ?, ?, ?, ?)"
    insert_query = generate_insert_query(columns)
    # assert insert_query == expected_insert_query
    breakpoint()
    db.executemany(insert_query, to_insert)

    # old_db_path = "linkedin_1.duckdb"
    # new_db_path = "linkedin.duckdb"
    # populate_new_company_db(new_db_path, old_db_path)

if __name__ == "__main__":
    # old_db_path = "linkedin_1.duckdb"
    new_db_path = "linkedin.duckdb"
    # populate_new_company_db(new_db_path, old_db_path)
    # urls = db_job_urls(new_db_path)

    get_job_urls(new_db_path)
    breakpoint()
