import json
from saatchi import bench, cli
from saatchi.models import *


def mk(i, english, gold_v, spark_v, conf, sam):
    c = Claim(i, 0, english, english, "count", "bolt", 4)
    from saatchi import verifier
    return verifier.verify(c, SparkEvidence(spark_v, conf, "r", []), sam)


def test_metrics_and_ablation(tmp_path):
    sam4 = SamEvidence("bolt", 4, 4, [], 15.0)
    # falsified narration: Spark wrongly says SUPPORTED, SAM (4 tracks) vs claim 4... use count mismatch via claim count 6
    c_false = Claim(1, 0, "I fitted 6 bolts", "I fitted 6 bolts", "count", "bolt", 6)
    from saatchi import verifier
    r_true = verifier.verify(Claim(0, 0, "4 bolts", "I fitted 4 bolts", "count", "bolt", 4),
                             SparkEvidence(SUPPORTED, .9, "r", []), sam4)
    r_false = verifier.verify(c_false, SparkEvidence(SUPPORTED, .9, "r", []), sam4)
    pairs = [(SUPPORTED, r_true), (CONTRADICTED, r_false)]
    ev = bench.evaluate(pairs, iters=50)
    assert ev["spark_only"]["false_confirmation_rate"] == 1.0   # Spark alone confirmed the lie
    assert ev["spark_plus_sam"]["false_confirmation_rate"] == 0.0  # two channels abstained
    assert ev["spark_plus_sam"]["coverage"] == 0.5
    assert "Small-sample" in bench.format_report(ev, 0, 2)


def test_load_and_match(tmp_path):
    sam4 = SamEvidence("bolt", 4, 4, [], 15.0)
    r = mk(0, "I fitted 4 bolts", SUPPORTED, SUPPORTED, .9, sam4)
    (tmp_path / "c1.json").write_text(json.dumps([r.to_dict()]))
    lab = tmp_path / "l.json"
    lab.write_text(json.dumps([{"clip": "c1", "claims": [{"match": "4 BOLTS", "gold": "SUPPORTED"},
                                                         {"match": "painted", "gold": "CONTRADICTED"}]},
                               {"clip": "missing", "claims": [{"match": "x", "gold": "SUPPORTED"}]}]))
    pairs, missed = bench.load(str(tmp_path), str(lab))
    assert len(pairs) == 1 and missed == 2
    cli.main(["bench", str(tmp_path), str(lab)])
