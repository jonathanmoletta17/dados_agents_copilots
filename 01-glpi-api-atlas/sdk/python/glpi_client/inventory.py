from .client import GLPIClient

class InventoryClient:
    def __init__(self, client: GLPIClient):
        self.client = client
    def list_resource(self, resource, range_start=0, range_limit=1000):
        p = {"range": f"{range_start}-{range_start+range_limit-1}"}
        return self.client.get(f"/{resource}", params=p)