# Spatial-Memory Refresh

Updated: 2026-09-15 · ID: Q9

## Status

`deferred`; the current depth/surface refresh route is not selected for further investment after
the [research-value review](../related_work/policy-geometry.md#q9-research-value-2026-09-15).
The [selection record](../../selection.md#q9-investment-decision-2026-09-15) owns the decision.
The [observation study](../pilot_studies/q9-refresh/README.md#surface-comparison-2026-09-15)
preserves execution and evidence. This is an investment choice, not a refutation of spatial-memory
refresh or a claim that object correspondence is solved. The original question/design remains
below as context; it is not an active execution queue. No hypothesis or paper claim is selected.

## Facts

- DynaBench has a public sequence/annotation repository. Env1's 54,700,824-byte pickle passed
  SHA-256 verification and CPU deserialization: 42 RGB/depth/pose/intrinsics entries, no timestamps
  or combined semantic features. Other sequence pickles remain uninspected.
- Path-level environment/time identifiers must be retained. Query wording changes across
  snapshots, and blank coordinates alone do not identify removed versus never-observed objects.
- Two-case point and surface diagnostics ran in CPU Docker. They are not a complete Q9 memory system,
  DynaMem reproduction or embodied planning benchmark.

## Source Claims

- RSS 2026 [Multi-modal Interaction Field](https://www.roboticsproceedings.org/rss22/p023.html)
  detects map--reality discrepancy and locally updates obsolete memory for dynamic humanoid
  navigation.
- [DynaMem](https://arxiv.org/html/2411.04999v2), especially §3.2–4.3, already updates dynamic
  spatial memory, removes obsolete points and verifies query grounding. DynaBench evaluates
  time-indexed object localization without navigation, exploration or manipulation.
- [MIF's project](https://ziya-jiang.github.io/MIF-homepage/) marks code Coming Soon at this check.
  Its method remains a direct prior even without a verified reproduction route.
- [Memory for Attention](https://arxiv.org/html/2607.23797v1) directly studies budgeted
  re-perception, history/relevance, recency controls and observation reliability. The
  [focused review](../related_work/policy-geometry.md#q9-focused-review-2026-09-15) owns the comparison.

## Agent Inference

The first trace found schedule-dependent coverage of point evidence, but visual inspection
showed that approximate query coordinates cannot be treated as exact object surface landmarks.
The surface comparison now shows a simple geometric-eligibility schedule capturing the measured
interval evidence at the same two depth accesses per case. Bowl frame 17 becomes consistent;
orange has contradictions even within the initial index range, with the fruit still visible
near the projected samples. Movement versus registration/correspondence is unresolved. There
is no demonstrated object-level accuracy gain or need for a learned scheduler. Generic budgeted refresh,
dynamic memory, recency, relevance and point removal already have strong prior overlap.
Any later contribution must explain a diagnosed failure of simple update rules and matter to
robot state estimation or decisions; localization improvement alone does not establish that path.

## Research Question Or Suspected Phenomenon

Given the same causally available RGB-D stream and a capped number of memory updates, when do
uniform, time-to-live and geometric-change schedules differ in stale-object localization and
absent-object errors? Does query relevance explain a difference beyond these simple controls?

This narrows the initial plan-completion question to an observable offline precursor. If relevance
is evaluated, query information available at each decision must be explicit: future evaluation
queries/coordinates cannot guide a causal trigger. An oracle may diagnose room for improvement
but is not an implementable baseline.

## Significance

Obsolete spatial beliefs can send a robot toward an old object location or retain an absent
object. The study would determine whether update allocation at limited compute warrants further
robotics research, or whether simple periodic/change-based updates are sufficient.

## Current State Of The Art And Limitation

DynaMem/MIF address obsolete memory; Memory for Attention is also close to budgeted refresh and
relevance. A possible further question concerns observation opportunities in a sequential RGB-D
stream, but its distinction from these priors is unproven. The simple visibility control already
accounts for interval coverage in the selected cases. The subsequent review assesses remaining
correspondence/cost uncertainty and the value of a revised explanatory question.

The completed review additionally identifies VLMM's explicit static-background pose refinement
and correspondence/depth uncertainty, and Khronos's ray-based evidence reconciliation. These
constrain a generic correspondence-repair reformulation. Their published limitations remain;
neither is verified to solve the orange case. The review owns the exact sections and boundaries.

## Evaluation Target

Candidate observables are localization within the released tolerance for positive queries,
false presence/absence for negative queries, and memory update/perception/query costs. Define
positive and negative denominators separately before combining them. Three or four annotated
snapshots per environment do not identify continuous stale-belief duration without extra labels.
A first exploratory case can describe its selected observations without estimating population
effects. Broader evaluation must choose splits and uncertainty at the scene level; repeated queries
are not independent scenes. No metric, threshold, split or significance gate is frozen yet.

## Available Data / Code / Evaluator

The comparative review owns the full inventory and
[reassessment_sources.json](../related_work/reassessment_sources.json) owns pinned URLs/hashes.

- [DynaBench](https://huggingface.co/datasets/hello-peiqi/DynaMem-DynaBench): nine environments;
  annotation/time files verified. Env1 raw input has been inspected; official checkpoint
  indexing, annotation correspondence and full evaluation compatibility remain unresolved.
- DynaMem source at `6272b28e3ff7be482af3b427a4551d1772ebf7d7` exposes
  `process_rgbd_images`. Its saved-map loader applies `num_frames` only to one reconstruction
  loop and later restores combined semantic features. Source inspection therefore identifies a
  potential future-information path. Env1 has no combined semantic features, and the first
  diagnostic uses raw arrays instead of that loader. Pose-estimation provenance is unresolved.
- Current CPU documentation changes perception/matching settings; local feasibility and parity
  are unverified. The live CLI constructs a robot client, so it is not a ready offline runner.
- MemoryVLA and PARTNR remain adjacent routes. The previously inspected 33.5 GB MemoryVLA
  checkpoint is not required to establish whether this smaller DynaBench route is usable.

## Simplest Baseline Or Counterexample

Never refresh and all-frame refresh bound the tradeoff but are not equal-cost competitors.
Compare fixed-period/uniform allocation, TTL and geometric-change rules under the same budget;
add a simple recency/relevance rule if query information is legitimately available. Charge the
cost of reading/processing rejected frames to change-based triggers. The original DynaMem rule
is a necessary reference for later method claims. The first observation needs only the comparison
that makes it interpretable. Provisional trigger sketches may accompany that observation; a later
contribution still needs diagnosed simple-rule failures and the existing paper-level evidence.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| a causal per-frame stream can reconstruct memory | only full-sequence combined features survive, or poses/features use future frames | source and feature-provenance audit; then bounded input inspection in Docker |
| query times and labels map to that stream | ambiguous time units/frame inclusion or unverifiable absent-object labels | compare original annotation paths, paper protocol and frame metadata |
| updates can be externally controlled | map deletion, encoding and insertion cannot be separated consistently | trace the first case's update path; check equivalence where the comparison depends on native behavior |
| costs can be matched | triggers get free all-frame inference or privileged query labels | separate sensing access, perception, map writes and query cost |
| relevant versus irrelevant changes are identifiable | wording changes cannot be linked to stable objects or sparse labels miss events | state matching/annotation requirements before attributing failures |
| the first contrast has research value | periodic/TTL/change rules explain the proposed effect, or prior work already answers it | nearest-prior and counterexample review before a new module |

## Feasibility Or Pilot Study

2026-09-15 first observation completed: use `env1`'s earliest two annotation checkpoints
(`14`, `26`) to trace whether depth observations can contradict an old object location.
`metal bowl` is positive at 14 and a negative query at 26; `orange` has different coordinates.
These are exploratory cases chosen after reading annotations, not held-out tests. Initial
annotated coordinates were privileged approximate seeds, not verified object surface landmarks.
The first trace compares array indices 15–24; official checkpoint indexing remains unresolved.
Only one of five two-read periodic phases captured the bowl point's depth evidence; the orange
point had none. Visual inspection limits these to point evidence, not object absence or robot
task success. The execution and interpretation owner is
[q9-refresh](../pilot_studies/q9-refresh/README.md).

The follow-up used nine manually selected initial surface samples per case and the same margin.
At two depth accesses each, visibility selects bowl [17,22] and orange [19,24], matching each
case's best periodic phase. Extra scheduling pose checks are recorded; total compute is not
matched. Orange also contradicts its initial samples at frame 9, so the initial range cannot
serve as a verified unchanged-object control. Observed surface seeding helps one case but does
not establish object-event detection. The accounting correction preserved the exact trace and
all scientific decisions; this remains exploratory, not independent replication.

If a bounded CPU replay is plausible, bundle the necessary input inspection and minimum execution
preparation toward that observation. If access is costly, compare the value of a small constructed
case, explicitly distinct from DynaBench evidence. Any pickle handling or method execution needs
a new workspace-owned Docker recipe, restricted inputs, identifiable outputs and relevant checks.
Exploratory case/threshold choices and changes must disclose what data informed them. A later
confirmation needs evaluation data not used for those choices.

## Preliminary Success Criteria

Success for the next design means one interpretable comparison with a plausible causal input,
time/label mapping and explicit cost boundary, plus what we learn from each outcome. Full-scene
parity, the complete control suite and a positive effect are not entry conditions. Native/adapter
checks are required where the first inference depends on them. An effect gate belongs to a later
prospective protocol.

## Expected Deliverable

Completed: primary-prior review, initial point/surface observations, equal-depth-access simple
control comparison, visual interpretation and the research-value decision. The current route is
deferred. No additional surface/calibration audit or enlarged benchmark is scheduled.

## Timeline And Milestones

Stage 4–5 design, the same-case surface follow-up and investment reassessment completed on
2026-09-15. The next selected work is a Q7/Q14 comparison within the existing Robotics scope.
Neither that comparison nor Q9 deferral automatically reactivates another paused experiment.

## Interpretation Of A Negative Result

If all-frame refresh is inexpensive, or periodic/TTL/change rules suffice, do not add learned
memory machinery. If only the input/label contract fails, stop the affected inference and compare
repair with deferral, without claiming that update timing has no effect. Either result clarifies
whether the next investment belongs in representation, update allocation, data access, or another
research question.

## Resource Requirements

The first observation used one public 52.2 MiB input and CPU PyTorch/NumPy in a new image;
semantic encoding may later require a GPU. No foundation-model training, live robot or
full dataset/model download is part of the selected work. Fixed-view replay cannot measure
savings in robot exploration or changes in action-conditioned observations.

## Related-Work Overlap

`high`; DynaMem/MIF and Memory for Attention constrain refresh/allocation; VLMM and Khronos
also constrain generic uncertainty/correspondence repair. Open questions and comparison limits
are recorded in the [review](../related_work/policy-geometry.md#q9-research-value-2026-09-15).

## Investment decision and re-entry

The useful observed schedule difference is explained by simple current-view eligibility.
Object-level interpretation remains unresolved, and the separate per-case budgets do not test
competition among objects or total compute. Extending this trace would mostly quantify an
already explained effect or apply known geometric repairs, without a specific further explanation
to distinguish. That limits the current investment value; it is not a demand for final novelty,
statistical significance, full benchmark coverage or a finished method at buildup entry.

A possible revised question is whether causal view availability changes multi-object budget
allocation beyond visible-only oldest-first or a masked Whittle index. This is an unselected
draft, not an effect demonstrated by the pilot. Reconsider it, or another concrete robot-decision
question, when a small observation/analytic construction gives distinguishable predictions from
the relevant simple alternative. Positive results and a complete prior reproduction are not
required to reopen exploratory comparison. Calibration cleanup alone does not automatically
restore Q9 to the active queue.

## User Decision Needed

None for this disposition or the next bounded candidate comparison within the existing scope.
