# Robotics Research Scope

Updated: 2026-09-11

## Status

`active_scoping`

Robotics candidate research question 15개를 기록했다. Q12/Q13 Stage 4–5와 후속 비교를 마치고
Q12의 CPU input/schema/coordinate protocol v1을 실제 네 쌍에 실행·독립 검증했다. Input
controls는 통과했으나 physical frame은 미확정이다. Q12는 `feasibility_study`, Q13은
`deferred`, Q14는 reserve다. 이후 실제 네 입력의 CPU reference completion을 실행·독립 검증했다.
Native CUDA parity·물리 연결은 미검증이며 hypothesis와 method 선택은 아직 없다.

## Facts

- Primary research area는 Robotics다.
- 3D Vision은 독립적인 reconstruction 목표보다 robot state estimation,
  decision과 behavior에 기여하는 부차적 enabling area로 다룬다.
- 초기 탐색 관심사는 VLA, robot learning, whole-body control, LLM-enabled
  planning과 reasoning이다. 이 목록은 scope를 제한하지 않는다.
- 연구 기간은 약 6개월이며 IROS 2027 제출을 목표로 한다. IEEE Robotics and
  Automation Society가 게시한 paper submission deadline은 2027-03-01이다.
- 정량 검증과 성능 비교는 simulation 또는 dataset에서 먼저 완료한다.
- Real-robot deployment는 정량 근거가 확보된 뒤 qualitative demonstration을
  얻는 후반 단계로 둔다.
- Foundation model을 새로 학습하거나 무거운 model training을 요구하는 방향은
  피한다.

## Motivation And Expected Significance

특정 architecture나 유행하는 subfield에 먼저 고정하지 않고 Robotics closed
loop에서 중요한 failure, missing capability 또는 evaluation gap을 찾아 6개월
안에 검증 가능한 연구 질문으로 발전시키는 것이 목적이다. 최종 방향은
simulation/dataset의 재현 가능한 정량 evidence와, 가능한 경우 real-robot
qualitative evidence를 연결할 수 있어야 한다.

## Research Boundary

### Included

- planning, reasoning, control, feedback와 failure recovery
- robot learning과 data-efficient adaptation
- VLA의 action representation, memory, latency, feedback와 embodiment transfer
- locomotion, whole-body control과 mobile/loco-manipulation
- downstream robot behavior를 바꾸는 3D perception 또는 spatial state

### Excluded Or Deprioritized

- 새로운 foundation model의 pretraining
- 대규모 compute와 장기간 학습이 핵심 contribution인 방향
- robot behavior와 연결되지 않는 순수 3D reconstruction 성능 경쟁
- simulation/dataset 정량 검증 없이 real-world deployment부터 시작하는 방향
- real-robot result만으로 main quantitative claim을 구성하는 연구 설계

## Evaluation And Deployment Strategy

1. 공개 또는 접근 가능한 dataset, simulator, evaluator와 baseline으로 핵심
   claim을 정량 검증한다.
2. Robustness, generalization, cost와 failure mode를 simulation/dataset에서
   측정한다.
3. 충분한 정량 evidence가 확보된 경우에만 real robot으로 옮긴다.
4. Real-robot 결과는 우선 qualitative validation으로 한정하고, hardware
   motion은 별도 사용자 승인 후 수행한다.

## Literature Source

- Local discovery registry: [`PaperReview`](/home/yoohyun/PaperReview/README.md)
- Machine-readable registry: [`papers.json`](/home/yoohyun/PaperReview/work/sources/papers.json)
- Track synthesis and open questions: [`synthesis/`](/home/yoohyun/PaperReview/synthesis/README.md)
- Reading priority and lineage: [`READING_PLAN.md`](/home/yoohyun/PaperReview/research/READING_PLAN.md)

`PaperReview`는 candidate discovery, prior mapping과 gap cue에 사용한다. Registry
metadata나 synthesis의 `CURATION-SEED`를 최종 사실로 간주하지 않으며, candidate의
novelty, evaluation setting과 artifact availability는 primary paper, appendix,
official code/data와 최신 official source에서 다시 확인한다. `PaperReview`는 이
scope 작업에서 read-only로 사용한다.

2026-09-08 사용자가 지정한 63개 관심 논문의 mapping과 이를 바탕으로 한 Q11--Q15
탐색·비교는 [Policy and geometry search](related_work/policy-geometry.md)가 소유한다.

## Known Resource Constraints

| Resource | Current boundary |
| --- | --- |
| time | 약 6개월 |
| target venue | IROS 2027; paper deadline 2027-03-01 |
| model scale | foundation-scale 또는 heavy training 제외 |
| quantitative evaluation | simulation/dataset 우선 |
| real robot | 후반 qualitative demonstration; 별도 motion 승인 필요 |
| compute/GPU | local RTX 5090 32,607 MiB, 20 CPU와 약 67 GB RAM; 2026-09-06 snapshot에서 405 MiB used, 0% utilization |
| container runtime | 기존 workspace CUDA feasibility는 검증됨; 새 후보별 runtime은 별도 검증 필요 |
| simulator | pre-existing Isaac Sim/Isaac Lab image는 사용·수정·삭제 금지; candidate마다 새 image/environment를 구성 |
| robot embodiment/access | 확인 필요 |
| dataset access | public data 우선; Q10 REASSEMBLE selective ZIP-member retrieval 검증 |
| annotation budget | 필요한 경우 소규모 manual annotation 허용; Q10 v3에서 4 pair 사용 |

미확정 resource는 candidate 비교에서 feasibility risk로 명시하며 임의로 보유한
것으로 가정하지 않는다.

## Candidate Question Registry

| ID | Question | Status | Immediate role |
| --- | --- | --- | --- |
| Q1 | [Success-Predicate Stability](questions/success-predicate-stability.md) | `discontinued` | [Stage 7 disposition](../selection.md#q1--discontinue-2026-09-08); excluded from active execution priority |
| Q2 | [Plan Executability Decomposition](questions/plan-executability-decomposition.md) | `deferred` | direct-prior collision; reformulation needed |
| Q3 | [Physics-Setting Ranking Stability](questions/physics-ranking-stability.md) | `exploratory` | policy/artifact-dependent reserve |
| Q4 | [Task-Relevant Spatial State](questions/task-relevant-spatial-state.md) | `exploratory` | high-overlap 3D route |
| Q5 | [Whole-Body Command Admissibility](questions/wbc-command-admissibility.md) | `deferred` | executable-controller/embodiment blocked |
| Q6 | [Temporal Mismatch Decomposition](questions/temporal-mismatch-decomposition.md) | `exploratory` | asynchronous execution factorization; direct-overlap risk |
| Q7 | [Failure-Source Generalization](questions/failure-source-generalization.md) | `exploratory` | natural versus constructed failure transfer |
| Q8 | [Local Recoverability Coverage](questions/local-recoverability-coverage.md) | `under_review` | repeated audit completed; `refine`, tested grid uninformative |
| Q9 | [Spatial-Memory Refresh](questions/spatial-memory-refresh.md) | `exploratory` | fixed-budget stale-memory update; direct-overlap risk |
| Q10 | [Contact-Outcome Observability](questions/contact-outcome-observability.md) | `discontinued` | [Stage 7 disposition](../selection.md#q10--discontinue-2026-09-08); excluded from active execution priority |
| Q11 | [Contact-Preserving Action Compression](questions/contact-action-compression.md) | `discontinued` | [Stage 7 closure](../selection.md#q11--discontinue-current-route-2026-09-10); bounded current method route ended |
| Q12 | [Reliance on Generated Geometry](questions/generated-geometry-reliance.md) | `feasibility_study` | Four-pair input audit verified; prepare bounded model-loading and independent-completion validation |
| Q13 | [Action-Relevant View Selection](questions/action-relevant-view-selection.md) | `deferred` | Direct-prior overlap and state/value setup cost; draft preserved with re-entry conditions |
| Q14 | [Coordinate-Frame Error Propagation](questions/frame-error-propagation.md) | `exploratory` | geometry reserve; analytic-transform baseline pressure |
| Q15 | [Reward Transfer Across Dynamics](questions/reward-dynamics-transfer.md) | `deferred` | reward-learning route; independent training cost unbounded |

## Comparative Assessment — Initial Stage 3

아래 평가는 초기 candidate 비교의 기록이다. 현재 실행 우선순위는 `Current Decision`을 따른다.

`H/M/L`은 각각 `high/medium/low`다. `related-work overlap`만 H가 더 큰 충돌 위험을
뜻한다.

| Question | significance | empirical access | feasibility | information | resource fit | depth | overlap | rigorous path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 predicate stability | M | H | H | H | H | M | H | H |
| Q2 plan decomposition | H | M | H | H | H | H | H | H |
| Q3 physics ranking | H | M | M | H | H | H | H | H |
| Q4 spatial state | H | M | M | H | M | H | H | M |
| Q5 WBC admissibility | H | L | L | H | L | H | M | M |
| Q6 temporal mismatch | H | M | M | H | M | H | H | H |
| Q7 failure source | H | M | H | H | H | H | H | H |
| Q8 recoverability coverage | H | H | M | H | H | H | H | H |
| Q9 memory refresh | H | L | M | H | M | H | H | M |
| Q10 contact observability | H | M | H | H | H | H | M | H |

### Evidence Behind The Ratings

- **Q1:** 공개 evaluator의 state log만 있으면 재학습 없이 tolerance sweep를 할 수 있어
  접근성과 one-week feasibility가 가장 높다. 반면 metric audit만으로 끝날 수 있어
  scientific depth는 중간이며 SafeVLA-Bench·SIMPLER overlap을 먼저 제거해야 한다.
- **Q2:** ProcWorld의 큰 trajectory denominator와 deterministic validator route가 있어
  resource fit과 negative-result value가 높다. Plan schema와 failure attribution이 실제로
  가능한지는 아직 확인되지 않았고 task-and-motion planning·SIMPACT 충돌 위험이 높다.
- **Q3:** Local RTX 5090과 NVIDIA Docker runtime이 있어 compute fit은 높고 simulator
  result의 ranking validity는 controlled evaluation으로 확장하기 좋다. 그러나 compatible
  frozen policy와 candidate-specific image가 없고, 성숙한 sim-to-real/randomization prior
  때문에 즉시성은 Q1/Q2보다 낮다.
- **Q4:** 3D representation을 downstream utility로 평가하는 질문은 깊이가 있지만 Clio가
  task-dependent granularity를 직접 다룬다. Public graph와 embodied task를 공정하게
  연결하는 denominator도 새로 확인해야 한다.
- **Q5:** VLA/planner--WBC interface의 의미는 크고 local GPU/Docker는 사용할 수 있다.
  하지만 기존 Isaac image는 범위 밖이고 새 simulator, executable controller, command
  support metadata와 compatible embodiment가 미확정이라 pilot을 보장할 수 없어 deferred다.
- **Q6:** temporal factors를 분리하면 insight가 크지만 REMAC이 intra/inter-chunk 원인을
  직접 다루고 checkpoint-level intervention access가 미확인이다.
- **Q7:** 새 FailBench가 natural/constructed source를 함께 제공해 cheap offline study가
  가능할 수 있으나 exact analysis와 release가 아직 미확인이다.
- **Q8:** public simulator state와 policy로 local recovery를 직접 측정할 수 있고 data
  curation으로 확장 가능하다. Perturbation semantics와 mature coverage prior가 위험이다.
- **Q9:** stale spatial memory는 중요한 closed-loop 문제지만 MIF direct overlap과 public
  controllable-memory interface 부재로 empirical access가 낮다.
- **Q10:** contact-rich outcome의 visual ambiguity가 최신 benchmark에서 관찰됐고 lightweight
  probe로 반증 가능하다. synchronized multimodal public denominator 확인이 핵심이다.

## Second-Round Comparative Priority — 2026-09-04

초기 문헌 검토 순서의 기록이며 현재 실행 queue가 아니다.

1. **Q10 Contact-Outcome Observability:** dataset/schema audit만으로 가장 중요한 feasibility
   uncertainty를 줄일 수 있고, bigger VLM보다 simple physical signal이 중요한지 묻는다.
2. **Q8 Local Recoverability Coverage:** robot data와 closed-loop robustness를 연결하며
   public simulator route가 있다. Exact-prior와 perturbation semantics를 먼저 감사한다.
3. **Q7 Failure-Source Generalization:** 매우 최신의 public-corpus opportunity이지만
   FailBench가 exact question을 이미 점유했을 가능성이 높다.
4. **Q6 Temporal Mismatch Decomposition:** scientific depth는 높지만 REMAC/RTC 계열과의
   direct overlap 및 training/runtime cost가 크다.
5. **Q9 Spatial-Memory Refresh:** 중요하지만 MIF와 충돌하고 first executable substrate가
   불명확하다.

## Earlier Provisional Review Priority

1. **Q1 Success-Predicate Stability:** exact predicate-family/rank-reversal question을
   직접 점유한 2024--2026 prior는 이번 audit에서 확인되지 않았다. ManiSkill3의 public
   task/evaluator와 state-replay schema는 확인했고
   Public PPO checkpoint 두 개로 구성한
   [small feasibility study v3](pilot_studies/q1-predicate-stability/manifest_v3.md)를
   고정했다. 당시 uncertainty였던 checkpoint/runtime, matched initialization과
   state relabeling은 아래 Current Decision의 v3 실행에서 검증했다.

Q2는 Embodied Agent Interface, ET-Plan-Bench, ProcWorld와 SIMPACT가 planning failure
decomposition, feasibility와 simulator validation의 핵심 원리를 이미 점유해 selection
decision을 `reformulate`로 기록했다. Q3는 새 environment를 처음부터 구성할 수 있는 실행 reserve다. Q4는
Clio와의 최소 차이를 찾기 전에는 pilot으로 보내지 않는다. Q5는 executable controller와
embodiment가 확인될 때까지 deferred다.

## Current Decision

Q12의 입력 취득·frozen protocol·실제 입력 실행/독립 검증과 후속 준비는
[study README](pilot_studies/q12-generated-geometry/README.md)가 소유한다.

사용자가 선택했던 Q11은 [v3 실행·독립 검증](pilot_studies/q11-action-compression/README.md#v3-verified-results) 후
[사전 중단 규칙에 따른 Stage 7 종료](../selection.md#q11--discontinue-current-route-2026-09-10)를 기록했다.
Registry는 `discontinued`; 현재 method route의 종료이며 broader contact question의 반증은 아니다.
종료된 연구의 compact summary는 [literature/README.md](../../literature/README.md)가 소유한다.

[Reserve 재비교](related_work/policy-geometry.md#reserve-reassessment-2026-09-10) 결과
Stage 4–5 순서는 **Q12 → Q13**이었다. Q12의 [source/assumption 검토](questions/generated-geometry-reliance.md#stage-5-assessment-2026-09-10)와
Q13의 [source/assumption 검토](questions/action-relevant-view-selection.md#stage-5-assessment-2026-09-10)를 완료했다.
[후속 비교](../selection.md#q12q13-measurement-selection-2026-09-10)에서 Q12 입력/좌표 검증
준비를 선택하고 Q13을 `deferred`로 두었다. 이후 Q12 입력 취득과 CPU protocol 고정을 완료했고,
실제 네 쌍의 검사를 독립 검증했다. 이후 checkpoint strict loading·synthetic CPU reference
검증을 마쳤고, [고정된 completion protocol](pilot_studies/q12-generated-geometry/model/README.md)을
실제 네 입력에 실행·독립 감사했다. 다음은 native CUDA parity와 physical linkage를 확보하는
경로의 비용·정보 가치 비교다. 두 조건은 미검증이다.
Q14는 exploratory reserve, Q15는 deferred다. Hypothesis/experiment는 미선택이다.
Q8은 `under_review` / `refine`이며 재진입 조건 전에 실행하지 않는다. 실행 중인 study는 없다.

다음 기존 기록은 이 후보들이 비교 대상으로 남은 배경이며 실행 재개를 뜻하지 않는다.

Broad Robotics scope와 [research context](context.md)를 바탕으로 candidate question
5개를 만들고 Stage 3 기준으로 비교했다. Q2는 `reformulate` 후 `deferred`, Q1은
preliminary literature review와 evaluator/schema feasibility assessment를 완료했다.
[Cross-scope Stage 7 decision](../selection.md)은 Q1에 `repeat feasibility study`를
선택했다. 당시에는 pinned study를 실행하지 않아
`feasibility_study`를 유지했다. 어떤 question도 아직 `ready_for_hypothesis`로
선택되지 않았다.

사용자 판단에 따라 Q1 실행에 바로 commit하지 않고 Stage 1--3 buildup을 한 차례 더
진행했다. [Second-round frontier scan](related_work/frontier-scan-2.md)에서 Q6--Q10
정식 candidate record를 만들고 기존 Q1과 비교했다. Q10과 Q8의 preliminary literature
review를 완료했다. Q10은 [REASSEMBLE-backed public route](related_work/q10-contact-outcome-observability.md)가
확인됐지만 generic multimodal fusion claim은 점유됐고, Q8은
[CFNBC와의 높은 overlap](related_work/q8-local-recoverability-coverage.md) 때문에 frozen-policy
physical-state return-probability diagnostic으로 좁혔다. 두 후보 모두 아직 hypothesis로
선택하지 않았다.

Stage 5 assumption/risk analysis는 각 candidate record에 완료했다. Q10의 first risk는
[matched usable multimodal denominator](questions/contact-outcome-observability.md#q10-a-matched-usable-denominator),
Q8의 first scientific risk는
[task-preserving physical perturbation](questions/local-recoverability-coverage.md#q8-b-task-preserving-physical-perturbation)이다.

| candidate | source-level support | decisive unresolved risk | cheapest first measurement | current priority |
| --- | --- | --- | --- | --- |
| Q8 | public checkpoint/runtime and pre-contact fixture verified | all-pass profile, scalar-success identity, mid-demo restart and full zero-control limits | distinct target/data-linked policy/restore reformulation | refine; no same-grid expansion |

Public data를 우선하고 필요한 경우 소규모 manual annotation만 허용한다는 기존 resource
boundary를 유지한다. Q8 반복 검증과 Q1 CUDA protocol 실행은 각각 별도 evidence로 보존한다.
Stage 7 decision의 question별 처분과 원본 artifact 경로는
[selection record](../selection.md)가 소유한다.

## User Decisions Still Needed

- 접근 가능한 robot embodiment와 센서
- 새로 구성할 simulator 후보와 허용 가능한 setup 시간
- 소규모 manual annotation의 총 시간/수량 상한
