# Catalog risk inventory

Generated on: 2026-07-10
Catalog snapshot: 82086af08e53421c3cb92b97e0b9d1acf40c2b4a
Generator: scripts/build_catalog_risk_report.py v2
Canonical papers: 109

## What this report establishes

This is a deterministic review queue for the canonical papers/*.yaml catalog. It combines the read-only structural auditor with explicit risk heuristics; it does not establish that a paper is in scope, that its description is faithful, or that its taxonomy is semantically correct.

At this snapshot, scripts/audit_catalog.py reports **0 errors / 8 warnings**. Every semantic conclusion still requires manual review against the primary paper source. This inventory does not auto-fix YAML and must not be used as evidence for automatic tag or content changes.

## Priority rules

- **P0:** at least one auditor error.
- **P1:** not P0, and either more than one mechanism_tags value or membership in the manual scope-review seed set.
- **P2:** not P0/P1, and either an auditor warning or an exact domain_tags/tags value that occurs once in the full catalog.
- **P3:** all remaining papers.
- Reasons are deduplicated and sorted lexicographically. Singleton frequency uses one combined domain_tags plus tags table and is exact and case-sensitive across all 109 canonical records; the two axes are not counted separately.

Batch sizes: **P0 0 / P1 15 / P2 73 / P3 21**.

The manual scope-review seeds are scheduling inputs only, not findings or conclusions: 2601.21582, 2604.27981, 2605.17811. A seed paper may be accurate and in scope; the label only says to check the primary source early.

A publication year/date warning is also not an automatic correction. The catalog year may intentionally represent a venue year while published_date records an earlier preprint date, so venue and primary-source evidence must be checked before editing either field.

## P0 — structural blockers

| Paper | Auditor findings | Required review |
| --- | --- | --- |

## P1 — early semantic review

| Paper | Reasons |
| --- | --- |
| 2506.21734 | multiple-mechanism-tags |
| 2510.24824 | multiple-mechanism-tags |
| 2601.21582 | manual-scope-review-seed<br>singleton-alias-tag:Dreamer |
| 2603.08082 | multiple-mechanism-tags |
| 2604.14442 | multiple-mechanism-tags<br>singleton-alias-tag:hierarchical-recurrence<br>singleton-alias-tag:universal-transformer |
| 2604.27981 | manual-scope-review-seed |
| 2605.07277 | multiple-mechanism-tags<br>singleton-alias-tag:weight-tying |
| 2605.12466 | multiple-mechanism-tags |
| 2605.17811 | manual-scope-review-seed<br>multiple-mechanism-tags |
| 2605.19376 | multiple-mechanism-tags<br>singleton-alias-tag:GRAM |
| 2605.20613 | multiple-mechanism-tags<br>singleton-alias-tag:HRM-Text<br>singleton-alias-tag:PrefixLM |
| 2605.20784 | multiple-mechanism-tags |
| 2605.21488 | multiple-mechanism-tags<br>singleton-alias-tag:EqR |
| 2606.18023 | multiple-mechanism-tags<br>singleton-alias-tag:LoopCoder-v2 |
| 2606.18206 | multiple-mechanism-tags |

P1 reasons are review triggers, not evidence of an error. In particular, multiple mechanism tags can be legitimate when the paper genuinely combines mechanisms.

## P2 and P3 coverage

### P2 — 73 papers

Warnings and singleton vocabulary require human judgment. A singleton tag can be precise and valid; frequency alone is never a reason to rename or remove it.

- 1511.08228, 1807.03819, 2006.08656, 2111.05177, 2209.11142, 2301.13196, 2310.10845, 2311.12424, 2402.13572, 2405.16039, 2410.01405, 2410.20672
- 2502.07827, 2502.17416, 2507.02199, 2507.07996, 2507.10524, 2511.08577, 2512.14693, 2602.05999, 2602.07845, 2602.08864, 2602.09080, 2602.10520
- 2602.11451, 2602.11698, 2603.01914, 2603.04971, 2603.05234, 2603.08391, 2603.19714, 2603.21676, 2604.07822, 2604.09168, 2604.09870, 2604.11279
- 2604.12946, 2604.15259, 2604.18839, 2604.21106, 2604.21254, 2604.21999, 2604.25551, 2605.06510, 2605.07721, 2605.09226, 2605.11011, 2605.18464
- 2605.18797, 2605.19705, 2605.19943, 2605.20389, 2605.23872, 2605.26106, 2605.26733, 2605.30215, 2605.31215, 2606.01495, 2606.03287, 2606.04438
- 2606.04678, 2606.06245, 2606.06574, 2606.14498, 2606.18208, 2606.22462, 2606.26488, 2606.31779, 2606.31796, 2607.00341, 2607.02491, openreview-chaingpt
- openreview-modr

### P3 — 21 papers

P3 is lower heuristic risk, not verified accuracy. These papers still need primary-source content and taxonomy review.

- 1603.08983, 1909.01377, 2502.05171, 2509.23314, 2510.04871, 2510.25741, 2511.07384, 2604.11791, 2604.17224, 2605.06609, 2605.09165, 2605.12578
- 2605.16048, 2605.20670, 2605.28919, 2605.30757, 2606.00114, 2606.00605, 2606.03741, 2606.18524, 2606.29983

## Review order and evidence requirement

1. **P0:** resolve structural blockers only after checking the primary source and recording evidence.
2. **P1:** review manual scope seeds and multi-mechanism classifications against the paper method, equations, and experiments.
3. **P2:** adjudicate auditor warnings and singleton vocabulary; preserve intentional venue-year differences and precise rare tags.
4. **P3:** complete the remaining paper-by-paper content and taxonomy review.

For every paper, use the canonical primary paper rather than a title, search snippet, run name, or this heuristic report. Record source version, locator, scope evidence, taxonomy rationale, and content checks in audits/papers before changing canonical metadata. No item in this report authorizes an automatic fix.
