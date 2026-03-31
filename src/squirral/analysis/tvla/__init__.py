"""TVLA analysis implementation."""

from .tvla_core import (
    TVLAConfig,
    TVLAAnalysisResult,
    TVLAConvergenceResult,
    TVLAAnalyzer,
    compute_welch_ttest,
    detect_leakage_points,
    analyze_convergence,
)
from .synthetic import (
    SyntheticProfile,
    PROFILE_PRESETS,
    resolve_profile,
    generate_synthetic_tvla_dataset,
    build_labeled_traces,
)
from .pipeline import TVLAPipelineResult, run_tvla_pipeline

__all__ = [
    "TVLAConfig",
    "TVLAAnalysisResult",
    "TVLAConvergenceResult",
    "TVLAAnalyzer",
    "compute_welch_ttest",
    "detect_leakage_points",
    "analyze_convergence",
    "SyntheticProfile",
    "PROFILE_PRESETS",
    "resolve_profile",
    "generate_synthetic_tvla_dataset",
    "build_labeled_traces",
    "TVLAPipelineResult",
    "run_tvla_pipeline",
]
