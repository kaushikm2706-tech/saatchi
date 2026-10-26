from dataclasses import dataclass, field, asdict
from typing import Optional

SUPPORTED, CONTRADICTED, UNVERIFIABLE = "SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"


@dataclass
class Turn:
    turn_id: int
    start_ms: int
    end_ms: int
    transcript: str
    speaker: Optional[str] = None


@dataclass
class Claim:
    claim_id: int
    turn_id: int
    quote: str            # original words (Tamil / English / mixed)
    english: str          # normalised English
    ctype: str            # action | count | order | state | tool
    noun: str             # one short noun phrase for SAM, e.g. "bolt"
    count: Optional[int] = None


@dataclass
class Track:
    object_id: int
    frames: list = field(default_factory=list)   # frame indices
    boxes: dict = field(default_factory=dict)    # frame -> (x1,y1,x2,y2)


@dataclass
class SamEvidence:
    noun: str
    n_tracks: int
    max_simultaneous: int
    intervals_s: list     # [(start_s, end_s)] per track
    fps: float


@dataclass
class SparkEvidence:
    verdict: str          # SUPPORTED | CONTRADICTED | UNVERIFIABLE
    confidence: float
    rationale: str
    timestamps_s: list


@dataclass
class Result:
    claim: Claim
    verdict: str
    reason: str
    spark: Optional[SparkEvidence] = None
    sam: Optional[SamEvidence] = None
    request: Optional[str] = None  # evidence request when not SUPPORTED

    def to_dict(self):
        return asdict(self)
