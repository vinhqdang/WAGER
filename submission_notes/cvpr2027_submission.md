# CVPR 2027 submission

**Deadlines (all Anywhere on Earth).** Paper registration 10 November 2026; full paper
16 November 2026; supplementary material 23 November 2026.
Source: https://cvpr.thecvf.com/Conferences/2027/Dates

## What to upload

| Item | File | Notes |
|---|---|---|
| Paper | `cvpr2027/paper.pdf` | 8 pages; 7 of content, references from page 7 |
| Supplementary PDF | `cvpr2027/supp.pdf` | 23 pages, single-column |
| Supplementary code | `code.zip` | anonymized by default; 20 tests pass inside the archive |

`cvpr2027/build.sh` builds one document from the official author kit and splits it into
`paper.pdf` and `supp.pdf`, failing if the paper runs past eight pages of content.
`python experiments/build_code_archive.py` rebuilds the archive.

## Rules that would get the paper rejected without review

- **Eight pages, including figures and tables, excluding references.** Current: seven.
  `build.sh` enforces it.
- **The official template.** Built from `cvpr-org/author-kit` at commit `2917585`. The 2027
  author guidelines page was not yet published when this was built (it returned 404 on
  2026-10-03); the rules above are from the 2026 guidelines. **Check the 2027 guidelines
  and kit before the deadline** and rebuild if either has changed.
- **Anonymity, including the supplementary.** Both PDFs contain no author name,
  affiliation, email, ORCID or repository URL, and the PDF metadata carries no author. The
  code archive is scrubbed by `build_code_archive.py`; verify with
  `unzip -q code.zip -d /tmp/chk && grep -rli "vinh\|british university" /tmp/chk`.

## Obligations that come with submitting

- **Reviewing.** "All authors commit to serve as reviewers, area chairs, or senior area
  chairs when invited by the program chairs." As sole author you will very likely be
  invited, during roughly December–January.
- **OpenReview profile.** Must be up to date for every author. An institutional email
  activates automatically; a non-institutional one goes through moderation of up to two
  weeks. Use the institutional address and check the profile well before 10 November.
- **Dual submission.** No substantially similar paper may be submitted to another
  conference or workshop between 16 November 2026 and 22 February 2027. Nothing is under
  review anywhere now: TMLR desk-rejected on 2026-10-03 and the Econometrics and
  Statistics submission was withdrawn.
- **Generative AI.** CVPR 2027 says its LLM policy is "currently being finalized" and will
  be published before the deadline. The long-form manuscript carries a disclosure; the CVPR
  paper currently does not. **Read the policy when it appears and add whatever it
  requires.**

## Title and abstract for the registration form

Title: *What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level
Gains in Scene Graph Generation*

The abstract is `cvpr2027/sec/0_abstract.tex`. Generate a plain-text copy from the source,
not by copying out of the PDF, which mangles words hyphenated across line breaks.

## On acceptance

`\usepackage{cvpr}` instead of `\usepackage[review]{cvpr}` in `cvpr2027/main.tex`; the
author block is already in the source. Restore the repository URL in the conclusion and
the supplementary overview, and rebuild the archive with `--identified`.
