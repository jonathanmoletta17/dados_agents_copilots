from .client import GLPIClient

class TicketsClient:
    def __init__(self, client: GLPIClient):
        self.client = client
    def list(self, range_start=0, range_limit=1000, params=None):
        p = {"range": f"{range_start}-{range_start+range_limit-1}", "expand_dropdowns": "false", "get_hateoas": "false"}
        if params:
            p.update(params)
        r = self.client.get("/Ticket", params=p)
        return r
    def list_all(self, range_limit=1000, params=None, max_pages=10000):
        items = []
        start = 0
        for _ in range(max_pages):
            resp = self.list(range_start=start, range_limit=range_limit, params=params)
            if resp.status_code not in (200, 206):
                break
            batch = resp.json()
            if not batch:
                break
            items.extend(batch)
            if len(batch) < range_limit:
                break
            start += range_limit
        return items
    def get(self, ticket_id):
        return self.client.get(f"/Ticket/{ticket_id}")
    def create(self, data):
        return self.client.post("/Ticket", json=data)
    def update(self, ticket_id, data):
        return self.client.put(f"/Ticket/{ticket_id}", json=data)
    def delete(self, ticket_id):
        return self.client.delete(f"/Ticket/{ticket_id}")