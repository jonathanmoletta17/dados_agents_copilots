"""
SQLAlchemy models for PostgreSQL with schema support.
Supports separate schemas for DTIC and SIS contexts.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DECIMAL,
    DateTime, CheckConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

Base = declarative_base()


class Ticket(Base):
    """
    Ticket model with expanded GLPI fields.
    Used in both dtic and sis schemas.
    """
    __tablename__ = 'tickets'
    
    # Identificadores
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Conteúdo
    titulo = Column(String(500), nullable=False)
    descricao = Column(Text)
    descricao_md = Column(Text)
    
    # Classificação
    status = Column(String(50), nullable=False, index=True)
    status_id = Column(Integer)
    prioridade = Column(String(20), index=True)
    prioridade_id = Column(Integer)
    tipo = Column(String(50))
    tipo_id = Column(Integer)
    
    # Impacto e Urgência (GLPI: 1-5)
    impact = Column(Integer, CheckConstraint('impact BETWEEN 1 AND 5'))
    urgency = Column(Integer, CheckConstraint('urgency BETWEEN 1 AND 5'))
    
    # Entidades (Nomes enriquecidos + IDs)
    categoria = Column(String(255), index=True)
    categoria_id = Column(Integer)
    entidade = Column(String(255))
    entidade_id = Column(Integer)
    tecnico = Column(String(255), index=True)
    tecnico_id = Column(Integer)
    grupo = Column(String(255), index=True)
    grupo_id = Column(Integer)
    grupo_nivel = Column(String(10))
    requerente = Column(String(255))
    requerente_id = Column(Integer)
    ultimo_atualizador = Column(String(255))
    ultimo_atualizador_id = Column(Integer)
    
    # Localização e Ativos
    localizacao = Column(String(255))
    localizacao_id = Column(Integer)
    item_relacionado_tipo = Column(String(100))
    item_relacionado_id = Column(Integer)
    
    # SLA/OLA
    sla_ttr_id = Column(Integer)
    sla_tto_id = Column(Integer)
    ola_ttr_id = Column(Integer)
    ola_tto_id = Column(Integer)
    tempo_para_resolver = Column(Integer)
    tempo_para_atribuir = Column(Integer)
    
    # Tempos de Interação (segundos)
    tempo_primeira_interacao = Column(Integer)
    tempo_acao_total = Column(Integer)
    
    # Tipo de Requisição
    tipo_requisicao = Column(String(50))
    tipo_requisicao_id = Column(Integer)
    
    # Validação e Satisfação
    status_validacao = Column(String(50))
    percentual_validacao = Column(Integer)
    
    # Fornecedor
    fornecedor = Column(String(255))
    fornecedor_id = Column(Integer)
    
    # Custos
    custo_tempo = Column(DECIMAL(10, 2))
    custo_fixo = Column(DECIMAL(10, 2))
    custo_material = Column(DECIMAL(10, 2))
    
    # Timestamps (com timezone)
    criado_em = Column(TIMESTAMP(timezone=True), nullable=False)
    atualizado_em = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    solucionado_em = Column(TIMESTAMP(timezone=True))
    fechado_em = Column(TIMESTAMP(timezone=True))
    
    # Metadados
    url = Column(String(500))
    is_deleted = Column(Boolean, default=False)
    
    # Controle de Sincronização
    ticket_hash = Column(String(32), index=True)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    versao = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<Ticket(glpi_id={self.glpi_id}, titulo='{self.titulo[:50]}...')>"

    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }


class SyncMeta(Base):
    """Metadados de sincronização."""
    __tablename__ = 'sync_meta'
    
    chave = Column(String(50), primary_key=True)
    valor = Column(Text)
    atualizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SyncMeta(chave='{self.chave}', valor='{self.valor}')>"


class SyncHistory(Base):
    """Histórico de execuções de sincronização."""
    __tablename__ = 'sync_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_sync = Column(String(20), nullable=False)
    tickets_novos = Column(Integer, default=0)
    tickets_atualizados = Column(Integer, default=0)
    tickets_sem_mudanca = Column(Integer, default=0)
    tickets_total = Column(Integer, default=0)
    erros = Column(Integer, default=0)
    duracao_segundos = Column(DECIMAL(10, 2))
    iniciado_em = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    finalizado_em = Column(TIMESTAMP(timezone=True))
    sucesso = Column(Boolean)
    observacoes = Column(Text)
    
    def __repr__(self):
        return f"<SyncHistory(tipo='{self.tipo_sync}', iniciado={self.iniciado_em})>"

    def to_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }


class SyncError(Base):
    """Log de erros durante sincronização."""
    __tablename__ = 'sync_errors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_id = Column(Integer, index=True)
    tipo_erro = Column(String(100))
    mensagem_erro = Column(Text)
    stack_trace = Column(Text)
    criado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SyncError(glpi_id={self.glpi_id}, tipo='{self.tipo_erro}')>"


class Carregador(Base):
    """
    Modelo para Carregadores (PluginGenericobjectCarregador).
    """
    __tablename__ = 'carregadores'
    
    id = Column(Integer, primary_key=True) # GLPI ID
    name = Column(String(255))
    locations_id = Column(Integer)
    location_name = Column(String(255))
    users_id = Column(Integer)
    user_name = Column(String(255))
    is_deleted = Column(Integer)
    date_mod = Column(TIMESTAMP(timezone=True))
    date_creation = Column(TIMESTAMP(timezone=True))
    
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Carregador(id={self.id}, name='{self.name}')>"


class CarregadorTicket(Base):
    """
    Tabela de ligação entre Tickets e Carregadores.
    """
    __tablename__ = 'carregador_tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tickets_id = Column(Integer, index=True) # Link to Ticket.glpi_id
    items_id = Column(Integer, index=True) # Link to Carregador.id
    itemtype = Column(String(100)) # 'PluginGenericobjectCarregador'
    
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CarregadorTicket(ticket={self.tickets_id}, carregador={self.items_id})>"