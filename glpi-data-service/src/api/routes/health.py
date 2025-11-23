from fastapi import APIRouter
from src.db.postgres_manager import get_db_manager

router = APIRouter()

@router.get("/health")
async def health_check():
    status = {"status": "healthy", "contextos": {}}
    for ctx in ["dtic", "sis"]:
        try:
            db = get_db_manager(ctx)
            count = db.count_tickets()
            last_sync = db.get_sync_meta("last_sync_time")
            status["contextos"][ctx] = {
                "banco_dados": "ok",
                "total_tickets": count,
                "ultima_sincronizacao": last_sync
            }
        except Exception as e:
            status["contextos"][ctx] = {"error": str(e)}
    return status
