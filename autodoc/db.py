
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Tuple

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    category TEXT,
    sender TEXT,
    subject TEXT,
    received_at TEXT,
    saved_at TEXT DEFAULT (datetime('now')),
    size_bytes INTEGER,
    hash_sha256 TEXT
);
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_sender ON documents(sender);
CREATE INDEX IF NOT EXISTS idx_documents_received ON documents(received_at);
"""

def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()

def insert_document(conn: sqlite3.Connection, rec: Dict[str, Any]) -> int:
    keys = ",".join(rec.keys())
    placeholders = ",".join([":" + k for k in rec.keys()])
    cur = conn.execute(f"INSERT INTO documents ({keys}) VALUES ({placeholders})", rec)
    conn.commit()
    return cur.lastrowid

def query_documents(conn: sqlite3.Connection, where: str = "", params: Tuple = ()) -> List[Tuple]:
    sql = "SELECT id, filename, filepath, category, sender, subject, received_at, saved_at, size_bytes FROM documents"
    if where:
        sql += " WHERE " + where
    sql += " ORDER BY received_at DESC, saved_at DESC;"
    cur = conn.execute(sql, params)
    return cur.fetchall()
