"""Unit tests for input loaders."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from squirral.io.loaders import load_trace_groups


class LoaderTests(unittest.TestCase):
    def test_load_npz_fixed_random(self) -> None:
        fixed = np.random.default_rng(0).normal(size=(10, 32)).astype(np.float32)
        random = np.random.default_rng(1).normal(size=(12, 32)).astype(np.float32)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "demo.npz"
            np.savez_compressed(path, fixed_traces=fixed, random_traces=random)

            fixed_loaded, random_loaded = load_trace_groups(path, "npz")

            self.assertEqual(fixed_loaded.shape, (10, 32))
            self.assertEqual(random_loaded.shape, (12, 32))


if __name__ == "__main__":
    unittest.main()
