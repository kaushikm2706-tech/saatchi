"""Tiny local web UI (stdlib only). Browser posts the raw video bytes; server runs the pipeline and returns the report."""
import json, os, re, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import pipeline, report

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Saatchi</title><style>body{font:16px system-ui;max-width:760px;margin:3rem auto;padding:0 1rem}
button{font-size:1rem;padding:.6rem 1.2rem}#out{margin-top:2rem}</style>
<h1>Saatchi <small lang=ta>சாட்சி</small></h1>
<p>Upload a narrated work video (MP4, Tamil or English). Each spoken claim is checked against what the video shows.</p>
<input type=file id=f accept="video/mp4"> <button id=b>Verify</button><div id=out></div>
<script>
b.onclick=async()=>{const file=f.files[0];if(!file){out.textContent='Choose an MP4 first.';return}
out.textContent='Working... this can take a few minutes (real API calls).';
const r=await fetch('/verify',{method:'POST',headers:{'X-Filename':encodeURIComponent(file.name)},body:file});
out.innerHTML=r.ok?await r.text():'Error: '+await r.text()}
</script>"""


def make_handler(backends, work_root="work", **run_kw):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="text/html; charset=utf-8"):
            data = body.encode("utf-8")
            self.send_response(code); self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

        def do_GET(self):
            self._send(200, PAGE) if self.path == "/" else self._send(404, "not found", "text/plain")

        def do_POST(self):
            if self.path != "/verify":
                return self._send(404, "not found", "text/plain")
            try:
                n = int(self.headers.get("Content-Length", 0))
                if n <= 0 or n > 1_000_000_000:
                    return self._send(400, "empty or too large (limit 1 GB)", "text/plain")
                name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(self.headers.get("X-Filename", "clip.mp4")))[:80] or "clip.mp4"
                job = os.path.join(work_root, f"{int(time.time())}_{name}")
                os.makedirs(job, exist_ok=True)
                path = os.path.join(job, "input.mp4")
                remaining = n
                with open(path, "wb") as f:
                    while remaining:
                        chunk = self.rfile.read(min(1 << 20, remaining))
                        if not chunk:
                            break
                        f.write(chunk); remaining -= len(chunk)
                res = pipeline.run(path, job, backends, **run_kw)
                json.dump([r.to_dict() for r in res], open(os.path.join(job, "results.json"), "w", encoding="utf-8"),
                          ensure_ascii=False, indent=1)
                self._send(200, report.render(res))
            except Exception as e:  # show the real error to the developer
                self._send(500, f"{type(e).__name__}: {e}", "text/plain; charset=utf-8")
    return H


def serve(backends, port=8000, **kw):
    print(f"Saatchi UI on http://127.0.0.1:{port}  (real API calls, billed to your credits)")
    ThreadingHTTPServer(("127.0.0.1", port), make_handler(backends, **kw)).serve_forever()
