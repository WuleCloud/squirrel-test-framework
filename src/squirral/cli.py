"""Command line interface for Squirral."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from squirral.analysis.tvla import run_tvla_pipeline
from squirral.analysis.tvla import TVLAConfig
from squirral.plot.tvla_plot import plot_tvla_result


def _build_tvla_config(args: argparse.Namespace) -> TVLAConfig:
    return TVLAConfig(
        algorithm=args.algorithm,
        threshold=args.threshold,
        encryption_start=args.encryption_start,
        encryption_end=args.encryption_end,
    )


def _run_analysis(args: argparse.Namespace):
    return run_tvla_pipeline(
        input_path=str(args.input),
        input_format=args.format,
        config=_build_tvla_config(args),
    )


def _write_report(report, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _resolve_trace_index(trace_index: int, fixed_count: int, random_count: int) -> int:
    return max(0, min(trace_index, fixed_count - 1, random_count - 1))


def _write_plot(analysis_bundle, args: argparse.Namespace, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_index = _resolve_trace_index(
        args.trace_index,
        analysis_bundle.fixed_traces.shape[0],
        analysis_bundle.random_traces.shape[0],
    )
    plot_tvla_result(
        fixed_trace=analysis_bundle.fixed_traces[resolved_index],
        random_trace=analysis_bundle.random_traces[resolved_index],
        t_values=analysis_bundle.analysis.t_values,
        leakage_points=analysis_bundle.analysis.leakage_points,
        config=_build_tvla_config(args),
        output_path=str(output_path),
        show_plot=args.show_plot,
    )


def _run_tvla_command(args: argparse.Namespace) -> int:
    analysis_bundle = _run_analysis(args)
    output_dir = Path(args.output_dir)
    report_path = output_dir / "tvla_report.json"
    plot_path = output_dir / "tvla_plot.png"

    _write_report(analysis_bundle.analysis.report, report_path)
    _write_plot(analysis_bundle, args, plot_path)

    print(f"Report saved: {report_path}")
    print(f"Plot saved:   {plot_path}")
    print(f"Leakage points: {analysis_bundle.analysis.report.total_leakage_points}")
    return 0


def _report_only_command(args: argparse.Namespace) -> int:
    analysis_bundle = _run_analysis(args)
    output_path = Path(args.output)
    _write_report(analysis_bundle.analysis.report, output_path)
    print(f"Report saved: {output_path}")
    print(f"Leakage points: {analysis_bundle.analysis.report.total_leakage_points}")
    return 0


def _plot_only_command(args: argparse.Namespace) -> int:
    analysis_bundle = _run_analysis(args)
    output_path = Path(args.output)
    _write_plot(analysis_bundle, args, output_path)
    print(f"Plot saved: {output_path}")
    print(f"Leakage points: {analysis_bundle.analysis.report.total_leakage_points}")
    return 0


def _add_common_tvla_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", required=True, help="Input trace file path")
    parser.add_argument("--format", choices=["zarr", "ets"], default="zarr", help="Input file format")
    parser.add_argument("--algorithm", default="AES", help="Algorithm name for reporting")
    parser.add_argument("--threshold", type=float, default=4.5, help="TVLA threshold")
    parser.add_argument("--encryption-start", type=int, default=0, help="Encryption start index")
    parser.add_argument(
        "--encryption-end",
        type=int,
        default=None,
        help="Encryption end index (default: trace length)",
    )
    parser.add_argument("--trace-index", type=int, default=0, help="Trace index used in plot")
    parser.add_argument("--show-plot", action="store_true", help="Display plot window")


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""

    parser = argparse.ArgumentParser(prog="squirral", description="Squirral CLI")
    subparsers = parser.add_subparsers(dest="command")

    tvla_parser = subparsers.add_parser("tvla", help="TVLA analysis commands")
    tvla_subparsers = tvla_parser.add_subparsers(dest="tvla_command")

    run_parser = tvla_subparsers.add_parser("run", help="Run TVLA analysis")
    _add_common_tvla_arguments(run_parser)
    run_parser.add_argument("--output-dir", default="./out", help="Output directory")
    run_parser.set_defaults(handler=_run_tvla_command)

    report_parser = tvla_subparsers.add_parser("report-only", help="Run TVLA and generate JSON report only")
    _add_common_tvla_arguments(report_parser)
    report_parser.add_argument("--output", default="./out/tvla_report.json", help="Output report file path")
    report_parser.set_defaults(handler=_report_only_command)

    plot_parser = tvla_subparsers.add_parser("plot-only", help="Run TVLA and generate plot only")
    _add_common_tvla_arguments(plot_parser)
    plot_parser.add_argument("--output", default="./out/tvla_plot.png", help="Output plot file path")
    plot_parser.set_defaults(handler=_plot_only_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return 1

    try:
        return args.handler(args)
    except FileNotFoundError as exc:
        print(f"[SCAToolBox] input file error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"[SCAToolBox] invalid input: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"[SCAToolBox] runtime error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
