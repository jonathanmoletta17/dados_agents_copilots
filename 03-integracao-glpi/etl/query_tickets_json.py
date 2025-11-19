import os
import uuid
import json
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "glpi.sqlite")

def parse_br_date(s):
    if not s:
        return None
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None

def query(periodo=None, page=1, page_size=1000):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tickets_flat")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT ID, \"Título\", \"Descrição\", \"Status\", \"Categoria\", \"Entidade\", \"Requerente\", \"Técnico\", \"Grupo\", \"Data Criação\", \"Data Modificação\" FROM tickets_flat"
        )
        rows = cur.fetchall()
        items = []
        for r in rows:
            it = {
                "ID": r[0],
                "Título": r[1] or "",
                "Descrição": r[2] or "",
                "Status": r[3] or "",
                "Categoria": r[4] or "",
                "Entidade": r[5] or "",
                "Requerente": r[6] or "",
                "Técnico": r[7] or "",
                "Grupo": r[8] or "",
                "Data Criação": r[9] or "",
                "Data Modificação": r[10] or "",
            }
            items.append(it)
        if periodo == "6m":
            now = datetime.now()
            start = now - timedelta(days=180)
            items = [it for it in items if (lambda d: d is None or (start <= d <= now))(parse_br_date(it.get("Data Criação", "")))]
        start_idx = max((page - 1) * page_size, 0)
        end_idx = start_idx + page_size
        page_items = items[start_idx:end_idx]
        payload = {
            "status": "ok",
            "data": {
                "meta": {
                    "total": len(items),
                    "pagina": page,
                    "tamanho_pagina": page_size,
                    "filtro_periodo": periodo or ""
                },
                "dados": page_items
            },
            "request_id": str(uuid.uuid4())
        }
        print(json.dumps(payload, ensure_ascii=True))
    finally:
        conn.close()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--periodo", default=None)
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--page_size", type=int, default=1000)
    args = ap.parse_args()
    query(periodo=args.periodo, page=args.page, page_size=args.page_size)

if __name__ == "__main__":
    main()