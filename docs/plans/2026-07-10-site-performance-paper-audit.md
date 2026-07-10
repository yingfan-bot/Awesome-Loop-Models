# Site Performance and Paper Audit Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce catalog transfer and rendering work, add durable catalog-quality checks, and verify every canonical paper's content and tags against primary sources.

**Architecture:** Keep the zero-framework GitHub Pages site and YAML source-of-truth model. Generate separate browser payloads for browsing and submission, add a read-only structural/evidence auditor plus per-paper audit ledgers, then correct canonical YAML only when primary-source evidence supports the change.

**Tech Stack:** Static HTML/CSS/JavaScript, Python 3.12 standard library, PyYAML, generated JSON/Markdown, `unittest`, GitHub Pages.

---

### Task 1: Preserve and measure the current baseline

**Files:**
- Create: `docs/plans/2026-07-10-site-performance-baseline.md`

**Step 1: Record the current source and artifact counts**

Record the current commit, number of canonical paper YAML files, `index.html` bytes, `papers.json` bytes and gzip bytes, briefing count/body bytes, favicon dimensions/bytes, and the known render-path observations.

**Step 2: Run lightweight measurements**

Run:

```bash
find papers -maxdepth 1 -name '*.yaml' | wc -l
wc -c index.html submit.html papers.json assets/favicon.png
gzip -c papers.json | wc -c
jq '.briefings | length' papers.json
jq '[.briefings[].content | length] | add' papers.json
git diff --check
```

Expected: valid counts, valid JSON queries, and no whitespace errors.

**Step 3: Commit the baseline**

```bash
git add docs/plans/2026-07-10-site-performance-baseline.md
git commit -m "docs: record site performance baseline"
```

### Task 2: Specify a minimal browser catalog payload

**Files:**
- Modify: `tests/test_build.py`
- Modify: `scripts/build.py`

**Step 1: Add failing unit tests**

Add tests asserting that the browser payload:

- includes papers and blogs;
- includes at most the latest briefing;
- omits briefing `content`;
- preserves fields rendered by `index.html`;
- does not change the complete briefing model used for README generation.

**Step 2: Have CI or the user verify the tests fail**

Run externally:

```bash
python3 -m unittest tests.test_build -v
```

Expected before implementation: the new payload tests fail because all briefing bodies are emitted.

**Step 3: Implement a dedicated payload serializer**

Add focused helpers with docstrings to `scripts/build.py` that serialize browser data independently from internal build records. Emit only the latest briefing fields used by the catalog.

**Step 4: Have CI or the user verify the tests pass**

Run externally:

```bash
python3 -m unittest tests.test_build -v
```

Expected: the new payload tests pass.

**Step 5: Commit**

```bash
git add scripts/build.py tests/test_build.py
git commit -m "perf: trim browser catalog payload"
```

### Task 3: Generate submission-only metadata

**Files:**
- Modify: `scripts/build.py`
- Modify: `submit.html`
- Modify: `tests/test_build.py`
- Create: `submission-meta.json`

**Step 1: Add failing tests for the submission artifact**

Assert that the artifact contains only source paths and normalized tag inventories needed by `submit.html`, and contains no descriptions, authors, metrics, links, or briefing bodies.

**Step 2: Add a documented generator helper**

Generate `submission-meta.json` atomically with the other build artifacts.

**Step 3: Switch the submission page fetch**

Update `submit.html` to request `submission-meta.json` and retain an explicit fetch-failure message.

**Step 4: Verify via CI/user command**

```bash
python3 scripts/build.py
python3 -m unittest tests.test_build -v
```

Expected: generated metadata matches tests and the submission page no longer requires the full catalog.

**Step 5: Commit**

```bash
git add scripts/build.py submit.html tests/test_build.py submission-meta.json
git commit -m "perf: split submission metadata payload"
```

### Task 4: Eliminate duplicate initial card rendering

**Files:**
- Modify: `index.html`
- Modify: `tests/test_build.py`

**Step 1: Add a failing source-contract test**

Assert that category/blog section construction creates empty grids and that `renderAllGrids()` is the only path that populates ordinary catalog card grids.

**Step 2: Remove eager card insertion**

Keep tree and section shell creation, but defer card HTML until the initial search/render pass. Preserve the existing lazy table rendering behavior.

**Step 3: Add assertions for table cleanup**

Keep a source-contract test that table rows are not generated in category view and are cleared when leaving table view.

**Step 4: Verify via CI/user command**

```bash
python3 -m unittest tests.test_build -v
```

Expected: render-contract tests pass.

**Step 5: Commit**

```bash
git add index.html tests/test_build.py
git commit -m "perf: render catalog cards once on startup"
```

### Task 5: Reduce critical resource overhead

**Files:**
- Modify: `index.html`
- Modify: `assets/favicon.png`
- Modify: `tests/test_build.py`

**Step 1: Add static resource assertions**

Assert that `index.html` has no Google Fonts stylesheet request and the favicon stays below an agreed deterministic byte ceiling.

**Step 2: Use the existing system font stack**

Remove Google Fonts preconnect and stylesheet tags while keeping the CSS fallback stack.

**Step 3: Resize the favicon mechanically**

Create a 48x48 or 64x64 optimized PNG from the existing asset without changing its design.

**Step 4: Visually inspect before accepting**

Confirm header layout, card wrapping, dark mode, and favicon appearance in a browser.

**Step 5: Commit**

```bash
git add index.html assets/favicon.png tests/test_build.py
git commit -m "perf: reduce critical font and favicon cost"
```

### Task 6: Add deterministic asset budgets

**Files:**
- Create: `scripts/check_asset_budgets.py`
- Create: `tests/test_asset_budgets.py`
- Modify: `.github/workflows/build-papers.yml`
- Modify: `CONTRIBUTING.md`

**Step 1: Write failing budget tests**

Cover catalog JSON raw/gzip size, submission metadata size, maximum briefing count/body policy, and critical favicon bytes. New source files must have file-level docstrings and every public helper must have a docstring.

**Step 2: Implement a deterministic checker**

The checker prints each measured value and its limit, exits nonzero for exceeded hard limits, and does not use network access.

**Step 3: Wire the checker into CI**

Run it after generation so budgets cover committed artifacts.

**Step 4: Document local/CI usage**

Add the exact command and explain how to update a budget intentionally.

**Step 5: Verify via CI/user command**

```bash
python3 scripts/check_asset_budgets.py
python3 -m unittest tests.test_asset_budgets -v
```

Expected: measured values are printed and all budgets pass.

**Step 6: Commit**

```bash
git add scripts/check_asset_budgets.py tests/test_asset_budgets.py .github/workflows/build-papers.yml CONTRIBUTING.md
git commit -m "ci: enforce static site asset budgets"
```

### Task 7: Add the catalog structural auditor

**Files:**
- Create: `scripts/audit_catalog.py`
- Create: `tests/test_audit_catalog.py`
- Create: `audits/README.md`
- Modify: `CONTRIBUTING.md`

**Step 1: Write unit tests for finding severity and output**

Cover required strings/lists, unknown fields, URL schemes, arXiv filename/link parity, duplicates, year/date warnings, controlled tags, cross-axis collisions, description style, deterministic ordering, and exit codes.

**Step 2: Implement the read-only auditor**

Use documented dataclasses or simple typed records for findings. The command must never rewrite YAML. Support human-readable output and `--format json`.

**Step 3: Define hard errors versus warnings**

Structural impossibilities and broken identifiers are errors. Venue-year differences, soft tag vocabulary, and prose heuristics remain warnings.

**Step 4: Document use**

Explain that warnings route human review and are not permission for automatic metadata edits.

**Step 5: Verify via CI/user command**

```bash
python3 scripts/audit_catalog.py
python3 -m unittest tests.test_audit_catalog -v
```

Expected: the command reports the current catalog deterministically; tests pass.

**Step 6: Commit**

```bash
git add scripts/audit_catalog.py tests/test_audit_catalog.py audits/README.md CONTRIBUTING.md
git commit -m "feat: add read-only paper catalog auditor"
```

### Task 8: Define and validate per-paper evidence records

**Files:**
- Create: `audits/papers/_template.yaml.example`
- Create: `scripts/validate_audits.py`
- Create: `tests/test_validate_audits.py`
- Modify: `audits/README.md`

**Step 1: Specify the ledger schema**

Require paper ID, source URL/version, verification date, status, scope evidence, taxonomy rationales, content/link checks, confidence, unresolved questions, and reviewer provenance.

**Step 2: Write failing validation tests**

Cover missing evidence, invalid status/confidence, source/audit ID mismatch, duplicate audit IDs, unknown paper IDs, and complete-catalog parity mode.

**Step 3: Implement validation**

The validator supports partial coverage during migration and `--require-complete` for the final gate.

**Step 4: Verify via CI/user command**

```bash
python3 -m unittest tests.test_validate_audits -v
```

Expected: schema tests pass.

**Step 5: Commit**

```bash
git add audits/papers/_template.yaml.example scripts/validate_audits.py tests/test_validate_audits.py audits/README.md
git commit -m "feat: define paper evidence audit records"
```

### Task 9: Produce the machine-generated risk inventory

**Files:**
- Create: `audits/catalog-risk-report.json`
- Create: `audits/catalog-risk-report.md`

**Step 1: Run the auditor in report mode**

```bash
python3 scripts/audit_catalog.py --format json
```

Expected: deterministic findings covering every canonical paper.

**Step 2: Rank review batches**

Prioritize scope conflicts, multiple mechanism tags, cross-axis tag collisions, singleton tags, missing fields, and date/venue warnings.

**Step 3: Check report/source parity**

Confirm all canonical paper IDs occur in the inventory exactly once.

**Step 4: Commit**

```bash
git add audits/catalog-risk-report.json audits/catalog-risk-report.md
git commit -m "docs: add catalog audit risk inventory"
```

### Task 10: Verify high-risk papers against primary sources

**Files:**
- Create: `audits/papers/<paper-id>.yaml`
- Modify when evidence requires: `papers/<paper-id>.yaml`

**Step 1: Divide non-overlapping paper batches among research agents**

Each agent must use the canonical paper/PDF/project source, quote no more than needed, and record page/section/figure/equation-level evidence when the abstract does not prove the loop mechanism.

**Step 2: Review scope first**

Confirm the same learned internal module/operator is reused within one forward process. Mark unsupported entries for removal rather than stretching the taxonomy.

**Step 3: Review content and taxonomy**

Verify title, author order, dates/venue, description claims, category, foundation/must-read judgment, mechanism/focus/domain/alias tags, and link ownership.

**Step 4: Apply evidence-backed corrections**

Only change canonical YAML when the ledger explains the evidence. Keep unresolved claims explicitly unresolved.

**Step 5: Validate the batch**

```bash
python3 scripts/validate_audits.py
python3 scripts/audit_catalog.py
git diff --check
```

Expected: no structural errors; remaining warnings are documented.

**Step 6: Commit each review batch**

```bash
git add audits/papers papers
git commit -m "data: verify high-risk paper metadata batch"
```

### Task 11: Verify the remaining catalog

**Files:**
- Create: `audits/papers/<paper-id>.yaml`
- Modify when evidence requires: `papers/<paper-id>.yaml`

**Step 1: Continue disjoint batches of 15-25 papers**

Use the same evidence standard as Task 10. Agents return evidence records and proposed YAML corrections; the primary agent reviews every changed source file before integration.

**Step 2: Require complete parity**

Run externally or locally if approved:

```bash
python3 scripts/validate_audits.py --require-complete
```

Expected: every canonical paper has exactly one verified audit record or an explicit removal record.

**Step 3: Resolve all open high-severity findings**

No paper may remain `needs-review` when the overall goal is declared complete.

**Step 4: Commit each review batch**

```bash
git add audits/papers papers
git commit -m "data: verify paper catalog batch"
```

### Task 12: Regenerate outputs and perform completion verification

**Files:**
- Modify generated: `README.md`
- Modify generated: `TAGS.md`
- Modify generated: `papers.json`
- Modify generated: `submission-meta.json`

**Step 1: Regenerate through the canonical build**

Run externally under CI/Slurm policy:

```bash
python3 scripts/build.py
```

Expected: generated artifacts reflect canonical YAML and the new payload policy.

**Step 2: Run the complete verification suite externally**

```bash
python3 scripts/check_asset_budgets.py
python3 scripts/audit_catalog.py
python3 scripts/validate_audits.py --require-complete
python3 -m unittest discover -s tests -t . -p 'test_*.py'
git diff --check
```

Expected: all commands exit zero.

**Step 3: Perform browser verification**

Serve the repository locally and inspect initial catalog load, searching, tag/date/quick filters, category/table switching, briefing notice, submission duplicate checks, desktop/mobile layouts, and light/dark themes.

**Step 4: Compare performance evidence**

Update the baseline document with after-values and percentage reductions. Confirm the browser catalog payload, submission metadata, and first render are all improved without functionality loss.

**Step 5: Review the complete diff**

Confirm unrelated `figures/` and `loop_transformers_baseline_backbone_report.md` remain untouched.

**Step 6: Commit generated artifacts and final evidence**

```bash
git add README.md TAGS.md papers.json submission-meta.json docs/plans/2026-07-10-site-performance-baseline.md
git commit -m "chore: regenerate audited catalog artifacts"
```
