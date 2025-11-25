#!/usr/bin/env python3
"""
Cliente GLPI para sincronização incremental
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Iterator
from urllib.parse import urljoin
import os
from dotenv import load_dotenv
from src.utils.sync_logger import sync_logger
from src.utils.text_processor import TextProcessor

# Carrega variáveis de ambiente
class GLPIClient:
    def __init__(self, base_url: str, app_token: str, user_token: str):
        self.base_url = base_url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        
        if not all([self.base_url, self.app_token, self.user_token]):
            raise ValueError("URL, App Token e User Token são obrigatórios para inicializar o cliente GLPI.")
        
        self.session_token = None
        self.session = requests.Session()
        
        # Configurações de retry e timeout
        self.session.timeout = 30
        self.max_retries = 3
        self.retry_delay = 5
        
        # Caches
        self.users_cache = {}
        self.entities_cache = {}
        self.categories_cache = {}
        self.groups_cache = {}
        self.pending_reasons_cache = {}
        
        # Inicia sessão
        self.init_session()
    
    def init_session(self):
        """Inicializa sessão com GLPI"""
        url = f"{self.base_url}/initSession"
        
        headers = {
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}'
        }
        
        sync_logger.info(f"Iniciando sessão GLPI em {self.base_url}")
        
        for attempt in range(self.max_retries):
            try:
                sync_logger.debug(f"Tentativa {attempt + 1} de initSession", extra={'url': url, 'headers': headers})
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                self.session_token = data.get('session_token')
                
                if not self.session_token:
                    raise Exception("Token de sessão não recebido")
                
                sync_logger.info(f"✅ Sessão GLPI iniciada: {self.session_token[:8]}...")
                return
                
            except Exception as e:
                sync_logger.error(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Falha ao iniciar sessão GLPI após {self.max_retries} tentativas")
    
    def close_session(self):
        """Encerra sessão GLPI"""
        if not self.session_token:
            return
        
        url = f"{self.base_url}/killSession"
        headers = {
            'App-Token': self.app_token,
            'Session-Token': self.session_token
        }
        
        try:
            sync_logger.debug("Encerrando sessão", extra={'url': url, 'headers': headers})
            response = self.session.get(url, headers=headers)
            sync_logger.info(f"✅ Sessão GLPI encerrada")
        except Exception as e:
            sync_logger.warning(f"⚠️  Erro ao encerrar sessão: {e}")
        finally:
            self.session_token = None
    
    def make_request(self, endpoint: str, params: Dict = None, method: str = 'GET', json_data: Dict = None) -> Dict:
        """Faz requisição autenticada à API GLPI"""
        if not self.session_token:
            raise Exception("Sessão não iniciada")
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'App-Token': self.app_token,
            'Session-Token': self.session_token,
            'Content-Type': 'application/json'
        }
        
        for attempt in range(self.max_retries):
            try:
                sync_logger.debug(f"Request {method} para {endpoint}", extra={'url': url, 'params': params, 'json': json_data})
                
                if method.upper() == 'GET':
                    response = self.session.get(url, headers=headers, params=params)
                elif method.upper() == 'POST':
                    response = self.session.post(url, headers=headers, params=params, json=json_data)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, headers=headers, params=params, json=json_data)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")

                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:  # Unauthorized
                    sync_logger.warning("🔄 Sessão expirada ou inválida. Renovando sessão...")
                    self.init_session()
                    headers['Session-Token'] = self.session_token
                    continue
                else:
                    sync_logger.error(f"HTTP Error em {endpoint}: {e}", extra={'status': response.status_code, 'response': response.text})
                    raise
            except Exception as e:
                sync_logger.error(f"❌ Tentativa {attempt + 1} falhou em {endpoint}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def update_ticket(self, ticket_id: int, updates: Dict) -> Dict:
        """Atualiza um ticket no GLPI."""
        endpoint = f"Ticket/{ticket_id}"
        # GLPI expects the input to be wrapped in 'input' key usually, or direct fields depending on version.
        # Standard GLPI API v9/v10 usually expects: {"input": {"id": 1, "field": "value"}} for PUT
        
        payload = {"input": updates}
        # Ensure ID is in the input for safety, though URL has it
        payload["input"]["id"] = ticket_id
        
        return self.make_request(endpoint, method='PUT', json_data=payload)

    def create_ticket(self, input_payload: Dict) -> Dict:
        """Cria um ticket no GLPI.
        Espera um dicionário com os campos do Ticket (sem o wrapper), e envia como {"input": {...}}.
        Retorna o JSON da API do GLPI.
        """
        if not isinstance(input_payload, dict):
            raise ValueError("input_payload deve ser um dict")
        payload = {"input": input_payload}
        return self.make_request("Ticket", method='POST', json_data=payload)

    def _get_all_pages(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Helper to fetch all pages from an endpoint."""
        if params is None:
            params = {}
        
        all_items = []
        start = 0
        limit = 1000 # Max range size
        
        while True:
            params['range'] = f"{start}-{start + limit - 1}"
            try:
                items = self.make_request(endpoint, params)
                if not items:
                    break
                all_items.extend(items)
                if len(items) < limit:
                    break
                start += limit
            except Exception as e:
                sync_logger.error(f"Error fetching all pages for {endpoint}: {e}")
                break
                
        return all_items

    def load_caches(self):
        """Preloads metadata caches."""
        sync_logger.info("Loading metadata caches...")
        
        # Users
        users = self._get_all_pages("User")
        for u in users:
            uid = str(u.get('id'))
            name = u.get('realname') or u.get('name') or f"User {uid}"
            if u.get('firstname'):
                name = f"{u.get('firstname')} {u.get('realname') or ''}".strip()
            self.users_cache[uid] = name
            
        # Entities
        entities = self._get_all_pages("Entity")
        for e in entities:
            self.entities_cache[str(e.get('id'))] = e.get('name', 'Unknown Entity')
            
        # Categories - usar completename para obter hierarquia completa
        cats = self._get_all_pages("ITILCategory")
        for c in cats:
            # completename inclui hierarquia: "Manutenção > Elétrica > Instalação"
            # name inclui apenas: "Instalação"
            category_full_path = c.get('completename') or c.get('name', 'Unknown Category')
            self.categories_cache[str(c.get('id'))] = category_full_path
            
        # Groups
        groups = self._get_all_pages("Group")
        for g in groups:
            self.groups_cache[str(g.get('id'))] = g.get('name', 'Unknown Group')
            
        sync_logger.info("Metadata caches loaded.")

    def fetch_pending_reasons_map(self) -> Dict[int, str]:
        """Fetches a map of Ticket ID -> Pending Reason Name using the Search API."""
        sync_logger.info("Fetching pending reasons map...")
        pending_map = {}
        step = 2000
        start = 0
        
        while True:
            params = {
                "forcedisplay[0]": 2,   # ID
                "forcedisplay[1]": 400, # Motivo de pendência
                "range": f"{start}-{start+step}"
            }
            # Use search/Ticket endpoint
            # Note: make_request handles base_url
            try:
                data = self.make_request("search/Ticket", params)
                items = data.get('data', [])
                if not items:
                    break
                    
                for item in items:
                    tid = item.get("2") or item.get(2) # Handle string or int keys
                    reason = item.get("400") or item.get(400)
                    if tid and reason:
                        pending_map[int(tid)] = reason
                
                total = data.get('totalcount', 0)
                if start + step >= total:
                    break
                start += step
            except Exception as e:
                sync_logger.error(f"Error fetching pending reasons: {e}")
                break
            
        return pending_map

    def get_tickets_incremental(self, last_sync: datetime, limit: int = 100) -> Iterator[List[Dict]]:
        """Busca tickets modificados após a última sincronização e enriquece os dados."""
        
        # Ensure caches are loaded
        if not self.users_cache:
            self.load_caches()
            
        # Fetch Pending Reasons Map (refreshing it for sync)
        pending_reasons_map = self.fetch_pending_reasons_map()
        
        params = {
            'range': f'0-{limit-1}',
            'sort': 'date_mod',
            'order': 'DESC'
        }
        
        offset = 0
        total_processed = 0
        stop_fetching = False
        
        sync_logger.info(f"📥 Iniciando busca incremental (DESC) até {last_sync}")
        
        while not stop_fetching:
            try:
                params['range'] = f'{offset}-{offset + limit - 1}'
                
                raw_tickets = self.make_request('Ticket', params)
                
                if not raw_tickets:
                    sync_logger.info(f"✅ Sincronização completa (sem mais tickets). Total processado: {total_processed}")
                    break
                
                # Filter and Enrich tickets
                enriched_tickets = []
                for t in raw_tickets:
                    # Check date_mod
                    date_mod_str = t.get('date_mod')
                    if date_mod_str:
                        try:
                            ticket_date = datetime.strptime(date_mod_str, '%Y-%m-%d %H:%M:%S')
                            # Make ticket_date offset-aware (UTC) if last_sync is aware
                            if last_sync.tzinfo is not None and ticket_date.tzinfo is None:
                                ticket_date = ticket_date.replace(tzinfo=last_sync.tzinfo)
                            elif last_sync.tzinfo is None and ticket_date.tzinfo is not None:
                                # Make last_sync aware if ticket is aware (unlikely here but safe)
                                last_sync = last_sync.replace(tzinfo=ticket_date.tzinfo)
                                
                            if ticket_date <= last_sync:
                                # Found a ticket older than last_sync, stop processing this and future batches
                                stop_fetching = True
                                # We continue to process this ticket if it EQUALS last_sync? 
                                # Usually we want > last_sync.
                                # If ticket_date == last_sync, we might have already processed it, but upsert is safe.
                                # However, if we want strictly new, we stop.
                                # Let's stop if < last_sync. If ==, we include it to be safe (in case of multiple updates in same second).
                                if ticket_date < last_sync:
                                    continue 
                        except ValueError:
                            pass # Ignore parse error, process ticket
                    
                    tid = str(t.get('id'))
                    
                    # Fetch Actors (Requester, Technician)
                    requester = 'N/A'
                    technician = 'N/A'
                    group = 'N/A'
                    
                    try:
                        actors = self.make_request(f"Ticket/{tid}/Ticket_User")
                        for a in actors:
                            uid = str(a.get('users_id'))
                            type_ = a.get('type') # 1=Requester, 2=Technician
                            user_name = self.users_cache.get(uid, f"User {uid}")
                            if type_ == 1:
                                requester = user_name
                            elif type_ == 2:
                                technician = user_name
                    except Exception:
                        pass 
                        
                    try:
                        groups_rel = self.make_request(f"Ticket/{tid}/Group_Ticket")
                        group_names = []
                        for g in groups_rel:
                            gid = str(g.get('groups_id'))
                            group_names.append(self.groups_cache.get(gid, f"Group {gid}"))
                        if group_names:
                            group = "\n".join(group_names)
                    except Exception:
                        pass

                    # Status mapping
                    status_map = {
                        1: 'Novo', 2: 'Em andamento (atribuído)', 3: 'Em andamento (planejado)',
                        4: 'Pendente', 5: 'Solucionado', 6: 'Fechado'
                    }
                    status_id = int(t.get('status', 1))
                    status_text = status_map.get(status_id, f"Status {status_id}")
                    
                    # Markdown conversion
                    content_html = t.get('content', '')
                    content_md = TextProcessor.html_to_markdown(content_html)
                    
                    enriched_tickets.append({
                        'ID': int(tid),
                        'TITULO': t.get('name', ''),
                        'DESCRICAO': content_md,
                        'STATUS': status_text,
                        'CATEGORIA': self.categories_cache.get(str(t.get('itilcategories_id')), 'N/A'),
                        'ENTIDADE': self.entities_cache.get(str(t.get('entities_id')), 'N/A'),
                        'REQUERENTE': requester,
                        'TECNICO': technician,
                        'GRUPO': group,
                        'DATA_CRIACAO': t.get('date'),
                        'DATA_MODIFICACAO': t.get('date_mod'),
                        'DATA_SOLUCAO': t.get('solvedate'),
                        'DATA_FECHAMENTO': t.get('closedate'),
                        'MOTIVO_PENDENCIA': pending_reasons_map.get(int(tid), ''),
                        'IS_DELETED': 0 if t.get('is_deleted') == 0 else 1,
                        'URL': f"{self.base_url.replace('/apirest.php', '')}/front/ticket.form.php?id={tid}"
                    })

                if enriched_tickets:
                    batch_size = len(enriched_tickets)
                    total_processed += batch_size
                    sync_logger.info(f"📦 Lote processado: {batch_size} tickets (total: {total_processed})")
                    yield enriched_tickets
                
                if stop_fetching:
                    sync_logger.info(f"⏹️  Alcançada data limite ({last_sync}). Parando.")
                    break

                if len(raw_tickets) < limit:
                    break
                
                offset += limit
                time.sleep(0.5)
                
            except Exception as e:
                sync_logger.error(f"❌ Erro ao buscar tickets incrementalmente: {e}")
                raise
    
    def get_ticket_details(self, ticket_id: int) -> Dict:
        return self.make_request(f'Ticket/{ticket_id}')
    
    def get_ticket_followups(self, ticket_id: int) -> List[Dict]:
        try:
            return self.make_request(f'Ticket/{ticket_id}/TicketFollowup')
        except:
            return []
    
    def get_ticket_tasks(self, ticket_id: int) -> List[Dict]:
        try:
            return self.make_request(f'Ticket/{ticket_id}/TicketTask')
        except:
            return []
    
    def get_entities(self) -> List[Dict]:
        return self.make_request('Entity')
    
    def get_groups(self) -> List[Dict]:
        return self.make_request('Group')
    
    def get_users(self) -> List[Dict]:
        return self.make_request('User')
    
    def get_itil_categories(self) -> List[Dict]:
        return self.make_request('ITILCategory')
    
    
    # ==================== CARREGADORES METHODS ====================
    
    def get_carregadores(self, is_deleted: int = 0) -> List[Dict]:
        """
        Busca todos os carregadores (PluginGenericobjectCarregador) do GLPI.
        
       Args:
            is_deleted: Filtrar por status de exclusão (0 = ativos, 1 = deletados)
            
        Returns:
            Lista de carregadores com seus dados
        """
        sync_logger.info(f"Buscando carregadores do GLPI (is_deleted={is_deleted})")
        
        try:
            all_carregadores = []
            endpoint = "PluginGenericobjectCarregador"
            start = 0
            step = 100
            
            while True:
                params = {
                    "range": f"{start}-{start + step - 1}",
                    "is_deleted": is_deleted
                }
                
                response = self.make_request(endpoint, params)
                
                # GLPI retorna array direto ou vazio
                if not response:
                    break
                    
                items = response if isinstance(response, list) else []
                if not items:
                    break
                
                all_carregadores.extend(items)
                
                # Se retornou menos que step, não há mais páginas
                if len(items) < step:
                    break
                    
                start += step
            
            sync_logger.info(f"✅ {len(all_carregadores)} carregadores encontrados")
            return all_carregadores
            
        except Exception as e:
            sync_logger.error(f"❌ Erro ao buscar carregadores: {e}")
            return []
    
    def get_ticket_items(self, ticket_id: int) -> List[Dict]:
        """
        Busca items vinculados a um ticket específico.
        
        Args:
            ticket_id: ID do ticket
            
        Returns:
            Lista de items vinculados (cada item tem: id, items_id, itemtype)
        """
        endpoint = f"Ticket/{ticket_id}/Item_Ticket"
        
        try:
            response = self.make_request(endpoint)
            items = response if isinstance(response, list) else []
            return items
            
        except Exception as e:
            sync_logger.debug(f"Nenhum item vinculado ao ticket {ticket_id}: {e}")
            return []
    
    def get_carregadores_by_ticket(self, ticket_id: int) -> List[Dict]:
        """
        Busca carregadores vinculados a um ticket específico.
        
        Args:
            ticket_id: ID do ticket
            
        Returns:
            Lista de carregadores filtrados (apenas itemtype = PluginGenericobjectCarregador)
        """
        items = self.get_ticket_items(ticket_id)
        
        # Filtrar apenas carregadores
        carregadores = [
            item for item in items 
            if item.get('itemtype') == 'PluginGenericobjectCarregador'
        ]
        
        return carregadores
    
    def get_location_name(self, location_id: int) -> Optional[str]:
        """
        Busca nome da localização por ID.
        
        Args:
            location_id: ID da localização
            
        Returns:
            Nome da localização ou None
        """
        if not location_id:
            return None
            
        try:
            endpoint = f"Location/{location_id}"
            response = self.make_request(endpoint)
            return response.get('name') or response.get('completename')
        except Exception as e:
            sync_logger.debug(f"Erro ao buscar localização {location_id}: {e}")
            return None
    
    # ==================== CONTEXT MANAGER ====================
    
    def __enter__(self):
        self.init_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()
