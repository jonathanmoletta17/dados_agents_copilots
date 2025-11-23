from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from src.db.postgres_manager import get_db_manager
import re

router = APIRouter()

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
    data_solucao: Optional[str]
    data_fechamento: Optional[str]
    motivo_pendencia: Optional[str]
    url: Optional[str]
    highlight: Optional[str]
    score: float

class SearchResponse(BaseModel):
    items: List[SearchResponseItem]
    total: int
    page: int
    size: int
    pages: int

def build_search_query(q: str, filters: dict, context: str) -> tuple:
    """Build PostgreSQL full-text search query with filters."""
    
    # Base query
    where_clauses = ["is_deleted = false"]
    params = {}
    
    # Full-text search on titulo and descricao_md
    if q:
        # Clean and prepare search query
        search_term = re.sub(r'[^\w\s]', ' ', q)
        tsquery = ' & '.join(search_term.split())
        where_clauses.append("""
            (to_tsvector('portuguese', COALESCE(titulo, '')) || 
             to_tsvector('portuguese', COALESCE(descricao_md, ''))) 
            @@ to_tsquery('portuguese', :search_term)
        """)
        params['search_term'] = tsquery
    
    # Filters
    if filters.get('status'):
        # Map frontend status to DB status
        status_map = {
            'novo': 'NOVO',
            'processando (atribuído)': 'ATRIBUIDO',
            'pendente': 'PENDENTE',
            'solucionado': 'SOLUCIONADO',
            'fechado': 'FECHADO'
        }
        
        raw_status = filters['status'].lower()
        db_status = status_map.get(raw_status, raw_status.upper())
        
        where_clauses.append("status = :status")
        params['status'] = db_status
    
    if filters.get('prioridade'):
        where_clauses.append("prioridade = :prioridade")
        params['prioridade'] = filters['prioridade']
    
    if filters.get('categoria'):
        where_clauses.append("categoria ILIKE :categoria")
        params['categoria'] = f"%{filters['categoria']}%"
    
    if filters.get('entidade'):
        where_clauses.append("entidade ILIKE :entidade")
        params['entidade'] = f"%{filters['entidade']}%"
    
    if filters.get('tecnico'):
        where_clauses.append("tecnico ILIKE :tecnico")
        params['tecnico'] = f"%{filters['tecnico']}%"
    
    if filters.get('grupo'):
        where_clauses.append("grupo ILIKE :grupo")
        params['grupo'] = f"%{filters['grupo']}%"
    
    if filters.get('requerente'):
        where_clauses.append("requerente ILIKE :requerente")
        params['requerente'] = f"%{filters['requerente']}%"
    
    if filters.get('dt_ini'):
        where_clauses.append("criado_em >= :dt_ini")
        params['dt_ini'] = f"{filters['dt_ini']} 00:00:00"
    
    if filters.get('dt_fim'):
        where_clauses.append("criado_em <= :dt_fim")
        params['dt_fim'] = f"{filters['dt_fim']} 23:59:59"
    
    where_clause = " AND ".join(where_clauses)
    
    # Select with relevance scoring
    if q:
        select_sql = f"""
            SELECT 
                glpi_id as id,
                titulo,
                descricao_md as descricao,
                status,
                prioridade,
                categoria,
                entidade,
                tecnico,
                grupo,
                requerente,
                to_char(criado_em, 'YYYY-MM-DD HH24:MI:SS') as data_criacao,
                to_char(atualizado_em, 'YYYY-MM-DD HH24:MI:SS') as data_modificacao,
                to_char(solucionado_em, 'YYYY-MM-DD HH24:MI:SS') as data_solucao,
                to_char(fechado_em, 'YYYY-MM-DD HH24:MI:SS') as data_fechamento,
                '' as motivo_pendencia,
                url,
                ts_headline('portuguese', COALESCE(titulo, '') || ' ' || COALESCE(descricao_md, ''), 
                           to_tsquery('portuguese', :search_term),
                           'MaxWords=50, MinWords=10') as highlight,
                ts_rank(to_tsvector('portuguese', COALESCE(titulo, '') || ' ' || COALESCE(descricao_md, '')),
                       to_tsquery('portuguese', :search_term)) as score
            FROM {context}.tickets
            WHERE {where_clause}
        """
    else:
        select_sql = f"""
            SELECT 
                glpi_id as id,
                titulo,
                descricao_md as descricao,
                status,
                prioridade,
                categoria,
                entidade,
                tecnico,
                grupo,
                requerente,
                to_char(criado_em, 'YYYY-MM-DD HH24:MI:SS') as data_criacao,
                to_char(atualizado_em, 'YYYY-MM-DD HH24:MI:SS') as data_modificacao,
                to_char(solucionado_em, 'YYYY-MM-DD HH24:MI:SS') as data_solucao,
                to_char(fechado_em, 'YYYY-MM-DD HH24:MI:SS') as data_fechamento,
                '' as motivo_pendencia,
                url,
                '' as highlight,
                0.0 as score
            FROM {context}.tickets
            WHERE {where_clause}
        """
    
    count_sql = f"SELECT COUNT(*) FROM {context}.tickets WHERE {where_clause}"
    
    return select_sql, count_sql, params

# --- Implementation Helpers ---

async def _search_tickets_impl(context, q, status, prioridade, categoria, entidade, tecnico, grupo, requerente, dt_ini, dt_fim, page, size, sort):
    try:
        db = get_db_manager(context)
        filters = {
            k: v for k, v in locals().items() 
            if k in ['status', 'prioridade', 'categoria', 'entidade', 'tecnico', 'grupo', 'requerente', 'dt_ini', 'dt_fim'] and v is not None
        }
        
        select_sql, count_sql, params = build_search_query(q, filters, context)
        
        # Add sorting
        if sort == 'recent':
            select_sql += " ORDER BY data_modificacao DESC"
        else:
            # If search query exists, order by rank, else by date
            if q and q.strip():
                select_sql += " ORDER BY score DESC, data_modificacao DESC"
            else:
                select_sql += " ORDER BY data_modificacao DESC"
                
        # Add pagination
        select_sql += f" LIMIT {size} OFFSET {(page - 1) * size}"
        
        with db.get_session() as session:
            total = session.execute(text(count_sql), params).scalar()
            result = session.execute(text(select_sql), params)
            
            items = []
            for row in result:
                item = {
                    "id": row.id,
                    "titulo": row.titulo,
                    "descricao": row.descricao,
                    "status": row.status,
                    "prioridade": row.prioridade,
                    "categoria": row.categoria,
                    "entidade": row.entidade,
                    "tecnico": row.tecnico,
                    "grupo": row.grupo,
                    "requerente": row.requerente,
                    "data_criacao": row.data_criacao,
                    "data_modificacao": row.data_modificacao,
                    "data_solucao": row.data_solucao,
                    "data_fechamento": row.data_fechamento,
                    "motivo_pendencia": row.motivo_pendencia,
                    "url": row.url,
                    "score": getattr(row, 'score', 0)
                }
                
                # Add highlight if available
                if hasattr(row, 'highlight'):
                    item['highlight'] = row.highlight
                    
                items.append(item)
                
            return {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR in _search_tickets_impl: {e}")
        raise e

async def _suggest_values_impl(context, field, prefix):
    db = get_db_manager(context)
    # Validate field to prevent injection
    allowed_fields = ['categoria', 'entidade', 'tecnico', 'requerente']
    if field not in allowed_fields:
        return []
        
    query = text(f"""
        SELECT DISTINCT {field}
        FROM {context}.tickets
        WHERE {field} ILIKE :prefix
        AND is_deleted = false
        ORDER BY {field}
        LIMIT 10
    """)
    
    with db.get_session() as session:
        result = session.execute(query, {"prefix": f"%{prefix}%"})
        return [row[0] for row in result if row[0]]

async def _get_search_stats_impl(context):
    db = get_db_manager(context)
    stats = {}
    
    with db.get_session() as session:
        # Status counts
        res = session.execute(text(f"SELECT status, COUNT(*) FROM {context}.tickets WHERE is_deleted = false GROUP BY status"))
        stats['status'] = [[row[0], row[1]] for row in res if row[0]]
        
        # Top Categories
        res = session.execute(text(f"SELECT categoria, COUNT(*) FROM {context}.tickets WHERE is_deleted = false GROUP BY categoria ORDER BY 2 DESC LIMIT 10"))
        stats['categoria'] = [[row[0], row[1]] for row in res if row[0]]
        
    return stats

async def _export_search_results_impl(context, q, status, prioridade, categoria, entidade, tecnico, grupo, requerente, dt_ini, dt_fim, format):
    # Reuse search logic but without pagination
    db = get_db_manager(context)
    filters = {
        k: v for k, v in locals().items() 
        if k in ['status', 'prioridade', 'categoria', 'entidade', 'tecnico', 'grupo', 'requerente', 'dt_ini', 'dt_fim'] and v is not None
    }
    
    select_sql, _, params = build_search_query(q, filters, context)
    select_sql += " LIMIT 1000" # Limit export
    
    with db.get_session() as session:
        result = session.execute(text(select_sql), params)
        return {"message": "Export not fully implemented yet", "count": result.rowcount}

# --- DTIC Endpoints ---

@router.get("/dtic/search", response_model=SearchResponse)
async def search_tickets(
    q: str = Query(None, description="Termo de busca"),
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    categoria: Optional[str] = None,
    entidade: Optional[str] = None,
    tecnico: Optional[str] = None,
    grupo: Optional[str] = None,
    requerente: Optional[str] = None,
    dt_ini: Optional[str] = None,
    dt_fim: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort: str = Query("score", regex="^(score|recent)$")
):
    """Busca full-text em tickets da DTIC com filtros."""
    return await _search_tickets_impl(
        "dtic", q, status, prioridade, categoria, entidade, 
        tecnico, grupo, requerente, dt_ini, dt_fim, page, size, sort
    )

@router.get("/dtic/search/suggest")
async def suggest_values(
    field: str = Query(..., regex="^(categoria|entidade|tecnico|requerente)$"),
    prefix: str = Query("", min_length=1)
):
    """Sugestões para autocomplete."""
    return await _suggest_values_impl("dtic", field, prefix)

@router.get("/dtic/search/stats")
async def get_search_stats():
    """Estatísticas para filtros."""
    return await _get_search_stats_impl("dtic")

@router.get("/dtic/search/export")
async def export_search_results(
    q: str = Query(None),
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    categoria: Optional[str] = None,
    entidade: Optional[str] = None,
    tecnico: Optional[str] = None,
    grupo: Optional[str] = None,
    requerente: Optional[str] = None,
    dt_ini: Optional[str] = None,
    dt_fim: Optional[str] = None,
    format: str = Query("csv", regex="^(csv|xlsx)$")
):
    """Exporta resultados da busca."""
    return await _export_search_results_impl(
        "dtic", q, status, prioridade, categoria, entidade,
        tecnico, grupo, requerente, dt_ini, dt_fim, format
    )

# --- SIS Endpoints ---

@router.get("/sis/search", response_model=SearchResponse)
async def search_sis_tickets(
    q: str = Query(None, description="Termo de busca"),
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    categoria: Optional[str] = None,
    entidade: Optional[str] = None,
    tecnico: Optional[str] = None,
    grupo: Optional[str] = None,
    requerente: Optional[str] = None,
    dt_ini: Optional[str] = None,
    dt_fim: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort: str = Query("score", regex="^(score|recent)$")
):
    """Busca full-text em tickets do SIS com filtros."""
    return await _search_tickets_impl(
        "sis", q, status, prioridade, categoria, entidade, 
        tecnico, grupo, requerente, dt_ini, dt_fim, page, size, sort
    )

@router.get("/sis/search/suggest")
async def suggest_sis_values(
    field: str = Query(..., regex="^(categoria|entidade|tecnico|requerente)$"),
    prefix: str = Query("", min_length=1)
):
    """Sugestões para autocomplete no SIS."""
    return await _suggest_values_impl("sis", field, prefix)

@router.get("/sis/search/stats")
async def get_sis_search_stats():
    """Estatísticas para filtros do SIS."""
    return await _get_search_stats_impl("sis")

@router.get("/sis/search/export")
async def export_sis_search_results(
    q: str = Query(None),
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    categoria: Optional[str] = None,
    entidade: Optional[str] = None,
    tecnico: Optional[str] = None,
    grupo: Optional[str] = None,
    requerente: Optional[str] = None,
    dt_ini: Optional[str] = None,
    dt_fim: Optional[str] = None,
    format: str = Query("csv", regex="^(csv|xlsx)$")
):
    """Exporta resultados da busca SIS."""
    return await _export_search_results_impl(
        "sis", q, status, prioridade, categoria, entidade,
        tecnico, grupo, requerente, dt_ini, dt_fim, format
    )
