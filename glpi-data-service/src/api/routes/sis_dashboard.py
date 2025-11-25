from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
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

@router.get("/sis/dashboard/stats-gerais")
async def get_sis_general_stats(
    inicio: Optional[str] = None,
    fim: Optional[str] = None
):
    context = "sis"
    db = get_db_manager(context)
    date_filter = get_date_filter(inicio, fim)
    
    with db.get_session() as session:
        query_status = text(f"""
            SELECT status, COUNT(*) 
            FROM {context}.tickets 
            WHERE is_deleted = false {date_filter}
            GROUP BY status
        """)
        result = session.execute(query_status)
        raw = [(str(row[0] or ''), int(row[1] or 0)) for row in result]
        # Normaliza para lower-case
        lowered = { (s or '').lower(): c for s, c in raw }

        def get_sum(*synonyms: str) -> int:
            return sum(lowered.get(s.lower(), 0) for s in synonyms)

        novos = get_sum('novo')
        em_atendimento = get_sum('atribuido','em andamento (atribuído)','em andamento (atribuido)')
        pendentes = get_sum('pendente')
        planejados = get_sum('planejado','em andamento (planejado)')
        solucionados = get_sum('solucionado')
        fechados = get_sum('fechado')
        resolvidos = solucionados + fechados

        return {
            "novos": novos,
            "em_atendimento": em_atendimento,
            "pendentes": pendentes,
            "planejados": planejados,
            "resolvidos": resolvidos
        }

@router.get("/sis/dashboard/ranking-entidades")
async def get_sis_entity_ranking(
    inicio: Optional[str] = None,
    fim: Optional[str] = None
):
    context = "sis"
    db = get_db_manager(context)
    date_filter = get_date_filter(inicio, fim)
    
    with db.get_session() as session:
        # Use 'entidade' column which is populated by the sync worker
        query = text(f"""
            SELECT entidade, COUNT(*) as total
            FROM {context}.tickets
            WHERE entidade IS NOT NULL 
            AND entidade != ''
            AND is_deleted = false
            {date_filter}
            GROUP BY entidade
            ORDER BY total DESC
            LIMIT 20
        """)
        result = session.execute(query)
        
        return [
            {"entity_name": row[0], "ticket_count": row[1]}
            for row in result
        ]

@router.get("/sis/dashboard/ranking-categorias")
async def get_sis_category_ranking(
    inicio: Optional[str] = None,
    fim: Optional[str] = None
):
    context = "sis"
    db = get_db_manager(context)
    date_filter = get_date_filter(inicio, fim)
    
    with db.get_session() as session:
        query = text(f"""
            SELECT categoria, COUNT(*) as total
            FROM {context}.tickets
            WHERE categoria IS NOT NULL 
            AND is_deleted = false
            {date_filter}
            GROUP BY categoria
            ORDER BY total DESC
        """)
        result = session.execute(query)
        
        return [
            {"category_name": row[0], "ticket_count": row[1]}
            for row in result
        ]

@router.get("/sis/dashboard/ranking-tecnicos")
async def get_sis_technician_ranking(
    inicio: Optional[str] = None,
    fim: Optional[str] = None
):
    context = "sis"
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
            LIMIT 20
        """)
        result = session.execute(query)
        
        return [
            {"tecnico": row[0], "tickets": row[1], "nivel": "N1"}
            for row in result
        ]

@router.get("/sis/dashboard/tickets-novos")
async def get_sis_new_tickets(limit: int = 10):
    context = "sis"
    db = get_db_manager(context)
    
    tickets = db.list_tickets(
        filters={"status": "NOVO", "is_deleted": False},
        limit=limit,
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
