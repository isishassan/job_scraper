"""
DB Jobs Scraper & CV Matcher
Scrapes Deutsche Bahn job listings and scores them against your CV profile.
Run weekly: python db_job_scraper.py
Output: db_jobs_YYYY-MM-DD.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import urllib.parse

# ─────────────────────────────────────────────
# YOUR CV PROFILE
# Edit this to adjust what gets weighted heavily
# ─────────────────────────────────────────────

CV_TEXT = """
Senior Analytics und Insights Führungskraft mit 10 Jahren Erfahrung im E-Commerce.
SQL Experte BigQuery Datenanalyse Business Intelligence KPI Kennzahlen Reporting.
Kundenfeedback Kundeninsights Voice of Customer VoC NPS Retourenanalyse Funnel-Analyse.
Machine Learning ML Python scikit-learn NLP Textklassifikation Feature Engineering.
Looker Dashboards Tableau Google Cloud Platform Datenvisualisierung.
Produktanalyse Product Owner Product Manager E-Commerce Lead Digitalisierung.
Prozessautomatisierung Workflow-Optimierung Effizienzsteigerung Prozessverbesserung.
Stakeholder-Management abteilungsübergreifende Teams Data Governance Metrik-Definition.
Kundensegmentierung Kundenerlebnis Merchandising Lieferantenmanagement.
Retourenreduzierung Produktoperationen BPO-Management.
Teamführung OKR Roadmap-Planung Analytics-Anforderungen Requirements Engineering.
Data Product Manager Lead Analyst Senior Data Analyst Senior Analyst.
Digitales Merchandising Produktinhalt Katalogqualität Content Management.
Predictive Modelling logistische Regression BERT NLP Kundenfeedback Sentiment.
Datengetriebene Entscheidungen Datenstrategie Datenqualität.
SQL analytics data analysis business intelligence KPI dashboard
customer insights ecommerce product analytics returns merchandising
python machine learning process automation stakeholder management reporting
"""

# Keywords that boost relevance score
HIGH_WEIGHT_TERMS = [
    "sql", "datenanalyse", "data analysis", "analytics", "business intelligence", "bi",
    "looker", "product analytics", "kundeninsights", "customer insights", "kpi",
    "dashboard", "reporting", "e-commerce", "ecommerce", "digital", "retouren",
    "merchandising", "digitalisierung", "daten", "data", "datenanalyse"
]
MEDIUM_WEIGHT_TERMS = [
    "python", "machine learning", "ml", "prozessverbesserung", "automatisierung",
    "stakeholder", "product owner", "product manager", "produktmanager",
    "anforderungen", "requirements", "projektmanagement"
]
IGNORE_TERMS = [
    # Trades & physical operations
    "fahrdienstleiter", "lokführer", "triebfahrzeugführer", "baggerfahrer",
    "schweißer", "elektriker", "monteur", "gleisbau", "tiefbau", "hochbau",
    "mechaniker", "stapler", "schaffner", "zugbegleiter", "sicherheitsbeamter",
    "bauüberwacher", "oberbau", "oberleitung",
    "gleise", "weichen", "signaltechnik", "leit- und sicherungstechnik",
    # Entry level / student programmes
    "ausbildung", "duales studium", "praktikum", "werkstudent",
    # Other
    "kraftfahrer", "busfahrer",
]

# ─────────────────────────────────────────────
# SCRAPER CONFIG
# ─────────────────────────────────────────────

BASE_URL = "https://db.jobs"
SEARCH_URL = "https://db.jobs/service/search/de-de/5441588"

# Only keep jobs where location contains one of these strings (case-insensitive)
# "wo du willst" = DB label for fully remote roles
ALLOWED_LOCATIONS = ["berlin", "wo du willst"]

# Run multiple focused queries instead of scraping all 3,385 jobs.
# Deduplication removes overlaps between queries.
SEARCH_QUERIES = [
    "Analyst",
    "Analytics",
    "Data",
    "Digitalisierung",
    "Product Manager",
    "Produktmanager",
    "Business Intelligence",
    "Reporting",
]

MAX_PAGES_PER_QUERY = 5   # 5 pages x 20 jobs x 8 queries = up to 800 before dedup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}

PAGE_SIZE = 20
SLEEP_BETWEEN_PAGES = 1.5
SLEEP_BETWEEN_DETAIL_PAGES = 1.0

MIN_SCORE = 15
PRE_FILTER_SCORE = 5


# ─────────────────────────────────────────────
# SCRAPING
# ─────────────────────────────────────────────

def is_allowed_location(location: str) -> bool:
    """Check if job location matches our Berlin/remote filter."""
    loc_lower = location.lower()
    return any(allowed in loc_lower for allowed in ALLOWED_LOCATIONS)


def fetch_page(query: str, page_num: int) -> list[dict]:
    """Fetch one page of job listings for a given search query."""
    params = {
        "country": "Deutschland",
        "qli": "true",
        "query": query,
        "targetGroup": "",
        "sort": "score",
        "page": page_num,
    }
    url = SEARCH_URL + "?" + urllib.parse.urlencode(params)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ⚠️  Page {page_num} failed: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []

    for hit in soup.select(".m-search-hit"):
        title_el = hit.select_one(".m-search-hit__title")
        title = title_el.get_text(strip=True) if title_el else ""

        link = hit.get("href", "")
        if link and not link.startswith("http"):
            link = BASE_URL + link

        job_id = hit.get("data-job-id", "")

        detail_items = hit.select(".m-search-hit__detail-item, li")
        details = [d.get_text(strip=True) for d in detail_items if d.get_text(strip=True)]
        location = details[0] if len(details) > 0 else ""
        company = details[1] if len(details) > 1 else "Deutsche Bahn"
        start_date = details[2] if len(details) > 2 else ""

        if title and is_allowed_location(location):
            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "start_date": start_date,
                "link": link,
                "description": title,
            })

    return jobs


def fetch_description(job: dict) -> str:
    """
    Fetch full job description from detail page.
    DB embeds job content in a JS digitalData object — we extract it with regex.
    Returns combined tasks + profile text, HTML tags stripped.
    """
    if not job.get("link"):
        return job["title"]

    try:
        resp = requests.get(job["link"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    ⚠️  Detail fetch failed for {job['title'][:40]}: {e}")
        return job["title"]

    html = resp.text

    # Extract jobTasks and jobProfile from the embedded JS digitalData object
    tasks_match = re.search(r'"jobTasks":\s*"(.*?)",\s*"jobProfile"', html, re.DOTALL)
    profile_match = re.search(r'"jobProfile":\s*"(.*?)",\s*"language"', html, re.DOTALL)

    tasks = tasks_match.group(1) if tasks_match else ""
    profile = profile_match.group(1) if profile_match else ""

    # Unescape JS string (e.g. \/ → /)
    combined = (tasks + " " + profile).replace("\\/", "/").replace("\\n", " ").replace('\\"', '"')

    # Strip HTML tags
    clean = re.sub(r"<[^>]+>", " ", combined)
    # Collapse whitespace
    clean = re.sub(r"\s+", " ", clean).strip()

    return clean if clean else job["title"]


def enrich_with_descriptions(jobs: list[dict]) -> list[dict]:
    """Fetch full descriptions for all jobs. Shows progress."""
    print(f"📄 Fetching full descriptions for {len(jobs)} jobs (this takes a few minutes)...")
    for i, job in enumerate(jobs, 1):
        print(f"  [{i}/{len(jobs)}] {job['title'][:55]}", end=" ... ")
        desc = fetch_description(job)
        job["description"] = desc
        word_count = len(desc.split())
        print(f"{word_count} words")
        time.sleep(SLEEP_BETWEEN_DETAIL_PAGES)
    print(f"✅ Descriptions fetched.\n")
    return jobs


def scrape_all_jobs() -> list[dict]:
    """Run all search queries, filter by location, deduplicate."""
    all_jobs = []
    loc_str = " / ".join(ALLOWED_LOCATIONS)
    print(f"🔍 Scraping DB jobs | Location: {loc_str} | {len(SEARCH_QUERIES)} queries × {MAX_PAGES_PER_QUERY} pages...")

    for query in SEARCH_QUERIES:
        print(f"\n  Query: '{query}'")
        for page in range(1, MAX_PAGES_PER_QUERY + 1):
            jobs = fetch_page(query, page)
            if not jobs:
                break
            all_jobs.extend(jobs)
            print(f"    Page {page}: {len(jobs)} location-matched jobs (running total: {len(all_jobs)})")
            time.sleep(SLEEP_BETWEEN_PAGES)

    # Deduplicate by job_id
    seen = set()
    unique = []
    for j in all_jobs:
        if j["job_id"] not in seen:
            seen.add(j["job_id"])
            unique.append(j)

    print(f"\n✅ Scraped {len(unique)} unique location-matched jobs.\n")
    return unique


# ─────────────────────────────────────────────
# FILTERING
# ─────────────────────────────────────────────

def is_clearly_irrelevant(title: str) -> bool:
    """Filter out jobs you'd never apply to."""
    title_lower = title.lower()
    for term in IGNORE_TERMS:
        if term in title_lower:
            return True
    return False


# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────

def keyword_bonus(text: str) -> float:
    """Extra score for high/medium weight terms present in job title."""
    text_lower = text.lower()
    bonus = 0
    for term in HIGH_WEIGHT_TERMS:
        if term in text_lower:
            bonus += 8
    for term in MEDIUM_WEIGHT_TERMS:
        if term in text_lower:
            bonus += 3
    return min(bonus, 30)  # cap bonus at 30 points


def score_jobs(jobs: list[dict]) -> list[dict]:
    """Score jobs using TF-IDF cosine similarity + keyword bonus."""
    print("📊 Scoring jobs against your CV profile...")

    descriptions = [j["description"] for j in jobs]
    corpus = [CV_TEXT] + descriptions

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words=None,       # keep German words
        max_features=5000
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    cv_vector = tfidf_matrix[0]
    job_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(cv_vector, job_vectors)[0]

    for i, job in enumerate(jobs):
        base_score = round(similarities[i] * 100, 1)
        bonus = keyword_bonus(job["description"])
        final_score = min(round(base_score + bonus, 1), 100)
        job["score"] = final_score

    jobs.sort(key=lambda x: x["score"], reverse=True)
    print(f"✅ Scoring complete.\n")
    return jobs


# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────

def save_csv(jobs: list[dict], filename: str):
    """Save results to CSV."""
    fieldnames = ["score", "title", "company", "location", "start_date", "link", "job_id"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(jobs)

    print(f"💾 Saved to {filename}")


def print_top(jobs: list[dict], n: int = 20):
    """Print top N results to terminal."""
    print(f"\n{'─'*70}")
    print(f"TOP {n} MATCHES")
    print(f"{'─'*70}")
    for i, job in enumerate(jobs[:n], 1):
        print(f"{i:>2}. [{job['score']:>5}] {job['title']}")
        print(f"     {job['company']} | {job['location']}")
        print(f"     {job['link']}")
        print()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Scrape job listings (titles + links)
    jobs = scrape_all_jobs()

    # 2. Filter obvious noise by title (saves time fetching descriptions)
    before = len(jobs)
    jobs = [j for j in jobs if not is_clearly_irrelevant(j["title"])]
    print(f"🗑️  Filtered out {before - len(jobs)} irrelevant jobs by title.\n")

    # 3. Fetch full descriptions
    jobs = enrich_with_descriptions(jobs)

    # 4. Score against CV
    jobs = score_jobs(jobs)

    # 5. Apply minimum score threshold
    jobs_above = [j for j in jobs if j["score"] >= MIN_SCORE]
    print(f"📋 {len(jobs_above)} jobs above minimum score threshold ({MIN_SCORE})\n")

    # Always show top 20 regardless of threshold (useful for calibration)
    print_top(jobs, n=20)

    filename = f"db_jobs_{date.today()}.csv"
    save_csv(jobs, filename)  # saves ALL scored jobs so you can inspect the full range
    print(f"\nDone. Open {filename} to review all results.")
    print(f"Tip: Sort by 'score' column descending. Adjust MIN_SCORE if results look off.")
