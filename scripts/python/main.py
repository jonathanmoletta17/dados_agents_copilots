#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE DE ANÁLISE GLPI - SCRIPT PRINCIPAL
==========================================

Script principal que coordena todo o pipeline de análise de tickets do GLPI.
Executa sequencialmente os três estágios principais:

1. Extração de dados da API GLPI
2. Filtro dos dados (últimos 6 meses)
3. Geração de métricas e relatórios

Este script:
- Verifica a existência de todos os scripts necessários
- Valida dependências Python
- Executa cada etapa em sequência
- Monitora o progresso e trata erros
- Fornece relatório final do pipeline

Funcionalidades:
- Verificação automática de dependências
- Execução sequencial com tratamento de erros
- Logs detalhados de cada etapa
- Relatório final de execução
- Interrupção segura em caso de falha

Autor: Sistema Automatizado
Data: 2025-10-29
Versão: 3.0
"""

import subprocess
import sys
import os
from datetime import datetime

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class PipelineGLPI:
    """
    Classe principal para coordenar o pipeline de análise GLPI.
    
    Esta classe gerencia a execução sequencial de todos os scripts
    necessários para extrair, filtrar e analisar dados do GLPI.
    
    Attributes:
        scripts (list): Lista de scripts a serem executados
        dependencias (list): Lista de dependências Python necessárias
    """
    
    def __init__(self):
        """
        Inicializa o pipeline com configurações dos scripts e dependências.
        """
        # Definir scripts do pipeline
        self.scripts = [
            {
                'numero': 1,
                'nome': 'Extração de Dados',
                'arquivo': 'extrair_dados_api_glpi_com_filtro_data.py',
                'descricao': 'Extrai tickets da API GLPI com filtro de data'
            },
            {
                'numero': 2,
                'nome': 'Filtro de Dados',
                'arquivo': 'filtrar_ultimos_6_meses.py',
                'descricao': 'Filtra dados para os últimos 6 meses'
            },
            {
                'numero': 3,
                'nome': 'Geração de Métricas',
                'arquivo': 'extrair_metricas_tickets.py',
                'descricao': 'Gera métricas e relatórios detalhados'
            }
        ]
        
        # Dependências necessárias
        self.dependencias = ['pandas', 'requests']

    def verificar_scripts(self):
        """
        Verifica se todos os scripts necessários existem.
        
        Returns:
            bool: True se todos os scripts existem, False caso contrário
        """
        print("[VERIFICACAO] Verificando existência dos scripts...")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_faltando = []
        
        for script in self.scripts:
            caminho_script = os.path.join(script_dir, script['arquivo'])
            if not os.path.exists(caminho_script):
                print(f"[ERRO] Script não encontrado: {script['arquivo']}")
                scripts_faltando.append(script['arquivo'])
            else:
                print(f"[OK] {script['arquivo']} - OK")
        
        if not scripts_faltando:
            print("[OK] Todos os scripts foram encontrados!\n")
            return True
        else:
            return False

    def verificar_dependencias(self):
        """
        Verifica se todas as dependências Python estão instaladas.
        
        Returns:
            bool: True se todas as dependências estão disponíveis, False caso contrário
        """
        print("[VERIFICACAO] Verificando dependências Python...")
        
        dependencias_faltando = []
        
        for dep in self.dependencias:
            try:
                __import__(dep)
                print(f"[OK] {dep} - OK")
            except ImportError:
                print(f"[ERRO] {dep} não está instalado!")
                dependencias_faltando.append(dep)
        
        if not dependencias_faltando:
            print("[OK] Todas as dependências estão disponíveis!\n")
            return True
        else:
            return False

    def executar_script(self, script_info):
        """
        Executa um script individual do pipeline.
        
        Args:
            script_info (dict): Informações do script a ser executado
            
        Returns:
            bool: True se execução bem-sucedida, False caso contrário
        """
        numero_etapa = script_info['numero']
        nome = script_info['nome']
        arquivo = script_info['arquivo']
        descricao = script_info['descricao']
        
        print("=" * 80)
        print(f"[ETAPA {numero_etapa}] {nome.upper()}")
        print("=" * 80)
        print(f"[INFO] {descricao}")
        print(f"[SCRIPT] {arquivo}")
        print()
        
        try:
            # Obter diretório do script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            caminho_script = os.path.join(script_dir, arquivo)
            
            # Executar script
            inicio = datetime.now()
            
            resultado = subprocess.run(
                [sys.executable, caminho_script],
                cwd=script_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            fim = datetime.now()
            duracao = fim - inicio
            
            # Verificar resultado
            if resultado.returncode == 0:
                print(f"\n[SUCESSO] Etapa {numero_etapa} concluída com sucesso!")
                print(f"[TEMPO] Duração: {duracao}")
                
                # Mostrar saída se houver
                if resultado.stdout.strip():
                    print(f"[SAIDA] {resultado.stdout.strip()}")
                
                return True
            else:
                print(f"\n[ERRO] ERRO na execução do script!")
                print(f"[CODIGO] Código de saída: {resultado.returncode}")
                print(f"[TEMPO] Duração: {duracao}")
                
                if resultado.stderr:
                    print(f"[ERRO] {resultado.stderr}")
                if resultado.stdout:
                    print(f"[SAIDA] {resultado.stdout}")
                
                return False
                
        except Exception as e:
            print(f"\n[ERRO] Erro inesperado ao executar {script_info['arquivo']}: {e}")
            return False

    def executar_pipeline(self):
        """
        Executa todo o pipeline de análise.
        
        Returns:
            bool: True se pipeline executado com sucesso, False caso contrário
        """
        inicio_pipeline = datetime.now()
        
        print("=" * 80)
        print("[INICIO] INICIANDO PIPELINE DE ANÁLISE GLPI")
        print("=" * 80)
        print("[INFO] Este processo irá:")
        print("   1. Extrair dados da API GLPI")
        print("   2. Filtrar dados dos últimos 6 meses")
        print("   3. Gerar métricas e relatórios")
        print()
        
        # Executar cada script em sequência
        for i, script in enumerate(self.scripts, 1):
            sucesso = self.executar_script(script)
            
            if not sucesso:
                print(f"\n[ERRO] Pipeline interrompido na etapa {i}")
                return False
        
        # Pipeline concluído com sucesso
        fim_pipeline = datetime.now()
        duracao_total = fim_pipeline - inicio_pipeline
        
        print("\n" + "=" * 80)
        print("[SUCESSO] PIPELINE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        print("[RESUMO] Todas as etapas foram executadas com sucesso:")
        print("   [OK] Dados extraídos da API GLPI")
        print("   [OK] Dados filtrados (últimos 6 meses)")
        print("   [OK] Métricas e relatórios gerados")
        print()
        print(f"[TEMPO] Duração total: {duracao_total}")
        print(f"[CONCLUSAO] Concluído em: {fim_pipeline.strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 80)
        
        return True

def main():
    """
    Função principal do pipeline.
    
    Coordena a verificação de dependências e execução do pipeline completo.
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        # Inicializar pipeline
        pipeline = PipelineGLPI()
        
        # Verificar dependências
        if not pipeline.verificar_dependencias():
            print("[ERRO] Dependências não atendidas. Instale as dependências necessárias.")
            return False
        
        # Verificar scripts
        if not pipeline.verificar_scripts():
            print("[ERRO] Scripts necessários não encontrados.")
            return False
        
        # Executar pipeline
        sucesso = pipeline.executar_pipeline()
        
        if sucesso:
            return True
        else:
            print("[ERRO] Pipeline falhou. Verifique os logs acima.")
            return False
            
    except KeyboardInterrupt:
        print("\n\n[AVISO] Execução cancelada pelo usuário.")
        return False
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        sys.exit(1)