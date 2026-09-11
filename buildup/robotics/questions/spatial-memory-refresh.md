# Spatial-Memory Refresh

Updated: 2026-09-04

## Status

`exploratory`

## Facts

- Persistent spatial memory can become inconsistent when objects move or perception is distorted.
- No scene-graph system or embodied planning benchmark has been executed in this workspace.

## Source Claims

- RSS 2026 [Multi-modal Interaction Field](https://www.roboticsproceedings.org/rss22/p023.html)
  detects map--reality discrepancy and locally updates obsolete memory for dynamic humanoid
  navigation.
- ICLR 2025 [PARTNR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a3cf318fbeec1126da21e9185ae9908c-Abstract-Conference.html)
  provides 100,000 language tasks across 60 houses for embodied human--robot planning.

## Agent Inference

Learned memory evolution may owe its benefit to increased sensing/update budget rather than its
representation. Fixed-budget comparison to periodic and change-threshold refresh is needed before a
new memory module is justified.

## Research Question Or Suspected Phenomenon

Under the same sensing and update budget, when do periodic, time-to-live, geometric-change and
learned discrepancy triggers differ in stale-belief duration and downstream plan completion?

## Significance

The answer would clarify whether dynamic embodied memory needs learned update logic or merely an
explicit freshness contract.

## Current State Of The Art And Limitation

MIF directly addresses obsolete memory with a learned multi-modal discrepancy. The unverified
residue is budget-matched trigger comparison across task-relevant versus irrelevant changes.

## Evaluation Target

Plan completion, stale-belief duration, unnecessary refresh count and compute/sensor queries under
controlled object relocations.

## Available Data / Code / Evaluator

PARTNR has a public benchmark route; MIF's official proceedings page did not expose code in this
scan. Whether either supports controlled memory-update policies is unverified.

## Simplest Baseline Or Counterexample

Always refresh, never refresh, fixed period, time-to-live and geometric change threshold. If a
simple trigger matches the learned approach, no new learned memory mechanism is needed.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| memory updates can be externally controlled | update is inseparable from the policy | API audit |
| stale facts affect downstream decisions | planner ignores changed entries | scripted relocation |
| update budget can be matched | methods expose incomparable sensors | information audit |

## Feasibility Or Pilot Study

Use one scripted embodied task with relevant and irrelevant object relocations and compare always,
never and TTL refresh before any learned trigger.

## Preliminary Success Criteria

A nontrivial budget--staleness tradeoff in which task relevance changes the best simple refresh
policy.

## Expected Deliverable

Refresh-budget curves, relocation taxonomy and a decision on whether task-conditioned updating is
needed.

## Timeline And Milestones

Artifact/API audit, scripted relocation subset, simple triggers, Stage 7 decision.

## Interpretation Of A Negative Result

If always refresh is cheap or TTL/change threshold dominates, discontinue the learned-memory
question.

## Resource Requirements

Public embodied simulator and planner interface; likely CPU/single-GPU, with substantial setup risk.

## Related-Work Overlap

`high`; MIF directly owns discrepancy-triggered update in dynamic environments.

## User Decision Needed

None before artifact review.
