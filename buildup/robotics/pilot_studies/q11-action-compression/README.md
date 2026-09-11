# Q11 Action Compression Feasibility

Updated: 2026-09-08

## Status and scope

`completed`: Stage 6 measurement readiness; `READY_FOR_CONTROLLED_PILOT`. User selected Q11 and authorized the next TODO.
[Question and prior/risk audit](../../questions/contact-action-compression.md) owns research framing.
No physical compression variants or policy training in v1. Eight fixed seeds 0--7; one planner
attempt each, at most two original-action replays each. Failed attempts stay in the denominator.

## Protocol and artifacts

`protocol.json` is frozen with source/code checksums before the first measurement run.
Physics/Torch CPU, explicit NVIDIA graphics exposure for SAPIEN scene creation, no rendering.
New image `research3-q11-readiness:v1`; no previous research image is a base/runtime.
Working directory `/home/yoohyun/research3`. Source `external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8`
is a previously downloaded public source checkout copied into the new image; old outputs are not inputs.
Pinned FAST files go to `datasets/q11/fast/`, mounted read-only as `/inputs/fast`.
Study is `/work:ro`; new raw outputs and writable caches are `runs/q11_v1/` mounted `/outputs`.
Logs use timestamped `logs/*q11*`. No heavy dataset or policy checkpoint is needed.

## Commands and jobs

Build: `sh buildup/robotics/pilot_studies/q11-action-compression/build.sh` in a separate tmux session.
Expected: build exit 0, image ID and dependency/OS lock captured in the output bundle.
Runtime and independent verification: `sh buildup/robotics/pilot_studies/q11-action-compression/run.sh`.
Exact launches and verification receipts will be appended here. Workload cap is two hours after build.

## Frozen v1 measurement rules

Config: [protocol.json](protocol.json); immutable implementation hashes: [freeze.json](freeze.json).
Initial state absolute tolerance 1e-7, relative tolerance zero: a strict same-initialization check,
not an acceptable robot task error. Official sampled success/on/static/grasp sequences must be
exactly equal on every completed generation/replay. State drift over the full trajectory is
reported separately. No tolerance is chosen from outcomes. All completed records must pass
measurement checks; at least one must also contain successful grasp/release/noncontact evidence.

Quantile stats use seeds 0--3 only; all eight are readiness inputs and cannot become future held-out
seeds. Constant quantile channels get half-range 1.0, no clipping; controller-bound normalization
is a separate variant. Tail chunks repeat the last action to 20 steps, carry valid lengths and are
never physically executed. Codec identities use float64 with 1e-12 absolute error tolerance.
Empty-token zero fallback is a synthetic instrumentation check, not a natural codec failure.
Independent verifier reconstructs the four official labels from saved poses, velocities and
finger forces, and BPE/DCT accounting from saved arrays without importing collector/simulator.

## Execution log

- Build `completed`, `logs/20260908_q11_build.log`, exit 0 in
  `logs/20260908_q11_build.exit`; new image built from pinned Python base with `--pull --no-cache`.
- Pinned FAST input download `completed`: six files, 696,940 bytes; hashes in [inputs.json](inputs.json).
  No training checkpoint or large demonstration dataset downloaded.
- Workload `completed`, exit 0, after freeze:

```bash
tmux new-session -d -s research3_q11_run 'cd /home/yoohyun/research3 && sh buildup/robotics/pilot_studies/q11-action-compression/run.sh > logs/20260908_q11_run.log 2>&1; echo $? > logs/20260908_q11_run.exit'
```

Expected raw artifacts: eight seed receipts and NPZ files, up to sixteen replays,
`codec.json`, `verification.json`, `job.json`, image/dependency/OS metadata and `outputs.sha256.json`
in `runs/q11_v1/`. Worker logs are `logs/20260908_q11_seed<seed>_<mode>.log`.
Verification command inside the same new image: `python /work/verify.py`, with study/input mounts
read-only and `/outputs` pointing at the retained v1 bundle. `run.sh` supplies exact runtime/mounts;
re-running the collection entrypoint on an existing bundle is refused.

## Verified result

**Decision: `READY_FOR_CONTROLLED_PILOT`.** This means measurement access, not a positive Q11
compression effect. [Compact result](results.json) and [independent verification](verification.json)
retain the evidence; full rows/arrays remain under `runs/q11_v1/`.

| Check | Result |
| --- | --- |
| Fixed attempts | 8/8 completed and successful; no retries or exclusions |
| Recorded original actions | 859 control steps across 8 episodes |
| Fresh-scene unchanged replays | 16/16 passed; action bytes and all sampled label sequences identical |
| Physical state agreement | initial and full-trajectory maximum absolute discrepancy 0 |
| Event access | all eight have one grasp onset, one release and sampled noncontact intervals |
| Independent evaluator | 10,404 labels reconstructed from poses/velocities/finger forces; no discrepancies |
| Codec accounting | 92 padded chunks across two normalizations; all BPE coefficient round-trips valid |
| Natural codec errors | zero lower-clamps, decoder exceptions or official-vs-analytical discrepancies |
| Artifact verification | 96 recorded file hashes verified in a separate read-only Docker container |
| Runtime | 24 worker processes + codec/verification completed in 86.92 s, excluding image build |

All seeds are calibration/readiness material, including seeds 4--7; none can be recycled as
future held-out outcome evaluation. Deterministic replays are measurement checks, not independent
statistical samples. Contact force is the last physics substep sampled at control frequency;
noncontact here means both sampled finger force magnitudes are below 0.5 N, not absence of all
physical contacts or complete substep information.

Joint-limit normalization had no values outside [-1,1]. Calibration quantiles had 682 such scalar
values; quantile normalization was deliberately not clipped. They caused no coefficient lower-clamp
or decode discrepancy. This observation must be carried into later scaling controls, not silently
clipped away. Empty-token decoding returned zeros as the source predicts, solely in the synthetic
instrumentation check. None of the reconstructed actions was sent to the simulator.

## Reproduction and preservation

2026-09-11 image 정리 검토와 삭제 후 재현 제약은
[cleanup assessment](../../../../docs/reproducibility.md#image-cleanup-assessment--2026-09-11)을 따른다.
V2 image는 v3에도 사용됐다. 이번 검토에서 image나 frozen artifact를 삭제·수정하지 않았다.

Image ID: `sha256:a60ff16758acf641b033c6d60cada1857b74757b96105e94545e6440671a640f`.
[dependencies.lock](dependencies.lock) and [os-packages.lock](os-packages.lock) capture the actual
installed environment. Dockerfile uses pinned base and package constraints; a rebuild must compare
its captured dependency/OS inventory before being called identical to v1.

The historical `run.sh` targets the original bundle and must not be used to overwrite it.
For a new reproduction directory, use the [separate entrypoint](reproduce.sh), which refuses existing
paths and keeps worker logs separate. This convenience entrypoint was added after v1 and does
not change frozen collector/verifier code; it has syntax validation, not a second runtime trial.

```bash
sh buildup/robotics/pilot_studies/q11-action-compression/reproduce.sh /home/yoohyun/research3/runs/q11_v1_repeat
```

Launch long reproductions through tmux with a timestamped log as above. Independent hash audit:

```bash
docker run --rm --name research3-q11-hash-verifier --network none --cpus 1 --memory 1g \
  -v /home/yoohyun/research3/runs/q11_v1:/outputs:ro research3-q11-readiness:v1 \
  python -c 'import json,hashlib,pathlib; p=pathlib.Path("/outputs"); h=json.loads((p/"outputs.sha256.json").read_text()); assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==v for n,v in h.items()); print("Verified",len(h),"output checksums")'
```

Host read of the graphics cache was denied by its container-created file permissions; the
read-only Docker hash audit passed. No permissions, old images/data or host simulator were changed.
Preserve source/input receipts, frozen code/config, compact verification and raw action/state/contact
arrays for continuation; full reproduction also needs the pinned input files and environment.
No asset deletion or external backup verification was performed.

## Next decision

Proceed to a separately frozen controlled physical pilot: disjoint episode split, fixed rate/error
matching, exact gripper bypass, scaling and interpolation controls. First decide whether natural
codec residuals localize to contact transitions beyond these controls. Do not promote to hypothesis,
change compression until a failure appears, or claim learned-policy gains from this readiness result.

## Controlled physical pilot v2 preparation

Final pre-outcome seal: [freeze.json](v2/freeze.json). It covers protocol, code, preflight and
environment receipts, plus the unchanged source/label-verifier dependencies.

`completed_and_verified`: disjoint 8-calibration/16-held-out population and 194 physical
trajectories completed in the new Docker. Frozen decision: `INCOMPLETE_CODEC_SUPPORT`;
see [verified results](#v2-verified-results) for available comparisons and limitations.
[Protocol](v2/protocol.json) and the detailed contract below govern execution. Readiness code, freeze and outputs remain unchanged.

Fresh build job: `sh buildup/robotics/pilot_studies/q11-action-compression/v2/build.sh`, background
tmux `research3_q11_v2_build`, log `logs/20260908_q11_v2_build.log`, exit file with `.exit` suffix.
No v2 simulator episode is generated in the protocol/preflight preparation task.

### v2 research question and claim boundary

At fixed controller, initial scene and action duration, do naturally occurring FAST reconstruction
errors change task outcomes beyond exact gripper preservation and scaling? Separately, does the
same arm-error pattern cause different outcomes when localized near grasp/release versus a
speed-matched sampled noncontact interval? These are different comparisons. Codec efficiency
requires measured byte support; localization is an oracle diagnostic with no bitrate claim.

Single-task expert-action replay cannot establish learned-policy/VLA improvement, universal
contact causality or final novelty. State-aware/skill-aware tokenizers remain prior-work pressure.
No new tokenizer architecture, policy training or physical robot is introduced.

### v2 population and outcome-blind ordering

- Calibration: seeds 1000--1007, one motion-planning attempt each. Held-out: 2000--2015,
  one attempt each. All readiness seeds 0--7 are excluded. This is one task distribution with
  disjoint seeds, not a cross-task generalization split.
- Keep unsuccessful, planner-failed, incomplete and runtime-error receipts. Completed originals
  are replayed twice from fresh scenes, with the unchanged v1 measurement gates. A technical
  original/replay disagreement stops the run; it cannot be relabelled as a compression effect.
- Completed replay-valid originals enter comparison irrespective of original task success.
  Failed/incomplete planning attempts stay in the attempted-population table; no replacement
  seeds or success quotas. Require at least four calibration originals and eight held-out originals
  for the planned assessment. These are feasibility minima, not a power guarantee.
- Choose normalization and control parameters using calibration action arrays only. Seal
  `calibration.json` and its SHA-256 before any held-out generation. The schema verifier uses
  task labels to certify replay, but parameter selection does not rank by task success.
- Generate and verify held-out originals, then encode all variants and determine source-event
  windows before any compressed-action rollout. Seal every `planned/manifest.json` before
  execution. Held-out errors/rates are reported without retuning or outcome-dependent filtering.

### v2 codecs and comparison costs

| Variant | Fixed intervention |
| --- | --- |
| `fast_joint` | FAST scale 10, joint-limit affine normalization, all eight channels |
| `fast_quantile` | Same processor/scale; calibration 1st/99th quantiles, no clipping |
| `fast_joint_gripper` | Joint normalization, FAST arm only, exact original binary gripper stream |
| `fast_quantile_gripper` | Quantile normalization and exact gripper; source of localization residuals |
| `uniform_gripper` | Joint-normalized uniform arm quantization; precision chosen on calibration under the reference byte cap |
| `linear_gripper` | Uniformly spaced arm knots and linear interpolation with quantized knot values; precision/density selected under the same cap |

FAST uses the pinned official universal processor, with no coefficient-scale search or BPE retraining.
The quantization/interpolation grids are enumerated in [protocol.json](v2/protocol.json); choose the
minimum calibration joint-normalized arm MSE among settings below the measured mean-byte cap
of `fast_joint_gripper`. Ties resolve by bytes and then the parameter tuple. If no setting fits,
record `NO_CALIBRATION_RATE_SUPPORT`; do not enlarge the grid/budget until a result appears.

Each 20-step packet has a 12-byte header. Actual packed token/scalar payload, exact gripper bits,
escape masks/float64 values, four-byte packet lengths and the episode packet count all count.
Normalization is 128 shared bytes per method/cohort, amortized by chunk count. Quantizer outliers
use lossless scalar escapes, so tails are not silently clipped. Gripper bypass requires original
±1 commands and charges one bit per padded step; no continuous command is thresholded to binary.
The six FAST input files and codec implementations are pre-shared assets whose sizes/provenance
are reported separately. This accounting is a wire-format comparison, not an autoregressive token
prediction or wall-clock inference speed comparison.

On the held-out common verified population, report whether mean costs are within 10% and
joint-normalized arm MSE within 20% (absolute floor 1e-12) of `fast_joint_gripper`. These are
predeclared operational overlap checks, not proof of error equivalence. Unmatched comparisons
remain in the table and cannot support an equal-rate/equal-error contact claim. Parameters are
never refit on the held-out actions. Nominal gripper outputs outside [-1,1] are counted; the pinned
controller's ordinary gripper clipping remains in effect and exact bypass is its control.
Out-of-limit arm targets or invalid codec representations are unavailable variants, not observed
contact failures; retain the unavailable denominator instead of inventing a successful/failing rollout.

### v2 contact-localization diagnostic

The first sampled grasp onset and first subsequent release define at most two event types per
original. For a label transition at state index e, the causing command is action e−1; the event
window contains that command and two commands on either side. Use five commands without
extending past the episode boundary.

Use the arm residual from `fast_quantile_gripper` over that event window. One diagnostic adds
only that 5×7 residual at the event window, while its pair adds the identical residual matrix to
an eligible noncontact window. All other arm actions and the full gripper stream remain original.
Thus both trajectories have equal total joint-normalized arm squared error; verify action arrays
before and after execution. These constructed trajectories are not compressed-codec proposals.

An eligible noncontact window has no sampled grasp or finger-force magnitude ≥0.5 N at its
six bounding states, constant gripper commands inside the five-command window, no grasp transition
within the three-step margin, no event-window overlap, and no out-of-limit arm target after injection.
Match mean normalized command-speed within a factor of two; if either speed is below 1e-6,
both must be below that value. Minimize log speed mismatch, breaking ties by earliest window.
No eligible window means `no_speed_matched_noncontact`; do not relax criteria after outcomes.

This controls residual energy/channel pattern and roughly matches speed. Robot configuration,
clearance and acceleration remain possible explanations; the result is a localization diagnostic,
not randomization of contact state. Last-substep sampled forces cannot resolve all contact peaks.

### v2 metrics, uncertainty and stopping

- Primary outcome: unchanged official final success at the original planner-completion horizon.
  Use the same number of actions in every variant; no first-success stopping or added settling.
- Report attempted → completed → replay-valid → method-available counts, original and variant
  success, paired lost/gained successes, byte cost, arm MSE, gripper MSE and clipping counts.
  Missing variants are reported separately, not imputed as physical failures. Paired comparisons
  use a visibly declared common verified population.
- Episode-level paired bootstrap: 2,000 resamples with fixed RNG seed, descriptive 95% interval;
  no chunk-level pseudo-replication. Grasp/release localization uses exact two-sided paired sign
  tests, Bonferroni alpha .025 each, and at least eight eligible pairs for a diagnostic signal.
  Such a signal alone does not satisfy simple-control resistance or establish novelty.
- Measurement failure → `MEASUREMENT_INVALID`; too few originals → `INSUFFICIENT_DENOMINATOR`;
  missing codec support → `INCOMPLETE_CODEC_SUPPORT`; identical final task outcomes for all
  verified codec variants → `NO_TASK_OUTCOME_CHANGES`; otherwise →
  `OUTCOME_CHANGES_REQUIRE_STAGE7_REVIEW`. Localization and rate/MSE support tables accompany
  this task-outcome decision. A task-outcome null does not assert identical contact trajectories.
- Maximum 232 trajectories: 24 generations + 48 original replays + 96 codec rollouts + 64
  possible localized rollouts. At most 400 control steps each, 120 s per collector attempt,
  150 s process watchdog, two-hour overall workload cap. Source setup/build time is separate.
  Fewer eligible cases do not authorize replacement attempts or a larger compression grid.

### v2 implementation and preflight evidence

Collector [collect.py](v2/collect.py) preserves v1 recording/scene/controller logic and adds planned
variant action-file loading. [prepare.py](v2/prepare.py) selects parameters and event windows;
[codecs_impl.py](v2/codecs_impl.py) defines charged byte streams;
[evaluate.py](v2/evaluate.py) independently reconstructs physical labels using the frozen v1
label routine and verifies executed actions against saved plans and decoded packets.
[job.py](v2/job.py) enforces calibration-before-held-out-before-intervention ordering.

New image: `sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f`.
[Environment receipt](v2/environment.json) records the image and actual dependency/OS hashes;
Python package inventory matches readiness v1. No old image was used as a base or retagged.
[Preflight receipt](v2/preflight.json): six synthetic test groups passed in the new CPU Docker,
covering bit packing, all codec formats/gripper/tails, scalar escapes, full-knot interpolation,
actual event matching/rejection and action-only parameter selection under the byte cap.
The full v2 simulator orchestration subsequently completed and passed independent audit; see
the execution results below. Synthetic preflight is separate from empirical pilot evidence.

### v2 commands and preservation

Working directory: `/home/yoohyun/research3`.
Study v2 → `/work:ro`, original study → `/baseline:ro`, pinned input → `/inputs:ro`, new output →
`/outputs`, timestamped host `logs/q11_v2_<UTC stamp>/` → `/logs`. Physics/Torch CPU with 4 CPUs,
8 GiB RAM; explicit GPU device 0 for NVIDIA graphics only, offline runtime, no rendered frames.

Build and preflight completed; the following physical job was **launched on 2026-09-08**
in tmux `research3_q11_v2` (status: completed and independently verified):

```bash
tmux new-session -d -s research3_q11_v2 'cd /home/yoohyun/research3 && sh buildup/robotics/pilot_studies/q11-action-compression/v2/run.sh /home/yoohyun/research3/runs/q11_v2 > logs/20260908_q11_v2_run.log 2>&1; echo $? > logs/20260908_q11_v2_run.exit'
```

[run.sh](v2/run.sh) binds the inspected immutable image ID and refuses an existing output path.
Expected outputs: calibration decision/hash, every attempt receipt, original/variant state-action
arrays, binary packets, plan hashes, `analysis.json`, `job.json`, and `outputs.sha256.json`.
Cache/log files remain on disk but are excluded from the scientific output hash inventory.
Independent analysis is called by the runner after all variants; standalone command in the same
image/mounts is `python -c 'import json,evaluate; j=json.load(open("/outputs/job.json")); s=[r["seed"] for r in j["eligibility"] if r["status"]=="replay_valid" and r["seed"] in evaluate.P["heldout_seeds"]]; evaluate.summarize(s)'`.
Preserve the original v1 bundle. No external copy verification or asset deletion occurred.

### v2 execution record (2026-09-08)

Status: completed and independently verified; both exit receipts are 0 and no job remains active.
Scientific runtime: 657.73 seconds (build excluded). Original tmux session: `research3_q11_v2`; orchestration log
`logs/20260908_q11_v2_run.log`, exit receipt `logs/20260908_q11_v2_run.exit`.
The launcher records the per-worker log directory in `runs/q11_v2/log_path.txt`.
Code freeze (19 files including three baseline references), 15 local source/input hashes,
and the immutable image were verified before launch. Available disk was 118 GiB; physics
runs on CPU and existing GPU workloads are left intact.

Calibration has sealed its action-only parameter decision. Uniform quantization has no
candidate under the fixed byte cap and remains `NO_CALIBRATION_RATE_SUPPORT`;
linear interpolation selected six bits and two knots. No cap/grid/seed changes are made.

A separate [post-run audit](audit_v2.py) reads the output bundle without importing the
collector, planner or v2 evaluator. It reuses the frozen v1 analytical physical-label routine,
independently decodes binary packets via Tokenizer/IDCT and integer bit extraction, and
recomputes byte/MSE/outcome summaries and localized residual checks. It also checks full
original replay state differences, source/calibration/plan hashes and stage ordering.
Queued in tmux `research3_q11_v2_audit` to run only after the scientific job returns exit 0
(polls the exit receipt every five seconds; no additional simulation):

```bash
sh buildup/robotics/pilot_studies/q11-action-compression/audit_v2.sh /home/yoohyun/research3/runs/q11_v2_audit > logs/20260908_q11_v2_audit.log 2>&1
```

The audit uses the same immutable image, CPU only, `/outputs:ro` and a distinct `/audit`
output mount. It performs no simulator rollouts or scientific reruns.

### v2 verified results

[Compact results](results_v2.json) and [independent audit receipt](verification_v2.json) are the
tracked summaries; `runs/q11_v2/` owns raw trajectories/plans/packets and
`runs/q11_v2_audit/verification.json` owns the original audit receipt. The frozen scientific
code/protocol and v1 files were not edited. No extra seeds, grid changes or scientific reruns.

**Facts.** All eight calibration and 16 held-out original attempts completed, succeeded and
passed two original replays each. Total: 24 originals + 48 replays + 80 codec rollouts + 42
localized rollouts = **194 trajectories / 20,570 control actions**. The separate CPU Docker audit
passed **617 output hashes, 83,056 reconstructed official labels, 460 held-out codec chunks**,
and all 45 calibration candidates plus the FAST reference (2,208 calibration chunk evaluations).
Original replay full physical-state maximum difference and independent packet-decode difference
were both **0**. Calibration statistics/selection, disjoint seeds, calibration sealing before
held-out generation and all plan sealing before intervention were independently checked.

Calibration reference: 36.1042 bytes/chunk. Uniform's cheapest candidate, one bit, costs 40.3333
bytes/chunk, so all 16 Uniform variants are unavailable under the unchanged cap. Linear selected
six bits / two knots at 33.3333 calibration bytes/chunk. Unavailable is not observed failure.

Held-out original success is 16/16; each available codec below uses the same 16 originals and
92 chunks. Byte costs include framing, exact gripper bits where applicable and amortized
128-byte normalization metadata. Arm MSE uses joint-limit normalization regardless of codec.

| Codec | Final success | Lost / gained vs original | Bytes/chunk | Arm MSE | Rate / MSE matched to FAST joint + exact gripper |
| --- | ---: | ---: | ---: | ---: | --- |
| FAST joint | 2/16 | 14 / 0 | 47.2717 | 9.5593e-5 | no / yes |
| FAST quantile | 16/16 | 0 / 0 | 53.8913 | 8.3219e-6 | no / no |
| FAST joint + exact gripper | 2/16 | 14 / 0 | 34.3587 | 9.5593e-5 | reference |
| FAST quantile + exact gripper | 16/16 | 0 / 0 | 41.3152 | 8.3219e-6 | no / no |
| Uniform + exact gripper | unavailable (16) | — | — | — | no calibration rate support |
| Linear + exact gripper | 5/16 | 11 / 0 | 32.0870 | 2.3871e-4 | yes / no |

Paired success-change 95% descriptive bootstrap intervals: joint FAST variants
[-1.0000, -0.6875]; quantile variants [0, 0]; Linear [-0.8750, -0.4375]. The degenerate
quantile interval is not proof of population equivalence or a zero failure rate. Both full FAST
variants have 1,392 raw gripper values outside [-1,1], while exact-gripper variants have zero
such values. Exact gripper preservation leaves aggregate success counts unchanged. In joint FAST, seed 2000
changes success→failure and seed 2003 failure→success; quantile outcomes agree for every seed.
Thus gripper has case-specific effects even though its preservation alone does not improve the
aggregate success count.

Localization: grasp has nine eligible pairs (seven no speed-matched noncontact windows),
release has 12 (four no matched windows). Both event and free injections succeed in every
eligible pair: grasp 9/9 versus 9/9, release 12/12 versus 12/12. Both exact paired p-values are
1, with no diagnostic signal at the frozen threshold. Error energy, event indices, complete
matching search and selected windows were independently reconstructed. These results concern
the fixed quantile-FAST residuals, not larger injected errors or arbitrary contact perturbations.

The audit receipt retains descriptive per-case final on/static/grasp flags and whether grasp/on
was ever observed. Of the 14 joint-FAST failures in either gripper condition, 12 end off-stack
and two end on-stack but nonstatic; all end ungrasped, and two never attain a sampled grasp.
Of 11 Linear failures, all end off-stack/ungrasped and five never attain a sampled grasp.
These are observed predicates, not established physical failure causes.

**Frozen decision:** `INCOMPLETE_CODEC_SUPPORT` because Uniform has no calibration rate support.
This takes precedence over the observed task-outcome changes; it does not mean measurement
failed. Available comparisons and localization remain verified evidence.

**Agent inference for the next review.** Scaling changes reconstruction error and task outcomes;
gripper preservation alone does not improve aggregate success under joint normalization. Quantile arm MSE is
about 11.5 times smaller, with higher byte cost. No non-reference control simultaneously meets
both frozen rate and MSE tolerances. Thus the pilot establishes neither equal-cost superiority
nor a contact-specific mechanism that survives scaling. The localized diagnostic supplies no
positive signal on this population; it does not prove contact never matters. One expert replay
task does not establish generality, learned-policy gains or novelty.

Stage 7 review is now complete: [refine decision](../../../selection.md#q11--refine-2026-09-08).
Q11 is `under_review` for one bounded protocol revision; no hypothesis admission or further
physical runtime is implied by the completed v2 execution. V1/v2 inputs and raw artifacts remain preserved; no external
backup verification or deletion was performed.

### Stage 7 support audit (2026-09-08)

[Selection audit](selection_audit.py) reads frozen JSON only. [Receipt](selection.json) preserves
all 45 existing calibration grid points, the original strict-cap membership, separate symmetric
rate/MSE overlap flags, held-out support and case-level gripper changes. This is a post-outcome
descriptive audit; it does not refit codecs or turn a calibration grid point into a held-out result.

- Uniform: 9 points, zero under the original cap and zero within the symmetric rate tolerance.
- Linear: 36 points, 7 under the original cap, 5 within ±10% rate, and one within both ±10% rate
  and ±20% MSE. The latter is **6-bit / 3-knot**, calibration 38.333333 bytes/chunk and arm MSE
  8.5881451e-5 versus reference 36.104167 and 1.0309468e-4: +6.1743% cost / −16.6965% MSE.
  It is **outside the original strict cap**. It was correctly excluded from v2 execution. Its
  held-out outcome/support are unknown. The original selected 6-bit / 2-knot point remains unchanged.
- Held-out v2 has zero non-reference methods meeting both frozen rate/MSE tolerances.
- The localization reference is `fast_quantile_gripper`, with 16/16 full-episode successes;
  the failing joint-normalized residual was not the localized exposure. This limits the null's
  scope; it does not guarantee that a different residual would yield a contact-specific effect.

Primary-source recheck: [FAST §V-B and §V-C](https://arxiv.org/html/2501.09747v1#S5)
explicitly uses training-set 1st/99th quantile normalization and recommends one-second chunks.
Thus quantile normalization is an established baseline, not a new corrective method. Joint-limit
normalization remains the pilot's diagnostic condition; its failures are not evidence that the
recommended FAST preprocessing fails. This check revisits the existing source, not a new novelty survey.

Command (cwd `/home/yoohyun/research3`; CPU only, one CPU / 1 GiB, network off, same immutable
project image, read-only scientific inputs, separate output; exit 0):

```bash
docker run --rm --name research3-q11-stage7 --network none --cpus 1 --memory 1g -e PYTHONDONTWRITEBYTECODE=1 -v /home/yoohyun/research3/runs/q11_v2:/inputs:ro -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q11-action-compression:/study:ro -v /home/yoohyun/research3/runs/q11_stage7:/audit sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f python /study/selection_audit.py > logs/20260908_q11_stage7.log 2>&1
```

Expected and verified receipt: `runs/q11_stage7/selection.json` (tracked copy above); source and
three raw input hashes are embedded. No simulator, method dependency, GPU, model fitting,
new calibration data or new held-out outcome was executed. V1/v2 scientific artifacts remain intact.
The Stage 7 decision and bounded next-step conditions belong to `buildup/selection.md`.


## Bounded physical pilot v3 preparation

Preparation was **checked and frozen on 2026-09-08**. Physical execution and independent
audit completed on 2026-09-10; see [verified v3 results](#v3-verified-results).
This is the one [Stage 7 revision](../../../selection.md#q11--refine-2026-09-08).
The [protocol](v3/protocol.json), [fixed calibration snapshot](v3/calibration.json) and
[freeze](v3/freeze.json) bind 16 v3 files and nine baseline references. Final freeze SHA-256:
`e3a029ef3a460bae6d0559ecfcd1e5ea27780d67ac07f93c44d63f0e8c58d311`.
No v1/v2 frozen code, decision or raw outcome was changed.

### Revision and comparison target

Three fixed full-episode variants: `fast_joint_gripper`, `fast_quantile_gripper`, and
`linear_gripper` with six bits / three knots. All retain the exact original binary gripper.
The comparison asks about approximately matched rate and arm MSE, not the old hard byte cap.
The Linear point already existed in v2 calibration; its extra bytes remain charged and visible.
Uniform is not a runnable v3 comparator; its v2 unavailability is preserved. There is no new
precision/knots search, fitted model, tokenizer training or new normalization estimate.

All normalization statistics come from v2 calibration seeds 1000–1007. The snapshot records
its source hash and explicitly records the post-v2 change in fixed Linear parameters. V2's
original selected two-knot control is not overwritten. Quantile normalization remains a required
simple control and an established FAST input procedure, not a proposed new method.

**Primary diagnostic:** relocate the unchanged 5×7 arm residual of natural joint-normalized
FAST from the first grasp/release event window to a matched sampled noncontact window. The
residual is not rescaled, increased, sign-flipped, or selected by whether its full codec later
fails. Every new assigned original goes through the same procedure. All other arm actions
and the complete gripper stream remain original.

A grasp transition at state e is caused by action e−1; the five-command window starts at e−3.
Keep the v2 matching rule: six bounding states ungrasped with each finger-force norm <0.5 N,
constant gripper inside the free window, no overlap and no grasp transition in the three-step
margin, arm targets within joint limits. Match mean normalized command speed within a factor
of two (both below 1e-6 in the near-zero case), minimize log speed mismatch and choose the
first tied window. No eligible match stays unavailable. The copied residual yields identical
whole-episode normalized arm MSE between event/free. Configuration, clearance, acceleration
and gripper phase remain possible contextual explanations; this does not randomize contact.

The full joint/Linear comparison is secondary and cohort-level. Report rates/MSE and paired
success differences on the entire declared supported cohort, not a favorable subset. The
quantile control tests whether lower error through standard scaling is sufficient for success;
it is not required to match joint FAST's rate or error. Codec success differences alone are
not a contact-localization effect or a learned-policy/VLA result.

### Calibration-only preparation evidence

[Precheck](v3/precheck.py) ran in the immutable workspace Docker, CPU only. Its shell mounts
only the eight calibration seed directories as data, plus the pinned FAST files and v3 code;
old held-out trajectories and new confirmation inputs are not mounted. It reads actions,
grasp and sampled finger-force arrays, without task-success or variant outcome fields.

[Receipt](v3/precheck.json): **PASS**, all three codecs valid on all eight originals; **144
chunks** independently reconstructed with maximum difference **0**. Joint FAST costs 36.1042
bytes/chunk with arm MSE 1.03095e-4; Linear costs 38.3333 with 8.58815e-5; both symmetric
±10% rate / ±20% MSE criteria pass. Quantile FAST costs 43.5417 with 8.70832e-6.
Natural joint-residual matching provides **five grasp pairs and three release pairs**; event/free
arm-error energy and all exact gripper streams agree. No new simulator episode was run.

The preparation requires at least two pairs per event to establish an executable exposure,
not infer statistical power. Three release pairs in calibration do not guarantee the fresh
confirmation gate will pass. Its counts and tolerances remain fixed; no extra seeds are added
if confirmation support is inadequate. All old v1/v2 seeds are excluded from new confirmation.

[Contract tests](v3/test_contract.py) and [receipt](v3/contract.json): three groups passed for
support/availability/count stops without subgroup selection, decision priority with fabricated
outcomes, and fixed seeds/budgets/discrete sign-test thresholds. These tests are not physical
outcomes. Collector and binary codec code are byte-identical to validated v2; the revised full
orchestration has not yet executed a simulator episode.

### Fresh confirmation and outcome rules

- Assign seeds **3000–3023**, one planner attempt each, max 400 actions, no success quota or
  replacement. Retain planner-failed/incomplete receipts. Technical errors or independent
  original/replay disagreement stop the job as measurement failure. Completed replay-valid
  originals enter comparison regardless of original task success; replay each twice.
- Before the first compressed/localized rollout, prepare all action arrays, binary packets,
  event manifests and support results; hash every planned file and seal the support result.
  No variant outcome exists when this gate is evaluated. Require **at least 16** valid originals,
  all three codecs available on every valid original, aggregate joint/Linear rate within ±10%
  and MSE within ±20% on that whole cohort, and **at least eight pairs for each event**.
  Failure yields `STOP_INSUFFICIENT_DENOMINATOR`, `STOP_NO_COMPARISON_SUPPORT` or
  `STOP_NO_EVENT_SUPPORT`, with **zero intervention rollouts**. Originals/replays remain recorded.
- Primary outcome is unchanged official final success after the original number of actions.
  No added settling, first-success stopping, alternative label or retrospective denominator.
  Event/free comparisons use exact two-sided paired sign tests, alpha .025 for each of grasp
  and release, minimum eight verified pairs, and the direction event-fails/free-succeeds.
  With six concordantly directed discordances p=.03125, with seven p=.015625: the minimum
  pair count is a feasibility limit, not evidence of adequate power or equivalence under a null.
- All available variants undergo independent raw-state label, initial-state, action-byte and
  packet reconstruction checks. Technical/measurement failure takes precedence over science.
  Require at least one joint-codec loss relative to its original for a connection to the
  unresolved failure population; otherwise `STOP_NO_FAILURE_LINK`. This is a final interpretation
  rule, never a criterion for selecting episodes or event windows.
- No positive directional localization test yields `STOP_NO_CONTACT_LOCALIZATION_SIGNAL`;
  all counts, opposite-direction effects and uncertainties remain reported. This means the
  bounded study did not establish the required signal, not that every contact effect is zero.
  A positive test yields only `LOCALIZED_DIFFERENCE_REQUIRES_REVIEW`; baseline/scaling/context
  limits still prevent automatic hypothesis or method selection. Full-codec contrasts use
  descriptive paired 2,000-resample bootstrap intervals, fixed RNG 20260908.
- At most **240 trajectories**: 24 originals + 48 original replays + 72 full-codec + 96 localized.
  Attempt limit 120 s, subprocess watchdog 150 s, overall two hours; 20 Hz control / 100 Hz
  CPU physics, no rendering. No amplitude, grid, seed-count or task expansion after a stop.
  A completed valid null ends the current contact-sensitive method route under Stage 7.

### Docker commands and preservation

Cwd `/home/yoohyun/research3`. [Environment reference](v3/environment.json) binds the existing
**workspace-built Q11** immutable image
`sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f`, the v2 Dockerfile/build
command, actual dependency/OS locks and source receipt. No pre-workspace external image is used.

Preparation commands completed, exit 0 (for reproduction choose new output directories):

```bash
sh buildup/robotics/pilot_studies/q11-action-compression/v3/check.sh /home/yoohyun/research3/runs/q11_v3_precheck > logs/20260908_q11_v3_precheck.log 2>&1

docker run --rm --name research3-q11-v3-contract --network none --cpus 1 --memory 4g -e PYTHONDONTWRITEBYTECODE=1 -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q11-action-compression/v3:/work:ro -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q11-action-compression:/baseline:ro -v /home/yoohyun/research3/runs/q11_v3_contract:/outputs sha256:fb9c530b6d664536b7665a3647c28459c729b250e5b1300cc47494820c388b5f python test_contract.py > logs/20260908_q11_v3_contract.log 2>&1
```

Expected preparation outputs: `runs/q11_v3_precheck/precheck.json` and
`runs/q11_v3_contract/contract.json`; identical tracked copies are linked above, with input/source
hashes. Runtime caches stay ignored. [check.sh](v3/check.sh) refuses existing output paths.

The following was the prepared command on 2026-09-08; the actual 2026-09-10 invocation is
recorded below with launch-date logs:

```bash
tmux new-session -d -s research3_q11_v3 'cd /home/yoohyun/research3 && sh buildup/robotics/pilot_studies/q11-action-compression/v3/run.sh /home/yoohyun/research3/runs/q11_v3 > logs/20260908_q11_v3_run.log 2>&1; echo $? > logs/20260908_q11_v3_run.exit'
```

[run.sh](v3/run.sh) refuses an existing output directory, mounts code/baseline/input read-only,
allocates four CPUs / 8 GiB and explicit NVIDIA device 0 for SAPIEN graphics only. PhysX/Torch
remain CPU. New outputs go to `runs/q11_v3/`, worker logs to the timestamped directory named
in its `log_path.txt`. Network is off. [job.py](v3/job.py) checks source/input/dependency hashes,
seals calibration before new originals, enforces [support.py](v3/support.py) and verifies results
with [evaluate.py](v3/evaluate.py). Independent analytic label reconstruction uses frozen v1.

Expected outputs: image/dependency/protocol/calibration receipts, all attempt arrays and receipts,
planned arrays/packets/manifests, `support.json`, `plans.sha256.json`, `job.json`, and
`outputs.sha256.json`; `analysis.json` appears only if the pre-intervention gate passes and all
variants complete. An early support stop is a completed scientific decision, not a missing-analysis
runtime failure. Verification checks the hash inventory, every recorded action/label, declared
denominators and gate/decision before interpreting success counts. The next TODO owns physical
execution and a separate read-only audit of the resulting bundle.

No asset was deleted or externally backed up. V1/v2 outputs and this preparation remain preserved.


### V3 execution (2026-09-10)

Status: **completed and independently verified**, both run/audit exit receipts 0.
Scientific runtime: 603.42 seconds; no job remains active. Before launch, 25 frozen file references,
15 source/input hashes and the immutable workspace image were verified. Free disk: 89 GiB.
GPU memory: 6,663/32,607 MiB; existing workloads left intact; physics remains CPU.

```bash
tmux new-session -d -s research3_q11_v3 'cd /home/yoohyun/research3 && sh buildup/robotics/pilot_studies/q11-action-compression/v3/run.sh /home/yoohyun/research3/runs/q11_v3 > logs/20260910_q11_v3_run.log 2>&1; echo $? > logs/20260910_q11_v3_run.exit'
```

Cwd `/home/yoohyun/research3`; output `runs/q11_v3/`; per-worker logs are named in
`runs/q11_v3/log_path.txt`. Seed list, support gates and all frozen source remain unchanged.


The separate [v3 audit](audit_v3.py) completed in tmux `research3_q11_v3_audit`, after polling the
scientific exit receipt every five seconds and running only after exit 0. It imports no collector,
simulator or v3 evaluator/support code. It independently decodes packets with integer extraction
and Tokenizer/IDCT, enumerates event windows, recomputes support on the full cohort and checks
physical labels using the frozen v1 analytical routine. It handles pre-intervention stops explicitly.

```bash
sh buildup/robotics/pilot_studies/q11-action-compression/audit_v3.sh /home/yoohyun/research3/runs/q11_v3_audit > logs/20260910_q11_v3_audit.log 2>&1
```

Audit image is the same immutable workspace Q11 image; CPU only, two CPUs / 4 GiB, network off,
source/input/scientific output mounted read-only, separate `/audit` output mount. Expected receipt:
`runs/q11_v3_audit/verification.json`; exit log `logs/20260910_q11_v3_audit.exit`. No extra physics
or scientific reruns. Run and audit commands above execute from `/home/yoohyun/research3`.


### V3 verified results

[Compact results](results_v3.json) and [independent verification](verification_v3.json) are tracked;
`runs/q11_v3/` retains raw trajectories, planned packets/arrays, support and hash manifests.
`runs/q11_v3_audit/verification.json` is the original audit receipt. Frozen v1/v2/v3 sources,
thresholds, seeds, denominators and model inputs remain unchanged; scientific reruns: **0**.

**Facts.** All **24/24** assigned originals completed, succeeded and passed two original
replays each. No replacement or outcome filtering. Original actions total **2,523**, with **137
chunks per codec**. The outcome-free support gate passed on all 24: three codecs available,
joint/Linear rate and MSE within frozen tolerances, and **13 grasp / 16 release** eligible pairs.
The other 11 grasp / 8 release originals have no speed-matched noncontact window and remain
visible in the eligibility counts. No variant was unavailable and no technical failure occurred.

Total physical work: **202 trajectories = 24 originals + 48 replays + 72 full-codec + 58 localized**,
**21,166 executed control actions**. The separate CPU audit passed **642 output hashes**, including
**227 sealed plan/support hashes**, reconstructed **85,472 official labels**, and independently
decoded **411 planned/executed codec chunks**. Initial-state, full original replay-state and packet
reconstruction maximum differences were all **0**. Event/free normalized arm-MSE difference was
at most **7.63e-21**. The audit independently enumerated matching windows, recomputed the support
gate, paired/bootstrap statistics and the final stop rule, with scientific outputs read-only.

| Full-episode codec (all exact gripper) | Success / 24 | Lost / gained vs original | Bytes/chunk | Joint-normalized arm MSE |
| --- | ---: | ---: | ---: | ---: |
| FAST joint | 10 | 14 / 0 | 34.1533 | 9.63662e-5 |
| FAST quantile | 23 | 1 / 0 | 41.3796 | 8.45147e-6 |
| Linear 6-bit / 3-knot | 4 | 20 / 0 | 36.6350 | 9.05953e-5 |

Linear costs about **7.27% more** and has **5.99% less** mean arm MSE than joint FAST on this
cohort, satisfying approximate support; it is not equal-budget dominance. Linear-minus-joint
success difference is −0.25, descriptive paired bootstrap 95% interval [−0.5417, +0.0417], with
10 lost and four gained successes relative to joint FAST. This interval does not establish a
population-level codec ranking. FAST quantile has substantially lower error and a higher rate;
its 23/24 successes do not establish a learned-policy or universal normalization result.

| Localization | Eligible pairs | Event success | Free success | Event fails / free succeeds | Opposite | Exact two-sided p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Grasp | 13 | 12/13 | 13/13 | 1 | 0 | 1.000 |
| Release | 16 | 12/16 | 16/16 | 4 | 0 | 0.125 |

There **are observed directional outcome differences**. Neither event meets the predeclared
Bonferroni alpha **.025**. Do not describe this as all outcomes identical or as proof that contact
never matters. Do not pool the two event types after seeing results: the tests and correction
were frozen separately, and the event observations are not all independent episode draws.
The full joint codec loses 14 original successes, so `STOP_NO_FAILURE_LINK` does not apply.
The verified final decision is **`STOP_NO_CONTACT_LOCALIZATION_SIGNAL`**: the bounded study
failed to establish its required diagnostic signal with the fixed population and exposure.

The audit retains descriptive per-case final predicates. Joint FAST's 14 failures all end
off-stack/ungrasped; five never attain sampled grasp. Linear's 20 failures include 17 off-stack
and three on-stack but nonstatic; nine never attain sampled grasp. The quantile failure ends
on-stack but nonstatic. These endpoint descriptions are not established causal explanations.
Configuration, clearance, acceleration, sampled contact resolution and the original stopping
horizon remain limitations. No extra settling or relabeling was added to turn these into successes.

**Disposition under the precommitted rule.** End the current Q11 contact-sensitive method route;
no more seed, amplitude, codec-grid or task expansion follows this bounded revision. Keep the
observed release/grasp differences as uncertain evidence, not a new-method claim or proof of
zero effect. [Stage 7 closure](../../../selection.md#q11--discontinue-current-route-2026-09-10)
records the scope of termination. The next work is comparative reassessment of reserves,
including Q12, within the existing Robotics scope. No hypothesis, new learned method, artifact
deletion, or external backup verification occurred.
