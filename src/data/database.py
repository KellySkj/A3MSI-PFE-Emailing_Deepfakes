# penser à run 'npm install better-sqlite3' à la racine

import sqlite3
from pathlib import Path
import csv

# Chemin du dossier data
DATA_DIR = Path(__file__).resolve().parent

# Fichier de la base de données
DB_PATH = DATA_DIR / "pfe.db"


def create_database():
    with sqlite3.connect(DB_PATH) as conn:
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


def import_employees():
    with sqlite3.connect(DB_PATH) as conn:
        with open(DATA_DIR / "fake_ad_export.csv", "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                conn.execute("""
                    INSERT INTO employees (
                        object_id, prenom, nom, email,
                        service, poste, manager_object_id, actif
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(object_id) DO NOTHING
                """, (
                    row["object_id"],
                    row["prenom"],
                    row["nom"],
                    row["email"],
                    row["service"],
                    row["poste"],
                    row["manager_object_id"] or None,
                    1 if row["actif"].lower() == "true" else 0
                ))


def count_employees():
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute("SELECT COUNT(*) FROM employees")
        return result.fetchone()[0]


def get_employee_groups():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        groups = conn.execute("""
            SELECT service, COUNT(*) AS employee_count
            FROM employees
            WHERE actif = 1
            GROUP BY service
            ORDER BY service
        """).fetchall()

        return [dict(group) for group in groups]


def get_employees_by_service():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        employees = conn.execute("""
            SELECT object_id, prenom, email, service, poste
            FROM employees
            WHERE actif = 1
            ORDER BY service, nom
        """).fetchall()

        groups = {}

        for employee in employees:
            service = employee["service"]

            if service not in groups:
                groups[service] = []

            groups[service].append(dict(employee))

        return groups


def get_service_contexts():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        employees = conn.execute("""
            SELECT service, poste
            FROM employees
            WHERE actif = 1
            ORDER BY service, poste
        """).fetchall()

        contexts = {}

        for employee in employees:
            service = employee["service"]
            poste = employee["poste"]

            if service not in contexts:
                contexts[service] = {
                    "service": service,
                    "nombre_employes": 0,
                    "postes": set()
                }

            contexts[service]["nombre_employes"] += 1
            contexts[service]["postes"].add(poste)

        # Conversion des ensembles en listes
        for context in contexts.values():
            context["postes"] = sorted(context["postes"])

        return contexts


if __name__ == "__main__":
    create_database()
    import_employees()
    print(f"Base de données créée : {DB_PATH}")
    print(f"Nombre d'employés : {count_employees()}")
    for group in get_employee_groups():
            print(group)

    groups = get_employees_by_service()
    for service, employees in groups.items():
        print(f"\n{service} : {len(employees)} employés")
        for employee in employees:
            print(f" - {employee['prenom']} ({employee['poste']})")

    print("\n--- CONTEXTES POUR GEMINI ---")
    contexts = get_service_contexts()
    for service, context in contexts.items():
        print(context)