"""Run the full WAGER experiment suite end-to-end: SGG, Phase-1, ablations,
figures, and report generation. Each stage is guarded so a later-stage failure
does not lose earlier results."""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def stage(name, fn):
    print(f"\n{'='*70}\n## {name}\n{'='*70}", flush=True)
    try:
        fn()
        print(f"[OK] {name}", flush=True)
    except Exception:
        print(f"[FAIL] {name}", flush=True)
        traceback.print_exc()


def main():
    import numpy as np
    np.seterr(all="ignore")

    from experiments.run_sgg_wager import main as sgg_main
    from experiments.phase1_simulation import main as phase1_main
    from experiments import make_figures, gen_report

    stage("Phase 2 - SGG (Visual Genome PredCls)", sgg_main)
    stage("Phase 1 - validity & power simulations", phase1_main)

    def ablate():
        from experiments.ablations import main as abl_main
        abl_main()
    stage("Phase 5 - ablations", ablate)

    stage("Figures", lambda: (make_figures.fig_phase1(), make_figures.fig_sgg()))
    stage("Report", gen_report.main)


if __name__ == "__main__":
    main()
