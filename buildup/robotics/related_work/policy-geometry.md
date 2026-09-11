# Policy, Geometry and Action: Candidate Search

Updated: 2026-09-10

문헌 검토는 **Q12 → Q13** 순으로 진행했으며 Q14는 reserve다.
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
