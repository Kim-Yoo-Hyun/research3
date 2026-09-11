# Q10 Regularized Summary Probes v6

Created: 2026-09-07

## Status And Question

`specified_not_executed`. The preceding validation audit is completed and distinct from the
unexecuted logistic probe. Its results, run commands and verification live in [README.md](README.md).
The protocol is frozen by `protocol_v6.json`, including the SHA-256 of this document, dependency
record, fixed row-level inputs, prior model code and audit evidence. Future implementation must
verify that record before fitting; implementation hashes and a fresh image digest are an additional
execution freeze, not permission to change this scientific protocol.

**Question:** Do L2-regularized logistic probes on the existing physical summaries improve held-out
outcome prediction beyond the v5 rule-selection procedure and duration-only controls when tuning
is contained inside recording-grouped nested CV?

This is a bounded, exploratory Stage 6 separability check. It does not test RGB sufficiency,
annotation validity, novel architecture, online detection, causal information, object-disjoint
transfer or minimum sensing requirements. All 104 official test rows have already been inspected
in v5; reusing them here is exploratory. Nested train CV is also exploratory because this design
was informed by the v5 audit. No result here alone promotes Q10 to a hypothesis or paper claim.

## Evidence That Determines The Design

Facts from the fixed validation audit:

- Train failure-bearing recordings are pick 5, insert 9, remove 5. Across every outer/inner
  leave-recording-out training partition, minimum remaining failures are 3, 16, 3 respectively.
  Both classes are present in all 675 enumerated outer/inner training count records.
- Removing an action-bearing training recording changes v5's selected rule 0/11 times for pick,
  4/11 for insert, and 5/6 for remove. Deleting recordings without that action does not measure
  the stability of its rule and must not inflate the apparent agreement denominator.
- V5 ordinary selected CV macro BA is 0.7649; nested selection-procedure CV is 0.7239.
  Remove's BA falls from 0.6146 to 0.4917. This motivates nested selection, not a particular probe.
- Official test has only one remove recording and two failure-bearing pick recordings. It cannot
  resolve the grouped-transfer uncertainty, even if a probe obtains an encouraging test score.

## Fixed Population And Signal Boundary

Reuse the exact v5 JSONL features, without re-extracting HDF5 or adding new recordings:

| Input | Rows | Success | Failure | Role |
| --- | ---: | ---: | ---: | --- |
| `runs/q10_v5/train_features.jsonl` | 309 | 269 | 40 | nested CV, final train fitting |
| `runs/q10_v5/test_features.jsonl` | 104 | 94 | 10 | one exploratory test evaluation after training seal |

Keep pick/insert/remove, official file split, v4 row IDs and official issue handling unchanged.
No row dropping, imputation, class resampling, new label, new HDF5 read or action-specific
denominator changes. Missing/nonfinite features, conflicting labels, source-hash mismatch or an
unexpected class-deficient training fold are `INVALID_PROTOCOL`; stop without a scientific score.
All supplied features must match v5's finite 33-field schema and exact feature-name list.

Allowed numeric inputs are only the 33 v5 summaries. Action family routes separate binary models.
Recording ID is grouping metadata; exact action text belongs only to the v5 prior comparator.
Segment IDs, recording timestamps/identity, object names, labels and low-level annotations are
not numeric model inputs. Ground-truth segment boundaries are inherited: results are retrospective.

## Fixed Comparisons

Fit one independent model per action and feature group. Do not select a feature group using
either outer CV or official test results. Report all six groups, with `state_force` primary.

| Group | Features | Purpose |
| --- | ---: | --- |
| `duration` | 1: annotated segment duration | stopping-time control |
| `state` | v5 STATE, 14 | terminal pose/gripper baseline |
| `force` | v5 FORCE, 18 | force-summary baseline |
| **`state_force`** | STATE + FORCE, 32 | primary regularized physical-summary probe |
| `state_force_duration` | all 33 | incremental explicit-duration diagnostic |
| `state_force_peak` | STATE + measured/relative/compensated peak, 17 | sensitivity to removing force integrals/occupancy durations |

Feature names are expanded and frozen in `protocol_v6.json`, sorted lexicographically. No
interactions, polynomial features, learned embedding, feature selection, winsorization, transforms
or custom signal windows. Excluding explicit duration does not remove time information: impulse
and threshold-occupancy features still depend on window length. Even peak/state summaries can
reflect stopping conventions. The peak-only sensitivity is diagnostic, not a causal adjustment.

Comparators use the same outer folds and rows:

1. Family and exact-action-text Laplace priors from unchanged v5 code.
2. The complete bounded v5 library, including its duration/state/force/combined depth-1/2 rules.
   Within each outer training partition, select the per-action rule by the unchanged inner-CV
   algorithm. This is the primary deterministic comparator, not the v5 test winner.
3. The nested duration-only logistic probe. Probability threshold tuning must also be inside
   inner CV, so the probe is not compared with an artificially weak 0.5-threshold control.

The frozen audit already supplies the v5 selected-rule nested predictions. Reuse them only after
verifying hashes, outer-group membership and exact row alignment; a replay must reproduce them.
Keep the fixed `state_d1` results descriptive; do not replace the comparator after test inspection.

## Model, Preprocessing And Hyperparameters

Implementation target is scikit-learn 1.7.2, pinned by `requirements_v6.txt`:

- `StandardScaler(with_mean=True, with_std=True)`, fitted on the current fitting partition only.
  Zero-variance columns use scale 1; record columns and scaler statistics. No statistic is fit
  on an inner validation fold, outer held-out recording or official test.
- `LogisticRegression(penalty="l2", solver="lbfgs", fit_intercept=True, class_weight=None,
  max_iter=2000, tol=1e-8, random_state=20260907)`, float64 inputs, no sample weighting.
- Inverse regularization grid `C = [0.01, 0.1, 1.0, 10.0]`. No expansion after performance results.
- Success probability is the unweighted model's `predict_proba` for label True/1. This avoids
  interpreting class-balanced training probabilities as natural-frequency estimates; calibration
  is still empirical and must be measured.
- Hard success prediction is `p(success) >= t`, where `t` is selected from
  `{0.05,0.10,...,0.95,0.975,0.99}` inside inner CV. A threshold of 0.5 is not compulsory under
  class imbalance. Probability scores use the original p, not threshold-rescaled probabilities.
- For each action/group, pool inner out-of-fold predictions for every C. Select `(C,t)` by
  highest balanced accuracy, then lower Brier, smaller C, threshold closest to 0.5, smaller t.
  Use deterministic comparisons, treating metric differences <=1e-12 as ties. No calibration fit.
- A convergence warning, nonfinite coefficient or exhausted iteration limit invalidates the
  run. No automatic solver, tolerance, feature or denominator change is permitted. A numerical
  repair requires a documented revision before interpreting results.

Official implementation references: [LogisticRegression](https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.LogisticRegression.html)
defines L2/lbfgs and inverse regularization C;
[StandardScaler](https://scikit-learn.org/1.7/modules/generated/sklearn.preprocessing.StandardScaler.html)
defines training-set normalization and zero-variance handling. Nested model selection separates
tuning from evaluation, as explained in the [official nested-CV example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).
The concrete folds, grids and pilot tolerances here are agent design choices, not source claims.

## Nested CV And Final Fitting

1. Sort all 15 official train recording IDs. Each is one outer held-out group. A recording
   with no rows of an action contributes no predictions for that action; keep it in the global
   group scheme. No individual fold BA is assigned where held-out rows lack a class.
2. Within the remaining 14 recordings, perform inner leave-one-recording-out fitting separately
   for each action/group/C, with a fresh scaler on every fitting partition.
3. Pool inner held-out rows by action before choosing C and t. An inner held-out fold may have
   one class; pooled inner outcomes and each fitting partition must have both classes.
4. Refit the chosen scaler/model on that outer training partition and predict only the outer
   recording. All 309 rows must receive exactly one outer prediction per probe/comparator.
5. Report pooled outer metrics, selection frequencies, coefficient norms and scaler/threshold
   variability. Outer fold scores do not choose the final C, t or primary feature group.
6. Independently repeat ordinary leave-one-recording-out tuning on all 309 train rows to select
   final C/t for each group/action, then fit on all train rows. Seal parameters, scalers, CV
   predictions, input/source hashes and their timestamp before mounting the test feature file.
7. Run one separately invoked test evaluation from that sealed bundle, producing predictions
   for all six pre-fixed groups and baseline controls on all 104 test rows. It cannot refit,
   choose models or change the Stage 6 decision. Report test/nested disagreements explicitly.

No use of the phrase “independent nested CV samples”: outer training folds overlap, and design
adaptation has already occurred. This is a diagnostic estimate of a fixed training procedure.

## Metrics, Uncertainty And Pre-Fixed Decisions

Same definitions as v5: positive=success, action BA=(success recall+failure recall)/2; macro BA
is the equal mean over three actions. Report per-action confusion, both recalls, macro Brier,
log loss and five-bin equal-width ECE. Record hard threshold separately from probability outputs.

Primary contrast: nested `state_force` macro BA minus nested v5 selected-rule macro BA.
Also report paired contrasts against family prior, duration probe and state-only probe.
Bootstrap the 15 train recording groups using fixed outer predictions, 2,000 draws, seed 20260907,
15 groups sampled with replacement. Use identical draws across comparisons. Skip (and count)
draws missing a class in any action, without replacing them. Report percentile 95% intervals;
fewer than 1,000 valid draws gives `UNCERTAIN_PROBE`. This is conditional uncertainty of the
fixed outer predictions, not full training/selection uncertainty. Report selection variability
separately. Official test intervals retain v5's five-cluster caveat and are descriptive only.

Frozen pilot decisions, based on **nested train CV only**, in order:

1. `INVALID_PROTOCOL`: integrity/numerical/fold failure. No scientific result; record failure.
2. `UNCERTAIN_PROBE`: fewer than 1,000 valid bootstrap draws. Stage 7: repeat feasibility or
   refine evaluation population; no architecture escalation.
3. `SUMMARY_SIGNAL_SUPPORTED` requires all of: primary macro BA >=0.75; >=0.05 gain over each
   of v5 selected-rule, family prior and duration probe; primary-v5 gain interval lower bound >0;
   >=0.05 BA gain over the v5 rule in at least two actions; primary macro Brier <= prior+0.02.
   The 0.75/0.05 thresholds measure a useful pilot signal, not v5's stronger practical sufficiency.
   Stage 7: repeat feasibility on separately frozen independent recordings and resolve label/RGB
   validity before any hypothesis admission.
4. `NO_USEFUL_SUMMARY_GAIN`: none of `state`, `force`, `state_force` achieves >=0.05 macro BA
   gain over the v5 selected-rule **and** >=0.05 gain over duration on nested predictions.
   Stage 7: discontinue this summary-only probe route, or explicitly reformulate Q10 from new
   evidence. Do not try a larger architecture to preserve the original claim.
5. Otherwise `MIXED_OR_UNSTABLE`: record the failed conditions and choose refine/repeat based on
   recording errors. A duration-inclusive gain alone is not physical-signal support.

Separately report v5's stronger practical-sufficiency checks (macro BA >=0.85, prior gain >=0.10,
every action BA/failure recall >=0.75, Brier <=prior+0.02) unchanged, on nested and test outputs.
Passing those checks does not bypass the new primary comparisons or establish saturation.
Force increment over state is descriptive unless it reaches >=0.05 macro BA, >=0.05 in two
actions and has a positive paired interval lower bound. Even then it is predictive, not causal,
and is not evidence for information beyond RGB. No automatic promotion in any branch.

## Deliverables, Runtime And Verification

Next task is implementation and execution of this protocol, followed by a Stage 7 decision.
No v6 logistic model has yet been fit. Planned runtime: fresh workspace-owned Dockerfile/image
`research3-q10-probe:v6`, the same pinned public Python base as the audit, `requirements_v6.txt`,
CPU-only with OMP/OPENBLAS/MKL threads=1 and seed 20260907. No pre-workspace Docker assets.
Fresh build uses `--pull --no-cache`; runtime network is disabled. Source/data are read-only.
The runner must background long work with timestamped logs and exit/status files under `logs/`.
Estimated work: fewer than 20,000 small logistic fits (6 groups, 3 actions, 4 C values, nested
15x14 folds plus final tuning/refits); set a 30-minute wall-clock cap and 4 GiB memory limit.
If the cap is reached, retain partial artifacts as incomplete and do not change the experiment.

Planned outputs: ignored `runs/q10_v6/` for nested/inner/test predictions and errors; compact
`artifacts_v6/` for implementation freeze, image/dependencies, final model/scaler bundle, metric
tables, uncertainty, decision and verification. Create them only at execution, not as empty roots.
Exact Dockerfile and train/evaluate/verify commands must be recorded in the existing study README
before launch. The test feature file must be absent from the training container's mounts.

Required verification before accepting results:

- protocol/input hashes, exact feature sets, no train/test or nested-fold group overlap;
- scaler/train-fit membership, pooled inner selection arithmetic, final seal before test mount;
- synthetic meaningful checks for class imbalance, threshold choice and fold-local preprocessing;
- independent replay from saved numeric coefficients/scalers and row IDs, confusion/BA/Brier;
- 309 nested and 104 test predictions per reported group, fixed denominator and no NaNs;
- decision conditions computed independently; convergence and resource status, output checksums.

Record results in the existing README; do not create a new `report_*.md`. Keep v1--v5 and the
validation audit immutable. No new data, annotation, foundation model, hypothesis or three-gate
execution is part of this protocol.
