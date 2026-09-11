# Q1 Predicate Stability Study

Updated: 2026-09-08

## Status

`completed`: frozen [v3 protocol](manifest_v3.md)의 실행·독립 검증을 완료했다.
Outcome: `NO_LABEL_CHANGES_UNINFORMATIVE`; Stage 7 decision: Q1 `refine`.
Protocol의 `not executed`는 작성 당시 상태이며 파일을 수정하지 않는다.
별도 CUDA Docker image/cache/output을 사용하고 Q8 결과는 읽기 전용 provenance다.

## Pre-outcome implementation decisions

- ManiSkill commit과 두 checkpoint는 v3 그대로다. Q8에서 받은 verified source와 checkpoints를
  read-only build/input 경로로 사용한다. No pre-workspace Docker/Isaac asset is used.
- [PyTorch 2.7 release](https://pytorch.org/blog/pytorch-2-7/)의 Blackwell 지원을 근거로
  Torch 2.7.1 / CUDA 12.8 wheel을 사용한다. SAPIEN 3.0.2, numpy 1.26.4,
  gymnasium 0.29.1 등 selected simulator dependencies를 기록한다.
- RTX 5090 snapshot: 13,802/32,607 MiB used, 65% utilization; free disk 109 GiB.
  8 evaluation environments, 4 host CPU / 12 GiB RAM으로 bounded workload를 순차 실행한다.
  기존 GPU workload를 중단하지 않는다. No training.
- Pinned official `ppo.py` 전체를 실행하고 `gym.make`의 evaluation environment에 observation-only
  recorder를 추가한다. `--evaluate --seed 1 --num-eval-envs 8 --num-eval-steps 50`이며
  official extra reset과 eval reconfiguration을 보존한다. Video는 끄고 state HDF5를 기록한다.
- 초기 reset과 official evaluation 직전 reset은 구분한다. 실제 첫 action 직전 state를
  paired initialization으로 비교한다. Final state는 auto-reset 이전 wrapper에서 기록한다.
- Official Panda static predicate는 max(abs(7 arm qvel)) <= 0.2다. v3 prose의 `<0.2`보다
  source의 official predicate preservation을 따른다. Exact-boundary occurrence도 검증한다.
- 20/25/30 mm × once/end grid, 16 trajectories와 disconfirmation rule은 불변이다.
  No threshold/seed search or automatic hypothesis promotion.

## Reproduction and jobs

CWD: `/home/yoohyun/research3`.
Source context: `external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8` (read-only).
Inputs: `datasets/q8/ppo_*_ckpt.pt` (read-only); output/cache: `runs/q1_v3/` and
`runs/q1_v3/cache/`; logs: timestamped `logs/*q1*`.

Build: `sh buildup/robotics/pilot_studies/q1-predicate-stability/build.sh` in tmux
`research3_q1_build`, with `--pull --no-cache`. Image name `research3-q1-predicate:v3`.
Expected: image ID, dependency/OS records and GPU binary cache receipt before offline evaluation.
Build/run/verification commands and measured results are accumulated here.

## Frozen execution and verification

Build log/status: `logs/20260908_q1_build.log` and `logs/20260908_q1_build.exit`.
The v3 manifest's pre-run hash is retained in `runs/q1_v3/protocol.sha256`.

```bash
Q1_NETWORK=bridge sh buildup/robotics/pilot_studies/q1-predicate-stability/run.sh smoke.py
sh buildup/robotics/pilot_studies/q1-predicate-stability/run.sh evaluate.py pd_ee_delta_pos
sh buildup/robotics/pilot_studies/q1-predicate-stability/run.sh evaluate.py pd_joint_delta_pos
sh buildup/robotics/pilot_studies/q1-predicate-stability/run.sh relabel.py
sh buildup/robotics/pilot_studies/q1-predicate-stability/run.sh verify.py
```

Smoke seed 901 only checks CUDA/backend readiness; no frozen policy is evaluated in that check.
It may download the required SAPIEN PhysX GPU binary into the new `/cache` mount and records its
checksum. Scientific execution then disables networking. Each policy runs in a fresh container.
Explicit `--runtime=nvidia --gpus device=0`; Vulkan ICD from pinned source and system EGL library.

Output: `runs/q1_v3/{ee,joint}/trajectory.{h5,json}`, each HDF5 has 51 snapshots × 8 environments
and 50 actions × 8 environments. Initial repeated resets before first action produce no extra
trajectory. Completed files use exclusive creation and hashes; no output overwrite.

`relabel.py` first requires exact paired actor/articulation/cube/goal/qpos/qvel initialization.
It produces `matching.json`, `labels.csv`, `summary.json`, `distance.png` and `distance.pdf`.
`verify.py` independently reconstructs all labels from raw actor and articulation state (not the
producer's extracted distance/static columns), checks 800 official step labels and exact initial
matching, and writes `verification.json`. Both use the same frozen six predicates. Sign changes
involving a tie are distinguished from strict rank reversals.

Sequential orchestration: `sh buildup/robotics/pilot_studies/q1-predicate-stability/execute.sh`
under tmux `research3_q1_execute`. Logs are `logs/20260908_q1_{smoke,ee,joint,relabel,verify}.log`;
outer status is `logs/20260908_q1_execute.exit`. A nonzero exit stops dependent stages.

## Verified results

Build and complete execution exited 0. Two fresh offline GPU containers ran the unchanged
official PPO entrypoint with passive recording. Torch CUDA and PhysX CUDA were both active.
Image ID: `sha256:975debd34a94b33182f73f73151d1e7c6b1c65a67f055db976805af6ac805681`.
PhysX GPU library version `105.1-physx-5.3.1.patch0`, 236,705,440 bytes, SHA-256
`4c582a16509a71faf5592fe9708586dfcc7ab61ae932eabc1ddd81f290818706`.

| Threshold | PPO-EE once / end | PPO-Joint once / end | EE − Joint |
| --- | --- | --- | --- |
| 20 mm | 4/8 / 4/8 | 8/8 / 8/8 | −0.50 |
| 25 mm (official) | 4/8 / 4/8 | 8/8 / 8/8 | −0.50 |
| 30 mm | 4/8 / 4/8 | 8/8 / 8/8 | −0.50 |

- 8 paired initializations exactly matched for every recorded actor/articulation and cube,
  goal, qpos and qvel; maximum error 0. Both policy metadata retain per-episode state hashes.
- 16 complete 50-step trajectories; all 96 labels independently reconstructed from raw actor
  and articulation fields. All 800 official step success labels agreed.
- Changed trajectories: 0/16; sign changes: 0; strict rank reversals: 0.
- No exact static-threshold boundary values were observed. Inclusive source semantics therefore
  did not introduce a difference from the frozen prose shorthand.
- No policy rerun, new seed, threshold/aggregation change, training or sample expansion followed
  this negative result. Hypothesis/paper promotion did not occur.

Compact artifacts: [all 16 rows](labels.csv), [summary](result.json),
[initial matching](matching.json), [independent verification](verification.json),
[runtime](runtime.json), [dependency lock](dependencies.lock), [OS lock](os-packages.lock),
[distance plot](distance.png) / [PDF](distance.pdf), [checksums](checksums.txt).
Raw HDF5/metadata remain under ignored `runs/q1_v3/{ee,joint}/`.

## Diagnosis of the negative result

`diagnose.py` reads only the frozen trajectories; this is descriptive analysis, not a new
evaluation. Command: `sh buildup/robotics/pilot_studies/q1-predicate-stability/run.sh diagnose.py`.
Log `logs/20260908_q1_diagnose.log`, exit 0; output [diagnosis](diagnosis.json).

All 12 successful episodes end 6.00--16.74 mm from the goal with the official static condition,
inside even the strictest 20 mm variant. PPO-EE failures 2/4/6 never approach 30 mm (minimum
distances 215.95/271.29/246.61 mm). Failure 3 briefly enters 30 mm (minimum 27.76 mm) but is never
robot-static; arm maximum speed on those near-goal steps is 0.4528--4.0806, above 0.2. Thus neither
the frozen distance grid nor once/end aggregation changes any episode's result.

The case-level distinction is well-inside-goal success versus large-distance/robot-motion failure,
not a concentration of marginal cases near the chosen conjunction boundary. This describes
these named artifacts only. It does not show that one action interface/algorithm is generally
superior or that success-predicate sensitivity cannot occur elsewhere.

## Stage 7 decision and next boundary

**Agent decision: `refine` Q1; current two-policy/PickCube v3 route is uninformative and is not
expanded.** Measurement access is supported, but the hypothesized predicate-dependent ranking
phenomenon is unsupported on the frozen sample. No unresolved measurement issue warrants an
identical repeat. Eight episodes per policy do not establish general ranking stability.

Next work is a bounded formulation/population review, using this diagnosis and public artifact
metadata to determine whether a semantically justified, informative route exists. Do not select
new thresholds/seeds just to create a reversal, and do not label an exploratory new population
as confirmation of v3. Without a defensible refinement, discontinue Q1 rather than expanding
the evaluator. The repository-wide decision is owned by
[selection](../../../selection.md#q1-v3--refine-2026-09-08).

## Recovery

The runner mounts the fixed `runs/q1_v3/` output/cache path. For full rerun, first transfer and
checksum-verify the original bundle elsewhere, then prepare an empty output path; retain the
original timestamped logs too. Scripts refuse to overwrite existing evaluation outputs.
Verify the recorded bundle from the repository root with
`sha256sum -c buildup/robotics/pilot_studies/q1-predicate-stability/checksums.txt`.
The ignored HDF5 files and PhysX
cache need separate transfer; compact CSV/JSON/plots/code alone preserve the reported pilot
summary but not independent trajectory reanalysis. No data, cache or image was deleted.
