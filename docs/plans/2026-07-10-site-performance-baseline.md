# Site Performance Baseline

## Measurement point

- Measured at: 2026-07-10 11:11:08 KST (+0900)
- Branch: `codex/site-performance-paper-audit`
- Baseline commit: `382914b56a104d82b103dad11cc6ff171b7c728e`
- Canonical paper YAML files (`papers/*.yaml`): 112

These values describe the checked-out files at the commit above, before the payload and initial-render changes in the site-performance implementation plan. The branch already includes commit `95501d9` (`perf: avoid hidden table rendering`).

## Artifact sizes

| Artifact | Uncompressed bytes | Gzip bytes | Additional detail |
|---|---:|---:|---|
| `index.html` | 134,931 | — | Inline CSS and JavaScript included |
| `submit.html` | 61,277 | — | Fetches the full catalog payload at this baseline |
| `papers.json` | 370,796 | 74,220 | `gzip -c papers.json` |
| `assets/favicon.png` | 89,103 | — | 512 × 512 pixels |

The four measured files total 656,107 uncompressed bytes. This total is a filesystem-size sum, not a network-transfer estimate.

## Briefing payload

- Briefing records in `papers.json`: 32
- Sum of `briefings[].content` JSON string lengths: 99,648 characters

The content figure is the result of jq string `length`, so it is a Unicode character count rather than the UTF-8 byte size of those fields. At this baseline, all historical briefing bodies are present in the browser payload even though the catalog only surfaces the latest briefing summary.

## Known render path

- During category-section construction, `createCategorySection()` immediately generates each paper grid with `renderCard()`. `createBlogSection()` does the same for blog cards.
- After section construction and initialization, the initial `doSearch()` call enters `renderAllGrids()` and generates the same grid cards again. The default first load therefore builds category/blog card markup once while constructing sections and once more during the initial search/render pass.
- The branch already uses lazy table rendering: `CURRENT_VIEW` starts as `category`, `renderAllGrids()` calls `renderTableView()` only when the active view is `table`, and it clears an existing table body while category view is active. The table body is therefore not populated on the default first load.

## Measurement commands

```text
find papers -maxdepth 1 -name '*.yaml' | wc -l
wc -c index.html submit.html papers.json assets/favicon.png
gzip -c papers.json | wc -c
jq '.briefings | length' papers.json
jq '[.briefings[].content | length] | add' papers.json
sips -g pixelWidth -g pixelHeight assets/favicon.png
git diff --check
```

All commands completed successfully, and `git diff --check` reported no whitespace errors.
