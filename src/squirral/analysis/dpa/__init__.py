"""DPA (Differential Power Analysis) analyzer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np
from squirral.base import AnalysisResult, Analyzer


@dataclass
class DPAConfig:
    """Configuration for DPA analysis."""

    algorithm: str = "AES"
    target_byte: int = 0
    threshold: float = 0.05


@dataclass
class DPAAnalysisResult(AnalysisResult):
    """Result from DPA analysis."""

    differences: np.ndarray | None = None
    max_differences: np.ndarray | None = None

    method: str = "dpa"
    input_path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class DPAAnalyzer(Analyzer):
    """DPA (Differential Power Analysis) analyzer.

    Differential attack comparing traces with different intermediate values.
    """

    name = "dpa"
    description = "DPA - Differential Power Analysis"

    def __init__(self, config: dict[str, Any] | None = None):
        if config is None:
            config = {}
        if isinstance(config, dict):
            self.config = DPAConfig(**config)
        else:
            self.config = config

    def analyze(
        self,
        traces: np.ndarray,
        labels: np.ndarray | None = None,
        plaintext: np.ndarray | None = None,
        key: np.ndarray | None = None,
        **kwargs,
    ) -> DPAAnalysisResult:
        """Run DPA analysis.

        Args:
            traces: Power traces (num_traces, num_samples)
            plaintext: Plaintext data
            key: Key guess

        Returns:
            DPAAnalysisResult
        """
        raise NotImplementedError(
            "DPA analysis not yet implemented. "
            "This is a placeholder for future implementation."
        )

    def detect_leakage_points(
        self,
        result: DPAAnalysisResult,
        threshold: float | None = None,
    ) -> np.ndarray:
        """Detect leakage points from DPA result."""
        if threshold is None:
            threshold = self.config.threshold
        if result.max_differences is not None:
            return np.where(np.abs(result.max_differences) > threshold)[0]
        return np.array([], dtype=int)
