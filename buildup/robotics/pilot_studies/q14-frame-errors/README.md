# Q14 Prediction Error Dependence

Updated: 2026-09-16

## Purpose and status

`completed; verified`; exploratory first observation for
[Q14](../../questions/frame-error-propagation.md). Measure how action/rotation prediction
dependence changes composed action error at fixed ground truth. Compare a closed-form
geometric estimator with a two-head regressor and a direct base-action regressor.
This is a known-scale planar keypoint proxy, not a VLA reproduction or robot rollout.

This record is written before numeric results. No positive effect, detrimental oracle
replacement, or new method is required. The question record owns motivation and prior work;
this folder owns exact configuration, execution, verification and observations.

The pre-execution design below was retained. [Results](#results-2026-09-16) distinguish
the planned comparison from the subsequent first-order geometric diagnosis.

After the [real-keypoint follow-up](real/README.md), the
[investment review](../../questions/frame-error-propagation.md#investment-decision-and-re-entry)
deferred Q14's current route. This completed study and its original interpretation remain preserved.

## Inputs and bounded comparison

- Generate 8,192 training scenes with seed 20260916. End-effector direction is uniform on
  the circle and radius uniform [0.5, 1]; base action and image offset each uniform [-0.5, 0.5]^2.
  Goal equals end-effector plus action. Camera angle is uniform [-60, 60] degrees.
- Input is the three labeled 2D keypoints (origin, end-effector, goal) and exact base-frame
  end-effector position. Unit scale and labels are known. Independent Gaussian noise with
  sigma 0.01 is added to each keypoint coordinate, once for the fixed training pool.
  True rotation and world goal are supervision/evaluation data only.
- Generate eight new layouts using seed 20260917; observe each at 0 and 90 degrees.
  Use 64 independent noise observations per scene (seed 20260918), plus one noiseless
  competence/geometry control. All estimators receive the same observations.
- Two-head MLP: 8 -> 64 Tanh -> 64 Tanh -> 4; action coordinates plus (cos, sin).
  Loss is mean coordinate MSE for action plus mean coordinate MSE for raw (cos, sin).
  Convert the rotation head by atan2; norm <= 1e-8 is invalid and stops the comparison.
- Direct MLP: same hidden layers, output 2D base action, coordinate MSE loss.
  Both use Adam, learning rate 0.003, batch 128, exactly 1,000 updates, seeds 0 and 1.
  Shared data/minibatch sequences and update budget; different output-head parameter counts.
  **Maximum four fits.** No hyperparameter search, early stopping or composition loss.
- Geometric rotation is angle(e) - angle(u_E-u_O); action is u_G-u_E. Direction norm
  <= 1e-8 is invalid. A zero action supplies an elementary competence reference.

For every fixed scene, compare original pairs with all 64 x 64 rotation/action combinations
(empirical product of marginals, including diagonal pairs), and oracle rotation replacement.
The product is an offline diagnostic, not a physically executed intervention. It preserves
each head's empirical marginal but does not create independent tasks or additional data.
Report per-scene vector squared-error means (sum over coordinates), component norm terms,
cross term, its bias/centered split, rotation angular MSE, oracle MSE and direct MSE.
Noise-free controls are reported separately. No CI or statistical significance claim is planned.

## Verification and interpretation

The verifier independently reconstructs camera geometry and scalar SO(2) action composition
from saved arrays, checks every scene's original/product metrics, both norm-term marginal
invariances, cross-term decomposition, and oracle replacement identity. It checks parameter
counts, four fit records, saved checkpoint predictions and train/evaluation separation.
Analytic noiseless and deliberately cancelling rotations are implementation controls only.
No new learning occurs during verification.

If geometry exhibits the effect too, shared measurement noise is a sufficient mechanism;
it does not prove learned representations unnecessary in real images. If MLPs are worse
than elementary controls, treat that as baseline competence evidence. No effect or weak
regression does not falsify all of Q14. Interpret size/sign by scene and camera angle;
90 degrees means extrapolation for this training distribution only.

## Results 2026-09-16

Facts: all four fits completed at their original 1,000-update budget. Eight new layouts at
two angles produced 1,024 noisy and 16 noiseless observations, shared by five estimators
(5,200 prediction rows). No hyperparameters, labels or sampling were revised after results.
Numeric execution took 1.78 seconds excluding image build/container startup; this is a
tiny regression proxy. Parameter counts are 4,996 (joint) and 4,866 (direct).

Each table entry is the mean over eight fixed scenes at the stated angle. Metric is mean
**squared vector error**, summed over coordinates, in synthetic coordinate units squared.
Positive delta means original pairing is better than the empirical product comparison.
These are descriptive means, not CI-backed effects or task success rates.

| estimator | camera angle | original MSE | product MSE − original MSE | oracle-rotation MSE |
| --- | ---: | ---: | ---: | ---: |
| Geometric | 0° | 0.00047188 | −0.00000033 | 0.00039520 |
| Geometric | 90° | 0.00048609 | +0.00001496 | 0.00041741 |
| Joint MLP seed 0 | 0° | 0.00113802 | −0.00000354 | 0.00102102 |
| Joint MLP seed 1 | 0° | 0.00114660 | −0.00000466 | 0.00080513 |
| Joint MLP seed 0 | 90° | 0.03168129 | +0.00000269 | 0.00180379 |
| Joint MLP seed 1 | 90° | 0.02923856 | −0.00000297 | 0.00290947 |

Direct base-action MLP means are 0.00292405 / 0.00411951 at 0°, and
0.12020168 / 0.10354255 at 90° (seeds 0 / 1). Zero action is 0.16738509 at both angles.
All MLP group means beat zero, but the simple geometric estimator has the lowest group mean
among the implementable estimators. Oracle rotation is privileged information, not an
implementable baseline. No conclusion about better-tuned or other architectures follows.

**Scene effects remain despite small signed averages.** Geometric pairing helps four and
hurts four scenes at each angle. For the learned heads, the mean signed product difference
is −0.31% / −0.41% of original MSE at 0°, and +0.0085% / −0.0102% at 90°. Mean absolute
scene differences are about 8.5e-5 / 9.9e-5 at 0° and 2.7e-5 / 4.5e-5 at 90°.
Do not call this equivalence or absence of conditional dependence. Oracle improves the group
mean in all six rows, but worsens some individual scenes; the scene CSV retains those cases.

### Post hoc geometric explanation

After reading the first verified results, derive the geometric estimator's first-order
shared-noise term. Let q=Rᵀe, d=g−e, a=Rᵀd, and J be 90° counterclockwise rotation.

```text
delta_theta ≈ −(Jq)ᵀ(eta_E − eta_O) / ||e||²
delta_a = eta_G − eta_E
E[2 GᵀA] ≈ 2 sigma² (eᵀd) / ||e||²
E[MSE_product − MSE_paired] ≈ −(1 − 1/N) 2 sigma² (eᵀd) / ||e||²
```

The factor (1−1/N), N=64, accounts for diagonal original pairs included in the empirical
product. Toward-origin versus away-from-origin action components therefore predict opposite
signs under this construction. The sign predicted by the population first-order expression
matches 16/16 observed geometric comparisons; these are **eight layouts at two angles**.
Using realized input noise in the same linearization also matches all signs; its maximum
absolute discrepancy from the exact measured delta is 2.94e-6. This is an approximate,
post hoc explanatory calculation, not independent confirmation or a new covariance principle.

At 0°, learned and geometric delta signs agree on 7/8 scenes in each seed; at 90°, only
4/8 and 6/8 agree. Thus geometry supplies a mechanism for the sign-changing effect but
does not establish that every learned residual is explained. Learned cross terms also include
substantial conditional bias products; a large negative cross term alone is not evidence
of beneficial stochastic dependence.

For the joint MLP at 90°, the rotation contribution G² is 0.03050 / 0.02725, against total
MSE 0.03168 / 0.02924. Noiseless MSE is still 0.03082 / 0.02840, and oracle rotation sharply
reduces mean error. This points primarily to the component's angle-extrapolation error in
this proxy, not a large average benefit destroyed by recombination.

### Verification and decision

Independent complex-coordinate reconstruction passed 2,926 numeric comparisons across
all 96 composition and 96 direct/zero metric records. Maximum discrepancy was 7.49e-16.
All saved checkpoint outputs matched exactly; input geometry, fixed-scene GT, no shared
training/evaluation input rows, marginal norm invariance, error decomposition and oracle
identity passed. Noiseless geometric action error is below 1.2e-32. The intentionally
cancelling analytic control is explicitly separate from learned outputs.

Run and verification exited 0. The first post hoc analysis failed only when serializing
NumPy integer counts; the corrected analysis exited 0 without training again. Source,
failure log, inputs and original predictions are retained. [outcome.json](outcome.json)
contains verified summaries, post hoc scope and preservation hashes; full scene metrics
are under `runs/q14/20260916_103919/result/` and `analysis_v2/scenes.csv`.

Agent inference: this observation lowers the priority of a new correction module motivated
only by beneficial learned error dependence. The proxy favors known geometry and exposes
angle extrapolation in the regressor. Keep Q14 `under_review` with a `refine` decision:
compare a geometry-based prediction plus learned residual against simpler calibration/input
representations in settings where the geometric assumptions can actually fail. This is a
tentative direction for the next value/prior review, not authorization for automatic extra
fits or proof of a useful residual method. A meaningful next contrast must explain what the
strong geometric baseline misses. Formal hypothesis and paper promotion remain unselected.

Continuation update, 2026-09-16: the geometry/learning review and subsequent
[24-frame real-keypoint observation](real/README.md#results-2026-09-16) are complete and verified.
Q14 is now `under_review`/`refine`. Shared-detection PnP/RANSAC, oracle-2D controls and a post hoc
saved-pose selector diagnose measurement and geometry limitations; they do not measure VLA
joint-head errors. No residual training is selected. The continuation does not change this completed
synthetic study's outcomes, source snapshots or cleanup record. `real/` owns the new run and recovery.

## Environment and recovery

Fresh CPU image `research3-q14-frame-errors:v1`; public pinned Python base, pinned CPU PyTorch
and NumPy dependencies. No pre-existing research/simulator image is used. Build uses `--pull
--no-cache`. Runtime: 2 CPUs, 3 GiB RAM, one Torch/BLAS thread, no GPU, no network, read-only
root/source, explicit writable output. Source is local workspace code; exact source bytes
and parent Git commit are retained with each run because the worktree is uncommitted.

- Recipe/config/code: this directory, including `requirements.lock` and `config.json`.
- Derived inputs, predictions, four checkpoints, metrics, dependency versions, source snapshot,
  manifest and verification: fresh ignored `runs/q14/<run_id>/`.
- Compact outcome: `outcome.json` here after verification; raw rows stay under `runs/`.
- Timestamped build/run/verification logs and exit files: `logs/`.
- Results preservation requires compact outcome plus ignored predictions/inputs/metrics and
  verification. Reanalysis needs these arrays and source; resume needs checkpoints/image too.
  Full reproduction needs the pinned public packages/base and saved source/config/seeds.
  No external backup has been verified, so do not delete result payloads.
- Before removing only this run's unnecessary containers, preserve inspect/logs, verify exit
  status and match creation records, workspace mounts and commands. Never delete by prefix.

## Commands and jobs

Working directory: `/home/yoohyun/research3`. Exact launch commands, image identity and job
status are appended when launched. Long build/run jobs use tmux and timestamped logs.

Build launched: `20260916_103404`; session `research3_q14_build_20260916_103404`; status `launched`.
Log/exit prefix: `logs/20260916_103404_q14_build`. Expected image: `research3-q14-frame-errors:v1`.

```bash
docker build --pull --no-cache -t research3-q14-frame-errors:v1 /home/yoohyun/research3/buildup/robotics/pilot_studies/q14-frame-errors
```

Build `20260916_103404`: `completed`, exit 0.
Image ID: `sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33`. Parent Git commit: `fdb730c37d166f3f54cec0fcba4af1fb710a9743`; dirty source snapshot/hash manifest retained under `runs/q14/20260916_103919/`.

Run/verification launched: `20260916_103919`; session `research3_q14_20260916_103919`; status `launched`.
Expected: result arrays, four checkpoints, metrics and `verification.json`; inspect/status under same output root.

run: `research3-q14-run-20260916_103919`; log `logs/20260916_103919_q14_run.log`; exit file replaces `.log` with `.exit`.

```bash
timeout 3600s docker run --name research3-q14-run-20260916_103919 --cidfile /home/yoohyun/research3/runs/q14/20260916_103919/run.cid --label research3.workspace=/home/yoohyun/research3 --label research3.study=q14-frame-errors --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 3g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw,nosuid,size=64m --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919/source,dst=/study,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919,dst=/output --env Q14_IMAGE=sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 --env Q14_PARENT_COMMIT=fdb730c37d166f3f54cec0fcba4af1fb710a9743 sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 /study/observe.py --config /study/config.json --output /output/result
```

verify: `research3-q14-verify-20260916_103919`; log `logs/20260916_103919_q14_verify.log`; exit file replaces `.log` with `.exit`.

```bash
timeout 600s docker run --name research3-q14-verify-20260916_103919 --cidfile /home/yoohyun/research3/runs/q14/20260916_103919/verify.cid --label research3.workspace=/home/yoohyun/research3 --label research3.study=q14-frame-errors --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 3g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw,nosuid,size=64m --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919/source,dst=/study,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919,dst=/output --env Q14_IMAGE=sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 --env Q14_PARENT_COMMIT=fdb730c37d166f3f54cec0fcba4af1fb710a9743 --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919/result,dst=/result,readonly sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 /study/verify.py --result /result --output /output/verification.json
```

Run and independent verification `20260916_103919`: `completed`, both exit 0.

Post hoc analysis: after reading the verified mean errors, inspect scene-level signs and
compare geometric dependence with a first-order shared-keypoint-noise calculation.
This adds no fits and changes no predictions/config/metrics. Original snapshot is preserved;
new code is under `runs/q14/20260916_103919/analysis_source/`.
Analysis launched: `20260916_104300`; log `logs/20260916_104300_q14_analysis.log`.

```bash
timeout 600s docker run --name research3-q14-analysis-20260916_104300 --cidfile /home/yoohyun/research3/runs/q14/20260916_103919/analysis.cid --label research3.workspace=/home/yoohyun/research3 --label research3.study=q14-frame-errors --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 3g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw,nosuid,size=64m --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919/analysis_source,dst=/study,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919,dst=/output --env Q14_IMAGE=sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 --env Q14_PARENT_COMMIT=fdb730c37d166f3f54cec0fcba4af1fb710a9743 --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919/result,dst=/result,readonly sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 /study/analyze.py --result /result --output /output/analysis
```

Analysis `20260916_104300`: `failed`, exit 1; NumPy integer sign counts were not JSON
serializable. This was output serialization, not a model/metric failure. Cast counts to
Python int and rerun diagnosis into a fresh `analysis_v2/` directory; original outputs and
failed source/log remain preserved. No training repeats.

Corrected analysis launched: `20260916_104337`; log `logs/20260916_104337_q14_analysis.log`.

```bash
timeout 600s docker run --name research3-q14-analysis-20260916_104337 --cidfile /home/yoohyun/research3/runs/q14/20260916_103919/analysis_v2.cid --label research3.workspace=/home/yoohyun/research3 --label research3.study=q14-frame-errors --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 3g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw,nosuid,size=64m --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919/analysis_v2_source,dst=/study,readonly --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919,dst=/output --env Q14_IMAGE=sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 --env Q14_PARENT_COMMIT=fdb730c37d166f3f54cec0fcba4af1fb710a9743 --mount type=bind,src=/home/yoohyun/research3/runs/q14/20260916_103919/result,dst=/result,readonly sha256:24d9be0793b5e9e663b0ab675ca6a768358fd615f460b63706a9f09e0c8d8f33 /study/analyze.py --result /result --output /output/analysis_v2
```

## Container cleanup 2026-09-16

Corrected analysis `20260916_104337`: `completed`, exit 0. After preserving input/output
manifests, source snapshots, inspect metadata, all logs and compact outcome, removed only
the four containers created by this study. Ownership was checked against CID/creation
records, exact commands, labels, workspace mounts and exited state; names alone were not used.

- `research3-q14-run-20260916_103919` (`99cf78346522`), exit 0.
- `research3-q14-verify-20260916_103919` (`8c29a9edd4cb`), exit 0.
- `research3-q14-analysis-20260916_104300` (`575266aa2711`), exit 1.
- `research3-q14-analysis-20260916_104337` (`a9b7907305b4`), exit 0.

Cleanup log: `logs/20260916_104600_q14_cleanup.log`; detailed record:
`runs/q14/20260916_103919/cleanup.json`. Image, source, checkpoints and raw results remain.
Other containers/images/volumes/build caches were not changed.

## Docker cleanup review 2026-09-16

Image/container 삭제 후보와 재개·전체 재현에 미치는 영향은
[repository cleanup review](../../../../docs/reproducibility.md#docker-cleanup-review-2026-09-16)가 소유한다.
이번 검토는 읽기 전용이며 Docker 자산을 삭제하지 않았다. 기존 실행/보존 기록은 유지한다.
