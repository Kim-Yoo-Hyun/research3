# Q9 Refresh Observations

Updated: 2026-09-15

## Purpose and status

`completed; further investment deferred`; exploratory observations for
[Q9](../../questions/spatial-memory-refresh.md). Given a known old location, can a sparse refresh
schedule miss the frames that provide depth evidence against it? This is a diagnostic of
observation opportunities, not a new method, DynaMem reproduction or localization benchmark.

Latest: [observed-surface comparison](#surface-comparison-2026-09-15) completed. A simple
visibility schedule captures the measured interval evidence at two depth accesses per case,
but orange exposes unresolved surface correspondence. The first point trace remains below.
The subsequent [research-value review](../../related_work/policy-geometry.md#q9-research-value-2026-09-15)
keeps these results intact and defers further work on the current route.

## First input and comparison

- Dataset: `hello-peiqi/DynaMem-DynaBench`, revision
  `1d561e2de8718addf398e5e967f2c44dc015c366`, `env1/env.pkl` (54,700,824 bytes).
- Expected SHA-256: `9b4f894a63556563fe7bc856d32131948b2b5df495d1aab5b88a2dc1834b1897`.
- Annotation/time source: existing [source record](../../related_work/reassessment_sources.json).
  Checkpoints 14 and 26; `metal bowl` and `orange` are exploratory cases selected after reading
  labels. Initial coordinates are privileged approximate diagnostic seeds. Later labels never
  drive scheduling; these coordinates are not verified object surface landmarks.
- Read raw per-frame depth, camera poses and intrinsics. Do not use full-sequence combined
  semantic features. First resolve whether checkpoint numbers identify frame counts or times.
- Compare sparse periodic phases and a simple causal depth-evidence trigger, if valid frames
  exist. Charge all inspected depth/pose frames to the trigger; equal map writes alone do not
  establish equal compute. The all-frame trace is a diagnostic reference.
- Observe frustum/occlusion/free-space evidence for an old point. A point test does not prove
  whole-object absence, updated object identity or successful language grounding.
- If data cannot support this comparison cheaply, retain the reason and assess a smaller
  constructed observation. No automatic threshold tuning to obtain a desired effect.

## Execution boundary

One public sequence, CPU only, no pretrained model, no robot client or external service. New
workspace-owned images `research3-q9-refresh:v1` and `v2`; runtime mounts only selected input read-only and
its output directory, with network disabled. No pre-workspace image is a research dependency.
Input/schema inspection precedes numerical interpretation in the same bounded task. Use a
5-minute runtime limit, 2 CPUs and 4 GiB RAM; adapt only with recorded reasons.

Outputs live under ignored `runs/q9/`; inputs under ignored `datasets/q9/`. Docker recipe,
dependency versions, commands and outcome are recorded here. No previous study is modified.

## Commands and jobs

Working directory: `/home/yoohyun/research3`. Download and build ran in separate tmux sessions
`research3_q9_download_20260915` and `research3_q9_build_20260915`; both completed. Their logs and
exit files use `logs/20260915_q9_download.*` and `logs/20260915_q9_build.*`. Input inspection
completed with a dependency failure, recorded in `runs/q9/inspect_v1/schema.json` and
`logs/20260915_q9_inspect.log`: input bytes/hash match, but the pickle requires PyTorch.
Version 2 adds CPU PyTorch 2.8.0 and maps serialized tensor storage to CPU. No input or result
selection changed; version 1 output remains preserved. This is a preparation issue, not a
question-level failure. The v2 build, inspection, first trace and visual inspection completed.

```bash
wget -c --timeout=30 --tries=3 -O datasets/q9/env1/env.pkl https://huggingface.co/datasets/hello-peiqi/DynaMem-DynaBench/resolve/1d561e2de8718addf398e5e967f2c44dc015c366/env1/env.pkl
docker build --pull -t research3-q9-refresh:v1 buildup/robotics/pilot_studies/q9-refresh
timeout 300s docker run --name research3-q9-inspect-v1 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 4g --pids-limit 64 --user "$(id -u):$(id -g)" --mount type=bind,src=/home/yoohyun/research3/datasets/q9/env1,dst=/input,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q9/inspect_v1,dst=/output research3-q9-refresh:v1 --input /input/env.pkl --output /output/schema.json
```

For a rerun, use a new container name and output directory. The inspector checks expected input
bytes/SHA-256 and records Python/NumPy versions; it does not overwrite its output.

Execution environment: Python 3.11.14, NumPy 2.2.6, PyTorch 2.8.0+cpu; exact resolved packages
are in [requirements.lock](requirements.lock). V2 was built with those direct pins; the current
Dockerfile pins its observed base digest and resolved dependencies for future rebuilds.

| Artifact | Immutable identity / location |
| --- | --- |
| first dependency-failure image v1 | `sha256:ad32f46c6d79e854bd78cbe228f3bd06847c84640efa15cc55ff4e5f403f15f7` |
| executed CPU image v2 | `sha256:7eca5af889f3bd97fb795f74f86bd6832aa3d2b2887ba283ca83503b6f109df5` |
| observation source | [observe.py](observe.py); executed SHA-256 `2b16349a0112937d6e95875cfa53b6ea5b9cfe5aed7c773dfa4d87322af9ae75` |
| input schema | `runs/q9/inspect_v2/schema.json` |
| full point trace and result | `runs/q9/observation_v1/trace.jsonl`, `result.json` |
| visual interpretation | `runs/q9/visual_v1/metal_bowl.png`, `orange.png`; [render_cases.py](render_cases.py) |
| compact result | [outcome.json](outcome.json) |

The v2 build command substitutes `research3-q9-refresh:v2` for v1 above; its tmux session was
`research3_q9_build_v2_20260915`, log/exit prefix `logs/20260915_q9_build_v2`.
The v2 inspection substitutes container `research3-q9-inspect-v2`, image `:v2`, output mount
`runs/q9/inspect_v2`; log `logs/20260915_q9_inspect_v2.log`. Its exit code was 0 (v1 was 2).
The trace command below exited 0; log `logs/20260915_q9_observe.log`. No random sampling is used.

```bash
timeout 300s docker run --name research3-q9-observe-v1 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 4g --pids-limit 64 --user "$(id -u):$(id -g)" --entrypoint python --mount type=bind,src=/home/yoohyun/research3/datasets/q9/env1,dst=/input,readonly --mount type=bind,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q9-refresh/observe.py,dst=/study/observe.py,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q9,dst=/output research3-q9-refresh:v2 /study/observe.py --input /input --output /output/observation_v1
```

Visual inspection used the same runtime limits and image, mounting this study read-only at
`/study`, `runs/q9/observation_v1` read-only at `/results`, and `runs/q9` at `/output`; entrypoint
`python /study/render_cases.py /output/visual_v1`, container `research3-q9-visual-v1`, log
`logs/20260915_q9_visual.log`, exit 0. These frames were selected after the trace to interpret it.

## What we learn

Before the first depth trace: the input has 42 raw RGB/depth/pose/intrinsics entries and no
timestamps or semantic features. Use zero-based indices 15–24 as an interior diagnostic window,
not the official evaluation boundary. Old points come only from checkpoint 14. Fix a 3×3 median
with at least five finite depth values in (0.1, 2.0] m, old-point range (0.1, 2.0] m, and a 0.05 m
residual margin for this exploratory trace. Keep continuous residuals. Do not infer whole-object
absence from a ray. Check pose validity and compare inverse versus rigid-transform projection.
Five periodic phases each read two frames; a causal first-evidence control stops at its first
free-space observation. Its frame-read cost is reported separately, so this is not a matched
compute or equal-write superiority test.

A useful contrast identifies an observation missed by a schedule and suggests a visibility-aware
simple control. If every schedule sees the same evidence, this case does not motivate a new
trigger. Missing evidence may instead mean occlusion, pose/depth uncertainty or inappropriate
input timing; it is not evidence that memory refresh never matters.

## Observations and interpretation

**Facts.** The input contains 42 raw frames, only RGB/depth/pose/intrinsics, and no timestamps or
combined semantic features. All 42 basic camera/shape checks passed. Inverse and rigid-transform
projections differed by at most `1.15e-7` in camera coordinates. This checks implementation
consistency, not calibration or semantic correspondence. Official checkpoint indexing and pose
estimation provenance remain unresolved; the inspected interval is only an array-index diagnostic.

| Approximate old query coordinate | Depth evidence in indices 15–24 | Five periodic phases, two frame reads each |
| --- | --- | --- |
| metal bowl | 17 and 22 exceed the 0.05 m margin; residuals 0.0648 and 0.0745 m | Only phase 2, selecting [17,22], captures it; the other four capture none. |
| orange | No free-space evidence; index 19 remains within the margin. | All five capture none. |

These five phases are schedules of the **same two selected cases**, not five independent trials
or a population failure rate. The causal first-evidence control reads three depth frames before
updating at 17 for the bowl; for orange it reads ten and never updates. Its read cost and number
of writes differ from periodic, so no equal-cost superiority follows.

**Visual facts.** In the diagnostic RGB panels, the initial orange query coordinate projects to
the table near the fruit, rather than the fruit surface. At frame 17 the metal bowl is still
visible near the projected old coordinate; at 22 the marked region shows table. Thus the released
query coordinate/tolerance is not an exact object surface point. The `oracle_initial_point` key
in the raw result records a privileged annotation seed, not a verified object landmark.

**Agent inference.** Refresh phase can miss sparse point evidence, but that observation alone is
not object removal, localization success, or a new mechanism. The initial point interpretation
needs refinement: use small manually identified object surface regions in the initial RGB-D
frame, preserve occluded/out-of-view as unknown, and compare relevant simple visibility controls.
Do not change the existing margin or replace these outputs to manufacture an object-level gain.
Both the useful timing contrast and the orange/visual counterexamples are retained.

## Surface comparison plan

The following continuation was selected and executed; its choices were recorded before the
new surface trace. [regions.json](regions.json) contains two small initial RGB regions and nine
interior samples each: bowl frame 0 and orange frame 2. Both initial views and later results were
already inspected, so this is an exploratory repair, not held-out confirmation. Keep the old
0.05 m residual margin, depth limits and indices 15–24. Backproject using only initial depth.

Compare all five periodic phases (two reads each) with the earliest current frame where at
least five stored points project within the image/range. The visibility rule receives pose/K
only, never unselected depth or later annotations. A deadline fallback spends any remaining
budget on the last available frames, so both schedules use exactly two depth reads. Pose checks
are counted separately; this is matched depth access, not matched total computation. At least
five of the fixed nine points must have free-space evidence to contradict the sampled region;
occluded/out-of-view/invalid points remain unknown, not negative evidence. All-frame diagnostics
and initial-view controls are separate from schedule decisions. No object-absence claim follows.

## Surface comparison 2026-09-15

**Execution facts.** [surface.py](surface.py) ran in the existing workspace-owned CPU v2 image
with the unchanged input, margin, depth range and interval. Nine fixed samples per object were
backprojected from its initial RGB-D frame. Initial RGB inspection places the samples on the
bowl/fruit; it does not establish cross-view correspondence. All 18 initial depths were valid.
Initial reprojection roundtrips passed; this is an algebraic check, not calibration validation.
Each case has a separate two-access budget. This is not a joint multi-object scheduler.

| Initial surface region | Periodic, all five phases | Simple visibility schedule | Interval evidence |
| --- | --- | --- | --- |
| metal bowl, frame 0 | Only phase 2, [17,22], captures a contradiction. | [17,22]; 2 depth accesses, 8 scheduling pose checks, 18 depth patches. | 17: all 9 consistent; 22: all 9 free-space, residual 0.0729–0.1073 m. |
| orange, frame 2 | Only phase 4, [19,24], captures a contradiction. | [19,24]; 2 depth accesses, 10 scheduling pose checks, 9 depth patches. | 19: 7/9 free-space, residuals over all 9 points 0.0494–0.0709 m. Frame 24 is an out-of-view deadline fallback. |

Each periodic phase uses two scheduling/evaluation pose checks and two depth accesses. The
five phases reuse the same cases; they are not independent trials or an 80% population failure
rate. Visibility selection uses current pose/K and the stored points only. It matches the
case-specific best periodic phase here and captures all interval contradictions in the offline
reference, with extra pose checks. It does not establish expected superiority over periodic.

The cost unit is **selected depth-frame access/evaluation**, not sensor acquisition or total
compute. Both methods share one initial RGB-D frame per case. Out-of-view selections still
consume their scheduled frame access but read no patches; each plan tests 18 point candidates.
Pose counts describe distinct frames checked by the schedule/evaluator, not matrix-inversion
calls: the implementation also reprojects during selected-frame evaluation. The full pickle is
loaded for offline replay and the full trace is computed after selection, so no wall-time,
semantic-inference, map-write or deployment-compute saving is measured.

**Visual observations and counterevidence.** Four-panel RGB images show initial/17/19/22,
left to right. The bowl surface samples lie on the visible bowl at 17 and on table at 22.
Unlike the earlier approximate-coordinate test, frame 17 is now consistent without changing
the 0.05 m margin. This resolves that particular seed interpretation problem.

Orange's initial/9 control panels show the fruit still visible at 9 while the old projected
samples lie on table next to it. At 19 the fruit is also visible near, rather than under, the
projected samples. Frame 9 already has 9/9 free-space contradictions (0.0841–0.1457 m), before
the selected interval. The initial-range summary is therefore 1 consistent, 10 unknown and
1 contradicted frame for orange (indices 2–13); bowl has 2 consistent and 12 unknown (0–13).
These ranges are **not verified unchanged-object controls**: actual movement, camera registration
error and surface correspondence remain unresolved. Do not call the orange contradiction a
confirmed false positive or a confirmed movement/removal. Presence somewhere in the image does
not settle old-location validity. Unknown views remain in the fixed denominator.

**Agent inference.** Availability of a view is enough to explain the schedule contrast on these
sampled points; the run provides no evidence that a learned scheduler is needed. Initial surface
seeding improves the bowl example but does not turn the orange trace into an object-level event
detector. A frustum/range test is geometric eligibility, not visibility through occluders.
Additional object-level claims need correspondence evidence relevant to the claim. This local
limitation is not a refutation of Q9 as a whole and is not a new contribution by itself.

### Execution and verification

Run from `/home/yoohyun/research3`:

```bash
bash buildup/robotics/pilot_studies/q9-refresh/run_surface.sh
```

[run_surface.sh](run_surface.sh) records the exact immutable image, read-only input/study mounts,
CPU/memory limits, network isolation, entrypoint and a fresh timestamped output/log path. No
random sampling or GPU is used. Both jobs below completed with container exit 0.

| Run | Output directory | Log / exit prefix |
| --- | --- | --- |
| `research3-q9-surface-20260915_115726` | `runs/q9/surface_20260915_115726/result/` | `logs/20260915_115726_q9_surface` |
| `research3-q9-surface-20260915_120106` | `runs/q9/surface_20260915_120106/result/` | `logs/20260915_120106_q9_surface` |

The first run called all 18 candidate point tests `depth_patch_reads`, even when geometry
prevented a patch read. The second run corrects only this accounting, adds
`surface_point_tests`, and renders initial-range control views. The first executed source and
regions are preserved beside its output. Source SHA-256 changed from
`e3eac8202a415f51575a41165aeee6ef616502a99d2a099b0036f9bc5c2e329b` to
`51e3b05de71ac2afc2892c8b7dc4a237fe61fe8df29e8f4ff109cfb28b5d8cbc`.
Regions SHA-256 is `0829ab6b860fc62d1f4a0c2bc394f151496c98741cff75db3bd33c1fdc633676`.

Both runs pass six in-container controls: consistent surface, free space, occlusion, invalid
depth, out-of-view deadline budget, and causal geometry-only selection. The second output's
`verification.json` records matching source/config identities, 84 serialized trace rows,
12 schedules of exactly two accesses, and schedule readings matching the reference rows.
Full trace bytes and the original two RGB panels are identical across the accounting correction;
all numerical results and decisions match. These are implementation/record checks and a repeat
after a reporting fix, not independent physical ground truth or statistical replication.
The compact tracked [outcome.json](outcome.json) retains the first observation and adds
`surface_comparison`; raw traces, images and the verification receipt remain under `runs/q9/`.

## Next bounded observation

The initial-surface comparison and subsequent
[prior/investment review](../../related_work/policy-geometry.md#q9-research-value-2026-09-15)
are complete. Q9 is now `deferred`: the simple control explains the measured interval coverage,
while further correspondence repair currently lacks a concrete next explanation beyond the
identified priors. This does not change the raw results or settle orange's motion/registration
ambiguity. No new execution is queued here. The question record owns
[re-entry considerations](../../questions/spatial-memory-refresh.md#investment-decision-and-re-entry);
the next repository task is a bounded Q7/Q14 comparison.

## Preservation and verification

There is no paper result. Preserving this diagnostic requires raw traces/results, the visual
interpretation, input identity/annotations and these sources. Resuming needs the input plus v2
image (or pinned rebuild); full reproduction additionally needs registry distributions and the
dataset URL above. No external backup was verified and no deletion was performed.

For verification, inspect container exit codes and image IDs with `docker inspect`, compare the
recorded input/source SHA-256, and rerun the trace in Docker to a new path only if reproducing its
numerical result is needed. The visual check limits the interpretation; it is not an independent
object-localization evaluation.

## Docker cleanup review 2026-09-16

Image/container 삭제 후보와 재개·전체 재현에 미치는 영향은
[repository cleanup review](../../../../docs/reproducibility.md#docker-cleanup-review-2026-09-16)가 소유한다.
이번 검토는 읽기 전용이며 Docker 자산을 삭제하지 않았다. 기존 실행/보존 기록은 유지한다.
