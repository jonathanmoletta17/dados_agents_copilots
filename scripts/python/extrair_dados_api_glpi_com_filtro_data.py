#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair dados de tickets da API do GLPI com FILTRO DE DATA
Permite escolher um range de datas específico (ex: últimos 6 meses)
"""

import requests
import csv
import html
import re
import json
import argparse
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Configurar encoding para Windows
if os.name == 'nt':  # Windows
    import locale
    try:
        # Tentar configurar UTF-8
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            # Fallback para configuração padrão do Windows
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except locale.Error:
            pass
    
    # Configurar stdout/stderr para UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        # Para versões mais antigas do Python
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

class GLPIAPIExtractorComFiltroData:
    def __init__(self, api_url, app_token, user_token):
        """Inicializa o extrator da API do GLPI com filtro de data"""
        self.api_url = api_url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        self.session_token = None
        self.session = requests.Session()
        
        # Cache para evitar chamadas repetidas
        self.cache_usuarios = {}
        self.cache_entidades = {}
        self.cache_categorias = {}
        self.cache_localizacoes = {}
        self.cache_grupos = {}
        
        # Headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'App-Token': self.app_token
        })
    
    def init_session(self):
        """Inicia sessão na API do GLPI"""
        try:
            print("[SEGURANCA] Iniciando sessão na API do GLPI...")
            
            url = f"{self.api_url}/initSession"
            headers = {
                'Authorization': f'user_token {self.user_token}',
                'App-Token': self.app_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('session_token')
                self.session.headers.update({'Session-Token': self.session_token})
                print(f"[OK] Sessão iniciada com sucesso!")
                return True
            else:
                print(f"[ERRO] Erro ao iniciar sessão: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERRO] Erro na conexão: {e}")
            return False
    
    def kill_session(self):
        """Encerra sessão na API do GLPI"""
        if self.session_token:
            try:
                url = f"{self.api_url}/killSession"
                response = self.session.get(url)
                print("[EMOJI] Sessão encerrada")
            except:
                pass
    
    def calcular_periodo_predefinido(self, periodo):
        """Calcula datas para períodos pré-definidos"""
        hoje = datetime.now()
        
        if periodo == "ultimos_6_meses":
            data_inicial = hoje - timedelta(days=180)
            data_final = hoje
            descricao = "Últimos 6 meses"
        elif periodo == "ultimo_ano":
            data_inicial = hoje - timedelta(days=365)
            data_final = hoje
            descricao = "Último ano"
        elif periodo == "ultimos_3_meses":
            data_inicial = hoje - timedelta(days=90)
            data_final = hoje
            descricao = "Últimos 3 meses"
        elif periodo == "ultimo_mes":
            data_inicial = hoje - timedelta(days=30)
            data_final = hoje
            descricao = "Último mês"
        elif periodo == "ano_atual":
            data_inicial = datetime(hoje.year, 1, 1)
            data_final = hoje
            descricao = f"Ano atual ({hoje.year})"
        elif periodo == "ano_passado":
            ano_passado = hoje.year - 1
            data_inicial = datetime(ano_passado, 1, 1)
            data_final = datetime(ano_passado, 12, 31, 23, 59, 59)
            descricao = f"Ano passado ({ano_passado})"
        else:
            # Padrão: últimos 6 meses
            data_inicial = hoje - timedelta(days=180)
            data_final = hoje
            descricao = "Últimos 6 meses (padrão)"
        
        return data_inicial, data_final, descricao
    

    
    def limpar_descricao(self, descricao_raw):
        """Limpa e otimiza a descrição do ticket"""
        if not descricao_raw:
            return ""
        
        try:
            descricao = html.unescape(str(descricao_raw))
            descricao = re.sub(r'<[^>]+>', '', descricao)
            descricao = re.sub(r'\s+', ' ', descricao)
            descricao = descricao.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            
            # Remover caracteres Unicode problemáticos
            descricao = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f]', '', descricao)
            
            if len(descricao) > 500:
                descricao = descricao[:497] + "..."
            
            return descricao.strip()
        except Exception as e:
            print(f"   [AVISO] Erro ao limpar descrição: {e}")
            return ""
    
    def limpar_campo_texto(self, texto):
        """Limpa campos de texto"""
        if not texto:
            return ""
        
        try:
            texto = str(texto)
            texto = texto.replace('\r', '').replace('\n', ' ').replace('\t', ' ')
            texto = texto.replace('"', '""')
            texto = re.sub(r'\s+', ' ', texto)
            
            # Remover caracteres Unicode problemáticos
            texto = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f]', '', texto)
            
            return texto.strip()
        except Exception as e:
            print(f"   [AVISO] Erro ao limpar campo de texto: {e}")
            return ""
    
    def formatar_data(self, data_str):
        """Formata data para o padrão brasileiro"""
        if not data_str or data_str == 'NULL':
            return ""
        
        try:
            if ' ' in data_str:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
                return data_obj.strftime('%d/%m/%Y %H:%M:%S')
            else:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                return data_obj.strftime('%d/%m/%Y')
        except:
            return str(data_str)
    
    def traduzir_status(self, status_id):
        """Traduz ID do status para texto"""
        status_map = {
            1: 'Novo',
            2: 'Em andamento (atribuído)',
            3: 'Em andamento (planejado)',
            4: 'Pendente',
            5: 'Solucionado',
            6: 'Fechado'
        }
        return status_map.get(int(status_id), f'Status {status_id}')
    
    def carregar_cache_usuarios(self):
        """Carrega todos os usuários em cache"""
        print("[EMOJI] Carregando cache de usuários...")
        try:
            range_start = 0
            range_limit = 1000
            
            while True:
                url = f"{self.api_url}/User"
                params = {'range': f'{range_start}-{range_start + range_limit - 1}'}
                response = self.session.get(url, params=params)
                
                if response.status_code in [200, 206]:
                    users = response.json()
                    if not users:
                        break
                    
                    for user in users:
                        user_id = str(user.get('id'))
                        firstname = user.get('firstname', '')
                        realname = user.get('realname', '')
                        nome_completo = f"{firstname} {realname}".strip()
                        self.cache_usuarios[user_id] = nome_completo if nome_completo else f"Usuário {user_id}"
                    
                    if len(users) < range_limit:
                        break
                    
                    range_start += range_limit
                else:
                    break
            
            print(f"   [OK] {len(self.cache_usuarios)} usuários carregados")
        except Exception as e:
            print(f"   [AVISO] Erro ao carregar usuários: {e}")
    
    def carregar_cache_entidades(self):
        """Carrega todas as entidades em cache"""
        print("[EMOJI] Carregando cache de entidades...")
        try:
            url = f"{self.api_url}/Entity"
            params = {'range': '0-1000'}
            response = self.session.get(url, params=params)
            
            if response.status_code in [200, 206]:
                entities = response.json()
                for entity in entities:
                    entity_id = str(entity.get('id'))
                    self.cache_entidades[entity_id] = entity.get('name', 'Sem Entidade')
                
                print(f"   [OK] {len(self.cache_entidades)} entidades carregadas")
        except Exception as e:
            print(f"   [AVISO] Erro ao carregar entidades: {e}")
    
    def carregar_cache_categorias(self):
        """Carrega todas as categorias em cache"""
        print("[EMOJI] Carregando cache de categorias...")
        try:
            url = f"{self.api_url}/ITILCategory"
            params = {'range': '0-1000'}
            response = self.session.get(url, params=params)
            
            if response.status_code in [200, 206]:
                categories = response.json()
                for category in categories:
                    category_id = str(category.get('id'))
                    self.cache_categorias[category_id] = category.get('name', 'Sem Categoria')
                
                print(f"   [OK] {len(self.cache_categorias)} categorias carregadas")
        except Exception as e:
            print(f"   [AVISO] Erro ao carregar categorias: {e}")
    
    def carregar_cache_localizacoes(self):
        """Carrega todas as localizações em cache"""
        print("[EMOJI] Carregando cache de localizações...")
        try:
            url = f"{self.api_url}/Location"
            params = {'range': '0-1000'}
            response = self.session.get(url, params=params)
            
            if response.status_code in [200, 206]:
                locations = response.json()
                for location in locations:
                    location_id = str(location.get('id'))
                    self.cache_localizacoes[location_id] = location.get('name', 'Sem Localização')
                
                print(f"   [OK] {len(self.cache_localizacoes)} localizações carregadas")
        except Exception as e:
            print(f"   [AVISO] Erro ao carregar localizações: {e}")
    
    def carregar_cache_grupos(self):
        """Carrega todos os grupos em cache"""
        print("[EMOJI]‍[SISTEMA] Carregando cache de grupos...")
        try:
            url = f"{self.api_url}/Group"
            params = {'range': '0-1000'}
            response = self.session.get(url, params=params)
            
            if response.status_code in [200, 206]:
                groups = response.json()
                for group in groups:
                    group_id = str(group.get('id'))
                    self.cache_grupos[group_id] = group.get('name', 'Sem Grupo')
                
                print(f"   [OK] {len(self.cache_grupos)} grupos carregados")
        except Exception as e:
            print(f"   [AVISO] Erro ao carregar grupos: {e}")
    
    def carregar_todos_caches(self):
        """Carrega todos os caches necessários"""
        print("[PROCESSANDO] Carregando caches para otimização...")
        self.carregar_cache_usuarios()
        self.carregar_cache_entidades()
        self.carregar_cache_categorias()
        self.carregar_cache_localizacoes()
        self.carregar_cache_grupos()
        print("[OK] Todos os caches carregados!")
    
    def buscar_tickets_com_filtro_data(self, data_inicial, data_final):
        """Busca todos os tickets e filtra por data durante o processamento"""
        print(f"[EMOJI] Buscando todos os tickets para filtrar entre {data_inicial.strftime('%d/%m/%Y')} e {data_final.strftime('%d/%m/%Y')}...")
        
        todos_tickets = []
        range_start = 0
        range_limit = 1000
        
        while True:
            print(f"   Buscando tickets {range_start} a {range_start + range_limit - 1}...")
            
            url = f"{self.api_url}/Ticket"
            params = {
                'range': f'{range_start}-{range_start + range_limit - 1}',
                'expand_dropdowns': 'false',
                'get_hateoas': 'false'
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code in [200, 206]:
                tickets = response.json()
                if not tickets:
                    break
                
                # Filtrar tickets por data durante o processamento
                tickets_filtrados = []
                for ticket in tickets:
                    data_criacao_str = ticket.get('date')
                    if data_criacao_str:
                        try:
                            # Converter data de criação para datetime
                            data_criacao = datetime.strptime(data_criacao_str, '%Y-%m-%d %H:%M:%S')
                            
                            # Verificar se está no período
                            if data_inicial <= data_criacao <= data_final:
                                tickets_filtrados.append(ticket)
                        except ValueError:
                            # Se não conseguir converter a data, incluir o ticket
                            tickets_filtrados.append(ticket)
                
                todos_tickets.extend(tickets_filtrados)
                
                if len(tickets) < range_limit:
                    break
                
                range_start += range_limit
            else:
                print(f"[ERRO] Erro ao buscar tickets: {response.status_code}")
                print(f"Resposta: {response.text}")
                break
        
        return todos_tickets
    
    def buscar_relacionamentos_tickets(self, ticket_ids):
        """Busca relacionamentos de usuários e grupos para os tickets"""
        print("[EMOJI] Buscando relacionamentos de usuários e grupos...")
        
        relacionamentos = defaultdict(lambda: {
            'requerente': 'Sem Requerente',
            'tecnico': 'Não Atribuído',
            'grupo': 'Sem Grupo'
        })
        
        # Buscar relacionamentos de usuários
        try:
            url = f"{self.api_url}/Ticket_User"
            params = {'range': '0-50000'}
            response = self.session.get(url, params=params)
            
            if response.status_code in [200, 206]:
                user_relations = response.json()
                
                for relation in user_relations:
                    ticket_id = str(relation.get('tickets_id'))
                    user_id = str(relation.get('users_id'))
                    type_user = relation.get('type')
                    
                    if ticket_id in ticket_ids:
                        nome_usuario = self.cache_usuarios.get(user_id, f"Usuário {user_id}")
                        
                        if type_user == 1:  # Requerente
                            relacionamentos[ticket_id]['requerente'] = nome_usuario
                        elif type_user == 2:  # Técnico
                            relacionamentos[ticket_id]['tecnico'] = nome_usuario
        except Exception as e:
            print(f"   [AVISO] Erro ao buscar relacionamentos de usuários: {e}")
        
        # Buscar relacionamentos de grupos
        try:
            url = f"{self.api_url}/Group_Ticket"
            params = {'range': '0-50000'}
            response = self.session.get(url, params=params)
            
            if response.status_code in [200, 206]:
                group_relations = response.json()
                
                for relation in group_relations:
                    ticket_id = str(relation.get('tickets_id'))
                    group_id = str(relation.get('groups_id'))
                    type_group = relation.get('type')
                    
                    if ticket_id in ticket_ids and type_group == 2:  # Grupo técnico
                        nome_grupo = self.cache_grupos.get(group_id, f"Grupo {group_id}")
                        relacionamentos[ticket_id]['grupo'] = nome_grupo
        except Exception as e:
            print(f"   [AVISO] Erro ao buscar relacionamentos de grupos: {e}")
        
        return relacionamentos
    
    def extrair_tickets_por_periodo(self, data_inicial=None, data_final=None, periodo_predefinido=None):
        """Extrai tickets por período específico"""
        if not self.init_session():
            return False
        
        try:
            # Determinar período
            if periodo_predefinido:
                data_inicial, data_final, descricao_periodo = self.calcular_periodo_predefinido(periodo_predefinido)
                print(f"[DATA] Período selecionado: {descricao_periodo}")
            elif data_inicial and data_final:
                descricao_periodo = f"De {data_inicial.strftime('%d/%m/%Y')} até {data_final.strftime('%d/%m/%Y')}"
                print(f"[DATA] Período personalizado: {descricao_periodo}")
            else:
                # Padrão: últimos 6 meses
                data_inicial, data_final, descricao_periodo = self.calcular_periodo_predefinido("ultimos_6_meses")
                print(f"[DATA] Período padrão: {descricao_periodo}")
            
            print(f"[EMOJI] Data inicial: {data_inicial.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"[EMOJI] Data final: {data_final.strftime('%d/%m/%Y %H:%M:%S')}")
            print()
            
            # Carregar caches primeiro
            self.carregar_todos_caches()
            
            # Buscar tickets com filtro de data
            todos_tickets = self.buscar_tickets_com_filtro_data(data_inicial, data_final)
            print(f"[OK] Total de tickets encontrados no período: {len(todos_tickets):,}")
            
            if not todos_tickets:
                print("[ERRO] Nenhum ticket encontrado no período especificado!")
                return False
            
            # Buscar relacionamentos
            ticket_ids = {str(ticket['id']) for ticket in todos_tickets}
            relacionamentos = self.buscar_relacionamentos_tickets(ticket_ids)
            
            # Processar e formatar dados
            print("🧹 Processando e formatando dados...")
            dados_formatados = []
            
            for i, ticket in enumerate(todos_tickets):
                if (i + 1) % 500 == 0:
                    print(f"   Processados {i + 1:,} de {len(todos_tickets):,} tickets...")
                
                try:
                    ticket_id = str(ticket.get('id'))
                    
                    # Buscar dados dos caches
                    entidade = self.cache_entidades.get(str(ticket.get('entities_id', '0')), 'Sem Entidade')
                    categoria = self.cache_categorias.get(str(ticket.get('itilcategories_id', '0')), 'Sem Categoria')
                    localizacao = self.cache_localizacoes.get(str(ticket.get('locations_id', '0')), 'Sem Localização')
                    
                    # Buscar relacionamentos
                    rel = relacionamentos[ticket_id]
                    
                    # Formatar linha de dados
                    linha = [
                        ticket_id,
                        self.limpar_campo_texto(ticket.get('name', '')),
                        self.limpar_campo_texto(entidade),
                        self.traduzir_status(ticket.get('status', 1)),
                        self.formatar_data(ticket.get('date_mod')),
                        self.formatar_data(ticket.get('date')),
                        self.limpar_campo_texto(rel['requerente']),
                        self.limpar_campo_texto(rel['tecnico']),
                        self.limpar_campo_texto(rel['grupo']),
                        self.limpar_campo_texto(categoria),
                        self.limpar_campo_texto(localizacao),
                        self.limpar_descricao(ticket.get('content', ''))
                    ]
                    
                    dados_formatados.append(linha)
                    
                except Exception as e:
                    print(f"   [AVISO] Erro ao processar ticket {ticket.get('id', 'N/A')}: {e}")
                    continue
            
            # Gerar arquivo CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            periodo_nome = periodo_predefinido if periodo_predefinido else "personalizado"
            nome_arquivo = f"tickets_api_glpi_{periodo_nome}_{timestamp}.csv"
            
            # Determinar pasta de destino baseada no tipo de execução
            if periodo_predefinido == "ultimos_6_meses":
                pasta_destino = "../dados/tickets_6_meses"
            elif periodo_predefinido == "ultimo_mes":
                pasta_destino = "../dados/tickets_ultimo_mes"
            elif periodo_nome == "personalizado":
                pasta_destino = "../dados/tickets_data_personalizada"
            else:
                # Para outros períodos (3 meses, ano, etc.), usar pasta padrão
                pasta_destino = "../dados/tickets_mensais"
            
            # Criar pasta se não existir
            import os
            os.makedirs(pasta_destino, exist_ok=True)
            
            caminho_arquivo = f"{pasta_destino}/{nome_arquivo}"
            
            print(f"[EMOJI] Gerando arquivo: {nome_arquivo}")
            
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
                escritor = csv.writer(arquivo_csv, quoting=csv.QUOTE_ALL)
                
                # Cabeçalho
                cabecalho = [
                    'ID', 'Titulo', 'Entidade', 'Status', 'Ultima_atualizacao', 
                    'Data_abertura', 'Requerente', 'Tecnico_atribuido', 
                    'Grupo_tecnico', 'Categoria', 'Localizacao', 'Descricao'
                ]
                escritor.writerow(cabecalho)
                
                # Dados
                escritor.writerows(dados_formatados)
            
            print(f"\n[OK] Extração concluída com sucesso!")
            print(f"[ARQUIVO] Arquivo: {caminho_arquivo}")
            print(f"[GRAFICO] Total de registros: {len(dados_formatados):,}")
            print(f"[DATA] Período: {descricao_periodo}")
            print(f"[EMOJI] Timestamp: {timestamp}")
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro durante extração: {e}")
            return False
        
        finally:
            self.kill_session()

def main():
    """Função principal com opções de linha de comando"""
    parser = argparse.ArgumentParser(description='Extrator de dados da API GLPI com filtro de data')
    
    # Opções de período pré-definido
    parser.add_argument('--periodo', choices=[
        'ultimo_mes', 'ultimos_3_meses', 'ultimos_6_meses', 
        'ultimo_ano', 'ano_atual', 'ano_passado'
    ], help='Período pré-definido para extração')
    
    # Opções de data personalizada
    parser.add_argument('--data-inicial', type=str, help='Data inicial (formato: DD/MM/YYYY)')
    parser.add_argument('--data-final', type=str, help='Data final (formato: DD/MM/YYYY)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("[INICIO] EXTRATOR DE DADOS DA API GLPI COM FILTRO DE DATA")
    print("=" * 70)
    
    # Importar configurações
    try:
        from config import API_URL, APP_TOKEN, USER_TOKEN
        print("[OK] Configurações carregadas de config.py")
    except ImportError:
        print("[ERRO] ERRO: Arquivo config.py não encontrado!")
        print("[LISTA] INSTRUÇÕES:")
        print("   1. Copie config_exemplo.py para config.py")
        print("   2. Edite config.py com seus tokens reais")
        print("   3. Execute o script novamente")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] ERRO ao carregar configurações: {e}")
        sys.exit(1)
    
    print(f"[EMOJI] API URL: {API_URL}")
    print(f"[EMOJI] App Token: {APP_TOKEN[:10]}...")
    print(f"[EMOJI] User Token: {USER_TOKEN[:10]}...")
    print()
    
    # Processar argumentos
    data_inicial = None
    data_final = None
    periodo_predefinido = args.periodo
    
    if args.data_inicial and args.data_final:
        try:
            data_inicial = datetime.strptime(args.data_inicial, '%d/%m/%Y')
            data_final = datetime.strptime(args.data_final, '%d/%m/%Y')
            data_final = data_final.replace(hour=23, minute=59, second=59)  # Fim do dia
            periodo_predefinido = None
        except ValueError:
            print("[ERRO] Formato de data inválido! Use DD/MM/YYYY")
            return
    
    # Se não especificou nada, usar modo interativo
    if not periodo_predefinido and not (data_inicial and data_final):
        print("[LISTA] OPÇÕES DE PERÍODO:")
        print("1. Último mês")
        print("2. Últimos 3 meses")
        print("3. Últimos 6 meses (padrão)")
        print("4. Último ano")
        print("5. Ano atual")
        print("6. Ano passado")
        print("7. Período personalizado")
        print()
        
        try:
            opcao = input("Escolha uma opção (1-7) [3]: ").strip()
            if not opcao:
                opcao = "3"
            
            if opcao == "1":
                periodo_predefinido = "ultimo_mes"
            elif opcao == "2":
                periodo_predefinido = "ultimos_3_meses"
            elif opcao == "3":
                periodo_predefinido = "ultimos_6_meses"
            elif opcao == "4":
                periodo_predefinido = "ultimo_ano"
            elif opcao == "5":
                periodo_predefinido = "ano_atual"
            elif opcao == "6":
                periodo_predefinido = "ano_passado"
            elif opcao == "7":
                data_inicial_str = input("Data inicial (DD/MM/YYYY): ").strip()
                data_final_str = input("Data final (DD/MM/YYYY): ").strip()
                
                data_inicial = datetime.strptime(data_inicial_str, '%d/%m/%Y')
                data_final = datetime.strptime(data_final_str, '%d/%m/%Y')
                data_final = data_final.replace(hour=23, minute=59, second=59)
                periodo_predefinido = None
            else:
                print("Opção inválida! Usando padrão (últimos 6 meses)")
                periodo_predefinido = "ultimos_6_meses"
                
        except (ValueError, KeyboardInterrupt):
            print("\nUsando padrão: últimos 6 meses")
            periodo_predefinido = "ultimos_6_meses"
    
    print()
    inicio = datetime.now()
    
    # Criar extrator e executar
    extrator = GLPIAPIExtractorComFiltroData(API_URL, APP_TOKEN, USER_TOKEN)
    sucesso = extrator.extrair_tickets_por_periodo(
        data_inicial=data_inicial,
        data_final=data_final,
        periodo_predefinido=periodo_predefinido
    )
    
    fim = datetime.now()
    duracao = fim - inicio
    
    print("\n" + "=" * 70)
    if sucesso:
        print("[SUCESSO] EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("[ERRO] EXTRAÇÃO FALHOU!")
    
    print(f"[TEMPO]  Tempo de execução: {duracao}")
    print("=" * 70)

if __name__ == "__main__":
    main()