# Pattern Recognition submission questionnaire — answers

Every figure below is measured from the built PDFs in `manuscript/`, not from the LaTeX
source. Regenerate with `manuscript/build.sh`. Three items marked **YOUR CALL** are
decisions, not measurements.

---

## Questionnaire

**Please include the word count of your manuscript in the box below.**

> 9,869 words up to the reference list; 10,690 words including it. The manuscript is 35
> numbered pages: pages 1–31 carry the text, one figure, one table and the declarations,
> and pages 32–35 carry the 39 references. Supplementary material is a separate 45-page
> file and is not counted here.

**Please confirm that you have mentioned all organizations that funded your research in
the Acknowledgements section, including grant numbers.**

> Select: *I confirm.*
> The manuscript carries a Funding section stating that the research received no specific
> grant from funding agencies in the public, commercial or not-for-profit sectors.

**Software co-submission (Software Impacts, 250 USD open-access fee).**  — **YOUR CALL**

> Recommendation: decline. The estimator is released with the paper under a public
> repository and a verification script, which is what a reader needs; a second reviewed
> article about the same code adds a fee and a second review process without adding
> reach. If the form forces the single option "No — I have no software to contribute",
> note that its wording is inaccurate for this paper (there *is* released software); if
> the field is optional, leave it unselected rather than assert that.

**Research data/code availability statement.**  — **YOUR CALL**

> Do **not** select "Data will be made available on request": it understates a release
> that is already public and would be published verbatim beside the article.
> Select the public-repository option and give
> `https://github.com/vinhqdang/WAGER`.
> Pattern Recognition applies Elsevier's **Option C**, which asks for a deposit in a
> repository that can be *cited*. GitHub has no DOI, so archive the release on Zenodo
> (GitHub → Zenodo integration mints one per tag) and give the Zenodo DOI in the
> statement and in the manuscript's Data and code availability section. If you would
> rather not, the statement is still defensible as a public-repository release, but
> Option C is met properly only by the DOI.

**Free preprint service (SSRN).**  — **YOUR CALL**

> Recommendation: **YES**. It mints a DOI at the point the paper enters review, costs
> nothing, does not affect the editorial process, and leaves the work readable whatever
> the decision. The only reason to decline is if you would rather no version of the
> paper be public until acceptance.

### Fitness & length

**In what field is the scope of your paper?**

> Pattern recognition, specifically the evaluation of pattern-recognition systems.
> The paper addresses benchmarks whose labels are partly determined by a feature both
> compared models observe — the object-class pair in scene graph generation, the class
> frequency in long-tailed recognition — and gives an exact decomposition of the score
> gain between two frozen models into the part attributable to fitting label frequencies
> within groups of that feature and the part attributable to telling individual cases
> apart. The empirical work is on Visual Genome VG150 predicate classification (including
> an audit of two publicly released MOTIFS/MOTIFS-TDE checkpoints), a frozen-CLIP
> ViT-B/32 variant reading real image crops, CIFAR-100-LT and long-tailed
> 20-Newsgroups. It therefore sits in the journal's scope for evaluation methodology,
> dataset bias and benchmark auditing in visual and long-tailed recognition.

**Are you covering the State of the Art?**

> Yes, and the cover letter answers this explicitly. The paper is an evaluation method
> rather than a predictor, so there is no accuracy to beat; what it can be positioned
> against is current practice on the same question, which Section 2 does. The five works
> representing that state of the art are: Zellers et al. (2018), whose frequency
> baseline is the standard prior-only reference; Tang et al. (2020), whose mean-recall
> reporting and causal intervention are the dominant debiasing practice in scene graph
> generation and whose released checkpoints the paper audits; Li et al. (2022), on the
> pathologies of the mean-recall metric itself; Kervadec et al. (2021), whose GQA-OOD
> stratifies evaluation by answer rarity within question groups; and Lu et al. (2016),
> which introduced zero-shot recall. Each is a prior-aware slicing or stress test of a
> *single* model; none decomposes the gain between two fixed systems with a
> finite-sample identity and uncertainty, which is what this paper adds. Recent
> pattern-recognition work on the same pathologies is cited as well (Zhou et al. 2025,
> Luo et al. 2025, Kuang et al. 2024, Li et al. 2024, Duan et al. 2024).

**How many columns is your paper written in?**

> One. Single-column throughout, fully justified, with numbered pages. No
> double-column formatting is used anywhere, including in tables and figures.

**Is your paper double-spaced or single-spaced?**

> Select: *double-spaced.* Set with the `setspace` package (`\doublespacing`) from the
> first page of text.

**How long is your paper?**

> 35 numbered pages, inside the 20–35 page limit. Pages 1–31 carry the text, one figure,
> one table and the declarations; pages 32–35 carry the reference list. Supplementary
> material — proofs, the influence-function derivation, implementation and
> reproducibility detail, two further empirical studies and the sensitivity analyses —
> is uploaded as a separate 45-page file and is outside the manuscript.

### Files & formatting

**What font did you use?**

> Times New Roman. Set by the `times` option of the Elsevier class,
> `\documentclass[preprint,times,10pt,a4paper]{elsarticle}`, which selects Times for
> text and the matching Times mathematics fonts.

**What is the font size of text incl. tables?**

> 10 pt. The document base size is 10 pt and table content is set at the same 10 pt; no
> table is reduced with `\small` or `\footnotesize`.

**What font size did you use for footnotes and captions?**

> 8 pt. At a 10 pt base, `\footnotesize` is 8 pt, and captions are set with
> `\usepackage[font=footnotesize,labelfont=bf]{caption}`, so figure and table captions
> and footnotes are all 8 pt, with the caption label in bold.

**What margins did you use?**

> 4.3 cm top, 4.8 cm right, 4.3 cm bottom, 4.8 cm left, on A4, set with
> `\usepackage[top=4.3cm,right=4.8cm,bottom=4.3cm,left=4.8cm]{geometry}` — exactly the
> 4.3/4.8/4.3/4.8 cm the guide specifies.

**In what format is your table?**

> Select: *editable text* (not an image). The single main-text table is LaTeX `tabular`
> text set with `booktabs` rules; it has no vertical rules and no cell shading, and its
> notes sit below the table body.

**How are your figures provided?**

> Select: *within the text and as separate files.* Figure 1 is placed at its point of
> discussion in the manuscript and the same PNG is uploaded as a separate numbered file
> with its caption supplied separately. It is a photographic figure, 5000 x 2160 px at 400 dpi, above the 300 dpi and 2244 px full-page minimums.

**If you use LaTeX to edit your article, what is the header you used?**

> ```
> \documentclass[preprint,times,10pt,a4paper]{elsarticle}
> \usepackage[top=4.3cm,right=4.8cm,bottom=4.3cm,left=4.8cm]{geometry}
> \usepackage{setspace}                                    % \doublespacing
> \usepackage[font=footnotesize,labelfont=bf]{caption}     % 8pt captions
> \usepackage{graphicx}
> \usepackage{amsmath,amssymb,amsfonts,amsthm}
> \usepackage{booktabs}
> \bibliographystyle{elsarticle-num-names}
> ```
> The Elsevier `elsarticle` class with the `preprint`, `times`, `10pt` and `a4paper`
> options, plus `geometry` for the required margins, `setspace` for double spacing and
> `caption` for the 8 pt captions.

### Mandatory manuscript components

**How many words is your title?**

> 14 words: "WAGER: An Exact Decomposition of Model-Pair Score Gains on Benchmarks with
> Strong Label Priors" — inside the guide's 10–15 words, with no abbreviation other than
> the method's own name and no formulae.

**What font size did you use for the title?**

> 14 pt, set explicitly. The Elsevier class would otherwise typeset the title at
> `\Large`, which is 14.4 pt at a 10 pt base, so the size is pinned with
> `\fontsize{14}{17}\selectfont` to give exactly the 14 pt the guide asks for. Author
> names, affiliations and corresponding-author details on the separate title page are
> 8 pt.

**How many words is your Abstract?**

> 241 words, inside the 250-word limit. Counted on the rendered page, so inline
> mathematics and dashes are counted as the reader sees them.

**How many keywords did you provide?**

> 7, inside the 1–7 range: Model evaluation; Benchmark auditing; Dataset bias; Scene
> graph generation; Long-tailed recognition; Proper scoring rules; U-statistics.

**How many highlights did you provide?**

> 5, inside the 3–5 range, each within the 85-character limit (the longest is 83
> characters). Supplied as a separate file.

**Did you divide the manuscript into clearly defined and numbered sections and
subsections numbered as 1.1, 1.1.1, then 1.2, and so on?**

> Yes. Six numbered sections — 1 Introduction, 2 Related work, 3 The estimator and its
> properties, 4 Experiments, 5 Discussion and limitations, 6 Conclusion — with 24
> subsections numbered in that scheme (1.1, 1.2, 1.3, 2.1–2.4, 3.1–3.10, 4.1–4.5,
> 5.1–5.2). Every cross-reference in the text uses those numbers. The back matter
> (supplementary material, data and code availability, CRediT, competing interests,
> funding, generative-AI declaration) is unnumbered, as is conventional. Supplementary
> sections are numbered S1–S15 with an S prefix and are cited in that form.

### References

**How many references do you have?**

> 39, inside the requested 35–55. They span journal articles, conference proceedings and
> books; only four cite a preprint venue; recent pattern-recognition work is cited
> (2024–2025 entries included); and no citation appears as an uncommented group — every
> reference is discussed individually, as the guide asks.

**What style did you use for the bibliography references?**

> Elsevier numbered style (elsarticle-num-names): bracketed numerals [n], numbered in
> order of appearance, with DOIs where available.

**Is every in-text citation appearing in the reference list and vice versa?**

> Yes, and this is checked mechanically rather than by eye. The bibliography is generated
> by BibTeX from the cited keys, so the list cannot contain an uncited entry, and
> `manuscript/build.sh` fails the build if the LaTeX log reports any undefined citation
> or reference. The current build reports none. The six entries in `ref.bib` cited only
> by the supplementary appear in that document's own reference list, not the
> manuscript's.

### Cover letter

**How long is your Cover letter?**

> 2 pages, 1,078 words.

**Read your cover letter carefully and confirm if it explains importance and fit to
scope.**

> Select: *Yes.* It opens with the problem in pattern-recognition terms — a reported
> ten-point mean-recall gain on Visual Genome whose composition no existing metric can
> read — states what the paper contributes, and says why Pattern Recognition rather than
> a statistics venue is the right readership.

**Did you explicitly answer whether you compared to the state-of-the-art mentioning 5
SOTA papers (or explain why not)?**

> Yes. The cover letter answers the question under its own heading, explains that an
> evaluation method has no accuracy to beat, and names the five works that represent
> current practice on the same question — Zellers et al. (2018), Tang et al. (2020),
> Li et al. (2022), Kervadec et al. (2021) and Lu et al. (2016) — saying for each what
> it does and what this paper adds to it.

**Is your work an extension of a previously published paper, e.g. in a conference?**

> Select: *No.* Nothing in this manuscript has appeared in a conference or journal
> proceedings; there is no shorter published version to extend.

### Declarations & ethics

**Is your manuscript under consideration elsewhere, or previously published beyond
allowed forms?**  — **CHECK BEFORE ANSWERING**

> Select: *No* — but confirm one thing first. Earlier and substantially different
> versions of this work were submitted to statistics journals. Those must all be closed
> (declined, or withdrawn by you) before you answer No. In particular, if the
> Econometrics and Statistics submission was only *sent back* for double-blind
> reformatting rather than withdrawn or rejected, it may still be an open submission in
> that system; withdraw it explicitly before submitting here. The cover letter states
> that no earlier submission remains open, so the two answers must agree.

**Have you submitted a declaration regarding the question above?**

> Select: *Yes.* The cover letter carries a Declarations paragraph stating that the
> manuscript is original, is not under consideration elsewhere, and that earlier
> submissions are closed.

**Have you submitted a competing interests declaration (uploaded as requested)?**

> Select: *Yes.* Uploaded as `declarations.docx`, which carries the competing-interests
> statement together with the funding, CRediT and generative-AI declarations; the same
> statements also appear as sections of the manuscript.

**Did you use Generative AI at any stage of manuscript preparation?**

> Select: *Yes.*

**If you have used Generative AI, confirm you have completed the Generative AI
disclosure.**

> Select: *Yes.* The manuscript carries the declaration in Elsevier's prescribed form,
> under the heading "Declaration of generative AI and AI-assisted technologies in the
> manuscript preparation process", stating the use, that the author reviewed and edited
> the output, and that the author takes full responsibility for the content. No figure
> or image was generated or altered by an AI tool, so no per-caption disclosure is
> required.

**Did you define the contributions of all authors?**

> Select: *Yes.* There is a single author, and the manuscript carries a CRediT statement
> listing the roles: Conceptualization; Methodology; Formal analysis; Software;
> Investigation; Validation; Visualization; Writing – original draft; Writing – review
> and editing.

### Data & code

**Did you do a Data statement, explaining data availability; if not shareable,
explaining why?**

> Yes. The manuscript carries a "Data and code availability" section. All data used is
> public: Visual Genome via the canonical VG150 predicate-classification split, the two
> publicly released MOTIFS and MOTIFS-TDE checkpoints of Tang et al. evaluated with the
> authors' own code, CIFAR-100 and 20-Newsgroups. No proprietary, restricted or
> personal data is used, so nothing is withheld. The estimator, every experiment driver,
> the unit tests, the cached model outputs and a verification script that checks each of
> the 89 reported numerical values against the committed results files are released at
> `https://github.com/vinhqdang/WAGER`.
> **YOUR CALL:** add a Zenodo DOI for the release, as Option C asks (see the data
> availability item above), and put the DOI in this statement as well.

---

## Attach-files checklist

| Item | File | Measured |
|---|---|---|
| Manuscript | `manuscript/main.pdf` (source `main.tex` + inputs) | 35 pp, 39 refs |
| Supplementary material | `manuscript/supplementary.pdf` | 45 pp |
| Cover letter | `manuscript/cover_letter.pdf` | 2 pp, 1,078 words |
| Highlights | `manuscript/highlights.pdf` / `.txt` | 5 bullets, ≤83 chars |
| Title page | `manuscript/title_page.pdf` | 2 pp, 8 pt author details |
| Declarations | `manuscript/declarations.docx` | competing interests, funding, CRediT, GenAI |
| Figure file | `manuscript/figures/fig1_new_concept.png` | separate, numbered, 5000 x 2160 px at 400 dpi |
| Code | `code.zip` | 61 files, 132 KB |
| Editable source | `submission/` (flat bundle, `--zip` for the archive) | renders identically to the modular build |

Editorial Manager wants editable source, not only PDF: upload the flat bundle from
`python experiments/build_flat_submission.py --zip`, whose `main.tex` and
`supplementary.tex` have every `\input` inlined, the `figures/` paths flattened, and the
cross-document reference numbers frozen.
