#!/usr/bin/env python3
"""
Demonstração do sistema de mapeamento de campos GLPI
Autor: Assistant
Data: 2025-11-16
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Adicionar o diretório endpoints ao path para importar o mapeamento
sys.path.append(os.path.join(os.path.dirname(__file__), 'endpoints'))

from mapeamento_glpi_campos import (
    MAPEAMENTO_CAMPOS_GLPi,
    MAPEAMENTO_ACOES_GLPi, 
    MAPEAMENTO_ITEMTYPE_GLPi,
    interpretar_alteracao_completa
)

def demonstrar_mapeamento_basico():
    """Demonstra o mapeamento básico dos campos que você encontrou"""
    print("=== MAPEAMENTO DOS CAMPOS NUMÉRICOS ===\n")
    
    # Campos que você identificou no CSV
    campos_identificados = [64, 65, 66, 150, 52]
    
    print("Campos encontrados no seu CSV:")
    for campo in campos_identificados:
        descricao = MAPEAMENTO_CAMPOS_GLPi.get(campo, f'Campo desconhecido ({campo})')
        print(f"  Campo {campo}: {descricao}")
    
    print("\n=== EXEMPLOS DE AÇÕES ===")
    
    # Ações comuns que aparecem nos logs
    acoes_exemplos = [15, 12, 17, 0, 20]
    for acao in acoes_exemplos:
        descricao = MAPEAMENTO_ACOES_GLPi.get(acao, f'Ação desconhecida ({acao})')
        print(f"  Ação {acao}: {descricao}")

def demonstrar_interpretacao_dados():
    """Demonstra como interpretar os dados reais do seu XLSX"""
    print("\n=== INTERPRETAÇÃO DOS DADOS DO XLSX ===\n")
    
    # Exemplos baseados nos dados que você encontrou
    exemplos = [
        {
            'itemtype_link': 'User',
            'linked_action': 15,
            'id_search_option': 64,
            'old_value': '0',
            'new_value': '123'
        },
        {
            'itemtype_link': 'Group', 
            'linked_action': 12,
            'id_search_option': 65,
            'old_value': '45',
            'new_value': '0'
        },
        {
            'itemtype_link': 'Document',
            'linked_action': 17,
            'id_search_option': 66,
            'old_value': '',
            'new_value': 'Documento_123.pdf'
        }
    ]
    
    for i, exemplo in enumerate(exemplos, 1):
        print(f"Exemplo {i}:")
        interpretacao = interpretar_alteracao_completa(
            exemplo['itemtype_link'],
            exemplo['linked_action'],
            exemplo['id_search_option'],
            exemplo['old_value'],
            exemplo['new_value']
        )
        print(f"  {interpretacao}")
        print()

def analisar_xlsx_usuario():
    """Analisa o XLSX específico que você mencionou"""
    xlsx_path = "c:/Users/jonathan-moletta/OneDrive - Governo do Estado do Rio Grande do Sul/Área de Trabalho/BD_cau_sis/bd_cau/scripts/dados/historicos/historico_ticket_10800_20251116_164313.xlsx"
    
    if os.path.exists(xlsx_path):
        print(f"\n=== ANÁLISE DO ARQUIVO: {os.path.basename(xlsx_path)} ===\n")
        
        try:
            df = pd.read_excel(xlsx_path)
            print(f"Total de registros: {len(df)}")
            
            # Análise manual dos campos
            print("\nDistribuição de campos modificados:")
            campos_contagem = df['id_search_option'].value_counts().head(10)
            for campo, contagem in campos_contagem.items():
                nome_campo = MAPEAMENTO_CAMPOS_GLPi.get(campo, f'Campo {campo}')
                print(f"  {nome_campo}: {contagem} alterações")
            
            print("\nDistribuição de tipos de ação:")
            acoes_contagem = df['linked_action'].value_counts().head(10)
            for acao, contagem in acoes_contagem.items():
                nome_acao = MAPEAMENTO_ACOES_GLPi.get(acao, f'Ação {acao}')
                print(f"  {nome_acao}: {contagem} ocorrências")
            
            print("\nEntidades relacionadas:")
            itemtypes_contagem = df['itemtype_link'].value_counts().head(10)
            for itemtype, contagem in itemtypes_contagem.items():
                nome_itemtype = MAPEAMENTO_ITEMTYPE_GLPi.get(itemtype, itemtype)
                print(f"  {nome_itemtype}: {contagem} referências")
                
        except Exception as e:
            print(f"Erro ao analisar CSV: {e}")
    else:
        print(f"Arquivo não encontrado: {csv_path}")
        print("Verifique se o caminho está correto.")

def explicar_relevancia_campos():
    """Explica a relevância dos campos que você perguntou"""
    print("\n=== RELEVÂNCIA DOS CAMPOS PARA ANÁLISE ===\n")
    
    relevancia = {
        64: {
            'nome': 'Usuário Associado',
            'importancia': 'Crítico - Mostra quem foi atribuído ao chamado',
            'uso': 'Rastreamento de responsabilidade e carga de trabalho'
        },
        65: {
            'nome': 'Grupo Associado', 
            'importancia': 'Alto - Indica equipe responsável',
            'uso': 'Análise de distribuição por departamentos'
        },
        66: {
            'nome': 'Ativo/Equipamento Relacionado',
            'importancia': 'Alto - Identifica equipamentos envolvidos',
            'uso': 'Gestão de ativos e problemas recorrentes'
        },
        150: {
            'nome': 'Solução/Acompanhamento',
            'importancia': 'Crítico - Contém a resolução do chamado',
            'uso': 'Análise de qualidade do suporte'
        },
        52: {
            'nome': 'Data de Vencimento',
            'importancia': 'Médio - Impacta SLA e prioridades',
            'uso': 'Cumprimento de prazos e métricas de tempo'
        }
    }
    
    print("Relevância dos campos encontrados:")
    for campo_id, info in relevancia.items():
        print(f"\nCAMPO {campo_id}: {info['nome']}")
        print(f"  Importância: {info['importancia']}")
        print(f"  Uso: {info['uso']}")
    
    print("\n=== RELEVÂNCIA DOS CAMPOS DE RELACIONAMENTO ===\n")
    
    print("itemtype_link: Define QUAL entidade foi modificada")
    print("  - User: Mudanças em usuários (atribuições, remoções)")
    print("  - Group: Alterações em grupos (equipes responsáveis)")  
    print("  - Document: Anexos e documentações adicionadas/removidas")
    print("  - ITILFollowup: Acompanhamentos e atualizações")
    
    print("\nlinked_action: Define O QUE foi feito na entidade")
    print("  - 15: Adicionou/atribuiu uma entidade")
    print("  - 12: Removeu uma entidade")
    print("  - 17: Adicionou documento/anexo")
    print("  - 0: Atualização geral de informações")

def main():
    """Função principal que executa todas as demonstrações"""
    print("SISTEMA DE MAPEAMENTO GLPI - DEMONSTRAÇÃO")
    print("=" * 50)
    
    # 1. Mapeamento básico
    demonstrar_mapeamento_basico()
    
    # 2. Interpretação de dados
    demonstrar_interpretacao_dados()
    
    # 3. Análise do CSV real
    analisar_csv_usuario()
    
    # 4. Explicação da relevância
    explicar_relevancia_campos()
    
    print("\n" + "=" * 50)
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("\nPara usar o sistema com seus dados:")
    print("1. Importe o módulo: from endpoints.mapeamento_glpi_campos import *")
    print("2. Use interpretar_alteracao_completa() para interpretar linhas individuais")
    print("3. Use analisar_csv_completo() para analisar arquivos CSV inteiros")

if __name__ == "__main__":
    main()