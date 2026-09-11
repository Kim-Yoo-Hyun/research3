# CD4 Counterfactual Failure Attribution

Updated: 2026-09-04

## Status

`deferred`

Stage 7 decision은 `reformulate`다. 현재 formulation은 direct prior와 충돌하며,
continuous-control residue의 public substrate가 확인될 때만 별도 revised candidate로
다시 기록한다.

## Facts

- 이 workspace에서는 agent/robot failed trajectory를 생성하거나 수정 replay하지 않았다.
- 선택된 public environment, failure taxonomy, intervention interface와 denominator는 없다.
- Foundation model/VLA 학습과 real-robot motion은 현재 범위 밖이다.

## Source Claims

- 2025 [AgenTracer](https://arxiv.org/abs/2509.03312)는 oracle-corrected action과 suffix
  re-simulation으로 success를 회복하는 가장 이른 step을 decisive error로 정의한다.
- 2026 [Causal Agent Replay](https://arxiv.org/abs/2606.08275)는 agent step에 `do` intervention을
  적용하고 stochastic suffix를 재실행해 outcome-distribution shift를 측정한다.
- 2026 [AgenticRAG-FP](https://arxiv.org/abs/2608.20627)는 certified hop fault를 주입하고
  suffix를 재실행한 뒤 post-hoc 및 counterfactual diagnoser의 exact-hop attribution을
  비교한다.

## Agent Inference

원래 inference는 타당하지만 새롭지 않다. Minimal intervention의 recovery effect로 causal
attribution을 검증하는 핵심 원리는 AgenTracer, CAR와 AgenticRAG-FP가 이미 직접 사용한다.
남을 수 있는 것은 continuous-control robotics에서 intervention validity와 physical
state divergence가 attribution을 어떻게 바꾸는지뿐이며, 이는 별도 검토가 필요하다.

## Research Question Or Suspected Phenomenon

Frozen failed trajectory의 진단된 한 step/component만 oracle-corrected replay했을 때,
diagnostic score가 실제 recovery와 marginal downstream improvement를 random/neighbor
correction보다 잘 예측하는가?

## Significance

Failure taxonomy를 설명용 label에서 actionable bottleneck evidence로 바꿀 수 있다. Agent,
planning, robot learning의 data selection과 recovery design에 같은 원리를 적용할 수 있다.

## Current State Of The Art And Limitation

Counterfactual replay direct prior는 이미 가장 이른 oracle-recovering step, same-policy
resampling effect와 certified injected-hop localization을 다룬다. 따라서 **진단된 원인을
국소적으로 수정했을 때 outcome이 회복되는가**라는 현재 gap은 점유됐다. 상세 근거는
[preliminary prior audit](../related_work/cd4-counterfactual-failure-attribution.md)에 있다.

## Evaluation Target

- primary: diagnosed-only intervention의 paired recovery lift over same-cost random correction
- secondary: regret to full privileged oracle, intervention precision@k, effect calibration
- diagnosis: failure type, intervention location과 downstream recovery의 heterogeneity
- denominator: frozen failed traces × candidate locations/components × counterfactual seeds

## Available Data / Code / Evaluator

CAR는 public executable LLM-agent replay implementation을 제공하지만 그 자체가 direct
prior다. Continuous-control robotics에서 deterministic state restore와 physically valid
local intervention을 함께 제공하는 first artifact는 아직 확정하지 않았다.

## Simplest Baseline Or Counterexample

1. random failed-step correction;
2. temporal-neighbor 및 last-action correction;
3. AgenTracer식 earliest oracle correction with suffix replay;
4. CAR same-policy `do_resample` 및 point-of-commitment;
5. full privileged correction oracle.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| exact state restore가 가능하다 | same action replay도 outcome이 불안정하다 | 10-trace determinism test |
| component-local intervention이 정의된다 | correction이 interface 전체를 바꾼다 | action/schema audit |
| oracle correction이 success를 높인다 | privileged fix에도 recovery가 없다 | 20-failure oracle probe |
| diagnosis가 simple location heuristic보다 낫다 | random/earliest가 동등하다 | matched small subset |

## Feasibility Or Pilot Study

현재 formulation으로 feasibility study를 실행하지 않는다. Stage 7의 `reformulate`
결정에 따라 continuous-control intervention validity의 public substrate가 확인된 뒤
별도 revised question으로만 protocol을 작성한다.

## Preliminary Success Criteria

- privileged local correction이 practical downstream lift를 만듦;
- existing diagnosis와 outcome 사이에 systematic mismatch가 재현됨;
- strongest simple localization baseline 뒤 residual이 남음;
- residual이 intervention-effect ranking problem과 연결됨.

## Expected Deliverable

Diagnosis-versus-causal-effect matrix, matched intervention benchmark protocol, failure-type별
recoverability map과 lightweight effect-ranking method의 필요성 판정.

## Timeline And Milestones

- completed: nearest primary work와 official artifact audit
- finding: current causal core에 direct collision 확인
- completed: Q1/CD1과 Stage 7 비교 후 `reformulate` 결정
- deferred: physically local intervention과 deterministic restore를 제공하는 public
  continuous-control substrate 확인
- reactivation 시에만 별도 revised question과 feasibility protocol 작성

## Interpretation Of A Negative Result

Oracle correction 자체가 recovery를 만들지 않으면 attribution target이 잘못됐으므로
종료한다. Simple earliest/random correction이 diagnosis와 동등하면 learned attribution을
만들지 않는다. Exact replay가 불가능하면 authorized scope 안에서 후보를 reject한다.

## Resource Requirements

한 public executable environment, deterministic replay, CPU 또는 짧은 single-GPU
inference. New project-specific container만 허용하며 human annotation/hardware는 불필요해야
한다.

## Related-Work Overlap

`high / direct collision`. [Preliminary prior audit](../related_work/cd4-counterfactual-failure-attribution.md)에서
AgenTracer, CAR와 AgenticRAG-FP가 현재 causal core를 이미 점유함을 확인했다.

## User Decision Needed

없음. Reactivation condition을 만족하기 전에는 진행하지 않는다.
