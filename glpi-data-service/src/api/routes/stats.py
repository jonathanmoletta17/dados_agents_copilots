from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from src.db.postgres_manager import get_db_manager

router = APIRouter()

@router.get("/{context}/estatisticas/resumo")
async def get_stats_summary(context: str):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    total = db.count_tickets({"is_deleted": False})
    
    # Contagem por status
    with db.get_session() as session:
        result = session.execute(text(f"SELECT status, COUNT(*) FROM {context}.tickets WHERE is_deleted = false GROUP BY status"))
        por_status = {row[0]: row[1] for row in result}
    
    return {
        "contexto": context,
        "total_tickets": total,
        "por_status": por_status
    }

@router.get("/{context}/estatisticas/tecnicos")
async def get_technician_ranking(context: str, limite: int = 20):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    
    with db.get_session() as session:
        query = text(f"""
            SELECT tecnico, COUNT(*) as total
            FROM {context}.tickets
            WHERE tecnico IS NOT NULL AND status IN ('SOLUCIONADO', 'FECHADO')
            GROUP BY tecnico
            ORDER BY total DESC
            LIMIT :limite
        """)
        result = session.execute(query, {"limite": limite})
        ranking = [{"tecnico": row[0], "total_resolvido": row[1]} for row in result]
    
    return {
        "contexto": context,
        "ranking": ranking
    }
