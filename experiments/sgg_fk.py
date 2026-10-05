"""F@K, the harmonic mean of R@K and mR@K (as reported with IETrans), for the audited
PredCls models, from the replayed official-protocol recalls (graph constraint).

Run: python experiments/sgg_fk.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
s = json.loads((ROOT / "data/vg_motifs/wager_sgg/summary.json").read_text())["recalls"]
i = json.loads((ROOT / "data/vg_motifs/wager_ietrans/summary.json").read_text())["official_protocol"]
out = {}
for K in (20, 50, 100):
    rows = {v: (s[v][f"R@{K}"], s[v][f"mR@{K}"]) for v in ("none", "TDE", "la1")}
    if f"standard_test ietrans R@{K}" in i:
        rows["ietrans"] = (i[f"standard_test ietrans R@{K}"], i[f"standard_test ietrans mR@{K}"])
    out[f"F@{K}"] = {v: 2 * r * m / (r + m) for v, (r, m) in rows.items()}
(ROOT / "results/sgg_fk.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
