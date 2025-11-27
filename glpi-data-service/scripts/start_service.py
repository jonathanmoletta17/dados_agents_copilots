import asyncio
import logging
import threading
import uvicorn
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.workers.realtime_sync_worker import RealtimeSyncWorker
from src.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_workers():
    """Runs all workers concurrently."""
    logger.info("🚀 Starting Workers (Sync)...")
    await asyncio.gather(
        RealtimeSyncWorker().run()
    )

def run_worker():
    """Runs the workers in an asyncio loop."""
    asyncio.run(start_workers())

def run_api():
    """Runs the FastAPI application using Uvicorn."""
    logger.info("🚀 Starting FastAPI server...")
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("UVICORN_RELOAD", "False").lower() == "true",
        log_level="info"
    )

if __name__ == "__main__":
    print(f"🔌 DATABASE_URL: {config.DATABASE_URL}", flush=True)
    logger.info("🔥 Starting GLPI Data Service (Workers + API)...")
    
    # Start Worker in a separate thread
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    
    # Start API in the main thread
    run_api()
