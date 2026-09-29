# TODO

Updated: 2026-09-29

## Now

- [ ] [Q17 ML 첫 관찰](buildup/selection.md#q17-task-family-reassessment-2026-09-29):
  `blocks_ranking_rgb_rotate_view` 공식 ID seed `100000` 하나에서 초기/회전 후
  입력의 목표 블록 가시성과 공개 OFT의 첫 집기 대상·실제 집기를 판독한다.
  처음부터 목표가 보이거나 집기까지 도달하지 못하면 이 경로를 확대하지 않는다.

## Next

- [ ] 첫 관찰이 정보 획득 뒤 잘못된 조작 대상 선택을 보여 줄 때만 같은 상태의
  간단한 task-text 목표 위치 단서 대조와 ActiveArena memory/planner·PALM 비교를 설계한다.
  아니면 Q17과 다른 후보를 다시 비교한다. Q16 seed/grid는 재진입 조건 없이
  확대하지 않는다.

## Deferred Reassessment

- [ ] Q16은 단순 관측 피드백·재계획으로 설명되지 않는 대표 실패 조건,
  같은 정보의 강한 정책 대안과 타당한 paired 평가 경로가 구체화될 때
  재비교한다. 현재 2D 보정/짧은 chunk 경로와 Can PH 재생 경로의 보류는
  [선택 기록](buildup/selection.md#q16-shorter-chunk-outcome-and-investment-decision-2026-09-28)을 따른다.

- [ ] Q16의 Can PH v1.5.1 자료는 generator의 전체 dependency version 또는
  새로 사전 지정한 replay 계약이 확보될 때만 재진입한다. 현재 Docker는
  반복 가능하지만 기록된 다음 state/23D 관측과의 frozen 일치 기준을 실패했다.
  [원인 범위·처분](buildup/robotics/pilot_studies/q16-motion/README.md#can-action-replay-protocol-2026-09-27-before-simulator-execution).

- [ ] CD5는 사용자 요청으로 실행 선택을 철회했다. 입력·설계를 보존하며 model 취득과
  추론은 진행하지 않는다. 실험 실패에 따른 보류가 아니다.
  [처분](buildup/cross_domain/questions/information-budgeted-representation-utility.md#disposition-2026-09-23).

- [ ] Q15는 성공 후 실행 제어 선택이 중요한 구체적 사례와 단순 유지·목표 여유·기존
  안정화/피드백 대안을 구분할 작은 관찰이 생기면 재비교한다. 현재 reward/hold의 같은
  grid 확대는 보류한다. [결과·재검토](buildup/robotics/pilot_studies/q15-reward/README.md#investment-decision-and-preservation).

- [ ] Q3는 설정 선택이 구체적인 행동 결정에 주는 영향을 가르는 작은 대조와 비용이 생기면
  재비교한다. 현재 timestep grid/seed 확대나 임의의 policy pair 추가는 보류한다.
  [판단·재검토](buildup/robotics/questions/physics-ranking-stability.md#investment-decision-and-re-entry).

- [ ] Q4는 robot action/partial observation과 연결된 구체적 사례에서 단순 closure·
  goal-conditioned 선택·search 변경을 구분할 작은 대조가 생기면 재비교한다. 현재 fully
  observable instance-selection 경로의 optimal/route 추가 대조와 같은 slice 확대는 보류한다.
  [판단·재검토](buildup/robotics/questions/task-relevant-spatial-state.md#investment-decision-and-re-entry).

- [ ] CD2는 실제 평가 결정을 바꾸는 조건별 loss/failure severity의 작은 공개 또는
  constructed 관찰이 구체화되면 재비교한다. 현재 평균/profile-preservation 경로의
  seed/budget 확대나 새 sampler는 선택하지 않는다.
  [결과·투자 판단](buildup/cross_domain/pilot_studies/cd2-evaluation/README.md#investment-decision-and-re-entry).

- [ ] Q14는 의미가 명시된 action/calibration paired 출력을 통해 geometry/direct regression과
  구분할 작은 관찰이 구체화되면 재비교한다. 현재 DREAM pose 비교나 generic residual 학습은
  확대하지 않는다. [보류·재진입](buildup/robotics/questions/frame-error-propagation.md#investment-decision-and-re-entry).

- [ ] Q7은 task-state label을 방어하는 명시적 construction intervention과 source/model/
  evidence 설명을 구분하는 작은 관찰이 생기면 재비교한다. 같은 prompt/모델 변형만으로 재개하지 않는다.
  [보류·재진입](buildup/robotics/questions/failure-source-generalization.md#investment-decision-and-re-entry).

- [ ] Q9는 기존 simple/prior 대안과 다른 예측을 내는 작은 관찰·analytic example 또는
  구체적인 robot-decision 질문이 생기면 재비교한다. Calibration 정리나 scene 확대만으로
  현재 경로를 자동 재개하지 않는다. [판단·재진입](buildup/robotics/questions/spatial-memory-refresh.md#investment-decision-and-re-entry).

- [ ] Q6는 first-event/원본 label의 명시적 계약과 delay-order 비교의 정보 가치, 제한된 새
  readiness 설계가 함께 구체화될 때 재비교한다. Label 수정만으로 재개하지 않으며 기존
  2,048-record pilot은 대기열에서 제외한다.
  [재평가·재진입](buildup/robotics/questions/temporal-mismatch-decomposition.md#source-and-record-reassessment-2026-09-15).

- [ ] Q12는 reference/uncertainty 처리, completion input controls와 observable action contrast를
  함께 갖춘 제한된 연구 설계가 구체화될 때 다른 후보와 재비교한다. 추가 raster/mesh 정리만으로
  재개하지 않는다. [재진입 조건](buildup/robotics/pilot_studies/q12-generated-geometry/real/README.md#follow-up-value-and-stop-decision).

- [ ] Q13은 matching checkpoint·작은 matched-state/action-value 사례 또는 구체적인
  source-grounded failure case가 생기면 재비교한다. [재진입 조건](buildup/selection.md#q13-disposition-and-re-entry).

- [ ] Q8의 distinct perturbation-transfer target, equal-cost empirical-success control,
  training-data-linked policy와 valid demonstration restart가 구체화될 때만 재진입을 검토한다.

## Recently Completed

- [x] Q17의 IA·ML·MD 과업 source/evaluator와 Q13/Q9·Q16·CD1의 선행·비용을
  다시 비교했다. Hidden-color IA는 정보 획득 장벽이 더 크고 MD count sibling은
  버튼 모호성을 반복한다. ML 회전 시점의 첫 목표 물체는 별도 판독 가능하므로
  공식 ID 한 사례만 저비용 screen으로 선택했다. 색·순서는 지시에 이미 있어
  새 색 추론의 증거로 쓰지 않는다. [비교·선택](buildup/selection.md#q17-task-family-reassessment-2026-09-29).
  (2026-09-29)

- [x] Q17 color-count의 저장 화면에서 네 블록과 세 색이 보인 후 버튼 접근 전인
  step 48을 고정했다. 원본과 완전 일치하는 89-step 재생을 확인하고,
  동일 48-step prefix·RGB/18D 상태에서 정답 3/버튼 3 문장만 바꾼 분기를 실행했다.
  행동은 달라졌으나 다시 step 89에 2번 버튼을 눌러 native 실패했다. 원인은
  여전히 미분리이므로 같은 사례의 추가 prompt/seed를 멈추고 경로를 재비교한다.
  재생·분기 output을 검산하고 소유한 종료 container/network만 정리했다.
  [결과·한계](buildup/robotics/pilot_studies/q17-evidence/README.md#earlier-answer-cue-decision-point-2026-09-28).
  (2026-09-28)

- [x] Q17 color-count seed `100000`의 재생이 원본과 89 step·6 request·21 RGB
  입력·state/action chunk 모두 일치했다. 같은 80번째 결정 상태에서 count 3과
  버튼 3을 지시한 oracle 문장은 행동 수치를 바꿨지만 여전히 89번째 동작에서
  2번 버튼을 눌렀다. 당시 팔은 이미 2번 버튼 위에 있어 이 늦은 개입으로
  counting/기억/실행 원인을 분리할 수 없다. 62 step에서 멈춘 첫 실행은
  결과로 쓰지 않고 보존했고, 재시도는 완료·검산했다. 소유한 종료 container와
  network만 정리했다. [원본·재생·해석](buildup/robotics/pilot_studies/q17-evidence/README.md#matched-button-decision-diagnostic-2026-09-28).
  (2026-09-28)

- [x] Q17 `count_color_kinds_press_button`의 버튼 자산·source·첫 고정 ID seed를
  확인하고 workspace 전용 Docker에서 한 사례를 실행했다. 정책 입력에 빨강·초록·
  파랑이 보인 뒤 정답 3번 대신 2번 버튼을 89번째 동작에서 실제 눌러 native
  `wrong_button_pressed`로 종료했다. 89 step·6 request·21 입력 PNG와 버튼 joint를
  검산했다. 한 사례이며 기억/선택/실행 원인은 미분리다. 소유한 종료 container와
  network만 정리했다. [결과·복구](buildup/robotics/pilot_studies/q17-evidence/README.md#color-count-button-route-2026-09-28).
  (2026-09-28)

- [x] Workspace에서 생성한 불필요한 Docker image를 container와 같은 소유권·
  보존·참조 확인 후 개별 정리하도록 [운영 규칙](AGENTS.md)을 갱신했다.
  Q17의 종료된 진단·초기 image 네 개만 삭제하고 재실행에 필요한 다섯 image는
  유지했다. [정리 기록](buildup/robotics/pilot_studies/q17-evidence/README.md#workspace-owned-image-cleanup).
  (2026-09-28)

- [x] Q17 `check_block_color`의 첫 세 공식 ID seed를 workspace 전용 simulator
  Docker와 공개 OFT checkpoint의 탐색용 websocket bridge로 실행했다.
  3/3 사례에서 각 19개 정책 입력 프레임에 뒷면 색이 판독되지 않았고,
  pad 선택도 판정 불가였으며 native 성공은 없었다. 이는 정보 사용 이후의
  실패를 입증하지 않는다. EGL ICD로 Vulkan 장면 생성을 복구했고,
  artifact·로그·Docker 의존성을 보존했다. 양팔 계측을 수정한 exact-text 재생에서
  세 원본의 입력 프레임·행동·블록 궤적이 모두 일치했고, 누락됐던 오른쪽
  그리퍼 개방을 보완해도 pad 선택 판정은 바뀌지 않았다. 모든 불필요한 전용
  컨테이너와 전용 네트워크를 정리했다.
  [원본·판독·한계](buildup/robotics/pilot_studies/q17-evidence/README.md#held-out-fixed-seed-observation-and-route-decision-2026-09-28).
  (2026-09-28)

- [x] Q17 공식 OFT checkpoint 한 개와 Qwen3-VL base를 pinned revision/SHA256으로
  취득하고, workspace 전용 GPU Docker에서 두 **학습** 시연의 같은 현재 상태를
  4조건씩 대조했다. Generic 지시의 전체 history 대 current-only 16-step 행동
  L1은 green 0.038/0.129, red 0.029/0.082; 정답 task text는 0.020/0.013이다.
  독립 검증으로 8개 행동 출력·16프레임 이력·현재 영상/상태 hash를 확인했다.
  보조 텍스트는 green을 red로 오인했고 red는 색을 명시하지 않았으며 결정적
  반복에서 동일했다. 학습 시연·history 길이 confound·보조 출력이므로 실제
  목표 선택 또는 method 이점으로 해석하지 않는다. 필요한 컨테이너는 모두
  `--rm`으로 정리됐다. [결과·복구](buildup/robotics/pilot_studies/q17-evidence/README.md#limited-offline-policy-probe).
  (2026-09-28)

- [x] Q17 `check_block_color`의 source/LeRobot/evaluation 계약을 workspace 전용
  CPU Docker에서 검사했다. 학습 metadata 100/100의 지시문은 정답 색을 밝히지만,
  공식 fixed-seed `unseen`은 ID/OOD 각각 0/250이다. 공개 Parquet 세 시연의
  행·이미지·hash를 검산하고, 색이 보이는 검사 장면과 뒤의 선택 직전 장면을
  확인했다. `info_complete`는 실제 색 판독 label이 아니며 이 자료만으로 정책의
  목표 선택 오류와 실행 오류를 판정할 수 없다. 첫 문자열 검사 버그를 수정한
  v2 결과만 instruction 수치에 사용한다. [근거·한계·재현](buildup/robotics/pilot_studies/q17-evidence/README.md#current-findings-and-decision).
  Audit 컨테이너는 모두 소유 확인 후 `--rm`으로 자동 정리했다. (2026-09-28)

- [x] 기존 reserve의 재진입 조건과 최신 active-perception/long-horizon 방향을
  비교하고 [Q17 Evidence-Conditioned Action Selection](buildup/robotics/questions/evidence-conditioned-action-selection.md)을
  다음 제한된 탐색 질문으로 선택했다. ActiveArena의 실패 분해는 정보 이용과
  실행 실패를 섞어 보므로 한 hidden-color 과업에서 둘을 분리하는 관찰을
  우선한다. 방법 효과나 novelty는 확인되지 않았다.
  [선택·비교](buildup/selection.md#q17-selection-2026-09-28). (2026-09-28)

- [x] Q16 공식 Diffusion Policy의 사전 지정 seed 49200–49215, 32회 rollout에서
  8-step 성공 7/16, 2-step 성공 6/16(구제 2·악화 3)을 확인했다. 2-step은
  정책 호출 4.16배·추론 시간 4.19배였다. 원본 환경의 32개 독립 재생, paired
  초기 상태와 첫 두 행동·상태 검증이 통과했다. 순구제가 없어 현재 2D 방법
  경로를 보류하고 다른 후보를 재비교하기로 결정했다.
  [결과·재현](buildup/robotics/pilot_studies/q16-motion/README.md#shorter-action-chunk-comparison-2026-09-27-prospective-protocol),
  [선택](buildup/selection.md#q16-shorter-chunk-outcome-and-investment-decision-2026-09-28).
  두 평가 job 모두 `completed`/exit 0이며 검증 후 이번에 만든 종료 컨테이너
  두 개만 [정리](logs/20260928_095808_q16_chunk_cleanup.log)했다. (2026-09-28)

- [x] Buildup 운영 방향을 재검토해 잠정 설명·가까운 선행과의 차이·결과별 다음 선택을 활성 후보에 짧게 연결하고, 유효한 관찰 뒤에는 연구 판단을 먼저 하도록 규칙을 보강했다. 준비·실행·검산은 한 관찰로 묶고 상세 이력은 가까운 owner에 두며, 현 Q16 판단과 paper 기준은 유지했다. [운영 규칙](docs/buildup.md). (2026-09-28)

- [x] Q16의 강한 2D 정책, Can PH v1.5.1 재생 실패, 공개 VLA/3D benchmark와
  Q12/Q13 및 reserve 후보의 정보 가치·준비 비용을 재비교했다. 최신
  LIBERO-plus는 공개 checkpoint·Docker 경로가 있지만 Q16의 물체 운동/접촉
  질문과 직접 같지 않고 prediction feedback 선행이 이미 해당 benchmark를
  사용한다. 현재 2D 정책의 **8-step 대 2-step 재계획**을 새 paired seed에서
  한 번 보는 것을 선택하고, 어느 결과든 같은 2D 보정 규칙의 추가 조정은
  하지 않는 중단 조건을 기록했다. [비교·선택](buildup/selection.md#q16-and-reserve-candidate-reassessment-2026-09-27). (2026-09-27)

- [x] Q16 Can PH v1.5.1의 사전 지정 두 시연을 Docker에서 각각 첫 32행
  행동 재생했다. 초기 state는 정확히 복원되고 동일 prefix 반복도 정확했지만,
  두 시연 모두 기록된 다음 state·23D 관측과의 frozen 기준을 32/32행에서
  실패했다. Raw-state 최대 오차의 주원인은 비선택 물체이나 정책 관측도
  최대 약 0.001 차이여서 현재 Can PH route의 policy 학습은 보류했다.
  [결과·경계](buildup/robotics/pilot_studies/q16-motion/README.md#can-action-replay-protocol-2026-09-27-before-simulator-execution). (2026-09-27)

- [x] Q16의 3D robomimic Can PH 경로를 공식 source·model zoo·dataset version으로
  비교했다. 현재 v1.5.1 low-dimensional 파일 46,889,752 bytes를 checksum 확인하고
  별도 CPU Docker에서 200개 시연·23,207행, 각 시연의 23D 관측·7D 행동,
  71D state와 매 episode XML을 검산했다. 오래된 공개 Can checkpoint는 `offline_study` 또는
  `robomimic 0.2` 계열이어서 현재 runtime의 직접 기준선으로 사용하지 않는다.
  XML/state 복원 API는 확인했지만 행동 재생의 일치는 아직 미검증이다. 새 image,
  raw assessment, full lock과 18개 파일의 local hash를 보존했고 audit container는
  `--rm`으로 종료 시 정리했다. [결과·선택](buildup/robotics/pilot_studies/q16-motion/README.md#3d-can-route-feasibility-2026-09-27-exploratory-protocol-before-data-access). (2026-09-27)

- [x] Q16 공식 Diffusion Policy의 새 초기 상태 16개를 원본 Push-T 환경에서
  frozen, 관측 기반 feedback, 행동 조건 예측 선택, 동일 160개 시연을 사용한
  300-step 정책 갱신으로 비교했다. 성공은 각각 8/16, 8/16, 8/16, 4/16이었다.
  예측 선택은 9개 gate에서 네 행동을 바꿨으나 frozen 실패를 구하지 못했다.
  64개 trajectory를 독립 재생하고 native 판정·동일 초기 상태·개입 전 prefix를
  검산했다. 원본 저장 keypoint와 기록 state의 불일치는 별도 실패 진단으로
  보존하고, 정책 갱신은 공식 저장 keypoint 계약을 사용했다. 395개 파일의
  local hash를 확인하고 이번 실행의 종료 container 7개만 정리했다.
  [결과·한계](buildup/robotics/pilot_studies/q16-motion/README.md#observation-matched-policy-continuation-2026-09-27-exploratory-protocol-before-execution). (2026-09-27)

- [x] Q16 공식 low-dimensional Diffusion Policy의 원본 source/checkpoint를
  별도 Docker에서 확인했다. 새 초기 상태 8개에서 정책은 4/8, 기존 ridge BC는
  같은 초기 상태에서 0/8 성공했고, 원본 환경의 평가 trace 16개를 독립 재생했다.
  접촉 실패 두 곳의 원래 정책 반복 분기와 변경 행동 8개 trace도 검산했다.
  한 곳은 simulator-state feedback과 임의 +40 px 모두 성공으로 바뀌었고 다른
  곳은 둘 다 실패했다. 따라서 예측 모델 이득은 아직 없다. 결과·원본 등
  179개 파일을 local hash 확인한 뒤 이번 실행의 종료 container 8개만 정리했다.
  [결과·복구](buildup/robotics/pilot_studies/q16-motion/README.md#released-low-dimensional-policy-compatibility-2026-09-27-protocol-before-execution). (2026-09-27)

- [x] Q16의 기존 `gym-pusht` 학습 BC 실패 두 곳에서 고정한 여섯 후보를
  CPU Docker로 짝지어 비교했다. 별도 시연 검증의 모델 XY RMSE는 1.68 px였지만
  모델이 고른 행동의 최종 overlap은 단순 feedback과 동일한 0.4237 및 BC보다 낮은
  0.3511이었다. 12개 후보와 두 반복 BC trace를 독립 검산했고, 원본·신규 파일
  215개를 local hash 확인한 뒤 이번 실행 소유의 종료 container 3개만 정리했다.
  두 사례는 개발용이며 예측 보정의 이득은 없다.
  [결과·다음 투자 판단](buildup/robotics/pilot_studies/q16-motion/README.md#same-state-action-selection-contrast-2026-09-27-exploratory-protocol-before-execution). (2026-09-27)

- [x] Q16의 공개 2D `gym-pusht`와 공식 206-episode 시연을 별도 CPU Docker에서
  조사했다. 사전 지정한 접촉 사례 2/2, 학습 BC의 실제 접촉 실패 사례 2/2에서
  동일 행동의 분기 재생이 1e-8 이내로 일치했다. 약한 ridge BC는 새 seed 16개
  모두 T에 접촉했지만 성공 0/16이고, 바뀐 행동은 두 실패 사례의 T 궤적을 바꿨다.
  예측 방법의 이득은 아직 없다. 원본·trace·실행 기록 151개를 local hash 검증하고
  이번 작업 소유의 종료 container 8개만 정리했다. 이 경로를 Q16의 **개발용 행동
  진단**으로 선택했으며 강한 정책/3D 검증은 남았다.
  [결과·선택](buildup/robotics/pilot_studies/q16-motion/README.md#alternative-contact-task-assessment-2026-09-26-protocol-before-execution). (2026-09-27)

- [x] Q16 `PushT-v1`의 기존 BC 실패 4개를 대상으로 행동 조건 예측 모델을
  75,289/8,286개 시연 전이로 학습했지만, 짝지은 행동 분기는 검증에 실패했다.
  기존 trace 재생, 새 reset 반복, 물리·제어기 state 복원의 세 시도에서 각각
  행동 이력 또는 동일 BC 대조가 달랐다. 따라서 유효한 후보 행동 비교나 모델
  이점은 없으며 이 과업의 현재 분기 경로는 인과 타당성 문제로 보류했다.
  입력·모델·실패 기록 46개 파일을 local hash 확인하고 소유 확인한 종료 container
  4개만 정리했다. [결과·한계](buildup/robotics/pilot_studies/q16-motion/README.md#paired-action-diagnosis-2026-09-26-exploratory-protocol-before-execution). (2026-09-26)

- [x] Q16 `PushT-v1` 공식 시연을 생성 commit의 원본 CUDA 과업과 CPU/충돌-only
  adapter에서 재생·검산했다. 원본/충돌-only CUDA trace는 8/8 byte-identical이며
  원본과 공식 replay 모두 최종 성공 2/8이었다; CPU는 0/8이었다. 기록 상태에서
  31D 관측/3D 행동을 복원하고, 64/8 및 792/88 episode의 단순 imitation 경로를
  실행했다. 새 초기 상태에서 PPO/BC/zero는 각각 8/8·1/8·0/8(첫 8개),
  16/16·12/16·0/16(후속 16개)이며 72개 policy trace와 replay 검산을 마쳤다.
  후속 평가는 첫 결과를 본 뒤 진행한 탐색이며 PPO는 equal-data가 아니다.
  [호환성·정책 결과](buildup/robotics/pilot_studies/q16-motion/README.md#pusht-demonstration-compatibility-2026-09-25). (2026-09-25)

- [x] Q16의 pinned `PushT-v1`과 `RollBall-v1`을 별도 CPU Docker의 collision-only
  변형으로 비교했다. 마지막 같은 제어기·8개 paired seed에서 native 성공은 모두
  0/8이었으나 T 중첩률은 hold 0.288, 현재 feedback 0.375, 초기 상태 고정 0.331;
  ball 목표 거리는 각각 1.451/1.439/1.440 m였다. 48개 trace와 native 판정·초기
  상태를 검산하고 `PushT-v1`을 다음 개발 과업으로 잠정 선택했다. 공식 시연 ZIP을
  checksum 확인했으나 현재 CPU 변형에서 초기 물리 상태까지 복원한 재생은 0/8이었다.
  Raw 결과와 source를 보존하고 소유 확인한 종료 container 12개만 삭제했다.
  [비교·선택](buildup/robotics/pilot_studies/q16-motion/README.md#contact-task-comparison-and-selection). (2026-09-23)

- [x] Q16의 별도 CPU Docker에서 `PushCube-v1` 물체 pose·velocity의 4-step/0.2 s 지연을
  실행했다. 단순 지연/CV feedback, frozen·동일 추가 데이터 policy, model guidance와
  깨끗한 상태의 진단용 reference를 새 초기 상태 16개 × 두 마찰 조건에서 비교했다.
  160개 시연·192회 평가, 9,792 raw evaluation states, 352 checksum과 지연·native
  판정·paired reset을 검산했다. 지연·CV·clean feedback 모두 16/16 양 조건이라
  이 과업에서 지연은 유의미한 제어 실패를 만들지 않았다. 원본/compact 결과와 source를
  보존하고 이번 종료 container 5개만 정리했다.
  [결과·한계](buildup/robotics/pilot_studies/q16-motion/README.md#delayed-observation-result-and-boundary). (2026-09-23)

- [x] Q16을 pinned `PushCube-v1`의 collision-only CPU 변형으로 확장했다. 160개 시연,
  frozen/동일 추가 데이터 policy·dynamics 학습, 첫 평가 192회와 실패 진단 후 새 초기 상태
  256회 수정안 평가를 완료했다. 448회 평가·22,848 raw states와 checksum/native 판정,
  paired 사례를 검산했다. 새 split에서 단순 feedback 16/16 양 조건, frozen 13/16,
  contact-gated 보정 6/16 양 조건이다. Raw/compact 결과·source·명령을 보존하고 이번
  종료 container 9개만 개별 정리했다. 완전 상태에서 단순 residual bias 재조정 대신
  관측/물체 조건 확장을 선택하며 positive model claim은 보류한다.
  [방법·결과](buildup/robotics/pilot_studies/q16-motion/README.md#revised-result-interpretation-and-preservation). (2026-09-23)

- [x] Q16 첫 정책 적응 prototype을 새 CPU Docker에서 구현하고 224개 teacher 시연,
  정책·8-step dynamics 학습, 두 개발 평가와 새 초기 상태 32개 반복 576회를 실행·검산했다.
  Moving 조건은 learned policy 9/32, fixed predictive correction와 단순 CV 32/32,
  feedback-adjusted correction 29/32였다. 46,656 raw states와 96 paired conditions를
  확인하고 compact 결과/원본을 보존한 뒤 이번 종료 container 11개만 정리했다.
  [방법·한계·복구](buildup/robotics/pilot_studies/q16-motion/README.md#adaptation-results-2026-09-23). (2026-09-23)

- [x] 사용자 의견을 반영해 Q16을 넓은 예측 기반 정책 적응 방향으로 계속 개발하기로 했다.
  DynaGuide/DyWA/Feedback World Model/DynamicWAM과 첫 구현 범위를 비교하고
  learned policy·multi-step prediction·feedback의 개발 범위와 초기 예산을 정했다.
  Buildup 운영 규칙에 시의성과 반복 개발을 반영했으며 최종 paper 기준은 유지했다.
  새 학습·rollout은 없다. [결정·근거](buildup/selection.md#q16-method-development-2026-09-23). (2026-09-23)

- [x] Q16의 새 CPU Docker에서 160개 train/validation rollout과 두 작은 model fit,
  240회 평가를 완료했다. 다섯 route 모두 static/sliding 24/24 성공이며 예측 오차 개선의
  성공률 이점은 없었다. Raw state 32,400개·decision rows 17,920개를 검산하고 사례를 해석했다.
  결과·로그 보존 후 이번 종료 container 7개만 정리했다.
  [결과·한계·복구](buildup/robotics/pilot_studies/q16-motion/README.md#results-2026-09-23). (2026-09-23)

- [x] 사용자 요청으로 CD5를 실행 전 보류하고 정책·접촉 데이터·좌표계 방향을 primary source로
  비교해 Q16을 다음 후보로 선택했다. Action-conditioned motion prediction의 질문·잠정 방법·
  작은 제어/학습 비교와 비용을 기록했다. 새 학습·rollout은 없다.
  [선택·근거](buildup/selection.md#q16-selection-2026-09-23). (2026-09-23)

- [x] CD5/CD1/Q8을 primary source·행동 질문·준비 비용으로 비교해 CD5 관찰을 선택했다.
  공개 symbolic JSON의 실제 178개 record와 source 13개 hash를 확인하고 6+24 task를
  고정했다. CD1의 공개 synthetic 실행 경로를 반영했고 Q8 보류 조건은 유지했다.
  새 inference·Docker 실행은 없다. [선택·근거](buildup/selection.md#cd5-observation-selection-2026-09-22). (2026-09-22)

- [x] Q15의 576회 hold 비교·독립 검산·18개 사례 해석을 완료했다. Native 86→93/96,
  no-grasp 94→93/96, half 93→93/96이며 9개 pair 개선·3개 악화를 확인했다.
  전환 전 288 pair와 기존 continued trace 9개가 정확히 일치했다. 현재 경로의 추가
  투자는 보류하고 결과 보존 후 이번 종료 container 3개만 정리했다.
  [결과·근거](buildup/robotics/pilot_studies/q15-reward/README.md#hold-results-2026-09-22). (2026-09-22)

- [x] 요청된 일회성 [연구 개요 보고서](research_overview.md)에 보상 비교의 최신 결과,
  성공 후 유지 제어의 후속 설계와 완료된 시간 간격 실험을 반영했다. (2026-09-18)

- [x] Q15의 scale·학습 진행도·목표 유지 실패를 PPO normalization, DrEureka와
  reach-and-stay 선행 6편에 대조했다. 추가 학습 대신 기존 checkpoint의 joint-position
  hold 대조를 선택하고 576 episodes의 범위·예산·판단 분기를 정했다. Zero delta와
  고정 reference의 차이를 pinned controller source에서 확인했다. 새 실행은 없다.
  [문헌·투자 판단](buildup/robotics/related_work/policy-geometry.md#q15-follow-up-investment-2026-09-18). (2026-09-18)

- [x] Q15의 9 fits·18 checkpoints·2,304 episodes를 Docker에서 완료했다. 최종 nominal
  성공은 native/no-grasp/half-scale 86/94/93 of 96이며 scale·학습 시점 효과를 확인했다.
  Static 판정/파일 경로 검산 오류를 수정하고 native labels 345,600개·평가 rewards
  115,200개를 검산했다. 최종 실패 53건을 해석해 `refine`으로 기록했으며 결과 보존 후
  이번 종료 container 7개만 정리했다.
  [결과·수정·복구](buildup/robotics/pilot_studies/q15-reward/README.md#results-2026-09-18). (2026-09-18)

- [x] Q3를 SIMPLER·contact-model 분석·closed-loop benchmark audit와 대조해 현재 경로의
  추가 투자를 보류했다. Q3/Q4/CD1/Q15의 정보 가치·비용을 비교해 Q15의 작은 학습 관찰을
  선택하고 DrEureka/HPRS의 직접 중복을 명시했다. 공식 source 11개를 immutable 원격과
  bytes/hash 대조했다. Q15 학습·새 rollout은 아직 없다.
  [판단·선택](buildup/selection.md#q3-investment-and-q15-selection-2026-09-18). (2026-09-18)

- [x] 지정 Docker image 6개와 workspace 정리 후보를 읽기 전용으로 검토했다.
  Image 5개는 삭제 가능, Q9 v2/잔여 container 1개는 생성 주체 미확인으로 보류했다.
  재생성 가능 파일 약 747 MiB와 외부 backup 검증 후 조건부 payload 12.720 GiB를 구분했다.
  저장 결과/runtime 729개 및 source 중복 1,495개를 대조했으며 실제 삭제는 없다.
  [목록·보존·재현 영향](docs/reproducibility.md#docker-and-workspace-cleanup-review-2026-09-18). (2026-09-18)

- [x] Q3 새 GPU Docker에서 96회를 실행하고 raw-state predicate 14,400개를 독립 검산했다.
  모든 조건 end/once 8/8, 반복 차이 0이며 100–400 Hz cube RMS 차이는 closed loop
  3.742 mm / target replay 1.469 mm였다. `refine`으로 기록하고 단위별 joint 진단을 정정했다.
  결과·로그 보존 후 이번 종료 container 세 개만 삭제했다.
  [결과·검산·복구](buildup/robotics/pilot_studies/q3-timestep/README.md#results-2026-09-18). (2026-09-18)

- [x] Q4 후속을 Taskography/PLOI/Scale-Plan과 비교하고 현재 instance-selection 경로를
  보류했다. SIMPLER·contact-model 분석·closed-loop 재현성 선행을 반영해 Q3의 단일 PPO
  timestep/absolute-target replay 관찰을 선택했다. Source 9개·checkpoint bytes/hash를
  확인했으며 새 수치 실행은 없다.
  [비교·선택 근거](buildup/selection.md#q4-investment-and-q3-selection-2026-09-18). (2026-09-18)

- [x] Q4 goal-conditioned b0 여섯 조건의 구현·CPU Docker 실행·검산·해석을 완료했다.
  모두 valid, 평균 plan 77.7→69.3 actions이며 한 문제는 51→71로 악화됐다. 거리 30,670개,
  assignment 6,254개와 transition/goal 8,052개를 검산하고 양방향 plan transfer로 search
  영향을 구분했다. 기존 447개·새 113개 출력 파일 보존 후 이번 종료 container 4개만 정리했다.
  [결과·반례·복구](buildup/robotics/pilot_studies/q4-planning/README.md#goal-conditioned-observation-2026-09-18). (2026-09-18)

- [x] Q4 CPU Docker의 40개 조건을 실행·검산·해석했다. 39개 valid/Full 1개 timeout이며
  61,511개 transition/goal 검사와 거리 550개 대조를 통과했다. b1의 더 긴 계획 7건 모두
  짧은 b0 plan이 실행 가능해 search 영향을 구분했다. `refine`으로 판단했고 실패·출력·로그
  보존 후 이번 종료 container 10개만 정리했다.
  [결과·사례·복구](buildup/robotics/pilot_studies/q4-planning/README.md#results-2026-09-18). (2026-09-18)

- [x] Q3와 Q4/CD5의 실제 입력·대안·정보 가치·준비 비용을 비교해 Q4의 작은 Taskography
  관찰을 선택했다. SCRUB/SEEK·Scale-Plan의 직접 선행을 반영하고 test 문제 8개와 대응
  입력을 확보했다. Source/input 32개 hash를 확인했으며 planner 실행은 아직 없다.
  [비교·선택](buildup/selection.md#q4-observation-selection-2026-09-18). (2026-09-18)

- [x] CD2 LBM의 500개 기록을 CPU Docker에서 분석했다. 1,600개 subset·6,400개 score·
  3,200개 gap을 독립 검산하고 작은 task gap의 역전을 유한 표본 계산과 대조했다.
  NPY metric 가정을 수정한 실패 기록도 보존했다. 현재 경로는 `deferred`이며 결과·로그
  보존 후 이번 종료 container 6개만 삭제했다.
  [결과·해석·재현](buildup/cross_domain/pilot_studies/cd2-evaluation/README.md#episode-results-2026-09-17). (2026-09-17)

- [x] CD2 episode-level 후속 투자를 STEP/N-SCORE/Active Experiment Selection/PEAK 및
  RoboArena와 비교했다. LBM의 작은 공개 trial 입력을 확보해 task mix와 within-task
  variation을 분리할 관찰 한 번을 선택했다. Source 23개 hash와 NPY 10개 header를
  확인했으며 새 수치 실행은 없다. [판단·다음 관찰](buildup/selection.md#cd2-follow-up-assessment-2026-09-17). (2026-09-17)

- [x] CD2 첫 관찰을 CPU Docker에서 실행·해석했다. 1,604개 subset, 4,812개 target score와
  5,614개 pair를 독립 검산했다. 단순 층화의 coverage/score 이점과 작은 gap의 순위 역전,
  greedy의 Long Horizon 누락을 구분해 `refine`/`under_review`로 기록했다. 결과·로그 보존 후
  이번 종료 container 세 개만 삭제했다. [결과·한계·복구](buildup/cross_domain/pilot_studies/cd2-evaluation/README.md#results-2026-09-17). (2026-09-17)

- [x] Q3, Q4/CD5, CD2를 현재 primary source·작은 관찰의 정보 가치·비용으로 비교해 CD2를
  선택했다. VLA-Arena 공개 8-model × 33-cell 입력과 단순 baseline·model split을 정하고
  source 12개 hash/schema를 확인했다. 새 수치 실행은 아직 없다.
  [근거·선택](buildup/selection.md#cd2-observation-selection-2026-09-16). (2026-09-16)

- [x] Workspace 파일 용량·복구 의존성을 검토했다. 재생성 가능한 source/cache 약 458 MiB와
  Q7/Q12/Q14 대형 payload 약 12.72 GiB를 구분했다. 후자는 외부 backup 검증 전 조건부다.
  실제 삭제는 없다. [목록·보존 조건](docs/reproducibility.md#workspace-file-cleanup--2026-09-16). (2026-09-16)

- [x] Q14 잔여 세 사례를 action 변환식·visual servoing·SQPnP·uncertainty-aware PnP와
  비교해 현재 경로를 `deferred`로 판단했다. ADD 순위를 action 오차로 해석할 수 없으며,
  broad learned-dependence 질문은 미해결로 보존한다. 새 수치 실행은 없다.
  [근거·다음 선택](buildup/selection.md#q14-investment-decision-2026-09-16). (2026-09-16)

- [x] Q14 실제 24-frame DREAM 추론·96개 solver 대조를 CPU Docker에서 완료했다.
  RANSAC은 4개 개선·6개 악화·14개 유사했고, 사후 단순 pose 선택이 두 큰 오류를 피했다.
  독립 검산 1,745개와 미사용 residual 표기 정정 672개를 통과했다. 출력·로그 보존 후
  이번 종료 container 네 개만 삭제했다. [결과·경계·복구](buildup/robotics/pilot_studies/q14-frame-errors/real/README.md#results-2026-09-16). (2026-09-16)

- [x] Q14 수정 방향을 CamVLA·DREAM·EasyHeC++·GeoCalib·EquiBot·BPnP/EPro-PnP와 비교했다.
  Generic residual 학습 대신 실제 keypoint 24-frame 관찰을 선택하고 DREAM의 GT-camera-frame
  평가 계약을 구분했다. 공식 source 6개와 discovery note 2개를 hash 기록했다. 새 수치 실행은 없다.
  [비교·선택](buildup/selection.md#q14-geometry-review-2026-09-16). (2026-09-16)

- [x] 지정한 Docker image 7개와 관련 종료 container 18개를 읽기 전용으로 검토했다.
  결과/로그 98개 검사를 통과했고 container 17개를 삭제 후보로 분류했다. Mount/생성 기록이
  없는 Q9 dependency container 1개와 그 image의 삭제는 조건부로 남겼다. 실제 삭제는 없다.
  [목록·복구 영향](docs/reproducibility.md#docker-cleanup-review-2026-09-16). (2026-09-16)

- [x] Q14 CPU study의 네 fit·16개 scene·5,200 prediction을 실행하고 독립 수치 대조를
  통과했다. 장면별 결합 효과와 기하 noise 설명을 확인했지만 learned pairing의 평균 이점은
  일관되지 않았고 90° 오차는 calibration extrapolation이 지배했다. `refine`/`under_review`로
  기록하고 결과·로그 보존 후 이번 작업의 종료 container 네 개만 삭제했다.
  [결과·한계·복구](buildup/robotics/pilot_studies/q14-frame-errors/README.md#results-2026-09-16). (2026-09-16)

- [x] Q7/Q14를 primary paper·공식 release·관찰 비용/정보 가치로 재비교해 Q14를 선택했다.
  Fixed-state prediction pairing 대조와 기하/direct-regression 대안을 구체화했고, Q7은
  현재 경로의 추가 투자를 보류했다. 새 학습/추론/container 실행은 없다.
  [선행·비교](buildup/robotics/related_work/policy-geometry.md#q7-q14-reassessment-2026-09-16) ·
  [선택](buildup/selection.md#q14-selection-2026-09-16). (2026-09-16)

- [x] Q7 END+END 대조를 완료했다. 8개 신규 추론·7개 입력 identity 재사용을 Docker에서
  검증했고, START+END와 같은 6/15 label 일치 및 두 사례의 상반된 변화를 기록했다.
  Q7을 `under_review`로 두고 Q14와의 투자 재비교를 다음으로 정했다.
  [결과·한계](buildup/robotics/pilot_studies/q7-failure-source/README.md#repetition-results-2026-09-16). (2026-09-16)

- [x] 사용자 요청으로 workspace가 생성한 불필요한 container만 정리하는 규칙을
  AGENTS.md에 추가했다. 결과·로그·재현 정보를 보존하고 이번 Q7 container 3개만 삭제했다.
  [정리 근거](buildup/robotics/pilot_studies/q7-failure-source/README.md#container-cleanup-2026-09-16). (2026-09-16)

- [x] Q7 SmolVLM2의 두 관측 조건을 CUDA Docker에서 30개 추론·대조까지 완료했다.
  JSON 형식 준수는 0/30이며 원문 판정의 사후 label 일치 2/15 vs 6/15를 따로 보존했다.
  동일 이미지 반복만으로도 판정이 바뀌어 END+END 대조를 다음 시도로 선택했다.
  [결과·한계·재현](buildup/robotics/pilot_studies/q7-failure-source/README.md#vlm-results-2026-09-15). (2026-09-15)

- [x] Q7 첫 영상 관찰과 CPU Docker 비교를 완료했다. 15개 입력·45개 view score의 계산을
  독립 대조했고, 단일-view 역전과 이를 네 쌍 모두 설명하는 사후 median 대안을 함께 기록했다.
  원본 label은 유지하고 작은 general VLM의 상태/전후 관측 비교를 다음 시도로 선택했다.
  [결과·한계·재현](buildup/robotics/pilot_studies/q7-failure-source/README.md#results-2026-09-15). (2026-09-15)

- [x] Q7/Q14의 직접 선행·실제 사례·정보 가치와 비용을 비교해 Q7의 작은 관찰을 선택했다.
  Guardian 공식 metadata에서 같은 시작 장면의 성공/실패 네 쌍을 찾았고, OC-VLA의 코드
  경로와 CamVLA의 oracle/noise 대조군을 반영했다. 영상/모델 실행은 아직 없다.
  [비교·결정](buildup/robotics/related_work/policy-geometry.md#q7-q14-comparison-2026-09-15). (2026-09-15)

- [x] Q9의 잔여 문제를 DynaMem·Memory for Attention·VLMM·Khronos primary text 및
  기존 source와 대조하고 현재 경로의 추가 투자를 `deferred`로 결정했다. 단순 visibility
  효과와 미해결 correspondence를 구분하고 재진입 초안을 남겼다. 새 수치 실행은 없다.
  [비교·대안·판단](buildup/robotics/related_work/policy-geometry.md#q9-research-value-2026-09-15). (2026-09-15)

- [x] Q9의 초기 물체 표면점과 동일 두-depth-access schedule 비교를 CPU Docker에서
  완료했다. 단순 visibility 규칙이 두 사례의 interval 증거를 포착했지만 orange의 초기
  구간 모순으로 object-level 해석은 미확정이다. 비용 표기 수정 후 재실행의 trace·판정은
  동일했고 84행·12 schedule을 확인했다. [결과·한계](buildup/robotics/pilot_studies/q9-refresh/README.md#surface-comparison-2026-09-15). (2026-09-15)

- [x] Q9의 선행 검토·작은 CPU 입력 준비·두 사례의 첫 관찰을 묶어 완료했다. 42-frame
  env1에서 periodic 위상의 point-evidence 차이를 확인했지만 영상상 query 좌표의 물체
  표면 의미가 부족했다. Memory for Attention의 직접 중복을 반영하고 초기 관측 표면점과
  단순 visibility control로 다음 범위를 좁혔다. [결과·한계](buildup/robotics/pilot_studies/q9-refresh/README.md). (2026-09-15)

- [x] 조사 근거를 buildup 기준에 반영했다. 간결한 진입, 관찰·설명·방법 수정의 반복,
  탐색/확증과 실패 유형을 구분했다. Paper의 기존 기준은 유지하며 최종 실험 완료 후
  일곱 조건을 모두 충족할 때 `paper/`를 연다. Q9 다음 범위를 정리했고 기존 결과는 유지했다.
  [반영 범위](buildup/selection.md#buildup-workflow-update-2026-09-15). (2026-09-15)

- [x] Buildup의 gate를 대학의 연구 제안·COS·ICLR/CVPR/NeurIPS 지침과 비교했다. 문서의
  stage 구분은 대체로 적절하지만 실제 초기 운영의 검증/중단 부담은 과하고 탐색적 수정
  경로가 부족하다고 평가했다. 당시에는 개선 제안만 기록하고 규칙·기존 결과·Q9 선택을 유지했다.
  [비교 근거와 적용 범위](buildup/selection.md#buildup-gate-assessment-2026-09-15). (2026-09-15)

- [x] Q6의 성공 판정 불일치를 source/보존 record로 재평가하고 Q6/Q9/Q7/Q14를 비교해
  Q9를 다음 Stage 4–5 대상으로 선택했다. Q6의 first-event 재설계 가능성은 남겼으며
  DynaMem source 5개와 DynaBench annotation/time 37개를 byte 검증했다. 새 수치 실행은 없다.
  [비교·근거·선택 경계](buildup/robotics/related_work/policy-geometry.md#q6-reassessment-and-reserve-comparison-2026-09-15). (2026-09-15)

- [x] Q6 CPU readiness를 실행하고 원본 성공 판정 불일치로 보류했다. Source 265개·두
  checkpoint schema·합성 검증을 통과했지만 다섯 번째 record의 step 33에서 substep
  reward [1,0]과 official solved=false가 달랐다. 별도 원본 engine 재구성으로 확인하고
  실패 근거를 보존했다. 나머지 135개·held-out pilot은 미실행이다.
  [검증·보류·재현](buildup/robotics/pilot_studies/q6-timing/README.md#verified-outcome-2026-09-15). (2026-09-15)

- [x] Workspace 파일 삭제 후보를 검토했다. Source archive/PhysX cache/bytecode 약 458 MiB와
  외부 backup 확인이 필요한 Q12 약 3.93 GiB를 구분했다. ZIP 중복·source 1,495개·기존 hash가
  일치했고 실제 삭제는 없다. Q10 HDF5는 현재 없음을 확인했다.
  [용량·보존 조건·검증](docs/reproducibility.md#workspace-file-cleanup--2026-09-15). (2026-09-15)

- [x] Q6 Stage 4–5를 완료했다. 고정 추정·교체 시점에서 지연 순서 효과가 사라지는 구조적
  대조군을 정의하고 두 level·64 seeds·8 profiles, 성공 판정·중단 기준·CPU 비용을 명시했다.
  공식 source 9개를 추가 검증했다. REMAC 최종 PDF 접근은 미해결이며 runtime/weights 실행은 없다.
  [Prior 검토](buildup/robotics/related_work/policy-geometry.md#q6-stage-4-review-2026-09-15) ·
  [측정 설계](buildup/robotics/questions/temporal-mismatch-decomposition.md#stage-5-assessment-2026-09-15). (2026-09-15)

- [x] Q6/Q7/Q9/Q14를 비교해 Q6을 다음 Stage 4–5 대상으로 선택했다. 실제 지연 순서와
  지연 추정 오차를 분리하는 질문으로 좁혔으며 Q9는 reserve다. PaperReview 8개 note의 발췌,
  공식 source 11개와 checkpoint metadata를 확인했다. Runtime/학습/payload 취득은 없다.
  [비교·근거·한계](buildup/robotics/related_work/policy-geometry.md#candidate-comparison-2026-09-15). (2026-09-15)

- [x] Q12 BOP 실패와 calibration 근거의 한 번의 source/record 재평가를 완료해 추가 투자를
  `deferred`로 결정했다. Visibility의 단방향 조건과 depth 기반 pose annotation을 확인했고,
  개별 ray 누락 원인은 미확정으로 남겼다. 8개 freeze·37개 입력·18개 출력 파일을 byte 검증했다.
  [근거·경계·재진입](buildup/robotics/pilot_studies/q12-generated-geometry/real/README.md#reassessment-2026-09-14). (2026-09-14)

- [x] 지정한 container 53개와 Q12 image 4개를 읽기 전용으로 검토했다. Image 참조는 모두
  0개이며 이전 Q12 runtime 세 개는 삭제 후보, real-input은 유지 권장이다. Container는
  transfer 14개와 다른 작업 39개의 결과 확인 수준을 구분했다. 실제 삭제는 없다.
  [대상·조건·보존/재개/재현의 차이](docs/reproducibility.md#docker-cleanup-assessment--2026-09-14). (2026-09-14)

- [x] Frozen BOP 입력 감사를 CPU Docker에서 실행·독립 검증했다. 5개 mesh와 10개 case의
  입력/좌표 검사는 통과했지만 320개 ray 중 6개가 model과 교차하지 않아 `DEFER_RAY_SUPPORT`다.
  모든 case·residual·freeze를 보존했고 sensor/pose calibration은 미확정이다.
  [결과·실패 사례·재현](buildup/robotics/pilot_studies/q12-generated-geometry/real/README.md#verified-real-input-results-2026-09-14). (2026-09-14)

- [x] Q12 BOP 입력 감사의 protocol·부분 취득·새 CPU Docker·독립 verifier를 준비했다.
  37개 파일의 byte/CRC/hash와 합성 검증 9개 군을 확인하고 실제 수치 실행 전 고정했다.
  실행 묶음 검증의 실패 기록과 기존 freeze는 보존했으며 sensor/pose calibration은 미확정이다.
  [준비 결과·검증·다음 실행](buildup/robotics/pilot_studies/q12-generated-geometry/real/README.md). (2026-09-14)

- [x] Q12 대체 경로와 추가 보류를 비교해 BOP YCB-V의 제한된 real-data 입력 감사 준비를
  선택했다. Official revision·HTTP Range·ZIP/JSON metadata를 확인해 작은 취득 경로를 확보했다.
  Camera/model 수치 유효성은 미검증이며 image/mesh payload·새 runtime·completion 실행은 없다.
  [비교·근거·다음 범위](buildup/robotics/pilot_studies/q12-generated-geometry/README.md#alternative-routes-2026-09-14). (2026-09-14)

- [x] Q12 exact-coordinate merging·zero-area face 정리를 별도 CPU Docker에서 감사했다.
  정확한 표면 보존과 네 case의 고정 query 동등성은 확인했지만 mug에 degree-4 edge 3개가
  남아 현재 asset 경로를 보류했다. 추가 독립 감사로 잔여 face·query를 확인했고 v1·원본·
  모든 출력은 보존했다. Readiness revision·completion 비교는 진행하지 않았다.
  [근거·경계·다음 분기](buildup/robotics/pilot_studies/q12-generated-geometry/geometry/README.md#preservation-outcome-2026-09-14). (2026-09-14)

- [x] Q12 frozen camera/geometry readiness를 실제 두 YCB mesh에 실행했다. Box 두 view의
  camera·63개 robust 후보·두 oracle density 검증은 통과했으나 mug 두 view는 mesh gate에서
  중단돼 `REFINE_LINKAGE`다. 별도 CPU Docker 감사가 중복 좌표·degree-4 edge 9개·zero-area
  face 6개를 독립 확인했다. Freeze·네 case를 보존했고 mesh repair·completion 비교는 없다.
  [실제 결과·독립 감사·다음 분기](buildup/robotics/pilot_studies/q12-generated-geometry/geometry/README.md#verified-readiness-results-2026-09-11). (2026-09-11)

- [x] Q12 camera/geometry readiness의 두 YCB mesh 취득·hash 검증과 새 CPU Docker를 준비했다.
  Synthetic controls·네 case의 독립 verifier·변조 거부 검사를 통과했다. Synthetic support
  부족을 한 차례 수정한 이력을 보존하고 20개 파일을 실제 YCB 결과 전에 고정했다.
  실제 YCB rendering·completion 비교·hypothesis 승격은 없다.
  [Protocol·검증·다음 실행](buildup/robotics/pilot_studies/q12-generated-geometry/geometry/README.md). (2026-09-11)

- [x] Q12 native parity·원본 metadata 복원·GraspNet·controlled renderer·G3Flow 경로를
  비용/정보 가치로 비교했다. Stage 7은 `refine`: known geometry/camera와 고정 gripper
  pose의 collision 진단 준비를 선택했다. KNN fork와 작은 YCB asset 접근을 source/HEAD로
  확인했으며 새 실행·payload 취득·hypothesis 승격은 없다.
  [근거·비교·다음 분기](buildup/robotics/pilot_studies/q12-generated-geometry/README.md#linkage-route-assessment-2026-09-11). (2026-09-11)

- [x] 지정한 Q11/Q12 Docker image 네 개의 삭제 가능성을 검토했다. Container 참조는 모두
  0개다. Q11 두 개는 우선 삭제 후보, Q12 input은 삭제 가능, active Q12 model은 유지 권장이다.
  실제 삭제는 없으며 [결과 보존·재개·전체 재현의 차이](docs/reproducibility.md#image-cleanup-assessment--2026-09-11)를 기록했다. (2026-09-11)

- [x] Q12 frozen CPU reference protocol을 실제 네 입력에 두 process/총 8 forward로 실행했다.
  네 case의 독립 verifier와 NPZ 8개/NPY 48개의 byte 감사를 통과해
  `REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED`다. GT row·기존 freeze를
  보존했으며 native/물리 검증·새 metric·hypothesis 승격은 없다.
  [결과·artifact·한계](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11). (2026-09-11)

- [x] Q12 checkpoint의 408개 tensor schema·strict loading과 독립 metadata 검증을 완료했다.
  새 CPU Docker와 reference completion protocol을 준비하고 synthetic forward·pipeline 및
  copied-point 변조 검출을 확인했다. 실제 네 입력 추론 전 43개 파일을 고정했으며 native
  CUDA parity·물리 연결은 미검증이다. [결과·protocol·command](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md). (2026-09-10)

- [x] Q12 frozen input v1을 실제 네 쌍에 CPU Docker로 실행·독립 검증했다. 네 쌍의 schema·좌표
  controls와 원본 hash가 통과해 `INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`다.
  GT 반복 좌표와 train/test 중복을 기록했으며 protocol 변경·model inference·hypothesis 승격은 없다.
  [결과·검증·경계](buildup/robotics/pilot_studies/q12-generated-geometry/README.md#verified-input-results-2026-09-10). (2026-09-10)


- [x] Q12 공개 dataset/model 취득, 네 partial/GT 쌍의 name/CRC/SHA-256 검증과 CPU input
  protocol v1 고정을 완료했다. 새 Docker의 synthetic end-to-end·독립 verifier 검증을 통과했다.
  실제 XYZ array 검사와 model inference는 미실행이며 train/test object 중복·물리 좌표 metadata
  부재를 명시했다. [준비·protocol·다음 실행](buildup/robotics/pilot_studies/q12-generated-geometry/README.md). (2026-09-10)


- [x] Q12/Q13을 여덟 기준과 다음 측정의 정보 가치·비용으로 비교했다. Q12의 독립 입력/좌표
  검증 준비를 선택하고 Q13은 `deferred`로 두었다. 두 후보의 novelty와 empirical effect는
  미확정이며 protocol 고정·실행·학습은 시작하지 않았다.
  [비교·선택·다음 분기](buildup/selection.md#q12q13-measurement-selection-2026-09-10). (2026-09-10)

- [x] Q13 Stage 4–5를 완료했다. DISaM/GCNGrasp-VP의 직접 선행, virtual view와 새 관측의
  차이, 공개 evaluator의 상태·비용·성공 판정 한계를 확인했다. 기존 score와 decision value의
  제한된 진단으로 좁히고 조건부 검증안을 기록했다. Source/metadata만 검사했다.
  [근거](buildup/robotics/related_work/policy-geometry.md#q13-stage-4-review-2026-09-10) ·
  [가정·검증안](buildup/robotics/questions/action-relevant-view-selection.md#stage-5-assessment-2026-09-10). (2026-09-10)

- [x] Q12 Stage 4–5를 완료했다. G3Flow의 shared physical/virtual asset 경로와
  3DSGrasp의 좌표 복원 차이를 확인하고, independent completion/GT 입력 검증안을 정했다.
  Source/metadata만 검사했으며 Q12는 `under_review`; 다음 검토는 Q13이다.
  [근거](buildup/robotics/related_work/policy-geometry.md#q12-stage-4-review-2026-09-10) ·
  [가정·검증안](buildup/robotics/questions/generated-geometry-reliance.md#stage-5-assessment-2026-09-10). (2026-09-10)

- [x] Q12/Q13/Q14를 primary source와 공개 artifact 기준으로 재비교해 Q12 1순위,
  Q13 2순위, Q14 reserve로 정했다. G3Flow의 별도 encoding/consistency를 반영해 Q12의
  초기 가정을 수정하고 Q13의 기존 action-guided sensing 충돌을 기록했다. 문헌·source·
  metadata만 검사했으며 새 실행/학습·hypothesis 승격은 없다.
  [비교와 후속 과제](buildup/robotics/related_work/policy-geometry.md#reserve-reassessment-2026-09-10). (2026-09-10)

- [x] Frozen Q11 v3를 실행·독립 검증했다. 202 trajectories, 642 hashes, 85,472 labels와
  codec 411 chunks 검증 통과. Support는 충족했지만 grasp 1쌍/release 4쌍의 방향성 있는
  차이가 사전 alpha .025를 충족하지 못해 `STOP_NO_CONTACT_LOCALIZATION_SIGNAL`이다.
  고정 규칙대로 현재 method route를 종료했고 reserve 재비교를 다음에 두었다.
  [결과](buildup/robotics/pilot_studies/q11-action-compression/README.md#v3-verified-results) ·
  [종료 경계](buildup/selection.md#q11--discontinue-current-route-2026-09-10). (2026-09-10)

- [x] Q11의 한 번의 제한된 v3 revision을 구현·고정했다. Calibration 8개 / codec 144
  chunks에서 독립 복원 오차 0, joint/Linear rate·MSE overlap, 자연 residual grasp 5쌍 /
  release 3쌍을 확인했다. Contract test 3개 군을 통과하고 새 seed·support gate·중단 기준을
  freeze했다. 기존 v1/v2 변경, 새 physical episode·fit·grid 확대는 없었다.
  [Frozen v3](buildup/robotics/pilot_studies/q11-action-compression/v3/freeze.json). (2026-09-08)

- [x] Q11 Stage 7을 `refine`으로 결정했다. CPU Docker에서 기존 calibration 45개 점을
  감사해 6-bit/3-knot의 symmetric rate/MSE overlap과 strict-cap 초과를 구분했다.
  Held-out 동시 support 부재와 성공한 quantile residual만 사용한 localization 한계를
  근거로 제한된 수정·종료 조건을 기록했다. 새 rollout/refit/grid 확대·hypothesis 승격 없음.
  [결정](buildup/selection.md#q11--refine-2026-09-08). (2026-09-08)

- [x] Frozen Q11 v2를 Docker에서 실행하고 별도 감사했다. 194 trajectories, 617 hashes,
  83,056 labels와 held-out codec 460 chunks를 검증했다. Joint FAST 2/16 vs quantile
  16/16; exact gripper 후 총 성공 수는 같지만 joint 두 case가 반대로 바뀌었다.
  Grasp 9쌍/release 12쌍 모두 event/free 성공 차이 없음. Uniform byte cap support 부재로
  `INCOMPLETE_CODEC_SUPPORT`; protocol 변경·재실행 없음.
  [결과·감사](buildup/robotics/pilot_studies/q11-action-compression/README.md#v2-verified-results). (2026-09-08)

- [x] Q11 v2 physical pilot protocol·실행/분석 코드·source hash를 결과 전에 고정했다.
  8 calibration/16 held-out seeds, actual byte cap, exact gripper/scaling/interpolation controls와
  동일 arm-error localization을 정의했다. 새 Docker를 빌드하고 synthetic preflight 6개
  검사군을 통과했다. 실제 v2 episode/outcome은 아직 없으며 v1 자료는 보존했다.
  [Frozen v2](buildup/robotics/pilot_studies/q11-action-compression/v2/freeze.json). (2026-09-08)

- [x] Q11 Stage 6 measurement readiness v1을 새 Docker에서 실행·독립 검증했다.
  StackCube 8개 seed/859 actions, 원본 replay 16회와 공식 label 10,404개가 일치했고
  FAST 92 chunks 및 output hash 96개를 검증했다. `READY_FOR_CONTROLLED_PILOT`;
  압축 action의 물리 실행·학습·hypothesis 승격은 아직 없다.
  [Study](buildup/robotics/pilot_studies/q11-action-compression/README.md). (2026-09-08)

- [x] 사용자 선택에 따라 Q11을 단일 active buildup question으로 반영하고 Stage 4--5를
  완료했다. OAT 확장판/SA-VLA/MoEActok과 FASTer를 비교하고, FAST의 clamp/zero-fallback,
  mixed-unit controller와 sampled-contact 한계를 분리했다. Pinned source 9개 원격 일치와
  FAST 2개 파일 hash를 확인해 StackCube measurement-readiness 초안을 정했다.
  Runtime/학습은 미실행이며 Q12는 reserve다. [Q11](buildup/robotics/questions/contact-action-compression.md). (2026-09-08)

- [x] 사용자 관심 논문 63개를 PaperReview와 연결하고 대표 16개 insights 발췌 및 공식
  source를 참고해 Q11--Q15를 작성·비교했다. Q11 action compression과 Q12 generated
  geometry를 Stage 4--5 우선순위로 선택했다. Novelty/Stage 6/hypothesis는 미확정이며
  PaperReview 수정, 새 학습·실행·대규모 download는 없었다.
  [관심 mapping·근거·비교](buildup/robotics/related_work/policy-geometry.md). (2026-09-08)

- [x] 지정된 research3 Docker image 8개와 다운로드 data의 정리 가능성을 검토했다.
  Container 참조는 없고 recipe는 보존돼 있다. Q10 원본 27.80 GiB는 외부 사본 검증 후
  삭제 후보, Q8의 작은 공통 input과 결과는 보존 권장이다. 실제 삭제는 하지 않았다.
  [보존 목적·삭제 조건](docs/reproducibility.md#cleanup-assessment--2026-09-08). (2026-09-08)

- [x] Q1 refinement audit을 완료했다. Pinned task source, public tree의 26 checkpoints,
  열 개 metadata와 primary work를 확인했으나 grounded continuation을 정당화하지 못해
  현재 formulation을 `discontinue`했다. V3 원본을 보존하고 추가 실행은 하지 않았다.
  [Audit](buildup/robotics/related_work/q1-artifact-schema.md#bounded-refinement-audit--2026-09-08) ·
  [Stage 7](buildup/selection.md#q1--discontinue-2026-09-08). (2026-09-08)

- [x] Q1 v3을 새 CUDA Docker에서 실행하고 8쌍의 exact initialization, 16 trajectories,
  96 predicate labels와 800 official step labels를 독립 검증했다. 여섯 조건 모두 PPO-EE
  4/8, PPO-Joint 8/8로 label/rank 변화가 없어 `NO_LABEL_CHANGES_UNINFORMATIVE`다.
  Stage 7은 `refine`; 현재 two-policy/PickCube route 확대와 hypothesis 승격은 하지 않았다.
  [Study와 plot](buildup/robotics/pilot_studies/q1-predicate-stability/README.md). (2026-09-08)

- [x] Q8 심화 감사와 Docker 반복 검증 뒤 Q1을 다음 Stage 6 후보로 선택했다. 두 protocol의
  restore 비교 1,800회와 public demo transition 27회를 확인했다. Reset/contact-history
  문제를 scene reconstruction으로 보완했으며, v2 full-zero-qualified 98개 조건은 3회 모두
  성공해 recovery 차이를 구분하지 못했다. Demo middle-state replay는 0/18 통과했고 scalar
  recovery/empirical-success identity도 확인해 Q8은 `refine`이다. Q1 v3은 변경·실행하지
  않았다. [검증 기록](buildup/robotics/pilot_studies/q8-recoverability/README.md). (2026-09-08)

- [x] Q10 [Stage 7 decision](buildup/selection.md#q10--discontinue-2026-09-08)을 완료했다.
  Summary-only route와 현재 formulation은 `discontinue`, 더 넓은 RGB-relative question은
  미검증으로 구분했다. 근거 있는 reformulation이 없어 Q10을 active priority에서 제외하고
  종료 요약은 `literature/README.md`로 모았다. Q8/Q1은 비교 대상으로 남겼으며 실행·재개·
  artifact 삭제는 하지 않았다. (2026-09-08)
- [x] Q10 v6 regularized probe를 frozen protocol 그대로 CPU-only Docker에서 실행·검증했다.
  Nested primary macro BA 0.5791 vs v5 0.7239, gain interval [-0.2299, -0.0347]로
  `NO_USEFUL_SUMMARY_GAIN`이다. 기존 test의 0.6579는 exploratory로 유지했다. 16,488 fits,
  111,240 inner와 7,021 nested/test predictions를 독립 검증했다. Verifier의 log-loss clipping
  순서만 수정했고 refit/test 재실행·protocol 변경은 없었다. 상세 provenance는
  [study README](buildup/robotics/pilot_studies/q10-contact-observability/README.md)가 소유한다. (2026-09-08)
- [x] Q10 train-only validation audit을 새 Docker에서 완료하고 v6 regularized probe protocol을
  SHA-256으로 고정했다. 실패를 포함한 train recording은 pick/insert/remove 5/9/5개이며,
  모든 nested fitting partition에 양 class가 남았다. Remove는 action-bearing deletion
  6회 중 5회 선택이 바뀌고 CV BA가 0.6146에서 nested 0.4917로 하락했다. 675 fold count와
  309 nested prediction 독립 검증을 통과했다. Logistic probe는 아직 실행하지 않았다.
  [Audit와 protocol 기록](buildup/robotics/pilot_studies/q10-contact-observability/README.md#validation-audit-before-v6). (2026-09-07)
- [x] Q10 deterministic baseline v5를 결과 전에 고정하고 새 CPU-only Docker에서 실행·검증했다.
  413개 row(official train 309/test 104)를 보존했다. Train-CV-selected rule의 test macro BA는
  0.5261, prior는 0.5000, gain bootstrap interval은 [-0.0593, +0.0556]으로
  `UNCERTAIN_RESIDUAL`이다. Remove test가 한 recording에 집중된 한계를 기록했다.
  Invariant test 5개와 독립 1,144 prediction 검증을 통과했고 추가 probe는 실행하지 않았다.
  상세 결과·command·log는 [study README](buildup/robotics/pilot_studies/q10-contact-observability/README.md)가 소유한다. (2026-09-07)
- [x] Q10 larger denominator v4를 label-blind fixed-hash protocol로 실행했다. 기존 v2 anchor
  4개와 issue-free train 12/test 4개를 합친 20개 공개 recording 모두 열렸고, 570 segments 중
  569개가 matched였다. `No action.`을 제외한 524 target rows는 success 473/failure 51이며
  train failure 40, test failure 11이다. Pick 10, insert 29, remove 11 failure로 세 action이
  양 split에서 비교 가능해 `PASS_DENOMINATOR`; place는 failure 1개라 다음 baseline에서
  제외한다. 새 16개 transfer는 6.16 GB compressed/27.49 GB extracted였고 CPU-only Docker로
  실행했다. (2026-09-06)
- [x] Q10 Stage 6 v1--v3를 실행했다. v1은 official train 111/test 37 split과 148개 assigned
  HDF5, per-member byte range access를 확인했다. v2는 label-blind four-file subset 4/4를
  CRC/size/SHA-256 검증해 받고 45개 segment 중 공식 F/T issue 1개를 제외한 44개를
  RGB+F/T+proprioception으로 join했다(40 success/4 failure, `PASS_SCHEMA`). v3는 failure
  4개와 pre-fixed success control 4개의 sparse RGB를 소규모 manual audit했고, 세 방향 판단
  모두 오답/한 pair indistinguishable로 `MIXED_NEEDS_DENOMINATOR`였다. GPU는 사용하지
  않았고 종료 시 RTX 5090은 405/32,607 MiB, 0% utilization이었다. Public data만 사용했으며
  추가 annotation/learned method/three-gate는 시작하지 않았다. (2026-09-06)
- [x] Q10을 단일 Stage 6 candidate로 선택하고 resource boundary를 확인했다. REASSEMBLE
  전체는 54.8 GiB compressed/약 246 GiB extracted라 현재 storage에서 full extraction을
  금지하고 selective retrieval route를 택했다. 사용자는 public data 우선과 필요한 경우
  소규모 manual annotation을 허용했다. Q8은 `under_review`, Q1은 paused로 유지했다.
  (2026-09-06)

- [x] Q10/Q8의 Stage 5 critical-assumption analysis를 완료했다. 각 assumption에 scientific/
  operational necessity, current evidence, disconfirming observation, cost/duration, cheaper proxy와
  supported/contradicted/ambiguous decision branch를 기록했다. Q10은 matched usable denominator,
  Q8은 task-preserving physical perturbation을 first risk로 정했다. Q10을 resource 확인 전
  provisional Stage 6 priority로 두되 어느 후보도 아직 선택하거나 실행하지 않았다. Disk/GPU
  상태는 read-only로만 확인했고 기존 image/container는 조회하거나 사용하지 않았다.
  (2026-09-05)
- [x] Q10/Q8의 Stage 4 preliminary literature review를 완료했다. Q10은 REASSEMBLE의
  4,551 contact-rich demonstrations, synchronized RGB/state/force와 segment success label로
  public empirical route가 확인됐지만 generic multimodal fusion claim은 FINO-Net 계열이
  점유한다. Q8은 CFNBC와 broad claim이 충돌해 frozen-policy physical-state closed-loop
  return-probability diagnostic으로 경계를 좁혔다. 두 후보 모두 final novelty나 hypothesis로
  확정하지 않았고 외부 artifact를 내려받거나 실행하지 않았다. (2026-09-04)
- [x] Second-round frontier에서 Q6--Q10의 정식 candidate record를 작성하고 기존
  candidate와 Stage 3의 8개 기준으로 비교했다. Q10 Contact-Outcome Observability와
  Q8 Local Recoverability Coverage를 preliminary literature review 우선순위로 정했다.
  어떤 candidate도 hypothesis로 선택하지 않았고 실행도 시작하지 않았다. (2026-09-04)
- [x] 첫 candidate set의 evaluation/diagnosis 편향을 보완하기 위해 Stage 1을 확장했다.
  Temporal execution, constructed-to-natural failure transfer, recoverability-aware data
  coverage, dynamic spatial memory와 contact-rich outcome observability의 recent frontier,
  direct collision pressure와 empirical opportunity를 official source로 정리했다. Q1 실행은
  추가 candidate 비교 전까지 일시 정지했다. (2026-09-04)
- [x] Q1/CD4/CD1을 `docs/buildup.md`의 Entry To Hypothesis Formulation 8개 항목으로
  비교했다. Q1은 8개 조건을 문서상 충족하지만 실행되지 않은 measurement uncertainty
  때문에 `repeat feasibility study`, CD4는 direct collision로 `reformulate`, CD1은
  public multi-action denominator 부재로 `refine`을 선택했다. 어떤 후보도
  `ready_for_hypothesis`로 넘기지 않았다. (2026-09-04)
- [x] CD4/CD1의 Stage 4 preliminary literature review를 완료했다. CD4의 counterfactual
  replay core는 AgenTracer/CAR/AgenticRAG-FP와 direct collision이고, CD1의 broad
  calibration-to-utility framing도 TDQC와 decision-risk/utility-directed work가 이미
  점유함을 확인했다. 각 후보의 official artifact 상태, 최소 차이와 strongest adjacent
  baseline을 기록했으며 외부 artifact는 내려받거나 실행하지 않았다. (2026-09-04)
- [x] Q1의 source/license와 comparable pairwise input을 read-only로 확인했다. ManiSkill3
  `v3.0.1` full commit, public demonstration revision과 두 public PPO checkpoint checksum을
  기록하고, 16-rollout small-subset [protocol v3](buildup/robotics/pilot_studies/q1-predicate-stability/manifest_v3.md)를
  결과 전에 고정했다. 외부 artifact는 내려받거나 실행하지 않았다. (2026-09-04)
- [x] Q1의 public artifact/state-log/evaluator schema를 read-only audit했다. 근거 없는
  추가 hard rule을 폐기하고
  [feasibility protocol v2](buildup/robotics/pilot_studies/q1-predicate-stability/manifest_v2.md)를
  `docs/buildup.md` 기준으로 다시 작성했다. (2026-09-04)
- [x] Robotics에 한정하지 않은 cross-domain context map과 서로 다른 research-gap
  candidate 5개를 도출하고 Stage 3 비교로 CD4/CD1을 preliminary review 대상으로
  정했다. 아직 `ready_for_hypothesis`인 question은 없다. (2026-09-04)

- [x] 현재 workspace의 `AGENTS.md`, `docs/` workflow와 stage 상태를 확인했다. (2026-09-02)
- [x] Robotics 중심의 initial research scope와 high-level constraints를 기록했다. (2026-09-04)
- [x] `PaperReview`와 official sources를 사용해 7개 track의 initial research context와 accessible substrate를 정리했다. (2026-09-04)
- [x] 서로 다른 candidate research question 5개를 작성·비교하고 Q2/Q1을 preliminary-review priority로 정했다. (2026-09-04)
- [x] Local compute/runtime을 확인했다: RTX 5090 32,607 MiB, Docker 29.6.1,
  NVIDIA runtime, 20 CPU와 약 67 GB RAM. 당시 local Isaac image는 목록만 확인했으며,
  이후 사용자 결정에 따라 전부 연구 범위 밖 read-only 자산으로 제외했다. Workload
  GPU smoke test는 실행하지 않았다. (2026-09-04)
- [x] Pre-existing Docker/simulator 자산을 research에서 사용·수정·삭제하지 않고 모든
  environment를 project-specific Dockerfile과 새 이름으로 구성하는 boundary를 고정했다.
  (2026-09-04)
- [x] Q2/Q1의 2024--2026 focused prior audit를 완료했다. Q2는 direct-prior collision으로
  `reformulate` 후 `deferred`, Q1은 exact predicate-stability question을 직접 점유한
  prior를 이번 preliminary review에서 확인하지 못해 `under_review`다. (2026-09-04)
