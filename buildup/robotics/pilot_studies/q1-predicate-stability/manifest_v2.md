# Q1 Success-Predicate Stability — Feasibility Protocol v2

Created: 2026-09-04

Superseded without execution by [protocol v3](manifest_v3.md) after the pairwise input audit.

## Status

`documented feasibility assessment`, `not executed`

이 protocol은 [`docs/buildup.md`](../../../../docs/buildup.md)의 Stage 5--7만 따른다.
목적은 가장 중요한 operational uncertainty를 줄이는 것이며 full experiment나 method
평가가 아니다.

## Research Question

동일한 manipulation rollout에 의미상 방어 가능한 success-predicate variants를 적용할
때 policy pair의 ordering이 달라지는가?

## Critical Operational Assumption

같은 task, observation/action interface와 evaluator version에서 비교 가능한 policy 또는
rollout input이 있고, 각 trajectory가 predicate constituent를 재계산할 state를 보존한다.

Disconfirming observation:

- fair pairwise comparison을 구성할 수 없다;
- immutable state 또는 exact replay로 constituent margin을 복원할 수 없다;
- predicate variant를 outcome과 독립적으로 정의할 수 없다.

## Current Feasibility Evidence

- ManiSkill3는 raw trajectory의 initial state, action과 seed를 보존하고 environment-state
  replay를 지원한다.
- `PickCube-v1`과 `PlugCharger-v1` evaluator에는 distance, angle 또는 static condition의
  constituent가 있다.
- Comparable policy/rollout input은 아직 선택하지 않았다.

## Input Audit

1. ManiSkill3 source tag/full SHA, dependency, task source와 license를 기록한다.
2. 동일 evaluator와 action interface에서 비교 가능한 policy/rollout source가 있는지
   확인한다.
3. 이 질문은 pairwise ordering을 측정하므로 최소 empirical input은 두 policy/rollout
   source다. 이는 question-specific measurement requirement이며 일반 buildup 기준이 아니다.
4. Public pretrained checkpoint만 허용하는 별도 규칙은 두지 않는다. Official public
   implementation으로 재현 가능하게 생성한 frozen rollout도 후보가 될 수 있다.
5. 실제 input이 정해진 뒤 execution 전에 policy 수, trajectory 수, seed, predicate grid,
   metric과 disconfirmation rule을 새 version에 고정한다.

## Candidate Predicate Axes

현재 단계에서는 exact grid를 고정하지 않는다. Source code로 정당화할 수 있는 다음 axis가
실제 selected task에서 reconstructable한지만 확인한다.

- terminal geometric distance or angle threshold;
- robot/object static condition;
- once-achieved, terminal 또는 consecutive-step persistence.

Exact values는 artifact 확인 후 outcome을 보기 전에 고정한다.

## Simplest Baseline Or Counterexample

1. official binary success;
2. continuous signed geometric/static margin;
3. once/end/persistence report;
4. paired uncertainty interval over the selected trajectories.

모든 합리적인 variants에서 ordering이 같거나 continuous report가 apparent reversal을
설명하면 suspected phenomenon은 지지되지 않는다.

## Feasibility Output

- source/checkpoint-or-rollout/schema table;
- reconstructable evaluator-field table;
- exact next pilot input/output/metric proposal;
- `discontinue / refine / reformulate / repeat feasibility study / select for hypothesis
  formulation` 중 하나의 Stage 7 decision.

## Milestones

1. source/license/schema audit;
2. comparable pairwise input audit;
3. 가능하면 small subset 또는 one-case relabeling counterexample protocol 작성;
4. evidence에 따른 Stage 7 decision.

## Environment Boundary

External method를 실제 재현하거나 평가할 때만 새 project-specific Docker environment를
만든다. 기존 Docker/Isaac image, container, volume, cache와 simulator installation은
사용·수정·삭제하지 않는다. 이 문서 단계에서는 외부 artifact를 실행하지 않는다.
