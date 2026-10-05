# Configure your own Nano4 site context

This distribution removes the original author's username, billing account,
socket paths, and workstation-specific absolute paths. Use the recipient's own
credentials and authorized project. Never assume shared documentation grants
access or permission to bill someone else's account.

## Establish non-secret configuration

Ask only for missing information; inspect the current project first:

- `NANO4_USER`: recipient's cluster username, not necessarily local `$USER`.
- `NANO4_LOGIN`: that username at `nano4.nchc.org.tw`.
- `NANO4_ACCOUNT`: the intended authorized Slurm billing account; verify association.
- `NANO4_SSH_SOCKET`: an owner-specific socket for this workstation/session.
- Local project directory and remote project root under `/work/{remote_user}`.
- Desired task, model/data locations, resource scope, and experiment command.

Keep those settings in the user's shell or private project configuration, not in
this shared package. Passwords, OTPs, keys, and tokens must not be added here.
Push MFA is the preferred login method unless the current user requests otherwise.

## Minimal project handoff

This skill bundle does not include the Book Agent pipeline or a Slurm wrapper.
An ordinary project only needs its own environment/data setup and executable
experiment command. Inspect its README and launcher rather than requiring the
original project's directory names. A single-node allocation template is below;
replace the account, paths, environment setup, and experiment before submission.
Create the log directory on the remote host before running sbatch.

```bash
#!/usr/bin/env bash
#SBATCH --account=YOUR_AUTHORIZED_PROJECT
#SBATCH --partition=dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=180G
#SBATCH --time=00:30:00
#SBATCH --output=/work/%u/logs/smoke-%j.out
#SBATCH --error=/work/%u/logs/smoke-%j.err
set -euo pipefail
cd "/work/${USER}/repos/YOUR_PROJECT"
# Activate your verified environment or run through the pinned container here.
python YOUR_EXPERIMENT.py
```

This is an allocation template, not a ready-to-run experiment or a command to
submit without authorization. Confirm live partition/QoS limits and the correct
GPU/CPU/memory request. The `8gpus` partition historically accepted one-GPU jobs;
the name is not a minimum allocation requirement.

## If the recipient has the original Book Agent repository

Inspect these paths relative to that project's root:

- `uni_agent_rollouts/nano4.toml`: stage resource definitions.
- `uni_agent_rollouts/scripts/run_nano4_inference.sh`: inference modes and preflight.
- `uni_agent_rollouts/scripts/run_nano4_colqwen.sh`: retriever setup/serve.
- `uni_agent_rollouts/scripts/run_nano4_colqwen_managed.sh`: helper watchdog.
- `uni_agent_rollouts/upstream.lock.json`: pinned environment/upstream revisions.

If the separate `nano4_exps/workflow/nano4.py` CLI is available, it supports
validate, doctor, sync, submit, status and logs. Inspect it before use: the
historical sync used `rsync --delete`, dry-run could create remote directories,
and status showed only live jobs. It is optional and not included in this package.

Retriever readiness is published in a job-local ready.json. Pass its current
private-IP URL using `BOOK_AGENT_COLQWEN_URL` on the remote submission side and
verify an actual query from the policy allocation. Upload/read back the consumer
job ID for the watchdog. Never copy an old service endpoint or socket blindly.

The original ColQwen adapter/index validation detected an incompatible checkpoint
key mapping; retain its tensor checks. Use separate retriever and policy GPU
allocations when the policy nearly fills its device. The qwen-sglang-mtp skill
documents the pinned stack and performance measurements independently of accounts.
