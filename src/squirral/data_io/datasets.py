"""Dataset writing helpers for synthetic generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import zarr


def save_synthetic_zarr(
    output_path: str | Path,
    *,
    fixed_traces: np.ndarray | None = None,
    random_traces: np.ndarray | None = None,
    traces: np.ndarray | None = None,
    labels: np.ndarray | None = None,
    extra_arrays: dict[str, np.ndarray] | None = None,
    tile: str = "/0/0/",
) -> Path:
    """Save synthetic dataset in Zarr format.

    Zarr structure:
        /0/0/traces        - combined traces (if traces provided)
        /0/0/labels       - labels (0=random, 1=fixed)
        /0/0/fixed_traces - fixed group traces (optional)
        /0/0/random_traces - random group traces (optional)
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    store = zarr.DirectoryStore(str(path))
    root = zarr.group(store=store, overwrite=True)

    if traces is not None and labels is not None:
        root.create_dataset(f"{tile}traces", data=np.asarray(traces))
        root.create_dataset(f"{tile}labels", data=np.asarray(labels))

    if fixed_traces is not None:
        root.create_dataset(f"{tile}fixed_traces", data=np.asarray(fixed_traces))
    if random_traces is not None:
        root.create_dataset(f"{tile}random_traces", data=np.asarray(random_traces))

    if extra_arrays:
        for key, value in extra_arrays.items():
            root.create_dataset(f"{tile}{key}", data=np.asarray(value))

    root.attrs["squirral_version"] = "0.1.0"
    return path


def save_generation_metadata(
    metadata_path: str | Path,
    metadata: dict[str, Any],
) -> Path:
    """Save metadata JSON for generated dataset."""

    path = Path(metadata_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
