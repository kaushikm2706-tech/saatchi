import json, requests
from .config import BASE_URL, VOICE_MODEL
from .http import headers
from .models import Turn

KEYWORDS = ["bolt", "nut", "wrench", "torque", "valve", "pipe", "wire", "switch"]


def build_request(keywords=None, languages=("Tamil", "English")) -> dict:
    return {"model": VOICE_MODEL, "audioEncoding": "WAV", "mode": "DIARIZATION",
            "keywords": list(keywords or KEYWORDS), "languageBias": list(languages)}


def parse_turns(resp: dict) -> list:
    return [Turn(t["turnId"], t["startMs"], t["endMs"], t["transcript"], t.get("speaker"))
            for t in resp.get("turns", [])]


def transcribe(wav_path: str, keywords=None) -> list:
    req = build_request(keywords)
    with open(wav_path, "rb") as f:
        r = requests.post(
            f"{BASE_URL}/asr/transcribe", headers=headers({"Accept": "application/json"}),
            files={"request": (None, json.dumps(req), "application/json"),
                   "audio": ("audio.wav", f, "audio/wav")}, timeout=600)
    r.raise_for_status()
    return parse_turns(r.json())


class MockVoice:
    def __init__(self, turns):
        self.turns = turns

    def __call__(self, wav_path, keywords=None):
        return self.turns
