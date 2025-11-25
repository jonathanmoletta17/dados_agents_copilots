from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from sqlalchemy import text
from datetime import datetime, timedelta
from src.db.postgres_manager import get_db_manager

router = APIRouter()

# SQL query to list all chargers with their current status
# NOTE: This endpoint has been DISABLED due to performance issues.
# The query contains hundreds of nested subqueries that execute for every row,
# causing ~15 second response times. Use the optimized /kanban endpoint instead.
QUERY_LIST_CARREGADORES = """
    SELECT 
        c.id,
        c.name as nome,
        c.location_name as localizacao,
        CASE 
            WHEN t.id IS NOT NULL THEN 'ocupado'
            ELSE 'disponivel'
        END as status,
        t.glpi_id as ticket_id,
        t.titulo as ticket_titulo,
        CASE
            WHEN t.id IS NOT NULL THEN 
                FLOOR(EXTRACT(EPOCH FROM (NOW() - t.criado_em))/3600) || 'h ' ||
                FLOOR((EXTRACT(EPOCH FROM (NOW() - t.criado_em)) - FLOOR(EXTRACT(EPOCH FROM (NOW() - t.criado_em))/3600)*3600)/60) || 'm'
            ELSE NULL
        END as tempo_atribuido,
        CASE
            WHEN t.id IS NULL THEN
                FLOOR(EXTRACT(EPOCH FROM (NOW() - COALESCE(
                    (SELECT MAX(t2.atualizado_em) 
                     FROM {schema}.tickets t2
                     JOIN {schema}.carregador_tickets ct2 ON ct2.tickets_id = t2.glpi_id
                     WHERE ct2.items_id = c.id 
                       AND t2.status IN ('FECHADO', 'SOLUCIONADO')),
                    c.date_creation
                )))/3600) || 'h ' ||
                FLOOR((EXTRACT(EPOCH FROM (NOW() - COALESCE(
                    (SELECT MAX(t2.atualizado_em) 
                     FROM {schema}.tickets t2
                     JOIN {schema}.carregador_tickets ct2 ON ct2.tickets_id = t2.glpi_id
                     WHERE ct2.items_id = c.id 
                       AND t2.status IN ('FECHADO', 'SOLUCIONADO')),
                    c.date_creation
                ))) - FLOOR(EXTRACT(EPOCH FROM (NOW() - COALESCE(
                    (SELECT MAX(t2.atualizado_em) 
                     FROM {schema}.tickets t2
                     JOIN {schema}.carregador_tickets ct2 ON ct2.tickets_id = t2.glpi_id
                     WHERE ct2.items_id = c.id 
                       AND t2.status IN ('FECHADO', 'SOLUCIONADO')),
                    c.date_creation
                )))/3600)*3600)/60) || 'm'
            ELSE NULL
        END as tempo_disponivel
    FROM {schema}.carregadores c
    LEFT JOIN LATERAL (
        SELECT t.*, ct.items_id
        FROM {schema}.carregador_tickets ct
        JOIN {schema}.tickets t ON t.glpi_id = ct.tickets_id
        WHERE ct.items_id = c.id
          AND t.status NOT IN ('FECHADO', 'SOLUCIONADO')
          AND t.is_deleted = false
        ORDER BY t.criado_em DESC
        LIMIT 1
    ) t ON true
    WHERE c.is_deleted = 0
    ORDER BY c.name
"""

# ENDPOINT DISABLED: Performance bottleneck with nested subqueries
# Use /sis/carregadores/kanban instead for optimized performance
# @router.get("/sis/carregadores/")
# async def list_carregadores():
#     """
#     Lista todos os carregadores com status atual.
#     
#     Status calculation:
#     - 'ocupado': Tem ticket em andamento (status != FECHADO/SOLUCIONADO)
#     - 'disponivel': Sem tickets ou todos fechados
#     
#     Returns:
#         Lista com: id, nome, localizacao, status, ticket_id, tempo_atribuido, tempo_disponivel
#     """
#     context = "sis"
#     db = get_db_manager(context)
#     
#     with db.get_session() as session:
#         query = text(QUERY_LIST_CARREGADORES.format(schema=context))
#         result = session.execute(query)
#         return [
#             {
#                 "id": row[0],
#                 "nome": row[1],
#                 "localizacao": row[2],
#                 "status": row[3],
#                 "ticket_id": row[4],
#                 "ticket_titulo": row[5][:50] + '...' if row[5] and len(row[5]) > 50 else row[5],
#                 "tempo_atribuido": row[6],
#                 "tempo_disponivel": row[7]
#             }
#             for row in result
#         ]

@router.get("/sis/carregadores/ranking")
async def carregadores_ranking(
    inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    date_field: str = Query('date_creation', regex='^(date_creation|criado_em)$')
):
    """
    Ranking de carregadores por tickets atribuídos no período.
    
    Args:
        inicio: Data de início do filtro (YYYY-MM-DD)
        fim: Data de fim do filtro (YYYY-MM-DD)
        date_field: Campo de data para filtrar (date_creation ou criado_em)
        
    Returns:
        Lista ordenada por quantidade de tickets atribuídos
    """
    context = "sis"
    db = get_db_manager(context)
    
    # Construir filtro de data
    date_filter = ""
    if inicio:
        date_filter += f" AND t.criado_em >= '{inicio} 00:00:00'"
    if fim:
        date_filter += f" AND t.criado_em <= '{fim} 23:59:59'"
    
    with db.get_session() as session:
        query = text(f"""
            SELECT 
                c.id,
                c.name as nome,
                COUNT(DISTINCT ct.tickets_id) as tickets_atribuidos
            FROM {context}.carregadores c
            JOIN {context}.carregador_tickets ct ON ct.items_id = c.id
            JOIN {context}.tickets t ON t.glpi_id = ct.tickets_id
            WHERE c.is_deleted = 0
              AND t.is_deleted = false
              {date_filter}
            GROUP BY c.id, c.name
            ORDER BY tickets_atribuidos DESC
            LIMIT 20
        """)
        
        result = session.execute(query)
        return [
            {
                "id": row[0],
                "nome": row[1],
                "tickets_atribuidos": row[2]
            }
            for row in result
        ]

@router.get("/sis/carregadores/kanban")
async def get_carregadores_kanban():
    """
    Retorna dados formatados para a visão Kanban:
    - Ocupados: Com ticket ativo, tempo de ocupação e localização.
    - Disponíveis: Sem ticket ativo, tempo ocioso e último ticket.
    """
    context = "sis"
    db = get_db_manager(context)

    with db.get_session() as session:
        # Query para Ocupados
        query_occupied = text(f"""
            SELECT
                c.id,
                c.name,
                t.glpi_id as ticket_id,
                t.titulo as ticket_titulo,
                c.location_name as localizacao,
                FLOOR(EXTRACT(EPOCH FROM (NOW() - t.criado_em))/60) as tempo_minutos
            FROM {context}.carregadores c
            JOIN {context}.carregador_tickets ct ON ct.items_id = c.id
            JOIN {context}.tickets t ON t.glpi_id = ct.tickets_id
            WHERE c.is_deleted = 0
              AND t.status NOT IN ('FECHADO', 'SOLUCIONADO')
              AND t.is_deleted = false
            ORDER BY c.name
        """)

        # Query para Disponíveis
        query_available = text(f"""
            SELECT
                c.id,
                c.name,
                last_t.glpi_id as last_ticket_id,
                last_t.titulo as last_ticket_titulo,
                FLOOR(EXTRACT(EPOCH FROM (NOW() - COALESCE(last_t.solucionado_em, c.date_creation)))/60) as tempo_ocioso_minutos
            FROM {context}.carregadores c
            LEFT JOIN LATERAL (
                SELECT t.*
                FROM {context}.carregador_tickets ct
                JOIN {context}.tickets t ON t.glpi_id = ct.tickets_id
                WHERE ct.items_id = c.id
                  AND t.status IN ('FECHADO', 'SOLUCIONADO')
                ORDER BY t.solucionado_em DESC
                LIMIT 1
            ) last_t ON true
            WHERE c.is_deleted = 0
              AND NOT EXISTS (
                  SELECT 1
                  FROM {context}.carregador_tickets ct_active
                  JOIN {context}.tickets t_active ON t_active.glpi_id = ct_active.tickets_id
                  WHERE ct_active.items_id = c.id
                    AND t_active.status NOT IN ('FECHADO', 'SOLUCIONADO')
                    AND t_active.is_deleted = false
              )
            ORDER BY c.name
        """)

        occupied_result = session.execute(query_occupied).fetchall()
        available_result = session.execute(query_available).fetchall()

        return {
            "ocupados": [
                {
                    "id": row[0],
                    "nome": row[1],
                    "ticket": {
                        "id": row[2],
                        "titulo": row[3],
                        "localizacao": row[4]
                    },
                    "tempo_min": row[5]
                } for row in occupied_result
            ],
            "disponiveis": [
                {
                    "id": row[0],
                    "nome": row[1],
                    "ultimo_ticket": {
                        "id": row[2],
                        "titulo": row[3]
                    } if row[2] else None,
                    "tempo_min": row[4]
                } for row in available_result
            ]
        }
