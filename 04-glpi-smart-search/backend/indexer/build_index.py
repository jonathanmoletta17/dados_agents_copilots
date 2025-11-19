import os
import sqlite3
import sys
from datetime import datetime

# Add current directory to path to find modules
sys.path.append(os.path.dirname(__file__))

from glpi_api import fetch_all_for_indexer
from text_processor import TextProcessor

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INDEX_DB = os.path.join(BASE_DIR, "indexer", "search.db")

def norm_text(s):
    """Normalizes text for search indexing (lowercase, no accents)."""
    if s is None:
        return ""
    return TextProcessor.clean_text(str(s)).lower()

def ensure_schema(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    # We store:
    # - id: Ticket ID
    # - titulo: Title (Display)
    # - descricao: Description (Markdown Display)
    # - ... other fields ...
    # - titulo_search: Normalized title for search
    # - descricao_search: Normalized description for search
    # FTS5 table will index the _search columns or we can just index the raw ones and let FTS5 handle it.
    # For simplicity and power, let's use FTS5 on the content directly but we might want a separate 'display' table if we want to be perfect.
    # However, to keep it simple and compatible with the existing query logic (which likely queries this table), 
    # we will stick to the existing schema but ensure the content is clean.
    
    # Existing schema was:
    # CREATE VIRTUAL TABLE tickets_index USING fts5(id UNINDEXED, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, is_deleted UNINDEXED)
    
    cur.execute("DROP TABLE IF EXISTS tickets_index")
    cur.execute("""
        CREATE VIRTUAL TABLE tickets_index USING fts5(
            id UNINDEXED, 
            titulo, 
            descricao, 
            status, 
            prioridade, 
            categoria, 
            entidade, 
            tecnico, 
            grupo, 
            requerente, 
            data_criacao, 
            data_modificacao, 
            url UNINDEXED,
            is_deleted UNINDEXED
        )
    """)
    cur.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()

def build():
    print("🚀 Starting Index Build...")
    
    if not os.path.exists(os.path.dirname(INDEX_DB)):
        os.makedirs(os.path.dirname(INDEX_DB), exist_ok=True)
        
    conn = sqlite3.connect(INDEX_DB)
    ensure_schema(conn)
    
    # Fetch data
    tickets = fetch_all_for_indexer()
    print(f"📥 Fetched {len(tickets)} tickets.")
    
    if not tickets:
        print("⚠️ No tickets found. Aborting.")
        return

    rows = []
    for t in tickets:
        # We will store the Markdown description in 'descricao'.
        # FTS5 will index it. Searching for words inside markdown works fine.
        
        rows.append((
            t['ID'],
            t['TITULO'],
            t['DESCRICAO'], # Markdown
            t['STATUS'],
            "", # Prioridade (not fetched yet, can be added later)
            t['CATEGORIA'],
            t['ENTIDADE'],
            t['TECNICO'],
            t['GRUPO'],
            t['REQUERENTE'],
            t['DATA_CRIACAO'],
            t['DATA_MODIFICACAO'],
            t['URL'],
            t['IS_DELETED']
        ))
        
    if rows:
        print(f"💾 Inserting {len(rows)} rows into database...")
        conn.executemany("""
            INSERT INTO tickets_index(
                id, titulo, descricao, status, prioridade, categoria, 
                entidade, tecnico, grupo, requerente, data_criacao, 
                data_modificacao, url, is_deleted
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, rows)
        
    # Update metadata
    conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_sync', ?)", 
                 (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    
    conn.commit()
    conn.close()
    print("✅ Index build complete.")

if __name__ == "__main__":
    build()