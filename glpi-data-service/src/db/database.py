#!/usr/bin/env python3
"""
Módulo de banco de dados simples para GLPI Data Service
Usa sqlite3 nativo para evitar problemas de compatibilidade
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

class Database:
    def __init__(self, db_path: str = None, context: str = None):
        """
        Inicializa Database para um contexto específico.
        
        Args:
            db_path: Caminho do banco (opcional)
            context: Contexto (DTIC, SIS) - usado para determinar db_path se não fornecido
        """
        self.context = context
        
        if db_path is None:
            if context is None:
                raise ValueError("db_path ou context devem ser fornecidos")
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, f'{context.lower()}.db')
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados criando as tabelas se não existirem"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de tickets
            # NOTE: Mantendo consistência com init_db.py
            extra_columns = ""
            if self.context and self.context.upper() == 'DTIC':
                extra_columns = "motivo_pendencia TEXT,"

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    glpi_id INTEGER NOT NULL UNIQUE,
                    titulo TEXT NOT NULL,
                    descricao TEXT,
                    status TEXT,
                    prioridade TEXT,
                    org TEXT,
                    categoria TEXT,
                    entidade TEXT,
                    tecnico TEXT,
                    grupo TEXT,
                    requerente TEXT,
                    {extra_columns}
                    created_at TEXT,
                    updated_at TEXT,
                    solved_at TEXT,
                    closed_at TEXT,
                    url TEXT,
                    is_deleted BOOLEAN DEFAULT 0
                )
            """)
            
            # Índices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tickets(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_org ON tickets(org)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_updated_at ON tickets(updated_at DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON tickets(created_at DESC)')
            
            # FTS5 para busca textual
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS tickets_search USING fts5(
                    titulo,
                    descricao,
                    id UNINDEXED,
                    tokenize="porter unicode61 remove_diacritics 1"
                )
            """)
            
            # Triggers para manter FTS5 sincronizado
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS tickets_ai AFTER INSERT ON tickets BEGIN
                    INSERT INTO tickets_search(rowid, titulo, descricao, id)
                    VALUES (new.id, new.titulo, new.descricao, new.id);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS tickets_ad AFTER DELETE ON tickets BEGIN
                    DELETE FROM tickets_search WHERE rowid = old.id;
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS tickets_au AFTER UPDATE ON tickets BEGIN
                    UPDATE tickets_search 
                    SET titulo = new.titulo, descricao = new.descricao 
                    WHERE rowid = old.id;
                END
            """)
            
            # Tabela de metadados de sincronização
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de erros de sincronização
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    glpi_id INTEGER,
                    source TEXT,
                    context TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_connection(self):
        """Retorna uma conexão com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        return conn
    
    def get_tickets(self, org: str = None, status: str = None, 
                   start_date: str = None, end_date: str = None,
                   limit: int = 100, offset: int = 0) -> List[Dict]:
        """Busca tickets com filtros"""
        
        query = "SELECT * FROM tickets WHERE 1=1"
        params = []
        
        if org:
            query += " AND org = ?"
            params.append(org)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if start_date:
            query += " AND updated_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND updated_at <= ?"
            params.append(end_date)
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Converte rows para dict
            return [dict(row) for row in rows]
    
    def get_ticket_by_glpi_id(self, glpi_id: int) -> Optional[Dict]:
        """Busca ticket por ID do GLPI"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets WHERE glpi_id = ?", (glpi_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def upsert_ticket(self, ticket_data: Dict) -> bool:
        """Insere ou atualiza ticket"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verifica se existe pelo glpi_id
                existing = cursor.execute(
                    "SELECT id FROM tickets WHERE glpi_id = ?", 
                    (ticket_data['glpi_id'],)
                ).fetchone()
                
                if existing:
                    # Atualiza
                    fields = [f"{k} = ?" for k in ticket_data.keys()]
                    values = list(ticket_data.values())
                    values.append(ticket_data['glpi_id'])
                    
                    query = f"UPDATE tickets SET {', '.join(fields)} WHERE glpi_id = ?"
                    cursor.execute(query, values)
                else:
                    # Insere
                    fields = ', '.join(ticket_data.keys())
                    placeholders = ', '.join(['?' for _ in ticket_data])
                    values = list(ticket_data.values())
                    
                    query = f"INSERT INTO tickets ({fields}) VALUES ({placeholders})"
                    cursor.execute(query, values)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao salvar ticket: {e}")
            return False
    
    def get_sync_meta(self, key: str) -> Optional[str]:
        """Retorna valor de metadado de sincronização"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM sync_meta WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
    
    def set_sync_meta(self, key: str, value: str):
        """Define valor de metadado de sincronização"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO sync_meta (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, datetime.now().isoformat())
            )
            conn.commit()
    
    def log_sync_error(self, glpi_id: int, error_type: str, error_message: str):
        """Registra erro de sincronização"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO sync_errors (glpi_id, error_type, error_message) 
                   VALUES (?, ?, ?)""",
                (glpi_id, error_type, error_message)
            )
            conn.commit()
    
    def get_ticket_stats(self, org: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """Retorna estatísticas de tickets"""
        query = "SELECT status, COUNT(*) as count FROM tickets WHERE 1=1"
        params = []
        
        if org:
            query += " AND org = ?"
            params.append(org)
            
        if start_date:
            query += " AND updated_at >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND updated_at <= ?"
            params.append(end_date)
        
        query += " GROUP BY status"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            stats = {}
            total = 0
            for row in rows:
                stats[row['status']] = row['count']
                total += row['count']
            
            stats['total'] = total
            return stats
    
    def get_level_stats(self, org: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """
        Retorna estatísticas agrupadas por nível de suporte (N1, N2, N3, N4).
        Baseado em keywords no campo 'grupo'.
        """
        query = "SELECT grupo, status, COUNT(*) as count FROM tickets WHERE 1=1"
        params = []
        
        if org:
            query += " AND org = ?"
            params.append(org)
            
        if start_date:
            query += " AND updated_at >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND updated_at <= ?"
            params.append(end_date)
            
        query += " GROUP BY grupo, status"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Inicializa estrutura
            levels = {
                "N1": {"novos": 0, "em_progresso": 0, "pendentes": 0, "resolvidos": 0, "total": 0},
                "N2": {"novos": 0, "em_progresso": 0, "pendentes": 0, "resolvidos": 0, "total": 0},
                "N3": {"novos": 0, "em_progresso": 0, "pendentes": 0, "resolvidos": 0, "total": 0},
                "N4": {"novos": 0, "em_progresso": 0, "pendentes": 0, "resolvidos": 0, "total": 0},
                "Outros": {"novos": 0, "em_progresso": 0, "pendentes": 0, "resolvidos": 0, "total": 0},
            }
            
            # Mapeamento de status (igual ao metrics_logic.py)
            status_map = {
                "Novo": "novos", "New": "novos",
                "Em andamento (atribuído)": "em_progresso", "Atribuído": "em_progresso",
                "Em andamento (planejado)": "em_progresso", "Planejado": "em_progresso",
                "Em andamento": "pendentes", "Pendente": "pendentes",
                "Solucionado": "resolvidos", "Fechado": "resolvidos", "Solved": "resolvidos", "Closed": "resolvidos"
            }
            
            for row in rows:
                grupo = (row['grupo'] or "").upper()
                status = row['status']
                count = row['count']
                
                # Determina nível
                level = "Outros"
                if "N1" in grupo: level = "N1"
                elif "N2" in grupo: level = "N2"
                elif "N3" in grupo: level = "N3"
                elif "N4" in grupo: level = "N4"
                
                target_status = status_map.get(status, "pendentes") # Default fallback
                levels[level][target_status] += count
                levels[level]["total"] += count
            
            return levels

    def get_technician_ranking(self, org: str = None, start_date: str = None, end_date: str = None, limit: int = 20) -> List[Dict]:
        """
        Retorna ranking de técnicos com base em tickets solucionados/fechados.
        """
        query = """
            SELECT tecnico, COUNT(*) as count 
            FROM tickets 
            WHERE status IN ('Solucionado', 'Fechado', 'Solved', 'Closed')
            AND tecnico IS NOT NULL 
            AND tecnico != 'Não atribuído'
        """
        params = []
        
        if org:
            query += " AND org = ?"
            params.append(org)
            
        if start_date:
            query += " AND updated_at >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND updated_at <= ?"
            params.append(end_date)
            
        query += " GROUP BY tecnico ORDER BY count DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {"tecnico": row['tecnico'], "tickets": row['count'], "nivel": "N/A"} 
                for row in rows
            ]

    def get_entity_ranking(self, org: str = None, start_date: str = None, end_date: str = None, limit: int = 20) -> List[Dict]:
        """
        Retorna ranking de entidades por volume de tickets.
        """
        query = """
            SELECT entidade, COUNT(*) as count 
            FROM tickets 
            WHERE entidade IS NOT NULL 
            AND entidade != ''
        """
        params = []
        
        if org:
            query += " AND org = ?"
            params.append(org)
            
        if start_date:
            query += " AND updated_at >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND updated_at <= ?"
            params.append(end_date)
            
        query += " GROUP BY entidade ORDER BY count DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {"entity_name": row['entidade'], "ticket_count": row['count']} 
                for row in rows
            ]

    def get_category_ranking(self, org: str = None, start_date: str = None, end_date: str = None, limit: int = 20) -> List[Dict]:
        """
        Retorna ranking de categorias por volume de tickets.
        """
        query = """
            SELECT categoria, COUNT(*) as count 
            FROM tickets 
            WHERE categoria IS NOT NULL 
            AND categoria != ''
        """
        params = []
        
        if org:
            query += " AND org = ?"
            params.append(org)
            
        if start_date:
            query += " AND updated_at >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND updated_at <= ?"
            params.append(end_date)
            
        query += " GROUP BY categoria ORDER BY count DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {"category_name": row['categoria'], "ticket_count": row['count']} 
                for row in rows
            ]

    def search_tickets(self, query_text: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Busca tickets usando FTS5"""
        search_query = """
            SELECT t.* FROM tickets t
            INNER JOIN tickets_search ts ON t.id = ts.id
            WHERE tickets_search MATCH ?
            ORDER BY rank LIMIT ? OFFSET ?
        """
        params = [query_text, limit, offset]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(search_query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    
    def get_departments(self) -> List[str]:
        """Retorna lista de departamentos únicos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT org FROM tickets WHERE org IS NOT NULL ORDER BY org")
            return [row['org'] for row in cursor.fetchall()]
    
    def get_last_sync_time(self) -> Optional[str]:
        """Retorna timestamp do último sync realizado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM sync_meta WHERE key = 'last_sync_time'")
            row = cursor.fetchone()
            return row['value'] if row else None
    
    def update_last_sync_time(self, timestamp: str):
        """Atualiza timestamp do último sync"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sync_meta (key, value, updated_at) 
                VALUES ('last_sync_time', ?, ?)
            """, (timestamp, datetime.now().isoformat()))
            conn.commit()