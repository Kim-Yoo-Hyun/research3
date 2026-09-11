# Success-Predicate Stability

Updated: 2026-09-08

## Status

`discontinued`

2026-09-08 frozen v3의 CUDA 실행과 독립 검증을 완료했다. 8쌍 초기 state가 정확히
일치했고 16 trajectories / 96 labels 및 800 official step labels를 검증했다.
모든 여섯 조건에서 PPO-EE 4/8, PPO-Joint 8/8로 label/rank 변화는 없었다.
[Study evidence](../pilot_studies/q1-predicate-stability/README.md#verified-results)를 따른다.

V3 직후의 `refine`에 이어 [bounded refinement audit](../related_work/q1-artifact-schema.md#bounded-refinement-audit--2026-09-08)를
완료했다. 최신 [Stage 7 decision](../../selection.md#q1--discontinue-2026-09-08)은
현재 formulation의 `discontinue`다. 아래 질문과 계획은 provenance로 보존하며 실행 queue가 아니다.
종료 요약은 [literature/README.md](../../../literature/README.md)가 소유한다.

## Facts

- 검토한 manipulation evaluator는 step별 state predicate를 계산하고 once/end 같은
  temporal aggregation으로 episode success를 보고한다.
- VLA-Arena, ManiSkill3, LIBERO 계열 evaluation에는 공개 task와 evaluator가 있다.
- Q1 frozen CUDA v3과 Q8의 별도 CPU-physics fixture를 모두 실행·검증했다.

## Source Claims

- [VLA-Arena](https://vla-arena.github.io/)는 170개 task를 Safety, Distractor,
  Extrapolation, Long Horizon 조건과 L0--L2 difficulty로 구성한다.
- [SafeVLA-Bench](https://safevla.org/)는 LIBERO와 RoboCasa-365 rollout에서 native
  success와 별도로 safety-aware trajectory metric을 평가한다.
- [SIMPLER](https://github.com/simpler-env/SimplerEnv)는 simulation policy ranking과
  real-world performance의 상관을 MMRV와 Pearson correlation으로 비교한다.

## Agent Inference

동일한 물리적 rollout도 predicate tolerance, terminal window 또는 conjunction
구성에 따라 success label이 달라질 수 있다. 이 변화가 모든 policy에 균등하지
않다면 benchmark의 scalar success rate보다 **policy ranking stability**가 더 먼저
검증돼야 한다. 이는 현재까지 확인한 direct prior의 핵심 질문과 같다고 확정할 수
없으며, exact overlap audit가 필요하다.

## Research Question Or Suspected Phenomenon

의미상 같은 task를 나타내는 합리적인 success-predicate family 안에서 manipulation
policy의 순위와 결론은 얼마나 안정적인가? Rank reversal이 있다면 continuous
geometric margin과 temporal persistence만 보고해도 그 불안정성을 설명할 수 있는가?

## Significance

Benchmark 결론이 evaluator의 한 threshold에 의존하면 policy improvement와
generalization claim을 해석하기 어렵다. 반대로 합리적인 predicate family에서
ranking이 안정적이면 이 방향은 빠르게 종료할 수 있다.

## Current State Of The Art And Limitation

현재 benchmark는 task success와 일부 safety/robustness metric을 제공하지만,
predicate specification 자체에 대한 ranking sensitivity가 표준 보고 항목인지는
확인되지 않았다. SafeVLA-Bench와 SIMPLER가 각각 metric 확장과 ranking validity를
다루므로 가장 가까운 충돌 후보다.

## Evaluation Target

- primary: policy-pair rank reversal rate over a preregistered predicate family
- secondary: Kendall's tau, bootstrap rank confidence interval, success-rate range
- diagnosis: terminal-state margin, persistence window와 reversal의 관계
- denominator: evaluated policy pairs × task families × frozen predicate variants

## Available Data / Code / Evaluator

- first route: ManiSkill3 public tasks, demonstrations, baselines and task evaluators
- second route: VLA-Arena or public LIBERO/SafeVLA-Bench rollouts, subject to schema audit
- evaluator input: immutable trajectory/state log; policy rerun 없이 label recomputation이
  가능한 route를 우선한다.
- [Artifact/schema audit](../related_work/q1-artifact-schema.md)에서 ManiSkill3의 exact
  state replay 구조와 PickCube evaluator constituent를 확인했다. Initial feasibility
  input으로 public `PickCube-v1` PPO checkpoint 두 개를 선택했다. 두 artifact는 state
  observation과 policy code를 공유하지만 control mode가 다르므로 claim은 해당 named
  artifacts의 evaluator stability로 제한한다.

## Simplest Baseline Or Counterexample

1. Official binary success predicate 하나만 사용한다.
2. Raw terminal geometric margin을 함께 보고한다.
3. Tolerance sweep와 bootstrap confidence interval만 적용한다.
4. 모든 policy가 같은 방향·크기로 변하면 candidate의 핵심 phenomenon은 없다.

## Critical Assumptions

| Assumption | Disconfirming observation | Cheaper measurement |
| --- | --- | --- |
| Public rollout이 predicate 재계산에 필요한 state를 보존한다. | RGB/action만 있고 object/robot state가 없다. | dataset schema와 evaluator code audit |
| 합리적인 predicate variants를 결과 전에 정의할 수 있다. | variant가 임의적이거나 task semantics를 바꾼다. | task 2개에 대한 specification review |
| policy별 terminal-margin distribution이 다르다. | 모든 policy 분포와 ranking이 안정적이다. | 2 policy × 1 task의 small stored subset |

## Feasibility Or Pilot Study

[Small feasibility study v3](../pilot_studies/q1-predicate-stability/manifest_v3.md)은
`PickCube-v1`, public PPO checkpoint 두 개, policy당 official-default 8개 trajectory와
3 distance thresholds × 2 temporal aggregations을 고정한다. 이는 총 16개 rollout과
96개 episode-predicate label의 small-subset study이며 confirmatory claim을 허용하지 않는다.

## Preliminary Success Criteria

- 최소 한 task family에서 bootstrap uncertainty를 넘는 policy-pair rank reversal이
  관찰된다.
- reversal이 임의의 단일 outlier가 아니라 preregistered tolerance interval의
  연속 구간에서 유지된다.
- raw margin 또는 persistence 같은 simple report가 reversal을 완전히 해소하는지도
  같이 판정한다.

## Expected Deliverable

Predicate sensitivity curve, policy ranking matrix, reversal taxonomy와 evaluator
reporting recommendation의 최소 버전.

## Timeline And Milestones

- completed: schema/evaluator audit
- completed: source pin, license와 comparable pairwise input 확인
- completed: exact small-subset input/output/metric/disconfirmation protocol v3 고정
- completed: 새 project-specific CUDA Docker에서 frozen v3 실행·독립 검증
- completed: no label/rank changes에 따라 Stage 7 `refine`
- completed: task semantics와 public artifact metadata의 bounded refinement audit; Stage 7 `discontinue`

## Interpretation Of A Negative Result

Frozen variants에서 label/ranking이 안정적인 현재 route는 확대하지 않는다. Eight episodes
per policy의 negative result를 benchmark 전체의 ranking 안정성으로 일반화하지 않는다.
정당화 가능한 informative refinement가 없으면 candidate를 discontinue한다.

## Resource Requirements

Stored state trajectory가 있으면 CPU 중심으로 가능하다. Policy rerun이 필요하면
GPU 종류와 inference budget 확인이 필요하며, annotation과 hardware는 불필요하다.

## Related-Work Overlap

`medium`. [Focused audit](../related_work/q1-success-predicate.md)에서 benchmark validity,
fine-grained metric과 post-hoc safety evaluation prior는 확인했지만, 동일 rollout에
semantically equivalent success-predicate family를 적용해 policy rank reversal을
측정한 direct prior는 확인하지 못했다. 이는 exact novelty 확정이 아니다.

## User Decision Needed

현재 종료 결정에 추가 사용자 판단은 필요하지 않다. 새 실행은 선택하지 않았다.
