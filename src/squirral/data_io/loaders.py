"""Trace loading utilities."""

from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np
import zarr


def _normalize_labels(labels: np.ndarray) -> np.ndarray:
    flat = np.asarray(labels).reshape(-1)

    if flat.dtype.kind in {"S", "U", "O"}:
        mapped = np.zeros(flat.shape[0], dtype=np.int8)
        for index, value in enumerate(flat):
            text = str(value).strip().lower()
            if text in {"1", "fixed", "fix", "true"}:
                mapped[index] = 1
            elif text in {"0", "random", "rand", "false"}:
                mapped[index] = 0
            else:
                raise ValueError(f"unsupported label value: {value!r}")
        return mapped

    return flat.astype(np.int8, copy=False)


def _split_by_labels(traces: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if traces.shape[0] != labels.shape[0]:
        raise ValueError("trace count does not match label count")

    random_mask = labels == 0
    fixed_mask = labels == 1

    fixed = np.asarray(traces[fixed_mask], dtype=np.float64)
    random = np.asarray(traces[random_mask], dtype=np.float64)

    if fixed.size == 0 or random.size == 0:
        raise ValueError("both fixed and random groups are required")

    return fixed, random


def _load_ets_with_scared(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    import scared

    ths = scared.traces.read_ths_from_ets_file(str(path))
    traces = np.asarray(ths.samples[:], dtype=np.float64)

    if hasattr(ths, "set"):
        labels = _normalize_labels(np.asarray(ths.set))
    elif hasattr(ths, "metadata") and "set" in ths.metadata:
        labels = _normalize_labels(np.asarray(ths.metadata["set"]))
    else:
        raise ValueError("ETS data does not expose set labels")

    return _split_by_labels(traces, labels)


def _load_ets_with_h5(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    with h5py.File(path, "r") as ets_file:
        if "traces" not in ets_file:
            raise ValueError("ETS/HDF5 file does not contain 'traces' dataset")

        traces = np.asarray(ets_file["traces"][:], dtype=np.float64)

        labels = None
        if "metadata" in ets_file and "set" in ets_file["metadata"]:
            labels = np.asarray(ets_file["metadata"]["set"][:])
        elif "set" in ets_file:
            labels = np.asarray(ets_file["set"][:])

        if labels is None:
            raise ValueError("ETS/HDF5 file does not contain set labels")

    normalized = _normalize_labels(labels)
    return _split_by_labels(traces, normalized)


def load_ets(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load fixed/random trace groups from ETS format."""

    try:
        return _load_ets_with_scared(path)
    except Exception:
        return _load_ets_with_h5(path)


def load_zarr(path: str | Path, tile: str = "/0/0/") -> tuple[np.ndarray, np.ndarray]:
    """Load fixed/random trace groups from Zarr format.

    Expected Zarr structure:
        /0/0/traces     - (num_traces, num_samples)
        /0/0/labels     - labels (0=random, 1=fixed)
    """
    path = Path(path)
    z = zarr.open(str(path), mode="r")

    if f"{tile}traces" not in z:
        raise ValueError(f"Zarr file does not contain '{tile}traces' dataset")

    traces = np.asarray(z[f"{tile}traces"][:], dtype=np.float64)

    labels = None
    if f"{tile}labels" in z:
        labels = np.asarray(z[f"{tile}labels"][:])
    elif f"{tile}fixed" in z:
        fixed_arr = np.asarray(z[f"{tile}fixed"][:])
        random_arr = np.asarray(z[f"{tile}random"][:])
        labels = np.where(fixed_arr == 1, 1, 0)
        labels = np.where(random_arr == 1, 0, labels)
    elif f"{tile}set" in z:
        labels = np.asarray(z[f"{tile}set"][:])

    if labels is None:
        raise ValueError("Zarr file does not contain label information")

    normalized = _normalize_labels(labels)
    return _split_by_labels(traces, normalized)


def load_trace_groups(path: str | Path, input_format: str) -> tuple[np.ndarray, np.ndarray]:
    """Load fixed/random groups from the requested format."""

    fmt = input_format.lower().strip()
    if fmt == "ets":
        return load_ets(path)
    if fmt == "zarr":
        return load_zarr(path)

    raise ValueError(f"unsupported format: {input_format}. Use 'zarr' or 'ets'.")
