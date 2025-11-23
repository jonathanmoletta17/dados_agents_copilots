from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy import text
from src.db.postgres_manager import get_db_manager

router = APIRouter()

def get_date_filter(inicio: Optional[str], fim: Optional[str]) -> str:
    """Gera cláusula WHERE para filtro de data."""
    clauses = []
    if inicio:
        clauses.append(f"criado_em >= '{inicio} 00:00:00'")
    if fim:
        clauses.append(f"criado_em <= '{fim} 23:59:59'")
    
    if not clauses:
        return ""
    
    return "AND " + " AND ".join(clauses)

@router.get("/{context}/metrics-gerais")
async def get_general_metrics(
    context: str,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    date_filter = get_date_filter(inicio, fim)
    
    with db.get_session() as session:
        # Total tickets in period
        query_total = text(f"SELECT COUNT(*) FROM {context}.tickets WHERE is_deleted = false {date_filter}")
        total = session.execute(query_total).scalar()
        
        # By status
        query_status = text(f"""
            SELECT status, COUNT(*) 
            FROM {context}.tickets 
            WHERE is_deleted = false {date_filter}
            GROUP BY status
        """)
        result = session.execute(query_status)
        status_counts = {row[0]: row[1] for row in result}
        
        # Map to frontend expected keys
        # Frontend expects: novos, em_progresso, pendentes, resolvidos
        # Backend statuses: NOVO, ATRIBUIDO, PLANEJADO, PENDENTE, SOLUCIONADO, FECHADO
        
        novos = status_counts.get('NOVO', 0)
        em_progresso = status_counts.get('ATRIBUIDO', 0) + status_counts.get('PLANEJADO', 0)
        pendentes = status_counts.get('PENDENTE', 0)
        resolvidos = status_counts.get('SOLUCIONADO', 0) + status_counts.get('FECHADO', 0)
        
        return {
            "novos": novos,
            "em_progresso": em_progresso,
            "pendentes": pendentes,
            "resolvidos": resolvidos
        }

@router.get("/{context}/status-niveis")
async def get_level_stats(
    context: str,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
):
    """
    Retorna distribuição de tickets por nível de suporte (N1, N2, N3, N4).
    Cada nível mostra contagem por status.
    """
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    date_filter = get_date_filter(inicio, fim)
    
    with db.get_session() as session:
        result = {}
        
        # Para cada nível (N1, N2, N3, N4)
        for nivel in ['N1', 'N2', 'N3', 'N4']:
            # Busca contagem por status para este nível
            query = text(f"""
                SELECT status, COUNT(*) as total
                FROM {context}.tickets 
                WHERE is_deleted = false 
                AND grupo_nivel = :nivel
                {date_filter}
                GROUP BY status
            """)
            
            rows = session.execute(query, {"nivel": nivel}).fetchall()
            status_counts = {row[0]: row[1] for row in rows}
            
            # Mapeia para formato esperado pelo frontend
            novos = status_counts.get('NOVO', 0)
            em_progresso = status_counts.get('ATRIBUIDO', 0) + status_counts.get('PLANEJADO', 0)
            pendentes = status_counts.get('PENDENTE', 0)
            resolvidos = status_counts.get('SOLUCIONADO', 0) + status_counts.get('FECHADO', 0)
            total = novos + em_progresso + pendentes + resolvidos
            
            result[nivel] = {
                "novos": novos,
                "em_progresso": em_progresso,
                "pendentes": pendentes,
                "resolvidos": resolvidos,
                "total": total
            }
        
        return result

@router.get("/{context}/ranking-tecnicos")
async def get_technician_ranking(
    context: str,
    inicio: Optional[str] = None,
    fim: Optional[str] = None
):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    date_filter = get_date_filter(inicio, fim)
    
    with db.get_session() as session:
        query = text(f"""
            SELECT tecnico, COUNT(*) as total
            FROM {context}.tickets
            WHERE tecnico IS NOT NULL 
            AND tecnico != 'N/A'
            AND is_deleted = false
            {date_filter}
            GROUP BY tecnico
            ORDER BY total DESC
            LIMIT 10
        """)
        result = session.execute(query)
        
        ranking = []
        for row in result:
            ranking.append({
                "tecnico": row[0],
                "tickets": row[1],
                "nivel": "N1" # Placeholder
            })
            
        return ranking

@router.get("/{context}/tickets-novos")
async def get_new_tickets(context: str):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    
    # Fetch last 10 new tickets
    tickets = db.list_tickets(
        filters={"status": "NOVO", "is_deleted": False},
        limit=10,
        order_by="criado_em DESC"
    )
    
    return [
        {
            "id": t.glpi_id,
            "titulo": t.titulo,
            "solicitante": t.requerente,
            "data": t.criado_em.isoformat() if t.criado_em else None,
            "prioridade": t.prioridade
        }
        for t in tickets
    ]
