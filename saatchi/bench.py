"""Saatchi-Bench: offline scoring of recorded pipeline outputs against human labels.

Labels file (JSON): [{"clip":"c01_truthful","claims":[{"match":"4 bolts","gold":"SUPPORTED"}, ...]}, ...]
  - "match": case-insensitive substring of the extracted claim's English text OR original quote.
  - "gold": SUPPORTED (the video shows it) or CONTRADICTED (the video shows otherwise).
Results: one JSON per clip written by `saatchi run` (<report>.json), named <clip>.json in one folder.
Ablation: "spark_only" re-runs the verifier with SAM evidence removed (no extra API calls).
"""
import json, random
from pathlib import Path
from .models import result_from_dict, SUPPORTED, CONTRADICTED, UNVERIFIABLE
from . import verifier

LABELS = (SUPPORTED, CONTRADICTED)
PREDS = (SUPPORTED, CONTRADICTED, UNVERIFIABLE)


def match_claims(labels, results):
    """Pair gold labels with extracted results. Returns (pairs, n_missed_gold)."""
    pairs, missed, used = [], 0, set()
    for g in labels:
        key = g["match"].lower()
        hit = next((i for i, r in enumerate(results) if i not in used and
                    (key in r.claim.english.lower() or key in r.claim.quote.lower())), None)
        if hit is None:
            missed += 1
        else:
            used.add(hit)
            pairs.append((g["gold"], results[hit]))
    return pairs, missed


def load(results_dir, labels_path):
    labels = json.load(open(labels_path, encoding="utf-8"))
    out, missed = [], 0
    for item in labels:
        f = Path(results_dir) / f"{item['clip']}.json"
        if not f.exists():
            missed += len(item["claims"]); continue
        res = [result_from_dict(d) for d in json.load(open(f, encoding="utf-8"))]
        pr, ms = match_claims(item["claims"], res)
        out += [(g, r) for g, r in pr]; missed += ms
    return out, missed


def spark_only(result):
    return verifier.verify(result.claim, result.spark, None).verdict


def confusion(golds, preds):
    m = {g: {p: 0 for p in PREDS} for g in LABELS}
    for g, p in zip(golds, preds):
        m[g][p] += 1
    return m


def stats(golds, preds):
    """Safety-first metrics. 'false confirmation' = gold CONTRADICTED but predicted SUPPORTED."""
    n = len(golds)
    answered = [(g, p) for g, p in zip(golds, preds) if p != UNVERIFIABLE]
    correct = sum(g == p for g, p in answered)
    contra = [p for g, p in zip(golds, preds) if g == CONTRADICTED]
    return {
        "n": n,
        "coverage": len(answered) / n if n else float("nan"),
        "accuracy_on_answered": correct / len(answered) if answered else float("nan"),
        "false_confirmation_rate": (sum(p == SUPPORTED for p in contra) / len(contra)) if contra else float("nan"),
    }


def bootstrap(golds, preds, key, iters=2000, seed=0):
    rng = random.Random(seed)
    n, vals = len(golds), []
    for _ in range(iters):
        idx = [rng.randrange(n) for _ in range(n)]
        v = stats([golds[i] for i in idx], [preds[i] for i in idx])[key]
        if v == v:  # drop NaN
            vals.append(v)
    if not vals:
        return (float("nan"), float("nan"))
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))]


def evaluate(pairs, iters=2000):
    golds = [g for g, _ in pairs]
    systems = {"spark_only": [spark_only(r) for _, r in pairs], "spark_plus_sam": [r.verdict for _, r in pairs]}
    out = {}
    for name, preds in systems.items():
        s = stats(golds, preds)
        s["confusion"] = confusion(golds, preds)
        s["ci95"] = {k: bootstrap(golds, preds, k, iters) for k in
                     ("coverage", "accuracy_on_answered", "false_confirmation_rate")}
        out[name] = s
    return out


def format_report(ev, missed, n_pairs) -> str:
    lines = [f"Saatchi-Bench: {n_pairs} labelled claims scored, {missed} gold claims not matched (extraction misses).",
             "Small-sample warning: wide intervals are expected; do not over-read differences.", ""]
    for name, s in ev.items():
        lines.append(f"[{name}] n={s['n']}")
        for k in ("coverage", "accuracy_on_answered", "false_confirmation_rate"):
            lo, hi = s["ci95"][k]
            lines.append(f"  {k}: {s[k]:.3f}  (95% bootstrap CI {lo:.3f}-{hi:.3f})")
        lines.append("  confusion (rows=gold, cols=pred S/C/U): " +
                     "; ".join(f"{g[:1]}: " + "/".join(str(s['confusion'][g][p]) for p in PREDS) for g in LABELS))
        lines.append("")
    return "\n".join(lines)
