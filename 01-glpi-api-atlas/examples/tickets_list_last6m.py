import os
from datetime import datetime, timedelta
from sdk.python.glpi_client import GLPIClient, TicketsClient

def main():
    base = os.environ.get("GLPI_API_URL", "/apirest.php")
    app = os.environ.get("APP_TOKEN", "")
    ses = os.environ.get("SESSION_TOKEN", "")
    client = GLPIClient(base_url=base, app_token=app, session_token=ses)
    tc = TicketsClient(client)
    all_items = tc.list_all(range_limit=1000)
    now = datetime.now()
    start = now - timedelta(days=180)
    def parse(s):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None
    filtered = []
    for it in all_items:
        d = parse(it.get("date", ""))
        if d and start <= d <= now:
            filtered.append(it)
    print(len(filtered))

if __name__ == "__main__":
    main()