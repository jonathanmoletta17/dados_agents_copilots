import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdk.python.glpi_client import GLPIClient
from sdk.python.glpi_client.tasks import TasksClient

def main():
    base = os.environ.get("GLPI_API_URL", "")
    app = os.environ.get("APP_TOKEN", "")
    ses = os.environ.get("SESSION_TOKEN", "")
    items_id = int(os.environ.get("TASK_ITEMS_ID", "0"))
    content = os.environ.get("TASK_CONTENT", "")
    client = GLPIClient(base_url=base, app_token=app, session_token=ses)
    tc = TasksClient(client)
    r = tc.create({"items_id": items_id, "itemtype": "Ticket", "content": content})
    print(r.status_code)

if __name__ == "__main__":
    main()