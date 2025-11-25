"""
PostgreSQL Database Manager with Schema Support.
Manages connections to DTIC and SIS schemas separately.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator, Optional
import logging

from src.config import config
from src.db.models import Base, Ticket, SyncMeta, SyncHistory, SyncError

logger = logging.getLogger(__name__)


class PostgreSQLManager:
    """
    Gerenciador de conexões PostgreSQL com suporte a schemas separados.
    """
    
    def __init__(self, context: str):
        """
        Inicializa o gerenciador para um contexto específico.
        
        Args:
            context: 'dtic' ou 'sis'
        """
        self.context = context.lower()
        self.schema = config.get_schema(self.context)
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Cria engine com connection pooling e configurações otimizadas."""
        try:
            self.engine = create_engine(
                config.DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verifica conexões antes de usar
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    "options": f"-c search_path={self.schema},public"
                }
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False
            )
            
            logger.info(f"✅ PostgreSQL engine inicializado para contexto '{self.context}' (schema: {self.schema})")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar engine PostgreSQL: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager para sessões do banco.
        
        Usage:
            with db_manager.get_session() as session:
                tickets = session.query(Ticket).all()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Erro na sessão do banco: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Testa conexão com o banco."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info(f"✅ Conexão PostgreSQL OK para schema '{self.schema}'")
                return True
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            return False
    
    def create_tables(self):
        """Cria todas as tabelas no schema (se não existirem)."""
        try:
            # Set search_path antes de criar tabelas
            with self.engine.begin() as conn:
                conn.execute(text(f"SET search_path TO {self.schema}"))
                Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"✅ Tabelas criadas/verificadas no schema '{self.schema}'")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            raise
    
    def get_ticket_by_glpi_id(self, glpi_id: int) -> Optional[Ticket]:
        """Busca ticket por GLPI ID."""
        with self.get_session() as session:
            return session.query(Ticket).filter(Ticket.glpi_id == glpi_id).first()
    
    def upsert_ticket(self, ticket_data: dict) -> Ticket:
        """
        Insere ou atualiza ticket.
        
        Args:
            ticket_data: Dicionário com dados do ticket
            
        Returns:
            Ticket object
        """
        with self.get_session() as session:
            existing = session.query(Ticket).filter(
                Ticket.glpi_id == ticket_data['glpi_id']
            ).first()
            
            if existing:
                # Atualizar
                for key, value in ticket_data.items():
                    setattr(existing, key, value)
                existing.versao += 1
                ticket = existing
            else:
                # Inserir
                ticket = Ticket(**ticket_data)
                session.add(ticket)
            
            session.flush()
            return ticket
    
    def list_tickets(self, filters: dict = None, limit: int = 50, offset: int = 0, order_by: str = None) -> list[Ticket]:
        """Lista tickets com filtros e paginação."""
        with self.get_session() as session:
            query = session.query(Ticket)
            
            if filters:
                if 'status' in filters:
                    query = query.filter(Ticket.status == filters['status'])
                if 'is_deleted' in filters:
                    query = query.filter(Ticket.is_deleted == filters['is_deleted'])
                if 'tecnico' in filters:
                    query = query.filter(Ticket.tecnico == filters['tecnico'])
                if 'categoria' in filters:
                    query = query.filter(Ticket.categoria == filters['categoria'])
                if 'prioridade' in filters:
                    query = query.filter(Ticket.prioridade == filters['prioridade'])

            if order_by:
                # Ex: "criado_em DESC"
                parts = order_by.split()
                field_name = parts[0]
                direction = parts[1] if len(parts) > 1 else 'ASC'
                
                if hasattr(Ticket, field_name):
                    field = getattr(Ticket, field_name)
                    if direction.upper() == 'DESC':
                        query = query.order_by(field.desc())
                    else:
                        query = query.order_by(field.asc())
            
            return query.limit(limit).offset(offset).all()

    def count_tickets(self, filters: dict = None) -> int:
        """Conta tickets com filtros opcionais."""
        with self.get_session() as session:
            query = session.query(Ticket)
            
            if filters:
                if 'status' in filters:
                    query = query.filter(Ticket.status == filters['status'])
                if 'is_deleted' in filters:
                    query = query.filter(Ticket.is_deleted == filters['is_deleted'])
            
            return query.count()
    
    def get_sync_meta(self, chave: str) -> Optional[str]:
        """Retorna valor de metadado de sincronização."""
        with self.get_session() as session:
            meta = session.query(SyncMeta).filter(SyncMeta.chave == chave).first()
            return meta.valor if meta else None
    
    def set_sync_meta(self, chave: str, valor: str):
        """Define valor de metadado de sincronização."""
        with self.get_session() as session:
            meta = session.query(SyncMeta).filter(SyncMeta.chave == chave).first()
            
            if meta:
                meta.valor = valor
            else:
                meta = SyncMeta(chave=chave, valor=valor)
                session.add(meta)
    
    def log_sync_history(self, history_data: dict) -> SyncHistory:
        """Registra execução de sincronização no histórico."""
        with self.get_session() as session:
            history = SyncHistory(**history_data)
            session.add(history)
            session.flush()
            return history
    
    def log_sync_error(self, error_data: dict):
        """Registra erro de sincronização."""
        with self.get_session() as session:
            error = SyncError(**error_data)
            session.add(error)
    
    
    # ==================== CARREGADORES METHODS ====================
    
    def upsert_carregador(self, carregador_data: dict):
        """
        Insere ou atualiza carregador.
        
        Args:
            carregador_data: Dicionário com dados do carregador
        """
        from src.db.models import Carregador
        from sqlalchemy.dialects.postgresql import insert
        from datetime import datetime
        
        with self.get_session() as session:
            stmt = insert(Carregador).values(**carregador_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'name': stmt.excluded.name,
                    'locations_id': stmt.excluded.locations_id,
                    'location_name': stmt.excluded.location_name,
                    'users_id': stmt.excluded.users_id,
                    'user_name': stmt.excluded.user_name,
                    'is_deleted': stmt.excluded.is_deleted,
                    'date_mod': stmt.excluded.date_mod,
                    'sincronizado_em': datetime.utcnow()
                }
            )
            session.execute(stmt)
    
    def link_carregador_to_ticket(self, ticket_id: int, carregador_id: int, itemtype: str = 'PluginGenericobjectCarregador'):
        """
        Cria vínculo entre ticket e carregador.
        
        Args:
            ticket_id: ID do ticket (glpi_id)
            carregador_id: ID do carregador
            itemtype: Tipo do item (default: PluginGenericobjectCarregador)
        """
        from src.db.models import CarregadorTicket
        from sqlalchemy.dialects.postgresql import insert
        
        with self.get_session() as session:
            link_data = {
                'tickets_id': ticket_id,
                'items_id': carregador_id,
                'itemtype': itemtype
            }
            stmt = insert(CarregadorTicket).values(**link_data)
            # Evitar duplicatas
            stmt = stmt.on_conflict_do_nothing()
            session.execute(stmt)
    
    def get_carregadores_count(self, is_deleted: int = 0) -> int:
        """Conta carregadores no banco."""
        from src.db.models import Carregador
        
        with self.get_session() as session:
            return session.query(Carregador).filter(
                Carregador.is_deleted == is_deleted
            ).count()
    
    def get_carregador_by_id(self, carregador_id: int):
        """Busca carregador por ID."""
        from src.db.models import Carregador
        
        with self.get_session() as session:
            return session.query(Carregador).filter(
                Carregador.id == carregador_id
            ).first()
    
    # ==================== END CARREGADORES METHODS ====================
    
    def close(self):
        """Fecha conexões e limpa recursos."""
        if self.engine:
            self.engine.dispose()
            logger.info(f"Conexões fechadas para schema '{self.schema}'")


# Factory function para criar managers
def get_db_manager(context: str) -> PostgreSQLManager:
    """
    Retorna um database manager para o contexto especificado.
    
    Args:
        context: 'dtic' ou 'sis'
        
    Returns:
        PostgreSQLManager instance
    """
    return PostgreSQLManager(context)
