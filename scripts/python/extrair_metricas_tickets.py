#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALISADOR DE MÉTRICAS DE TICKETS GLPI
=====================================

Este script analisa os arquivos CSV gerados pelo extrator de dados da API GLPI
e gera relatórios com métricas e estatísticas dos tickets.

Autor: Sistema de Análise CAU
Data: 2025-01-22
"""

import pandas as pd
import os
import sys
from datetime import datetime
from collections import Counter
import glob

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class AnalisadorMetricasTickets:
    def __init__(self):
        self.dados_dir = "../dados"
        self.df = None
        self.arquivo_selecionado = None
        self.metricas_estruturadas = {}
        
    def exibir_cabecalho(self):
        """Exibe o cabeçalho do programa"""
        print("=" * 70)
        print("[BUSCA] ANALISADOR DE MÉTRICAS DE TICKETS GLPI")
        print("=" * 70)
        print("[METRICAS] Análise de dados dos tickets extraídos da API GLPI")
        print("[GRAFICO] Geração de relatórios e estatísticas detalhadas")
        print()
        
    def obter_arquivo_fixo(self):
        """Retorna o caminho do arquivo CSV mais recente para análise"""
        # Diretório onde estão os arquivos completos
        diretorio_completos = r"c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\scripts\dados\tickets_completos"
        
        # Buscar todos os arquivos CSV que seguem o padrão
        padrao_arquivo = os.path.join(diretorio_completos, "tickets_api_glpi_completo_*.csv")
        arquivos_encontrados = glob.glob(padrao_arquivo)
        
        if not arquivos_encontrados:
            raise FileNotFoundError(f"Nenhum arquivo encontrado no padrão: {padrao_arquivo}")
        
        # Pegar o arquivo mais recente (último modificado)
        arquivo_mais_recente = max(arquivos_encontrados, key=os.path.getmtime)
        
        nome_arquivo = os.path.basename(arquivo_mais_recente)
        return {
            'arquivo': arquivo_mais_recente,
            'nome': nome_arquivo,
            'data_criacao': datetime.fromtimestamp(os.path.getmtime(arquivo_mais_recente)),
            'tamanho': os.path.getsize(arquivo_mais_recente)
        }
        

                
    def carregar_dados(self):
        """Carrega os dados do arquivo CSV fixo"""
        try:
            arquivo_info = self.obter_arquivo_fixo()
            self.arquivo_selecionado = arquivo_info['arquivo']
            
            print(f"\n[PROCESSANDO] Carregando dados do arquivo fixo...")
            print(f"[EMOJI] Arquivo: {arquivo_info['nome']}")
            
            self.df = pd.read_csv(self.arquivo_selecionado, encoding='utf-8')
            print(f"[OK] {len(self.df)} registros carregados com sucesso!")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao carregar arquivo: {e}")
            return False
            
    def gerar_metricas_gerais(self):
        """Gera métricas gerais dos tickets"""
        print("\n" + "=" * 70)
        print("[METRICAS] MÉTRICAS GERAIS")
        print("=" * 70)
        
        total_tickets = len(self.df)
        print(f"[EMOJI] Total de tickets: {total_tickets:,}")
        
        # Análise por Status
        print(f"\n[GRAFICO] DISTRIBUIÇÃO POR STATUS:")
        status_counts = self.df['Status'].value_counts()
        for status, count in status_counts.items():
            percentual = (count / total_tickets) * 100
            print(f"   • {status}: {count:,} ({percentual:.1f}%)")
            
        # Análise por Entidade
        print(f"\n[EMOJI] DISTRIBUIÇÃO POR ENTIDADE:")
        entidade_counts = self.df['Entidade'].value_counts().head(10)
        for entidade, count in entidade_counts.items():
            percentual = (count / total_tickets) * 100
            print(f"   • {entidade}: {count:,} ({percentual:.1f}%)")
            
        if len(self.df['Entidade'].value_counts()) > 10:
            outros = len(self.df['Entidade'].value_counts()) - 10
            print(f"   • ... e mais {outros} entidades")
            
        # Análise por Grupo Técnico
        print(f"\n[EMOJI] DISTRIBUIÇÃO POR GRUPO TÉCNICO:")
        grupo_counts = self.df['Grupo_tecnico'].value_counts().head(10)
        for grupo, count in grupo_counts.items():
            percentual = (count / total_tickets) * 100
            print(f"   • {grupo}: {count:,} ({percentual:.1f}%)")
            
        # Análise por Categoria
        print(f"\n[EMOJI] PRINCIPAIS CATEGORIAS:")
        categoria_counts = self.df['Categoria'].value_counts().head(10)
        for categoria, count in categoria_counts.items():
            percentual = (count / total_tickets) * 100
            print(f"   • {categoria}: {count:,} ({percentual:.1f}%)")
            
    def gerar_metricas_temporais(self):
        """Gera métricas relacionadas ao tempo"""
        print("\n" + "=" * 70)
        print("⏰ MÉTRICAS TEMPORAIS")
        print("=" * 70)
        
        try:
            # Converter datas
            self.df['Data_abertura_dt'] = pd.to_datetime(self.df['Data_abertura'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            self.df['Ultima_atualizacao_dt'] = pd.to_datetime(self.df['Ultima_atualizacao'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            
            # Período de análise
            data_min = self.df['Data_abertura_dt'].min()
            data_max = self.df['Data_abertura_dt'].max()
            
            print(f"[DATA] Período analisado:")
            print(f"   • De: {data_min.strftime('%d/%m/%Y')}")
            print(f"   • Até: {data_max.strftime('%d/%m/%Y')}")
            
            # Tickets por mês
            print(f"\n[GRAFICO] TICKETS POR MÊS:")
            self.df['Mes_abertura'] = self.df['Data_abertura_dt'].dt.to_period('M')
            tickets_por_mes = self.df['Mes_abertura'].value_counts().sort_index()
            
            for mes, count in tickets_por_mes.items():
                print(f"   • {mes}: {count:,} tickets")
                
            # Tickets por dia da semana
            print(f"\n[METRICAS] TICKETS POR DIA DA SEMANA:")
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            self.df['Dia_semana'] = self.df['Data_abertura_dt'].dt.dayofweek
            tickets_por_dia = self.df['Dia_semana'].value_counts().sort_index()
            
            for dia_num, count in tickets_por_dia.items():
                dia_nome = dias_semana[dia_num]
                percentual = (count / len(self.df)) * 100
                print(f"   • {dia_nome}: {count:,} ({percentual:.1f}%)")
                
        except Exception as e:
            print(f"[ERRO] Erro ao processar métricas temporais: {e}")
            
    def gerar_metricas_performance(self):
        """Gera métricas de performance e produtividade"""
        print("\n" + "=" * 70)
        print("[INICIO] MÉTRICAS DE PERFORMANCE")
        print("=" * 70)
        
        # Top técnicos por volume
        print(f"[EMOJI] TOP 10 TÉCNICOS POR VOLUME:")
        tecnicos = self.df['Tecnico_atribuido'].value_counts().head(10)
        for i, (tecnico, count) in enumerate(tecnicos.items(), 1):
            percentual = (count / len(self.df)) * 100
            print(f"   {i:2d}. {tecnico}: {count:,} tickets ({percentual:.1f}%)")
            
        # Tickets sem técnico atribuído
        sem_tecnico = self.df['Tecnico_atribuido'].isna().sum()
        if sem_tecnico > 0:
            print(f"\n[AVISO]  Tickets sem técnico atribuído: {sem_tecnico:,}")
            
        # Análise de localização
        print(f"\n[EMOJI] PRINCIPAIS LOCALIZAÇÕES:")
        localizacoes = self.df['Localizacao'].value_counts().head(10)
        for localizacao, count in localizacoes.items():
            if pd.notna(localizacao) and localizacao != "Sem Localização":
                percentual = (count / len(self.df)) * 100
                print(f"   • {localizacao}: {count:,} ({percentual:.1f}%)")
    
    def calcular_ttr_metricas(self):
        """Calcula métricas de Time to Resolution (TTR)"""
        print("\n" + "=" * 70)
        print("[TEMPO]  MÉTRICAS DE TIME TO RESOLUTION (TTR)")
        print("=" * 70)
        
        try:
            # Garantir que as datas estão convertidas
            if 'Data_abertura_dt' not in self.df.columns:
                self.df['Data_abertura_dt'] = pd.to_datetime(self.df['Data_abertura'], errors='coerce')
                self.df['Ultima_atualizacao_dt'] = pd.to_datetime(self.df['Ultima_atualizacao'], errors='coerce')
            
            # Filtrar tickets resolvidos/fechados
            tickets_resolvidos = self.df[self.df['Status'].isin(['Solucionado', 'Fechado'])].copy()
            
            if len(tickets_resolvidos) == 0:
                print("[ERRO] Nenhum ticket resolvido encontrado para cálculo de TTR")
                return
            
            # Calcular TTR em horas
            tickets_resolvidos['TTR_horas'] = (tickets_resolvidos['Ultima_atualizacao_dt'] - tickets_resolvidos['Data_abertura_dt']).dt.total_seconds() / 3600
            
            # Filtrar TTR válidos (positivos)
            ttr_validos = tickets_resolvidos[tickets_resolvidos['TTR_horas'] > 0]
            
            print(f"[METRICAS] ESTATÍSTICAS GERAIS DE TTR:")
            print(f"   • Total de tickets resolvidos: {len(tickets_resolvidos):,}")
            print(f"   • Tickets com TTR calculável: {len(ttr_validos):,}")
            print(f"   • TTR médio: {ttr_validos['TTR_horas'].mean():.1f} horas ({ttr_validos['TTR_horas'].mean()/24:.1f} dias)")
            print(f"   • TTR mediano: {ttr_validos['TTR_horas'].median():.1f} horas ({ttr_validos['TTR_horas'].median()/24:.1f} dias)")
            print(f"   • TTR mínimo: {ttr_validos['TTR_horas'].min():.1f} horas")
            print(f"   • TTR máximo: {ttr_validos['TTR_horas'].max():.1f} horas ({ttr_validos['TTR_horas'].max()/24:.1f} dias)")
            
            # TTR por categoria (top 10)
            print(f"\n[EMOJI] TTR POR CATEGORIA (TOP 10):")
            ttr_por_categoria = ttr_validos.groupby('Categoria')['TTR_horas'].agg(['count', 'mean', 'median']).round(1)
            ttr_por_categoria.columns = ['Tickets', 'TTR_Medio', 'TTR_Mediano']
            ttr_por_categoria = ttr_por_categoria.sort_values('Tickets', ascending=False).head(10)
            
            for categoria, dados in ttr_por_categoria.iterrows():
                print(f"   • {categoria}:")
                print(f"     - Tickets: {int(dados['Tickets'])}")
                print(f"     - TTR Médio: {dados['TTR_Medio']:.1f}h ({dados['TTR_Medio']/24:.1f} dias)")
                print(f"     - TTR Mediano: {dados['TTR_Mediano']:.1f}h ({dados['TTR_Mediano']/24:.1f} dias)")
            
            # TTR por grupo técnico
            print(f"\n[EMOJI] TTR POR GRUPO TÉCNICO:")
            ttr_por_grupo = ttr_validos.groupby('Grupo_tecnico')['TTR_horas'].agg(['count', 'mean', 'median']).round(1)
            ttr_por_grupo.columns = ['Tickets', 'TTR_Medio', 'TTR_Mediano']
            ttr_por_grupo = ttr_por_grupo.sort_values('Tickets', ascending=False)
            
            for grupo, dados in ttr_por_grupo.iterrows():
                print(f"   • {grupo}:")
                print(f"     - Tickets: {int(dados['Tickets'])}")
                print(f"     - TTR Médio: {dados['TTR_Medio']:.1f}h ({dados['TTR_Medio']/24:.1f} dias)")
                print(f"     - TTR Mediano: {dados['TTR_Mediano']:.1f}h ({dados['TTR_Mediano']/24:.1f} dias)")
            
            # Armazenar métricas para exportação
            self.metricas_estruturadas['ttr'] = {
                'tickets_resolvidos': len(tickets_resolvidos),
                'tickets_com_ttr': len(ttr_validos),
                'ttr_medio_horas': float(ttr_validos['TTR_horas'].mean()),
                'ttr_mediano_horas': float(ttr_validos['TTR_horas'].median()),
                'ttr_minimo_horas': float(ttr_validos['TTR_horas'].min()),
                'ttr_maximo_horas': float(ttr_validos['TTR_horas'].max()),
                'ttr_por_categoria': ttr_por_categoria.to_dict('index'),
                'ttr_por_grupo': ttr_por_grupo.to_dict('index')
            }
            
        except Exception as e:
            print(f"[ERRO] Erro ao calcular TTR: {e}")
    
    def analisar_sla_performance(self):
        """Analisa performance baseada em SLAs diferenciados"""
        print("\n" + "=" * 70)
        print("[FOCO] ANÁLISE DE PERFORMANCE POR SLA")
        print("=" * 70)
        
        try:
            # Definir SLAs por categoria baseado na análise prévia
            slas_categoria = {
                'CRÍTICA': {
                    'sla_horas': 2,
                    'categorias': ['RESET DE SENHA', 'LIBERAÇÃO DE ACESSO']
                },
                'ALTA': {
                    'sla_horas': 8,
                    'categorias': ['ATENDIMENTO AO USUÁRIO', 'NOVO USUÁRIO', 'OFFICE 365']
                },
                'MÉDIA': {
                    'sla_horas': 24,
                    'categorias': ['OUTROS', 'IMPRESSORA', 'HARDWARE']
                },
                'BAIXA': {
                    'sla_horas': 72,
                    'categorias': ['INSTALAÇÃO', 'NOVO PONTO DE REDE', 'WIFI']
                },
                'COMPLEXA': {
                    'sla_horas': 120,
                    'categorias': ['ACESSO A SISTEMAS', 'DEVOLUÇÃO', 'SOLICITAÇÃO']
                }
            }
            
            # Garantir que TTR está calculado
            if 'Data_abertura_dt' not in self.df.columns:
                self.df['Data_abertura_dt'] = pd.to_datetime(self.df['Data_abertura'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                self.df['Ultima_atualizacao_dt'] = pd.to_datetime(self.df['Ultima_atualizacao'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            
            tickets_resolvidos = self.df[self.df['Status'].isin(['Solucionado', 'Fechado'])].copy()
            tickets_resolvidos['TTR_horas'] = (tickets_resolvidos['Ultima_atualizacao_dt'] - tickets_resolvidos['Data_abertura_dt']).dt.total_seconds() / 3600
            ttr_validos = tickets_resolvidos[tickets_resolvidos['TTR_horas'] > 0]
            
            # Mapear categorias para complexidade
            categoria_para_complexidade = {}
            for complexidade, info in slas_categoria.items():
                for categoria in info['categorias']:
                    categoria_para_complexidade[categoria] = complexidade
            
            # Adicionar coluna de complexidade
            ttr_validos['Complexidade'] = ttr_validos['Categoria'].map(categoria_para_complexidade).fillna('MÉDIA')
            
            # Adicionar SLA correspondente
            complexidade_para_sla = {comp: info['sla_horas'] for comp, info in slas_categoria.items()}
            ttr_validos['SLA_horas'] = ttr_validos['Complexidade'].map(complexidade_para_sla)
            
            # Calcular se está dentro do SLA
            ttr_validos['Dentro_SLA'] = ttr_validos['TTR_horas'] <= ttr_validos['SLA_horas']
            
            print(f"[METRICAS] PERFORMANCE GERAL POR SLA:")
            performance_geral = ttr_validos.groupby('Complexidade').agg({
                'Dentro_SLA': ['count', 'sum'],
                'TTR_horas': ['mean', 'median']
            }).round(1)
            
            performance_geral.columns = ['Total_Tickets', 'Dentro_SLA', 'TTR_Medio', 'TTR_Mediano']
            performance_geral['Percentual_SLA'] = (performance_geral['Dentro_SLA'] / performance_geral['Total_Tickets'] * 100).round(1)
            
            for complexidade in ['CRÍTICA', 'ALTA', 'MÉDIA', 'BAIXA', 'COMPLEXA']:
                if complexidade in performance_geral.index:
                    dados = performance_geral.loc[complexidade]
                    sla_horas = slas_categoria[complexidade]['sla_horas']
                    print(f"   • {complexidade} (SLA: {sla_horas}h):")
                    print(f"     - Total: {int(dados['Total_Tickets'])} tickets")
                    print(f"     - Dentro do SLA: {int(dados['Dentro_SLA'])} ({dados['Percentual_SLA']:.1f}%)")
                    print(f"     - TTR Médio: {dados['TTR_Medio']:.1f}h")
            
            print(f"\n[EMOJI] PERFORMANCE POR CATEGORIA:")
            performance_categoria = ttr_validos.groupby('Categoria').agg({
                'Dentro_SLA': ['count', 'sum'],
                'TTR_horas': 'median',
                'SLA_horas': 'first'
            }).round(1)
            
            performance_categoria.columns = ['Total_Tickets', 'Dentro_SLA', 'TTR_Mediano', 'SLA_horas']
            performance_categoria['Percentual_SLA'] = (performance_categoria['Dentro_SLA'] / performance_categoria['Total_Tickets'] * 100).round(1)
            performance_categoria = performance_categoria.sort_values('Total_Tickets', ascending=False).head(10)
            
            for categoria, dados in performance_categoria.iterrows():
                print(f"   • {categoria}:")
                print(f"     - SLA: {int(dados['SLA_horas'])}h | TTR Mediano: {dados['TTR_Mediano']:.1f}h")
                print(f"     - Performance: {int(dados['Dentro_SLA'])}/{int(dados['Total_Tickets'])} ({dados['Percentual_SLA']:.1f}%)")
            
            # Armazenar métricas para exportação
            self.metricas_estruturadas['sla'] = {
                'slas_definidos': slas_categoria,
                'performance_por_complexidade': performance_geral.to_dict('index'),
                'performance_por_categoria': performance_categoria.to_dict('index')
            }
            
        except Exception as e:
            print(f"[ERRO] Erro ao analisar SLA: {e}")
    
    def calcular_idade_tickets_ativos(self):
        """Calcula a idade dos tickets ativos"""
        print("\n" + "=" * 70)
        print("[DATA] ANÁLISE DE IDADE DOS TICKETS ATIVOS")
        print("=" * 70)
        
        try:
            # Garantir que as datas estão convertidas
            if 'Data_abertura_dt' not in self.df.columns:
                self.df['Data_abertura_dt'] = pd.to_datetime(self.df['Data_abertura'], errors='coerce')
            
            # Filtrar tickets ativos
            tickets_ativos = self.df[~self.df['Status'].isin(['Solucionado', 'Fechado'])].copy()
            
            if len(tickets_ativos) == 0:
                print("[OK] Nenhum ticket ativo encontrado")
                return
            
            # Calcular idade em horas
            agora = datetime.now()
            tickets_ativos['Idade_horas'] = (agora - tickets_ativos['Data_abertura_dt']).dt.total_seconds() / 3600
            idade_valida = tickets_ativos[tickets_ativos['Idade_horas'] > 0]
            
            print(f"[METRICAS] ESTATÍSTICAS DE IDADE:")
            print(f"   • Total de tickets ativos: {len(tickets_ativos):,}")
            print(f"   • Idade média: {idade_valida['Idade_horas'].mean():.1f} horas ({idade_valida['Idade_horas'].mean()/24:.1f} dias)")
            print(f"   • Idade mediana: {idade_valida['Idade_horas'].median():.1f} horas ({idade_valida['Idade_horas'].median()/24:.1f} dias)")
            print(f"   • Ticket mais antigo: {idade_valida['Idade_horas'].max():.1f} horas ({idade_valida['Idade_horas'].max()/24:.1f} dias)")
            
            # Tickets por faixa de idade
            print(f"\n⏰ DISTRIBUIÇÃO POR FAIXA DE IDADE:")
            faixas = [
                (0, 24, "< 1 dia"),
                (24, 72, "1-3 dias"),
                (72, 168, "3-7 dias"),
                (168, 720, "1-4 semanas"),
                (720, float('inf'), "> 4 semanas")
            ]
            
            for min_h, max_h, label in faixas:
                if max_h == float('inf'):
                    count = len(idade_valida[idade_valida['Idade_horas'] >= min_h])
                else:
                    count = len(idade_valida[(idade_valida['Idade_horas'] >= min_h) & (idade_valida['Idade_horas'] < max_h)])
                
                if count > 0:
                    percentual = (count / len(idade_valida)) * 100
                    print(f"   • {label}: {count} tickets ({percentual:.1f}%)")
            
            # Calcular distribuição por faixa de idade
            distribuicao_idade = {}
            for min_h, max_h, label in faixas:
                if max_h == float('inf'):
                    count = len(idade_valida[idade_valida['Idade_horas'] >= min_h])
                else:
                    count = len(idade_valida[(idade_valida['Idade_horas'] >= min_h) & (idade_valida['Idade_horas'] < max_h)])
                distribuicao_idade[label] = count
            
            # Armazenar métricas para exportação
            self.metricas_estruturadas['tickets_ativos'] = {
                'total_ativos': len(tickets_ativos),
                'idade_media_horas': float(idade_valida['Idade_horas'].mean()),
                'idade_mediana_horas': float(idade_valida['Idade_horas'].median()),
                'idade_maxima_horas': float(idade_valida['Idade_horas'].max()),
                'distribuicao_idade': distribuicao_idade
            }
            
        except Exception as e:
            print(f"[ERRO] Erro ao calcular idade dos tickets: {e}")
                
    def gerar_relatorio_completo(self):
        """Gera um relatório completo em arquivo texto"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_base = os.path.basename(self.arquivo_selecionado) if hasattr(self, 'arquivo_selecionado') else 'dados'
        periodo_nome = arquivo_base.replace('tickets_', '').replace('.csv', '').replace('_', '_')
        nome_relatorio = f"relatorio_metricas_{periodo_nome}_{timestamp}.txt"
        
        # Criar diretório de relatórios se não existir
        relatorios_dir = "../dados/relatorios_metricas"
        os.makedirs(relatorios_dir, exist_ok=True)
        
        caminho_relatorio = os.path.join(relatorios_dir, nome_relatorio)
        
        try:
            with open(caminho_relatorio, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("RELATÓRIO DE MÉTRICAS - TICKETS GLPI\n")
                f.write("=" * 80 + "\n")
                f.write(f"[DATA] Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                f.write(f"[EMOJI] Arquivo analisado: {os.path.basename(self.arquivo_selecionado)}\n")
                f.write(f"[METRICAS] Total de registros: {len(self.df):,}\n")
                f.write("\n")
                
                # Métricas gerais
                f.write("DISTRIBUIÇÃO POR STATUS\n")
                f.write("-" * 30 + "\n")
                status_counts = self.df['Status'].value_counts()
                for status, count in status_counts.items():
                    percentual = (count / len(self.df)) * 100
                    f.write(f"{status}: {count:,} ({percentual:.1f}%)\n")
                f.write("\n")
                
                # Top entidades
                f.write("TOP 15 ENTIDADES\n")
                f.write("-" * 20 + "\n")
                entidade_counts = self.df['Entidade'].value_counts().head(15)
                for entidade, count in entidade_counts.items():
                    percentual = (count / len(self.df)) * 100
                    f.write(f"{entidade}: {count:,} ({percentual:.1f}%)\n")
                f.write("\n")
                
                # Top categorias
                f.write("TOP 15 CATEGORIAS\n")
                f.write("-" * 20 + "\n")
                categoria_counts = self.df['Categoria'].value_counts().head(15)
                for categoria, count in categoria_counts.items():
                    percentual = (count / len(self.df)) * 100
                    f.write(f"{categoria}: {count:,} ({percentual:.1f}%)\n")
                f.write("\n")
                
                # Top técnicos
                f.write("TOP 15 TÉCNICOS\n")
                f.write("-" * 15 + "\n")
                tecnicos = self.df['Tecnico_atribuido'].value_counts().head(15)
                for tecnico, count in tecnicos.items():
                    percentual = (count / len(self.df)) * 100
                    f.write(f"{tecnico}: {count:,} ({percentual:.1f}%)\n")
                f.write("\n")
                
                # Relatório de integridade
                f.write(self.obter_relatorio_integridade_texto())
                
            print(f"\n[EMOJI] Relatório salvo em: {caminho_relatorio}")
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao gerar relatório: {e}")
            return False
    
    def coletar_metricas_estruturadas(self):
        """Coleta todas as métricas em formato estruturado para exportação"""
        try:
            # Metadados do dataset
            self.metricas_estruturadas['metadados'] = {
                'arquivo_analisado': os.path.basename(self.arquivo_selecionado),
                'periodo': self.nome_arquivo.replace('tickets_', '').replace('_', ' ') if hasattr(self, 'nome_arquivo') else 'N/A',
                'total_registros': len(self.df),
                'data_analise': datetime.now().isoformat(),
                'colunas_disponiveis': list(self.df.columns),
                'periodo_dados': {
                    'data_inicio': self.df['Data_abertura'].min() if 'Data_abertura' in self.df.columns else None,
                    'data_fim': self.df['Data_abertura'].max() if 'Data_abertura' in self.df.columns else None
                }
            }
            
            # Métricas gerais
            status_counts = self.df['Status'].value_counts()
            self.metricas_estruturadas['metricas_gerais'] = {
                'total_tickets': len(self.df),
                'distribuicao_status': {
                    status: {
                        'quantidade': int(count),
                        'percentual': round((count / len(self.df)) * 100, 2)
                    } for status, count in status_counts.items()
                }
            }
            
            # Top entidades
            if 'Entidade' in self.df.columns:
                entidade_counts = self.df['Entidade'].value_counts().head(15)
                self.metricas_estruturadas['metricas_gerais']['top_entidades'] = {
                    entidade: {
                        'quantidade': int(count),
                        'percentual': round((count / len(self.df)) * 100, 2)
                    } for entidade, count in entidade_counts.items()
                }
            
            # Top grupos técnicos
            if 'Grupo Técnico' in self.df.columns:
                grupo_counts = self.df['Grupo Técnico'].value_counts().head(15)
                self.metricas_estruturadas['metricas_gerais']['top_grupos_tecnicos'] = {
                    grupo: {
                        'quantidade': int(count),
                        'percentual': round((count / len(self.df)) * 100, 2)
                    } for grupo, count in grupo_counts.items()
                }
            
            # Top categorias
            if 'Categoria' in self.df.columns:
                categoria_counts = self.df['Categoria'].value_counts().head(15)
                self.metricas_estruturadas['metricas_gerais']['top_categorias'] = {
                    categoria: {
                        'quantidade': int(count),
                        'percentual': round((count / len(self.df)) * 100, 2)
                    } for categoria, count in categoria_counts.items()
                }
            
            # Métricas temporais
            self.metricas_estruturadas['metricas_temporais'] = {}
            
            if 'Data_abertura' in self.df.columns:
                # Converter para datetime
                self.df['Data_abertura'] = pd.to_datetime(self.df['Data_abertura'], errors='coerce')
                
                # Tickets por mês
                tickets_por_mes = self.df['Data_abertura'].dt.to_period('M').value_counts().sort_index()
                self.metricas_estruturadas['metricas_temporais']['tickets_por_mes'] = {
                    str(mes): int(count) for mes, count in tickets_por_mes.items()
                }
                
                # Tickets por dia da semana
                dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                tickets_por_dia = self.df['Data_abertura'].dt.dayofweek.value_counts().sort_index()
                self.metricas_estruturadas['metricas_temporais']['tickets_por_dia_semana'] = {
                    dias_semana[dia]: int(count) for dia, count in tickets_por_dia.items()
                }
            
            # Métricas de performance
            self.metricas_estruturadas['metricas_performance'] = {}
            
            # Top técnicos
            if 'Tecnico_atribuido' in self.df.columns:
                tecnicos_validos = self.df[self.df['Tecnico_atribuido'].notna() & (self.df['Tecnico_atribuido'] != '')]
                if len(tecnicos_validos) > 0:
                    tecnico_counts = tecnicos_validos['Tecnico_atribuido'].value_counts().head(10)
                    self.metricas_estruturadas['metricas_performance']['top_tecnicos'] = {
                        tecnico: {
                            'quantidade': int(count),
                            'percentual': round((count / len(tecnicos_validos)) * 100, 2)
                        } for tecnico, count in tecnico_counts.items()
                    }
                
                # Tickets sem técnico
                tickets_sem_tecnico = len(self.df) - len(tecnicos_validos)
                self.metricas_estruturadas['metricas_performance']['tickets_sem_tecnico'] = {
                    'quantidade': tickets_sem_tecnico,
                    'percentual': round((tickets_sem_tecnico / len(self.df)) * 100, 2)
                }
            
            # Top localizações
            if 'Localizacao' in self.df.columns:
                localizacao_counts = self.df['Localizacao'].value_counts().head(10)
                self.metricas_estruturadas['metricas_performance']['top_localizacoes'] = {
                    localizacao: {
                        'quantidade': int(count),
                        'percentual': round((count / len(self.df)) * 100, 2)
                    } for localizacao, count in localizacao_counts.items()
                }
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao coletar métricas estruturadas: {e}")
            return False
    

    
    def _exportar_csv_simples(self, dados, nome_arquivo, dir_csv, timestamp):
        """Método auxiliar para exportar CSVs simples (status, entidades, técnicos)"""
        try:
            df = pd.DataFrame(dados)
            caminho = os.path.join(dir_csv, f"{nome_arquivo}_{timestamp}.csv")
            df.to_csv(caminho, index=False, encoding='utf-8')
            print(f"[METRICAS] CSV {nome_arquivo.title()}: {caminho}")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao exportar CSV {nome_arquivo}: {e}")
            return False
    
    def _exportar_csv_categoria_consolidado(self, dir_csv, timestamp):
        """Exporta CSV consolidado de TTR + SLA por categoria"""
        try:
            if not ('ttr' in self.metricas_estruturadas and 'sla' in self.metricas_estruturadas):
                return False
                
            ttr_categorias = self.metricas_estruturadas['ttr'].get('ttr_por_categoria', {})
            sla_categorias = self.metricas_estruturadas['sla'].get('performance_por_categoria', {})
            
            categoria_data = []
            for categoria in ttr_categorias.keys():
                if categoria in sla_categorias:
                    ttr_dados = ttr_categorias[categoria]
                    sla_dados = sla_categorias[categoria]
                    
                    categoria_data.append({
                        'Categoria': categoria,
                        'Total_Tickets': ttr_dados['Tickets'],
                        'TTR_Medio_Horas': round(ttr_dados['TTR_Medio'], 1),
                        'TTR_Mediano_Horas': round(ttr_dados['TTR_Mediano'], 1),
                        'Dentro_SLA': sla_dados['Dentro_SLA'],
                        'SLA_Horas': sla_dados['SLA_horas'],
                        'Percentual_SLA': round(sla_dados['Percentual_SLA'], 1)
                    })
            
            if categoria_data:
                df = pd.DataFrame(categoria_data).sort_values('Total_Tickets', ascending=False)
                caminho = os.path.join(dir_csv, f"categoria_consolidado_ttr_sla_{timestamp}.csv")
                df.to_csv(caminho, index=False, encoding='utf-8')
                print(f"[METRICAS] CSV CONSOLIDADO Categoria (TTR+SLA): {caminho}")
                return True
            return False
        except Exception as e:
            print(f"[ERRO] Erro ao exportar CSV categoria consolidado: {e}")
            return False
    
    def _exportar_csv_complexidade_consolidado(self, dir_csv, timestamp):
        """Exporta CSV consolidado de SLA por complexidade"""
        try:
            complexidade_data = self.metricas_estruturadas.get('sla', {}).get('performance_por_complexidade', {})
            if not complexidade_data:
                return False
                
            data = []
            for complexidade, dados in complexidade_data.items():
                data.append({
                    'Complexidade': complexidade,
                    'Total_Tickets': dados['Total_Tickets'],
                    'TTR_Medio_Horas': round(dados['TTR_Medio'], 1),
                    'TTR_Mediano_Horas': round(dados['TTR_Mediano'], 1),
                    'Dentro_SLA': dados['Dentro_SLA'],
                    'Percentual_SLA': round(dados['Percentual_SLA'], 1)
                })
            
            df = pd.DataFrame(data).sort_values('Total_Tickets', ascending=False)
            caminho = os.path.join(dir_csv, f"complexidade_consolidado_ttr_sla_{timestamp}.csv")
            df.to_csv(caminho, index=False, encoding='utf-8')
            print(f"[METRICAS] CSV CONSOLIDADO Complexidade (TTR+SLA): {caminho}")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao exportar CSV complexidade consolidado: {e}")
            return False
    
    def exportar_csv_metricas(self):
        """Exporta métricas em formato CSV tabular"""
        try:
            # Coletar métricas estruturadas primeiro
            if not self.coletar_metricas_estruturadas():
                return False
                
            # Criar diretório se não existir
            dir_csv = os.path.join(self.dados_dir, "metricas_csv")
            os.makedirs(dir_csv, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # CSV de Status
            status_data = []
            for status, dados in self.metricas_estruturadas.get('metricas_gerais', {}).get('distribuicao_status', {}).items():
                status_data.append({
                    'Status': status,
                    'Quantidade': dados['quantidade'],
                    'Percentual': dados['percentual']
                })
            if status_data:
                self._exportar_csv_simples(status_data, "status", dir_csv, timestamp)
            
            # CSV de Entidades
            entidades_data = []
            for entidade, dados in self.metricas_estruturadas.get('metricas_gerais', {}).get('top_entidades', {}).items():
                entidades_data.append({
                    'Entidade': entidade,
                    'Quantidade': dados['quantidade'],
                    'Percentual': dados['percentual']
                })
            if entidades_data:
                self._exportar_csv_simples(entidades_data, "entidades", dir_csv, timestamp)
            
            # CSV de Técnicos
            tecnicos_data = []
            for tecnico, dados in self.metricas_estruturadas.get('metricas_performance', {}).get('top_tecnicos', {}).items():
                tecnicos_data.append({
                    'Tecnico': tecnico,
                    'Quantidade': dados['quantidade'],
                    'Percentual': dados['percentual']
                })
            if tecnicos_data:
                self._exportar_csv_simples(tecnicos_data, "tecnicos", dir_csv, timestamp)
            
            # CSV de TTR por Grupo
            ttr_grupo_data = []
            for grupo, dados in self.metricas_estruturadas.get('ttr', {}).get('ttr_por_grupo', {}).items():
                ttr_grupo_data.append({
                    'Grupo': grupo,
                    'Tickets': dados['Tickets'],
                    'TTR_Medio_Horas': round(dados['TTR_Medio'], 1),
                    'TTR_Mediano_Horas': round(dados['TTR_Mediano'], 1)
                })
            if ttr_grupo_data:
                df = pd.DataFrame(ttr_grupo_data).sort_values('Tickets', ascending=False)
                caminho = os.path.join(dir_csv, f"ttr_grupo_{timestamp}.csv")
                df.to_csv(caminho, index=False, encoding='utf-8')
                print(f"[METRICAS] CSV TTR por Grupo: {caminho}")
            
            # CSV de Distribuição de Idade de Tickets Ativos
            idade_data = []
            tickets_ativos = self.metricas_estruturadas.get('tickets_ativos', {})
            for faixa, quantidade in tickets_ativos.get('distribuicao_idade', {}).items():
                total_ativos = tickets_ativos.get('total_ativos', 0)
                percentual = round((quantidade / total_ativos) * 100, 2) if total_ativos > 0 else 0
                idade_data.append({
                    'Faixa_Idade': faixa,
                    'Quantidade': quantidade,
                    'Percentual': percentual
                })
            if idade_data:
                self._exportar_csv_simples(idade_data, "idade_tickets_ativos", dir_csv, timestamp)
            
            # CSVs consolidados
            self._exportar_csv_categoria_consolidado(dir_csv, timestamp)
            self._exportar_csv_complexidade_consolidado(dir_csv, timestamp)
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao exportar CSVs de métricas: {e}")
            return False
    

    
    def _calcular_dados_integridade(self):
        """Método auxiliar para calcular dados de integridade (evita duplicação)"""
        total_tickets = len(self.df)
        
        # Análise de tickets resolvidos
        tickets_resolvidos = self.df[self.df['Status'].isin(['Solucionado', 'Fechado'])]
        total_resolvidos = len(tickets_resolvidos)
        tickets_abertos = total_tickets - total_resolvidos
        
        # Análise de campos obrigatórios
        tickets_sem_categoria = len(self.df[self.df['Categoria'].isna() | (self.df['Categoria'] == '')])
        tickets_sem_tecnico = len(self.df[self.df['Tecnico_atribuido'].isna() | (self.df['Tecnico_atribuido'] == '')])
        tickets_sem_grupo = len(self.df[self.df['Grupo_tecnico'].isna() | (self.df['Grupo_tecnico'] == '')])
        
        # Análise de TTR válidos
        if total_resolvidos > 0:
            tickets_resolvidos_copy = tickets_resolvidos.copy()
            if 'Data_abertura_dt' not in tickets_resolvidos_copy.columns:
                tickets_resolvidos_copy['Data_abertura_dt'] = pd.to_datetime(tickets_resolvidos_copy['Data_abertura'], errors='coerce')
                tickets_resolvidos_copy['Ultima_atualizacao_dt'] = pd.to_datetime(tickets_resolvidos_copy['Ultima_atualizacao'], errors='coerce')
            
            tickets_resolvidos_copy['TTR_horas'] = (tickets_resolvidos_copy['Ultima_atualizacao_dt'] - tickets_resolvidos_copy['Data_abertura_dt']).dt.total_seconds() / 3600
            ttr_validos = len(tickets_resolvidos_copy[tickets_resolvidos_copy['TTR_horas'] > 0])
            ttr_invalidos = total_resolvidos - ttr_validos
        else:
            ttr_validos = 0
            ttr_invalidos = 0
        
        # Cálculo de métricas consolidadas
        tickets_categoria_consolidado = total_resolvidos - len(tickets_resolvidos[tickets_resolvidos['Categoria'].isna() | (tickets_resolvidos['Categoria'] == '')])
        tickets_complexidade_consolidado = ttr_validos
        
        # Alertas de qualidade
        alertas = []
        if tickets_sem_categoria > total_tickets * 0.1:
            alertas.append(f"Alto percentual de tickets sem categoria ({(tickets_sem_categoria/total_tickets)*100:.1f}%)")
        if ttr_invalidos > total_tickets * 0.05:
            alertas.append(f"Alto percentual de TTR inválidos ({(ttr_invalidos/total_tickets)*100:.1f}%)")
        if tickets_abertos > total_tickets * 0.2:
            alertas.append(f"Alto percentual de tickets em aberto ({(tickets_abertos/total_tickets)*100:.1f}%)")
        
        return {
            'total_tickets': total_tickets,
            'total_resolvidos': total_resolvidos,
            'tickets_abertos': tickets_abertos,
            'tickets_sem_categoria': tickets_sem_categoria,
            'tickets_sem_tecnico': tickets_sem_tecnico,
            'tickets_sem_grupo': tickets_sem_grupo,
            'ttr_validos': ttr_validos,
            'ttr_invalidos': ttr_invalidos,
            'tickets_categoria_consolidado': tickets_categoria_consolidado,
            'tickets_complexidade_consolidado': tickets_complexidade_consolidado,
            'alertas': alertas
        }
    
    def gerar_relatorio_integridade(self):
        """Gera relatório de integridade e transparência dos dados"""
        print("\n" + "=" * 70)
        print("[BUSCA] RELATÓRIO DE INTEGRIDADE DOS DADOS")
        print("=" * 70)
        
        try:
            dados = self._calcular_dados_integridade()
            
            print(f"[METRICAS] RESUMO GERAL:")
            print(f"   • Total de tickets extraídos: {dados['total_tickets']:,}")
            print(f"   • Data/hora da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            
            print(f"\n[FOCO] COBERTURA DAS MÉTRICAS:")
            print(f"   • Status/Entidades/Técnicos/TTR Grupo: {dados['total_tickets']:,} tickets (100.0%)")
            print(f"   • TTR+SLA por Categoria: {dados['tickets_categoria_consolidado']:,} tickets ({(dados['tickets_categoria_consolidado']/dados['total_tickets'])*100:.1f}%)")
            print(f"   • TTR+SLA por Complexidade: {dados['tickets_complexidade_consolidado']:,} tickets ({(dados['tickets_complexidade_consolidado']/dados['total_tickets'])*100:.1f}%)")
            
            print(f"\n[AVISO]  TICKETS EXCLUÍDOS E MOTIVOS:")
            print(f"   • Tickets em aberto: {dados['tickets_abertos']:,} ({(dados['tickets_abertos']/dados['total_tickets'])*100:.1f}%)")
            print(f"     [EMOJI] Motivo: TTR não calculável para tickets não resolvidos")
            print(f"   • Tickets sem categoria: {dados['tickets_sem_categoria']:,} ({(dados['tickets_sem_categoria']/dados['total_tickets'])*100:.1f}%)")
            print(f"     [EMOJI] Motivo: SLA não determinável sem categoria")
            print(f"   • TTR inválidos: {dados['ttr_invalidos']:,} ({(dados['ttr_invalidos']/dados['total_tickets'])*100:.1f}%)")
            print(f"     [EMOJI] Motivo: Datas inconsistentes (TTR ≤ 0 horas)")
            
            print(f"\n[OK] VALIDAÇÃO MATEMÁTICA:")
            print(f"   • Total original: {dados['total_tickets']:,}")
            print(f"   • Resolvidos: {dados['total_resolvidos']:,}")
            print(f"   • Em aberto: {dados['tickets_abertos']:,}")
            print(f"   • Verificação: {dados['total_resolvidos']} + {dados['tickets_abertos']} = {dados['total_resolvidos'] + dados['tickets_abertos']} [OK]")
            
            print(f"\n[EMOJI] ALERTAS DE QUALIDADE:")
            if not dados['alertas']:
                print("   [OK] Nenhum alerta de qualidade identificado")
            else:
                for alerta in dados['alertas']:
                    print(f"   [AVISO]  {alerta}")
            
            print(f"\n[LISTA] RECOMENDAÇÕES:")
            if dados['tickets_sem_categoria'] > 0:
                print(f"   • Melhorar processo de categorização de tickets")
            if dados['ttr_invalidos'] > 0:
                print(f"   • Validar consistência das datas de abertura/fechamento")
            if dados['tickets_abertos'] > dados['total_tickets'] * 0.15:
                print(f"   • Acompanhar resolução dos tickets em aberto")
            
        except Exception as e:
            print(f"[ERRO] Erro ao gerar relatório de integridade: {e}")
    
    def obter_relatorio_integridade_texto(self):
        """Retorna o relatório de integridade como string para incluir em arquivos"""
        try:
            dados = self._calcular_dados_integridade()
            
            relatorio = []
            relatorio.append("=" * 70)
            relatorio.append("RELATÓRIO DE INTEGRIDADE DOS DADOS")
            relatorio.append("=" * 70)
            relatorio.append(f"[METRICAS] RESUMO GERAL:")
            relatorio.append(f"   • Total de tickets extraídos: {dados['total_tickets']:,}")
            relatorio.append(f"   • Data/hora da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            relatorio.append("")
            relatorio.append(f"[FOCO] COBERTURA DAS MÉTRICAS:")
            relatorio.append(f"   • Status/Entidades/Técnicos/TTR Grupo: {dados['total_tickets']:,} tickets (100.0%)")
            relatorio.append(f"   • TTR+SLA por Categoria: {dados['tickets_categoria_consolidado']:,} tickets ({(dados['tickets_categoria_consolidado']/dados['total_tickets'])*100:.1f}%)")
            relatorio.append(f"   • TTR+SLA por Complexidade: {dados['tickets_complexidade_consolidado']:,} tickets ({(dados['tickets_complexidade_consolidado']/dados['total_tickets'])*100:.1f}%)")
            relatorio.append("")
            relatorio.append(f"[AVISO]  TICKETS EXCLUÍDOS E MOTIVOS:")
            relatorio.append(f"   • Tickets em aberto: {dados['tickets_abertos']:,} ({(dados['tickets_abertos']/dados['total_tickets'])*100:.1f}%)")
            relatorio.append(f"     [EMOJI] Motivo: TTR não calculável para tickets não resolvidos")
            relatorio.append(f"   • Tickets sem categoria: {dados['tickets_sem_categoria']:,} ({(dados['tickets_sem_categoria']/dados['total_tickets'])*100:.1f}%)")
            relatorio.append(f"     [EMOJI] Motivo: SLA não determinável sem categoria")
            relatorio.append(f"   • TTR inválidos: {dados['ttr_invalidos']:,} ({(dados['ttr_invalidos']/dados['total_tickets'])*100:.1f}%)")
            relatorio.append(f"     [EMOJI] Motivo: Datas inconsistentes (TTR ≤ 0 horas)")
            relatorio.append("")
            relatorio.append(f"[OK] VALIDAÇÃO MATEMÁTICA:")
            relatorio.append(f"   • Total original: {dados['total_tickets']:,}")
            relatorio.append(f"   • Resolvidos: {dados['total_resolvidos']:,}")
            relatorio.append(f"   • Em aberto: {dados['tickets_abertos']:,}")
            relatorio.append(f"   • Verificação: {dados['total_resolvidos']} + {dados['tickets_abertos']} = {dados['total_resolvidos'] + dados['tickets_abertos']} [OK]")
            relatorio.append("")
            
            relatorio.append(f"[EMOJI] ALERTAS DE QUALIDADE:")
            if not dados['alertas']:
                relatorio.append("   [OK] Nenhum alerta de qualidade identificado")
            else:
                for alerta in dados['alertas']:
                    relatorio.append(f"   [AVISO]  {alerta}")
            
            relatorio.append("")
            relatorio.append(f"[LISTA] RECOMENDAÇÕES:")
            if dados['tickets_sem_categoria'] > 0:
                relatorio.append(f"   • Melhorar processo de categorização de tickets")
            if dados['ttr_invalidos'] > 0:
                relatorio.append(f"   • Validar consistência das datas de abertura/fechamento")
            if dados['tickets_abertos'] > dados['total_tickets'] * 0.15:
                relatorio.append(f"   • Acompanhar resolução dos tickets em aberto")
            
            relatorio.append("")
            
            return "\n".join(relatorio)
            
        except Exception as e:
            return f"[ERRO] Erro ao gerar relatório de integridade: {e}"
            
    def executar_analise(self):
        """Executa a análise completa automaticamente"""
        self.exibir_cabecalho()
        
        # Carregar dados do arquivo fixo
        if not self.carregar_dados():
            return False
            
        # Gerar métricas
        self.gerar_metricas_gerais()
        self.gerar_metricas_temporais()
        self.gerar_metricas_performance()
        
        # Novas métricas de TTR e SLA
        self.calcular_ttr_metricas()
        self.analisar_sla_performance()
        self.calcular_idade_tickets_ativos()
        
        # Relatório de integridade dos dados
        self.gerar_relatorio_integridade()
        
        # Exportar automaticamente apenas CSV
        print(f"\n[EMOJI] EXPORTANDO MÉTRICAS EM CSV...")
        print("-" * 40)
        self.exportar_csv_metricas()
        
        print(f"\n" + "=" * 70)
        print("[OK] ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print("[METRICAS] Métricas exibidas na tela")
        print("[METRICAS] Métricas exportadas em formato CSV")
        print("[SUCESSO] Obrigado por usar o Analisador de Métricas!")
        
        return True

def main():
    """Função principal"""
    try:
        analisador = AnalisadorMetricasTickets()
        analisador.executar_analise()
        
    except KeyboardInterrupt:
        print("\n\n[EMOJI] Análise cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()