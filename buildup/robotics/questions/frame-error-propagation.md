# Coordinate-Frame Error Propagation

Updated: 2026-09-10 · ID: Q14

## Status

`exploratory`; reserve after the
[2026-09-10 Q12/Q13 reassessment](../related_work/policy-geometry.md#reserve-reassessment-2026-09-10).
No runtime or formal hypothesis selected. Cheap analytic checks alone do not make this the
highest-value learning question.

## Facts

Robot action and geometric observations can be expressed in different coordinate frames.
Pure changes of coordinates must transform all related quantities consistently; they are not
the same intervention as moving the physical camera or supplying an incorrect calibration.

## Source Claims

[CamVLA](https://arxiv.org/abs/2607.05396) predicts camera-frame actions and hand-eye transforms
and composes them into robot-base actions. [DP3](https://github.com/YanjieZe/3D-Diffusion-Policy)
provides a small point-cloud policy route. [OC-VLA §III](https://arxiv.org/html/2508.13103v1)
explicitly describes calibration-based action conversion, including delta-pose conjugation.
[EquAct](https://github.com/ZXP-S-works/EquAct) provides an equivariant policy's train/eval source.
Compatible checkpoint and matched frame variants remain unaudited; CamVLA's checked project page
still marks code as Coming Soon.

## Agent Inference

Apparent viewpoint robustness may combine visual generalization with error cancellation or
amplification in geometry/action conversion. Identifying which mechanism dominates could guide
representation learning, but a coordinate-convention correction alone is not a new method.

## Research Question Or Suspected Phenomenon

Camera/base/object-relative action 표현은 실제 관측 변화와 shared calibration error에
서로 다르게 반응하는가? 일관된 좌표변환과 단순 augmentation 뒤에도 차이가 남는가?

## Significance

Robot/camera 배치가 바뀌는 deployment에서 필요한 representation의 조건을 찾는다.

## Current State Of The Art And Limitation

Camera-centric, calibration-free and equivariant policies are already established directions.
The candidate concerns the interaction of shared versus independent errors; generic view-robustness
claims are occupied. Its scientific depth depends on a residue beyond analytic transforms.

## Evaluation Target

Action error in a common physical frame and paired task success. Separate coordinate relabeling,
physical view shift, depth noise and calibration error; keep task physics fixed.

## Available Data / Code / Evaluator

DP3-style simulator camera/depth generation is accessible as source. Matched frame variants,
calibration metadata and a small trained-policy bundle still need audit. CamVLA's abstract is
not proof of local runtime availability.

## Simplest Baseline Or Counterexample

Exact coordinate conversion; recalibration/oracle calibration; SE(3) data augmentation;
relative object-to-end-effector features. Equal backbone/data/training budget across frame variants.

## Critical Assumptions

First check algebraic error cancellation with synthetic coordinates. If transforms or relative
features explain the whole difference, stop before multi-model training. Residual must persist
when image information and controllability are matched.
Distinguish absolute poses, spatial/body-frame delta poses and vector increments before deriving
cancellation. A correct coordinate identity is not evidence that a learned policy is invariant to
physical camera movement, occlusion or erroneous calibration.

## Feasibility Or Pilot Study

Audit action semantics and transformations, then a factorized synthetic-coordinate check in
Docker. Only an unexplained effect justifies matched small-policy training. Changing object
orientation under gravity is not a pure coordinate change.

## Preliminary Success Criteria

A reproducible interaction beyond coordinate bookkeeping and augmentation identifies a distinct
learning requirement. Calibration-noise injection alone does not meet the criterion.

## Expected Deliverable

Error-source matrix, analytic controls and continuation/stop decision.

## Timeline And Milestones

Reserve source/algebra audit estimate: 1--3 days; no training schedule set.

## Interpretation Of A Negative Result

Record the simpler coordinate convention or calibration fix; discontinue the novel-method route.

## Resource Requirements

Small policy training only if needed; Docker-only. No new foundation model or real robot required.

## Related-Work Overlap

High with CamVLA, OC-VLA and equivariance. Distinct from Q3 simulator physics changes.

## User Decision Needed

None for this scoping record.
