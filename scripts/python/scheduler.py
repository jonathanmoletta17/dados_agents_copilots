#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador Simples para Pipeline GLPI
====================================

Script para executar automaticamente o pipeline de extração e análise
de dados GLPI a cada 60 minutos, com controle básico para evitar
execuções sobrepostas.

Uso:
    python scheduler.py  # Execução única
    
Para automação contínua, use Windows Task Scheduler ou execute
o script continuous_scheduler.py

Autor: Sistema de Análise GLPI
Data: 2024
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime


class SimplePipelineScheduler:
    """
    Agendador simples para execução do pipeline GLPI.
    
    Controla a execução do main.py com verificação básica
    para evitar execuções sobrepostas.
    """
    
    def __init__(self):
        """Inicializa o agendador."""
        self.script_dir = Path(__file__).parent
        self.lock_file = self.script_dir / "pipeline.lock"
        self.main_script = self.script_dir / "main.py"
        self.log_file = self.script_dir / "scheduler.log"
        
    def log_message(self, message: str) -> None:
        """
        Registra mensagem no log e no console.
        
        Args:
            message: Mensagem a ser registrada
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        # Exibir no console
        print(log_entry)
        
        # Salvar no arquivo de log
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"[ERRO] Falha ao escrever no log: {e}")
    
    def is_pipeline_running(self) -> bool:
        """
        Verifica se o pipeline já está em execução.
        
        Returns:
            bool: True se o pipeline está rodando, False caso contrário
        """
        if not self.lock_file.exists():
            return False
        
        # Verificar se o lock não é muito antigo (mais de 3 horas)
        try:
            lock_age = time.time() - self.lock_file.stat().st_mtime
            if lock_age > 10800:  # 3 horas em segundos
                self.log_message("Lock antigo detectado. Removendo...")
                self.lock_file.unlink()
                return False
        except Exception as e:
            self.log_message(f"Erro ao verificar idade do lock: {e}")
            return True
        
        return True
    
    def create_lock(self) -> bool:
        """
        Cria arquivo de lock para indicar execução em andamento.
        
        Returns:
            bool: True se o lock foi criado com sucesso, False caso contrário
        """
        try:
            self.lock_file.touch()
            return True
        except Exception as e:
            self.log_message(f"Erro ao criar lock: {e}")
            return False
    
    def remove_lock(self) -> None:
        """Remove o arquivo de lock."""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            self.log_message(f"Erro ao remover lock: {e}")
    
    def execute_pipeline(self) -> bool:
        """
        Executa o pipeline principal (main.py).
        
        Returns:
            bool: True se a execução foi bem-sucedida, False caso contrário
        """
        # Verificar se o script principal existe
        if not self.main_script.exists():
            self.log_message(f"ERRO: Script principal não encontrado: {self.main_script}")
            return False
        
        # Verificar se já está executando
        if self.is_pipeline_running():
            self.log_message("Pipeline já em execução. Pulando esta execução.")
            return True
        
        # Criar lock
        if not self.create_lock():
            self.log_message("ERRO: Não foi possível criar arquivo de lock.")
            return False
        
        try:
            self.log_message("=" * 60)
            self.log_message("INICIANDO EXECUÇÃO DO PIPELINE")
            self.log_message("=" * 60)
            
            inicio = time.time()
            
            # Executar main.py
            resultado = subprocess.run(
                [sys.executable, str(self.main_script)],
                cwd=str(self.script_dir),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            fim = time.time()
            duracao = fim - inicio
            
            if resultado.returncode == 0:
                self.log_message(f"SUCESSO: Pipeline concluído em {duracao:.2f} segundos")
                if resultado.stdout:
                    self.log_message("Saída do pipeline:")
                    self.log_message(resultado.stdout)
                return True
            else:
                self.log_message(f"ERRO: Pipeline falhou com código {resultado.returncode}")
                if resultado.stderr:
                    self.log_message("Erro detalhado:")
                    self.log_message(resultado.stderr)
                if resultado.stdout:
                    self.log_message("Saída do pipeline:")
                    self.log_message(resultado.stdout)
                return False
                
        except Exception as e:
            self.log_message(f"ERRO: Exceção durante execução do pipeline: {e}")
            return False
            
        finally:
            # Sempre remover o lock
            self.remove_lock()
            self.log_message("=" * 60)
    
    def run_once(self) -> bool:
        """
        Executa o pipeline uma única vez.
        
        Returns:
            bool: True se a execução foi bem-sucedida, False caso contrário
        """
        self.log_message("Iniciando execução única do agendador...")
        return self.execute_pipeline()


def main():
    """Função principal do agendador."""
    print("=" * 60)
    print("AGENDADOR SIMPLES - PIPELINE GLPI")
    print("=" * 60)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Criar e executar o agendador
    scheduler = SimplePipelineScheduler()
    
    try:
        sucesso = scheduler.run_once()
        
        print("\n" + "=" * 60)
        if sucesso:
            print("RESULTADO: EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("RESULTADO: EXECUÇÃO FALHOU!")
        print("=" * 60)
        print(f"Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Retornar código de saída apropriado
        sys.exit(0 if sucesso else 1)
        
    except KeyboardInterrupt:
        print("\n[INTERROMPIDO] Execução cancelada pelo usuário.")
        scheduler.remove_lock()
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Erro inesperado: {e}")
        scheduler.remove_lock()
        sys.exit(1)


if __name__ == "__main__":
    main()