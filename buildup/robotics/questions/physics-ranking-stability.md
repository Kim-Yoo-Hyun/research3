# Physics-Setting Ranking Stability

Updated: 2026-09-18

## Status

`deferred` — 단일 PPO timestep 관찰·검산과 후속 투자 검토를 완료했다.
현재 trajectory-sensitivity 경로의 추가 실행을 보류한다. 원래 policy-ranking 질문
전체의 반증이나 종료 판정은 아니다.

## Investment decision and re-entry

[직접 선행·후속 비용 비교](../related_work/policy-geometry.md#q3-investment-and-q15-selection-2026-09-18)를
마쳤다. Contact-model 분석은 timestep self-consistency를, SIMPLER는 물성 변화와 policy
순위를, manipulation benchmark audit는 closed-loop 수치 차이의 전파를 이미 다룬다.
이번 관찰은 그 설명과 양립하며, 시험한 범위에서 outcome 변화는 없었다.

에이전트 판단: 같은 grid/seed 확대나 controller 둘을 임의로 골라 순위를 만드는 것보다
Q15의 제한된 reward-training 관찰에서 새로 줄일 불확실성이 크다. Q3의 기존 결과와
검산은 보존한다. 초기 상태 여덟 개로 일반적인 안정성을 입증한 것은 아니다.

구체적인 contact/control 사례에서 **설정 선택이 어떤 행동 결정을 바꿀 수 있는지**,
이를 가르는 작은 대조와 비용이 생기면 재검토한다. 실제 실패나 양의 결과, 새 원리를
미리 요구하지 않는다. Compatible policy 비교가 목적에 맞는 경우도 열어 두되 단순히
정책 수를 늘리는 것을 다음 작업으로 삼지 않는다.

## Observation 2026-09-18

[Q3 study](../pilot_studies/q3-timestep/README.md#results-2026-09-18)에서 96회를 완료했다.
모든 mode/frequency/repeat의 end/once success는 8/8이다. 같은 조건의 반복과 100 Hz
reference-target replay에서 cube/qpos/target 차이는 0이었다. Frequency 변경 시 cube
trajectory 차이는 발생했고 closed loop가 target replay보다 컸지만 성공 결과는 유지됐다.
검산·수치·실행 복구와 제한은 study owner를 따른다.

관찰 직후 판단은 `refine`이었다. 수치적 민감도와 target 갱신의 관여를 관찰했으며
outcome fragility나 ranking reversal의 증거는 없었다. 위 후속 검토에서 현재 경로의
추가 투자를 보류했다. 새 method의 필요성을 가정하거나 같은 grid/seed를 자동 확대하지 않는다.

## Selected First Observation

[Q4 후속·직접 선행·비용 비교](../related_work/policy-geometry.md#q4-follow-up-investment-review-2026-09-18)를
마치고 다음 작은 관찰을 선택했다. Q4의 현재 symbolic instance-selection 경로는 보류한다.
Q3에서도 timestep sensitivity, contact solver 영향과 closed-loop amplification은 기존
연구에 있다. 이 관찰로 새로운 현상이나 method를 입증했다고 전제하지 않는다.

**질문:** action 주기·PD 설정·평가 시점을 고정한 하나의 frozen manipulation policy에서
physics timestep의 변화가 trajectory만 바꾸는가, 성공 결과도 바꾸는가? 기록한 absolute
joint-target sequence를 재생할 때와 policy가 매 control step target을 갱신할 때 차이는
어떻게 달라지는가?

**잠정 설명:** 작은 수치/접촉 변화가 policy와 relative-target 갱신을 거쳐 커지거나,
feedback이 오히려 보정할 수 있다. 성공이 안정적이고 작은 trajectory 차이만 남을 수도
있다. 둘 다 다음 투자 판단에 유용하다. 단일 policy이므로 **policy ranking은 측정하지
않는다**. Two-policy 조건을 충족한 것처럼 쓰거나 기존 EE/joint PPO를 같은 interface의
알고리즘 비교로 합치지 않는다.

### Inputs and comparisons

- ManiSkill `v3.0.1`, commit `a4a4f9272ad64b1564035874b605ceb687b63ed8`;
  `PickCube-v1`, Panda, `state` observation, PhysX CUDA. Workspace의 source와 작은
  checkpoint는 read-only input으로 쓰고 별도 Docker image/cache/output을 만든다.
- 하나의 `ppo_pd_joint_delta_pos_ckpt.pt`를 공식 PPO `Agent`의 deterministic inference로
  사용한다. SHA256 `78959417279892d73e4ed5930a6d8de8626a24eee0ec553dfc6af61391b0b356`.
  Q1/Q8에서 취득한 public artifact의 재사용이며 과거 종료 질문을 재개한 것은 아니다.
- Control frequency **20 Hz**, simulation frequency **100/200/400 Hz**; 각각
  **5/10/20 substeps**, dt **10/5/2.5 ms**. 모든 condition에서 50 control steps = 2.5초다.
  Object mass/friction, contact/solver 설정, PD gain/force limit과 interpolation을 고정한다.
  Arm/gripper의 `interpolate=False`를 runtime config에서 확인한다.
- Native vector environment 8개, reset seed **20260918**, env index 0–7을 paired unit으로
  사용한다. Fresh environment 두 반복을 각 condition에 적용한다. **2 modes × 3 frequencies
  × 8 initial states × 2 repeats = 96 episodes**; 8개 state의 반복이지 96개 독립 scene이 아니다.
  결과를 본 뒤 seed/task를 성공률에 맞춰 선택하지 않는다. 탐색 중 기술 수정은 이유와 범위를 남긴다.
- Mode A: 정상 closed-loop PPO. Mode B: 첫 100 Hz closed-loop 반복의 각 초기 상태에서
  기록한 **arm/gripper absolute joint drive targets**를 동일 20 Hz로 재생한다. 모든
  frequency의 mode B는 같은 target trace를 사용한다. Normalized delta action의 재생은
  현재 qpos에 따라 target이 달라지므로 이 대조를 대신할 수 없다.
- Mode B도 low-level PD feedback과 physics를 유지한다. Pure open-loop torque replay나
  controller-free physics 분해가 아니다. 비교가 제거하는 것은 policy 및 relative-target
  재계산이며 완전한 causal mediation 비율을 추정하지 않는다.

### Readout and necessary verification

각 episode에서 동일한 control boundary의 joint position/velocity, cube pose/velocity,
goal distance, action/drive targets와 원본 success를 기록한다. `success_at_end`를 primary
outcome, `success_once`를 보조로 보고하며 둘의 차이를 숨기지 않는다. Official distance
threshold 0.025 m와 robot-static 0.2 기준은 바꾸지 않는다. `is_grasped`/contact는 가능한
경우 보조 진단에 사용하고 그 predicate 변화만으로 physical grasp 실패를 단정하지 않는다.

기본 100 Hz 대비 trajectory/target 오차와 outcome 일치, 200–400 Hz 차이, 같은 condition
두 반복의 차이를 함께 제시한다. 두 반복은 실행 변동을 보는 작은 대조이며 통계적 error
bound가 아니다. Frequency 간 차이를 단순 bitwise 불일치 하나로 실질적 성능 변화라고
부르지 않는다. 높은 frequency에서 일치해도 real-world fidelity나 수렴 증명은 아니다.

필요한 검산은 같은 initial robot/cube/goal state, action/control 시간축, 실제 substep 수,
고정 PD/physics 설정, target replay buffer 반영, 원본 success의 별도 재계산이다. 100 Hz의
target replay와 closed-loop reference 및 동일 조건 반복을 먼저 대조해 adapter 오류와
자연 실행 변동을 구분한다. Shared state/hash는 관측된 초기 상태의 일치이며 숨은 solver
state까지 보장하지 않는다. GPU target apply 경로를 포함해 container 안에서 검증한다.

### Cost and interpretation

새 Docker/adapter 준비·검산 **1–2 작업일**, 본 rollout **GPU wall 1시간 이내**가 계획
예산이었다. 실행 전에는 source/checkpoint 접근·bytes/hash만 확인한 상태였고,
이후 새 image와 target replay runtime을 위 study에서 검증했다. 별도 사용자 승인 gate로 쪼개지 않고 실행·검산·해석까지
한 TODO로 진행한다. 장시간 build는 background job과 timestamp log를 사용한다.

- Difference가 동일 조건 변동보다 뚜렷하고 outcome까지 바뀌면 해당 contact/control 사례를
  바탕으로 Q3의 다음 질문을 수정한다. 곧바로 leaderboard fragility나 ranking reversal을
  주장하지 않는다.
- Trajectory만 바뀌거나 모두 안정적이면 이 policy·state·frequency 범위의 안정성으로
  기록한다. 차이가 나올 때까지 timestep/seed를 확대하지 않는다.
- Closed loop와 replay의 차이는 feedback/relative-target 갱신의 관여에 대한 단서다.
  모든 원인을 physics로, 또는 policy로 단정하지 않는다.
- 초기 상태나 target replay 계약이 맞지 않으면 영향을 받는 대조를 수리한다. 준비 예산을
  넘거나 policy가 전 조건에서 task를 수행하지 못해 관찰 가치가 낮으면 결과와 실패 원인을
  보존하고 재설계/보류를 판단한다. Host 우회나 새 학습을 하지 않는다.

이미 사용한 public checkpoint에서 새 setting을 탐색하는 buildup 관찰이다. Stronger
ranking claim에는 이후 compatible policy와 별도 관찰이 필요하며 이번의 통과 조건은 아니다.

## Review 2026-09-18

[Q4와 입력·단순 대안·비용을 비교](../related_work/policy-geometry.md#q3-q4-observation-comparison-2026-09-18)해
당시 Q4의 작은 Taskography 관찰을 선택했다. Q3는 reserve였으며 실패 판정이 아니었다.
Workspace의 ManiSkill source/recipe는 존재하지만 보유한 두 PPO의 action interface가 달라
그대로 같은-interface policy 순위로 해석할 수 없다. Common-interface scripted controller
비교 또는 system-level sensitivity로의 명시적 질문 수정은 여전히 가능하다.

당시 작은 초안은 PickCube 하나에서 control 20 Hz, sim 100/200/400 Hz를 고정한
discretization 대조다. PD target interpolation, gain, horizon, 초기 상태를 함께 기록해야
하며 default와 세밀한 두 timestep의 대조는 physical validity가 아닌 convergence 단서다.
새 Docker/control adapter 준비를 1–2 작업일로 추정한다. 기존 simulator image는 쓰지 않는다.
이 초안의 controller-pair 비교는 위 단일-policy mechanism 관찰로 축소했다.
아래 2-task/week 설계는 초기 미실행 원안이며 현재 실행 대기열이 아니다.

## Review 2026-09-16

[남은 후보 비교](../related_work/policy-geometry.md#remaining-candidate-comparison-2026-09-16)에서
Q3를 reserve로 유지하고 CD2의 작은 관찰을 먼저 선택했다. [SIMPLER §VI-D와 Table X](https://arxiv.org/html/2405.05941v1)는
이미 여러 정책의 mass/friction sensitivity와 ranking을 비교한다. 일반적인 physics-setting
ranking이라는 구분만으로 새 질문의 차별성을 확보한 것은 아니다.

가능한 축소는 한 task·두 compatible policy에서 control interval을 고정한 timestep/substep
대조다. Default와 같은 rollout budget의 configuration 평균을 단순 대안으로 둔다.
이 설계의 실행·정책 선택은 아직 하지 않았다. 안정적인 순위도 유용한 관찰이며 positive
residual·최종 novelty를 첫 관찰의 gate로 요구하지 않는다. 아래의 일주일 pilot은 초기
미실행 초안이고 현재 실행 대기열이 아니다.

## Facts

- Contact-rich simulation 결과는 contact solver, timestep, friction, object mass와
  controller discretization의 영향을 받을 수 있다.
- ManiSkill3와 SIMPLER는 public simulator-based manipulation evaluation route를
  제공한다.
- 단일-policy timestep 실행과 독립 검산을 완료했다. Source/checkpoint/runtime과
  결과 보존은 [study owner](../pilot_studies/q3-timestep/README.md)가 소유한다.

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

SIMPLER의 물성 sensitivity 비교는 현재 질문의 직접 선행이다. 해당 결과가 모든 task나
discretization choice의 안정성을 보장하지는 않는다. 남는 질문은 구체적인 설정과 control
semantics를 정해야 평가할 수 있으며 close prior의 존재만으로 자동 discontinue하지 않는다.

## Evaluation Target

아래 ranking target과 후속 2-task 원안은 장기 formulation이다. 현재 선택한 단일-policy
관찰의 필수조건·분모는 위 [Selected First Observation](#selected-first-observation)을 따른다.

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
5. 선택한 plausible 범위에서 ranking이 안정적이면 그 범위의 robustness evidence로 해석한다.

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

## Observations To Interpret

- solvability-matched configurations 사이의 순위·변동성과 관찰 가능한 불확실성.
- 변화가 있다면 seed 또는 contact regime으로 설명되는지.
- calibrated single setting 또는 configuration average가 어떤 차이를 설명하는지.

Positive reversal이나 단순 대안 이후 residual은 관찰 결과이며 진행 필수조건이 아니다.

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

`high`. Generic sim-to-real, simulator benchmarking, physics randomization 및 SIMPLER의
직접 물성 비교와 가깝다. 추가 정보가 있는 좁은 관찰과 그 비용으로 재비교한다.

## User Decision Needed

없음. 위 96-episode 탐색 관찰을 선택했으며 과거 일주일 GPU pilot은 실행 대기열이 아니다.
