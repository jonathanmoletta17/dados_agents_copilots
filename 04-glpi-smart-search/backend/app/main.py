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
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    explicit = r"C:\\Users\\jonathan-moletta\\OneDrive - Governo do Estado do Rio Grande do Sul\\Área de Trabalho\\BD_cau_sis\\bd_cau\\.env"
    for p in [os.path.join(root, ".env"), os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), explicit]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except Exception:
                pass
_load_env()
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from indexer.glpi_api import init_session, kill_session, search_tickets, search_tickets_by_text
USE_GLPI_LIVE = (os.environ.get("USE_GLPI_LIVE", "").lower() in {"1","true","t","yes","y"}) or bool(os.environ.get("GLPI_URL"))

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
    highlight: Optional[str]
    score: float

@app.get("/health")
def health():
    ok = os.path.exists(DB_PATH)
    return {"ok": ok}

@app.get("/debug/count")
def debug_count():
    conn = get_conn()
    cur = conn.cursor()
    c = cur.execute("SELECT COUNT(*) FROM tickets_index").fetchone()[0]
    conn.close()
    return {"count": c}

@app.get("/debug/one")
def debug_one():
    conn = get_conn()
    cur = conn.cursor()
    r = cur.execute("SELECT id, titulo, entidade FROM tickets_index LIMIT 1").fetchone()
    conn.close()
    return {"row": r}

@app.get("/debug/is_deleted")
def debug_is_deleted(id: int):
    conn = get_conn()
    cur = conn.cursor()
    r = cur.execute("SELECT id, status, is_deleted FROM tickets_index WHERE id = ?", [id]).fetchone()
    conn.close()
    return {"id": r[0] if r else None, "status": r[1] if r else None, "is_deleted": r[2] if r else None}

@app.get("/debug/sample_deleted")
def debug_sample_deleted(limit: int = 10):
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("SELECT id, titulo, status FROM tickets_index WHERE is_deleted = 1 ORDER BY data_modificacao DESC LIMIT ?", [limit]).fetchall()
    conn.close()
    return [{"id": r[0], "titulo": r[1], "status": r[2]} for r in rows]

@app.get("/debug/glpi_is_deleted")
def debug_glpi_is_deleted(id: int):
    import os, json, urllib.request
    url = (os.environ.get("GLPI_URL",""))
    app = os.environ.get("GLPI_APP_TOKEN","")
    user = os.environ.get("GLPI_USER_TOKEN","")
    if not url:
        return {"glpi": None}
    h = {"Content-Type":"application/json"}
    if app:
        h["App-Token"] = app
    if user:
        h["Authorization"] = f"user_token {user}"
    req = urllib.request.Request(url.rstrip("/")+f"/Ticket/{id}", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"is_deleted": data.get("is_deleted"), "status": data.get("status")}
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/stats")
def debug_stats():
    conn = get_conn()
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM tickets_index").fetchone()[0]
    non_empty_title = cur.execute("SELECT COUNT(*) FROM tickets_index WHERE titulo != ''").fetchone()[0]
    non_empty_desc = cur.execute("SELECT COUNT(*) FROM tickets_index WHERE descricao != ''").fetchone()[0]
    non_empty_ent = cur.execute("SELECT COUNT(*) FROM tickets_index WHERE entidade != ''").fetchone()[0]
    conn.close()
    return {"total": total, "titulo_non_empty": non_empty_title, "descricao_non_empty": non_empty_desc, "entidade_non_empty": non_empty_ent}

@app.get("/stats")
def stats():
    conn = get_conn()
    cur = conn.cursor()
    s_rows = cur.execute("SELECT status, COUNT(*) AS c FROM tickets_index GROUP BY status ORDER BY COUNT(*) DESC").fetchall()
    e_rows = cur.execute("SELECT entidade, COUNT(*) AS c FROM tickets_index GROUP BY entidade ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    conn.close()
    status = [[r["status"], r["c"]] for r in s_rows if r["status"]]
    entidade = [[r["entidade"], r["c"]] for r in e_rows if r["entidade"]]
    return {"status": status, "entidade": entidade}

@app.get("/search", response_model=List[SearchResponseItem])
def search(q: str = Query(""), status: Optional[str] = None, prioridade: Optional[str] = None, categoria: Optional[str] = None, entidade: Optional[str] = None, tecnico: Optional[str] = None, grupo: Optional[str] = None, dt_ini: Optional[str] = None, dt_fim: Optional[str] = None, page: int = 1, size: int = 50, sort: Optional[str] = None):
    _load_env()
    if USE_GLPI_LIVE:
        st = init_session()
        try:
            start = max(0, (page - 1) * size)
            items = search_tickets_by_text(st, q, range_start=start, range_len=size) if q.strip() else search_tickets(st, include_deleted=False, range_start=start, range_len=size)
            if sort == "recent":
                try:
                    items = sorted(items, key=lambda x: str(x.get('DATA_MODIFICACAO') or ''), reverse=True)
                except Exception:
                    pass
            res = []
            for it in items:
                res.append(SearchResponseItem(
                    id=int(it.get('ID') or 0),
                    titulo=str(it.get('TITULO') or ""),
                    descricao=it.get('DESCRICAO'),
                    status=str(it.get('STATUS') or ""),
                    prioridade="",
                    categoria=str(it.get('CATEGORIA') or ""),
                    entidade=str(it.get('ENTIDADE') or ""),
                    tecnico=str(it.get('TECNICO') or ""),
                    grupo=str(it.get('GRUPO') or ""),
                    requerente=str(it.get('REQUERENTE') or ""),
                    data_criacao=str(it.get('DATA_CRIACAO') or ""),
                    data_modificacao=str(it.get('DATA_MODIFICACAO') or ""),
                    highlight="",
                    score=0.0
                ))
            return res
        finally:
            if st:
                kill_session(st)
    conn = get_conn()
    conn.create_function("lower", 1, lambda s: s.lower() if isinstance(s, str) else s)
    cur = conn.cursor()
    match_sql, params, where_sql, _ = parse(q, {"status":status,"prioridade":prioridade,"categoria":categoria,"entidade":entidade,"tecnico":tecnico,"grupo":grupo,"dt_ini":dt_ini,"dt_fim":dt_fim,"include_deleted": False})
    if match_sql:
        base_sql = "SELECT id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, snippet(tickets_index, '<mark>', '</mark>', '...', 5, 10) AS highlight, bm25(tickets_index) AS score FROM tickets_index"
    else:
        base_sql = "SELECT id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao, '' AS highlight, 0.0 AS score FROM tickets_index"
    clauses = []
    if match_sql:
        clauses.append("tickets_index MATCH ?")
        params = [match_sql] + params
    if where_sql:
        clauses.append(where_sql)
    sql = base_sql
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
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
                id=r["id"], titulo=(r["titulo"] or ""), descricao=r["descricao"], status=r["status"], prioridade=r["prioridade"], categoria=r["categoria"], entidade=r["entidade"], tecnico=r["tecnico"], grupo=r["grupo"], requerente=r["requerente"], data_criacao=r["data_criacao"], data_modificacao=r["data_modificacao"], highlight=r["highlight"], score=float(r["score"]) if r["score"] is not None else 0.0
            ))
        return result
    finally:
        conn.close()

@app.get("/suggest")
def suggest(field: str, prefix: str = "", limit: int = 10):
    _load_env()
    if USE_GLPI_LIVE:
        st = init_session()
        try:
            items = search_tickets(st, include_deleted=False, range_start=0, range_len=200)
            key = {
                "status": "STATUS",
                "prioridade": "PRIORIDADE",
                "categoria": "CATEGORIA",
                "entidade": "ENTIDADE",
                "tecnico": "TECNICO",
                "grupo": "GRUPO",
                "requerente": "REQUERENTE"
            }.get(field, "CATEGORIA")
            s = set()
            for it in items:
                v = str(it.get(key) or "")
                if v and v.lower().startswith((prefix or "").lower()):
                    s.add(v)
            out = list(s)
            out.sort()
            return out[:limit]
        finally:
            if st:
                kill_session(st)
    conn = get_conn()
    cur = conn.cursor()
    field = field if field in {"status", "prioridade", "categoria", "entidade", "tecnico", "grupo", "requerente"} else "categoria"
    sql = f"SELECT DISTINCT {field} FROM tickets_index WHERE {field} LIKE ? ORDER BY {field} LIMIT ?"
    rows = cur.execute(sql, [prefix + "%", limit]).fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

@app.post("/index/rebuild")
def index_rebuild():
    ok = os.system(f"python {os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indexer', 'build_index.py')}") == 0
    return {"rebuild": ok}
@app.get("/export")
def export(q: str = "", status: Optional[str] = None, prioridade: Optional[str] = None, categoria: Optional[str] = None, entidade: Optional[str] = None, tecnico: Optional[str] = None, grupo: Optional[str] = None, dt_ini: Optional[str] = None, dt_fim: Optional[str] = None, limit: int = 1000, format: str = "xlsx"):
    import pandas as pd, io
    conn = get_conn()
    cur = conn.cursor()
    where = []
    params = []
    if status:
        where.append("status = ?")
        params.append(status)
    if prioridade:
        where.append("prioridade = ?")
        params.append(prioridade)
    if categoria:
        where.append("categoria = ?")
        params.append(categoria)
    if entidade:
        where.append("entidade = ?")
        params.append(entidade)
    if tecnico:
        where.append("tecnico = ?")
        params.append(tecnico)
    if grupo:
        where.append("grupo = ?")
        params.append(grupo)
    if dt_ini:
        where.append("data_criacao >= ?")
        params.append(dt_ini)
    if dt_fim:
        where.append("data_criacao <= ?")
        params.append(dt_fim)
    clauses = []
    if q.strip():
        clauses.append("tickets_index MATCH ?")
        params = [q.strip()] + params
    clauses.append("is_deleted = 0")
    if where:
        clauses.append(" AND ".join(where))
    sql = "SELECT id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, requerente, data_criacao, data_modificacao FROM tickets_index"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " LIMIT ?"
    params += [limit]
    rows = cur.execute(sql, params).fetchall()
    conn.close()
    cols = ["ID","TITULO","DESCRICAO","STATUS","PRIORIDADE","CATEGORIA","ENTIDADE","TECNICO","GRUPO","REQUERENTE","DATA_CRIACAO","DATA_MODIFICACAO"]
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