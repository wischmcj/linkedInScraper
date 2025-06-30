import duckdb

db = duckdb.connect("linkedin.duckdb")



# @dlt.resource
def db_followed_companies():
    db = duckdb.connect("linkedin.duckdb") 
    followed_companies = db.sql("select * from linkedin_data.followed_companies")
    return followed_companies.df().to_dict(orient='records')

def get_finished_jobs():
    db = duckdb.connect("linkedin.duckdb") 
    job_descs = db.sql("select job_posting_urn from linkedin_data.job_description")
    return job_descs.df()['job_posting_urn'].to_list()

def identified_jobs():
    db = duckdb.connect("linkedin.duckdb") 
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
    
def get_jobs_filtered(filter_str = "'Data' in job_posting_title" ):
    db = duckdb.connect("linkedin.duckdb")
    jobs = db.sql("""
        select distinct a.job_posting_title, 
                        b.company_name, 
                        a.job_posting_urn,
                        c.description
        from (
                Select job_posting_urn, 
                        job_posting_title, 
                        _followed_companies_company_id 
                FROM linkedin_data.jobs_by_company) as a 
            left join (
                SELECT name as company_name, company_id 
                FROM linkedin_data.followed_companies) as b 
            on a._followed_companies_company_id=b.company_id
            left join (
                SELECT job_posting_urn, description_text as description
                FROM linkedin_data.job_description) as c 
            on a.job_posting_urn=c.job_posting_urn""")
    data_jobs = jobs.filter(filter_str)
    return data_jobs.df()
    