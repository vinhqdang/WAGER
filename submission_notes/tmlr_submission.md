# TMLR submission checklist

Submission goes through OpenReview. TMLR has no cover letter, no highlights, no title
page and no author-declaration uploads, so most of the Pattern Recognition deliverable
set is not used; those files stay in the repository unchanged in case the paper moves
again.

## What to upload

| Item | File | Notes |
|---|---|---|
| Paper (PDF) | `manuscript/main.pdf` | 42 pages: 17 body and references, 25 appendices |
| Supplementary material | `code.zip` | 58 files, 128 KB, anonymized, tests pass inside the archive |
| LaTeX source, if asked | `submission/` (`build_flat_submission.py --zip`) | renders identically to the modular build |

## OpenReview form

- **Title.** WAGER: An Exact Decomposition of Model-Pair Score Gains on Benchmarks with
  Strong Label Priors
- **Abstract.** 241 words, one paragraph, as it appears on page 1.
- **Authors.** Enter the real author in OpenReview; the PDF itself must stay anonymous,
  and it is — `tmlr.sty` prints "Anonymous authors / Paper under double-blind review"
  unless the `accepted` or `preprint` option is set.
- **Keywords.** Model evaluation; benchmark auditing; dataset bias; scene graph
  generation; long-tailed recognition; proper scoring rules; U-statistics.
- **Previous submission.** TMLR asks whether the work was submitted elsewhere. Earlier
  and substantially different versions were declined by Computer Vision and Image
  Understanding, Computational Statistics and Data Analysis and the Journal of
  Statistical Planning and Inference; an Econometrics and Statistics submission was sent
  back before review. **Confirm every one of those is closed before answering** — in
  particular withdraw the Econometrics and Statistics submission explicitly if it is
  still open in that system.
- **Code and data.** Both are in the supplementary archive. The public repository is
  deliberately not named anywhere in the PDF or the archive; add it for the camera-ready.

## Anonymity — what was removed, and what to put back on acceptance

The PDF contains no author name, affiliation, email, ORCID or repository URL; the
archive contains none either, and `build_code_archive.py` is what enforces that. On
acceptance:

1. `\usepackage[accepted]{tmlr}` in `manuscript/main.tex`, and set `\month`, `\year` and
   `\openreview`.
2. Restore the CRediT statement, the competing-interests declaration and the funding
   statement, which the TMLR template says to add only once deanonymized. The text is in
   `manuscript/declarations.docx`, built by `experiments/build_declarations_docx.py`.
3. Replace the Reproducibility Statement's pointer to the anonymized archive with the
   repository URL, ideally a Zenodo DOI for the tagged release.
4. Rebuild the archive with `python experiments/build_code_archive.py --identified`.

## Why TMLR

Four venues declined earlier versions, and none of them on correctness: CVIU and CSDA
desk-rejected on novelty and fit, JSPI rejected after review on legibility. TMLR's stated
acceptance test is whether the claims are supported by clear evidence and whether anyone
in its audience would be interested — which is the axis this paper is strongest on, and
not the axis it keeps losing on. It is also free, imposes no page limit, and returns
decisions in roughly two months.

Two things to be aware of. TMLR is not indexed in JCR and carries no impact factor, so
it may not count for an institutional evaluation that requires one. And the anonymized
submission becomes publicly visible on OpenReview once an action editor assigns
reviewers — earlier than a conventional journal, though the reviews stay private until
all three are in.
