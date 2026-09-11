# Reliance on Generated Geometry

Updated: 2026-09-11 · ID: Q12

## Status

`feasibility_study`; [CPU input/schema/coordinate protocol v1](../pilot_studies/q12-generated-geometry/README.md)
was executed on four real pairs and independently verified. All input controls passed, yielding
`INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`. Checkpoint strict loading and independent metadata
verification pass. The frozen [CPU reference completion protocol](../pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11)
has now run on the four inputs in two processes; output provenance and repeatability passed independent
verification. Native CUDA parity and physical linkage remain unverified. Next is a cost/information
assessment of those remaining routes before action-linked validation. No hypothesis is selected.
[Comparison](../../selection.md#q12q13-measurement-selection-2026-09-10) and
[Stage 4 evidence](../related_work/policy-geometry.md#q12-stage-4-review-2026-09-10) remain historical provenance.

## Facts

[G3Flow](https://github.com/TianxingChen/G3Flow) publishes a generation/tracking/policy pipeline.
[DP3](https://github.com/YanjieZe/3D-Diffusion-Policy) provides a point-cloud policy and simulator
training route. End-to-end runtime and exact compatible weights remain unverified here.
G3Flow's separate observed/feature-cloud branches lead to joint/gripper actions. In the inspected
`bottle_adjust_T` route, the physical actor and virtual feature geometry refer to the same GLB asset.
3DSGrasp's public dataset/model payloads and four basename-matched partial/GT pairs are now
checksum-verified. The real-input audit confirmed expected finite array shapes and coordinate
controls; GT contains repeated rows. Model state compatibility and real-input CPU reference output
provenance/repeatability are verified, while native runtime parity and metric frames remain unverified. The
study owns current results; Stage 4 source assessment is historical.

## Source Claims

[G3Flow](https://tianxingchen.github.io/G3Flow/) uses generated digital twins and semantic flow
for manipulation. [Measuring Uncertainty in Shape Completion](https://arxiv.org/html/2504.16183v1)
uses completion uncertainty to improve grasp ranking. [SpringGrasp](https://tml.stanford.edu/SpringGrasp/)
plans compliant grasps under shape uncertainty.

## Agent Inference

Completion can supply missing context but also impose systematic geometric bias. Sample variance
need not expose bias shared by generated samples. Even a policy with separate input branches may
rely on a biased generated representation. This is a suspected phenomenon, not an observed G3Flow
failure. The earlier premise that G3Flow treats observed and inferred points identically is withdrawn:
its paper already describes separate encoding and consistency checks; see the current assessment.

## Research Question Or Suspected Phenomenon

관측과 생성 정보를 구분하는 policy에서도, 관측에 맞지만 가려진 부분이 틀린 geometry가
언제 행동을 잘못 유도하는가? Pose 보정과 단순 consistency/uncertainty control로 생성 정보의
이득과 손해를 설명할 수 있는가, 아니면 action에 따른 의존 차이가 남는가?

## Significance

3D generative priors의 visual plausibility와 실제 manipulation value를 분리한다. Residual이
있으면 observation consistency와 action-sensitive conditioning의 학습 원리를 탐색할 수 있다.

## Current State Of The Art And Limitation

Shape uncertainty, grasp reranking, learned grasp/place success prediction and compliant planning
are established. “Generated shapes are uncertain” and learning a success predictor are not new.
Candidate residue is learned-policy dependence on biased completion
after controlling observation consistency, pose error and ordinary uncertainty-aware planning.
G3Flow also uses semantic features and initial exploration. A geometry-specific claim must
separate these from shape error; otherwise narrow the target to the generated representation.

## Evaluation Target

Task success, collision/contact location and action deviation under a fixed observation/policy
budget. Chamfer distance is diagnostic, not the primary robotics outcome. Split objects and
occlusion patterns before outcomes; preserve accurate-completion benefit as well as failure cost.

## Available Data / Code / Evaluator

The G3Flow-embedded DP3 shares its task/action interface; standalone DP3 is an architecture
reference, not a compatible checkpoint. The audited G3Flow source traces observations through
14-dimensional joint/gripper action to a source-defined task outcome, but uses a shared physical
and virtual asset. This route needs independent completion before it can test Q12.
3DSGrasp offers an alternative pretrained completion and partial/GT dataset schema. The study
now preserves downloaded weights and four raw pairs, with source-defined name correspondence.
Both selected objects occur in archive train/test; no object-disjoint claim is possible. Camera rays,
metric units, robot evaluator linkage, explicit weight/data terms and model-stack compatibility remain unresolved. Its online restoration
also differs from the inverse normalization; this must be isolated as a wrapper effect.

## Simplest Baseline Or Counterexample

1. Observed-only point-cloud policy, with equal point/feature budgets.
2. Full completion with the same policy capacity and training budget.
3. Hard observation/free-space consistency projection before encoding.
4. Uncertainty-weighted or conservative geometry and a nearest uncertainty-aware grasp baseline.
Oracle full geometry and oracle pose separate perception errors from policy/controller errors.
Share all initial exploration views with the observed-only baseline; compare multi-view observed
fusion before attributing gains to generated hidden surfaces. Separate input encoders are a baseline,
not a proposed contribution. Keep semantic features matched or explicitly qualify their confounding.

## Critical Assumptions

The [Stage 5 assessment](#stage-5-assessment-2026-09-10) owns the historical assumptions and
branches. The [verified input audit](../pilot_studies/q12-generated-geometry/README.md#verified-input-results-2026-09-10)
now supports name/schema/numerical controls. Independent generated output and a valid physical
frame remain unresolved before any learned-policy comparison.

## Feasibility Or Pilot Study

The [frozen input protocol](../pilot_studies/q12-generated-geometry/README.md) was executed and
independently verified on all four real pairs without changing source, thresholds or denominator.
Inputs were already numerically centered/unit-radius; wrapper restoration is separated from any
model effect. Next prepare strict checkpoint/model loading and independent-output provenance
with explicit GT sampling and physical/camera limitations. No inference or policy pilot has run.

## Preliminary Success Criteria

Completion-specific harm and benefit are separable from pose error, input distribution shift and
the simple controls. If so, a small learned-policy study can test an evidence-conditioned method.

## Expected Deliverable

Geometry-source/action/outcome matrix, failure cases and explicit continuation/stop decision.

## Timeline And Milestones

Source/assumption assessment and the first CPU input audit are complete. The earlier 1–2 working-day
readiness estimate was a plan, not measured model runtime. The next model-loading validation
requires an explicit setup/inference cap before execution. A learned-policy budget is not fixed.

## Interpretation Of A Negative Result

If observation consistency or pose correction suffices, stop the new-method route. If synthetic
perturbations create effects absent in actual completion outputs, do not claim a generative-policy flaw.

## Resource Requirements

Small 3D policy/asset set preferred; no new 3D foundation-model training. G3Flow's native extension
and foundation-model dependencies are material setup risks. All execution remains Docker-only.

## Related-Work Overlap

High: completion uncertainty, SpringGrasp, FFHFlow and learned 3D policies. Q4 concerns task-state
selection, Q9 memory freshness; Q12 changes the provenance/consistency of geometric policy input.

## User Decision Needed

None for documenting the completed input audit or preparing its next bounded validation.
The study owns acquisition/execution evidence; model inference and a physical/policy pilot remain
separate, not-yet-frozen tasks.

## Stage 5 assessment 2026-09-10

**Assessment, not an experiment result:** retain the question as `under_review`; do not use the
unchanged shared-asset G3Flow route to test completion bias. Source consumption is established,
but actual reliance, a useful effect and a fair learned comparison are unmeasured. The nearest
prior comparison and pinned source citations are owned by the linked Stage 4 record above.

| Critical assumption / necessity | Current evidence and disconfirmation | Cheapest check; estimated cost/duration | Decision branches |
| --- | --- | --- | --- |
| Independent completion and physical truth exist. **Scientific:** otherwise shape error is not identifiable. | **Contradicted for the unchanged G3Flow route:** shared asset lookup. **Ambiguous for 3DSGrasp:** intended partial/GT pairs, unverified payload. Duplicate GT supplied as completion, invalid pairing or unavailable input would defeat that route. | Source/index audit completed; next inspect a few explicit pairs and pretrained-output provenance. Metadata/schema first, about half a day if selectively accessible. | Supported → frame/visibility integrity. Contradicted → replace or defer that substrate, not infer absence of the phenomenon. Ambiguous → obtain pair metadata before inference. |
| Metric frame and observed/generated provenance are valid. **Scientific and operational:** wrapper errors cannot count as learned shape bias. | 3DSGrasp dataset/online restoration differ by a 7/6 radial factor; model output includes copied input points. Actual units/GT alignment are unknown. Failed inverse round trip or a mismatch explained solely by restoration disconfirms the attribution. | Check exact inverse, copied-point indices and explicit partial/GT frame in Docker; a few inputs, less than half a day after setup. Rays are separately required for free-space claims. | Supported → geometry intervention. Contradicted → correct/qualify the adapter and reconsider the attributed effect. Ambiguous → frame-only diagnostic; withhold hidden/free-space labels. |
| Input geometry can vary while pose, semantics and physics stay fixed. **Scientific:** isolate the proposed cause. | G3Flow mesh affects rendered features and tracking, while repeated `get_obs` advances physics. A pose/feature/time change explaining the effect is a counterexample. | Draft an XYZ-only route with one observation snapshot and independently known pose/physical mesh. Source-level design about half a day; physical execution budget comes later. | Supported → paired action/outcome test. Contradicted → narrow to representation or pose error; do not keep a geometry-only claim. Ambiguous → oracle-pose diagnostic, explicitly evaluation-only. |
| Observed-only and completion comparisons have comparable training and sensor support. **Scientific:** avoid attributing OOD or extra views to useful completion. | Same-task DP3 interface exists; matched demos, weights, training cost and view budgets are not verified. Dropping a branch from fixed completion-trained weights is only sensitivity/OOD evidence. | Check demo/weight manifests, permitted initial views and compute accounting before training; about half a day for metadata if available. | Supported → freeze matched comparison. Contradicted → matched small training or narrower sensitivity question. Ambiguous → no policy ranking claim; keep geometry readiness separate. |
| A useful action effect remains after simpler controls. **Scientific:** potential insight beyond established uncertainty-aware grasping. | No effect observed. Registration, consistency projection, conservative grasping and learned grasp/place success prediction are existing explanations/baselines. Full recovery by these controls undermines a new-method route. | First validate real completion outputs; later compare fixed action candidates with matched information. A grasp diagnostic is cheaper than policy training but is not closed-loop evidence; reserve at most 1–2 days for designing it after readiness. | Supported → test the specific residual with a small policy study. Contradicted → retain diagnosis and stop/reformulate new-method direction. Ambiguous → distinguish input/evaluator noise before adding components. |
| A small independent-completion route fits available resources. **Operational:** avoid a foundation-scale setup dependency. | Linked Drive pages accessible; payload size, content/license and pretrained load unverified. 3DSGrasp uses an old CUDA/PyTorch stack with native extensions, and the 2025 uncertainty extension is not released there. | Selective-access/license check, then a new workspace Docker and one weight-load/inference check; 1–2 working days total target. No host workaround or heavy training. | Supported → finish bounded readiness. Contradicted → defer this implementation; assess a lighter route before proceeding. Ambiguous → metadata/build-only check with an explicit cap, not full downloads by default. |

Costs are planning estimates and overlapping work, not an additive schedule or measured performance.
The Stage 3 priority is historical. The subsequent comparison, linked in Status, selected this
readiness task's preparation; it did not establish empirical feasibility or publication novelty.

## Bounded measurement task draft

This is the historical broader readiness draft. The subsequent
[study preparation](../pilot_studies/q12-generated-geometry/README.md#why-input-controls-precede-inference)
split out a frozen CPU input audit as the first measurement; native model inference remains later.

**Purpose:** determine whether an independent pretrained completion can be paired with partial
observations and full geometry in a valid coordinate frame. This is a proposed measurement-readiness
task selected for preparation, not a frozen Stage 6 protocol or an executed result.

1. **Access and pairing first.** Inspect 3DSGrasp's linked data/weight metadata, provenance and
   use terms. Seek at most two objects with two explicit partial/GT pairs each: four inputs total,
   chosen by a declared file-order rule before looking at completion outcomes. Record split and
   training provenance; do not call a test folder an object-disjoint split. Confirm payload size and
   selective retrieval before transfer. If the archive cannot be inspected selectively, record the
   actual size and cost for a new decision rather than starting an unbounded full download.
2. **Fresh Docker, one pretrained model.** Prepare a workspace-owned recipe with pinned source,
   dependencies, read-only inputs and separate outputs. Limit this task to model loading and fixed
   inference; no fitting, GPD/ROS integration, policy training or physical rollout. Target at most
   two GPU-hours after setup; this is a proposed cap requiring protocol freeze, not a runtime claim.
   If setup cannot fit the 1–2-day target, document the concrete blocker and reassess the route.
3. **Explicit transformation controls.** Freeze file IDs, sampling seed and preprocessing. Store
   input centroid/radius, exact inverse-normalized output and the original online wrapper's
   restoration as separate controls. Preserve generated versus copied-input indices. Check the
   normalization round trip and copied-point consistency before interpreting reconstruction error;
   do not tune scale against GT to rescue a result. Retain the upstream source and qualify any adapter.
4. **Limited measurements.** Verify finite arrays, pair identity, frame/units and non-copied generated
   output. Record distances to paired GT as diagnostics only after alignment is established. Label
   visible/hidden/free-space regions only if camera/ray provenance supports them; XYZ alone is
   insufficient. No stochastic-uncertainty claim from the available zero-dropout model and no
   claim that this reproduces the unreleased 2025 uncertainty extension.
5. **Reviewable deliverable and branches.** A compact receipt contains source/input/output hashes,
   Docker identity/commands, device, file selection, coordinate transforms, provenance checks and
   excluded/missing inputs. Valid independent pairs and restoration → design an action-linked
   controlled test with fixed physical geometry. Pair/frame failure → repair or defer this substrate.
   Valid points but no camera/physical linkage → completion diagnostic only, with the missing
   robotics interface as the next risk. No outcome implies useful learned-policy reliance by itself.

Before execution, freeze actual IDs, data-transfer cap, commands and acceptance tolerances in the
selected study's owner. No study root, download job, Docker build or model inference was started
during this Stage 4–5 assessment.
