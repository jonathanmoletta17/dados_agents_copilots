import os
import csv
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "glpi.sqlite")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "dados", "tickets_completos", "todos_tickets_atual.csv")
CSV_BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "dados", "tickets_completos", "todos_tickets_base_atual.csv")

def main():
    path = CSV_BASE_PATH if os.path.exists(CSV_BASE_PATH) else CSV_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)
        cur.execute("DELETE FROM tickets_flat")
        cols = [
            "ID","Título","Descrição","Status","Categoria","Entidade",
            "Requerente","Técnico","Grupo","Data Criação","Data Modificação"
        ]
        placeholders = ",".join(["?" for _ in cols])
        sql = "INSERT OR REPLACE INTO tickets_flat("+",".join(["\""+c+"\"" for c in cols])+") VALUES("+placeholders+")"
        for r in rows:
            for c in cols:
                if c not in r:
                    r[c] = ""
            cur.execute(sql, [r[c] for c in cols])
        conn.commit()
        print("[OK] Inseridos", len(rows), "registros em tickets_flat")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
