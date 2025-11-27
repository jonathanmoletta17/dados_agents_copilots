import os
import logging
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration for GLPI AI Agent.
    """
    
    # Contexts
    CONTEXTS = ["dtic", "sis"]
    
    # GLPI Configuration
    GLPI_DTIC_URL: str = os.getenv("GLPI_DTIC_URL", "")
    GLPI_DTIC_APP_TOKEN: str = os.getenv("GLPI_DTIC_APP_TOKEN", "")
    GLPI_DTIC_USER_TOKEN: str = os.getenv("GLPI_DTIC_USER_TOKEN", "")

    GLPI_SIS_URL: str = os.getenv("GLPI_SIS_URL", "")
    GLPI_SIS_APP_TOKEN: str = os.getenv("GLPI_SIS_APP_TOKEN", "")
    GLPI_SIS_USER_TOKEN: str = os.getenv("GLPI_SIS_USER_TOKEN", "")
    
    # AI Configuration
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://host.docker.internal:11434/api/generate")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "llama3")
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.85"))
    
    # Worker Configuration
    POLLING_INTERVAL: int = int(os.getenv("POLLING_INTERVAL", "60"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Category Cache Configuration
    CATEGORY_CACHE_TTL_SECONDS: int = int(os.getenv("CATEGORY_CACHE_TTL_SECONDS", "300"))

    @classmethod
    def get_credentials(cls, context: str) -> Dict[str, str]:
        """Returns credentials for a specific context."""
        context = context.lower()
        if context == 'sis':
            return {
                "url": cls.GLPI_SIS_URL,
                "app_token": cls.GLPI_SIS_APP_TOKEN,
                "user_token": cls.GLPI_SIS_USER_TOKEN
            }
        # Default to DTIC
        return {
            "url": cls.GLPI_DTIC_URL,
            "app_token": cls.GLPI_DTIC_APP_TOKEN,
            "user_token": cls.GLPI_DTIC_USER_TOKEN
        }
