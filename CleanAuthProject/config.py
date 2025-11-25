import os
from dataclasses import dataclass
from dotenv import load_dotenv

# load default .env and fallback to project-level .env
load_dotenv()
_here = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_here, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)

@dataclass
class Settings:
    glpi_url: str = os.environ.get("GLPI_URL", "").rstrip("/")
    glpi_app_token: str = os.environ.get("GLPI_APP_TOKEN", "")
    glpi_user_token: str = os.environ.get("GLPI_USER_TOKEN", "")
    request_timeout: int = int(os.environ.get("REQUEST_TIMEOUT", "10"))
    verify_ssl: bool = os.environ.get("GLPI_VERIFY_SSL", "true").lower() in {"1", "true", "yes"}

    def validate(self):
        if not self.glpi_url or not self.glpi_app_token:
            raise RuntimeError("GLPI_URL/GLPI_APP_TOKEN ausentes.")

settings = Settings()
