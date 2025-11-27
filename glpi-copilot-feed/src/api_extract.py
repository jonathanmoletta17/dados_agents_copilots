import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("GLPI_DTIC_URL")
APP_TOKEN = os.getenv("GLPI_DTIC_APP_TOKEN")
USER_TOKEN = os.getenv("GLPI_DTIC_USER_TOKEN")

class GLPIApi:
    def __init__(self):
        self.session_token = None
        if not all([API_URL, APP_TOKEN, USER_TOKEN]):
            raise ValueError("Credenciais da API GLPI não configuradas no .env")

    def init_session(self):
        url = f"{API_URL}/initSession"
        headers = {
            "App-Token": APP_TOKEN,
            "Authorization": f"user_token {USER_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.session_token = response.json()['session_token']
        else:
            raise Exception(f"Falha ao iniciar sessão API: {response.text}")

    def kill_session(self):
        if self.session_token:
            url = f"{API_URL}/killSession"
            headers = {
                "App-Token": APP_TOKEN,
                "Session-Token": self.session_token
            }
            requests.get(url, headers=headers)
            self.session_token = None

    def get_all_items(self, endpoint, limit=5000):
        """Busca todos os itens de um endpoint (paginado se necessário)"""
        if not self.session_token:
            self.init_session()

        url = f"{API_URL}/{endpoint}"
        headers = {
            "App-Token": APP_TOKEN,
            "Session-Token": self.session_token
        }
        
        all_items = []
        range_start = 0
        batch_size = 100 # GLPI default limit is often small
        
        while True:
            params = {
                "range": f"{range_start}-{range_start+batch_size}",
                "expand_dropdowns": "false"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 206 or response.status_code == 200:
                data = response.json()
                if not data:
                    break
                
                all_items.extend(data)
                
                # Check headers for total count to know when to stop
                content_range = response.headers.get('Content-Range')
                if content_range:
                    # Format: 0-99/2700
                    try:
                        total = int(content_range.split('/')[1])
                        if range_start + batch_size >= total:
                            break
                    except:
                        pass
                
                if len(data) < batch_size:
                    break
                    
                range_start += batch_size
                # Avoid rate limiting
                time.sleep(0.1)
            else:
                print(f"Erro ao buscar {endpoint}: {response.status_code}")
                break
                
            if len(all_items) >= limit:
                break
                
        return pd.DataFrame(all_items)

def get_tasks():
    api = GLPIApi()
    try:
        print("Extraindo Tarefas (TicketTask)...")
        df = api.get_all_items("TicketTask")
        return df
    finally:
        api.kill_session()

def get_problems():
    api = GLPIApi()
    try:
        print("Extraindo Problemas (Problem)...")
        df = api.get_all_items("Problem")
        return df
    finally:
        api.kill_session()

def get_changes():
    api = GLPIApi()
    try:
        print("Extraindo Mudanças (Change)...")
        df = api.get_all_items("Change")
        return df
    finally:
        api.kill_session()

def get_followups_count():
    """Retorna contagem de followups agrupada por ticket_id"""
    api = GLPIApi()
    try:
        print("Extraindo Acompanhamentos (TicketFollowup)...")
        # Para followups, volume é alto (14k). Vamos pegar apenas campos essenciais.
        # Infelizmente GLPI API standard não faz aggregate count fácil.
        # Vamos pegar tudo mas só colunas ID e tickets_id
        df = api.get_all_items("TicketFollowup", limit=20000)
        if not df.empty and 'tickets_id' in df.columns:
            return df['tickets_id'].value_counts().reset_index()
        return pd.DataFrame()
    finally:
        api.kill_session()
