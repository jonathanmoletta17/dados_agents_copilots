#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILTRO DE DADOS - ÚLTIMOS 6 MESES
==================================

Script para filtrar dados de tickets do GLPI para os últimos 6 meses.
Localiza o arquivo CSV mais recente e gera uma versão filtrada.

Este script:
1. Localiza o arquivo CSV mais recente na pasta tickets_completos
2. Filtra os dados para os últimos 6 meses baseado na data de abertura
3. Gera um novo arquivo CSV na pasta tickets_6_meses

Funcionalidades:
- Detecção automática do arquivo mais recente
- Filtro inteligente por período de 6 meses
- Validação de dados e tratamento de erros
- Relatório detalhado do processamento

Autor: Sistema de Análise GLPI
Data: 2024
"""

import pandas as pd
import os
import glob
import sys
from datetime import datetime, timedelta

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def encontrar_arquivo_mais_recente(diretorio, padrao="*.csv"):
    """
    Encontra o arquivo CSV mais recente no diretório especificado.
    
    Args:
        diretorio (str): Caminho do diretório para buscar
        padrao (str): Padrão de arquivo a buscar (default: "*.csv")
        
    Returns:
        str: Caminho do arquivo mais recente ou None se não encontrado
        
    Raises:
        FileNotFoundError: Se o diretório não existir
        ValueError: Se nenhum arquivo for encontrado
    """
    if not os.path.exists(diretorio):
        raise FileNotFoundError(f"Diretório não encontrado: {diretorio}")
    
    # Buscar todos os arquivos CSV no diretório
    arquivos = glob.glob(os.path.join(diretorio, padrao))
    
    if not arquivos:
        raise ValueError(f"Nenhum arquivo {padrao} encontrado em {diretorio}")
    
    # Encontrar o arquivo mais recente baseado na data de modificação
    arquivo_mais_recente = max(arquivos, key=os.path.getmtime)
    
    print(f"[ARQUIVO] Arquivo mais recente encontrado: {os.path.basename(arquivo_mais_recente)}")
    print(f"[CAMINHO] {arquivo_mais_recente}")
    
    return arquivo_mais_recente

def calcular_periodo_6_meses():
    """
    Calcula o período de 6 meses a partir da data atual.
    
    Returns:
        tuple: (data_inicio, data_fim) no formato datetime
    """
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=180)  # Aproximadamente 6 meses
    
    print(f"[PERIODO] Filtrando dados de {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")
    
    return data_inicio, data_fim

def filtrar_dados_6_meses(arquivo_entrada, diretorio_saida):
    """
    Filtra os dados do arquivo CSV para os últimos 6 meses.
    
    Args:
        arquivo_entrada (str): Caminho do arquivo CSV de entrada
        diretorio_saida (str): Diretório onde salvar o arquivo filtrado
        
    Returns:
        str: Caminho do arquivo filtrado gerado
        
    Raises:
        Exception: Se houver erro no processamento dos dados
    """
    try:
        print(f"[CARREGANDO] Carregando dados de: {os.path.basename(arquivo_entrada)}")
        
        # Carregar dados
        df = pd.read_csv(arquivo_entrada, encoding='utf-8')
        total_registros = len(df)
        print(f"[DADOS] Total de registros carregados: {total_registros:,}")
        
        # Verificar se a coluna de data existe
        if 'Data_abertura' not in df.columns:
            raise ValueError("Coluna 'Data_abertura' não encontrada no arquivo")
        
        # Converter coluna de data para datetime
        print("[PROCESSANDO] Convertendo datas...")
        df['Data_abertura'] = pd.to_datetime(df['Data_abertura'], errors='coerce')
        
        # Verificar registros com data inválida
        registros_invalidos = df['Data_abertura'].isna().sum()
        if registros_invalidos > 0:
            print(f"[AVISO] {registros_invalidos} registros com data inválida serão removidos")
            df = df.dropna(subset=['Data_abertura'])
        
        # Calcular período de 6 meses
        data_inicio, data_fim = calcular_periodo_6_meses()
        
        # Filtrar dados
        print("[FILTRANDO] Aplicando filtro de 6 meses...")
        df_filtrado = df[
            (df['Data_abertura'] >= data_inicio) & 
            (df['Data_abertura'] <= data_fim)
        ]
        
        registros_filtrados = len(df_filtrado)
        percentual = (registros_filtrados / total_registros) * 100 if total_registros > 0 else 0
        
        print(f"[RESULTADO] Registros após filtro: {registros_filtrados:,} ({percentual:.1f}%)")
        
        # Criar diretório de saída se não existir
        os.makedirs(diretorio_saida, exist_ok=True)
        
        # Gerar nome do arquivo de saída com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo_saida = f"tickets_6_meses_{timestamp}.csv"
        caminho_saida = os.path.join(diretorio_saida, nome_arquivo_saida)
        
        # Salvar dados filtrados
        print(f"[SALVANDO] Salvando dados filtrados em: {nome_arquivo_saida}")
        df_filtrado.to_csv(caminho_saida, index=False, encoding='utf-8')
        
        # Verificar se o arquivo foi criado
        if os.path.exists(caminho_saida):
            tamanho_arquivo = os.path.getsize(caminho_saida) / (1024 * 1024)  # MB
            print(f"[SUCESSO] Arquivo criado com sucesso!")
            print(f"[ARQUIVO] {caminho_saida}")
            print(f"[TAMANHO] {tamanho_arquivo:.2f} MB")
        else:
            raise Exception("Erro ao criar arquivo de saída")
        
        return caminho_saida
        
    except Exception as e:
        print(f"[ERRO] Erro ao filtrar dados: {e}")
        raise

def main():
    """
    Função principal do script de filtragem.
    
    Coordena todo o processo de filtragem dos dados para os últimos 6 meses.
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        print("=" * 80)
        print("[INICIO] FILTRO DE DADOS - ÚLTIMOS 6 MESES")
        print("=" * 80)
        print("[INFO] Este script irá:")
        print("   1. Localizar o arquivo CSV mais recente")
        print("   2. Filtrar dados dos últimos 6 meses")
        print("   3. Gerar novo arquivo filtrado")
        print()
        
        inicio = datetime.now()
        
        # Definir diretórios
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dados_dir = os.path.join(script_dir, '..', 'dados')
        
        diretorio_entrada = os.path.join(dados_dir, 'tickets_completos')
        diretorio_saida = os.path.join(dados_dir, 'tickets_6_meses')
        
        print(f"[CONFIG] Diretório de entrada: {diretorio_entrada}")
        print(f"[CONFIG] Diretório de saída: {diretorio_saida}")
        print()
        
        # Encontrar arquivo mais recente
        print("[ETAPA 1] Localizando arquivo mais recente...")
        arquivo_entrada = encontrar_arquivo_mais_recente(diretorio_entrada)
        print()
        
        # Filtrar dados
        print("[ETAPA 2] Filtrando dados...")
        arquivo_saida = filtrar_dados_6_meses(arquivo_entrada, diretorio_saida)
        print()
        
        # Relatório final
        fim = datetime.now()
        duracao = fim - inicio
        
        print("=" * 80)
        print("[SUCESSO] FILTRO CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        print("[RESUMO] Processo executado com sucesso:")
        print(f"   [OK] Arquivo processado: {os.path.basename(arquivo_entrada)}")
        print(f"   [OK] Arquivo gerado: {os.path.basename(arquivo_saida)}")
        print(f"   [OK] Período filtrado: Últimos 6 meses")
        print()
        print(f"[TEMPO] Duração total: {duracao}")
        print(f"[CONCLUSAO] Concluído em: {fim.strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 80)
        
        return True
        
    except FileNotFoundError as e:
        print(f"[ERRO] Arquivo ou diretório não encontrado: {e}")
        return False
    except ValueError as e:
        print(f"[ERRO] Erro de valor: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        exit(1)