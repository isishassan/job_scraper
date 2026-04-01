"""
config_isis.py
User-level configuration for job scraping and scoring.
Import this in any scraper notebook:
    from config_isis import CV_TEXT, HIGH_WEIGHT_TERMS, MEDIUM_WEIGHT_TERMS, IGNORE_TERMS, ALLOWED_LOCATIONS

To adapt for another user: copy this file, rename it (e.g. config_anna.py), and update all values.
"""

# ─────────────────────────────────────────────
# CV PROFILE
# Bilingual (DE/EN) for better TF-IDF matching against German job descriptions.
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
SQL analytics data analysis business intelligence KPI dashboard reporting.
Customer insights ecommerce product analytics returns merchandising.
Python machine learning process automation stakeholder management.
"""

# ─────────────────────────────────────────────
# SCORING KEYWORDS
# ─────────────────────────────────────────────

HIGH_WEIGHT_TERMS = [
    "sql", "datenanalyse", "data analysis", "analytics", "business intelligence", "bi",
    "looker", "product analytics", "kundeninsights", "customer insights", "kpi",
    "dashboard", "reporting", "e-commerce", "ecommerce", "digital", "retouren",
    "merchandising", "digitalisierung", "daten", "data",
]

MEDIUM_WEIGHT_TERMS = [
    "python", "machine learning", "ml", "prozessverbesserung", "automatisierung",
    "stakeholder", "product owner", "product manager", "produktmanager",
    "anforderungen", "requirements", "projektmanagement",
]

# ─────────────────────────────────────────────
# IGNORE TERMS (title-level filter)
# Add company-specific extras in the notebook's Section 2.
# ─────────────────────────────────────────────

IGNORE_TERMS = [
    "fahrdienstleiter", "lokführer", "triebfahrzeugführer", "baggerfahrer",
    "schweißer", "elektriker", "monteur", "gleisbau", "tiefbau", "hochbau",
    "mechaniker", "stapler", "schaffner", "zugbegleiter", "sicherheitsbeamter",
    "bauüberwacher", "oberbau", "oberleitung", "gleise", "weichen", "signaltechnik",
    "ausbildung", "duales studium", "praktikum", "werkstudent",
    "kraftfahrer", "busfahrer",
]

# ─────────────────────────────────────────────
# LOCATION FILTER
# Case-insensitive substring match against the job's location field.
# ─────────────────────────────────────────────

ALLOWED_LOCATIONS = [
    "berlin",
    "wien",
    "vienna",
    "remote",
    "wo du willst",
    "home office",
    "homeoffice",
]

# ─────────────────────────────────────────────
# SCORING THRESHOLDS
# ─────────────────────────────────────────────

MIN_SCORE = 15
KEYWORD_BONUS_CAP = 30