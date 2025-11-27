import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class GLPIClient:
    def __init__(self, base_url: str, app_token: str, user_token: str):
        self.base_url = base_url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        
        if not all([self.base_url, self.app_token, self.user_token]):
            raise ValueError("URL, App Token and User Token are required.")
        
        self.session_token = None
        self.session = requests.Session()
        self.session.timeout = 30
        self.max_retries = 3
        self.retry_delay = 5
        
        self.init_session()
    
    def init_session(self):
        """Initializes GLPI session."""
        url = f"{self.base_url}/initSession"
        headers = {
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                self.session_token = data.get('session_token')
                if not self.session_token:
                    raise Exception("No session token received")
                return
            except Exception as e:
                logger.error(f"Failed to init session (Attempt {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def close_session(self):
        """Closes GLPI session."""
        if not self.session_token:
            return
        url = f"{self.base_url}/killSession"
        headers = {
            'App-Token': self.app_token,
            'Session-Token': self.session_token
        }
        try:
            self.session.get(url, headers=headers)
        except Exception as e:
            logger.warning(f"Error closing session: {e}")
        finally:
            self.session_token = None

    def make_request(self, endpoint: str, params: Dict = None, method: str = 'GET', json_data: Dict = None) -> Dict:
        """Makes authenticated request to GLPI API."""
        if not self.session_token:
            raise Exception("Session not initialized")
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'App-Token': self.app_token,
            'Session-Token': self.session_token,
            'Content-Type': 'application/json'
        }
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, headers=headers, params=params)
                elif method.upper() == 'POST':
                    response = self.session.post(url, headers=headers, params=params, json=json_data)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, headers=headers, params=params, json=json_data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    logger.warning("Session expired. Renewing...")
                    self.init_session()
                    headers['Session-Token'] = self.session_token
                    continue
                logger.error(f"HTTP Error in {endpoint}: {e}")
                raise
            except Exception as e:
                logger.error(f"Request failed (Attempt {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def update_ticket(self, ticket_id: int, updates: Dict) -> Dict:
        """Updates a ticket."""
        endpoint = f"Ticket/{ticket_id}"
        payload = {"input": updates}
        payload["input"]["id"] = ticket_id
        return self.make_request(endpoint, method='PUT', json_data=payload)

    def create_ticket(self, input_payload: Dict) -> Dict:
        """Creates a ticket."""
        payload = {"input": input_payload}
        return self.make_request("Ticket", method='POST', json_data=payload)

    def get_all_pages(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Fetches all pages from an endpoint."""
        if params is None: params = {}
        all_items = []
        start = 0
        limit = 1000
        
        while True:
            params['range'] = f"{start}-{start + limit - 1}"
            try:
                items = self.make_request(endpoint, params)
                if not items: break
                all_items.extend(items)
                if len(items) < limit: break
                start += limit
            except Exception as e:
                logger.error(f"Error fetching pages for {endpoint}: {e}")
                break
        return all_items
