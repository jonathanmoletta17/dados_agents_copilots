import os
import requests
import pandas as pd
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

API_URL = os.getenv("GLPI_DTIC_URL")
APP_TOKEN = os.getenv("GLPI_DTIC_APP_TOKEN")
USER_TOKEN = os.getenv("GLPI_DTIC_USER_TOKEN")

if not all([API_URL, APP_TOKEN, USER_TOKEN]):
    print("❌ Erro: Credenciais da API (URL, APP_TOKEN, USER_TOKEN) não encontradas no .env")
    print("Por favor, copie-as do arquivo glpi-data-service/.env")
    exit(1)

def get_session_token():
    """Inicializa sessão e retorna session_token"""
    url = f"{API_URL}/initSession"
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['session_token']
    else:
        raise Exception(f"Falha ao iniciar sessão: {response.text}")

def kill_session(session_token):
    """Fecha a sessão"""
    url = f"{API_URL}/killSession"
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token
    }
    requests.get(url, headers=headers)

def analyze_endpoint(session_token, endpoint, limit=50):
    """Busca itens do endpoint e analisa preenchimento de campos"""
    url = f"{API_URL}/{endpoint}"
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token
    }
    params = {
        "range": f"0-{limit}",
        "expand_dropdowns": "true" 
    }
    
    print(f"\n🔍 Analisando endpoint: {endpoint}...")
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code not in (200, 206):
            print(f"   ⚠️ Erro {response.status_code}: {response.text}")
            return

        data = response.json()
        if not data:
            print("   ⚠️ Nenhum dado retornado.")
            return

        df = pd.DataFrame(data)
        print(f"   ✅ {len(df)} itens recuperados.")
        
        # Análise de Colunas Interessantes (não vazias)
        print("   📊 Campos com dados relevantes (>10% preenchidos):")
        filled_cols = []
        for col in df.columns:
            non_null = df[col].count()
            # Tenta converter para numérico para ver se tem zeros que contam como dados
            try:
                numeric_vals = pd.to_numeric(df[col], errors='coerce')
                non_zeros = numeric_vals[numeric_vals != 0].count()
            except:
                non_zeros = non_null
            
            fill_rate = non_null / len(df)
            if fill_rate > 0.1:
                filled_cols.append(col)
                # print(f"      - {col}: {fill_rate*100:.0f}%")
        
        # Exibir amostra de colunas chave
        print(f"      Total colunas úteis: {len(filled_cols)}")
        
        # Checagens específicas
        if endpoint == "Ticket":
            check_ticket_specifics(df)
        elif endpoint == "TicketTask":
            print(f"      Tempo total tarefas (amostra): {df['actiontime'].sum() if 'actiontime' in df else 'N/A'}")
        
        return df
    except Exception as e:
        print(f"   ❌ Erro ao analisar {endpoint}: {e}")

def check_ticket_specifics(df):
    """Verifica campos específicos de Tickets para novas métricas"""
    print("   🕵️ Análise Profunda de Tickets:")
    
    # SLA / OLA
    if 'slas_id_ttr' in df.columns:
        has_sla = df[df['slas_id_ttr'] != 0].shape[0]
        print(f"      - Tickets com SLA TTR definido: {has_sla} ({has_sla/len(df)*100:.1f}%)")
    
    # Tempo de Solução
    if 'solve_delay_stat' in df.columns:
        print(f"      - Estatísticas de Tempo de Solução disponíveis.")
        
    # Satisfação (Survey)
    # Geralmente fica em tabela separada, mas pode ter flag aqui
    
    # Localização
    if 'locations_id' in df.columns:
        locs = df['locations_id'].nunique()
        print(f"      - Localizações únicas: {locs}")

def main():
    try:
        print("🔌 Conectando ao GLPI...")
        token = get_session_token()
        print(f"🔑 Sessão iniciada: {token[:10]}...")
        
        endpoints = [
            "Ticket",
            "TicketTask", 
            "TicketFollowup",
            "TicketValidation",
            "Problem",
            "Change",
            "Satisfaction", # Pesquisa de satisfação
            "ITILSolution"
        ]
        
        for ep in endpoints:
            analyze_endpoint(token, ep)
            
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
    finally:
        if 'token' in locals():
            kill_session(token)
            print("\n🔒 Sessão encerrada.")

if __name__ == "__main__":
    main()
