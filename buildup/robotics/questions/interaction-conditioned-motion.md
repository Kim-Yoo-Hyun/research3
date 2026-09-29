# Q16 Predictive Policy Adaptation

Updated: 2026-09-28

Status: `deferred` — 현재 공식 2D 정책에서 예측 선택의 별도 성공 이득을
관찰하지 못했다. 새 paired seed의 짧은 재계획 대조도 8-step 7/16 대비
2-step 6/16, 구제 2건·악화 3건이어서 순구제가 없고 추론 비용이 약 4.19배였다.
3D Can PH 자료의 저장 행동 재생 parity도 사전 기준을 실패해 해당 route를
보류했다. [2026-09-28 선택](../../selection.md#q16-shorter-chunk-outcome-and-investment-decision-2026-09-28)은
현재 방법·자료 경로의 투자 보류이며 넓은 Q16 질문의 반증이 아니다. 다른
대표 조건에서 예측 보정 효과는 아직 미검증이다.
실행 설정·수정·결과와 개발 범위는 [study owner](../pilot_studies/q16-motion/README.md)를 따른다.

**잠정 설명과 재진입 기준:** 학습된 행동 묶음이 물체의 운동·접촉 변화에 대응하지
못하는 일부 실패에서는 예정 행동의 결과를 예측하는 것이 유용할 수 있다. 그러나 현재
2D 관찰은 예측 선택의 별도 성공 이득을 보이지 않았고, 단순 피드백·빠른 재계획과의
차이도 아직 입증되지 않았다. DynaGuide와 Feedback World Model은 예측과 피드백을
이미 다루므로, 단순히 이를 결합하는 것은 차별점이 아니다. 새 paired 관찰에서도
짧은 재계획의 순구제가 없었다. 더 투자하려면 단순 관측 피드백·재계획이 설명하지
못하는 대표 실패 조건과 같은 정보의 강한 정책 대안을 먼저 제시하고, 그 차이를
가를 타당한 paired 평가의 비용을 산정한다. 그 전에는 현재 2D 보정 경로를
재조정하지 않고 다른 후보와 비교한다.

## Development direction recorded 2026-09-23

**물체의 운동과 접촉 조건이 달라질 때, 미래 궤적 예측과 실행 피드백으로 학습된 조작
정책을 어떻게 적응시킬 수 있는가?** 작은 데이터와 계산 비용으로 기존 행동을 재사용하는
것을 개발 목표로 둔다. Dynamic manipulation, model-based policy adaptation과
world-model-guided control의 흐름에 해당한다.

현재 많은 manipulation policy는 training demonstration의 조건에 영향을 받는다.
동적 물체와 상호작용할 때는 관측 갱신뿐 아니라, 예정 행동이 물체 상태를 어떻게 바꾸는지와
실제 실행이 예측에서 얼마나 벗어나는지를 함께 다루는 것이 유용할 수 있다. 이는 검증할
설명이며 모든 기존 policy의 실패나 아직 해결되지 않은 빈 영역이라는 주장은 아니다.

사용자는 시의성과 발전 방향이 있으면 초기 결과가 작더라도 진행할 것을 요청했다.
이를 반영해 당시 단일 cube의 잔여 실패를 찾는 데 질문을 제한하지 않고 **learned action-chunk
policy + multi-step dynamics + execution feedback**의 방법 개발을 진행했다. 첫 task는
잡기·운반과 밀기를 실행했다. 관측 pose/geometry는 이후 시각 입력으로 확장할 연결점이다.
새 Q를 만들거나 formal hypothesis로 승격한 것은 아니다.

첫 [정책 적응 결과](../pilot_studies/q16-motion/README.md#adaptation-results-2026-09-23)는
moving 조건에서 learned policy 9/32, fixed predictive correction 32/32였으나 단순 CV도
32/32였다. 직전 예측 오차를 단순 bias로 추가한 방법은 29/32였다. World model에는
policy 시연 외의 moving teacher data가 들어갔다. 이 결과는 현 정책의 보정 가능성과
현재 task의 강한 단순 대안을 동시에 보여준다. Feedback adaptation·data efficiency·
다른 과업의 성능을 주장하기 전에 pushing과 같은 데이터 예산 대조가 필요했다.

[밀기 결과](../pilot_studies/q16-motion/README.md#revised-result-interpretation-and-preservation)는
같은 추가 데이터로 정책을 갱신한 대안과 native `PushCube-v1` goal을 비교했다. 새 초기 상태
양 조건에서 단순 feedback 16/16, frozen·갱신 정책 13/16, 접촉 상태에 제한한 예측 보정
6/16이었다. 잡기의 보정 이점은 이 지속 접촉 과업으로 일반화되지 않았다. 접촉 상태에
작은 residual bias를 더 조정하는 대신 관측 불완전성 또는 물체 변화의 대표 조건에서
같은 정보를 받는 단순 대안과 다시 비교한다. 이는 현재 방법의 기여가 검증됐다는 뜻이 아니다.

[지연 관측 결과](../pilot_studies/q16-motion/README.md#delayed-observation-result-and-boundary)는
물체 pose/velocity만 4 control steps 늦췄다. Native goal의 새 초기 상태에서 지연
feedback과 지연 속도 외삽 feedback은 nominal/저마찰 각각 16/16, frozen policy는
각각 9/16, 동일 추가 데이터 갱신 policy는 각각 10/16, model-guided는 6/16·9/16이었다.
진단용 현재 상태 feedback도 16/16이었다. 관측 지연은 정확히 검증됐지만 이 task의
기하학적 feedback 행동과 성공을 실질적으로 바꾸지 못했다. 이 무차이를 model-based
policy adaptation의 반증으로 옮기지 않는다. [후속 비교](../pilot_studies/q16-motion/README.md#contact-task-comparison-and-selection)는
`PushT-v1`을 다음 개발 과업으로 잠정 선택했다. 두 과업의 단순 제어는 native 성공
0/8이었고 현재 변형에서 공식 T 시연도 재생되지 않았다. 다음은 source/backend를 맞춘
시연과 동일 관측 정책 대안의 실행 가능성을 확인한다.

[DynaGuide](https://arxiv.org/html/2506.13922v2)는 dynamics로 frozen diffusion policy를
유도하고, [Feedback World Model](https://arxiv.org/html/2605.15705v1)은 관측 피드백과
action-aware guidance를 결합한다. [DyWA](https://arxiv.org/html/2503.16806v2)는 동역학 적응을
비파지 조작에서 다루며, [DynamicWAM](https://arxiv.org/html/2608.00793v2)은 동적 조작에서
motion-conditioned world/action prediction을 다룬다. 논문들의 방법 범위는 시의성의 근거다.
Feedback World Model과 DynamicWAM은 확인한 2026 preprint이며 저자 성능 주장을 재현한
것은 아니다. 직접 중복도 인정하며 구체적 차별점은 개발하면서 찾아간다.
[비교·읽은 범위](../related_work/policy-geometry.md#q16-policy-adaptation-direction-2026-09-23)를 따른다.

## First outcome 2026-09-23

다섯 controller가 static/sliding 각각 24/24 성공했다. Action-conditioned model은 validation
접근/closing 예측 오차를 줄였지만 closed-loop 성공 이점은 관찰하지 못했다. 학습 자료 수집
160회, evaluation 240회와 raw state 32,400개 검산을 완료했다.
[결과·해석·한계](../pilot_studies/q16-motion/README.md#results-2026-09-23)를 따른다.
현재 단순 full-state task에서 feedback의 충분성을 확인한 것이며 broad 질문의 반증은 아니다.
실제 구현은 0.1 s 단일 예측과 xy 후보 선택에 한정됐고 transport는 규칙 feedback이었다.
후속 정책 적응 연구 전체를 판단한 결과가 아니다. 현재 개발 결정은 위 방향과
[구체적 계획](../pilot_studies/q16-motion/README.md#method-development-2026-09-23)을 따른다.

## Initial question and significance

아래는 첫 관찰을 시작한 질문이다. 현재 연구 방향은 위와 같이 정책 적응으로 넓혔다.

**움직이는 물체를 잡을 때, 로봇의 예정 행동이 물체 운동에 미치는 영향을 예측하면
관측 이력만으로 미래 위치를 예측하거나 자주 재계획하는 것보다 적은 상호작용 데이터로
접촉 전후의 grasp-and-transport 성공을 높일 수 있는가?**

예를 들어 미끄러지는 물체의 미래 위치에 손을 보내더라도 손가락이 먼저 닿으면 물체가
밀리거나 회전한다. 이후의 목표 위치는 기존 속도뿐 아니라 다음 로봇 행동에도 달려 있다.
이때 더 빠른 피드백으로 충분한 조건과 행동을 고려한 예측이 유용한 조건을 구분한다.
이는 dynamic manipulation, model-based control, data-efficient policy adaptation의 질문이다.
접촉 자체를 검출하거나 motion prediction 오차만 줄이는 것을 최종 목표로 삼지 않는다.

## Evidence and closest work

| Primary source | 확인한 범위와 이 질문에 주는 제약 |
| --- | --- |
| [SIDO](https://arxiv.org/html/2607.27890v1), §4.1–4.3 | Static demonstration에서 dynamic target용 action을 증강한다. 증강 대상은 action chunk가 grasp 시점 전에 끝나는 구간이다. 이것은 논문의 범위이며 접촉 후 실패를 입증하지 않는다. DynaSIDO의 robot dynamics와 trajectory optimization도 이미 존재한다. |
| [DynamicVLA](https://arxiv.org/html/2601.22153v1), method와 task appendix | Continuous inference/latency-aware execution, grasp 단계별 제어와 접촉으로 운동이 바뀌는 task를 다룬다. Dynamic contact handling 자체를 미해결 또는 새 기여라고 쓰지 않는다. |
| [Action-conditioned Face Interaction Graph Networks](https://arxiv.org/html/2509.12151v1), abstract/introduction | Action-conditioned contact dynamics와 MPC가 직접 선행이다. 예정 행동을 predictor에 추가한다는 사실만으로 차별화되지 않는다. |
| [Reactive Diffusion Policy](https://www.roboticsproceedings.org/rss21/p052.html), paper introduction | Slow-fast visual-tactile feedback가 contact-rich manipulation을 다룬다. Fast correction이나 contact feedback 자체도 새 기여가 아니다. |
| [Language-Driven Closed-Loop Grasping](https://arxiv.org/html/2406.09039v1), abstract/introduction | Online model-predictive trajectory replanning은 반드시 고려할 단순/기존 제어 대안이다. |

**에이전트의 잠정 설명:** 관측 이력만으로는 아직 실행하지 않은 서로 다른 행동이 만드는
물체 운동을 구분하기 어렵다. 다만 이 차이가 실제 제어에서 중요한지는 feedback 속도,
접촉 전환과 학습 데이터에 달려 있다. 작은 action-conditioned model이 충분할 수 있다는
설명은 미검증이며, 위 선행보다 우수하거나 novel하다는 판단은 아직 없다.

## Provisional method

Nominal demonstrations로 작은 state-based Diffusion Policy를 학습한 뒤 weights를 고정한다.
최근 관측·행동과 candidate action sequence로 여러 step의 object/robot trajectory를
예측하고, task progress와 원래 policy 행동의 보존을 고려해 chunk를 수정한다. 짧게 실행한
뒤 실제 state와 예측의 차이를 context에 반영한다. 처음부터 foundation model을 학습하지 않는다.

단순 frozen policy, 빠른 재계획과 geometric feedback, 피드백 context가 없는 predictive
correction을 순차적으로 대조한다. 새 dynamics data의 비용도 포함한다. Module 조합 자체를
기여라고 쓰지 않으며, 실패의 원인과 필요한 model form을 사례·학습 과정에서 수정한다.
첫 prototype부터 최종 novelty와 여러 benchmark의 성공을 동시에 요구하지 않는다.

## First observation

아래는 선택 당시의 초안이다. 실제 CPU 실행, model 적용 구간과 raw-state 검사는
[study owner](../pilot_studies/q16-motion/README.md#observation-configuration)가 소유한다.

- **구성:** 새 workspace Docker에서 ManiSkill의 dynamic rigid cube를 잡아 정해진 위치로
  옮기는 단일 task를 만든다. Static control과 sliding 조건부터 시작한다. 운동은 물리 초기
  속도/힘으로 만들고 접촉 중 pose를 강제로 덮어쓰지 않는다. 기존 PickCube benchmark 결과로
  보고하지 않으며 task와 판정식을 명시한다.
- **관측:** 첫 비교는 simulator object state와 robot proprioception을 공통 입력으로 써서
  perception 영향을 분리한다. 미래 state와 GT contact/grasp flag는 평가·진단 전용이다.
  Simple phase switch도 공통 관측의 거리·상대 운동·gripper state로 계산한다.
- **대조:** (1) 현재 위치를 따르는 feedback servo, (2) constant-velocity prediction과
  단순 approach/grasp/lift 전환, (3) history-only learned prediction,
  (4) 위 action-conditioned residual model을 비교한다. Learned pair는 동일 데이터·후보
  행동·planner·update rate를 사용한다. 가장 강한 단순 제어의 더 짧은 재계획 주기도 함께
  읽되 추가 연산·관측 비용을 보고해 동일 비용 효과와 분리한다.
- **작은 방법 시도:** 공통 controller의 제한된 행동 변형으로 최대 500개 짧은 학습 rollout을
  모으는 초안이다. 평가 initial state/velocity는 episode 단위로 분리한다. 우선 24개 초기
  상태의 static/sliding paired rollout에서 세부 실패를 읽고 model 비교까지 한 묶음으로
  시도한다. Episode 수는 탐색 예산이며 효과를 본 뒤 바꾸면 변경 이유를 기록한다.
- **측정:** 정해진 시간 내 grasp-and-transport 성공, 접촉 후 놓침/재접촉, 완료 시간,
  inference/planning latency, 학습 interaction 수. 예측 오차는 설명용이다. 성공·놓침을
  실제 object/gripper state 및 작은 영상 사례로 교차 확인한다. 같은 초기 상태에서 시작하고
  임의의 중간 simulator snapshot이 완전 복원된다고 가정하지 않는다.
- **예산:** 첫 구현과 관찰을 약 2 working days, GPU 실행 8시간 이내로 제한하는 추정이다.
  측정된 runtime 보장이 아니다. 준비가 길어지면 task/controller를 단순화하고 이유를 기록한다.
  Strong external VLA의 전체 재현을 이 첫 관찰의 선행조건으로 추가하지 않는다.

## What the observation can teach

1. 단순 feedback/phase switch로 충분하면 그 조건과 비용을 기록한다. 임의 noise나 기준
   변경 없이 대표 과업·learned policy로 방법을 발전시킬 수 있으며, 좁은 잔여 실패의 존재를
   계속 진행하기 위한 필수조건으로 두지 않는다.
2. Prediction 오차만 개선되고 행동 성공은 같으면 현재 predictor의 제어상 필요성을 지지하지
   않는다. Planner 또는 학습 분포 문제인지 사례로 구분한다.
3. 같은 데이터·계산 조건에서 접촉 후 실패가 줄면 action input 제거, 전환 구간 제거 등으로
   원인을 좁힌다. 이후 shape/mass/friction 변화와 관측 pose 오류로 확장할 수 있다.
4. Model/controller가 기본 grasp조차 못하면 설명의 반증으로 세지 않는다. 작은 수리의 가치와
   비용을 판단하며 전체 source audit나 큰 benchmark 구축으로 자동 확대하지 않는다.

## Access and boundary

Workspace에 공개 ManiSkill source `a4a4f9272ad64b1564035874b605ceb687b63ed8`의
dynamic PickCube와 diffusion-policy example 파일이 있다. Q16은 별도의 CPU Docker에서
collision-only cube task와 작은 supervised dynamics model을 구현·실행했다. Diffusion policy
example 자체나 공식 VLA baseline을 재현한 것은 아니다.
[DynamicVLA official repository](https://github.com/hzxie/DynamicVLA)는 code/data/model 경로를
공개하지만 Isaac Sim 4.5.0 / Isaac Lab 2.2.1 환경과 별도 취득이 필요하다. README만 확보했고
기존 host Isaac 자산을 사용하지 않는다. 공식 baseline의 full reproduction은 후속 비교다.

이 관찰은 state-based constructed simulation이며 vision/VLA, real robot, 일반 contact
manipulation의 성능을 주장하지 않는다. Q15의 reward/성공 후 hold 질문과 구분하며 기존
결과를 새 증거로 재사용하지 않는다. CD5를 보류한 사용자 요청과 후보 비교 근거는
[선택 기록](../../selection.md#q16-selection-2026-09-23)이 소유한다.

## Feasibility boundary recorded 2026-09-27

`PushT-v1`의 공식 시연과 같은 31D state 관측에서 BC·PPO 실행 경로는 확보했지만,
[행동 분기 진단](../pilot_studies/q16-motion/README.md#paired-action-diagnosis-2026-09-26-exploratory-protocol-before-execution)은
반복 BC 제어의 결과가 달라 현재 native CUDA 중간 상태를 인과적인 후보 행동 비교에
사용할 수 없음을 보였다. 이는 예측 기반 적응의 일반적 실패를 뜻하지 않는다.
현재 설명 초안은 유지한다. 공개 2D `gym-pusht`에서 약한 학습 정책의 접촉
실패와 안정적인 반복 분기 두 사례를 확인해 [개발용 경로로 선택했다](../pilot_studies/q16-motion/README.md#alternative-contact-task-assessment-2026-09-26-protocol-before-execution).
같은 상태의 단순 feedback과 행동 조건 예측 대안은 [두 개발 사례에서 비교했다](../pilot_studies/q16-motion/README.md#same-state-action-selection-contrast-2026-09-27-exploratory-protocol-before-execution).
현재 kNN/pose-score 선택은 feedback보다 낫지 않았고, 후보 행동 오차와 native
overlap 불일치가 드러났다. [공식 low-dimensional Diffusion Policy의 원본 환경
실행](../pilot_studies/q16-motion/README.md#released-low-dimensional-policy-compatibility-2026-09-27-protocol-before-execution)에서는
새 초기 상태 4/8 성공과 접촉 근접 실패 세 곳을 확인했다. 그중 두 곳은 원래
정책이 반복 재현됐고 한 곳의 행동 변경은 진단용 simulator-state feedback과
임의 offset 모두 성공으로 바뀌었다. 이는 모델 이득이 아니라 행동 민감도다.
이어 [관측 동일·새 seed 16개 비교](../pilot_studies/q16-motion/README.md#observation-matched-policy-continuation-2026-09-27-exploratory-protocol-before-execution)에서
frozen/feedback/prediction/작은 정책 갱신은 8/16·8/16·8/16·4/16이었다.
예측 선택은 네 행동을 바꿨으나 frozen 실패를 구하지 못했다. 저장 시연의
keypoint와 기록 state 사이 일부 불일치는 입력 검증의 한계로 남겼다.
3D robomimic Can의 다른 실패 조건·관측 정보·비용·반복성을 판단할 첫
[Can PH v1.5.1 자료 감사](../pilot_studies/q16-motion/README.md#3d-can-route-feasibility-2026-09-27-exploratory-protocol-before-data-access)는
23D 물체/robot 관측, 7D 행동, 200개 시연의 state/XML을 확인했다.
당시에는 구형 checkpoint의 호환성과 실제 행동 재생이 미측정이었다. 이후
[Can PH 재생](../pilot_studies/q16-motion/README.md#can-action-replay-protocol-2026-09-27-before-simulator-execution)은
저장 state·관측 parity를 실패했고, [짧은 재계획 대조](../pilot_studies/q16-motion/README.md#shorter-action-chunk-comparison-2026-09-27-prospective-protocol)는
순구제가 없었다. 최신 status와 재진입 조건은 문서 첫머리와
[선택 기록](../../selection.md#q16-shorter-chunk-outcome-and-investment-decision-2026-09-28)을 따른다.
