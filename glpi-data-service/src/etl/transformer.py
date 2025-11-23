#!/usr/bin/env python3
"""
Transformador de dados GLPI para formato interno PostgreSQL.
Captura campos expandidos incluindo SLA, custos, localização, etc.
"""
import re
import hashlib
from datetime import datetime
from typing import Dict, Optional


class DataTransformer:
    """Transforma dados brutos do GLPI para formato do banco PostgreSQL."""
    
    def __init__(self):
        # Mapeamento de status GLPI ID para nomes
        self.status_map = {
            1: 'NOVO',
            2: 'ATRIBUIDO',
            3: 'PLANEJADO',
            4: 'PENDENTE',
            5: 'SOLUCIONADO',
            6: 'FECHADO'
        }
        
        # Mapeamento de prioridades
        self.priority_map = {
            1: 'MUITO_BAIXA',
            2: 'BAIXA',
            3: 'MEDIA',
            4: 'ALTA',
            5: 'MUITO_ALTA',
            6: 'CRITICA'
        }
        
        # Níveis de grupo (keywords para derivar)
        self.level_keywords = {
            'N1': ['n1', 'nivel 1', 'suporte 1'],
            'N2': ['n2', 'nivel 2', 'suporte 2'],
            'N3': ['n3', 'nivel 3', 'suporte 3'],
            'N4': ['n4', 'nivel 4', 'suporte 4']
        }
    
    def transform_ticket(self, raw_ticket: Dict, enriched_data: Dict = None) -> Dict:
        """
        Transforma ticket GLPI para formato PostgreSQL.
        
        Args:
            raw_ticket: Dados brutos da API GLPI
            enriched_data: Dados enriquecidos (nomes de entidades, etc.)
            
        Returns:
            Dicionário pronto para inserção no banco
        """
        enriched = enriched_data or {}
        
        # Dados básicos
        ticket_data = {
            # Identificadores
            'glpi_id': int(raw_ticket.get('id', 0)),
            
            # Conteúdo
            'titulo': raw_ticket.get('name', ''),
            'descricao': raw_ticket.get('content', ''),  # HTML original
            'descricao_md': self._html_to_markdown(raw_ticket.get('content', '')),
            
            # Classificação
            'status': self.status_map.get(raw_ticket.get('status'), 'NOVO'),
            'status_id': raw_ticket.get('status'),
            'prioridade': self.priority_map.get(raw_ticket.get('priority'), 'MEDIA'),
            'prioridade_id': raw_ticket.get('priority'),
            'tipo': self._get_ticket_type(raw_ticket.get('type', 1)),
            'tipo_id': raw_ticket.get('type'),
            
            # Impacto e Urgência
            'impact': raw_ticket.get('impact'),
            'urgency': raw_ticket.get('urgency'),
            
            # Entidades (com IDs)
            'categoria': enriched.get('categoria_nome', ''),
            'categoria_id': raw_ticket.get('itilcategories_id'),
            'entidade': enriched.get('entidade_nome', ''),
            'entidade_id': raw_ticket.get('entities_id'),
            'tecnico': enriched.get('tecnico_nome', ''),
            'tecnico_id': raw_ticket.get('users_id_tech') or raw_ticket.get('users_id_assign'),
            'grupo': enriched.get('grupo_nome', ''),
            'grupo_id': raw_ticket.get('groups_id_assign') or raw_ticket.get('groups_id_tech'),
            'grupo_nivel': self._derive_level(enriched.get('grupo_nome', '')),
            'requerente': enriched.get('requerente_nome', ''),
            'requerente_id': raw_ticket.get('users_id_recipient'),
            'ultimo_atualizador': enriched.get('ultimo_atualizador_nome', ''),
            'ultimo_atualizador_id': raw_ticket.get('users_id_lastupdater'),
            
            # Localização e Ativos
            'localizacao': enriched.get('localizacao_nome'),
            'localizacao_id': raw_ticket.get('locations_id'),
            'item_relacionado_tipo': raw_ticket.get('itemtype'),
            'item_relacionado_id': raw_ticket.get('items_id'),
            
            # SLA/OLA
            'sla_ttr_id': raw_ticket.get('slas_id_ttr'),
            'sla_tto_id': raw_ticket.get('slas_id_tto'),
            'ola_ttr_id': raw_ticket.get('olas_id_ttr'),
            'ola_tto_id': raw_ticket.get('olas_id_tto'),
            'tempo_para_resolver': raw_ticket.get('time_to_resolve'),
            'tempo_para_atribuir': raw_ticket.get('time_to_own'),
            
            # Tempos de Interação
            'tempo_primeira_interacao': raw_ticket.get('takeintoaccount_delay_stat'),
            'tempo_acao_total': raw_ticket.get('actiontime'),
            
            # Tipo de Requisição
            'tipo_requisicao': enriched.get('tipo_requisicao_nome'),
            'tipo_requisicao_id': raw_ticket.get('requesttypes_id'),
            
            # Validação
            'status_validacao': raw_ticket.get('global_validation'),
            'percentual_validacao': raw_ticket.get('validation_percent'),
            
            # Fornecedor
            'fornecedor': enriched.get('fornecedor_nome'),
            'fornecedor_id': raw_ticket.get('suppliers_id_assign'),
            
            # Custos
            'custo_tempo': raw_ticket.get('cost_time'),
            'custo_fixo': raw_ticket.get('cost_fixed'),
            'custo_material': raw_ticket.get('cost_material'),
            
            # Timestamps
            'criado_em': self._parse_datetime(raw_ticket.get('date')),
            'atualizado_em': self._parse_datetime(raw_ticket.get('date_mod')),
            'solucionado_em': self._parse_datetime(raw_ticket.get('solvedate')),
            'fechado_em': self._parse_datetime(raw_ticket.get('closedate')),
            
            # Metadados
            'url': enriched.get('url', ''),
            'is_deleted': bool(raw_ticket.get('is_deleted', 0)),
            
            # Controle de Sincronização
            'ticket_hash': None,  # Será calculado depois
            'sincronizado_em': datetime.utcnow(),
            'versao': 1
        }
        
        # Calcular hash do ticket
        ticket_data['ticket_hash'] = self.calculate_ticket_hash(ticket_data)
        
        return ticket_data
    
    def calculate_ticket_hash(self, ticket_data: Dict) -> str:
        """
        Calcula MD5 hash de campos relevantes para detectar mudanças.
        
        Args:
            ticket_data: Dicionário com dados do ticket
            
        Returns:
            String MD5 hash (32 caracteres)
        """
        # Campos relevantes para detectar mudanças
        relevant_fields = [
            str(ticket_data.get('titulo', '')),
            str(ticket_data.get('descricao', '')),
            str(ticket_data.get('status', '')),
            str(ticket_data.get('prioridade', '')),
            str(ticket_data.get('tecnico', '')),
            str(ticket_data.get('grupo', '')),
            str(ticket_data.get('atualizado_em', ''))
        ]
        
        combined = '|'.join(relevant_fields)
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def _get_ticket_type(self, type_id: int) -> str:
        """Mapeia tipo de ticket."""
        type_map = {
            1: 'INCIDENT',
            2: 'REQUEST'
        }
        return type_map.get(type_id, 'INCIDENT')
    
    def _derive_level(self, group_name: str) -> Optional[str]:
        """Deriva nível de suporte (N1-N4) do nome do grupo."""
        if not group_name:
            return None
        
        group_lower = group_name.lower()
        for level, keywords in self.level_keywords.items():
            for keyword in keywords:
                if keyword in group_lower:
                    return level
        return None
    
    def _html_to_markdown(self, html: str) -> str:
        """
        Conversão básica de HTML para Markdown.
        Remove tags HTML mantendo texto legível.
        """
        if not html:
            return ''
        
        # Remove tags HTML comuns
        text = re.sub(r'<br\s*/?>', '\n', html)
        text = re.sub(r'<p>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decodifica entidades HTML
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        
        # Remove espaços duplicados e linhas vazias excessivas
        text = re.sub(r'\n\n+', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """
        Converte string de data GLPI para datetime.
        
        Args:
            date_str: Data em formato ISO ou GLPI
            
        Returns:
            datetime object ou None
        """
        if not date_str or date_str == 'NULL':
            return None
        
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue
        
        return None