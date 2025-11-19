import os
import json
import requests
import time
from typing import List, Dict, Any, Optional
from text_processor import TextProcessor

# ==========================================
# CONFIGURATION & ENV
# ==========================================

def _load_env_file():
    """Loads .env file manually if not loaded."""
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'), # 04-glpi-smart-search/.env
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'), # root .env
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"): continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
                return
            except Exception:
                pass

_load_env_file()

GLPI_URL = os.environ.get("GLPI_URL", "")
GLPI_APP_TOKEN = os.environ.get("GLPI_APP_TOKEN", "")
GLPI_USER_TOKEN = os.environ.get("GLPI_USER_TOKEN", "")

# ==========================================
# GLPI CLIENT
# ==========================================

class GLPIClient:
    def __init__(self):
        self.base_url = GLPI_URL.rstrip("/")
        self.app_token = GLPI_APP_TOKEN
        self.user_token = GLPI_USER_TOKEN
        self.session_token = None
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "App-Token": self.app_token
        })
        
        # Caches
        self.users_cache = {}
        self.entities_cache = {}
        self.categories_cache = {}
        self.groups_cache = {}

    def init_session(self) -> bool:
        """Initializes GLPI session."""
        if not self.base_url or not self.user_token:
            print("[ERROR] GLPI URL or User Token not configured.")
            return False
            
        try:
            url = f"{self.base_url}/initSession"
            headers = {"Authorization": f"user_token {self.user_token}"}
            resp = self.session.get(url, headers=headers)
            
            if resp.status_code == 200:
                self.session_token = resp.json().get("session_token")
                self.session.headers.update({"Session-Token": self.session_token})
                return True
            else:
                print(f"[ERROR] Init session failed: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            return False

    def kill_session(self):
        """Kills GLPI session."""
        if self.session_token:
            try:
                self.session.get(f"{self.base_url}/killSession")
            except:
                pass

    def _get_all_pages(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Helper to fetch all pages from an endpoint."""
        if params is None:
            params = {}
        
        all_items = []
        start = 0
        limit = 1000 # Max range size
        
        while True:
            params['range'] = f"{start}-{start + limit - 1}"
            try:
                resp = self.session.get(f"{self.base_url}/{endpoint}", params=params)
                if resp.status_code in [200, 206]:
                    items = resp.json()
                    if not items:
                        break
                    all_items.extend(items)
                    if len(items) < limit:
                        break
                    start += limit
                else:
                    print(f"[WARN] Error fetching {endpoint}: {resp.status_code}")
                    break
            except Exception as e:
                print(f"[ERROR] Exception fetching {endpoint}: {e}")
                break
                
        return all_items

    def load_caches(self):
        """Preloads metadata caches."""
        print("Loading metadata caches...")
        
        # Users
        users = self._get_all_pages("User")
        for u in users:
            uid = str(u.get('id'))
            name = u.get('realname') or u.get('name') or f"User {uid}"
            if u.get('firstname'):
                name = f"{u.get('firstname')} {u.get('realname') or ''}".strip()
            self.users_cache[uid] = name
            
        # Entities
        entities = self._get_all_pages("Entity")
        for e in entities:
            self.entities_cache[str(e.get('id'))] = e.get('name', 'Unknown Entity')
            
        # Categories
        cats = self._get_all_pages("ITILCategory")
        for c in cats:
            self.categories_cache[str(c.get('id'))] = c.get('name', 'Unknown Category')
            
        # Groups
        groups = self._get_all_pages("Group")
        for g in groups:
            self.groups_cache[str(g.get('id'))] = g.get('name', 'Unknown Group')

    def fetch_all_tickets(self) -> List[Dict]:
        """Fetches all tickets with rich data."""
        if not self.session_token:
            if not self.init_session():
                return []
                
        self.load_caches()
        
        print("Fetching all tickets...")
        raw_tickets = self._get_all_pages("Ticket", params={"expand_dropdowns": "false"})
        
        # Fetch relationships (Actors)
        print("Fetching ticket actors...")
        actors = self._get_all_pages("Ticket_User")
        ticket_actors = {} # ticket_id -> {requester: name, technician: name}
        
        for a in actors:
            tid = str(a.get('tickets_id'))
            uid = str(a.get('users_id'))
            type_ = a.get('type') # 1=Requester, 2=Technician
            
            if tid not in ticket_actors:
                ticket_actors[tid] = {'requester': 'N/A', 'technician': 'N/A'}
                
            user_name = self.users_cache.get(uid, f"User {uid}")
            
            if type_ == 1:
                ticket_actors[tid]['requester'] = user_name
            elif type_ == 2:
                ticket_actors[tid]['technician'] = user_name

        # Process tickets
        processed_tickets = []
        for t in raw_tickets:
            tid = str(t.get('id'))
            actors_data = ticket_actors.get(tid, {'requester': 'N/A', 'technician': 'N/A'})
            
            # Status mapping
            status_map = {
                1: 'Novo', 2: 'Em andamento (atribuído)', 3: 'Em andamento (planejado)',
                4: 'Pendente', 5: 'Solucionado', 6: 'Fechado'
            }
            status_id = int(t.get('status', 1))
            status_text = status_map.get(status_id, f"Status {status_id}")
            
            # Markdown conversion
            content_html = t.get('content', '')
            content_md = TextProcessor.html_to_markdown(content_html)
            
            processed_tickets.append({
                'ID': int(tid),
                'TITULO': t.get('name', ''),
                'DESCRICAO': content_md,
                'STATUS': status_text,
                'CATEGORIA': self.categories_cache.get(str(t.get('itilcategories_id')), 'N/A'),
                'ENTIDADE': self.entities_cache.get(str(t.get('entities_id')), 'N/A'),
                'REQUERENTE': actors_data['requester'],
                'TECNICO': actors_data['technician'],
                'GRUPO': 'N/A', # Group logic can be added if needed, keeping simple for now
                'DATA_CRIACAO': t.get('date'),
                'DATA_MODIFICACAO': t.get('date_mod'),
                'IS_DELETED': 0 if t.get('is_deleted') == 0 else 1,
                'URL': f"{self.base_url.replace('/apirest.php', '')}/front/ticket.form.php?id={tid}"
            })
            
        return processed_tickets

# ==========================================
# LEGACY COMPATIBILITY / EXPORTS
# ==========================================

def fetch_all_for_indexer():
    """Facade for the indexer script."""
    client = GLPIClient()
    try:
        return client.fetch_all_tickets()
    finally:
        client.kill_session()