# Connection, deployment, and completion

## Authentication and transport

Use explicit `NANO4_USER`, `NANO4_LOGIN`, `NANO4_ACCOUNT`, and
`NANO4_SSH_SOCKET` values from the current project/user environment. The login
host is `nano4.nchc.org.tw`; do not substitute a historical login-node IP.

Test an existing socket with a bounded read-only command:

```bash
timeout -k 2 20 ssh -S "$NANO4_SSH_SOCKET" -o BatchMode=yes \
  -o ConnectTimeout=8 "$NANO4_LOGIN" 'date; hostname; id -un'
```

`ssh -O check` proves only that the local master process exists. A real remote
command is required: stale masters have accepted local requests but stopped
returning remote output. Local and remote `$USER` can differ; single-quote a
remote command when its variables should expand remotely.

For an authorized new login, use a PTY and a new socket path if the old one is
unresponsive. Do not kill another user's terminal or working master:

```bash
ssh -M -S "$NANO4_SSH_SOCKET" -o ControlPersist=2h \
  -o ConnectTimeout=25 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  "$NANO4_LOGIN"
```

Read the actual menu. Historically option 2 was Mobile APP PUSH, followed by a
password prompt and phone approval. Menu selection alone does not mean a push
was sent. Use a user-authorized secure credential mechanism or let the user enter
the password in their terminal; do not request passwords be committed or pasted
into generated code. Ask the user to approve the phone request, and confirm login
with a remote command. Never disable host-key verification to bypass a failure.

Banner timeouts / no route are transport failures before MFA. Permission denied
with keyboard-interactive is an authentication failure. Retry one transient
transport failure if appropriate; repeated failure, rejection, or an unavailable
credential requires user/network intervention, not repeated push notifications.

## Preflight and allocation

Useful remote read-only checks:

```bash
squeue --user="$USER" -o '%.18i %.12P %.28j %.2t %.10M %.10l %R'
sacctmgr -n show assoc user="$USER" format=Account,Partition,QOS
scontrol show partition dev
scontrol show partition 8gpus
sacctmgr -n show qos p_dev,p_8gpus format=Name,MinTRES,MaxTRESPerJob,MaxWall
sinfo -o '%P %a %l %D %G'
```

Use `sbatch --test-only` with the intended request to validate scheduler acceptance;
its output can mention an anticipated job ID but does not submit a real job.
Check partition limits again for a new experiment. The `8gpus` name does not mean
every allocation must request eight GPUs. Avoid silently using another associated
account if the intended one is unavailable.

On allocated compute nodes check `command -v apptainer`, the container path,
Python environment, and `nvidia-smi`. Some nodes historically lacked Apptainer;
an old node failure is not grounds for a permanent exclusion list.

## Safe synchronization and environment

- Prefer an existing project workflow after inspecting its actual commands.
- Preview source transfers with `rsync -ani`; exclude environments, caches,
  credentials, large unrelated data, and remote results. Avoid `--delete` unless
  deletion is explicitly intended and reviewed. Back up overlapping remote code.
- Preserve the run's code/config snapshot; do not overwrite code a running job
  might still import. New runs should get unique artifact directories.
- On the remote side export required runtime variables before `sbatch
  --export=ALL`. That exports the remote submission environment, not the local
  workstation's environment. Do not dump the entire environment into logs.
- Containers: `apptainer exec --nv --bind /work/$USER:/work/$USER ...`.
  Bind host data/model paths actually needed by the project. Pin image digests,
  model revision, upstream commit, and compatibility patches for reproducibility.
- Nano4 may export `ROCR_VISIBLE_DEVICES` on NVIDIA jobs. Our verl environment
  rejects that together with `CUDA_VISIBLE_DEVICES`; unset only the AMD variable
  in that environment. Preserve the scheduler's CUDA assignment.
- Use job-specific short Ray temp paths such as `/tmp/book-ray-$USER-$SLURM_JOB_ID`
  and nonconflicting ports. Long paths can exceed the Unix socket limit. Do not
  run global `ray stop` or broad `pkill` on a node shared with other jobs.

## Monitor and retrieve

Use `squeue` for live jobs, `sacct` for finished jobs, and explicit run paths for
application results. For old jobs supply a start date:

```bash
sacct -j "$JOB_ID" --starttime="$RUN_DATE" \
  --format=JobID,State,Elapsed,ExitCode,AllocTRES -n
```

A missing queue entry is not sufficient evidence of success. Inspect `.out`,
`.err`, application logs, validation errors, and actual artifact counts. Preserve
partial results on failure. `FAILED` can mean the final validator rejected some
traces even though every session returned output; `COMPLETED` can still conceal
an application that never did useful work if its script swallowed errors.

Retrieve into a run-specific local directory with non-deleting rsync. Avoid
retransferring cached book packs or model weights with every status check. For
inference, count terminal reasons and nonempty outputs; for training, inspect
steps, losses, checkpoint integrity, and resume state. Do not call inference-only
rollouts training.

## Helper services and cleanup

Retriever and policy can occupy different nodes. Bind the retriever to a reachable
compute-node private IP, publish readiness only after weights/index are loaded,
then perform an actual query from the policy environment before loading the policy.
Serialize the verified endpoint into worker/task config; Ray workers may not
inherit the launcher's environment.

Use a helper-service watchdog or an equivalent managed lifetime. The site's Book
Agent watchdog reads a `consumer-job-id` file and polls the user's full queue.
`squeue --jobs=finished-id` can error after record purging; successful full-queue
queries without the ID indicate completion, while failed queries must not be
treated as completion. Upload and read back the consumer ID before handoff.

Match helper wall time to consumer duration plus startup/queue delay. A helper
on the four-hour dev partition cannot serve a potentially twelve-hour consumer.
If the consumer cannot be submitted, stop only the helper allocated for this
attempt. Confirm cleanup through scheduler state; closing SSH is not cleanup.
