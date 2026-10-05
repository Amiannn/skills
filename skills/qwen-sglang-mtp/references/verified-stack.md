# Verified stack and launch configuration

## Provenance

Recorded Oct 5, 2026 from the local Book Agent implementation and saved runs.
Project root: the recipient's own checkout of `book-agent-lab`, if available.
Remote historical project: `/work/{user}/repos/book-agent-qwen38`.
Do not assume this repository is bundled with the skill on another machine.

Authoritative local files to inspect before an execution change:

- `uni_agent_rollouts/upstream.lock.json`
- `uni_agent_rollouts/launch_inference.py`
- `uni_agent_rollouts/scripts/run_nano4_inference.sh`
- `uni_agent_rollouts/scripts/setup_nano4.sh`
- `uni_agent_rollouts/patches/*.patch`
- `uni_agent_rollouts/task_config.world-history.yaml`

Verified upstream pins:

- Uni-Agent: `89733ec81a69c3cc93ac90479de7ea7f01e51c1f`
- bundled verl: `fefb080262e1c015a0ea05f958822a6a512dc795`
- image tag `verlai/verl:sgl0512.dev4`, digest
  `sha256:89641f08fe51b0b73a7abaaa77d7e1fab1b0f0e76027e627bee7debf2ac13ce7`
- local runtime SGLang 0.5.12; historical model `Qwen/Qwen3.8-27B`
- Apptainer image `/work/{user}/containers/verl-sgl0512-dev4.sif`
- policy venv `/work/{user}/envs/book-agent-uni-89733ec8`

The local model ID is an observed artifact, not a claim that public model support
is unchanged. If adopting another Qwen model, recheck architecture and MTP weights.

## Native MTP settings for this pinned stack

| Setting | MTP2 | MTP4 |
| --- | --- | --- |
| Algorithm | NEXTN | NEXTN |
| Speculative steps | 1 | 3 |
| Draft tokens | 2 | 4 |
| EAGLE top-k | 1 | 1 |
| SGLANG_ENABLE_SPEC_V2 | 1 | 1 |
| mamba_scheduler_strategy | extra_buffer | extra_buffer |
| Active requests per policy GPU | 2 | 2 |

In this implementation top-k=1 requires draft width = steps + 1; incompatible
values were silently adjusted by the engine. Hybrid DeltaNet/Mamba state with
RadixCache and native MTP required `extra_buffer` in this stack. Do not apply
those constraints blindly to a different architecture or version.

The launcher maps configuration into:

- `actor_rollout_ref.model.mtp.{enable,enable_rollout}=true`
- `actor_rollout_ref.model.mtp.enable_train=false`
- `actor_rollout_ref.model.mtp.speculative_algorithm=NEXTN`
- `actor_rollout_ref.model.mtp.speculative_num_steps=3`
- `actor_rollout_ref.model.mtp.speculative_num_draft_tokens=4`
- `actor_rollout_ref.model.mtp.speculative_eagle_topk=1`
- `actor_rollout_ref.rollout.max_num_seqs=2`
- `actor_rollout_ref.rollout.engine_kwargs.sglang.mamba_scheduler_strategy=extra_buffer`
- environment `SGLANG_ENABLE_SPEC_V2=1`

These are verl/Uni-Agent keys, not direct standalone SGLang CLI flags. Read the
installed server's help for standalone flags; do not paste this YAML shape into
an unrelated harness. Our rollout used tensor parallel size 1 and four separate
policy GPU replicas for the larger benchmark, not four-way TP for one replica.

## Existing launch modes

`run_nano4_inference.sh` supports smoke (2, baseline), smoke_mtp (2, MTP4),
benchmark16_baseline, benchmark16_mtp2, benchmark16_mtp4, and benchmark (64).

Important: plain `benchmark` defaults MTP OFF unless explicitly enabled in the
remote submission environment. For the historical 64-path MTP4 configuration:

```bash
export BOOK_AGENT_MTP_ENABLE=1
export BOOK_AGENT_MTP_NUM_DRAFT_TOKENS=4
export BOOK_AGENT_MTP_NUM_STEPS=3
export BOOK_AGENT_MAX_RUNNING_REQUESTS=2
# Inside the authorized allocation, with retrieval preflight configured:
bash uni_agent_rollouts/scripts/run_nano4_inference.sh benchmark
```

This creates 8 prompt groups x 8 independent samples, 64 live sessions. It does
not train weights. The retained base configuration filename contains `-16`, but
the dataset and launcher supply group/sample counts for this Uni-Agent path.
Confirm `BOOK_AGENT_RUNTIME_SETTINGS` and the actual run output, not filenames.

## Context and rendering pitfalls

Model context was 262,144; upstream prompt partition was 4,096. The pinned Gateway
adds prompt_length and response_length to allocate trajectory capacity. A model
max_new_tokens limit alone does not solve its MTP edge-of-window overflow.

```text
response_length = context_window - prompt_length - speculative_margin
                = 262144 - 4096 - 8 = 258040
trajectory_capacity = 262136
```

The 8-token margin was tested for this stack/draft width. Recompute and test at
context boundaries when changing it; eight is not a universal constant.
The Book Agent imposed no smaller per-turn output cap (max_tokens_per_turn=0),
but the engine/Gateway still had real context/trajectory limits, plus the 500
action loop guard and a 900-second request timeout in this experiment.

Gateway renders the prompt. `reasoning_effort=medium` must reach
`data.apply_chat_template_kwargs`; request-local extra_body alone did not reach
the codec. The Qwen tool parser was `qwen3_coder`. Verify the rendered template
and parser when migrating; do not change the prompt or reasoning setting as a
hidden consequence of enabling MTP.

The pinned Gateway dropped request seed control, so equal caller-side seeds did
not establish exact paired generation. Training requires preserving the exact
rendered token sequence, tool observations, response masks and logprobs, and
accounting for sampling/behavior-policy probabilities. MTP telemetry does not
establish GRPO correctness or an on-policy training pipeline.

## External documentation when changing versions

- [SGLang speculative decoding](https://docs.sglang.io/docs/advanced_features/speculative_decoding)
- [Uni-Agent source](https://github.com/verl-project/uni-agent)
- [SGLang source](https://github.com/sgl-project/sglang)

Use version-matched primary docs and installed source. The local pins and tests,
not whichever flags happen to appear in today's main branch, govern reproduction.
