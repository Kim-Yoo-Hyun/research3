# Real Keypoint Geometry

Updated: 2026-09-16

## Scope and status

`completed; verified`; exploratory 24-frame observation selected in the
[Q14 design](../../../questions/frame-error-propagation.md#real-keypoint-observation).
One frozen DREAM Panda VGG-Q detector, Panda-3Cam RealSense, shared predicted keypoints
for EPnP + iterative refinement and RANSAC (5 px, seed 20260916, 100 iterations,
confidence 0.99) + inlier refinement. Common-point and all-in-frame GT-2D controls
separate localization and support. Full annotated 3D point set for comparable ADD.
No training or action-head evaluation. Camera-frame annotated geometry is privileged;
the estimated transform is a pose-error transform with identity reference.

Current research disposition: [deferred after the follow-up review](#follow-up-investment-decision-2026-09-16).
The completed observation and its original `refine` decision are preserved below.

The [workspace cleanup review](../../../../../docs/reproducibility.md#workspace-file-cleanup--2026-09-16)
lists the full data archive and detector weights as candidates only after external-backup verification.
Selected inputs, metadata and outputs should remain; no files were deleted.

## Preparation and recovery

Working directory: `/home/yoohyun/research3`. Source revision:
`NVlabs/DREAM@3360f2aa45f66a58eaa70d0d40f2c46c2682c0bb`.
Only selected official data/weight/YAML download IDs are acquired, not the entire download script.
Inputs: `datasets/q14/dream/`; read-only source: `external/q14-dream/`.
Execution snapshots and outputs: `runs/q14/real_<timestamp>/`.
Downloads/builds and inference run in separate tmux sessions with timestamped `logs/`.
The new CPU Docker image uses a pinned public Python base, not an unrelated local image.
Older DREAM hardcodes CUDA; any device adaptation is preserved separately and checked against
the original model, preprocessing and checkpoint keys. No host method imports/install/runtime.

Input acquisition entry point: `python buildup/robotics/pilot_studies/q14-frame-errors/real/acquire.py`.
Expected: official source ZIP and extracted source; dataset archive; `.pth` and matching `.yaml`;
`datasets/q14/dream/acquisition.json` with URL, size, SHA256 and access status. Source/archive
identity and file layout are inspected before the 24 IDs are frozen and before model inference.
Exact job commands and execution results are appended below as work proceeds.

## Jobs 2026-09-16

Acquisition completed: official source, YAML, weights and archive downloaded with resumable curl.
`prepare_inputs.py` inspected 5,944 RGB IDs and extracted the preselected 24 images + 24 annotations
and camera metadata (49 members, ZIP CRC and SHA256 recorded in `selected/manifest.json`).
No prediction was available when sampling. Source archive and raw payloads remain preserved.

Docker build completed as `research3-q14-real-keypoints:v1`; immutable ID is in
`runs/q14/real_20260916_113000/image.id`. CPU adaptation removes two unused analysis/training
imports, changes network `.cuda()` to `.to("cpu")`, and skips discarded ImageNet initialization.
The released checkpoint is loaded strictly, with every loaded tensor compared to its source.
Inference uses the released YAML's `resize`, not the paper's training `shrink-and-crop` setting.
This is a released-model observation, not an exact paper-table reproduction.

Background command pattern (each command is passed to its own tmux session):

```bash
cd /home/yoohyun/research3
python buildup/robotics/pilot_studies/q14-frame-errors/real/acquire.py > logs/20260916_114000_q14_real_acquire.log 2>&1
python buildup/robotics/pilot_studies/q14-frame-errors/real/prepare_inputs.py
python buildup/robotics/pilot_studies/q14-frame-errors/real/job.py build real_20260916_113000 > logs/20260916_113000_q14_real_build.log 2>&1
python buildup/robotics/pilot_studies/q14-frame-errors/real/job.py observe real_20260916_113000 > logs/20260916_113400_q14_real_observe.log 2>&1
```

Each background wrapper also writes the corresponding `.exit`. Filenames are job labels;
the acquisition log was created at 11:27:30 KST (its label is 11:40). Actual inference duration
is measured in output. Exact Docker argv, mount/CPU/memory/timeout options and source snapshots
are in the run's `commands.jsonl`; full dependency versions and applied source hashes are retained
in the output. Observe status: `completed`. Produced: 24 records/arrays/overlays, solver summaries,
execution metadata and output manifest. Verification command is the same job entry point with
`verify` phase; it consumes observations read-only and runs in a separate Docker container.

## Post-observation diagnostic

The planned observation and independent verifier completed (24 frames, 96 solver rows).
Two opposite cases, 001033 and 001808, show that each solver can produce a large pose error.
Before any further inference/training, evaluate a simpler explanation using the **saved poses**:
choose the candidate with lower mean squared reprojection error on the same available predicted
points. Selection uses predicted 2D points and the already-privileged 3D input, never GT-2D or ADD.
This is a post hoc control prompted by viewed results, not a held-out result or novel method.
Record both candidates' score and resulting ADD for every original frame, independently recompute
the selected metric, and do not tune any threshold. Also describe point geometry numerically
without claiming that it identifies the cause of a particular optimization failure.

## Results 2026-09-16

The planned 24 detector inferences and 96 solver rows completed; all four solver conditions
returned a pose on all 24 frames. CPU observation took 16.63 seconds, excluding build/startup.
No training, model/threshold search or additional sensor/view data was used.
Strict checkpoint load and exact equality of every loaded tensor passed.
Immutable image: `sha256:9c8a10f15a70841aabb72be506768aa7cf17331fc36a02172d453693b85ddf1d`.

**ADD below uses native annotation coordinates and all seven annotated 3D points.** Runtime
metadata describes the scale as metres in DREAM convention; this study did not independently
calibrate metric scale, so it preserves raw units and makes no mm-level physical accuracy claim.
The GT camera-frame input remains privileged, and the reference pose-error transform is identity.

| Estimator | Successful frames | Mean ADD | Median ADD | Max ADD |
| --- | --- | --- | --- | --- |
| Official EPnP + iterative refinement | 24/24 | 0.0295091 | 0.0141489 | 0.3170274 |
| RANSAC + inlier refinement | 24/24 | 0.0283908 | 0.0136342 | 0.2581194 |
| GT-2D, common points | 24/24 | 2.21e-16 | 2.11e-16 | 5.53e-16 |
| GT-2D, all in-frame points | 24/24 | 2.21e-16 | 2.11e-16 | 5.53e-16 |
| Lower all-point reprojection MSE, **post hoc** | 24/24 | 0.0169537 | 0.0141489 | 0.0461792 |

RANSAC improved ADD in 4 frames, worsened it in 6, and matched within 1e-8 in 14. Means do not
establish consistent improvement. Twenty-three frames had seven detections; frame 002583 had
five. Its absent IDs 5/6 are both GT-out-of-frame, so **all GT-in-frame keypoints were detected**.
Common/all oracle controls therefore use identical point sets throughout. This slice does not
identify the effect of missing in-frame correspondences. An earlier progress update saying every
frame had seven detections was corrected after inspecting the complete records.

GT 2D projections agree numerically with the same 3D annotations and K. Near-zero oracle errors
are thus expected for this internally consistent construction. They show localization/solver
effects relative to those labels, not independent truth of DART-derived annotations.

### Concrete cases and visual review

The complete 24-image overlay sheet and full-size 001033/001808 overlays were visually inspected.
Green marks are projected annotated keypoints, not necessarily externally visible physical joints;
the released Panda keypoint convention is retained. RGB alone does not label occlusion or contacts.

| Frame | Observation | Interpretation boundary |
| --- | --- | --- |
| 001033 | All seven predictions are within 5.68 px of their reference. Official ADD 0.01887, RANSAC/refined ADD 0.25812; rotation error 0.30° vs 81.51°. RANSAC uses six points. Its returned pose already has large error before refinement. | Gross keypoint mislabeling or missing points is not necessary for this solver failure. The final returned/refined inlier reprojection error is not guaranteed below RANSAC's original hypothesis threshold. |
| 001808 | Official ADD 0.31703 and rotation error 103.07°; robust ADD 0.01570 and rotation error 3.81°. Max keypoint error is 11.61 px. | A robust hypothesis can avoid a poor solution on the same observations; this does not prove all high errors are removable outliers. |
| 002583 | Two hand-side keypoints and the arm end lie outside the image; five in-frame detections. Both solvers give ADD 0.04618; their common-point oracle is near zero. | Visible-point localization/pose estimation remains sufficient to account for error relative to the supplied geometry. There is no in-frame missed detection and no demonstrated need to hallucinate hidden correspondences. |

Centered 3D point sets in 001033/001808 have smallest/largest singular-value ratios 0.0250/0.0164;
002583's five-point set has 0.00152. These are descriptive near-planarity cues, **not a measured
condition number of the pose problem or causal proof** of a specific local minimum.

The post hoc selector scores both saved poses on the same available predicted 2D points. It
chooses the lower reprojection MSE without consulting GT-2D/ADD, avoiding both largest failures.
It selects the robust candidate seven times (including floating-point near-ties). In 000775,
001550 and 003617, the candidate with lower reprojection error has higher reference ADD.
Thus reprojection score is not an oracle for pose accuracy. This control was devised after seeing
the two extreme cases and evaluated on the same frames; no held-out improvement is claimed.

### Verification and decision

Independent Docker verification passed 1,745 numeric comparisons; max difference 1.12e-11.
Checks cover original annotation identity, heatmap-peak extraction and resize mapping, direct
OpenCV reconstruction of official EPnP/refinement, RANSAC/inlier/refinement reproduction,
homogeneous-coordinate metric reconstruction, summaries, and nondegenerate synthetic pose/frame
composition. Forty-nine input files and 54 observation output files matched recorded hashes.
The post hoc score has a separate OpenCV projection check. No additional detector inference occurred.

**Observation-time decision: `refine`; Q14 `under_review`.** A simple candidate-selection control explains the two
dominant failures without learning. The remaining projection/pose ranking disagreements do not
yet establish a new principle, learnable residual, or action relevance. The next investment review
should compare a concrete action/calibration question with simpler pose estimation alternatives
and explicit deferral; generic residual training and automatic frame/view expansion are not selected.
This is a diagnostic result, not a rejection of Q14's broader learned joint-error question.

Compact machine-readable evidence: [outcome.json](outcome.json). Raw outputs:
`runs/q14/real_20260916_113000/{observe,verify,analyze}/`; full commands in `commands.jsonl`,
source snapshots in `*_source/`, dependency/source adaptation records in `observe/`.
`verify/contact_sheet.png` contains all cases; `observe/overlays/` retains full resolution.

```bash
python buildup/robotics/pilot_studies/q14-frame-errors/real/job.py verify real_20260916_113000 > logs/20260916_113800_q14_real_verify.log 2>&1
python buildup/robotics/pilot_studies/q14-frame-errors/real/job.py analyze real_20260916_113000 > logs/20260916_114200_q14_real_analyze.log 2>&1
```

Both ran in separate tmux sessions and exited 0. Each wrapper preserves container inspect/logs
and a cidfile. Existing run/output directories are not overwritten by the job launcher. For reruns,
use a fresh run ID and the pinned build or recorded image, preserving selected input IDs. Restoring
this result requires the raw outputs/compact outcome; rerunning inference additionally needs the
weights, YAML, selected images/annotations, source and image/rebuild. Source/full-archive URLs
and SHA256 are in `datasets/q14/dream/acquisition.json`. No external backup has been verified.

### Diagnostic correction and cleanup

The original unused `reprojection_all_mean_px` included sentinel positions for the two absent
predictions in 002583 (official/robust and their auxiliary diagnostics). This field is invalid
there. The runtime code now returns null when a full-point residual is unavailable and separately
reports the residual on available points. `correct.py` recomputed metrics from saved poses only:
672 checks passed; all poses, ADD, input-point residuals, oracle comparisons and post hoc selection
are unchanged. Original records/source remain intact; `correct/metrics.json` owns the corrected
primary solver diagnostics. Do not use the legacy full-point residual or its auxiliary values
for this frame. No detector inference was repeated.

```bash
python buildup/robotics/pilot_studies/q14-frame-errors/real/job.py correct real_20260916_113000 > logs/20260916_114700_q14_real_correct.log 2>&1
```

After output-manifest, exit-status, label, creation-command and exact-mount checks, only this
run's four exited containers (observe/verify/analyze/correct) were individually removed. Cidfiles,
inspect snapshots, container logs and source snapshots remain under the run root. Exact IDs and
checks: `runs/q14/real_20260916_113000/cleanup.json` and
`logs/20260916_115000_q14_real_cleanup.log`. No unrelated container, image, volume or cache was changed.

### Follow-up investment decision 2026-09-16

The subsequent [action-relevance review](../../../related_work/policy-geometry.md#q14-action-relevance-review-2026-09-16)
compared the three remaining cases, free-vector action semantics and existing pose/control methods.
Q14's current route is now [deferred](../../../questions/frame-error-propagation.md#investment-decision-and-re-entry).
The observation-time `refine` decision and numerical outcome remain unchanged. No new numerical
experiment, inference or container operation was performed for this review. These data contain no
paired learned action/calibration outputs; lower ADD does not establish lower action error.
