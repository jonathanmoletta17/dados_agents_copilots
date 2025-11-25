#!/usr/bin/env python3
"""
Script de Reconciliação Manual para Tickets SIS
Força atualização de tickets específicos do GLPI para PostgreSQL
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'glpi-data-service', 'src'))

from src.config import config
from src.glpi_client.client import GLPIClient
from src.db.postgres_manager import get_db_manager
from src.etl.transformer import DataTransformer
from datetime import datetime

def reconcile_tickets(context: str, ticket_ids: list):
    """
    Força reconciliação de tickets específicos.
    
    Args:
        context: 'sis' ou 'dtic'
        ticket_ids: Lista de IDs de tickets para reconciliar
    """
    print(f"\n🔄 Iniciando reconciliação para {context}")
    print(f"📋 Tickets a reconciliar: {ticket_ids}")
    
    # Inicializar cliente e database
    db = get_db_manager(context)
    transformer = DataTransformer()
    
    with GLPIClient(
        base_url=config.get_base_url(context),
        app_token=config.get_app_token(context),
        user_token=config.get_user_token(context)
    ) as client:
        for ticket_id in ticket_ids:
            try:
                print(f"\n🎫 Processando Ticket {ticket_id}...")
                
                # Buscar do GLPI
                raw_ticket = client.get_ticket_details(ticket_id)
                
                # Status mapping
                status_map = {
                    1: 'Novo', 2: 'Em andamento (atribuído)', 3: 'Em andamento (planejado)',
                    4: 'Pendente', 5: 'Solucionado', 6: 'Fechado'
                }
                status_id = raw_ticket.get('status', 1)
                status_text = status_map.get(status_id, 'Novo')
                
                is_deleted = bool(raw_ticket.get('is_deleted', 0))
                
                print(f"   Status GLPI: {status_text} (ID: {status_id})")
                print(f"   is_deleted: {is_deleted}")
                
                # Buscar atores
                requester = 'N/A'
                technician = 'N/A'
                try:
                    actors = client.make_request(f"Ticket/{ticket_id}/Ticket_User")
                    for a in actors:
                        if a.get('type') == 1:  # Requester
                            uid = str(a.get('users_id'))
                            requester = client.users_cache.get(uid, f"User {uid}")
                        elif a.get('type') == 2:  # Technician
                            uid = str(a.get('users_id'))
                            technician = client.users_cache.get(uid, f"User {uid}")
                except:
                    pass
                
                # Mapear status
                status_mapping = {
                    'Novo': 'NOVO',
                    'Em andamento (atribuído)': 'ATRIBUIDO',
                    'Em andamento (planejado)': 'PLANEJADO',
                    'Pendente': 'PENDENTE',
                    'Solucionado': 'SOLUCIONADO',
                    'Fechado': 'FECHADO'
                }
                
                # Criar ticket_data
                ticket_data = {
                    'glpi_id': ticket_id,
                    'titulo': raw_ticket.get('name', ''),
                    'descricao': raw_ticket.get('content', ''),
                    'descricao_md': raw_ticket.get('content', ''),
                    'status': status_mapping.get(status_text, 'NOVO'),
                    'requerente': requester,
                    'tecnico': technician,
                    'criado_em': datetime.strptime(raw_ticket['date'], '%Y-%m-%d %H:%M:%S') if 'date' in raw_ticket else None,
                    'atualizado_em': datetime.strptime(raw_ticket['date_mod'], '%Y-%m-%d %H:%M:%S') if 'date_mod' in raw_ticket else None,
                    'solucionado_em': datetime.strptime(raw_ticket['solvedate'], '%Y-%m-%d %H:%M:%S') if raw_ticket.get('solvedate') else None,
                    'fechado_em': datetime.strptime(raw_ticket['closedate'], '%Y-%m-%d %H:%M:%S') if raw_ticket.get('closedate') else None,
                    'is_deleted': is_deleted,
                    'sincronizado_em': datetime.utcnow()
                }
                
                # Calcular hash
                ticket_data['ticket_hash'] = transformer.calculate_ticket_hash(ticket_data)
                
                # Upsert no banco
                db.upsert_ticket(ticket_data)
                
                print(f"   ✅ Ticket {ticket_id} reconciliado com sucesso!")
                print(f"   Status no banco agora: {ticket_data['status']}")
                print(f"   is_deleted: {ticket_data['is_deleted']}")
                
            except Exception as e:
                print(f"   ❌ Erro ao reconciliar ticket {ticket_id}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    # Reconciliar tickets problemáticos da SIS
    reconcile_tickets('sis', [5052, 5056, 5064])
    
    print("\n✅ Reconciliação concluída!")
