from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
import logging
import json
from src.services.ai_service import handle_ticket_update

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/webhook/ticket")
async def glpi_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives webhook events from GLPI.
    Expected payload depends on GLPI Webhook plugin configuration.
    Commonly:
    {
        "event": "add",
        "itemtype": "Ticket",
        "items": [{"id": 123, ...}]
    }
    """
    try:
        payload = await request.json()
        logger.info(f"Webhook received: {json.dumps(payload)}")
        
        ticket_id = None
        event = payload.get('event')
        itemtype = payload.get('itemtype')
        
        # Validate ItemType
        if itemtype != 'Ticket':
            return {"status": "ignored", "reason": "Not a ticket"}
            
        # Extract ID
        items = payload.get('items', [])
        if items and isinstance(items, list):
            ticket_id = items[0].get('id')
        elif payload.get('id'):
            # Some webhook formats send ID directly
            ticket_id = payload.get('id')
            
        if not ticket_id:
             logger.error("Could not extract Ticket ID from payload")
             return {"status": "error", "message": "Ticket ID not found"}
             
        # Trigger Background Task
        # Defaulting to 'dtic' context. 
        # TODO: Logic to determine context (SIS vs DTIC) based on entities_id if available in payload
        context = 'dtic' 
        
        background_tasks.add_task(handle_ticket_update, ticket_id, context)
        
        return {"status": "processing", "ticket_id": ticket_id}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
