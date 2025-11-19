from .client import GLPIClient

class ChangesClient:
    def __init__(self, client: GLPIClient):
        self.client = client
    def list(self, range_start=0, range_limit=1000):
        p = {"range": f"{range_start}-{range_start+range_limit-1}"}
        return self.client.get("/Change", params=p)