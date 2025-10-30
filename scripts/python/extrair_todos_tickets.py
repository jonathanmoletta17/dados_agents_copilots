#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para extrair TODOS os tickets da API do GLPI (sem filtro de data)
Baseado na funcionalidade da opção 8 do script original
"""

import requests
import csv
import html
import re
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Configurar encoding para Windows
if os.name == 'nt':  # Windows
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except locale.Error:
            pass
    
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

class GLPITodosTicketsExtractor:
    def __init__(self, api_url, app_token, user_token):
        """Inicializa o extrator para buscar TODOS os tickets do GLPI"""
        self.api_url = api_url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        self.session_token = None
        self.session = requests.Session()
        
        # Cache para otimização
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
            print("[EMOJI] Iniciando sessão na API do GLPI...")
            
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
                print("[OK] Sessão iniciada com sucesso!")
                return True
            else:
                print(f"[ERRO] Erro ao iniciar sessão: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERRO] Erro na conexão: {e}")
            return False
    
    def processar_dados_tickets(self, tickets, relacionamentos, descricao="tickets"):
        """Processa e formata dados dos tickets"""
        print(f"🧹 Processando e formatando {descricao}...")
        dados_formatados = []
        
        for i, ticket in enumerate(tickets):
            if (i + 1) % 500 == 0:
                print(f"   [DADOS] Processados {i + 1:,} de {len(tickets):,} {descricao}...")
            
            try:
                ticket_id = str(ticket.get('id'))
                
                # Buscar dados dos caches
                entidade = self.cache_entidades.get(str(ticket.get('entities_id', '')), 'Sem Entidade')
                categoria = self.cache_categorias.get(str(ticket.get('itilcategories_id', '')), 'Sem Categoria')
                
                # Buscar relacionamentos
                rel = relacionamentos[ticket_id]
                
                # Montar linha de dados
                linha = {
                    'ID': ticket_id,
                    'Título': self.limpar_campo_texto(ticket.get('name', '')),
                    'Descrição': self.limpar_descricao(ticket.get('content', '')),
                    'Status': self.traduzir_status(ticket.get('status', 1)),
                    'Prioridade': ticket.get('priority', ''),
                    'Urgência': ticket.get('urgency', ''),
                    'Impacto': ticket.get('impact', ''),
                    'Categoria': categoria,
                    'Entidade': entidade,
                    'Requerente': rel['requerente'],
                    'Técnico': rel['tecnico'],
                    'Grupo': rel['grupo'],
                    'Data Criação': self.formatar_data(ticket.get('date')),
                    'Data Modificação': self.formatar_data(ticket.get('date_mod')),
                    'Data Solução': self.formatar_data(ticket.get('solvedate')),
                    'Data Fechamento': self.formatar_data(ticket.get('closedate')),
                    'Tempo Solução (min)': ticket.get('solve_delay_stat', ''),
                    'Tempo Fechamento (min)': ticket.get('close_delay_stat', ''),
                    'Satisfação': ticket.get('satisfaction', ''),
                    'Tipo': ticket.get('type', ''),
                    'Localização': ticket.get('locations_id', ''),
                    'Validação': ticket.get('global_validation', '')
                }
                
                dados_formatados.append(linha)
                
            except Exception as e:
                print(f"   [AVISO] Erro ao processar ticket {ticket.get('id', 'N/A')}: {e}")
                continue
        
        return dados_formatados
    
    def kill_session(self):
        """Encerra sessão na API do GLPI"""
        if self.session_token:
            try:
                url = f"{self.api_url}/killSession"
                response = self.session.get(url)
                print("[EMOJI] Sessão encerrada")
            except:
                pass
    
    def limpar_campo_texto(self, texto):
        """Limpa campos de texto para CSV"""
        if not texto:
            return ""
        
        try:
            texto = str(texto)
            texto = texto.replace('\r', '').replace('\n', ' ').replace('\t', ' ')
            texto = texto.replace('"', '""')
            texto = re.sub(r'\s+', ' ', texto)
            texto = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f]', '', texto)
            return texto.strip()
        except Exception as e:
            print(f"[AVISO] Erro ao limpar campo de texto: {e}")
            return ""
    
    def limpar_descricao(self, descricao_raw):
        """Limpa e otimiza a descrição do ticket"""
        if not descricao_raw:
            return ""
        
        try:
            descricao = html.unescape(str(descricao_raw))
            descricao = re.sub(r'<[^>]+>', '', descricao)
            descricao = re.sub(r'\s+', ' ', descricao)
            descricao = descricao.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            descricao = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f]', '', descricao)
            
            if len(descricao) > 500:
                descricao = descricao[:497] + "..."
            
            return descricao.strip()
        except Exception as e:
            print(f"[AVISO] Erro ao limpar descrição: {e}")
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
        print("[GRUPO] Carregando cache de usuários...")
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
        print("[EMPRESA] Carregando cache de entidades...")
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
    
    def carregar_cache_grupos(self):
        """Carrega todos os grupos em cache"""
        print("[EMOJI]‍[EMOJI]‍[EMOJI]‍[EMOJI] Carregando cache de grupos...")
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
        print("[EMOJI] Carregando caches para otimização...")
        self.carregar_cache_usuarios()
        self.carregar_cache_entidades()
        self.carregar_cache_categorias()
        self.carregar_cache_grupos()
        print("[OK] Todos os caches carregados!")
    
    def buscar_todos_tickets(self):
        """Busca TODOS os tickets sem filtro de data"""
        print("[TICKET] Buscando TODOS os tickets (sem filtro de data)...")
        
        todos_tickets = []
        range_start = 0
        range_limit = 1000
        
        while True:
            print(f"   [EMOJI] Buscando tickets {range_start} a {range_start + range_limit - 1}...")
            
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
                
                # Adicionar TODOS os tickets sem filtro
                todos_tickets.extend(tickets)
                
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
    
    def extrair_todos_tickets(self):
        """Extrai TODOS os tickets do GLPI e gera dois arquivos: completo e últimos 6 meses"""
        if not self.init_session():
            return False
        
        try:
            print("[EMOJI] Iniciando extração de TODOS os tickets...")
            print("[LISTA] Este script irá gerar 2 arquivos:")
            print("   1️⃣ Arquivo completo com todos os tickets")
            print("   2️⃣ Arquivo filtrado com apenas os últimos 6 meses")
            print()
            
            # Carregar caches primeiro
            self.carregar_todos_caches()
            
            # Buscar todos os tickets
            todos_tickets = self.buscar_todos_tickets()
            print(f"[OK] Total de tickets encontrados: {len(todos_tickets):,}")
            
            if not todos_tickets:
                print("[ERRO] Nenhum ticket encontrado!")
                return False
            
            # Buscar relacionamentos
            ticket_ids = {str(ticket['id']) for ticket in todos_tickets}
            relacionamentos = self.buscar_relacionamentos_tickets(ticket_ids)
            
            # Calcular período dos últimos 6 meses
            data_inicial_6m, data_final_6m = self.calcular_periodo_6_meses()
            print(f"[MES] Período dos últimos 6 meses: {data_inicial_6m.strftime('%d/%m/%Y')} até {data_final_6m.strftime('%d/%m/%Y')}")
            
            # Filtrar tickets dos últimos 6 meses
            tickets_6_meses = self.filtrar_tickets_por_data(todos_tickets, data_inicial_6m, data_final_6m)
            print(f"[OK] Tickets dos últimos 6 meses: {len(tickets_6_meses):,}")
            print()
            
            # Processar dados completos
            dados_completos = self.processar_dados_tickets(todos_tickets, relacionamentos, "todos os tickets")
            
            # Processar dados dos últimos 6 meses
            dados_6_meses = self.processar_dados_tickets(tickets_6_meses, relacionamentos, "tickets dos últimos 6 meses")
            
            # Gerar timestamp para os arquivos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Salvar arquivo completo
            print()
            print("=" * 60)
            print("[EMOJI] SALVANDO ARQUIVO COMPLETO")
            print("=" * 60)
            nome_arquivo_completo = f'../dados/tickets_completos/todos_tickets_{timestamp}.csv'
            sucesso_completo = self.salvar_dados_csv(dados_completos, nome_arquivo_completo, "arquivo completo")
            
            # Salvar arquivo dos últimos 6 meses
            print()
            print("=" * 60)
            print("[EMOJI] SALVANDO ARQUIVO DOS ÚLTIMOS 6 MESES")
            print("=" * 60)
            nome_arquivo_6m = f'../dados/tickets_6_meses/tickets_api_glpi_ultimos_6_meses_{timestamp}.csv'
            sucesso_6m = self.salvar_dados_csv(dados_6_meses, nome_arquivo_6m, "arquivo dos últimos 6 meses")
            
            # Resumo final
            print()
            print("=" * 60)
            print("[DADOS] RESUMO DA EXTRAÇÃO")
            print("=" * 60)
            print(f"[OK] Total de tickets processados: {len(todos_tickets):,}")
            print(f"[EMOJI] Arquivo completo: {'[OK] Salvo' if sucesso_completo else '[ERRO] Erro'}")
            print(f"[EMOJI] Arquivo 6 meses: {'[OK] Salvo' if sucesso_6m else '[ERRO] Erro'}")
            print()
            
            if sucesso_completo:
                print(f"[EMOJI] Arquivo completo salvo em: {nome_arquivo_completo}")
            if sucesso_6m:
                print(f"[EMOJI] Arquivo 6 meses salvo em: {nome_arquivo_6m}")
            
            return sucesso_completo and sucesso_6m
            
        except Exception as e:
            print(f"[ERRO] Erro durante extração: {e}")
            return False
        
        finally:
            self.kill_session()

    def calcular_periodo_6_meses(self):
        """Calcula as datas para os últimos 6 meses"""
        hoje = datetime.now()
        data_inicial = hoje - timedelta(days=180)
        data_final = hoje
        return data_inicial, data_final

    def filtrar_tickets_por_data(self, tickets, data_inicial, data_final):
        """Filtra tickets por período de data"""
        tickets_filtrados = []
        
        for ticket in tickets:
            try:
                data_criacao_str = ticket.get('date', '')
                if not data_criacao_str:
                    continue
                
                # Converter string para datetime
                data_criacao = datetime.strptime(data_criacao_str, '%Y-%m-%d %H:%M:%S')
                
                # Verificar se está no período
                if data_inicial <= data_criacao <= data_final:
                    tickets_filtrados.append(ticket)
                    
            except (ValueError, TypeError):
                # Se não conseguir converter a data, pula o ticket
                continue
        
        return tickets_filtrados

    def salvar_dados_csv(self, dados_formatados, nome_arquivo, descricao="dados"):
        """Salva dados formatados em arquivo CSV"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
            
            print(f"[SALVAR] Salvando {descricao} em: {nome_arquivo}")
            
            with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                if dados_formatados:
                    fieldnames = dados_formatados[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(dados_formatados)
            
            print(f"[OK] Arquivo {descricao} salvo com sucesso!")
            print(f"[DADOS] Total de tickets exportados: {len(dados_formatados):,}")
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao salvar {descricao}: {e}")
            return False

def main():
    """Função principal"""
    print("=" * 70)
    print("[TICKET] EXTRATOR DE TODOS OS TICKETS DA API GLPI")
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
    
    inicio = datetime.now()
    
    # Criar extrator e executar
    extrator = GLPITodosTicketsExtractor(API_URL, APP_TOKEN, USER_TOKEN)
    sucesso = extrator.extrair_todos_tickets()
    
    fim = datetime.now()
    duracao = fim - inicio
    
    print("\n" + "=" * 70)
    if sucesso:
        print("[FIM] EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("[ERRO] EXTRAÇÃO FALHOU!")
    
    print(f"⏱️ Tempo de execução: {duracao}")
    print("=" * 70)

if __name__ == "__main__":
    main()