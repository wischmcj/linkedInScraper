
from saved_queries import (
    get_data_jobs,
    get_software_jobs,
    db_followed_companies
)
from pandas import DataFrame

import re
from itertools import chain
from collections import Counter

my_resume_skills = [
    "ETL",
    "pipeline",
    "pipelines",
    "cloud infrastructure",
    "AWS",
    "CloudFormation"
    "Docker",
    "ECS",
    "IaC",
    "Terraform",
    "CI/CD",
    "GitHub Actions",
    "orchestration",
    "Prefect",
    "Airflow",
    "PostgreSQL",
    "Redshift",
    "Snowflake",
    "dbt",
    "SQL",
    "data governance",
    "data quality",
    "Python",
    "NumPy",
    "Pandas",
    "PyTorch",
    "geospatial data",
    "LiDAR",
    "remote sensing",
    "distributed",
    "K3s",
    "kubernetes",
]

stopwords_for_skills_analysis = [
        'company', 'team', 'role', 'position', 'opportunity', 'applicant', 'applicants', 'candidate', 'candidates',
        'employer', 'employment', 'organization', 'department', 'member', 'members', 'join', 'work', 'working',
        'environment', 'culture', 'mission', 'vision', 'values', 'benefits', 'offer', 'offers', 'provide', 'provides',
        'including', 'include', 'includes', 'responsibility', 'responsibilities', 'requirement', 'requirements',
        'qualification', 'qualifications', 'preferred', 'desired', 'must', 'should', 'will', 'may', 'can', 'ability',
        'experience', 'years', 'year', 'background', 'backgrounds', 'degree', 'bachelor', 'bachelors', 'master', 'masters',
        'phd', 'education', 'field', 'related', 'relevant', 'applicable', 'equal', 'opportunity', 'employer', 'status',
        'protected', 'veteran', 'disability', 'race', 'color', 'religion', 'sex', 'gender', 'identity', 'expression',
        'sexual', 'orientation', 'age', 'national', 'origin', 'law', 'laws', 'regard', 'regarding', 'consideration',
        'consider', 'consistent', 'accommodation', 'reasonable', 'applicants', 'applying', 'application', 'submit',
        'submission', 'please', 'contact', 'us', 'email', 'phone', 'address', 'location', 'locations', 'remote', 'onsite',
        'hybrid', 'full-time', 'part-time', 'contract', 'internship', 'temporary', 'permanent', 'salary', 'compensation',
        'pay', 'bonus', 'equity', 'stock', 'insurance', 'benefit', 'vacation', 'leave', 'holiday', 'holidays', 'time',
        'off', 'schedule', 'hours', 'shift', 'shifts', 'week', 'weeks', 'month', 'months', 'day', 'days', 'night',
        'weekend', 'weekends', 'travel', 'relocation', 'required', 'not', 'required', 'preferred', 'plus', 'etc', 'etc.',
        'other', 'additional', 'various', 'variety', 'multiple', 'different', 'varied', 'varies', 'variety', 'across',
        'within', 'throughout', 'per', 'as', 'needed', 'when', 'where', 'how', 'who', 'what', 'which', 'with', 'without',
        'and', 'or', 'but', 'if', 'then', 'so', 'such', 'that', 'this', 'these', 'those', 'the', 'a', 'an', 'in', 'on',
        'at', 'by', 'for', 'to', 'from', 'of', 'about', 'over', 'under', 'between', 'among', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'out', 'into', 'upon', 'across', 'along', 'around', 'through', 'throughout',
        'each', 'every', 'all', 'any', 'some', 'none', 'few', 'many', 'most', 'more', 'less', 'least', 'greatest',
        'best', 'better', 'good', 'excellent', 'outstanding', 'strong', 'stronger', 'strongest', 'successful', 'success',
        'successfully', 'high', 'higher', 'highest', 'low', 'lower', 'lowest', 'new', 'old', 'current', 'future',
        'past', 'present', 'previous', 'recent', 'now', 'today', 'tomorrow', 'yesterday', 'soon', 'immediately',
        'quickly', 'fast', 'slow', 'slower', 'slowest', 'easy', 'easily', 'difficult', 'hard', 'challenging', 'complex',
        'simple', 'basic', 'advanced', 'intermediate', 'junior', 'senior', 'lead', 'manager', 'director', 'executive',
        'chief', 'officer', 'head', 'supervisor', 'coordinator', 'specialist', 'analyst', 'consultant', 'assistant',
        'associate', 'intern', 'trainee', 'entry', 'level', 'mid', 'mid-level', 'senior-level', 'principal', 'staff',
        'individual', 'contributor', 'collaborate', 'collaboration', 'communicate', 'communication', 'interpersonal',
        'skills', 'skill', 'ability', 'abilities', 'aptitude', 'talent', 'proficiency', 'knowledge', 'understanding',
        'awareness', 'familiarity', 'expertise', 'expert', 'specialist', 'specialization', 'focus', 'interest', 'passion',
        'enthusiasm', 'motivation', 'drive', 'initiative', 'self', 'independent', 'independently', 'teamwork', 'team',
        'teams', 'member', 'members', 'group', 'groups', 'collaborative', 'environment', 'setting', 'workplace',
        'office', 'site', 'facility', 'location', 'locations', 'branch', 'branches', 'division', 'department',
        'organization', 'company', 'firm', 'business', 'corporation', 'enterprise', 'industry', 'sector', 'field',
        'area', 'areas', 'domain', 'discipline', 'function', 'functions', 'role', 'roles', 'position', 'positions',
        'job', 'jobs', 'opening', 'openings', 'vacancy', 'vacancies', 'posting', 'postings', 'advertisement',
        'description', 'descriptions', 'summary', 'summaries', 'overview', 'details', 'information', 'info', 'data',
        'record', 'records', 'document', 'documents', 'report', 'reports', 'reporting', 'system', 'systems', 'tool',
        'tools', 'technology', 'technologies', 'software', 'hardware', 'platform', 'platforms', 'application',
        'applications', 'program', 'programs', 'project', 'projects', 'task', 'tasks', 'assignment', 'assignments',
        'responsibility', 'responsibilities', 'duty', 'duties', 'function', 'functions', 'requirement', 'requirements',
        'expectation', 'expectations', 'goal', 'goals', 'objective', 'objectives', 'target', 'targets', 'deliverable',
        'deliverables', 'output', 'outputs', 'result', 'results', 'outcome', 'outcomes', 'achievement', 'achievements',
        'performance', 'standard', 'standards', 'policy', 'policies', 'procedure', 'procedures', 'process', 'processes',
        'practice', 'practices', 'method', 'methods', 'approach', 'approaches', 'strategy', 'strategies', 'plan',
        'plans', 'planning', 'implementation', 'execution', 'operation', 'operations', 'management', 'supervision',
        'leadership', 'direction', 'guidance', 'support', 'assistance', 'help', 'aid', 'service', 'services', 'customer',
        'client', 'clients', 'user', 'users', 'stakeholder', 'stakeholders', 'partner', 'partners', 'vendor', 'vendors',
        'supplier', 'suppliers', 'contractor', 'contractors', 'consultant', 'consultants', 'advisor', 'advisors',
        'liaison', 'contact', 'contacts', 'network', 'networking', 'relationship', 'relationships', 'interaction',
        'interactions', 'communication', 'communications', 'presentation', 'presentations', 'meeting', 'meetings',
        'conference', 'conferences', 'event', 'events', 'training', 'trainings', 'development', 'learning', 'education',
        'certification', 'certifications', 'license', 'licenses', 'registration', 'registrations', 'compliance',
        'regulation', 'regulations', 'law', 'laws', 'policy', 'policies', 'procedure', 'procedures', 'standard',
        'standards', 'guideline', 'guidelines', 'requirement', 'requirements', 'expectation', 'expectations'
    ]

def remove_stopwords(text, stopwords=None):
    if stopwords is None:
        # A basic set of English stopwords
        stopwords = {
            'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'on', 'with', 'as', 'by', 'an', 'at', 'from', 'or',
            'that', 'this', 'be', 'are', 'it', 'will', 'we', 'you', 'your', 'our', 'can', 'if', 'not', 'have',
            'has', 'but', 'they', 'their', 'all', 'more', 'may', 'such', 'any', 'which', 'who', 'what', 'when',
            'where', 'how', 'about', 'into', 'also', 'other', 'than', 'these', 'those', 'been', 'was', 'were',
            'so', 'do', 'does', 'did', 'should', 'would', 'could', 'no', 'yes', 'he', 'she', 'his', 'her', 'its',
            'them', 'then', 'there', 'out', 'up', 'down', 'over', 'under', 'again', 'new',
            'role', 'roles', 'experience', 'skills', 'skill', 'requirement', 'requirements', 'responsibility', 'responsibilities', 'requirement', 'requirements', 'requirement', 'requirements',
        }
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word not in stopwords]
    return ' '.join(filtered_tokens)

def preprocess_text(text, company_names):
    # Remove special characters, keep only words and spaces, lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text))
    text = re.sub(r'\s+', ' ', text)
    text = remove_stopwords(text)
    text = remove_stopwords(text, ['apply', 'easy', 'logo','follow',
                                    'state','federal','qualified','experience','skills','skill','requirement','requirements',
                                    'responsibility','responsibilities','requirement','requirements','requirement','requirements',
                                    'e','g', 't','c','linkedin','company','work','years','year','day','days','month','months',
                                    'degree','bachelor','master','phd','masters','bachelors',
                                    'fair chance', 'software engineer', 'computer science', 'us', 
                                    'job details', 'blue', 'origin', 'want', 'learn', 'jobot', 'click', 'now', 'equal', 'opportunity', 
                                    'sexual', 'orientation', 'national', 'gender', 'veteran', 'computer', 'race','fair', 'chance', 'apply', 'easy', 'logo','follow',
                                    'without regard','protected status', 'team members', 'problem solving', 'related', 
                                    'field', 'employment','without', 'consideration', 'regard','color',
                                    'follow',
                                    'state','federal','qualified','experience','skills','skill','requirement','requirements',
                                    'responsibility','responsibilities','requirement','requirements','requirement','requirements',
                                    'e','g', 't','c','linkedin','company',
                                    'job','details', 'click', 'now', 'equal', 'opportunity', 
                                    'protected','status','team','members','solving','related','field',
                                    'local','laws', 'characteristic'
                                    ])
    text= remove_stopwords(text, ['accommodation', 'age', 'angeles', 'applicable', 'apply', 'authorization', 
                                  'bachelor', 'bachelors', 'backed', 'background', 'backgrounds', 'best', 
                                  'bio', 'bit', 'blue', 'button', 'candidates', 'celebrates', 'chance', 
                                  'characteristic', 'checks', 'click', 'clicking', 'color', 'combinator', 
                                  'company', 'computer', 'consider', 'consideration', 'consistent', 
                                  'criminal', 'cross', 'd', 'day', 'days', 'degree', 'details', 'disability', 
                                  'diversity', 'driven', 'easy', 'employer', 'employment', 'environment', 'equal', 
                                  'excited', 'expression', 'fair', 'fast', 'field', 'fit', 'follow', 'francisco', 
                                  'functional', 'gender', 'generation', 'genetics', 'hearing', 'hiring', 'histories',
                                    'holidays', 'identity', 'including', 'inclusive', 'initiative', 'interested', 
                                    'job', 'jobot', 'join', 'labs', 'law', 'laws', 'leave', 'limited', 'local', 'logo',
                                      'looking', 'los', 'love', 'manner', 'master', 'masters', 'members', 'mission', 
                                      'month', 'months', 'national', 'next', 'now', 'opportunity', 'ordinance', 
                                      'orientation', 'origin', 'paced', 'page', 'paid', 'parental', 'per', 'perform', 
                                      'phd', 'please', 'practices', 'process', 'protected', 'provide', 'race', 
                                      're', 'reasonable', 'receive', 'regard', 'regarding', 'related', 'religion', 
                                      'required', 'resume', 's', 'salary', 'san', 'sending', 'sex', 'sexual',
                                        'solving', 'sometimes', 'staff', 'status', 'team', 'tech', 
                                  'time', 'trm', 'us', 'veteran', 'why', 'without', 'work', 'y', 'year', 'years'])
    text = remove_stopwords(text, company_names)
    text = remove_stopwords(text, stopwords_for_skills_analysis)
    return text

def get_ngrams(text, n=2):
    tokens = text.split()
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def extract_common_ngrams(df, field='description', n=2, top_k=20, company_names=None):
    ngram_counter = Counter()
    for desc in df[field].dropna():
        clean_text = preprocess_text(str(desc).lower(), company_names)
        ngrams = get_ngrams(clean_text, n)
        ngram_counter.update(ngrams)
    return ngram_counter.most_common(top_k)

def ngrams(n=2,k=30):

    data_jobs = get_data_jobs()
    software_jobs = get_software_jobs()
    companies = db_followed_companies()
    company_names = list(chain.from_iterable([company['name'].split(' ')[0] for company in companies]))
    # Function to remove stop words from text
    print("Top bigrams in data_jobs:")
    ngrams =    extract_common_ngrams(data_jobs, field='description', n=n, top_k=k,company_names=company_names)
    print(ngrams)
    return ngrams

def count_keyword_instances(jobs, job_description_key='description'):
    """
    Ranks jobs by the number of my_resume_skills keywords found in each job's description.

    Args:
        jobs (list of dict): List of job dicts, each containing a job description.
        my_resume_skills (list of str): List of keywords/skills to search for.
        job_description_key (str): Key in job dict for the job description.

    Returns:
        list of dict: Jobs sorted in descending order by number of skill matches.
    """
    import re

    # Preprocess skills for case-insensitive matching
    skills_set = set([skill.lower() for skill in my_resume_skills if skill.strip()])

    def count_skills_in_text(text):
        if not isinstance(text, str):
            return 0
        # Tokenize text into words, lowercase
        words = re.findall(r'\b\w+\b', text.lower())
        return sum(1 for word in words if word in skills_set)

    # Annotate each job with a count of skill matches
    print(jobs.columns)
    import pandas as pd 
    jobs['resume_skill_matches'] = pd.Series([count_skills_in_text(x) for x in jobs[job_description_key]])
    # Sort jobs by number of matches, descending
    jobs.sort_values(by = ['resume_skill_matches'])
    # ranked_jobs = sorted(jobs, key=lambda x: x['resume_skill_matches'], reverse=True)
    return jobs
    
if __name__ == "__main__":
    ranked_jobs = count_keyword_instances(get_data_jobs())
    print(ranked_jobs)

    # print("\nTop bigrams in software_jobs:")
    # print(extract_common_ngrams(software_jobs, field='description', n=2, top_k=20))
    # breakpoint()
    # Identify a list of words in the below that are irrelevant to the purpose of the job whose description they appear in

    breakpoint()
