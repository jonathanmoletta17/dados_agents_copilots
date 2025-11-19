import os
import json
from sdk.python.glpi_client import GLPIClient
from sdk.python.glpi_client.users import UsersClient
from sdk.python.glpi_client.groups import GroupsClient
from sdk.python.glpi_client.entities import EntitiesClient
from sdk.python.glpi_client.itilcategories import ITILCategoriesClient

def main():
    base = os.environ.get("GLPI_API_URL", "")
    app = os.environ.get("APP_TOKEN", "")
    ses = os.environ.get("SESSION_TOKEN", "")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "snapshots")
    os.makedirs(out_dir, exist_ok=True)
    client = GLPIClient(base_url=base, app_token=app, session_token=ses)
    data = {}
    data["users"] = UsersClient(client).list_all(range_limit=1000)
    data["groups"] = GroupsClient(client).list_all(range_limit=1000)
    data["entities"] = EntitiesClient(client).list_all(range_limit=1000)
    data["itilcategories"] = ITILCategoriesClient(client).list_all(range_limit=1000)
    with open(os.path.join(out_dir, "core_snapshot.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(os.path.join(out_dir, "core_snapshot.json"))

if __name__ == "__main__":
    main()