#!/usr/bin/env python3
"""
Database Factory - Singleton pattern for context-specific databases
Manages separate databases for DTIC and SIS
"""
import os
from typing import Dict
from .database import Database

class DatabaseFactory:
    """
    Factory para criar e gerenciar instâncias de Database por contexto.
    Garante que cada contexto (DTIC, SIS) tenha sua própria conexão.
    """
    
    _instances: Dict[str, Database] = {}
    
    @classmethod
    def get_database(cls, context: str) -> Database:
        """
        Retorna instância de Database para o contexto especificado.
        
        Args:
            context: Contexto (ex: 'DTIC', 'SIS')
            
        Returns:
            Database instance
        """
        if context not in cls._instances:
            # Define path do banco por contexto
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            db_path = os.path.join(data_dir, f'{context.lower()}.db')
            cls._instances[context] = Database(db_path=db_path, context=context)
            
        return cls._instances[context]
    
    @classmethod
    def reset(cls):
        """Limpa todas as instâncias (útil para testes)"""
        cls._instances = {}
