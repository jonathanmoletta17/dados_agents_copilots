import os
import json
from sdk.python.glpi_client import GLPIClient
from sdk.python.glpi_client.relations import TicketUsersClient, GroupTicketsClient

class ProfilesClient:
    def __init__(self, client):
        self.client = client
    def list(self, range_start=0, range_limit=1000):
        p = {"range": f"{range_start}-{range_start+range_limit-1}"}
        return self.client.get("/Profile", params=p)

def main():
    base = os.environ.get("GLPI_API_URL", "")
    app = os.environ.get("APP_TOKEN", "")
    ses = os.environ.get("SESSION_TOKEN", "")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "snapshots")
    os.makedirs(out_dir, exist_ok=True)
    client = GLPIClient(base_url=base, app_token=app, session_token=ses)
    data = {}
    pc = ProfilesClient(client)
    pr = pc.list(range_start=0, range_limit=1000)
    data["profiles_status"] = pr.status_code
    data["profiles"] = pr.json() if pr.status_code in (200,206) else []
    tuc = TicketUsersClient(client)
    gt = GroupTicketsClient(client)
    tur = tuc.list(range_start=0, range_limit=50000)
    gtr = gt.list(range_start=0, range_limit=50000)
    data["ticket_users_status"] = tur.status_code
    data["group_tickets_status"] = gtr.status_code
    data["ticket_users"] = tur.json() if tur.status_code in (200,206) else []
    data["group_tickets"] = gtr.json() if gtr.status_code in (200,206) else []
    with open(os.path.join(out_dir, "profiles_relations_snapshot.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(os.path.join(out_dir, "profiles_relations_snapshot.json"))

if __name__ == "__main__":
    main()