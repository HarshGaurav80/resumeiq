"""
SQLite persistence for analysis history (uses Python's built-in sqlite3 – no ORM needed).
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL,
    file_name       TEXT    NOT NULL,
    job_role        TEXT    NOT NULL DEFAULT '',
    job_description TEXT    NOT NULL,
    match_score     INTEGER NOT NULL,
    ats_score       INTEGER NOT NULL,
    method          TEXT    NOT NULL,      -- 'gemini', 'openai' or 'offline'
    result_json     TEXT    NOT NULL       -- full AnalysisResult as JSON
);
"""


@contextmanager
def get_conn():
    settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def save_analysis(file_name: str, job_role: str, job_description: str, result: dict, method: str) -> dict:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO analyses (created_at, file_name, job_role, job_description, match_score, "
            "ats_score, method, result_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (created_at, file_name, job_role, job_description, result["match_score"],
             result["ats_score"], method, json.dumps(result)),
        )
        new_id = cur.lastrowid
    return get_analysis(new_id)


def _row_to_dict(row: sqlite3.Row, full: bool) -> dict:
    data = {
        "id": row["id"],
        "created_at": row["created_at"],
        "file_name": row["file_name"],
        "job_role": row["job_role"],
        "match_score": row["match_score"],
        "ats_score": row["ats_score"],
        "method": row["method"],
    }
    if full:
        data["job_description"] = row["job_description"]
        data["result"] = json.loads(row["result_json"])
    return data


def list_analyses(limit: int = 200) -> List[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [_row_to_dict(r, full=False) for r in rows]


def get_analysis(analysis_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    return _row_to_dict(row, full=True) if row else None


def delete_analysis(analysis_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    return cur.rowcount > 0
