"""WAGER: Wealth-Anchored Gain Estimation of Reasoning.

A distribution-free, anytime-valid framework for attributing computer-vision
benchmark gains to genuine visual reasoning vs. annotation-frequency priors.

Reference: algorithm.md (Đặng Quang Vinh), target venue WACV 2027 E&D track.
"""

from .core import (
    kt_projection,
    prior_excess_logscore,
    wealth_process,
    betting_mean_ci,
    betting_mean_point,
    OnsBettor,
)
from .pipeline import (
    WagerResult,
    ModelData,
    build_projection,
    run_wager_single,
    run_wager_permutations,
    run_wager_eval,
)
from .rgr import reasoning_gain_ratio, fieller_ratio_ci, RgrResult

__version__ = "0.1.0"

__all__ = [
    "kt_projection",
    "prior_excess_logscore",
    "wealth_process",
    "betting_mean_ci",
    "betting_mean_point",
    "OnsBettor",
    "WagerResult",
    "ModelData",
    "build_projection",
    "run_wager_single",
    "run_wager_permutations",
    "run_wager_eval",
    "reasoning_gain_ratio",
    "fieller_ratio_ci",
    "RgrResult",
]
