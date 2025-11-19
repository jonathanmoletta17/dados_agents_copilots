import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdk.python.glpi_client import GLPIClient
from sdk.python.glpi_client.tickets import TicketsClient
from sdk.python.glpi_client.relations import TicketUsersClient, GroupTicketsClient

def main():
    base = os.environ.get("GLPI_API_URL", "/apirest.php")
    app = os.environ.get("APP_TOKEN", "")
    ses = os.environ.get("SESSION_TOKEN", "")
    ticket_id = os.environ.get("TICKET_ID")
    user_id = os.environ.get("USER_ID")
    group_id = os.environ.get("GROUP_ID")
    client = GLPIClient(base_url=base, app_token=app, session_token=ses)
    tc = TicketsClient(client)
    tuc = TicketUsersClient(client)
    gc = GroupTicketsClient(client)
    if user_id:
        tuc.create({"tickets_id": int(ticket_id), "users_id": int(user_id), "type": 2})
    if group_id:
        gc.create({"tickets_id": int(ticket_id), "groups_id": int(group_id), "type": 2})
    r = tc.get(int(ticket_id))
    print(r.status_code)

if __name__ == "__main__":
    main()