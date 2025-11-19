"""
ENDPOINT DE HISTÓRICO DE ALTERAÇÕES DE TICKETS GLPI
==================================================

Este módulo fornece endpoints para acessar o histórico completo de alterações
de tickets do GLPI via API REST.

Dados retornados para cada alteração:
- ID da alteração
- Data/hora da modificação
- Usuário que realizou a alteração
- Campo que foi modificado
- Valor antigo
- Valor novo
- Tipo de ação realizada
- Item relacionado

Autor: Analista de Dados - Casa Civil
Data: 2025-11-16
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Adicionar o diretório pai ao path para importar o cliente GLPI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sdk.python.glpi_client import GLPIClient

def ler_configuracao():
    """Lê as configurações do arquivo .env"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    config[k.strip()] = v.strip()
    return config

def inicializar_cliente_glpi():
    """Inicializa o cliente GLPI com as configurações"""
    config = ler_configuracao()
    
    GLPI_API_URL = config.get("GLPI_URL", "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php")
    APP_TOKEN = config.get("GLPI_APP_TOKEN", "")
    USER_TOKEN = config.get("GLPI_USER_TOKEN", "")
    
    if not APP_TOKEN or not USER_TOKEN:
        raise ValueError("APP_TOKEN e USER_TOKEN devem estar configurados no arquivo .env")
    
    client = GLPIClient(base_url=GLPI_API_URL, app_token=APP_TOKEN, session_token="")
    
    # Autenticar
    r = client.get("/initSession", params={"user_token": USER_TOKEN})
    if r.status_code != 200:
        raise RuntimeError(f"Falha na autenticação: {r.status_code} - {r.text}")
    
    session_token = r.json()["session_token"]
    client.session.headers.update({"Session-Token": session_token})
    
    return client, session_token

def obter_historico_ticket(client: GLPIClient, ticket_id: int) -> List[Dict]:
    """
    Obtém o histórico completo de alterações de um ticket específico.
    
    Args:
        client: Cliente GLPI autenticado
        ticket_id: ID do ticket
    
    Returns:
        Lista de dicionários com os dados de histórico
    """
    # Endpoint principal que funciona: /Ticket/{id}/Log
    response = client.get(f"/Ticket/{ticket_id}/Log")
    
    if response.status_code != 200:
        print(f"[ERRO] Falha ao obter histórico do ticket {ticket_id}: {response.status_code}")
        return []
    
    try:
        historico = response.json()
        
        # Processar e enriquecer os dados
        for item in historico:
            # Adicionar informações do ticket ID para referência
            item['ticket_id'] = ticket_id
            
            # Converter data para formato legível se necessário
            if 'date_mod' in item:
                item['data_formatada'] = item['date_mod']
            
            # Identificar tipo de alteração de forma legível
            item['tipo_alteracao'] = interpretar_tipo_alteracao(item)
            
            # Mapear campo modificado
            item['campo_modificado'] = mapear_campo_modificado(item.get('id_search_option', 0))
        
        return historico
    
    except Exception as e:
        print(f"[ERRO] Falha ao processar histórico do ticket {ticket_id}: {e}")
        return []

def interpretar_tipo_alteracao(item: Dict) -> str:
    """Interpreta o tipo de alteração baseado nos campos do log"""
    itemtype_link = item.get('itemtype_link', '')
    linked_action = item.get('linked_action', 0)
    
    # Mapeamento de tipos de alteração com base nos dados observados
    mapeamento = {
        ('Document', 15): 'Adicionado documento/anexo',
        ('User', 15): 'Alteração de usuário atribuído',
        ('ITILFollowup', 12): 'Adicionado acompanhamento',
        ('ITILFollowup', 17): 'Atualizado acompanhamento',
        ('ITILFollowup', 19): 'Deletado acompanhamento',
        ('Group', 15): 'Alteração de grupo atribuído',
        ('TicketTask', 17): 'Tarefa criada/modificada',
        ('TicketValidation', 12): 'Validação de ticket',
        ('PendingReason', 15): 'Motivo de pendência adicionado',
        ('PendingReason', 16): 'Motivo de pendência removido',
        ('ITILSolution', 17): 'Solução aplicada',
        ('PluginFormcreatorFormAnswer', 15): 'Formulário respondido',
        ('', 0): 'Alteração de campo',
        ('', 20): 'Status alterado'
    }
    
    # Procurar mapeamento exato
    chave = (itemtype_link, linked_action)
    if chave in mapeamento:
        return mapeamento[chave]
    
    # Tentar mapeamento parcial
    for (link, action), descricao in mapeamento.items():
        if link == itemtype_link and action == linked_action:
            return descricao
    
    # Descrição padrão
    if itemtype_link:
        return f"Alteração em {itemtype_link}"
    else:
        return f"Alteração de campo (ação {linked_action})"

def mapear_campo_modificado(search_option: int) -> str:
    """Mapeia o id_search_option para o nome do campo real"""
    # Mapeamento baseado nos dados observados e padrões GLPI
    campos = {
        0: 'Campo geral',
        1: 'Nome/Título',
        2: 'Descrição',
        3: 'Status',
        4: 'Usuário atribuído',
        5: 'Grupo atribuído',
        6: 'Categoria',
        7: 'Prioridade',
        8: 'Urgência',
        9: 'Impacto',
        10: 'Data de vencimento',
        11: 'Entidade',
        12: 'Localização',
        13: 'Tipo',
        14: 'Requerente',
        15: 'Técnico',
        16: 'Data de modificação',
        17: 'Data de criação',
        18: 'Solução',
        19: 'Acompanhamento',
        20: 'Validação'
    }
    
    return campos.get(search_option, f'Campo {search_option}')

def formatar_historico_json(historico: List[Dict]) -> str:
    """Formata o histórico em JSON legível"""
    return json.dumps(historico, ensure_ascii=False, indent=2)

def exportar_historico_csv(historico: List[Dict], ticket_id: int, output_dir: str = None):
    """Exporta o histórico para CSV"""
    if not historico:
        print(f"[AVISO] Nenhum histórico para exportar do ticket {ticket_id}")
        return None
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'dados', 'historicos')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Criar DataFrame
    df = pd.DataFrame(historico)
    
    # Selecionar e renomear colunas principais
    colunas_exportar = [
        'id', 'ticket_id', 'data_formatada', 'user_name', 'campo_modificado',
        'old_value', 'new_value', 'tipo_alteracao', 'itemtype_link', 'linked_action'
    ]
    
    # Filtrar colunas que existem no DataFrame
    colunas_disponiveis = [col for col in colunas_exportar if col in df.columns]
    df_export = df[colunas_disponiveis]
    
    # Nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_saida = os.path.join(output_dir, f"historico_ticket_{ticket_id}_{timestamp}.xlsx")
    
    # Exportar
    df_export.to_excel(arquivo_saida, index=False)
    
    print(f"[INFO] Histórico exportado: {arquivo_saida}")
    print(f"[INFO] Total de registros: {len(df_export)}")
    
    return arquivo_saida

def endpoint_historico_ticket(ticket_id: int, formato: str = 'json', exportar_csv: bool = False):
    """
    Endpoint principal para obter histórico de um ticket.
    
    Args:
        ticket_id: ID do ticket
        formato: 'json' ou 'csv'
        exportar_csv: Se True, também exporta para CSV
    
    Returns:
        Dados do histórico no formato solicitado
    """
    print(f"[INFO] Buscando histórico do ticket {ticket_id}")
    
    try:
        # Inicializar cliente GLPI
        client, session_token = inicializar_cliente_glpi()
        
        # Obter histórico
        historico = obter_historico_ticket(client, ticket_id)
        
        if not historico:
            return {"erro": f"Nenhum histórico encontrado para o ticket {ticket_id}"}
        
        # Processar resultados
        resultado = {
            "ticket_id": ticket_id,
            "total_alteracoes": len(historico),
            "periodo": {
                "primeira_alteracao": historico[-1].get('date_mod') if historico else None,
                "ultima_alteracao": historico[0].get('date_mod') if historico else None
            },
            "usuarios_envolvidos": list(set(item.get('user_name', 'Sistema') for item in historico)),
            "tipos_alteracoes": list(set(item.get('tipo_alteracao', '') for item in historico)),
            "historico_detalhado": historico
        }
        
        # Exportar CSV se solicitado
        if exportar_csv:
            arquivo_csv = exportar_historico_csv(historico, ticket_id)
            resultado["arquivo_csv"] = arquivo_csv
        
        # Formatar resultado final
        if formato.lower() == 'csv':
            # Converter para CSV string
            df = pd.DataFrame(historico)
            colunas_principais = ['id', 'ticket_id', 'date_mod', 'user_name', 'campo_modificado', 'old_value', 'new_value', 'tipo_alteracao']
            colunas_disponiveis = [col for col in colunas_principais if col in df.columns]
            return df[colunas_disponiveis].to_csv(index=False, encoding='utf-8', sep=';')
        else:
            # Retornar JSON
            return resultado
    
    except Exception as e:
        erro_msg = f"[ERRO] Falha ao obter histórico: {str(e)}"
        print(erro_msg)
        return {"erro": erro_msg}
    
    finally:
        # Sempre encerrar sessão
        try:
            client.get("/killSession")
            print("[INFO] Sessão GLPI encerrada")
        except:
            pass

def endpoint_historico_multiplos_tickets(ticket_ids: List[int], exportar_csv: bool = False):
    """
    Endpoint para obter histórico de múltiplos tickets.
    
    Args:
        ticket_ids: Lista de IDs de tickets
        exportar_csv: Se True, exporta todos os históricos para CSV
    
    Returns:
        Dicionário com históricos de todos os tickets
    """
    print(f"[INFO] Buscando histórico de {len(ticket_ids)} tickets")
    
    todos_historicos = {}
    arquivos_csv = []
    
    try:
        client, session_token = inicializar_cliente_glpi()
        
        for ticket_id in ticket_ids:
            print(f"[INFO] Processando ticket {ticket_id}")
            historico = obter_historico_ticket(client, ticket_id)
            
            if historico:
                todos_historicos[ticket_id] = {
                    "total_alteracoes": len(historico),
                    "historico": historico
                }
                
                if exportar_csv:
                    arquivo = exportar_historico_csv(historico, ticket_id)
                    if arquivo:
                        arquivos_csv.append(arquivo)
            else:
                todos_historicos[ticket_id] = {
                    "total_alteracoes": 0,
                    "historico": [],
                    "aviso": "Nenhum histórico encontrado"
                }
        
        # Resumo geral
        resumo = {
            "total_tickets_processados": len(ticket_ids),
            "tickets_com_historico": len([t for t, h in todos_historicos.items() if h['total_alteracoes'] > 0]),
            "total_alteracoes_geral": sum(h['total_alteracoes'] for h in todos_historicos.values()),
            "historicos_por_ticket": todos_historicos
        }
        
        if exportar_csv and arquivos_csv:
            resumo["arquivos_csv_gerados"] = arquivos_csv
        
        return resumo
    
    except Exception as e:
        erro_msg = f"[ERRO] Falha ao processar múltiplos tickets: {str(e)}"
        print(erro_msg)
        return {"erro": erro_msg}
    
    finally:
        try:
            client.get("/killSession")
            print("[INFO] Sessão GLPI encerrada")
        except:
            pass

# Funções de exemplo e teste
def exemplo_basico():
    """Exemplo básico de uso do endpoint"""
    print("=" * 60)
    print("EXEMPLO BÁSICO - HISTÓRICO DE TICKET")
    print("=" * 60)
    
    # Testar com ticket ID 10798 (do nosso teste anterior)
    ticket_id = 10798
    resultado = endpoint_historico_ticket(ticket_id, formato='json', exportar_csv=True)
    
    if "erro" not in resultado:
        print(f"✅ Ticket {ticket_id} processado com sucesso!")
        print(f"📊 Total de alterações: {resultado['total_alteracoes']}")
        print(f"👥 Usuários envolvidos: {len(resultado['usuarios_envolvidos'])}")
        print(f"📝 Tipos de alterações: {len(resultado['tipos_alteracoes'])}")
        print(f"📅 Período: {resultado['periodo']['primeira_alteracao']} até {resultado['periodo']['ultima_alteracao']}")
        
        if 'arquivo_csv' in resultado:
            print(f"💾 CSV exportado: {resultado['arquivo_csv']}")
        
        # Mostrar amostra do histórico
        print("\n🔍 AMOSTRA DAS ALTERAÇÕES:")
        for i, alteracao in enumerate(resultado['historico_detalhado'][:3]):
            print(f"\n{i+1}. {alteracao.get('tipo_alteracao', 'Alteração')}")
            print(f"   📅 Data: {alteracao.get('date_mod', 'N/A')}")
            print(f"   👤 Usuário: {alteracao.get('user_name', 'Sistema')}")
            print(f"   📝 Campo: {alteracao.get('campo_modificado', 'N/A')}")
            if alteracao.get('old_value') or alteracao.get('new_value'):
                print(f"   🔄 De: '{alteracao.get('old_value', '')}' Para: '{alteracao.get('new_value', '')}'")
    
    else:
        print(f"❌ Erro: {resultado['erro']}")

def exemplo_multiplos_tickets():
    """Exemplo com múltiplos tickets"""
    print("\n" + "=" * 60)
    print("EXEMPLO MÚLTIPLOS TICKETS")
    print("=" * 60)
    
    ticket_ids = [10798, 10799, 10800]  # IDs dos nossos testes
    resultado = endpoint_historico_multiplos_tickets(ticket_ids, exportar_csv=True)
    
    if "erro" not in resultado:
        print(f"✅ Processados {resultado['total_tickets_processados']} tickets")
        print(f"📊 Tickets com histórico: {resultado['tickets_com_historico']}")
        print(f"🔄 Total de alterações: {resultado['total_alteracoes_geral']}")
        
        print("\n📋 DETALHES POR TICKET:")
        for ticket_id, dados in resultado['historicos_por_ticket'].items():
            print(f"\n🎫 Ticket {ticket_id}: {dados['total_alteracoes']} alterações")
            if dados['total_alteracoes'] > 0:
                # Mostrar última alteração
                ultima = dados['historico'][0]
                print(f"   📅 Última: {ultima.get('date_mod', 'N/A')}")
                print(f"   👤 Usuário: {ultima.get('user_name', 'Sistema')}")
                print(f"   📝 Tipo: {ultima.get('tipo_alteracao', 'Alteração')}")
    
    else:
        print(f"❌ Erro: {resultado['erro']}")

if __name__ == "__main__":
    print("🚀 ENDPOINT DE HISTÓRICO DE TICKETS GLPI")
    print("Este módulo fornece acesso completo ao histórico de alterações dos tickets")
    print("\n📋 FUNÇÕES DISPONÍVEIS:")
    print("- endpoint_historico_ticket(ticket_id, formato, exportar_csv)")
    print("- endpoint_historico_multiplos_tickets(ticket_ids, exportar_csv)")
    
    # Executar exemplos
    try:
        exemplo_basico()
        exemplo_multiplos_tickets()
    except Exception as e:
        print(f"\n❌ Erro nos exemplos: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ENDPOINT PRONTO PARA USO!")
    print("Use as funções para acessar históricos de qualquer ticket GLPI")
    print("=" * 60)