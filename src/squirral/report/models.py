"""Data models for TVLA reporting."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class TVLAReport:
    """Structured report generated from a TVLA run."""

    algorithm: str
    input_path: str
    threshold: float
    total_samples: int
    trace_count_fixed: int
    trace_count_random: int
    encryption_range_start: int
    encryption_range_end: int
    ttest_min: float
    ttest_max: float
    ttest_mean_abs: float
    total_leakage_points: int
    leakage_before_encryption: int
    leakage_during_encryption: int
    leakage_after_encryption: int
    leakage_points: list[int]
    first_leakage_point: int | None
    first_leakage_tvalue: float | None
    first_encryption_leakage_point: int | None
    first_encryption_leakage_tvalue: float | None
    generated_at_utc: str

    @classmethod
    def now_utc(cls) -> str:
        """Return a stable UTC timestamp string."""

        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def to_dict(self) -> dict:
        """Convert the report to a JSON-serializable dictionary."""

        return asdict(self)
