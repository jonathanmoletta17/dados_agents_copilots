"""
Utilitário para gerenciamento de arquivos com backup e substituição
Evita acumulação infinita de arquivos com timestamp
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

class FileManager:
    """Gerenciador de arquivos com sistema de backup e substituição"""
    
    @staticmethod
    def salvar_com_backup(dados, caminho_arquivo: str, descricao: str = "arquivo") -> bool:
        """
        Salva arquivo com sistema de backup automático.
        
        Args:
            dados: DataFrame ou dados a serem salvos
            caminho_arquivo (str): Caminho do arquivo atual
            descricao (str): Descrição para logs
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            caminho = Path(caminho_arquivo)
            
            # Criar diretório se não existir
            caminho.parent.mkdir(parents=True, exist_ok=True)
            
            # Se arquivo atual existe, fazer backup
            if caminho.exists():
                arquivo_backup = caminho.with_name(caminho.stem + "_anterior" + caminho.suffix)
                shutil.copy2(caminho, arquivo_backup)
                print(f"[BACKUP] {descricao} anterior salvo como: {arquivo_backup.name}")
            
            # Salvar novo arquivo baseado na extensão
            if caminho.suffix.lower() == '.csv':
                if hasattr(dados, 'to_csv'):
                    dados.to_csv(caminho, index=False, encoding='utf-8-sig', sep=';')
                else:
                    import pandas as pd
                    df = pd.DataFrame(dados)
                    df.to_csv(caminho, index=False, encoding='utf-8-sig', sep=';')
            elif caminho.suffix.lower() == '.xlsx':
                if hasattr(dados, 'to_excel'):
                    dados.to_excel(caminho, index=False)
                else:
                    import pandas as pd
                    df = pd.DataFrame(dados)
                    df.to_excel(caminho, index=False)
            else:
                # Fallback para CSV
                if hasattr(dados, 'to_csv'):
                    dados.to_csv(caminho, index=False, encoding='utf-8-sig', sep=';')
                else:
                    import pandas as pd
                    df = pd.DataFrame(dados)
                    df.to_csv(caminho, index=False, encoding='utf-8-sig', sep=';')
            
            print(f"[OK] {descricao} salvo: {caminho.name}")
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao salvar {descricao}: {e}")
            return False
    
    @staticmethod
    def gerar_nome_fixo(pasta: str, tipo: str, extensao: str = "xlsx") -> str:
        """
        Gera nome de arquivo fixo (sem timestamp).
        
        Args:
            pasta (str): Pasta de destino
            tipo (str): Tipo do arquivo (ex: 'todos_tickets', 'status')
            extensao (str): Extensão do arquivo
            
        Returns:
            str: Caminho completo do arquivo
        """
        return os.path.join(pasta, f"{tipo}_atual.{extensao}")
    
    @staticmethod
    def limpar_arquivos_antigos(pasta: str, padrao: str, manter: int = 2) -> int:
        """
        Remove arquivos antigos com timestamp, mantendo apenas os mais recentes.
        
        Args:
            pasta (str): Pasta a ser limpa
            padrao (str): Padrão dos arquivos (ex: 'status_*.csv')
            manter (int): Quantidade de arquivos a manter
            
        Returns:
            int: Número de arquivos removidos
        """
        removidos = 0
        try:
            import glob
            
            pasta_path = Path(pasta)
            if not pasta_path.exists():
                return removidos
            
            # Buscar arquivos com padrão de timestamp
            arquivos = glob.glob(os.path.join(pasta, padrao))
            
            if len(arquivos) <= manter:
                return removidos
            
            # Ordenar por data de modificação (mais recentes primeiro)
            arquivos.sort(key=os.path.getmtime, reverse=True)
            
            # Remover arquivos antigos
            arquivos_para_remover = arquivos[manter:]
            
            for arquivo in arquivos_para_remover:
                try:
                    os.remove(arquivo)
                    print(f"[LIMPEZA] Removido arquivo antigo: {os.path.basename(arquivo)}")
                    removidos += 1
                except Exception as e:
                    print(f"[AVISO] Não foi possível remover {arquivo}: {e}")
                    
        except Exception as e:
            print(f"[AVISO] Erro na limpeza de arquivos antigos: {e}")
            
        return removidos
    
    @staticmethod
    def obter_info_arquivo(caminho: str) -> dict:
        """
        Obtém informações sobre um arquivo.
        
        Args:
            caminho (str): Caminho do arquivo
            
        Returns:
            dict: Informações do arquivo
        """
        try:
            caminho_path = Path(caminho)
            if not caminho_path.exists():
                return {"existe": False}
            
            stat = caminho_path.stat()
            return {
                "existe": True,
                "tamanho": stat.st_size,
                "modificado": datetime.fromtimestamp(stat.st_mtime),
                "nome": caminho_path.name
            }
        except Exception:
            return {"existe": False}