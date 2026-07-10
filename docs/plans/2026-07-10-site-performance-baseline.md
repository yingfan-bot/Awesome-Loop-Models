# Site Performance Baseline

## Measurement point

- Baseline first measured at: 2026-07-10 11:11:08 KST (+0900)
- Fixed-SHA measurements reproduced at: 2026-07-10 11:16:36 KST (+0900)
- Branch: `codex/site-performance-paper-audit`
- Baseline commit: `382914b56a104d82b103dad11cc6ff171b7c728e`
- Canonical paper YAML files (`papers/*.yaml`): 112

These values describe the checked-out files at the commit above, before the payload and initial-render changes in the site-performance implementation plan. The branch already includes commit `95501d9` (`perf: avoid hidden table rendering`).

## Artifact sizes

| Artifact | Uncompressed bytes | Gzip bytes | Additional detail |
|---|---:|---:|---|
| `index.html` | 134,931 | — | Inline CSS and JavaScript included |
| `submit.html` | 61,277 | — | Fetches the full catalog payload at this baseline |
| `papers.json` | 370,796 | 74,208 | `git show <baseline>:papers.json \| gzip -n -c` |
| `assets/favicon.png` | 89,103 | — | 512 × 512 pixels |

The four measured files total 656,107 uncompressed bytes. This total is a filesystem-size sum, not a network-transfer estimate.

## Briefing payload

- Briefing records in `papers.json`: 32
- Sum of `briefings[].content` JSON string lengths: 99,648 characters
- Concatenated `briefings[].content` UTF-8 size: 99,742 bytes

The character figure is the sum of jq string `length` values. The byte figure writes the same strings contiguously with `jq -j` and counts their UTF-8 bytes. Neither number includes JSON quotes, separators, field names, or escaping overhead. At this baseline, all historical briefing bodies are present in the browser payload even though the catalog only surfaces the latest briefing summary.

## Known render path

- During category-section construction, `createCategorySection()` immediately generates each paper grid with `renderCard()`. `createBlogSection()` does the same for blog cards.
- After section construction and initialization, the initial `doSearch()` call enters `renderAllGrids()` and generates the same grid cards again. The default first load therefore builds category/blog card markup once while constructing sections and once more during the initial search/render pass.
- The branch already uses lazy table rendering: `CURRENT_VIEW` starts as `category`, `renderAllGrids()` calls `renderTableView()` only when the active view is `table`, and it clears an existing table body while category view is active. The table body is therefore not populated on the default first load.

## Measurement commands

```sh
BASELINE=382914b56a104d82b103dad11cc6ff171b7c728e

git ls-tree --name-only "${BASELINE}:papers" \
  | awk '/\.yaml$/ { count++ } END { print count+0 }'

git cat-file -s "${BASELINE}:index.html"
git cat-file -s "${BASELINE}:submit.html"
git cat-file -s "${BASELINE}:papers.json"
git cat-file -s "${BASELINE}:assets/favicon.png"

git show "${BASELINE}:papers.json" | gzip -n -c | wc -c
git show "${BASELINE}:papers.json" | jq '.briefings | length'
git show "${BASELINE}:papers.json" \
  | jq '[.briefings[].content | length] | add'
git show "${BASELINE}:papers.json" \
  | jq -j '.briefings[].content' | wc -c

git show "${BASELINE}:assets/favicon.png" | file -

git show "${BASELINE}:index.html" \
  | rg -n "CURRENT_VIEW = 'category'|function renderAllGrids|function createCategorySection|function createBlogSection|grid.innerHTML|doSearch\(document|getElementById\('papers-table-body'\)|renderTableView"

git diff --check
```

Every content and size measurement above reads an object from the fixed baseline commit rather than the current worktree. `gzip -n` suppresses filename and timestamp metadata, making the compressed byte count reproducible for that blob. The favicon dimensions are read directly from the fixed-SHA blob through `file -`, so no temporary file is required. All commands completed successfully, and `git diff --check` reported no whitespace errors.
