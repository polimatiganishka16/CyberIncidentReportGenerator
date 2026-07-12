"""
database.py
------------
Handles all SQLite database operations for the app:
- creating the table
- inserting a new incident + generated report
- fetching report history
- fetching a single report by id
- deleting a report

We use Python's built-in `sqlite3` module, so no extra install is needed.
"""

import sqlite3
from datetime import datetime
import config


def get_connection():
    """Open a new connection to the SQLite database file."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, like a dict
    return conn


def init_db():
    """
    Create the 'reports' table if it does not already exist.
    Called once when the Flask app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            date TEXT,
            time TEXT,
            attack_type TEXT,
            severity TEXT,
            source_ip TEXT,
            destination_system TEXT,
            affected_user TEXT,
            malware TEXT,
            detection_tool TEXT,
            status TEXT,
            action_taken TEXT,
            report_text TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_report(incident_data: dict, report_text: str) -> int:
    """
    Save a new incident + its generated report into the database.
    Returns the new row's id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reports (
            incident_id, date, time, attack_type, severity, source_ip,
            destination_system, affected_user, malware, detection_tool,
            status, action_taken, report_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_data.get("incident_id"),
        incident_data.get("date"),
        incident_data.get("time"),
        incident_data.get("attack_type"),
        incident_data.get("severity"),
        incident_data.get("source_ip"),
        incident_data.get("destination_system"),
        incident_data.get("affected_user"),
        incident_data.get("malware"),
        incident_data.get("detection_tool"),
        incident_data.get("status"),
        incident_data.get("action_taken"),
        report_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_reports():
    """Return every saved report, most recent first, for the History page."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_report_by_id(report_id: int):
    """Return a single report row, or None if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_report(report_id: int):
    """Delete a report by its id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
