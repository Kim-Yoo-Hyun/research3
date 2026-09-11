# Q1 Public Artifact And Evaluator-Schema Audit

Updated: 2026-09-08

Current disposition: [bounded refinement audit](#bounded-refinement-audit--2026-09-08).
The original 2026-09-04 pre-execution audit below is historical; CUDA execution is now
verified in the [v3 study](../pilot_studies/q1-predicate-stability/README.md).

## Audit Boundary

이 문서는 Q1의 공개 실행 기반과 denominator를 결과 생성 전에 확인하는 read-only
audit이다. ManiSkill package, dataset, checkpoint와 simulator는 내려받거나 실행하지
않았다. 기존 host Docker/Isaac 자산도 조회·실행·수정·삭제하지 않았다.

The source/artifact audit was extended on 2026-09-04. No package, checkpoint or dataset was
downloaded to the workspace during the extension.

## Official Sources Checked

- [ManiSkill3 repository](https://github.com/haosulab/maniskill)
- [replay documentation](https://maniskill.readthedocs.io/en/latest/user_guide/datasets/replay.html)
- [learning-from-demonstrations setup](https://maniskill.readthedocs.io/en/latest/user_guide/learning_from_demos/setup.html)
- [custom-task evaluator tutorial](https://maniskill.readthedocs.io/en/latest/user_guide/tutorials/custom_tasks/intro.html)
- [advanced state tutorial](https://maniskill.readthedocs.io/en/latest/user_guide/tutorials/custom_tasks/advanced.html)
- [PickCube evaluator source](https://maniskill.readthedocs.io/en/latest/_modules/mani_skill/envs/tasks/tabletop/pick_cube.html)
- [StackCube evaluator source](https://maniskill.readthedocs.io/en/latest/_modules/mani_skill/envs/tasks/tabletop/stack_cube.html)
- [PlugCharger evaluator source](https://maniskill.readthedocs.io/en/latest/_modules/mani_skill/envs/tasks/tabletop/plug_charger.html)
- [official baseline documentation](https://maniskill.readthedocs.io/en/latest/user_guide/reinforcement_learning/baselines.html)
- [VLA-Arena project](https://vla-arena.github.io/) and
  [repository](https://github.com/PKU-Alignment/VLA-Arena)

## Verified Schema Facts

### Trajectory And Replay

- ManiSkill raw demonstrations pair `trajectory.h5` with `trajectory.json` and retain
  initial states, actions and seeds.
- The official replay utility can use recorded environment states directly with
  `--use-env-states`, and can regenerate observations and rewards during replay.
- Compressed demonstration files can omit observations while retaining the information
  required for reproducibility.
- Evaluation records distinguish at least `success_once` and `success_at_end`; the
  official learning-from-demonstrations guide recommends full-episode evaluation and
  commonly reports `success_once`.
- `env.get_state_dict()` exposes actor and articulation state, and a task may add custom
  state required for exact replay.

These facts establish that post-hoc relabeling is structurally possible when the selected
rollout artifact actually retains environment states or can be deterministically replayed.
They do not establish that every public policy result exposes such a rollout.

### Evaluator Constituents

| task | official success structure | directly exposed diagnostic |
| --- | --- | --- |
| `PickCube-v1` | object-goal distance below `0.025 m` and robot static | `is_obj_placed`, `is_robot_static`, `is_grasped`; robot-static velocity threshold is `0.2` in source |
| `PlugCharger-v1` | object-goal distance at most `0.005 m` and angular error at most `0.2 rad` | raw `obj_to_goal_dist`, raw `obj_to_goal_angle` |
| `StackCube-v1` | bounded xy/z placement error, cube static and no longer grasped | placement/static/grasp constituent booleans |

`PickCube-v1` and `PlugCharger-v1` are the first pilot pair because each has a compact,
interpretable conjunction and at least one continuous geometric margin. `StackCube-v1` is
a reserved third task, not part of the initial denominator.

## Artifact Decision

### Selected First Route

`ManiSkill3 v3.0.1` at commit
`a4a4f9272ad64b1564035874b605ceb687b63ed8` is the selected first benchmark substrate.
Repository code is Apache-2.0. The official README states that rigid-body environments use
permissive licenses and assets use CC BY-NC 4.0. The public demonstration dataset declares
Apache-2.0; its selected immutable revision is
`d674485bbffdd533914e52d272fdda34c0515608`.

### Comparable Pairwise Input

The official demonstration repository contains pretrained `PickCube-v1` PPO checkpoints
for multiple control modes. The initial feasibility pair is:

| input | task/observation | control mode | checkpoint SHA-256 |
| --- | --- | --- | --- |
| PPO-EE | `PickCube-v1`, state | `pd_ee_delta_pos` | `0b17b5ed9690ccf83111d0f09af8d1599f69ee7ba0077e1aac48814ac78ce99c` |
| PPO-Joint | `PickCube-v1`, state | `pd_joint_delta_pos` | `78959417279892d73e4ed5930a6d8de8626a24eee0ec553dfc6af61391b0b356` |

Both are evaluated by the same pinned PPO script, task version, Panda robot, state
observation, 50-step horizon and deterministic action selection. Control mode is an explicit
policy difference, so this comparison cannot support a controller- or algorithm-fairness
claim. It is sufficient to test whether the evaluator choice changes the ordering of these
two named artifacts.

The pinned PPO evaluation path sets `save_trajectory=True` when `--evaluate` is used. This
removes the trajectory-recording blocker for the small feasibility study. The official BC
and Diffusion Policy recipes remain possible later inputs, but they require training and are
not needed for the first study.

Pinned source checksums:

| source | SHA-256 |
| --- | --- |
| `pick_cube.py` | `6f881f11151bd124a4ec6d1189e86e20b17d366aa1cbcc6e2f751f1f5bb03ed1` |
| `examples/baselines/ppo/ppo.py` | `3fa4818861d428480244aae889bc679b2c8e89b59d6289014003c266a84dbab0` |

### Deferred Expansion Route

VLA-Arena is useful as a later cross-domain/scale check because it publishes 170 tasks,
model configurations and aggregate results. Its public leaderboard result schema is not,
by itself, an immutable per-step state trajectory from which alternate task predicates can
be recomputed. Its VLA checkpoints are also a heavier first feasibility dependency. It is
therefore not part of the initial feasibility route.

## Denominator Audit

| denominator component | assessment | reason |
| --- | --- | --- |
| public tasks and evaluator | `VERIFIED` | executable task code and explicit success constituents are public |
| predicate-family construction | `FEASIBLE_UNTESTED` | a finite family can be defined around official thresholds before execution |
| immutable state/replay schema | `DOCUMENTED_NOT_SELECTED` | framework supports exact state replay; selected rollout files remain unverified |
| comparable policy/rollout inputs | `SELECTED_FOR_FEASIBILITY` | two named public PPO checkpoints share task, evaluator, observation and policy code; control mode differs and bounds the claim |
| exact pilot denominator | `FIXED_IN_PROTOCOL_V3` | one task, two named checkpoints, eight official-default evaluation trajectories each and six predicate/aggregation variants |

The research question is pairwise, so two comparable policies or rollout sources are the
minimum empirical input for a rank-reversal feasibility study. This is a consequence of the
evaluation target, not a general `docs/buildup.md` rule. Three or more policies can strengthen
a later ranking analysis but are not a stage-entry condition. The exact policy count,
trajectory count and predicate grid must be recorded before execution after the artifacts
are known; they may not be changed in response to results.

## Feasibility Finding

The evaluator/schema feasibility and one bounded pairwise study design are supported by
public artifacts. This does not establish that the checkpoints load successfully in a new
container, that their initial states match, or that alternate predicates change any label.
Those are the remaining uncertainties in [protocol v3](../pilot_studies/q1-predicate-stability/manifest_v3.md).

## Evidence Separation

- **Fact:** official task code exposes explicit predicate constituents and ManiSkill
  supports state-dict replay.
- **Agent inference:** these affordances are sufficient for a cheap relabeling pilot if a
  compatible frozen policy set exists.
- **Unknown:** checkpoint/runtime compatibility, matched initial states, exact recorded
  fields and end-to-end runtime in a new project-specific container.
- **Feasibility result:** source, license, evaluator schema and a bounded pairwise input are
  documented; execution has not started.

## Bounded Refinement Audit — 2026-09-08

### Question and inspection boundary

Can the v3 diagnosis justify another population or formulation for **policy-ranking sensitivity
under semantically equivalent success specifications**, without choosing thresholds, seeds or
policies for an observed reversal? This is the post-v3 TODO, not another evaluation protocol.

Read-only inspection covered the pinned ManiSkill task/evaluator source, the complete public
dataset tree at revision `d674485bbffdd533914e52d272fdda34c0515608`, and ten JSON metadata files
for the previously reserved StackCube/PlugCharger tasks, precision insertion and PushT.
The tree still matches the revision displayed by the public repository on the inspection date.
No new policy, HDF5, image or simulator was downloaded or run. The lookup is bounded to these
routes and the adjacent primary works below; it is not proof that no other public route exists.

[Inspection receipt](q1-artifacts.json) owns exact paths, hashes, checkpoint inventory, source
commit and metadata counts. Raw downloaded JSON receipts are in `runs/q1_refinement_audit/`;
the immutable URLs and SHA-256 values in the receipt allow recovery. Host work was limited to
source reading, metadata download/inspection and file verification. Frozen v3 artifacts remain unchanged.

### Facts: available artifacts and denominator limits

The [public dataset](https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/tree/d674485bbffdd533914e52d272fdda34c0515608/demos)
tree has 198 entries and no pagination continuation; it lists 26 checkpoint files across eleven
task directories. StackCube and PushT each have three PPO checkpoints. Thus a fresh small
inference study is technically plausible; lack of checkpoints is **not** the rejection reason.
The tree lists no checkpoint file under PlugCharger or PegInsertionSide. This absence is specific
to the inspected tree, not a claim about the Internet or files inside uninspected archives.

| Metadata route | Observed records | Limitation for a new policy-ranking study |
| --- | --- | --- |
| StackCube RL, three control modes | 902 / 995 / 932 episodes, every `success` true | Success-conditioned released population; complete evaluated denominator and failed state trajectories not established |
| PushT RL, three control modes | 888 / 719 / 999 episodes, every `success` true | Same limitation; raw near-boundary prevalence is unknown |
| StackCube / PlugCharger motion planning | 1,000 episodes each, every `success` true | Not a matched pair of complete policy evaluations |
| PegInsertionSide motion planning | 1,000 episodes, every `success` true; horizon 100 | Different collection route and horizon from the RL metadata |
| PegInsertionSide RL | 975 true / 25 false; horizon 50 | Failures exist, but source type/description are absent and comparison with the planner is not controlled |

All ten metadata files omit separate `success_once` / `success_at_end` fields. An omitted field
does not mean a false label. The six RL file sizes/counts are not policy success-rate estimates:
the original attempted denominator, sampling and export lineage must be verified first.
Not all public demonstrations are success-only, as the PegInsertionSide exception shows.

### Facts: task semantics

Sources are the [pinned task directory](https://github.com/haosulab/ManiSkill/tree/a4a4f9272ad64b1564035874b605ceb687b63ed8/mani_skill/envs/tasks/tabletop)
and the [official evaluation guide](https://maniskill.readthedocs.io/en/latest/user_guide/learning_from_demos/setup.html).

- PickCube explicitly conjoins distance and robot-static conditions. Dropping static because
  failure 3 approaches 30 mm changes the declared completion criterion. No measured v3 issue
  requires that repair; the source and independent labels agreed.
- StackCube requires placement, object stability and release. Its source comments on simulated
  angular-velocity instability. This is a source warning, not an observed Q1 label error or
  evidence for an acceptable interval of alternative geometric/static thresholds.
- PlugCharger uses 5 mm position and 0.2 rad angular tolerances. PegInsertionSide uses the peg
  head's location relative to the hole. Arbitrarily widening these changes admitted physical
  placements; it is not a calibrated uncertainty about one fixed success specification.
- PushCube, PullCube and RollBall offer geometric goal tests without the PickCube robot-static
  conjunction; PokeCube retains that conjunction. Changing task can remove the observed
  masking condition, but also changes dynamics, objectives and policy populations.
- The official guide defines once and end as different temporal events and already exposes both.
  It also warns about backend differences on precise tasks. Temporal completion, simulation
  fidelity and specification equivalence must therefore remain separate questions.

### Agent assessment of the alternatives

| Possible refinement | What supports trying it | Why it is not selected as the next Q1 study |
| --- | --- | --- |
| More PickCube seeds or the third checkpoint | Cheap public inference | No unresolved v3 measurement issue; supplies more draws without explaining the absent predicate-sensitive population |
| Relax/remove robot static | V3 identifies static as the blocker in one near-goal failure | Outcome-driven change to task success; no independent semantic justification |
| StackCube/PushT or geometric-only tasks | Existing checkpoints and different evaluator constituents | Fresh unfiltered rollouts are feasible, but the inspected evidence provides no independently justified equivalence interval; a task sweep alone does not resolve that construct |
| Reuse precise-task demonstrations | Compact states may support conditional margin analysis | Success-conditioned or unmatched populations cannot directly establish policy ordering on a shared evaluation distribution |
| Replace ranking sensitivity with persistence, safety or continuous progress | Meaningful diagnostics and established metrics exist | Different estimands; current negative evidence does not establish a new unexplained phenomenon beyond those simple reports |
| Numerical reliability of static/contact predicates | StackCube source warning and replay documentation | A potentially separate measurement-validity question; requires its own invariant/ground truth and source audit, not a rescue claim for semantic equivalence |

The original v3 deliberately called ±5 mm a local sensitivity probe, not a universally equivalent
task family. That caveat is correct. This audit did not find an external specification uncertainty,
task-grounded annotation rule or other independent basis that upgrades such a sweep into the
original semantic-equivalence question. A preregistered arbitrary interval would prevent some
selection bias, but would not supply that missing interpretation.

Three simple alternatives remain sufficient descriptions of the evidence: official constituent
labels, continuous geometric margins, and the already documented once/end pair. A new metric
module is not needed to explain the negative v3 cases. This is a scoping decision, not a demand
for a finished method or multi-domain paper before a pilot can begin.

### Adjacent primary work and decision

[SafeVLA-Bench](https://safevla.org/) preserves native success and adds safety specifications.
[Beyond Binary Success](https://arxiv.org/html/2603.13616v1) develops sequential policy comparison
for partial-credit and continuous metrics. These support the importance of richer evaluation;
they do not supply a semantically equivalent predicate family for Q1. The narrower prior-work
boundary is recorded in [the focused audit](q1-success-predicate.md#refinement-pressure--2026-09-08).

**Agent decision: discontinue the current Q1 formulation and active route.** Measurement is
available, but v3 did not show the suspected phenomenon and this bounded review did not establish
a defensible refinement. This does not prove global ranking stability, rule out future predicate
sensitivity or imply that StackCube/PushT experiments are impossible. No new protocol is frozen.

Future re-entry would need a task-grounded specification uncertainty or a separate observed
measurement failure, an unfiltered comparable population, and a question distinguishable from
simply reporting native success, margins and persistence. Such a proposal must return to candidate
comparison. Q8 is not automatically selected; the existing Robotics scope remains active.
See [Stage 7 disposition](../../selection.md#q1--discontinue-2026-09-08).
