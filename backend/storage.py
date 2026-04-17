import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "research.db"

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id  TEXT PRIMARY KEY,
                saved_at  TEXT,
                duration  REAL,
                entries   TEXT  -- JSON array
            )
        """)

def save_match(match_id: str, duration: float, research_entries: list[dict]):
    print(f"SAVING MATCH: {match_id}")
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO matches VALUES (?, ?, ?, ?)",
            (match_id, datetime.now(timezone.utc).isoformat(), duration, json.dumps(research_entries))
        )

def get_all_matches(limit=100, offset=0):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM matches ORDER BY saved_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    return [{"match_id": r["match_id"], "saved_at": r["saved_at"], "duration": r["duration"], "entries": json.loads(r["entries"])} for r in rows]

def get_match(match_id: str) -> Optional[dict]:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    if not row:
        return None
    return {"match_id": row["match_id"], "saved_at": row["saved_at"], "duration": row["duration"], "entries": json.loads(row["entries"])}