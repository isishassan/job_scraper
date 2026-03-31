import sqlite3
conn = sqlite3.connect("data/jobs.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT,
        source TEXT,
        source_job_id TEXT,
        company TEXT,
        title TEXT,
        location TEXT,
        start_date TEXT,
        link TEXT,
        score REAL,
        description TEXT,
        UNIQUE(source, source_job_id)
    )
""")
conn.commit()
conn.close()
print("DB created.")