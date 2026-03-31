#!/usr/bin/env python3
"""Generate synthetic TVLA dataset for demos/tests."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np

from squirral.analysis.tvla import (
    PROFILE_PRESETS,
    build_labeled_traces,
    generate_synthetic_tvla_dataset,
    resolve_profile,
)
from squirral.io.datasets import save_generation_metadata, save_synthetic_zarr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic TVLA NPZ dataset with reproducible metadata"
    )
    parser.add_argument("--output", required=True, help="Output Zarr path")
    parser.add_argument(
        "--schema",
        choices=["fixed-random", "labeled", "both"],
        default="both",
        help="Dataset schema: fixed/random arrays, labeled arrays, or both",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILE_PRESETS.keys()),
        default="medium",
        help="Preset generation profile",
    )
    # These parameters can also be set via environment variables:
    #   NUM_TRACES, NUM_SAMPLES, LEAKAGE_START, LEAKAGE_END
    parser.add_argument("--num-traces", type=int, default=None, help="Trace count per group (or use NUM_TRACES env var)")
    parser.add_argument("--num-samples", type=int, default=None, help="Sample count per trace (or use NUM_SAMPLES env var)")
    parser.add_argument("--leakage-start", type=int, default=None, help="Leakage start index (or use LEAKAGE_START env var)")
    parser.add_argument("--leakage-end", type=int, default=None, help="Leakage end index (or use LEAKAGE_END env var)")
    parser.add_argument(
        "--leakage-shape",
        choices=["step", "gaussian"],
        default="step",
        help="Leakage pattern shape inside leakage window",
    )
    parser.add_argument(
        "--leakage-amplitude",
        type=float,
        default=None,
        help="Leakage amplitude (override profile default)",
    )
    parser.add_argument(
        "--noise-std",
        type=float,
        default=None,
        help="Noise std deviation (override profile default)",
    )
    parser.add_argument("--jitter", type=int, default=0, help="Per-trace leakage window jitter (samples)")
    parser.add_argument("--fixed-offset", type=float, default=0.0, help="DC offset added to fixed traces")
    parser.add_argument("--random-offset", type=float, default=0.0, help="DC offset added to random traces")
    parser.add_argument(
        "--no-shuffle",
        action="store_true",
        help="Keep group order when generating labeled schema",
    )
    parser.add_argument("--seed", type=int, default=7, help="Random seed")
    parser.add_argument(
        "--metadata",
        default=None,
        help="Output metadata JSON path (default: <output>.meta.json)",
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Do not write metadata JSON",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    # Apply environment variable overrides with bash-style defaults
    num_traces = int(os.environ["NUM_TRACES"]) if "NUM_TRACES" in os.environ else (args.num_traces if args.num_traces is not None else 2000)
    num_samples = int(os.environ["NUM_SAMPLES"]) if "NUM_SAMPLES" in os.environ else (args.num_samples if args.num_samples is not None else 3000)
    leakage_start = int(os.environ["LEAKAGE_START"]) if "LEAKAGE_START" in os.environ else (args.leakage_start if args.leakage_start is not None else 500)
    leakage_end = int(os.environ["LEAKAGE_END"]) if "LEAKAGE_END" in os.environ else (args.leakage_end if args.leakage_end is not None else 900)
    profile = resolve_profile(args.profile)
    leakage_amplitude = (
        profile.leakage_amplitude if args.leakage_amplitude is None else args.leakage_amplitude
    )
    noise_std = profile.noise_std if args.noise_std is None else args.noise_std

    fixed, random = generate_synthetic_tvla_dataset(
        num_traces=num_traces,
        num_samples=num_samples,
        leakage_start=leakage_start,
        leakage_end=leakage_end,
        leakage_amplitude=leakage_amplitude,
        noise_std=noise_std,
        leakage_shape=args.leakage_shape,
        jitter=args.jitter,
        fixed_offset=args.fixed_offset,
        random_offset=args.random_offset,
        seed=args.seed,
    )

    traces = None
    labels = None
    if args.schema in {"labeled", "both"}:
        traces, labels = build_labeled_traces(
            fixed_traces=fixed,
            random_traces=random,
            shuffle=not args.no_shuffle,
            seed=args.seed,
        )

    output = save_synthetic_zarr(
        args.output,
        fixed_traces=fixed if args.schema in {"fixed-random", "both"} else None,
        random_traces=random if args.schema in {"fixed-random", "both"} else None,
        traces=traces if args.schema in {"labeled", "both"} else None,
        labels=labels if args.schema in {"labeled", "both"} else None,
        extra_arrays={
            "leakage_window": np.array([leakage_start, leakage_end], dtype=np.int32),
            "seed": np.array([args.seed], dtype=np.int32),
        },
    )

    metadata_path = None
    if not args.no_metadata:
        output_path = Path(output)
        metadata_path = Path(args.metadata) if args.metadata else output_path.with_suffix(".meta.json")
        metadata = {
            "generator": "squirral.synthetic.v1",
            "output_path": str(output_path),
            "format": "zarr",
            "schema": args.schema,
            "profile": args.profile,
            "seed": args.seed,
            "num_traces_per_group": num_traces,
            "num_samples_per_trace": num_samples,
            "leakage_window": [leakage_start, leakage_end],
            "leakage_shape": args.leakage_shape,
            "leakage_amplitude": float(leakage_amplitude),
            "noise_std": float(noise_std),
            "jitter": int(args.jitter),
            "fixed_offset": float(args.fixed_offset),
            "random_offset": float(args.random_offset),
            "ground_truth": {
                "has_leakage": bool(leakage_amplitude != 0.0 and leakage_end > leakage_start),
                "target_group": "fixed",
                "target_metric": "mean_shift",
            },
            "zarr_arrays": {
                "fixed_traces": args.schema in {"fixed-random", "both"},
                "random_traces": args.schema in {"fixed-random", "both"},
                "traces": args.schema in {"labeled", "both"},
                "labels": args.schema in {"labeled", "both"},
            },
        }
        save_generation_metadata(metadata_path, metadata)

    print(f"Saved dataset: {output}")
    print(f"fixed_traces shape:  {fixed.shape}")
    print(f"random_traces shape: {random.shape}")
    print(f"leakage window:      [{leakage_start}, {leakage_end})")
    print(f"profile:             {args.profile}")
    print(f"schema:              {args.schema}")
    if args.schema in {"labeled", "both"} and traces is not None and labels is not None:
        print(f"labeled traces:      {traces.shape}")
        print(f"labels shape:        {labels.shape}")
        print(f"shuffle labels:      {not args.no_shuffle}")
    if metadata_path is not None:
        print(f"metadata:            {metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
