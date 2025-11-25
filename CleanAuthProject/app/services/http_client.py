import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def build_session(timeout: int, retries: int = 2, backoff: float = 0.3, verify: bool = True) -> requests.Session:
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=(502, 503, 504), allowed_methods=frozenset(["GET", "POST"]))
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.request_timeout = timeout
    s.verify = verify
    return s
