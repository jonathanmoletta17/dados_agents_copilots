#!/usr/bin/env python3
"""
Realtime Sync Worker - Sincronização contínua a cada 15 segundos.
Integrado com o GLPIClient existente.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config import config
from src.db.models import Base, Ticket, SyncMeta, SyncHistory, SyncError, Carregador, CarregadorTicket
from src.glpi_client.client import GLPIClient
from src.db.postgres_manager import get_db_manager
from src.etl.transformer import DataTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeSyncWorker:
    """
    Worker de sincronização em tempo real.
    - Sincroniza a cada 15 segundos
    - Detecta mudanças via hash MD5
    - Suporta múltiplos contextos (DTIC, SIS)
    """
    
    def __init__(self, poll_interval: int = None):
        """Args: poll_interval: Intervalo em segundos (padrão: 15)"""
        self.poll_interval = poll_interval or config.SYNC_INTERVAL
        self.contexts = []
        self.running = False
        self.transformer = DataTransformer()
        self.clients = {}
        self.db_managers = {}
        
        # Inicializar clientes e managers para contextos com tokens
        for context in ['dtic', 'sis']:
            user_token = config.get_user_token(context)
            if user_token:
                try:
                    self.clients[context] = GLPIClient(
                        config.get_base_url(context),
                        config.get_app_token(context),
                        user_token
                    )
                    self.db_managers[context] = get_db_manager(context)
                    self.contexts.append(context)
                    logger.info(f"✅ Worker inicializado para contexto: {context}")
                except Exception as e:
                    logger.error(f"❌ Erro ao inicializar {context}: {e}")
    
    async def startup_consistency_check(self):
        """
        Validação de consistência ao iniciar.
        - Compara contagem local vs GLPI
        - Decide entre sync completo ou incremental
        """
        logger.info("🔍 Executando validação de consistência no startup...")
        
        for context in self.contexts:
            try:
                db_manager = self.db_managers[context]
                local_count = db_manager.count_tickets({'is_deleted': False})
                
                # Configuração de lookback
                lookback_days = config.SYNC_FULL_DAYS_LOOKBACK
                logger.info(f"📊 {context.upper()}: Local={local_count} (Lookback configurado: {lookback_days} dias)")
                
                # Se banco vazio, fazer sync completo
                if local_count == 0:
                    logger.info(f"🔄 {context}: Banco vazio - executando SYNC COMPLETO ({lookback_days} dias)")
                    await self.full_sync(context)
                else:
                    logger.info(f"⚡ {context}: Executando SYNC INCREMENTAL")
                    await self.incremental_sync(context)
                
            except Exception as e:
                logger.error(f"❌ Erro na validação de {context}: {e}")
    
    async def incremental_sync(self, context: str, since: datetime = None):
        """Sincronização incremental usando GLPIClient existente."""
        start_time = datetime.now()
        stats = {'novos': 0, 'atualizados': 0, 'sem_mudanca': 0, 'erros': 0}
        
        try:
            client = self.clients[context]
            db_manager = self.db_managers[context]
            
            # Obter último timestamp de sync
            if since is None:
                last_sync = db_manager.get_sync_meta('last_sync_time')
                since = datetime.fromisoformat(last_sync) if last_sync else datetime.now() - timedelta(hours=1)
            
            # Iniciar sessão GLPI
            with client:
                # Buscar tickets incrementais (usa o método existente do client)
                ticket_batches = client.get_tickets_incremental(since, limit=100)
                
                total_tickets = 0
                for batch in ticket_batches:
                    for enriched_ticket in batch:
                        try:
                            # O client já retorna tickets enriquecidos
                            # Precisamos transformar para formato do banco
                            ticket_data = self._transform_enriched_ticket(enriched_ticket)
                            
                            # Verificar se existe localmente
                            existing = db_manager.get_ticket_by_glpi_id(ticket_data['glpi_id'])
                            
                            if not existing:
                                db_manager.upsert_ticket(ticket_data)
                                stats['novos'] += 1
                            elif existing.ticket_hash != ticket_data['ticket_hash']:
                                db_manager.upsert_ticket(ticket_data)
                                stats['atualizados'] += 1
                            else:
                                stats['sem_mudanca'] += 1
                            
                            total_tickets += 1
                        
                        except Exception as e:
                            logger.error(f"❌ Erro ao processar ticket: {e}")
                            stats['erros'] += 1
                
                # Atualizar last_sync_time
                db_manager.set_sync_meta('last_sync_time', datetime.now().isoformat())
                
                # Registrar no histórico
                duration = (datetime.now() - start_time).total_seconds()
                db_manager.log_sync_history({
                    'tipo_sync': 'INCREMENTAL',
                    'tickets_novos': stats['novos'],
                    'tickets_atualizados': stats['atualizados'],
                    'tickets_sem_mudanca': stats['sem_mudanca'],
                    'tickets_total': total_tickets,
                    'erros': stats['erros'],
                    'duracao_segundos': duration,
                    'iniciado_em': start_time,
                    'finalizado_em': datetime.now(),
                    'sucesso': True
                })
                
                logger.info(
                    f"✅ {context}: Sync completo - "
                    f"Novos: {stats['novos']}, "
                    f"Atualizados: {stats['atualizados']}, "
                    f"Sem mudança: {stats['sem_mudanca']}, "
                    f"Erros: {stats['erros']}"
                )
        
        except Exception as e:
            logger.error(f"❌ Erro no sync incremental de {context}: {e}")
            raise
    
    async def full_sync(self, context: str):
        """Sincronização completa (últimos N dias)."""
        logger.info(f"🔄 Iniciando sync COMPLETO para {context}...")
        since = datetime.now() - timedelta(days=config.SYNC_FULL_DAYS_LOOKBACK)
        await self.incremental_sync(context, since)
    
    def _transform_enriched_ticket(self, enriched: Dict) -> Dict:
        """
        Transforma ticket enriquecido do GLPIClient para formato do banco.
        O GLPIClient retorna formato diferente, precisamos mapear.
        """
        # Mapear do formato enriquecido do cliente para nosso modelo
        grupo_text = enriched.get('GRUPO', '')
        
        ticket_data = {
            'glpi_id': enriched.get('ID'),
            'titulo': enriched.get('TITULO', ''),
            'descricao_md': enriched.get('DESCRICAO', ''),
            'descricao': enriched.get('DESCRICAO', ''),  # Mesmo conteúdo
            'status': self._map_status(enriched.get('STATUS', '')),
            'status_id': None,  # Cliente não retorna ID, só texto
            'prioridade': 'MEDIA',  # Cliente não retorna prioridade
            'categoria': enriched.get('CATEGORIA', ''),
            'entidade': enriched.get('ENTIDADE', ''),
            'tecnico': enriched.get('TECNICO', ''),
            'grupo': grupo_text,
            'grupo_nivel': self._extract_nivel_from_grupo(grupo_text),  # NOVO: Extrai nível automaticamente
            'requerente': enriched.get('REQUERENTE', ''),
            'criado_em': self._parse_datetime(enriched.get('DATA_CRIACAO')),
            'atualizado_em': self._parse_datetime(enriched.get('DATA_MODIFICACAO')),
            'solucionado_em': self._parse_datetime(enriched.get('DATA_SOLUCAO')),
            'fechado_em': self._parse_datetime(enriched.get('DATA_FECHAMENTO')),
            'url': enriched.get('URL', ''),
            'is_deleted': False,
            'sincronizado_em': datetime.utcnow(),
            'versao': 1
        }
        
        # Calcular hash
        ticket_data['ticket_hash'] = self.transformer.calculate_ticket_hash(ticket_data)
        
        return ticket_data
    
    def _extract_nivel_from_grupo(self, grupo_text: str) -> Optional[str]:
        """
        Extrai nível de suporte (N1-N4) do campo grupo.
        O campo grupo contém múltiplos grupos separados por quebra de linha.
        Exemplo: "CC-SE-SUBADM-DTIC\nN2\nN3"
        
        Retorna o nível de maior prioridade (N1 > N2 > N3 > N4).
        """
        if not grupo_text:
            return None
        
        # Divide por quebra de linha para obter lista de grupos
        grupos = [g.strip() for g in grupo_text.split('\n') if g.strip()]
        
        # Prioridade: N1 > N2 > N3 > N4
        # Se ticket tem múltiplos níveis, retorna o de maior prioridade
        for nivel in ['N1', 'N2', 'N3', 'N4']:
            if nivel in grupos:
                return nivel
        
        return None
    
    def _map_status(self, status_text: str) -> str:
        """Mapeia status em português para formato padrão."""
        mapping = {
            'Novo': 'NOVO',
            'Em andamento (atribuído)': 'ATRIBUIDO',
            'Em andamento (planejado)': 'PLANEJADO',
            'Pendente': 'PENDENTE',
            'Solucionado': 'SOLUCIONADO',
            'Fechado': 'FECHADO'
        }
        return mapping.get(status_text, 'NOVO')
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Converte string para datetime."""
        if not date_str or date_str == 'N/A':
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None
    
    async def sync_carregadores(self, context: str):
        """Sincroniza Carregadores e seus links com Tickets."""
        if context != 'sis':
            return

        try:
            logger.info(f"🔄 {context}: Iniciando sync de carregadores...")
            client = self.clients[context]
            db_manager = self.db_managers[context]
            
            # 1. Sync Carregadores
            # Fetch all Carregadores (assuming < 1000)
            carregadores = client.make_request("PluginGenericobjectCarregador", {"range": "0-1000", "expand_dropdowns": "true"})
            logger.info(f"📊 {context}: Encontrados {len(carregadores)} carregadores no GLPI.")
            
            with db_manager.get_session() as session:
                for c in carregadores:
                    loc_val = c.get('locations_id', 0)
                    loc_id = loc_val if isinstance(loc_val, int) else 0
                    loc_name = str(loc_val) if not isinstance(loc_val, int) else ''
                    
                    user_val = c.get('users_id', 0)
                    user_id = user_val if isinstance(user_val, int) else 0
                    user_name = str(user_val) if not isinstance(user_val, int) else ''
                    
                    carregador = Carregador(
                        id=c.get('id'),
                        name=c.get('name'),
                        locations_id=loc_id,
                        location_name=loc_name,
                        users_id=user_id,
                        user_name=user_name,
                        is_deleted=c.get('is_deleted', 0),
                        date_mod=self._parse_datetime(c.get('date_mod')),
                        date_creation=self._parse_datetime(c.get('date_creation')),
                        sincronizado_em=datetime.utcnow()
                    )
                    session.merge(carregador)
                session.commit() # Commit carregadores first
            
            # 2. Sync Links
            # Search Tickets with itemtype = PluginGenericobjectCarregador
            params = {
                "criteria[0][field]": 131,
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "PluginGenericobjectCarregador",
                "forcedisplay[0]": 13, # Items ID
                "forcedisplay[1]": 131, # Item Type
                "range": "0-1000"
            }
            
            tickets_data = client.make_request("search/Ticket", params)
            tickets = tickets_data.get('data', [])
            logger.info(f"🔗 {context}: Encontrados {len(tickets)} tickets vinculados a carregadores.")
            
            with db_manager.get_session() as session:
                # Clear existing links
                deleted = session.query(CarregadorTicket).delete()
                logger.info(f"🗑️ {context}: Removidos {deleted} vínculos antigos.")
                
                links_count = 0
                for t in tickets:
                    tid = t.get('2') or t.get(2)
                    items_ids = t.get('13') or t.get(13)
                    item_types = t.get('131') or t.get(131)
                    
                    if items_ids and item_types:
                        if not isinstance(items_ids, list): items_ids = [items_ids]
                        if not isinstance(item_types, list): item_types = [item_types]
                        
                        for i, item_id in enumerate(items_ids):
                            if i < len(item_types) and item_types[i] == 'PluginGenericobjectCarregador':
                                link = CarregadorTicket(
                                    tickets_id=int(tid),
                                    items_id=int(item_id),
                                    itemtype='PluginGenericobjectCarregador',
                                    sincronizado_em=datetime.utcnow()
                                )
                                session.add(link)
                                links_count += 1
                
                session.commit()
                logger.info(f"✅ {context}: Inseridos {links_count} novos vínculos.")
            
            logger.info(f"✅ {context}: Carregadores sincronizados com sucesso.")

        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar carregadores: {e}")

    async def run(self):
        """Loop principal do worker."""
        if not self.clients:
            logger.error("❌ Nenhum cliente configurado. Verifique tokens no .env")
            return
        
        self.running = True
        logger.info(f"🚀 Worker iniciado. Intervalo: {self.poll_interval}s")
        
        # Validação inicial ao startup
        await self.startup_consistency_check()
        
        # Loop de sincronização contínua
        while self.running:
            try:
                for context in self.contexts:
                    await self.incremental_sync(context)
                    await self.sync_carregadores(context)
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                logger.info("⏸️ Interrupção recebida.")
                self.stop()
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                await asyncio.sleep(5)  # Backoff em caso de erro
    
    def stop(self):
        """Para o worker gracefully."""
        logger.info("🛑 Parando worker...")
        self.running = False
        
        # Fechar conexões
        for db_manager in self.db_managers.values():
            db_manager.close()


async def main():
    """Função principal para rodar o worker standalone."""
    worker = RealtimeSyncWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
