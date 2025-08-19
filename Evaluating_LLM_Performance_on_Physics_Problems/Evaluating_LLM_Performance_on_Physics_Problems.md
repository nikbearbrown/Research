# Evaluating LLM Performance on Physics Problems

Here’s a single, end-to-end, “do-this-next” protocol you can hand to a grad student to run the full study— from pulling OpenStax problems to stats, figures, and write-up. It folds in your outline + methodology + refined data plan and adds concrete file structures, prompts, scoring rules, and QA gates.

# Standard Operating Procedure (SOP)

## Evaluating LLM Performance on OpenStax Physics Problems

### Executive Summary

You will (1) build a structured dataset of OpenStax physics problems + solutions, (2) sample a balanced test set, (3) query several LLMs with standardized prompts, (4) score answers using an objective rubric (with human spot checks), (5) analyze accuracy by topic/problem type, and (6) produce figures and a paper-ready Results/Discussion.

---

## 0) Prerequisites & Repo Skeleton

### Tools

* Python 3.11+
* Conda or uv/poetry
* Pandas, NumPy, Pydantic, Jupyter
* Stats: pingouin or statsmodels, scikit-learn
* Plotting: matplotlib (and seaborn only for local EDA if desired)
* API SDKs as needed (e.g., OpenAI, Anthropic, provider for Llama)
* YAML (ruamel.yaml or pyyaml)
* Optional: Snakemake or Makefile for repeatable pipelines

### Folder layout

```
llm-physics-eval/
  README.md
  env.yml
  config.yaml
  data/
    raw/               # downloaded OpenStax content (keep CC-BY attribution)
    interim/           # OCR/text conversions, per-chapter txt
    processed/         # structured JSONL of problems
    testsets/          # sampled test batches (JSONL)
    references/        # ground-truth solutions withheld from LLMs
  prompts/
    solve_prompt.txt
    self_eval_prompt.txt
  runs/
    <model_name>/
      <YYYYMMDD>_<run_id>/
        responses.jsonl
        meta.json
  eval/
    scores/
      item_scores.jsonl
      summary_by_model.csv
      error_taxonomy.csv
    human_ratings/
      sampled_items.jsonl
      raters/    # store blinded annotations
  analysis/
    notebooks/
      01_dataset_overview.ipynb
      02_scoring_qc.ipynb
      03_stats.ipynb
      04_figures.ipynb
    figures/
      accuracy_by_model.png
      heatmap_chapter.png
  paper/
    outline.md
    results.md
    discussion.md
    references.bib
  scripts/
    00_download_openstax.py
    01_convert_to_text.py
    02_parse_problems.py
    03_qc_validate_schema.py
    04_sample_testsets.py
    05_run_models.py
    06_self_evaluate.py
    07_score_and_clean.py
    08_stats_and_figures.py
```

### Configuration (edit `config.yaml`)

```yaml
models:
  - name: gpt5 # or "gpt-4.1" etc; use provider's exact ID
    provider: openai
    temperature: 0.2
    max_tokens: 2048
  - name: claude-3.7-sonnet
    provider: anthropic
    temperature: 0.2
    max_tokens: 2048
  - name: llama-3.1-405b
    provider: providerX
    temperature: 0.2
    max_tokens: 2048

sampling:
  total_target: 400         # aim 300–500 total
  per_domain_min: 40        # mechanics, E&M, thermo, waves/optics, modern, etc.
  per_chapter_min: 10
  difficulty_mix: [easy, medium, hard]
  types: [concept, numerical, graph, short_answer, multiple_choice]

numerical_tolerance:
  absolute: 1e-2
  relative: 0.02            # 2% relative margin
units_required: true
seed: 42
```

---

## 1) Acquire & Prepare OpenStax Problems

1. **Download** relevant OpenStax physics textbooks (e.g., *College Physics*, *University Physics*), including problem sections and official solutions. Keep license/attribution (OpenStax is CC BY).
2. **Convert to text**

   * If PDFs: use a reliable PDF→TXT pipeline (e.g., `pdftotext`), then clean math/headers. If images contain equations/graphs, export figures and keep references (e.g., `Fig. 2.1`).
   * If HTML/EPUB: parse with `BeautifulSoup`/`readability-lxml`.
3. **Parse into structured JSONL** (`data/processed/problems.jsonl`) using a schema like:

```json
{
  "problem_id": "CP_V1_C2_P17",
  "book": "College Physics",
  "volume": 1,
  "chapter": 2,
  "chapter_title": "Motion in One Dimension",
  "section": "2.1 Relative Motion, Distance, and Displacement",
  "problem_number": 17,
  "problem_type": "multiple_choice", 
  "problem_text": "Billy drops a ball from a height of 1 m ...",
  "options": [
    {"label":"A","text":"..."},
    {"label":"B","text":"..."},
    {"label":"C","text":"..."},
    {"label":"D","text":"..."}
  ],
  "correct_answer": "D",
  "reference_solution": "The correct answer is (D). The displacement is ...",
  "topic_tags": ["displacement","distance","1D motion"],
  "difficulty_estimate": "medium",
  "requires_math": true,
  "requires_graph_interpretation": false,
  "key_principles": ["sign conventions","vector vs scalar"],
  "key_equations": ["Δx = x_f - x_i"]
}
```

4. **QC gate (schema + content)**

   * Validate required fields, ensure `correct_answer` is present for MCQ.
   * Ensure `reference_solution` aligns with the problem (spot check 10–15%).
   * Verify chapter/section mapping and topic tags.

**Tip:** For graph/figure-dependent items, add a concise textual description of the figure; if a model run will be multimodal-enabled, also store the image path (keep a text-only variant for comparability).

---

## 2) Classification & Mapping

1. **Primary classification** (OpenStax native): Book → Volume → Chapter → Section → Problem Type → Number.
2. **Secondary tags**: domain (mechanics/E\&M/thermo/…); format (MCQ/short/numerical/graph); math complexity (algebra/trig/calculus/vectors/units); cognitive level (recall/apply/analyze/evaluate).

Create `data/processed/chapter_to_domain.csv` mapping each chapter to a domain.

---

## 3) Sampling the Test Set

1. **Stratify** by domain, chapter, type, and difficulty to meet `config.yaml` targets.
2. **Randomize** with fixed seed.
3. **Produce batches** for runs:

   * Save `data/testsets/batch_001.jsonl`, `batch_002.jsonl`, … each with:

   ```json
   {"batch_id":"batch_001","problems":[{"problem_id":"..."},{"problem_id":"..."}]}
   ```
4. **Hold out** all solutions in `data/references/solutions.jsonl`. Models **must not** see this file during solving.

---

## 4) Prompting & Model Harness

### Solve Prompt (`prompts/solve_prompt.txt`)

Use exactly this, unless model provider forbids chain-of-thought. If they do, change “show your work” to “state key equations and a concise rationale,” and score only final answers + brief rationale.

```
You are assisting with solving a physics problem. Solve step-by-step, showing relevant equations and concise reasoning. Then give a single “Final Answer” on the last line, including units where applicable.

Problem:
[INSERT PROBLEM TEXT ONLY — DO NOT INCLUDE OPTIONS/ANSWER KEY]
```

**MCQ policy:** Prefer **generative** answering without options to reduce cueing. For a secondary run, include options to compare.

### Self-Eval Prompt (`prompts/self_eval_prompt.txt`)

```
You previously solved this physics problem:

[Problem text]

Your solution:
[LLM solution]

Reference solution:
[Official OpenStax solution/excerpt with final value or correct option]

Evaluate your solution using this rubric (0–5 each):
1) Correctness of final answer
2) Accuracy of method/approach
3) Completeness of steps
4) Proper use of physics principles
5) Mathematical accuracy

Explain each rating briefly. Then compute a composite score = (sum / 25).
Identify the main error types (choose from: units/sign/concept/formula/setup/algebra/rounding/other).
```

### Run Settings

* Temperature = 0.2 (low variance for fairness)
* Top\_p default; stop sequences where useful (“Final Answer”)
* Max tokens sufficient for worked steps (≥ 1024–2048)
* Single attempt per item per model for main analysis. (Optionally collect 3 attempts for within-model variance in an appendix.)
* Log: request/response IDs, timestamps, tokens, cost, model version.

### Execution

* Implement `scripts/05_run_models.py` to:

  * Load each batch, call each model, write `runs/<model>/<date>/responses.jsonl`.
  * Respect provider usage limits; exponential backoff on errors.
  * Record latency.

---

## 5) Scoring Pipeline

### A) Primary objective scoring

* **MCQ**: correct if model’s final answer text unambiguously matches the correct option content (not just letter). Implement robust matching:

  * Normalize text (case/whitespace), allow “(D)” or “Option D”.
  * If the model provides a value matching the keyed option text, count as correct.

* **Numerical**: parse final numeric value and units. Correct if:

  * Units match expected dimension (e.g., m, m/s, m/s²). Allow equivalent SI units (cm→m).
  * Value within tolerance: success if `abs(ŷ − y*) ≤ max(absolute_tol, relative_tol*|y*|)`.
  * Track significant-figure mismatch separately (does not auto-fail unless wildly off).

* **Short/Conceptual**: use rule-based keyword checks + reference solution patterns. When ambiguous, flag for human check in the 5–10% QA sample.

### B) Rubric scoring (self-eval)

* Parse the model’s rubric outputs into 5 integers + composite.
* **Do not** let self-eval change correctness; it populates error analysis and explanation quality.

### C) Human verification (5–10%)

* Randomly sample across domains/types/difficulties and across **correct** and **incorrect** calls.
* Provide blinded packets: problem text, model final answer/rationale, reference solution (hidden initially), and the rubric.
* Compute Cohen’s κ between raters and agreement vs. automated scoring.

### D) Error taxonomy labeling

For each incorrect item, auto-label primary error from:
`{units, sign, conceptual, formula selection, setup/diagram, algebra/arithmetic, rounding/precision, misreading, other}`.
Allow multiple tags; human raters refine in sampled subset.

---

## 6) Data Products & Schemas

### Responses (`runs/.../responses.jsonl`)

```json
{
  "run_id": "2025-08-18_gpt5_b001",
  "model": "gpt5",
  "problem_id": "CP_V1_C2_P17",
  "prompt_variant": "no_options",
  "request_meta": {"temperature":0.2,"max_tokens":2048},
  "llm_solution": "… full text …",
  "final_answer": {"type":"numeric","value":-0.80,"units":"m"},
  "latency_s": 3.42,
  "input_tokens": 512,
  "output_tokens": 624
}
```

### Reference solutions (`data/references/solutions.jsonl`)

```json
{
  "problem_id":"CP_V1_C2_P17",
  "final_answer": {"type":"numeric","value":-0.80,"units":"m"},
  "mcq_correct_option":"D",
  "reference_solution_text":"The correct answer is (D)…",
  "key_principles":["…"],
  "key_equations":["…"]
}
```

### Scores (`eval/scores/item_scores.jsonl`)

```json
{
  "model":"gpt5",
  "problem_id":"CP_V1_C2_P17",
  "correct_binary":1,
  "numeric_abs_err":0.0,
  "units_ok":true,
  "self_eval_scores":{"final":5,"method":4,"completeness":4,"principles":5,"math":5,"composite":0.92},
  "error_tags":[]
}
```

---

## 7) Statistical Analysis Plan

1. **Descriptives**

   * Overall accuracy per model.
   * Accuracy by domain, chapter, type, difficulty.
   * Error-type frequencies.

2. **Hypothesis tests**

   * **Between-model differences**: χ² tests for proportions or logistic regression.
   * **Mixed-effects logistic regression** (recommended):

     ```
     correct ~ model + domain + type + difficulty + (1|problem_id)
     ```

     (Optionally add `(1|chapter)` or random slopes.)
   * **ANOVA** on rubric composites (if approximately normal) or Kruskal–Wallis.

3. **Predictors of success/failure**

   * Logistic regression with features: requires\_graph, math\_complexity, units\_required, presence\_of\_diagram, chapter index (as proxy for curriculum progression).

4. **Robustness**

   * Re-run scoring with (a) stricter numerical tolerance, (b) options provided vs withheld, (c) paraphrased problems (see §9).

5. **Inter-rater reliability**

   * Cohen’s κ for correctness calls on sampled items.
   * ICC or weighted κ for rubric sub-scores.

---

## 8) Visualization Plan (save to `analysis/figures/`)

* Bar chart: accuracy by model.
* Heatmap: accuracy by chapter (rows) × model (cols).
* Stacked bars: error taxonomy distribution by model.
* Scatter: difficulty (x) vs accuracy (y) with loess per model.
* Ribbon plot: accuracy by domain with 95% CIs.

---

## 9) Validity, Bias, and Contamination Checks

1. **Order & Blinding**

   * Randomize problem order per model.
   * Blind human raters to model identity.

2. **Memorization audit**

   * Create a paraphrased subset (reworded numbers/context without changing physics) and re-run on all models; compare deltas.
   * Flag any responses mentioning “OpenStax” or quoting text verbatim.

3. **Unsolvable/control items**

   * Insert a tiny set of ill-posed or under-specified items; expect models to defer or note insufficiency.

4. **Graph/Image dependency**

   * For items requiring figures, run both text-only (described figure) and, if supported, multimodal inputs; compare.

---

## 10) Human Subjects & Ethics

* Human raters are evaluating explanations, not giving personal data; typical studies don’t require IRB, but follow your institution’s guidance.
* Respect OpenStax CC BY license—store attribution and cite in the paper.
* Do not publish full proprietary API logs with keys; keep `.env` out of version control.

---

## 11) Reproducibility

* Freeze environment (`env.yml`) and model version strings.
* Fix random seeds (dataset sampling, paraphrase generation).
* Commit `config.yaml` and all scripts.
* Keep a `meta.json` per run with start time, git commit hash, and model IDs.

---

## 12) Timeline (phases you can track in your Gantt)

* **Preparation (4–6 wks):** ingestion, parsing, QC, pilot 20–30 items.
* **Data collection (6–8 wks):** full model runs.
* **Evaluation (4–6 wks):** self-eval, human spot checks, cleaning.
* **Analysis (6–8 wks):** stats + figures.
* **Reporting (4–6 wks):** manuscript drafting.

---

## 13) Writing Guide (use your paper outline)

* **Introduction:** LLMs in STEM ed; need for standardized evaluation on vetted textbooks.
* **Methods:** Dataset, sampling, prompts, models, scoring rubric, human verification, statistics, bias checks.
* **Results:** Overall accuracy; by domain/chapter/type; error taxonomy; figures.
* **Discussion:** Pedagogical implications, strengths/weaknesses by model, limitations (possible training contamination, figure dependence), future work (paraphrase-first test sets, lab-style multi-step problems, solver+verifier architectures).
* **Conclusion:** Concise recap; next steps for educational deployment.
* **References:** Include OpenStax citation + LLM/provider docs + prior STEM LLM eval work.

---

## 14) Concrete Checklists

### Daily run checklist

* [ ] `git pull` latest; environment activated
* [ ] `data/processed/problems.jsonl` passes schema validation
* [ ] `data/testsets/*.jsonl` created with seed = 42
* [ ] API quotas checked; `.env` loaded
* [ ] `scripts/05_run_models.py` on batch N (log tokens & latency)
* [ ] New `runs/<model>/<date>/responses.jsonl` saved
* [ ] Backup to secure storage

### Scoring checklist

* [ ] Parse final answers reliably (number + units extraction)
* [ ] Apply tolerance rules
* [ ] MCQ normalization (content match > letter-only)
* [ ] Populate `item_scores.jsonl`
* [ ] Sample 10% for human review; compute κ

### Analysis checklist

* [ ] Tables: accuracy by model/domain/type/difficulty
* [ ] Mixed-effects model fitted; diagnostics OK
* [ ] Figures saved; captions drafted

---

## 15) Implementation Notes & Snippets

### Schema validation (Pydantic example)

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Option(BaseModel):
    label: str
    text: str

class Problem(BaseModel):
    problem_id: str
    book: str
    volume: int
    chapter: int
    chapter_title: str
    section: Optional[str] = None
    problem_number: int
    problem_type: str
    problem_text: str
    options: Optional[List[Option]] = []
    correct_answer: Optional[str] = None
    reference_solution: Optional[str] = None
    topic_tags: List[str]
    difficulty_estimate: str
    requires_math: bool
    requires_graph_interpretation: bool
    key_principles: List[str] = []
    key_equations: List[str] = []
```

### Robust numeric comparison

```python
def is_num_correct(pred, truth, abs_tol=1e-2, rel_tol=0.02):
    return abs(pred - truth) <= max(abs_tol, rel_tol*abs(truth))
```

### Mixed-effects logistic (statsmodels)

```python
# Convert to long-form dataframe with columns: correct, model, domain, type, difficulty, problem_id
# Use `mixedlm` for continuous; for logistic, use `BinomialBayesMixedGLM` or run per-problem random intercept via GLMM (or fit with `bambi`/`pymer4` equivalent).
```

---

## 16) Handling the Provided Example Set (Chapter 2 Excerpts)

* Ensure these sample items from “2 | Motion in One Dimension” are parsed into the schema above (MCQ with correct options and solutions).
* For problems (e.g., #17, #19, #21, #23): store a **text-only** description of any missing figure context using the sentences included in the item (as you pasted).
* Tag example problems with `topic_tags`: `["1D motion","displacement","velocity","graphs","average acceleration"]`.
* Include both MCQ and numerical evaluation logic for items like #37, #51, #55, etc.

---

## 17) Extensions (optional but valuable)

* **Options withheld vs provided** A/B runs.
* **Few-shot vs zero-shot**: add minimal exemplars and compare.
* **Verifier pass**: second LLM checks the first answer (do not use the reference solution); measure gains.
* **Curricular progression**: model accuracy vs chapter index (learning curve proxy).

---

## 18) Attribution & Licensing

* Keep OpenStax CC BY attribution in `README.md` and cite in the paper.
* Do not redistribute full problem text publicly unless license terms allow; sharing derived statistics and brief excerpts within fair use is standard.

---

NOTE

If you want, you can ask an LLM to generate: (a) a ready-to-run `env.yml`, (b) starter `config.yaml` filled for your target models, and (c) stubs for the `scripts/` so the student can just fill in API keys and go.


