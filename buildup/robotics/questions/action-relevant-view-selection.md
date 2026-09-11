# Action-Relevant View Selection

Updated: 2026-09-10 · ID: Q13

## Status

`deferred` after the [Q12/Q13 comparison](../../selection.md#q12q13-measurement-selection-2026-09-10).
Stage 4–5 assessment completed on 2026-09-10. Broad action-aware view selection and learned
action-uncertainty framing have direct prior overlap. The conditional decision-value diagnosis
is preserved for re-entry if a concrete case or improved artifact access reduces its preparation
cost. No execution or formal hypothesis selected; the question is not empirically disproved.
[Source evidence and assessment](../related_work/policy-geometry.md#q13-stage-4-review-2026-09-10).

## Facts

[ActiveVLA's repository](https://github.com/ZhenyangLiu/ActiveVLA-Injecting-Active-Perception-into-VLA)
currently marks code, models and evaluation scripts as pending release. A paper benchmark is
not yet a verified executable artifact in this workspace.
Official DISaM, active_grasp and GCNGrasp-VP source interfaces were traced. DISaM links pretrained
weights, but only generic Box page access is verified. GCNGrasp-VP has public weight metadata
while explicitly withholding its NBV evaluation dataset. active_grasp needs independent target
outcome verification. All runtime and dataset/checkpoint payloads remain unverified here.

## Source Claims

[DISaM](https://arxiv.org/html/2410.18964v1) uses manipulation-action discrepancy to train information
seeking and action uncertainty to switch sensing/acting. GCNGrasp-VP uses task affordance for view
selection. ActiveVLA selects virtual rendered views; SaPaVe predicts camera and manipulation actions.
The linked Stage 4 record owns the detailed comparison and its primary sources.

## Agent Inference

A view that reduces visual uncertainty may leave the preferred action unchanged, while a less
visually informative view may resolve which grasp or approach is safe. This is a value-of-information
question; a generic active-perception module would not be novel. DISaM directly occupies the
earlier proposed distinction of learned-policy decision uncertainty. Any remaining study must
diagnose a measurable mismatch between an existing score and downstream decision value;
renaming value-of-information or switching from entropy to action disagreement is insufficient.

## Research Question Or Suspected Phenomenon

같은 관측 비용과 action evaluator에서, 기존 task-aware view score와 learned action
uncertainty는 추가 관측 후 decision regret 감소를 언제 설명하지 못하는가?

The previous visibility-versus-action question is retained as motivation only. A mismatch is
suspected, not observed, and would not by itself establish a new method or novelty.

## Significance

새로 볼 필요가 없는 경우를 포함해 sensing과 control을 연결한다. Efficient sensing을 위한
decision-sensitive acquisition이 가능한지 확인한다.

## Current State Of The Art And Limitation

POMDP, active grasping and value-of-information are direct priors. In particular,
[action-guided dexterous grasping](https://arxiv.org/abs/1708.04185) already selects observations
around intended contacts and approach safety. ActiveVLA/SaPaVe cover active perception in VLAs.
DISaM also uses a learned policy's decision uncertainty; GCNGrasp-VP is a recent task-affordance
selector. A residue must survive these applicable controls as well as a fixed extra view. Physical
sensor acquisition and virtual reprojection must be separated. No empirical residue is established.

## Evaluation Target

Success versus total observation/motion/inference cost; expected decision regret under the same
finite action evaluator. Action switching and uncertainty reduction are diagnostic only: switching
between equally successful actions is not a benefit. An oracle view bound must obey the same
initial information partition; it cannot secretly select a different view for indistinguishable states.

## Available Data / Code / Evaluator

A controlled simulator camera/occlusion study is plausible. SaPaVe describes ActiveManip-Bench
but its checked official project page did not expose a downloadable execution bundle.
active_grasp offers a ROS Noetic/MoveIt/VGN simulation route, with source-level prescreening and
success-proxy limitations. DISaM's `walled` route offers an existing skill policy and camera commands;
matching weights and a valid state/observation adapter are prerequisites. GCNGrasp-VP's offline
recorded-view evaluation is a selector reference, not verified physical task success. A small
diagnostic is not a reproduction of the named VLA or a new benchmark claim.

## Simplest Baseline Or Counterexample

No additional view; fixed extra view; random feasible view; maximum visible target area; entropy
reduction; an existing planned-contact/task-affordance selector; DISaM's applicable action-uncertainty
and sensing policy; oracle action-value information.
Charge camera movement, elapsed time and model calls consistently for every method. Action samples
from a stochastic policy can differ without epistemic uncertainty; control policy sampling variation.

## Critical Assumptions

Necessity, current evidence, disconfirmation, cost and supported/contradicted/ambiguous branches
are owned by the [Stage 5 assessment](#stage-5-assessment-2026-09-10). The first operational risk
is matching public checkpoint access; the first scientific risk is a valid observation-dependent
action comparison beyond the existing method's score.

## Feasibility Or Pilot Study

The objective/source comparison is complete. A conditional [bounded readiness task](#bounded-measurement-task-draft)
would check a matched DISaM checkpoint and a small observation/action interface before a decision-value
pilot. This task is deferred by the comparison; Q12 proceeds to preparation first. No scene set, checkpoint payload or executable protocol is
frozen, and no model, simulator or baseline has run for Q13.

## Preliminary Success Criteria

A valid, informative diagnosis separates action-distribution variation from changes in expected
task utility. A new-method direction would additionally require useful effects beyond fixed-view
and existing task-aware/uncertainty controls, with sensing cost accounted for.

## Expected Deliverable

Source/metric readiness receipt first; if justified, view-score versus decision-value cases and a
continuation/refinement/stop decision. No method training is needed merely to finish the first receipt.

## Timeline And Milestones

Stage 4–5 review complete. Conditional next task: metadata/pairing half a day, then at most 2–4
working days for a fresh Docker and matched-snapshot check if files are accessible. These are
planning estimates. Physical utility evaluation and any training require a separately fixed budget.

## Interpretation Of A Negative Result

Prefer the fixed view if it explains all gains. Do not add memory or more cameras to sustain the claim.

## Resource Requirements

Simulator-first, small policy or planner; no humanoid hardware assumption or VLA pretraining.

## Related-Work Overlap

High. Q9 refreshes memory; Q13 asks whether acquiring a new observation changes the decision.

## User Decision Needed

None for this review; no hardware motion or new runtime selected.

## Stage 5 assessment 2026-09-10

**Assessment at Stage 4–5 completion:** narrow the initial framing and retain `under_review` for comparison.
The later comparative decision, linked in Status, defers this candidate's next measurement.
Direct-prior overlap is established, but neither the suspected failure nor its absence has been
measured. This is not a Stage 7 termination or hypothesis admission decision.

| Assumption / necessity | Current evidence and disconfirmation | Cheapest check; estimated cost | Decision branches |
| --- | --- | --- | --- |
| A useful question remains after existing task-aware and action-uncertainty methods. **Scientific.** | The broad distinction is already covered. A particular disagreement-to-regret mismatch remains unmeasured; fixed/affordance/DISaM controls explaining all benefit undermines a new-method route. | Source/prior comparison completed. Define an explicit score and independent decision-value target before fitting; about half a day. | Supported → test the named mismatch. Contradicted → stop or reformulate the method route. Ambiguous → narrow diagnosis, not another generic module. |
| An additional observation can distinguish action-relevant hidden alternatives. **Scientific.** | Source environments support different contexts and camera views; a matched ambiguous observation set is not verified. Identical action utility across contexts or initial observations already revealing the answer disconfirms the intended comparison. | Two small context pairs with fixed initial sensor state; compare all allowed initial fields, then candidate observations. At most four initial states in the draft, after setup. | Supported → view-value measurement. Contradicted → record trivial/uninformative cases; no outcome-guided scene search. Ambiguous → validate visibility/input schema before policy inference. |
| Existing score variation reflects missing information, not policy randomness. **Scientific.** | DISaM samples inferred contexts and action distributions; active_grasp accumulates correlated view history. Neither is an independent task label. Same-input resampling explaining all variation defeats the interpretation. | Fixed observations and common RNG draws; separately repeat a stationary sensor reading. Small fixed inference batch, proposed at most two GPU-hours. | Supported → compare score with independently estimated utility. Contradicted → diagnose stochastic or numerical behavior, not sensing value. Ambiguous → repeat only the declared noise control. |
| Actions have valid independent utilities and comparable starts. **Scientific.** | active_grasp's gripper-width proxy is insufficient; DISaM has task distance/contact predicates but counterfactual branch restore is untested. Changed camera/arm/task state or different denominators can produce apparent utility differences. | Audit full simulator/task/camera/RNG state and selected target predicates. One fixed action/controller set; preserve failures. About one working day after basic loading. | Supported → paired action outcomes. Contradicted → repair the evaluator/state adapter or defer the route. Ambiguous → input/interface-only receipt; no regret result. |
| View comparisons respect available information and cost. **Scientific and operational.** | Virtual reprojection, recorded-view snapping and physical sensor movement are different routes. Constant candidate costs and update counts do not verify equal motion/time. Hidden scene labels or unacquired frames selecting a view would invalidate a deployed comparison. | Declare sensor budget, camera motion semantics, acquired frames and model calls; match candidate sets before outcomes. About half a day of protocol design. | Supported → compare sensing choices. Contradicted → qualify as virtual/offline diagnostic or narrow the claim. Ambiguous → report separate costs, withhold equal-cost superiority. |
| A pretrained source fits resources without retraining. **Operational.** | DISaM has source and generic checkpoint-link access; exact encoder/PPO pairing is unknown. GCNGrasp-VP weight metadata is public but its NBV evaluation set is withheld. active_grasp has legacy dependencies and unchecked asset payloads. | Identify one matched DISaM bundle and dependencies, then a new Docker load/snapshot check; half-day metadata and at most 2–4 working days total setup target. | Supported → bounded readiness. Contradicted → defer that route; no full training as an automatic fallback. Ambiguous → resolve metadata/size first, not a full blind download. |

Estimates overlap and are not an additive schedule. Q13's direct-prior pressure and state/action/cost
validation needs informed its deferral relative to Q12's first input check. Neither candidate's
experimental accessibility is certified by source access; improved access can change the allocation.

## Bounded measurement task draft

**Purpose:** establish whether an existing learned action-uncertainty method can be inspected with
matched observations and independent outcome labels. This is a conditional readiness draft using
DISaM `walled` as the first source candidate. The draft is preserved while Q13 is deferred;
it is not a new selector or an active Stage 6 study.

1. **Checkpoint and dependency pairing.** Identify one released camera-policy/encoder pair and
   its embedded or associated receiving policy. Inspect names, sizes, use terms and checkpoint
   linkage before transfer. Freeze the robosuite revision, custom SB3 revision and remaining
   dependencies in a new workspace Docker recipe. If selective access or matching files cannot
   be verified, stop at an access receipt; do not retrain either policy or start another full stack.
2. **A small explicit observation set.** Limit the draft to the first manipulation stage, two
   predeclared initial-layout groups with two possible hidden contexts each: at most four states.
   Verify within-pair ambiguity against every permitted initial observation field, while group
   differences may be observable. Declare a finite set of at most three camera commands plus
   no new observation. IDs, scene construction, RNG seeds and tolerances must be frozen before
   running. Retain non-ambiguous/uninformative cases as findings rather than searching until a
   desired failure appears. This constructed set cannot estimate natural failure prevalence.
3. **State and input audit.** Store simulator state, task variables, camera transform, counters,
   RNG and policy state, and check round-trip restoration. Camera-only branches must expose their
   changes in physical/time state. Keep hidden context and unacquired images in evaluator storage;
   record the allowed observation keys at policy boundaries. A dataset replay or direct camera-pose
   edit is only a simulated sensor diagnostic until feasible path and elapsed-time accounting exist.
4. **Fixed inference checks.** Use the released uncertainty computation and a matched finite
   downstream action set. Compare identical-input stochastic repeats, fresh readings at the same
   camera pose and actual new-view readings. Cap model work at two GPU-hours after setup as a
   planning target. Preserve the original method and name any adaptation explicitly; no thresholds
   selected against task outcomes, no retraining and no full camera-policy benchmark in this task.
5. **Independent value interface.** Specify how existing block/region/contact outcomes will label
   actions from matched starts. First verify schema and restoration, then freeze a separate bounded
   action-outcome pilot if needed. Argmax changes, lower KL, AP or gripper opening alone cannot
   supply those labels. Any source skill using privileged geometry must be shared across methods
   and described as a skill-policy assumption, not claimed as learned visual motor control.

The receipt must include source/input hashes, Docker identity/commands/device, checkpoint linkage,
all included and excluded states, observation provenance, restoration errors and cost accounting.
Valid loading/input/state/outcome interface → design a small score-versus-value pilot. Invalid
pairing or restore → repair once within the task budget or defer. A working score without valid
task utility → sensitivity evidence only. No new method or hypothesis follows automatically.

For a later pilot, the comparison is **expected decision value**, not a hindsight switch label.
Let `b(s | o0)` be the declared belief over initially indistinguishable alternatives, `U(a,s)` the
common independent utility, and `a_v(o0,y)` the fixed decision rule after acquiring observation `y`
at view `v`. Evaluate `E[U(a_v(o0,y),s) | o0,v]` under that same belief and observation model, and
compare with the no-view rule under the same action space. The best-view bound maximizes this
expectation over admissible views using only `o0`; maximizing separately with access to the true
hidden state is a stronger clairvoyant bound, not deployable selection. A global best fixed view
must be chosen before held-out outcomes; report if it explains the entire apparent adaptive benefit.
Do not optimize the downstream rule separately for each view after seeing the outcome table.

No model payload, fresh Docker build, simulator episode or hypothesis was created in this review.
