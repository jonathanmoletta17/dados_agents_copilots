#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Principal de Extração e Análise de Dados GLPI
======================================================

Este script orquestra a execução sequencial dos módulos de extração de dados
e análise de métricas do sistema GLPI, garantindo a ordem correta de execução
e validação dos dados em cada etapa.

Fluxo de Execução:
1. Extração de todos os tickets (extrair_todos_tickets.py)
2. Verificação da integridade dos dados brutos gerados
3. Extração e análise de métricas (extrair_metricas_tickets_otimizado.py)
4. Validação final dos resultados

Autor: Sistema de Análise GLPI
Data: 2024
"""

import os
import sys
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


class PipelineOrchestrator:
    """
    Orquestrador principal do pipeline de extração e análise de dados GLPI.
    
    Responsável por coordenar a execução sequencial dos scripts de extração
    de dados e análise de métricas, garantindo a integridade e ordem correta
    das operações.
    """
    
    def __init__(self):
        """Inicializa o orquestrador do pipeline."""
        self.setup_logging()
        self.script_dir = Path(__file__).parent
        self.dados_dir = self.script_dir.parent / "dados"
        self.logger = logging.getLogger(__name__)
        
        # Caminhos dos scripts
        self.script_extracao = self.script_dir / "extrair_todos_tickets.py"
        self.script_metricas = self.script_dir / "extrair_metricas_tickets_otimizado.py"
        
        # Diretórios de dados esperados
        self.dir_tickets_completos = self.dados_dir / "tickets_completos"
        self.dir_tickets_6_meses = self.dados_dir / "tickets_6_meses"
        self.dir_metricas_csv = self.dados_dir / "metricas_csv"
        
        self.logger.info("=" * 80)
        self.logger.info("INICIANDO PIPELINE DE EXTRAÇÃO E ANÁLISE DE DADOS GLPI")
        self.logger.info("=" * 80)
        
    def setup_logging(self) -> None:
        """Configura o sistema de logging do pipeline."""
        # Configuração do formato de log
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Configuração do logger principal
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    filename='pipeline_execution.log',
                    mode='a',
                    encoding='utf-8'
                )
            ]
        )
        
    def verificar_prerequisitos(self) -> bool:
        """
        Verifica se todos os pré-requisitos para execução estão atendidos.
        
        Returns:
            bool: True se todos os pré-requisitos estão atendidos, False caso contrário
        """
        self.logger.info("ETAPA 1: Verificando pré-requisitos do sistema...")
        
        # Verificar se os scripts existem
        scripts_necessarios = [
            (self.script_extracao, "Script de extração de tickets"),
            (self.script_metricas, "Script de análise de métricas")
        ]
        
        for script_path, descricao in scripts_necessarios:
            if not script_path.exists():
                self.logger.error(f"[ERRO] {descricao} não encontrado: {script_path}")
                return False
            self.logger.info(f"[OK] {descricao} encontrado: {script_path}")
        
        # Criar diretórios necessários se não existirem
        self.dados_dir.mkdir(exist_ok=True)
        self.logger.info(f"[OK] Diretório de dados verificado: {self.dados_dir}")
        
        self.logger.info("[OK] Todos os pré-requisitos verificados com sucesso")
        return True
        
    def executar_script(self, script_path: Path, descricao: str, timeout: int = 3600) -> Tuple[bool, str]:
        """
        Executa um script Python e monitora sua execução.
        
        Args:
            script_path: Caminho para o script a ser executado
            descricao: Descrição do script para logs
            timeout: Timeout em segundos para execução (padrão: 1 hora)
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem_de_saida)
        """
        self.logger.info(f"Iniciando execução: {descricao}")
        self.logger.info(f"Script: {script_path}")
        
        inicio = time.time()
        
        try:
            # Executar o script usando subprocess
            resultado = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.script_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            fim = time.time()
            duracao = fim - inicio
            
            if resultado.returncode == 0:
                self.logger.info(f"[OK] {descricao} executado com sucesso")
                self.logger.info(f"[OK] Tempo de execução: {duracao:.2f} segundos")
                if resultado.stdout:
                    self.logger.info(f"Saída do script:\n{resultado.stdout}")
                return True, resultado.stdout
            else:
                self.logger.error(f"[ERRO] {descricao} falhou com código: {resultado.returncode}")
                if resultado.stderr:
                    self.logger.error(f"Erro detalhado:\n{resultado.stderr}")
                if resultado.stdout:
                    self.logger.error(f"Saída do script:\n{resultado.stdout}")
                return False, resultado.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"[ERRO] {descricao} excedeu o timeout de {timeout} segundos")
            return False, f"Timeout após {timeout} segundos"
            
        except Exception as e:
            self.logger.error(f"[ERRO] Erro inesperado ao executar {descricao}: {str(e)}")
            return False, str(e)
    
    def verificar_dados_brutos(self) -> bool:
        """
        Verifica se os dados brutos foram gerados corretamente após a extração.
        
        Returns:
            bool: True se os dados foram gerados corretamente, False caso contrário
        """
        self.logger.info("ETAPA 3: Verificando integridade dos dados brutos gerados...")
        
        # Verificar se os diretórios foram criados
        diretorios_esperados = [
            (self.dir_tickets_completos, "Tickets completos"),
            (self.dir_tickets_6_meses, "Tickets dos últimos 6 meses")
        ]
        
        for diretorio, descricao in diretorios_esperados:
            if not diretorio.exists():
                self.logger.error(f"[ERRO] Diretório não encontrado: {descricao} ({diretorio})")
                return False
            
            # Verificar se há arquivos no diretório
            arquivos = list(diretorio.glob("*.csv"))
            if not arquivos:
                self.logger.error(f"[ERRO] Nenhum arquivo CSV encontrado em: {descricao}")
                return False
            
            # Verificar se os arquivos não estão vazios
            total_registros = 0
            for arquivo in arquivos:
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        linhas = sum(1 for _ in f) - 1  # Subtrair cabeçalho
                        total_registros += linhas
                except Exception as e:
                    self.logger.error(f"[ERRO] Erro ao ler arquivo {arquivo}: {str(e)}")
                    return False
            
            self.logger.info(f"[OK] {descricao}: {len(arquivos)} arquivos, {total_registros} registros")
        
        self.logger.info("[OK] Verificação dos dados brutos concluída com sucesso")
        return True
    
    def verificar_metricas_geradas(self) -> bool:
        """
        Verifica se as métricas foram geradas corretamente.
        
        Returns:
            bool: True se as métricas foram geradas corretamente, False caso contrário
        """
        self.logger.info("ETAPA 5: Verificando métricas geradas...")
        
        if not self.dir_metricas_csv.exists():
            self.logger.error(f"[ERRO] Diretório de métricas não encontrado: {self.dir_metricas_csv}")
            return False
        
        # Verificar arquivos de métricas esperados
        arquivos_metricas = list(self.dir_metricas_csv.glob("*.csv"))
        if not arquivos_metricas:
            self.logger.error("[ERRO] Nenhum arquivo de métrica encontrado")
            return False
        
        total_metricas = 0
        for arquivo in arquivos_metricas:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    linhas = sum(1 for _ in f) - 1  # Subtrair cabeçalho
                    total_metricas += linhas
            except Exception as e:
                self.logger.error(f"[ERRO] Erro ao ler arquivo de métrica {arquivo}: {str(e)}")
                return False
        
        self.logger.info(f"[OK] Métricas geradas: {len(arquivos_metricas)} arquivos, {total_metricas} registros")
        return True
    
    def executar_pipeline(self) -> bool:
        """
        Executa o pipeline completo de extração e análise de dados.
        
        Returns:
            bool: True se todo o pipeline foi executado com sucesso, False caso contrário
        """
        inicio_pipeline = time.time()
        
        try:
            # ETAPA 1: Verificar pré-requisitos
            if not self.verificar_prerequisitos():
                self.logger.error("[ERRO] Pré-requisitos não atendidos. Abortando execução.")
                return False
            
            # ETAPA 2: Executar extração de todos os tickets
            self.logger.info("ETAPA 2: Executando extração de todos os tickets...")
            sucesso_extracao, saida_extracao = self.executar_script(
                self.script_extracao,
                "Extração de todos os tickets",
                timeout=7200  # 2 horas para extração
            )
            
            if not sucesso_extracao:
                self.logger.error("[ERRO] Falha na extração de tickets. Abortando pipeline.")
                return False
            
            # ETAPA 3: Verificar dados brutos gerados
            if not self.verificar_dados_brutos():
                self.logger.error("[ERRO] Dados brutos não foram gerados corretamente. Abortando pipeline.")
                return False
            
            # ETAPA 4: Executar análise de métricas
            self.logger.info("ETAPA 4: Executando análise de métricas...")
            sucesso_metricas, saida_metricas = self.executar_script(
                self.script_metricas,
                "Análise de métricas de tickets",
                timeout=3600  # 1 hora para análise
            )
            
            if not sucesso_metricas:
                self.logger.error("[ERRO] Falha na análise de métricas. Pipeline parcialmente concluído.")
                return False
            
            # ETAPA 5: Verificar métricas geradas
            if not self.verificar_metricas_geradas():
                self.logger.error("[ERRO] Métricas não foram geradas corretamente.")
                return False
            
            # Pipeline concluído com sucesso
            fim_pipeline = time.time()
            duracao_total = fim_pipeline - inicio_pipeline
            
            self.logger.info("=" * 80)
            self.logger.info("PIPELINE CONCLUÍDO COM SUCESSO!")
            self.logger.info("=" * 80)
            self.logger.info(f"Tempo total de execução: {duracao_total:.2f} segundos")
            self.logger.info(f"Data/hora de conclusão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERRO] Erro inesperado durante execução do pipeline: {str(e)}")
            return False
    
    def gerar_relatorio_execucao(self) -> Dict[str, Any]:
        """
        Gera um relatório detalhado da execução do pipeline.
        
        Returns:
            Dict[str, Any]: Relatório com estatísticas da execução
        """
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "diretorios": {
                "dados": str(self.dados_dir),
                "tickets_completos": str(self.dir_tickets_completos),
                "tickets_6_meses": str(self.dir_tickets_6_meses),
                "metricas_csv": str(self.dir_metricas_csv)
            },
            "arquivos_gerados": {}
        }
        
        # Contar arquivos gerados
        for nome_dir, caminho_dir in [
            ("tickets_completos", self.dir_tickets_completos),
            ("tickets_6_meses", self.dir_tickets_6_meses),
            ("metricas_csv", self.dir_metricas_csv)
        ]:
            if caminho_dir.exists():
                arquivos = list(caminho_dir.glob("*.csv"))
                relatorio["arquivos_gerados"][nome_dir] = {
                    "quantidade": len(arquivos),
                    "arquivos": [arquivo.name for arquivo in arquivos]
                }
            else:
                relatorio["arquivos_gerados"][nome_dir] = {
                    "quantidade": 0,
                    "arquivos": []
                }
        
        return relatorio


def main():
    """Função principal do pipeline."""
    print("=" * 80)
    print("PIPELINE DE EXTRAÇÃO E ANÁLISE DE DADOS GLPI")
    print("=" * 80)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Criar e executar o orquestrador
    orquestrador = PipelineOrchestrator()
    
    try:
        # Executar pipeline
        sucesso = orquestrador.executar_pipeline()
        
        # Gerar relatório
        relatorio = orquestrador.gerar_relatorio_execucao()
        
        # Exibir resultado final
        print("\n" + "=" * 80)
        if sucesso:
            print("RESULTADO: PIPELINE EXECUTADO COM SUCESSO!")
            print("=" * 80)
            print("\nResumo dos arquivos gerados:")
            for categoria, info in relatorio["arquivos_gerados"].items():
                print(f"  • {categoria}: {info['quantidade']} arquivos")
        else:
            print("RESULTADO: PIPELINE FALHOU!")
            print("=" * 80)
            print("Verifique os logs acima para detalhes dos erros.")
        
        print(f"\nConcluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Retornar código de saída apropriado
        sys.exit(0 if sucesso else 1)
        
    except KeyboardInterrupt:
        print("\n[INTERROMPIDO] Pipeline cancelado pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Erro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()