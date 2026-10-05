---
name: qwen-sglang-mtp
description: Configure and evaluate Qwen native MTP speculative decoding with SGLang, including Uni-Agent/verl rollout integration, context and memory limits, and acceptance telemetry. Use for MTP2/MTP4 setup, debugging, or throughput benchmarking.
---

# Qwen + SGLang native MTP

Reuse the verified local MTP path without treating its parameters as universal
Qwen defaults. This skill configures inference acceleration, not RL optimization.

## Required routing

- Before changing launch configuration read [verified-stack.md](references/verified-stack.md).
- For performance comparisons, scaling, completion audits, or a slowdown read
  [measurement.md](references/measurement.md).
- For Nano4 login/allocation use `nano4-workflow` if available. On other hardware
  follow the site's existing allocation workflow, not Nano4-specific defaults.

## Workflow

1. Identify the exact checkpoint/revision, architecture, SGLang version, container,
   and harness. The reference Qwen/Qwen3.8-27B model ID comes from local logs;
   verify its availability and native MTP support for a new setup. Do not replace
   the user's requested model or assume every Qwen checkpoint has an MTP head.
2. Reproduce the pinned setup when asked to reproduce prior runs. For a new stack,
   inspect installed `sglang.launch_server --help`, model configuration, and
   official version-specific docs. NEXTN/MTP flags and scheduler constraints
   can change. Separate native MTP from methods needing a separate draft model.
3. Prefer existing library features and the project's launcher. Keep patches
   narrowly version-locked; require `git apply --check` or an already-applied
   reverse check. Do not upgrade a shared environment to make a patch apply.
4. Separate live agent-session concurrency from GPU-resident generation requests.
   Our validated H200 configuration allowed two active requests per GPU even when
   many agent sessions were waiting. More sessions are not automatically faster.
5. Preserve task prompt, tools, reward, sampling, model precision, and context
   policy for a decoding comparison. Treat context protocol headroom as accounting,
   not permission to silently shorten the user's reading task.
6. Verify effective runtime settings and real output: complete tool conversations,
   parseable tool calls, saved token IDs/masks/logprobs, and valid MTP counters.
   Engine readiness and high GPU utilization alone are insufficient.
7. Start with a scoped smoke for an unverified configuration. Expand only to the
   authorized batch. Preserve failing traces and report the failed fraction.
   Do not infer that acceptance rate or speculative speedup improves KG quality.

## Read-only artifact audit

Run `python scripts/summarize_run.py /path/to/downloaded/run` relative to this
skill directory. It summarizes saved Book Agent terminal states, rewards,
tool usage, and declared benchmark metrics without changing files, authenticating,
starting GPUs, or claiming a full semantic/token-alignment validation.

The project has a stricter validator and reporter; see measurement.md. Hand off
effective MTP settings, workload/concurrency, completion count, tokens/s, GPU-hour
denominator, memory headroom, and any telemetry or inference/train mismatch.
