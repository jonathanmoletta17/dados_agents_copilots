from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from datetime import datetime, timezone

from src.db.postgres_manager import get_db_manager
from src.db.models import Carregador, CarregadorTicket, Ticket

router = APIRouter(prefix="/sis/carregadores", tags=["Carregadores"])

def calculate_time_minutes(dt: datetime) -> int:
    """Calculate minutes since given datetime"""
    if not dt:
        return 0
    # Ensure dt is aware (Postgres returns aware)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
        
    now = datetime.now(timezone.utc)
    delta = now - dt
    return int(delta.total_seconds() / 60)

def format_time(minutes: int) -> str:
    """Format minutes as human readable time"""
    if minutes < 60:
        return f"{minutes}min"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h{mins}min"

@router.get("/", response_model=List[dict])
def get_carregadores():
    """
    Retorna lista de carregadores com status atual e tempo.
    """
    db_manager = get_db_manager('sis')
    with db_manager.get_session() as session:
        # Fetch all Carregadores
        carregadores = session.query(Carregador).filter(Carregador.is_deleted == 0).all()
        
        # Fetch active tickets linked to Carregadores with date info
        active_links = session.query(CarregadorTicket, Ticket).join(
            Ticket, CarregadorTicket.tickets_id == Ticket.glpi_id
        ).filter(
            Ticket.status.notin_(['SOLUCIONADO', 'FECHADO']),
            Ticket.is_deleted == False
        ).all()
        
        # Map active links by Carregador ID
        active_map = {}
        for link, ticket in active_links:
            active_map[link.items_id] = ticket
            
        result = []
        for c in carregadores:
            ticket = active_map.get(c.id)
            status = 'ocupado' if ticket else 'disponivel'
            
            # Calculate time based on status
            if ticket and ticket.criado_em:
                # Occupied: time since ticket creation
                time_minutes = calculate_time_minutes(ticket.criado_em)
                tempo_text = format_time(time_minutes)
            else:
                # Available: use last modification date
                time_minutes = calculate_time_minutes(c.date_mod) if c.date_mod else 0
                tempo_text = format_time(time_minutes)
            
            item = {
                "id": c.id,
                "nome": c.name,
                "status": status,
                "localizacao": c.location_name,
                "ticket_id": ticket.glpi_id if ticket else None,
                "tempo_atribuido": tempo_text if status == 'ocupado' else "0min",
                "tempo_disponivel": tempo_text if status == 'disponivel' else "0min",
                "ref_date": datetime.now().isoformat(),
                "tempo_ocupado_min_hoje": time_minutes if status == 'ocupado' else 0,
                "tempo_disponivel_min_hoje": time_minutes if status == 'disponivel' else 0,
                "expediente_status": "aberto"
            }
            result.append(item)
            
        return result

@router.get("/ranking", response_model=List[dict])
def get_carregadores_ranking(inicio: Optional[str] = None, fim: Optional[str] = None):
    """
    Retorna ranking de uso dos carregadores (últimos 30 dias por padrão).
    """
    db_manager = get_db_manager('sis')
    with db_manager.get_session() as session:
        # Base query: count tickets per carregador
        query = session.query(
            Carregador.id,
            Carregador.name,
            func.count(CarregadorTicket.tickets_id).label('tickets_count')
        ).outerjoin(
            CarregadorTicket, Carregador.id == CarregadorTicket.items_id
        ).filter(
            Carregador.is_deleted == 0
        ).group_by(
            Carregador.id, Carregador.name
        ).order_by(
            desc('tickets_count')
        )
        
        results = query.all()
        
        return [
            {
                "id": r.id,
                "nome": r.name,
                "tickets_atribuidos": r.tickets_count
            }
            for r in results
        ]
