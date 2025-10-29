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
import json
import yaml
from datetime import datetime
from collections import Counter
import glob

class AnalisadorMetricasTickets:
    def __init__(self):
        self.dados_dir = "../dados"
        self.df = None
        self.arquivo_selecionado = None
        self.periodo_selecionado = None
        self.metricas_estruturadas = {}
        
    def exibir_cabecalho(self):
        """Exibe o cabeçalho do programa"""
        print("=" * 70)
        print("[BUSCA] ANALISADOR DE MÉTRICAS DE TICKETS GLPI")
        print("=" * 70)
        print("[METRICAS] Análise de dados dos tickets extraídos da API GLPI")
        print("[GRAFICO] Geração de relatórios e estatísticas detalhadas")
        print()
        
    def listar_arquivos_disponiveis(self):
        """Lista todos os arquivos CSV disponíveis organizados por período"""
        print("[ARQUIVO] ARQUIVOS DISPONÍVEIS PARA ANÁLISE:")
        print("-" * 50)
        
        opcoes = {}
        contador = 1
        
        # Mapear pastas para descrições amigáveis
        pastas_info = {
            "tickets_ultimo_mes": "[DATA] Último mês",
            "tickets_mensais": "[DATA] Últimos 3 meses", 
            "tickets_6_meses": "[DATA] Últimos 6 meses"
        }
        
        for pasta, descricao in pastas_info.items():
            pasta_path = os.path.join(self.dados_dir, pasta)
            if os.path.exists(pasta_path):
                arquivos = glob.glob(os.path.join(pasta_path, "*.csv"))
                if arquivos:
                    print(f"\n{descricao}")
                    for arquivo in sorted(arquivos, reverse=True):  # Mais recente primeiro
                        nome_arquivo = os.path.basename(arquivo)
                        # Extrair timestamp do nome do arquivo
                        if "_" in nome_arquivo:
                            timestamp_part = nome_arquivo.split("_")[-1].replace(".csv", "")
                            try:
                                # Converter timestamp para data legível
                                data_obj = datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")
                                data_formatada = data_obj.strftime("%d/%m/%Y às %H:%M")
                            except:
                                data_formatada = timestamp_part
                        else:
                            data_formatada = "Data não identificada"
                            
                        print(f"   {contador}. {nome_arquivo}")
                        print(f"      [DATA] Gerado em: {data_formatada}")
                        opcoes[contador] = {
                            'arquivo': arquivo,
                            'pasta': pasta,
                            'nome': nome_arquivo,
                            'data': data_formatada
                        }
                        contador += 1
        
        if not opcoes:
            print("[ERRO] Nenhum arquivo CSV encontrado!")
            print("[DICA] Execute primeiro o script de extração de dados.")
            return None
            
        return opcoes
        
    def selecionar_arquivo(self):
        """Permite ao usuário selecionar qual arquivo analisar"""
        opcoes = self.listar_arquivos_disponiveis()
        if not opcoes:
            return False
            
        print(f"\n[LISTA] SELEÇÃO DE ARQUIVO:")
        print("-" * 30)
        
        while True:
            try:
                escolha = input(f"[EMOJI] Digite o número do arquivo para analisar (1-{len(opcoes)}): ").strip()
                
                if not escolha:
                    print("[ERRO] Por favor, digite um número.")
                    continue
                    
                escolha = int(escolha)
                
                if escolha in opcoes:
                    arquivo_info = opcoes[escolha]
                    self.arquivo_selecionado = arquivo_info['arquivo']
                    self.periodo_selecionado = arquivo_info['pasta']
                    
                    print(f"\n[OK] Arquivo selecionado:")
                    print(f"   [EMOJI] {arquivo_info['nome']}")
                    print(f"   [DATA] {arquivo_info['data']}")
                    print(f"   [ARQUIVO] Período: {arquivo_info['pasta'].replace('tickets_', '').replace('_', ' ')}")
                    return True
                else:
                    print(f"[ERRO] Opção inválida. Digite um número entre 1 e {len(opcoes)}.")
                    
            except ValueError:
                print("[ERRO] Por favor, digite apenas números.")
            except KeyboardInterrupt:
                print("\n\n[EMOJI] Análise cancelada pelo usuário.")
                return False
                
    def carregar_dados(self):
        """Carrega os dados do arquivo CSV selecionado"""
        try:
            print(f"\n[PROCESSO] Carregando dados do arquivo...")
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
                
    def gerar_relatorio_completo(self):
        """Gera um relatório completo em arquivo texto"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        periodo_nome = self.periodo_selecionado.replace('tickets_', '').replace('_', '_')
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
                'periodo': self.periodo_selecionado.replace('tickets_', '').replace('_', ' '),
                'total_registros': len(self.df),
                'data_analise': datetime.now().isoformat(),
                'colunas_disponiveis': list(self.df.columns),
                'periodo_dados': {
                    'data_inicio': self.df['Data de Abertura'].min() if 'Data de Abertura' in self.df.columns else None,
                    'data_fim': self.df['Data de Abertura'].max() if 'Data de Abertura' in self.df.columns else None
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
            
            if 'Data de Abertura' in self.df.columns:
                # Converter para datetime
                self.df['Data de Abertura'] = pd.to_datetime(self.df['Data de Abertura'], errors='coerce')
                
                # Tickets por mês
                tickets_por_mes = self.df['Data de Abertura'].dt.to_period('M').value_counts().sort_index()
                self.metricas_estruturadas['metricas_temporais']['tickets_por_mes'] = {
                    str(mes): int(count) for mes, count in tickets_por_mes.items()
                }
                
                # Tickets por dia da semana
                dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                tickets_por_dia = self.df['Data de Abertura'].dt.dayofweek.value_counts().sort_index()
                self.metricas_estruturadas['metricas_temporais']['tickets_por_dia_semana'] = {
                    dias_semana[dia]: int(count) for dia, count in tickets_por_dia.items()
                }
            
            # Métricas de performance
            self.metricas_estruturadas['metricas_performance'] = {}
            
            # Top técnicos
            if 'Técnico Atribuído' in self.df.columns:
                tecnicos_validos = self.df[self.df['Técnico Atribuído'].notna() & (self.df['Técnico Atribuído'] != '')]
                if len(tecnicos_validos) > 0:
                    tecnico_counts = tecnicos_validos['Técnico Atribuído'].value_counts().head(10)
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
            if 'Localização' in self.df.columns:
                localizacao_counts = self.df['Localização'].value_counts().head(10)
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
    
    def exportar_json(self):
        """Exporta métricas em formato JSON"""
        try:
            # Criar diretório se não existir
            dir_json = os.path.join(self.dados_dir, "metricas_json")
            os.makedirs(dir_json, exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            periodo_nome = self.periodo_selecionado.replace('tickets_', '')
            nome_arquivo = f"metricas_{periodo_nome}_{timestamp}.json"
            caminho_json = os.path.join(dir_json, nome_arquivo)
            
            # Salvar JSON
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(self.metricas_estruturadas, f, ensure_ascii=False, indent=2)
            
            print(f"[EMOJI] JSON exportado: {caminho_json}")
            return caminho_json
            
        except Exception as e:
            print(f"[ERRO] Erro ao exportar JSON: {e}")
            return None
    
    def exportar_yaml(self):
        """Exporta métricas em formato YAML"""
        try:
            # Criar diretório se não existir
            dir_yaml = os.path.join(self.dados_dir, "metricas_yaml")
            os.makedirs(dir_yaml, exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            periodo_nome = self.periodo_selecionado.replace('tickets_', '')
            nome_arquivo = f"metricas_{periodo_nome}_{timestamp}.yaml"
            caminho_yaml = os.path.join(dir_yaml, nome_arquivo)
            
            # Salvar YAML
            with open(caminho_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(self.metricas_estruturadas, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            print(f"[EMOJI] YAML exportado: {caminho_yaml}")
            return caminho_yaml
            
        except Exception as e:
            print(f"[ERRO] Erro ao exportar YAML: {e}")
            return None
    
    def exportar_csv_metricas(self):
        """Exporta métricas em formato CSV tabular"""
        try:
            # Criar diretório se não existir
            dir_csv = os.path.join(self.dados_dir, "metricas_csv")
            os.makedirs(dir_csv, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            periodo_nome = self.periodo_selecionado.replace('tickets_', '')
            
            # CSV de Status
            if 'metricas_gerais' in self.metricas_estruturadas and 'distribuicao_status' in self.metricas_estruturadas['metricas_gerais']:
                status_data = []
                for status, dados in self.metricas_estruturadas['metricas_gerais']['distribuicao_status'].items():
                    status_data.append({
                        'Status': status,
                        'Quantidade': dados['quantidade'],
                        'Percentual': dados['percentual']
                    })
                
                df_status = pd.DataFrame(status_data)
                caminho_status = os.path.join(dir_csv, f"status_{periodo_nome}_{timestamp}.csv")
                df_status.to_csv(caminho_status, index=False, encoding='utf-8')
                print(f"[METRICAS] CSV Status: {caminho_status}")
            
            # CSV de Entidades
            if 'metricas_gerais' in self.metricas_estruturadas and 'top_entidades' in self.metricas_estruturadas['metricas_gerais']:
                entidades_data = []
                for entidade, dados in self.metricas_estruturadas['metricas_gerais']['top_entidades'].items():
                    entidades_data.append({
                        'Entidade': entidade,
                        'Quantidade': dados['quantidade'],
                        'Percentual': dados['percentual']
                    })
                
                df_entidades = pd.DataFrame(entidades_data)
                caminho_entidades = os.path.join(dir_csv, f"entidades_{periodo_nome}_{timestamp}.csv")
                df_entidades.to_csv(caminho_entidades, index=False, encoding='utf-8')
                print(f"[METRICAS] CSV Entidades: {caminho_entidades}")
            
            # CSV de Técnicos
            if 'metricas_performance' in self.metricas_estruturadas and 'top_tecnicos' in self.metricas_estruturadas['metricas_performance']:
                tecnicos_data = []
                for tecnico, dados in self.metricas_estruturadas['metricas_performance']['top_tecnicos'].items():
                    tecnicos_data.append({
                        'Tecnico': tecnico,
                        'Quantidade': dados['quantidade'],
                        'Percentual': dados['percentual']
                    })
                
                df_tecnicos = pd.DataFrame(tecnicos_data)
                caminho_tecnicos = os.path.join(dir_csv, f"tecnicos_{periodo_nome}_{timestamp}.csv")
                df_tecnicos.to_csv(caminho_tecnicos, index=False, encoding='utf-8')
                print(f"[METRICAS] CSV Técnicos: {caminho_tecnicos}")
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao exportar CSVs de métricas: {e}")
            return False
    
    def exportar_formatos_estruturados(self):
        """Exporta métricas em todos os formatos estruturados"""
        print(f"\n[EMOJI] EXPORTAÇÃO DE FORMATOS ESTRUTURADOS:")
        print("-" * 50)
        
        # Coletar métricas estruturadas
        if not self.coletar_metricas_estruturadas():
            return False
        
        # Exportar em diferentes formatos
        json_path = self.exportar_json()
        yaml_path = self.exportar_yaml()
        csv_success = self.exportar_csv_metricas()
        
        print(f"\n[OK] Exportação concluída!")
        print(f"🤖 Formatos ideais para IA/Copilot Studio:")
        print(f"   [EMOJI] JSON: Estruturado para APIs e processamento")
        print(f"   [EMOJI] YAML: Legível para humanos e configuração")
        print(f"   [METRICAS] CSV: Tabular para análise e visualização")
        
        return True
            
    def executar_analise(self):
        """Executa a análise completa"""
        self.exibir_cabecalho()
        
        # Selecionar arquivo
        if not self.selecionar_arquivo():
            return False
            
        # Carregar dados
        if not self.carregar_dados():
            return False
            
        # Gerar métricas
        self.gerar_metricas_gerais()
        self.gerar_metricas_temporais()
        self.gerar_metricas_performance()
        
        # Perguntar sobre exportações
        print(f"\n[EMOJI] OPÇÕES DE EXPORTAÇÃO:")
        print("-" * 30)
        print("1. Relatório em texto (.txt)")
        print("2. Formatos estruturados (JSON/YAML/CSV)")
        print("3. Ambos")
        print("4. Nenhum")
        
        while True:
            try:
                opcao = input("[PROCESSO] Escolha uma opção (1-4): ").strip()
                
                if opcao == '1':
                    self.gerar_relatorio_completo()
                    break
                elif opcao == '2':
                    self.exportar_formatos_estruturados()
                    break
                elif opcao == '3':
                    self.gerar_relatorio_completo()
                    self.exportar_formatos_estruturados()
                    break
                elif opcao == '4':
                    break
                else:
                    print("[ERRO] Opção inválida. Digite 1, 2, 3 ou 4.")
                    
            except KeyboardInterrupt:
                print("\n\n[EMOJI] Exportação cancelada pelo usuário.")
                break
            
        print(f"\n" + "=" * 70)
        print("[OK] ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print("[METRICAS] Métricas exibidas na tela")
        if opcao in ['1', '3']:
            print("[EMOJI] Relatório detalhado salvo em arquivo")
        if opcao in ['2', '3']:
            print("🤖 Formatos estruturados exportados para IA")
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