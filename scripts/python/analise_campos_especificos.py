#!/usr/bin/env python3
"""
Análise específica dos campos numéricos encontrados no XLSX do ticket 10800
Autor: Assistant
Data: 2025-11-16
"""

import pandas as pd
import sys
import os

# Adicionar o diretório endpoints ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'endpoints'))

from mapeamento_glpi_campos import (
    MAPEAMENTO_CAMPOS_GLPi,
    MAPEAMENTO_ACOES_GLPi,
    MAPEAMENTO_ITEMTYPE_GLPi,
    interpretar_alteracao_completa
)

def analisar_xlsx_especifico():
    """Analisa especificamente os campos que você encontrou"""
    xlsx_path = "c:/Users/jonathan-moletta/OneDrive - Governo do Estado do Rio Grande do Sul/Área de Trabalho/BD_cau_sis/bd_cau/scripts/dados/historicos/historico_ticket_10800_20251116_164313.xlsx"
    
    if not os.path.exists(xlsx_path):
        print(f"Arquivo não encontrado: {xlsx_path}")
        return
    
    try:
        # Lê o XLSX
        df = pd.read_excel(xlsx_path)
        print(f"=== ANÁLISE DETALHADA DO TICKET 10800 ===")
        print(f"Total de registros de histórico: {len(df)}\n")
        
        print("Colunas disponíveis no XLSX:")
        for col in df.columns:
            print(f"  - {col}")
        print()
        
        # Identifica os campos numéricos baseado nas descrições textuais
        print("=== IDENTIFICANDO CAMPOS NUMÉRICOS PELOS NOMES ===")
        
        # Procura por campos que mencionam números nas descrições
        campo_64_mencoes = df[df['campo_modificado'].str.contains('Usuário atribuído|Usuario|User', case=False, na=False)]
        campo_65_mencoes = df[df['campo_modificado'].str.contains('Grupo atribuído|Grupo|Group', case=False, na=False)]
        campo_66_mencoes = df[df['campo_modificado'].str.contains('Ativo|Equipamento|Asset|Item', case=False, na=False)]
        
        print(f"Registros que parecem ser Campo 64 (Usuário): {len(campo_64_mencoes)}")
        print(f"Registros que parecem ser Campo 65 (Grupo): {len(campo_65_mencoes)}")
        print(f"Registros que parecem ser Campo 66 (Ativo): {len(campo_66_mencoes)}")
        
        print("\n=== ANÁLISE DOS CAMPOS QUE VOCÊ PERGUNTOU ===")
        
        # Análise específica dos campos que você mencionou
        campos_analisados = [
            ('Usuário atribuído', 64, 'User'),
            ('Grupo atribuído', 65, 'Group'), 
            ('Campo 150', 150, 'Campo Personalizado'),
            ('Campo geral', 0, 'Informação Geral')
        ]
        
        for nome_campo_texto, numero_campo, tipo_esperado in campos_analisados:
            registros = df[df['campo_modificado'] == nome_campo_texto]
            if len(registros) > 0:
                nome_campo_mapeado = MAPEAMENTO_CAMPOS_GLPi.get(numero_campo, f'Campo {numero_campo}')
                print(f"\n📝 '{nome_campo_texto}' → Campo {numero_campo}: {nome_campo_mapeado}")
                print(f"   Quantidade de alterações: {len(registros)}")
                
                # Mostra exemplos concretos
                print(f"   Exemplos de alterações:")
                for i, (_, registro) in enumerate(registros.head(3).iterrows()):
                    print(f"     {i+1}. De: '{registro['old_value']}' → Para: '{registro['new_value']}'")
                    print(f"        Usuário: {registro['user_name']}")
                    print(f"        Data: {registro['data_formatada']}")
                    print(f"        Tipo: {registro['tipo_alteracao']}")
                    
                    # Interpretação usando o mapeamento
                    interpretacao = interpretar_alteracao_completa(
                        registro['itemtype_link'],
                        registro['linked_action'],
                        numero_campo,  # Usa o número do campo que identificamos
                        str(registro['old_value']),
                        str(registro['new_value'])
                    )
                    print(f"        Significado: {interpretacao['descricao_completa']}")
                    print()
        
        print("\n=== DISTRIBUIÇÃO DE TIPOS DE AÇÃO ===")
        acoes_dist = df['linked_action'].value_counts()
        print("Distribuição de ações no histórico:")
        for acao, qtd in acoes_dist.items():
            nome_acao = MAPEAMENTO_ACOES_GLPi.get(acao, f'Ação {acao}')
            print(f"  {nome_acao} (ação {acao}): {qtd} vezes")
        
        print("\n=== DISTRIBUIÇÃO POR TIPO DE ITEM ===")
        itemtypes_dist = df['itemtype_link'].value_counts()
        print("Distribuição por tipo de item:")
        for itemtype, qtd in itemtypes_dist.items():
            nome_itemtype = MAPEAMENTO_ITEMTYPE_GLPi.get(itemtype, itemtype)
            print(f"  {nome_itemtype}: {qtd} alterações")
        
        print("\n=== LINHA DO TEMPO DAS PRINCIPAIS ALTERAÇÕES ===")
        # Mostra as 8 primeiras alterações cronológicas
        print("\nPrincipais alterações do ticket (ordem cronológica):")
        for i, (_, registro) in enumerate(df.head(8).iterrows()):
            print(f"  {i+1}. [{registro['id']}] {registro['tipo_alteracao']}")
            print(f"     Campo: {registro['campo_modificado']}")
            print(f"     De: '{registro['old_value']}' Para: '{registro['new_value']}'")
            print(f"     Usuário: {registro['user_name']}")
            print(f"     Data: {registro['data_formatada']}")
            print()
        
        print("\n=== RESUMO EXECUTIVO ===")
        print("O que os campos 64, 65, 66 significam para a análise deste ticket:")
        print("- Campo 64 (Usuário Associado): Mostra QUEM foi responsabilizado pelo chamado")
        print("- Campo 65 (Grupo Associado): Indica QUAL equipe ficou responsável")  
        print("- Campo 66 (Ativo Relacionado): Identifica QUAL equipamento está envolvido")
        print("\nEsses campos são fundamentais para entender a evolução e responsabilidade!")
        
    except Exception as e:
        print(f"Erro ao processar XLSX: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Executa a análise específica"""
    print("ANÁLISE ESPECÍFICA DOS CAMPOS NUMÉRICOS DO GLPI")
    print("=" * 60)
    print("Este script analisa os campos 64, 65, 66 que você identificou\n")
    
    analisar_xlsx_especifico()
    
    print("\n" + "=" * 60)
    print("ANÁLISE CONCLUÍDA")
    print("\nResumo dos campos que você perguntou:")
    print("- Campo 64: Usuário Associado (quem está responsável pelo chamado)")
    print("- Campo 65: Grupo Associado (qual equipe está responsável)")  
    print("- Campo 66: Ativo/Equipamento Relacionado (qual equipamento está envolvido)")
    print("\nEsses campos são essenciais para entender a evolução do chamado!")

if __name__ == "__main__":
    main()