from .client import GLPIClient

class TicketUsersClient:
    def __init__(self, client: GLPIClient):
        self.client = client
    def list(self, range_start=0, range_limit=50000):
        p = {"range": f"{range_start}-{range_start+range_limit-1}"}
        return self.client.get("/Ticket_User", params=p)
    def create(self, data):
        return self.client.post("/Ticket_User", json=data)
    def delete(self, relation_id):
        return self.client.delete(f"/Ticket_User/{relation_id}")

class GroupTicketsClient:
    def __init__(self, client: GLPIClient):
        self.client = client
    def list(self, range_start=0, range_limit=50000):
        p = {"range": f"{range_start}-{range_start+range_limit-1}"}
        return self.client.get("/Group_Ticket", params=p)
    def create(self, data):
        return self.client.post("/Group_Ticket", json=data)
    def delete(self, relation_id):
        return self.client.delete(f"/Group_Ticket/{relation_id}")

class SearchClient:
    def __init__(self, client: GLPIClient):
        self.client = client
    def search_tickets(self, criteria, forcedisplay=None, range_start=0, range_limit=1000):
        p = {"range": f"{range_start}-{range_start+range_limit-1}"}
        for i, c in enumerate(criteria):
            p[f"criteria[{i}][field]"] = str(c.get("field", ""))
            p[f"criteria[{i}][searchtype]"] = str(c.get("searchtype", "contains"))
            p[f"criteria[{i}][value]"] = str(c.get("value", ""))
        if forcedisplay:
            for f in forcedisplay:
                p.setdefault("forcedisplay[]", f)
        return self.client.get("/search/Ticket", params=p)