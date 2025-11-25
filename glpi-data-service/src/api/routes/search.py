from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from src.db.postgres_manager import get_db_manager
from src.utils.text_processor import TextProcessor
import re

router = APIRouter()

class SearchResponseItem(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    descricao_preview: Optional[str] = None
    descricao_full: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None
    categoria: Optional[str] = None
    entidade: Optional[str] = None
    tecnico: Optional[str] = None
    grupo: Optional[str] = None
    requerente: Optional[str] = None
    data_criacao: Optional[str] = None
    data_modificacao: Optional[str] = None
    data_solucao: Optional[str] = None
    data_fechamento: Optional[str] = None
    motivo_pendencia: Optional[str] = None
    url: Optional[str] = None
    score: float

class SearchResponse(BaseModel):
    items: List[SearchResponseItem]
    total: int
    page: int
    size: int
    pages: int

def build_search_query(q: str, filters: dict, context: str) -> tuple:
    """Build search query with multi-term AND across fields and simple relevance score."""
    
    # Base query
    where_clauses = ["is_deleted = false"]
    params = {}

    # Helper: tokenize query string into terms (supports quotes for phrases)
    def _tokenize(query: str) -> list:
        import shlex
        try:
            terms = [t.strip() for t in shlex.split(query) if t.strip()]
            return terms if terms else []
        except Exception:
            return [query.strip()] if query and query.strip() else []

    # Search across displayed fields using AND between terms, OR across fields
    score_parts = []
    if q and q.strip():
        terms = _tokenize(q)
        term_blocks = []
        # Field list and weights for scoring
        field_weight = [
            ("titulo", 3),
            ("descricao_md", 3),
            ("categoria", 2),
            ("entidade", 2),
            ("requerente", 2),
            ("tecnico", 1),
            ("grupo", 1),
            ("status", 1),
        ]

        # For single numeric query, add exact ID match
        if len(terms) == 1 and terms[0].isdigit():
            params['q_num'] = int(terms[0])
            # Include ID exact match OR partial in its block
            # Build block for numeric term
        
        for idx, term in enumerate(terms):
            p = f"t{idx}"
            params[p] = f"%{term}%"
            field_checks = [f"unaccent({fname}) ILIKE unaccent(:{p})" for fname, _ in field_weight]
            # Always include partial ID text match as a field
            field_checks.append(f"glpi_id::text ILIKE :{p}")
            # If single numeric term, also allow exact ID match
            if len(terms) == 1 and term.isdigit():
                field_checks.append("glpi_id = :q_num")
            term_blocks.append(f"({' OR '.join(field_checks)})")

            # Score: sum weights when field matches this term
            for fname, wt in field_weight:
                score_parts.append(f"CASE WHEN unaccent({fname}) ILIKE unaccent(:{p}) THEN {wt} ELSE 0 END")
            # ID match contributes small weight
            score_parts.append(f"CASE WHEN glpi_id::text ILIKE :{p} THEN 1 ELSE 0 END")

        # AND across terms: all terms must be present in at least one field
        where_clauses.append(" AND ".join(term_blocks))
    
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
    if q and q.strip():
        score_sql = " + ".join(score_parts) if score_parts else "0"
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
                ({score_sql}) as score
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
                0.0 as score
            FROM {context}.tickets
            WHERE {where_clause}
        """
    
    count_sql = f"SELECT COUNT(*) FROM {context}.tickets WHERE {where_clause}"
    
    return select_sql, count_sql, params

# --- Implementation Helpers ---

async def _search_tickets_impl(context, q, status, prioridade, categoria, entidade, tecnico, grupo, requerente, dt_ini, dt_fim, page, size, sort):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔍 _search_tickets_impl called for context='{context}', q='{q}', page={page}, size={size}, sort='{sort}'")
        
        db = get_db_manager(context)
        logger.info(f"✅ DB manager obtained for context '{context}'")
        
        filters = {
            k: v for k, v in locals().items() 
            if k in ['status', 'prioridade', 'categoria', 'entidade', 'tecnico', 'grupo', 'requerente', 'dt_ini', 'dt_fim'] and v is not None
        }
        logger.info(f"📋 Filters: {filters}")
        
        select_sql, count_sql, params = build_search_query(q, filters, context)
        logger.info(f"📝 Query built. Params: {params}")
        logger.debug(f"SQL: {select_sql}")
        
        # Add sorting
        if sort == 'recent':
            select_sql += " ORDER BY data_modificacao DESC"
        else:
            # If search query exists, order by rank, else by date
            if q and q.strip():
                select_sql += " ORDER BY score DESC, data_modificacao DESC"
            else:
                select_sql += " ORDER BY data_modificacao DESC"
        
        logger.info(f"📊 Sort applied: {sort}")
                
        # Add pagination
        select_sql += f" LIMIT {size} OFFSET {(page - 1) * size}"
        logger.info(f"📄 Pagination: LIMIT {size} OFFSET {(page - 1) * size}")
        
        with db.get_session() as session:
            total = session.execute(text(count_sql), params).scalar()
            result = session.execute(text(select_sql), params)
            
            items = []
            for row in result:
                item = {
                    "id": row.id,
                    "titulo": row.titulo,
                    "descricao": None,
                    "descricao_preview": None,
                    "descricao_full": None,
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
                    "score": float(getattr(row, 'score', 0))
                }
                raw_desc = getattr(row, 'descricao', None)
                if raw_desc:
                    # Extrair apenas campo "Descrição" de formulários estruturados
                    extracted = TextProcessor.extract_form_description(raw_desc)
                    # Aplicar limpeza de texto padrão
                    cleaned = TextProcessor.clean_text(extracted)
                    item["descricao_full"] = cleaned
                    # preview: 3 lines or 200 chars
                    lines = cleaned.splitlines()
                    preview = " ".join(lines) if len(lines) <= 3 else " ".join(lines[:3])
                    if len(preview) > 200:
                        preview = preview[:200].rsplit(" ", 1)[0] + "…"
                    elif len(lines) > 3 or len(preview) < len(cleaned):
                        preview = preview + "…"
                    item["descricao_preview"] = preview
                    item["descricao"] = preview
                    
                items.append(item)
                
            response_data = {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
            
            logger.info(f"✅ Response prepared: {len(items)} items, total={total}, page={page}")
            if items:
                logger.debug(f"📦 First item sample: {items[0]}")
            
            return response_data
    except Exception as e:
        import traceback
        logger.error("="*80)
        logger.error(f"❌ ERROR in _search_tickets_impl for context='{context}'")
        logger.error(f"Parameters: q={q}, page={page}, size={size}, sort={sort}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception message: {str(e)}")
        
        # If it's a Pydantic validation error, log details
        if hasattr(e, 'errors'):
            logger.error("🔍 Pydantic Validation Errors:")
            for err in e.errors():
                logger.error(f"  - Field: {err.get('loc')}, Type: {err.get('type')}, Msg: {err.get('msg')}")
        
        logger.error("Stack trace:")
        traceback.print_exc()
        logger.error("="*80)
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

async def _get_search_stats_impl(context, q=None, status=None, prioridade=None, categoria=None, entidade=None, tecnico=None, grupo=None, requerente=None, dt_ini=None, dt_fim=None):
    db = get_db_manager(context)
    stats = {}
    where_clauses = ["is_deleted = false"]
    params = {}
    
    if status:
        status_map = {
            'novo': 'NOVO',
            'processando (atribuído)': 'ATRIBUIDO',
            'pendente': 'PENDENTE',
            'solucionado': 'SOLUCIONADO',
            'fechado': 'FECHADO'
        }
        raw_status = status.lower()
        db_status = status_map.get(raw_status, raw_status.upper())
        where_clauses.append("status = :status")
        params['status'] = db_status
    if prioridade:
        where_clauses.append("prioridade = :prioridade")
        params['prioridade'] = prioridade
    if categoria:
        where_clauses.append("categoria ILIKE :categoria")
        params['categoria'] = f"%{categoria}%"
    if entidade:
        where_clauses.append("entidade ILIKE :entidade")
        params['entidade'] = f"%{entidade}%"
    if tecnico:
        where_clauses.append("tecnico ILIKE :tecnico")
        params['tecnico'] = f"%{tecnico}%"
    if grupo:
        where_clauses.append("grupo ILIKE :grupo")
        params['grupo'] = f"%{grupo}%"
    if requerente:
        where_clauses.append("requerente ILIKE :requerente")
        params['requerente'] = f"%{requerente}%"
    if dt_ini:
        where_clauses.append("criado_em >= :dt_ini")
        params['dt_ini'] = f"{dt_ini} 00:00:00"
    if dt_fim:
        where_clauses.append("criado_em <= :dt_fim")
        params['dt_fim'] = f"{dt_fim} 23:59:59"
    
    if q and q.strip():
        import shlex
        try:
            terms = [t.strip() for t in shlex.split(q) if t.strip()]
        except Exception:
            terms = [q.strip()]
        blocks = []
        for idx, term in enumerate(terms):
            p = f"st{idx}"
            params[p] = f"%{term}%"
            fields = [
                "unaccent(titulo) ILIKE unaccent(:%s)" % p,
                "unaccent(categoria) ILIKE unaccent(:%s)" % p,
                "unaccent(entidade) ILIKE unaccent(:%s)" % p,
                "unaccent(requerente) ILIKE unaccent(:%s)" % p,
                "unaccent(tecnico) ILIKE unaccent(:%s)" % p,
                "unaccent(grupo) ILIKE unaccent(:%s)" % p,
                "unaccent(status) ILIKE unaccent(:%s)" % p,
                "glpi_id::text ILIKE :%s" % p,
            ]
            blocks.append(f"({' OR '.join(fields)})")
        where_clauses.append(" AND ".join(blocks))
    
    where_clause = " AND ".join(where_clauses)
    
    with db.get_session() as session:
        res = session.execute(text(f"SELECT status, COUNT(*) FROM {context}.tickets WHERE {where_clause} GROUP BY status"), params)
        stats['status'] = [[row[0], row[1]] for row in res if row[0]]
        res = session.execute(text(f"SELECT categoria, COUNT(*) FROM {context}.tickets WHERE {where_clause} GROUP BY categoria ORDER BY 2 DESC LIMIT 10"), params)
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
async def get_search_stats(
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
):
    return await _get_search_stats_impl("dtic", q, status, prioridade, categoria, entidade, tecnico, grupo, requerente, dt_ini, dt_fim)

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
async def get_sis_search_stats(
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
):
    return await _get_search_stats_impl("sis", q, status, prioridade, categoria, entidade, tecnico, grupo, requerente, dt_ini, dt_fim)

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
