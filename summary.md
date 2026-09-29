# Research Summary

Updated: 2026-09-29

## Current State

- Phase: `research scoping active`; primary scope Robotics, supporting 3D Vision.
- 가장 최근 개발한 Q16 Predictive Policy Adaptation의 현 2D 방법 경로는 `deferred`다.
  공식 Diffusion Policy의 같은 관측 비교에서 예측 선택은 frozen/단순 feedback보다
  별도 성공 이득을 보이지 않았다. 새 seed의 [8-step 대 2-step 대조](buildup/robotics/pilot_studies/q16-motion/README.md#shorter-action-chunk-comparison-2026-09-27-prospective-protocol)는
  7/16 대 6/16, 구제 2·악화 3, 2-step의 추론 시간 4.19배였다. 32개 trace의 독립
  재생과 paired 초기 상태·첫 두 행동/상태 검증이 통과했다.
- 3D Can PH의 현재 자료/runtime 행동 재생은 저장된 다음 state·관측의 사전
  parity 기준을 실패해 보류한다. 이 두 결과는 Q16의 넓은 질문을 반증하지 않는다.
- [최신 선택](buildup/selection.md#q17-selection-2026-09-28)에 따라 Q17
  Evidence-Conditioned Action Selection을 다음 제한된 탐색 질문으로 골랐다.
  ActiveArena 한 hidden-color 과업에서 정보 획득, 목표 선택, 물리 실행의 실패를
  구분한다. 공개 학습 시연 100/100의 텍스트에 정답 색상이 있고 공식 fixed-seed
  `unseen` 지시문에서는 각 split의 0/250개만 정답을 밝힌다. 따라서 시연만으로
  시각 단서 이용을 판정할 수 없다. 같은 현재 상태의 두 **학습** 시연에서 전체
  과거 화면은 현재 화면만 쓸 때보다 행동 모방 L1을 낮췄으나, 색 단서만의 효과와
  실제 목표 선택/실행은 미분리다. 보조 생성 문장은 두 색 모두 정확히 식별하지
  못했다. `check_block_color`의 첫 공식 ID seed 세 사례를 공개 checkpoint의
  탐색용 Docker bridge로 실행했지만, 정책에 전달된 화면에서는 색 단서가
  판독되지 않았고 pad 선택도 판정 불가였으며 native 성공은 없었다. 따라서
  정보 획득 후 목표 결합 오류는 그 과업에서 미검증이다. 대체
  `count_color_kinds_press_button`의 첫 공식 ID 사례에서는 빨강·초록·파랑이
  정책 입력 화면에 보인 뒤, 정답 3번 대신 2번 버튼을 실제 눌러 native 실패했다.
  이는 한 사례의 가시적 단서 이후 오답이며 count·단서 이용·버튼 실행 중 원인은
  미분리다. 원본과 89 step·6 request가 정확히 일치하는 재생에서 80번째 동작의
  count 3/버튼 3 oracle 문장은 행동을 조금 바꿨으나 다시 2번 버튼을 눌렀다.
  당시 팔은 이미 2번 버튼 위에 있었다. 네 블록이 보이고 팔이 버튼에서 떨어진
  step 48에서 동일 입력·상태로 정답 문장만 바꾼 분기도 행동은 달라졌지만 다시
  2번 버튼을 눌렀다. 이 한 사례로 count·기억·언어 반응·실행 원인은 분리되지
  않아 현재 color-count 경로의 반복을 멈췄다. [다른 과업군·후보 비교](buildup/selection.md#q17-task-family-reassessment-2026-09-29)에서
  ML 회전 시점의 첫 ID 사례만 다음 관찰로 골랐다. 초기에는 목표 green 블록이
  가려져 있다가 회전 뒤 보이는지와 첫 집기 대상을 확인한다. 이 과업은 색·순서를
  지시에 명시하므로 숨은 색 추론 결과로 해석하지 않는다.
  CD5의 사용자 보류는 유지한다.
- Q17의 [탐색 study](buildup/robotics/pilot_studies/q17-evidence/README.md)가 진행 중이다.
  Selected formal hypothesis, paper experiment 또는 contribution claim은 없다.

## Selected exploratory direction

**능동적 관찰로 과업 정보를 얻은 뒤, 정책은 이를 올바른 다음 조작 대상·목표·행동에
연결하는가?** [ActiveArena](https://arxiv.org/html/2609.24124)는 관련 과업과 공식
정책·평가 경로를 제공한다. 논문에서 보고한 `Context Retained` 실패는 관련 물체가
최종 화면에 보인 경우일 뿐 정보 이용 오류와 조작 실행 오류를 분리하지 않는다.
한 hidden-color 과업의 source annotation과 소수의 같은 현재 상태 정책 입력 대조로
이 차이를 먼저 확인했다. 공개 시연의 텍스트는 목표 색상을 알려 주므로 시각적
증거 이용의 단독 근거로 사용하지 않는다. 첫 held-out 세 사례에서는 색이 정책
입력에서 판독되지 않아 pad 선택을 평가할 수 없었다. 대체 색-종류/버튼 과업의
첫 사례에서는 세 색이 정책 입력에 보인 후 오답 버튼이 실제 눌렸다. 첫 화면부터
세 색 종류가 상당 부분 보였으므로 기억 병목의 증거로 사용하지 않는다. 늦은
oracle-count 문장은 이미 2번 버튼 위에 있는 팔을 바꾸지 못했다. 버튼 접근 전
step 48의 answer cue도 실제 버튼 선택을 바꾸지 못해 원인 분해는 여전히 열려 있다.
다른 과업군·후보를 비교해 ML 회전 시점의 단일 첫 집기 관찰을 선택했다. 가까운
ActiveArena subtask/planner, PALM, memory·active-view 대안과 구분되는 조건은 아직
미확정이다. [Q17 질문·범위](buildup/robotics/questions/evidence-conditioned-action-selection.md)를
따른다.

## Most recent developed question and direction (deferred)

**물체의 운동과 접촉 조건이 달라질 때, 미래 궤적 예측과 실행 피드백으로 학습된 조작
정책을 어떻게 적응시킬 수 있는가?** 작은 데이터와 계산 비용으로 기존 행동을 재사용하는
것을 개발 목표로 둔다.

Dynamic manipulation, world-model-guided control과 data-efficient policy adaptation에 속한다.
첫 방법은 learned action chunk와 multi-step object/robot dynamics를 연결했다. 관측-예측
오차를 다음 행동에 반영하는 대안도 비교했다. 잡기·운반과 지속 접촉의 밀기로 확장했다.
기존 단일 displacement 관찰을 이 전체 방법의 검증으로 보지 않는다. 질문·선행은
[Q16 record](buildup/robotics/questions/interaction-conditioned-motion.md), 실행·수정·결과는
[study owner](buildup/robotics/pilot_studies/q16-motion/README.md)가 소유한다.

## Prior evidence and claim boundary

[DynaGuide](https://arxiv.org/html/2506.13922v2)와
[Feedback World Model](https://arxiv.org/html/2605.15705v1)은 dynamics/feedback로 diffusion
policy를 유도한다. [DyWA](https://arxiv.org/html/2503.16806v2)와
[DynamicWAM](https://arxiv.org/html/2608.00793v2)은 물성·물체 운동 변화에 대한 적응과
motion-conditioned prediction을 다룬다. 이는 시의성과 직접 선행의 근거이며 검증된
빈 연구 영역이라는 뜻은 아니다. 저자 결과를 직접 재현하지 않았고 2026 두 논문은
확인한 preprint다. [방향 검토](buildup/robotics/related_work/policy-geometry.md#q16-policy-adaptation-direction-2026-09-23)를 따른다.

[SIDO](https://arxiv.org/html/2607.27890v1)의 pre-grasp augmentation은 출발점이며 접촉 후
실패를 입증하지 않는다. [DynamicVLA](https://arxiv.org/html/2601.22153v1)는 접촉으로 물체 운동이
바뀌는 task를 다룬다. [Action-conditioned contact dynamics](https://arxiv.org/html/2509.12151v1)와
[RDP](https://www.roboticsproceedings.org/rss21/p052.html)는 dynamics+MPC와 contact feedback의
직접 선행이다. Action input이나 작은 model을 붙인 사실을 기여로 삼지 않는다.
[후보 비교·읽은 범위](buildup/robotics/related_work/policy-geometry.md#candidate-replacement-2026-09-23)를 따른다.

## First observation and evidence

Panda가 처음부터 정지하거나 미끄러지는 cube를 잡아 공중 목표로 옮기는 state-based task를
구성했다. Object pose/velocity와 proprioception은 공통 입력이고 contact/grasp flag는
평가 전용이다. Native finger-force predicate와 목표 거리로 마지막 5 states의 성공을 판정했다.

현재 위치 servo, constant-velocity prediction, history-only MLP, action-conditioned MLP,
20 Hz CV 재계획 **다섯 route 모두 static/sliding 각각 24/24 성공했다.** Release도 없었다.
Model은 접근/closing에만 적용하고 transport feedback은 공유했다.
두 MLP는 7,299 parameters와 128 training/32 validation episodes를 공유했다.

| Validation prediction | Approach/closing RMSE | All-phase RMSE |
| --- | ---: | ---: |
| Constant velocity | 4.029 mm | 9.745 mm |
| History-only | 4.634 mm | 5.479 mm |
| Action-conditioned | 0.527 mm | 0.293 mm |

이 RMSE는 checkpoint 선택에 사용한 validation 결과다. Closed-loop evaluation은 별도
24 initial seeds × static/sliding으로 수행했다. 두 learned route의 행동·궤적은 달랐지만
성공 이점은 없었다. Sliding CV는 첫 관측 finger contact 직전 속도 median 0.085 m/s로,
모두 정지한 물체만 잡은 결과는 아니다.

**검증:** 400 train/evaluation episodes, raw states 32,400개, decision rows 17,920개의
force-based grasp, goal/sustained success, release, action/feature/target 및 episode split을
검사했다. Evaluation의 48 paired 초기 상태도 일치했다. 상세 근거는
[결과·검산](buildup/robotics/pilot_studies/q16-motion/README.md#verification-preservation-and-cleanup)을 따른다.

## Earlier observations and interpretation

이하 결과와 당시 후속 계획은 Q16의 탐색 이력이다. 현재 선택과 다음 작업은
문서 첫머리와 [TODO](TODO.md)를 따른다.

**에이전트 판단:** 현재 full-state 단일 cube와 feedback 조건에서 단순 제어가 충분했다.
예측 정확도 개선만으로 learned model의 제어상 필요성을 주장할 수 없다. 포화된 24개
paired 조건은 모든 dynamic manipulation에서 model이 불필요하다는 반증도 아니다.

**후속 구현·관찰:** static teacher 128 training/32 validation episodes로 학습한 작은
state-conditioned action-chunk diffusion policy와, 추가 moving teacher 48 training/16
validation episodes를 사용한 8-step object/TCP model을 연결했다. 첫 정책은 grasp 전에
gripper를 닫는 실패를 보여 supervised action head를 추가했다. 수정 뒤 새 초기 상태 32개 ×
세 조건 × 여섯 route의 576회를 비교·검산했다.

| 조건 | CV feedback | Learned policy | Predictive correction | Feedback-adjusted correction |
| --- | ---: | ---: | ---: | ---: |
| Static | 32/32 | 32/32 | 32/32 | 32/32 |
| Moving | 32/32 | 9/32 | 32/32 | 29/32 |
| Moving + friction 0.05 | 32/32 | 31/32 | 32/32 | 32/32 |

**에이전트 판단:** 예측 기반 행동 보정은 이 학습 정책의 moving 실패를 줄였다.
단순 CV도 모든 조건에서 성공했고 학습·추론 비용이 더 작다. 실행 오차를 단순 bias로
더하면 fixed correction보다 moving 세 사례가 악화됐다. World model은 추가 moving data를
썼으므로 데이터 효율성이나 model-only 효과를 주장할 수 없다. 자세한 분모·대안·실패
사례·latency는 [후속 결과](buildup/robotics/pilot_studies/q16-motion/README.md#adaptation-results-2026-09-23)를 따른다.

**밀기 관찰:** pinned ManiSkill `PushCube-v1`의 시각 요소를 제거한 CPU 변형에서 native
goal radius 0.1 m와 50-step 판정을 유지했다. 96+24 nominal 및 32+8 저마찰 시연,
동일 추가 데이터를 사용한 정책 갱신과 동역학 학습을 수행했다. 첫 192회 평가 결과로
접촉 상태에서만 작게 보정하는 수정안을 만들고, 새 초기 상태 16개 × 두 조건 × 여덟
route의 256회를 검산했다.

| 새 밀기 조건 | 단순 feedback | Frozen policy | 동일 추가 데이터 policy | 원래 예측 보정 | 접촉 조건 보정 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Nominal | 16/16 | 13/16 | 13/16 | 4/16 | 6/16 |
| Low friction | 16/16 | 13/16 | 13/16 | 2/16 | 6/16 |

**에이전트 판단:** 수정 보정은 원래보다 낫지만 frozen policy의 성공을 같은 초기 상태에서
각 조건 7개씩 해쳤고, rescue는 없었다. 시연 validation의 8-step object-position RMSE
0.00397 m는 후보 행동 선택의 신뢰성을 보장하지 않았다. 단순 residual bias를 이 설정에서
더 조정하기보다, 같은 정보·데이터를 받는 단순 feedback/정책/보정 대안을 대표 조건에서
비교한다. 이는 Q16 방향을 넓히는 관찰이지 예측 방법의 기여나 데이터 효율성 주장으로
승격한 것이 아니다. [밀기 결과](buildup/robotics/pilot_studies/q16-motion/README.md#revised-result-interpretation-and-preservation)를 따른다.

**지연 관측 후속:** 같은 `PushCube-v1`의 물체 pose/velocity에만 4-step(0.2 s) 지연을
적용하고, 현재 로봇 상태·목표는 공유했다. 새 초기 상태 16개 × nominal/저마찰에서
지연 feedback와 지연 속도 외삽 feedback 모두 각 16/16, frozen policy 각 9/16,
동일 추가 데이터 policy 각 10/16, model-guided policy 6/16·9/16이었다. 192회 평가의
지연·native 판정·paired reset을 검산했다. **에이전트 판단:** 이 과업의 초기 정지 물체와
고정 목표 기반 push 제어에서는 지연이 단순 feedback의 행동을 거의 바꾸지 않았다.
따라서 prediction의 유효성을 판정하기보다 접촉 중 object-relative correction이 계속
필요한 공개 과업을 비교한다. [지연 관찰](buildup/robotics/pilot_studies/q16-motion/README.md#delayed-observation-result-and-boundary)을 따른다.

**다음 과업 선택:** collision-only CPU 변형의 8개 같은 초기 상태에서 `PushT-v1`의
평균 최종 T 영역 중첩률은 zero-action 0.288, 현재 물체 feedback 0.375, 초기 상태
고정 reference 0.331이었다. `RollBall-v1`의 평균 목표 거리는 각각 1.451, 1.439,
1.440 m였다. 두 과업·세 route 모두 native 성공 0/8이고, T feedback이 고정 대조보다
좋은 seed도 3/8뿐이다. **에이전트 판단:** 물체 위치·회전의 계속적인 접촉 조정을
보려는 Q16에는 `PushT-v1`이 더 적합해 다음 개발 과업으로 잠정 선택한다. 공식
시연 888개 성공 에피소드의 행동과 초기 상태를 현재 변형으로 재생한 8개는 모두
실패했다. 생성 ManiSkill commit/PhysX CUDA와 현재 commit/CPU 변형이 달라 원인은
분리되지 않았다. Source-matched/native 재생과 동일 관측·데이터 policy 대안이 먼저
필요하며, 현재 결과는 prediction의 이점이나 최종 과업 성능을 뒷받침하지 않는다.
[비교·재생 기록](buildup/robotics/pilot_studies/q16-motion/README.md#contact-task-comparison-and-selection)을 따른다.

**시연 호환성·정책 대안 후속 (2026-09-25):** 생성 ManiSkill commit과 100/20 Hz,
기록 초기 상태를 맞춘 CPU 재생은 0/8, 원본 `PushT-v1`/PhysX CUDA 재생은 최종 2/8
성공이었다. 공식 replay 도구도 같은 여섯 시연을 실패로 판정했고, 원본 CUDA와
시각 요소만 제거한 CUDA adapter의 여덟 trace는 동일했다. 따라서 이전 CPU의 즉시
관절 궤적 오차에는 backend 차이가 중요했지만, 생성 시연 전체가 현 런타임에서
행동 재생 가능한 자료라고 주장할 수 없다. 기록 상태에서 source-matched `state`
관측 31D/행동 3D를 복원해 검산했다. 동일 관측의 단순 behavioral cloning은
64개 학습 시연에서 새 seed 1/8, 792개 학습 시연에서 **별도의** 새 seed 12/16;
공식 pretrained PPO는 각각 8/8, 16/16이었다. 후속 확대는 첫 결과를 본 뒤 진행한
탐색이고 PPO는 다른 RL 데이터를 썼다. 이는 Q16의 실행 가능한 단순 policy 대안과
네 실패 사례를 제공할 뿐, 예측 보정의 이점이나 데이터 효율성을 입증하지 않는다.
당시 계획은 같은 접촉 상태의 기본/단순 feedback/예측 행동을 실제 결과와 짝지어
비교하고, 같은 추가 데이터를 받는 정책 갱신을 대조하는 것이었다.
[호환성·정책 경계](buildup/robotics/pilot_studies/q16-motion/README.md#pusht-demonstration-compatibility-2026-09-25)를 따른다.

**행동 분기 타당성 후속 (2026-09-26):** 기존 792/88개 시연으로 행동 조건
one-step model을 학습해 검증 전이의 물체 XY/yaw RMSE 0.00131/0.00179 m,
0.01624 rad를 얻었다. 그러나 이전 BC 실패 네 사례를 실제 행동 결과와
짝지으려던 세 진단은 모두 재생 또는 상태 복원 일치 검사에서 중단했다.
특히 저장한 물리·제어기 상태에서도 같은 BC 행동의 반복 결과가 사전 허용차를
넘어 달랐다. **유효한 후보 행동 비교나 예측 보정 효과는 없다.** 현재
`PushT-v1`의 중간 branch 경로는 인과 타당성 때문에 보류했다.
[진단·보존](buildup/robotics/pilot_studies/q16-motion/README.md#paired-action-diagnosis-2026-09-26-exploratory-protocol-before-execution)을
따른다. Q16의 일반적인 유효성이나 hidden simulator state의 원인은 미확정이다.

**개발용 접촉 과업 선택 (2026-09-27):** 공개 2D `gym-pusht`와 Diffusion Policy
원본 206-episode 데이터를 별도 CPU Docker에서 조사했다. 단순 ridge BC는 새로운
16개 초기 상태에서 접촉 16/16, 성공 0/16이었다. 이 실패 중 관찰 후 고른 두
사례의 동일 BC 행동 분기는 1e-8 이내로 반복됐고, 한 후보 행동 변경으로 T의
후속 위치가 달라졌다. 따라서 이 경로를 실제 접촉 실패의 **개발용 행동 선택
진단**으로 선택했다. BC는 약한 기준선이며 변경 행동의 overlap 효과는 두 사례에서
서로 달랐다. 다음에는 단순 feedback과 행동 조건 예측 모델의 후보 선택을 같은
상태에서 비교한다. 강한 Diffusion Policy·같은 추가 데이터의 정책 갱신·3D Can과
새 초기 상태 검증은 아직 필요하다. [원본·검산·선택](buildup/robotics/pilot_studies/q16-motion/README.md#alternative-contact-task-assessment-2026-09-26-protocol-before-execution)을 따른다.

**고정 후보 행동 대조 (2026-09-27):** 그 두 개발용 실패 상태에서 frozen BC, 단순
기하 feedback, BC 주변 네 행동을 모두 실행하고 행동 조건 32-neighbor 모델로
후보를 선택했다. 기록 시연의 다음 물체 위치 검증 RMSE는 1.68 px였으나,
모델 선택 행동의 11-step overlap은 첫 사례에서 feedback과 같은 0.4237,
둘째에서 BC 0.3714보다 낮은 0.3511이었다. 둘째의 one-step pose 점수가
가장 높은 행동도 native overlap과 후속 접촉에는 불리했다. 후보 행동의 모델
오차와 score/evaluator 불일치가 관찰돼, 같은 두 seed의 score 수정으로 효과를
찾지 않는다.
[원본·검산·판단](buildup/robotics/pilot_studies/q16-motion/README.md#same-state-action-selection-contrast-2026-09-27-exploratory-protocol-before-execution)을 따른다.

**강한 정책의 개발용 대조:** 공식 low-dimensional Diffusion Policy checkpoint는
원본 `PushTKeypointsEnv`에서 20D keypoint 관측과 8-step 행동을 사용했다. 8개 새
초기 상태의 성공은 4/8이며 같은 초기 상태의 기존 5D ridge BC는 0/8이었다.
접촉 근접 실패 두 곳의 변경 행동은 서로 다른 결과를 냈다. 49005에서
simulator-state feedback과 임의 +40 px는 모두 한 번의 수정으로 성공했지만,
49006에서는 둘 다 실패했다. 원본 행동 반복과 전체 branch 재생은 1e-8 이내로
검산됐다. 이 두 선택 사례는 행동 민감도의 탐색 근거이지 예측 방법의 우위가 아니다.
정책 간 관측 표현·훈련 데이터도 다르다. 다음에는 정책에 실제 주어지는 관측으로
계산하는 고정 대안, 행동 조건 예측, 동일 추가 데이터의 정책 갱신을 새 초기 상태에서
비용과 함께 대조한다. 3D Can은 이후 대표성 검토 경로다.
[계약·원본·한계](buildup/robotics/pilot_studies/q16-motion/README.md#released-low-dimensional-policy-compatibility-2026-09-27-protocol-before-execution)를 따른다.

Vision/VLA inference, camera rendering, real robot, multi-shape/dynamics, model-seed 반복과
학습 data-budget curve는 미검증이다. 이번 결과를 data efficiency 또는 generality의 근거로
확장하지 않는다. Formal hypothesis/paper로 승격하지 않았다.

## Preservation and previous work

첫 관찰·잡기·밀기·지연 관측 prototype과 접촉 과업 비교의 source/lock/command, raw states,
model checkpoint 또는 시연 ZIP을 각각 보존했다. 각 작업에서 생성한 종료 container
7개, 11개, 9개, 5개, 12개만 해당 생성 기록 확인 후 개별 정리했다. 복구·보존 경계는
[runbook](docs/reproducibility.md#q16-contact-task-audit-and-demonstration-compatibility-2026-09-23)에 있다.
CD5의 미실행 설계와 Q15/Q3/Q4/CD2/Q14/Q7/Q9/Q6/Q12/Q13의 보류, Q8의 조건부 재검토는
[선택 기록](buildup/selection.md)과 가까운 owner에 보존한다.

## Stage Ownership

- Research scoping, candidate-question assessment와 feasibility studies: `buildup/`
- Formal hypothesis와 focused validation: `hypothesis/`
- 충분히 검증된 hypothesis의 paper-level work: `experiments/`

최종 paper의 기존 novelty/evidence 기준을 유지한다. `paper/`는 최종 실험을 모두 마치고
실제 논문을 작성할 때 [Paper Folder Gate](docs/paper.md#paper-folder-gate)를 모두 충족해 연다.
