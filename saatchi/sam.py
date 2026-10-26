"""SAM 3.1 video tracking client + parser.

Documented (dev.meta.ai/docs/sam/segmenting): one line per frame in response.output_text.delta events;
each line starts with a frame marker like <0f>; each object is `<id><|box;x1=..;y1=..;x2=..;y2=..;w=..;h=..|>`
followed by a mask payload. The exact mask payload layout is NOT parsed here (boxes only). [U] until
a real stream is captured: run `python -m saatchi.cli sam-probe` and keep the raw dump it writes.
"""
import json, re
from .config import SAM_MODEL
from .http import post_json
from .models import Track, SamEvidence

FRAME_RE = re.compile(r"<(\d+)f>")
BOX_RE = re.compile(r"(\d+)<\|box;x1=(\d+);y1=(\d+);x2=(\d+);y2=(\d+)(?:;w=\d+;h=\d+)?\|>")


def build_body(noun: str, file_id=None, video_url=None) -> dict:
    vid = {"type": "input_video"}
    if file_id:
        vid["file_id"] = file_id
    else:
        vid["video_url"] = video_url
    return {"model": SAM_MODEL, "stream": True,
            "input": [{"type": "message", "role": "user",
                       "content": [{"type": "input_text", "text": noun}, vid]}]}


def parse_stream_text(text: str) -> dict:
    """text = concatenated deltas. Returns {object_id: Track}. Keyed by frame marker, not line order."""
    tracks = {}
    parts = FRAME_RE.split(text)  # [pre, frame, body, frame, body...]
    for i in range(1, len(parts) - 1, 2):
        frame = int(parts[i])
        for oid, x1, y1, x2, y2 in BOX_RE.findall(parts[i + 1]):
            t = tracks.setdefault(int(oid), Track(int(oid)))
            t.frames.append(frame)
            t.boxes[frame] = (int(x1), int(y1), int(x2), int(y2))
    return tracks


def collect_deltas(lines) -> str:
    """lines: iterable of SSE text lines. Joins response.output_text.delta payloads."""
    out, event = [], None
    for raw in lines:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "replace")
        raw = raw.rstrip("\r\n")
        if raw.startswith("event:"):
            event = raw[6:].strip()
        elif raw.startswith("data:"):
            data = raw[5:].strip()
            if data == "[DONE]":
                continue
            try:
                obj = json.loads(data)
            except ValueError:
                continue
            if (event or obj.get("type")) == "response.output_text.delta":
                out.append(obj.get("delta", ""))
    return "".join(out)


def to_evidence(noun, tracks: dict, fps: float, gap_frames=None) -> SamEvidence:
    gap = gap_frames or int(fps)  # a gap >1s splits an appearance interval
    intervals, per_frame = [], {}
    for t in tracks.values():
        fr = sorted(t.frames)
        for f in fr:
            per_frame[f] = per_frame.get(f, 0) + 1
        s = p = fr[0]
        for f in fr[1:]:
            if f - p > gap:
                intervals.append((s / fps, p / fps)); s = f
            p = f
        intervals.append((s / fps, p / fps))
    return SamEvidence(noun, len(tracks), max(per_frame.values(), default=0), sorted(intervals), fps)


def track(noun: str, file_id: str, fps: float, dump_path=None) -> SamEvidence:
    r = post_json("/responses", build_body(noun, file_id=file_id), stream=True, accept="text/event-stream")
    r.raise_for_status()
    text = collect_deltas(r.iter_lines())
    if dump_path:
        open(dump_path, "w").write(text)  # raw dump, to verify the format on first live run
    return to_evidence(noun, parse_stream_text(text), fps)


class MockSam:
    """Deterministic stand-in: maps noun -> SamEvidence."""
    def __init__(self, table):
        self.table = table

    def __call__(self, noun, file_id=None, fps=15.0, dump_path=None):
        return self.table.get(noun, SamEvidence(noun, 0, 0, [], fps))
