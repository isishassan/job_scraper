## Personalised Job Scraper (WIP)

Some bigger companies (e.g. Siemens, Maersk, Deutsche Bahn) have really interesting jobs buried deep on their careers page. I could get frustrated using bad filtering systems, or I could use this as an opportunity to build a little scraping tool and practicising some skills.
Therefore, I am building company-specific scrapers, matching the job descriptions against my CV and preferences and storing good matches in SQL. Using dbt, I will schedule a company-specific scraper to run each weekday, so I have new jobs to review each day.

This projects main goals are
1) practice - I am a novice at machine learning and building up my skills
2) find good job matches

### MVP

1. Configure Job Preferences (Python)

- set up job preferences (e.g. job location, high/low weight terms, hard exclusion criteria)

2. Build Company specific scrapers (Jupyter Notebook, SQLite)

- scrape all job titles and locations from careers pages
- exclude job titles based on hard exclusion criteria
- scrape remaining job descriptions, match against job preferences using TF-IDF Vectorizer
- store in SQLite table

### Process Improvements Planned

1. Scheduling / Orchestration (dbt)

- schedule a scraper to run each weekday (assuming I have five)
- dbt is a gap in my CV, so I plan to use this project to teach myself

2. Update it to work for a person other than myself (without Python skills)
