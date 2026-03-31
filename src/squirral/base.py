"""Squirral - Side Channel Analysis Toolbox.

Unified framework for TVLA, CPA, DPA, and deep learning based side-channel attacks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class AnalysisResult:
    """Base class for all analysis results."""

    method: str
    input_path: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceDataset:
    """Container for trace data."""

    fixed_traces: np.ndarray | None = None
    random_traces: np.ndarray | None = None
    traces: np.ndarray | None = None
    labels: np.ndarray | None = None
    plaintext: np.ndarray | None = None
    key: np.ndarray | None = None
    ciphertext: np.ndarray | None = None


class Analyzer:
    """Base class for all side-channel analysis methods.

    Subclasses must implement:
    - analyze() method
    - detect_leakage_points() method (optional)
    """

    name: str = "base"
    description: str = "Base analyzer"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate analyzer configuration. Override in subclasses."""
        pass

    def analyze(
        self,
        traces: np.ndarray,
        labels: np.ndarray | None = None,
        plaintext: np.ndarray | None = None,
        key: np.ndarray | None = None,
        **kwargs,
    ) -> AnalysisResult:
        """Run analysis on traces.

        Args:
            traces: Trace data (num_traces, num_samples)
            labels: Trace labels (num_traces,)
            plaintext: Plaintext data
            key: Key data

        Returns:
            AnalysisResult subclass instance
        """
        raise NotImplementedError("Subclasses must implement analyze()")

    def detect_leakage_points(
        self,
        result: AnalysisResult,
        threshold: float | None = None,
    ) -> np.ndarray:
        """Detect leakage points from analysis result.

        Args:
            result: Analysis result
            threshold: Detection threshold

        Returns:
            Array of leakage point indices
        """
        raise NotImplementedError("Subclasses must implement detect_leakage_points()")

    @staticmethod
    def load_traces(path: str | Path, format: str = "zarr") -> TraceDataset:
        """Load traces from file.

        Args:
            path: Input file path
            format: File format (zarr, npz, ets, h5)

        Returns:
            TraceDataset
        """
        from squirral.io.loaders import load_trace_groups

        fixed, random = load_trace_groups(path, format)
        return TraceDataset(fixed_traces=fixed, random_traces=random)

    @staticmethod
    def save_traces(
        dataset: TraceDataset,
        path: str | Path,
        format: str = "zarr",
    ) -> Path:
        """Save traces to file.

        Args:
            dataset: TraceDataset to save
            path: Output file path
            format: Output format

        Returns:
            Output path
        """
        from squirral.io.datasets import save_synthetic_zarr

        if format == "zarr":
            return save_synthetic_zarr(
                path,
                fixed_traces=dataset.fixed_traces,
                random_traces=dataset.random_traces,
                traces=dataset.traces,
                labels=dataset.labels,
            )
        else:
            raise ValueError(f"Unsupported format: {format}")


class Squirral:
    """Unified interface for Squirral analysis methods.

    Usage:
        squirral = Squirral()
        result = squirral.run("tvla", traces, labels)
        result = squirral.run("cpa", traces, plaintext)
    """

    def __init__(self):
        self._analyzers: dict[str, type[Analyzer]] = {}
        self._register_default_analyzers()

    def _register_default_analyzers(self) -> None:
        """Register built-in analyzers."""
        from squirral.analysis.tvla import TVLAAnalyzer

        self.register("tvla", TVLAAnalyzer)

    def register(self, name: str, analyzer_class: type[Analyzer]) -> None:
        """Register a new analyzer.

        Args:
            name: Analyzer name (e.g., "tvla", "cpa")
            analyzer_class: Analyzer class
        """
        self._analyzers[name.lower()] = analyzer_class

    def get_analyzer(self, name: str, **config) -> Analyzer:
        """Get analyzer by name.

        Args:
            name: Analyzer name
            **config: Analyzer configuration

        Returns:
            Analyzer instance
        """
        name = name.lower()
        if name not in self._analyzers:
            available = list(self._analyzers.keys())
            raise ValueError(f"Unknown analyzer: {name}. Available: {available}")
        return self._analyzers[name](config)

    def run(
        self,
        method: str,
        traces: np.ndarray,
        labels: np.ndarray | None = None,
        plaintext: np.ndarray | None = None,
        key: np.ndarray | None = None,
        **kwargs,
    ) -> AnalysisResult:
        """Run analysis.

        Args:
            method: Analysis method ("tvla", "cpa", etc.)
            traces: Trace data
            labels: Labels (for TVLA)
            plaintext: Plaintext (for CPA)
            key: Key data

        Returns:
            AnalysisResult
        """
        analyzer = self.get_analyzer(method)
        return analyzer.analyze(traces, labels, plaintext, key, **kwargs)

    def list_methods(self) -> list[str]:
        """List available analysis methods."""
        return list(self._analyzers.keys())


__all__ = [
    "AnalysisResult",
    "Analyzer",
    "Squirral",
    "TraceDataset",
]
