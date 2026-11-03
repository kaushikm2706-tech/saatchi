import argparse, json, sys
from . import pipeline, report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="saatchi")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="verify a narrated video (needs MODEL_API_KEY; real API calls cost credits)")
    r.add_argument("video"); r.add_argument("--work", default="work"); r.add_argument("--out", default="report.html")
    r.add_argument("--live", action="store_true", help="required: confirm you want real, billed API calls")
    pr = sub.add_parser("sam-probe", help="one SAM call; saves the raw stream so we can confirm the output format")
    pr.add_argument("video"); pr.add_argument("noun"); pr.add_argument("--live", action="store_true")
    sv = sub.add_parser("serve", help="local web UI (real API calls)")
    sv.add_argument("--live", action="store_true"); sv.add_argument("--port", type=int, default=8000)
    mx = sub.add_parser("mux", help="put a recorded narration (wav/m4a/mp3) onto a video: mux video narration out.mp4")
    mx.add_argument("video"); mx.add_argument("narration"); mx.add_argument("out")
    bn = sub.add_parser("bench", help="score recorded results against labels (offline, no API calls)")
    bn.add_argument("results_dir"); bn.add_argument("labels")
    a = ap.parse_args(argv)
    if a.cmd == "mux":
        from . import ingest
        print(ingest.mux_narration(a.video, a.narration, a.out))
        return
    if a.cmd == "serve":
        if not a.live:
            sys.exit("Refusing to start a server that makes billed API calls without --live.")
        from . import web
        return web.serve(pipeline.live_backends(), a.port)
    if a.cmd == "bench":
        from . import bench
        pairs, missed = bench.load(a.results_dir, a.labels)
        print(bench.format_report(bench.evaluate(pairs), missed, len(pairs)))
        return
    if a.cmd == "sam-probe":
        if not a.live:
            sys.exit("Refusing to call the API without --live.")
        from . import sam
        from .apiclient import upload_file
        ev = sam.track(a.noun, upload_file(a.video), 15.0, dump_path="sam_probe.raw.txt")
        print(ev); print("raw stream saved to sam_probe.raw.txt (check it matches the parser; paste the first 600 chars to Claude)")
        return
    if a.cmd == "run":
        if not a.live:
            sys.exit("Refusing to call the API without --live. Mocked runs live in tests/ and bench/.")
        res = pipeline.run(a.video, a.work, pipeline.live_backends())
        open(a.out, "w", encoding="utf-8").write(report.render(res))
        json.dump([x.to_dict() for x in res], open(a.out + ".json", "w"), ensure_ascii=False, indent=1)
        print(f"wrote {a.out} and {a.out}.json  (for the benchmark, copy the .json to results/<clip>.json)")


if __name__ == "__main__":
    main()
