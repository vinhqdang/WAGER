"""WAGER: Within-cell Antisymmetric Gain Evaluation of Resolution.

Attributes the proper-score difference between two frozen probabilistic models
into a prior-transported component and an instance-alignment residual, using
within-cell label transport. The public API is :func:`decompose_gain`; see
``algorithm.md`` for the mathematics and ``README.md`` for usage.
"""

from .antisymmetric import (
    GainDecomposition,
    cyclic_randomization_test,
    decompose_gain,
    gain_matrix,
    score_matrix,
)

__all__ = [
    "GainDecomposition",
    "cyclic_randomization_test",
    "decompose_gain",
    "gain_matrix",
    "score_matrix",
]
