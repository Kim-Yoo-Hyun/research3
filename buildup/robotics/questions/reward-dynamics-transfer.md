# Reward Transfer Across Dynamics

Updated: 2026-09-08 · ID: Q15

## Status

`deferred`; meaningful learning question, but lower current resource fit than Q11/Q12.

## Facts

[DrEureka code](https://github.com/eureka-research/DrEureka) contains reward/DR search and
locomotion environments. No new reward search, LLM API call or RL training was performed here.

## Source Claims

[DrEureka](https://arxiv.org/html/2406.01967v1) automates reward and domain-randomization design
using language models and a reward-aware physics prior. Eureka in the user list supplies the
reward-generation lineage; generic automatic reward design is not a new question.

## Agent Inference

Rewards selected for fast nominal learning may induce different contact/motion strategies whose
advantages disappear with dynamics changes. The suspected issue is selection under a training
distribution, not raw reward-score comparability or another claim that DR improves robustness.

## Research Question Or Suspected Phenomenon

동일 task와 training budget에서 선택한 reward shaping의 우열이 dynamics shift에 따라
바뀌는가? 단순 reward normalization이나 potential-based shaping으로 설명되지 않는가?

## Significance

LLM-generated reward를 실제 adaptation/transfer에 사용할 때 무엇을 선택 기준으로 삼아야
하는지 다룬다. A robust-selection rule would require evidence beyond nominal success ranking.

## Current State Of The Art And Limitation

DrEureka, robust RL, adversarial DR and reward-search methods impose strong overlap. A reward
variant's raw return cannot be compared with another reward's scale as a task-performance metric.

## Evaluation Target

Common native task success under held-out dynamics, learning cost and contact-strategy diagnostics.
Use the same evaluator for all rewards. Simulation-only evidence supports sim-to-sim robustness,
not real-world transfer.

## Available Data / Code / Evaluator

Official search code is available; candidate smaller substrate is a few manipulation tasks with
published reward code and configurable dynamics. Porting to a new simulator changes the reproduction
claim. The original project's Isaac runtime is not presumed compatible or available.

## Simplest Baseline Or Counterexample

Human task reward; reward normalization; potential-based shaping; fixed uniform DR; nominal versus
held-out validation selection. Fix optimizer, interaction budget, training seeds and evaluator.

## Critical Assumptions

Reward-induced behavior must differ beyond scale and learning speed. Inspect published candidate
reward programs first. Short-training performance reversals may disappear at convergence; without
longer-budget checks, they do not establish a robustness principle.

## Feasibility Or Pilot Study

Start with a fixed small reward set rather than iterative LLM search. A factorial reward×dynamics
study needs independent training repeats and held-out parameter combinations. Estimate that cost
before creating a Docker study; no automatic reuse of existing host Isaac assets.

## Preliminary Success Criteria

An interpretable reward/strategy interaction survives scale, training-budget and DR controls.

## Expected Deliverable

Reward×dynamics outcome matrix and a cost-aware decision on whether to pursue robust reward selection.

## Timeline And Milestones

Source/cost audit estimate: 2--3 days. Training cost is unknown and is the reason for deferral.

## Interpretation Of A Negative Result

If normalization or fixed DR explains the effect, keep those simple rules and stop the new method.

## Resource Requirements

Several independent RL fits; materially more costly than codec/geometry diagnosis. No foundation
pretraining, paid model search or hardware experiment selected.

## Related-Work Overlap

High with Eureka/DrEureka and robust RL. Unlike Q8, this intervenes on training rewards and
strategies rather than measuring local recovery of an already frozen policy.

## User Decision Needed

No decision needed to keep this candidate deferred; compute allocation would follow a concrete plan.
