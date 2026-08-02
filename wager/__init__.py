"""WAGER: Within-cell Antisymmetric Gain Evaluation of Reasoning.

The current public API is implemented in :mod:`wager.antisymmetric`.  The older
``core``, ``pipeline``, and ``rgr`` modules are retained only to reproduce the
desk-rejected projection/betting formulation and should not be used for new work.
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
