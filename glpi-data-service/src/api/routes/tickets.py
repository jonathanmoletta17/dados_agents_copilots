from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from src.db.postgres_manager import get_db_manager

router = APIRouter()

@router.get("/{context}/tickets")
async def list_tickets(
    context: str,
    pagina: int = 1,
    limite: int = 50,
    status: Optional[str] = None,
    tecnico: Optional[str] = None,
    categoria: Optional[str] = None,
    prioridade: Optional[str] = None,
    requerente: Optional[str] = None  # NOVO: filtro por requerente
):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
    
    db = get_db_manager(context)
    filters = {"is_deleted": False}
    if status: filters["status"] = status
    if tecnico: filters["tecnico"] = tecnico
    if categoria: filters["categoria"] = categoria
    if prioridade: filters["prioridade"] = prioridade
    if requerente: filters["requerente"] = requerente  # NOVO: aplicar filtro
    
    offset = (pagina - 1) * limite
    tickets = db.list_tickets(filters, limit=limite, offset=offset)
    total = db.count_tickets(filters)
    
    return {
        "contexto": context,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": (total + limite - 1) // limite,
        "tickets": [t.to_dict() for t in tickets]
    }

@router.get("/{context}/tickets/{glpi_id}")
async def get_ticket(context: str, glpi_id: int):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    ticket = db.get_ticket_by_glpi_id(glpi_id)
    if not ticket:
        raise HTTPException(404, "Ticket não encontrado")
        
    return ticket.to_dict()

@router.get("/{context}/meus-chamados/{username}")
async def get_meus_chamados(context: str, username: str):
    """Retorna tickets do usuário especificado (para mobile app)"""
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
    
    db = get_db_manager(context)
    # Filtrar por requerente
    filters = {"is_deleted": False, "requerente": username}
    
    tickets = db.list_tickets(filters, limit=100, offset=0)
    
    # Formatar para compatibilidade com TicketSummary.fromJson() do mobile
    tickets_formatted = []
    for t in tickets:
        t_dict = t.to_dict()
        tickets_formatted.append({
            "id": t_dict.get("id"),
            "glpi_id": t_dict.get("glpi_id"),
            "titulo": t_dict.get("titulo", ""),
            "status": t_dict.get("status", "Desconhecido"),
            "prioridade": t_dict.get("prioridade", "Média"),
            "criado_em": t_dict.get("data_criacao"),
            "atualizado_em": t_dict.get("data_modificacao"),
            "categoria": t_dict.get("categoria")
        })
    
    return {
        "tickets": tickets_formatted,
        "total": len(tickets_formatted)
    }
