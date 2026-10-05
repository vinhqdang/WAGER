"""Calibration-free within-cell discrimination.

The case-level part of the split asks whether a model separates relations that
share a subject-object class pair. Its proper-score form still responds to
calibration, so this module gives a rank version that does not: for each cell c
and each pair of labels (y, z) present in it, the relations labelled y should
have a larger log-odds  log q(y) - log q(z)  than the relations labelled z.

    AUC_c(y, z) = P( s_i > s_j ),  s = log q(y) - log q(z),  y_i = y, y_j = z

(ties count one half), averaged over cells and label pairs. Two weightings:

  comparison  weight n_c(y) n_c(z), the number of comparisons. Within a cell this
              is the p(y) p(z) weighting of the pairwise form of the case-level
              part, but across cells it weights a cell by about n_c^2, so the
              largest cells dominate.
  relation    weight n_c(y) n_c(z) / n_c = n_c p(y) p(z): the weighting of the
              case-level part itself, which combines cells in proportion to n_c.

Within a cell a temperature T maps
s to s / T and any change of the predicted prior adds a constant to s, so the
statistic is unchanged by calibration and by every group-level adjustment.

Uncertainty comes from a cluster bootstrap over images; the sort order of each
block is fixed, so a replicate only re-weights a segmented cumulative sum.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class _Blocks:
    """Concatenated (cell, y, z) comparison blocks in sorted score order."""
    elem: np.ndarray        # row index of each element
    pos: np.ndarray         # True if the element is labelled y (positive)
    block: np.ndarray       # block id of each element
    tie: np.ndarray         # tie-group id (same block and score)
    n_blocks: int
    blk_cell: np.ndarray    # cell id of each block
    row_cell: np.ndarray    # cell id of each input row
    n_cells: int


def _blocks(logq: np.ndarray, y: np.ndarray, phi: np.ndarray) -> _Blocks:
    _, inv = np.unique(phi, return_inverse=True)
    order = np.argsort(inv, kind="stable")
    bounds = np.flatnonzero(np.diff(inv[order])) + 1
    elems, poss, blks, scores, bcell = [], [], [], [], []
    b = 0
    for idx in np.split(order, bounds):
        labs, cnt = np.unique(y[idx], return_counts=True)
        cell = inv[idx[0]]
        if len(labs) < 2:
            continue
        for a in range(len(labs)):
            for c in range(a + 1, len(labs)):
                ly, lz = labs[a], labs[c]
                m = idx[(y[idx] == ly) | (y[idx] == lz)]
                s = logq[m, ly] - logq[m, lz]
                elems.append(m)
                poss.append(y[m] == ly)
                blks.append(np.full(len(m), b))
                scores.append(s)
                bcell.append(cell)
                b += 1
    if b == 0:
        raise ValueError("no cell holds two different labels")
    elem, pos = np.concatenate(elems), np.concatenate(poss)
    block, score = np.concatenate(blks), np.concatenate(scores)
    o = np.lexsort((score, block))
    elem, pos, block, score = elem[o], pos[o], block[o], score[o]
    new_tie = np.r_[True, (np.diff(block) != 0) | (np.diff(score) != 0)]
    return _Blocks(elem, pos, block, np.cumsum(new_tie) - 1, b,
                   np.asarray(bcell), inv, int(inv.max()) + 1)


def _auc(bl: _Blocks, w: np.ndarray, weighting: str = "comparison") -> float:
    """Mean within-cell AUC for element weights w (one per row)."""
    we = w[bl.elem]
    wn = np.where(bl.pos, 0.0, we)
    wp = np.where(bl.pos, we, 0.0)
    # negative weight strictly below each element within its block
    cum = np.cumsum(wn)
    tie_neg = np.bincount(bl.tie, wn)
    tie_end = np.cumsum(np.bincount(bl.tie))            # exclusive end per tie
    below_tie = cum[tie_end - 1] - tie_neg               # cum at end of tie - tie
    blk_start = np.r_[0, np.flatnonzero(np.diff(bl.block)) + 1]
    blk_cum0 = np.r_[0.0, cum][blk_start]                # cum before each block
    below = below_tie[bl.tie] - blk_cum0[bl.block]
    num = np.bincount(bl.block, wp * (below + 0.5 * tie_neg[bl.tie]), bl.n_blocks)
    den = np.bincount(bl.block, wp, bl.n_blocks) * np.bincount(bl.block, wn, bl.n_blocks)
    if weighting == "comparison":
        return float(num.sum() / den.sum())
    if weighting != "relation":
        raise ValueError(weighting)
    n_cell = np.bincount(bl.row_cell, w, bl.n_cells)[bl.blk_cell]
    ok = n_cell > 0
    scale = np.where(ok, 1.0 / np.where(ok, n_cell, 1.0), 0.0)
    return float((num * scale).sum() / (den * scale).sum())


@dataclass(frozen=True)
class AUCContrast:
    auc_new: float
    auc_old: float
    difference: float
    ci: tuple[float, float]
    ci_new: tuple[float, float]
    ci_old: tuple[float, float]
    n_blocks: int
    n_boot: int


def within_cell_auc(q: np.ndarray, y: np.ndarray, phi: np.ndarray,
                    eps: float = 1e-12, weighting: str = "comparison") -> float:
    """Within-cell AUC of one model."""
    logq = np.log(np.maximum(np.asarray(q, dtype=np.float64), eps))
    return _auc(_blocks(logq, np.asarray(y), np.asarray(phi)), np.ones(len(y)), weighting)


def within_cell_auc_contrast(q_new, q_old, y, phi, groups, *, n_boot=200,
                             alpha=0.05, seed=0, eps=1e-12, weighting="comparison",
                             weights=None) -> AUCContrast:
    """AUC of each model and their difference, cluster bootstrap over groups."""
    y, phi = np.asarray(y), np.asarray(phi)
    bn = _blocks(np.log(np.maximum(np.asarray(q_new, float), eps)), y, phi)
    bo = _blocks(np.log(np.maximum(np.asarray(q_old, float), eps)), y, phi)
    base = np.ones(len(y)) if weights is None else np.asarray(weights, float)
    a_new, a_old = _auc(bn, base, weighting), _auc(bo, base, weighting)
    _, ginv = np.unique(groups, return_inverse=True)
    n_g = ginv.max() + 1
    rng = np.random.default_rng(seed)
    draws = np.empty((n_boot, 2))
    for r in range(n_boot):
        w = rng.multinomial(n_g, np.full(n_g, 1.0 / n_g)).astype(float)[ginv] * base
        draws[r] = _auc(bn, w, weighting), _auc(bo, w, weighting)
    lo, hi = 100 * alpha / 2, 100 * (1 - alpha / 2)
    d = draws[:, 0] - draws[:, 1]
    return AUCContrast(a_new, a_old, a_new - a_old,
                       tuple(np.percentile(d, [lo, hi])),
                       tuple(np.percentile(draws[:, 0], [lo, hi])),
                       tuple(np.percentile(draws[:, 1], [lo, hi])),
                       bn.n_blocks, n_boot)
