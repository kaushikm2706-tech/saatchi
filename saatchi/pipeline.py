from . import ingest, voice, spark, sam, verifier


class Backends:
    """Swap real/mocked clients. Real ones need MODEL_API_KEY."""
    def __init__(self, transcribe, spark_mod, sam_track, upload):
        self.transcribe, self.spark, self.sam_track, self.upload = transcribe, spark_mod, sam_track, upload


def live_backends():
    from .http import upload_file
    return Backends(voice.transcribe, spark, sam.track, upload_file)


def run(video: str, work: str, b: Backends, sam_fps=15, window_pad_s=2.0):
    import os
    os.makedirs(work, exist_ok=True)
    wav = ingest.extract_wav(video, f"{work}/audio.wav")
    sam_mp4 = ingest.make_sam_copy(video, f"{work}/sam.mp4", sam_fps)
    dur = ingest.duration_s(video)
    turns = b.transcribe(wav)
    claims = b.spark.extract_claims(turns)
    spark_id, sam_id = b.upload(video), b.upload(sam_mp4)
    by_turn = {t.turn_id: t for t in turns}
    sam_cache, results = {}, []
    for c in claims:
        t = by_turn.get(c.turn_id)
        t0 = max(0.0, (t.start_ms / 1000 if t else 0) - window_pad_s)
        t1 = min(dur, (t.end_ms / 1000 if t else dur) + window_pad_s)
        sp = b.spark.verify_claim(c, spark_id, t0, t1)
        if c.noun not in sam_cache:  # one SAM request per noun phrase, reused across claims
            sam_cache[c.noun] = b.sam_track(c.noun, sam_id, float(sam_fps), f"{work}/sam_{len(sam_cache)}.raw.txt")
        results.append(verifier.verify(c, sp, sam_cache[c.noun]))
    return results
