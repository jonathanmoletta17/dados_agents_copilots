import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Hardcoded config for debugging
DATABASE_URL = "postgresql://glpi_user:glpi_secure_2024@postgres:5432/glpi_data"

def check_data():
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("Connected to DB.")

        # 1. Check for duplicate links in carregador_tickets
        print("--- Checking for duplicate links in carregador_tickets ---")
        query_dupes = text("""
            SELECT tickets_id, items_id, COUNT(*)
            FROM sis.carregador_tickets
            GROUP BY tickets_id, items_id
            HAVING COUNT(*) > 1
        """)
        dupes = session.execute(query_dupes).fetchall()
        if dupes:
            print(f"FOUND {len(dupes)} DUPLICATE LINKS:")
            for d in dupes:
                print(f"Ticket {d[0]} - Item {d[1]}: {d[2]} times")
        else:
            print("No duplicate links found.")

        # 2. Check for duplicate chargers
        print("\n--- Checking for duplicate chargers ---")
        query_charger_dupes = text("""
            SELECT id, COUNT(*)
            FROM sis.carregadores
            GROUP BY id
            HAVING COUNT(*) > 1
        """)
        c_dupes = session.execute(query_charger_dupes).fetchall()
        if c_dupes:
            print(f"FOUND {len(c_dupes)} DUPLICATE CHARGERS:")
            for d in c_dupes:
                print(f"ID {d[0]}: {d[1]} times")
        else:
            print("No duplicate chargers found.")

        # 3. Check if linked tickets exist in tickets table
        print("\n--- Checking if linked tickets exist in tickets table ---")
        query_missing = text("""
            SELECT ct.tickets_id
            FROM sis.carregador_tickets ct
            LEFT JOIN sis.tickets t ON t.glpi_id = ct.tickets_id
            WHERE t.id IS NULL
        """)
        missing = session.execute(query_missing).fetchall()
        if missing:
            print(f"FOUND {len(missing)} LINKED TICKETS MISSING IN TICKETS TABLE:")
            print([m[0] for m in missing[:10]], "..." if len(missing) > 10 else "")
        else:
            print("All linked tickets exist in tickets table.")

        # 4. Check total counts
        print("\n--- Total Counts ---")
        n_chargers = session.execute(text("SELECT COUNT(*) FROM sis.carregadores")).scalar()
        n_links = session.execute(text("SELECT COUNT(*) FROM sis.carregador_tickets")).scalar()
        n_tickets = session.execute(text("SELECT COUNT(*) FROM sis.tickets")).scalar()
        print(f"Carregadores: {n_chargers}")
        print(f"Links: {n_links}")
        print(f"Tickets: {n_tickets}")
        
    except Exception as e:
        print(f"Error: {str(e)[:500]}")

if __name__ == "__main__":
    check_data()
