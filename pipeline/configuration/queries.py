## These really ought to be udfs or something
from __future__ import annotations

data_jobs_filter = """((
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
                        )

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

software_jobs_filter = """('software engineer' in job_posting_title
                        OR 'software developer' in job_posting_title
                        OR 'software' in job_posting_title
                        OR 'developer' in job_posting_title
                        OR 'programmer' in job_posting_title
                        )
                        """
