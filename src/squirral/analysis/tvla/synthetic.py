"""Synthetic data generation for reproducible TVLA demos."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class SyntheticProfile:
    """Preset profile for synthetic dataset generation."""

    leakage_amplitude: float
    noise_std: float


PROFILE_PRESETS: dict[str, SyntheticProfile] = {
    "none": SyntheticProfile(leakage_amplitude=0.0, noise_std=1.0),
    "weak": SyntheticProfile(leakage_amplitude=0.6, noise_std=1.0),
    "medium": SyntheticProfile(leakage_amplitude=1.2, noise_std=1.0),
    "strong": SyntheticProfile(leakage_amplitude=2.0, noise_std=1.0),
}


def resolve_profile(profile: str) -> SyntheticProfile:
    """Resolve synthetic profile by name."""

    key = profile.strip().lower()
    if key not in PROFILE_PRESETS:
        raise ValueError(
            f"unsupported profile: {profile!r}. "
            f"available profiles: {', '.join(sorted(PROFILE_PRESETS))}"
        )
    return PROFILE_PRESETS[key]


def _generate_leakage_pattern(
    *,
    num_samples: int,
    leakage_start: int,
    leakage_end: int,
    leakage_amplitude: float,
    leakage_shape: str,
) -> np.ndarray:
    pattern = np.zeros(num_samples, dtype=np.float64)
    if leakage_end <= leakage_start or leakage_amplitude == 0.0:
        return pattern

    shape = leakage_shape.strip().lower()
    if shape == "step":
        pattern[leakage_start:leakage_end] = leakage_amplitude
        return pattern

    if shape == "gaussian":
        length = leakage_end - leakage_start
        x = np.linspace(-2.5, 2.5, num=length, dtype=np.float64)
        gaussian = np.exp(-(x**2))
        gaussian /= np.max(gaussian)
        pattern[leakage_start:leakage_end] = leakage_amplitude * gaussian
        return pattern

    raise ValueError("leakage_shape must be one of: step, gaussian")


def _apply_jittered_leakage(
    fixed_traces: np.ndarray,
    pattern: np.ndarray,
    *,
    leakage_start: int,
    leakage_end: int,
    jitter: int,
    rng: np.random.Generator,
) -> None:
    if np.all(pattern == 0.0):
        return

    if jitter <= 0:
        fixed_traces += pattern
        return

    window_len = leakage_end - leakage_start
    if window_len <= 0:
        return

    base_window = pattern[leakage_start:leakage_end]
    for trace_index in range(fixed_traces.shape[0]):
        shift = int(rng.integers(-jitter, jitter + 1))
        start = max(0, leakage_start + shift)
        end = min(fixed_traces.shape[1], start + window_len)
        effective = end - start
        if effective > 0:
            fixed_traces[trace_index, start:end] += base_window[:effective]


def generate_synthetic_tvla_dataset(
    num_traces: int = 2000,
    num_samples: int = 3000,
    leakage_start: int = 500,
    leakage_end: int = 900,
    leakage_amplitude: float = 1.2,
    noise_std: float = 1.0,
    leakage_shape: str = "step",
    jitter: int = 0,
    fixed_offset: float = 0.0,
    random_offset: float = 0.0,
    seed: int | None = 7,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic fixed/random trace groups for TVLA testing."""

    if num_traces < 2:
        raise ValueError("num_traces must be at least 2")
    if num_samples < 2:
        raise ValueError("num_samples must be at least 2")
    if not (0 <= leakage_start <= leakage_end <= num_samples):
        raise ValueError("leakage window is out of bounds")
    if jitter < 0:
        raise ValueError("jitter must be >= 0")
    if noise_std <= 0:
        raise ValueError("noise_std must be > 0")

    rng = np.random.default_rng(seed)
    random_traces = rng.normal(loc=0.0, scale=noise_std, size=(num_traces, num_samples))
    fixed_traces = rng.normal(loc=0.0, scale=noise_std, size=(num_traces, num_samples))

    leakage_pattern = _generate_leakage_pattern(
        num_samples=num_samples,
        leakage_start=leakage_start,
        leakage_end=leakage_end,
        leakage_amplitude=leakage_amplitude,
        leakage_shape=leakage_shape,
    )
    _apply_jittered_leakage(
        fixed_traces,
        leakage_pattern,
        leakage_start=leakage_start,
        leakage_end=leakage_end,
        jitter=jitter,
        rng=rng,
    )

    fixed_traces += fixed_offset
    random_traces += random_offset

    return fixed_traces.astype(np.float32, copy=False), random_traces.astype(np.float32, copy=False)


def build_labeled_traces(
    fixed_traces: np.ndarray,
    random_traces: np.ndarray,
    *,
    shuffle: bool = True,
    seed: int | None = 7,
) -> tuple[np.ndarray, np.ndarray]:
    """Build concatenated traces and labels from fixed/random groups."""

    fixed = np.asarray(fixed_traces)
    random = np.asarray(random_traces)
    if fixed.ndim != 2 or random.ndim != 2:
        raise ValueError("fixed_traces and random_traces must be 2D arrays")
    if fixed.shape[1] != random.shape[1]:
        raise ValueError("fixed_traces and random_traces must have the same sample length")

    traces = np.vstack([random, fixed]).astype(np.float32, copy=False)
    labels = np.concatenate(
        [
            np.zeros(random.shape[0], dtype=np.int8),
            np.ones(fixed.shape[0], dtype=np.int8),
        ]
    )

    if shuffle:
        rng = np.random.default_rng(seed)
        order = rng.permutation(traces.shape[0])
        traces = traces[order]
        labels = labels[order]

    return traces, labels
