from fastapi import FastAPI
import logging
from src.api.webhook import router as webhook_router
from src.config.settings import Config

# Setup Logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="GLPI AI Agent", version="1.0.0")

app.include_router(webhook_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "glpi-ai-agent"}
