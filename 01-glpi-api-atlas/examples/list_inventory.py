import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdk.python.glpi_client import GLPIClient
from sdk.python.glpi_client.inventory import InventoryClient

def main():
    base = os.environ.get("GLPI_API_URL", "")
    app = os.environ.get("APP_TOKEN", "")
    ses = os.environ.get("SESSION_TOKEN", "")
    resource = os.environ.get("RESOURCE", "Computer")
    client = GLPIClient(base_url=base, app_token=app, session_token=ses)
    ic = InventoryClient(client)
    r = ic.list_resource(resource, range_start=0, range_limit=10)
    print(r.status_code)

if __name__ == "__main__":
    main()