"""Unit tests for dataset writing helpers."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from squirral.io.datasets import save_generation_metadata, save_synthetic_npz


class DatasetIOTests(unittest.TestCase):
    def test_save_npz_with_fixed_random(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "demo.npz"
            fixed = np.random.default_rng(0).normal(size=(8, 16)).astype(np.float32)
            random = np.random.default_rng(1).normal(size=(8, 16)).astype(np.float32)
            save_synthetic_npz(out, fixed_traces=fixed, random_traces=random)

            self.assertTrue(out.exists())
            with np.load(out, allow_pickle=False) as data:
                self.assertIn("fixed_traces", data.files)
                self.assertIn("random_traces", data.files)

    def test_save_generation_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "meta.json"
            payload = {"seed": 7, "profile": "medium", "schema": "both"}
            save_generation_metadata(out, payload)

            self.assertTrue(out.exists())
            loaded = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(loaded["seed"], 7)
            self.assertEqual(loaded["profile"], "medium")


if __name__ == "__main__":
    unittest.main()
