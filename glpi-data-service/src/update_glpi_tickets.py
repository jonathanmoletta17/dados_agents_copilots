import sys
import os
import time

# Ensure src is in path
sys.path.append('/app')

from src.config import config
from src.glpi_client.client import GLPIClient

def update_tickets():
    print("Initializing GLPI Client...")
    client = GLPIClient(
        base_url=config.GLPI_SIS_URL,
        app_token=config.GLPI_SIS_APP_TOKEN,
        user_token=config.GLPI_SIS_USER_TOKEN
    )
    
    # Revert 4228 -> 1 (Novo)
    
    updates = [
        (4228, 1)
    ]
    
    with client:
        for tid, status in updates:
            print(f"Reverting Ticket {tid} to status {status}...")
            try:
                response = client.update_ticket(tid, {"status": status})
                print(f"Success: {response}")
            except Exception as e:
                print(f"Failed to update Ticket {tid}: {e}")

if __name__ == "__main__":
    update_tickets()
