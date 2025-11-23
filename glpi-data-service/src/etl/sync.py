#!/usr/bin/env python3
"""
Orquestrador de sincronização GLPI
"""
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from glpi_client.client import GLPIClient
from etl.transformer import DataTransformer
from db.database_factory import DatabaseFactory
from config import config
from utils.sync_logger import sync_logger

class SyncOrchestrator:
    def __init__(self):
        self.transformer = DataTransformer()
        self.batch_size = 50
        self.sync_interval = 300  # 5 minutos
        self.max_sync_duration = 3600  # 1 hora
        
        sync_logger.info(f"🔄 Orquestrador inicializado. Contextos disponíveis: {config.contexts}")
    
    def get_last_sync_time(self, db: 'Database', context: str) -> datetime:
        """
        Retorna o timestamp da última sincronização para o contexto
        """
        last_sync_str = db.get_sync_meta(f'last_sync')
        
        if last_sync_str:
            try:
                return datetime.fromisoformat(last_sync_str)
            except:
                sync_logger.warning(f"⚠️  Data de sincronização inválida para {context}, usando epoch")
                return datetime(1970, 1, 1)
        
        return datetime(1970, 1, 1)  # Epoch se nunca sincronizado
    
    def update_last_sync_time(self, db: 'Database', sync_time: datetime):
        """
        Atualiza timestamp da última sincronização
        """
        db.set_sync_meta('last_sync', sync_time.isoformat())
        db.set_sync_meta('last_sync_status', 'success')
    
    def sync_tickets(self, full_sync: bool = False):
        """
        Sincroniza tickets de todos os contextos configurados
        """
        sync_logger.info(f"🚀 Iniciando sincronização {'COMPLETA' if full_sync else 'INCREMENTAL'}")
        
        for context in config.contexts:
            sync_logger.info(f"📦 Processando contexto: {context}")
            
            try:
                # Obtém Database específico para este contexto
                db = DatabaseFactory.get_database(context)
                
                # Obtém credenciais do contexto
                creds = config.get_context_credentials(context)
                
                # Inicializa cliente GLPI com credenciais do contexto
                with GLPIClient(
                    base_url=creds['url'],
                    app_token=creds['app_token'],
                    user_token=creds['user_token']
                ) as client:
                    
                    # Determina data início da sincronização
                    if full_sync:
                        sync_start = datetime(1970, 1, 1)
                        sync_logger.info(f"📅 Sincronização COMPLETA desde o início")
                    else:
                        sync_start = self.get_last_sync_time(db, context)
                        sync_logger.info(f"📅 Sincronização INCREMENTAL desde: {sync_start.isoformat()}")
                    
                    # Usa iterator para buscar tickets em batches
                    successful = 0
                    errors = 0
                    batch_num = 0
                    
                    sync_logger.info(f"🔄 Iniciando busca de tickets...")
                    
                    try:
                        # O client já retorna tickets ENRIQUECIDOS
                        for batch in client.get_tickets_incremental(sync_start, limit=self.batch_size):
                            batch_num += 1
                            
                            sync_logger.info(f"🔄 Processando lote {batch_num} ({len(batch)} tickets)")
                            
                            s, e = self._process_batch(batch, context, db)
                            successful += s
                            errors += e
                        
                        if batch_num == 0:
                            sync_logger.warning(f"⚠️  Nenhum lote retornado pelo GLPI!")
                    
                    except Exception as e:
                        sync_logger.error(f"❌ Erro durante iteração de tickets: {e}")
                    
                    # Atualiza timestamp de última sincronização
                    sync_end = datetime.now()
                    self.update_last_sync_time(db, sync_end)
                    
                    sync_logger.info(f"✅ {context} finalizado: Sucesso={successful}, Erros={errors}")
                    
            except Exception as e:
                sync_logger.error(f"❌ Erro na sincronização do contexto {context}: {e}")
        
        sync_logger.info(f"✅ Sincronização concluída para todos os contextos!")
    
    def _process_batch(self, tickets: List[Dict], context: str, db: 'Database') -> tuple:
        """
        Processa um lote de tickets enriquecidos
        """
        successful = 0
        errors = 0
        
        for enriched_ticket in tickets:
            try:
                # Transforma ticket
                internal_ticket = self.transformer.transform_ticket(
                    enriched_ticket,
                    context
                )
                
                # Salva no banco
                if db.upsert_ticket(internal_ticket):
                    successful += 1
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                # Registra erro
                db.log_sync_error(
                    enriched_ticket.get('ID', 0),
                    'transform_error',
                    str(e)
                )
        
        return successful, errors
    
    def get_sync_status(self) -> Dict:
        """Retorna status da sincronização"""
        status = {}
        for context in config.contexts:
            db = DatabaseFactory.get_database(context)
            status[context] = {
                'last_sync': db.get_sync_meta('last_sync'),
                'sync_status': db.get_sync_meta('sync_status'),
                'tickets_processed': db.get_sync_meta('tickets_processed'),
                'sync_errors': db.get_sync_meta('sync_errors')
            }
        return status

def main():
    """Função principal para teste"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sincronização de dados do GLPI')
    parser.add_argument('--full', action='store_true', help='Fazer sincronização completa (histórico)')
    args = parser.parse_args()
    
    orchestrator = SyncOrchestrator()
    orchestrator.sync_tickets(full_sync=args.full)
    
    status = orchestrator.get_sync_status()
    print("\n📊 Status da Sincronização:")
    print(status)

if __name__ == '__main__':
    main()