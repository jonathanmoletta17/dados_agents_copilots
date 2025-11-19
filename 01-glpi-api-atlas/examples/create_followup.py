import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdk.python.glpi_client import GLPIClient
from sdk.python.glpi_client.followups import FollowupsClient

def main():
    base = os.environ.get("GLPI_API_URL", "")
    app = os.environ.get("APP_TOKEN", "")
    ses = os.environ.get("SESSION_TOKEN", "")
    ticket_id = int(os.environ.get("TICKET_ID", "0"))
    content = os.environ.get("FOLLOWUP_CONTENT", "")
    client = GLPIClient(base_url=base, app_token=app, session_token=ses)
    fc = FollowupsClient(client)
    r = fc.create({"items_id": ticket_id, "itemtype": "Ticket", "content": content})
    print(r.status_code)

if __name__ == "__main__":
    main()