#!/usr/bin/env python3
"""
Continuous Sync Worker - Polls GLPI every 15s and detects changes
"""
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Set, List, Optional
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config import config
from src.glpi_client.client import GLPIClient
from src.db.database_factory import DatabaseFactory
from src.utils.sync_logger import sync_logger


class ContinuousSyncWorker:
    """
    Worker que faz polling contínuo no GLPI a cada intervalo configurado.
    Detecta mudanças usando hash de tickets e notifica via event queue.
    """
    
    def __init__(self, poll_interval: int = 15):
        """
        Args:
            poll_interval: Intervalo em segundos entre polls (default: 15s)
        """
        self.poll_interval = poll_interval
        self.event_queue = asyncio.Queue()
        self.last_hashes: Dict[str, Dict[int, str]] = {}  # context -> ticket_id -> hash
        self.running = False
        
        sync_logger.info(f"🔄 Worker inicializado com intervalo de {poll_interval}s")
    
    def _calculate_ticket_hash(self, ticket: Dict) -> str:
        """Calcula hash MD5 de um ticket para detectar mudanças."""
        # Campos relevantes para detecção de mudanças
        key_fields = {
            'id': ticket.get('ID'),
            'titulo': ticket.get('TITULO'),
            'status': ticket.get('STATUS'),
            'tecnico': ticket.get('TECNICO'),
            'grupo': ticket.get('GRUPO'),
            'updated': ticket.get('DATA_MODIFICACAO')
        }
        
        data_str = json.dumps(key_fields, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def check_context_changes(self, context: str, full_sync: bool = False) -> Optional[Dict]:
        """
        Verifica mudanças em um contexto específico.
        
        Returns:
            Dict com informações de mudanças, ou None se não houver
        """
        try:
            sync_logger.debug(f"🔍 Verificando mudanças em {context} (full_sync={full_sync})...")
            
            creds = config.get_context_credentials(context)
            
            with GLPIClient(creds['url'], creds['app_token'], creds['user_token']) as client:
                # Determina desde quando buscar tickets
                db = DatabaseFactory.get_database(context)
                last_sync = db.get_last_sync_time()
                
                if full_sync:
                    # Sincronização completa: busca desde 2023-01-01
                    since = datetime(2023, 1, 1)
                    sync_logger.info(f"📅 Sincronização COMPLETA solicitada desde {since}")
                elif last_sync:
                    # Sincronização incremental desde último sync
                    since = datetime.fromisoformat(last_sync)
                    sync_logger.info(f"📅 Sincronização incremental desde {last_sync}")
                else:
                    # Primeira execução: busca últimas 24 horas
                    since = datetime.now() - timedelta(hours=24)
                    sync_logger.info(f"🆕 Primeira sincronização! Buscando últimas 24 horas desde {since.isoformat()}")
                
                changed_tickets = []
                new_hashes = {}
                
                # Get tickets via generator
                for batch in client.get_tickets_incremental(since, limit=50):
                    for ticket in batch:
                        ticket_id = ticket['ID']
                        ticket_hash = self._calculate_ticket_hash(ticket)
                        new_hashes[ticket_id] = ticket_hash
                        
                        # Verifica se é novo ou mudou
                        old_hash = self.last_hashes.get(context, {}).get(ticket_id)
                        
                        if old_hash is None:
                            sync_logger.info(f"✨ Novo ticket detectado: {context}#{ticket_id}")
                            changed_tickets.append({
                                'id': ticket_id,
                                'type': 'new',
                                'ticket': ticket
                            })
                        elif old_hash != ticket_hash:
                            sync_logger.info(f"🔄 Ticket atualizado: {context}#{ticket_id}")
                            changed_tickets.append({
                                'id': ticket_id,
                                'type': 'updated',
                                'ticket': ticket
                            })
                
                # Atualiza cache de hashes
                if context not in self.last_hashes:
                    self.last_hashes[context] = {}
                self.last_hashes[context].update(new_hashes)
                
                # Atualiza timestamp do último sync no banco
                if changed_tickets or not last_sync:
                    db.update_last_sync_time(datetime.now().isoformat())
                
                if changed_tickets:
                    return {
                        'context': context,
                        'timestamp': datetime.now().isoformat(),
                        'changes': changed_tickets,
                        'count': len(changed_tickets)
                    }
                
                return None
                
        except Exception as e:
            sync_logger.error(f"❌ Erro ao verificar {context}: {e}")
            return None
    
    async def process_changes(self, change_event: Dict):
        """Processa mudanças detectadas e atualiza o banco."""
        context = change_event['context']
        changes = change_event['changes']
        
        sync_logger.info(f"💾 Processando {len(changes)} mudanças em {context}")
        
        db = DatabaseFactory.get_database(context)
        
        for change in changes:
            ticket = change['ticket']
            
            # Mapear campos para formato do banco
            ticket_data = {
                'glpi_id': ticket['ID'],
                'titulo': ticket['TITULO'],
                'descricao': ticket.get('DESCRICAO', ''),
                'descricao_md': ticket.get('DESCRICAO', ''),  # Já vem em MD
                'status': ticket['STATUS'],
                'status_text': ticket['STATUS'],
                'prioridade': ticket.get('PRIORIDADE', 'N/A'),
                'org': self._derive_org(ticket),
                'categoria': ticket.get('CATEGORIA', ''),
                'entidade': ticket.get('ENTIDADE', ''),
                'tecnico': ticket.get('TECNICO', ''),
                'grupo': ticket.get('GRUPO', ''),
                'requerente': ticket.get('REQUERENTE', ''),
                'motivo_pendencia': ticket.get('MOTIVO_PENDENCIA', ''),
                'created_at': ticket.get('DATA_CRIACAO'),
                'updated_at': ticket.get('DATA_MODIFICACAO'),
                'solved_at': ticket.get('DATA_SOLUCAO'),
                'closed_at': ticket.get('DATA_FECHAMENTO'),
                'url': ticket.get('URL', ''),
                'is_deleted': ticket.get('IS_DELETED', 0)
            }
            
            success = db.upsert_ticket(ticket_data)
            
            if not success:
                sync_logger.error(f"❌ Falha ao salvar ticket {ticket['ID']}")
    
    def _derive_org(self, ticket: Dict) -> str:
        """Deriva organização baseada em keywords."""
        grupo = ticket.get('GRUPO', '').upper()
        categoria = ticket.get('CATEGORIA', '').upper()
        
        if 'DTIC' in grupo or 'N3' in grupo or 'N2' in grupo or 'N1' in grupo:
            return 'DTIC'
        elif 'MANUT' in grupo or 'CONSERV' in grupo:
            return 'MANUTENCAO'
        elif 'DTIC' in categoria:
            return 'DTIC'
        else:
            return 'OUTROS'
    
    async def run(self):
        """Loop principal do worker."""
        self.running = True
        sync_logger.info(f"🚀 Worker iniciado (polling a cada {self.poll_interval}s)")
        
        retry_count = 0
        max_retries = 5
        
        while self.running:
            try:
                contexts = config.contexts
                
                if not contexts:
                    sync_logger.warning("⚠️ Nenhum contexto configurado")
                    await asyncio.sleep(60)
                    continue
                
                # Verifica mudanças em todos os contextos
                for context in contexts:
                    change_event = await self.check_context_changes(context)
                    
                    if change_event:
                        # Processa mudanças
                        await self.process_changes(change_event)
                        
                        # Envia evento para fila de notificações
                        await self.event_queue.put(change_event)
                
                # Reset retry counter em sucesso
                retry_count = 0
                
                # Aguarda próximo ciclo
                await asyncio.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                sync_logger.info("⏹️ Worker interrompido pelo usuário")
                self.running = False
                break
                
            except Exception as e:
                retry_count += 1
                sync_logger.error(f"❌ Erro no worker (tentativa {retry_count}/{max_retries}): {e}")
                
                if retry_count >= max_retries:
                    sync_logger.error("🚨 Máximo de retries atingido. Aguardando 5 minutos...")
                    await asyncio.sleep(300)
                    retry_count = 0
                else:
                    # Exponential backoff
                    backoff = min(60, 2 ** retry_count)
                    sync_logger.info(f"⏳ Aguardando {backoff}s antes de retry...")
                    await asyncio.sleep(backoff)
        
        sync_logger.info("👋 Worker finalizado")
    
    def stop(self):
        """Para o worker gracefully."""
        sync_logger.info("🛑 Parando worker...")
        self.running = False


# Singleton global
worker_instance: Optional[ContinuousSyncWorker] = None


def get_worker() -> ContinuousSyncWorker:
    """Retorna instância singleton do worker."""
    global worker_instance
    if worker_instance is None:
        worker_instance = ContinuousSyncWorker(poll_interval=15)
    return worker_instance


async def main():
    """Função principal para rodar o worker standalone."""
    worker = get_worker()
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
