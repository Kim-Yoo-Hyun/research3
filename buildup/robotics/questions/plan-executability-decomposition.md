# Plan Executability Decomposition

Updated: 2026-09-04

## Status

`deferred`

## Facts

- Long-horizon embodied task의 실패는 semantic ordering, symbolic precondition, spatial
  reachability와 low-level feasibility를 함께 포함할 수 있다.
- ProcWorld는 large-scale procedural indoor environment와 trajectory를 제공한다.
- VLA-Arena는 Long Horizon category를 포함한다.

## Source Claims

- [ProcWorld](https://aclanthology.org/2025.emnlp-main.635/)는 16개 task type,
  5,000개 room과 1,000만 개 이상의 trajectory를 포함하고 reachability constraint를
  사용한다.
- [SIMPACT](https://simpact.github.io/)는 simulation-in-the-loop feedback을 사용해
  VLM action planning을 개선하며 별도 training을 요구하지 않는다.
- [VLA-Arena](https://vla-arena.github.io/)는 long-horizon task를 structured evaluation
  category로 제공한다.

## Agent Inference

LLM/VLM의 “reasoning failure”로 묶이는 오류 중 상당수는 symbolic, spatial 또는
interaction feasibility validator로 분리될 수 있다. 그러나 simulation-in-the-loop와
task-and-motion planning이 이미 강한 direct prior이므로, 단순 validator method가
아니라 **failure denominator와 residual decomposition**이 먼저 필요하다.

## Research Question Or Suspected Phenomenon

Frozen planner가 생성한 long-horizon plan에서 semantic ordering을 고정한 뒤 남는 실행
실패의 비율은 symbolic precondition, spatial reachability, interaction/contact
feasibility로 각각 얼마나 설명되는가? 가장 단순한 validators를 모두 적용한 뒤에도
planner-specific residual이 남는가?

## Significance

계획 실패의 원인을 구분하면 새로운 LLM planner가 필요한지, deterministic checker가
필요한지, 또는 low-level controller/data가 병목인지 판단할 수 있다. 어느 결과든 method
선택을 제한하는 정보가 된다.

## Current State Of The Art And Limitation

Task-and-motion planning은 symbolic/continuous feasibility 결합을 오래 다뤘고,
SIMPACT는 simulator feedback을 VLM planning loop에 넣는다. 따라서 “simulation으로
plan을 고친다”는 contribution은 점유됐다. Candidate는 matched frozen plans의 단계별
failure attribution과 strongest-validator residual에 한정한다.

## Evaluation Target

- primary: failed plans 중 preregistered validator family가 설명하는 exclusive and
  overlapping fraction
- downstream: validators 이후 executable plan rate 또는 simulator task success
- secondary: false rejection, validation cost, failure detection lead time
- denominator: fixed planner outputs × tasks × scenes × seeds

## Available Data / Code / Evaluator

- first route: ProcWorld public rooms/trajectories and reachability constraints
- second route: VLA-Arena long-horizon tasks or ManiSkill multi-step task subset
- planner: frozen open model/API-free lightweight planner or public stored plan set;
  exact route depends on artifact audit

## Simplest Baseline Or Counterexample

1. Symbolic precondition checker.
2. Navigation/reachability graph check.
3. Collision/interaction feasibility proxy.
4. Full simulator one-step rollout within the same interaction budget.
5. Oracle future success label, evaluator only.

## Critical Assumptions

| Assumption | Disconfirming observation | Cheaper measurement |
| --- | --- | --- |
| Planner outputs can be normalized without changing semantics. | free-form plans cannot be aligned to actions. | 50-plan schema audit |
| Failure labels can be attributed with acceptable ambiguity. | categories overlap almost completely or lack state evidence. | hand-audit 20 failures without new annotation campaign |
| Simple validators leave a nontrivial residual. | checker/rollout baseline explains nearly all failures. | small held-out task subset |

## Feasibility Or Pilot Study

ProcWorld의 소수 task type과 frozen plan set을 고정한다. Symbolic precondition,
reachability와 simple interaction proxy를 독립적으로 적용하고 simulator/evaluator
outcome과 비교한다. Category definition, overlap rule와 denominator를 결과 전에
manifest로 고정한다.

## Preliminary Success Criteria

- nominal control과 failed plan이 모두 있어 분해 가능한 denominator를 확보한다.
- strongest simple validators 뒤에도 practical-size residual 또는 systematic false
  rejection이 남는다.
- privileged simulator/oracle가 residual case의 downstream outcome을 의미 있게
  개선할 수 있음을 counterfactual로 보인다.

## Expected Deliverable

Failure-decomposition table, validator precision/recall-cost frontier, representative
counterexamples와 다음 research decision에 필요한 diagnosis.

## Timeline And Milestones

- day 1--2: dataset/action/evaluator schema audit
- day 3: fixed plan subset and failure taxonomy manifest
- day 4--6: validator baselines and oracle comparison
- day 7: overlap 확인과 `reformulate / discontinue` 결정

## Interpretation Of A Negative Result

Simple validators가 대부분의 failure를 설명하고 downstream success를 회복하면 learned
planner/module을 만들지 않는다. Failure attribution이 불가능하면 broad “reasoning” claim을
포기하고 observable task subset으로 reformulate한다.

## Resource Requirements

Initial offline audit는 CPU 중심으로 설계한다. Simulator rerun에는 GPU가 필요할 수
있으나 foundation-scale training, robot와 신규 annotation campaign은 요구하지 않는다.

## Related-Work Overlap

`direct_collision`. [Focused audit](../related_work/q2-plan-executability.md)에서
Embodied Agent Interface가 planning module과 trajectory feasibility failure를 이미
세분화하고, ET-Plan-Bench·ProcWorld가 spatial/temporal/reachability-constrained planning
denominator를, SIMPACT가 physical simulator validation과 correction을 점유함을 확인했다.
현재 질문의 failure-decomposition principle은 충분히 분리되지 않는다.

## Selection Decision

`reformulate`. Direct-prior overlap 때문에 현재 질문 그대로 feasibility study로 보내지
않는다. 새로운 observable residual이 정의되기 전까지 `deferred`로 유지한다.

## User Decision Needed

없음. GPU availability will decide whether the first study stops at offline plan validity
or includes simulator execution.
