from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from .query_parser import parse
from fastapi.middleware.cors import CORSMiddleware
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "indexer", "search.db")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _load_env():
    """Loads .env file manually."""
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except Exception:
                pass

_load_env()

class SearchResponseItem(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    status: Optional[str]
    prioridade: Optional[str]
    categoria: Optional[str]
    entidade: Optional[str]
    tecnico: Optional[str]
    grupo: Optional[str]
    requerente: Optional[str]
    data_criacao: Optional[str]
    data_modificacao: Optional[str]
    url: Optional[str]
    highlight: Optional[str]
    score: float

@app.get("/health")
def health():
    ok = os.path.exists(DB_PATH)
    return {"ok": ok}

@app.get("/stats")
def stats():
    conn = get_conn()
    cur = conn.cursor()
    try:
        s_rows = cur.execute("SELECT status, COUNT(*) AS c FROM tickets_index GROUP BY status ORDER BY COUNT(*) DESC").fetchall()
        e_rows = cur.execute("SELECT entidade, COUNT(*) AS c FROM tickets_index GROUP BY entidade ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
        status = [[r["status"], r["c"]] for r in s_rows if r["status"]]
        entidade = [[r["entidade"], r["c"]] for r in e_rows if r["entidade"]]
        return {"status": status, "entidade": entidade}
    except Exception:
        return {"status": [], "entidade": []}
    finally:
        conn.close()

@app.get("/search", response_model=List[SearchResponseItem])
def search(q: str = Query(""), status: Optional[str] = None, prioridade: Optional[str] = None, categoria: Optional[str] = None, entidade: Optional[str] = None, tecnico: Optional[str] = None, grupo: Optional[str] = None, dt_ini: Optional[str] = None, dt_fim: Optional[str] = None, page: int = 1, size: int = 50, sort: Optional[str] = None):
    conn = get_conn()
    conn.create_function("lower", 1, lambda s: s.lower() if isinstance(s, str) else s)
    cur = conn.cursor()
    
    match_sql, params, where_sql, _ = parse(q, {"status":status,"prioridade":prioridade,"categoria":categoria,"entidade":entidade,"tecnico":tecnico,"grupo":grupo,"dt_ini":dt_ini,"dt_fim":dt_fim,"include_deleted": False})
    
    # Select URL
    if match_sql:
        base_sql = "SELECT id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, url, snippet(tickets_index, '<mark>', '</mark>', '...', 5, 10) AS highlight, bm25(tickets_index) AS score FROM tickets_index"
    else:
        base_sql = "SELECT id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, url, '' AS highlight, 0.0 AS score FROM tickets_index"
        
    clauses = []
    if match_sql:
        clauses.append("tickets_index MATCH ?")
        params = [match_sql] + params
    if where_sql:
        clauses.append(where_sql)
        
    sql = base_sql
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    
    # Ensure deleted are excluded (though they shouldn't be in index if build process is correct, but good safety)
    sql += (" WHERE " if not clauses else " AND ") + " is_deleted = 0"
    
    order = "score" if match_sql else "data_modificacao DESC"
    if sort == "recent":
        order = "data_modificacao DESC"
        
    sql += f" ORDER BY {order} LIMIT ? OFFSET ?"
    params += [size, max(0, (page - 1) * size)]
    
    try:
        rows = cur.execute(sql, params).fetchall()
        result = []
        for r in rows:
            result.append(SearchResponseItem(
                id=r["id"], 
                titulo=(r["titulo"] or ""), 
                descricao=r["descricao"], 
                status=r["status"], 
                prioridade=r["prioridade"], 
                categoria=r["categoria"], 
                entidade=r["entidade"], 
                tecnico=r["tecnico"], 
                grupo=r["grupo"], 
                requerente=r["requerente"], 
                data_criacao=r["data_criacao"], 
                data_modificacao=r["data_modificacao"], 
                url=r["url"],
                highlight=r["highlight"], 
                score=float(r["score"]) if r["score"] is not None else 0.0
            ))
        return result
    finally:
        conn.close()

@app.get("/suggest")
def suggest(field: str, prefix: str = "", limit: int = 10):
    conn = get_conn()
    cur = conn.cursor()
    field = field if field in {"status", "prioridade", "categoria", "entidade", "tecnico", "grupo", "requerente"} else "categoria"
    sql = f"SELECT DISTINCT {field} FROM tickets_index WHERE {field} LIKE ? ORDER BY {field} LIMIT ?"
    rows = cur.execute(sql, [prefix + "%", limit]).fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

@app.post("/index/rebuild")
def index_rebuild():
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indexer', 'build_index.py')
    ok = os.system(f"python {script_path}") == 0
    return {"rebuild": ok}

@app.get("/export")
def export(q: str = "", status: Optional[str] = None, prioridade: Optional[str] = None, categoria: Optional[str] = None, entidade: Optional[str] = None, tecnico: Optional[str] = None, grupo: Optional[str] = None, dt_ini: Optional[str] = None, dt_fim: Optional[str] = None, limit: int = 1000, format: str = "xlsx"):
    import pandas as pd, io
    conn = get_conn()
    cur = conn.cursor()
    
    # Re-use parse logic or simple build
    # For export, we usually want the exact same filter as search
    match_sql, params, where_sql, _ = parse(q, {"status":status,"prioridade":prioridade,"categoria":categoria,"entidade":entidade,"tecnico":tecnico,"grupo":grupo,"dt_ini":dt_ini,"dt_fim":dt_fim,"include_deleted": False})
    
    clauses = []
    if match_sql:
        clauses.append("tickets_index MATCH ?")
        params = [match_sql] + params
    if where_sql:
        clauses.append(where_sql)
    clauses.append("is_deleted = 0")
    
    sql = "SELECT id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, url FROM tickets_index"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " LIMIT ?"
    params += [limit]
    
    rows = cur.execute(sql, params).fetchall()
    conn.close()
    
    cols = ["ID","TITULO","DESCRICAO","STATUS","PRIORIDADE","CATEGORIA","ENTIDADE","TECNICO","GRUPO","REQUERENTE","DATA_CRIACAO","DATA_MODIFICACAO", "URL"]
    df = pd.DataFrame(rows, columns=cols)
    
    if format == "csv":
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        from fastapi.responses import StreamingResponse
        return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=busca_glpi.csv"})
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition":"attachment; filename=busca_glpi.xlsx"})