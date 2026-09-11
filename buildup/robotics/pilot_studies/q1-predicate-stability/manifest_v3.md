# Q1 Success-Predicate Stability — Small Feasibility Study v3

Created: 2026-09-04

## Status

`specified`, `not executed`

This is a Stage 6 small-subset feasibility study under
[`docs/buildup.md`](../../../../docs/buildup.md). It tests measurement accessibility and may
produce a preliminary counterexample; it is not a full benchmark result.

## Research Question

For two named public `PickCube-v1` PPO artifacts, can alternate local distance thresholds or
official temporal aggregations change their pairwise ordering on fixed recorded rollouts?

## Source And Inputs

- ManiSkill3 tag: `v3.0.1`
- source commit: `a4a4f9272ad64b1564035874b605ceb687b63ed8`
- dataset repository: `haosulab/ManiSkill_Demonstrations`
- dataset revision: `d674485bbffdd533914e52d272fdda34c0515608`
- task: `PickCube-v1`, Panda, state observation, 50-step horizon, PhysX CUDA
- deterministic policy inference with the pinned official `ppo.py`

Policy artifacts:

1. `ppo_pd_ee_delta_pos_ckpt.pt`, SHA-256
   `0b17b5ed9690ccf83111d0f09af8d1599f69ee7ba0077e1aac48814ac78ce99c`
2. `ppo_pd_joint_delta_pos_ckpt.pt`, SHA-256
   `78959417279892d73e4ed5930a6d8de8626a24eee0ec553dfc6af61391b0b356`

The policies differ in control mode. Therefore the claim is restricted to evaluator
stability for these artifacts; no claim about a superior algorithm or action interface is
allowed.

## Environment And Output Boundary

- use a new project-specific Dockerfile/image/container and new cache/output paths;
- do not use, run, modify or delete pre-existing Docker/Isaac assets;
- mount downloaded public artifacts read-only after checksum verification;
- write each policy trajectory to a distinct versioned output path;
- retain raw `.h5/.json`, stdout, source/config manifest and checksum file unchanged.

No image is built and no artifact is downloaded by this specification step.

## Evaluation Sample

- evaluation seed: official script seed `1` for both policies;
- `num_eval_envs=8`, the pinned script default;
- `num_eval_steps=50`, equal to the registered task horizon;
- expected denominator: eight complete trajectories per policy;
- before relabeling, verify that paired initial cube/goal/robot states match across policies;
- if they do not match, do not report a paired comparison and use the Stage 7 `refine` decision.

## Frozen Relabeling Grid

Keep the official robot-static condition, `q velocity < 0.2`. Recompute success for:

- goal distance threshold: `{0.020, 0.025, 0.030}` metres;
- temporal aggregation: `{success_once, success_at_end}`.

The reference is `0.025 m + success_once`, matching the task default and the commonly
reported ManiSkill imitation-learning aggregation. The `±0.005 m` values are a local
sensitivity probe around the official threshold, not a claim that they are universally
equivalent task definitions.

Total expected relabeled output: `2 policies × 8 trajectories × 6 variants = 96`
episode-predicate labels.

## Output Fields

- policy artifact ID, source/dataset revision and checkpoint checksum;
- episode index and initial-state checksum;
- per-step cube-goal distance and robot-static boolean;
- official `success_once` and `success_at_end`;
- six recomputed labels;
- final/minimum distance and number of successful steps.

## Metric And Simplest Baselines

Primary descriptive metric:

- whether the sign of `success_rate(PPO-EE) - success_rate(PPO-Joint)` changes relative to
  the reference variant.

Always report:

1. official binary success;
2. final and minimum continuous distance per trajectory;
3. `success_once` and `success_at_end` together;
4. the complete 16-trajectory label table.

With eight trajectories per policy, no confirmatory statistical or generality claim is
allowed.

## Feasibility Success And Disconfirmation

Measurement feasibility is supported only if both checkpoints load, each produces eight
complete immutable state trajectories, initial-state matching is verified and all six labels
can be reconstructed independently of the policy code.

Decision branches:

- no reconstructable state or no matched initialization: `refine` the study design;
- no trajectory changes label anywhere in the frozen grid: selected route is uninformative;
  choose `refine` or `discontinue` after reviewing the critical assumption;
- labels change but ordering does not: record the negative result; only `repeat feasibility
  study` if a specific low-cost measurement uncertainty remains;
- ordering changes: record a preliminary counterexample and choose `repeat feasibility
  study`; do not promote directly from eight trajectories.

## Expected Deliverable

A source/runtime verification record, 16-row trajectory summary, 6-column predicate matrix,
continuous-margin plot and one Stage 7 decision.
