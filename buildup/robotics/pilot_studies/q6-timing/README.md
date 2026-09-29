# Q6 Timing Readiness

Updated: 2026-09-15

## Scope and status

`VERIFIED_DEFER_TERMINAL_SEMANTICS`. This study implements the prospectively fixed
[Q6 measurement design](../../questions/temporal-mismatch-decomposition.md#readiness-gates-and-resource-cap).
The original evaluator failed a prespecified terminal-validity gate. The held-out pilot is blocked
by that scientific stop rule; it is not a queued execution. No training or checkpoint search.

Readiness order: source/weight/schema linkage; synthetic timing and terminal controls;
96 original/adapter parity records and four independent-process repeats; eight buffer invariance
records; 32 competence records. A failed source, parity, terminal or resource gate defers this route.
Partial records remain evidence of readiness failure and never enter the scientific denominator.

## Resources and artifacts

- New source: `external/q6/{rtc,kinetix,jaxued}/`; weights: `datasets/q6/policies/`.
- New runtime/output: `runs/q6/readiness/`; container paths `/source`, `/data`, `/study`, `/output`.
- CPU only, 8 CPUs, 24 GiB RAM; fixed Python 3.11/JAX 0.4.35/jaxlib 0.4.34/Flax 0.10.2/NumPy 1.26.4.
- Build/pull cap 2 h; readiness after build 2 h; prospective pilot 4 h. Image/dependencies 12 GiB,
  weight payload 25 MiB, study output 512 MiB; one bounded dependency repair, 16 h preparation cap.
- Source/data/study mounts are read-only. Logs use timestamped files under repository `logs/`.

Acquisition, build, execution, verification and exact identities are recorded below as they occur.
This README owns live evidence; the question record owns the prospective scientific protocol.

## Commands and job record

All commands below run from `/home/yoohyun/research3`.

1. Acquisition: `timeout 1200s python3 -u buildup/robotics/pilot_studies/q6-timing/acquire.py`,
   detached with `nohup`; log `logs/20260915_q6_acquire.log`. `completed`: 265 source files
   verified against three immutable Git trees; both weight payloads verified with size, MD5,
   CRC32c and SHA-256. [assets.json](assets.json) owns all URLs and hashes.
2. Lock projection: `python3 buildup/robotics/pilot_studies/q6-timing/project_lock.py` (host text
   transformation only). [requirements.txt](requirements.txt) pins 102 registry distributions
   and upstream-allowed archive hashes. Source packages are read-only `PYTHONPATH` entries;
   Kinetix/RTC packaging CUDA extras are not installed. `schema.py` explicitly adds jaxued's
   `src/` layout to the import path. No numerical dependency version change or repair was needed.
3. Build: `timeout 7200s docker build --pull --no-cache -t research3-q6-readiness:v1
   buildup/robotics/pilot_studies/q6-timing`, detached with `nohup`; log
   `logs/20260915_q6_build.log`. Completed image:
   `sha256:d558ddf6158302871270e39c4eb7abfcfc339fdb6ed2eeeebf05b79dd185245a`.
   Base is the official Python digest in [Dockerfile](Dockerfile), not a prior research image.
   [cpu_install.json](cpu_install.json) records selected archive hashes; [installed.txt](installed.txt)
   records installed versions including the base pip bootstrap. `pip check` passed.
4. `python3 buildup/robotics/pilot_studies/q6-timing/launch.py schema`: completed, log
   `logs/20260915_100733_q6_schema.log`. Exact checkpoint tree/dtype/shape and loader defaults passed
   for both levels: observation width 679, action width 6; CPU backend confirmed.
5. `python3 buildup/robotics/pilot_studies/q6-timing/launch.py preflight`: completed, log
   `logs/20260915_101038_q6_preflight.log`. Sixteen profile/order fixtures, 96 rejected timing
   mutations, two RNG streams and six terminal cases passed.
6. `python3 buildup/robotics/pilot_studies/q6-timing/launch.py readiness`: stopped at the terminal gate,
   10:13:22–10:14:06 KST, exit 1;
   log `logs/20260915_101321_q6_readiness.log`; exact Docker argv/image/mounts in
   `runs/q6/readiness/readiness_launch.json`. The launcher runs detached with an in-container
   timeout, 8 CPUs, 24 GiB RAM, no network/GPU, read-only source/data/study and writable output.
7. `python3 buildup/robotics/pilot_studies/q6-timing/launch.py verify`: completed, exit 0,
   10:16:04–10:16:20 KST; log `logs/20260915_101603_q6_verify.log`. This separate process loads
   saved arrays and reconstructs one saved terminal step using unmodified source. No new rollout.

The first three log basenames contain the date only; subsequent detached jobs use full timestamps
and exit files. Source/build completion is verified from artifacts and the completed build log;
their shell exit files were not produced. Runtime launch records and per-stage output JSONs own
execution status. Inspect targeted log tails and Docker container state before resuming.

## Measurement and verification implementation

[config.json](config.json) and [pre_execution.json](pre_execution.json) record the design and code
identity before physical readiness. This is not a passed pilot freeze.

[instrument.py](instrument.py) adds diagnostic outputs to the pinned original evaluator and physics
engine using exact, single-match text replacements. It preserves action generation, RNG splitting,
environment stepping and terminal equations. It removes video creation/rendering from the original
route. The transformed source and complete diffs are saved under output `instrumentation/`.
No original source file is changed. The original terminal aggregation, including its precedence
and last-substep semantics, is retained for validity testing.

[adapter.py](adapter.py) uses preassigned source-equivalent per-seed RNG keys and separate estimate
and switch inputs. [checks.py](checks.py) independently derives expected event timing and first-
terminal accounting without importing the adapter/planner. All executed records are readiness seeds.

Each `records/*.json` carries identity, planned/consumed delay histories, per-step state hashes,
terminal label/time, validity, timing and NPZ hash. Its compressed NPZ contains commanded/noisy/
processed actions, observations, RNG keys, substep rewards/labels, finite flags, and named raw-state
leaves. Adapter records also preserve capture observations, initial/old/new chunks and event times.
Original records preserve the instrumented original path. A failed gate retains both the error
and available records; there is no seed replacement or automatic pilot launch.

## Verified outcome 2026-09-15

**Fact:** the fifth readiness record, original naive `grasp_easy`, constant delay 1, seed 0,
terminated at control step **33** with substep rewards **[1, 0]** and substep GoalR **[true, false]**.
The source reports aggregated reward 1 and `done=true`, but official `GoalR` and
`returned_episode_solved` are **false**. All scored state/action checks are finite. This is exactly
the prospectively specified disagreement, not a timeout, dependency failure or adapter effect.

**Independent verification:** [verify.py](verify.py) imports none of the adapter, planner,
instrumentation or runner outcome functions. It checked 265 source files, two weights, 16 frozen
execution files, five NPZ identities and all 1,280 stored state hashes. From the saved step-33
pre-state and source RNG/wrapper path, the **unmodified** official engine returned `done=true`,
`GoalR=false`, reward 1. Separately exposing both physics substeps reproduced [1, 0].
[verification.json](verification.json) owns the exact observations.

| Gate | Result |
| --- | --- |
| Sources / CPU dependencies / two checkpoint schemas | PASS; 42 parameter leaves per checkpoint |
| Synthetic timing, RNG and terminal fixtures | PASS; no physical result implied |
| Zero-delay naive original/adapter, seeds 0 and 1, grasp_easy | Two pairs PASS, maximum pre-terminal difference 0; terminal steps 28 and 30 |
| Next original record, delay 1, seed 0 | FAIL: first-terminal success disagreement at step 33 |
| Remaining parity / independent-process repeats / buffer invariance / competence | Not executed after the required stop; 135 of the planned 140 records remain unexecuted |
| Held-out 2,048-record pilot / pilot-ready freeze | Not executed / not admitted |

The preceding four zero-delay records are neither a two-task competence result nor evidence about
delay ordering. Warmed execution of those completed records was about 1.06–1.08 seconds per full
256-step scan, but no hard/soft or two-level pilot cost estimate is validated. Equal number of flow
steps would not establish equal compute cost. Readiness stopped for semantics well inside its cap.

**Source diagnosis:** `engine_step` takes maximum reward over both substeps and terminates on a
nonzero substep, but retains `info` only from the final substep. `LogWrapper` reports that final
GoalR as solved. The earlier noted `done` precedence issue is not needed to explain this finite
case. This observation establishes a measurement mismatch under the selected success definition;
it does not by itself establish a novel control method or disprove the delay-order question.

**Decision:** defer this measurement route and Q6 execution. Preserve the original label, failed
seed and all outputs. Do not substitute any-positive success, reduce frame skip, replace the
checkpoint/level, finish the remaining records or open held-out seeds under the same protocol.
The next bounded source/record reassessment should compare the scientific value of a prospective
reformulation against the reserve questions. A defensible new task-success definition would need
an explicit new design, original-result compatibility accounting and the same causal controls.
An evaluator fix alone is not a contribution. Q9 is not selected automatically.

## Preservation and recovery

[preservation.json](preservation.json) hashes this stopped execution, compact evidence, raw-output
inventory and exact commands. It is an evidence-preservation freeze, **not** a pilot-ready freeze.
The source/weight receipt and Docker recipe are retained; [outputs.json](outputs.json) lists every
raw artifact. Compact `schema.json`, `preflight.json`, `failure.json`, `verification.json` are byte
copies of the corresponding raw outputs. Row-level records remain in ignored `runs/q6/readiness/`.

- **Result preservation:** there is no paper result. Keep the frozen compact evidence plus the
  complete raw output directory, especially the failed step's NPZ, and timestamped logs.
- **Audit/resume:** keep the source and two policy payloads, frozen code, raw outputs and the new
  CPU image. The fixed failed route has no automatic resume. Commands refuse output overwrite;
  an explicitly designed future replay must use a separate output/launch receipt.
- **Full reproduction:** additionally preserve or reacquire every pinned Git file and registry
  distribution using recorded hashes; retain selected level files and generation-specific weights.
  The Docker image ID is local content identity, not evidence of a remotely uploaded image.

No external backup has been verified and no data/image/container was deleted. Do not treat
re-downloadability as a verified backup of source, weights or raw row-level evidence.

## Docker cleanup review 2026-09-16

Image/container 삭제 후보와 재개·전체 재현에 미치는 영향은
[repository cleanup review](../../../../docs/reproducibility.md#docker-cleanup-review-2026-09-16)가 소유한다.
이번 검토는 읽기 전용이며 Docker 자산을 삭제하지 않았다. 기존 실행/보존 기록은 유지한다.
