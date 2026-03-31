"""Reusable analysis pipeline helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from squirral.analysis.tvla.tvla_core import TVLAAnalysisResult, TVLAAnalyzer, TVLAConfig
from squirral.io.loaders import load_trace_groups


@dataclass(slots=True)
class TVLAPipelineResult:
    """Bundle containing analysis result and input traces."""

    analysis: TVLAAnalysisResult
    fixed_traces: np.ndarray
    random_traces: np.ndarray


def run_tvla_pipeline(
    *,
    input_path: str,
    input_format: str,
    config: TVLAConfig,
) -> TVLAPipelineResult:
    """Load traces and run TVLA with the provided config."""

    fixed_traces, random_traces = load_trace_groups(input_path, input_format)
    analyzer = TVLAAnalyzer(config)
    analysis = analyzer.analyze(
        fixed_traces=fixed_traces,
        random_traces=random_traces,
        input_path=input_path,
    )
    return TVLAPipelineResult(
        analysis=analysis,
        fixed_traces=fixed_traces,
        random_traces=random_traces,
    )
