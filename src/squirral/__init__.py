"""Squirral - Side Channel Analysis Toolbox."""

from .base import AnalysisResult, Analyzer, Squirral, TraceDataset

__all__ = [
    "AnalysisResult",
    "Analyzer",
    "Squirral",
    "TraceDataset",
    "TVLAAnalyzer",
    "TVLAConfig",
]
__version__ = "0.1.0"

from .analysis import (
    TVLAAnalyzer,
    TVLAConfig,
    CPAAnalyzer,
    DPAAnalyzer,
    LSTMAnalyzer,
)
