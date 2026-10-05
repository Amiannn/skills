# Completion, telemetry, and scaling

## Validate three separate layers

1. Scheduler: job state, exit code, allocation duration, helper cleanup.
2. Application: expected vs saved sessions, terminal reasons, nonempty KG, parse
   errors, request timeouts, validation output, task-specific quality.
3. Training artifacts / MTP: token arrays, response masks, logprobs, reward parity,
   request-level counters preserved through the entire Gateway chain.

In Book Agent, use the existing project validator after downloading a run:

```bash
python -m uni_agent_rollouts.validate_run RUN_DIR --expected 64 --require-mtp-telemetry
python -m uni_agent_rollouts.benchmark_report RUN_DIR --gpu-count 4
```

The validator requires every trace to end model_submit and can stop at the first
failure. A failure means later validations may not have run. Inspect all terminal
reasons separately with the skill's read-only summarize_run.py. Do not weaken the
validator merely to relabel a partially completed experiment successful.

## MTP counters

SGLang 0.5.12 returned `spec_num_proposed_drafts`, `spec_num_correct_drafts`, and
`spec_verify_ct`. The pinned verl adapter expected older names; a fallback once
mistook configured draft width for total proposed tokens. A plausible number is
not proof the telemetry is correct. The project's version-locked patches:

- `verl-sglang-0512-mtp-telemetry.patch`: map actual engine counter fields.
- `verl-mtp-resume-telemetry.patch`: accumulate partial-generation counters.
- `uni-agent-mtp-telemetry.patch`: preserve counters through Gateway, rollback,
  and materialized trajectory metadata.

For proposed drafts D, accepted drafts A, verification steps V:

```text
acceptance_rate = A / D
accepted_drafts_per_verify = A / V
accept_length = (A + V) / V
```

Require D > 0, V > 0, 0 <= A <= D, consistent reported rates, and for this tested
speculative path D >= V. Sum counters before computing aggregate rates, rather
than averaging per-request percentages. Acceptance length includes the extra
verified token; it is not the same as accepted drafts per verification.

## Historical benchmarks and limitations

Artifacts under `book-agent-lab/uni_agent_rollouts/artifacts/`:

| Run | Valid paths | Inference wall | Aggregate output tok/s |
| --- | --- | --- | --- |
| baseline 362890, 4 H200 | 15/16 | 4377.1 s | 348.20 |
| MTP2 363027, 4 H200 | 16/16 | 3187.1 s | 490.06 |
| MTP4 363175, 4 H200 | 16/16 | 2033.0 s | 741.32 |
| MTP4 + ColQwen 431114, 4 policy H200 | 54/64 | 33126.3 s | 181.48 |

The controlled 16-path benchmark observed 2.13x output throughput for MTP4 over
baseline, with approximately 82.23% draft acceptance and 98.87% peak GPU memory.
This is evidence for that workload, not a universal speedup or reasoning gain.
Earlier job 362873 had invalid MTP telemetry; do not use its acceptance results.

The 64-path job had 4 output_limit and 6 APITimeoutError terminal states; all
64 traces were saved but only 54 submitted normally. Mean reward was 0.6593,
including unfinished graphs. MTP counters remained valid (~82.50% acceptance).
Its lower throughput is an observed scaling problem, not proof that MTP failed
or that any single scheduling mechanism caused it. Toolset and concurrency also
differ from the older benchmark. Request timeout includes time spent waiting;
investigate before classifying it as a model or network fault.

## Diagnose throughput without using GPU percentage as the objective

- Separate model startup, prefill, decode, queue wait, tools, and tail latency.
- Compare output tokens divided by full inference wall time. Keep the narrower
  episode-window rate separate. Include completed trajectories per GPU-hour.
- Report completion rate and quality alongside speed; discarded/unfinished
  trajectories consume real compute too.
- Report per-replica load, prefix/cache behavior, context lengths and live-session
  vs active-request concurrency. More live sessions can increase queueing and
  cache pressure even if GPU-resident request count remains fixed.
- The report's active GPU utilization filters samples by memory >= 50% and
  power > 200 W. It is not the whole-job average. High active utilization is
  compatible with worse useful throughput.
- Four-policy-GPU rates exclude ColQwen's separate GPU. Include retriever, setup,
  startup, and idle allocation time when computing end-to-end GPU cost.
- Peak memory near 99% is not evidence of headroom for more active requests.
  Change concurrency, context, or memory settings in controlled tests rather
  than silently shrinking the experiment.

Keep workload, toolset, reward and sampling fixed for a performance comparison.
If investigating the 64-session slowdown, a bounded session-concurrency sweep is
a hypothesis test, not an already-proven fix. Do not attribute quality differences
to MTP from unpaired stochastic traces or lexical reward alone.
