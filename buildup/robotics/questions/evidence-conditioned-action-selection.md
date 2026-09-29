# Evidence-Conditioned Action Selection

Updated: 2026-09-29 · ID: Q17

## Status

`feasibility_study` — [후보 비교](../../selection.md#q17-selection-2026-09-28)에서 다음 제한된 탐색 질문으로 선택했다. 아직 현상 확인, 방법의 이점, formal hypothesis 또는 paper claim은 없다.

## Question And Significance

능동적 관찰과 물체 조작으로 과업에 필요한 정보를 얻은 뒤, 로봇 정책은 그 정보를 올바른 **다음 조작 대상·목표·행동**에 얼마나 안정적으로 연결하는가? 실패할 때 정보 획득/보존, 목표 선택, 물리적 실행 중 무엇이 주된 제약인지 구분할 수 있는가?

이는 active perception과 long-horizon VLA의 경계에 있다. 새로운 시점이나 더 큰 memory를 추가해도 획득한 정보가 행동 결정에 쓰이지 않으면 과업은 완료되지 않는다. 반대로 이미 올바른 대상을 고르지만 제어가 실패한다면 정보 표현을 바꾸는 방법은 우선순위가 낮다.

## Evidence And Close Prior

- **논문 주장:** [ActiveArena](https://arxiv.org/html/2609.24124)는 35개 능동 지각 조작 과업, 단계/가시성/정보 획득 주석, ID/OOD 평가와 VLA baseline을 제공한다. 저자의 실패 분해에서 ActiveArena-OFT의 실패 중 `Context Retained`는 ID 91.5%, OOD 89.5%다. 이 범주는 최종 화면에 관련 물체가 보였다는 뜻일 뿐 **숨은 색·날짜를 읽었거나 올바른 목표를 선택했다는 증거가 아니다**. 저자도 이를 downstream reasoning과 execution이 섞인 상태로 해석한다. Memory writing, subtask supervision과 planner-mediated memory는 논문에서 이미 비교했다.
- **공개 artifact 사실:** [공식 simulator/evaluator](https://github.com/leeibo/ActiveArena), [공식 VLA 코드](https://github.com/leeibo/ActiveArena-VLA), [한 task의 LeRobot 자료](https://huggingface.co/datasets/leeibo/ActiveArena-Data/tree/main/check_block_color)와 [공식 checkpoint](https://huggingface.co/leeibo/ActiveArena-VLA)가 공개돼 있다. 전체 dataset은 76.6 GB, `check_block_color` 폴더는 2.79 GB다. 공개 LeRobot viewer에 보이는 필드는 영상·state·action·subtask/stage/keyframe 등이며 논문의 HDF5 `info_complete`, object masks, outcome field가 같은 형태로 제공되는지는 미확인이다. 저자의 RTX 4090 단일 평가 프로파일은 peak VRAM 21.8 GB를 보고하지만, 이 workspace에서 Docker 실행·메모리 적합성은 검증하지 않았다.
- **가까운 선행:** ActiveArena 자체는 evidence acquisition, memory, planning과 subtask supervision을 다룬다. [PALM](https://arxiv.org/abs/2601.07060)은 affordance와 progress cue로 long-horizon 실행을 개선한다고 보고한다. [From Seeing to Doing](https://arxiv.org/abs/2505.08548)은 spatial reasoning에서 조작 결정으로의 연결을 다룬다. [Memory for Attention](https://arxiv.org/abs/2607.23797)은 제한된 예산의 재관찰을 다룬다. 이들보다 단순히 중간 표현·planner·memory를 붙이는 것은 차별점이 아니다.
- **에이전트 추론:** 획득한 단서를 행동에 연결하지 못하는 실패가 존재할 수 있다. 위 `Context Retained` 수치만으로 그 빈도나 원인을 추정하지 않는다. 먼저 같은 과업/상태에서 task evidence의 유무와 target/action 선택을 분리해야 한다.

## First Feasibility Observation

[공식 source와 공개 자료의 제한 검사](../pilot_studies/q17-evidence/README.md#current-findings-and-decision)에서 확인한 **artifact 사실**은 다음과 같다. `check_block_color` 학습 시연 100개 모두의 task text가 정답 색을 밝히지만, 공식 fixed-seed ID/OOD의 `unseen` instruction 250개씩에는 정답 색이 없다. `seen`은 각 split의 200/250개에서 색을 밝힌다. 이 차이는 정책 실패나 평가 누출의 증거가 아니다. 공개 Parquet에는 `info_complete`, target mask, 독립적인 최종 성공 판정이 없으며, source의 `info_complete`도 실제 색 판독의 pixel-level label이 아니다. 두 전문가 시연에서는 검사 중 색이 보이고 뒤의 선택 직전 화면에서는 보이지 않는 장면을 직접 확인했다.

**해석:** 학습 시연에서 정답 목표를 맞히는 것만으로는 시각적 단서 이용을 주장할 수 없다. 소수의 같은 현재 영상·상태에서 generic 지시와 과거 관찰의 유무를 바꾸는 공식 checkpoint의 행동 민감도 검사를 우선한다. 이는 오프라인 대조로서 물리적 성공이나 오류 원인 분해를 확정하지 못한다. 정답 텍스트 의존성과 기억 의존성의 후보를 가르는 첫 단계로만 쓴다.

**오프라인 관찰:** 공개 OFT checkpoint 한 개를 별도 GPU Docker에서 학습 시연 두 개의 동일 현재 영상·상태에 적용했다. Generic 지시에서 전체 과거 화면 대 현재 화면만 사용한 16-step 행동의 시연 L1은 green 사례 0.038/0.129, red 사례 0.029/0.082였다. 정답 색을 task text에 명시하면 각각 0.020/0.013으로 낮아졌다. 정답 색을 subtask text에만 넣어도 행동은 바뀌지 않았는데, 해당 checkpoint의 행동 prompt가 task instruction을 선택하는 source 계약과 일치한다. 보조 생성 문장은 green을 red로 잘못 썼고 red의 색은 명시하지 않았다. 두 시연은 **학습 자료**이고 history 대조는 색 외의 문맥과 입력 길이도 바꾸므로, 이 결과는 실제 visual evidence use 또는 목표 선택·실행 오류의 증거가 아니다. 여덟 행동 출력과 동일 현재 상태·입력 hash를 독립 검산했다. [원본·검증·해석](../pilot_studies/q17-evidence/README.md#limited-offline-policy-probe)을 따른다.

**Held-out 관찰:** 공식 ID seed의 첫 세 `check_block_color` 사례를 공개 OFT checkpoint와 탐색용 Docker websocket bridge로 실행했다. 세 사례 모두 저장된 정책 요청 화면에서 뒷면 색이 판독되지 않았고, 사전 정의한 pad 선택도 확인되지 않았으며 native 성공도 없었다. 이는 **정보 획득 이전의 관찰·조작 실패가 이 세 사례를 지배했다**는 제한된 관찰이지, 정보 획득 후 목표 결합 오류의 존재나 부재를 검증한 결과가 아니다. Bridge와 공식 서버의 held-out 동일성은 미확인이고 렌더러의 OIDN 오류도 남는다. [case 원본·판독·복구](../pilot_studies/q17-evidence/README.md#held-out-fixed-seed-observation-and-route-decision-2026-09-28)를 따른다.

**대체 과업 첫 관찰:** `count_color_kinds_press_button`의 공식 ID seed `100000`에서 정책 입력 화면에 빨강·초록·파랑 블록이 드러난 뒤, 공개 checkpoint의 탐색용 Docker bridge는 정답 3번이 아닌 2번 버튼을 89번째 동작에서 실제로 눌렀다. Native 판정은 `wrong_button_pressed`다. 이 한 사례는 단서 이전에 멈춘 `check_block_color`와 달리 **가시적 단서 이후의 오답 선택**을 제공하지만, 첫 화면부터 세 색 종류가 상당 부분 보이므로 긴 시간의 기억 실패나 새로운 방법의 필요성을 입증하지 않는다. [입력·버튼 joint·검산](../pilot_studies/q17-evidence/README.md#color-count-button-route-2026-09-28)을 따른다.

**일치 재생과 늦은 oracle 진단:** 첫 사례를 같은 seed·지시문으로 재실행한 결과 89개 동작, 6개 정책 요청의 RGB·18D 상태·행동 chunk와 native 오답이 원본과 정확히 일치했다. 80번째 동작에서만 outgoing 정책 요청에 count 3/버튼 3을 명시하고 과거 화면·상태를 유지한 탐색적 분기는 행동 수치를 약간 바꿨지만 89번째 동작에서 다시 2번 버튼을 눌렀다. 80번째 화면에는 팔이 이미 2번 버튼 위에 있어 개입이 **목표 선택 이후**였을 수 있다. 그러므로 이 결과는 기억·count/선택·버튼 실행의 원인 분해가 아니며 oracle 구제 불가능의 증거도 아니다. [재생 검산·런타임 한계](../pilot_studies/q17-evidence/README.md#matched-button-decision-diagnostic-2026-09-28)을 따른다.

**조기 answer-cue 진단:** 실제 정책 요청 이력에서 세 색은 step 16까지 나타나고 네 블록은 step 48까지 확인된다. Step 48 화면에는 팔이 아직 버튼 위에 없으므로 이 지점을 새로 고정했다. 원본과 89개 동작·6개 요청이 정확히 일치하는 재생을 검증한 뒤, step 48부터 정답 3/버튼 3 문장만 바꾼 분기도 동일한 48-step prefix와 RGB·상태 입력에서 출발했다. 행동 chunk는 변했지만 정책은 다시 step 89에 2번 버튼을 눌러 native 실패했다. 이는 한 사례에서 **조기 답 제공만으로 버튼 선택이 구제되지 않았다**는 관찰이다. 정책이 문장을 잘 쓰지 못했는지, 이미 내부적으로 목표를 고정했는지, 버튼 3 실행이 어려운지는 미분리다. [검산·한계](../pilot_studies/q17-evidence/README.md#earlier-answer-cue-decision-point-2026-09-28)을 따른다.

**다음 선택:** 아직 방법 개발이나 hypothesis로 넘기지 않는다. 이 사례의 prompt/seed 확대, full-history 대 최신 frame 대조는 지금 원인 분해를 보장하지 않으므로 진행하지 않는다. [과업군·다른 후보의 재비교](../../selection.md#q17-task-family-reassessment-2026-09-29)에서 ML 회전 시점 과업의 첫 공식 ID 사례를 저비용 판별 관찰로 선택했다. 이 과업의 색·순서는 지시에 이미 있으므로, 초기에는 목표 블록이 안 보이고 시점 이동 뒤 보이는지부터 확인한다. Q17 자체의 실패나 기각으로 일반화하지 않는다.

## First Observation And Working Explanation

`check_block_color`처럼 물체 뒷면의 색을 확인한 뒤 대응 pad를 고르는 **한 과업**에서 출발한다. 공식 source의 `info_complete`, target/mask, subtask transition 및 성공 판정이 실제 기록·평가에 어떻게 연결되는지 확인한 후, 제한된 고정 사례에서 같은 정책·초기 상태·실행 예산으로 일반 memory 입력과 정답 단서를 포함한 **허용된 과거 관찰**을 비교한다. 과거에 볼 수 없던 정보를 정책에 주는 oracle 조건은 진단 상한으로만 표기한다. `oracle subtask/target`을 준 경우에도 같은 정책·제어기와 실행 예산을 유지하는 대조를 통해 목표 선택 오류와 집기/놓기 실행 오류를 분리할 수 있는지 확인한다. Source annotation이 정보 충분성을 보증하지 않으면 사람 판독 또는 simulator task state로 별도 검증하며, 그 계약이 불가능하면 성공률을 근거로 결론 내리지 않는다.

잠정 설명은 **정보가 입력에 있을 때도 관련 증거를 조작 대상·목표에 결합하는 과정이 병목일 수 있다**는 것이다. 방법 초안은 획득한 단서, 선택한 목표와 다음 행동의 연결을 명시적으로 검사하거나 조건화하는 작은 interface다. 이는 관찰 결과에 따라 바뀌며, 기존 subtask supervision/affordance/planner와 구별되는 유효 사례가 없으면 새 방법으로 주장하지 않는다.

## Outcome-Dependent Decision

- 같은 정보에서 목표 선택 오류가 반복되고 단서/목표 oracle이 이를 구제하면, evidence-to-action coupling을 수정하는 작은 방법을 ActiveArena 기본 memory·subtask 대조와 비교한다.
- 목표는 이미 맞고 실행만 실패하면 조작 제어/affordance 쪽으로 질문을 수정한다. 추가 memory나 새 진단기를 정답으로 가정하지 않는다.
- 단서 확보가 실제로 안 됐거나 oracle 입력도 결과를 바꾸지 못하면 획득/관찰 조건 또는 과업 선택을 재검토한다. 같은 설정의 seed나 model variant를 자동 확대하지 않는다.
- 공식 annotation·상태 복원·checkpoint가 제한된 예산 안에서 해석 가능한 대조를 허용하지 않으면 `unavailable`로 기록하고 다른 과업·간결한 constructed 사례와 다른 후보를 재비교한다.

## Next Bounded Observation

첫 color-count 사례의 늦은 step-80 및 조기 step-48 oracle 진단 모두 실제 2번 버튼 press를 바꾸지 못했다. 다음은 다른 ActiveArena 과업군과 기존 후보의 [source·문헌·비용 비교](../../selection.md#q17-task-family-reassessment-2026-09-29)에서 정한 **ML 회전 시점 한 사례**다. 공식 ID seed `100000`의 초기/회전 후 정책 입력에서 green 목표의 가시성과 첫 집기 대상·물리적 집기를 기록한다. 처음부터 보이거나 첫 집기에 도달하지 못하면 정보 획득→목표 선택의 사례로 확대하지 않는다. 실제 simulator/evaluator 실행은 workspace 전용 Docker에서만 한다. 전체 dataset, 35-task 재현, model 재학습 또는 real robot을 선행하지 않는다. 단일 GPU의 짧은 평가에서도 관찰 가치가 낮으면 다른 과업·후보와 재비교한다. 이는 Q17 전체의 기각 기준이 아니다.

범위상 Q13은 **어느 시점을 볼 것인가**, Q9는 **언제 memory를 갱신할 것인가**를 묻는다. Q7은 constructed/execution failure의 **사후 판정 단서 전이**를 묻는다. Q17은 정보가 행동 선택에 반영되는 **전향적 정책 결정**을 묻는다. 겹치는 baseline과 데이터는 공유할 수 있으나 기존 frozen 판정을 소급 변경하지 않는다.
