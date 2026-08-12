# P1.1 execution plan — PredCls softmax from released SGG checkpoints (Colab T4)

> Research report, 2026-08-10. Feasibility 7/10: hours per model once running; budget ~1 debugging day for the torch-2 shim. All URLs were opened/verified by the researcher.

## Winning route: KaihuaTang/Scene-Graph-Benchmark.pytorch + third-party checkpoints, inference-only "no-compile" patch

- The eval already dumps what WAGER needs: with `OUTPUT_DIR` set, `vg_eval.py::save_output()` writes `eval_results.pytorch` with per-image `rel_pair_idxs` (GT-box indices, PredCls scores every ordered GT pair) and `pred_rel_scores` (**#rels × 51 softmax**, `F.softmax` in `relation_head/inference.py:102`). `result_dict.pytorch` (R@50/mR@50) saved alongside. No interception needed.
- **Models** (published, biased/debiased contrasts):
  1. **MOTIFS-SUM baseline + MOTIFS-TDE from ONE checkpoint** — `upload_causal_motif_predcls.zip`, 1.99 GB, OneDrive link in Kaihua README §Pretrained Models; run twice with `CAUSAL.EFFECT_TYPE none` vs `TDE`. Minimum viable pair (CVPR 2020).
  2. **Motifs + IETrans** — `vg50-predcls-I0.9E1.0-model_0030000.pth`, Google Drive (gdown-able), IETrans MODEL_ZOO; plain MotifPredictor; their fork keeps the same eval dump.
  3. **SQUAT** (CVPR 2023) — Google Drive folder `1_S90m0TIZxOD8qjyJtfnhn1AHiAW0Y-N`; R@50 55.67/mR@50 30.87.
  4. (optional) SHA-GCL (CVPR 2022) — OneDrive, unverified link.
  - Dead ends checked: RTPB (empty ckpt cells), PENET official (stub repo), precomputed prediction files (none public anywhere), Maelic/SGG-Benchmark (modern & clean but NO released PredCls weights, no CausalAnalysisPredictor).

## USER ACTION REQUIRED (browser-only OneDrive, ~4 GB, one time)
1. `upload_causal_motif_predcls.zip` (1.99 GB) — link in https://github.com/KaihuaTang/Scene-Graph-Benchmark.pytorch README, "Pretrained Models".
2. `VG-SGG-with-attri.h5` + dicts + `image_data.json` (~2 GB) — "scene graphs" link in DATASET.md.
Put both in Google Drive (assistant mounts Drive in Colab from there). Anonymous OneDrive API tricks verified dead (401/403).

## No-compile patch (each maps to a guaranteed failure otherwise)
(a) replace `layers/nms.py` + `layers/roi_align.py` bodies with `torchvision.ops.nms` / `roi_align(aligned=False)` (bit-identical); (b) drop roi_pool/SigmoidFocalLoss/dcn imports from `layers/__init__.py`; (c) `utils/imports.py`: `torch._six.PY3` → `True`; (d) `visual_genome.py:223/226`: `np.float`→`float`, `np.bool`→`bool`; (e) stub `apex.amp` package (`init` no-op), run `DTYPE float32`; (f) PYTHONPATH the repo, never run setup.py. Install: `pip install yacs ninja cython matplotlib tqdm opencv-python overrides h5py "numpy<2"`. GloVe (~1 GB) auto-downloads.

## Data (~35-40 GB peak, fits Colab disk)
VG images direct from Stanford: `VG_100K_2/images.zip` (9 GB) + `images2.zip` (5 GB) → `datasets/vg/VG_100K`; h5/dicts from Drive; edit `config/paths_catalog.py`.

## Run command pattern (per model)
```
python tools/relation_test_net.py --config-file configs/e2e_relation_X_101_32_8_FPN_1x.yaml \
  MODEL.ROI_RELATION_HEAD.USE_GT_BOX True MODEL.ROI_RELATION_HEAD.USE_GT_OBJECT_LABEL True \
  MODEL.ROI_RELATION_HEAD.PREDICTOR CausalAnalysisPredictor \
  MODEL.ROI_RELATION_HEAD.CAUSAL.EFFECT_TYPE none|TDE \
  MODEL.ROI_RELATION_HEAD.CAUSAL.FUSION_TYPE sum MODEL.ROI_RELATION_HEAD.CAUSAL.CONTEXT_LAYER motifs \
  TEST.IMS_PER_BATCH 1 DTYPE "float32" GLOVE_DIR /content/glove \
  MODEL.PRETRAINED_DETECTOR_CKPT <ckpt_dir> OUTPUT_DIR <ckpt_dir>
```
Gotcha #1: fix `last_checkpoint` file inside the unzipped ckpt dir to the local path. IETrans: their fork, `PREDICTOR MotifPredictor`, `PREDICT_USE_BIAS True`, `configs/sup-50.yaml`. SQUAT: their `scripts/test.sh`.

## Harvest & alignment
`groundtruths[i].get_field('relation_tuple')` = (sub_idx, obj_idx, gt_pred); match rows of `rel_pair_idxs` → 51-dim `pred_rel_scores` row. Dataset order = test-split order of `VG-SGG-with-attri.h5`; image ids via `image_data.json`; BoxList boxes are GT boxes in the RESIZED frame — `.resize(original_size)` or match by index order against `data/vg/vg_predcls.npz` (image + sbox/obox).

## Runtime & sanity checks
~2-3.5 h/model on T4 over 26,446 test images (batch 1). Sanity: MOTIFS-SUM-none R@50 ≈ 65; TDE mR@50 ≈ 25-26. `eval_results.pytorch` ≈ 0.3-1 GB per model.

## Fallback
(1) condacolab: py3.9 + pytorch 1.10 + cudatoolkit 11.3 wheels (T4 = sm_75 supported), build `_C` the SQUAT-era way (~45-60 min, historically reliable). (2) If only some models run: MOTIFS ± TDE alone is publishable minimum. (3) Last resort: train Motifs in Maelic's rewrite (days; weights then not "released checkpoints").
