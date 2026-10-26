import requests
from .config import BASE_URL, api_key


def headers(extra=None):
    h = {"Authorization": f"Bearer {api_key()}"}
    h.update(extra or {})
    return h


def post_json(path, body, timeout=300, stream=False, accept=None):
    return requests.post(f"{BASE_URL}{path}", json=body, stream=stream, timeout=timeout,
                         headers=headers({"Accept": accept} if accept else None))


def upload_file(path: str) -> str:
    """Files API: POST /v1/files, purpose=user_data. Returns file id (e.g. file-123...)."""
    with open(path, "rb") as f:
        r = requests.post(f"{BASE_URL}/files", headers=headers(), data={"purpose": "user_data"},
                          files={"file": f}, timeout=600)
    r.raise_for_status()
    return r.json()["id"]
