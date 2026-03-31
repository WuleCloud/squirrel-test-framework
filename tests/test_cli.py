"""Integration-style test for CLI entrypoint."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from squirral.cli import main


class CLITests(unittest.TestCase):
    @staticmethod
    def _build_dataset(path: Path) -> None:
        rng = np.random.default_rng(42)
        fixed = rng.normal(size=(200, 256)).astype(np.float32)
        random = rng.normal(size=(200, 256)).astype(np.float32)
        fixed[:, 80:120] += 1.3
        np.savez_compressed(path, fixed_traces=fixed, random_traces=random)

    def test_tvla_run_creates_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            dataset = tmp / "dataset.npz"
            output_dir = tmp / "out"
            self._build_dataset(dataset)

            exit_code = main(
                [
                    "tvla",
                    "run",
                    "--input",
                    str(dataset),
                    "--format",
                    "npz",
                    "--output-dir",
                    str(output_dir),
                    "--encryption-start",
                    "80",
                    "--encryption-end",
                    "120",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "tvla_report.json").exists())
            self.assertTrue((output_dir / "tvla_plot.png").exists())

            report = json.loads((output_dir / "tvla_report.json").read_text(encoding="utf-8"))
            self.assertGreater(report["total_leakage_points"], 0)

    def test_tvla_report_only_creates_report_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            dataset = tmp / "dataset.npz"
            report_file = tmp / "reports" / "summary.json"
            self._build_dataset(dataset)

            exit_code = main(
                [
                    "tvla",
                    "report-only",
                    "--input",
                    str(dataset),
                    "--format",
                    "npz",
                    "--output",
                    str(report_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(report_file.exists())
            report = json.loads(report_file.read_text(encoding="utf-8"))
            self.assertGreater(report["leakage_during_encryption"], 0)

    def test_tvla_plot_only_creates_plot_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            dataset = tmp / "dataset.npz"
            plot_file = tmp / "plots" / "result.png"
            self._build_dataset(dataset)

            exit_code = main(
                [
                    "tvla",
                    "plot-only",
                    "--input",
                    str(dataset),
                    "--format",
                    "npz",
                    "--output",
                    str(plot_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(plot_file.exists())

    def test_missing_input_file_returns_error_code(self) -> None:
        with patch("sys.stderr") as fake_stderr:
            exit_code = main(
                [
                    "tvla",
                    "run",
                    "--input",
                    "/tmp/not_exist_dataset_for_scatoolbox.npz",
                    "--format",
                    "npz",
                ]
            )
            self.assertEqual(exit_code, 2)
            self.assertTrue(fake_stderr.write.called)


if __name__ == "__main__":
    unittest.main()
