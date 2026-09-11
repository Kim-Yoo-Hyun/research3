# Physics-Setting Ranking Stability

Updated: 2026-09-04

## Status

`exploratory`

## Facts

- Contact-rich simulation 결과는 contact solver, timestep, friction, object mass와
  controller discretization의 영향을 받을 수 있다.
- ManiSkill3와 SIMPLER는 public simulator-based manipulation evaluation route를
  제공한다.
- 이 workspace에서는 simulator image, policy checkpoint 또는 task를 아직 실행하지
  않았다.

## Source Claims

- [ManiSkill3](https://www.roboticsproceedings.org/rss21/p021.html)는 GPU-parallel
  simulation, heterogeneous environment, demonstrations와 RL/IL baseline을 제공한다.
- [SIMPLER](https://github.com/simpler-env/SimplerEnv)는 real-to-sim visual matching과
  real-world policy ordering의 일치를 평가하며 공개 environment와 policy code를
  제공한다.

## Agent Inference

Real-world fidelity의 절대값보다, 합리적인 simulator implementation choice 아래서
**정책 간 상대 순위가 유지되는지**가 benchmark denominator의 더 직접적인 조건일 수
있다. Generic sim-to-real gap은 이미 널리 점유된 문제이므로, candidate의 범위는
frozen policies의 matched-control ranking stability와 contact-regime attribution으로
제한한다.

## Research Question Or Suspected Phenomenon

Visual observation, action interface와 evaluation predicate를 고정했을 때, 합리적인
physics/timestep/contact 설정 변화가 manipulation policy ranking을 뒤집는가? 뒤집힌다면
simple system-identification tuning 또는 randomization average 이후에도 residual이
남는가?

## Significance

Simulator leaderboard의 순위가 undocumented implementation setting에 민감하면 model
comparison과 sim-first research conclusion의 재현성이 약해진다. 안정적이면 simulator
사용의 중요한 validity evidence가 된다.

## Current State Of The Art And Limitation

SIMPLER는 simulated와 real performance의 상관을 중심으로 하고, simulator benchmark는
통상 한 default physics configuration을 사용한다. Candidate는 real-world score 예측이
아니라 공개 benchmark 내부의 controlled implementation uncertainty와 rank stability를
측정한다. 이 구분이 direct-prior audit에서 유지되지 않으면 discontinue한다.

## Evaluation Target

- primary: policy-pair rank reversal rate across preregistered physics configurations
- secondary: Kendall's tau, task success variance, contact impulse/failure-mode shift
- strongest-simple-control residual: identified default, configuration ensemble mean,
  matched compute/tuning budget 뒤의 reversal
- denominator: policy pairs × tasks × frozen configurations × seeds

## Available Data / Code / Evaluator

- first route: ManiSkill3 task/evaluator and small public baseline policies
- adjacent validation: SIMPLER task and policy subset
- configuration candidates: timestep/substeps, friction, restitution/contact solver and
  object mass within benchmark-documented or physically plausible bounds

## Simplest Baseline Or Counterexample

1. Official default configuration.
2. One calibrated configuration selected without test-policy outcomes.
3. Uniform configuration ensemble average.
4. Domain-randomized evaluation with the same rollout budget.
5. Ranking이 모든 plausible setting에서 안정적이면 candidate는 종료한다.

## Critical Assumptions

| Assumption | Disconfirming observation | Cheaper measurement |
| --- | --- | --- |
| 적어도 2개 frozen policy가 같은 task/action interface에서 실행된다. | compatible public checkpoints가 하나뿐이다. | repository/checkpoint audit |
| physics range를 결과와 독립적으로 고정할 수 있다. | documentation이나 physical bound가 없다. | task asset metadata audit |
| variation이 task semantics를 바꾸지 않는다. | object behavior가 비현실적으로 변한다. | scripted controller sanity test |

## Feasibility Or Pilot Study

Docker에서 2개 contact-rich task, 2--3개 lightweight policy, 3개 frozen physics
configuration, 소수 seed를 실행한다. 먼저 scripted/oracle controller로 task
solvability를 확인한 뒤 policy ranking과 failure trace를 계산한다.

## Preliminary Success Criteria

- solvability-matched configurations 사이에 uncertainty를 넘는 rank reversal이 있다.
- reversal이 one-off seed가 아니라 특정 contact regime과 반복적으로 연결된다.
- calibrated single setting 또는 configuration average 뒤에도 residual이 남는지를
  명시적으로 판정한다.

## Expected Deliverable

Configuration manifest, rank-stability plot, contact failure taxonomy와 simulator
evaluation uncertainty를 보고하는 최소 protocol.

## Timeline And Milestones

- day 1--2: Docker/source/checkpoint audit와 configuration freeze
- day 3: scripted solvability control
- day 4--6: pilot rollouts
- day 7: ranking analysis와 kill decision

## Interpretation Of A Negative Result

Default-near physics 범위에서 ranking이 안정적이면 benchmark fragility claim을 버리고,
해당 range를 evaluation robustness evidence로 남긴다. 모든 차이가 ensemble average로
사라지면 learned correction을 만들지 않는다.

## Resource Requirements

Local RTX 5090 32,607 MiB와 NVIDIA Docker runtime이 확인됐다. Robot, annotation,
private data는 불필요하다. Compatible ManiSkill/SIMPLER image와 정확한 task throughput은
smoke test 전까지 미확인이다.

## Related-Work Overlap

`high`. Generic sim-to-real, simulator benchmarking, physics randomization 연구와 매우
가깝다. Nearest work가 matched policy-ranking uncertainty를 이미 체계화했다면
`discontinue` 또는 훨씬 좁은 contact-specific formulation이 필요하다.

## User Decision Needed

RTX 5090을 일주일 동안 사용할 수 있는 총 rollout compute와 동시 작업 제한.
