"""Analysis modules."""

from .tvla import (
    TVLAAnalyzer,
    TVLAConfig,
    TVLAAnalysisResult,
    TVLAConvergenceResult,
    analyze_convergence,
    compute_welch_ttest,
    detect_leakage_points,
    SyntheticProfile,
    PROFILE_PRESETS,
    resolve_profile,
    generate_synthetic_tvla_dataset,
    build_labeled_traces,
    TVLAPipelineResult,
    run_tvla_pipeline,
)
from .cpa import CPAAnalyzer, CPAConfig, CPAAnalysisResult
from .dpa import DPAAnalyzer, DPAConfig, DPAAnalysisResult
from .lstm import LSTMAnalyzer, LSTMConfig, LSTMAnalysisResult

__all__ = [
    "TVLAAnalyzer",
    "TVLAConfig",
    "TVLAAnalysisResult",
    "TVLAConvergenceResult",
    "analyze_convergence",
    "compute_welch_ttest",
    "detect_leakage_points",
    "SyntheticProfile",
    "PROFILE_PRESETS",
    "resolve_profile",
    "generate_synthetic_tvla_dataset",
    "build_labeled_traces",
    "TVLAPipelineResult",
    "run_tvla_pipeline",
    "CPAAnalyzer",
    "CPAConfig",
    "CPAAnalysisResult",
    "DPAAnalyzer",
    "DPAConfig",
    "DPAAnalysisResult",
    "LSTMAnalyzer",
    "LSTMConfig",
    "LSTMAnalysisResult",
]
