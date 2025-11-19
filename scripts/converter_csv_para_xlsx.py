#!/usr/bin/env python3
"""
Script para converter todos os arquivos CSV do projeto para XLSX
Mantém a estrutura de diretórios e cria arquivos XLSX correspondentes
"""

import pandas as pd
import os
from pathlib import Path
import glob

def converter_csv_para_xlsx(caminho_csv, caminho_xlsx):
    """
    Converte um arquivo CSV para XLSX
    """
    try:
        # Detecta o encoding do arquivo
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(caminho_csv, sep=';', encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            # Tenta com separador diferente
            for encoding in encodings:
                try:
                    df = pd.read_csv(caminho_csv, sep=',', encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
        
        if df is not None:
            # Salva como XLSX
            df.to_excel(caminho_xlsx, index=False)
            print(f"✅ Convertido: {os.path.basename(caminho_csv)} -> {os.path.basename(caminho_xlsx)}")
            return True
        else:
            print(f"❌ Erro ao converter: {caminho_csv}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {caminho_csv}: {e}")
        return False

def main():
    """
    Converte todos os arquivos CSV encontrados para XLSX
    """
    print("🔄 Iniciando conversão de CSV para XLSX")
    print("=" * 50)
    
    # Diretório base
    base_dir = Path("C:/Users/jonathan-moletta/OneDrive - Governo do Estado do Rio Grande do Sul/Área de Trabalho/BD_cau_sis/bd_cau/scripts")
    
    # Encontra todos os arquivos CSV
    arquivos_csv = list(base_dir.rglob("*.csv"))
    
    if not arquivos_csv:
        print("❌ Nenhum arquivo CSV encontrado")
        return
    
    print(f"📊 Encontrados {len(arquivos_csv)} arquivos CSV")
    
    total_convertidos = 0
    total_erros = 0
    
    for arquivo_csv in arquivos_csv:
        try:
            # Cria o caminho do arquivo XLSX
            arquivo_xlsx = arquivo_csv.with_suffix('.xlsx')
            
            # Converte o arquivo
            if converter_csv_para_xlsx(arquivo_csv, arquivo_xlsx):
                total_convertidos += 1
            else:
                total_erros += 1
                
        except Exception as e:
            print(f"❌ Erro ao processar {arquivo_csv}: {e}")
            total_erros += 1
    
    print("\n" + "=" * 50)
    print(f"📈 Resumo da conversão:")
    print(f"✅ Convertidos com sucesso: {total_convertidos}")
    print(f"❌ Erros: {total_erros}")
    print(f"📊 Total processado: {len(arquivos_csv)}")
    
    if total_convertidos == len(arquivos_csv):
        print("\n🎉 Todos os arquivos foram convertidos com sucesso!")
    else:
        print(f"\n⚠️  {total_erros} arquivos não puderam ser convertidos")

if __name__ == "__main__":
    main()