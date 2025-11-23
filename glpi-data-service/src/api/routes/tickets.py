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
    prioridade: Optional[str] = None
):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
    
    db = get_db_manager(context)
    filters = {"is_deleted": False}
    if status: filters["status"] = status
    if tecnico: filters["tecnico"] = tecnico
    if categoria: filters["categoria"] = categoria
    if prioridade: filters["prioridade"] = prioridade
    
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
