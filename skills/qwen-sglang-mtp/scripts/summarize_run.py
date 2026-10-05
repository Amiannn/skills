#!/usr/bin/env python3
"""Read-only summary of downloaded Book Agent runs; not a semantic validator."""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics


def summarize(root: Path) -> dict:
    paths = sorted((root / "book-traces").glob("**/simulation-*.json"))
    if not paths:
        raise ValueError(f"No Book Agent traces in {root / 'book-traces'}")
    traces = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    ids = [t["id"] for t in traces]
    reasons = Counter(t["terminal_state"].get("terminal_reason", "unknown") for t in traces)
    submitted = [t for t in traces if t["terminal_state"].get("terminal_reason") == "model_submit"]
    scores = [float(t["reward"]["total"]) for t in traces]
    result = {
        "run_dir": str(root.resolve()),
        "saved_traces": len(traces),
        "duplicate_simulation_ids": sorted(k for k, n in Counter(ids).items() if n > 1),
        "terminal_counts": dict(reasons),
        "submitted_nonempty_graphs": sum(all(t["terminal_state"].get("graph", {}).get(k)
                                            for k in ("nodes", "edges", "evidence")) for t in submitted),
        "mean_reward_all": statistics.fmean(scores),
        "mean_reward_submitted": statistics.fmean(float(t["reward"]["total"]) for t in submitted) if submitted else None,
        "tool_calls": dict(Counter(a.get("tool", "unknown") for t in traces for a in t.get("actions", []))),
        "search_using_traces": sum(any(a.get("tool") == "search_book" for a in t.get("actions", [])) for t in traces),
        "provider_error_trace_ids": [t["id"] for t in traces if t["terminal_state"].get("terminal_reason") == "provider_error"],
        "traces_with_provider_diagnostics": [t["id"] for t in traces if t["terminal_state"].get("provider_errors")],
    }
    benchmark = root / "benchmark-summary.json"
    if benchmark.exists():
        data = json.loads(benchmark.read_text(encoding="utf-8"))
        result["reported_benchmark"] = {k: data.get(k) for k in (
            "inference_wall_seconds", "output_tokens", "gateway_model_tokens",
            "aggregate_output_tokens_per_second", "valid_trajectories_per_gpu_hour",
            "speculative_decoding", "gpu")}
    validation = root / "validation-status.txt"
    result["saved_validation_status"] = validation.read_text().strip() if validation.exists() else "not recorded"
    result["scope"] = "Artifact summary only; does not verify token alignment, reward semantics, or live scheduler state. Benchmark metrics are reported, not independently revalidated."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    try:
        result = summarize(args.run_dir)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Cannot summarize run: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
