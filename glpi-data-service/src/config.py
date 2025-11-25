import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuração centralizada para GLPI Data Service.
    Suporta PostgreSQL com schemas separados para DTIC e SIS.
    """
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "glpi_data")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "glpi_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "glpi_secure_2024")
    
    # Database URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Schema mapping for contexts
    CONTEXT_SCHEMAS: Dict[str, str] = {
        "dtic": "dtic",
        "sis": "sis"
    }
    
    # Configurações do GLPI (DTIC)
    GLPI_DTIC_URL: str = os.getenv("GLPI_DTIC_URL", "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php")
    GLPI_DTIC_APP_TOKEN: str = os.getenv("GLPI_DTIC_APP_TOKEN", "")
    GLPI_DTIC_USER_TOKEN: str = os.getenv("GLPI_DTIC_USER_TOKEN", "")

    # Configurações do GLPI (SIS)
    GLPI_SIS_URL: str = os.getenv("GLPI_SIS_URL", "http://cau.ppiratini.intra.rs.gov.br/sis/apirest.php")
    GLPI_SIS_APP_TOKEN: str = os.getenv("GLPI_SIS_APP_TOKEN", "")
    GLPI_SIS_USER_TOKEN: str = os.getenv("GLPI_SIS_USER_TOKEN", "")

    # Mapeamento de Tokens de Usuário por Contexto
    GLPI_USER_TOKENS: Dict[str, str] = {
        "dtic": GLPI_DTIC_USER_TOKEN,
        "sis": GLPI_SIS_USER_TOKEN
    }
    
    # Sync Configuration
    SYNC_INTERVAL: int = int(os.getenv("SYNC_INTERVAL", "15"))
    
    # Application Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DISABLE_SYNC: bool = os.getenv("DISABLE_SYNC", "false").lower() == "true"
    
    @classmethod
    def get_user_token(cls, context: str) -> str:
        """Retorna o user token para um contexto específico."""
        return cls.GLPI_USER_TOKENS.get(context.lower(), "")

    @classmethod
    def get_base_url(cls, context: str) -> str:
        """Retorna a URL base para um contexto específico."""
        if context.lower() == 'sis':
            return cls.GLPI_SIS_URL
        return cls.GLPI_DTIC_URL

    @classmethod
    def get_app_token(cls, context: str) -> str:
        """Retorna o App Token para um contexto específico."""
        if context.lower() == 'sis':
            return cls.GLPI_SIS_APP_TOKEN
        return cls.GLPI_DTIC_APP_TOKEN
    
    @classmethod
    def get_schema(cls, context: str) -> str:
        """Retorna o schema PostgreSQL para um contexto."""
        return cls.CONTEXT_SCHEMAS.get(context.lower(), "dtic")
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se todas as configurações necessárias estão presentes."""
        if cls.DISABLE_SYNC:
            return True
        missing = []
        
        # Validação DTIC
        if not cls.GLPI_DTIC_URL: missing.append("GLPI_DTIC_URL")
        if not cls.GLPI_DTIC_APP_TOKEN: missing.append("GLPI_DTIC_APP_TOKEN")
        
        # Validação SIS
        if not cls.GLPI_SIS_URL: missing.append("GLPI_SIS_URL")
        if not cls.GLPI_SIS_APP_TOKEN: missing.append("GLPI_SIS_APP_TOKEN")

        # Validação de Tokens de Usuário
        if not any(cls.GLPI_USER_TOKENS.values()):
            raise ValueError("Pelo menos um User Token (GLPI_DTIC_USER_TOKEN ou GLPI_SIS_USER_TOKEN) é necessário")

        if missing:
            raise ValueError(f"Configurações obrigatórias ausentes: {', '.join(missing)}")
        return True


# Instância global
config = Config()
