"""Combine the two evidence channels. Conservative by design: disagreement or low confidence => UNVERIFIABLE."""
from .models import Result, SUPPORTED, CONTRADICTED, UNVERIFIABLE

MIN_CONF = 0.6


def request_text(claim) -> str:
    # Tamil line should be reviewed by a native speaker before the demo.
    ta = "இந்தச் செயலைத் தெளிவாகக் காட்டும் 10 வினாடி வீடியோ எடுத்து அனுப்புங்கள்"
    return f"{ta} / Please send a clear 10-second clip showing: {claim.english}"


def sam_vote(claim, sam):
    """Returns (vote, note). vote in SUPPORTED/CONTRADICTED/None(no opinion)."""
    if sam is None:
        return None, "no SAM evidence"
    if sam.n_tracks == 0:
        return None, f"SAM found no '{claim.noun}' (absence is not proof)"
    if claim.ctype == "count" and claim.count is not None:
        if claim.count in (sam.n_tracks, sam.max_simultaneous):
            return SUPPORTED, f"SAM tracks={sam.n_tracks}, max simultaneous={sam.max_simultaneous}"
        if claim.count > max(sam.n_tracks, sam.max_simultaneous):
            return CONTRADICTED, f"claimed {claim.count} but SAM tracked at most {max(sam.n_tracks, sam.max_simultaneous)}"
        return None, "claimed count below tracks; track fragmentation possible"
    return None, f"SAM saw '{claim.noun}' ({sam.n_tracks} track(s)); presence only"


def verify(claim, spark, sam) -> Result:
    vote, note = sam_vote(claim, sam)
    if spark is None:
        return Result(claim, UNVERIFIABLE, "no Spark evidence", None, sam, request_text(claim))
    if spark.confidence < MIN_CONF:
        verdict, reason = UNVERIFIABLE, f"Spark confidence {spark.confidence:.2f} < {MIN_CONF}"
    elif vote and vote != spark.verdict and spark.verdict in (SUPPORTED, CONTRADICTED):
        verdict, reason = UNVERIFIABLE, f"channels disagree: Spark={spark.verdict}, SAM={vote} ({note})"
    elif spark.verdict == SUPPORTED and sam is not None and sam.n_tracks == 0:
        verdict, reason = UNVERIFIABLE, f"Spark says supported but SAM found no '{claim.noun}'"
    else:
        verdict, reason = spark.verdict, f"Spark: {spark.rationale} | {note}"
    req = request_text(claim) if verdict != SUPPORTED else None
    return Result(claim, verdict, reason, spark, sam, req)
