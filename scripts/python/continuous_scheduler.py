#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador Contínuo para Pipeline GLPI
=====================================

Script que executa continuamente, agendando a execução do pipeline
de extração e análise de dados GLPI a cada 60 minutos.

Este script roda indefinidamente até ser interrompido manualmente.
É uma alternativa ao Windows Task Scheduler.

Uso:
    python continuous_scheduler.py
    
Para parar: Ctrl+C

Autor: Sistema de Análise GLPI
Data: 2024
"""

import time
import signal
import sys
from datetime import datetime, timedelta
from scheduler import SimplePipelineScheduler


class ContinuousScheduler:
    """
    Agendador contínuo que executa o pipeline a cada 60 minutos.
    """
    
    def __init__(self):
        """Inicializa o agendador contínuo."""
        self.scheduler = SimplePipelineScheduler()
        self.running = True
        self.interval_minutes = 60
        self.next_execution = None
        
        # Configurar handler para interrupção
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """
        Handler para sinais de interrupção.
        
        Args:
            signum: Número do sinal
            frame: Frame atual
        """
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Recebido sinal de interrupção...")
        self.running = False
    
    def calculate_next_execution(self) -> datetime:
        """
        Calcula o próximo horário de execução.
        
        Returns:
            datetime: Próximo horário de execução
        """
        return datetime.now() + timedelta(minutes=self.interval_minutes)
    
    def log_status(self, message: str) -> None:
        """
        Registra status no console.
        
        Args:
            message: Mensagem a ser registrada
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def run_continuous(self) -> None:
        """
        Executa o agendador continuamente.
        """
        self.log_status("=" * 60)
        self.log_status("AGENDADOR CONTÍNUO - PIPELINE GLPI")
        self.log_status("=" * 60)
        self.log_status(f"Intervalo de execução: {self.interval_minutes} minutos")
        self.log_status("Pressione Ctrl+C para parar")
        self.log_status("=" * 60)
        
        # Executar imediatamente na primeira vez
        self.log_status("Executando pipeline inicial...")
        try:
            sucesso = self.scheduler.execute_pipeline()
            if sucesso:
                self.log_status("Pipeline inicial executado com sucesso")
            else:
                self.log_status("Pipeline inicial falhou")
        except Exception as e:
            self.log_status(f"Erro na execução inicial: {e}")
        
        # Calcular próxima execução
        self.next_execution = self.calculate_next_execution()
        self.log_status(f"Próxima execução agendada para: {self.next_execution.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Loop principal
        while self.running:
            try:
                current_time = datetime.now()
                
                # Verificar se é hora de executar
                if current_time >= self.next_execution:
                    self.log_status("Iniciando execução agendada...")
                    
                    try:
                        sucesso = self.scheduler.execute_pipeline()
                        if sucesso:
                            self.log_status("Execução agendada concluída com sucesso")
                        else:
                            self.log_status("Execução agendada falhou")
                    except Exception as e:
                        self.log_status(f"Erro durante execução agendada: {e}")
                    
                    # Calcular próxima execução
                    self.next_execution = self.calculate_next_execution()
                    self.log_status(f"Próxima execução agendada para: {self.next_execution.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Aguardar 1 minuto antes de verificar novamente
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.log_status("Interrupção detectada...")
                break
            except Exception as e:
                self.log_status(f"Erro inesperado no loop principal: {e}")
                time.sleep(60)  # Aguardar antes de tentar novamente
        
        self.log_status("=" * 60)
        self.log_status("AGENDADOR CONTÍNUO FINALIZADO")
        self.log_status("=" * 60)


def main():
    """Função principal do agendador contínuo."""
    try:
        scheduler = ContinuousScheduler()
        scheduler.run_continuous()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n[INTERROMPIDO] Agendador cancelado pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()