import json, re
from .config import SPARK_MODEL
from .apiclient import post_json
from .models import Claim, SparkEvidence, UNVERIFIABLE, SUPPORTED, CONTRADICTED

CLAIM_PROMPT = """You get a worker's narration as timed turns (Tamil, English or mixed).
Extract atomic, checkable claims about what physically happened. Ignore opinions and chit-chat.
Return ONLY JSON: {"claims":[{"turn_id":int,"quote":str,"english":str,"ctype":"action|count|order|state|tool","noun":str,"count":int|null}]}
"noun" is ONE short English noun phrase naming the key object (e.g. "bolt"). Do not invent claims.

TURNS:
"""

VERIFY_PROMPT = """Watch the attached video. Check ONE claim, using only what is visible.
Claim: "{english}" (said at about {t0:.1f}s-{t1:.1f}s).
Return ONLY JSON: {{"verdict":"SUPPORTED|CONTRADICTED|UNVERIFIABLE","confidence":0-1,"rationale":str,"timestamps_s":[numbers]}}
Use UNVERIFIABLE if the relevant action is not clearly visible. Never guess."""


def extract_text(resp: dict) -> str:
    """OpenAI-Responses-style output extraction. [U] exact Meta shape: verify on first live call."""
    if isinstance(resp.get("output_text"), str):
        return resp["output_text"]
    parts = []
    for item in resp.get("output", []):
        for c in item.get("content", []) or []:
            if c.get("type") in ("output_text", "text") and "text" in c:
                parts.append(c["text"])
    return "".join(parts)


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    return json.loads(m.group(0))


def _ask(content, max_tokens=4000):
    body = {"model": SPARK_MODEL, "max_output_tokens": max_tokens,
            "input": [{"type": "message", "role": "user", "content": content}]}
    r = post_json("/responses", body)
    r.raise_for_status()
    j = r.json()
    return extract_text(j), j.get("usage")


def extract_claims(turns) -> list:
    listing = "\n".join(f"[{t.turn_id}] {t.start_ms/1000:.1f}-{t.end_ms/1000:.1f}s: {t.transcript}" for t in turns)
    text, _ = _ask([{"type": "input_text", "text": CLAIM_PROMPT + listing}])
    out = []
    for i, c in enumerate(parse_json(text).get("claims", [])):
        out.append(Claim(i, int(c["turn_id"]), c["quote"], c["english"], c["ctype"], c["noun"].strip(), c.get("count")))
    return out


def verify_claim(claim: Claim, file_id: str, t0: float, t1: float) -> SparkEvidence:
    prompt = VERIFY_PROMPT.format(english=claim.english, t0=t0, t1=t1)
    text, usage = _ask([{"type": "input_text", "text": prompt}, {"type": "input_video", "file_id": file_id}])
    j = parse_json(text)
    v = j.get("verdict", UNVERIFIABLE)
    if v not in (SUPPORTED, CONTRADICTED, UNVERIFIABLE):
        v = UNVERIFIABLE
    return SparkEvidence(v, float(j.get("confidence", 0)), j.get("rationale", ""), j.get("timestamps_s", []))


class MockSpark:
    def __init__(self, claims, verdicts):
        self.claims, self.verdicts = claims, verdicts  # verdicts: claim_id -> SparkEvidence

    def extract_claims(self, turns):
        return self.claims

    def verify_claim(self, claim, file_id, t0, t1):
        return self.verdicts.get(claim.claim_id, SparkEvidence(UNVERIFIABLE, 0.0, "mock", []))
