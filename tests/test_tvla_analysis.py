"""Unit tests for TVLA analysis."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from squirral.analysis.synthetic import generate_synthetic_tvla_dataset
from squirral.analysis.tvla import TVLAAnalyzer, TVLAConfig


class TVLAAnalysisTests(unittest.TestCase):
    def test_detects_leakage_in_expected_region(self) -> None:
        fixed, random = generate_synthetic_tvla_dataset(
            num_traces=600,
            num_samples=1200,
            leakage_start=300,
            leakage_end=500,
            leakage_amplitude=1.5,
            seed=123,
        )

        analyzer = TVLAAnalyzer(
            TVLAConfig(
                algorithm="AES",
                threshold=4.5,
                encryption_start=300,
                encryption_end=500,
            )
        )
        result = analyzer.analyze(fixed, random, input_path="synthetic")

        self.assertGreater(result.report.total_leakage_points, 0)
        self.assertGreater(result.report.leakage_during_encryption, 0)
        self.assertGreater(result.report.leakage_during_encryption, result.report.leakage_before_encryption)
        self.assertEqual(result.report.total_samples, 1200)


if __name__ == "__main__":
    unittest.main()
