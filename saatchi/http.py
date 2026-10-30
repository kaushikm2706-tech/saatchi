import time
import requests
from .config import BASE_URL, api_key

RETRY_STATUS = {429, 500, 502, 503, 504}


def headers(extra=None):
    h = {"Authorization": f"Bearer {api_key()}"}
    h.update(extra or {})
    return h


def request_with_retry(method, url, tries=4, base_delay=2.0, **kw):
    """Exponential backoff on 429/5xx and connection errors (Meta docs recommend backoff for 429)."""
    last = None
    for i in range(tries):
        try:
            r = requests.request(method, url, **kw)
            if r.status_code not in RETRY_STATUS:
                return r
            last = r
        except (requests.ConnectionError, requests.Timeout) as e:
            last = e
        time.sleep(base_delay * (2 ** i))
    if isinstance(last, Exception):
        raise last
    return last


def post_json(path, body, timeout=300, stream=False, accept=None):
    return request_with_retry("POST", f"{BASE_URL}{path}", json=body, stream=stream, timeout=timeout,
                              headers=headers({"Accept": accept} if accept else None))


def upload_file(path: str) -> str:
    """Files API: POST /v1/files, purpose=user_data. Returns file id (e.g. file-123...)."""
    with open(path, "rb") as f:
        r = requests.post(f"{BASE_URL}/files", headers=headers(), data={"purpose": "user_data"},
                          files={"file": f}, timeout=600)
    r.raise_for_status()
    return r.json()["id"]
