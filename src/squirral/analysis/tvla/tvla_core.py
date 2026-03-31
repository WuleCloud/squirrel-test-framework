"""TVLA (Test Vector Leakage Assessment) analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from squirral.base import AnalysisResult, Analyzer
from squirral.report.models import TVLAReport


@dataclass
class TVLAConfig:
    """Configuration for TVLA analysis."""

    algorithm: str = "AES"
    threshold: float = 4.5
    encryption_start: int = 0
    encryption_end: int | None = None


@dataclass
class TVLAAnalysisResult(AnalysisResult):
    """Result from TVLA analysis."""

    t_values: np.ndarray | None = None
    leakage_points: np.ndarray | None = None
    report: TVLAReport | None = None

    method: str = "tvla"
    input_path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TVLAConvergenceResult:
    """Result for trace count convergence analysis."""

    trace_counts: np.ndarray
    max_t_values: np.ndarray
    mean_t_values: np.ndarray


def _validate_traces(
    fixed_traces: np.ndarray,
    random_traces: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    fixed = np.asarray(fixed_traces, dtype=np.float64)
    random = np.asarray(random_traces, dtype=np.float64)

    if fixed.ndim != 2 or random.ndim != 2:
        raise ValueError("fixed_traces and random_traces must be 2D arrays")
    if fixed.shape[1] != random.shape[1]:
        raise ValueError("fixed_traces and random_traces must have same sample length")
    if fixed.shape[0] < 2 or random.shape[0] < 2:
        raise ValueError("each trace group must include at least 2 traces")

    return fixed, random


def compute_welch_ttest(
    fixed_traces: np.ndarray,
    random_traces: np.ndarray,
) -> np.ndarray:
    """Compute point-wise Welch's t-test between fixed and random traces."""

    fixed, random = _validate_traces(fixed_traces, random_traces)

    mean_fixed = np.mean(fixed, axis=0)
    mean_random = np.mean(random, axis=0)

    var_fixed = np.var(fixed, axis=0, ddof=1)
    var_random = np.var(random, axis=0, ddof=1)

    n_fixed = fixed.shape[0]
    n_random = random.shape[0]

    denominator = np.sqrt(var_fixed / n_fixed + var_random / n_random)
    with np.errstate(divide="ignore", invalid="ignore"):
        t_values = np.divide(
            mean_fixed - mean_random,
            denominator,
            out=np.zeros_like(mean_fixed),
            where=denominator > 0,
        )

    return t_values


def detect_leakage_points(t_values: np.ndarray, threshold: float) -> np.ndarray:
    """Return indexes where |t| > threshold."""

    values = np.asarray(t_values, dtype=np.float64)
    return np.flatnonzero(np.abs(values) > threshold)


class TVLAAnalyzer(Analyzer):
    """TVLA (Test Vector Leakage Assessment) analyzer.

    Implements Welch's t-test based leakage detection.
    """

    name = "tvla"
    description = "TVLA - Test Vector Leakage Assessment using Welch's t-test"

    def __init__(self, config: dict[str, Any] | None = None):
        if config is None:
            config = {}
        if isinstance(config, dict):
            self.config = TVLAConfig(**config)
        else:
            self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        if self.config.threshold <= 0:
            raise ValueError("threshold must be positive")

    def analyze(
        self,
        traces: np.ndarray | None = None,
        labels: np.ndarray | None = None,
        plaintext: np.ndarray | None = None,
        key: np.ndarray | None = None,
        fixed_traces: np.ndarray | None = None,
        random_traces: np.ndarray | None = None,
        input_path: str = "",
        **kwargs,
    ) -> TVLAAnalysisResult:
        """Run TVLA analysis.

        Args:
            traces: Combined traces (num_traces, num_samples)
            labels: Labels (0=random, 1=fixed)
            fixed_traces: Fixed group traces
            random_traces: Random group traces
            input_path: Input file path

        Returns:
            TVLAAnalysisResult
        """
        if fixed_traces is not None and random_traces is not None:
            fixed, random = _validate_traces(fixed_traces, random_traces)
        elif traces is not None and labels is not None:
            random_mask = labels == 0
            fixed_mask = labels == 1
            fixed = np.asarray(traces[fixed_mask], dtype=np.float64)
            random = np.asarray(traces[random_mask], dtype=np.float64)
        else:
            raise ValueError("Must provide fixed_traces/random_traces or traces/labels")

        t_values = compute_welch_ttest(fixed, random)
        leakage_points = detect_leakage_points(t_values, self.config.threshold)

        total_samples = int(t_values.shape[0])
        encryption_end = (
            total_samples if self.config.encryption_end is None else int(self.config.encryption_end)
        )
        encryption_start = int(self.config.encryption_start)

        before_mask = leakage_points < encryption_start
        during_mask = (leakage_points >= encryption_start) & (leakage_points < encryption_end)
        after_mask = leakage_points >= encryption_end

        first_leakage = int(leakage_points[0]) if leakage_points.size else None
        first_tval = float(t_values[first_leakage]) if first_leakage is not None else None

        enc_leakage = leakage_points[during_mask]
        first_enc = int(enc_leakage[0]) if enc_leakage.size else None
        first_enc_tval = float(t_values[first_enc]) if first_enc is not None else None

        report = TVLAReport(
            algorithm=self.config.algorithm,
            input_path=input_path,
            threshold=float(self.config.threshold),
            total_samples=total_samples,
            trace_count_fixed=int(fixed.shape[0]),
            trace_count_random=int(random.shape[0]),
            encryption_range_start=encryption_start,
            encryption_range_end=encryption_end,
            ttest_min=float(np.min(t_values)),
            ttest_max=float(np.max(t_values)),
            ttest_mean_abs=float(np.mean(np.abs(t_values))),
            total_leakage_points=int(leakage_points.size),
            leakage_before_encryption=int(np.sum(before_mask)),
            leakage_during_encryption=int(np.sum(during_mask)),
            leakage_after_encryption=int(np.sum(after_mask)),
            leakage_points=leakage_points.astype(int).tolist(),
            first_leakage_point=first_leakage,
            first_leakage_tvalue=first_tval,
            first_encryption_leakage_point=first_enc,
            first_encryption_leakage_tvalue=first_enc_tval,
            generated_at_utc=TVLAReport.now_utc(),
        )

        return TVLAAnalysisResult(
            method="tvla",
            input_path=input_path,
            t_values=t_values,
            leakage_points=leakage_points,
            report=report,
            metadata={
                "algorithm": self.config.algorithm,
                "threshold": self.config.threshold,
                "trace_count_fixed": int(fixed.shape[0]),
                "trace_count_random": int(random.shape[0]),
            },
        )

    def detect_leakage_points(
        self,
        result: TVLAAnalysisResult,
        threshold: float | None = None,
    ) -> np.ndarray:
        """Detect leakage points from TVLA result."""
        if threshold is None:
            threshold = self.config.threshold
        if result.t_values is not None:
            return detect_leakage_points(result.t_values, threshold)
        return np.array([], dtype=int)


def analyze_convergence(
    fixed_traces: np.ndarray,
    random_traces: np.ndarray,
    *,
    max_trace_counts: int | None = None,
    num_steps: int = 20,
    seed: int | None = 42,
) -> TVLAConvergenceResult:
    """Analyze how max t-value changes with trace count."""

    fixed = np.asarray(fixed_traces, dtype=np.float64)
    random = np.asarray(random_traces, dtype=np.float64)

    max_traces = min(fixed.shape[0], random.shape[0])
    if max_trace_counts is not None:
        max_traces = min(max_traces, max_trace_counts)

    trace_counts = np.linspace(10, max_traces, num=num_steps, dtype=int)
    trace_counts = np.unique(trace_counts)

    max_t_values = np.zeros(len(trace_counts), dtype=np.float64)
    mean_t_values = np.zeros(len(trace_counts), dtype=np.float64)

    rng = np.random.default_rng(seed)

    for i, n in enumerate(trace_counts):
        idx_fixed = rng.choice(fixed.shape[0], size=n, replace=False)
        idx_random = rng.choice(random.shape[0], size=n, replace=False)

        subset_fixed = fixed[idx_fixed]
        subset_random = random[idx_random]

        t_values = compute_welch_ttest(subset_fixed, subset_random)
        max_t_values[i] = np.max(np.abs(t_values))
        mean_t_values[i] = np.mean(np.abs(t_values))

    return TVLAConvergenceResult(
        trace_counts=trace_counts,
        max_t_values=max_t_values,
        mean_t_values=mean_t_values,
    )
