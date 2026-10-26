import html
from .models import SUPPORTED

COLORS = {"SUPPORTED": "#1a7f37", "CONTRADICTED": "#cf222e", "UNVERIFIABLE": "#9a6700"}


def render(results, title="Saatchi verified work report") -> str:
    n = len(results)
    ok = sum(r.verdict == SUPPORTED for r in results)
    rows = []
    for r in results:
        e = html.escape
        ts = ", ".join(f"{t:.1f}s" for t in (r.spark.timestamps_s if r.spark else []))
        rows.append(
            f"<tr><td>{r.claim.claim_id}</td><td lang='ta'>{e(r.claim.quote)}<br><small>{e(r.claim.english)}</small></td>"
            f"<td style='color:{COLORS[r.verdict]};font-weight:600'>{r.verdict}</td>"
            f"<td>{e(r.reason)}<br><small>{e(ts)}</small></td><td>{e(r.request or '')}</td></tr>")
    return f"""<!doctype html><meta charset=utf-8><title>{html.escape(title)}</title>
<style>body{{font:15px system-ui;margin:2rem auto;max-width:1000px;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:.5rem;vertical-align:top}}</style>
<h1>{html.escape(title)}</h1><p>{ok} of {n} claims supported by video evidence. Unsupported claims are never silently accepted.</p>
<table><tr><th>#</th><th>Claim / உரை</th><th>Verdict</th><th>Evidence</th><th>Evidence request</th></tr>
{''.join(rows)}</table>"""
