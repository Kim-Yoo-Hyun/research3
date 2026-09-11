# Contact-Preserving Action Compression

Updated: 2026-09-10 · ID: Q11

## Status

`discontinued` for the current contact-sensitive method formulation/physical route (2026-09-10).
[Stage 7 closure](../../selection.md#q11--discontinue-current-route-2026-09-10) implements the
frozen bounded-stop rule. The broader contact-error question is unresolved, not disproved.
The user selected this question for buildup on 2026-09-08; it is no longer an execution priority.
Stage 4 preliminary review and Stage 5 risk assessment completed.
[Stage 6 measurement readiness](../pilot_studies/q11-action-compression/README.md) completed:
`READY_FOR_CONTROLLED_PILOT`. Controlled physical pilot v2 subsequently completed and passed
independent audit: `INCOMPLETE_CODEC_SUPPORT`. See [verified results](../pilot_studies/q11-action-compression/README.md#v2-verified-results).
[Stage 7 decision](../../selection.md#q11--refine-2026-09-08): one bounded protocol revision.
[V3](../pilot_studies/q11-action-compression/README.md#v3-verified-results) subsequently completed
and passed independent audit, with `STOP_NO_CONTACT_LOCALIZATION_SIGNAL`. Nonzero directional
differences did not meet the predeclared criterion. No further physical run or hypothesis selection.
[Comparative assessment](../related_work/policy-geometry.md#stage-3-comparison).

## Facts

[FAST official code](https://huggingface.co/physical-intelligence/fast) provides action encode/decode.
The inspected implementation quantizes scaled DCT coefficients. It also clamps coefficients
below `min_token` before character encoding and returns a zero coefficient array on decode
exceptions. These paths must be distinguished from quantization. DCT is invertible and BPE
is lossless when the coefficient character string round-trips correctly. No natural coefficient-clamp/BPE/decode failure
was observed in the verified pilot. Joint-normalized reconstructed actions did produce physical
task failures; distinguish these from codec implementation failure. Readiness v1 verified original replay and natural codec
round-trips; synthetic empty-token decoding exercised the documented zero fallback. Source receipts: [audit inputs](q11-sources.json).

## Source Claims

[FAST](https://arxiv.org/html/2501.09747v1) reports efficient high-frequency action tokenization.
[SA-VLA](https://arxiv.org/html/2606.30113v1) conditions decoding on state and compares learned
policies with FAST. The newer [OAT full paper](https://arxiv.org/html/2607.21670v1)
extends the original ordered-prefix work to block generation and token co-training.
The comparisons below are paper claims and source-access observations, not reproductions.

## Agent Inference

Average action MSE may underweight short grasp/release or contact-transition errors. The useful
residue would be an execution-relevant distortion criterion, not another generic tokenizer.
This is a suspected mechanism, not a demonstrated flaw in FAST or those papers.
The broad statement that reconstruction quality alone does not guarantee policy success is
already explicit in OAT. Q11 can only investigate the narrower contact-transition mechanism,
after implementation defects, action scaling, gripper handling and matched-error controls.

## Research Question Or Suspected Phenomenon

같은 compression budget과 비슷한 평균 복원 오차에서, 접촉 전환 주변의 action 오차가
free-motion 오차보다 실행 성공을 더 크게 바꾸는가? 단순 gripper 보존으로도 설명되지 않는가?

## Significance

VLA action interface의 효율을 실제 제어에 필요한 정보 보존과 연결할 수 있다. 검증 뒤에는
event-sensitive codec/loss라는 method 방향이 가능하지만 지금 architecture를 선택하지 않는다.

## Current State Of The Art And Limitation

### Stage 4 nearest primary work

| Primary source / inspected scope | Exact question and claimed contribution | Boundary and minimum Q11 difference | Artifact access on 2026-09-08 |
| --- | --- | --- | --- |
| [OAT full paper](https://arxiv.org/html/2607.21670v1), §§3--6, Algorithm 1 and policy-interface definitions; original [RSS version](https://arxiv.org/html/2602.04215v2) | Compact, totally decodable, ordered tokens as a policy interface; prefix reconstruction, block generation and token co-training | Already separates reconstruction from policy utility. Q11 must identify *where* valid codec errors change contact execution under fixed actions/controller. Merely plotting MSE against success is insufficient. | [Original code](https://github.com/Chaoqi-LIU/oat) archived; maintained [Praxis](https://github.com/Chaoqi-LIU/praxis-vla) has codec/training/evaluation interface. Exact compatible tokenizer checkpoint not verified. |
| [SA-VLA](https://arxiv.org/html/2606.30113v1), §§3--4 and appendix | Conditions VQ decoding on robot state through cross-attention or an action-wise scaling adapter; reports manipulation gains | State matters to decoded actions is already occupied. Q11 first fixes source actions, state and controller and localizes compression error; this is an untested minimum difference, not novelty proof. | No matching official executable bundle established by this bounded search. `SSSSphinx/SA-VLA` / arXiv:2602.00743 is a different spatial RL paper; do not substitute it. |
| [MoEActok](https://openaccess.thecvf.com/content/CVPR2026/html/Xu_MoEActok_A_MoE-based_Action_Tokenizer_for_Vision-Language-Action_Models_CVPR_2026_paper.html), CVF abstract and official README | Clusters action chunks into skills, uses expert quantization and skill-conditioned VLA training | A skill/contact-labelled expert tokenizer alone is not a difference. Q11 needs within-episode physical event evidence that survives simpler channel controls. Full PDF access failed; exact event-level evaluation remains unverified. | [Official code](https://github.com/cpaaax/MoEActok) raw README marks Simpler-Env inference released, tokenizer/VLA training data and training code pending; BridgeV2 weight link exists, payload not verified. |

### Supporting controls and overlap

- [FAST paper](https://arxiv.org/html/2501.09747v1), §V and official processor: reference
  analytical codec. Training-set 1st/99th quantiles and approximately one-second chunks are
  recommended. Normalization is external to this processor.
- [FASTer](https://arxiv.org/html/2512.04952v2), §3.1: separates physical action groups,
  including the gripper, and combines time-domain L1 and DCT-domain reconstruction losses.
  Thus physical grouping, multi-frequency loss or gripper-aware handling alone is occupied.
  HTML source checked; OpenReview PDF was blocked by a browser challenge.
- [Gripper-aware VLA / GVLA](https://arxiv.org/html/2608.24603v1), §§1 and 4: gripper
  morphology embeddings and adapter routing across embodiments. This is adjacent but is
  not itself a codec study of grasp/release command timing. A similar title is not a direct collision.
- Strongest adjacent learned-tokenizer comparison: OAT at matched local data, action horizon,
  decoder capacity and measured rate; FASTer/MoEActok add physical-group/skill pressure before
  a paper claim. They are not required installations for the first measurement check.

**Assessment:** high overlap; no exact-prior-free claim. The review supports a small diagnostic
study, not a new architecture. MoEActok full-text comparison remains a bounded literature
uncertainty; it does not prevent checking whether an action/contact measurement is valid.

## Evaluation Target

- Primary pilot: original versus reconstructed actions의 paired task outcomes/contact sequence.
- Diagnostics: action units별 reconstruction error, gripper transition timing, contact impulse
  또는 접촉 발생 시점; invalid decoder outputs도 denominator에 남긴다.
- Cost: encoded bytes/tokens, decoding latency, horizon/frequency. 서로 다른 vocabulary의
  token count만으로 공정한 bitrate를 주장하지 않는다.

## Available Data / Code / Evaluator

### Source-level execution route

- FAST HF revision `ec4d7aa71691cac0b8bed6942be45684db2110f4`: processor config
  `scale=10`, `min_token=-354`, `vocab_size=2048`; explicit horizon/dimension on decode.
  Immutable URLs and inspected SHA-256 values are in [audit inputs](q11-sources.json).
- ManiSkill source `a4a4f9272ad64b1564035874b605ceb687b63ed8`, already fetched by this
  workspace under `external/q8/`, inspected as text only. This is public source, not permission
  to run old images or use old Q8 outputs as Q11 evidence.
- First task: `StackCube-v1`, `panda`, `pd_joint_pos`. Official motion-planning solution has
  reach, grasp, lift, stack and release; cubes are procedural assets. Panda/assets, MPLib,
  SAPIEN and graphics dependencies subsequently passed readiness and v2 execution in new Q11 Docker images.
- Action is seven absolute arm joint targets in radians plus a normalized mimic-gripper
  command, not eight homogeneous values in `[-1,1]`. Planner uses `+1` open / `-1` closed;
  gripper target limits are `[-0.01, 0.04]` m. Log actual runtime action space and controller config.
- Source default physics/control frequencies are 100/20 Hz; explicitly configure and verify
  them. A one-second codec chunk is therefore 20 control steps, not 50. A task default
  `max_episode_steps=50` is distinct from the length of a motion-planning solution.
- Official StackCube success is cubeA-on-cubeB AND cubeA-static AND NOT cubeA-grasped.
  Record these components unchanged. `Panda.is_grasping` uses two finger force/angle checks
  (defaults 0.5 N and 85 degrees); open/close commands are not physical contact labels.
- `get_pairwise_contact_forces` returns impulse divided by the physics timestep. A call after
  `env.step` does not give an integral or all peaks over its five physics substeps. First study
  claims only sampled contact/grasp timing, with resolution stated; impulse/peak-force claims
  require separate substep instrumentation.
- Keep planner failures and unsuccessful attempts. The official generator can optionally
  drop unsuccessful trajectories; do not use `--only-count-success` or retry until a success quota.
  Record reset-time state and every action during generation. Use fresh scene initialization
  and full action replay; previous Q8 middle-demo restoration is not a valid shortcut.

**Updated access verdict:** the source route passed [readiness v1](../pilot_studies/q11-action-compression/README.md);
generated actions, checked original replay and sampled contact records are available. No policy
checkpoint was necessary for this diagnostic. `PegInsertionSide-v1` is a later independent
contact task only if the first route is informative; it is not an automatic fallback after a null.

## Simplest Baseline Or Counterexample

1. Original float actions and lossless round-trip: recorder/controller competence control.
2. Uniform scalar quantization with matched rate and correct normalization.
3. FAST with gripper channel preserved separately, charging those bits to the same budget.
4. Per-channel scaling and piecewise-linear compression; a strong learned tokenizer from the
   nearest-prior audit is required before any paper-level comparison.

For fixed planner `±1` commands, exact gripper bypass can use one bit/control step plus a
declared format header; do not threshold a general continuous gripper dataset into binary.
Record actual serialized bytes (including side channels/indices/headers), token lengths and
latency separately. Token count is not interchangeable with bitrate across vocabularies.
Match rate on calibration inputs before outcome evaluation; if codecs have no overlapping
rate/distortion region, report that comparison unavailable rather than select convenient cases.

## Critical Assumptions

### Stage 5 assumption and decision branches

Times below are engineering estimates, not measured runtime; each includes a cheaper check.

| Assumption / necessity | Current evidence and cheapest check | Disconfirmation / supported / ambiguous branch | Estimated cost |
| --- | --- | --- | --- |
| A. Original replay and contact labels are valid; otherwise no causal attribution | Planner, controller and evaluator source exist. Check full reset-to-end replay and sampled events before compression. | Contradicted: stop codec attribution and repair measurement. Supported: B. Ambiguous: compare fresh scene state/action logs and sampling resolution, without more tasks. | New Docker setup 0.5--2 working days; first ≤8-seed check capped at 2 h after build. |
| B. Errors come from supported codec operation, not interface bugs | Quantization, coefficient clamp and zero fallback are separate source paths. Compare normalization-only, analytical quantization and official character/BPE round-trip. | Contradicted: classify normalization/range/decode defect, not contact sensitivity. Supported: C. Ambiguous: inspect one failing chunk in Docker, preserving input and intermediate arrays. | CPU codec/schema check hours; no policy training. |
| C. Local error position matters beyond error size, channel, velocity and episode difficulty | Suspected only. On later frozen episodes, use source-event windows, matched noncontact windows and arm-error localization at equal energy; retain common rate support for codec comparisons. | Contradicted: discard event-specific explanation. Supported: D. Ambiguous: no matched windows/common error support means unidentifiable; narrow target explicitly. | Later bounded paired replays, planned ≤1 working day after protocol freeze. |
| D. Gripper bypass, normalization and simple interpolation do not fully explain the effect | FASTer already exploits physical action grouping. First compare three simple controls before a learned component. | Contradicted: practical interface lesson; discontinue new-method route. Supported: second-task and learned-tokenizer comparison. Ambiguous: fixed-rate comparison lacks power/support; record uncertainty, not positive effect. | Small codec/replay grid; no large VLA fit. |
| E. Replay finding can matter to a learned policy | No Q11 evidence. Offline codec fidelity and autoregressive predictability are different (OAT). | Contradicted in later small-policy test: bound finding to replay. Supported: hypothesis work may follow with explicit learning effect. Ambiguous: assess small-policy cost before committing. | Later estimate only, small-policy study 1--2 weeks; not part of next TODO. |

## Feasibility Or Pilot Study

### Next Stage 6: measurement readiness

Selected first uncertainty: can the source route produce a valid, reproducible action/contact
record? The following was the Stage 4--5 implementation draft. The runnable config, tolerances,
freeze and execution receipts now belong to the [study README](../pilot_studies/q11-action-compression/README.md).

1. Inputs: pinned source above; `StackCube-v1`, Panda, absolute-joint controller, fixed seed
   attempts `0..7`, one environment, explicit 100/20 Hz, physics CPU backend in Docker.
   Graphics may require explicit `--gpus`; CPU physics does not imply GPU-free setup.
   Seed attempts are measurement/calibration inputs, never a later held-out outcome set.
2. Generate at most one planner attempt per seed; keep exception/timeout/failure status and all
   available actions. Cap each attempt at 400 control steps (20 s simulated); truncated records
   remain incomplete. Explicitly configure the wrapper horizon to the same cap and log it.
   Stop on planner completion or cap, not first success. Do not add settling steps retrospectively.
3. For each completed record, replay the unchanged action sequence twice from a fresh scene
   with the same initialization. Save robot/object poses and velocities at reset and each step,
   commands, sampled finger forces, grasp flags and official success components. Preserve exact
   actions/dtype; lossless serialization must recover identical action bytes.
4. Gate A: compare initial physical states within predeclared numerical tolerances, then complete
   sampled grasp/success sequences across the generation and both replays. A disagreement is
   measurement failure and blocks physical codec attribution on that record. Never delete it.
   To proceed beyond readiness, require at least one successful replay-valid record with grasp
   and release plus a noncontact interval. This is an existence gate, not statistical support.
5. Codec-only diagnostics on recorded chunks: normalization/denormalization identity, DCT/IDCT
   identity, analytical scale-10 quantization versus official processor, lower-clamp counts,
   pre/post-BPE coefficient equality, decoder validity and tail-chunk length. No simulator codec
   variants or contact-sensitive method are executed in this first gate.
   Report joint-limit affine normalization and calibration-only quantile normalization separately;
   define constant-channel handling, tail padding/masking and no-clipping default before run.
6. Outputs: per-attempt receipt, actions/state/contact arrays, replay comparison, codec diagnostics,
   environment/dependency manifest and checksums. At most 8 generation attempts + 16 replays;
   workload cap 2 h after environment build. Final recipes, mount paths and command belong in
   the new Q11 study README when implemented, with logs under `logs/` and background launch.
7. Decisions: `READY_FOR_CONTROLLED_PILOT` if A and codec-path accounting are valid;
   `REPLAY_OR_SCHEMA_INVALID` if measurement disagrees; `NO_USABLE_EVENT_RECORD` if the
   fixed attempts cannot supply the required events; `RUNTIME_UNAVAILABLE` if setup fails.
   Readiness does not select a hypothesis or establish the Q11 phenomenon.

### Conditional physical pilot after readiness

Freeze disjoint calibration/held-out episodes, normalization statistics, rate grid, matched-error
rules and contact windows before codec-outcome runs. Compare original, uniform quantization,
FAST, exact gripper bypass, scaling and interpolation controls. Use paired final task outcomes;
ever-success is a secondary diagnostic and evaluation length is identical within an episode.
Use the original physical trajectory to define event windows before intervention, not the
perturbed success/failure outcome. Distinguish command transitions, grasp transitions and
object-object contact. A later equal-energy arm-error localization comparison is a mechanism
diagnostic, not a deployable codec or a fair bitrate comparison by itself. Control speed/error
distribution or report their confounding. One task and eight readiness seeds cannot establish
generality, statistical null effects, or VLA learning gains.

## Preliminary Success Criteria

An execution-relevant contact error survives the simple controls and is reproducible on held-out
episodes. A later small policy-learning comparison must separate codec fidelity from learnability.

## Expected Deliverable

First: verified measurement/codec-path table and continue/repair/stop decision. If valid,
subsequent controlled pilot: rate/distortion/outcome table and case-level taxonomy for Stage 7.

## Timeline And Milestones

Stage 4--5 and Stage 6 measurement readiness completed 2026-09-08. Controlled physical pilot
v2 completed and passed independent audit; Stage 7 selected `refine`. Bounded v3 completed and
passed independent audit on 2026-09-10. The fixed stop criterion ended the current method route;
no further seed/amplitude/grid/task expansion or hypothesis admission is queued. All v1/v2 seeds are excluded from future independent
held-out claims; no large VLA training.

## Interpretation Of A Negative Result

If gripper handling/scaling explains everything, record a practical interface lesson and stop the
new-method route. Do not increase compression until failures appear or claim VLA learning gains.

## Resource Requirements

Codec inspection/round-trip can run in a small CPU Docker image; simulator validation may need
GPU. Small policy training is a later option. All runtime stays in new project-owned Docker.

## Related-Work Overlap

High; the contact-localized question was not established by the bounded v2/v3 studies.
Current formulation is discontinued under the precommitted rule. Quantile normalization is
already part of the FAST baseline.
MoEActok full text and stronger learned baseline become necessary before any novelty claim.
Q6 concerns asynchronous timing; Q11 fixes timing and changes action encoding.

## User Decision Needed

The bounded Q11 route is closed. Next is comparative reserve reassessment under the existing
Robotics scope; Q12 is a priority to reassess, not an automatically selected hypothesis. Heavy training or real-robot use is outside
this readiness plan; simulator setup failures are recorded rather than bypassed on the host.
