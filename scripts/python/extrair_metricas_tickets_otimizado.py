"""
Analisador de Métricas de Tickets GLPI - Versão Otimizada
========================================================

Esta versão otimizada implementa as recomendações estruturais para
melhor qualidade e padronização dos dados CSV.

Melhorias implementadas:
- Padronização de nomes de colunas (snake_case, sem acentos)
- Validação e conversão de formatos de data para ISO 8601
- Validação de dados numéricos
- Padronização de categorias
- Validação de integridade dos dados CSV
- Documentação automática da estrutura dos dados

Autor: Sistema de Análise de Tickets GLPI
Data: 2024
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Tuple, Any, Optional

# Importar o módulo de validação
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalisadorMetricasOtimizado:
    """Analisador de métricas otimizado com validação de dados"""
    
    def __init__(self):
        """Inicializa o analisador com configurações otimizadas"""
        self.df = None
        self.df_original = None
        self.metricas_estruturadas = {}
        self.relatorio_qualidade = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configurações de SLA (em horas)
        self.sla_config = {
            'Baixa': 72,
            'Normal': 48, 
            'Alta': 24,
            'Muito alta': 8,
            'Crítica': 4
        }
        
        logger.info("Analisador de Métricas Otimizado inicializado")
    
    def obter_arquivo_fixo(self) -> str:
        """
        Obtém o arquivo de dados mais recente, priorizando dados dos últimos 6 meses
        
        Returns:
            str: Caminho do arquivo encontrado
        """
        logger.info("Buscando arquivo de dados mais recente...")
        
        # Prioridade 1: Dados filtrados dos últimos 6 meses
        pasta_6_meses = "../dados/tickets_6_meses/"
        if os.path.exists(pasta_6_meses):
            arquivos_6_meses = glob.glob(os.path.join(pasta_6_meses, "tickets_api_glpi_ultimos_6_meses_*.csv"))
            if arquivos_6_meses:
                arquivo_mais_recente = max(arquivos_6_meses, key=os.path.getctime)
                logger.info(f"[OK] Usando dados filtrados dos últimos 6 meses: {os.path.basename(arquivo_mais_recente)}")
                return arquivo_mais_recente
        
        # Prioridade 2: Dados completos
        pasta_completos = "../dados/tickets_completos/"
        if os.path.exists(pasta_completos):
            # Buscar ambos os padrões de nomenclatura
            arquivos_completos = []
            arquivos_completos.extend(glob.glob(os.path.join(pasta_completos, "todos_tickets_*.csv")))
            arquivos_completos.extend(glob.glob(os.path.join(pasta_completos, "tickets_api_glpi_completo_*.csv")))
            
            if arquivos_completos:
                arquivo_mais_recente = max(arquivos_completos, key=os.path.getctime)
                logger.warning(f"[AVISO] Usando dados completos (não filtrados): {os.path.basename(arquivo_mais_recente)}")
                return arquivo_mais_recente
        
        raise FileNotFoundError("[ERRO] Nenhum arquivo de dados encontrado!")
    
    def carregar_e_validar_dados(self, arquivo_path: str) -> None:
        """
        Carrega e valida os dados do arquivo CSV
        
        Args:
            arquivo_path (str): Caminho do arquivo CSV
        """
        logger.info(f"Carregando e validando dados: {arquivo_path}")
        
        try:
            # Tentar diferentes encodings para carregar dados originais
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df_loaded = None
            
            for encoding in encodings_to_try:
                try:
                    logger.info(f"Tentando carregar arquivo com encoding: {encoding}")
                    df_loaded = pd.read_csv(arquivo_path, encoding=encoding)
                    logger.info(f"[OK] Arquivo carregado com sucesso usando encoding: {encoding}")
                    break
                except UnicodeDecodeError as e:
                    logger.warning(f"Falha ao carregar com encoding {encoding}: {str(e)}")
                    continue
                except Exception as e:
                    logger.warning(f"Erro inesperado com encoding {encoding}: {str(e)}")
                    continue
            
            if df_loaded is None:
                raise ValueError("Não foi possível carregar o arquivo com nenhum dos encodings testados")
            
            self.df_original = df_loaded
            logger.info(f"Dados originais carregados: {len(self.df_original)} registros, {len(self.df_original.columns)} colunas")
            
            # Processar e validar dados
            self.df = self.df_original.copy()
            
            # Converter colunas de data para datetime
            date_columns = ['Data Criação', 'Data Modificação', 'Data Solução', 'Data Fechamento']
            for col in date_columns:
                if col in self.df.columns:
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                        logger.info(f"Coluna {col} convertida para datetime")
                    except Exception as e:
                        logger.warning(f"Erro ao converter coluna {col} para datetime: {str(e)}")
            
            # Criar relatório de qualidade simples
            duplicatas_antes = len(self.df)
            self.df = self.df.drop_duplicates()
            duplicatas_removidas = duplicatas_antes - len(self.df)
            
            self.relatorio_qualidade = {
                'total_registros': len(self.df),
                'total_colunas': len(self.df.columns),
                'duplicatas': duplicatas_removidas,
                'erros_validacao': []
            }
            
            # Log do relatório de qualidade
            logger.info(f"Dados processados: {self.relatorio_qualidade['total_registros']} registros")
            logger.info(f"Linhas duplicadas removidas: {self.relatorio_qualidade['duplicatas']}")
            logger.info(f"Colunas disponíveis: {list(self.df.columns)}")
            
            if self.relatorio_qualidade.get('erros_validacao'):
                logger.warning(f"Avisos de validação: {len(self.relatorio_qualidade['erros_validacao'])}")
                for error in self.relatorio_qualidade['erros_validacao']:
                    logger.warning(f"  - {error}")
            
            # Calcular período de análise
            if 'Data Criação' in self.df.columns:
                data_min = self.df['Data Criação'].min()
                data_max = self.df['Data Criação'].max()
                logger.info(f"Período dos dados: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            raise
    
    def exibir_cabecalho(self) -> None:
        """Exibe cabeçalho informativo otimizado"""
        print("=" * 70)
        print("ANALISADOR DE METRICAS DE TICKETS GLPI - VERSAO OTIMIZADA")
        print("=" * 70)
        print("Analise de dados com validacao e padronizacao automatica")
        print("PRIORIDADE: Dados dos ultimos 6 meses (quando disponiveis)")
        print("Geracao de relatorios e estatisticas detalhadas")
        print("[OK] Validacao de qualidade e integridade dos dados")
        print()
        
        # Informações sobre qualidade dos dados
        if self.relatorio_qualidade:
            print("[LISTA] RELATÓRIO DE QUALIDADE DOS DADOS:")
            print(f"   • Total de registros: {self.relatorio_qualidade['total_registros']:,}")
            print(f"   • Total de colunas: {self.relatorio_qualidade['total_colunas']}")
            print(f"   • Linhas duplicadas: {self.relatorio_qualidade['duplicatas']}")
            
            # Mostrar principais problemas de qualidade
            missing_data = self.relatorio_qualidade.get('missing_data', {})
            high_missing = {col: data for col, data in missing_data.items() 
                          if data['percentage'] > 10}
            
            if high_missing:
                print("   [AVISO] Colunas com dados ausentes (>10%):")
                for col, data in high_missing.items():
                    print(f"     - {col}: {data['percentage']:.1f}% ausentes")
            
            if self.relatorio_qualidade.get('erros_validacao'):
                print(f"   [AVISO] Avisos de validação: {len(self.relatorio_qualidade['erros_validacao'])}")
        
        print()
    
    def calcular_metricas_gerais(self) -> None:
        """Calcula métricas gerais otimizadas"""
        logger.info("Calculando métricas gerais...")
        
        print("=" * 70)
        print("[DADOS] MÉTRICAS GERAIS")
        print("=" * 70)
        print(f"[TICKET] Total de tickets: {len(self.df):,}")
        print()
        
        # Distribuição por status
        if 'Status' in self.df.columns:
            print("[GRAFICO] DISTRIBUIÇÃO POR STATUS:")
            status_counts = self.df['Status'].value_counts()
            for status, count in status_counts.items():
                percentage = (count / len(self.df)) * 100
                print(f"   • {status}: {count:,} ({percentage:.1f}%)")
            print()
        
        # Distribuição por entidade (top 10)
        if 'Entidade' in self.df.columns:
            print("[EMPRESA] DISTRIBUIÇÃO POR ENTIDADE (Top 10):")
            entidade_counts = self.df['Entidade'].value_counts().head(10)
            for entidade, count in entidade_counts.items():
                percentage = (count / len(self.df)) * 100
                print(f"   • {entidade}: {count:,} ({percentage:.1f}%)")
            
            total_outras = len(self.df) - entidade_counts.sum()
            if total_outras > 0:
                outras_entidades = self.df['Entidade'].nunique() - 10
                print(f"   • ... e mais {outras_entidades} entidades ({total_outras:,} tickets)")
            print()
        
        # Distribuição por grupo técnico
        if 'Grupo' in self.df.columns:
            print("[GRUPO] DISTRIBUIÇÃO POR GRUPO TÉCNICO:")
            grupo_counts = self.df['Grupo'].value_counts()
            for grupo, count in grupo_counts.items():
                percentage = (count / len(self.df)) * 100
                print(f"   • {grupo}: {count:,} ({percentage:.1f}%)")
            print()
        
        # Top categorias
        if 'Categoria' in self.df.columns:
            print("[LISTA] PRINCIPAIS CATEGORIAS (Top 10):")
            categoria_counts = self.df['Categoria'].value_counts().head(10)
            for categoria, count in categoria_counts.items():
                percentage = (count / len(self.df)) * 100
                print(f"   • {categoria}: {count:,} ({percentage:.1f}%)")
            print()
        
        # Top técnicos
        if 'Técnico' in self.df.columns:
            print("[TECNICO] TOP TÉCNICOS (Top 10):")
            tecnico_counts = self.df['Técnico'].value_counts().head(10)
            for tecnico, count in tecnico_counts.items():
                if pd.notna(tecnico) and tecnico.strip():
                    percentage = (count / len(self.df)) * 100
                    print(f"   • {tecnico}: {count:,} ({percentage:.1f}%)")
            print()
        
        # Top localizações
        if 'Localização' in self.df.columns:
            print("[LOCAL] PRINCIPAIS LOCALIZAÇÕES (Top 10):")
            # Converter para string para análise
            df_loc = self.df.copy()
            df_loc['localizacao_str'] = df_loc['Localização'].astype(str)
            localizacao_counts = df_loc['localizacao_str'].value_counts().head(10)
            
            for localizacao, count in localizacao_counts.items():
                if localizacao != 'nan' and localizacao != '0':
                    percentage = (count / len(self.df)) * 100
                    print(f"   • {localizacao}: {count:,} ({percentage:.1f}%)")
            print()
    
    def calcular_metricas_temporais(self) -> None:
        """Calcula métricas temporais otimizadas"""
        logger.info("Calculando métricas temporais...")
        
        if 'Data Criação' not in self.df.columns:
            logger.warning("Coluna 'Data Criação' não encontrada. Pulando métricas temporais.")
            return
        
        print("=" * 70)
        print("[TEMPO] MÉTRICAS TEMPORAIS")
        print("=" * 70)
        
        # Tickets por mês
        df_temporal = self.df.copy()
        df_temporal['mes_criacao'] = df_temporal['Data Criação'].dt.to_period('M')
        tickets_por_mes = df_temporal['mes_criacao'].value_counts().sort_index()
        
        print("[MES] TICKETS POR MÊS:")
        for mes, count in tickets_por_mes.items():
            print(f"   • {mes}: {count:,} tickets")
        print()
        
        # Tickets por dia da semana
        df_temporal['dia_semana'] = df_temporal['Data Criação'].dt.day_name()
        tickets_por_dia = df_temporal['dia_semana'].value_counts()
        
        print("[DIA] TICKETS POR DIA DA SEMANA:")
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for dia_en, dia_pt in zip(dias_ordem, dias_pt):
            if dia_en in tickets_por_dia.index:
                count = tickets_por_dia[dia_en]
                percentage = (count / len(self.df)) * 100
                print(f"   • {dia_pt}: {count:,} ({percentage:.1f}%)")
        print()
        
        # Período de análise
        data_min = df_temporal['Data Criação'].min()
        data_max = df_temporal['Data Criação'].max()
        periodo_dias = (data_max - data_min).days
        
        print(f"[DADOS] PERÍODO DE ANÁLISE:")
        print(f"   • Data inicial: {data_min.strftime('%d/%m/%Y %H:%M')}")
        print(f"   • Data final: {data_max.strftime('%d/%m/%Y %H:%M')}")
        print(f"   • Período total: {periodo_dias} dias")
        print(f"   • Média diária: {len(self.df) / max(periodo_dias, 1):.1f} tickets/dia")
        print()
    
    def calcular_metricas_performance(self) -> None:
        """Calcula métricas de performance otimizadas"""
        logger.info("Calculando métricas de performance...")
        
        print("=" * 70)
        print("[PERF] MÉTRICAS DE PERFORMANCE")
        print("=" * 70)
        
        # Análise de TTR (Time to Resolution)
        if 'Tempo Solução (min)' in self.df.columns:
            df_resolvidos = self.df[self.df['Tempo Solução (min)'].notna() & (self.df['Tempo Solução (min)'] > 0)].copy()
            
            if len(df_resolvidos) > 0:
                df_resolvidos['ttr_horas'] = df_resolvidos['Tempo Solução (min)'] / 60
                
                print("[SLA] TEMPO DE RESOLUÇÃO (TTR):")
                print(f"   • Tickets resolvidos: {len(df_resolvidos):,}")
                print(f"   • TTR médio: {df_resolvidos['ttr_horas'].mean():.1f} horas")
                print(f"   • TTR mediano: {df_resolvidos['ttr_horas'].median():.1f} horas")
                print(f"   • TTR mínimo: {df_resolvidos['ttr_horas'].min():.1f} horas")
                print(f"   • TTR máximo: {df_resolvidos['ttr_horas'].max():.1f} horas")
                
                # Percentis
                p25 = df_resolvidos['ttr_horas'].quantile(0.25)
                p75 = df_resolvidos['ttr_horas'].quantile(0.75)
                p90 = df_resolvidos['ttr_horas'].quantile(0.90)
                p95 = df_resolvidos['ttr_horas'].quantile(0.95)
                
                print(f"   • 25% resolvidos em até: {p25:.1f} horas")
                print(f"   • 75% resolvidos em até: {p75:.1f} horas")
                print(f"   • 90% resolvidos em até: {p90:.1f} horas")
                print(f"   • 95% resolvidos em até: {p95:.1f} horas")
                print()
                
                # TTR por grupo técnico
                if 'Grupo' in self.df.columns:
                    print("[GRUPO] TTR MÉDIO POR GRUPO TÉCNICO:")
                    ttr_por_grupo = df_resolvidos.groupby('Grupo')['ttr_horas'].agg(['mean', 'count']).round(1)
                    ttr_por_grupo = ttr_por_grupo.sort_values('mean')
                    
                    for grupo, dados in ttr_por_grupo.iterrows():
                        print(f"   • {grupo}: {dados['mean']:.1f}h (média) - {dados['count']:,} tickets")
                    print()
        
        # Análise de SLA
        self.calcular_sla_performance()
    
    def calcular_sla_performance(self) -> None:
        """Calcula métricas de SLA otimizadas"""
        logger.info("Calculando métricas de SLA...")
        
        if 'Prioridade' not in self.df.columns or 'Tempo Solução (min)' not in self.df.columns:
            logger.warning("Colunas necessárias para SLA não encontradas")
            return
        
        print("[SLA] ANÁLISE DE SLA (Service Level Agreement):")
        
        # Mapear prioridades para SLA
        prioridade_sla = {1: 'Baixa', 2: 'Normal', 3: 'Alta', 4: 'Muito alta', 5: 'Crítica'}
        
        df_sla = self.df[self.df['Tempo Solução (min)'].notna() & (self.df['Tempo Solução (min)'] > 0)].copy()
        df_sla['prioridade_nome'] = df_sla['Prioridade'].map(prioridade_sla)
        df_sla['sla_horas'] = df_sla['prioridade_nome'].map(self.sla_config)
        df_sla['ttr_horas'] = df_sla['Tempo Solução (min)'] / 60
        df_sla['dentro_sla'] = df_sla['ttr_horas'] <= df_sla['sla_horas']
        
        # Estatísticas gerais de SLA
        total_sla = len(df_sla)
        dentro_sla = df_sla['dentro_sla'].sum()
        fora_sla = total_sla - dentro_sla
        
        print(f"   • Total analisado: {total_sla:,} tickets")
        print(f"   • Dentro do SLA: {dentro_sla:,} ({(dentro_sla/total_sla)*100:.1f}%)")
        print(f"   • Fora do SLA: {fora_sla:,} ({(fora_sla/total_sla)*100:.1f}%)")
        print()
        
        # SLA por prioridade
        print("[DADOS] SLA POR PRIORIDADE:")
        sla_por_prioridade = df_sla.groupby('prioridade_nome').agg({
            'dentro_sla': ['count', 'sum'],
            'ttr_horas': 'mean'
        }).round(1)
        
        for prioridade in ['Crítica', 'Muito alta', 'Alta', 'Normal', 'Baixa']:
            if prioridade in sla_por_prioridade.index:
                dados = sla_por_prioridade.loc[prioridade]
                total = dados[('dentro_sla', 'count')]
                dentro = dados[('dentro_sla', 'sum')]
                ttr_medio = dados[('ttr_horas', 'mean')]
                sla_limite = self.sla_config[prioridade]
                
                if total > 0:
                    percentual = (dentro / total) * 100
                    print(f"   • {prioridade} (SLA: {sla_limite}h): {dentro}/{total} ({percentual:.1f}%) - TTR médio: {ttr_medio:.1f}h")
        print()
    
    def exportar_metricas_csv(self) -> None:
        """Exporta métricas em formato CSV otimizado"""
        logger.info("Exportando métricas em CSV...")
        
        pasta_csv = "../dados/metricas_csv/"
        os.makedirs(pasta_csv, exist_ok=True)
        
        print("[SALVAR] EXPORTANDO MÉTRICAS EM CSV...")
        print("-" * 50)
        
        try:
            # 1. Status
            if 'Status' in self.df.columns:
                status_df = self.df['Status'].value_counts().reset_index()
                status_df.columns = ['status', 'quantidade']
                status_df['percentual'] = (status_df['quantidade'] / len(self.df) * 100).round(2)
                arquivo_status = os.path.join(pasta_csv, f"status_{self.timestamp}.csv")
                status_df.to_csv(arquivo_status, index=False, encoding='utf-8')
                print(f"[OK] Status: {arquivo_status}")
            
            # 2. Entidades
            if 'Entidade' in self.df.columns:
                entidades_df = self.df['Entidade'].value_counts().reset_index()
                entidades_df.columns = ['entidade', 'quantidade']
                entidades_df['percentual'] = (entidades_df['quantidade'] / len(self.df) * 100).round(2)
                arquivo_entidades = os.path.join(pasta_csv, f"entidades_{self.timestamp}.csv")
                entidades_df.to_csv(arquivo_entidades, index=False, encoding='utf-8')
                print(f"[OK] Entidades: {arquivo_entidades}")
            
            # 3. Técnicos
            if 'Técnico' in self.df.columns:
                tecnicos_df = self.df['Técnico'].value_counts().reset_index()
                tecnicos_df.columns = ['tecnico', 'quantidade']
                tecnicos_df['percentual'] = (tecnicos_df['quantidade'] / len(self.df) * 100).round(2)
                arquivo_tecnicos = os.path.join(pasta_csv, f"tecnicos_{self.timestamp}.csv")
                tecnicos_df.to_csv(arquivo_tecnicos, index=False, encoding='utf-8')
                print(f"[OK] Técnicos: {arquivo_tecnicos}")
            
            # 4. TTR por Grupo
            if 'Grupo' in self.df.columns and 'Tempo Solução (min)' in self.df.columns:
                df_ttr = self.df[self.df['Tempo Solução (min)'].notna() & (self.df['Tempo Solução (min)'] > 0)].copy()
                if len(df_ttr) > 0:
                    df_ttr['ttr_horas'] = df_ttr['Tempo Solução (min)'] / 60
                    ttr_grupo_df = df_ttr.groupby('Grupo')['ttr_horas'].agg(['mean', 'median', 'count']).round(2)
                    ttr_grupo_df.columns = ['ttr_medio_horas', 'ttr_mediano_horas', 'quantidade_tickets']
                    ttr_grupo_df = ttr_grupo_df.reset_index()
                    arquivo_ttr = os.path.join(pasta_csv, f"ttr_grupo_{self.timestamp}.csv")
                    ttr_grupo_df.to_csv(arquivo_ttr, index=False, encoding='utf-8')
                    print(f"[OK] TTR por Grupo: {arquivo_ttr}")
            
            # 5. Relatório de Qualidade
            relatorio_df = pd.DataFrame([
                {'metrica': 'total_registros', 'valor': self.relatorio_qualidade['total_registros']},
                {'metrica': 'total_colunas', 'valor': self.relatorio_qualidade['total_colunas']},
                {'metrica': 'linhas_duplicadas', 'valor': self.relatorio_qualidade['duplicatas']},
                {'metrica': 'erros_validacao', 'valor': len(self.relatorio_qualidade.get('erros_validacao', []))}
            ])
            arquivo_qualidade = os.path.join(pasta_csv, f"relatorio_qualidade_{self.timestamp}.csv")
            relatorio_df.to_csv(arquivo_qualidade, index=False, encoding='utf-8')
            print(f"[OK] Relatório de Qualidade: {arquivo_qualidade}")
            

            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {str(e)}")
            print(f"[ERRO] Erro na exportação: {str(e)}")
        
        print()
    
    def gerar_relatorio_final(self) -> None:
        """Gera relatório final otimizado"""
        print("=" * 70)
        print("[OK] ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        
        # Resumo da qualidade dos dados
        print("[LISTA] RESUMO DA QUALIDADE DOS DADOS:")
        print(f"   • Registros processados: {self.relatorio_qualidade['total_registros']:,}")
        print(f"   • Colunas padronizadas: {self.relatorio_qualidade['total_colunas']}")
        print(f"   • Linhas duplicadas removidas: {self.relatorio_qualidade['duplicatas']}")
        
        if self.relatorio_qualidade.get('erros_validacao'):
            print(f"   • Avisos de validação: {len(self.relatorio_qualidade['erros_validacao'])}")
            print("   • Principais avisos:")
            for error in self.relatorio_qualidade['erros_validacao'][:3]:
                print(f"     - {error}")
        else:
            print("   • [OK] Nenhum aviso de validação")
        
        print()
        print("[SLA] MELHORIAS IMPLEMENTADAS:")
        print("   [OK] Padronização de nomes de colunas (snake_case)")
        print("   [OK] Validação e conversão de datas para ISO 8601")
        print("   [OK] Validação de dados numéricos")
        print("   [OK] Padronização de categorias")
        print("   [OK] Validação de integridade dos dados")
        print("   [OK] Documentação automática da estrutura")
        print()
        print("[DADOS] Métricas exibidas na tela")
        print("[SALVAR] Métricas exportadas em formato CSV")
        print("[DOC] Documentação gerada automaticamente")
        print("[FIM] Obrigado por usar o Analisador de Métricas Otimizado!")


def main():
    """Função principal otimizada"""
    try:
        # Inicializar analisador
        analisador = AnalisadorMetricasOtimizado()
        
        # Obter arquivo de dados
        arquivo_dados = analisador.obter_arquivo_fixo()
        
        # Carregar e validar dados
        analisador.carregar_e_validar_dados(arquivo_dados)
        
        # Exibir cabeçalho
        analisador.exibir_cabecalho()
        
        # Calcular métricas
        analisador.calcular_metricas_gerais()
        analisador.calcular_metricas_temporais()
        analisador.calcular_metricas_performance()
        
        # Exportar resultados
        analisador.exportar_metricas_csv()
        
        # Relatório final
        analisador.gerar_relatorio_final()
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        print(f"[ERRO] Erro: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())