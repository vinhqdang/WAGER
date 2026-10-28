"""Detectable AUC changes and multiplicity for the quoted secondary results.

(1) For TDE against its baseline, the standard error of each within-cell AUC contrast comes
from the 1,000-replicate image-bootstrap 95% interval ((hi - lo) / 3.92); the change that a
two-sided 5% test detects with 80% power is (1.96 + 0.84) SE.
(2) Six secondary results that the paper quotes are tested by a normal approximation from the
same intervals and adjusted by Holm's step-down procedure. The family is a choice and is
stated; the primary quantities (the graph-constrained mR@50 split and the relation-weighted
AUC for TDE) are not in it.

Run: python experiments/sgg_secondary_adjust.py
"""
import json
import pathlib
from statistics import NormalDist

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "results"
N = NormalDist()
Z95, Z80 = 1.959964, 0.841621


def load(name):
    return json.loads((RES / name).read_text())


def se_from_ci(lo, hi):
    return (hi - lo) / (2 * Z95)


def main():
    lw = load("sgg_auc_label_weighting.json")["auc"]
    fl = load("sgg_cross_release_floor.json")
    pn = load("sgg_penet_audit.json")
    za = load("sgg_zeroshot_auc.json")["by_weighting"]["relation"]["contrasts"]["TDE vs la1"]["zero_shot"]

    power = {}
    for w in ("relation", "comparison", "pair", "predicate"):
        b = lw["TDE vs none"][w]
        se = se_from_ci(*b["ci95"])
        power[w] = {"difference": b["difference"], "se": se, "mde_80_power": (Z95 + Z80) * se,
                    "baseline_auc": b["auc_old"], "geometry_gain": b["reference_gain"]}

    family = [
        ("IETrans AUC change, relation", lw["ietrans vs none"]["relation"]),
        ("TDE unseen-triplet AUC change, relation (post hoc)", {"difference": za["change"], "ci95": za["ci"]}),
        ("baseline against baseline AUC, relation", fl["auc_change"]["dlfe_base vs none"]["relation"]),
        ("TDE AUC change, pair", lw["TDE vs none"]["pair"]),
        ("PE-Net AUC change, relation", pn["auc"]["relation"]),
        ("DLFE AUC change against its baseline, relation", lw["dlfe vs dlfe_base"]["relation"]),
    ]
    rows = []
    for name, b in family:
        d, (lo, hi) = b["difference"], b["ci95"]
        z = d / se_from_ci(lo, hi)
        rows.append({"name": name, "difference": d, "z": z, "p": 2 * (1 - N.cdf(abs(z)))})
    rows.sort(key=lambda r: r["p"])
    m, prev = len(rows), 0.0
    for i, r in enumerate(rows):
        prev = min(1.0, max(prev, (m - i) * r["p"]))
        r["holm_p"] = prev
    out = {"method": "normal approximation from the bootstrap 95% intervals; Holm step-down over the six rows",
           "detectable_change": power, "holm": rows}
    (RES / "sgg_secondary_adjust.json").write_text(json.dumps(out, indent=1))
    for w, p in power.items():
        print(f"{w:10s} SE {p['se']:.5f}  80%-power change {p['mde_80_power']:.4f}")
    for r in rows:
        print(f"{r['name']:55s} d {r['difference']:+.4f} p {r['p']:.4f} Holm {r['holm_p']:.4f}")


if __name__ == "__main__":
    main()
