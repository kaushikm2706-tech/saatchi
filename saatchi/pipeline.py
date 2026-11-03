from . import ingest, voice, spark, sam, verifier


class Backends:
    """Swap real/mocked clients. Real ones need MODEL_API_KEY."""
    def __init__(self, transcribe, spark_mod, sam_track, upload):
        self.transcribe, self.spark, self.sam_track, self.upload = transcribe, spark_mod, sam_track, upload


def live_backends():
    from .apiclient import upload_file
    return Backends(voice.transcribe, spark, sam.track, upload_file)


def run(video: str, work: str, b: Backends, sam_fps=15, window_pad_s=2.0, use_sam=True):
    import os
    os.makedirs(work, exist_ok=True)
    wav = ingest.extract_wav(video, f"{work}/audio.wav")
    sam_mp4 = ingest.make_sam_copy(video, f"{work}/sam.mp4", sam_fps)
    dur = ingest.duration_s(video)
    turns = b.transcribe(wav)
    claims = b.spark.extract_claims(turns)
    spark_id = b.upload(video)
    sam_id = b.upload(sam_mp4) if use_sam else None
    by_turn = {t.turn_id: t for t in turns}
    sam_cache, results = {}, []
    for c in claims:
        t = by_turn.get(c.turn_id)
        t0 = max(0.0, (t.start_ms / 1000 if t else 0) - window_pad_s)
        t1 = min(dur, (t.end_ms / 1000 if t else dur) + window_pad_s)
        sp = b.spark.verify_claim(c, spark_id, t0, t1)
        sm = None
        if use_sam:
            if c.noun not in sam_cache:  # one SAM request per noun phrase, reused across claims
                sam_cache[c.noun] = b.sam_track(c.noun, sam_id, float(sam_fps), f"{work}/sam_{len(sam_cache)}.raw.txt")
            sm = sam_cache[c.noun]
        results.append(verifier.verify(c, sp, sm))
    return results


def recheck(result, extra_video: str, work: str, b: Backends, sam_fps=15):
    """Active loop: the user sent the clip we asked for; re-verify one claim against it."""
    import os
    os.makedirs(work, exist_ok=True)
    dur = ingest.duration_s(extra_video)
    sp = b.spark.verify_claim(result.claim, b.upload(extra_video), 0.0, dur)
    sam_mp4 = ingest.make_sam_copy(extra_video, f"{work}/recheck_sam.mp4", sam_fps)
    sm = b.sam_track(result.claim.noun, b.upload(sam_mp4), float(sam_fps), f"{work}/recheck.raw.txt")
    return verifier.verify(result.claim, sp, sm)
