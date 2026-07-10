"""Contract tests for deterministic static-site asset budgets."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import check_asset_budgets


def write_json(path: Path, payload: object) -> None:
    """Write a deterministic JSON fixture to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def write_valid_fixture(root: Path) -> None:
    """Create the smallest valid repository fixture for the budget checker."""
    write_json(
        root / "papers.json",
        {
            "papers": [],
            "blogs": [],
            "briefings": [{"date": "2026-07-10", "title": "Latest briefing"}],
        },
    )
    write_json(
        root / "submission-meta.json",
        {
            "existing_paths": [],
            "tag_inventories": {
                "mechanism": [],
                "focus": [],
                "domain": [],
            },
        },
    )
    favicon_path = root / "assets" / "favicon.png"
    favicon_path.parent.mkdir(parents=True, exist_ok=True)
    favicon_path.write_bytes(b"fixture favicon")


def deterministic_noise(length: int) -> str:
    """Return deterministic, poorly compressible ASCII text of ``length`` characters."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    state = 0xC0FFEE
    characters = []
    for _ in range(length):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        characters.append(alphabet[state % len(alphabet)])
    return "".join(characters)


def measurement(report: check_asset_budgets.AssetBudgetReport, name: str) -> int | None:
    """Return the measured value for ``name`` from an asset-budget report."""
    return next(item.measured for item in report.measurements if item.name == name)


class AssetBudgetContractTests(unittest.TestCase):
    """Exercise every byte and schema contract enforced by the checker."""

    def test_valid_fixture_passes_every_budget(self):
        """A minimal valid fixture should satisfy every configured budget."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)

            report = check_asset_budgets.check_asset_budgets(root)

        self.assertTrue(report.ok, report.violations)
        self.assertEqual(
            {item.name for item in report.measurements},
            {
                "papers.json raw bytes",
                "papers.json deterministic gzip bytes",
                "papers.json briefing count",
                "papers.json briefing content fields",
                "submission-meta.json raw bytes",
                "assets/favicon.png raw bytes",
            },
        )

    def test_rejects_papers_raw_bytes_over_limit(self):
        """The raw papers catalog should fail independently of its gzip size."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            write_json(root / "papers.json", {"briefings": [], "padding": "x" * 260_000})

            report = check_asset_budgets.check_asset_budgets(root)

        self.assertGreater(
            measurement(report, "papers.json raw bytes"),
            check_asset_budgets.PAPERS_RAW_BYTES_LIMIT,
        )
        self.assertLessEqual(
            measurement(report, "papers.json deterministic gzip bytes"),
            check_asset_budgets.PAPERS_GZIP_BYTES_LIMIT,
        )
        self.assertIn("papers.json raw bytes", "\n".join(report.violations))

    def test_rejects_papers_gzip_bytes_over_limit(self):
        """The deterministic gzip budget should catch a high-entropy catalog."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            write_json(
                root / "papers.json",
                {"briefings": [], "padding": deterministic_noise(140_000)},
            )

            report = check_asset_budgets.check_asset_budgets(root)

        self.assertLessEqual(
            measurement(report, "papers.json raw bytes"),
            check_asset_budgets.PAPERS_RAW_BYTES_LIMIT,
        )
        self.assertGreater(
            measurement(report, "papers.json deterministic gzip bytes"),
            check_asset_budgets.PAPERS_GZIP_BYTES_LIMIT,
        )
        self.assertIn("papers.json deterministic gzip bytes", "\n".join(report.violations))

    def test_rejects_submission_metadata_over_limit(self):
        """Oversized but schema-valid submission metadata should fail its byte budget."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            write_json(
                root / "submission-meta.json",
                {
                    "existing_paths": [f"papers/{index:05d}.yaml" for index in range(1_500)],
                    "tag_inventories": {
                        "mechanism": [],
                        "focus": [],
                        "domain": [],
                    },
                },
            )

            report = check_asset_budgets.check_asset_budgets(root)

        self.assertGreater(
            measurement(report, "submission-meta.json raw bytes"),
            check_asset_budgets.SUBMISSION_META_BYTES_LIMIT,
        )
        self.assertIn("submission-meta.json raw bytes", "\n".join(report.violations))

    def test_rejects_favicon_over_limit(self):
        """An oversized favicon should fail without affecting JSON validation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            (root / "assets" / "favicon.png").write_bytes(
                b"x" * (check_asset_budgets.FAVICON_BYTES_LIMIT + 1)
            )

            report = check_asset_budgets.check_asset_budgets(root)

        self.assertIn("assets/favicon.png raw bytes", "\n".join(report.violations))

    def test_rejects_more_than_one_browser_briefing(self):
        """The browser payload should contain at most the latest briefing."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            write_json(
                root / "papers.json",
                {"briefings": [{"date": "2026-07-10"}, {"date": "2026-07-09"}]},
            )

            report = check_asset_budgets.check_asset_budgets(root)

        self.assertEqual(measurement(report, "papers.json briefing count"), 2)
        self.assertIn("papers.json briefing count", "\n".join(report.violations))

    def test_rejects_briefing_content_field(self):
        """Rendered briefing Markdown must stay out of the browser catalog."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            write_json(
                root / "papers.json",
                {"briefings": [{"date": "2026-07-10", "content": "Too much text"}]},
            )

            report = check_asset_budgets.check_asset_budgets(root)

        self.assertEqual(measurement(report, "papers.json briefing content fields"), 1)
        self.assertIn("must not contain a 'content' field", "\n".join(report.violations))

    def test_reports_missing_and_malformed_json_clearly(self):
        """Missing and malformed JSON files should be reported in one run."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            (root / "papers.json").unlink()
            (root / "submission-meta.json").write_text("{not-json", encoding="utf-8")

            report = check_asset_budgets.check_asset_budgets(root)

        violations = "\n".join(report.violations)
        self.assertIn("papers.json: missing required file", violations)
        self.assertIn("submission-meta.json: invalid JSON", violations)

    def test_reports_all_schema_violations_in_one_run(self):
        """Invalid top-level and submission schemas should not stop later checks."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            write_json(root / "papers.json", [])
            write_json(root / "submission-meta.json", {"existing_paths": "not-a-list"})

            report = check_asset_budgets.check_asset_budgets(root)

        violations = "\n".join(report.violations)
        self.assertIn("papers.json: top-level JSON value must be an object", violations)
        self.assertIn("submission-meta.json.existing_paths must be an array", violations)
        self.assertIn("submission-meta.json.tag_inventories must be an object", violations)

    def test_cli_prints_measurements_and_returns_zero_on_success(self):
        """The CLI should print measured/limit rows and return zero on success."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = check_asset_budgets.main(["--root", str(root)])

        rendered = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("measured=", rendered)
        self.assertIn("limit=", rendered)
        self.assertIn("Asset budgets: PASS", rendered)

    def test_cli_lists_all_violations_and_returns_nonzero(self):
        """The CLI should aggregate failures and return nonzero when any budget fails."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_valid_fixture(root)
            write_json(
                root / "papers.json",
                {
                    "briefings": [
                        {"content": "first"},
                        {"content": "second"},
                    ]
                },
            )
            (root / "assets" / "favicon.png").write_bytes(
                b"x" * (check_asset_budgets.FAVICON_BYTES_LIMIT + 1)
            )
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = check_asset_budgets.main(["--root", str(root)])

        rendered = output.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("papers.json briefing count", rendered)
        self.assertIn("must not contain a 'content' field", rendered)
        self.assertIn("assets/favicon.png raw bytes", rendered)
        self.assertIn("Asset budgets: FAIL", rendered)


if __name__ == "__main__":
    unittest.main()
