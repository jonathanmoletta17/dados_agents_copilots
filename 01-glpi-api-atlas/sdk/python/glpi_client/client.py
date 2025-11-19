import os
import requests

class GLPIClient:
    def __init__(self, base_url=None, app_token=None, session_token=None):
        self.base_url = (base_url or os.environ.get("GLPI_API_URL", "/apirest.php")).rstrip("/")
        self.session = requests.Session()
        app = app_token or os.environ.get("APP_TOKEN", "")
        ses = session_token or os.environ.get("SESSION_TOKEN", "")
        if app:
            self.session.headers.update({"App-Token": app})
        if ses:
            self.session.headers.update({"Session-Token": ses})
        self.session.headers.update({"Content-Type": "application/json"})
    def get(self, path, params=None):
        url = f"{self.base_url}{path}"
        return self.session.get(url, params=params)
    def post(self, path, json=None):
        url = f"{self.base_url}{path}"
        return self.session.post(url, json=json)
    def put(self, path, json=None):
        url = f"{self.base_url}{path}"
        return self.session.put(url, json=json)
    def delete(self, path):
        url = f"{self.base_url}{path}"
        return self.session.delete(url)