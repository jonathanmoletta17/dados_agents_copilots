import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "glpi.sqlite")

def ensure_dirs(path):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)

def create_tables(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            name TEXT,
            content TEXT,
            status INTEGER,
            priority INTEGER,
            urgency INTEGER,
            impact INTEGER,
            itilcategories_id TEXT,
            entities_id TEXT,
            date TEXT,
            date_mod TEXT,
            solvedate TEXT,
            closedate TEXT,
            solve_delay_stat INTEGER,
            close_delay_stat INTEGER,
            satisfaction TEXT,
            type INTEGER,
            locations_id INTEGER,
            global_validation INTEGER,
            inserted_at TEXT,
            updated_at TEXT,
            source_fetched_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            firstname TEXT,
            realname TEXT,
            full_name TEXT,
            inserted_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            id TEXT PRIMARY KEY,
            name TEXT,
            inserted_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            name TEXT,
            inserted_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS itilcategories (
            id TEXT PRIMARY KEY,
            name TEXT,
            inserted_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ticket_users (
            tickets_id TEXT,
            users_id TEXT,
            type INTEGER,
            PRIMARY KEY (tickets_id, users_id, type)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS group_tickets (
            tickets_id TEXT,
            groups_id TEXT,
            type INTEGER,
            PRIMARY KEY (tickets_id, groups_id, type)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets_flat (
            ID TEXT PRIMARY KEY,
            "Título" TEXT,
            "Descrição" TEXT,
            "Status" TEXT,
            "Categoria" TEXT,
            "Entidade" TEXT,
            "Requerente" TEXT,
            "Técnico" TEXT,
            "Grupo" TEXT,
            "Data Criação" TEXT,
            "Data Modificação" TEXT
        )
        """
    )
    conn.commit()

def main():
    ensure_dirs(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        create_tables(conn)
        print("[OK] Esquema criado em", DB_PATH)
    finally:
        conn.close()

if __name__ == "__main__":
    main()