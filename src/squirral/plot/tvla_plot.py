"""Plot helpers for TVLA results."""

from __future__ import annotations

import numpy as np
from matplotlib import pyplot as plt

from squirral.analysis.tvla import TVLAConfig, TVLAConvergenceResult


def plot_tvla_result(
    fixed_trace: np.ndarray,
    random_trace: np.ndarray,
    t_values: np.ndarray,
    leakage_points: np.ndarray,
    config: TVLAConfig,
    output_path: str,
    show_plot: bool = False,
) -> None:
    """Plot one fixed/random trace and corresponding T-test values."""

    sample_axis = np.arange(t_values.shape[0])
    encryption_end = t_values.shape[0] if config.encryption_end is None else config.encryption_end

    figure = plt.figure(figsize=(14, 8))

    ax1 = figure.add_subplot(2, 1, 1)
    ax1.plot(sample_axis, fixed_trace, linewidth=1.2, label="Fixed trace")
    ax1.plot(sample_axis, random_trace, linewidth=1.2, alpha=0.8, label="Random trace")
    ax1.axvline(config.encryption_start, color="green", linestyle="--", linewidth=1.5)
    ax1.axvline(encryption_end, color="orange", linestyle="--", linewidth=1.5)
    ax1.set_title(f"{config.algorithm} trace samples")
    ax1.set_ylabel("Amplitude")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="upper right")

    ax2 = figure.add_subplot(2, 1, 2)
    ax2.plot(sample_axis, t_values, color="black", linewidth=1.1, label="T-values")
    ax2.axhline(config.threshold, color="red", linestyle="-", linewidth=1.5)
    ax2.axhline(-config.threshold, color="red", linestyle="-", linewidth=1.5)
    ax2.axvline(config.encryption_start, color="green", linestyle="--", linewidth=1.5)
    ax2.axvline(encryption_end, color="orange", linestyle="--", linewidth=1.5)

    if leakage_points.size:
        ax2.scatter(
            leakage_points,
            t_values[leakage_points],
            s=8,
            color="crimson",
            alpha=0.8,
            label=f"Leakage ({leakage_points.size})",
        )

    ax2.set_title("TVLA T-test")
    ax2.set_xlabel("Sample index")
    ax2.set_ylabel("T-value")
    ax2.grid(alpha=0.3)
    ax2.legend(loc="upper right")

    figure.tight_layout()
    figure.savefig(output_path, dpi=220, bbox_inches="tight")

    if show_plot:
        plt.show()
    else:
        plt.close(figure)


def plot_convergence(
    convergence_result: TVLAConvergenceResult,
    config: TVLAConfig,
    output_path: str,
    show_plot: bool = False,
) -> None:
    """Plot convergence of max t-value with trace count."""

    figure = plt.figure(figsize=(10, 6))

    ax = figure.add_subplot(1, 1, 1)
    ax.plot(
        convergence_result.trace_counts,
        convergence_result.max_t_values,
        marker="o",
        markersize=4,
        linewidth=2,
        color="steelblue",
        label="Max |T-value|",
    )
    ax.plot(
        convergence_result.trace_counts,
        convergence_result.mean_t_values,
        marker="s",
        markersize=4,
        linewidth=2,
        color="coral",
        label="Mean |T-value|",
    )
    ax.axhline(config.threshold, color="red", linestyle="--", linewidth=1.5, label=f"Threshold ({config.threshold})")

    ax.set_title("TVLA Convergence Analysis")
    ax.set_xlabel("Number of traces per group")
    ax.set_ylabel("T-value")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")

    figure.tight_layout()
    figure.savefig(output_path, dpi=220, bbox_inches="tight")

    if show_plot:
        plt.show()
    else:
        plt.close(figure)
