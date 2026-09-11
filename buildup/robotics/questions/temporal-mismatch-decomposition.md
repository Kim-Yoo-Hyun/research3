# Temporal Mismatch Decomposition

Updated: 2026-09-04

## Status

`exploratory`

## Facts

- Asynchronous robot-policy inference can execute an old chunk prefix while computing a new chunk.
- No asynchronous policy or simulator has been run in this workspace.

## Source Claims

- [REMAC](https://arxiv.org/abs/2601.20130) separates inter-chunk discontinuity from
  intra-chunk perception--action inconsistency and trains a delay-aware correction.
- [Why Does Action Chunking Improve Behavioral Cloning Performance?](https://arxiv.org/abs/2608.02547)
  attributes chunking gains partly to delayed conditioning and implicit ensembling rather than
  temporal consistency alone.

## Agent Inference

Recent methods change training, sampling and execution together. A matched factorial intervention
on observation age, committed prefix and boundary composition may reveal which temporal mismatch
actually causes downstream degradation, but REMAC may already occupy this explanation.

## Research Question Or Suspected Phenomenon

For a frozen action-chunk policy, which independently controlled temporal mismatch—stale
observation, committed old-prefix execution or chunk-boundary composition—causes task failure as
delay increases?

## Significance

The answer would distinguish an inference-speed problem from a policy-state or action-composition
problem and determine whether retraining is necessary.

## Current State Of The Art And Limitation

REMAC directly identifies intra/inter-chunk inconsistency and proposes a learned solution. The
unverified difference is a policy-agnostic, matched-control decomposition that tests whether simple
execution controls explain the gain.

## Evaluation Target

- downstream success and recovery after controlled delay;
- trajectory discontinuity and state--action mismatch;
- interaction effects among observation age, prefix length and blending rule.

## Available Data / Code / Evaluator

REMAC publishes simulation code and reports a 12 GB GPU minimum. Exact checkpoint availability,
frozen-policy evaluation hooks and container reproducibility remain unverified.

## Simplest Baseline Or Counterexample

Blocking execution, zero-order hold, linear boundary blend and fresh-observation oracle. If one
simple execution rule removes the degradation, a learned temporal module is not justified.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| factors can be varied independently | changing delay necessarily changes all three | code/API audit |
| frozen policy has nontrivial delay failures | success is stable over supported delay | small delay sweep |
| factor effects generalize beyond one task | ordering is task-specific | two-task subset |

## Feasibility Or Pilot Study

Audit the official runtime for a checkpoint and independent intervention hooks. Only if they exist,
run one task with a small preregistered factorial grid.

## Preliminary Success Criteria

A reproducible interaction or dominant factor that is not explained by success-neutral trajectory
smoothing and changes downstream task success.

## Expected Deliverable

Temporal-factor response surface, matched execution baselines and a decision on whether a learned
policy change is necessary.

## Timeline And Milestones

Artifact audit, small delay grid, then Stage 7 decision; no training before the factorization is
shown to be measurable.

## Interpretation Of A Negative Result

If factors cannot be isolated or simple blending/holding removes the failure, discontinue this
question and treat latency handling as systems engineering.

## Resource Requirements

Public checkpoint, asynchronous simulator interface and short single-GPU evaluation in a new
project-specific container.

## Related-Work Overlap

`high`; REMAC directly owns the strongest causal explanation currently under consideration.

## User Decision Needed

None before the artifact audit.
