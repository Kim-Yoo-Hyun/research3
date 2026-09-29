# Policy, Geometry and Action: Candidate Search

Updated: 2026-09-23

최신 검토는 [Q16의 정책 적응 방향과 방법 개발 선택](#q16-policy-adaptation-direction-2026-09-23)이다.
첫 cube 관찰을 연구 방향 전체의 판정으로 쓰지 않고, 최근 predictive control/policy steering
흐름을 근거로 learned action-chunk policy의 적응 방법을 발전시키기로 했다.
아래 날짜별 선택과 첫 관찰의 수치 결과는 당시 범위로 보존한다.

이전 후보 선택의 근거는 [Q7/Q14 재비교](#q7-q14-reassessment-2026-09-16)가 소유한다.
Q7의 [영상·VLM·END 반복 관찰](../pilot_studies/q7-failure-source/README.md#repetition-results-2026-09-16) 뒤
primary sources와 다음 관찰의 정보 가치를 다시 비교했다. 이후 Q14의 작은 관찰을 완료했으며
[현재 판단](../../selection.md#q14-first-observation-2026-09-16)은 Q14 수정 방향 검토와
Q7 현재 경로의 보류다. 새 수치 결과는 [study owner](../pilot_studies/q14-frame-errors/README.md#results-2026-09-16)가 소유한다.
Q9의 후속 직접 선행과 첫 관찰 범위는 [Q9 focused review](#q9-focused-review-2026-09-15)를 따른다.
**Q9의 현재 refresh 경로는 선행·관찰 재평가 후 `deferred`**다.
[추가 투자 판단](#q9-research-value-2026-09-15)은 유지한다.
아래 Q12 → Q13 문헌 검토와 실행 전 상태는 당시의 기록이다.

문헌 검토는 **Q12 → Q13** 순으로 진행했으며 Q14는 reserve였다.
[2026-09-10 재비교](#reserve-reassessment-2026-09-10)가 Stage 3 우선순위 근거를 소유한다.
Q12의 후속 [Stage 4 source 검토](#q12-stage-4-review-2026-09-10)와
[Stage 5 assumption 검토](../questions/generated-geometry-reliance.md#stage-5-assessment-2026-09-10)는 완료했으며,
기본 G3Flow 경로의 제약과 조건부 measurement task를 기록했다.
[Q13 Stage 4 검토](#q13-stage-4-review-2026-09-10)도 완료했다.
[후속 비교 결정](../../selection.md#q12q13-measurement-selection-2026-09-10)은 Q12의 작은 입력 검증 준비를
선택하고 Q13을 `deferred`로 두었다. 이 문서의 Stage 4 상태는 각 검토 완료 당시의 기록이다.
이후 asset 취득과 frozen CPU input protocol은 [Q12 study](../pilot_studies/q12-generated-geometry/README.md)가
소유한다. 실제 입력 검사는 실행·독립 검증됐으며 completion model의 실행 결과는 아직 없다.
그 앞의 Stage 1--3 비교는 2026-09-08의 기록이며 당시 실행 queue가 아니다.

## Scope and evidence

사용자가 지정한 2024--2026 learning/policy/diffusion/geometry 및 VLA 논문에서 새로운
buildup question을 찾는 Stage 1--3 작업이다. 기존 Robotics, simulation/dataset-first,
foundation-scale training 제외 조건을 유지한다. 평가 지표의 변형보다 representation과
action/control 사이의 구체적 failure 및 학습·실행 개선 가능성을 우선한다.

**사실:** 지정한 63개 제목을 local registry에서 모두 찾았다. [Interest inventory](interest-papers.json)는
정규화한 제목, local folder, original source URL와 inspection 범위를 기록한다. 그중 16개
대표 논문의 `05_insights.md` 발췌를 읽었다. 63편 전체를 정독했다거나 사용자가 정독했다는
의미가 아니다. Eureka/DrEureka, 3D-VLA/Any3D-VLA, SAFE/ViSafe와 두 OmniVLA 동명이작을
분리했다. 사용자가 지정한 OmniVLA는 navigation 논문이다.

`/home/yoohyun/PaperReview`는 수정하지 않았다. Local notes는 discovery cue이며 아래
source claim은 official paper/project/code로 확인한 범위만 쓴다. 새로운 PDF, dataset,
checkpoint download, policy 실행과 학습은 하지 않았다. 일부 공식 페이지의 접근 실패는
arXiv나 저자 repository로 보완했으며, 미확인 artifact를 사용 가능한 것으로 표시하지 않는다.

## Interest map

| 관심 축 | 사용자 목록의 대표 anchor | 남겨야 할 연구 질문 |
| --- | --- | --- |
| 3D policy와 spatial grounding | DP3, EquAct, SpatialVLA, G3Flow, GravMAD, CordViP, ReKep, DiffuView | 어떤 geometric 정보가 실제 action에 필요하며 오차가 어디서 증폭되는가? |
| action representation과 efficiency | FAST, π0, DiffusionVLA, HybridVLA, TinyVLA, SmolVLA, SARA-RT | 같은 자원에서 어떤 action 정보 손실이 행동의 성공을 바꾸는가? |
| active perception와 temporal state | ActiveVLA, SaPaVe, SOMA, MemoryVLA, HiMe, 4D-VLA | 더 많이 관측/기억하는 것과 올바른 action을 선택하는 것은 언제 다른가? |
| language/reasoning에서 execution | PALM, AtomicVLA, ThinkAct, VLA-OS, CodeDiffuser, OWMM-Agent | reasoning/subgoal이 policy가 실제로 수행할 수 있는 행동과 일치하는가? |
| reward, adaptation와 contact | Eureka, DrEureka, ReinboT, Tabero, Scaffolding Dexterous Manipulation | reward와 feedback의 어느 성질이 dynamics 변화에도 보존되는가? |

전체 목록은 위 표에 반복하지 않고 inventory가 소유한다. Pure LiDAR completion은 이번
manipulation 질문의 직접 benchmark로 선택하지 않았다. QUAR-VLA/OmniVLA와 whole-body
방향도 관심 범위에 남지만 현재 embodiment 확보를 가정하지 않는다.

## Primary-source checks

아래 `paper claim`은 재현 결과가 아니다. `source access`도 Docker runtime 검증과 다르다.

| Source | 확인한 내용 | 이번 후보에 주는 압력 |
| --- | --- | --- |
| [FAST paper](https://arxiv.org/html/2501.09747v1), [official tokenizer](https://huggingface.co/physical-intelligence/fast) | DCT 기반 quantization/BPE action codec; 공개 encode/decode와 custom fit 경로 | Q11은 새 tokenizer 추가나 MSE 개선만으로 차별화할 수 없음 |
| [FAST source](https://huggingface.co/physical-intelligence/fast/blob/main/processing_action_tokenizer.py) | `dct` 후 계수를 scale/round하고 `idct`로 복원하는 code를 read-only 확인 | DCT 변환과 정상 BPE round-trip은 가역적; Q11 후속 감사에서 coefficient clamp와 decode zero fallback도 확인 |
| [SA-VLA](https://arxiv.org/html/2606.30113v1), sections 3--4 | state-conditioned decoding을 제안하며 FAST 등을 RoboTwin에서 비교 | state-aware adapter를 붙이는 일반 아이디어는 이미 직접 선행 |
| [OAT](https://arxiv.org/abs/2602.04215v2), abstract | ordered action tokens와 prefix decoding으로 fidelity/cost trade-off를 주장 | token 수를 줄이거나 가변 prefix로 실행하는 것만으로는 차이가 부족 |
| [Wavelet Policy](https://arxiv.org/abs/2504.04991v5), abstract | multi-scale latent action modeling과 world-prior memory 결합 | wavelet 교체 자체를 Q11 contribution으로 삼지 않음 |
| [G3Flow project](https://tianxingchen.github.io/G3Flow/), [code](https://github.com/TianxingChen/G3Flow) | 생성된 digital twin, semantic feature와 tracking을 manipulation policy에 연결; training/evaluation code 존재 | generated geometry + diffusion 조합은 이미 점유 |
| [DP3 code](https://github.com/YanjieZe/3D-Diffusion-Policy) | point-cloud policy, simulator/demo generation/training scripts와 expert download links 제공 | observed-only simple 3D policy가 Q12의 필수 baseline; 링크 존재와 checkpoint 검증을 구분 |
| [Measuring Uncertainty in Shape Completion](https://arxiv.org/html/2504.16183v1) | shape-completion uncertainty를 grasp quality score에 사용 | uncertainty로 grasp를 rerank하는 일반 주장은 새롭지 않음 |
| [SpringGrasp](https://tml.stanford.edu/SpringGrasp/), [FFHFlow](https://proceedings.mlr.press/v305/feng25a.html) | 각각 compliant planning, uncertainty-aware diverse grasp generation을 다룸 | Q12는 geometry uncertainty만 말해서는 부족; 관측 일치성/learned-policy 의존을 분리해야 함 |
| [ActiveVLA official repository](https://github.com/ZhenyangLiu/ActiveVLA-Injecting-Active-Perception-into-VLA) | viewpoint selection/3D zoom을 주장; code/model/evaluator release 항목은 아직 미완료라고 명시 | Q13은 해당 모델을 바로 실행할 수 있다고 가정하지 않음 |
| [SaPaVe project](https://lmzpai.github.io/SaPaVe/) | camera/manipulation action 분리, active-view learning과 Isaac Sim benchmark를 소개 | active perception를 VLA에 넣는 것 자체는 선행; 접근 가능한 download bundle은 이번 페이지에서 미확인 |
| [CamVLA](https://arxiv.org/abs/2607.05396), abstract | camera-frame action과 hand-eye transform을 예측해 base-frame action으로 합성 | calibration-free/camera-centric VLA 일반 제안은 이미 선행 |
| [DrEureka paper](https://arxiv.org/html/2406.01967v1), [code](https://github.com/eureka-research/DrEureka) | reward와 domain-randomization 설정의 LLM-guided search | Q15는 DR를 LLM으로 생성한다는 주장 대신 reward 선택과 dynamics의 상호작용을 물어야 함 |
| [Tabero official code](https://github.com/NathanWu7/Tabero) | tactile simulation/benchmark 연구의 공개 repository 확인 | contact 연구 접근 후보일 뿐 기존 host Isaac 자산이나 전체 VTLA 학습을 자동 사용하지 않음 |

Current web 확인일은 2026-09-08이다. ArXiv source만 확인한 새 논문은 acceptance/venue를
추정하지 않는다. OAT, SA-VLA, CamVLA 등은 사용자가 준 목록 밖에서 찾은 comparison
sources이며 PaperReview에 신규 등록하지 않았다. 이 검색으로 exact novelty를 확정하지 않는다.

## Five candidate questions

| ID | Question / suspected mechanism | First informative study | Main risk |
| --- | --- | --- | --- |
| [Q11](../questions/contact-action-compression.md) | 작은 평균 action 복원 오차가 grasp/release·접촉 전환을 불균등하게 손상시키는가? | 고정 codec의 round-trip과 원본 action을 동일 상태/controller에서 비교; gripper 별도 보존 control | 단순 gripper 보존 또는 scaling만으로 완전히 해결될 수 있음 |
| [Q12](../questions/generated-geometry-reliance.md) | 관측과 생성 geometry를 똑같이 사용하는 policy가 systematic completion bias에 취약한가? | oracle pose/geometry를 가진 작은 asset set에서 observed-only/full completion/consistency projection 비교 | uncertainty-aware grasping과 높은 overlap; cheap control 뒤 residual 미확인 |
| [Q13](../questions/action-relevant-view-selection.md) | 가장 잘 보이는 view와 action 선택을 바꿔야 할 정보를 주는 view가 다른가? | 같은 관측 비용에서 visibility/entropy/action-disagreement view와 oracle value 비교 | POMDP/value-of-information 선행, active model release 불확실 |
| [Q14](../questions/frame-error-propagation.md) | camera/base/object frame별 policy의 오차는 시각 정보 손실과 calibration mismatch 중 무엇에 지배되는가? | 순수 좌표변환, 실제 camera 이동, calibration 오류를 분리한 small policy comparison | 해석적 coordinate correction/augmentation만으로 설명될 수 있음 |
| [Q15](../questions/reward-dynamics-transfer.md) | nominal dynamics에서 고른 reward가 작은 dynamics shift에서 다른 contact strategy를 학습시키는가? | 고정 reward set × dynamics set의 소형 PPO 학습; normalization·potential-based shaping controls | 여러 학습 반복 비용, robust reward/DR prior |

이 질문은 모두 **에이전트 추론**이며 repository에서 새 현상을 관찰한 결과가 아니다.
각 question record에 evaluator, controls, negative-result branch와 source boundaries를 남겼다.
Final architecture, 완성된 novelty proof나 multi-domain evidence를 Stage 2 진입 조건으로
요구하지 않는다. 반대로 작은 codec/geometry 진단을 곧바로 VLA 성능 개선으로 주장하지 않는다.

## Stage 3 comparison

이 절의 순위는 최초 비교 당시의 기록이다. 현재 순위는 아래 reserve 재비교를 따른다.

H/M/L은 현재 상대적 판단이다. Overlap 열은 H일수록 위험이 크며, 나머지는 H일수록 유리하다.
시간은 candidate audit/pilot의 계획 추정으로 Docker runtime 측정치가 아니다.

| Criterion | Q11 | Q12 | Q13 | Q14 | Q15 |
| --- | --- | --- | --- | --- | --- |
| Significance | H: action fidelity가 물리 실행에 연결 | H: 3D prior가 잘못된 행동을 유도할 수 있음 | H: 관측 비용과 task decision 연결 | M: 배포 시 coordinate mismatch | H: reward가 학습한 strategy의 transfer |
| Empirical access | H: official codec와 encode/decode source | M: G3Flow/DP3 code, exact bundle 미확인 | M: custom small camera study 가능, named VLA 미출시 | M: small 3D policy 가능, fair frame variants 필요 | M: reward code와 simulator 존재, 학습 필요 |
| Feasibility | H: 대형 VLA 없이 시작 | M: oracle geometry pilot 후 frozen model | M: view/action 대응과 calibrated uncertainty 필요 | M: baseline 세 가지를 제대로 맞춰야 함 | L: reward×dynamics×seed 학습 반복 |
| Informational value | H: codec artifact인지 policy learning인지 분리 | H: simple geometry consistency만으로 충분한지 판정 | M: uncertainty가 실제 action utility를 예측하는지 | M: analytic cancellation이면 빠른 종료 | M: short-training ranking은 충분한 검증이 아님 |
| Resource fit | H: metadata/codec CPU, 실행 검증 small GPU | M: 3D policy 소형 학습/생성 의존성 | M: controlled simulator부터, full VLA 미사용 | M: 소형 policy 학습 가능 | L: 단일 GPU·여러 학습 비용 |
| Scientific depth | M: execution-aware distortion 원리의 가능성, 미확인 | H: observation와 generative prior의 사용 조건 | H: decision-dependent sensing | M: coordinate bookkeeping에 머물 위험 | H: shaping과 robustness의 연결 |
| Related-work overlap | H: SA-VLA/OAT/Wavelet, 일반 codec 제안 금지 | H: uncertainty-aware completion/grasp planning | H: ActiveVLA/SaPaVe와 고전 active perception | H: CamVLA/OC-VLA/equivariant policy | H: Eureka/DrEureka와 robust RL |
| Rigorous extension | H: held-out tasks/controllers, 학습한 small policy 평가 | M: objects/occlusion 분리, runtime/storage 확인 필요 | M: sensing cost와 action quality 모두 통제 | H: transforms와 rendering 원인 분리 가능 | M: training budget/seed/held-out dynamics 통제 |

### Decision

**Q11을 1순위, Q12를 2순위 Stage 4--5 검토 대상으로 둔다.** 이는 novelty나 Stage 6
실행 대상의 확정이 아니다. Q11은 action interface라는 사용자 관심과 작은 first experiment가
맞고, Q12는 geometry/policy 관심에 가장 가깝지만 setup/overlap risk가 더 크다.
Q13/Q14는 exploratory reserve, Q15는 compute 때문에 deferred다.

기존 Q3는 simulator-setting 평가, Q6는 timing mismatch, Q7은 failure detection source,
Q9는 memory refresh를 다룬다. Q11의 compression intervention과 Q12의 generated/observed
geometry intervention은 각각 이들과 구별된다. Q13도 memory 교체 주기 대신 새 view의
decision value를 묻지만 Q9와 인접하므로 중복 method 제안을 막아야 한다. Q8 자동 재개나
기존 데이터 보유량을 기준으로 한 topic 선택은 하지 않는다.

### Next bounded work

1. Q11: SA-VLA/OAT와 contact/skill-aware tokenizer의 exact residue를 확인한다. FAST
   quantization·normalization·controller interface를 분리하고, data/action units, gripper
   semantics와 event observation이 있는 작은 public subset 또는 생성 경로를 고정한다.
   첫 artifact는 code/source audit와 protocol 초안이다. 예상 준비 1--3 working days.
2. Q12: G3Flow/DP3 input bundle와 uncertainty-grasp prior의 state/geometry assumptions를
   확인한다. Learned-policy pilot 전에 observed-only와 hard observation-consistency
   control을 넣을 수 있는지 판단한다. 예상 source/setup audit 2--4 working days.
3. 둘 중 informative route가 남을 때만 Stage 6 protocol/source/input/output/disconfirmation을
   결과 전에 고정한다. 수치 threshold나 sample count는 이번 비교에서 임의로 확정하지 않는다.

Local GPU snapshot은 capacity 참고일 뿐 전용 GPU 예약이나 재현 성공 보장이 아니다.
기존 Docker image/data 삭제 요청으로 해석하지 않았으며 실제 asset 변경은 없다.

## Reserve reassessment 2026-09-10

**결정: Q12를 Stage 4–5 검토 1순위, Q13을 2순위로 선택하고 Q14는 exploratory reserve로
유지한다.** 이는 에이전트의 비교 판단이며 hypothesis, method 또는 Stage 6 실행 선택이 아니다.
Robotics, simulation/dataset-first, 약 6개월, 단일 GPU와 heavy training 제외 조건을 유지한다.

### Evidence scope

`PaperReview`의 G3Flow, DiffuView, ActiveVLA, SaPaVe, EquAct, OC-VLA insights 발췌를
discovery cue로 재검토했다. Primary paper의 method/assumption과 공식 code/project를 아래
범위에서 확인했다. 최신 검색은 exhaustive novelty audit가 아니다. 기존
[interest inventory](interest-papers.json)의 2026-09-08 inspection 기록은 그대로 보존한다.

**사실:** 이번 작업은 문헌·source text·원격 파일 목록 검사다. Dataset/checkpoint payload,
Docker build, simulator, inference와 학습은 실행하지 않았다. 파일 목록 접근은 파일 무결성,
라이선스 적합성, 호환 checkpoint 또는 실행 성공의 검증이 아니다.

### Primary evidence that changes the comparison

아래 논문 내용은 저자의 주장/방법 설명이며 workspace 재현 결과가 아니다.

| Candidate / primary source | 확인 범위와 source 내용 | 비교에 반영한 에이전트 판단 |
| --- | --- | --- |
| Q12 — [G3Flow v3](https://arxiv.org/html/2411.18369v3), §§3.2–3.4 | 초기 multi-view exploration, 관측 view와의 geometry/texture consistency 확인, 실제 point cloud·생성 semantic flow·robot state의 별도 MLP encoding을 명시 | “관측과 생성을 구분 없이 섞는다” 또는 “consistency 검사가 없다”를 선행의 결함으로 쓰지 않는다. 이미 구분된 입력에서의 잘못된 생성 정보 의존이 남는지 질문한다. 초기 탐색 관측도 baseline과 공유해야 한다. |
| Q12 — [Measuring Uncertainty in Shape Completion to Improve Grasp Quality](https://arxiv.org/html/2504.16183v1), §§III–IV | MC dropout으로 completion uncertainty를 구하고 후보 grasp 내부 영역의 uncertainty로 점수를 조정 | “action 근처의 shape uncertainty를 사용한다”까지 직접 선행이다. 단순 uncertainty-weighted geometry/reranking을 넘어서는 현상은 아직 미확인이다. |
| Q12 — [SpringGrasp](https://tml.stanford.edu/SpringGrasp/), [FFHFlow](https://proceedings.mlr.press/v305/feng25a.html) | 각각 shape uncertainty 아래 compliant grasp planning, partial geometry의 불확실성을 반영한 dexterous grasp generation/ranking | Grasp-only formulation이면 강한 adjacent baseline이다. 두 손가락 small-policy 결과를 dexterous baseline과 직접 같은 표에서 비교할 수 있다고 가정하지 않는다. |
| Q13 — [Active vision for dexterous grasping of novel objects](https://arxiv.org/abs/1708.04185) | 예정 contact 주변의 재구성과 접근 trajectory 안전을 위해 관측 방향을 선택 | 2017년부터 anticipated action을 고려한 sensing이 있다. 사용자 관심의 2024–2026 논문만으로 novelty를 판단하지 않는다. |
| Q13 — [Closed-Loop Next-Best-View Planning for Target-Driven Grasping](https://arxiv.org/abs/2207.10543), [Observe Then Act](https://arxiv.org/abs/2409.14891) | 각각 occluded target 탐색과 grasp 실행/계속 관측 결정, task-driven camera/gripper policy의 연계 학습 | Visibility뿐 아니라 기존 task-aware selector가 필수 비교 압력이다. Learned action disagreement가 언제 추가 관측의 가치를 예측하는지가 남은 질문이다. |
| Q13 — [ActiveVLA](https://arxiv.org/abs/2601.08325), [SaPaVe](https://lmzpai.github.io/SaPaVe/) | Task-relevant view/zoom 또는 camera/manipulation joint learning | 일반적인 active VLA 제안은 차별점이 아니다. 작은 controlled study가 이 논문들의 VLA 성능을 재현한다는 주장도 하지 않는다. |
| Q14 — [OC-VLA](https://arxiv.org/html/2508.13103v1), §III, [CamVLA](https://arxiv.org/html/2607.05396v1), method | OC-VLA는 calibration으로 action label과 실행 좌표를 변환하며 delta pose의 conjugation도 설명; CamVLA는 camera action과 hand-eye transform을 예측해 합성 | Camera-frame action 또는 calibration-free action head 자체는 선행이다. Shared/independent error의 차이가 알려진 변환식 이상을 설명해야 한다. |
| Q14 — [EquAct](https://openreview.net/pdf/7d1ac63392c225113c314e6263f1d18dfbff895e.pdf), abstract/intro, [code](https://github.com/ZXP-S-works/EquAct) | SE(3)-equivariant multi-task policy와 RLBench 학습/평가 경로 | Coordinate relabeling의 equivariance와 실제 camera 이동에 따른 가시성 변화는 다른 문제다. 기존 equivariance/relative-feature baseline 후 learning question은 아직 불명확하다. |

### Artifact accessibility

2026-09-10 read-only 확인. Source가 있다고 바로 실험 가능한 것으로 평가하지 않는다.

| Route | 확인한 사실 | 남은 operational uncertainty |
| --- | --- | --- |
| G3Flow | [source commit](https://github.com/TianxingChen/G3Flow/tree/e011ba6ae5a9493b93b02b2ca7b542f9cf629835), collection/process/train/eval scripts 존재. [Dataset adapter](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/G3FlowDP/dp/diffusion_policy_3d/dataset/G3FlowDP_dataset.py)는 `point_cloud`와 `feature_point_cloud`를 별도 key로 읽는다. | 실제 model encoder까지의 code-paper 일치, 물리 asset과 생성 twin의 독립성, matched observation·pose·semantic feature 비교는 미감사. |
| G3Flow bundle | [download source](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/tools/weights_for_g3flow/download_from_huggingface.py)는 [author HF dataset](https://huggingface.co/datasets/TianxingChen/G3Flow/tree/57431cd3131825fd5ccd49d92a253bfae8eb3ee1)을 가리킨다. API metadata는 nongated이며 weights/config와 `robotwin_assets.zip` 목록을 반환한다. | ZIP 내부의 정확한 mesh/observation pair, 생성 provenance, task-policy checkpoint와 용량/무결성은 검증하지 않았다. 전체 snapshot download를 시작하지 않는다. |
| DP3 | [official README](https://github.com/YanjieZe/3D-Diffusion-Policy)는 depth/point-cloud 생성, expert/demo, small-policy 학습/평가 scripts를 제공한다. | Observed-only baseline 구성 후보다. G3Flow와 공통 task/interface, exact expert/asset, 현 GPU의 새 Docker 호환성은 미검증. |
| ActiveVLA / SaPaVe | [ActiveVLA README](https://github.com/ZhenyangLiu/ActiveVLA-Injecting-Active-Perception-into-VLA)는 code/model/evaluator release 준비 중. SaPaVe project는 Isaac Sim 기반 ActiveManip-Bench를 설명하지만 확인한 페이지에 download bundle 링크가 없다. | Release 부재를 모든 active-perception 연구의 불가능으로 일반화하지 않는다. SaPaVe의 전 세계 공개 여부가 아닌 이번 official-page 확인 범위다. |
| active_grasp | [official repository](https://github.com/ethz-asl/active_grasp)는 ROS Noetic/MoveIt/VGN dependency, asset download 링크와 simulation entrypoint를 제공한다. | Asset 내부와 fresh Docker build 미검증. Q13에 작은 grasp study 경로가 있지만 ROS setup 비용이 있고 policy-specific question으로 연결해야 한다. |
| Q14 policies | [EquAct code](https://github.com/ZXP-S-works/EquAct)는 train/eval scripts와 CoppeliaSim/PyRep/RLBench 설치 경로를 제공한다. [CamVLA project](https://alibaba-damo-academy.github.io/CamVLA/)의 code는 Coming Soon이다. | Matched frame variants의 weight/data bundle은 미검증. Full OC-VLA/CamVLA 학습은 이번 resource fit 판단의 전제가 아니다. |

### Updated Stage 3 comparison

H/M/L은 현재 상대 판단이며 합산 점수나 empirical result가 아니다. Overlap만 H일수록
충돌 위험이 크다. Feasibility는 다음 uncertainty를 줄일 가능성이지 논문 완성 보장이 아니다.

| Criterion | Q12 generated geometry | Q13 action-relevant views | Q14 frame errors |
| --- | --- | --- | --- |
| Significance | H: geometric prior 사용 조건이 실제 행동에 연결 | H: 관측 비용을 행동 개선에 연결 | M: 배치 변화에 중요하지만 calibration 수리로 끝날 수 있음 |
| Empirical accessibility | M: 분리된 source input과 공개 asset 목록, paired geometry 미확인 | M: 공개 active_grasp simulator 경로, 최신 VLA bundle은 미확보 | M: EquAct/DP3 source, 공정한 frame variants는 새로 구성 필요 |
| Feasibility | M: source/asset audit로 먼저 줄일 수 있으나 tracking/semantics confound 존재 | M: 소형 scene/action/view 비교 가능성, valid selector 정보 경계가 관건 | H: action semantics와 변환식부터 싼 반례 검토 가능 |
| Informational value | H: 생성 정보가 유용한 조건과 simple consistency의 충분성을 함께 배움 | H: stochastic action 차이와 유용한 추가 관측을 구분 | M: analytic cancellation 확인은 유익하나 이미 알려진 답일 위험 |
| Resource fit | M: small policy 가능성, 전체 G3Flow native/model stack 비용 미측정 | M: VLA 대신 small planner 가능성, ROS/asset 비용 미측정 | M: 대수 검토는 저렴하나 공정한 learned 비교에는 복수 학습 필요 |
| Scientific depth | H: 관측 evidence와 prior의 의존 관계를 학습 문제로 확장할 여지 | H: policy uncertainty와 value of information의 관계를 시험할 여지 | M: 현재는 구체적인 learning residue보다 error bookkeeping에 가까움 |
| Related-work overlap | H: G3Flow는 이미 분리 encoding/consistency, grasp uncertainty도 선행 | H: action-guided sensing은 오래된 선행, active VLA도 혼잡 | H: OC-VLA/CamVLA/EquAct가 일반 framing 점유 |
| Rigorous evaluation path | M: pose·semantic feature·observation budget·training distribution 통제 필요 | M: 후보 view/action, no-view option, 이동/추론 비용을 함께 통제 필요 | H: 좌표 relabeling, 실제 view 변화, calibration 오류의 요인 분해 가능 |

### Selection rationale and next questions

**에이전트 추론:** Q12는 사용자 geometry/policy 관심에 직접 연결되며, 잘못된 생성 정보의
영향과 유용한 completion의 이득을 함께 다루는 질문이 남아 있다. 다만 confidence weighting,
source 분리, 관측 일치성 추가 자체로 novelty를 주장할 수 없다. 먼저 실제 생성 twin과 물리
geometry가 별개인지, 그 차이를 policy 입력에만 가할 수 있는지를 확인한다. 같은 generated
mesh를 물리 정답과 입력 양쪽에 쓰는 실험으로는 completion bias를 시험할 수 없다.

Q13은 두 번째 검토 가치가 있다. Disagreement가 크다는 사실이 아니라, 추가 view가
action 선택과 outcome을 바꾸는지를 비교할 수 있기 때문이다. 하지만 planned-contact
view selection과 겹치지 않는 최소 차이를 찾지 못하면 현재 formulation을 refine/defer한다.
Q14는 쉽다는 이유만으로 우선하지 않는다. Analytic transform/relative feature 뒤에 남는
구체적 학습 문제가 확인될 때 재검토한다. 어느 후보도 지금 반증되거나 novelty가 확정되지 않았다.

| Priority | 다음 bounded Stage 4–5 task의 산출물 | 부정적/불명확 결과에서 배울 것 |
| --- | --- | --- |
| 1 — Q12 | G3Flow/DP3와 uncertainty-grasp prior의 input/assumption 비교. 한 작은 task에 대해 실제 observation–generated geometry–physical geometry–action/evaluator의 provenance 연결과 simplest baseline을 문서화한다. Source/metadata audit부터 시작하며 예상 2–4 working days는 계획치다. | Pose/semantics 또는 관측량 차이로 전부 설명되면 geometry-reliance 주장을 좁힌다. 생성/물리 geometry를 분리할 수 없으면 해당 substrate를 보류한다. Source audit만으로 현상 부재를 선언하지 않는다. |
| 2 — Q13 | Action-guided grasping, closed-loop NBV, ActiveVLA/SaPaVe의 selection objective를 대조하고, 고정 추가 view 및 기존 task-aware selector 후 남는 비교를 명시한다. 후보 action/view와 관측 비용 정의 초안; 예상 1–2 working days. | 고정 view가 충분하거나 disagreement가 action sampling noise뿐이면 adaptive method route를 보류한다. 새 view의 oracle utility가 있어도 이를 추정할 정보가 없으면 measurement를 좁힌다. |
| Reserve — Q14 | 재검토 시 absolute pose/delta action, shared/independent transform error의 analytic counterexample부터 정리한다. | 알려진 좌표변환으로 충분하면 새 learning method를 학습할 이유가 없다. |

각 task의 더 구체적인 protocol/sample count/실행 비용과 disconfirmation은 Stage 4–5에서
정한다. Q12/Q13를 결합한 completion+active-view system, 새 학습 또는 Stage 6을 자동 시작하지 않는다.

## Q12 Stage 4 review 2026-09-10

**판단:** Q12의 질문은 유지하되, 공개 G3Flow를 그대로 실행하는 경로는 completion-bias
검증용으로 채택하지 않는다. Source-defined physical asset와 semantic-flow asset가 같은
경로를 공유한다. 독립된 completion 입력과 정답 geometry를 먼저 확보하는 작은 measurement
task가 필요하다. 이는 source에 근거한 feasibility 판단이며 physical failure나 현상 부재의
실험 결과가 아니다. Q12는 `under_review`; Stage 6/hypothesis로 승격하지 않는다.

### Scope and primary-work comparison

위 재비교의 G3Flow v3 §§3.2–3.4를 다시 확인하고, nearest uncertainty work의 method를 읽었다.
아래 세 편을 직접 비교 대상으로 삼았다. DP3는 simplest learned-policy substrate,
SpringGrasp/FFHFlow는 다른 embodiment/planning regime의 adjacent work다. 단순히 grasp에서
learned policy로 옮겼다는 이유로 novelty를 인정하지 않는다.

| Primary work | Exact question / claimed contribution | Assumption and boundary | Q12에 남을 수 있는 최소 차이 — 미검증 |
| --- | --- | --- | --- |
| [G3Flow v3](https://arxiv.org/html/2411.18369v3), §§3.2–3.4, §4 | 생성 digital twin의 semantic field를 tracking해 pose-aware manipulation과 object generalization을 개선할 수 있는가? | 초기 탐색·consistency 확인, twin 기반 pose tracking, 별도 feature encoding을 포함한다. 이 전체 표현의 이득이 shape completion 정확도 하나의 효과는 아니다. | 독립된 물리 정답 대비 틀린 completion에 대한 policy 의존이 simple controls 후에도 남는지. 관측/생성 분리 또는 consistency 추가 자체는 제외. |
| [Measuring Uncertainty in Shape Completion to Improve Grasp Quality](https://arxiv.org/html/2504.16183v1), §§III–IV | Stochastic completion의 오차를 후보 grasp의 quality score에 반영하면 ranking을 개선하는가? | MC dropout 평균/분산과 grasp 내부 영역을 사용한다. 단순 uncertainty weighting과 action-local shape score는 직접 선행이다. | 올바른 좌표·관측 일치성을 보존한 뒤에도 uncertainty score가 설명하지 못하는 learned-policy 의존이 있는지. 분산이 낮지만 bias가 크다는 현상 자체도 아직 측정하지 않았다. |
| [Robotic Pick-and-Place With Uncertain Object Instance Segmentation and Shape Completion](https://arxiv.org/html/2010.07892v2), §§III–V | 불완전한 perception 아래 grasp/place 실행 성공을 고려해 regrasp plan을 고르는가? | MC shape sampling, contact uncertainty, learned grasp/place success prediction을 비교한다. Antipodal grasp·stable placement와 modular planning 가정이 있다. | Q12가 성공 확률/접촉 uncertainty reranking으로 환원되는지 먼저 확인한다. 동일 input과 action 후보를 줄 수 있을 때 이 계열이 강한 external comparison이다. |

[SpringGrasp §III-D](https://arxiv.org/html/2404.13532v2)는 GPIS의 surface uncertainty와
compliant dexterous pregrasp를 공동 고려한다. [공식 source](https://github.com/Stanford-TML/SpringGrasp_release/tree/07c11318994001e42a92f342841ecbffbddd21e4)는
custom point cloud의 optimization 경로와 native dependencies를 제공하지만, 현재 Q12의
two-finger/joint-action task에 바로 대응하는 evaluator는 아니다. FFHFlow의 partial-geometry
uncertainty/ranking은 위 재비교에서 확인한 범위로 유지하며 이번에 별도 runtime audit를 하지 않았다.

### Read-only source evidence

Source revision, URL, byte length와 SHA-256, HF metadata와 ZIP index 요약은
[q12-sources.json](q12-sources.json)이 소유한다. 성공적으로 받은 source text 32개에서 관련
구간을 검사했다. Code import, native build, model loading, mesh rendering은 하지 않았다.
원격 branch 이름이 아니라 manifest의 revision을 기준으로 아래 내용을 해석한다.

#### One-task input-to-outcome trace

Audit task는 공개 `bottle_adjust_T`다. 이것은 실행 task 선택이 아니라 입력/출력 연결을
확인하기 위한 source case다. 아래 링크는 모두 G3Flow commit
`e011ba6ae5a9493b93b02b2ca7b542f9cf629835`에 고정한다.

| Link in the chain | Source fact | Implication / unresolved item |
| --- | --- | --- |
| Physical object | [task](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/RoboTwin_Benchmark/envs/bottle_adjust_T.py) selects train object 13 and a separate test ID list. [Actor factory](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/RoboTwin_Benchmark/envs/utils/create_actor.py) normally loads `models/bottles/base<ID>.glb` for collision and visual geometry, with model-data scale. | Simulator collision cooking may still differ from rendered surfaces; that would be a simulator/mesh issue, not evidence of learned completion bias. |
| Actual observation | [base task](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/RoboTwin_Benchmark/envs/base_task.py), `get_obs`, returns RGB/depth, camera matrices, point cloud and joint state. [Task config](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/RoboTwin_Benchmark/task_config/bottle_adjust_T.yml) uses head-only point cloud (`conbine: false`), FPS 1024, two-arm state. | Other camera arrays being logged does not mean the point policy receives their information. `get_obs` advances `scene.step()`: re-reading observations per input variant changes physical time. Future paired tests must use one frozen observation snapshot. |
| Supplied twin | [preprocessing](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/G3FlowDP/scripts/get_G3Flow_dataset.py) uses `scene_info.object_id/type` to load the same `base<ID>.glb`; OBJ from the same asset family initializes tracking. `apply_g3flow_dp` repeats this lookup at evaluation. | In this released path, object identity is supplied by simulator/expert metadata. No independent reconstruction from the measured partial view occurs at this point. An unchanged run cannot test the proposed source of geometry error. |
| Virtual features and pose | [tracker](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/G3FlowDP/featureTracking.py) calls [virtual renderer](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/G3FlowDP/imagineModel.py) on that GLB, extracts DINO features, applies training PCA and tracks poses. | Replacing the mesh can change geometry, rendered texture/features and pose estimation together. Geometry-only intervention requires pose and features fixed, or an explicitly broader representation claim. |
| Policy consumption | [G3FlowEncoder](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/G3FlowDP/dp/diffusion_policy_3d/model/vision/pointnet_extractor.py), `forward`, separately encodes observed points, feature points and state, then concatenates features. [Policy](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/G3FlowDP/dp/diffusion_policy_3d/policy/G3FlowDP.py) conditions action denoising on the result. | Input reaches the policy at source level. This does not measure how strongly the learned weights rely on it; no weight was loaded. |
| Action and control | [shape config](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/G3FlowDP/dp/diffusion_policy_3d/config/task/bottle_adjust_T.yaml) specifies 14-dimensional state/action. Base task splits each arm into six joint values plus gripper, then uses TOPP and gripper interpolation. | These are joint/gripper actions, not Cartesian pose deltas. Controller interpolation and planner failures must be retained as outcome categories. |
| Outcome and denominator | `check_success` in the task tests the branch-dependent sign/range of bottle x and z > 0.83; it has no explicit bottle-orientation predicate. [G3Flow evaluator](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/RoboTwin_Benchmark/script/eval_policy_G3FlowDP.py) and [DP3 evaluator](https://github.com/TianxingChen/G3Flow/blob/e011ba6ae5a9493b93b02b2ca7b542f9cf629835/RoboTwin_Benchmark/script/eval_policy_dp3.py) both screen seeds using expert plan/success. | Call this the source-defined outcome, not an orientation-accuracy metric. A new comparison must share the preselected seed set and log exclusions; do not independently filter each method's denominator. |

The paired path is therefore **observed scene → known object asset → tracked virtual feature cloud →
joint actions**, not yet **observed scene → independently generated erroneous shape → joint actions**.
This is a boundary of the inspected released route, not an accusation about all experiments in the paper.

#### Public bundle boundary

HF revision `57431cd3131825fd5ccd49d92a253bfae8eb3ee1` exposes the author bundle. Its
`robotwin_assets.zip` is 380,889,034 bytes by metadata. HTTP Range requests retrieved only the
EOCD/tail and central directory: **112,882 bytes**, **454 outer entries**. Header/entry counts and
range lengths matched. Whole-ZIP SHA-256 and member bodies were not verified or downloaded.
The index contains models and robot assets, including bottle 13's GLB/OBJ/model-data paths.
There is a nested `models/tools/obj/camera_obj.zip`; its contents were not inspected. We therefore
do not claim an exhaustive absence of data in every nested payload. The inspected source lookup,
rather than an absence-of-filename argument, establishes the shared-asset limitation above.

The bundle listing does not identify a trained task-policy checkpoint or an independently paired
completion/physical-truth dataset. The repository's MIT code license does not by itself establish
all asset or third-party weight licenses. Large payload transfer and a full G3Flow build are not
justified as the first uncertainty-reduction step.

### DP3 and an independent-completion alternative

**DP3:** the G3Flow repository already embeds a DP3 route for the same task/state/action interface.
Use that as the first source comparison before porting standalone DP3 to another simulator.
Standalone DP3 commit `47385d9d6f5bde3f2ebdf2400ecb8261cc9e6b97` provides `simple_dp3`,
but its inspected MetaWorld wrapper applies task-specific point-cloud transforms and a different
environment/controller. It is an architecture reference, not a compatible G3Flow checkpoint.

**3DSGrasp:** [official commit](https://github.com/NunoDuarte/3DSGrasp/tree/d6763d85e063db675d433dd119837a93e3657a29)
provides an independently applied completion network. Its README links a pretrained model and
an `input`/`gt` train/test bundle. Both Drive viewer pages returned HTTP 200 with matching file
titles via read-only HTTP inspection; browser access failed. This confirms page access, not payload
download, archive size/content, model compatibility or an object-disjoint split. The README still
marks the **2025 uncertainty extension** as awaiting code release.

Source facts requiring a measurement check before attributing any failure to completion:

- [Loader](https://github.com/NunoDuarte/3DSGrasp/blob/d6763d85e063db675d433dd119837a93e3657a29/Completion/utils/Data_loader_ycb.py)
  maps each partial XYZ to a GT XYZ by object/split and filename suffix. This establishes an intended
  pair schema, not verified metric units, camera rays, simulator collision geometry or robot actions.
- [Runner](https://github.com/NunoDuarte/3DSGrasp/blob/d6763d85e063db675d433dd119837a93e3657a29/Completion/tools/runner.py)
  centers/scales 2048 sampled input points. Dataset-mode restoration uses radius `m`; online mode
  uses `m + m/6`. The latter expands all output coordinates around the centroid by **7/6** relative
  to the inverse normalization. This is a wrapper rule, not measured generative-model bias.
  The example dataset mode also picks a random file; use a frozen explicit file list in any study.
- [Model](https://github.com/NunoDuarte/3DSGrasp/blob/d6763d85e063db675d433dd119837a93e3657a29/Completion/models/SGrasp.py)
  concatenates generated points with input points. Preserve that provenance through later sampling.
  A generic “add source tags/preserve observations” proposal would duplicate existing behavior.
  Its configured zero-dropout/eval route is not the released implementation of the 2025 MC-dropout method.
- [Dockerfile](https://github.com/NunoDuarte/3DSGrasp/blob/d6763d85e063db675d433dd119837a93e3657a29/Dockerfile)
  uses an older PyTorch/CUDA base, compiles point-cloud extensions and downloads full data during
  build. It is a source reference; a future workspace-specific recipe must decouple data acquisition
  and validate the local GPU. No build or inference was attempted here.

### Fair baseline and measurement boundary

Q12's first learned comparison, if later justified, should use the same demonstrations, backbone
capacity, action/controller, observation history and allowed sensor evidence. Compare observed-only,
observation-consistent completion and unfiltered completion. Include multi-view observed fusion if
the completion route gets initial exploration views. Account for generation/tracking calls as well
as policy latency; equal point counts alone do not equate total cost or information.

For a geometry-only test, use XYZ without generated semantics initially, a common measured pose,
fixed train-derived preprocessing, and the same metric coordinate frame. Hold physical mesh,
mass/friction and controller fixed. Changing an input branch of a policy trained only on complete
geometry is a sensitivity/OOD diagnostic; fair policy-performance comparisons require matched
training support. A point-only XYZ file does not certify observed free space: camera origin/depth
rays or a controlled renderer are needed for that control. Do not use GT-derived contact labels or
hidden geometry as deployment input.

Simple projection, rigid registration and the exact inverse of normalization are the first
counterexamples. Then compare conservative/uncertainty-aware grasp or success-prediction methods
when action/embodiment interfaces match. A grasp-quality metric can screen whether an input is
informative, but cannot establish closed-loop task success or learned-policy dependence.

Stage 5 necessity, evidence, cost and decision branches plus the next bounded task are owned by
[Q12's question record](../questions/generated-geometry-reliance.md#stage-5-assessment-2026-09-10).

### Repository verification

The tracked source receipt matches all 32 downloaded text files by byte length and SHA-256;
repository/revision/path keys are unique. ZIP range lengths, central-directory bounds and
metadata totals are internally consistent. Nine updated Markdown documents passed 136 local-link
checks, including 59 heading targets, plus fence/whitespace checks. These are lightweight
source/manifest/document checks, not model, dataset-payload or simulator validation.

## Q13 Stage 4 review 2026-09-10

**판단:** Q13의 broad action-aware view selection과 learned action-uncertainty framing은
이미 직접 선행이 있다. 기존 visibility baseline과 비교하는 것만으로 새 learning principle을
주장할 수 없다. Q13은 `under_review`로 유지하되, 기존 task-aware selector의 점수와 실제
관측 후 decision value가 어긋나는 조건을 확인하는 제한된 diagnosis로 좁힌다. 그 차이가
존재한다는 empirical evidence는 아직 없다. Stage 6 실행이나 hypothesis 선택은 하지 않았다.

### Nearest primary works

2024–2026 검색에서 DISaM과 GCNGrasp-VP를 추가로 확인했다. 아래 세 편의 method와
evaluation boundary를 직접 비교했다. PaperReview의 ActiveVLA/SaPaVe insights는 discovery
발췌로만 사용하고, 판단은 primary body와 official source에 근거한다.

| Primary work | Objective / source claim | Assumptions and direct overlap | Remaining empirical question, not novelty |
| --- | --- | --- | --- |
| [Learning to Look / DISaM](https://arxiv.org/html/2410.18964v1), §§3–6 | Trains information seeking with discrepancy from a context-informed manipulation policy; switches sensing/acting using pairwise KL of context-conditioned action distributions. | Ground-truth context supervises training; a competent receiving policy and largely separable seeking/acting spaces are important. Learned action uncertainty is already direct prior. | Does its action-distribution score predict which affordable new observation improves decisions, beyond merely triggering sensing? Generic value-of-information already covers the principle; a useful failure condition must be measured. |
| [GCNGrasp-VP](https://arxiv.org/html/2606.19091v1), §§III–IV-A | Predicts task-conditioned affordance, chooses a high-score region and ranks views by orientation, occlusion and elevation. | Task-relevant visibility is already an objective; the method compares against scene-uncertainty planners. Offline NBV evaluation uses a small annotated multi-view set. | Is there useful decision ambiguity after this task-aware control? A visibility-versus-action result without it would be too weak. |
| [Closed-Loop Next-Best-View Planning for Target-Driven Grasping](https://arxiv.org/html/2207.10543v1), §§III–IV | Combines target-region rear-side voxel gain with VGN and a grasp-quality-history stopping rule. | Requires a target box and reachable views. The paper excludes some motion-planning failures; view count denotes policy updates. | Do additional measurements change task utility under a common denominator and cost budget? The source's confidence/stopping rule must be compared, not relabeled as generic scene entropy. |

The earlier [action-guided dexterous grasping](https://arxiv.org/abs/1708.04185) remains historical
overlap evidence from the reserve review. The three works above are the deeper comparisons here;
this is not a claim of an exhaustive active-perception survey.

### VLA and observation boundaries

[ActiveVLA §3.2](https://arxiv.org/html/2601.08325v1) selects and zooms virtual views from its 3D
representation. Reprojection can help an imperfect policy, but it does not by itself acquire a new
sensor measurement of hidden geometry. Q13 must distinguish that representation benefit from
information acquired by moving a physical or simulated sensor. The checked official repository
still lists code, weights and evaluation release as pending.

[SaPaVe §§3.1–3.2](https://arxiv.org/html/2603.12193v1) explicitly predicts head pitch/yaw and
manipulation actions with separate heads; its official project page presents ActiveManip-Bench.
The inspected page's links still do not provide a downloadable execution bundle. This is a scoped
access finding, not proof that no release exists anywhere. [Observe Then Act §IV-D](https://arxiv.org/html/2409.14891v3)
already mixes task reward, reachable interaction and ROI occupancy-entropy reduction. Neither
camera/action separation nor combining task and entropy reward is an unoccupied contribution.

### Source and artifact evidence

Pinned revisions, 36 retrieved source texts, hashes, repository-tree summaries and access receipts are owned
by [q13-sources.json](q13-sources.json). Only relevant source sections were inspected; code was
never imported or executed. The following are source facts, not reproduced performance results.

#### DISaM: a learned-policy comparison route

Official repository revision: `37382315d4e262d381862752931fe7445c2a0594`.

- [Image-to-action model](https://github.com/UT-Austin-RobIn/l2l/blob/37382315d4e262d381862752931fe7445c2a0594/l2l/modules/image_model.py)
  samples inferred contexts and computes mean pairwise KL over skill-action distributions. The
  inspected discrete route uses threshold 0.5; that value is upstream behavior, not a Q13 tuning
  choice. The [policy wrapper](https://github.com/UT-Austin-RobIn/l2l/blob/37382315d4e262d381862752931fe7445c2a0594/l2l/wrappers/policy_wrappers.py)
  substitutes sampled context at the `privileged_info` feature. A future adapter must audit all
  allowed observation keys rather than assume every simulator field is deployable.
- [Evaluation](https://github.com/UT-Austin-RobIn/l2l/blob/37382315d4e262d381862752931fe7445c2a0594/l2l/scripts/final_eval_dual.py)
  loads a PPO camera checkpoint plus a path-associated encoder checkpoint, rotates the camera
  while uncertain, then executes a skill. Camera-step limits and repeated confident readings
  affect stopping; a single uncertainty call is not the full DISaM policy.
- [`walled` environment](https://github.com/UT-Austin-RobIn/l2l/blob/37382315d4e262d381862752931fe7445c2a0594/l2l/envs/robosuite/walled_multi_stage.py)
  has nine camera commands including no-op, pan/tilt and translation. Success uses the correct
  block/region distance and contact. The [skill wrapper](https://github.com/UT-Austin-RobIn/l2l/blob/37382315d4e262d381862752931fe7445c2a0594/l2l/envs/robosuite/skill_walled_multi_stage.py)
  selects named movement/grasp/place skills, with internal feedback and privileged target positions.
  This is a contextual skill-policy route, not a drop-in continuous grasp policy or VLA.
- [README](https://github.com/UT-Austin-RobIn/l2l/blob/37382315d4e262d381862752931fe7445c2a0594/README.md)
  links IR/IS weights and training data. The two checkpoint links returned generic Box HTML 200;
  archive contents, matching encoder/PPO files, sizes and licenses were not verified. Robosuite's
  specified commit and the custom stable-baselines3 gitlink are recorded in the manifest/source.
  Remaining dependency locks and a fresh Docker recipe are still needed. No training is justified
  merely because checkpoint access is uncertain.

#### active_grasp: observation-to-outcome trace

Official repository revision: `f48c5e76f16951f92881fa23b4fa94867afaf664`.

| Step | Source fact | Required comparison boundary |
| --- | --- | --- |
| Scene / target | [Simulation](https://github.com/ethz-asl/active_grasp/blob/f48c5e76f16951f92881fa23b4fa94867afaf664/src/active_grasp/simulation.py) chooses the least-visible rendered target, supplies its simulator AABB and repeats generation until VGN finds a target grasp in a multi-view reconstruction. | This conditions the scene population on prior grasp detection. Share a frozen scene/target list and record rejection; those prescreen images cannot enter the tested selector. |
| Observation / grasp | [Policy](https://github.com/ethz-asl/active_grasp/blob/f48c5e76f16951f92881fa23b4fa94867afaf664/src/active_grasp/policy.py) integrates depth and camera pose into a 40³ TSDF; VGN predicts grasps, filtered by target box and IK. | A supplied box is an oracle localization assumption unless separately observed. Keep it identical across baselines. Depth processing, VGN calls and history count toward sensing cost. |
| View selection / stop | [NBV source](https://github.com/ethz-asl/active_grasp/blob/f48c5e76f16951f92881fa23b4fa94867afaf664/src/active_grasp/nbv.py) generates up to 16 IK-feasible views, ranks rear-side voxel gain and tests a quality history. `cost_fn` returns 1 for every candidate. | Normalized constant cost does not price actual travel; repeated integration is not necessarily a new view. Quality at a location is not full grasp-pose agreement. Empty candidates/zero total gain require explicit handling in any adapter. |
| Camera / arm execution | [Controller](https://github.com/ethz-asl/active_grasp/blob/f48c5e76f16951f92881fa23b4fa94867afaf664/src/active_grasp/controller.py) moves the wrist camera with Cartesian velocity, then plans an approach and executes grasp/retreat. Collision geometry is derived from the acquired TSDF. | Extra views alter both grasp evidence and collision planning; wrist movement also alters the arm's start state. A geometry-only visibility study cannot silently count these as the same intervention. |
| Recorded outcome / cost | The controller returns success after a 5 cm retreat when gripper width exceeds 2 mm; logs `aborted`, `failed` and `no_motion_plan_found`, view count, sampled translation distance and timers. | This does not verify target identity or the paper's stated 10 cm target-lift criterion. Independent target pose/contact labels are needed for Q13. Retain planning failures in the common denominator; distance omits unrecorded path portions and rotation. |
| Simple controls / assets | [Baselines](https://github.com/ethz-asl/active_grasp/blob/f48c5e76f16951f92881fa23b4fa94867afaf664/src/active_grasp/baselines.py) implement initial view, top view and top trajectory; `FixedTrajectory` is a stub. The asset Drive page returns `assets_v1.zip`. | File-page access is not archive verification. ROS Noetic, MoveIt, robot_helpers, VGN weights and asset payloads remain setup dependencies; no fresh image was built. |

These facts support an accessible source interface, not turnkey measurement validity. In particular,
a source-defined success proxy cannot serve as both the policy confidence and the independent
task-value label without further checking.

#### GCNGrasp-VP: weights available, evaluation data boundary

Official source revision: `cda6a7849c4b2342e9651d299261061a59029bc2`.
The [README](https://github.com/Instinct323/GCNGrasp-VP/blob/cda6a7849c4b2342e9651d299261061a59029bc2/README.md)
explicitly withholds the NBV evaluation dataset, while linking model weights and example assets.
HF metadata at revision `3fefe9a977a3b566c086a3f75fbea406f0eedaee` lists a 143,292,312-byte
`checkpoints/best.ckpt`; neither it nor row-level predictions were downloaded.

[VirtualRobot](https://github.com/Instinct323/GCNGrasp-VP/blob/cda6a7849c4b2342e9651d299261061a59029bc2/gcngrasp/system/virtual_robot.py)
maps requested poses to the nearest recorded view. Workspace derives from recorded camera positions;
missing cached frames can invoke whole-sequence depth alignment and preprocessing. Missing labels
can trigger interactive annotation. Those are offline construction assumptions, not cost-free
online observations. A future use must trace any sequence-derived geometry into allowed inputs.
[NBV evaluation](https://github.com/Instinct323/GCNGrasp-VP/blob/cda6a7849c4b2342e9651d299261061a59029bc2/main_nbv.py)
reports AP and the top grasp's nearest annotated label, carrying the last metrics forward after
stopping. It does not execute a physical grasp or measure camera path feasibility. Accordingly,
this is a strong task-aware selector reference, not an available end-to-end Q13 benchmark.

### Equal-information and equal-cost controls

Freeze the admissible observations, action/camera candidates and history before measuring utility.
Use no new view, a fixed extra view chosen before test outcomes, random feasible view, geometric
gain, a task-affordance/contact selector and the applicable learned action-uncertainty baseline.
One common action evaluator must serve every selector. Repeating the same observation with new
policy RNG draws and repeating the same pose with fresh sensor readings are different controls.
Keep stochastic sampling fixed or separately estimated before attributing disagreement to missing
information. Different but equally successful actions are not decision errors.

Equal update counts alone are insufficient: record acquired frames, path translation/rotation,
elapsed time, reconstruction/inference calls and planning failures. Use a common cost budget or
predefined matched candidate set; do not choose a cost coefficient after observing results. If an
external method needs a different embodiment or extra supervision, qualify that comparison instead
of pretending that its published score is directly comparable.

The next bounded Q13 task and its decision branches are owned by the
[question record](../questions/action-relevant-view-selection.md#stage-5-assessment-2026-09-10).

### Q13 verification

All 36 source-text hashes and byte lengths match the saved files and pinned tree entries;
repository/revision/path keys are unique. Four saved access-page receipts also match their hashes.
Ten updated Markdown documents passed 153 local-link checks, including 76 heading targets,
and fence/whitespace checks. These checks validate the review records, not checkpoints, datasets,
model performance, simulator state restoration or physical outcomes.

## Candidate comparison 2026-09-15

**Decision: Q6을 다음 Stage 4–5 대상으로 선택한다.** Status: `completed`.
Q6은 `under_review`로 올리고 Q9는 비교 가능한 reserve, Q7/Q14는 낮은 실행 우선순위로 둔다.
새 hypothesis나 실행 protocol을 선택한 것은 아니다. Q12/Q13의 보류 조건과 frozen 결과를 유지한다.

### Scope and discovery

현재 Robotics scope 안에서 기존 질문 네 개를 비교했다. 새로운 번호를 추가할 만큼 별개의
질문보다, Q6의 미해결 부분을 좁히는 것이 이번 근거에 맞았다. PaperReview의 MemoryVLA,
HiMe, SAFE, FLARE, HALO, SmolVLA, OC-VLA, Tabero `05_insights.md`에서 선택한 발췌를
discovery cue로 사용했다. 전체 논문 정독이나 PaperReview의 검증 상태 변경은 하지 않았다.
Local note/hash, primary URL/section, source commit와 metadata receipt는
[comparison_sources.json](comparison_sources.json)이 소유한다.

| User-interest route | Candidate evaluated | Observation to test / simplest counterexample |
| --- | --- | --- |
| SmolVLA, π0, diffusion/action execution | Q6 temporal mismatch | 같은 지연 분포라도 실제 도착 순서와 지연 추정 오차가 실패에 주는 효과가 다른가? Constant delay, conservative estimate와 고정 prefix control로 설명되는지 먼저 확인 |
| SAFE, FLARE, failure recovery | Q7 failure-source generalization | 자연/구성 실패 사이 detector ordering이 task·visual evidence를 맞춘 뒤에도 달라지는가? Class/source/visibility matching이 차이를 없앨 수 있음 |
| MemoryVLA, HiMe, HALO | Q9 memory refresh | 같은 관측/갱신 예산에서 stale memory의 갱신 시점이 action에 영향을 주는가? Periodic/TTL/change trigger가 충분할 수 있음 |
| OC-VLA, EquAct, spatial grounding | Q14 coordinate-frame errors | Shared/independent calibration 오류 효과가 exact transform·relative features 뒤에도 남는가? 해석적 cancellation이면 learning question으로 확장하지 않음 |

### Primary evidence and access

**Paper claims:** [RTC](https://arxiv.org/html/2506.07339v1) already addresses chunk continuity and
uses a recent-window maximum delay estimate. Its Kinetix tasks use force-based control; pausing
the simulator or calling zero force a position hold would change the problem.
[Training-Time RTC](https://arxiv.org/html/2512.05964v1) already learns prefix conditioning with
simulated training delays. Neither asynchronous chunking nor prefix conditioning is a new idea here.

**Paper-setting fact:** [REMAC Appendix F](https://arxiv.org/html/2601.20130v1#A6) describes simulation
with fixed true delay and noisy/spiky delay values supplied to the policy. Its real-robot experiments
also include physical latency variation. **Inference:** a matched comparison of actual delay order
and estimation error is still worth assessing; claiming that REMAC never studies varying latency
would be incorrect. The OpenReview final-PDF route returned a browser challenge. This reading is
explicitly the linked arXiv version, and final-version differences remain part of Stage 4 review.

[Action-Prior Denoising for Smooth Real-Time Chunking](https://arxiv.org/html/2605.25537v1) already
compares soft-window lengths at fixed delays and documents success–smoothness tradeoffs.
Therefore a new blend or a lower jerk number alone is not the prospective contribution. General
delay sensitivity is also a classical control concern; the remaining question must concern the
interaction with a learned chunk policy's commitment and observation use.

**Verified source/metadata facts:**

| Route | What was actually verified | Remaining limit |
| --- | --- | --- |
| RTC / Kinetix | Pinned official README, evaluator, model, package requirements and submodule ref. Public `bc/` metadata lists 32 checkpoint directories × 12 level policies. HEAD of two final-directory examples returns HTTP 200, generation, size and CRC32c metadata matching the listing; each file is 12,290,914 bytes. | No checkpoint bytes/deserialization, schema load, GPU compatibility or rollout verified. 60 GiB expert-data tree is not needed merely to inspect these policy files. |
| RTC intervention interface | In `eval_flow.py`, one fixed `inference_delay` controls both the old/new action splice and the prefix condition. `execute_horizon` controls observation/inference cadence; the sweep couples its valid range to delay. | Independent actual-delay and estimated-delay interventions need a new, checked adapter. The default CLI runs a full grid, not the intended small study. |
| REMAC | Pinned public evaluator also uses fixed configuration delay in policy conditioning and execution splice; README describes training then LoRA. | No released REMAC checkpoint was identified in the inspected tree/README. Do not equate RTC base checkpoints with REMAC/TT-RTC weights or infer what private experiments ran. |
| MemoryVLA | Official code/model links now exist. Inspected consolidation merges the most similar adjacent pair. Official Mikasa checkpoint metadata lists 33,507,444,130 bytes and a model revision. | Serialized size is not VRAM. Weight loading, exact Mikasa version and an equal-budget stale-refresh intervention are unverified. MemoryVLA is an adjacent episodic-memory route, not an already compatible replacement for Q9's spatial-map interface. |

The [RTC evaluator](https://github.com/Physical-Intelligence/real-time-chunking-kinetix/blob/9296f31d62d5bfeb5779dcb2f9bcf71ca37f448b/src/eval_flow.py)
and [MemoryVLA source](https://github.com/shihao1895/MemoryVLA/blob/d732ea9072bc063399ccc817aed74ab172eb50be/vla/memory_vla.py)
support the interface statements above. The latter's [official model metadata](https://huggingface.co/shihao1895/memvla-mikasa/tree/510e90e7f3938d57bcb251f3987ce5beba97b373)
supports access, not runtime readiness. Both old dependency stacks need a new workspace Docker;
no host installation or use of unrelated simulator assets is justified.

**Other candidate pressure:** [FailBench](https://arxiv.org/html/2609.03611v1) already supplies
cross-source results and source-origin categories. The inspected paper/linked pages did not yield
a downloadable sample-level manifest or matched natural/constructed pairs. Its fourteen sources
are not automatically matched counterfactuals. Q7 therefore has a denominator problem before a
detector comparison. No claim is made that a release cannot exist elsewhere.

[MIF's official abstract](https://www.roboticsproceedings.org/rss22/p023.html) directly addresses
discrepancy-triggered stale-map updates. [RoboMME-Interference](https://arxiv.org/html/2606.22338v1)
already tests interference from unrelated past sessions, which differs from current-scene refresh.
Q9 needs a concrete within-scene change and controllable refresh interface before claiming a gap.
[CamVLA's project](https://alibaba-damo-academy.github.io/CamVLA/) still marks code Coming Soon;
the accessible repository is a project website. Q14's matched representation/policy bundle remains
unverified, and algebra alone has limited information about learned robustness.

### Updated Stage 3 comparison

Scores are agent judgments, not measurements. H/M/L denote high/medium/low; high overlap is a risk.

| Criterion | Q6 | Q9 | Q7 | Q14 |
| --- | --- | --- | --- | --- |
| Significance | H — feedback under variable inference delay | H — stale belief changes action | H — failure evaluation transfer | H — camera deployment robustness |
| Empirical accessibility | H — small public policy files and explicit splice source; runtime pending | M — policy release, but refresh/task match pending | L — sample-level matched denominator not found | L — matched frame-policy bundle not found |
| Feasibility | M — event scheduling and old JAX stack need checking | M — simulator/version and bank interventions needed | L — heterogeneous source assembly before measurement | M — cheap algebra, expensive matched policy evidence |
| Informational value | H — distinguishes actual timing from estimator assumptions without fitting a model | H — simple refresh may explain benefit | H — source matching can invalidate transfer claims | M — identity checks may only recover known transforms |
| Resource fit | H — frozen small-policy evaluation; no training initially | M — 33.5 GB listed checkpoint plus runtime; cheaper route still possible | M — inference modest only after denominator exists | M — small policies possible but training comparability unresolved |
| Scientific depth | M — needs policy-specific effect beyond generic jitter | H — relevance-dependent belief maintenance | M — can become dataset/source bookkeeping | M — may reduce to calibration bookkeeping |
| Related-work overlap | H — RTC, TT-RTC, REMAC, Soft RTC | H — MIF and memory/consolidation benchmarks | H — FailBench already covers much of broad question | H — camera-centric and equivariant policies |
| Rigorous evaluation path | H — 12 public dynamic levels; later distinct robotic control required | M — memory benchmark exists, target intervention pending | M — multiple sources, comparability unresolved | M — factorization possible, equal-information models pending |

### Selection and next measurement

**Select Q6 for Stage 4–5 review, not immediate execution.** Compared with the other three, its
source exposes the temporal quantities directly and small frozen policy files are publicly
addressable. That makes an informative first test plausible without retraining. Q9 is the second
review reserve because release access improved; it is not selected merely because memory is a
user interest. Q7/Q14 remain exploratory with the limitations above. Q12/Q13 are not reopened.

Narrowed Q6 question: **with a frozen action-chunk policy, fixed inference cadence and the same
multiset of actual delays, does their temporal ordering change failure, and what remains when
delay estimation and prefix commitment are separately controlled?** This is an agent-proposed
question, not an observed effect or a proven unoccupied topic.

Prospective first measurement: at most two named dynamic levels, one fixed policy checkpoint
per level, a fixed controller/inference schedule, and preregistered interleaved versus clustered
delay traces with equal counts. A known-delay diagnostic separates estimation error; causal
last-delay/recent-maximum/fixed-maximum rules are the deployable simple controls. Naive async and
official hard/soft RTC share the same policy. Account for actual chunk availability independently
of the estimator. Retain identical exogenous action-noise streams, starts and terminal accounting;
do not align delays with observed failures after running the policy. If episodes finish early,
equal planned trace histograms need not imply equal consumed histories: record both.

Measure task success and completion time first; action discontinuity is secondary. World dynamics
must advance throughout inference delay. No position-hold claim for force control; no instant
fresh-observation policy as a deployable equal-cost baseline. Use an oracle only as a labeled
diagnostic. JAX source's config equality is not evidence of trajectory parity; constant-delay and
first-terminal checks precede interpreting a new event scheduler.

**Planning estimates:** one working day for Stage 4–5 source/assumption/measurement specification;
if viable, at most two further working days to establish a new Docker and bounded pilot readiness.
Two candidate checkpoint files total about 24.6 MB; dependencies/compilation are additional and
not yet budgeted as a run. No 60 GiB expert download or new training is selected. The next task must
freeze cases, seeds, trace counts, effect/uncertainty rule and a runtime/storage cap before execution.
Failure to separate factors or establish a matching base-policy run stops preparation; repeated
dependency repair or broader sweeps are not automatic.

A sufficiently precise null result could support static-delay/causal simple-control adequacy only
on the tested conditions; a wide uncertainty interval remains inconclusive rather than equivalence.
If only the delay-estimation control explains a difference, pursue no new chunk-policy mechanism.
A residual would motivate diagnosing which observation/commitment interaction matters before
proposing a method. Kinetix is a 2D symbolic force-control diagnostic; it cannot establish VLA
visual/language reasoning, 3D manipulation or real-robot performance. Later robotic evidence is
required for such claims, rather than being an entry requirement for this candidate comparison.

### Verification and preservation

Three official repositories were pinned and 11 source files matched their Git blob IDs and sizes.
The cache contains 21 text/metadata files totaling 609,154 bytes. GCS HEAD checks validate metadata
agreement only; payload checksums and checkpoint compatibility are not verified. No policy,
simulator, model import, training, Docker build or numerical test occurred. PaperReview and all
prior frozen experiment artifacts were kept unchanged. This study remains in `buildup/`.
Closing checks passed for 340 local links and 146 heading targets across 17 changed/local Markdown
documents, all cached hashes/source blob identities, eight PaperReview note hashes and its registry
hash. `git diff --check` passed. These are documentation and provenance checks, not policy validation.

## Q6 Stage 4 review 2026-09-15

Status: `completed` as a bounded preliminary review. The next task is measurement readiness,
subject to the [Stage 5 design](../questions/temporal-mismatch-decomposition.md#stage-5-assessment-2026-09-15).
Source receipts are in [q6_sources.json](q6_sources.json). No rollout or checkpoint load occurred.

### Closest prior and version boundary

| Primary work | Verified setting / contribution | Consequence for Q6 |
| --- | --- | --- |
| [RTC](https://arxiv.org/html/2506.07339v1), Algorithm 1 | History-based maximum delay estimate, prediction during execution, replacement when ready; the real scheduler can change its execution horizon. | Delay prediction and asynchronous switching are prior work. Our fixed-cadence, bounded-delay diagnostic is only a restricted case. |
| [REMAC](https://arxiv.org/html/2601.20130v1), §3 and Appendix F | Learns masked action correction. The appendix's simulation corrupts the supplied delay with true delay held fixed; real experiments include correlated latency and historical estimates. | Estimation and actual arrival are distinguishable, but generic temporal-factor diagnosis is occupied. |
| [Understanding Asynchronous Inference Methods for Vision-Language-Action Models](https://arxiv.org/html/2605.08168v1), §3 and §7 | Already compares four methods on shared Kinetix/LIBERO backbones. Its limitations explicitly identify fixed integer delay, privileged future states in one route and unreliable simulation time-to-solve. | A new static-delay comparison or renamed failure taxonomy has little value. Reusing privileged future state would invalidate a deployable baseline. |

REMAC's [arXiv history](https://arxiv.org/abs/2601.20130) still lists v1 only. Its OpenReview forum,
direct final-PDF URL and public note API were checked; they returned a browser challenge or 403.
The final paper could not be independently read, and search-index excerpts were not treated as a
verified final version. This remains a novelty uncertainty, not evidence that the final paper lacks
the proposed experiment. Bounded measurement preparation can proceed; exact-prior admission must
resolve it before a novelty or contribution claim.

### Adjacent evidence and minimum difference

[Armory: Action Chunk Scheduling for Batched Robot Policy Serving](https://arxiv.org/html/2608.00337v1)
already studies actual network jitter. Appendix A.6 independently samples lognormal uplink/downlink
delays and varies their spread at fixed median. Appendix A.8 also identifies first-executed chunk
index as a possible scheduling confounder. Our proposed contrast preserves the entire planned delay
multiset and changes its order at fixed request times; it is not a first jitter study or a new serving
scheduler. Its simulation controls do not establish behavior under a shared real GPU queue.

[Predictive control for networked systems affected by correlated packet loss](https://www.eng.newcastle.edu.au/~mf140/home/Papers/IJRNC_2017_2.pdf)
uses packet-loss history and Markov dependence in predictive control. This is not the same channel
as a bounded inference delay, but it rules out presenting temporal correlation or buffering as a
new general control principle. The useful remaining target is an empirical learned-policy effect
that survives simple causal controls.

[VLASH](https://arxiv.org/html/2512.01031v1) already conditions on predicted future state, and
[Training-Time RTC](https://arxiv.org/html/2512.05964v1) learns prefix conditioning. They are strong
adjacent methods; adding such a mechanism is not the selected study. Their trained weights are not
interchangeable with the two RTC base files. [Soft RTC](https://arxiv.org/html/2605.25537v1), §V–VI,
also distinguishes base inference-time guidance from trained hard/soft conditioning and accounts
for guidance overhead. Equal denoising-step count does not mean equal FLOPs or wall-clock latency.

[CloudEdgeVLA](https://arxiv.org/html/2608.00569v1) samples observation age while retaining current
proprioception, with additional current edge vision for its own policy. That is a different
information intervention from changing when a chunk computed from one captured observation
arrives. Neither setting can silently stand in for the other.

**Agent decision:** retain Q6 for one bounded measurement-readiness task. A small controlled
delay-order study has informational value, but generic jitter sensitivity and the earlier
three-way decomposition do not constitute novelty. Q9 is not automatically activated.

### Source and measurement audit

Nine additional official files matched pinned Git blob IDs and sizes, totaling 497,097 bytes.
These include two level JSON files, the dependency lock, RTC's noise wrapper and Kinetix's loader,
environment and terminal wrappers. Existing evaluator/model receipts remain in comparison_sources.

| Source fact | Design consequence |
| --- | --- |
| RTC keeps its own `worlds/l/` files; `catcher_v3` is absent from the pinned Kinetix submodule tree. | Use both named levels from the RTC commit, not similarly named upstream levels. |
| Both level JSONs specify 256 control steps, physics `dt=1/60`, `frame_skip=2`; loader fills `downscale` and resets screen dimensions. | A control step is two physics substeps. Record original bytes and loader transformations; numerical loading remains pending. |
| Noise wrapper adds Gaussian action noise, SD 0.1, once per control step. Reset of a concrete level returns that level. | Seeds vary action/inference noise, not independently sampled scenes. Share noise per control step, correcting the earlier per-physics-step proposal. |
| At fixed `s`, one RNG split generates the chunk and `s` further splits drive environment steps. The model's `zeros`/`exp` schedules both use VJP guidance for a base policy. | Preserve the original RNG allocation before all terminal events. Hard prefix weights do not guarantee exact hard clamping of a base policy. |
| Source takes `done` over substeps, maximum reward, but `GoalR` from the last substep. `AutoReplayWrapper` resets after a terminal event. | Define success using the official first-terminal label and audit substep disagreement; never count a replayed episode or replace labels after results. |
| The `done` expression's AST parses as `sum(dones) > (0 \| nan_flag)`. | Do not rely on it to catch nonfinite states. An external finite-value check must invalidate the run; no upstream physics patch is selected. |
| Lock records JAX 0.4.35, jaxlib 0.4.34, Flax 0.10.2 and jaxued commit `62d155ae772aa2a0ecac9541d498df7ae88e6def`. | First readiness uses a new CPU Docker with a documented CPU dependency projection; RTX 5090 support is unverified and unnecessary for this first check. |

The two checkpoint names match RTC's filename construction and the `31` directory selected by
the default last-directory route. This is source/metadata linkage only: schema, numerical loading,
competence and physical terminal labels are not verified. No expert data, weights, simulator
runtime or installed dependency was acquired this turn.

### Q6 design verification

The nine new source hashes/blob identities and 21 earlier cache identities passed. Seventeen
changed/local Markdown files passed 347 local-link and 153 heading-target checks; `git diff --check`
passed. The design counts are 2,048 held-out records and 140 separate readiness records, not
executed results. Eight Q12 freeze-file hashes remain unchanged; their experiment entries were
not re-evaluated. The closing receipt is included in q6_sources.json.

## Q6 reassessment and reserve comparison 2026-09-15

Status: `completed`. **Select Q9 Spatial-Memory Refresh for Stage 4–5 review; keep Q6 deferred.**
This is a comparative allocation of the next review, not automatic succession after failure.
The [Q6 record](../questions/temporal-mismatch-decomposition.md#source-and-record-reassessment-2026-09-15)
owns endpoint alternatives and its re-entry conditions. [reassessment_sources.json](reassessment_sources.json)
owns this review's source/metadata receipts and preservation verification. No new numerical study,
payload pickle, checkpoint or runtime was acquired/executed in this task.

### Evidence that changes the comparison

**Q6:** the [Kinetix task definition](https://arxiv.org/html/2410.23208v1#S3.SS2) provides a source-based
reason to consider first-event termination. The saved mismatch has a local measurement explanation,
so it is not evidence against all temporal-order questions. Conversely, revising success accounting
does not supply a new learning/control principle. [REMAC Appendix F](https://arxiv.org/html/2601.20130v1#A6)
already addresses corrupted delay estimates and real fluctuating latency. Its final OpenReview
version remains unverified; this review does not resolve that earlier access limitation.

**Q9 paper claims:** [DynaMem §3.2–4.3](https://arxiv.org/html/2411.04999v2) maintains a dynamic voxel
memory and evaluates time-indexed object localization on DynaBench. Its offline benchmark omits
navigation/exploration/manipulation, and already ablates point removal and query verification.
An offline study would measure localization and false-presence errors, not plan completion.
Generic dynamic memory or point removal is therefore not a new contribution.

**Q9 release facts:** the public [DynaBench repository](https://huggingface.co/datasets/hello-peiqi/DynaMem-DynaBench)
at revision `1d561e2de8718addf398e5e967f2c44dc015c366` lists nine environments, nine `env.pkl`
inputs, 28 CSVs and nine `time.txt` files. The 37 small annotation/time files passed size/Git blob/
SHA-256 checks: 29,890 bytes, 639 query rows, 156 rows with empty coordinates, columns
`query,x,y,z,tol`. `env3` contains four annotated snapshots; the other eight contain three.
The viewer's flat table omits the environment/time identity encoded in paths, so it is not a
safe replacement for the original manifest. Empty coordinates alone do not distinguish a removed
object from one never observed; the paper distinguishes these cases, but reconstruction needs data.

Listed pickle sizes total about 5.46 GB decimal. `env1/env.pkl` is 54,700,824 bytes (52.2 MiB),
and env1+env2 total 320,890,211 bytes (306.0 MiB). These are access/size/LFS metadata, not verified
payload hashes or successful deserialization. The dataset has no explanatory card; evaluation
time units, frame inclusivity, object identity across changing query wording, and source-version
compatibility require audit. The `hello-peiqi` identity is also the DynaMem contributor addressed
in [release issue #269](https://github.com/hello-robot/stretch_ai/issues/269); its response promises
processing, not a verified paper-to-upload equivalence.

**Q9 source facts:** five files from `hello-robot/stretch_ai` commit
`6272b28e3ff7be482af3b427a4551d1772ebf7d7` passed immutable Git blob/size/SHA-256 checks.
[process_rgbd_images](https://github.com/hello-robot/stretch_ai/blob/6272b28e3ff7be482af3b427a4551d1772ebf7d7/src/stretch/mapping/voxel/voxel_dynamem.py#L326)
clears/rebuilds map evidence from RGB-D and pose. Its `read_from_pickle(num_frames=...)` loops over a
prefix for obstacle reconstruction but later restores `combined_xyz/combined_feats` for semantic
memory without applying that prefix bound. **Inference:** using that loader as a causal memory
prefix risks future-information leakage; actual leakage depends on the uninspected pickle.
A new audit must inspect raw per-frame provenance and reconstruct memory from authorized frames.

The [current CPU documentation](https://github.com/hello-robot/stretch_ai/blob/6272b28e3ff7be482af3b427a4551d1772ebf7d7/docs/dynamem.md#running-on-cpu)
describes a reduced configuration; it changes perception models, resolution and matching behavior.
It is neither a matched CPU/GPU ablation nor proof of local runtime. The live CLI constructs a
robot client even with saved input; a bounded offline adapter is required. No robot command was run.

**Other reserve facts:** [MIF's page](https://ziya-jiang.github.io/MIF-homepage/) still says Code Coming
Soon and its code button targets GitHub's homepage. Thus it is a direct prior, not a verified
reproduction dependency. MemoryVLA remains an adjacent episodic-policy route, not Q9's minimum
cost. [FailBench](https://arxiv.org/abs/2609.03611) still has no matched sample manifest identified
in this bounded check; unrelated repositories with the same name are not its release.
[CamVLA's page](https://alibaba-damo-academy.github.io/CamVLA/) still marks code Coming Soon, leaving
Q14's matched frame-policy bundle unresolved.

### Comparison after the failed measurement

H/M/L are agent judgments; high overlap is a risk. Scores concern a bounded first study, not venue
acceptance or a numerical claim of superiority.

| Criterion | Q6 event-based reformulation | Q9 spatial refresh / DynaBench | Q7 failure sources | Q14 coordinate frames |
| --- | --- | --- | --- | --- |
| Significance | H — delayed feedback | H — obsolete spatial beliefs | H — evaluation transfer | H — deployment robustness |
| Empirical accessibility | H for policy/source, M for valid revised endpoint | M — real sequence/label release; causal payload linkage unverified | L — matched rows unverified | L — matched policies unverified |
| Feasibility | M — new endpoint contract and full readiness | M — small first input possible; replay/feature version audit needed | L — source harmonization first | M for algebra, L for matched policy evidence |
| Informational value of next task | M — repairs interpretation; ordering phenomenon still open | H — resolves causal memory/observation budget access and simple-update sufficiency | M — largely release/matching uncertainty | M — may end at known cancellation |
| Resource fit | H — installed small CPU policy route | M–H — 52.2 MiB first input, no 33.5 GB VLA required; runtime still open | M once denominator exists | M for analysis, unresolved training cost |
| Scientific depth | M — must exceed generic timing sensitivity | M–H — task-relevant versus irrelevant stale updates; no learned module assumed | M — evidence/source confounding | M — beyond coordinate identities |
| Related-work overlap | H — RTC/REMAC/other async methods | H — DynaMem/MIF already update obsolete maps | H — FailBench | H — equivariant/camera-centric policies |
| Rigorous evaluation path | M–H — two fixed 2D policies then external robotics | M — nine scenes and negative queries; offline limitation is explicit | M — only after matched strata | M — only after matched representation budget |

**Decision rationale:** Q6 has the lowest immediate execution cost and an intellectually defensible
revision; it is not rejected merely because a readiness test failed. Q9 now has a materially more
concrete spatial-memory route than the earlier comparison established. Its next inexpensive audit
can determine whether a budget-matched intervention is identifiable at all. That question has
greater current information value than investing immediately in another Q6 evaluator revision.
Select Q9 for preliminary literature/assumption design, keeping Q6 as a conditional reserve and
Q12/Q13 deferred. This is a review selection, not a measured memory advantage or novelty claim.

### Selected next uncertainty and bounds

Q9's first candidate contrast is: **given the same causally available RGB-D stream and a capped
number of memory updates, do update timing and query relevance change stale-object localization
and absent-object errors beyond uniform/TTL and geometry-change controls?** A trigger that reads
all frames has spent that sensing/processing budget even if it commits few updates. Record
observation access, perception computation, writes and query cost separately. Offline replay can
test update allocation at fixed observations; it cannot establish savings in robot exploration.
Future annotations cannot choose the trigger's decision or its threshold.

The next Stage 4–5 task should settle time/frame semantics, feature provenance, missing-object
labels, simplest baselines, native-vs-adapter parity and a bounded CPU input-readiness proposal.
Use source/metadata first; no foundation-model download, new training or live robot operation.
Planning estimate: 1–2 days for this design/access audit. If no valid causal replay or nontrivial
baseline contrast is available, record the reason and compare again rather than fabricate state
changes, infer task success from query accuracy or automatically return to Q6. Hypothesis entry
and scaled experiments remain separate.

### Reassessment verification

Host-only byte/metadata validation passed for the unchanged Q6 preservation bundle (28 study
files, ten logs, 22 raw outputs), 265 source files and two policy payloads. New checks covered
five DynaMem source files, four source AST parses without imports, and all 37 DynaBench CSV/time
files against immutable tree entries. CSV paths match all nine time lists; all coordinate/tolerance
fields are jointly empty in 156 of 639 rows. A draft aggregate of 162 was corrected during this
check; original downloaded metadata was unchanged. Ten current documents passed local-link and
heading-target validation, and `git diff --check` passed. Exact counts/log identity are in the
reassessment receipt. These checks do not validate a Q9 numerical evaluator or its pickle payloads.

## Q9 focused review 2026-09-15

### Primary-source findings

2026-09-15 primary text 확인. 아래 결과는 저자의 주장이고 local reproduction 결과가 아니다.

| Primary source | 관련 내용 | Q9에 적용할 경계 |
| --- | --- | --- |
| [DynaMem §3.2–4.3](https://arxiv.org/html/2411.04999v2) | Depth로 오래된 점을 제거하며 recency/semantic exploration과 시점별 위치 질의를 다룬다. | Dynamic update·ray-based deletion 자체는 새 기여가 아니다. Offline 질의는 robot task success와 다르다. |
| [Learning to Evolve: Multi-modal Interactive Fields for Robust Humanoid Navigation in Dynamic Environments](https://www.roboticsproceedings.org/rss22/p023.html), RSS 2026 | Map–reality discrepancy로 local update를 유발한다. [Project](https://ziya-jiang.github.io/MIF-homepage/)의 code는 이 확인 시점에 Coming Soon이다. | Change-trigger 자체의 novelty를 주장하지 않는다. 공개 실행 경로 미확인은 선행 기여의 부재가 아니다. |
| [Memory for Attention: Language-Conditioned Re-Perception with a Vision–Language–Motion Map](https://arxiv.org/html/2607.23797v1), 2026-07-26 preprint, §II–III.H | 제한된 re-perception 예산에서 history·weighted recency·round-robin·Whittle index 등을 비교하고 language relevance와 관측 reliability도 검토한다. | Q9의 budgeted refresh와 relevance 가정에 매우 가까운 직접 선행이다. 관측 reliability가 중요하다는 사실도 이미 다룬다. |
| [AURA: Action-Gated Memory for Robot Policies at Constant VRAM](https://arxiv.org/html/2606.02775v1), §5/7 | Action-error gating과 write budget 비교를 다룬다. | 주된 정량 근거는 synthetic recall이며 spatial-map replay baseline으로 검증된 것은 아니다. Write 수를 compute 절감으로 바꾸지 않는다. 본문의 LIBERO panel과 limitation 문구가 일치하지 않아 해당 deployment 주장은 이 검토의 근거에서 제외했다. |

### Agent inference and first observation

Generic budgeted refresh·relevance-aware recency를 그대로 method novelty로 제안할 수 없다.
다만 이는 첫 관찰을 막는 이유가 아니다. 먼저 실제 RGB-D 관측 순서에서 **오래된 위치를
확인할 수 있는 시점과 단순 refresh 시점이 어긋나는지** 작은 사례로 본다. 관측마다의
visibility/free-space 증거와 비용을 분리하는 것이 이번 질문 구체화의 목적이다. 이것이 기존
active perception·DynaMem·Memory for Attention을 넘어서는 원리인지는 아직 미확정이다.

Source상 DynaMem `process_rgbd_images`는 depth 기반 제거와 semantic encoding/insertion을
수행한다. 따라서 full update 횟수, depth 검토 횟수, semantic inference 비용을 같다고
취급하면 안 된다. 원본 `read_from_pickle`의 combined semantic memory 복원도 첫 관찰에서는
사용하지 않는다. 근거 commit은 기존 reassessment receipt를 따른다.

Env1의 첫 두 annotation을 읽은 뒤 `metal bowl`과 `orange`를 탐색 사례로 골랐다.
전자는 positive→negative, 후자는 서로 다른 위치의 positive query다. 명칭 alias가 필요한
owl/apple보다 연결이 단순하다. 이것은 검토 후 선택한 사례이지 대표성 있는 표본이나
held-out evidence가 아니다. 실제 관측·구현·결과는
[Q9 first observation](../pilot_studies/q9-refresh/README.md)이 소유한다.

잠정 설명: 전체 frame의 변화량이나 경과 시간만으로는 특정 오래된 위치에 대한 관측 기회를
표현하지 못할 수 있다. 첫 방법 초안은 **보이는 위치만 검토하는 단순 geometry control**이며,
학습된 trigger를 전제하지 않는다. 이 대조군으로 충분하면 우선 그것을 결과로 받아들인다.

## Q9 research value 2026-09-15

### Question and evidence boundary

완료한 [표면점 관찰](../pilot_studies/q9-refresh/README.md#surface-comparison-2026-09-15)에서
남은 물체 대응·비용 문제가 구체적인 다른 설명으로 발전할 수 있는지 검토했다.
이번 작업은 primary text와 기존 source의 읽기 전용 대조다. 새 수치 실험은 없다.
아래 선행의 성능·기여는 저자 주장이고, Q9 관찰은 자체 실행 결과다.

### Direct-prior comparison

| 검토한 primary source | 실제로 다루는 내용 | Q9와의 관계와 남는 경계 |
| --- | --- | --- |
| [DynaMem v2](https://arxiv.org/html/2411.04999v2), §3.2–3.4 | View frustum/depth로 오래된 voxel을 제거하고, 최신 후보 영상을 object detector로 확인해 질의에 답하거나 abstain한다. Recency/semantic exploration도 포함한다. | 표면 불일치만으로 object absence를 정하는 것은 원본의 전체 grounding 경로와 다르다. Q9은 전체 DynaMem보다 낫거나 나쁘다는 비교를 수행하지 않았다. |
| [Memory for Attention v1](https://arxiv.org/html/2607.23797v1), §II, III-B/C/F/H, IV | Budgeted re-perception에 history, relevance-weighted oldest-first와 Whittle index를 비교한다. Rendered viewpoints에서 측정한 object detectability를 re-observation 성공률로 사용하며, 변화·재관측 과정은 simulation으로 남는다. | Budget·relevance·recency·관측 reliability라는 질문이 직접 겹친다. 자연 RGB-D 관측 순서의 정확한 visibility 제약과 실제 처리 비용은 본문 평가와 같지 않지만, 그 차이 자체가 Q9의 새 원리라는 증거는 없다. |
| [Vision–Language–Motion Maps v1](https://arxiv.org/html/2607.16173v1), §II-B, III-G, IV | Flow의 양방향 대응 검사를 하고, 우세한 정적 대응점의 RANSAC/rigid fit으로 pose 오차 성분을 보정한다. Depth·pixel 불확실성을 전파해 motion residual을 평가한다. | Orange의 대안 설명인 실제 이동/정합 오차를 가르는 기본 접근이 이미 존재한다. 다만 dominantly-static 가정과 real-data person-mask GT 한계를 저자가 명시하므로 실제 orange를 해결했다고 볼 수 없다. |
| [Khronos v2](https://arxiv.org/html/2402.13817v2), §V-C, VII | 최적화되는 pose/표면을 반영한 ray library로 presence/absence/occlusion을 구분하고 시간 구간 내 여러 ray의 지지를 요구한다. | 다중 표면점·부재 증거·pose 변화 대응은 기존 연구다. Partial-view association, 이동한 fragment의 연결, reference surface 부재 등의 한계도 남아 있다. |

확인 판본은 DynaMem v2, Memory for Attention/VLMM의 2026-07 v1 preprint,
Khronos v2 HTML이다. Khronos proceedings PDF는 이번 도구에서 열리지 않아 arXiv HTML의
해당 절을 직접 읽었다. 두 2026 preprint의 venue acceptance나 결과 재현을 주장하지 않는다.
검색의 secondary 요약은 발견 경로로만 사용했다. 선행의 한계는 보존하며 “모든 문제가
해결됐다”거나 “Q9과 완전히 같은 실험이 이미 있다”고 판단하지 않는다.

**Source fact — 비용 단위.** 기존에 고정한
[DynaMem source](https://github.com/hello-robot/stretch_ai/blob/6272b28e3ff7be482af3b427a4551d1772ebf7d7/src/stretch/mapping/voxel/voxel_dynamem.py#L326)의
`process_rgbd_images`에는 obstacle/semantic point clearing, encoder 실행, semantic insertion이
구분돼 있다. 따라서 cheap depth check와 expensive encoding을 나누는 구현 경로는 있으나,
이를 분리했다는 사실만으로 contribution이나 절감량이 성립하지 않는다. 실제 runtime을
계측하거나 native adapter를 실행한 것은 아니다. 기존 source identity는
[reassessment_sources.json](reassessment_sources.json)을 따른다.

### What the local observation does and does not distinguish

**실행 사실.** 단순 current-view eligibility 규칙은 두 사례의 측정 구간에서 reference의
표면 모순을 모두 포착했다. 두 물체에 예산을 각각 배정했으므로 물체끼리 제한된 예산을
놓고 경쟁하는 allocation은 평가하지 않았다. Depth 접근만 맞췄고 pose 검사·전체 연산
비용은 같지 않다. Orange의 초기 구간 모순은 실제 이동/정합/대응 오차 중 어느 원인인지
판정되지 않았다. 이후 화면에 과일이 보인다는 사실만으로 old location의 유효성은 정해지지 않는다.

**에이전트 추론.** 현재 관찰은 “정해진 시점의 sampling이 관측 기회를 놓친다”는 설명과
양립하며, 이를 단순 visibility 대조군이 설명한다. 다음 두 설명은 아직 구분되지 않는다.

- 물체가 실제로 이동했으므로 초기 표면점의 공간적 지지가 사라졌다.
- Pose/depth/correspondence 오차로 투영점이 물체를 벗어났고, refresh 여부와 무관하게
  표면점 검사가 부재 증거처럼 보였다.

정적 배경 정합이나 작은 known-motion construction은 이를 진단하는 유용한 수단이다.
그러나 지금 그 수리만 수행하면 주로 알려진 geometry control을 적용하는 결과가 된다.
수리 자체에 novelty를 요구해서 보류하는 것이 아니다. 수리 후 어떤 다른 예측·의사결정을
시험할지 아직 좁혀지지 않아, 추가 annotation/runtime 투자의 기대 정보 가치가 낮다고 판단했다.

### Alternatives and investment decision

| 다음 방향 | 배울 수 있는 것 | 이번 선택 |
| --- | --- | --- |
| 같은 periodic/visibility 비교를 더 많은 frame·scene으로 확대 | 같은 현상의 빈도와 조건 | 현재 설명은 단순 대조군으로 충분하다. 대표성 확대를 우선하지 않는다. |
| Orange의 배경 정합·대응을 보강 | 이동과 측정 오차 구분 | 필요한 수리가 될 수 있지만, 현재는 알려진 진단을 넘어 시험할 구체적 설명이 없어 추가 투자를 보류한다. |
| 여러 물체의 joint budget와 causal view 제약으로 reformulate | 관측 기회 제약이 recency/history allocation의 선택을 바꾸는지 | 열린 질문 초안이다. 우선 visible-only oldest-first/Whittle 같은 단순 대안과 다른 예측을 내는 작은 사례를 제시할 때 재비교한다. 현재 pilot이 이를 지지한다고 쓰지 않는다. |
| Q9 추가 투자를 보류하고 남은 Q7/Q14를 비교 | 더 직접적인 failure-transfer 또는 policy-representation 질문의 첫 관찰 가치 | **선택.** 두 후보의 기존 접근 제약도 함께 비교하며, 아직 어느 후보도 실행 우선순위로 확정하지 않는다. |

**판단:** 현재 Q9의 depth/surface refresh 경로는 `deferred`로 둔다. 현상의 부재,
유의성 부족, 전체 benchmark 미완성 또는 최종 method 미완성을 이유로 종료하는 판정이
아니다. 단순 대조군이 설명한 부분과 직접 선행이 다룬 부분을 제외하면, 지금의 추가 작업을
이끌 구체적 차이가 부족하다는 투자 판단이다. 폭넓은 spatial-memory 질문은 미검증으로 남긴다.

재검토는 기존 대조군과 다른 예측을 내는 관찰/analytic example 또는 명확한 robot decision
문제와 작은 비교 경로가 생겼을 때 한다. 양의 효과나 전체 baseline 재현을 재진입 gate로
요구하지 않는다. 정식 처분은 [selection](../../selection.md#q9-investment-decision-2026-09-15),
바로 다음 작업은 [TODO](../../../TODO.md)가 소유한다.

## Q7 Q14 Comparison 2026-09-15

### Decision and scope

**Q7을 다음 작은 feasibility observation으로 선택하고 Q14는 exploratory reserve로 둔다.**
Q7의 좁힌 질문은 구성한 no-progress 실패의 영상 변화 단서가 같은 grasp 장면의 실제
실패/성공에도 유효한가이다. 질문 선택의 근거는 기존 결과와 구별할 관찰과 해석 가능성이다.
Dataset availability는 비용을 낮추는 보조 근거다. Hypothesis나 새 contribution은 선택하지 않았다.

Q9/Q6/Q12/Q13의 기존 deferred 판단은 유지한다. 이번 작업은 현재 TODO의 두 후보 비교이며
새 detector evaluation, 모델 실행 또는 이미지 판독까지 완료한 작업은 아니다.

### Primary evidence and corrections

| primary source inspected | source claim / release fact | implication for this comparison |
| --- | --- | --- |
| [FailBench v1](https://arxiv.org/html/2609.03611v1), §3–4, Appendix A | source origin, input modality와 source별 detector 성능을 다룬다. UR5와 BDV2는 원본 dataset에서 선별한 subset이다. | heterogeneous-source gap은 이미 연구 대상이다. Source가 다르면 task·label·view 차이도 섞이므로 gap을 origin의 인과 효과로 해석할 수 없다. |
| [Guardian v4](https://arxiv.org/html/2512.01946v4), §3.2/3.4/5.3/5.4 | constructed execution failure와 policy-collected UR5 execution을 구분한다. Transfer/data-composition 및 view ablation을 보고한다. | 단순 synthetic-to-real 또는 multi-view 개선은 선행과 겹친다. 동일 시작 장면의 성공·실패·construction을 비교하는 좁은 설명 검토를 택한다. |
| [CamVLA v1](https://arxiv.org/html/2607.05396v1), §4.3, Appendix B–C | GT extrinsics와 state/action representation 대조군, delta-action translation cancellation 유도, rotation-noise ablation을 이미 포함한다. | Q14의 일반 calibration 대조군은 예상보다 직접 중복된다. 학습된 두 출력의 shared error라는 질문은 가능하지만 실제 joint error와 algebra를 구별해야 한다. |
| [OC-VLA code pointer](https://github.com/ZTY0213/OC-VLA) → [Dita](https://github.com/RoboDita/Dita) | camera/base action 전환과 ManiSkill2 generation 코드 경로를 확인했다. | 과거의 code 접근 미확정을 수정한다. Matched checkpoint는 검증하지 않았으며, code 부재만으로 Q14를 낮추지 않는다. |
| [CamVLA project](https://alibaba-damo-academy.github.io/CamVLA/) | 이 날짜에도 Code Coming Soon 표기 | released joint prediction을 즉시 관찰하는 경로는 아직 확인하지 못했다. 작은 독립 construction은 여전히 가능하다. |

Guardian의 UR5 planning은 구성한 실패도 포함하므로 execution과 합치지 않는다. 원본 metadata
mode의 `no_close`, `translation_object` 같은 이름은 개별 origin의 확증이 아니다. Publication의
policy-collected 설명과 개별 record에서 실제로 확인한 정보를 구분한다.

### What was actually inspected

공식 [UR5 test dataset](https://huggingface.co/datasets/paulpacaud/ur5fail_test_dataset)와
[BDV2 test dataset](https://huggingface.co/datasets/paulpacaud/bdv2fail_test_dataset)의 execution
metadata를 pinned revision에서 취득했다. Host에서는 stdlib로 metadata와 경로만 읽었다.
원본 UR5는 140행(69 success / 71 failure), BDV2는 1,000행(500 / 500)이다. 이것은 성능 실험
denominator나 독립 episode 수가 아니다. Source별 `episode_id`만으로 grouping하면 충돌한다.

중요한 관찰은 row count보다 **같은 지시·subtask·시작 이미지의 성공/실패 네 쌍**이 있다는 점이다.
또한 UR5에는 시작/종료 이미지 경로가 같은 success와 failure가 모두 있고, BDV2에는 그런
경로의 row 70개가 있다. 아직 image bytes와 task state는 보지 않았으므로 metadata만으로
label 오류나 detector shortcut을 선언하지 않는다. 첫 사례와 matching 조건의 상세 owner는
[Q7 First Observation](../questions/failure-source-generalization.md#first-observation)이다.

보존한 raw metadata는 약 1.7 MB이며 revision/hash/row pointer는
[comparison_sources.json](comparison_sources.json)의 `q7_q14_review_20260915`에 추가했다.
HF tree에서 확인한 archive 크기는 UR5 54,848,824 bytes, BDV2 188,611,050 bytes다.
이미지 archive나 checkpoint는 내려받지 않았다. UR5만으로 첫 관찰을 시작할 수 있다.

### Comparative value of the first observation

| criterion | Q7 | Q14 |
| --- | --- | --- |
| smallest interpretable observation | 같은 grasp 시작 장면에 source success/failure와 end=start construction을 나란히 놓고 시각 증거·전역 image change를 비교 | 같은 marginal rotation error에서 shared/independent perturbation을 분리한 작은 analytic construction |
| simple explanations | image duplication/배경·arm 변화, task 달성 상태, 관측 증거 부족 | exact frame conversion, 상대 좌표의 error cancellation, augmentation |
| what becomes clearer | 단순 change 단서가 실제 label을 구별하는지, 어떤 task evidence가 빠지는지, construction의 semantic validity | algebra상 상쇄 가능성; learned policy에서 같은 현상이 발생하는지는 별도 관찰 필요 |
| closest-prior pressure | FailBench/Guardian의 broad transfer와 겹친다. Same-start 사례는 첫 mechanism observation이지 새 benchmark claim이 아님 | CamVLA가 oracle/noise/delta 유도까지 포함한다. 단순 재현 이상의 다음 learning observation이 덜 구체적 |
| estimated first cost | UR5 archive 약 55 MB, CPU와 소수 이미지 판독, 반나절 이내 예상 | algebra construction은 수 시간 이내 예상; learned joint-error route의 데이터/학습 비용은 미산정 |
| negative-result value | 단순 rule이면 더 복잡한 verifier 필요성을 낮추고, 불가시성이면 상태 추론 질문으로 수정 | geometry convention 또는 known cancellation으로 설명되면 frame-learning 질문을 수정 |

시간은 실행 실측이 아닌 계획 추정이다. Q14의 analytic observation도 유효한 buildup 작업이며
싼 실험이 수학적이라는 이유로 배제하지 않는다. 다만 현재 구체적인 실제 robot 사례에서
설명을 나눌 수 있는 Q7의 다음 관찰이 더 직접적이므로 우선한다.

### Chosen continuation and claim boundary

Q7 첫 묶음은 source 11행과 최대 constructed input 4개다. 영상에서 초기 task 미달성 여부를
확인한 뒤 construction을 해석하며, 이미 달성된 상태에 end=start를 적용해 실패라고 가정하지 않는다.
준비·시각 판독·CPU 비교·설명 수정을 한 TODO로 실행한다. 전체 FailBench manifest, VLM
checkpoint 또는 모든 source의 matching 완료를 먼저 요구하지 않는다.

단순 change baseline이 constructed failure에서만 유리하면 failure-generation artifact의
작은 사례 근거가 된다. **Detector가 그 단서를 실제로 사용한다는 결론은 이후 모델 비교가 필요**하다.
Task-conditioned state verification/증거 부족 시 유보는 잠정 method sketch일 뿐이며,
이미지 equality의 알려진 반례를 새로운 principle이나 paper contribution으로 포장하지 않는다.

Q14는 실제 action/geometry joint error를 관찰할 작은 prediction 묶음 또는 구별 가능한
learned-policy construction이 구체화되면 재비교한다. 모든 checkpoint나 full benchmark를
재진입의 필수조건으로 만들지 않는다. 이번 선택은 두 연구 질문의 최종 우열 판정이 아니다.


## Q7 Q14 Reassessment 2026-09-16

### Decision

**Q14의 작은 supervised keypoint-regression 관찰을 다음으로 선택하고 Q7의 현재 경로는
`deferred`로 둔다.** Q14 질문은 “각 head의 오차 분포가 같아도, 같은 관측에서 나온
camera-frame action과 calibration의 오차 의존성이 최종 base-frame action 오차를 바꾸는가?”다.
알려진 covariance algebra를 새 원리라고 주장하지 않고, 학습된 출력에서의 영향과 단순 기하
추정기의 설명 범위를 비교한다. 최종 method/novelty 확정이나 hypothesis 승격은 아니다.

### Primary sources and what changed

2026-09-16에 아래 primary source를 다시 읽었다. PaperReview의 OC-VLA·SAFE·FLARE note는
관심 방향과 이전 발견의 문맥으로만 사용했다. 새 수치 실행, dataset/checkpoint 취득과
container 생성은 없다. Source/section과 확인 범위는 [source record](comparison_sources.json)의
`q7_q14_reassessment_20260916`이 소유한다.

| source | 논문 주장 또는 공개 사실 | 이번 판단에 주는 의미 |
| --- | --- | --- |
| [CamVLA v1 §3.4, §4.3 Table 5, Appendix B–C](https://arxiv.org/html/2607.05396v1) | Camera action과 hand-eye prediction을 합성한다. GT-extrinsic 변형의 성공률은 세 viewpoint-density 조건 모두 learned-extrinsic 변형보다 높다. Delta-vector translation cancellation과 rotation-noise 대조도 포함한다. | “Oracle calibration이 실제 모델을 해친다”는 관찰로 인용하지 않는다. 단순 oracle/noise 비교를 넘어서 joint error를 직접 볼 필요가 있다. |
| [CamVLA official project](https://alibaba-damo-academy.github.io/CamVLA/) | 이번 확인에도 Code (Coming Soon) 표기 | 공개 joint prediction을 지금 분석할 경로는 확인하지 못했다. Q14 첫 관찰은 독립적인 작은 regression proxy이며 CamVLA 재현이 아니다. |
| [OC-VLA §III](https://arxiv.org/html/2508.13103v1), [Dita official code](https://github.com/RoboDita/Dita) | Calibrated action conversion과 camera/base action training switch를 제공한다. | Known calibration의 action 표현 대안으로 유용하지만 learned hand-eye/action 두 출력의 joint-error trace를 제공한다고 간주하지 않는다. |
| [Mangelson et al., Characterizing the Uncertainty of Jointly Distributed Poses in the Lie Algebra](https://arxiv.org/abs/1906.07795) | 서로 상관된 pose의 uncertainty propagation을 이미 다룬다. | Correlation을 고려해야 한다는 명제와 covariance-aware propagation 자체는 새 contribution이 아니다. Q14의 남은 대상은 learned action/calibration 출력과 단순 estimator의 실제 비교다. |
| [Guardian v4 §3.2, §3.4, Appendix C](https://arxiv.org/html/2512.01946v4) | BDV2 construction은 instruction 변경 또는 END=START를 사용하며 UR5 execution은 policy rollout을 수동 labeling한다. 별도 trace 분석에서는 perception/reasoning 오류를 나눈다. | Source origin·시각 증거·모델 능력을 분리해야 한다. 작은 VLM의 설명 부재만으로 새 structured verifier를 정당화할 수 없다. |
| [FailBench v1 §3–4, Appendix A](https://arxiv.org/html/2609.03611v1) | Failure origin, 제공된 관측, source별 성능과 visual evidence의 차이를 다룬다. | “Source별 성능이 다르다” 또는 “task evidence가 중요하다”만으로는 Q7 수정의 차이가 부족하다. Source별 label 분포도 origin의 인과 효과가 아니다. |
| [KITE v1 §III–IV](https://arxiv.org/html/2604.07034v1) | Keyframes·object layout·시간 정보를 구조화해 VLM failure analysis에 제공한다. | 관측 증거를 구조화해 VLM에 넣는 일반적 방법 초안도 직접 선행이 있다. Q7을 곧바로 evidence module 추가로 바꾸는 선택은 하지 않는다. |

Q7 provenance 설명은 dataset을 만든 Guardian을 우선한다. FailBench의 BDV2 설명은 trajectory
편집이라고 넓게 기술하지만, 이를 실제로 실행된 물리적 실패나 영상 편집의 증거로 옮기지 않는다.
어느 설명도 기존 15개 사례의 terminal timing이나 개별 failure provenance를 새로 검증하지 않는다.

### Q7 reformulation: valuable question, weak next contrast

[Q7 control](../pilot_studies/q7-failure-source/README.md#repetition-results-2026-09-16)은 입력 반복의
혼동을 확인했고, 좁은 START-information 해석을 제한했다. Strong detector의 source transfer나
새 verifier 효과는 관찰하지 않았다. 수정 초안은 task 달성 증거를 맞춘 뒤 construction과
execution의 판정 차이가 남는가이다.

에이전트 추론: “증거를 맞춘다”의 수준을 더 구체화해야 한다. Detector가 입력 X만 받는다면
완전히 같은 X와 decoding에는 숨은 source ID 자체가 판정을 바꿀 경로가 없다. 반면 같은
사람 판독의 task state로 묶었을 때 X는 여전히 background·view·timing·contact evidence가
다를 수 있다. 그때 남은 source gap은 바로 origin의 인과 효과가 아니다. This is an
identifiability observation, not a measured result or a rejection of domain generalization.

가치 있는 수정은 명시한 construction intervention에서 task-state label을 방어하고 그 외
단서를 바꾸는 작은 비교다. 기존 metadata matching이나 prompt 수정만으로 그 비교를
대신하지 않는다. Guardian급 baseline 실행, 작은 simulator construction 또는 다른 terminal
사례는 가능한 경로지만 현재보다 더 많은 모델/입력 준비를 요구하며 첫 구별 관찰이 아직
Q14보다 덜 구체적이다. 모든 provenance·전체 benchmark를 진입 gate로 요구하는 판단은 아니다.

### Q14: a control that preserves the component errors

기존 Q14의 “common error가 상쇄된다”는 수작업 construction만 반복하면 알려진 좌표 항등식만
다시 확인한다. 다음 관찰은 두 출력의 error를 직접 만들어 넣지 않고, 작은 모델이 같은
noisy keypoints에서 action과 camera rotation을 예측하게 한다. 동일한 true scene/camera에서
여러 noise observation을 만들고, 예측을 원래 짝과 재조합한 짝으로 비교한다.

같은 fixed state 안에서만 짝을 섞으면 각 head의 empirical marginal distribution과 GT가
유지된다. 서로 다른 camera/task의 raw action을 뒤섞는 부적절한 대조를 피할 수 있다.
Closed-form geometric estimator에도 같은 비교를 적용해 학습 없이 설명되는 부분을 남긴다.
Exact error decomposition과 구체적인 observation/fit 범위는
[Q14 study design](../questions/frame-error-propagation.md#first-study-design)이 소유한다.

에이전트 추론: 이 관찰은 어느 부호의 dependence가 존재하는지, 그것이 단순한 공유 keypoint
noise에서도 나타나는지, geometry head를 별도로 개선하는 것이 합성 오차와 어떻게 연결되는지
구분할 수 있다. Learned dependence가 없거나 기하 대안이 전부 설명해도 다음 학습 방향의
필요성을 낮추는 정보가 된다. 상쇄를 반드시 찾아야 성공하는 실험으로 만들지 않는다.

### Comparative assessment

| 기준 | Q7 수정 | Q14 수정 |
| --- | --- | --- |
| 가장 작은 다음 관찰 | task-state label을 유지한 construction 변화와 믿을 만한 detector의 반응 | fixed scene 반복 관측에서 learned action/rotation의 원래 pairing과 empirical product-of-marginals 비교 |
| 기존 증거 | 실제 UR5 영상과 38개 약한 baseline 출력; source effect는 미식별 | 직접 VLA joint-error 증거 없음; 작은 regression 관찰의 GT·개입·기하 대조는 정의 가능 |
| 단순 설명 | duplication, task evidence, model/interface competence, label/timing | rotation composition, shared keypoint noise, per-head bias, classical estimator |
| 선행과의 관계 | Guardian/FailBench, 일반 evidence module은 KITE와 겹침 | CamVLA의 oracle/noise와 correlated-pose uncertainty를 기반으로 하며 둘을 새로운 원리로 쓰지 않음 |
| 첫 관찰 비용, 계획 추정 | 현재 image 재사용은 싸지만 meaningful source contrast/competent baseline을 함께 마련해야 함; 약 1–2일 | 작은 2D regression 네 fit + analytic estimator; 준비·해석 반나절–1일, CPU runtime 목표 1시간 이내 |
| 기대 정보 | 구체적 intervention이 정해지면 source gap과 evidence/model confound를 구분 | marginals를 고정한 dependence 영향과 geometric baseline의 설명 범위를 같은 입력에서 분리 |
| 주된 한계 | observation matching을 원인 식별로 과해석할 위험 | synthetic keypoint regression을 실제 VLA/robot success로 과해석할 위험 |

시간은 실측이 아니다. **Q14를 선택하는 이유는 artifact 존재나 단순히 더 싼 비용이 아니라,
다음 관찰의 GT·개입·단순 대안이 현재 더 구체적이기 때문**이다. Q7의 broader question을
과학적으로 기각하지 않고 현재 경로의 추가 투자를 보류한다.

### Chosen next action

Q14는 `feasibility_study`로 올린다. 새로운 project Docker 안에서 synthetic planar keypoints,
작은 supervised two-head/direct regressor, closed-form estimator와 fixed-state recombination 비교를
준비·실행·검증·해석까지 묶는다. [question record](../questions/frame-error-propagation.md)가
제한된 범위, 대조군과 결과별 다음 판단을 소유한다. 이번 turn에서는 실행하지 않았다.
Q7은 concrete label-preserving construction/meaningful source contrast가 생기면 다시 비교한다.
다른 deferred 후보, 기존 frozen 결과, 최종 paper 기준은 유지한다.


## Q14 Geometry Review 2026-09-16

### Decision and scope

**새 learned residual 학습은 선택하지 않고, 실제 영상의 keypoint 검출과 기하 추정을 분리하는
작은 관찰을 선택한다.** Q14는 `feasibility_study`로 이어 간다. 첫 synthetic study가 보인
calibration extrapolation을 실제 영상에서 재현했다고 가정하지 않는다. 다음 질문은 더 좁다.
“Gaussian keypoint noise를 벗어난 실제 검출 오류에서, 단순 robust geometry로 설명되는 부분과
측정 자체의 부족을 구분할 수 있는가?” 최종 method 선택이나 novelty 판정은 아니다.

2026-09-16 primary paper와 공식 source를 읽고 아래 비교를 완료했다. PaperReview의
EquAct·GeoCalib note는 discovery에만 사용했다. 이번 작업은 문헌·source 검토와 설계이며
dataset/weight 취득, model import, 학습·추론·Docker 실행은 없다. 접근 범위와 source hash는
[comparison_sources.json](comparison_sources.json)의 `q14_geometry_review_20260916`이 소유한다.

### Closest alternatives

| Primary source | 논문 주장 또는 공개 사실 | Q14에 적용할 경계 |
| --- | --- | --- |
| [CamVLA §4.3, §5](https://arxiv.org/html/2607.05396v1) | GT-extrinsic 대조가 있으며 extreme viewpoint/high-precision 작업의 한계로 OOD visual feature와 hand-eye regression error를 든다. | Toy의 90° 회귀 실패만으로 새 문제나 새 residual 원리를 주장할 수 없다. |
| [DREAM §II–III](https://arxiv.org/html/1911.09231v3) · [official code](https://github.com/NVlabs/DREAM) | Learned image keypoints와 known kinematics/intrinsics를 PnP에 결합한다. 실제 RGB 자료와 pretrained weights가 공개되어 있다. | Learned perception + explicit geometry 자체가 직접 선행이다. 실제 keypoint 오류를 관찰하는 baseline으로 사용한다. |
| [EasyHeC++ §III](https://arxiv.org/html/2410.09293v1) | Pretrained segmentation/feature matching, pose initialization, differentiable rendering refinement와 informative joint-pose exploration을 결합한다. | 재보정·다중 관측·불확실성 기반 관측 선택도 이미 있다. CAD/kinematics와 추가 관측을 쓰므로 단일 이미지와 같은 비용으로 취급하지 않는다. |
| [BPnP, CVPR 2020](https://openaccess.thecvf.com/content_CVPR_2020/papers/Chen_End-to-End_Learnable_Geometric_Vision_by_Backpropagating_PnP_Optimization_CVPR_2020_paper.pdf) · [EPro-PnP, CVPR 2022](https://arxiv.org/abs/2203.13254v4) | PnP를 통한 end-to-end 학습, probabilistic pose 및 correspondence/weight 학습을 각각 다룬다. | Differentiable solver나 learned confidence를 붙인다는 일반론도 새 contribution이 아니다. 여기서는 abstract 수준의 방법 범위만 확인했으며 로봇 baseline 성능을 비교하지 않았다. |
| [GeoCalib official release](https://github.com/cvg/GeoCalib) | Single-image intrinsics와 gravity direction을 deep learning + geometry로 추정하고 camera-model 선택과 shared-intrinsics 처리를 제공한다. | Robot-base에 대한 전체 extrinsics를 얻는 방법으로 혼동하지 않는다. Intrinsic/model mismatch의 대안이다. |
| [EquiBot §3](https://arxiv.org/html/2407.01479v1) | Point cloud와 proprioception에서 SIM(3)-equivariant diffusion policy를 구성한다. | 좌표변환에 대한 구조적 일반화는 기존 방향이다. 동일 point set의 회전과 실제 camera 이동에 따른 가림·누락은 같은 입력 변화가 아니다. |

[Continual Hand-Eye Calibration](https://arxiv.org/html/2604.15814v1)은 scene-coordinate
regression과 새로운 환경에 대한 continual camera localization을 다룬다. 제목만으로 이
proxy의 단일 장면 angle extrapolation과 같은 문제로 분류하지 않는다. EquAct primary page는
접근 제한이 있어 local note의 세부 주장으로 비교를 확정하지 않았다. 이 검토는 targeted
scoping이며 모든 관련 연구를 조사한 exact-novelty audit가 아니다.

### Failure conditions and simpler explanations

아래는 첫 실험에서 모두 관찰한 결과가 아니라 **입력 가정에 따른 분석과 다음 관찰 후보**다.

| 입력 조건 | 먼저 비교할 단순 대안, 최소 세 종류 | Learned residual에 남는 질문 |
| --- | --- | --- |
| Keypoint 역할·scale·proprioception은 정확하지만 학습 camera angle 밖이다 | Closed-form geometry; relative/canonical coordinates; rotation augmentation/equivariant representation | 현재 toy에서는 geometry가 이미 강하다. 작은 MLP의 외삽 실패를 잔차 학습의 필요성으로 쓰지 않는다. |
| 실제 detector가 일부 keypoint를 잘못 찾거나 누락한다 | Multi-point PnP; RANSAC + inlier refinement; 같은 점의 GT-2D 교체 대조 | Robust solver 뒤에 어떤 측정 오류가 남는지 먼저 본다. RANSAC 뒤의 잔여 오차가 자동으로 학습 가능한 signal은 아니다. |
| Intrinsics/distortion 또는 image resize 좌표가 틀린다 | 올바른 K/resize mapping; 명시적 distortion model; calibration/refinement | 알려진 camera model 오류를 unconstrained action residual로 가리는 것은 원인에 맞는 첫 대안이 아니다. |
| Point configuration이 퇴화하거나 충분한 대응점이 없다 | 추가 correspondence; 다른 robot pose/여러 frame; 관측 부족 표시 | 추가 입력 없이 식별 불가능한 경우는 learned prior가 정답을 보장할 수 없다. 누락이 항상 비식별을 뜻하는 것도 아니다. |
| Rigid-camera·known-kinematics 가정이 깨진다 | Timestamp/kinematic calibration; 움직임을 반영한 추정; 필요 측정 추가 | 현재 데이터로 확인하지 않은 동역학/비강체 문제를 새 모듈의 명분으로 도입하지 않는다. |

에이전트 추론: geometry와 learning의 역할은 각각 좌표·projection 관계와 시각적 대응점/관측
신뢰도로 나눠 검토할 수 있다. 이 분업 자체는 위 선행에 있으므로, 지금 필요한 것은 일반
모듈 조합보다 구체적인 실패 사례와 그 사례에서 어떤 추가 정보가 유효한지다.

### Public input route and coordinate contract

DREAM source revision `3360f2aa45f66a58eaa70d0d40f2c46c2682c0bb`를 읽었다.
[geometric_vision.py](https://github.com/NVlabs/DREAM/blob/3360f2aa45f66a58eaa70d0d40f2c46c2682c0bb/dream/geometric_vision.py)
의 기본 solver는 EPnP 후 iterative refinement이고 별도 RANSAC 함수의 threshold는 5 pixels다.
따라서 “PnP에 refinement를 추가했다”를 새 방법으로 다루지 않는다.

중요한 source 사실: `utilities.load_keypoints`의 3D 위치는 camera frame이며,
`analysis.py`는 이 GT camera-frame 점과 검출한 2D 점을 PnP에 넣는다. `add_from_pose`는
그 결과 transform을 같은 GT 3D 점에 적용한 displacement를 계산한다. 이것은 바로 배포할
camera-to-base pose가 아니라 **GT camera coordinates에 대한 pose-error transform**이다.

에이전트 수식 해석: base→camera GT transform을 T, X_C=T X_B로 두면, camera-frame 점을
입력으로 얻은 Δ는 이상적인 대응 관계에서 T_hat=ΔT와 연결된다. 따라서
`||Δ X_C - X_C|| = ||T_hat X_B - T X_B||`이며 GT는 Δ=I다. 좌표계 선택 자체로 평가가
잘못됐다는 뜻은 아니다. 다만 exact articulated 3D geometry를 주는 privileged diagnostic이고,
kinematic error나 실제 base-frame calibration 출력을 확보했다고 해석할 수 없다. Solver의
수치적 좌표변환 일관성은 다음 실행에서 작은 synthetic 대조로 확인한다.

공식 [data script](https://github.com/NVlabs/DREAM/blob/3360f2aa45f66a58eaa70d0d40f2c46c2682c0bb/data/DOWNLOAD.sh)는
Panda-3Cam RealSense archive를 343 MB,
[model script](https://github.com/NVlabs/DREAM/blob/3360f2aa45f66a58eaa70d0d40f2c46c2682c0bb/trained_models/DOWNLOAD.sh)는
권장 Panda VGG-Q weights를 85 MB로 안내한다. 이는 안내 용량이며 현재 payload 접근·checksum·
schema 검증은 하지 않았다. Google Drive 제한과 오래된 dependency 호환성은 실행상의 미확정이다.
전체 download script를 실행하면 다른 큰 자료도 받으므로 선택한 두 payload와 YAML만 대상으로 한다.

### Investment comparison and selected observation

| 다음 선택 | 알 수 있는 것 | 비용·한계에 대한 판단 |
| --- | --- | --- |
| Toy seed/width 확대 또는 rotation augmentation | 같은 회귀의 분포 범위 민감도 | 알려진 geometry 설명과 실제 visual-error 사이 간극을 거의 줄이지 않아 지금 선택하지 않는다. |
| Generic residual 학습 | 특정 분포에서 residual fitting이 되는지 | 실패 원인과 학습할 target이 아직 분리되지 않아 선택하지 않는다. |
| DREAM 한 모델·실제 24 frame·동일 keypoint의 solver/GT 대조 | 오검출, 누락, solver/geometry/annotation 한계의 case-level 단서 | 약 428 MB의 안내 payload, 준비·해석 약 1일/추론 1시간 이내를 계획 추정으로 두고 선택한다. Docker dependency 비용은 별도다. |
| 바로 투자 보류 | 비용 추가 없음 | 실제 measurement 조건을 한 번도 보지 않고 이상적인 keypoint proxy만으로 학습 역할을 판단하게 된다. 이번 한 관찰의 정보 가치가 더 크다고 판단한다. |

Panda-3Cam은 고정 camera에서 robot configuration이 변하는 자료다. 이 작은 선택은
**camera-view extrapolation 실험이 아니며** 2 GB Panda-Orb나 다른 sensor를 자동 추가하지 않는다.
실제 VLA action/calibration joint error도 측정하지 않는다. 이 단계에서 얻을 것은 방법의
효용 입증이 아니라 realistic measurement 조건에서 geometry 대안이 설명하는 범위다.

[다음 관찰 설계](../questions/frame-error-propagation.md#real-keypoint-observation)는 24 frame의
결정적 선택, 같은 검출 결과의 PnP/RANSAC 비교, GT-2D 교체의 common/all-point 대조와
결과별 후속 판단을 소유한다. 준비·추론·검산·사례 해석을 다음 TODO 한 묶음으로 수행한다.
그 결과에도 일반적인 perception/calibration 문제만 남으면 Q14 추가 투자를 보류할 수 있다.
반대로 구체적 잔여 사례가 생기면 그 정보를 이용한 방법 초안을 작성한다. 유의성·positive
result·full benchmark를 관찰의 통과 조건으로 만들지 않는다.

## Q14 Action Relevance Review 2026-09-16

**판단: Q14의 현재 geometry + learned residual 경로는 `deferred`로 둔다.** 실제 keypoint
관찰은 유효한 calibration 진단이었지만, 남은 ADD/reprojection 순위 차이를 원래의 learned
action/calibration dependence 질문으로 연결할 새 관측은 확보하지 못했다. 아래는 기존
출력의 읽기 전용 검토, 수식 해석과 primary literature 비교다. 새 수치 실행은 없다.

### Remaining cases and action semantics

사실: [기존 사후 선택](../pilot_studies/q14-frame-errors/real/README.md#results-2026-09-16)은
같은 검출점의 reprojection MSE가 작은 pose를 고른다. 남은 세 사례는 모두 official pose를
선택하지만 ADD는 robust pose가 작다. 다음은 저장된 `analyze/selection.json` 및
`correct/metrics.json`의 값이다. ADD는 native annotation units, angle은 residual rotation의
각도이며 새로운 action metric을 계산한 표가 아니다.

| Frame | Reprojection MSE, official / robust (px²) | ADD, official / robust | Angle, official / robust (°) |
| --- | --- | --- | --- |
| 000775 | 11.454881 / 14.356792 | 0.015914 / 0.013084 | 1.527476 / 2.485079 |
| 001550 | 30.816139 / 49.027680 | 0.018423 / 0.008278 | 2.054270 / 0.401363 |
| 003617 | 12.401835 / 14.339883 | 0.012263 / 0.011069 | 2.404933 / 2.074786 |

수식 해석: 여기서는 base→camera GT rotation을 R_BC, DREAM residual transform을
Δ=(Q,b)로 둔다. 따라서 추정 rotation은 Q R_BC다. **정확한 camera-frame free translation
vector a**를 base frame으로 변환할 때 calibration만으로 생기는 squared error는 다음과 같다.
이는 question record의 camera→base R과 반대 방향의 표기다.

```text
e = R_BCᵀ Qᵀ a - R_BCᵀ a
||e||² = aᵀ(2I - Q - Qᵀ)a
       = 4 sin²(theta/2) [||a||² - (nᵀa)²]
E[||e||²] = tr((2I - Q - Qᵀ) M),  M = E[aaᵀ]
```

n과 theta는 Q의 회전축과 각도다. M은 centered covariance가 아닌 second moment다.
Free vector에는 b가 작용하지 않지만 ADD는 b와 robot landmark 배치를 함께 반영한다.
고정 길이 l의 isotropic action 방향을 **가정하면** M=(l²/3)I이고 기대 오차는
`(8l²/3) sin²(theta/2)`다. 따라서 000775의 낮은 ADD인 robust pose가 이 가정의 action
오차에서는 오히려 불리하다. 다른 두 사례는 이 가정에서 robust가 유리하다. 실제 action
방향·회전축 관계는 다를 수 있으므로 세 사례의 실제 행동 순위로 해석하지 않는다.

Learned action a_hat의 경우에는 `||Qᵀ a_hat - a||²`를 봐야 한다. 현재 DREAM 자료에는
이 두 action 값과 joint output이 없으며, 임의 action 방향을 붙이면 위 기하식을 계산하는
진단만 추가된다. Absolute goal이나 SE(3) twist에는 다른 변환식이 필요하다. 이 차이는
**pose 지표만으로 action utility를 정할 수 없다는 경계**이며 새로운 원리나 관찰된 VLA 실패가 아니다.

### Primary sources and simpler alternatives

| Primary source / 대안 | 확인한 내용 | 현재 판단에 주는 정보 |
| --- | --- | --- |
| [Measurement Errors in Visual Servoing, §IV–VI](https://faculty.cc.gatech.edu/~hic/Georgia-HomePage/hic-papers/kyrki-kra-chr-2004.pdf) | Image error에서 pose와 control output으로 오차를 전파하고 공유 측정의 변수 간 correlation을 다룬다. | Control-space error와 covariance를 보자는 일반론은 기존 연구다. Classical visual servoing과 learned joint heads의 차이는 남는다. |
| [SQPnP, §1–2](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123460460.pdf) | 제시한 목적함수의 global optimum을 포함하는 regional minima 집합을 찾는 solver를 제안한다. §2는 pixel reprojection을 back-projection 기반 quadratic cost로 바꾼다. | 후보 pose·초기화 문제에는 기존 solver가 단순 대안이다. 이 보장을 현재 pixel MSE, GT pose, ADD 또는 action error의 최적성으로 확대하지 않는다. |
| [Uncertainty-Aware Camera Pose Estimation from Points and Lines, §3](https://arxiv.org/html/2107.03890v1) | 2D/3D feature uncertainty를 algebraic residual covariance에 반영한 EPnP/DLS 계열과 refinement를 다룬다. | 모든 검출점을 동일하게 취급하는 대안으로 uncertainty weighting이 이미 있다. Heatmap peak height 자체가 검증된 covariance는 아니며 이 자료에서 개선된다고 확인하지 않았다. |
| 기존 saved-pose 선택, [실행 결과](../pilot_studies/q14-frame-errors/real/README.md#results-2026-09-16) | 같은 입력의 두 후보 중 reprojection MSE로 선택해 두 큰 실패를 피했다. | 새 학습 없이 설명되는 큰 실패다. 같은 표본에서 만든 사후 대조이며 held-out 우세나 잔여 오류 해결은 아니다. |
| [CamVLA official project](https://alibaba-damo-academy.github.io/CamVLA/) | 2026-09-16 확인 시 `Code (Coming Soon)`이며 action/geometric head를 명시한다. | 실제 joint-output 경로는 여전히 미확인이다. 공개 지연 자체를 Q14의 scientific 반증이나 유일한 보류 이유로 삼지 않는다. |

앞선 DREAM·EasyHeC++·BPnP/EPro-PnP 비교도 유지한다. 위 solver들을 새로 실행한 것은
아니며 targeted review를 exhaustive novelty 판정으로 사용하지 않는다. 접근 범위와 읽은
기존 결과의 hash는 [source record](comparison_sources.json)의 `q14_action_review_20260916`에 둔다.

### Investment decision

| 다음 시도 | 새로 얻을 정보 | 이번 선택 |
| --- | --- | --- |
| 저장 pose에 임의 action 방향·길이를 추가 | 주어진 Q와 방향의 기하적 민감도 | 위 수식으로 관계를 알 수 있다. 실제 action/learned dependence를 추가하지 않아 실행하지 않는다. |
| SQPnP·uncertainty weighting 또는 frame 확대 | 특정 입력에서 기존 pose solver의 동작 | 유효한 calibration 연구 재료지만 현재는 원래 action 질문보다 일반 pose 비교로 이동하므로 보류한다. |
| Generic residual 또는 composition loss 학습 | 정한 supervision 아래 fitting의 변화 | 현재 실패 진단에서 선택할 고유 target이 정해지지 않았다. 일반 모듈·loss 추가를 다음 방법으로 확정하지 않는다. |
| 작은 paired action/calibration 관찰로 재설계 | Task-relevant joint error와 direct/geometry 대안의 차이 | 재진입 가능성이 있다. 공개 VLA를 반드시 기다릴 필요는 없지만 현재 DREAM에 없는 action을 어떻게 관찰할지 연구 설계가 먼저다. |
| 다른 exploratory 질문의 작은 관찰 비교 | 아직 관찰하지 않은 문제의 정보 가치 | **선택.** Q3, Q4와 관련 CD5, CD2를 기존 scope 안에서 비교한다. 아직 그중 하나를 선택한 것은 아니다. |

에이전트 판단: 첫 synthetic 결과의 평균 learned benefit은 일관되지 않았고, 실제 keypoint
관찰의 큰 실패는 단순 pose 선택으로 피했다. 남은 세 사례도 현재 입력에서는 task-free pose
지표의 차이다. 이 조합은 **지금 이 경로에 더 투자할 우선순위가 낮다**는 근거이며 broad Q14의
효과 부재 증명은 아니다. Final novelty·유의한 개선·두 번째 dataset이 없다는 이유로 닫는 것도 아니다.

재진입 초안: camera-frame action의 의미를 정한 작은 reaching 관찰에서 같은 state의 반복
관측으로 나온 action/rotation 두 출력을 확보하고, component-supervised heads·direct action
regression·explicit geometry가 다른 예측을 내는 입력 조건을 비교할 수 있다. 실제 영상의
goal/end-effector 관측을 쓸지 명시적 synthetic construction을 쓸지와 그때 무엇을 배우는지를
구체화하면 다시 비교한다. 큰 VLA, full benchmark, positive result는 첫 관찰의 선행조건이 아니다.
기존 toy의 seed/width 확대나 checkpoint 공개만으로 자동 재개하지 않는다.

## Remaining Candidate Comparison 2026-09-16

**판단: CD2의 작은 aggregate-result 관찰을 선택한다.** 기존 Robotics scope에서 Q3,
Q4와 관련 CD5, CD2를 비교했다. 아래는 primary text·공식 release의 읽기 전용 확인이며
새 수치 실험 결과가 아니다. 초기 문서의 positive-residual/novelty gate를 재사용하지 않는다.

### Primary sources and corrections

| Candidate / primary source | 확인한 사실 또는 논문 주장 | 에이전트 해석·남은 질문 |
| --- | --- | --- |
| Q3: [SIMPLER §VI-D, Appendix Table X](https://arxiv.org/html/2405.05941v1), [CoRL proceedings](https://proceedings.mlr.press/v270/li25c.html) | Google Robot policy 6개에 대해 can mass·gripper friction과 drawer joint friction을 바꾸고 MMRV/Pearson을 비교했다. 논문은 해당 범위에서 대체로 안정적인 순위·sim-real 상관을 보고한다. | 물성 변화 아래 ranking을 직접 다루지 않았다는 초기 구분은 성립하지 않는다. Timestep/substep과 control interval을 분리하는 좁은 질문은 남지만 새 조합 자체가 novelty는 아니다. |
| Q4: [Clio §VII](https://arxiv.org/html/2404.13696v2), [official code/data](https://github.com/MIT-SPARK/Clio) | Task-driven Information Bottleneck으로 graph granularity를 정한다. Prompt 영향과 관련된 두 object의 과도한 병합이 한계다. 공개 offline graph와 task별 GT object boxes가 있다. | Task-relevant compression 자체는 직접 선행이다. Object relevance GT는 executable-plan/action GT와 다르며 Clio graph를 VLA-Arena task에 바로 연결할 수 있다고 확인하지 않았다. |
| Q4/CD5: [ASHiTA §5–6](https://arxiv.org/html/2504.06553v3) | High-level task hierarchy와 scene graph를 함께 만들고 hierarchical Information Bottleneck, top-down pruning, spatial update 등을 대조한다. Relations와 여러 동종 object의 구별을 한계로 적는다. | Clio의 single-step 한계만으로 새 long-horizon method를 주장할 수 없다. 관계·identity를 보존한 selection과 단순 dependency closure의 차이가 작은 관찰 후보지만, 현재 action validity reference는 확보하지 않았다. |
| CD2: [Efficient Evaluation of Multi-Task Robot Policies With Active Experiment Selection](https://proceedings.mlr.press/v305/anwar25a.html), [preprint §III–VII](https://arxiv.org/html/2502.09829v1) | Outcome distribution의 불확실성, Expected Information Gain과 task-switch cost를 다룬다. Public-result 기반 비교와 MetaWorld를 사용하며 task-based selection도 비교한다. | 기존 연구를 평균 순위만 보는 방법으로 묘사하면 부정확하다. Uniform/task-stratified selection은 강한 대안이다. 현재 aggregate table만으로 이 방법의 trial-level 재현을 할 수 없다. |
| CD2: [Beyond Binary Success](https://arxiv.org/html/2603.13616v1) | Binary/partial-credit/continuous outcome을 사용하는 sequential policy comparison과 anytime-valid inference를 제안한다. | 적은 rollout으로 통계적 비교를 끝내는 일반 목표도 직접 선행이다. 현재 질문은 고정 aggregate table의 조건별 정보 손실로 한정한다. |
| Input: [VLA-Arena §2, §4.1](https://arxiv.org/html/2512.22539v2), [official result repository](https://github.com/vla-arena/vla-arena.github.io) | 11 suites, 4 categories, L0–L2를 제공한다. Paper는 SR/CC와 30-episode 평가를 설명하지만 선택한 개별 JSON에는 trial count·개별 episode가 없다. CC는 trajectory의 누적 constraint cost다. | Published cell mean의 compression은 관찰 가능하다. Rare-failure frequency, severity 분포, actual rollout savings는 이 파일로 식별되지 않는다. |

Source 기록은 [comparison_sources.json](comparison_sources.json)의
`remaining_candidates_20260916`이다. PaperReview의 Clio·SIMPLER·VLA-Arena note는 discovery에만
사용했고 primary에서 위 범위를 재확인했다. SIMPLER는 접근 가능한 v1, Active Experiment
Selection은 v1과 proceedings를 읽었다. 새 버전에서 달라졌을 수 있는 모든 사항이나 전체
관련 문헌을 빠짐없이 조사했다는 뜻은 아니다.

### Smallest useful observation and investment comparison

비용은 아직 실행하지 않은 **에이전트 추정**이다. 동일 비용의 실측 throughput 비교가 아니다.

| Candidate | 가능한 작은 관찰 / simplest controls | 알 수 있는 것과 남는 한계 | 예상 준비·실행 비용 / 이번 판단 |
| --- | --- | --- | --- |
| Q3 | 한 contact task, compatible frozen policy 2개, control interval을 고정한 substep 변화; default·동일 rollout-budget 평균 대조 | 물성 선행과 다른 discretization 효과의 존재·안정성. 범위의 물리적 타당성과 policy 호환성을 먼저 정해야 한다. | 새 simulator image·정책 두 개 준비, 대략 2–4일 이상의 불확실성; `exploratory` reserve |
| Q4/CD5 | 소수 object/relations와 명시적 goal/precondition을 가진 scene에서 relevance top-k vs dependency closure; 동일 fact set의 serialization 대조 | 관계 누락과 representation form을 구분할 수 있다. Constructed symbolic validity이며 실제 robot 성공으로 확대할 수 없다. | 기존 graph를 연결하면 대략 1–3일, 직접 construction은 더 작게 가능; 설명력이 있는 관계 사례를 아직 정하지 않아 `exploratory` reserve |
| CD2 | 공개 8-model × 33-cell SR 표에서 uniform·category/level stratification·development-only mean matching | 전체 score/ordering 보존과 조건별 profile/누락을 함께 관찰한다. 개별 rare event는 알 수 없다. | 입력 취득 완료, 반나절 이내 준비·해석 및 CPU 1시간 이내 예상; **다음 관찰 선택** |

에이전트 판단: CD2는 작은 공개 표에서 단순 대안이 충분한지도 바로 확인할 수 있다.
새 method나 양의 결과를 요구해서 다른 후보를 닫는 것이 아니다. Q3는 직접 물성 선행으로
기존 질문의 새 정보가 줄었고, Q4/CD5는 관계·행동 reference 구성의 선택이 더 필요하다.
CD5는 여기서 Q4의 information/serialization control 축으로 다루며 RAG scope를 열지 않는다.

### Selected observation and boundaries

세부 protocol·입력 cohort·budget·estimator·model splits·missing-stratum 처리는
[CD2 question record](../../cross_domain/questions/tail-preserving-efficient-evaluation.md#first-observation)가
소유한다. Source/schema 확인까지 완료했고 sampling, ranking 계산, model 실행은 하지 않았다.
이번 선택은 `feasibility_study`이며 formal hypothesis 선택이나 paper claim이 아니다.

첫 결과가 단순 stratification으로 설명되면 새 sampler를 만들 필요가 없다는 정보를 얻는다.
차이가 남으면 어떤 조건/목표 때문에 남는지 해석하며, 너무 거친 표라면 정보 부족으로 기록한다.
원래 rare-failure 질문은 어느 경우에도 이번 표만으로 확정하지 않는다. 이 관찰을 마친 뒤
episode-level 후속 연구의 가치 또는 보류를 판단하고 aggregate proxy만 계속 확대하지 않는다.

## CD2 Follow-up Assessment 2026-09-17

**에이전트 판단: 공개 LBM episode 기록을 이용한 작은 후속 관찰 한 번에 투자한다.**
새 sequential test나 learned sampler를 선택한 것은 아니다. 첫 관찰의 condition omission과
달리, task를 모두 관측한 뒤에도 남는 trial sampling variability와 task별 성능 차이를
분리한다. 이번에는 문헌·source·schema만 확인했으며 새 성능 계산이나 baseline 실행은 없다.

### Closest alternatives and what remains observable

| Primary source / 읽은 범위 | 논문 주장·확인한 사실 | CD2의 해석과 경계 |
| --- | --- | --- |
| [STEP §II–III, Introduction](https://arxiv.org/html/2503.10966v1) | Binary policy comparison, bounded evaluation budget, error control과 stopping을 다룬다. Multi-task/multi-policy 확장도 명시한다. | 작은 gap의 순위 흔들림에 통계적 판단·보류를 붙이는 것만으로 새 질문이 되지 않는다. |
| [N-SCORE §IV, VI-B, VI-C4, VII, Appendix B](https://arxiv.org/html/2603.13616v1), [RSS proceedings](https://www.roboticsproceedings.org/rss22/p076.html) | Bounded partial-credit/continuous outcomes, LBM task별 비교, RoboArena 여러 policy의 비교와 multiplicity 처리를 다룬다. I.i.d. 평가 가정을 명시하며 WSR 대안은 두 reward의 차이를 사용한다. | Partial success, pairing, 여러 policy 또는 confidence interval 자체는 차별점이 아니다. Task별 기존 검정을 단순 대안에 포함해야 한다. Proceedings는 게재 정보만 확인했으며 본문 검토는 v1이다. |
| [Active Experiment Selection §III–VII](https://arxiv.org/html/2502.09829v1), [CoRL proceedings](https://proceedings.mlr.press/v305/anwar25a.html) | Outcome distribution의 정보 획득과 task-switch cost를 직접 다룬다. Best-average policy, ranking, worst tasks 등 다른 목적에 대한 선택을 후속 방향으로 적는다. | 기존 연구를 mean-only라고 부르거나 task allocation 자체를 새 방법으로 삼지 않는다. 논문이 안내한 `AbrarAnwar/seq-eval` GitHub API는 확인 시 404였다. 이는 그 endpoint의 접근 상태이며 방법의 불가능성 판정이 아니다. |
| [PEAK Abstract·Introduction](https://arxiv.org/html/2402.06122v2) | 여러 bounded data stream의 mean에 대한 composite hypothesis, adaptive collection과 anytime-valid inference를 다룬다. | Task별 동시 uncertainty와 adaptive sampling도 일반 통계 선행이 있다. 전체 이론·구현 재현은 이번 검토 범위 밖이다. |
| [RoboArena §3, Appendix B.4/B.6, D](https://arxiv.org/html/2506.18123v2) | 같은 session의 policy 비교, partial success, task difficulty와 변화하는 평가 분포를 다룬다. | Pairing·평가 task mix·단순 평균의 문제도 이미 benchmark가 검토한다. Preference나 partial success를 rare high-severity failure label로 바꾸지 않는다. |

따라서 “overall 순위가 불확실하니 CI를 추가한다”는 방향은 선택하지 않는다. 남는 작은
관찰은 **고정된 task 집합에서 평균 추정과 task별 진단의 표본 요구량이 실제로 얼마나
다른지**, 그리고 그 차이가 coverage·task mix·within-task variation 중 무엇으로 설명되는지다.
그 차이의 존재는 일반적인 통계 사실과 양립하며 그 자체로 novelty를 주장하지 않는다.
Population inference나 adaptive stopping 효과를 주장할 때에는 위 선행을 실제 대조해야 한다.

### Public inputs and scope of verification

- [N-SCORE official repository](https://github.com/dasnyder5/nscore/tree/68c0a3453248d16da0c3f0b96f229fb9daf9fe78)의
  `lbm_data_eval_part2.py`는 `data/LBM/lbm_data.pkl`에서 task별 두 policy의 `success`와
  `task_progress` sequence를 읽는다. 논문은 hardware 5 tasks에서 policy당 50 trials를 설명한다.
  Pickle은 45,825 bytes로 취득했다. Host에서 unpickle/import/수치 실행은 하지 않았다.
  안전한 opcode 문자열 조사에서 `figure_4_hardware_tasks`, `policy_type`, `skill`,
  `success`, `task_progress`, `num_rollouts`, `n_questions`와 두 policy type을 확인했다.
- 같은 commit의 `data/{LBM,PC_LBM}/Part2/` 10개 NPY는 header가 모두 `(50, 2)`,
  `<f8`이다. Header만 검사했으므로 이것만으로 column 의미나 metric 간 row identity를
  확정하지 않는다. 후속 실행에서 원본 pickle의 **명시적 key/column**과 대조한다.
  저자 script의 dictionary 순서·column 번호를 그대로 복사하지 않는다. 두 policy의
  같은 row가 동일 initial state라는 근거는 없으며 matched trial로 취급하지 않는다.
- LBM 후보는 BikeRotorInstall, CutAppleIntoSlices, CleanLitterBox,
  ClearKitchenCounter, SetUpBreakfastTable이다. Binary/progress 두 metric은 별도
  독립 trial 집합이 아니다. Success label만으로 rare/severe failure를 식별할 수도 없다.
- [RoboArena July dump](https://huggingface.co/datasets/RoboArena/DataDump_07-17-2026)의
  revision `7931db81f3f6a48a3245427f7213a4c461f92ccc`도 확인했다. Global metadata가
  sessions 3,883개와 policy episodes 10,783개를 보고하며, 실제로 읽은 session YAML은
  사전순 첫 2개뿐이다. Policy ID, binary/partial success, duration, instruction 필드가 있다.
  이 두 schema에서 고정 task-family/severity label은 확인하지 못했다. 전체 data의 부재
  판정이 아니며 전수 session·video·trajectory는 받지 않았다. VLA-Arena와 다른 자료다.

Immutable URL, cache path, hash와 확인 범위는 [source record](comparison_sources.json)의
`cd2_followup_20260917`에 둔다. NPY의 byte/header 확인과 method runtime 검증은 구분한다.

### Investment comparison

아래 비용은 에이전트 추정이며 measured throughput이나 rollout 절감률이 아니다.

| 선택지 | 새 정보 / 단순 대안 | 비용·판단 |
| --- | --- | --- |
| 기존 VLA-Arena aggregate 표의 seed/model/budget 확대 | 같은 유한 평균표의 더 자세한 sampling 결과 | Within-task variation을 추가하지 못해 선택하지 않는다. |
| LBM 5-task episode 관찰 | Uniform vs equal task stratification으로 task mix와 trial variation을 분리하고 global/task error를 함께 본다. Full-task-mean substitution은 진단용 oracle이다. | Raw pickle과 NPY 합계 55,105 bytes 확보. CPU 준비·해석 반나절–하루, 실행 1시간 이내 예상. **선택.** |
| N-SCORE/STEP를 붙인 새 early-stopping method | 이미 다룬 mean-comparison 목적의 정밀 재현 | 이번 실패 진단에서 새 stopping 원리가 나오지 않았다. 첫 후속 관찰의 필수 선행 gate로 만들지 않는다. |
| RoboArena 전체 session의 context별 진단 | 자연 task/environment variation과 paired session을 다룰 수 있다. 기존 benchmark의 latent-task model이 강한 대안이다. | Task grouping·cohort·session dependence를 정의하는 추가 작업이 필요하다. LBM보다 첫 분해 비용이 커 reserve로 둔다. 공개 자료가 없어서 보류하는 것은 아니다. |
| Q3 또는 Q4/CD5로 이동 | Discretization 또는 relation/identity의 다른 연구 질문 | 앞선 비교의 가능성은 유지한다. LBM의 제한된 추가 관찰을 마친 뒤 투자 가치를 다시 비교한다. |

추가 관찰은 한 번의 구현·실행·검산·해석으로 묶는다. Positive residual이나 새 method를
통과 조건으로 요구하지 않는다. 단순 층화와 유한 표본 변동으로 결과가 설명되면 그것을
수용하고 새 sampler 투자를 보류할 수 있다. Task별로 다른 문제가 남으면 그 실제 사례에서
질문을 수정한다. 구체적 estimand·budget·대조·판정은
[question record](../../cross_domain/questions/tail-preserving-efficient-evaluation.md#episode-level-follow-up)가 소유한다.

## Q3 Q4 Observation Comparison 2026-09-18

목적은 CD2 보류 뒤 다음 작은 관찰 하나를 선택하는 것이다. 연구 세부 설계는
[Q4 question](../questions/task-relevant-spatial-state.md#first-observation), source/hash는
[comparison_sources.json](comparison_sources.json)의 `q3_q4_comparison_20260918`이 소유한다.
이번에는 문헌 목록에 그치지 않고 공식 test 입력과 단순 대안의 실행 경로를 확보했다.

### Primary-source findings

**논문 주장.** [Taskography](https://proceedings.mlr.press/v164/agia22a/agia22a.pdf)의
§3–6은 scene graph의 symbolic planning, goal-dependent SCRUB, learned object selection과
SEEK를 다룬다. Grounded goal과 class-level lifted goal을 구분하고 후자에서 SCRUB의
보수적인 pruning을 설명한다. Relation/ancestor 보존과 instance selection 자체는
기존 연구의 범위다. 따라서 Clio의 single-step 한계나 semantic top-k의 실패만으로
새 long-horizon compression을 주장할 수 없다.

[Scale-Plan v1](https://arxiv.org/html/2603.08814v1)의 §III-A도 PDDL precondition/effect
관계의 action graph와 goal에서 거슬러 가는 filtering으로 action/object 후보를 줄인다.
이는 dependency-aware selection의 추가 직접 선행이다. 이번에는 v1의 설계만 읽었으며
최신 revision의 결과나 code availability를 확인했다고 주장하지 않는다.

**공식 code/data 사실.** Taskography의 [PDDL fork](https://github.com/taskography/pddlgym)와
[planner release](https://github.com/taskography/scenegraph-planners)는 domain, test PDDL,
SCRUB 출력 및 source를 제공한다. Tiny lifted 5-goal 문제 여섯 개와 grounded 1-goal
문제 두 개, 대응 SCRUB 파일을 확보했다. `_test`의 숫자 ID 순으로 정했으며 결과를
보고 고른 것이 아니다. Train의 `*scrub/problem0`은 generator의 `no_scrub` 경로로
원래 pruned input이 아니므로 이번 대조에는 쓰지 않는다. Snapshot 32개 파일의
크기/SHA256을 검증했다. Planner는 아직 실행하지 않았다.

**Q3 source 사실.** Workspace가 Q8에서 취득한 ManiSkill v3.0.1 source와 Q1 manifest를
읽었다. Default simulation/control frequency는 100/20 Hz이고 control step 안에서
substep을 반복한다. PD controller의 interpolation도 substep 수를 사용하므로 action
주기만 고정해도 내부 target sampling은 달라질 수 있다. 보존된 EE-delta-position과
joint-delta-position PPO는 action interface가 달라 곧바로 같은-interface policy
순위로 비교할 수 없다. Source/recipe는 활용 가능한 workspace 자료이며 host의 기존
Isaac image와는 구분된다. 새 common-interface scripted controller 비교도 가능하므로
Q3를 checkpoint 문제만으로 blocked 처리하지 않는다.

### Comparison and decision

다음 비용은 **에이전트 계획 추정**이며 실행 throughput 측정이 아니다.

| Candidate | Concrete observation / simplest alternatives | What it can teach | Preparation and remaining limits |
| --- | --- | --- | --- |
| Q3 | PickCube 하나, control 20 Hz 고정, sim 100/200/400 Hz, 같은 초기 상태. Default·더 작은 timestep 대조; 먼저 같은 interface의 scripted controller 두 설정 또는 compatible policy 구성 | Discretization 변화가 controller/contact trajectory와 상대 성과를 바꾸는지. 두 세밀한 설정의 일치 여부는 convergence 단서이며 real fidelity 증명은 아님 | 기존 source/recipe가 있어 1–2 작업일의 새 Docker/control adapter가 잠정 예산. GPU/runtime smoke와 controller semantics 분리가 필요. 보유 두 PPO 비교는 system-level sensitivity로 질문을 수정해야 함 |
| Q4 | Taskography lifted test 6개 + grounded sanity 2개. Full·공식 SCRUB·ID순/거리순 instance 선택에 같은 closure 적용 | Relation을 보존한 뒤 class multiplicity와 단순 근접 선택으로 validity·계획 비용 차이를 설명할 수 있는지. Symbolic abstraction에서 충분하면 추가 model 필요성이 낮음 | 작은 입력 확보 완료. CPU Docker/planner/validator 0.5–1 작업일 추정. 최대 40개 bounded planner 호출. Physical/visual noise와 LLM 표현 능력은 관찰 밖 |
| CD5 | Q4와 같은 facts를 losslessly 직렬화하고 canonical PDDL로 복원 | Selection과 serialization이 섞이지 않았는지 검사 | 작은 부가 control. 동일 facts를 canonicalize하는 planner에서 표현 우월성을 발견하는 독립 연구로 삼지 않음 |

**선택: Q4의 instance 선택 관찰 한 번.** 직접 선행이 더 명확해졌지만 공개 action contract와
강한 단순 기준을 함께 확보해 적은 비용으로 현재 설명을 구체화할 수 있다. 가장 새로운
후보라고 판정한 것이 아니다. Q3는 physics-policy 질문의 가치를 유지한 reserve다.
Q4가 단순 대안으로 설명돼도 유효한 결과이며, 그때 같은 slice의 반복 확대보다 실제
사례에서 필요한 수정 또는 다른 관찰의 정보 가치를 비교한다. 최종 novelty·positive
residual·두 번째 domain을 이 선택의 gate로 추가하지 않는다.

## Q4 Follow-up Investment Review 2026-09-18

Q4의 [goal-conditioned 관찰](../pilot_studies/q4-planning/README.md#goal-conditioned-observation-2026-09-18)
뒤 직접 선행과 추가 관찰의 정보 가치를 비교했다. 이는 scoping review이며 exhaustive
novelty audit가 아니다. 읽은 판본·절과 source/input hash는 [comparison_sources.json](comparison_sources.json)의
`q4_followup_review_20260918`이 소유한다. 연구 결과 수치는 기존 study owner에 둔다.

### What the direct priors already cover

| Primary source and reading scope | 논문 주장 / 확인한 내용 | Q4 관찰과의 관계에 대한 에이전트 판단 |
| --- | --- | --- |
| [Taskography](https://proceedings.mlr.press/v164/agia22a/agia22a.pdf), §5–6, Fig.4, Table3–4 | SCRUB는 목표와 ancestor를 보존하고 SEEK는 learned scoring 뒤 연결성을 보완한다. Lifted Rearrangement(5)에서 pruning 유무 및 optimal/satisficing planner의 success·length·time을 함께 비교한다. | 관계 보존과 planner에 따른 계획 길이 차이는 이미 직접 평가 대상이다. 이번 단순 선택의 평균 개선만으로 새로운 representation principle을 주장하지 않는다. |
| [Planning with Learned Object Importance in Large Problem Instances using Graph Neural Networks v2](https://arxiv.org/pdf/2009.05613v2), §3–4, Appendix A | PLOI는 축약 문제의 해를 원본 문제에서 검증하고 필요하면 object set을 확대한다. 개별 object scoring이 같은 종류의 여러 copies 중 필요한 수만 선택하는 데 갖는 한계도 명시한다. Test planner는 LAMA-first, training에는 optimal planner를 사용한다. | 원본 validation, class multiplicity, learned selector의 도입 자체가 새 기여는 아니다. 우리 distinct assignment는 단순 대조이며 PLOI를 재현하거나 이겼다는 결과가 아니다. |
| [Scale-Plan v1](https://arxiv.org/html/2603.08814v1), §III-A | Precondition/effect로 만든 action graph에서 backward search하여 관련 action과 object를 필터링한다. | Dependency-aware selection의 추가 선행이다. 이번 정적인 fully observable PDDL 관찰이 언어 ambiguity·partial observation을 검증한 것은 아니다. 최신판 결과·코드 재현 주장은 하지 않는다. |

**관찰이 남긴 것:** 문제40에서 더 짧은 SCRUB plan이 Goal state에서도 유효하고, 문제42–45의
더 짧은 Goal plan도 SCRUB에서 유효했다. 그 차이는 현재 search output의 차이임을 이미
보였다. 문제43은 같은 proxy 최솟값의 tie에서 선택 instance가 바뀌고 긴 plan이 나왔다.
특정 짧은 plan이 제외됐지만 optimal cost 증가를 증명하지는 않았다.

따라서 남은 작은 기술 질문은 **문제43의 손실이 reduced problem의 optimal cost 증가인지,
선택한 search의 영향인지**다. Optimal planner나 더 강한 route 대조로 해석을 더 좁힐 수는
있다. 다만 그것만으로는 이번 fully observable object-selection 질문의 새로운 로봇 행동
문제나 원리가 생기지 않는다. Joint route/binding을 더 잘 최적화하는 수정, random tie,
learned scorer와 동일 slice 확대를 계속하는 것의 현재 추가 정보 가치는 낮다고 판단한다.

### Q3 is also close to prior work

**논문 주장:** [SIMPLER](https://arxiv.org/html/2405.05941v1), §VI-D/Table X는 mass·friction
변화에 따른 policy 성능과 real-to-sim 순위 상관을 이미 조사했다. 물성 변화에 대한
민감도나 순위 비교 전체를 미개척 문제라고 쓰지 않는다.

[Contact Models in Robotics: a Comparative Analysis](https://simple-robotics.github.io/publications/contact-models/static/paper/lelidec2024contacts.pdf),
§IV-B/D는 timestep self-consistency와 contact solver가 로봇 제어 결과에 미치는 영향을
분석한다. 작은 timestep을 물리적 ground truth로 취급해서는 안 된다.

[What Are We Actually Benchmarking in Robot Manipulation? v1](https://arxiv.org/html/2606.04233v1),
Appendix B는 hardware에 따른 작은 차이가 closed-loop state/action/outcome으로 전파되는
사례와 같은 hardware의 대조를 제시한다. Fixed-action replay는 closed-loop 재현성을
대체하지 않는다고 구분한다. **Feedback amplification 자체도 새 insight로 주장하지 않는다.**

**공식 source 사실:** 보존된 ManiSkill v3.0.1에서 `sim_freq/control_freq`가 substep 수를
정한다. Panda `pd_joint_delta_pos`는 현재 qpos에 delta를 더하고, interpolation 기본값은
false다. 따라서 normalized delta action의 단순 재생은 같은 absolute target을 뜻하지 않는다.
GPU `step(None)`은 새로운 action을 설정하지 않는 경로이므로 target replay adapter에는
arm/gripper target 설정뿐 아니라 GPU target buffer apply가 필요하다. 이는 source-level
실행 경로 확인이며 아직 adapter runtime 검증 결과가 아니다.

### Relative information value and cost

비용은 에이전트 계획 추정이며 새 runtime 측정값이 아니다.

| 선택지 | 다음에 줄일 uncertainty | 준비/실행 비용과 한계 | 판단 |
| --- | --- | --- | --- |
| Q4 optimal/route 대조 | 문제43에서 현재 subset의 optimal cost와 search gap을 더 분리 | 기존 CPU image 활용 가능; 반나절 내 제한된 대조 가능하나 timeout이면 미해결. 선행이 이미 다루는 pruning·plan quality 설명의 세부 확인 | 지금 추가 실행하지 않음 |
| Q4 perception/action 확장 | Partial observation·실제 행동에서 어떤 정보가 필요한가 | 새 state/action 연결 자료가 필요하고 현재 symbolic 반례가 특정 관찰을 요구하지 않음 | 원래 broad 질문은 보존, 현재 경로 보류 |
| Q3 단일 frozen policy의 timestep 대조 | 고정 control/PD 설정에서 numerical setting이 행동·성공을 바꾸는지; absolute-target replay와 closed loop에서 변화가 다른지 | 기존 작은 checkpoint/source 사용, 새 Docker와 target adapter 1–2 작업일; 본 관찰 GPU wall 1시간 이내 계획. Ranking·real fidelity를 검증하는 실험은 아님 | 작은 관찰 한 번 선택 |

**선택:** Q4의 현재 fully observable instance-selection 경로는 `deferred`로 두고 Q3의
작은 mechanism 관찰을 진행한다. 더 가까운 prior가 없어서가 아니라, Q4의 두 관찰로 이미
배운 pruning/search 설명을 반복하기보다 아직 보지 않은 controller–simulation 연결을
제한된 비용으로 관찰할 가치가 있다고 판단했다. Q3의 결과가 안정적이어도 유용하다.

보유한 EE PPO와 joint PPO의 서로 다른 action interface를 새 알고리즘 순위로 비교하지
않는다. 먼저 joint PPO 하나의 control 주기·PD 설정을 고정한다. Two-policy ranking을
진입 조건으로 앞당기지 않되 **이번에는 ranking을 측정하지 않는다는 범위 수정**을 명시한다.
선택한 대조·수·readout·중단 범위는 [Q3 first observation](../questions/physics-ranking-stability.md#selected-first-observation)이
소유한다. 새 학습, 최종 novelty 판정, hypothesis/paper 승격은 없다.

## Q3 Investment and Q15 Selection 2026-09-18

**판단: Q3의 현재 timestep-sensitivity 경로는 보류하고 Q15의 작은 reward-training
관찰을 선택한다.** 이번 작업은 기존 결과 해석, primary-source 검토와 읽기 전용 source
확인이다. Q15 학습·물성 개입은 아직 실행하지 않았다. 읽은 판본·범위와 source hash는
[comparison_sources.json](comparison_sources.json)의 `q3_followup_q15_selection_20260918`이 소유한다.

### Q3 result and closest explanations

**관찰 사실:** [Q3 결과](../pilot_studies/q3-timestep/README.md#results-2026-09-18)는 모든
condition에서 같은 여덟 초기 상태의 성공 결과가 유지됐음을 보인다. Frequency 간
trajectory 차이는 있고 closed loop에서 더 크지만 outcome fragility나 ranking은 관찰하지 않았다.

| Primary source / 읽은 범위 | 논문 주장 | 이번 결과에 대한 에이전트 판단 |
| --- | --- | --- |
| [SIMPLER v1](https://arxiv.org/html/2405.05941v1), §VI-D/Table X | Mass/friction 변화와 여러 policy의 real-to-sim 순위 상관을 평가한다. | 물성 변화나 순위 비교 자체는 새 질문이 아니다. 단일-policy timestep 결과를 이 논문의 ranking 검증으로 바꾸어 읽을 수 없다. |
| [Contact Models in Robotics](https://simple-robotics.github.io/publications/contact-models/static/paper/lelidec2024contacts.pdf), §IV-B/D | Timestep self-consistency와 solver에 따른 contact/control 차이를 다룬다. | 현재 trajectory 차이는 기존 설명과 양립한다. 더 작은 dt를 정답으로 삼거나 다른 solver를 추가하는 것만으로 새 원리가 생기지 않는다. |
| [What Are We Actually Benchmarking in Robot Manipulation? v1](https://arxiv.org/html/2606.04233v1), Appendix B | Bitwise, per-episode, aggregate, statistical agreement를 구분하며 closed-loop feedback에서 수치 차이가 전파되는 사례를 보인다. | Bitwise/trajectory 차이를 success 차이와 구분해야 한다. Target replay와 closed loop의 차이 자체를 새로운 amplification 현상으로 쓰지 않는다. 이 논문은 hardware 대조이고 우리의 timestep 대조와 동일 실험은 아니다. |

**후속 판단:** 성공이 같았다는 이유만으로 넓은 Q3를 반증하지 않는다. 추가 controller,
seed 또는 dt를 선택해 같은 설명을 반복하기보다, 구체적인 행동 결정의 불확실성을
줄이는 경우에 다시 투자한다. 안정적인 결과도 유효하며 양의 결과를 찾을 때까지
범위를 넓히지 않는다. Q3의 [재검토 조건](../questions/physics-ranking-stability.md#investment-decision-and-re-entry)을 갱신했다.

### Q15 is a learning observation with strong prior overlap

[Eureka official project](https://eureka-research.github.io/)의 reward program search를
출발점으로 삼되 이번에 LLM search를 재현하지 않는다.
[DrEureka v1](https://arxiv.org/html/2406.01967v1)의 §IV-B/C와 Appendix E/Table XVI는
reward-dependent behavior, safety instruction과 physics randomization의 관계를 직접 다룬다.
특히 nominal simulation에서 더 빠른 reward가 실제 전이에 실패하는 사례가 있어
**nominal reward 우열과 transfer 우열이 다를 수 있다는 일반 명제는 이미 선행에 있다.**
[HPRS](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1444188/full)의
Abstract/§2.1/§3.4/§5도 task hierarchy, potential-based shaping과 단순 engineered reward를
비교한다. Reward 항 하나를 조절하는 행위나 hierarchy 자체도 contribution이 아니다.

에이전트 판단: 그럼에도 현재 보유한 작은 manipulation task에서 reward의 구성요소를
실제로 바꾸어 학습하면, frozen-policy 평가만으로는 모르는 **학습 진행도·scale·접촉
행동의 관계**를 관찰할 수 있다. 차이가 남을 것으로 전제하지 않으며 하나의 grasp bonus
제거를 로봇 전반의 robust reward 원리로 일반화하지 않는다.

**Source 확인:** Pinned ManiSkill의 `pick_cube.py`에서 reward와 native success의 차이,
`ppo.py`/`examples.sh`에서 작은 state MLP의 PPO 학습 경로를 확인했다. 공식 README는
PickCube 학습을 2–5분으로 안내하지만 이는 우리 hardware의 실측 시간이 아니다.
Domain-randomization 문서는 GPU initialization 전 물성 설정과 shared-material 주의를
명시한다. Nominal reset만 바꾸는 것과 물성 개입을 구분해야 한다. 새 dataset, pretrained
foundation model이나 host의 기존 Isaac 설치는 이 관찰에 필요하지 않다.

### Information value and cost comparison

아래 비용은 이번에 실행해서 얻은 throughput이 아닌 **계획 추정/상한**이다.

| 선택지 | 다음에 배울 내용 | 비용과 판단 |
| --- | --- | --- |
| Q3 같은 grid 확대 / compatible policy 추가 | 이 범위의 안정성 또는 특정 policy pair의 민감도 | 기존 adapter 재사용으로 비교적 저렴하지만 현재 남은 trajectory 설명과 행동 결정의 연결이 구체적이지 않다. 지금 보류. |
| Q4 partial-observation/action 확장 | 실제 정보 누락이 instance selection과 실행에 주는 영향 | 새 관찰/행동 연결과 state reference를 정해야 한다. 기존 fully observable PDDL 추가 실행만으로는 해결되지 않아 보류 유지. |
| CD1 multi-action intervention | 같은 상태에서 retry/replan/defer의 실제 효용 | Counterfactual action·cost·replay 계약을 아직 확보하지 않았다. 기존 deferred record의 공개 denominator 문제는 이번에 해소하지 않았다. 보류 유지. |
| Q15 fixed reward intervention | Grasp shaping의 효과가 scale·학습 진행도와 어떻게 구분되는지; 물성 변화에서 행동/성공이 어떻게 달라지는지 | 기존 source와 task를 활용하되 새 Docker/training adapter 필요. 준비 1–2 작업일, 9 fits에 GPU wall 3시간·평가/검산 1시간 상한. 작은 관찰 한 번 선택. |

**선택 범위:** Official normalized dense, grasp bonus 제거, scale-only 대조를 세 training
seeds로 학습한다. 미리 고정한 중간/최종 checkpoint와 nominal/물성 변경을 함께 관찰한다.
정확한 식, 상호작용 수, 평가 분모, 검산·중단 조건은 [Q15 first observation](../questions/reward-dynamics-transfer.md#first-observation)이
소유한다. Uniform DR·potential-based shaping·validation-based selection은 해석에 따라
선택할 강한 후속 대안이지 첫 관찰 진입을 막는 추가 gate가 아니다.

가장 새로운 후보로 입증됐기 때문에 고른 것이 아니다. 기존 Q15의 학습비용 불확실성을
공식 작은 task 경로와 명시적 자원 상한으로 줄일 수 있고, 현재까지 직접 바꾸어 보지 않은
학습 개입이 다음 설명을 구체화할 수 있기 때문에 선택했다. 문헌 검토는 scoping 범위이며
exhaustive novelty audit나 DrEureka/HPRS 재현을 완료한 것이 아니다.

## Q15 Follow-up Investment 2026-09-18

**판단: 재학습 대신 성공 후 joint-position hold 대조 한 번을 선택한다.**
현재 grasp-bonus/물성 grid의 확대는 보류한다. 기존 결과는 reward별 행동 차이를 보였지만
고유한 transfer 이점을 지지하지 않았다. 아래 비교는 실행 결과가 아닌 후속 투자 판단이며,
읽은 source·접근 한계는 [comparison_sources.json](comparison_sources.json)의
`q15_followup_review_20260918`이 소유한다.

### Closest explanations and limits

| Primary source / 읽은 범위 | 논문 주장 | Q15에 대한 에이전트 판단 |
| --- | --- | --- |
| [Implementation Matters in Deep RL: A Case Study on PPO and TRPO](https://arxiv.org/pdf/2005.12729), §3/Fig.1; [What Matters In On-Policy Reinforcement Learning? A Large-Scale Empirical Study](https://arxiv.org/pdf/2006.05990), §3.3 | Reward/value normalization 등 구현 선택이 성능에 영향을 준다. Value normalization의 효과는 과제마다 다르며 advantage normalization과 구분한다. | Advantage normalization이 켜져 있다는 이유로 Q15의 scale 효과를 배제할 수 없다. 이 논문들이 현재 PickCube 실패의 원인을 입증한 것은 아니다. |
| [Reward Scale Robustness for Proximal Policy Optimization via DreamerV3 Tricks](https://papers.nips.cc/paper/2023/file/04f61ec02d1b3a025a59d978269ce437-Paper-Conference.pdf), NeurIPS 2023, §3.4/§4.2–4.3 | Normalization 기법의 이점은 reward 처리에 따라 달라지며 단순 clipping 대조가 강하다. 기법을 PPO에 옮겼다고 보편적 개선이 생기지는 않는다. | Scale 처리나 새 정규화 모듈 자체는 새 원리가 아니다. 해당 Atari/DM Control 결과를 contact-rich manipulation의 재현으로 읽지 않는다. |
| [DrEureka v1](https://arxiv.org/html/2406.01967v1), §IV-B/C | Reward가 유도하는 행동과 physics randomization의 관계를 다룬다. | Reward-dependent transfer는 이미 직접 선행이다. 현재 Q15는 nominal 차이가 크고 시험한 shift 감소가 작아 새 robust reward selection을 요구하지 않는다. |
| [Solving Reach-Avoid-Stay Problems Using Deep Deterministic Policy Gradients](https://arxiv.org/html/2410.02898v2), v2, §II–III/Fig.1 | 목표 집합 도달과 내부 유지 정책을 구분하고 control-invariant set에 기반해 전환한다. 이론적 보장은 학습 오차가 없는 등의 전제 아래 제시한다. | 도달과 유지의 구분이나 controller 전환 자체는 새 개념이 아니다. 이 논문의 보장을 우리의 단순 joint hold나 접촉 동역학에 적용하지 않는다. |
| [Learning Reach-Avoid Task with Reinforcement Learning: Vectorized Simulation and Benchmark](https://arxiv.org/html/2607.15935v1), 2026 preprint, §IV-A | 도달 후 episode를 계속하는 reach-and-stay setting과 joint action 표현·보상 설계를 비교한다. | 성공 이후 유지 평가도 선행에 있다. EE reaching과 grasped-object retention은 다르므로 현재 실패가 이미 해결됐다고 단정하지 않는다. |

OpenReview의 관련 forum/PDF 세 주소는 browser verification으로 내용 접근이 막혀
공개 arXiv/NeurIPS PDF를 사용했다. 위 표는 명시한 범위의 preliminary review이며
exhaustive survey, 논문 재현 또는 exact novelty 확정이 아니다.

### What the current data identify

**관찰 사실:** [Q15 결과 owner](../pilot_studies/q15-reward/README.md#results-2026-09-18)에
따르면 half-scale의 nominal 성공이 중간 65/96에서 최종 93/96으로 증가했고 no-grasp의
최종 94/96과 가까워졌다. Native의 성공 후 실패 9건 중 한 seed의 8건은 마지막에도
grasp/static이 true지만 목표 거리 25 mm를 벗어났다. 이 기록은 학습 원인이나 성공 이후
다른 action을 냈을 때의 결과를 제공하지 않는다.

**수학적 구분:** 동일한 dynamics·discount·종료 규칙의 expected-return objective에서
모든 보상을 양수 0.5배 하면 각 정책에 대해 `J_half(pi)=0.5*J_native(pi)`다. 따라서 그
objective의 최적 정책 집합은 변하지 않는다. 이번 half-scale의 유한 학습 결과 차이는
과제의 새 최적해를 찾았다는 증거가 아니며 optimizer/estimation/exploration 차이와 양립한다.
이 식은 no-grasp 개입에는 성립하지 않고 유한 PPO 학습의 동일성을 보장하지도 않는다.

**확인한 source 사실:** Pinned PPO는 별도 actor/critic, 정규화된 minibatch advantage,
정규화하지 않은 return에 대한 value MSE, 전체 parameter에 대한 gradient clipping,
KL early stop을 사용한다. 따라서 actor advantage의 normalization만으로 전체 update가
reward scale에 불변이라고 주장할 수 없다. 이 중 어느 요소가 이번 차이를 만들었는지는
검증되지 않았다. Scalar loss 로그의 상관만으로 이를 확정하지 않는다.

### Relative value of follow-ups

비용은 현재 약 7분/fit·72조건 평가 6분이라는 실측을 참고한 **계획 추정**이다.

| 대안 | 알아낼 내용 | 한계와 투자 판단 |
| --- | --- | --- |
| 학습 연장 / optimizer·value normalization 대조 | 학습 부족 또는 특정 최적화 요인의 효과 | Exact-resume state가 없어 조건을 맞춘 재학습이 필요하다. 수십 분~수 시간과 설정 탐색을 써도 현재의 목표 유지 실패에 필요한 행동을 직접 식별하지 않는다. 지금 선택하지 않음. |
| 물성 범위·seed 확대 / DR·PBRS 학습 | 더 넓은 shift와 학습 원리의 영향 | 현 관찰의 잔여 실패보다 문제 범위를 먼저 넓힌다. 현재 shift가 약했다는 한계는 보존하되 실패가 나올 때까지 확대하지 않음. |
| 저장 궤적의 action·value 상관 분석만 추가 | 목표 이탈 직전의 관측된 변화 | 다른 action의 결과가 없어 hold가 충분한지 알 수 없다. 기존 53건 분석은 보존하며 이를 독립적인 원인 증거로 확대하지 않음. |
| 기존 policy와 성공 후 joint-position hold 비교 | 재학습 없이 동일한 성공 상태에서 간단한 유지 제어가 실패를 피하는가 | 9개 최종 checkpoint·nominal·공통 32초기 상태를 재사용한 576 episodes. 준비 약 0.5–1 작업일, GPU rollout 15분/검산 포함 1시간 상한 계획. 작은 대조 한 번 선택. |

**정보 가치:** Hold로 실패를 피하면 현재 사례에는 새 reward 학습보다 단순 실행 제어가
충분할 수 있어 복잡한 방법 투자를 줄일 수 있다. Hold에서도 실패하면 어떤 상태에서
고정 관절 목표가 부족한지 배우지만, 물리적으로 불가피한 실패나 특정 reward 원인을
증명한 것은 아니다. 양쪽 결과 모두 현재 보상 개입의 해석을 좁힌다.

### Selected observation and boundary

관찰의 소유 문서는 [후속 설계](../pilot_studies/q15-reward/README.md#joint-position-hold-observation)다.
이미 본 초기 상태·checkpoint를 재사용하는 exploratory intervention이며, privileged native
success를 전환 신호로 쓴다. Learned trigger, 안정성 보장, real-world deployment나 새 method
주장은 없다. 단순 zero action은 현재 qpos 기준의 target을 매 step 다시 만들므로 고정
reference와 다르다는 것을 source에서 확인했다. 새 controller/normalization module 학습,
reward 계수 탐색, hypothesis/paper 승격은 선택하지 않았다.

## CD5 CD1 Q8 Comparison 2026-09-22

**판단: CD5의 동일 정보 symbolic planning 관찰 한 번을 선택한다.** CD1은 공개 synthetic
실행 경로가 새로 확인됐지만 지금 재개하지 않고, Q8은 기존 `refine` 조건을 유지한다.
최종 novelty가 입증됐다는 선택이 아니라 다음 행동 오류의 설명을 좁히는 정보 가치·비용
판단이다. Source identity·읽은 범위는 [comparison_sources.json](comparison_sources.json)의
`cd5_cd1_q8_review_20260922`가 소유한다.

### Primary evidence and inference

| Primary source / 확인 범위 | 논문 주장 | 이번 선택에 대한 에이전트 판단 |
| --- | --- | --- |
| [Talk like a Graph: Encoding Graphs for Large Language Models](https://arxiv.org/abs/2310.04560), abstract와 저자 연구 소개 | Graph encoding에 따라 LLM graph-task 성능이 달라진다. | 표현 방식에 따른 차이 자체는 새 현상이 아니다. 논문 전문 재현을 한 것은 아니다. |
| [Lost in Serialization: Invariance and Generalization of LLM Graph Reasoners](https://arxiv.org/html/2511.10234v3), v3, §3–4 | Node labeling, edge structure와 syntax를 분리하며 모델별 민감도와 일반화를 비교한다. | 동일 정보·순서 대조의 직접 선행이다. 단순 문자열/답변 변화 대신 robot-plan 실행 실패와 비용을 읽어야 한다. |
| [LookPlanGraph: Embodied Instruction Following Method with VLM Graph Augmentation](https://arxiv.org/html/2512.21243v1), §VII-D와 공식 source | Graph 표현 및 행동 보정의 ablation을 보고한다. | 표현만 바꾸고 실행 보정을 누락하면 잘못된 방법 필요성을 추론할 수 있다. 자연어/JSON 및 단순 보정을 먼저 비교한다. 전체 pipeline의 재현은 아니다. |
| [VeriGraph: Scene Graphs for Execution Verifiable Robot Planning](https://arxiv.org/html/2411.10446v3), §III-B–D | Scene graph에서 action feasibility와 goal을 검사하고 feedback으로 계획을 수정한다. | Graph verifier/repair를 붙이는 것 자체는 기여가 아니다. 첫 관찰에는 더 싼 deterministic prerequisite correction을 둔다. |
| [A Human-in-the-Loop Confidence-Aware Failure Recovery Framework for Modular Robot Policies](https://arxiv.org/html/2602.10289v1), §3–7 및 공식 [modular-query](https://github.com/empriselab/modular-query) | Module confidence, dependency와 human query cost를 함께 사용한다. Confidence-only와 cost-aware query 전략을 비교한다. | CD1의 broad calibration-vs-utility 전제와 직접 겹친다. Synthetic graph 실험 source가 공개돼 있으므로 “실행 가능한 public route가 없다”는 일반적 표현은 정정한다. 다만 실제 robot의 같은 상태에서 retry/replan/defer를 비교한 로그와는 다르다. |
| [RAYA: Learning Where and When to Intervene for Robot Recovery](https://arxiv.org/html/2609.21690v1), abstract/framework | Finite-horizon recoverability를 학습해 constrained controller의 task priority를 조정한다. | Recoverability와 intervention 연결도 직접 선행이다. Quadrotor/vehicle 결과를 manipulation demonstration coverage로 옮겨 읽지 않는다. |
| [EgoRecovery: Acquiring Failure Recovery Ability Through Human Recovery Demonstration](https://arxiv.org/html/2607.19745v1), abstract/method overview | Human recovery demonstration과 제한된 robot recovery data로 corrective intent와 recovery 동작을 학습한다. | Nominal demonstration의 주변 성공률을 recovery data로 바로 해석할 수 없다. Q8의 training-data linkage와 복원 유효성 문제가 해결됐다는 근거는 아니다. |

이 표는 읽은 범위의 preliminary comparison이며 exhaustive novelty audit가 아니다.
EgoRecovery의 연결된 GitHub endpoint는 이번 확인에서 404였다. 이 접근 실패를 전체
공개 artifact 부재나 연구 불가능으로 일반화하지 않는다.

### Public input and evaluator facts

LookPlanGraph project page의 dataset 안내만으로 unavailable로 판단하지 않았다. Pinned
GitHub tree에는 작은 BEHAVIOR 기반 symbolic JSON과 graph validator가 있었다.
`behaviour177.json`의 실제 record는 178개로 파일명/README/논문 수와 다르므로 현재
bytes/hash와 개별 task identity를 기준으로 분모를 고정한다. 이것은 원본 BEHAVIOR
simulator dataset 또는 물리 rollout이 아니다.

`SceneSim.correct_action`은 room 이동·closed container 열기 등을 삽입한다.
`validator.py`는 원래 계획을 검사하고 goal의 일부 object를 class-equivalent count로
비교한다. 따라서 원래 action의 오류와 보정 후 성공을 분리하며, 단순 action sequence
불일치를 실패로 보지 않는다. Self-placement 비교와 JSON converter의 전역 참조는
source에서 확인한 구현 주의점이며 실제 runtime correctness는 다음 Docker 관찰에서 검증한다.

Modular-query의 pinned source에는 confidence-only strategy, module dependency simulation과
synthetic experiment entry가 있다. Python 3.11+, solver 관련 dependencies가 명시됐지만
이번에 install/run하지 않았다. Source 접근과 robot-level counterfactual evidence를 구분한다.

### Information value and cost

아래 비용은 아직 측정하지 않은 준비 추정/자원 상한이다.

| 후보와 작은 대조 | 배울 내용 | 단순 대안·비용과 선택 |
| --- | --- | --- |
| CD5: 동일 initial facts의 JSON/text × ordered/shuffled, strict/corrected 실행 | Harmless plan variation과 실제 전제조건/goal 실패를 구분하고 단순 정렬·보정이 충분한 범위를 확인 | 공개 입력 약 1.4 MB, frozen 3B model 약 6.2 GB. 준비 약 1작업일, 최대 120 generation·GPU 4시간/검산 1시간. Q4의 canonical round trip과 달리 모델은 실제로 다른 입력을 읽는다. **선택.** |
| CD1: public module graph의 confidence-only/cost-aware query | Cost/dependency와 confidence가 선택 행동을 달리하는 구체적 사례 | CPU synthetic route는 가능하다. 준비 약 1–2작업일이나 직접 선행의 비교를 반복할 가능성이 높고 robot retry/replan의 잔여 질문은 별도다. Q15의 oracle-trigger 두 action을 confidence benchmark로 재명명하지 않는다. **보류 유지.** |
| Q8: demo 부근 physical perturbation의 recovery target | Nominal data와 다른 perturbation에 대한 회복의 관계 | 단순 empirical-success 대조, 학습 데이터에 연결된 policy와 유효 demo restart를 다시 구성해야 한다. 기존 fixture의 수십 초 실행시간은 이 준비 비용을 대표하지 않는다. 준비 최소 수작업일, 범위 불확실성이 상대적으로 크다. 같은 PPO grid 확대는 **선택하지 않음.** |

CD5의 기대 가치는 새 효과를 얻는 데 있지 않다. 단순 정렬·전제조건 보정으로 충분하면
표현 module 투자를 줄일 수 있고, 실패가 남으면 object/관계/goal 해석 중 무엇이 문제인지
다음 사례를 얻는다. 첫 관찰부터 multi-model, exact token matching, 전체 benchmark나
novel residual을 요구하지 않는다. 다만 같은 정보라는 계약과 evaluator 의미는 지켜야 한다.

선택한 [study protocol](../../cross_domain/pilot_studies/cd5-representation/README.md)은
6 development + 24 observation task, 네 입력 조건, 동일 계획의 strict/보정 대조와
해석 분기를 정한다. 물리 실행·부분 관측·real-robot generalization은 이번 관찰의 범위가
아니며 최종 hypothesis/paper 진입 기준은 유지한다.


## Candidate Replacement 2026-09-23

### Request and comparison

**사용자 판단:** 기존 후보 대신 다른 후보를 탐색·선택하라는 요청에 따라 CD5 실행 선택을
철회했다. 선호하지 않은 세부 이유는 전달되지 않았다. 아래 선택 이유는 에이전트 판단이다.
기존 Robotics/3D Vision, 약 6개월, 단일 workstation GPU, simulation-first 경계를 승계했다.
`PaperReview`의 registry와 learning/contact/VLA/3D synthesis를 discovery cue로 읽고,
논문 내용은 아래 primary source에서 확인했다. Local notes는 수정하지 않았다.

| 검토 질문 | 가장 가까운 선행과 겹치는 부분 | 다음 관찰의 가치·비용 및 판단 |
| --- | --- | --- |
| 상황 변화에 따라 action chunk를 언제 중단·재계획할까? | [BID](https://arxiv.org/html/2408.17355v1)는 chunk 간 coherence와 resampling을, [Bernoulli-Continuation Policy](https://arxiv.org/html/2608.03483v1)는 학습한 continuation과 adaptive execution horizon을 직접 다룬다. | Success/latency 질문은 중요하다. 다만 현재 초안인 continuation head만으로는 비교 질문이 좁혀지지 않았고 frozen VLA 실행 준비도 필요해 이번 우선순위는 낮췄다. 선행 존재만으로 폐기한 것은 아니다. |
| 적은 demonstration에서 접촉 구간의 유효 데이터를 만들 수 있을까? | [DemoGen](https://www.roboticsproceedings.org/rss21/p157.html)은 synthetic demonstration, [PhysicsGen](https://www.roboticsproceedings.org/rss21/p053.html)은 contact-rich trajectory optimization을 다룬다. | 접촉 실패를 직접 줄일 수 있지만 generic physics-aware augmentation은 이미 존재한다. 첫 관찰에 demo 생성·retarget·policy 학습을 함께 준비해야 하므로 reserve로 둔다. |
| 조작 단계에 따라 유리한 좌표계를 선택하면 어떨까? | [Mixture of Frames Policy](https://arxiv.org/html/2607.11884v1)는 multiple-frame denoising과 결합을 직접 다룬다. | 사용자의 geometry/policy 관심과 맞지만 frame 선택만을 제안하는 초안은 직접 중복이 크다. 새로운 task-specific 질문 없이 이번 구현 대상으로 삼지 않는다. |
| 접촉으로 운동이 바뀔 때 예정 행동을 고려한 짧은 예측이 필요한가? | SIDO, DynamicVLA, action-conditioned contact dynamics와 reactive control이 가까운 선행이다. | **Q16 선택.** 물체 운동을 제어가 바꾸는 상황과 closed-loop 성공을 바로 연결하며, 작은 state-based task·model과 단순 feedback 비교로 시작할 수 있다. Exact novelty와 실제 실행 비용은 미확정이다. |

### Main prior map and limits

- [SIDO: Static In, Dynamic Out](https://arxiv.org/html/2607.27890v1) §3–5와 limitations를 읽었다.
  Static demonstration의 action을 moving-target trajectory로 증강하고 pose history에서
  future target을 예측한다. §4.2의 증강 대상은 `t + T_p <= T_g`인 pre-grasp chunk다.
  DynaSIDO는 robot dynamics model과 MPPI refinement도 사용한다. **이 범위는 접촉 이후
  제어의 실패 증거가 아니며, 논문이 접촉 후에도 같은 외삽을 맹목적으로 쓴다고 주장하지 않는다.**
- [DynamicVLA](https://arxiv.org/html/2601.22153v1)의 method, dataset/controller 설명과 task
  appendix를 읽었다. Continuous inference, latency-aware execution과 단계별 grasp controller가
  있고 contact-induced deflection도 task에 포함된다. 따라서 동적 접촉 자체가 빠져 있다는
  gap은 성립하지 않는다. 실제 full baseline의 대응 성능은 Q16에서 아직 비교하지 않았다.
- [Learning Contact Dynamics for Control with Action-conditioned Face Interaction Graph Networks](https://arxiv.org/html/2509.12151v1)의
  abstract/introduction은 action-conditioned contact dynamics와 MPC를 명시한다. 이것이
  Q16의 가장 직접적인 method overlap이다. 단순한 action input 추가나 dynamics model+MPC를
  새 principle로 제시할 수 없다. Full architecture/code는 아직 audit하지 않았다.
- [Reactive Diffusion Policy](https://arxiv.org/html/2503.02881v1)의 abstract/introduction과
  [RSS record](https://www.roboticsproceedings.org/rss21/p052.html)를 확인했다. Slow-fast tactile
  feedback는 직접 비교 축이다. 다만 첫 state-based study에 tactile modality를 추가하지 않는다.
- [Language-Driven Closed-Loop Grasping with Model-Predictive Trajectory Replanning](https://arxiv.org/html/2406.09039v1)의
  abstract/introduction은 online replanning 대안을 제공한다. 고전적인 feedback/MPC보다
  나은지 묻지 않고 learned predictor만 비교하면 연구 필요성을 판별하기 어렵다.

SIDO, BCP, Mixture of Frames 및 action-conditioned graph dynamics는 확인한 arXiv version을
인용하며 venue acceptance를 추정하지 않는다. 논문 보고 성능은 workspace 재현 결과가 아니다.
위 문헌의 모든 appendix와 code를 완전히 검증한 survey도 아니다.

### Selected question, access and next action

Q16은 **로봇 행동이 만드는 물체 운동 변화를 작게 학습해 접촉 전후 정책 적응에 쓰는 방법**을
시도한다. 자세한 질문·model sketch·대조·예산은
[question record](../questions/interaction-conditioned-motion.md)가 소유한다. 첫 관찰부터 간단한
method attempt를 포함한다. Novel residual 입증 후에만 아이디어를 작성하는 순서를 요구하지 않는다.

공개 DynamicVLA repository의 README를 immutable commit
`bb702465fe3976ac853bc1fbed600668045909f2`에서 읽기 전용으로 확보했다.
Code, DOM data와 checkpoint 링크가 있으나 weight/data나 runtime은 취득·검증하지 않았다.
README의 Isaac Sim 4.5.0 / Isaac Lab 2.2.1 구성은 별도 setup 비용이 있으므로 full DOM
재현을 첫 관찰로 고르지 않았다. 기존 host Isaac 자산을 사용하지 않는다.
Workspace의 pinned ManiSkill PickCube source와 diffusion-policy example 경로를 확인했다.
Dynamic cube construction은 텍스트로 확인했지만 Q16 task와 실행 성능은 아직 없다.
출처·read scope와 작은 README snapshot은
[comparison_sources.json](comparison_sources.json)의 `candidate_replacement_20260923`에 기록했다.

**에이전트 판단:** 가장 중요한 불확실성은 model을 만들 수 있는지가 아니라, 동일 관측·비용에서
단순 feedback보다 배울 가치가 있는 행동 개선을 만드는지다. 부족한 부분이 있더라도 먼저 작은
관찰로 방법을 수정한다. 유망하면 data budget, held-out dynamics/shape, observed pose와 strong
external policy 비교로 발전시킬 수 있다. 현재는 후보 선택이며 기여·가설 승격 판정이 아니다.


## Q16 Policy Adaptation Direction 2026-09-23

### Decision and timeliness

**사용자 의견:** 작은 차이만 남도록 계속 좁히면 주제를 발전시키기 어려우므로, 시의성과
방향성이 보일 때 실제 방법 개발을 진행할 수 있어야 한다. 이를 반영해 Q16은 계속 진행한다.
넓은 방향은 **Predictive Policy Adaptation for Dynamic Manipulation**이며 첫 cube 관찰은
그중 가장 작은 dynamics/제어 구현의 결과로 둔다. 새로운 Q 번호나 최종 paper claim은 만들지 않는다.

**확인한 연구 흐름:** 아래 primary papers는 미래 예측의 활용을 policy steering, 실행 중
보정, 물리 특성 적응과 움직이는 대상 조작으로 확장한다. 이 흐름은 연구 relevance의 근거다.
여러 논문의 존재가 우리 방법의 신규성이나 효과를 보장하는 것은 아니다.

| Primary source와 확인 판본 | 읽은 내용 | 이번 개발에서의 역할 |
| --- | --- | --- |
| [DynaGuide](https://arxiv.org/html/2506.13922v2), v2 2025-11-09 | §3, 실험 개요, §5.1: 별도 dynamics의 예측을 diffusion action 생성에 반영하며 frozen policy를 steering한다. | Policy와 predictor를 연결하는 직접 출발점. Dynamics-guided steering 자체를 새 기여로 쓰지 않는다. |
| [DyWA](https://arxiv.org/html/2503.16806v2), 2025 | §3.3–3.6, §4.3: object-centric state prediction과 최근 observation/action에서 얻은 dynamics context를 함께 활용한다. | 단순 moving-target 외에 물체/접촉 특성 변화와 non-prehensile manipulation으로 확장하는 근거. History adaptation 자체도 기존 원리다. |
| [Feedback World Model](https://arxiv.org/html/2605.15705v1), v1 2026-05-15 | §4–5: 실행 후 관측을 predictor 보정과 action-aware guidance에 사용한다. | Online feedback correction의 직접 비교 대상. 단순 prediction residual을 더했다는 차별성은 주장하지 않는다. |
| [DynamicWAM](https://arxiv.org/html/2608.00793v2), 2026 | Method, §5 protocol: motion history와 운동 정보를 world/action prediction에 연결한다. | 동적 대상과 responsive execution의 시의성. 대규모 joint video-action 학습은 현재 자원 범위의 직접 개발 경로로 선택하지 않는다. |
| [Action-conditioned Face Interaction Graph Networks](https://arxiv.org/html/2509.12151v1), 2025 | Contact-dynamics/MPC 실험과 appendix의 planner 설명을 추가 확인했다. | 접촉 모델과 장기 제어를 연결하는 강한 비교 축. Learned contact dynamics+MPC가 이미 존재함을 유지한다. |

논문 결과는 저자 보고이며 workspace 재현이 아니다. DynamicWAM의 real-robot 비교는 방법별
실행 protocol 차이도 있으므로 특정 module의 순수 효과로 인용하지 않는다. 이 검토에서는
보고 success 수치를 우리 prototype의 예상 성능으로 옮기지 않는다. 2026 preprint의 venue
acceptance를 추정하지 않는다.

### What the first implementation did and did not test

[보존된 결과](../pilot_studies/q16-motion/README.md#results-2026-09-23)는 그대로다.
이번에는 raw metric을 재계산하거나 같은 rollout을 반복하지 않고 source와 compact 결과를
문헌의 method 범위에 대조했다.

| 첫 구현에서 확인한 사실 | 해석과 다음 방법 시도 |
| --- | --- |
| 0.1 s 후 object displacement 하나를 예측했다. | Multi-step contact/transport trajectory를 이용한 정책 적응은 아직 시험하지 않았다. Action sequence와 여러 미래 state를 모델링한다. |
| 후보 행동은 공통 controller 주변 xy 3×3이고 z/gripper와 phase 전환은 공유했다. | Grasp timing이나 3D 접근·운반 전략이 학습 예측으로 바뀌는 비교가 아니다. 학습된 전체 action chunk의 제한된 보정을 시도한다. |
| Phase 3 transport에서 predictor를 사용하지 않았다. | Transport prediction RMSE를 제어 이득으로 해석할 수 없다. 다음 방법은 구간 전체에서 실행되는 base policy를 대상으로 한다. |
| Base behavior는 learned policy가 아닌 규칙 controller였다. | Learned policy가 실행 중 벗어난 상태에 적응하는 질문은 남아 있다. 작은 Diffusion Policy를 기본 정책으로 둔다. |
| 한 cube, 정확한 state, 두 초기 운동 조건에서 모두 성공했다. | 충분한 단순 feedback의 범위는 확인했다. 이를 general dynamic manipulation의 주제 보류 근거로 확장하지 않는다. |

첫 관찰이 무효라는 뜻은 아니다. **에이전트 판단:** 남은 개발 여지가 좁은 exceptional failure
찾기보다 넓다. 작은 multi-step dynamics를 learned policy 실행에 연결하고 과업·물리 조건을
넓혀보는 것이 현재 더 유익하다. 이 판단은 novelty 증명과 구분한다.

### Concrete direction and resource fit

선택한 잠정 방법은 **관측 이력과 예정 action chunk로 object/robot trajectory를 예측하고,
그 예측 및 실제 실행 피드백으로 frozen policy의 chunk를 보정**하는 것이다. 처음에는
명시적 object state를 쓰고, 이후 관측 pose/point-cloud로 입력을 바꿀 수 있다. State-based
효과가 vision/VLA 성능이라는 주장은 하지 않는다.

한 주 정도의 초기 방법 개발을 계획하고 grasp-and-transport부터 시작해 pushing을 추가한다.
이는 기간 종료 때 반드시 이겨야 하는 통과 gate가 아니다. 어느 구성 요소를 수정하고
배울 수 있는지로 다음 투자를 정한다. 비용·단순 대안·실패 사례도 함께 기록한다.
세부 구현 순서와 목표는 [기존 study owner](../pilot_studies/q16-motion/README.md#method-development-2026-09-23)에 둔다.

공식 [DynaGuide repository](https://github.com/MaxDu17/DynaGuide)와
[DyWA repository](https://github.com/jiangranlv/DyWA/)를 읽었다. 전자는 policy/dynamics source를,
후자는 Docker·assets·training 경로를 공개한다. [Feedback World Model project](https://jingliangli.com/Feedback_World_Model/)는
code link를 제공한다. 이 확인은 full runtime/data/checkpoint 재현이 아니다.
기존 pinned ManiSkill의 PushCube source와 Diffusion Policy README를 텍스트로 확인했다.
PushCube의 native goal radius는 0.1 m이며 이를 조용히 좁히지 않는다. 새로운 task variant가
필요하면 별도 이름/목적/metric으로 기록한다. Simulator/source 접근 경로는 있지만 새 policy
학습·pushing runtime은 아직 실행하지 않았다.
