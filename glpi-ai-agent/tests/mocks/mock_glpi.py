import logging
import uvicorn
from fastapi import FastAPI, Header, Request, HTTPException, Query
from typing import Optional, Dict, List
import asyncio

app = FastAPI(title="Mock GLPI Server")

# Storage for validation
TICKETS = {
    101: {
        "id": 101,
        "name": "Minha internet não funciona",
        "content": "Não consigo acessar nenhum site, parece que o cabo está desconectado.",
        "itilcategories_id": 0  # Uncategorized
    },
    102: {
        "id": 102,
        "name": "Preciso instalar o Office",
        "content": "Preciso do Excel e Word instalados na minha máquina nova.",
        "itilcategories_id": 10  # Wrong Category (Hardware > Computadores) - should be Software > Office
    },
    103: {
        "id": 103,
        "name": "Impressora sem toner",
        "content": "A impressora do corredor precisa de toner preto.",
        "itilcategories_id": 11  # Correct Category (Hardware > Impressoras)
    }
}

CATEGORIES = [
    {"id": 10, "name": "Computadores", "completename": "Hardware > Computadores"},
    {"id": 11, "name": "Impressoras", "completename": "Hardware > Impressoras"},
    {"id": 20, "name": "Sistema Operacional", "completename": "Software > Sistema Operacional"},
    {"id": 21, "name": "Office", "completename": "Software > Office"},
    {"id": 30, "name": "Rede Cabeada", "completename": "Rede > Cabeada"},
    {"id": 31, "name": "Wi-Fi", "completename": "Rede > Wi-Fi"}
]

UPDATES_RECEIVED = []

@app.get("/initSession")
def init_session(app_token: Optional[str] = Header(None)):
    return {"session_token": "mock_session_token_12345"}

@app.get("/killSession")
def kill_session(session_token: Optional[str] = Header(None)):
    return {"message": "Session killed"}

@app.get("/Ticket/{ticket_id}")
def get_ticket(ticket_id: int):
    ticket = TICKETS.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.get("/ITILCategory")
def get_categories(range: str = Query("0-100")):
    # Simple pagination mock
    return CATEGORIES

@app.put("/Ticket/{ticket_id}")
async def update_ticket(ticket_id: int, request: Request):
    try:
        payload = await request.json()
        input_data = payload.get("input", {})
        
        print(f"🔄 [MOCK GLPI] Received Update for Ticket #{ticket_id}: {input_data}")
        
        if ticket_id in TICKETS:
            # Simple dictionary update
            for k, v in input_data.items():
                TICKETS[ticket_id][k] = v
                
            UPDATES_RECEIVED.append({
                "ticket_id": ticket_id,
                "updates": input_data
            })
            return [{"id": ticket_id, "message": "Update successful"}]
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/_debug/updates")
def get_updates():
    return UPDATES_RECEIVED

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
