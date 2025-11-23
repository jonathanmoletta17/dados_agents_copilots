from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.db.postgres_manager import get_db_manager
from src.workers.realtime_sync_worker import RealtimeSyncWorker

router = APIRouter()

@router.post("/{context}/sincronizar")
async def trigger_sync(context: str, background_tasks: BackgroundTasks, completa: bool = False):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    worker = RealtimeSyncWorker()
    if completa:
        background_tasks.add_task(worker.full_sync, context)
    else:
        background_tasks.add_task(worker.incremental_sync, context)
        
    return {"status": "success", "tipo": "completa" if completa else "incremental", "contexto": context}

@router.get("/{context}/sincronizacao/historico")
async def get_sync_history(context: str, limite: int = 10):
    if context not in ["dtic", "sis"]:
        raise HTTPException(400, "Contexto inválido")
        
    db = get_db_manager(context)
    history = db.get_sync_history(limit=limite)
    return {
        "contexto": context,
        "historico": [h.to_dict() for h in history]
    }
