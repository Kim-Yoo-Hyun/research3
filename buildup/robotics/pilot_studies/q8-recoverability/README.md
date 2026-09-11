# Q8 Recoverability Audit

Updated: 2026-09-08

## Status and scope

`completed`: 사용자 요청에 따른 Stage 6 후보 선정을 위한 bounded feasibility audit.
판정은 Q8 `refine`, tested PPO grid `uninformative`; 다음 Stage 6 후보는 Q1이다.
비교 결정은 [selection](../../../selection.md#q8q1--stage-6-selection-2026-09-08)이 소유한다.
Public source/checkpoint만 사용한다. Q1 v3 protocol은 변경하지 않는다.
새 Docker, 4 CPU / 8 GiB memory, PhysX/Torch CPU, no frame rendering/training을 사용했다.
초기 CPU-only 계획은 SAPIEN scene 생성의 graphics 의존성 때문에 아래 기록대로 수정했다.
2026-09-08 resource snapshot: RTX 5090 7,176/32,607 MiB, utilization 22%; disk 128 GiB free.

## Pre-outcome checks

1. Pinned ManiSkill source와 public checkpoint의 provenance/API/controller state를 감사한다.
2. PickCube의 task identity/goal/robot을 보존하는 pre-contact horizontal cube translation을
   검사한다. Physical perturbation에서 expert action equality는 요구하지 않는다.
3. Fixed-horizon official success와 trajectory-return의 차이, score/target split과
   equal-rollout-budget success-rate baseline을 먼저 정의한다.
4. Docker에서 nominal execution, state-only restore 및 reset+action-prefix replay를 비교한다.
   반복으로 simulator hidden/contact/controller state 누락을 검사한다.
5. 실행 가능한 route에서 outcome 전에 고정한 small perturbation grid를 반복한다.
   Repeated deterministic runs는 independent statistical samples로 세지 않는다.
6. Q1의 measurement readiness와 Q8의 scientific uncertainty를 비교한다. Fixture는
   demonstration coverage나 held-out predictive gain의 증명이 아니다.

## Artifact and command ownership

Working directory: `/home/yoohyun/research3`.
Source: `external/q8/`, read-only audit/build context only.
Runtime inputs/outputs: `datasets/q8/`, `runs/q8/`; source and checkpoint mounts read-only.
Logs: timestamped `logs/*q8*`. Exact commands, checksums and results are accumulated below.

## Source retrieval

`launched`: pinned ManiSkill archive, no host imports/install/runtime.

```bash
tmux new-session -d -s research3_q8_source 'cd /home/yoohyun/research3 && curl -fL --retry 3 -o external/q8/maniskill.tar.gz https://codeload.github.com/haosulab/ManiSkill/tar.gz/a4a4f9272ad64b1564035874b605ceb687b63ed8 > logs/20260908_q8_source.log 2>&1 && tar -xzf external/q8/maniskill.tar.gz -C external/q8 && sha256sum external/q8/maniskill.tar.gz > external/q8/source.sha256'
```

Expected: `external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8/` and
`external/q8/source.sha256`. Verify checksum and pinned `pyproject.toml`/task source.

## Runtime preparation

Source retrieval completed; archive SHA-256
`61c402b86337782e30815d205485b34aba458a3103cdcbe55c293cf0ec6f5293`.
`download.sh` completed; both PPO checkpoints match frozen official hashes. Motionplanning
HDF5 matches official SHA-256 `03ca60546541a7f18321d9d32721f0254bc75217828c0cadacd217d0c014576a`.
Input hash manifest: `runs/q8/inputs.sha256`; official tree: `external/q8/checkpoints.json`.
Motionplanning demos were recorded at source `652ad9353c0223507a938f0e8d990dd6f1c771ad`,
`pd_joint_pos`; they are not automatically on-policy data or training data for the PPO artifacts.

Build command: `sh buildup/robotics/pilot_studies/q8-recoverability/build.sh` in background tmux.
First build completed (`logs/20260908_140000_q8_build.log`, exit 0), but smoke failed at
`sapien.render.RenderMaterial`: `failed to find a rendering device` despite `render_backend=none`.
This is an environment failure, no scientific outcome. Docker recipe adds software Vulkan
(`mesa-vulkan-drivers`) and rebuilds from the pinned official base with `--pull --no-cache`.
No host dependency installation or GPU fallback is used.

Runtime command: `sh buildup/robotics/pilot_studies/q8-recoverability/run.sh <script.py>`.
Mounts: study read-only `/work`, `datasets/q8` read-only `/inputs`, `runs/q8` writable `/outputs`.
Device: PhysX CPU / Torch CPU; network disabled; 4 CPU / 8 GiB, no `--gpus`.
`smoke.py` executes only the unchanged `layer_init`/`Agent` AST from pinned official PPO source.
Checkpoint hashes are asserted before `weights_only=True` load. Actual dependency and OS locks
are captured inside the image (`/opt/dependencies.lock`, `/opt/os-packages.lock`).

CPU-only runtime refinement, before outcomes: software Vulkan still fails with rendering `none`;
explicit rendering `cpu` fails with `Failed to find a supported physical device "cpu"`.
Logs: `20260908_105100_q8_smoke.log` and `20260908_105300_q8_smoke_cpu.log`, both exit 1.
The runtime now exposes NVIDIA device 0 with explicit `--gpus device=0` and graphics/utility/compute
capabilities solely for SAPIEN material creation. Physics and inference remain CPU, no frames
rendered. This supersedes the earlier no-GPU runtime plan; the frozen scientific grid is unchanged.
The user authorized maximal inspection/repeated verification; no unrelated workload is stopped.

Further pre-outcome runtime diagnosis: explicit NVIDIA runtime and the pinned source's ICD
(`VK_ICD_FILENAMES=/opt/ManiSkill/docker/nvidia_icd.json`) expose the device but Vulkan reports
`ErrorIncompatibleDriver`. `LD_DEBUG=libs` isolates repeated unsuccessful `libEGL.so.1` lookup;
third fresh build adds `libegl1`. No host driver/configuration change is made.
Diagnostics: `logs/20260908_110600_q8_vulkan_debug.log` and targeted library-loader log
`logs/20260908_110800_q8_loader.log`. Runtime uses `render_backend=gpu` to create the scene,
but never calls render; physics/inference stay CPU. This is not CPU-only end-to-end execution.

Before outcomes, grid-anchor restore controls are also applied to seeds 103--108 (in addition
to the two source-interface seeds in the manifest), because each grid seed needs its own zero
control. `audit.py` includes 450 restore comparisons per process and 312 proposed interventions.
`manifest_v1.md` remains immutable; its SHA-256 is in `runs/q8/protocol.sha256`.

## Pinned source findings

- `BaseEnv.get_state_dict()` includes nonempty controller state; `set_state_dict()` delegates
  to actor/articulation state and does not call `agent.set_controller_state()` or restore the
  episode clock. The selected delta controllers default to `use_target=False` and expose empty
  state, so this source asymmetry alone does not prove their next-action failure.
- Contact-derived `is_grasped` is part of the 42-dimensional PPO observation. Pose/qpos equality
  alone therefore cannot certify observation equality after state injection.
- Panda `is_static(0.2)` uses the maximum absolute velocity over seven arm joints, inclusive
  `<=0.2`, not an L2 velocity norm. Independent verifier reconstructs this exact constituent.
- Cube translation within official initializer support retains task identity and goal;
  expert action equality is unnecessary. The conservative no-robot-overlap predicate uses actual
  collision-mesh AABBs, while solvability after nonzero-time intervention remains unproven.
- Public motionplanning dataset has 1,000 trajectories, older source commit and absolute joint
  position control. Full schema and installed-source equality receipts are `runs/q8/provenance.json`.

## Execution record

Third fresh build plus smoke: `completed`, `logs/20260908_111000_q8_build3.log` and
`logs/20260908_111000_q8_smoke3.log`, combined exit file
`logs/20260908_111000_q8_build_smoke.exit`. PPO-Joint seed 101 completes 50 steps and reaches
official success. No source patch to physics, policy or evaluator was needed.
Image `research3-q8-audit:v1` resolves to
`sha256:ba862a119ec3b363a2b39b8d4e9e6e4cabd3ab66c32fdeda22fec997bb0c0861`.

```bash
sh buildup/robotics/pilot_studies/q8-recoverability/run.sh provenance.py
Q8_REPEAT=0 sh buildup/robotics/pilot_studies/q8-recoverability/run.sh audit.py
Q8_REPEAT=1 sh buildup/robotics/pilot_studies/q8-recoverability/run.sh audit.py
Q8_REPEAT=2 sh buildup/robotics/pilot_studies/q8-recoverability/run.sh audit.py
sh buildup/robotics/pilot_studies/q8-recoverability/run.sh verify.py
```

Each command runs in a new container; repetitions are sequential. Provenance/audit 0 launch:
tmux `research3_q8_audit0`, logs `20260908_110230_q8_provenance.log` and
`20260908_110230_q8_audit0.log`, matching exit file. Outputs are created exclusively and never
overwritten. Expected: `audit_0.json` through `audit_2.json`, `verification.json`, provenance and
dependency locks under `runs/q8/`. Implementation hashes are frozen before audit 0.

## V1 repeated results and reset refinement

V1 three processes completed and independent verifier passed. Each had 450 restore comparisons,
312 proposed interventions and 56 admitted rows (51 nonzero). 55/56 reached success_once and
success_at_end; repeated labels and stored continuous trajectories were identical. **These are
superseded history-sensitive fixture results, not clean robustness evidence.**

Direct and reset+state restore each passed only 24/150 comparisons per process; prefix passed
144/150. All one-step success booleans agreed despite large continuous/action errors: verifying
only the official success label would miss the measurement failure. Selected controller states
were empty; contact-dependent observation mismatch is the relevant observed risk here.

The seed-101 empty-prefix reset reproduces physical state exactly, but observation differs by
1.0. Thus v2 fixes scene reconstruction, not a scientific threshold. [Manifest v2](manifest_v2.md)
was frozen after v1 audit 0 and before v2 execution. No seed/radius/phase/validity predicate is
changed. The additional zero-intervention check compares full continuations, not only next steps.

V1 repetition launch tmux: `research3_q8_repeat`; logs
`logs/20260908_110440_q8_audit1.log`, `..._audit2.log`, `..._verify.log`; exit 0.
V2 launch tmux: `research3_q8_cold`; each process uses:

```bash
Q8_REPEAT=0 sh buildup/robotics/pilot_studies/q8-recoverability/run.sh cold_audit.py
Q8_REPEAT=1 sh buildup/robotics/pilot_studies/q8-recoverability/run.sh cold_audit.py
Q8_REPEAT=2 sh buildup/robotics/pilot_studies/q8-recoverability/run.sh cold_audit.py
sh buildup/robotics/pilot_studies/q8-recoverability/run.sh demo_audit.py
sh buildup/robotics/pilot_studies/q8-recoverability/run.sh verify_cold.py
```

Logs: `logs/20260908_110750_q8_cold0.log` through `..._cold2.log`, `..._demo.log`,
matching `..._cold.exit`. Expected: `runs/q8/cold_0.json` through `cold_2.json`,
`demo_audit.json`, `cold_verification.json`. Full grid eligibility is recomputed by unchanged
rules; repairing a stale `is_grasped` observation can change admission and the nominal anchor
trajectory, so equal seed/axis names do not certify identical physical anchors between v1/v2.

## Final verified results

V2 three processes, public demo transition audit and independent artifact verification completed.
`logs/20260908_110750_q8_cold.exit` is 0; verification logs are
`logs/20260908_111100_q8_verify_cold.log` and `logs/20260908_111430_q8_decision_audit.log` (exit 0).
Verification commands: `run.sh verify_cold.py`, then `run.sh decision_audit.py` using the full
relative entrypoint path above. Compact tracked receipts:
[v1 verification](verification_v1.json), [v2 verification](verification_v2.json),
[gate audit](decision_audit.json), [source/input/schema](provenance.json),
[dependencies](dependencies.lock), [OS packages](os-packages.lock), [checksums](checksums.txt).
`decision_audit.json`의 decision 문구는 agent selection record이며 학습된 ranking score가 아니다.

| Check | Verified result | Interpretation |
| --- | --- | --- |
| V1 restore | 450 comparisons × 3 processes; direct/reset-state 24/150 each, prefix 144/150 per process | physical state equality and one-step success agreement do not guarantee action/transition equality |
| V2 prefix restore | 150/150 × 3; all five maximum errors exactly 0 | fresh scene + saved action prefix supports the selected next-step fixture |
| V2 proposed / geometric+next-step admission | 312 / 144 per process; 131 nonzero | 168 excluded by unchanged validity rules; exclusions retained |
| V2 success | 144/144 success_once and success_at_end in every process | all-pass selected population; no discriminating recovery profile |
| Full zero-intervention continuation | 9/13 anchor groups meet 1e-5; labels all match; max distance/velocity trace difference 6.9723e-5 | 4 groups fail the original continuous tolerance, so they cannot support precise intervention attribution |
| Full-zero-qualified population | 98 rows including 89 nonzero, 9 anchor groups; 98/98 success in all 3 processes | even after original zero-control gate the profile is all-pass; no post-hoc tolerance relaxation |
| Between-process repeatability | zero label disagreements; zero difference in stored distance/velocity traces | computational repeatability only, not independent statistical samples |
| Public demo one-step replay | 9/27 pass; t=0 9/9, t=5/20 0/18; max mixed-state coordinate error 3.9620e-4 | middle-of-demonstration exact replay not established under the current source/controller recipe |

Counts in repeated processes do not increase unique-state evidence. V1+V2 include 1,800 restore
comparisons and 27 public demonstration comparisons, but only 8 PPO-Joint seed groups in the
perturbation population. Qualified t=0 states test initialization robustness; t=5 pre-contact
states do not cover grasped/contact-rich recovery. No t=10 proposal was admitted.

PPO-Joint nominal success is 8/8; PPO-EE is 1/2 on the two CPU fixture seeds. This is neither
Q1's 16-trajectory CUDA study nor a policy-superiority result. Both public checkpoint load paths
and exact installed task/controller source equality were verified.

V1's single failure does not persist after clean reset. That refinement changes nominal anchor
states as well as eligibility, so the audit establishes history sensitivity, not a causal proof
that every failure came from a stale bit. The full-zero discrepancy is retained separately; its
cause is not fully isolated. No larger radius, new seed search, trained model or post-hoc metric
change was attempted to obtain failures.

추가 field-isolation check (`run.sh reset_audit.py`,
`logs/20260908_112000_q8_reset_audit.log`, exit 0)는 fresh/warm/cold reset의 `is_grasped`가
false/true/false임을 확인했다. Warm physical-state error는 정확히 0이고 변경된 observation
index는 18 하나뿐이었다. Cold observation error는 0이다. Compact receipt는
[reset audit](reset_audit.json)다. 이는 reset observation 차이의 위치를 확인하며, 모든
downstream failure나 full-zero trace drift의 원인을 확정하는 결과는 아니다.

Runtime for each v2 process: 76.76 / 75.12 / 76.31 seconds. This supports cheap bounded
verification on this machine, not a full benchmark or a predicted speed for VLA/second-task
studies. All research containers exited. Other GPU workloads remained untouched.

## Scientific conclusion and remaining uncertainty

Facts support executable, repeatable pre-contact fixtures after reset repair, with the limits
above. They do **not** support demonstration-training coverage, a non-degenerate recovery
curve, residual over density/action/critic/outcome controls, cross-group prediction or novelty.
The finite-horizon scalar is identical to the equal-budget empirical-success baseline when
computed on the same perturbation law. The literature/construct audit is owned by
[Q8 related work](../../related_work/q8-local-recoverability-coverage.md#repeated-audit--2026-09-08).

Stage 7 inference: `refine` Q8; discontinue expansion of this uninformative PPO/pre-contact
grid without a new failure-derived question. Q8 could return with a training-data-linked policy,
validated demonstration restart and a distinct held-out perturbation target plus equal-cost
controls. This is a re-entry condition, not a claim that local recovery research is impossible.
