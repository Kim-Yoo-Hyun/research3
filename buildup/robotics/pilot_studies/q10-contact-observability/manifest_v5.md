# Q10 Deterministic Baselines v5

Created: 2026-09-07

## Question And Boundary

On the fixed v4 population, can action-conditioned terminal-state and force threshold rules
predict segment outcomes well enough to make a more complex evaluator unnecessary?
This is a Stage 6 competence check, not an RGB comparison, minimum-signal proof, online detector,
causal intervention, or paper-level experiment. “Strongest” means the train-selected best member
of the explicitly bounded rule library below, not every possible deterministic rule.

## Frozen Population

- Inherit `selection_v4.json` and `artifacts_v4/segments.tsv` without editing or resampling.
- Only `target_action=True` and action in pick/insert/remove: 413 rows, 363 success/50 failure.
- Official train: 309 rows, 269 success/40 failure, 15 recordings.
- Official test: 104 rows, 94 success/10 failure, 5 recordings. Place's one test failure is excluded.
- Preserve segment boundaries and official sensor-issue exclusion. Do not drop rows for missing
  features. Any required signal with no finite in-window samples aborts with `INVALID_FEATURES`.
- Known v3 visual inspection and v4 outcome counts mean this is not a wholly unseen test set.
  No v5 signal/outcome analysis may inform thresholds, model selection or these criteria.

## Fixed Inputs And Features

Official schema: [REASSEMBLE README at pinned commit](https://github.com/TUWIEN-ASL/REASSEMBLE/blob/432cc15ce3e028edc2f98a786f28bf6baf31ac6f/README.md).
Pose is `(x,y,z,qw,qx,qy,qz)` and gripper positions are left/right finger positions.
Source/data provenance and download checksums inherit v1/v2/v4. Local implementation has no Git
metadata; source SHA-256, dependency lock, protocol and image digest are captured before execution.

All signal samples are inside the supplied high-level segment, including its endpoint. No future
segment, low-level labels, outcome text, success flag, recording ID or segment index is a feature.
Recording ID is grouping metadata; family is routing metadata; exact action text is used only by
the explicitly labeled prior control. Ground-truth segment duration/boundaries are available to
all rules, so this is retrospective evaluation and may reflect human stopping conventions.

- **State (14 features):** final XYZ; final-minus-initial XYZ; XYZ displacement norm; quaternion
  rotation angle `2 acos(abs(dot(q_start,q_end)))` after normalization; left/right terminal
  gripper positions and changes; terminal sum of finger positions and change in that sum.
  Initial/final means first/last available sample inside the segment; no interpolation or smoothing.
- **Force (18 features):** three magnitude traces: measured force norm; norm of measured force
  minus its first in-segment vector; compensated-base-force norm. Each yields peak, trapezoidal
  magnitude integral over available timestamps, and trapezoidal duration above each cutoff
  `{2,5,10,20}` in the dataset force units. With one sample, integral/duration are zero.
  These durations are threshold-occupancy proxies, not verified physical contact durations.
- **Duration control (1 feature):** annotated segment end minus start.
- Verify timestamp monotonicity, matching lengths, required dimensions, nonzero quaternion norm
  and finite values. Duplicated timestamps are allowed; decreasing timestamps are not.
- RGB payloads, embeddings and torque/joint channels are not used in this bounded v5 library.

## Fixed Rule Library And Fitting

1. Family success prior: `(success+1)/(n+2)` within each train action family; hard label at 0.5.
2. Exact-action-text prior: same Laplace estimate per train text; unseen text backs off to family.
3. Duration-only, state-only, force-only and combined (state+force+duration) threshold rules,
   each at maximum depth 1 or 2. Depth 2 provides simple conjunctions of threshold conditions.

Rules are axis-aligned binary trees, independently fit for each family. At each node choose the
midpoint between distinct training values maximizing class-balanced Gini reduction. Root training
weights sum to 0.5 for each outcome class and remain fixed down the tree. Each leaf must contain
at least five training rows. Stop at maximum depth, a pure node, or nonpositive gain. Ties choose
lexicographic feature name then smaller threshold. A one-class training fold returns a constant.
Hard decisions use weighted leaf majority (tie success); success probabilities use unweighted
Laplace-smoothed leaf counts. A balanced-accuracy decision need not equal `p(success)>=0.5`;
report calibration of the separate probability estimate transparently. No post-hoc calibration.

Train tuning uses leave-one-recording-out cross-validation over the 15 official train recordings.
For each family and candidate, pool its held-out predictions before computing balanced accuracy
and Brier score. Select the family rule by highest pooled balanced accuracy, then lower Brier,
then lower maximum depth, fewer features and candidate name. Include both prior controls among
candidates. If a training fold has no rows of a family, abort; do not consult test data.
Refit each candidate on all train rows. Save CV scores, selected family rule, all fitted rules,
and a SHA-256-sealed training artifact before loading test signal features. Evaluate all fixed
candidates descriptively, but only the CV-selected combination determines the decision.
No test ranking is used to pick a “best” method.

## Metrics And Practical Margin

Positive class is success. Primary metric is the unweighted mean of pick/insert/remove balanced
accuracy, each `(success recall + failure recall)/2`. Report per-family counts, confusion matrices,
success/failure recall and macro Brier score (equal action weight), log loss and five-bin equal-width
ECE. Brier is the primary probability score; ECE is descriptive with only 104 test rows.

Operational practical sufficiency requires **all** of:

- selected test macro balanced accuracy >= 0.85;
- macro balanced accuracy gain over family prior >= 0.10 (10 percentage points);
- every action balanced accuracy >= 0.75 and every action failure recall >= 0.75;
- macro Brier <= family prior macro Brier + 0.02.

These are agent-chosen pilot tolerances, fixed before results, not established benchmark standards.
They demand substantial error reduction and prevent the majority-success prior from passing.
With only two remove failures, that family's recall condition requires both to be detected.
Passing is practical pilot adequacy, not saturation or a statistically proven equivalence.

Uncertainty: paired recording-cluster bootstrap of the five test recordings, 2,000 draws with
seed 20260907, sampling five recordings with replacement. Report 2.5/97.5 percentiles of selected
macro BA and gain over the family prior. Draws missing either class in any action are invalid;
report valid/invalid counts and do not replace invalid draws. Fewer than 1,000 valid draws means
`UNCERTAIN_RESIDUAL` unless practical criteria already pass. Never treat individual segments as
independent trials for confidence intervals. Five clusters still give weak uncertainty estimates.

## Decision And Disconfirmation

- `SIMPLE_RULE_SUFFICIENT`: all practical criteria pass. Proceed only to Stage 7 assessment of
  measurement depth; no learned evaluator justified by v5.
- `RESIDUAL_REQUIRES_PROBE`: criteria fail, at least 1,000 bootstrap draws valid, and the lower
  percentile of macro BA gain is > 0. A separate frozen supervised regularized-probe study may
  ask whether remaining errors are separable using the same summaries.
- `UNCERTAIN_RESIDUAL`: criteria fail and the gain lower bound is <= 0 or uncertainty is invalid.
  First diagnose recording/action errors, calibration and stopping-duration confounding. A
  separate cheap probe can test summary separability; this is not evidence for a new architecture.
- `INVALID_FEATURES`: schema, provenance, split or feature checks fail. Repair and record the
  deviation before evaluating; never silently shrink the denominator or change thresholds.

Report false-success and false-failure counts by action and recording, overlaps between fixed
state/force/combined rule errors, and duration-only performance. These are error strata, not
physical-cause labels. They cannot establish visual ambiguity, outcome construct validity,
object/session-disjoint transfer, physical information beyond RGB, or method necessity.
Do not run a learned probe, annotate additional data, open a hypothesis or execute three gates in v5.

## Execution And Recovery

CPU-only, new workspace image `research3-q10-baselines:v5`, pinned public Python base and
`requirements_v2.txt`. Build with `--pull --no-cache`; use no pre-workspace image, simulator,
container or volume. No GPU requested. Dataset and source mounts are read-only; outputs are
under ignored `runs/q10_v5/` and compact summaries under `artifacts_v5/`.

Exact commands, job state, verification and results live in [README.md](README.md).
This protocol stays unchanged after freezing; deviations must be recorded in that README.
