# Failure-Source Generalization

Updated: 2026-09-16 · ID: Q7

## Status

`deferred` — [Q7/Q14 재비교](../related_work/policy-geometry.md#q7-q14-reassessment-2026-09-16)에서
Q14의 작은 action/calibration error 관찰을 다음으로 선택했다. 기존 Q7의 영상·38개 generation·
END 반복 대조는 보존한다. 현재 source-transfer 질문에 직접 연결되는 다음 관찰이 덜 구체적이라는
투자 판단이며 failure-source generalization의 반증이나 Q7 전체의 종료는 아니다.

## Facts

- 첫 관찰은 source 11행과 constructed input 4개, 세 camera의 45 score rows를 포함한다.
  입력 archive를 취득했고 CPU Docker에서 영상 판독·수치 비교·독립 계산 대조를 완료했다.
- Source label은 수정하지 않았다. 같은 시작 장면의 matching은 독립 rollout, 종료 시점이나
  natural failure의 개별 provenance를 보장하지 않는다.
- Metadata revision은 [source record](../related_work/comparison_sources.json), 실행 근거와 결과는
  [study owner](../pilot_studies/q7-failure-source/README.md)가 소유한다.
- SmolVLM2-2.2B-Instruct의 checkpoint를 pin/hash 검증하고 새 CUDA Docker에서 실행했다.
  첫 30개 뒤 END+END 8개를 추가하고 7개 동일 입력의 응답을 재사용했다. 누적 38개
  고유 generation의 JSON 형식 준수는 0/38이다. 학습, Guardian reproduction과 hypothesis 승격은 없다.

## Source Claims

[Guardian v4 §3.2/3.4](https://arxiv.org/html/2512.01946v4)는 BridgeDataV2에서 instruction
변경 또는 종료 이미지를 시작 이미지로 대체해 실패를 구성한다. UR5의 execution은 policy
rollout에 수동 label을 부여하고 planning은 별도로 구성했다고 설명한다. 이 구분을 유지한다.
[FailBench §3–4/Appendix A](https://arxiv.org/html/2609.03611v1)는 source별 성능과 관측 증거의
차이를 이미 다룬다. Cross-source gap 자체를 새 결과로 주장할 수 없다.

## Research Question Or Suspected Phenomenon

**같은 grasp 장면에서 구성한 no-progress 실패에 유효한 영상 변화 단서가 실제 실행 실패와
성공도 구별하는가, 아니면 task의 달성 상태를 확인해야 하는가?**

VLM 출력 뒤 **실제 START가 END 반복 이상의 판정 정보를 제공하는가**를 관찰했다.
이 모델·dev 사례에서 전체 label 일치 수의 이점은 없었고 두 사례의 변화는 서로 상쇄됐다.
남는 수정 초안은 **task 달성 증거를 맞춘 뒤 constructed/execution failure 사이에 어떤
판정 차이가 남는가?**다. Output format·입력 중복·기초 판정 능력만을 보는 비교로 끝나지
않을 작은 관찰을 다음에 검토한다. 아직 다음 실험이나 새 method를 확정한 것은 아니다.

원래의 detector ranking transfer 질문은 장기 평가 대상으로 남긴다. 첫 관찰은 이보다 좁은
단서의 전이를 다루며, 작은 사례만으로 detector 순위나 자연 실패 전체의 특성을 추론하지 않는다.

## Significance And Agent Inference

실패 데이터 생성 방식이 task 달성 여부 대신 쉽게 식별할 수 있는 시각적 단서를 제공하면,
그 데이터에서의 검증 성능을 deployment 신뢰도로 해석하기 어렵다. 이는 아직 잠정 설명이다.
반대로 실제 실패도 같은 단서로 설명되면 복잡한 verifier나 새 방법을 추가할 이유가 줄어든다.

## Closest Priors And Remaining Question

Guardian은 synthetic-to-real 평가와 multi-view ablation을, FailBench는 heterogeneous
source 평가를 이미 보고한다. 현재 검토한 부분에서 위의 같은 시작 장면을 이용한 비교는
확인하지 못했다. 이것이 exact novelty를 입증하지는 않는다. Construction 단서, task evidence와
관측 불충분을 분리해 보는 작은 관찰로 시작한다.

## First Observation

[실행 study](../pilot_studies/q7-failure-source/README.md)가 입력·사례 선택·실행 명령·시각 판독과
수치 결과를 소유한다. Source failure/success와 같은 시작 이미지를 종료로 쓰는 construction을
비교했다. 네 초기 상태 모두 목표 물체를 잡지 않은 것으로 보였으므로 construction을
미달성 snapshot으로 해석했다. 물리적으로 실행된 failure trajectory로 간주하지 않는다.

단일 camera의 전역 변화량은 일부 쌍에서 성공/실패 순서와 엇갈렸지만, 사후 three-view
median은 네 쌍의 순서를 모두 설명했다. 같은 영상을 반복한 source controls에는 success와
failure가 모두 있었다. 따라서 단순 변화량의 적용 한계와 더 강한 단순 대안을 함께 남긴다.

이미지에서 fingers의 열린/닫힌 상태와 물체의 상대 위치는 볼 수 있지만 secure grasp,
완료된 실패와 아직 끝나지 않은 동작의 차이는 확정할 수 없다. 현재 관찰은 자연 실패 전이의
확증이나 새 방법이 필요하다는 증거가 아니다.

## Simple Explanations And Disconfirmation

| explanation | first observation that distinguishes it | interpretation |
| --- | --- | --- |
| construction의 image duplication이 쉬운 단서를 만든다 | constructed negative에서만 equality/낮은 변화량이 label과 일치 | 단서 전이 문제의 사례 근거; learned detector가 이를 쓴다는 증거는 아님 |
| 실제 실패도 단순 change로 구분된다 | observed failure와 success가 같은 score 방향으로 분리 | 더 단순한 설명을 채택하고 새로운 verifier의 필요성을 낮춤 |
| task 달성 상태 또는 관측 정보량이 중요하다 | arm/background 변화와 label이 엇갈리거나 view에 따라 판독이 달라짐 | 상태 확인 또는 evidence 부족으로 질문·method sketch를 수정 |

같은 경로를 참조하는 positive/negative는 equality만으로 성공을 판정할 수 없다는 metadata상의
반례지만, label 오류나 실제 task 상태에 대해서는 아직 결론을 내리지 않는다. 시각 판독이
어렵다면 그 사례는 관측 한계의 결과다. 곧바로 Q7 전체를 기각하는 gate로 쓰지 않는다.

## VLM Observation And Revision

사실: 같은 15개 dev 사례에서 END-only와 START+END를 한 번씩 실행했다. 요청한 JSON 형식을
지킨 응답은 0/30이고, 29개 응답에는 evidence 문장이 없다. 사후에 명시적 원문 verdict만
추출하면 label 일치는 2/15 vs 6/15지만, always GOAL_NOT_MET는 9/15다. 원래 JSON 평가를
고치지 않았고 모델을 재실행하지 않았다. 이것은 작은 baseline의 interface/판정 한계다.

START=END인 7개에서도 4개 verdict가 바뀌었다. 따라서 유보 감소를 시간 정보의 이점으로
해석할 수 없다. 모델의 UNCERTAIN이 실제 관측 불가능성을 증명하지도 않는다. 개별 오판의
원인을 설명할 출력이 부족해 object 인식·grasp 이해·task 해석의 실패를 임의로 배정하지 않는다.

에이전트 추론: 새 verifier의 필요성보다 **추가 관측 내용의 영향과 입력 반복에 대한 민감도**를
먼저 나눠 볼 가치가 있다. 이 작은 대조는 이미 확보한 환경으로 가능하다. 모형 크기/형식 수리
때문에 끝없이 baseline을 교체하는 방향은 현재 선택하지 않는다.

## Repetition Control And Investment Review

사실: END+END 대조의 입력을 CPU Docker에서 확인하고 8개 새 generation·7개 동일 입력
재사용을 완료했다. START+END와 END+END의 원문 verdict는 새 8개 중 6개에서 같았다.
Drawer_ball failure에서는 실제 START가 reference 일치를 얻고 fruit failure에서는 잃어,
전체 일치 수는 둘 다 6/15다. 7개 재사용을 독립 반복 검증으로 세지 않는다.
[전체 결과·두 사례·한계](../pilot_studies/q7-failure-source/README.md#repetition-results-2026-09-16)가 상세를 소유한다.

에이전트 추론: 이전 END-only 대비 전체 일치 증가를 temporal reasoning의 근거로 쓸 수
없다. 하지만 두 사례 차이와 baseline 한계가 남으므로 START 무용성·조건 간 동등성·자연
실패 전이의 부재도 주장하지 않는다. 현재 모델/15개 사례의 추가 변형을 바로 확대하는
투자 가치는 낮다고 판단했다. 이후 재비교에서 현재 경로의 추가 투자를 `deferred`로 정했다.

## Evaluation And Method Sketch

현재 method sketch는 task-conditioned state verification에서 **task evidence와 source의
영향을 분리하는 비교**다. 본 결과는 그 전에 입력 반복만으로도 전체 metric이 바뀔 수 있다는
혼동을 보여 줬다. 이 진단 자체를 새 algorithm의 기여로 쓰지 않는다. 단순 three-view median의
paired ordering과 상수 판정 기준을 유지하며, 실패한 작은 VLM만을 새 방법의 근거로 삼지 않는다.

Q7 수정 질문을 Q14와 비교한 결과, 다음 관찰은 Q14로 선택했다. Q7을 다시 검토할 때는
task-state label을 유지하는 construction intervention과 가장 작은 유의미한 사례를 구체화한다. 출력 형식 강제, 새 대형 모델이나 frame/crop
sweep은 자동 다음 단계가 아니다. 선택한 설명을 검토할 관찰 경로가 생기면 필요한 baseline
수리도 그 정보 가치에 따라 함께 판단한다. 긍정 결과나 full benchmark를 비교의 선행조건으로
요구하지 않는다. Source별 detector ranking과 natural-failure transfer는 미검증으로 남는다.

## Investment Decision And Re-entry

현재 observation 비교는 source의 인과 효과를 식별하지 않는다. Exact detector input X가 같으면
숨은 source ID만으로 deterministic prediction이 달라질 수 없다. 반대로 task evidence의 일부만
맞췄다면 배경·view·timing·label·남은 시각 정보가 다를 수 있다. 어떤 matching과 intervention을
뜻하는지 정해야 한다. 이 논리적 경계는 cross-source generalization 문제 자체의 부정이 아니다.

재진입 초안은 **명시한 construction 변화에서 task-state label을 방어하고, 모델 능력/입력 단서와
failure-source 설명을 구별하는 작은 관찰**이다. 예를 들어 상태가 알려진 작은 simulation이나
completion 근거가 있는 real-data slice에 한 가지 label-preserving nuisance intervention을
두고, 단순 상태 규칙/적절한 detector가 어떻게 달라지는지 비교할 수 있다. 이때 generic
robustness와 source-transfer 질문의 차이도 설명한다. 전체 benchmark나 모든 provenance의
완성을 선행 gate로 요구하지 않는다.

이 구체적인 관찰이 생기면 Q14 및 다른 후보와 정보 가치·비용을 다시 비교한다. JSON 강제,
더 큰 VLM 교체, 같은 15개 사례의 변형 확대만으로 현재 경로를 자동 재개하지 않는다.
Guardian/FailBench 및 KITE와의 겹침과 선택 근거는 [재비교](../related_work/policy-geometry.md#q7-q14-reassessment-2026-09-16)가 소유한다.

## Resource And Recovery

Metadata는 `external/q7-sources/`, UR5 archive는 `datasets/q7-ur5/`, 첫 결과는 `runs/q7/`에
보존한다. [Study README](../pilot_studies/q7-failure-source/README.md#verification-and-preservation)와
[outcome.json](../pilot_studies/q7-failure-source/outcome.json)이 source pin, Docker recipe/digest,
command, dependency lock, input/output hash와 복원 절차를 소유한다. 첫 관찰은 CPU, VLM은
CUDA BF16을 사용했다. Model cache는 `checkpoints/q7/smolvlm2-2.2b/`, 30개 원문 출력은
`runs/q7/vlm/`에 보존한다. 새 여덟 출력·입력 대조는 `runs/q7/end_repeat/`에 있다.
이번 대조의 종료 container 3개만 결과·로그·실행 metadata 보존 후 삭제했다. Image/model/
원본 결과는 유지하며 다른 container는 변경하지 않았다.

## Decision Boundary

이번 성공 기준은 **양의 효과나 rank reversal이 아니라 설명을 구별할 실제 사례를 얻는 것**이다.
자료가 단순 change 설명을 지지하면 이를 기록하고 질문을 수정하거나 현재 경로의 추가 투자를
재평가한다. Candidate 전체의 폐기, hypothesis 승격과 paper novelty 판정은 현재 결정이 아니다.
현재 선택된 다음 작업은 Q14의 작은 feasibility study이며, Q7 수치 실행 재개는 선택하지 않았다.
