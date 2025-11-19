from .client import GLPIClient

class ITILCategoriesClient:
    def __init__(self, client: GLPIClient):
        self.client = client
    def list(self, range_start=0, range_limit=1000):
        p = {"range": f"{range_start}-{range_start+range_limit-1}"}
        return self.client.get("/ITILCategory", params=p)
    def list_all(self, range_limit=1000, max_pages=10000):
        items = []
        start = 0
        for _ in range(max_pages):
            resp = self.list(range_start=start, range_limit=range_limit)
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