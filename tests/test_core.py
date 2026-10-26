import json, subprocess
from saatchi import sam, voice, spark, verifier, report, pipeline
from saatchi.models import *


def test_sam_parse_by_frame_marker_not_order():
    text = ("<1f>0<|box;x1=10;y1=20;x2=30;y2=40;w=320;h=334|>MASK,1<|box;x1=50;y1=60;x2=70;y2=80;w=320;h=334|>MASK"
            "\n<0f>0<|box;x1=11;y1=21;x2=31;y2=41;w=320;h=334|>MASK")
    t = sam.parse_stream_text(text)
    assert sorted(t) == [0, 1]
    assert t[0].boxes[0] == (11, 21, 31, 41) and t[0].boxes[1] == (10, 20, 30, 40)
    assert t[1].frames == [1]


def test_sam_zero_matches_is_not_error():
    ev = sam.to_evidence("bolt", sam.parse_stream_text("<0f>\n<1f>"), 15.0)
    assert ev.n_tracks == 0 and ev.max_simultaneous == 0


def test_sam_intervals_split_on_gap():
    text = "".join(f"<{f}f>0<|box;x1=1;y1=1;x2=2;y2=2|>" for f in [0, 1, 2, 60, 61])
    ev = sam.to_evidence("x", sam.parse_stream_text(text), 15.0)
    assert ev.intervals_s == [(0.0, 2 / 15), (4.0, 61 / 15)]


def test_collect_deltas():
    lines = ["event: response.output_text.delta", 'data: {"type":"response.output_text.delta","delta":"<0f>"}', "",
             "event: response.completed", 'data: {"type":"response.completed"}']
    assert sam.collect_deltas(lines) == "<0f>"


def test_voice_request_shape():
    r = voice.build_request()
    assert r["mode"] == "DIARIZATION" and r["audioEncoding"] == "WAV" and r["languageBias"] == ["Tamil", "English"]
    turns = voice.parse_turns({"turns": [{"turnId": 0, "startMs": 0, "endMs": 900, "transcript": "x", "speaker": "A"}]})
    assert turns[0].speaker == "A"


def test_spark_extract_text_and_json():
    assert spark.extract_text({"output": [{"content": [{"type": "output_text", "text": "hi"}]}]}) == "hi"
    assert spark.parse_json('sure ```{"a": 1}```') == {"a": 1}


def C(ctype="count", count=4):
    return Claim(0, 0, "q", "I fitted 4 bolts", ctype, "bolt", count)


def sp(v, c=0.9):
    return SparkEvidence(v, c, "r", [1.0])


def ev(n, m):
    return SamEvidence("bolt", n, m, [], 15.0)


def test_verifier_agree_supports():
    assert verifier.verify(C(), sp(SUPPORTED), ev(4, 4)).verdict == SUPPORTED


def test_verifier_disagree_abstains():
    r = verifier.verify(C(count=6), sp(SUPPORTED), ev(4, 4))
    assert r.verdict == UNVERIFIABLE and "disagree" in r.reason and r.request


def test_verifier_low_confidence_abstains():
    assert verifier.verify(C(), sp(SUPPORTED, 0.3), ev(4, 4)).verdict == UNVERIFIABLE


def test_verifier_sam_absent_blocks_support():
    assert verifier.verify(C("action", None), sp(SUPPORTED), ev(0, 0)).verdict == UNVERIFIABLE


def test_verifier_contradiction_kept_when_sam_agrees():
    assert verifier.verify(C(count=9), sp(CONTRADICTED), ev(4, 4)).verdict == CONTRADICTED


def test_report_escapes_html():
    c = Claim(0, 0, "<script>", "e", "action", "n")
    out = report.render([verifier.verify(c, sp(SUPPORTED), ev(1, 1))])
    assert "<script>" not in out and "&lt;script&gt;" in out


def test_pipeline_with_mocks(tmp_path):
    video = str(tmp_path / "v.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=3:size=160x120:rate=15",
                    "-f", "lavfi", "-i", "sine=duration=3", "-shortest", "-pix_fmt", "yuv420p", video],
                   check=True, capture_output=True)
    turns = [Turn(0, 0, 2000, "naan 4 bolt fit pannen", "A")]
    claims = [Claim(0, 0, "naan 4 bolt fit pannen", "I fitted 4 bolts", "count", "bolt", 4)]
    mspark = spark.MockSpark(claims, {0: sp(SUPPORTED)})
    b = pipeline.Backends(voice.MockVoice(turns), mspark,
                          sam.MockSam({"bolt": ev(4, 4)}), lambda p: "file-1")
    res = pipeline.run(video, str(tmp_path / "w"), b)
    assert [r.verdict for r in res] == [SUPPORTED]
