import os
import sqlite3
import pandas as pd
from unicodedata import normalize
import sys
sys.path.append(os.path.dirname(__file__))
from glpi_api import init_session, kill_session, search_tickets_all, get_deleted_ids

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INDEX_DB = os.path.join(BASE_DIR, "indexer", "search.db")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def norm_text(s):
    if s is None:
        return ""
    s = str(s)
    s = normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.strip().lower()
    return s

def to_iso_datetime(s):
    if s is None or s == "":
        return ""
    try:
        dt = pd.to_datetime(str(s), dayfirst=True, errors='coerce')
        if pd.isna(dt):
            return ""
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return ""

def ensure_schema(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.execute("DROP TABLE IF EXISTS tickets_index")
    cur.execute("CREATE VIRTUAL TABLE tickets_index USING fts5(id UNINDEXED, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, is_deleted UNINDEXED)")
    cur.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()

def load_env_file():
    paths = [os.path.join(ROOT_DIR, ".env"), os.path.join(BASE_DIR, ".env")]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            os.environ.setdefault(k, v)
            except Exception:
                pass


def load_from_glpi():
    try:
        st = init_session()
        if not st:
            return []
        del_ids = get_deleted_ids(st)
        items = search_tickets_all(st, include_deleted=False)
        kill_session(st)
        rows = []
        for it in items:
            if int(it.get('ID') or it.get('id') or 0) in del_ids:
                # garante que IDs presentes na lixeira não entrem no índice
                continue
            del_flag = int(it.get('IS_DELETED') or 0)
        rows.append({
                'ID': it.get('ID') or it.get('id') or 0,
                'TITULO': it.get('TITULO') or it.get('name') or '',
                'DESCRICAO': it.get('DESCRICAO') or it.get('content') or '',
                'STATUS': str(it.get('STATUS') or it.get('status') or ''),
                'CATEGORIA': it.get('CATEGORIA') or it.get('itilcategories_id') or '',
                'ENTIDADE': it.get('ENTIDADE') or it.get('entities_id') or '',
                'REQUERENTE': it.get('REQUERENTE') or it.get('users_id_recipient') or '',
                'TECNICO': it.get('TECNICO') or it.get('users_id_assign') or '',
                'GRUPO': it.get('GRUPO') or it.get('groups_id_assign') or '',
                'DATA_CRIACAO': it.get('DATA_CRIACAO') or it.get('date') or '',
                'DATA_MODIFICACAO': it.get('DATA_MODIFICACAO') or it.get('date_mod') or '',
                'IS_DELETED': del_flag
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame([])

def build():
    if not os.path.exists(os.path.dirname(INDEX_DB)):
        os.makedirs(os.path.dirname(INDEX_DB), exist_ok=True)
    conn = sqlite3.connect(INDEX_DB)
    ensure_schema(conn)
    load_env_file()
    df = load_from_glpi()
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame([])
    rows = []
    for _, r in df.iterrows():
        rows.append((
            int(r['ID']) if str(r['ID']).isdigit() else 0,
            norm_text(r['TITULO']),
            norm_text(r['DESCRICAO']),
            norm_text(r['STATUS']),
            "",
            norm_text(r['CATEGORIA']),
            norm_text(r['ENTIDADE']),
            norm_text(r['TECNICO']),
            norm_text(r['GRUPO']),
            norm_text(r['REQUERENTE']),
            to_iso_datetime(r['DATA_CRIACAO']),
            to_iso_datetime(r['DATA_MODIFICACAO']),
            int(r['IS_DELETED']) if str(r['IS_DELETED']).strip() != '' else 0
        ))
    if rows:
        conn.executemany("INSERT INTO tickets_index(id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, is_deleted) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    try:
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_sync', strftime('%Y-%m-%d %H:%M:%S','now'))")
    except Exception:
        pass
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build()