#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ATUALIZADOR COMPLETO DE DADOS GLPI
=====================================

Script principal unificado para atualizar TODOS os dados do GLPI:
- Tickets completos (toda a base histórica)
- Tickets dos últimos 6 meses (dados recentes)
- Métricas e análises
- Históricos de tickets
- Exportação para SharePoint/banco de dados

ESTE É O ÚNICO SCRIPT QUE VOCÊ PRECISA EXECUTAR

Autor: Sistema de Análise GLPI - Casa Civil RS
Data: 2025-11-16
"""

import os
import sys
import json
import time
import logging
import subprocess
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('atualizacao_dados_glpi.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AtualizadorDadosGLPI:
    """
    Classe principal que orquestra a atualização completa dos dados GLPI.
    
    Responsável por:
    1. Extrair tickets da API GLPI
    2. Gerar métricas e análises
    3. Atualizar históricos
    4. Preparar dados para SharePoint
    """
    
    def __init__(self):
        """Inicializa o atualizador com configurações e caminhos."""
        self.diretorio_base = Path(__file__).parent
        self.diretorio_dados = self.diretorio_base / "dados"
        self.diretorio_scripts = self.diretorio_base / "python"
        
        # Configurar estrutura de diretórios
        self.configurar_diretorios()
        
        # Arquivos principais
        self.arquivos_esperados = {
            'tickets_completos': self.diretorio_dados / 'tickets_completos' / 'todos_tickets_atual.xlsx',
            'tickets_6_meses': self.diretorio_dados / 'tickets_6_meses' / 'tickets_ultimos_6_meses_atual.xlsx',
            'metricas': self.diretorio_dados / 'metricas_xlsx',
            'historicos': self.diretorio_dados / 'historicos'
        }
        
        logger.info("🚀 Inicializando Atualizador Completo de Dados GLPI")
        logger.info(f"📁 Diretório base: {self.diretorio_base}")
    
    def configurar_diretorios(self):
        """Cria estrutura de diretórios necessária."""
        diretorios_necessarios = [
            self.diretorio_dados,
            self.diretorio_dados / 'tickets_completos',
            self.diretorio_dados / 'tickets_6_meses',
            self.diretorio_dados / 'metricas_xlsx',
            self.diretorio_dados / 'historicos'
        ]
        
        for diretorio in diretorios_necessarios:
            diretorio.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Diretório verificado: {diretorio}")
    
    def executar_script_python(self, nome_script: str, descricao: str) -> bool:
        """
        Executa um script Python e retorna sucesso/erro.
        
        Args:
            nome_script: Nome do script (sem path)
            descricao: Descrição para logs
            
        Returns:
            True se executou com sucesso, False caso contrário
        """
        caminho_script = self.diretorio_scripts / nome_script
        
        if not caminho_script.exists():
            logger.error(f"❌ Script não encontrado: {caminho_script}")
            return False
        
        try:
            logger.info(f"🔄 Executando: {descricao}")
            logger.info(f"📄 Script: {nome_script}")
            
            # Executar o script
            resultado = subprocess.run(
                [sys.executable, str(caminho_script)],
                cwd=str(self.diretorio_scripts),
                capture_output=True,
                text=True,
                encoding='latin-1',
                errors='replace'
            )
            
            if resultado.returncode == 0:
                logger.info(f"✅ {descricao} - SUCESSO")
                if resultado.stdout:
                    logger.debug(f"Saída: {resultado.stdout[:200]}...")
                return True
            else:
                logger.error(f"❌ {descricao} - ERRO")
                if resultado.stderr:
                    logger.error(f"Erro: {resultado.stderr[:500]}...")
                return False
                
        except Exception as e:
            logger.error(f"❌ {descricao} - EXCEÇÃO: {e}")
            return False
    
    def verificar_arquivos_gerados(self) -> Dict[str, bool]:
        """
        Verifica se todos os arquivos esperados foram gerados.
        
        Returns:
            Dict com status de cada arquivo
        """
        logger.info("🔍 Verificando arquivos gerados...")
        
        status_arquivos = {}
        
        # Verificar tickets completos
        if self.arquivos_esperados['tickets_completos'].exists():
            tamanho = self.arquivos_esperados['tickets_completos'].stat().st_size
            status_arquivos['tickets_completos'] = tamanho > 1000  # Mais de 1KB
            logger.info(f"📊 Tickets completos: {'✅' if status_arquivos['tickets_completos'] else '❌'} ({tamanho} bytes)")
        else:
            status_arquivos['tickets_completos'] = False
            logger.warning("❌ Arquivo tickets_completos não encontrado")
        
        # Verificar tickets 6 meses
        if self.arquivos_esperados['tickets_6_meses'].exists():
            tamanho = self.arquivos_esperados['tickets_6_meses'].stat().st_size
            status_arquivos['tickets_6_meses'] = tamanho > 1000
            logger.info(f"📊 Tickets 6 meses: {'✅' if status_arquivos['tickets_6_meses'] else '❌'} ({tamanho} bytes)")
        else:
            status_arquivos['tickets_6_meses'] = False
            logger.warning("❌ Arquivo tickets_6_meses não encontrado")
        
        # Verificar métricas
        arquivos_metricas = list(self.arquivos_esperados['metricas'].glob("*.xlsx"))
        status_arquivos['metricas'] = len(arquivos_metricas) > 0
        logger.info(f"📊 Arquivos de métricas: {'✅' if status_arquivos['metricas'] else '❌'} ({len(arquivos_metricas)} arquivos)")
        
        # Verificar históricos
        arquivos_historicos = list(self.arquivos_esperados['historicos'].glob("*.xlsx"))
        status_arquivos['historicos'] = len(arquivos_historicos) > 0
        logger.info(f"📊 Arquivos de históricos: {'✅' if status_arquivos['historicos'] else '❌'} ({len(arquivos_historicos)} arquivos)")
        
        return status_arquivos
    
    def etapa_extracao_tickets_completos(self) -> bool:
        """Executa extração de todos os tickets (base completa)."""
        logger.info("\n" + "="*60)
        logger.info("📋 ETAPA 1: EXTRAÇÃO DE TICKETS COMPLETOS")
        logger.info("="*60)
        
        return self.executar_script_python(
            'extrair_todos_tickets.py',
            'Extração completa de todos os tickets do GLPI'
        )
    
    def etapa_extracao_tickets_6_meses(self) -> bool:
        """Executa extração de tickets dos últimos 6 meses."""
        logger.info("\n" + "="*60)
        logger.info("📅 ETAPA 2: EXTRAÇÃO DE TICKETS DOS ÚLTIMOS 6 MESES")
        logger.info("="*60)
        
        # Verificar se existe script específico para 6 meses
        script_6_meses = self.diretorio_scripts / 'extrair_tickets_6meses.py'
        if script_6_meses.exists():
            return self.executar_script_python(
                'extrair_tickets_6meses.py',
                'Extração de tickets dos últimos 6 meses'
            )
        else:
            logger.info("ℹ️ Usando filtro de 6 meses no extrator principal")
            return True  # Será tratado pelo extrair_todos_tickets.py
    
    def etapa_gerar_metricas(self) -> bool:
        """Executa geração de métricas e análises."""
        logger.info("\n" + "="*60)
        logger.info("📊 ETAPA 3: GERAÇÃO DE MÉTRICAS E ANÁLISES")
        logger.info("="*60)
        
        return self.executar_script_python(
            'extrair_metricas_tickets_otimizado.py',
            'Geração de métricas e análises detalhadas'
        )
    
    def etapa_atualizar_historicos(self) -> bool:
        """Executa atualização de históricos de tickets."""
        logger.info("\n" + "="*60)
        logger.info("📜 ETAPA 4: ATUALIZAÇÃO DE HISTÓRICOS")
        logger.info("="*60)
        
        # Tentar primeiro a versão completa
        script_historico = self.diretorio_scripts / 'endpoints' / 'historico_tickets_api.py'
        if script_historico.exists():
            sucesso = self.executar_script_python(
                'endpoints/historico_tickets_api.py',
                'Atualização de históricos de tickets'
            )
            if sucesso:
                return True
        
        # Fallback: usar versão simplificada
        script_historico_simples = self.diretorio_scripts / 'endpoints' / 'historico_tickets_simples.py'
        if script_historico_simples.exists():
            logger.info("📋 Usando versão simplificada de históricos...")
            return self.executar_script_python(
                'endpoints/historico_tickets_simples.py',
                'Geração de históricos simplificados'
            )
        else:
            logger.info("ℹ️ Scripts de históricos não encontrados, pulando etapa")
            return True
    
    def etapa_preparar_sharepoint(self) -> bool:
        """Prepara dados para exportação para SharePoint."""
        logger.info("\n" + "="*60)
        logger.info("☁️ ETAPA 5: PREPARAÇÃO PARA SHAREPOINT/INTEGRAÇÃO")
        logger.info("="*60)
        
        try:
            # Verificar arquivos principais
            arquivos_principais = self.verificar_arquivos_gerados()
            
            # Criar resumo de exportação
            resumo_export = {
                'data_atualizacao': datetime.now().isoformat(),
                'arquivos_gerados': {
                    k: str(v) if isinstance(v, Path) else v 
                    for k, v in self.arquivos_esperados.items()
                },
                'status': arquivos_principais
            }
            
            # Salvar resumo
            arquivo_resumo = self.diretorio_dados / 'resumo_exportacao.json'
            with open(arquivo_resumo, 'w', encoding='utf-8') as f:
                json.dump(resumo_export, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Resumo de exportação salvo: {arquivo_resumo}")
            
            # Criar arquivo consolidado para SharePoint se possível
            self.criar_arquivo_consolidado_sharepoint()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na preparação para SharePoint: {e}")
            return False
    
    def criar_arquivo_consolidado_sharepoint(self):
        """Cria arquivo consolidado para fácil importação no SharePoint."""
        try:
            logger.info("📦 Criando arquivo consolidado para SharePoint...")
            
            # Carregar tickets completos
            df_tickets = pd.read_excel(self.arquivos_esperados['tickets_completos'])
            
            # Adicionar metadados
            df_tickets['data_atualizacao'] = datetime.now().date()
            df_tickets['fonte_dados'] = 'GLPI API'
            df_tickets['versao_script'] = '1.0'
            
            # Salvar versão consolidada
            arquivo_consolidado = self.diretorio_dados / 'tickets_consolidado_sharepoint.xlsx'
            df_tickets.to_excel(arquivo_consolidado, index=False)
            
            logger.info(f"✅ Arquivo consolidado criado: {arquivo_consolidado}")
            logger.info(f"📊 Total de registros: {len(df_tickets)}")
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível criar arquivo consolidado: {e}")
    
    def executar_atualizacao_completa(self) -> Dict[str, any]:
        """
        Executa o processo completo de atualização dos dados GLPI.
        
        Returns:
            Dict com resultado da execução
        """
        inicio_execucao = datetime.now()
        logger.info("🚀 INICIANDO ATUALIZAÇÃO COMPLETA DOS DADOS GLPI")
        logger.info("="*70)
        
        resultado = {
            'inicio': inicio_execucao,
            'etapas': {},
            'sucesso': False,
            'arquivos_gerados': {}
        }
        
        try:
            # Etapa 1: Extrair tickets completos
            resultado['etapas']['tickets_completos'] = self.etapa_extracao_tickets_completos()
            
            # Etapa 2: Extrair tickets 6 meses
            resultado['etapas']['tickets_6_meses'] = self.etapa_extracao_tickets_6_meses()
            
            # Etapa 3: Gerar métricas
            resultado['etapas']['metricas'] = self.etapa_gerar_metricas()
            
            # Etapa 4: Atualizar históricos
            resultado['etapas']['historicos'] = self.etapa_atualizar_historicos()
            
            # Etapa 5: Preparar SharePoint
            resultado['etapas']['sharepoint'] = self.etapa_preparar_sharepoint()
            
            # Verificar arquivos finais
            resultado['arquivos_gerados'] = self.verificar_arquivos_gerados()
            
            # Avaliar sucesso geral
            etapas_obrigatorias = ['tickets_completos', 'tickets_6_meses', 'metricas']
            resultado['sucesso'] = all(resultado['etapas'].get(etapa, False) for etapa in etapas_obrigatorias)
            
            # Tempo total de execução
            fim_execucao = datetime.now()
            resultado['tempo_execucao'] = fim_execucao - inicio_execucao
            
            # Relatório final
            self.gerar_relatorio_final(resultado)
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO NA ATUALIZAÇÃO: {e}")
            resultado['erro_critico'] = str(e)
            return resultado
    
    def gerar_relatorio_final(self, resultado: Dict):
        """Gera relatório final da execução."""
        logger.info("\n" + "="*70)
        logger.info("📋 RELATÓRIO FINAL DA ATUALIZAÇÃO")
        logger.info("="*70)
        
        # Resumo de etapas
        logger.info("📊 RESUMO DAS ETAPAS:")
        for etapa, sucesso in resultado['etapas'].items():
            status = "✅ SUCESSO" if sucesso else "❌ FALHA"
            logger.info(f"   {etapa}: {status}")
        
        # Arquivos gerados
        logger.info("\n📁 ARQUIVOS GERADOS:")
        for tipo, status in resultado['arquivos_gerados'].items():
            logger.info(f"   {tipo}: {'✅' if status else '❌'}")
        
        # Tempo de execução
        if 'tempo_execucao' in resultado:
            logger.info(f"\n⏱️ TEMPO TOTAL: {resultado['tempo_execucao']}")
        
        # Resultado final
        if resultado['sucesso']:
            logger.info("\n🎉 ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
            logger.info("📊 Todos os dados foram atualizados e estão prontos para uso.")
        else:
            logger.warning("\n⚠️ ATUALIZAÇÃO FINALIZADA COM ALERTAS")
            logger.info("📋 Verifique o log para detalhes das etapas que falharam.")
        
        logger.info("="*70)


def main():
    """
    Função principal - ponto de entrada único para atualização dos dados GLPI.
    """
    print("🔄 ATUALIZADOR COMPLETO DE DADOS GLPI")
    print("="*50)
    print("Este script irá:")
    print("  📋 Extrair todos os tickets (base completa)")
    print("  📅 Extrair tickets dos últimos 6 meses")
    print("  📊 Gerar métricas e análises")
    print("  📜 Atualizar históricos")
    print("  ☁️ Preparar dados para SharePoint")
    print()
    
    # Confirmar execução
    try:
        resposta = input("Deseja continuar? (s/n): ").lower().strip()
        if resposta != 's':
            print("❌ Operação cancelada.")
            return
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário.")
        return
    
    # Executar atualização
    atualizador = AtualizadorDadosGLPI()
    resultado = atualizador.executar_atualizacao_completa()
    
    # Resultado final
    if resultado['sucesso']:
        print("\n🎉 Dados atualizados com sucesso!")
        print("📊 Seus dados estão prontos para o SharePoint.")
        sys.exit(0)
    else:
        print("\n⚠️ Atualização finalizada com alertas.")
        print("📋 Verifique o log: atualizacao_dados_glpi.log")
        sys.exit(1)


if __name__ == "__main__":
    main()