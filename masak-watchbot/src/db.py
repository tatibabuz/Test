from sqlalchemy import create_engine, text
import os

ENGINE = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS source_documents(
  id SERIAL PRIMARY KEY,
  url TEXT, fetched_at TIMESTAMP DEFAULT NOW(),
  sha256 CHAR(64), filetype TEXT, local_name TEXT
);
CREATE TABLE IF NOT EXISTS raw_entities(
  id SERIAL PRIMARY KEY,
  source_id INT REFERENCES source_documents(id),
  full_name TEXT, tckn TEXT, vkn TEXT, passport_no TEXT,
  birth_date DATE, nationality TEXT, payload_json JSONB
);
CREATE TABLE IF NOT EXISTS watchlist_items(
  id SERIAL PRIMARY KEY,
  raw_entity_id INT REFERENCES raw_entities(id),
  status TEXT, first_seen TIMESTAMP, last_seen TIMESTAMP,
  fingerprint TEXT
);
CREATE TABLE IF NOT EXISTS matches(
  id SERIAL PRIMARY KEY,
  customer_id TEXT, item_id INT REFERENCES watchlist_items(id),
  method TEXT, score INT, matched_fields_json JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
"""

def ensure_schema():
    with ENGINE.begin() as con:
        for stmt in SCHEMA_SQL.strip().split(";"):
            s = stmt.strip()
            if s:
                con.execute(text(s))
