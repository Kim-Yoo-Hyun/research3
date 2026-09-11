# Failure-Source Generalization

Updated: 2026-09-04

## Status

`exploratory`

## Facts

- Failure datasets may contain policy-generated natural failures, scripted perturbations or
  counterfactual constructions.
- No failure dataset or detector has been downloaded or run in this workspace.

## Source Claims

- [FailBench](https://arxiv.org/abs/2609.03611) aggregates 2,197 attempts from 14 public sources,
  reports 75% naturally occurring failures and finds poor cross-source reliability of specialist
  VLM detectors.
- [FAIL-Detect](https://www.roboticsproceedings.org/rss21/p073.html) learns runtime failure
  detection without failure training data.

## Agent Inference

Constructed failures can make evaluation partly identify a generation procedure. A detector ranking
measured on injected failures may therefore fail to predict ranking on naturally occurring failures
even after task and visible evidence are matched.

## Research Question Or Suspected Phenomenon

Does relative detector performance on constructed robot failures predict relative performance on
naturally occurring failures under matched task, outcome evidence and failure severity?

## Significance

Failure benchmarks and synthetic-data pipelines are useful only if their conclusions transfer to
the failures encountered during ordinary deployment.

## Current State Of The Art And Limitation

FailBench exposes cross-source failures and may already contain much of the needed analysis. Its
exact constructed-versus-natural split evaluation and public artifact route must be checked before
this becomes a distinct question.

## Evaluation Target

- detector rank correlation and pairwise rank reversal across failure sources;
- balanced accuracy within matched task/evidence strata;
- source-only predictability as a construction-artifact diagnostic.

## Available Data / Code / Evaluator

FailBench claims a common schema over public sources, but its arXiv page did not expose an official
code/data release during this scan. Source datasets are individually public with heterogeneous
licenses and schemas.

## Simplest Baseline Or Counterexample

Majority label, source-ID classifier, general-purpose VLM and one specialist detector. If matching
observable evidence removes source effects, the broad candidate is unsupported.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| source type is identifiable and sufficiently populated | metadata cannot separate construction | full-paper schema audit |
| matching leaves comparable examples | task/evidence strata have no overlap | contingency table |
| detector rankings differ by source | rankings remain stable with uncertainty | reported-table reanalysis |

## Feasibility Or Pilot Study

First reproduce the paper's source × label × evidence counts from a released manifest. If available,
evaluate two cheap detectors on one matched natural/constructed stratum.

## Preliminary Success Criteria

Stable detector rank reversal or a large source-conditioned performance gap that cannot be
explained by class balance and visible-evidence category.

## Expected Deliverable

Failure-source transfer matrix and guidance on when constructed failure benchmarks support
deployment claims.

## Timeline And Milestones

Full-paper and release audit, one matched stratum, then Stage 7 decision.

## Interpretation Of A Negative Result

If rankings transfer after matching or FailBench already reports the exact result, discontinue the
candidate.

## Resource Requirements

Public row-level manifest and videos/images; CPU preprocessing and limited inference. No simulator
or hardware is required for the first study.

## Related-Work Overlap

`high / unresolved`; FailBench was released one day before this scan and needs exact-paper audit.

## User Decision Needed

None before artifact availability is known.
