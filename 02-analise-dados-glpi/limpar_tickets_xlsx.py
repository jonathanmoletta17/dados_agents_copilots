#!/usr/bin/env python3
"""
Script de limpeza de tickets GLPI - Versão XLSX
Remove textos de formulário GLPI mantendo apenas o conteúdo relevante
"""

import pandas as pd
import re
import sys
from pathlib import Path

def limpar_formulario_glpi(texto):
    """
    Remove textos de estrutura de formulário GLPI, mantendo apenas o conteúdo
    """
    if pd.isna(texto) or not isinstance(texto, str):
        return texto
    
    # Padrões de formulário GLPI para remover
    padroes_formulario = [
        # Headers de formulário
        r'Dados do formulário.*?Dados Gerais\d+\)',
        r'Dados do formulário',
        r'Dados Gerais\d+\)',
        
        # Labels de campos seguidos por números ou espaços
        r'TIPO\s*:\s*\d+\s*\)',
        r'ORGANIZAÇÃO\s*:\s*\d+\s*\)',
        r'DATA\s*:\s*\d+\s*\)',
        r'HORA\s*:\s*\d+\s*\)',
        r'RESPONSÁVEL\s*:\s*\d+\s*\)',
        r'DEPARTAMENTO\s*:\s*\d+\s*\)',
        r'LOCAL\s*:\s*\d+\s*\)',
        r'RAMAL\s*:\s*\d+\s*\)',
        r'ASSUNTO\s*:\s*\d+\s*\)',
        r'DESCRICAO\s*:\s*\d+\s*\)',
        r'PRIORIDADE\s*:\s*\d+\s*\)',
        r'CATEGORIA\s*:\s*\d+\s*\)',
        r'ORIGEM\s*:\s*\d+\s*\)',
        r'RECURSO\s*:\s*\d+\s*\)',
        r'FORNECEDOR\s*:\s*\d+\s*\)',
        
        # Números de ordem seguidos de parênteses
        r'\d+\)\s*',
        
        # Espaços múltiplos e quebras de linha extras
        r'\n{3,}',
        r' {2,}',
    ]
    
    texto_limpo = texto
    for padrao in padroes_formulario:
        texto_limpo = re.sub(padrao, ' ', texto_limpo, flags=re.IGNORECASE | re.MULTILINE)
    
    # Limpeza final
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo)  # Espaços múltiplos
    texto_limpo = re.sub(r'\n\s*\n', '\n\n', texto_limpo)  # Linhas vazias múltiplas
    texto_limpo = texto_limpo.strip()
    
    return texto_limpo if texto_limpo else texto

def normalizar_headers(df):
    """
    Normaliza os headers do DataFrame removendo acentos e caracteres especiais
    """
    novos_headers = {}
    for col in df.columns:
        novo_nome = col
        # Remove acentos e caracteres especiais
        novo_nome = re.sub(r'[áàâãä]', 'a', novo_nome)
        novo_nome = re.sub(r'[éèêë]', 'e', novo_nome)
        novo_nome = re.sub(r'[íìîï]', 'i', novo_nome)
        novo_nome = re.sub(r'[óòôõö]', 'o', novo_nome)
        novo_nome = re.sub(r'[úùûü]', 'u', novo_nome)
        novo_nome = re.sub(r'[ç]', 'c', novo_nome)
        novo_nome = re.sub(r'[ñ]', 'n', novo_nome)
        novo_nome = re.sub(r'[^\w\s]', '_', novo_nome)  # Substitui caracteres especiais por _
        novo_nome = re.sub(r'\s+', '_', novo_nome)  # Espaços por _
        novo_nome = novo_nome.upper().strip('_')
        
        if novo_nome != col:
            novos_headers[col] = novo_nome
    
    if novos_headers:
        df = df.rename(columns=novos_headers)
    
    return df

def processar_arquivo_xlsx(caminho_entrada, caminho_saida):
    """
    Processa arquivo XLSX removendo textos de formulário GLPI
    """
    try:
        print(f"Lendo arquivo: {caminho_entrada}")
        df = pd.read_excel(caminho_entrada)
        print(f"Total de tickets: {len(df)}")
        
        # Normaliza headers
        df = normalizar_headers(df)
        print("Headers normalizados")
        
        # Encontra coluna de descrição
        coluna_descricao = None
        for col in df.columns:
            if 'descricao' in col.lower() or 'description' in col.lower() or 'content' in col.lower():
                coluna_descricao = col
                break
        
        if coluna_descricao:
            print(f"Processando coluna de descrição: {coluna_descricao}")
            
            # Calcula estatísticas antes da limpeza
            total_chars_antes = df[coluna_descricao].astype(str).str.len().sum()
            print(f"Total de caracteres antes da limpeza: {total_chars_antes:,}")
            
            # Aplica limpeza
            df[coluna_descricao] = df[coluna_descricao].apply(limpar_formulario_glpi)
            
            # Calcula estatísticas depois da limpeza
            total_chars_depois = df[coluna_descricao].astype(str).str.len().sum()
            reducao = total_chars_antes - total_chars_depois
            percentual = (reducao / total_chars_antes) * 100 if total_chars_antes > 0 else 0
            
            print(f"Total de caracteres depois da limpeza: {total_chars_depois:,}")
            print(f"Redução: {reducao:,} caracteres ({percentual:.1f}%)")
            
            # Conta tickets com form structures
            tickets_com_form = df[coluna_descricao].str.contains(
                r'Dados do formulário|TIPO\s*:|ORGANIZAÇÃO\s*:', 
                case=False, na=False
            ).sum()
            print(f"Tickets com estruturas de formulário: {tickets_com_form}")
            
        else:
            print("Aviso: Não foi encontrada coluna de descrição")
            # Tenta aplicar limpeza em todas as colunas de texto
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(limpar_formulario_glpi)
        
        # Salva resultado em XLSX
        print(f"Salvando arquivo limpo: {caminho_saida}")
        df.to_excel(caminho_saida, index=False)
        
        # Adiciona estatísticas em uma segunda aba
        with pd.ExcelWriter(caminho_saida, mode='a', engine='openpyxl') as writer:
            estatisticas = pd.DataFrame({
                'Métrica': ['Total de Tickets', 'Caracteres (Antes)', 'Caracteres (Depois)', 
                           'Redução (Caracteres)', 'Redução (%)', 'Tickets com Formulário'],
                'Valor': [len(df), total_chars_antes if 'total_chars_antes' in locals() else 0,
                         total_chars_depois if 'total_chars_depois' in locals() else 0,
                         reducao if 'reducao' in locals() else 0,
                         f"{percentual:.1f}%" if 'percentual' in locals() else '0%',
                         tickets_com_form if 'tickets_com_form' in locals() else 0]
            })
            estatisticas.to_excel(writer, sheet_name='Estatísticas', index=False)
        
        print(f"Processamento concluído! Arquivo salvo: {caminho_saida}")
        return True
        
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        return False

def main():
    """
    Função principal
    """
    # Diretórios
    diretorio_raw = Path("data/raw")
    diretorio_processed = Path("data/processed")
    
    # Cria diretórios se não existirem
    diretorio_processed.mkdir(parents=True, exist_ok=True)
    
    # Encontra arquivo XLSX de entrada
    arquivos_xlsx = list(diretorio_raw.glob("*.xlsx"))
    
    if not arquivos_xlsx:
        print("Erro: Nenhum arquivo XLSX encontrado em data/raw/")
        print("Por favor, coloque o arquivo de tickets no formato XLSX em data/raw/")
        return
    
    # Usa o primeiro arquivo XLSX encontrado
    arquivo_entrada = arquivos_xlsx[0]
    arquivo_saida = diretorio_processed / f"{arquivo_entrada.stem}_limpo.xlsx"
    
    print(f"Processando arquivo: {arquivo_entrada.name}")
    
    # Processa o arquivo
    sucesso = processar_arquivo_xlsx(arquivo_entrada, arquivo_saida)
    
    if sucesso:
        print(f"\n✅ Limpeza concluída com sucesso!")
        print(f"📁 Arquivo de entrada: {arquivo_entrada}")
        print(f"📁 Arquivo de saída: {arquivo_saida}")
    else:
        print(f"\n❌ Erro durante o processamento")
        sys.exit(1)

if __name__ == "__main__":
    main()