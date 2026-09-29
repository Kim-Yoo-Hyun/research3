# Reward Transfer Across Dynamics

Updated: 2026-09-22 · ID: Q15

## Status

`deferred` — [성공 후 joint-position hold 576회 비교·독립 검산](../pilot_studies/q15-reward/README.md#hold-results-2026-09-22)을
완료했다. 단순 유지 제어가 native의 주요 이탈을 피했지만 새 악화도 생겼으며, 현재
reward-selection/hold 경로의 확대는 보류한다. 질문 전체의 반증은 아니다.
[결과 owner](../pilot_studies/q15-reward/README.md#results-2026-09-18)에 9 fits와 2,304 episodes를
보존했다. Scale 대조도 최종 성능을 따라잡아 grasp bonus 제거만의 transfer robustness
이점은 지지하지 않는다. Formal hypothesis나 새 reward method의 선택은 아니다.
2026-09-08의 학습비용 미확정으로 인한 보류를
[후속 비교](../related_work/policy-geometry.md#q3-investment-and-q15-selection-2026-09-18)에서 재검토했다.

## Question and significance

**같은 조작 과제에서 grasp bonus의 유무로 학습한 정책은 cube 물성이 바뀔 때 서로 다른
성공률·접촉 행동을 보이는가? 그 차이는 단순 reward scale이나 학습 진행도의 차이와
구분되는가?** 이는 기존 broad reward-selection 질문의 첫 축소 관찰이다.

기본 환경에서 빠르게 학습되는 보상이 물성 변화에도 유용한 행동을 학습시키는지는
reward selection에 중요하다. 다만 이 일반 문제는 DrEureka 등에서 이미 다룬다.
이번에는 구성요소 하나를 바꾸는 작은 학습 개입이 해석 가능한 차이를 만드는지 배운다.
차이가 없거나 단순 대조로 설명돼도 유효한 결과다.

## Facts, prior claims and explanation

**확인한 source 사실:** ManiSkill v3.0.1의 PickCube dense reward에는 reaching,
grasp indicator, grasp-gated placement, placed-gated static reward가 있다. Native
success에서는 합을 5로 덮어쓰고 normalized dense reward는 이를 5로 나눈다.
State observation에도 `is_grasped`가 있으며, 성공은 goal 거리와 robot-static 조건이다.
따라서 grasp shaping과 task success는 동일 조건이 아니다.

**논문 주장:** [Eureka](https://eureka-research.github.io/)는 reward program 탐색을,
[DrEureka](https://arxiv.org/html/2406.01967v1)는 safety-aware reward와 reward-aware
domain randomization을 다룬다. 특히 DrEureka Appendix E/Table XVI는 nominal simulation에서
더 빠르지만 실제 전이가 실패하는 reward-induced behavior를 이미 제시한다.
[HPRS](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1444188/full)는
task requirements의 계층과 potential-based shaping을 다룬다. Reward hierarchy,
normalization 또는 물성에 따른 성능 변화 자체를 새 기여로 쓰지 않는다.

**에이전트 잠정 설명:** 성공 전 grasp 상태의 지속 보상은 접촉을 유지하는 학습 경로에
영향을 줄 수 있다. 반대로 placement 항만으로 충분하거나, 차이가 단순 최적화 속도일
수도 있다. Grasp bonus 제거가 더 좋다는 방향은 가정하지 않는다. 이 관찰은 DrEureka의
재현이나 우월성 비교가 아니며 LLM-generated reward 전체의 성질을 대표하지 않는다.

## First observation

### Fixed task and reward comparisons

- Public ManiSkill `v3.0.1`, commit `a4a4f9272ad64b1564035874b605ceb687b63ed8`;
  `PickCube-v1`, Panda, `state`, `pd_joint_delta_pos`, PhysX CUDA. Source/recipe만 활용하고
  Q15의 새 Dockerfile/image/cache/output을 만든다. Q3의 frozen checkpoint는 학습 초기화로
  사용하지 않는다. Physics 100 Hz, control 20 Hz, horizon 50 steps를 고정한다.
- **Official normalized dense:** 원본 `r0 = dense_reward / 5`.
- **Without grasp bonus:** `r1 = r0 - 0.2 * is_grasped * (1 - success)`.
  성공 시 보상, placement gate, static 항, observation, reset과 evaluator는 유지한다.
  이는 한 항을 제거한 대조이며 새 방법이나 potential-based shaping이 아니다.
- **Scale control:** `r2 = 0.5 * r0`. 동일 최적화 설정에서 scale 변화만으로 생기는
  차이를 관찰한다. 한 scale 대조가 모든 normalization/optimization 설명을 배제하지는 않는다.

### Training and fixed checkpoints

Official state PPO를 바탕으로 **3 rewards × 3 independent seeds = 9 fits**를 한다.
Seeds는 `101, 202, 303`; 같은 seed를 reward 사이에서 사용하되 rollout data가 같은
matched training set이라고 간주하지 않는다. Nominal dynamics로만 학습하며 원래의
initial-state randomization은 유지한다. Dynamic parameter randomization은 첫 관찰에서 하지 않는다.

공식 `examples.sh`의 PickCube 설정을 출발점으로 `num_envs=1024`, `num_steps=50`,
`update_epochs=8`, `num_minibatches=32`, learning rate `3e-4`, gamma `0.8`, GAE lambda
`0.9`, entropy coefficient `0`, advantage normalization을 고정한다. 다른 optimizer/PPO
설정은 pinned `ppo.py` 기본값을 명시적으로 저장한다. Training partial reset과 bootstrap
처리는 원본대로 유지하며 video/W&B는 끈다.

Batch는 51,200 transitions이고 `total_timesteps=10_000_000`의 원본 floor 동작에 따라
195 updates, **9,984,000 transitions/fit**다. Update **97과 195를 마친 직후**의
checkpoint 두 개를 저장한다(4,966,400 / 9,984,000 transitions). 원본의 update 이전
periodic save와 혼동하지 않으며 nominal 최고 checkpoint나 seed를 골라 보고하지 않는다.
두 checkpoint는 같은 학습의 중간/최종 관찰이며 독립 학습 반복이 아니다.

### Evaluation and diagnosis

각 checkpoint를 다음 **2 × 2 = 4 conditions**에서 deterministic inference로 평가한다.
Cube density 배율은 `1, 2`, cube material의 static/dynamic friction 배율은 `1, 0.5`다.
Nominal과 두 single changes, joint change를 모두 포함한다. Geometry·COM·robot·table
material은 고정하고 density 변화에 맞춰 mass와 inertia가 함께 바뀌도록 한다.
실제 material 값과 확인 가능한 friction-combine 설정을 runtime에서 기록한다. Effective
contact coefficient를 직접 확인할 수 없으면 미확인으로 남기며, cube friction 절반이
finger–cube effective friction 절반이라는 가정은 하지 않는다.

GPU 초기화 전 scene construction에서 물성을 적용하고 shared material로 robot/table이
같이 바뀌지 않도록 한다. 각 condition의 cube mass/inertia/material, 손가락·table material과
기본 condition의 원본 일치를 검증한다. 이 사전 설계의 runtime 확인은 아래 완료 관찰과
study owner에 기록한다. 물리적으로 가능한 실제 범위라는 claim은 하지 않는다.

Reset seed `2026091901`의 **32 initial states**를 모든 reward/seed/checkpoint/물성에서
공유한다. Pose/qpos/goal의 일치를 확인하고 처음부터 50 control steps를 실행한다.
총 **9 fits × 2 checkpoints × 4 conditions × 32 states = 2,304 episodes**다.
Training seed 단위 결과와 초기 상태별 paired outcome을 보존한다. 2,304회를 독립 정책
반복으로 세지 않는다. 세 shifted conditions는 학습에 쓰지 않지만 첫 exploratory 평가이며
독립적인 최종 confirmatory test set으로 주장하지 않는다.

Primary readout은 원본 `success_at_end`; `success_once`, goal distance, arm qvel,
grasp flag 변화와 cube 높이/상대 운동을 보조로 본다. Reward마다 raw return을 비교해
우열을 정하지 않는다. Goal 도달 실패, 도달했지만 nonstatic, 성공 후 이탈을 구분한다.
Grasp flag는 simulator predicate이며 실제 grasp 품질/접촉력의 ground truth가 아니다.
동일 물성의 reward 차이, 각 reward의 nominal 대비 변화, seed 간 변동과 두 학습 시점을
함께 읽는다. Nominal 성능 차이만으로 robustness 차이를 판정하지 않는다.

### Necessary checks and resource bound

Container에서 저장 state의 reward 구성과 native success를 별도로 재계산하고, 원본
reward/환경 대조, seed/initial-state/time/config, checkpoint step 수와 actual material을
확인한다. 학습 adapter 오류와 reward 개입의 효과를 구분한다. Package 설치/import와
학습/검산은 Docker 안에서 한다. 결과와 실행 기록을 보존한 뒤 이번 workspace에서 생성한
불필요한 종료 container만 정리한다.

공식 README의 PickCube 학습 **2–5분**은 저자 안내이며 이 workstation의 측정값이 아니다.
계획 예산은 구현·검산 **1–2 작업일**, 각 fit **20분**, 전체 training **GPU wall 3시간**,
evaluation/검산 **1시간** 상한이다. Build 시간은 별도 기록한다. 첫 fit부터 elapsed time,
throughput과 VRAM을 기록하며 상한 초과 시 부분 결과와 자원 제약을 보존한다. OOM이나
adapter 수정으로 protocol을 바꾸면 모든 비교에 동일하게 적용하고 변경 이유를 남긴다.
성공률을 보고 reward/seed/budget/물성 범위를 자동 조정하지 않는다.

## Observed outcome 2026-09-18

고정한 9 fits / 18 checkpoints / 72 conditions를 완료했다. 최종 nominal end success는
native 86/96, no-grasp 94/96, half-scale 93/96이다. Shifted 조건에서도 no-grasp와
half-scale의 차이는 1–2건이고 우세 방향이 바뀐다. Half-scale의 nominal 성공은 중간
65/96에서 최종 93/96으로 증가했다. 물성 변화 대비 감소와 reward 간 절대 성능 차이를
구분하면 grasp bonus 제거의 고유 robustness 이점은 지지되지 않는다.

Native nominal의 성공 후 실패 전환 9건 중 8건은 한 seed에서 grasp/static을 유지한 채
goal 거리 범위를 벗어난 사례다. 이 사례와 scale/학습 진행도는 다음 설명의 대상이며
원인이나 새 방법을 확정한 결과는 아니다. [전체 수치·반례·검산 수정·보존](../pilot_studies/q15-reward/README.md#results-2026-09-18)을
따른다. 원본 native 판정과 일치하는 독립 검산을 통과했으며 학습/평가 재실행은 없었다.

이후 [후속 투자 판단](../related_work/policy-geometry.md#q15-follow-up-investment-2026-09-18)에서
재학습 없이 동일한 성공 상태에서의 실행 제어를 바꾸는 관찰을 선택했다. 추가 학습·새
reward method·DR/PBRS 전체 구현은 선택하지 않았다.

## Selected follow-up

**성공 후 정책을 계속 실행할 때의 목표 이탈을, 단순 joint-position hold로 피할 수 있는가?**
관찰된 8건은 grasp/static 판정을 유지한 채 목표 범위를 벗어났지만, 다른 action을 냈을
경우의 결과는 기존 trace만으로 알 수 없다. 같은 성공 상태에서 실행 제어를 바꾸어 추가
reward 학습의 필요성을 먼저 판단한다. Hold에서도 실패하면 원인과 baseline 한계를
구분하며 물리적으로 불가피한 실패로 단정하지 않는다.

도달과 유지의 구분은 reach-and-stay 선행에 있고 PPO의 scale 민감도도 알려져 있다.
이를 새 현상이나 contribution으로 주장하지 않는다. 관절 목표 고정은 여기서 검증할
단순 대조이며 안정성이 보장된 controller가 아니다.

[정확한 개입·입력·readout·예산](../pilot_studies/q15-reward/README.md#joint-position-hold-observation)은
study owner가 소유한다. 기존 최종 checkpoint 9개와 nominal의 공통 32개 초기 상태를
두 route로 평가하는 576 episodes이며 재학습은 없다. 이미 본 상태와 privileged native
success를 쓰는 exploratory diagnostic이다. 2026-09-22 실행·검산·해석을 완료했다.

## Hold outcome and re-entry 2026-09-22

**사실:** Native 86→93/96, no-grasp 94→93/96, half 93→93/96이었다. Paired 개선은
각각 8/0/1건, 악화는 각각 1건이다. Native seed 202의 기존 이탈 8건은 첫 성공부터
끝까지 유지됐다. 288개 pair의 전환 전 상태·명령과 기존 continued trace 9개가 정확히
일치했고, 실제 고정 reference·원본 label/reward 검산도 통과했다.

**해석:** 단순 실행 제어만으로 주요 실패를 피할 수 있어 현재 사례에서 새로운 reward
학습의 필요성은 약해졌다. 반면 oracle success를 충족해도 물체 안정 파지가 보장되지
않으며, 고정 joint target은 실제 관절과 물체를 완전히 정지시키지 않는다. 이를 새로운
현상·보편적 안정 제어·reward 학습 원인으로 주장하지 않는다.

**투자 판단:** 현재 경로는 보류한다. 재검토하려면 성공 후 실행 제어 선택이 중요한
구체적 행동 질문과 단순 유지·더 안쪽 목표·기존 안정화/피드백 대안의 서로 다른 예측을
구분할 작은 관찰이 필요하다. 현재 결과나 최종 novelty를 추가 진입 gate로 쓰지 않으며
같은 grid/threshold/seed 확대는 선택하지 않는다. [사례와 범위](../pilot_studies/q15-reward/README.md#hold-results-2026-09-22)를 보존한다.

## Interpretation and next investment

- 차이가 없거나 scale control/학습 진행도로 설명되면 이 조작에서는 복잡한 robust
  reward selection을 도입할 근거가 약하다는 정보를 얻는다. 같은 grid 확대를 자동 선택하지 않는다.
- 물성 조건별 차이가 관찰되면 먼저 실제 실패 사례와 nominal 성능·seed 변동을 해석한다.
  그 사례가 요구하는 가장 싼 후속 대조를 선택하며 곧바로 새 principle로 승격하지 않는다.
- Uniform DR, potential-based shaping, validation-based reward selection은 다음 설명을
  구분할 강한 대안이다. 이들을 첫 관찰의 필수 gate로 전부 구현하지 않는다. 이 대안들을
  배제하지 않은 결과로 robust selection method의 필요성이나 새 optimality claim을 쓰지 않는다.
- 모든 reward가 task를 배우지 못하거나 물성 개입이 성립하지 않으면 학습/측정 한계로
  기록한다. Q15 전체가 반증된 것으로 처리하지 않는다.

## Recovery and boundaries

읽기 전용 source는 `external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8/`다.
파일·immutable URL·SHA256은 [comparison_sources.json](../related_work/comparison_sources.json)의
`q3_followup_q15_selection_20260918`이 소유한다. 새 dataset/model download는 필요하지
않으며 pre-existing Isaac image를 사용하지 않는다. 실제 recipe/command/lock/mount는
[Q15 study README](../pilot_studies/q15-reward/README.md#runtime-and-recovery)에 기록했다.

Simulation-only state-policy 관찰은 sim-to-sim sensitivity만 지지한다. Real-world transfer,
VLA generalization, 최종 reward 순위 또는 논문 기여는 아직 없다. 사용자가 이미 선택한
Robotics scope의 작은 학습 관찰이며 추가 scope 선택이나 유료 API 호출은 요구하지 않는다.
