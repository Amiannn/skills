---
name: nano4-workflow
description: Connect to NCHC Nano4 with Push MFA, deploy projects, submit and monitor Slurm GPU jobs, and retrieve experiment artifacts. Use for Nano4 login, training or rollout deployment, job progress, and resource cleanup.
---

# Nano4 workflow

Operate Nano4 without confusing SSH access, scheduler success, and experiment success.
This skill is framework-independent: preserve the user's training or inference stack.

## Routing

- Before login, deployment, or job inspection, read [operations.md](references/operations.md).
- For recipient-specific accounts, paths, project setup, or Book Agent services,
  also read [local-site.md](references/local-site.md). Configure the recipient's
  environment instead of borrowing another user's account or filesystem paths.
- For Qwen native MTP configuration, use `qwen-sglang-mtp` if available; Nano4
  access alone does not require that skill.

## Boundaries and execution

1. Determine whether the request is status-only, deployment, or an authorized run.
   A status request does not authorize resubmission, cancellation, or a larger run.
2. Reuse a working authenticated SSH socket. Prefer the user's requested Push MFA
   when reauthentication is needed. Keep passwords, OTPs, tokens, and private keys
   out of skills, launch scripts, reports, and command-line arguments. Do not turn
   a password seen in old transcripts into a reusable credential store.
3. Confirm the remote identity, intended billing account, live partition limits,
   environment, data, and existing jobs before allocating GPUs. Historical account
   associations do not establish remaining credit or authorization.
4. Inspect local code/configuration first. Run heavy setup, model loading, training,
   and benchmarks inside an allocation, never on a login node. Use `/work/$USER`
   for large artifacts and caches, and a compute-local directory for scratch.
5. Review the sync plan, preserve remote artifacts and user changes, and record
   versions/hashes. The original project's optional workflow sync used `--delete`;
   inspect any installed wrapper before using it on a remote experiment directory.
6. Submit only the requested workload. Set required variables on the remote side
   before `sbatch`; local exports are not automatically forwarded by SSH. Record
   job IDs immediately and avoid duplicate submissions after a transport timeout.
7. Distinguish pending, engine startup, first model/tool activity, saved traces,
   and validated completion. When monitoring fails, report the last confirmed
   timestamp, not a guessed current state. An SSH failure does not imply a job died.
8. Preserve partial results and diagnose boundedly. Do not start an unbounded
   retry loop or repeatedly trigger MFA. Coordinate helper-service lifetime with
   the consuming job so paid GPUs are not stranded after success or failure.

## Handoff

Report the job ID, stage, node/GPU allocation if known, output path, last checked
time, completion/error counts, and any still-live helper service. For results,
include scheduler state and application validation separately. If blocked before
submission, explicitly say no job was launched. Do not quote money estimates as
actual billing without verified applicable pricing and allocation time.
