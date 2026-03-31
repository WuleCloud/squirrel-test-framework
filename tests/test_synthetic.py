"""Unit tests for synthetic dataset generation utilities."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from squirral.analysis.synthetic import (
    build_labeled_traces,
    generate_synthetic_tvla_dataset,
    resolve_profile,
)


class SyntheticGenerationTests(unittest.TestCase):
    def test_resolve_profile(self) -> None:
        profile = resolve_profile("weak")
        self.assertGreater(profile.noise_std, 0.0)
        self.assertGreater(profile.leakage_amplitude, 0.0)

    def test_generate_gaussian_with_jitter(self) -> None:
        fixed, random = generate_synthetic_tvla_dataset(
            num_traces=200,
            num_samples=512,
            leakage_start=120,
            leakage_end=200,
            leakage_amplitude=1.0,
            leakage_shape="gaussian",
            jitter=2,
            seed=9,
        )

        self.assertEqual(fixed.shape, (200, 512))
        self.assertEqual(random.shape, (200, 512))

        mean_delta = np.mean(fixed[:, 120:200] - random[:, 120:200])
        self.assertGreater(mean_delta, 0.1)

    def test_build_labeled_traces(self) -> None:
        fixed, random = generate_synthetic_tvla_dataset(
            num_traces=32,
            num_samples=128,
            leakage_start=32,
            leakage_end=64,
            leakage_amplitude=1.0,
            seed=11,
        )

        traces, labels = build_labeled_traces(fixed, random, shuffle=False)
        self.assertEqual(traces.shape, (64, 128))
        self.assertEqual(labels.shape, (64,))
        self.assertEqual(np.sum(labels == 1), 32)
        self.assertEqual(np.sum(labels == 0), 32)


if __name__ == "__main__":
    unittest.main()
