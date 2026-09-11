# Q10 Feasibility Studies

Updated: 2026-09-08

## Ownership

Protocols and previous results: `manifest_v1.md` through `manifest_v4.md`.
Frozen protocols: [manifest_v5.md](manifest_v5.md) and [manifest_v6.md](manifest_v6.md).
V6 is executed and verified; its pre-execution manifest retains the original status text.
This README owns execution,
verification, result interpretation and deviations. These are Stage 6 studies in `buildup/`.

Current disposition: [Stage 7 — discontinue](../../../selection.md#q10--discontinue-2026-09-08).
Studies are completed provenance; no additional Q10 run is queued. The decision document owns
the question's disposition, and `literature/README.md` owns the compact retired-research summary.

## v5 Job

Status: `completed`, independently verified `PASS`; decision `UNCERTAIN_RESIDUAL`.
CPU-only; seed 20260907; no GPU mount.
Working directory: `/home/yoohyun/research3`.
Raw features, predictions and errors: ignored `runs/q10_v5/`.
Compact outputs: `buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v5/`.
Inputs: existing `datasets/q10_reassemble/v2/` and `v4/`, mounted read-only; no download needed.

Run command (orchestration only on host):

```bash
tmux new -d -s research3_q10_v5 'cd /home/yoohyun/research3 && bash buildup/robotics/pilot_studies/q10-contact-observability/run_v5.sh'
```

`run_v5.sh` records timestamped build/run/verification logs and exit status in `logs/`, builds
the fresh image, freezes protocol/source hashes, executes baseline tests, runs train/test analysis
and verifies the resulting artifacts. The exact Docker commands are in that script.
Expected compact files: `freeze.json`, `image.json`, `training.json`, `summary.json`,
`metrics.tsv`, `error_counts.tsv`, `verification.json`, `checksums.json`.
Expected ignored files: `train_features.jsonl`, `test_features.jsonl`, `predictions.jsonl`,
`errors.jsonl`, `bootstrap.json`, `provenance.json`.
Log prefix pointer: `logs/q10_v5_latest.txt`; each job writes `.status` and `.exit` alongside
timestamped `_build.log`, `_tests.log`, `_run.log` and `_verify.log`.

Independent verification (inside the new Docker image):

```bash
docker run --rm --network none --name research3-q10-verify-v5 \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability:/workspace:ro \
  -v /home/yoohyun/research3/runs/q10_v5:/output:ro \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v5:/artifacts:rw \
  --entrypoint python research3-q10-baselines:v5 /workspace/verify_v5.py
```

Outputs are exclusive-create and are not overwritten. The verification command above is the
original invocation; for a later rerun, use a separate writable artifact directory containing
copies of the frozen compact inputs, and a new ignored raw-output directory for re-execution.
Do not delete existing results just to rerun the script. The frozen `run_v5.sh` documents the
original invocation and intentionally refuses reuse of its populated output paths.

## v5 Result — 2026-09-07

**Fact:** All 413 fixed rows produced 33 finite features with no exclusions or denominator change.
The 309 train rows were processed and the fitted-rule artifact was sealed before signal
extraction from the 104 test rows. Five invariant tests passed; independent verification replayed
all 1,144 candidate/row predictions and reproduced the metrics, errors and decision.

| Fixed candidate | Test macro balanced accuracy | Macro Brier |
| --- | ---: | ---: |
| Family prior | 0.5000 | 0.09481 |
| Exact-action-text prior | 0.4868 | 0.11193 |
| Duration, depth 1 | 0.3426 | 0.10832 |
| Duration, depth 2 | 0.3230 | 0.11156 |
| State, depth 1 | 0.6976 | 0.08667 |
| State, depth 2 | 0.5365 | 0.09481 |
| Force, depth 1 | 0.5116 | 0.09816 |
| Force, depth 2 | 0.4737 | 0.10772 |
| Combined, depth 1 | 0.6976 | 0.08667 |
| Combined, depth 2 | 0.5267 | 0.09624 |
| **Train-CV-selected combination** | **0.5261** | **0.09855** |

Only the last row determines the decision. State/combined depth 1 have the highest descriptive
test score in this library, but replacing the selected rule with them after seeing test results
would violate the protocol. Full calibration metrics and confusion matrices are in
[`metrics.tsv`](artifacts_v5/metrics.tsv); train CV and exact fitted thresholds are in
[`training.json`](artifacts_v5/training.json).

| Action | Train-selected rule | Train OOF BA | Test BA | Failure recall | False success / false failure |
| --- | --- | ---: | ---: | ---: | ---: |
| pick | state, depth 1 | 0.9119 | 0.7500 | 2/4 | 2 / 0 |
| insert | state, depth 2 | 0.7682 | 0.4605 | 0/4 | 4 / 3 |
| remove | duration, depth 2 | 0.6146 | 0.3676 | 1/2 | 1 / 13 |

There are 23 selected-rule errors: seven failures predicted as success and 16 successes predicted
as failure. Brier alone passes its tolerance; the other four practical checks fail.
Paired recording bootstrap yields 1,198 valid and 802 invalid draws. The descriptive 95% interval
is `[0.4407, 0.5556]` for macro BA and `[-0.0593, +0.0556]` for gain over the family prior.
These intervals omit class-deficient draws as specified and are conditional on class coverage.
They are particularly weak evidence for remove, whose entire test population is one recording.

### Error Diagnosis And Claim Boundary

**Observed error strata:**

- Pick uses terminal left-finger position and detects two of four failures with no false failure.
  Its remaining false-success cases are in two different recordings.
- Insert's selected tree uses left-finger change/terminal position. It misses all four failures
  across three recordings. The train OOF score does not transfer to this official test subset.
- Remove's duration rule marks 13 of 17 successes as failure. All 19 remove test rows (including
  its two failures) come from `2025-01-09-17-14-59`; there is no multi-recording remove test evidence.
- Fixed state/force depth-2 rules make 15/29 errors and share seven; combined depth 2 retains
  all 15 state errors and adds one. Error complementarity alone does not yield a useful combined
  rule. See [`error_counts.tsv`](artifacts_v5/error_counts.tsv) and `summary.json` for exact strata.

**Agent inference:** Model selection with few minority outcomes and variation across recordings
is a plausible explanation for the CV/test discrepancy. Duration may encode operator stopping
conventions. Neither explanation has been causally verified; feature thresholds cannot identify
physical failure causes or annotation mistakes. This result does not establish that all physical
rules fail, that RGB is insufficient, or that a learned multimodal architecture is necessary.

**Next validation:** Freeze a separate regularized linear/logistic probe study on the same
summaries. Audit per-action failure-bearing train recording counts and grouped-validation
stability first; compare duration-only, state-only, force-only and state+force without duration,
with duration addition reported separately. Any further use of these already inspected 104 test
rows is exploratory. A later confirmatory claim needs a separately frozen evaluation population
with multiple independent recordings per action; keep v5's population and thresholds unchanged.
Outcome-label validity and matched RGB comparison also remain unresolved. No hypothesis,
architecture, new annotation or three-gate run was started.

### Provenance And Verification

- Original log prefix: `logs/20260907_002743_q10_v5`; final `.status=completed`, `.exit=0`.
- New image index digest: `sha256:c9180525677b6914e2012d710f33c457a14e66f5293da7f31e0582780fa28550`.
  Image config and platform manifest are recorded in [`image.json`](artifacts_v5/image.json).
- Frozen source/protocol/input SHA-256: [`freeze.json`](artifacts_v5/freeze.json).
  Output SHA-256 inventory: [`checksums.json`](artifacts_v5/checksums.json).
- Independent result: [`verification.json`](artifacts_v5/verification.json).
- Numerical tie audit reran the full-train and leave-recording-out fits inside the same v5 Docker
  image: 1,064 terminal nodes, zero mathematical weighted ties incorrectly assigned failure.
  Log: `logs/20260907_002743_q10_v5_tie_audit.log`. This audit changed no rule or output.
- Protocol deviations: none. The five-cluster/removal coverage limitation is an observed result,
  not a reason to revise the denominator or practical margin after execution.

## Validation Audit Before v6

Status: `completed`, independently verified `PASS`. This audit precedes the v6 probe protocol and fits only the frozen v5
threshold library. No logistic probe or new feature is tested. CPU-only; no GPU or HDF5 download.

Fixed audit, specified before its results:

1. Count rows, success/failure-bearing recordings and maximum failure concentration per action
   and official split using the unchanged v4 table.
2. On the 309 train rows only, enumerate outer leave-one-recording-out and inner
   leave-one-recording-out training class counts. Report missing classes and minimum remaining
   failures; an undefined balanced accuracy stays undefined, never zero or silently excluded.
3. Replay the full v5 train selection, checking its CV scores against sealed `training.json`.
4. Remove each of the 15 train recordings in turn and repeat v5's entire inner selection. Report
   selected-candidate frequencies and changes, distinguishing removals with/without that action.
   Predict only the omitted outer training recording with the inner-selected rule. Pool those
   outer predictions for a nested CV estimate. This evaluates the *selection procedure* and
   separates its performance from the optimistically selected ordinary CV score.
5. Retain all rows. If any necessary inner score or fit is undefined, report the affected action
   as not estimable; do not redesign the fold scheme based on a resulting performance score.
6. Audit is descriptive: selection frequencies have no pass threshold, and training deletion
   scores are not independent replicates. New v6 design decisions must cite these observations.

Runtime: new image `research3-q10-validation:v6`, pinned public Python base and the same
`requirements_v2.txt`; fresh `--pull --no-cache` build. Source mount is read-only. Only
`runs/q10_v5/train_features.jsonl` is mounted as feature input; v5 test features are not mounted.
Existing v4 split/label metadata and frozen v5 train models are read-only audit inputs.
Raw nested predictions: ignored `runs/q10_validation_v6/`; compact outputs:
`artifacts_validation_v6/` (`coverage.tsv`, `folds.tsv`, `stability.tsv`, `audit.json`,
`verification.json`, `freeze.json`, `image.json`, `checksums.json`).

Working directory: `/home/yoohyun/research3`. Exact commands are in `run_validation_v6.sh`.

```bash
tmux new -d -s research3_q10_validation_v6 'cd /home/yoohyun/research3 && bash buildup/robotics/pilot_studies/q10-contact-observability/run_validation_v6.sh'
```

Timestamped log/exit/status prefix pointer: `logs/q10_validation_v6_latest.txt`.
The runner executes `audit_validation.py`, then its independent `--verify` mode in Docker.
No v5 artifact, source, threshold or denominator is modified.

### Audit Findings — 2026-09-07

**Facts:**

| Action | Train recordings / with failure | Test recordings / with failure | Minimum inner-fit failures | Selection changes on action-bearing deletions | Ordinary selected CV BA | Nested CV BA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pick | 11 / 5 | 4 / 2 | 3 | 0/11 | 0.9119 | 0.9119 |
| insert | 11 / 9 | 3 / 3 | 16 | 4/11 | 0.7682 | 0.7682 |
| remove | 6 / 5 | 1 / 1 | 3 | 5/6 | 0.6146 | 0.4917 |

All 675 outer/inner fitting count records retain both classes. The v5 training selection and CV
scores replay exactly. Nested outer predictions preserve all 309 training rows, with no test
feature access. Macro BA changes from ordinary selected CV 0.7649 to nested selection CV 0.7239.

Pick always selects state depth 1. On action-bearing deletions, insert selects state depth 2 seven
times, state depth 1 twice and combined depth 2 twice. Remove selects state depth 2 three times,
state depth 1 twice and duration depth 2 only once. Using all 15 deletions would misleadingly
count nine removals of recordings with no remove action as additional agreement.

**Agent inference:** Pick's selected rule is stable under this specific deletion check. Remove's
ordinary CV score is sensitive to using the same validation predictions to choose a rule;
nested selection does not retain its apparent above-chance competence. This does not prove the
cause of the official test discrepancy or independent-session transfer. Recording is not
automatically a distinct session/operator/object. Outcome construct validity remains unresolved.

**Protocol consequence:** [v6](manifest_v6.md) is frozen before logistic fitting. It uses per-action
L2 logistic regression, four C values, fold-local scaling and nested recording CV for all tuning,
including probability thresholds. Six fixed feature groups separate explicit duration addition
and force peak-only sensitivity from the primary state+force summaries. Force integrals still
contain window-length information; exclusion of explicit duration is not a causal control.
The primary comparison is against the entire v5 rule-selection procedure on matched nested folds.
The already inspected official test is secondary exploratory evaluation only.

At the audit's completion on 2026-09-07, the logistic probe had not run. The subsequent v6 job
and results below own its execution status. No hypothesis, annotation or architecture was started
by the audit.

### Audit Recovery And Protocol Freeze

- Log prefix: `logs/20260907_103354_q10_validation_v6`; `.status=completed`, `.exit=0`.
- Audit image ID: `sha256:c8b29b70c5a48178e0c438318271f394b8e22438f6cf637158b0f146c27ef9b1`.
- Input/source hashes and runtime record: `artifacts_validation_v6/freeze.json`, `image.json`.
- Results and exact counts: [audit.json](artifacts_validation_v6/audit.json),
  [coverage.tsv](artifacts_validation_v6/coverage.tsv), `folds.tsv`, `stability.tsv`.
- Independent verification: [verification.json](artifacts_validation_v6/verification.json);
  artifact SHA-256 inventory: `artifacts_validation_v6/checksums.json`.
- Frozen v6 scientific specification: [protocol_v6.json](protocol_v6.json), SHA-256
  `0fa06e424870090b8fc46f205aaaa0748c3a04ca4aaedcfff5e214903c465dd4`.
  Its manifest, dependency pins, v5 inputs and audit evidence have separate embedded hashes.
  The subsequent execution's exact installed dependency list and image digest are recorded below.
- Audit runner and its `--verify` mode use exclusive-create outputs. To repeat, use fresh raw
  and compact output directories; never remove the original results to make a rerun succeed.

## v6 Job

Status: `completed`, corrected independent verification `PASS`; decision `NO_USEFUL_SUMMARY_GAIN`.
Initial verification found a log-loss clipping-order mismatch, corrected as documented below.
Scientific protocol, inputs, training and test predictions remain unchanged.
Working directory: `/home/yoohyun/research3`. CPU-only, 4 GiB memory cap, one thread and seed
20260907; no GPU, new data, annotation or HDF5 extraction. The new image is
`research3-q10-probe:v6`, using `Dockerfile_v6` and the frozen `requirements_v6.txt`.

Build (background, log under `logs/`; image metadata captured at execution):

```bash
tmux new -d -s research3_q10_probe_build_v6 'cd /home/yoohyun/research3 && docker build --pull --no-cache -t research3-q10-probe:v6 -f buildup/robotics/pilot_studies/q10-contact-observability/Dockerfile_v6 buildup/robotics/pilot_studies/q10-contact-observability > logs/20260908_q10_probe_v6_build.log 2>&1; task_exit=$?; echo "$task_exit" > logs/20260908_q10_probe_v6_build.exit'
```

The train process receives only the immutable v5 train feature file and audit prediction input.
Test features are mounted in a separate evaluation container after the final train artifact seal.
Planned raw outputs: ignored `runs/q10_v6/train/`, `runs/q10_v6/test/`;
compact outputs: `artifacts_v6/`. Inner models, predictions and tuning records remain ignored.
Execution: `run_probe_v6.sh` records tests, exact Docker commands, runtime cap, provenance,
verification and completion state. Frozen v6 manifest/JSON remain unchanged;
this README owns live execution status.

```bash
tmux new -d -s research3_q10_probe_v6 'cd /home/yoohyun/research3 && bash buildup/robotics/pilot_studies/q10-contact-observability/run_probe_v6.sh'
```

Log pointer: `logs/q10_probe_v6_latest.txt`, with timestamped `_tests.log`, `_train.log`,
`_evaluate.log`, `_verify.log`, `.status` and `.exit`. Build log is recorded above.
Runner uses the newly built image's immutable ID and enforces a shared 1,800-second budget for
training, evaluation and verification. `probe.py train` cannot access the test feature file;
`probe.py evaluate` uses only the sealed numeric bundle and cannot refit.

Expected compact outputs: `execution.json`, `image.json`, `dependencies.txt`, `training.json`,
`train_seal.json`, `nested.json`, `test.json`, `metrics.tsv`, `selection.tsv`, `errors.tsv`,
`variability.json`, `verification.json`, `checksums.json`.
Raw train files: `models.jsonl`, `inner.jsonl`, `tuning.jsonl`, `nested_predictions.jsonl`,
`baseline_models.json`, `bootstrap.json`. Raw test files: `predictions.jsonl`, `errors.jsonl`,
`bootstrap.json`. Verification is the final Docker command in `run_probe_v6.sh` and independently
replays saved coefficients/scalers, all tuning records, fold membership, metrics and decisions.
All outputs are exclusive-create; reruns must use new output paths and preserve previous attempts.

### Verification Correction — 2026-09-08

Original run prefix: `logs/20260908_100255_q10_probe_v6`. Training and test completed, but the
original verification exited before writing its accepted result. It independently reproduced
all inner predictions/tuning and reached metric validation. Only train force/insert log loss
differed: 0.70327466795 vs 0.70327486906. The verifier clipped the probability of the observed
class; frozen v5 clips p(success) first and then computes its complement for a failure. At a
probability rounded to one, floating-point subtraction makes these differ slightly.

`verify_probe_v2.py` corrects only that verifier formula and adds an endpoint regression fixture.
It calls the preserved original verifier for all other checks. The frozen `verify_probe.py`,
protocol, execution record, trained models, nested/test predictions and decision are unchanged.
This is a verification implementation correction, not a new experiment or metric revision.
New verifier provenance is in `artifacts_v6/verification_revision.json`. No refitting or repeated
test evaluation occurs. The original failed log and exit status remain preserved.

```bash
tmux new -d -s research3_q10_verify_v6 'cd /home/yoohyun/research3 && docker run --rm --network none --memory 4g --cpus 1 --name research3-q10-verify-v6-corrected -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability:/workspace:ro -v /home/yoohyun/research3/runs/q10_v5/train_features.jsonl:/input/train_features.jsonl:ro -v /home/yoohyun/research3/runs/q10_v5/test_features.jsonl:/input/test_features.jsonl:ro -v /home/yoohyun/research3/runs/q10_v6:/raw:ro -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v6:/artifacts:rw --entrypoint python research3-q10-probe:v6 -B /workspace/verify_probe_v2.py > logs/20260908_q10_probe_v6_verify_corrected.log 2>&1; task_exit=$?; echo "$task_exit" > logs/20260908_q10_probe_v6_verify_corrected.exit'
```

Correction result: `PASS`, exit `0`. Five original invariant tests and the clipped-endpoint
regression fixture passed. The new verifier independently checked 16,488 fits/scalers, 111,240
inner predictions, 288 tuning choices, 5,253 nested predictions and 1,768 test predictions.
No scientific protocol deviation or refitting occurred. For future reproduction, replace only
the frozen runner's verification invocation with the corrected command above, after creating its
verification revision record in a fresh artifact directory; the original runner is historical.

## v6 Result — 2026-09-08

**Fact:** `NO_USEFUL_SUMMARY_GAIN` under the pre-fixed nested-CV decision. All 309 train and
104 test rows were retained. Six probe groups and 11 v5 comparators each produced complete
predictions. The final train bundle was sealed before the separate test container started.

| Method | Nested macro BA | Nested macro Brier | Exploratory test macro BA | Test macro Brier |
| --- | ---: | ---: | ---: | ---: |
| Family prior | 0.5000 | 0.10768 | 0.5000 | 0.09481 |
| v5 rule-selection procedure | 0.7239 | 0.08963 | 0.5261 | 0.09855 |
| Duration logistic probe | 0.6097 | 0.10724 | 0.4103 | 0.09774 |
| State logistic probe | 0.6584 | 0.08952 | 0.6599 | 0.07385 |
| Force logistic probe | 0.5390 | 0.11100 | 0.4025 | 0.12721 |
| **State+force (primary)** | **0.5791** | **0.09638** | **0.6579** | **0.08831** |
| State+force+duration | 0.5750 | 0.09709 | 0.6579 | 0.08828 |
| State+force peaks | 0.6340 | 0.08829 | 0.7445 | 0.07061 |

No state/force/state+force probe achieved the required 0.05 nested macro BA gain over both the
v5 procedure and duration probe. The primary-v5 gain is -0.1448; its paired recording bootstrap
95% interval is `[-0.2299, -0.0347]` (1,997 valid / 3 invalid draws). Primary-state gain is
-0.0793 with interval `[-0.1507, -0.0316]`; the frozen force-increment condition is not met.
Intervals condition on fixed outer predictions and class-covered resamples; they do not include
all fitting/selection uncertainty. No primary practical-sufficiency pass occurs on either split.

The higher official test score does not reverse the decision. It is exploratory, already observed
in prior studies and has only five recordings. Its 1,198 valid / 802 invalid bootstrap draws do
not establish independent transfer. The peak-only group's test score also cannot be used to
replace the pre-fixed primary group after seeing results.

### Action Errors And Selection Variability

| Action | Nested primary BA | Nested failure recall | Nested false success / false failure | Test primary BA | Test failure recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| pick | 0.3285 | 1/6 | 5 / 53 | 0.5000 | 0/4 |
| insert | 0.7365 | 13/25 | 12 / 4 | 0.4737 | 0/4 |
| remove | 0.6722 | 4/9 | 5 / 8 | 1.0000 | 2/2 |

Primary nested errors total 87 (22 false success, 65 false failure). Test errors total 10
(eight false success, two false failure). Test pick and insert miss all failures. Remove's
perfect test hard decisions concern only 19 rows from one recording, not a generality result.

On action-bearing outer folds, primary pick chooses C=0.01/0.1/10 in 5/3/3 folds; its selected
threshold ranges from 0.1 to 0.99. Insert chooses C=0.1/1/10 in 6/4/1 folds; remove chooses
C=0.01/0.1/1 in 1/4/1 folds. These are descriptive stability observations, not independent
replicates. The final all-train primary C/threshold pairs are pick 0.01/0.5, insert 1/0.5 and
remove 0.1/0.8, selected by ordinary train CV after the nested assessment procedure was fixed.
Detailed coefficient norms and fold-local scaler ranges live in `variability.json`.

**Agent inference:** A small number of minority outcomes and unstable C/threshold selection are
plausible contributors to pick's weak nested performance. Adding the frozen force summaries
does not help the matched state probe under this procedure. Explicit duration addition does not
repair the primary result. These are predictive observations; they do not identify physical
failure causes, prove intrinsic signal insufficiency, or validate annotations.

**Selection decision:** [Stage 7](../../../selection.md#q10--discontinue-2026-09-08) applied the
pre-fixed negative branch and discontinued this route and current Q10 formulation. It did not
claim that the broader RGB-relative question was falsified. No larger evaluator or changed
threshold/feature group is queued. Label validity, matched RGB evidence and group-independent
evaluation remain unresolved; no hypothesis or three-gate execution was opened.

### v6 Provenance

- New image ID: `sha256:e45ade4bbe3081bc6b6659fa5efebd0a71744aca71c57ae8b476949c17d0b715`.
  Exact installed packages: [dependencies.txt](artifacts_v6/dependencies.txt); image metadata:
  `artifacts_v6/image.json`. Frozen pins match the installed versions; the image also includes
  `packaging==26.3`, recorded in the runtime inventory.
- Train fitting and nested assessment wall time: 27.05 seconds, 16,488 logistic fits, CPU only.
  Train/evaluate/verification containers use a 4 GiB limit and one CPU; no GPU was mounted.
- Scientific outputs: [nested.json](artifacts_v6/nested.json), [test.json](artifacts_v6/test.json),
  [metrics.tsv](artifacts_v6/metrics.tsv), [errors.tsv](artifacts_v6/errors.tsv),
  [selection.tsv](artifacts_v6/selection.tsv), [variability.json](artifacts_v6/variability.json).
- Final bundle and seal: `training.json`, `train_seal.json`; scientific/source integrity:
  `protocol_v6.json`, `artifacts_v6/execution.json` and `verification_revision.json`.
- Accepted verification: [verification.json](artifacts_v6/verification.json); complete raw/compact
  hash inventory: `artifacts_v6/checksums.json`. Corrected verifier log/exit are recorded above.
