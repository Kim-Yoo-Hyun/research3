# CD3 Temporal Outcome Semantics

Updated: 2026-09-04

## Status

`deferred`

## Facts

- Q1 Success-Predicate Stability가 이미 success tolerance와 temporal persistence를
  manipulation에서 조사하는 active candidate다.
- 이 workspace에서는 non-robot sequential benchmark trace를 실행하지 않았다.

## Source Claims

- ManiSkill의 [evaluation guide](https://maniskill.readthedocs.io/en/latest/user_guide/learning_from_demos/setup.html)는
  `success_once`와 `success_at_end`를 별도로 기록하며 learning-from-demonstrations에서는
  일반적으로 `success_once`를 보고한다고 설명한다.
- ManiSkill [custom-task tutorial](https://maniskill.readthedocs.io/en/latest/user_guide/tutorials/custom_tasks/intro.html)은
  evaluator가 per-step `success`를 반환하는 구조를 보인다.

## Agent Inference

같은 rollout의 first-hit, terminal과 sustained success는 서로 다른 behavior property를
측정하며, policy/system별 post-success regression이 다르면 순위를 바꿀 수 있다.

## Research Question Or Suspected Phenomenon

First-hit, terminal, dwell-time과 post-success-regression 정의가 sequential system의
ranking과 비교 결론을 얼마나 바꾸는가?

## Significance

순간적인 goal crossing과 안정적인 task completion을 구분해 benchmark claim boundary를
명확히 할 수 있다.

## Current State Of The Art And Limitation

Benchmark가 여러 temporal metrics를 기록하는 사례는 이미 있다. 단순히 여러 metric을
보고하는 것은 contribution이 아니다. 의미상 동일한 temporal family의 ranking stability와
cross-domain consequence가 남는 질문이지만 Q1과 중복된다.

## Evaluation Target

- pairwise rank reversal across temporal aggregations
- time-to-success, dwell time, terminal margin와 post-success regression rate
- denominator: systems × traces × frozen temporal aggregations

## Available Data / Code / Evaluator

ManiSkill per-step evaluator는 첫 domain 후보로 확인됐다. Non-robot sequential trace와
evaluator는 미확인이다.

## Simplest Baseline Or Counterexample

First-hit와 terminal을 함께 보고하고 continuous dwell/time-to-success distribution을
제공한다. 이 보고만으로 결론이 안정되면 별도 method나 project가 필요 없다.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| 충분한 post-success regression이 있다 | once/end label이 거의 같다 | stored trace audit |
| system별 regression이 다르다 | 모든 system이 동일하게 변한다 | pairwise table |
| Q1과 다른 general principle이 남는다 | tolerance/persistence Q1로 완전히 포괄된다 | question comparison |

## Feasibility Or Pilot Study

Q1의 immutable trace가 생긴 경우에만 temporal axis를 재사용한다. 별도 simulation이나
dataset 수집을 시작하지 않는다.

## Preliminary Success Criteria

한 accessible benchmark에서 practical rank reversal이 있고 continuous temporal report
뒤에도 benchmark claim ambiguity가 남아야 한다.

## Expected Deliverable

독립 project가 아니라 Q1의 cross-domain extension 또는 evaluator reporting rule.

## Timeline And Milestones

Q1 feasibility evidence를 검토한 뒤에만 재검토한다. 현재 일정 없음.

## Interpretation Of A Negative Result

Once/end/sustained ordering이 안정적이면 temporal metric choice는 해당 denominator에서
문제가 아니며 즉시 종료한다.

## Resource Requirements

기존 immutable per-step trace만 사용. 추가 GPU, hardware와 annotation 없음.

## Related-Work Overlap

`high`; active Q1과 내부 충돌한다.

## User Decision Needed

없음. 독립 후보로 진행하지 않는다.

Selection decision: Q1과 중복되므로 현재 `deferred`.
