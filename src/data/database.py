# penser à run 'npm install better-sqlite3' à la racine

import sqlite3
from pathlib import Path
import csv

# Chemin du dossier data
DATA_DIR = Path(__file__).resolve().parent

# Fichier de la base de données
DB_PATH = DATA_DIR / "pfe.db"


def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def create_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id TEXT NOT NULL UNIQUE,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                service TEXT NOT NULL,
                poste TEXT NOT NULL,
                manager_object_id TEXT,
                actif INTEGER NOT NULL DEFAULT 1
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                scenario_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'draft'
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS campaign_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                tracking_token TEXT NOT NULL UNIQUE,
                email_status TEXT NOT NULL DEFAULT 'pending',
                sent_at TEXT,

                FOREIGN KEY (campaign_id)
                    REFERENCES campaigns(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (employee_id)
                    REFERENCES employees(id),

                UNIQUE (campaign_id, employee_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tracking_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_count INTEGER NOT NULL DEFAULT 0,
                first_event_at TEXT,
                last_event_at TEXT,

                FOREIGN KEY (recipient_id)
                    REFERENCES campaign_recipients(id)
                    ON DELETE CASCADE,

                UNIQUE (recipient_id, event_type)
            )
        """)


if __name__ == "__main__":

    create_database()
