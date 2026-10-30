import threading, urllib.request, subprocess
from http.server import ThreadingHTTPServer
from saatchi import web, pipeline, voice, spark, sam
from saatchi.models import *


def test_web_roundtrip(tmp_path):
    video = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=2:size=160x120:rate=15",
                    "-f", "lavfi", "-i", "sine=duration=2", "-shortest", "-pix_fmt", "yuv420p", str(video)],
                   check=True, capture_output=True)
    claims = [Claim(0, 0, "q", "I fitted 4 bolts", "count", "bolt", 4)]
    b = pipeline.Backends(voice.MockVoice([Turn(0, 0, 1500, "x")]),
                          spark.MockSpark(claims, {0: SparkEvidence(SUPPORTED, .9, "ok", [1.0])}),
                          sam.MockSam({"bolt": SamEvidence("bolt", 4, 4, [], 15.0)}), lambda p: "file-1")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), web.make_handler(b, str(tmp_path / "jobs")))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_port}"
    assert b"Saatchi" in urllib.request.urlopen(base + "/").read()
    req = urllib.request.Request(base + "/verify", data=video.read_bytes(), method="POST",
                                 headers={"X-Filename": "../../evil name.mp4"})
    html = urllib.request.urlopen(req).read().decode()
    srv.shutdown()
    assert "SUPPORTED" in html and "1 of 1" in html
    assert not (tmp_path.parent / "evil name.mp4").exists()
