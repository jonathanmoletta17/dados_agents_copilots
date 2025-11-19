import io
import pandas as pd
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Optional
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "indexer", "search.db")
router = APIRouter()

def get_conn():
    return sqlite3.connect(DB_PATH)

@router.get("/export")
def export(q: str = "", status: Optional[str] = None, prioridade: Optional[str] = None, categoria: Optional[str] = None, entidade: Optional[str] = None, tecnico: Optional[str] = None, grupo: Optional[str] = None, dt_ini: Optional[str] = None, dt_fim: Optional[str] = None, limit: int = 1000, format: str = "xlsx"):
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
    if where:
        clauses.append(" AND ".join(where))
    sql = "SELECT id, titulo, descricao, status, prioridade, categoria, entidade, tecnico, grupo, data_criacao, data_modificacao FROM tickets_index"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " LIMIT ?"
    params += [limit]
    rows = cur.execute(sql, params).fetchall()
    conn.close()
    cols = ["ID","TITULO","DESCRICAO","STATUS","PRIORIDADE","CATEGORIA","ENTIDADE","TECNICO","GRUPO","DATA_CRIACAO","DATA_MODIFICACAO"]
    df = pd.DataFrame(rows, columns=cols)
    if format == "csv":
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=busca_glpi.csv"})
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition":"attachment; filename=busca_glpi.xlsx"})