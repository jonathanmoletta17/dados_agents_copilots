from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config import config
from src.api.routes import tickets, stats, sync, health, dashboard, sis_dashboard, search, sis_carregadores, glpi_submit
from src.workers.realtime_sync_worker import RealtimeSyncWorker

# Configuração de Logs
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando GLPI Data Service...")
    
    try:
        config.validate()
        task = None
        if not config.DISABLE_SYNC:
            sync_worker = RealtimeSyncWorker()
            task = asyncio.create_task(sync_worker.run())
            logger.info("✅ Sync worker iniciado")
        yield
        if task:
            sync_worker.stop()
            await task
        
    except Exception as e:
        logger.error(f"❌ Erro no startup: {e}")
        raise
    finally:
        logger.info("🛑 Encerrando GLPI Data Service...")

app = FastAPI(
    title="GLPI Data Service",
    description="API para sincronização e consulta de dados do GLPI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(health.router, tags=["Health"])
app.include_router(tickets.router, prefix="/api/v1", tags=["Tickets"])
app.include_router(stats.router, prefix="/api/v1", tags=["Estatísticas"])
app.include_router(sync.router, prefix="/api/v1", tags=["Sincronização"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(sis_dashboard.router, prefix="/api/v1", tags=["SIS Dashboard"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
logger.info("Registering Carregadores router...")
app.include_router(sis_carregadores.router, prefix="/api/v1", tags=["Carregadores"])
app.include_router(glpi_submit.router, prefix="/api/v1", tags=["GLPI Submission"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
