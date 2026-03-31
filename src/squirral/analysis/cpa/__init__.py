"""CPA (Correlation Power Analysis) analyzer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from squirral.base import AnalysisResult, Analyzer


@dataclass
class CPAConfig:
    """Configuration for CPA analysis."""

    algorithm: str = "AES"
    model: str = "hamming_weight"
    byte_idx: int = 0
    threshold: float = 0.1


@dataclass
class CPAAnalysisResult(AnalysisResult):
    """Result from CPA analysis."""

    correlations: np.ndarray | None = None
    max_correlations: np.ndarray | None = None
    key_guess: np.ndarray | None = None

    method: str = "cpa"
    input_path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class CPAAnalyzer(Analyzer):
    """CPA (Correlation Power Analysis) analyzer.

    Correlation-based attack using power consumption models.
    """

    name = "cpa"
    description = "CPA - Correlation Power Analysis"

    def __init__(self, config: dict[str, Any] | None = None):
        if config is None:
            config = {}
        if isinstance(config, dict):
            self.config = CPAConfig(**config)
        else:
            self.config = config

    def _validate_config(self) -> None:
        if self.config.threshold <= 0:
            raise ValueError("threshold must be positive")

    def analyze(
        self,
        traces: np.ndarray,
        labels: np.ndarray | None = None,
        plaintext: np.ndarray | None = None,
        key: np.ndarray | None = None,
        **kwargs,
    ) -> CPAAnalysisResult:
        """Run CPA analysis.

        Args:
            traces: Power traces (num_traces, num_samples)
            plaintext: Plaintext data (num_traces, 16)
            key: Known key (optional)

        Returns:
            CPAAnalysisResult
        """
        raise NotImplementedError(
            "CPA analysis not yet implemented. "
            "This is a placeholder for future implementation."
        )

    def detect_leakage_points(
        self,
        result: CPAAnalysisResult,
        threshold: float | None = None,
    ) -> np.ndarray:
        """Detect leakage points from CPA result."""
        if threshold is None:
            threshold = self.config.threshold
        if result.max_correlations is not None:
            return np.where(np.abs(result.max_correlations) > threshold)[0]
        return np.array([], dtype=int)
