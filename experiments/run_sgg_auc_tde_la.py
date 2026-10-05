"""Relation-weighted and comparison-weighted AUC change of TDE against the logit-adjusted
control (the TDE-LA row of Table 1), as in run_sgg_rank_robustness.py.

Run: python experiments/run_sgg_auc_tde_la.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import run_sgg_rank_robustness as RR  # noqa: E402

if __name__ == "__main__":
    Q, raw, y, phi, image, cal = RR.sgg_data()
    rows = RR.auc_rows(raw, [("TDE", "la1")], y, phi, image, ~cal)
    (ROOT / "results/sgg_auc_tde_la.json").write_text(json.dumps({"rows": rows}, indent=1))
