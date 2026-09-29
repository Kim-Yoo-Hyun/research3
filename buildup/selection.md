# Research Question Selection

Updated: 2026-09-28

## Decision Boundary

이 문서는 [`docs/buildup.md`](../docs/buildup.md)의 Stage 7 비교·선택 판단을 누적한다.
아래 과거 결정은 그 당시의 근거와 판정을 보존하며 현재 실행 대기열이 아니다.
현재 판단은 [Q17 선택](#q17-selection-2026-09-28)이다. Q17은 제한된 첫 관찰을 위한
탐색 질문이며 formal hypothesis 또는 검증된 방법은 아니다. Q16의 현재 2D 방법 경로는
`deferred`이며, 넓은 질문의 반증은 아니다. CD5는 사용자 요청으로 실행을 보류했다.
최신 작업은 [TODO](../TODO.md), 개별 관찰의 근거는 해당 question/study owner를 따른다.

## Entry-Criteria Comparison

`MET`은 현재 문서와 접근 가능한 artifact로 조건을 충족함을, `NOT MET`은 현재
formulation으로 조건을 충족하지 못함을 뜻한다. 이는 final novelty 또는 paper-level
admission 판정이 아니다.

| # | Entry criterion | Q1 Success-Predicate Stability | CD4 Counterfactual Failure Attribution | CD1 Intervention-Value Calibration |
| --- | --- | --- | --- | --- |
| 1 | one-sentence problem or phenomenon | `MET` — 같은 rollout에서 predicate 선택이 policy ordering을 바꾸는지 묻는다. | `MET` — diagnosed step의 correction effect가 recovery를 예측하는지 묻는다. | `MET` — detector ranking과 cost-adjusted intervention utility ordering의 일치 여부를 묻는다. |
| 2 | facts/source claims separated from explanation | `MET` — question record에서 세 범주가 분리돼 있다. | `MET` — direct-prior facts와 robotics residue inference가 분리돼 있다. | `MET` — prior claims와 multi-action residue inference가 분리돼 있다. |
| 3 | accessible data, benchmark, evaluator or study design | `MET` — pinned ManiSkill3, `PickCube-v1`, 두 checkpoint와 fixed study design이 있다. | `NOT MET` — original agent setting은 direct prior이고, robotics residue의 valid local-intervention substrate가 없다. | `NOT MET` — 같은 state에서 retry/replan/defer outcome을 비교할 public denominator가 없다. |
| 4 | simplest baseline or counterexample | `MET` — official predicate, continuous margin과 tolerance sweep가 정의돼 있다. | `MET` — random/neighbor/earliest correction과 CAR replay가 정의돼 있다. | `MET` — calibrated threshold, analytic expected-value rule과 tabular lookup이 정의돼 있다. |
| 5 | critical assumption and disconfirmation | `MET` — state reconstruction, semantic variants와 margin-distribution 조건이 명시돼 있다. | `MET` — restore, intervention locality와 oracle recovery 조건이 명시돼 있다. | `MET` — replay access, ordering reversal과 simple-rule residual 조건이 명시돼 있다. |
| 6 | feasibility evidence or documented assessment | `MET` — source/schema/license와 exact 16-rollout protocol을 문서화했다. | `MET` — direct collision과 robotics substrate 부재를 negative assessment로 문서화했다. | `MET` — broad collision과 multi-action denominator 부재를 negative assessment로 문서화했다. |
| 7 | negative-result decision | `MET` — stable ranking이면 종료하고 measurement failure이면 refine한다. | `MET` — oracle recovery나 replay validity가 없으면 종료한다. | `MET` — metric ordering이 일치하거나 simple lookup이 충분하면 종료한다. |
| 8 | draftable intervention, effect and evaluation target | `MET` — frozen predicate grid, pairwise sign change와 fixed denominator가 있다. | `NOT MET` — robotics intervention의 물리적 locality와 denominator가 고정되지 않았다. | `NOT MET` — intervention set, cost unit와 counterfactual outcome source가 고정되지 않았다. |

## Stage 7 Decisions

### Q1 — `repeat feasibility study`

Q1은 8개 entry criterion을 모두 충족해 hypothesis formulation에 들어갈 수 있는
형태는 갖췄다. 그러나 핵심 phenomenon은 아직 관찰되지 않았고, checkpoint load,
matched initialization, immutable state recording과 independent relabeling도 실행으로
검증되지 않았다. 이미 고정한 16-rollout study가 이 uncertainty를 낮추는 가장 싼
측정이므로 지금 `select for hypothesis formulation`하지 않는다.

- status: `feasibility_study` 유지
- next evidence: [manifest v3](robotics/pilot_studies/q1-predicate-stability/manifest_v3.md) 실행 결과
- next decision: manifest의 사전 정의된 branch에 따라 `refine`, `discontinue` 또는
  다시 `repeat feasibility study`
- prohibition: 8 trajectories per policy에서 ordering change가 나와도 곧바로 hypothesis로
  넘기지 않는다.

### CD4 — `reformulate`

원래의 domain-general single-step correction plus suffix replay question은 direct prior와
충돌한다. Continuous-control robotics에서 physical intervention validity와 attribution
identifiability라는 다른 설명 가능성은 보이지만, intervention과 denominator가 아직
정의되지 않아 현재 candidate를 hypothesis로 넘기지 않는다.

- status: `deferred`
- reactivation condition: physically local intervention, deterministic state restore와
  evaluator를 함께 제공하는 public continuous-control substrate 확인
- new-record rule: 위 조건을 충족하면 original CD4의 threshold나 denominator를 바꾸지
  않고 별도 revised candidate question으로 기록

### CD1 — `refine`

Calibration이 decision utility를 보장하지 않는다는 broad question은 recent prior와
겹친다. 남은 multi-action sequential question은 과학적으로 명확하지만, retry/replan/defer
결과를 동일 state와 cost unit에서 비교할 공개 substrate가 없다. 현재는 artifact가 없는
상태에서 가설을 구체화하지 않는다.

- status: `deferred`
- refinement target: 하나의 named sequential system, finite intervention set, common cost
  unit, state restore와 counterfactual outcome evaluator
- reactivation condition: 위 네 요소를 공개 artifact로 고정할 수 있음
- stop rule: accessible artifact가 TDQC의 early stop/action search만 재현한다면 종료

## Selection Result — 2026-09-04

이번 비교에서는 어떤 candidate도 `ready_for_hypothesis`로 선택하지 않는다. Q1만
실행 가능한 low-cost uncertainty reduction 경로를 가지므로 active feasibility candidate로
남긴다. CD4와 CD1은 각각 `reformulate`, `refine` 판정을 기록하고 보류한다.

2026-09-04 사용자 판단으로 research buildup을 더 확장하기로 했다. 따라서 이 결정은
Q1에 대한 exclusive topic commitment가 아니며, second-round candidate set의 Stage 3
비교 전에는 Q1 실행 우선순위를 확정하지 않는다.

이 결정 과정에서 `PaperReview`를 수정하지 않았고, simulator, checkpoint, container 또는
hardware를 실행하지 않았다.

## Q10 — `discontinue` (2026-09-08)

### Decision Scope

- Frozen terminal-state/force **summary-only probe route**: `discontinue`.
- [현재 Q10 candidate](robotics/questions/contact-outcome-observability.md)의 연구 진행:
  `discontinue`; status를 `discontinued`로 바꾼다. Active Stage 6 작업을 종료하며
  hypothesis로 넘기지 않는다.
- 더 넓은 “RGB 외 어떤 signal이 contact outcome을 식별하게 하는가?”라는 학술 질문:
  **미검증**. 모든 physical signal, temporal representation 또는 RGB 대비 정보 증가가
  부정됐다고 해석하지 않는다.
- 새로운 question으로의 `reformulate`: 현재는 선택하지 않는다. Candidate를 유지할 만한
  새로운 explanation이나 observable phenomenon이 확인되지 않았기 때문이다.

이는 현재 resource-bounded formulation에 대한 연구 선택이다. Wider question의 불가능성
증명이나 Robotics scope 전체의 종료가 아니다. Q10-D의 실용적 경로인 “simple physical
summary로 추가적인 예측 가치를 얻는다”는 계획이 고정한 시험에서 지지되지 않았고,
v6가 미리 정한 negative branch를 이행한다. 원래의 RGB-relative question까지 직접 반증했다고
말하지 않는다.

### Evidence And Interpretation

**Facts:** [v6 result and verified artifacts](robotics/pilot_studies/q10-contact-observability/README.md#v6-result--2026-09-08)
에서 state+force probe의 nested macro BA는 0.5791, 동일 fold의 v5 selection procedure는
0.7239다. 차이의 recording-bootstrap interval은 [-0.2299, -0.0347]이다. State/force/
state+force 어느 probe도 v5와 duration baseline 모두에 대한 사전 고정 useful-gain 조건을
통과하지 못해 `NO_USEFUL_SUMMARY_GAIN`으로 판정했다. 이 branch는 summary-only route
중단 또는 새 evidence에 근거한 reformulation을 요구한다.

**Claim boundary:** RGB-only matched probe는 수행하지 않았다. Physical rule이 포화했다고
입증한 것도 아니다. Five-recording exploratory test와 one-recording remove 결과로
generality를 주장할 수 없다. Peak-only test 결과를 보고 primary group을 바꾸거나 nested
evaluation을 test evaluation으로 대체하지 않는다. 상세 metric·오류·runtime의 owner는 위
study README이며 여기에는 결정에 필요한 근거만 남긴다.

**Agent inference:** 실패 label이 적고 C/threshold 선택이 불안정한 것은 plausible explanation이다.
그러나 그것이 label 오류, sensor의 본질적 한계 또는 특정 physical failure 원인이라는
증거는 없다. 따라서 instability 자체를 새로운 measurement contribution으로 명명하거나
더 큰 모델의 필요성으로 바꾸지 않는다. 현재 candidate를 계속 유지할 근거가 부족하며,
사전 고정 negative branch를 따르는 것이 적절하다.

### Remaining Uncertainties Are Not New Positive Evidence

| Unresolved item | Could a bounded study add information? | What it would and would not establish | Decision now |
| --- | --- | --- | --- |
| Outcome-label construct validity | 가능: official label rule과 사전 고정 segment의 blinded review | 반복되는 label contradiction이 확인되면 target-validity question을 만들 수 있다. 현재 v3 소수 RGB 판단 오류는 label contradiction을 보여주지 않는다. | 새 contradiction evidence가 없으므로 label-reliability question으로 자동 재명명하지 않는다. |
| Matched RGB versus physical evidence | 가능: 고정된 동일 population에서 capacity-matched RGB-only 비교 | 원래 question을 직접 시험하는 누락된 비교다. 다만 RGB가 약하다는 것만으로 physical summaries가 충분하거나 새 method가 필요하다고 결론낼 수 없다. | 현재 negative summary route를 계속하기 위한 자동 후속 실험으로 채택하지 않는다. |
| Recording coverage and transfer | 가능: 별도 label-blind recording population과 group-held-out evaluation | 추정 안정성과 transfer를 점검할 수 있다. 더 많은 data가 gain을 만들어 준다는 보장은 없고, 기존 nested negative result는 바뀌지 않는다. | 단지 결과를 개선하기 위한 denominator 확장을 시작하지 않는다. |
| Temporal information lost by summaries | 이론적으로 가능하지만 현재 case-level 증거가 없다 | 성공/실패를 가르는 구체적 시간 구조가 관찰돼야 기존 summaries가 왜 놓치는지 설명할 수 있다. | Temporal model/새 architecture로 확대하지 않는다. |

위 측정들이 불가능해서 종료하는 것은 아니다. 현재 route의 사전 고정 kill test가 negative이고,
남은 측정 중 어느 것도 이미 관찰된 새로운 설명을 확인하는 단계는 아니므로 이번 selection에서
`repeat feasibility study`를 선택하지 않는다. 미래에 재검토하려면 **새 case-level observation 또는
새 검증된 substrate**가 무엇인지 먼저 제시하고, 원래 v6의 metric/threshold/denominator를
변경하지 않는 별도 question으로 비교한다. 이는 오늘 승인·예약한 후속 실험이 아니다.

### Entry To Hypothesis Formulation

| # | Criterion | Assessment |
| --- | --- | --- |
| 1 | One-sentence problem | `MET` — contact outcome의 최소 추가 관측 신호라는 질문은 명확하다. |
| 2 | Facts and explanation separated | `MET` — source claims, observed negative results와 제안된 원인을 구분했다. |
| 3 | Accessible evaluation target | `MET` — public synchronized segments와 고정된 outcome denominator가 있다. |
| 4 | Simplest baseline/counterexample | `MET` — prior, deterministic rules와 regularized summary probes를 정의·실행했다. |
| 5 | Critical assumption/disconfirmation | `MET` — candidate assumptions와 v6의 negative branch가 사전에 고정됐다. |
| 6 | Feasibility evidence/assessment | `MET` — v1--v6와 validation audit의 검증된 artifact가 있다. |
| 7 | Negative-result decision | `MET` — summary-only route 중단을 이행하고 범위를 한정한다. |
| 8 | Draftable intervention/effect/target | `MET in form` — 같은 RGB evaluator에 physical evidence를 추가하면 group-held-out outcome BA가 증가한다는 반증 가능한 문장은 작성 가능하다. 그 효과는 아직 관찰하지 않았다. |

Criterion 8에 positive result를 필수조건으로 추가하지 않는다. Entry 조건은 hypothesis를
작성할 수 있는 형식적 최소요건이고 selection은 연구 투자 판단이다. Q1의 선행 결정처럼
조건을 충족해도 반드시 승격하지 않는다. 여기서는 최종 novelty나 architecture 부재 때문이
아니라 **실행한 bounded route의 사전 고정 negative branch와 evidence-backed reformulation
부재**를 이유로 `select for hypothesis formulation`하지 않는다.

### Status, Priority And Preservation

- Q10은 active execution priority에서 제외한다. 종료된 연구의 compact summary는
  [literature/README.md](../literature/README.md)가 소유한다.
- Q8은 `under_review`, Q1은 기존 protocol을 보존한 paused `feasibility_study`다.
  어느 쪽도 이번 결정만으로 Stage 6 실행 대상으로 선택하거나 재개하지 않는다.
- 다음 작업은 **Q8/Q1의 한정된 재비교**다. Q8의 task-preserving perturbation/independent
  recovery target이 source 수준에서 정의 가능한지와 Q1의 pinned study가 제공하는 정보량을
  같은 기준으로 비교해 다음 Stage 6 대상을 결정한다. Q8을 자동 승계자로 취급하지 않는다.

## Q8/Q1 — Stage 6 Selection (2026-09-08)

### Decision

**다음 Stage 6 후보는 Q1 Success-Predicate Stability다.** Q8은 `under_review`와
Stage 7 `refine`을 유지한다. Tested PPO/pre-contact grid는 uninformative하여 현재
formulation 그대로 확대하지 않는다. 어느 후보도 hypothesis나 paper claim으로 승격하지 않는다.

이 결정은 사용자 요청에 따라 Q8의 source/문헌/construct 감사와 두 protocol의 반복
Docker 검증까지 완료한 뒤 내린 에이전트 판단이다. Q1의 novelty가 확정됐다는 뜻은 아니다.

### Evidence and repeated challenges

- [Q8 study](robotics/pilot_studies/q8-recoverability/README.md#final-verified-results): 새 Docker에서
  두 public PPO checkpoint와 1,000-demo schema를 확인했다. V1+V2 restore 비교 1,800회와
  public demo transition 27회를 수행했다. Fresh scene + action prefix로 next-step restore를
  복구했지만 arbitrary stored-demo restart는 확립하지 못했다.
- V2 fixed 312 proposals 중 144가 geometry/next-step 조건을 통과했고 모두 성공했다.
  Full continuation zero-control까지 통과한 98개 (89 nonzero, 9 anchor groups)도 3 process
  모두 성공했다. 반복은 independent statistical sample이 아니다. 4/13 zero-control groups와
  demo middle-state transition 18/18은 기존 1e-5 tolerance를 넘었으며 기준을 완화하지 않았다.
- [Q8 literature/construct audit](robotics/related_work/q8-local-recoverability-coverage.md#repeated-audit--2026-09-08):
  basin stability, CCIL, CFNBC, Demo-SCORE, SEDS와 SAFE까지 압력을 확인했다. Fixed-horizon
  success를 scalar recovery로 쓰면 동일-budget empirical success estimate와 수학적으로 같다.
  Separate rollout만으로 novelty나 distinct predictive information이 생기지 않는다.
- Q1의 [v3 manifest](robotics/pilot_studies/q1-predicate-stability/manifest_v3.md)는 결과 전 고정된
  16 trajectories / 96 labels로 measurement와 pairwise ordering instability를 검사할 수 있다.
  현재는 CPU checkpoint 실행 가능성만 보강됐고, CUDA protocol 자체를 실행한 것은 아니다.

### Stage 3 comparison after validation

| Criterion | Q8 | Q1 |
| --- | --- | --- |
| Significance | physical recovery/data quality 연결은 중요하지만 이번 data-coverage 연결은 미확립 | benchmark conclusion의 evaluator dependence를 직접 묻는다 |
| Empirical access | policy/geometry fixture 실행됨; true training-data coverage 및 demonstration restart 부족 | 두 checkpoint 접근/CPU 실행 확인, evaluator constituents 공개 |
| Feasibility | fresh-prefix route 가능; profile와 independent target 재정의 필요 | frozen small-study가 구체적; CUDA setup/matched initialization 남음 |
| Informational value of next run | 같은 grid 확대는 all-pass/construct identity를 반복할 위험 | 16개 trajectory로 frozen label/ordering 변화를 직접 판정 가능 |
| Resource fit | 작은 fixture는 충분히 저렴함; 새로운 policy/data route 비용은 미산정 | 재학습 없는 bounded rollout/relabeling; 기존 GPU 자산 사용 불필요 |
| Scientific depth | 잠재력은 높지만 failure-derived principle 미발견 | metric audit에 머무를 위험은 여전; rank reversal 원인과 최소 보고 항목까지 가야 함 |
| Related-work overlap | basin/success prediction/data curation 모두 높은 충돌 압력 | SafeVLA-Bench/SIMPLER와 인접; exact predicate-family counterexample의 차이를 검증해야 함 |
| Rigorous extension path | distinct perturbation target + equal-cost outcome control + data-linked policy를 먼저 확보 | frozen trajectories, geometric margin, temporal persistence, 이후 다수 policy/task로 확장 가능 |

Q1의 nearest primary sources를 이번 비교에서 다시 확인했다:
[SafeVLA-Bench](https://safevla.org/)는 native success predicate를 보존하고 safety specification을
추가하며, [SIMPLER](https://simpler-env.github.io/)는 sim/real ranking consistency를 다룬다.
이 구분은 preliminary scope boundary이며 exhaustive novelty proof가 아니다.

### Immediate Stage 6 and stop conditions

Q1 v3을 다음 작업으로 배치한다: 별도 project-specific CUDA-capable Docker recipe, named
artifact checksum, matched cube/goal/robot initialization, immutable 16 trajectories와 independent
96-label reconstruction. Q8 CPU image/seed 결과로 v3을 대체하거나 manifest를 수정하지 않는다.
측정 불가/initialization 불일치면 `refine`; 전체 frozen grid에서 label 변화가 없으면
uninformative로 판정한다. 변화가 있어도 8 episodes/policy로 hypothesis에 바로 진입하지 않는다.

Q8 재진입에는 training-data-linked frozen policy와 valid demonstration restart, 기존 성공률과
구별되는 perturbation-transfer 질문 및 equal-rollout-budget control이 필요하다. 더 큰 radius나
새 seed를 탐색해 실패만 확보하는 것은 재진입 근거가 아니다. Q10은 종료 상태를 유지한다.

## Q1 v3 — `refine` (2026-09-08)

### Evidence

[Q1 v3 study](robotics/pilot_studies/q1-predicate-stability/README.md#verified-results)를 frozen
protocol 그대로 새 CUDA Docker에서 실행했다. 두 public checkpoint가 load됐고, 실제 평가
시작 state 8쌍이 actor/articulation까지 정확히 일치했다. 16 trajectories의 96 labels와
800 official step labels를 raw state에서 독립 재구성했다. Measurement feasibility는 supported다.

하지만 20/25/30 mm와 once/end의 여섯 조건 모두 PPO-EE 4/8, PPO-Joint 8/8이었다.
Label이 달라진 trajectory, sign change와 strict reversal은 모두 0이다. Frozen branch는
`NO_LABEL_CHANGES_UNINFORMATIVE`다. 상세 table과 case-level evidence는 study README가 소유한다.

### Decision

Q1을 `under_review` / **`refine`**으로 돌리고 현재 two-policy/PickCube route의 확대를
중단한다. Hypothesis formulation으로 선택하지 않는다. 동일 조건 반복을 정당화할 미해결
measurement uncertainty가 없으므로 `repeat feasibility study`를 자동 선택하지 않는다.

이 sample의 성공은 가장 엄격한 거리 조건 안쪽에 있고, 실패는 큰 거리 또는 robot motion
조건에 걸려 있어 frozen grid가 다른 판단을 만들지 못했다. 이는 informative boundary
population에 관한 초기 가정이 이 sample에서 지지되지 않았다는 의미다. Q1의 일반적
불가능성이나 전체 benchmark ranking 안정성을 증명한 결과는 아니다.

### Next work

다음 TODO는 Q1 formulation/population의 재정의 근거를 bounded audit하는 것이다. Current
negative diagnosis, task semantics와 public artifact metadata에서 새로운 observable question을
정당화할 수 있는지 검토한다. Outcome을 보고 threshold/seed를 조정하거나 reversal이 나는
pair만 고르는 방향은 피한다. 새 route가 없으면 Q1을 `discontinue`한다.

Q8은 이전 `refine`, Q10은 `discontinued`를 유지한다. 현재 즉시 실행 대상으로 선정된
추가 Stage 6 study와 active hypothesis는 없다.
- Runtime, dataset, cache, images, logs와 원본 study artifact는 삭제·이동·수정하지 않는다.
  재현 명령은 study README에 남고, 여기서는 추가 download/annotation/model 실행을 시작하지 않는다.
- 이번 판단에는 새 문헌 발견이나 외부 source의 최신성을 주장하지 않는다. 기존 frozen
  evidence와 repository workflow를 검토한 결과다. 실제 source audit은 다음 비교 작업이다.

## Q1 — `discontinue` (2026-09-08)

### Completed review

V3 뒤 요구했던 [formulation/population audit](robotics/related_work/q1-artifact-schema.md#bounded-refinement-audit--2026-09-08)를
완료했다. 기존 실패 진단, pinned task source, public artifact tree와 열 개 metadata 문서,
가까운 primary work를 검토했다. 세부 source/hash/count는 해당 audit와 receipt가 소유한다.

### Decision and boundary

**현재 Q1 formulation과 active route를 `discontinue`한다.** V3는 measurement feasibility를
확인했지만 suspected label/rank sensitivity를 관찰하지 못했고, 이번 한정된 검토에서도
task 의미에 근거한 specification-equivalence family와 informative population을 함께
정당화하지 못했다. 후속 checkpoint가 없어서 내린 결정은 아니다.

Checkpoint가 있는 다른 task의 실행은 가능하다. 그러나 임의 tolerance 확대, static 조건
제거, 성공 사례만 저장된 demonstration 비교 또는 task sweep만으로는 원래 질문의 미해결
가정을 해소하지 못한다. Once/end, safety, progress와 numerical validity는 구별되는 질문이며
새 설명과 평가 대상을 정리하기 전에 Q1의 positive finding으로 바꾸지 않는다.

이 판단은 Q1의 보편적 불가능성이나 benchmark 전체의 ranking 안정성을 뜻하지 않는다.
새 task-grounded specification uncertainty 또는 별도의 observed measurement failure가
구체화되면 comparable unfiltered population과 함께 새로운 candidate 비교로 돌아올 수 있다.
Current formulation을 유지하기 위한 추가 실행, v4 protocol과 hypothesis 승격은 선택하지 않았다.

### Next work and preservation

다음 TODO는 사용자가 선택한 Robotics scope 안에서 남은 후보와 source에서 나온 별도
질문을 포함한 3--5개 후보를 Stage 2--3 기준으로 다시 비교하는 것이다. Observable question,
simplest baseline, 첫 검증의 정보량과 resource fit을 우선하고 상위 1--2개만 Stage 4--5로
보낸다. 이번 turn에서는 그 비교 자체를 수행하거나 다음 Stage 6를 미리 선택하지 않았다.
Q8은 `under_review` / `refine`으로 남고 자동 승계하지 않는다.

종료 요약은 [literature/README.md](../literature/README.md)가 소유한다. V3의 manifest,
code, outputs와 checksum bundle은 그대로 보존했다. 이번 작업은 read-only source/metadata
audit이며 새 policy evaluation, dataset HDF5/checkpoint download, GPU workload, artifact
삭제·이동은 없었다. Robotics scope 자체는 계속 active다.

## Interest-Guided Comparison (2026-09-08)

사용자가 지정한 63개 관심 논문과 PaperReview를 읽기 전용 discovery source로 사용해
Q11--Q15를 만들고 기존 후보와 Stage 2--3 기준으로 비교했다.
[Authoritative comparison](robotics/related_work/policy-geometry.md#stage-3-comparison)이
source claims, artifact limits, controls와 상대 평가를 소유한다.

**다음 Stage 4--5 검토는 Q11 Contact-Preserving Action Compression, Q12 Reliance on
Generated Geometry 순서다.** 전자는 작은 codec/control 진단으로 시작할 수 있다는 점,
후자는 사용자의 geometry/policy 관심과 직접 연결된다는 점에서 우선한다. 둘 다 nearest
prior와 simple controls 뒤의 차이는 미확정이다. Q13/Q14는 exploratory reserve,
Q15는 training cost 때문에 deferred로 둔다.

이 결정은 새 research question의 검토 순서이며 Stage 7의 `select for hypothesis formulation`
또는 Stage 6 실행 대상 선정이 아니다. 최종 method, paper claim, 학습/실행 protocol은 선택하지
않았다. 원래 Q1/Q10 처분과 Q8의 refine 경계는 유지하며 자동 승계하지 않는다.

## Q11 User Selection and Stage 4--5 (2026-09-08)

사용자가 Q11로 진행하도록 선택했다. Q11은 단일 active buildup question이며 Q12는 reserve다.
[Q11 authoritative record](robotics/questions/contact-action-compression.md)가 nearest-primary
comparison, source receipts, simple controls, assumption branches와 Stage 6 준비 초안을 소유한다.

**판정:** Stage 4--5 완료; 작은 measurement-readiness study를 다음 작업으로 선택한다.
OAT의 reconstruction/policy-utility 구분, SA-VLA의 state-conditioned decoding,
MoEActok의 skill quantization과 FASTer의 physical grouping 때문에 일반 tokenizer 제안은
차별성이 부족하다. Contact-transition-localized error가 simple controls 뒤에도 남는지는
미검증이다. Source-level public route는 있으나 원본 replay와 event denominator는 아직 없다.

다음 Stage 6는 새 Q11 Docker에서 StackCube-v1 8개 고정 seed의 generation/replay 및 codec
경로를 검증하는 것이다. Runnable protocol/hash는 실행 전에 고정한다. 결과가 유효해야
held-out physical pilot으로 나아간다. 이는 Stage 7 hypothesis selection이나 method 확정이 아니다.
이번 작업에서 runtime/학습/대형 data·checkpoint download와 기존 asset 삭제는 없었다.

## Q11 Measurement Readiness (2026-09-08)

[Q11 study](robotics/pilot_studies/q11-action-compression/README.md) completed under frozen v1:
`READY_FOR_CONTROLLED_PILOT`. Original full replay, independently reconstructed labels and FAST
codec-path accounting are valid on the fixed readiness population. No compressed action was
physically executed, so the contact-specific scientific assumption remains untested.

Next: freeze an independent population, rate/error matching and simple controls for the physical
pilot. Keep Q11 `feasibility_study`; this is not `select for hypothesis formulation`. Q12 remains
reserve; Q1/Q10 dispositions and Q8 refine boundary are unchanged. Raw artifacts are preserved.

## Q11 Controlled Pilot Preparation (2026-09-08)

[Q11 v2 protocol and execution contract](robotics/pilot_studies/q11-action-compression/README.md#controlled-physical-pilot-v2-preparation)
is frozen before new calibration/held-out data. The next action is the prepared physical pilot,
not another topic search. New Docker and synthetic preflight passed; no v2 simulator episode
or physical compression outcome has been observed. V1 evidence and source freezes are unchanged.

Separate equal-cost codec comparison from equal-energy arm-error localization. Report unsupported
rate/error pairs and missing noncontact windows; do not change the grid or denominator to retain
a claim. Q11 stays `feasibility_study`; no Stage 7 hypothesis selection or final method claim yet.


## Q11 Controlled Pilot Execution (2026-09-08)

The frozen [v2 pilot](robotics/pilot_studies/q11-action-compression/README.md#v2-verified-results)
completed and passed separate read-only Docker audit. The protocol decision is
`INCOMPLETE_CODEC_SUPPORT`: Uniform has no feasible calibration byte support. Available
codec outcomes change with scaling; exact gripper preservation leaves aggregate success counts
unchanged but reverses two joint-FAST cases in opposite directions. No eligible grasp/release
localization pair changes success between event and noncontact injection. No non-reference
control satisfies both frozen rate and MSE matching tolerances.

This is completed Stage 6 evidence, not a Stage 7 continuation/termination decision. Next review
must assess the unsupported comparisons and absent localized signal before deciding whether a
grounded refinement exists. No grid expansion, new training or hypothesis admission has occurred.
Q11 remains `feasibility_study`; Q12 remains reserve.


## Q11 — refine (2026-09-08)

**Stage 7 decision: `refine`; registry status `under_review`.** The next work is one bounded
revision of the observable comparison, not hypothesis formulation or another topic search.
Q11 remains the user-selected direction; Q12 remains reserve. No new method is selected.
The [v2 study and support audit](robotics/pilot_studies/q11-action-compression/README.md#stage-7-support-audit-2026-09-08)
own all numerical results, raw-data provenance, grid inventory and commands.

### Evidence and interpretation

| Review target | Facts | Stage 7 interpretation |
| --- | --- | --- |
| Measurement / denominator | Calibration 8 and held-out 16 originals all completed and passed two replays; 80 codec and 42 localized rollouts independently verified | Measurement is usable; `repeat feasibility study` to repair the recorder is not justified. These are episode denominators, not 194 independent task draws. |
| Codec support | Uniform unavailable under the frozen calibration cap; no executed non-reference method jointly matches held-out rate and MSE | `INCOMPLETE_CODEC_SUPPORT` is a support flag, not a scientific rejection of contact sensitivity or an observed Uniform failure. |
| Simple controls | Quantile FAST succeeds on every held-out episode; exact gripper preserves total success counts but flips two joint-FAST cases oppositely; Linear changes both error structure and magnitude | Do not claim gripper irrelevance, matched-cost superiority or a contact-specific error principle. Correct scaling is a strong existing baseline. |
| Localization | Event/free final success agrees for every eligible pair; reference residual comes from the successful quantile codec | No positive diagnostic signal. The null concerns this natural residual, these windows and the original horizon; it neither establishes equivalence nor localizes the failures of the joint-normalized codec. |
| Concrete refinement opportunity | An already evaluated calibration Linear point, 6-bit/3-knot, meets symmetric rate/MSE overlap but exceeds the original strict cap | Distinguish a hard-budget claim from an approximately rate-matched comparison. The point is not a hidden v2 result and cannot replace the original selected control. It is a specific design option, not justification to enlarge the grid. |
| Scientific depth / scope | One expert replay task, no learned-policy result; contact-specific explanation remains suspected | A bounded identification study is still affordable. Missing full benchmarks or final novelty is not itself a buildup-stage rejection criterion. |

**Primary source:** [FAST §V](https://arxiv.org/html/2501.09747v1#S5), rechecked on 2026-09-08,
already prescribes quantile normalization. The successful quantile control supplies no new
normalization contribution. No claim is made that joint-limit normalization is an implementation
bug or that scaling alone explains every difference at equal rate and distortion: those equalized
conditions have not been tested.

**Agent inference.** The broad contact-sensitive compression claim is not supported enough to
promote. Discontinuing all of Q11 from these nulls would conflate absent evidence with an
identified negative mechanism. Refinement has a concrete basis: a comparison-support gap and
a mismatch between the residual used for localization and the residual associated with full
replay failures. Neither promises a positive result. Q11 is retained only for the bounded next
question: *can natural arm-error timing be tested independently of gripper, error energy and
known scaling differences on a declared, comparable population?*

### Alternatives considered

- `select for hypothesis formulation`: not selected; draft contrasts are expressible, but v2
  has not isolated the intended exposure. Final architecture, exact novelty or multi-task
  results are not being imposed as extra entry requirements.
- `repeat feasibility study`: not selected; current measurement is valid. A changed comparator
  or residual is a new explicit protocol revision, not a rerun of v2 or a repair of its results.
- `reformulate`: not selected; there is no demonstrated new explanation to elevate into a
  different question. Scaling and gripper effects are existing controls.
- `discontinue`: warranted for a claim that v2 already establishes a contact-sensitive method,
  but not yet for the narrower unresolved comparison while the bounded design check below remains.

### Entry-to-hypothesis review

The original question, facts/source distinction, executable substrate, simple controls,
assumptions, pilot evidence and negative-result branches are documented (criteria 1–7).
A draft falsifiable intervention (criterion 8) can be written, but a signed contact-specific
prediction is not supported by v2. These criteria make formulation possible, not compulsory;
Stage 7 prioritizes the cheaper identification revision. No hypothesis folder is opened.

### Bounded next TODO and stop boundary

Prepare **one revised protocol**, using existing data to design it and no physical rollout during
preparation. The revision must explicitly state:

1. **Separate estimands.** Hard-cap codec efficiency and approximately rate/MSE-matched
   physical sensitivity are different questions. Preserve v2's hard-cap result. If the existing
   6-bit/3-knot calibration point is used, disclose the extra bytes and the original ±10%/±20%
   tolerances; do not call it equal-budget dominance. Quantile FAST remains a required control.
   Do not create a new precision/knots search to obtain a preferred outcome.
2. **Natural residual and exposure.** Explain whether/how the already observed joint-arm
   reconstruction residual can probe the unresolved failures, with exact gripper and unchanged
   residual amplitude. Retain quantile behavior as the simpler explanation. Source choice must
   be a declared post-v2 revision applied to all new assigned episodes, not just chosen failures.
   If residual energy/timing cannot be compared without outcome-based selection, do not run.
3. **Calibration and fresh confirmation.** Existing v2 data may inform design but are no longer
   a fresh confirmatory sample. Any later physical study needs a new disjoint seed list, frozen
   attempts, source-defined windows, support checks, cost accounting, endpoints and exclusions
   before outcomes. No replacements, added settling or larger perturbations to force failures.
4. **One bounded decision.** Lack of measurement validity is a technical stop. No feasible
   comparator/eligible exposure after this design check ends this physical route. If a valid
   revised study is eventually run and again yields no localized outcome contrast, or its
   differences remain explained by scaling/error magnitude, stop the contact-sensitive method
   route; do not respond with another amplitude/grid/task expansion. Any distinct question then
   requires explicit new evidence and comparative review.

The next TODO ends at a concrete protocol plus its pre-outcome support/feasibility checks, or a
recorded inability to form that protocol. It does not authorize learning, new architecture,
automatic second-task deployment or immediate hypothesis admission. Q12 re-enters comparison
only if this bounded refinement ends the current route. All current artifacts remain preserved.


## Q11 Bounded Revision Prepared (2026-09-08)

The one allowed [v3 revision](robotics/pilot_studies/q11-action-compression/README.md#bounded-physical-pilot-v3-preparation)
is concrete, calibration-checked and frozen. The existing fixed comparison has calibration
support, and natural joint-arm residuals admit source-defined event/free windows without
outcome selection or amplitude changes. Runtime and pre-intervention stop gates are implemented.
This completes protocol preparation; it does not demonstrate fresh confirmation support or
physical effects. Registry status is `feasibility_study`; Stage 7's `refine` decision is retained.

Next: execute the frozen fresh-seed job and independently verify its bundle. The stage owner
retains the exact seed list, counts, gates, commands and freeze. An inadequate support gate stops
before interventions; a valid null ends the contact-sensitive method route under the existing
bounded decision. No automatic hypothesis admission, grid enlargement, new task or policy
training follows. Q12 remains reserve. No fresh simulator episode was executed during preparation.


## Q11 — discontinue current route (2026-09-10)

**Stage 7 disposition: `discontinue` the current Q11 contact-sensitive method formulation and
physical route.** Registry status becomes `discontinued`. This implements the termination rule
specified in the bounded revision, after execution and independent verification; it does not
claim that every contact-localized error effect is absent. The broader scientific question
remains unresolved. No hypothesis is selected and no further run/grid/task expansion is queued.

The [v3 study](robotics/pilot_studies/q11-action-compression/README.md#v3-verified-results) owns
numerical results, per-case evidence and verification. Measurement, denominators, approximate
rate/MSE support and event eligibility all passed. The frozen result is
`STOP_NO_CONTACT_LOCALIZATION_SIGNAL`, not an environment, comparison-support or decoder failure.

| Decision issue | Interpretation |
| --- | --- |
| Observed effects | Grasp and release each have event/free discordances in the hypothesized direction. They are preserved as observations, not described as identical outcomes. |
| Precommitted criterion | Neither separate exact paired test meets alpha .025. A valid diagnostic null ends this bounded method route under the prior rule. This is a decision under the fixed scope, not a statistical equivalence conclusion. |
| Codec comparison | The approximate joint/Linear rate/MSE comparison is now supported, but its paired success-difference interval includes zero. Quantile's stronger success uses a different rate/error level. Neither establishes a contact-sensitive method contribution. |
| Failure interpretation | Endpoint grasp/on/static predicates describe failures; no distinct causal mechanism or new method principle was established. State/configuration, sampled contact and short-window limitations remain. |
| Why not another refinement | The one permitted revision was executed as frozen. Adding seeds, pooling event tests, increasing error, changing windows/thresholds or switching tasks after these results would extend the stopped route. |

The physical records are valid research evidence, including the nonzero directional observations.
Their preservation permits later independent question development; it does not authorize a
retrospective success claim or call these already observed seeds fresh confirmation. All
existing inputs, images, code and raw outputs remain preserved. No artifact deletion or backup
verification occurred.

Current research scope remains Robotics with Robotics-enabling 3D Vision. The next TODO is
comparative reassessment of Q12/Q13/Q14 reserves using the existing interest-based comparison,
then selection of 1–2 preliminary-review priorities. Q12 is the leading reserve to reassess,
not an automatically admitted hypothesis or an already running experiment. The sole compact
retired summary is [literature/README.md](../literature/README.md#q11-contact-preserving-action-compression--2026-09-10).

## Reserve review priority 2026-09-10

**Stage 3 comparative decision:** Q12 `under_review`, priority 1; Q13 `under_review`,
priority 2; Q14 `exploratory`, reserve. This is a preliminary-review selection, not Stage 7
hypothesis admission or permission to start a new execution study.

The eight-criterion comparison, primary evidence, corrected G3Flow premise and artifact-access
limits are owned by the [reserve reassessment](robotics/related_work/policy-geometry.md#reserve-reassessment-2026-09-10).
Q12 retains a potentially informative question about reliance on generated geometry even with
separate input encoding and consistency checks. Q13 provides a second decision/sensing question,
but must be compared with existing action-guided selectors. Q14 has an inexpensive analytic check,
yet a less concrete learning question beyond known transforms. These are agent judgments, not
new empirical findings or established novelty claims.

Next is Q12's source/input/provenance and critical-assumption review, followed by Q13's selector
comparison. Stage 4–5 must determine a bounded measurement route or revise/defer the candidate.
No hypothesis, method, dataset payload, runtime or combined Q12/Q13 system was selected.

## Q12 Stage 4–5 assessment 2026-09-10

**Decision:** retain Q12 as `under_review`. Do not adopt the unchanged G3Flow shared-asset route
as a test of completion bias. Source inspection traces observation to action/outcome, but does
not establish an independent erroneous completion or any physical failure. The alternative
3DSGrasp path needs paired-input and coordinate-restoration checks before a policy comparison.

The [Stage 4 source/prior record](robotics/related_work/policy-geometry.md#q12-stage-4-review-2026-09-10)
owns evidence and limits; the [question's Stage 5 assessment](robotics/questions/generated-geometry-reliance.md#stage-5-assessment-2026-09-10)
owns assumptions, costs and a bounded measurement-readiness draft. This is a documented
feasibility assessment, not Stage 6 execution, a Stage 7 discontinuation or hypothesis selection.
Next: review Q13, then compare the next measurements' cost and information value. No new
training, model inference, Docker build or dataset/checkpoint payload transfer was started.

## Q13 Stage 4–5 assessment 2026-09-10

**Decision:** retain Q13 as `under_review` with narrower diagnostic framing. DISaM directly
uses learned manipulation-action uncertainty and GCNGrasp-VP provides a recent task-affordance
selector. Broad action-aware sensing is therefore not the candidate contribution. A mismatch
between existing scores and observation-dependent task value remains unmeasured.

The [Stage 4 record](robotics/related_work/policy-geometry.md#q13-stage-4-review-2026-09-10) owns
primary/source evidence. The [Stage 5 record and bounded draft](robotics/questions/action-relevant-view-selection.md#stage-5-assessment-2026-09-10)
own assumptions and a conditional DISaM checkpoint/state/value-readiness route. Virtual rendering,
offline recorded-view evaluation and acquired sensor information are separate comparison regimes.
This is a documented assessment, not Stage 6 execution or a new Stage 7 disposition.

Next: compare Q12's independent-completion check with Q13's narrower diagnosis using expected
information value, direct-prior pressure, accessible inputs and setup cost. Choose one bounded
measurement or refine/defer; do not assume either must proceed. No checkpoint/dataset payload,
model inference, training, Docker build, simulation or hardware execution occurred in this review.

## Q12/Q13 measurement selection 2026-09-10

**선택:** 다음 작업은 **Q12 independent-completion measurement readiness의 입력 확인과
protocol 준비**다. Q12는 `under_review`에서 준비 우선순위를 갖고, Q13은 `deferred`로 둔다.
이는 Stage 4–5 뒤 제한된 측정에 시간을 배정하는 비교 결정이다. 아직 protocol을 고정하거나
Stage 6을 실행하지 않았으며 formal hypothesis, method, paper contribution을 선택하지 않았다.

### Evidence and comparison

사실의 owner는 Q12/Q13의 [Stage 4 source 기록](robotics/related_work/policy-geometry.md#q12-stage-4-review-2026-09-10)과
[Q13 source 기록](robotics/related_work/policy-geometry.md#q13-stage-4-review-2026-09-10), 각 question의
Stage 5 assessment다. 이번 비교에서는 pinned [3DSGrasp README](https://github.com/NunoDuarte/3DSGrasp/blob/d6763d85e063db675d433dd119837a93e3657a29/README.md),
[DISaM README](https://github.com/UT-Austin-RobIn/l2l/blob/37382315d4e262d381862752931fe7445c2a0594/README.md)와
[DISaM project](https://robin-lab.cs.utexas.edu/learning2look/)를 다시 확인했다. 기존 source receipt의
32개/36개 text 파일도 byte length와 SHA-256이 모두 일치했다. 새로운 payload 접근 성공이나
runtime 호환성을 확인한 것은 아니다.

아래 `H/M/L`은 현재 evidence에 근거한 **에이전트 평가**다. Related-work overlap에서 H는
높은 충돌 위험이며, 다른 항목의 H는 유리한 평가다. 숫자로 합산해 publication 가능성을
추정하지 않는다. 두 후보의 폭넓은 중요성과 **바로 다음 측정의 정보 가치**를 구분한다.

| Criterion | Q12 generated geometry | Q13 action-relevant views |
| --- | --- | --- |
| Significance | **H** — 생성 geometry의 유용성과 오류에 대한 policy 의존을 구분하면 perception-to-action 신뢰성에 기여할 수 있다. | **H** — 불필요한 관측을 줄이면서 행동에 필요한 정보를 얻는 문제는 중요하다. |
| Empirical accessibility | **M** — partial/GT loader와 pretrained completion 경로는 있지만 실제 pair·units·weight는 미검증이다. | **M** — DISaM skill/camera/evaluator source는 있으나 matching weights와 같은 상태에서의 비교는 미검증이다. |
| Feasibility | **M** — 첫 위험을 독립적인 입력·좌표·한 모델의 inference로 제한할 수 있다. 오래된 native stack은 여전히 setup 위험이다. | **M** — 이미 학습된 method를 사용할 가능성은 있으나 camera/encoder/receiving policy 연결, task state와 outcome adapter를 함께 확인해야 한다. |
| Informational value of next task | **M** — 잘못된 pairing/복원 scale을 model bias로 오인할 가능성을 배제하고, 실제 completion 출력을 후속 action 검증에 쓸 수 있는지 판단한다. 현상 자체는 아직 검증하지 못한다. | **M** — 기존 uncertainty score를 올바르게 측정할 기반을 확인한다. Checkpoint load만 성공해도 실제 decision value와의 차이는 알 수 없다. |
| Resource fit | **M** — 기존 초안은 두 object·네 partial input, 한 pretrained model, setup 1–2 working days 및 이후 inference 최대 두 GPU-hours다. 모두 계획치다. | **M** — 네 initial state의 matched check를 위해 setup 2–4 working days와 이후 제한된 inference를 예상한다. Task dynamics를 포함하는 비용은 더 불확실하다. |
| Scientific depth | **M** — pose/consistency/uncertainty control 뒤 행동에 따른 의존 차이가 남아야 학습 원리로 발전할 수 있다. Wrapper 보정만으로는 부족하다. | **M** — 기존 score가 task value를 설명하지 못하는 구체적 조건이 필요하다. 단순 score/utility 불일치는 알려진 value-of-information 문제일 수 있다. |
| Related-work overlap | **H** — uncertainty-aware completion, grasp/place success prediction, consistency와 separate encoding이 이미 있다. Residual의 차별성은 미확정이다. | **H, 더 직접적** — DISaM이 learned action uncertainty를 사용하고 GCNGrasp-VP가 task-affordance view 선택을 다룬다. 초기 mechanism-level 설명이 직접 겹친다. |
| Rigorous evaluation path | **M** — 독립 completion → 고정 physical geometry/pose → matched observed-only·simple controls로 이어질 수 있으나 camera/physical truth와 공정한 policy 비교가 아직 연결되지 않았다. | **M** — 같은 상태/허용 관측/비용 아래 score와 독립 task utility를 비교해야 한다. View count, KL 감소 또는 grasp AP만으로 그 경로를 대체할 수 없다. |

### Why this allocation

Q12를 고르는 이유는 더 높은 성능이나 확정된 novelty가 아니라 **첫 불확실성을 더 독립적인
단위로 확인할 수 있기 때문**이다. 입력 pair와 좌표가 성립하지 않으면 policy/simulator를
준비하기 전에 이 경로를 중단할 수 있다. 성립하면 동일 출력을 후속 action-linked 진단의
입력으로 보존할 수 있다. 따라서 지금은 Q13 전체 연결보다 작은 준비 작업에 우선 배정한다.

이 선택에는 한계가 있다. Q13은 이미 task outcome까지 있는 source라는 장점이 있고,
Q12의 첫 결과는 geometry readiness에 그칠 수 있다. Q12에서 camera/physical geometry나
action evaluator로 이어질 수단이 나오지 않으면 순수 reconstruction 연구로 범위를 바꾸지
않고 다음 투자 결정을 다시 한다. 두 작업의 시간 차이는 실측이 아니므로 실제 asset 접근과
새 Docker의 호환성 확인이 현재 우선순위를 뒤집을 수 있다.

둘 다 즉시 보류하는 선택도 검토했다. 그러나 Q12에는 pairing과 좌표라는 구체적 첫 위험과
제한된 확인 방법이 있어 작은 준비 작업까지는 정보 가치가 있다. 그 준비가 불가능하면
전체 data download, 긴 environment 복구 또는 새 학습으로 범위를 늘리지 않고 보류 사유를
기록한다. Q13은 Q12가 막혔다는 이유만으로 자동 승계하지 않는다.

### Selected next task and decision branches

세부 sample 범위·controls·receipt는 [Q12 검증 초안](robotics/questions/generated-geometry-reliance.md#bounded-measurement-task-draft)이
계속 소유한다. 다음 TODO에서 그 초안을 실행 가능한 입력과 protocol로 구체화한다.

1. 3DSGrasp의 model/data 파일 metadata, selective access, pair naming과 frame/units 근거를
   확인한다. 파일 존재와 HTTP 200을 model load 또는 데이터 정합성으로 해석하지 않는다.
2. 접근 경로가 성립하면 실제 input ID, sampling/seed, 원래 wrapper와 inverse-normalization
   control, acceptance tolerance, transfer/setup/inference 한도와 새 Docker recipe를 고정한다.
   대규모 bundle이 필요하면 먼저 크기와 대안을 기록해 그 경로의 비용을 재평가한다.
3. **진행 가능:** 작은 입력과 재현 경로가 명시되면 Stage 6 protocol을 freeze한다.
   **반박:** 독립 pair가 아니거나 잘못된 좌표 문제뿐이면 해당 해석/입력 경로를 수정하거나 보류한다.
   **불명확:** metadata나 좌표를 먼저 확인하는 범위로 축소하고 empirical effect를 주장하지 않는다.

입력 검증 후에도 행동상의 효과는 별도 evidence가 필요하다. 유효한 completion이 확보돼도
task success, reliability, generalization 또는 새 uncertainty method가 입증된 것은 아니다.
Q12의 본 연구 질문과 이번 준비 과제의 성공 조건을 혼동하지 않는다.

### Q13 disposition and re-entry

Q13은 **`deferred`**다. 현재 배정할 다음 실행은 없으며, 질문이 반증됐거나 모든 active
perception 연구를 종료한다는 뜻은 아니다. 다음 중 하나가 구체화되면 다시 비교할 수 있다.

- 접근 가능한 matching checkpoint와 작은 matched-state/action-value 사례가 확인돼 준비 비용이 줄어든다.
- 기존 DISaM/affordance/고정 view control 이후 무엇을 측정할지 명확한 source-grounded failure case가 생긴다.

재진입은 최종 novelty나 여러 benchmark의 선행 증명을 요구하지 않는다. 구체적인 작은
측정과 합리적인 비용이 있으면 충분히 재검토할 수 있다. 기존 Q13 검토·검증 초안과 모든
source receipt는 유지한다. 이번 결정에서 model/dataset payload, Docker build, inference,
simulation, training 또는 artifact 삭제는 수행하지 않았다.

문서 검증: 갱신한 Markdown 9개의 local link 152개(heading link 81개 포함)와 Q12/Q13의
status·TODO 일관성을 확인했다. 오류는 없었으며, 위 source receipt 재검증과 함께 이번
선택 기록의 검증 범위로 남긴다. 이는 model이나 실험 결과의 검증이 아니다.

## Q12 input protocol preparation 2026-09-10

Q12를 `feasibility_study`로 옮기고 **CPU input/schema/coordinate audit v1**을 고정했다.
[Study README](robotics/pilot_studies/q12-generated-geometry/README.md)가 실제 입력·자원 결정·
source/frame 근거·Docker/검증 command를 소유한다. 공개 asset 취득과 synthetic Docker
preflight는 완료했지만 실제 입력 검사나 completion inference는 아직 없다.

기존 넓은 readiness 초안의 첫 실행을 input controls로 좁혔다. Archive의 partial/GT 이름
대응은 확보했으나 per-file metric/camera metadata는 없고, paper의 preprocessing 순서와
현행 wrapper의 순서가 다르다. 따라서 실제 input validity를 확인하기 전에 native model
stack을 복구하거나 point-cloud 연산자를 대체하지 않는다. 두 object는 archive train/test에
모두 있으므로 object-disjoint evidence도 아니다. 이는 결과를 보고 바꾼 threshold가 아니라
실제 array 검사 전 protocol 구체화다.

다음 TODO는 고정된 네 쌍을 CPU Docker에서 실행하고 독립 verifier를 적용하는 것이다.
실패 case를 포함한 denominator를 보존한다. 통과 시 model loading과 독립 generated output,
physical/camera linkage를 별도로 평가하며, schema/좌표 문제는 해당 경로를 refine/defer한다.
Q13은 `deferred`로 유지하고 자동 승계하지 않는다. Hypothesis나 empirical effect에 대한
Stage 7 판정은 이번 준비에서 하지 않았다.

## Q12 input audit outcome 2026-09-10

Frozen input v1을 실제 네 partial/GT 쌍에 CPU Docker로 실행했고 독립 verifier가 모두 확인했다.
판정은 **`INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`**다. 고정된 source/input,
seed, tolerance와 네 쌍 denominator는 변경하지 않았다. [Study 결과](robotics/pilot_studies/q12-generated-geometry/README.md#verified-input-results-2026-09-10)가
수치·실행/검증 receipt와 제한을 소유한다.

Name/schema/좌표 controls의 operational uncertainty는 줄었다. 입력은 이미 수치적으로
centered/unit-radius여서 이번 네 쌍에서 큰 normalization-order discrepancy는 관찰하지
못했다. GT에는 반복 좌표가 있어 향후 sampling/density control을 명시해야 한다. 이는
기존 row-weighted 결과를 수정하거나 case를 교체할 근거가 아니다.

다음은 기존 checkpoint를 사용하는 제한된 model-loading/independent-output 검증 준비다.
Physical/camera linkage와 공정한 action 평가 경로는 여전히 별도 위험이다. Q12는
`feasibility_study`로 유지하며 model effect, hypothesis selection 또는 broad question의
반증을 판정하지 않는다. 원본 v1 결과를 보존하고 Q13은 `deferred`로 유지한다.

## Q12 model readiness preparation 2026-09-10

**Decision:** retain Q12 `feasibility_study`; run the frozen bounded CPU reference output check next.
The existing checkpoint passed exact schema/strict loading and independent metadata verification
in a fresh workspace CPU image. Native dependency access and operator parity remain unresolved;
the CPU reference route therefore tests output provenance, not native reproduction or quality.
Synthetic full-architecture and separate-process pipeline controls passed, including rejection of
copied-point tampering after hashes were refreshed. Actual four-input inference has not run.

The [model owner](robotics/pilot_studies/q12-generated-geometry/model/README.md) contains the source
reasoning, immutable protocol, commands/caps, generated/copied indices, GT row preservation and
failure branches. The next measurement can establish whether this reference route produces
reproducible checkpoint-derived outputs without GT input. It cannot resolve physical/camera
linkage, native CUDA equivalence, useful completion, robotics effects or novelty. Reassess those
costs after the bounded result; do not automatically expand setup/training or inherit Q13.

## Q12 completion output outcome 2026-09-11

**Stage 6 outcome:** `REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED`.
The frozen CPU reference route executed four real inputs in two processes. All output-provenance,
normalization/inverse, shape/finiteness and repeatability controls passed the independent NumPy
verifier. A post-run standard-library byte audit confirmed copied suffixes and cross-process NPY
bytes without additional inference. The [model owner](robotics/pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11)
contains the compact result, exact resources, hashes, commands and limitations.

Q12 remains `feasibility_study`; this is neither a new Stage 7 selection nor hypothesis admission.
The route provides reproducible checkpoint-derived outputs without GT input. It does not establish
completion accuracy, native CUDA equivalence, physical/camera linkage or an action effect. The
next task compares the costs and information value of resolving those remaining links and decides
whether a small action-linked validation is justified or the route needs refinement/deferral.
The frozen denominator, metrics and source are unchanged; Q13 remains deferred without automatic
succession. No training or physical rollout was executed.

## Q12 — `refine` 2026-09-11

**Decision:** Q12는 `feasibility_study`로 유지하고 다음 측정을 **known geometry/camera +
fixed gripper pose collision diagnostic**으로 좁혀 준비한다. Native operator parity만으로는
원본 XYZ의 camera/metric metadata가 복원되지 않는다. 원본 metadata 복원, native CUDA,
GraspNet, controlled renderer, G3Flow 경로의 비용·정보 가치와 source 근거는
[study assessment](robotics/pilot_studies/q12-generated-geometry/README.md#linkage-route-assessment-2026-09-11)가 소유한다.

KNN source fork와 작은 YCB mesh의 접근 경로를 확인했지만 새 runtime·mesh payload는
검증하지 않았다. CPU reference라는 한정된 방법으로 새 synthetic observation을 검사할 수
있는지는 다음 camera/geometry controls에서 판단한다. 기존 네 XYZ/NPZ와 frozen protocol은
보존하고 새 scene에 맞춰 GT fitting을 하지 않는다. Native-original attribution, full learned
policy와 GraspNet 확장은 각각 구체적인 후속 정보 가치가 있을 때 재검토한다.

다음 결과를 만들기 전에 독립 collision truth, 공통 observation-only 후보, simplest controls,
abstention·density·distribution-shift 경계, 자원 cap과 중단 분기를 고정한다. 연결 실패나
candidate support 부재는 refine/defer, 유효하지만 판정·선택 차이가 없으면 현재 작은 route를
확대하지 않는다. Residual이 있더라도 static collision proxy의 진단이며 native method 실패,
grasp success, learned-policy reliance 또는 novelty의 증거로 승격하지 않는다.

이는 검증된 출력에서 다음 측정으로 이어지는 Stage 7 refinement 결정이다. Hypothesis
selection, 추가 inference/simulation/training 또는 Q13 자동 승계는 없다.

## Q12 camera geometry preparation 2026-09-11

Q12 `feasibility_study`와 Stage 7 `refine`을 유지한다. 두 public YCB mesh를 취득·hash 검증하고
새 CPU Docker의 camera/geometry readiness를 구현했다. [Geometry README](robotics/pilot_studies/q12-generated-geometry/geometry/README.md)가
source/asset/환경, synthetic 검증, baseline 범위와 frozen command를 소유한다.

초기 synthetic box에서 near-surface-only 후보가 양쪽 collision support를 제공하지 못했다.
실제 YCB 결과 전에 고정 10 cm retreat를 포함하는 한 차례의 준비 수정으로 좁혔고 원본
draft·negative receipt·이유를 보존했다. 최종 synthetic 네 case는 독립 geometry와 두 oracle
sampling density의 일치를 확인했으며, 변경한 source·후보·좌표와 output overwrite를 거부했다.
이는 실제 YCB denominator의 유효성이나 completion 효과를 확인한 결과가 아니다.

Protocol/implementation/receipt 20개 파일을 고정했다. 다음은 실제 두 mesh × 두 view를 실행해
독립 verifier의 linkage/support/oracle-representation 분기를 적용한다. 통과 후에만 별도의
completion 진단 adapter/protocol을 준비한다. 실패한 case나 threshold를 바꾸지 않고 현재
결과를 보존한다. Native parity, robot grasp success, learned-policy reliance 및 hypothesis
admission은 미검증이며 Q13은 계속 deferred다.

## Q12 camera geometry outcome 2026-09-11

**Frozen outcome: `REFINE_LINKAGE`.** 두 YCB mesh × 두 view의 네 case를 유지했다.
Box 두 view의 camera/geometry·robust candidate support와 두 oracle density는 검증됐으나
mug 두 view는 mesh gate에서 중단됐다. 별도의 scalar audit이 중복 좌표와 degenerate faces를
독립 확인했다. 수치, raw/compact receipts와 검증 경계는
[geometry 결과](robotics/pilot_studies/q12-generated-geometry/geometry/README.md#verified-readiness-results-2026-09-11)가 소유한다.

Q12는 `feasibility_study` / `refine`으로 유지하고 completion 비교를 보류한다. 성공한 box만으로
denominator를 축소하거나 mesh gate를 완화하지 않는다. 이 실패는 새로운 관측·평가 입력의
operational 문제이며 completion bias나 robotics benefit/harm, broader phenomenon의 부재를
보여주지 않는다. Box 결과는 이 제한된 측정 경로의 일부를 지지하지만 hypothesis 승격은 아니다.

다음은 exact-coordinate merging과 zero-area face 정리가 positive-area surface와 평가 의미를
보존하는지 제한적으로 검토하는 것이다. 보존 근거가 확인되면 원본 v1과 실패를 유지하는 별도
revision을 준비하고, 그렇지 않으면 이 asset 경로를 보류한다. 이번 실행에서는 mesh repair,
candidate/threshold 변경, completion inference, training 또는 Q13 자동 승계를 하지 않았다.

## Q12 mesh preservation disposition 2026-09-14

**Decision:** Q12는 `feasibility_study` / Stage 7 `refine`을 유지하되 현재 YCB asset 경로는
`deferred`로 둔다. Exact-coordinate merging·zero-area face 제거는 정확한 표면과 고정 query를
보존했지만 mug의 기존 edge gate 실패를 해결하지 못했다. 따라서 이 정정으로 readiness
revision이나 completion 비교를 진행하지 않는다. [Geometry owner](robotics/pilot_studies/q12-generated-geometry/geometry/README.md#preservation-outcome-2026-09-14)가
독립 exact proof, 잔여 edge/face, 유한 query 검증, frozen negative receipts와 재현 정보를 소유한다.

유한 query의 동등성은 global solid validity나 robotics 효과를 입증하지 않는다. 원본 네 case와
v1의 `REFINE_LINKAGE`를 유지한다. 이번 처분은 Q12 현상의 반증이나 hypothesis 승격이 아니다.
추가 triangle 삭제·mesh gate 완화·성공한 box만 선택하는 방식은 채택하지 않았다.

다음은 Q12 대체 측정 경로와 추가 보류를 camera/GT 독립성, 유효한 geometry, 공개 artifact
접근, 준비 비용, 기대 정보 가치로 비교하는 것이다. 대안이 선정되면 새로운 범위와 protocol을
실행 전에 정하며 기존 case를 사후 교체하지 않는다. Q13은 기존 재진입 조건 전까지 보류한다.

## Q12 real-data preparation selection 2026-09-14

**Decision:** Q12 `feasibility_study` / Stage 7 `refine`을 유지하고 **BOP YCB-V real-data
camera/model 입력 감사의 제한된 준비**를 선택한다. [Study owner의 비교](robotics/pilot_studies/q12-generated-geometry/README.md#alternative-routes-2026-09-14)가
GraspNet·analytic solids·original-frame/native recovery·추가 보류와의 비용/정보 가치 비교,
공식 source·부분 archive 접근·mask/pose 의존성과 다음 범위를 소유한다.

선택 이유는 small real-depth/camera/model metadata 접근을 실제로 확인해 다음 입력 검증을
작게 한정할 수 있기 때문이다. BOP가 유효한 collision mesh 또는 robotics outcome을 보장하기
때문이 아니다. 첫 scene의 두 frame과 모든 object를 metadata로 정하고 별도 protocol을
실제 image/model 취득·실행 전에 고정한다. 이전 네 synthetic case와 `REFINE_LINKAGE`는 보존한다.

이후 [real owner](robotics/pilot_studies/q12-generated-geometry/real/README.md)에서 protocol·CPU Docker·
부분 취득·합성 독립 verifier를 준비·고정했다. Sensor/pose의 물리 오차 상한은 정당화되지 않아
physical/free-space admission을 보류했다. 다음은 고정된 수치 입력 감사로 실패 위치를 확인하고
calibration 경계와 함께 한 번 재평가하는 것이다. 수치 통과만으로 collision 검증에 진입하지 않는다.
통과하더라도 별도 collision/evaluator 검증 전 completion 비교를 시작하지 않는다. Mesh variant,
scene, threshold를 사후 바꿔 경로를 구제하지 않으며 Q13 자동 승계·hypothesis 승격은 없다.

## Q12 real-data input outcome 2026-09-14

**Verified outcome:** frozen BOP 입력 감사와 별도 독립 verifier가 모두 `DEFER_RAY_SUPPORT`를
반환했다. Mesh·입력/좌표 검사는 통과했으나 일부 고정 ray에 model 교차가 없고 큰 depth
residual도 남았다. [Real owner](robotics/pilot_studies/q12-generated-geometry/real/README.md#verified-real-input-results-2026-09-14)가
전체 denominator, case별 값, raw output/검증 inventory와 실패 기록을 소유한다.

**Disposition:** 사전 규칙에 따라 현재 BOP 측정 경로를 보류한다. Sensor/pose calibration은
미확정이며 ray 누락의 원인을 특정하지 않았다. Q12 `feasibility_study` / Stage 7 `refine`을
유지하고 다음 TODO에서 실패와 calibration 근거를 한 번 재평가해 추가 투자 여부를 결정한다.
이 감사는 completion-specific 행동 효과의 반증이나 입증이 아니다. Threshold/sample/asset
변경, collision/completion 실행, Q13 자동 승계 또는 hypothesis 승격은 하지 않았다.

## Q12 investment reassessment 2026-09-14

**Decision:** Q12의 추가 투자를 보류하고 question status를 `deferred`로 바꾼다.
Stage 7은 미해결 `refine`으로 남지만 진행 중인 feasibility study는 없다.
이는 현재 근거·비용에 따른 선택이며 completion-specific 행동 현상의 부재 판정이 아니다.
기존 Google 16k와 BOP의 모든 frozen 실패/성공 기록을 유지한다.

[Real owner의 재평가](robotics/pilot_studies/q12-generated-geometry/real/README.md#reassessment-2026-09-14)가
공식 visibility 의미, raster convention 후보, annotation/calibration 근거와 후속 경로의
정보 가치를 소유한다. Mask는 절대 depth 일치를 보증하지 않으며 개별 ray 누락의 원인은
미확정이다. Source에서 찾은 engineering 진단 후보만으로 다음 action 실험을 정당화하지 않는다.
유효한 modeled-geometry study 가능성까지 배제한 것은 아니며 새 protocol을 시작하지 않았다.

**Re-entry:** reference/uncertainty 처리와 completion input controls, simplest baselines,
observable action contrast, 제한된 비용·중단 기준을 가진 구체적인 연구 설계를 다른 후보와
비교할 수 있을 때만 재검토한다. 긍정 결과나 완성된 method를 사전에 요구하지 않는다.
상세 조건은 위 owner에 둔다. Q13은 기존 재진입 조건을 유지하며 자동 승계하지 않는다.

**Next:** 현재 Robotics scope와 사용자 관심 논문을 바탕으로 남은 후보 및 구체화 가능한
질문을 비교한다. 첫 측정이 줄일 연구 불확실성, simplest baseline, 직접 선행과 접근 비용으로
다음 buildup question을 선택한다. 새 실행·대규모 취득은 그 선택 뒤 별도 범위를 정한다.

## Next question selection 2026-09-15

**Stage 3 decision: Q6을 다음 Stage 4–5 검토 대상으로 선택한다.** Registry status는
`under_review`다. [후보 비교](robotics/related_work/policy-geometry.md#candidate-comparison-2026-09-15)가
Q6/Q9/Q7/Q14의 여덟 기준, 관심 논문 연결, primary source와 artifact 접근 근거를 소유한다.
Q9는 두 번째 review reserve이고 Q7/Q14는 낮은 실행 우선순위를 유지한다. Q12/Q13은 보류다.

선택한 질문은 같은 policy·inference cadence·지연값 분포에서 **실제 지연의 시간적 배치가
실패를 바꾸는지, 그리고 지연 추정과 prefix commitment를 분리한 뒤 무엇이 남는지**다.
공개 RTC source의 개입 지점과 작은 checkpoint metadata 접근이 확인돼 재학습 없이 첫
측정을 설계할 가능성이 다른 후보보다 구체적이다. 이는 source/metadata 근거이며
checkpoint load, simulator readiness, empirical effect 또는 novelty의 검증이 아니다.

다음 과제는 [Q6 record](robotics/questions/temporal-mismatch-decomposition.md)의 critical
assumption을 검토하고 최소 측정의 일정·cases/seeds·잡음·종료 처리·판정 기준·비용을 정하는
것이다. Source에서 하나로 결합된 실제 지연과 추정 입력을 분리할 수 있는지 먼저 확인한다.
동일한 질문을 prior가 이미 답했거나 개입 의미를 분리할 수 없으면 실행 준비를 진행하지 않는다.
Kinetix 결과를 VLA/3D manipulation 결과로 취급하지 않으며 hypothesis 승격도 하지 않는다.

## Q6 Stage 4–5 assessment 2026-09-15

Stage 4–5를 완료했다. [문헌/source 검토](robotics/related_work/policy-geometry.md#q6-stage-4-review-2026-09-15)와
[측정 설계](robotics/questions/temporal-mismatch-decomposition.md#stage-5-assessment-2026-09-15)를
근거로 한 번의 bounded CPU measurement-readiness 준비를 선택한다. Status는 `under_review`다.

초기 독립적 세 요인 분해 대신, 지연 순서의 total effect와 단순한 추정·실행 규칙의 설명력을
측정한다. 고정 추정/교체 대조군의 순서 불변성은 구조적 identity이며 새 현상이 아니다.
REMAC/RTC/Armory와 unified comparison의 선행을 반영했고 REMAC 최종 PDF 접근 한계를 남겼다.

두 level·cases/seeds·timing/RNG·성공 판정·검증 기준·비용 상한은 Q6 record가 소유한다.
Runtime·checkpoint load·readiness·현상 검증은 아직 없다. 원본 동등성이나 terminal 의미가
실패하면 결과에 맞춰 교체하지 않고 해당 경로를 보류한다. Readiness가 통과한 뒤에만 실행
묶음을 고정하고 held-out pilot을 연다. Hypothesis 승격과 Q9 자동 승계는 없다.

## Q6 readiness disposition 2026-09-15

**Decision:** 사전 terminal-validity gate가 실패해 Q6의 현재 측정 경로와 실행을 `deferred`로
바꾼다. [Study owner](robotics/pilot_studies/q6-timing/README.md#verified-outcome-2026-09-15)가 원본
실패 사례, 독립적인 저장 상태 재구성, 완료/미실행 분모와 보존 freeze를 소유한다.
이 실패는 temporal-order 현상의 부재 또는 후보 전체의 scientific value를 판정하지 않는다.

원본 label과 any-positive substep 성공의 불일치를 검출했고 source engine으로 재확인했다.
Source/weight 연결과 합성 검증, 일부 zero-delay parity가 통과했다고 전체 readiness를 통과한
것으로 취급하지 않는다. 성공 predicate·frame skip·level·seed를 바꿔 기존 설계를 계속하지 않는다.
Held-out pilot과 hypothesis 승격은 없으며 evaluator 수정 자체를 novelty로 쓰지 않는다.

**Next:** 한 번의 제한된 source/record 재평가로 명시적인 새 측정 설계의 scientific value,
original-result compatibility, 비용을 reserve 후보와 비교한다. 기존 실패는 그대로 보존하며
새 설계 없이 추가 rollout을 실행하지 않는다. Q9의 자동 승계는 없다.

## Q6 reassessment and Q9 selection 2026-09-15

**Decision:** Q6의 source/보존 record 재평가와 네 후보 비교를 완료했다. **Q9 Spatial-Memory
Refresh를 다음 Stage 4–5 대상으로 선택**하고 status를 `under_review`로 바꾼다. Q6은
`deferred`로 유지한다. 이는 비교에 따른 다음 검토의 선택이며 hypothesis 승격이 아니다.

[비교 owner](robotics/related_work/policy-geometry.md#q6-reassessment-and-reserve-comparison-2026-09-15)가
여덟 기준과 새로운 공개 자료의 근거를 소유한다. Q6의
[endpoint 재평가](robotics/questions/temporal-mismatch-decomposition.md#source-and-record-reassessment-2026-09-15)는
Kinetix의 first-event 정의에 따른 재설계 가능성과 원본 label의 비교 경계를 남겼다.
Q6은 즉시 실행 비용이 가장 낮지만 성공 판정 수정만으로 새 contribution이 생기지는 않는다.
실패가 delay-order 질문을 반증한 것으로 해석하지 않는다.

Q9는 DynaBench의 시점별 annotation과 작은 첫 입력, DynaMem의 source 개입 지점이
확인돼 이전 비교보다 구체적인 경로를 갖게 됐다. 같은 관측에서 memory 갱신을 비교할 수
있는지 판단하는 다음 감사의 정보 가치가 현재 Q6 evaluator 재설계보다 높다고 판단했다.
이는 에이전트의 우선순위 판단이며 Q9의 효과·novelty·runtime readiness 검증이 아니다.

**Next:** [Q9 record](robotics/questions/spatial-memory-refresh.md)의 직접 선행, causal frame
prefix·feature provenance, query 시점과 부재 label, 동일 비용의 simple refresh 비교를
Stage 4–5에서 정리한다. Source/metadata부터 시작해 제한된 CPU 입력 readiness의 필요성과
범위를 정한다. Offline object localization은 navigation/manipulation 성공을 측정하지 않는다.
전체 memory의 미래 정보나 미계산 sensing/encoding 비용을 허용하는 설계는 진행하지 않는다.

**Preserved boundary:** Q6의 기존 label·source·physics·records·freeze와 미실행 pilot은 유지했다.
새 수치 실행, pickle/checkpoint 취득, 학습, Docker 실행과 삭제는 없다. 기존 Q6 bundle과
source/weights의 byte identity 및 새 source/annotation metadata를 검증했다.
[Receipt](robotics/related_work/reassessment_sources.json)가 검사 범위를 소유한다.
Q12/Q13의 재진입 조건과 Q7/Q14의 후순위를 유지한다. Q9의 접근/개입 설계가 성립하지 않으면
이유를 기록해 재비교하며 Q6이나 다른 후보를 자동으로 재개하지 않는다.

## Buildup gate assessment 2026-09-15

이 절은 규칙 변경 전의 비교와 제안 기록이다. 채택 범위와 사용자 지정 paper 기준은
아래 [후속 운영 규칙 갱신](#buildup-workflow-update-2026-09-15)을 따른다.

사용자 요청: 현재 buildup의 gate가 아이디어 발전에 과도한지 인터넷 자료와 비교한다.
**평가:** 문서의 stage 구분은 대체로 적절하지만 실제 운영은 초기 탐색에 비해 검증·중단
절차의 비중이 크다. 탐색적 관찰에서 설명과 방법을 수정하는 여지는 상대적으로 부족하다.
이는 아래 규정/사례의 질적 비교에 따른 에이전트 판단이다. 연구실들의 평균 gate 수나
성공률, 이 repo에서 절차 때문에 소요된 시간 비율을 측정한 결론은 아니다.

### External comparison

2026-09-15 primary source 확인. Course project, 연구 제안, 논문 심사는 서로 다른 단계다.
수업에서 novelty를 요구하지 않는다는 사실을 top-tier 논문의 novelty 면제로 옮기지 않는다.

| Source and stage | 확인한 기준 | 이 workspace에 대한 시사점 |
| --- | --- | --- |
| [Stanford CS231n Spring 2026](https://cs231n.stanford.edu/project.html), project proposal | 200–400 words로 문제·문헌·data·접근·평가를 설명한다. 정확한 방법은 아직 없어도 되며 이후 문제/선행 → 방법 → 예비 결과로 발전시킨다. | 초기에는 접근 방향과 평가 가능성으로 시작할 수 있다. |
| [MIT Underactuated Robotics Spring 2024](https://underactuated.csail.mit.edu/Spring2024/project.html), 4–5 week course project | 약 한 페이지/500 words 이내 제안. 재구현·단순 model system 적용을 허용하고 simulation 구축 비용을 경고한다. | Toy/작은 모델과 baseline 재현은 학습을 위한 정당한 시작점이다. 수업 평가와 논문 채택은 구분한다. |
| [Stanford CS PhD thesis proposal](https://www.cs.stanford.edu/phd-program-requirements-thesis-proposal), formal proposal | 문제·중요성·선행·preliminary work·남은 작업/일정과 committee feedback을 요구한다. | 계획과 예비 근거는 필요하지만 이 formal milestone을 최초 아이디어의 완료 기준으로 복사할 수 없다. |
| [DARPA Heilmeier Catechism](https://www.darpa.mil/about/heilmeier-catechism), research program assessment | 목표·기존 한계·새 접근의 성공 이유·중요성·위험·비용·기간·검증 지점을 묻는다. | 중요성·차별화 가능성·feasibility 검토는 유지해야 한다. 위험이 이미 제거됐다는 증명과는 다르다. |
| [Center for Open Science](https://www.cos.io/initiatives/prereg), research planning | 탐색과 확증을 구분하며 추가 탐색과 투명한 설계 변경을 허용한다. 탐색으로 만든 가설은 별도 데이터로 확인한다. | Frozen 결과를 보존하면서 새 탐색을 할 수 있다. 내부 freeze는 공개 preregistration과 동일하지 않다. |
| [ICLR 2026 Reviewer Guide](https://iclr.cc/Conferences/2026/ReviewerGuide), submitted paper | Claim을 지지하는 정확한 증거와 새로운 지식/가치를 평가한다. SOTA는 필수조건이 아니다. | 모든 기여를 유일한 새 module이나 failure-forced method로 제한할 근거가 아니다. |
| [CVPR 2026 Reviewer Guidelines](https://cvpr.thecvf.com/Conferences/2026/ReviewerGuidelines), submitted paper | 많은 dataset에서 아직 시험하지 않은 새 개념에도 열려 있어야 하며, novelty 부정에는 구체적인 선행과 설명이 필요하다. | 다중 domain 결과나 완전히 점유되지 않은 problem을 초기 질문의 필수조건으로 두기 어렵다. |
| [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), submitted paper | Claim에 맞는 재현성과 불확실성 보고를 요구하며 설명된 no/n/a를 기계적 탈락으로 취급하지 않는다. | 주장에 비례한 검증이 필요하다. 모든 초기 실험의 양의 유의성 통과를 요구하는 문서는 아니다. |

[Søgaard et al., EACL 2023](https://aclanthology.org/2023.eacl-main.6/)도 NLP preregistration의
장단점과 exploratory 재분류, 위험 회피 가능성을 양측 논변으로 검토한다. 이는 절차 강화가
항상 아이디어 생산성을 높인다는 단순 결론을 경계할 근거이며, 인과적 효과를 입증한 연구는 아니다.

### Local rules and operational examples

- [Buildup entry](../docs/buildup.md#entry-to-hypothesis-formulation)는 이미 final method,
  exact-prior 완결, multi-domain 결과, failure-derived principle을 필수조건에서 제외한다.
  Documented feasibility assessment만으로도 entry 근거를 마련할 수 있다. 따라서 “8개
  entry 항목 자체가 모두 과도하다”보다 실제 적용과 단계 구분을 점검해야 한다.
- [Paper gates](../docs/paper.md#promotion-gates)의 최소 세 단순 대안·두 독립 축·필연적 method
  form과 [hypothesis handoff](../docs/hypothesis.md#experiment-handoff-gate)의 최소 여섯 source는
  뒤 단계의 내부 기준이다. 초기 gate로 앞당기면 과도하고, 모든 논문 유형의 보편적 요건으로
  읽어도 지나치게 좁다. 관련성과 claim을 기준으로 적용 범위를 정할 필요가 있다.
- **Q6:** [원본 성공 판정 불일치](robotics/pilot_studies/q6-timing/README.md#verified-outcome-2026-09-15)를
  발견하고 그 protocol의 추론을 멈춘 것은 적절했다. 재설계/repair의 투자 여부는 다른
  결정이다. “수정 자체는 novelty가 없다”만으로 값싼 수정을 막으면, 연구 수단과 기여를
  혼동한다. 다만 기존 Q6 처분은 reserve 비용 비교도 포함했으므로 잘못된 종료로 단정하지 않는다.
- **Q11:** [v3 결과](robotics/pilot_studies/q11-action-compression/README.md#v3-verified-results)는
  grasp/release의 방향성 있는 차이를 보존했지만 p=1/.125로 사전 alpha .025를 통과하지 못했다.
  이는 고정된 작은 연구의 결과다. 이 threshold를 미래 모든 아이디어의 진입 gate로 쓰면
  탐색 단계에 과도하다. 검정력·효과 크기/불확실성과 투자 가치를 별도로 보아야 하며,
  이번 비교로 기존 test를 합치거나 threshold를 낮추거나 종료 판정을 소급 변경하지 않는다.
- **Q12:** [입력 감사](robotics/pilot_studies/q12-generated-geometry/real/README.md#verified-real-input-results-2026-09-14)의
  undefined ray와 calibration 불확실성을 physical claim에 사용하지 않은 것은 적절하다.
  다만 schema → model → geometry → real-input 검토가 이어진 뒤에도 중심 action contrast는
  미검증이었다. 향후에는 검증된 modeled setting의 작은 관찰로 질문을 먼저 구체화하는
  경로와 비교해야 한다. 좋은 ray만 사후 선택하거나 synthetic 결과를 real 결과로 쓰라는 뜻은 아니다.

### Recommended adjustment, not adopted rules

**유지:** 중요한 질문·가까운 선행·간단한 baseline·첫 측정의 의미, 허용된 자원, Docker 격리,
관련 입력 identity, label/causal validity, 모든 실패 결과와 설계 변경의 투명한 기록.

**뒤로 이동:** 초기 양의 통계 유의성, 전체 baseline suite·모든 scene의 완전한 parity,
final novelty·method necessity·다중 domain 검증. 각각 그 증거를 필요로 하는 주장 전까지
해결하되, 아이디어 초안을 작성하기 위한 조건으로 삼지 않는다.

**보완:** 같은 질문 안에서 작은 관찰 → 설명 후보 → 간단한 방법 시도 → 수정의 탐색을
허용하는 구체적 운영 경로. Revision 사유와 관찰한 데이터를 남기고 확증에는 새/held-out
자료를 쓴다. 기술적 준비 실패, 정보 부족, 현상에 반하는 증거, 투자 우선순위를 구분한다.
짧은 연구 논의/지도교수 feedback은 체크리스트를 보완할 수 있으나 추가 자동 승인 gate로
만들지 않는다. 기간/시도 횟수는 고정 보편 숫자보다 다음 측정의 정보 가치와 비용으로 정한다.

Q9에 적용한다면 첫 목표는 “실제 갱신 사례와 simple refresh의 차이를 설명할 수 있는 작은
관찰”이다. Causal prefix·label 의미는 해당 관찰에 필요한 수준에서 먼저 확인하고, 전체
benchmark/strongest baseline/robot task 성공 증명은 후속 claim에 맞춰 확장한다. 값싼
첫 사례조차 타당하게 만들 수 없다면 보류는 합리적이다.

이 비교 작업 당시에는 개선 제안만 기록했다. AGENTS/workflow 규칙, Q9 선택, 기존 Q6/Q11/Q12
결과·freeze·실행 상태는 변경하지 않았다. 새 numerical experiment나 dataset 취득도 없다.

## Buildup workflow update 2026-09-15

사용자 요청에 따라 위 조사에서 얻은 개선안을 buildup 운영에 반영했다. 대학의 초기 제안과
탐색/확증 지침을 적용한 내부 선택이며, 외부 지침이 이 repo의 세부 절차를 요구한다는 뜻은 아니다.

- [AGENTS.md](../AGENTS.md#research-scoping-and-topic-development)와
  [buildup workflow](../docs/buildup.md)는 짧은 질문 기록, 작은 관찰, 설명/방법 시도와
  수정의 반복을 허용한다. 각 Stage와 준비 검사를 독립적인 승인/통과 gate로 쓰지 않는다.
- 탐색/확증, 변경 이력, 다음 추론에 필요한 검증 범위를 구분했다. 기술적 실패·정보 부족·
  설명에 반하는 증거·투자 보류를 다른 판단으로 기록한다. 양의 유의성이나 전체 benchmark를
  초기 진입 조건으로 삼지 않으며, 수리 자체에 novelty를 요구하지 않는다.
- Literature의 scoping과 hypothesis 진입 설명을 맞췄다. Paper-level admission,
  Experiment Handoff Gate와 최종 novelty/evidence 기준은 기존대로 유지했다.
- 사용자가 최종 paper 기준 유지를 명시했다. `paper/`는 **최종 실험을 모두 마친 후 실제
  논문을 작성할 때만** 연다. 기존 일곱 조건의 authoritative owner는
  [Paper Folder Gate](../docs/paper.md#paper-folder-gate)이며 모두 필수다.
- [Q9 다음 범위](robotics/questions/spatial-memory-refresh.md#feasibility-or-pilot-study)와
  [TODO](../TODO.md)를 작은 refresh 관찰에서 무엇을 알아낼지 중심으로 정리했다.
  Q9는 `under_review`이며 새 hypothesis·runtime·입력 취득은 없다.

Docker-only, 허용된 자산 범위, 관련 입력 identity·label·causal validity와 실패 기록 보존은
유지한다. 기존 Q6/Q11/Q12 protocol·freeze·출력·처분을 수정하거나 자동 재개하지 않았다.
문서 기준의 변경이며 연구 결과를 재해석하거나 새로운 유효성을 인증하는 작업은 아니다.

검증: 변경 문서와 buildup workflow를 가리키는 local link/anchor를 확인했고 공백 검사를
통과했다. 기존 paper claim/gate와 일곱 생성 조건의 보존 여부를 변경 전 문서와 대조했다.

## Q9 first observation 2026-09-15

Decision: **continue a bounded exploratory refinement of Q9's observation target**;
status `feasibility_study`. No hypothesis/paper promotion, new scene, or learned trigger selection.

[Focused prior review](robotics/related_work/policy-geometry.md#q9-focused-review-2026-09-15)
identified Memory for Attention as a direct prior to budgeted refresh, relevance/recency and
observation reliability. Generic update scheduling is therefore insufficient as a contribution.

The [first CPU observation](robotics/pilot_studies/q9-refresh/README.md) bundled one small raw
input, dependency repair, point trace and visual interpretation. Periodic phase affected which
frames exposed depth evidence for the bowl query coordinate; the orange coordinate had no such
evidence. Images showed that approximate query coordinates cannot be treated as exact object
surface points. This limits object-level inference without erasing the point trace or forcing
question-level discontinuation. It is not equal-cost method superiority or an official benchmark.

Next use observed surface regions from the same cases' initial RGB-D frames and a simple
visibility-aware control at an explicit depth-read budget. The question is whether this gives
interpretable object support and whether a simple control suffices. No threshold change or
replacement of the existing outcomes is selected. Q6/Q11/Q12 and the other candidate dispositions
remain unchanged; final paper standards and folder conditions remain unchanged.

## Q9 surface comparison 2026-09-15

Decision: **complete the same-case surface observation and assess remaining research value**;
Q9 remains `feasibility_study`. This is a continuation of exploratory interpretation, not an
automatic hypothesis promotion or question-level rejection.

The [surface study](robotics/pilot_studies/q9-refresh/README.md#surface-comparison-2026-09-15)
uses initial observed surface samples and compares all periodic phases with a simple current-view
eligibility rule at two depth accesses per case. The simple rule captures the measured interval
evidence, matching each case's best phase. Extra pose checks are explicit. Initial surface
seeding resolves the bowl frame-17 interpretation, but orange contradicts its initial samples
even before the tested interval; actual movement versus registration/correspondence is unresolved.
The initial range is not a verified no-change control. Raw point evidence is not object absence.

Agent inference: these cases support the value of a simple view-aware baseline and do not
demonstrate a need for learned scheduling. The remaining correspondence problem might reflect
known observation uncertainty rather than a distinct Q9 contribution. The next selected task
is to compare that issue and the cost boundary with DynaMem/Memory for Attention and choose
whether to develop a specific explanation, narrow the route or defer it. Further measurement
should distinguish those explanations; broad calibration auditing or a full benchmark is not
automatically required. No new scene/model, hypothesis, paper folder or gate is added.

Both CPU runs exited 0. The follow-up corrected a patch-read counter and added control views;
the full trace and scientific decisions stayed identical. This is record/implementation
verification, not independent real-world confirmation. Earlier results and the other question
dispositions remain intact; the original paper conditions continue to apply.

## Q9 investment decision 2026-09-15

Decision: **defer additional investment in the current depth/surface refresh route**.
Q9 status changes from `feasibility_study` to `deferred`; the next selected work is a bounded
comparison of Q7 Failure-Source Generalization and Q14 Coordinate-Frame Error Propagation.
Neither is selected for execution yet. This decision does not reactivate any frozen study.

The [primary-source comparison](robotics/related_work/policy-geometry.md#q9-research-value-2026-09-15)
distinguishes the observed view-opportunity effect from object correspondence and genuine budget
allocation. A simple control accounts for interval coverage in the two inspected cases. The
remaining orange ambiguity does not establish a failure of a full prior method. Generic
uncertainty/pose refinement and ray-based reconciliation also have concrete prior mechanisms.
Known limitations of those priors remain in the review; universal adequacy is not claimed.

The review compared more of the same trace, correspondence repair, a multi-object reformulation,
and moving the next investment to another candidate comparison. The first two currently offer
limited new explanatory value; the third remains an unselected question draft. Thus this is
an investment decision under unresolved evidence, not a statistically negative result, a
technical blockage, or a scientific rejection of spatial-memory refresh. A finished method,
positive effect or paper-level admission was not required for continuation.

Re-entry is appropriate when a small observation or analytic construction distinguishes a
specific robot-relevant explanation from its simple/prior alternative. The
[question record](robotics/questions/spatial-memory-refresh.md#investment-decision-and-re-entry)
owns that draft. Merely repairing calibration or increasing scenes does not automatically reopen
the route. All original Q9 artifacts/results and Q6/Q11/Q12 dispositions are preserved.
No new numerical run, training, hypothesis or paper folder was created during this decision.

Next compare Q7/Q14 by the value and cost of their first interpretable observation, including
their known manifest/checkpoint limitations. A small public case or explicit construction may
support that judgment; neither full reproduction nor an exhaustive review is a prerequisite.
The original final-paper conditions remain unchanged.

## Q7 Observation Selection 2026-09-15

Q7/Q14를 closest prior, 실제 사례, 단순 설명과 첫 관찰의 정보 가치·비용으로 비교했다.
**Q7을 다음 feasibility observation으로 선택**, status를 `feasibility_study`로 갱신한다.
Q14는 `exploratory` reserve이며 기각하지 않는다.
[비교 근거](robotics/related_work/policy-geometry.md#q7-q14-comparison-2026-09-15)가 상세 내용을 소유한다.

- Q7 refinement: 원래 source별 detector ranking 질문에서, 같은 grasp 시작 장면의
  구성한 no-progress 실패와 관측된 실패/성공이 같은 시각 단서로 구별되는가로 좁힌다.
- 선택 이유: Guardian 원본 metadata의 paired 사례로 construction 단서·task state·관측
  불충분을 직접 나눠 볼 수 있다. Q14의 가장 싼 대조는 CamVLA의 기존 유도/ablation과
  더 직접 겹치고, 다음 learned-error 관찰이 아직 덜 구체적이다.
- 완료 범위: primary literature와 공식 metadata inspection, 사례 선택과 해석 계획.
  Metadata matching은 실험 결과나 실패 origin의 인과 식별이 아니다.
- 다음 작업: [Q7 첫 관찰](robotics/questions/failure-source-generalization.md#first-observation)을
  새 CPU Docker 준비·시각 판독·비교·해석까지 묶어 수행한다. 전체 benchmark나 rank reversal을
  첫 관찰의 선행조건/성공조건으로 요구하지 않는다.
- 기존 Q9/Q6/Q12/Q13 deferred와 Q8 refine은 유지한다. Formal hypothesis 선택, experiment
  handoff, paper claim은 없다. 최종 paper 기준도 유지한다.

## Q7 First Observation 2026-09-15

[Q7 첫 관찰](robotics/pilot_studies/q7-failure-source/README.md#results-2026-09-15)을 완료했다.
영상 판독 후 CPU image-change 비교를 실행하고 독립 계산으로 대조했다. 단일 camera에서의
성공/실패 순서 역전은 일부 존재했지만 사후 three-view median은 네 쌍 모두를 설명했다.
따라서 새 state verifier가 필요하다는 결론을 유보하고 더 강한 단순 대안을 유지한다.

Q7은 `feasibility_study`를 유지하며, **작은 general VLM의 종료 상태 / 시작·종료 관측 조건**을
같은 dev 사례에 적용하는 제한된 시도를 선택한다. 전체 benchmark·학습·반복 prompt tuning은
선택하지 않는다. 목적은 기존 모델이 이미 해결하는 부분과 남는 증거/추론 문제를 실제 출력으로
구분하는 것이다. 준비·소수 추론·해석은 하나의 작업으로 진행한다.

반복된 동일 이미지에도 source success/failure가 함께 있으므로 변화량만으로 현재 task 상태를
항상 결정할 수는 없다. 그러나 terminal timing, 개별 failure origin과 grasp 안정성은 미확정이다.
현재 관찰을 natural-failure transfer, 독립 사례의 accuracy나 새로운 contribution으로 사용하지 않는다.
Q14 reserve, 나머지 deferred 판단과 최종 paper 기준은 유지한다.

## Q7 VLM Comparison 2026-09-15

[Q7의 같은 사례 VLM 비교](robotics/pilot_studies/q7-failure-source/README.md#vlm-results-2026-09-15)를
30개 추론·입출력 대조까지 완료했다. JSON 형식 준수 실패와 원문 판정의 사후 진단을 구분했다.
후자의 START+END 일치 수 증가도 상수 baseline을 넘지 않았으며, 동일 이미지 반복 사례에서도
판정이 바뀌었다. 작은 모델의 불안정성을 Q7 전체의 반증이나 새 verifier의 필요성으로 쓰지 않는다.

Q7은 `feasibility_study`를 유지한다. 다음은 **실제 START 이미지가 END 반복보다 추가 판정
정보를 주는가**를 보는 END+END 대조다. 이미 확보한 runtime/checkpoint로 source 8개만
추가 추론하고 동일 입력 7개는 확인 후 재사용하므로 새로운 큰 준비 비용이 없다.
이 대조로 입력 개수/반복만의 설명을 나눠 볼 수 있어 현재 Q14 전환보다 우선한다.
차이가 남아도 temporal reasoning이나 failure-source transfer claim으로 올리지 않는다.

형식 실패를 고치기 위한 반복 prompt tuning, 더 큰 모델 취득, 새 verifier 학습과 full benchmark
확대는 현재 선택하지 않는다. 이 한 대조 뒤 실제 남는 설명과 투자 가치를 판단한다. 성공할
때까지의 자동 반복이나 새 stage gate가 아니다. Q14 reserve, 다른 후보의 기존 disposition,
hypothesis/experiment 경계와 최종 paper 기준은 유지한다.


## Q7 Repetition Control 2026-09-16

[END 반복 대조](robotics/pilot_studies/q7-failure-source/README.md#repetition-results-2026-09-16)를
8개 신규 추론·7개 동일 입력 재사용·Docker 입출력 검증까지 완료했다. 실제 START와 END 반복의
전체 label 일치 수는 같고, 두 failure case의 변화는 반대 방향이었다. 따라서 이전 전체 일치
증가를 실제 시간 정보의 이점으로 쓰지 않는다. 형식 실패와 baseline 능력·source label의
미확정 때문에 이를 Q7 전체의 반증이나 새 method의 필요성으로 확대하지도 않는다.

**현재 SmolVLM2 + 같은 15개 사례의 변형 확대는 선택하지 않고 Q7을 `under_review`로 둔다.**
다음은 task 달성 증거를 맞춘 뒤 남는 constructed/execution failure 차이를 묻는 Q7 수정
초안과 Q14의 learned action/geometry shared-error 질문을 비교하는 것이다. 가까운 선행과
단순 설명을 반영해 가장 작은 다음 관찰의 정보 가치·비용으로 하나를 선택한다. 아직 두
후보의 최종 재비교나 새 수치 실행은 완료/선택하지 않았다.

이는 baseline 수리가 무의미하다는 판단도, positive result가 없어서 적용하는 중단 gate도
아니다. 현재 비교가 알려줄 수 있는 한계에 도달했으므로 원래 연구 질문과 다음 관찰의 연결을
다시 판단하는 것이다. Q14는 exploratory reserve, 다른 후보의 기존 disposition과 최종
paper 기준은 유지한다. Formal hypothesis/experiment/paper로의 승격은 없다.


## Q14 Selection 2026-09-16

[Q7/Q14 재비교](robotics/related_work/policy-geometry.md#q7-q14-reassessment-2026-09-16)를 완료했다.
**Q14를 다음 feasibility study로 선택하고 Q7의 현재 경로는 `deferred`로 둔다.**
Q14의 질문은 fixed true state에서 learned action/calibration 출력의 marginal error를 유지한 채
pairing을 바꿨을 때 base-frame action error가 어떻게 달라지는가이다. 단순 geometric estimator와
직접 base-frame regression이 설명하는 범위를 함께 비교한다.

선택 이유는 Q14의 다음 관찰에서 GT·허용 입력·pairing 대조와 단순 설명을 현재 더 구체적으로
정할 수 있기 때문이다. CamVLA의 기존 oracle/noise 대조나 correlated-pose uncertainty를
새로 발견했다고 주장하지 않는다. 특히 공개 결과가 oracle calibration의 우세인 점을 보존하며,
학습된 오차 상쇄는 아직 관찰되지 않았다고 명시한다. CamVLA code 공개 부재만의 선택도 아니다.

다음 TODO는 [Q14의 작은 planar regression](robotics/questions/frame-error-propagation.md#first-study-design)을
Docker 준비·synthetic input·최대 네 작은 fit·기하 대조·검증·해석까지 묶어 수행하는 것이다.
첫 효과가 없거나 classical estimator로 설명돼도 단순 설명을 채택할 수 있다. 이 비교 turn에는
새 training/inference/container 실행이 없다. Heavy VLA training이나 simulator full reproduction도
선택하지 않았다.

Q7의 작은 VLM 실패를 source generalization의 반증으로 쓰지 않는다. Task-state label을 방어하는
명시적 construction intervention과 source/model/evidence 설명을 구분할 작은 관찰이 생기면
다시 비교한다. [Q7 record](robotics/questions/failure-source-generalization.md#investment-decision-and-re-entry)가
재진입 초안을 소유한다. 단순 prompt/모델 교체 또는 같은 사례 확대는 자동 재개 사유가 아니다.
다른 후보의 보류·기존 결과·최종 paper 기준은 유지하며 formal hypothesis 승격은 없다.


## Q14 First Observation 2026-09-16

**Decision: `refine`; registry `under_review`.** [첫 CPU study](robotics/pilot_studies/q14-frame-errors/README.md#results-2026-09-16)의
네 fit·고정 장면 비교·독립 검산을 완료했다. 개별 error marginals를 유지한 재조합에서
scene별 결합 효과는 있지만 learned pairing의 평균 이점은 일관되지 않았다. 단순 기하
추정기도 같은 종류의 효과를 보였고, shared-keypoint-noise의 사후 1차 근사가 그 부호를
설명했다. 모든 learned residual의 설명이나 Q14 전체의 반증은 아니다.

학습 모델의 90° 오차는 rotation component가 주로 설명했으며 noiseless 입력에서도
유지됐다. 관찰한 group mean에서 기하 대안이 가장 강했다. 따라서 beneficial learned
error dependence만으로 새 correction module을 학습하는 선택은 하지 않는다.

**다음 작업:** explicit geometry 기반 예측 + 필요한 learned residual이라는 잠정 초안을,
기하 추정기의 가정이 깨지는 구체적 입력 조건과 더 단순한 calibration/표현 대안 및 가까운
선행으로 재검토한다. 무엇이 실제로 개선될 수 있는지와 작은 다음 관찰의 정보 가치·비용을
판단하며, 구별되는 대상이 없으면 추가 투자를 보류할 수 있다. 새 모듈 학습, seed/width
확대나 full VLA reproduction을 자동 선택하지 않는다.

이는 새로운 entry gate나 최종 novelty 증명 요구가 아니다. 첫 관찰에서 강했던 단순 설명을
반영해 질문과 방법 초안을 수정하는 과정이다. 이 proxy의 알려진 keypoint/scale/proprioception
가정을 실제 VLA로 일반화하지 않는다. Formal hypothesis/experiment/paper로 승격하지 않았고,
다른 후보의 기존 처분은 유지한다. 실행별 로그·출력·실패한 사후 직렬화 코드까지 보존하고
이번 study가 만든 종료 container 네 개만 삭제했다.


## Q14 Geometry Review 2026-09-16

**Decision: 실제 keypoint의 작은 관찰을 선택; registry `feasibility_study`.**
[기하·학습 대안 비교](robotics/related_work/policy-geometry.md#q14-geometry-review-2026-09-16)를 완료했다.
CamVLA의 viewpoint/hand-eye 한계, DREAM의 learned keypoint + PnP, EasyHeC++의 refinement와
추가 관측, BPnP/EPro-PnP의 학습 가능한 기하 추정, GeoCalib·EquiBot의 역할을 구분했다.
Generic geometry + residual을 곧바로 새 contribution이나 추가 학습 방향으로 선택하지 않는다.

첫 synthetic 결과만으로 실제 visual measurement의 조건을 판단하기에는 관찰 범위가 좁다.
따라서 다음은 DREAM 한 checkpoint와 Panda-3Cam RealSense 24 frame에서 동일 검출값의
PnP/RANSAC, common/all-point GT-2D 대조를 실행한다. 오검출·누락과 geometry/annotation 한계를
구분하는 정보가 toy seed/width 확대보다 크다고 판단했다. 정확한 범위와 결과별 수정은
[question design](robotics/questions/frame-error-propagation.md#real-keypoint-observation)이 소유한다.

이 선택은 원래 action/calibration dependence 질문 중 measurement/calibration 측면의 진단이다.
실제 action head가 없으므로 VLA joint-error나 robot success를 검증하지 않으며, fixed-camera
자료를 camera extrapolation 실험으로 부르지 않는다. DREAM offline source의 GT-camera-frame
3D 입력은 pose-error transform을 평가하는 privileged geometry 조건임을 명시했다.
GT가 있어 평가가 무효라는 판단도, deployable base-frame calibration을 얻었다는 판단도 아니다.

공식 source 여섯 개와 PaperReview discovery note 두 개의 hash를 기록했다. Dataset/weights
payload는 아직 받지 않았고 접근·runtime 호환성은 미확인이다. 다음 TODO는 필요한 취득·Docker
준비·추론·검산·사례 해석까지 한 묶음이다. 방법 학습, 새 sensor/view benchmark, 큰 자료 확대를
자동 선택하지 않는다. 일반적인 calibration 설명만 남으면 추가 투자 보류도 가능한 결과다.
이는 positive effect를 요구하는 gate가 아니며 작은 관찰을 통한 방법 탐색을 위한 투자 판단이다.

기존 synthetic 결과·다른 후보의 disposition·최종 paper 조건은 유지한다. Formal hypothesis,
paper-level experiment 또는 paper folder를 열지 않았다. 이번 turn의 새 수치 실행과 Docker
생성·삭제는 없다.


## Q14 Real Keypoint Observation 2026-09-16

**Decision: `refine`; registry `under_review`.** [실제 관찰](robotics/pilot_studies/q14-frame-errors/real/README.md#results-2026-09-16)의
24개 frozen-model 추론·96개 solver 대조와 독립 검산을 완료했다. RANSAC은 일관되게
개선되지 않았고, 작은 keypoint 오차에서도 solver에 따라 큰 pose 오차가 나타났다.
서로 반대인 두 큰 실패를 본 뒤 all-point reprojection으로 저장된 후보를 선택하는
사후 단순 대조를 수행했다. 같은 24 frame에서 두 실패를 피하고 평균 ADD를 낮췄다.

이는 learned residual을 학습하기 전에 단순 추정 대안을 비교할 가치가 있다는 결과다.
RANSAC의 실패를 학습의 필요성으로 바로 옮기지 않는다. 사후 대조의 개선을 held-out
성능이나 새로운 방법으로 주장하지 않고, 세 사례의 reprojection/pose 순위 불일치도 남긴다.
이 진단에는 action head가 없어 원래 Q14의 learned action/calibration dependence나 실제
robot success를 검증하지 못한다. GT 3D geometry와 projection으로 만든 oracle도 실제
annotation 정확성의 독립 증거가 아니다.

다음은 잔여 사례에서 구체적 action/calibration 질문을 만들 수 있는지, 더 단순한 추정
대안과 현재 경로의 투자 보류를 비교하는 것이다. Generic residual 학습이나 scene/camera
확대는 선택하지 않았다. 아직 새 principle·formal hypothesis·paper claim은 없다.
기존 synthetic 결과, 다른 후보의 disposition과 최종 paper 기준을 유지한다.

독립 계산 1,745개를 통과했다. 미검출 sentinel이 들어간 미사용 full-point residual 표기는
별도 saved-output 계산으로 정정하고 672개 검사에서 주요 metric·pose·선택 불변을 확인했다.
원본/정정 출력과 source·로그를 모두 보존했고 이번 workspace 종료 container 네 개만 삭제했다.

## Q14 Investment Decision 2026-09-16

**Decision / registry: `deferred`.** 남은 세 ADD/reprojection 순위 불일치의 action 관련성과
단순 대안을 비교해 현재 경로의 추가 투자를 보류한다.
[사례·수식·primary source 비교](robotics/related_work/policy-geometry.md#q14-action-relevance-review-2026-09-16)가
근거를 소유한다. 새 학습·추론·solver 실행이나 Docker 생성·삭제는 없다.

사실: 000775는 ADD가 작은 pose에서 rotation error가 더 크다. 수식 해석상 free translation
vector의 calibration error는 action 방향과 residual rotation에 의존하며 translation은
소거된다. 따라서 ADD나 reprojection 차이를 행동 오차의 순위로 옮길 수 없다. 현재 real
자료에는 action/GT action 출력이 없고, 임의 방향 추가는 기하적 민감도만 보여 준다.

에이전트 판단: 첫 synthetic 결과의 평균 learned benefit은 일관되지 않았고 실제 관찰의
큰 오류는 단순 후보 선택으로 피했다. 기존 visual-servoing error propagation, SQPnP와
uncertainty-aware estimation을 고려하면 지금 추가할 generic residual이나 solver 확대의
정보 가치는 낮다. 단순 대안의 존재만으로 novelty를 부정한 것이 아니라, 현재 관찰에서
원래 질문으로 이어질 구별 가능한 다음 시도를 선택하지 못한 투자 판단이다.

재진입은 [question record](robotics/questions/frame-error-propagation.md#investment-decision-and-re-entry)의
작은 paired action/calibration 관찰 초안을 따른다. 공개 VLA나 full benchmark, positive result를
요구하지 않는다. Broad Q14는 미해결로 남기고 현재 실험·결과·재현 자료를 보존한다.

다음 TODO는 **Q3, Q4와 관련 CD5, CD2의 작은 관찰을 정보 가치·단순 baseline·비용으로
비교해 다음 시도를 선택**하는 것이다. 기존 Robotics / Robotics-enabling 3D Vision scope를
유지하고, cross-domain label 때문에 RAG 등으로 scope를 자동 전환하지 않는다. 초기 candidate
문서의 큰 pilot·엄격한 gate를 그대로 재사용하지 않고 현재 buildup 기준으로 구체화한다.
이번 비교 대상으로 남겼다는 사실은 그중 특정 후보의 우선순위나 실행 선택을 뜻하지 않는다.

## CD2 Observation Selection 2026-09-16

**Decision: CD2의 첫 관찰 선택; registry `feasibility_study`.** 기존 Robotics scope에서
Q3, Q4/CD5와 비교한 [primary-source·정보 가치·비용 평가](robotics/related_work/policy-geometry.md#remaining-candidate-comparison-2026-09-16)를
완료했다. Q3/Q4/CD5는 `exploratory` reserve이며 질문 자체를 반증하거나 중단하지 않는다.

SIMPLER는 이미 mass/friction과 정책 순위의 관계를 비교했다. ASHiTA는 Clio 이후 hierarchical
task/scene construction을 다룬다. 이 선행을 반영해 기존의 넓은 주장으로 시작하지 않는다.
Q3의 discretization 질문, Q4의 관계·identity 및 CD5의 동일 정보 대조는 가능한 후보다.
이번에는 실제 비교 입력을 작게 확보한 CD2가 첫 관찰의 정보/비용 측면에서 유리하다고 판단했다.

선택 질문은 **평균·순위를 보존하는 작은 evaluation subset이 조건별 성능도 보존하는지,
단순 stratification으로 충분한지**다. 입력은 pinned official VLA-Arena JSON이다.
[구체적 protocol](cross_domain/questions/tail-preserving-efficient-evaluation.md#first-observation)에
cohort, uniform/stratified/greedy controls, held-out model groups와 estimand를 기록했다.
사후 숫자 선별을 피하되 일부 공개 숫자를 이미 보았으므로 탐색으로 명시했다.

원래 rare-failure prevalence 목표는 현재 aggregate 값으로 식별되지 않는다. 이를 이유로
질문 전체를 닫거나 trial-level 효과를 추정하지 않는다. 이번 관찰이 직접 답하는 것은 유한
성능표의 조건별 정보 보존이다. 이후 episode-level 관찰의 새 정보와 비용을 판단하며
표만 확대해 원래 질문을 계속 미루지 않는다. CD2의 cross-domain 분류는 RAG/LLM scope
전환을 뜻하지 않는다.

완료 범위는 비교·선택·구체적 관찰 설계와 source/schema 확인이다. Public source/result
12개를 취득해 hash를 기록했으며 weights·episode dataset·새 image/container는 없다.
수치 관찰·통계 검증은 아직 실행하지 않았다. 다음 TODO는 준비·CPU Docker 실행·검산·해석의
한 묶음이다. Positive residual·exact novelty·두 번째 dataset을 별도 진행 gate로 요구하지 않는다.
Formal hypothesis, paper-level experiment, final method와 paper folder는 열지 않았다.

## CD2 First Observation 2026-09-17

**Decision: `refine`; registry `under_review`.** 선택한 aggregate-result 관찰의 준비·CPU
Docker 실행·독립 검산·사례 해석을 완료했다. [Study 결과](cross_domain/pilot_studies/cd2-evaluation/README.md#results-2026-09-17)가
수치·denominator·사후 진단·재현을 소유한다. Source/model cohort와 원래 protocol은 바꾸지 않았다.

사실: 단순 stratification은 조건 누락을 없애고 두 split·두 budget에서 uniform보다 평균
score 오차가 작았다. 그러나 조건별 profile를 정확히 복원하거나 모든 pair 순위를 더 잘
보존하지는 않았다. Greedy의 작은 score 오차와 Long Horizon의 전체 누락이 함께 나타났다.
순위 역전에는 작은 reference score gap이 관여한다. 원본 episode가 없어 이를 policy의
통계적으로 유의한 우열이나 population safety 문제로 해석할 수 없다.

에이전트 판단: 전체 score fidelity와 조건별 정보 보존을 분리할 필요는 이 표에서 관찰했다.
Coverage만을 위해서는 단순 stratification이 이미 대안이고 잔여 순위 문제도 기존 sampling/
comparison 설명의 범위에 있을 수 있다. 현재 근거로 learned sampler나 새 tail-aware method를
정당화하지 않는다. 그렇다고 broad rare-failure 질문의 반증으로 기록하지도 않는다.

다음 TODO는 episode-level 자료에서 추가로 구분할 질문을 정하고, 단순 stratification·기존
sequential comparison과의 차이, 작은 관찰의 새 정보와 비용으로 추가 투자/보류를 판단하는 것이다.
단순 자료 취득이나 같은 aggregate 표의 seed/model/budget 확대를 별도 다음 단계로 만들지 않는다.
Q3/Q4/CD5 및 다른 후보의 disposition, 최종 paper 기준은 유지한다. Formal hypothesis와
paper-level experiment는 열지 않았다.

## CD2 Follow-up Assessment 2026-09-17

**Decision: 작은 LBM episode-level 후속 관찰 한 번 선택; registry `feasibility_study`.**
첫 결과 뒤의 추가 투자 TODO를 완료했다. [Primary 비교·대안별 정보 가치·비용](robotics/related_work/policy-geometry.md#cd2-follow-up-assessment-2026-09-17)이
상세 근거를 소유한다. STEP/N-SCORE의 task별·여러 policy 비교, PEAK의 multiple-stream
inference와 RoboArena의 task-mix 처리를 확인했다. Confidence interval, pairing,
partial-credit 또는 early stopping을 새 contribution으로 선택하지 않는다.

사실: N-SCORE 공식 pinned source의 LBM hardware key에서 success/progress sequence를
읽는 경로를 확인했다. 작은 raw pickle과 NPY를 취득했고 byte/header와 source를 조사했다.
아직 container에서 값을 열거나 metric 간 identity·실제 성능을 검산한 것은 아니다.
RoboArena도 공개 episode metadata가 있지만 첫 task별 관찰에는 별도 grouping 작업이
필요하므로, 명시적인 5 tasks가 있는 LBM을 선택했다. Source record에는 읽은 범위와
immutable input URL·hash를 남겼다.

에이전트 판단: 첫 평균표가 식별하지 못한 within-task variation을 작은 추가 비용으로
관찰할 수 있다. 질문은 **task를 모두 관측한 뒤에도 전체 평균과 task별 진단의 표본
요구량이 얼마나 다른가**다. 단순 stratification과 trial variation으로 설명된다면 새
sampler 투자 필요성이 낮다는 정보를 얻는다. 일반 통계 사실의 재발견 자체로 paper
claim을 만들지 않으며, 새로운 알고리즘이 반드시 나와야 진행하는 gate도 두지 않는다.

다음 TODO는 [입력 정규화·선택한 대조·readout](cross_domain/questions/tail-preserving-efficient-evaluation.md#episode-level-follow-up)의
CPU Docker 구현·실행·검산·해석 한 묶음이다. 기존 유한 평균표를 확대하지 않고 개별 trial
기록으로 입력 단위를 바꾼다. 이번 후속도 고정 공개 자료에 대한 sampling 관찰이며 population
inference, rare/severe failure 식별, 실제 hardware cost나 N-SCORE 우월성은 판단하지 않는다.
예상 준비·해석 반나절–하루와 CPU 1시간 이내는 실행 전 비용 추정이다.

이번 완료 범위는 투자 비교·작은 설계·공개 입력 확보다. 새 수치 계산, model/runtime 설치,
Docker 실행과 artifact 삭제는 없다. Q3/Q4/CD5 reserve, 기존 후보 판정과 paper의 최종 기준은
유지한다. Formal hypothesis·paper experiment·paper folder는 열지 않았다.

## CD2 Episode Observation 2026-09-17

**Decision: 현재 generic mean/profile-preservation 경로 `deferred`.** LBM 500개 trial 기록의
준비·CPU Docker 실행·독립 검산·해석을 완료했다. [Study 결과](cross_domain/pilot_studies/cd2-evaluation/README.md#episode-results-2026-09-17)가
수치·분모·source 정정·사후 진단·재현을 소유한다. Success와 progress는 같은 기록의 두
metric이며 반복 표본으로 합치지 않는다.

사실: 50% record budget에서 global ordering은 두 sampling·두 metric 모두 200/200
유지됐지만 작은 task gap의 sign은 흔들렸다. CleanLitterBox의 success gap은 −2 pp이고
역전은 47/200이었다. 같은 유한 표의 exact hypergeometric 계산은 21.918%의 역전 확률을
준다. Stratification은 task mix를 고정하지만 within-task variation을 없애지 않는다.
Success/progress의 task별 reference 방향이 다른 사례도 관찰했으며 이는 metric 목적의 차이다.

에이전트 판단: 첫 관찰의 coverage 문제에는 stratification이 단순 대안이고 후속의 잔여
순위 변화는 작은 gap과 표본 변동으로 설명된다. 현재 자료의 반복 확대나 새 sampler를
설계할 추가 정보 가치가 낮으므로 보류한다. 모든 연구 질문에 positive residual·최종 novelty를
요구하는 결정이 아니며 원래 rare/severe failure 질문의 반증도 아니다.

입력 대조 실패는 adapter가 NPY 폴더 이름에서 metric을 추정한 것이 원인이었다. 두 폴더의
progress mapping을 실제로 확인하고 명시적 pickle label로 정정했다. Cohort·budget·seed·
estimand는 유지했으며 실패 출력·source와 수정 이유를 별도 run에 보존했다. 230,293개
독립 구현 검사와 180개 사후 analytic identity 대조를 통과했다. 결과·로그·재현 정보를
보존한 뒤 이번 workspace의 종료 container 6개만 삭제했다. Image와 입력·출력은 유지한다.

다음 TODO는 Q3의 control interval 고정 substep 관찰과 Q4/CD5의 relation/identity
관찰을 구체적 입력·단순 대안·학습 가치·준비 비용으로 비교해 작은 시도 하나를 선택하는 것이다.
CD2는 [재검토 가능성](cross_domain/pilot_studies/cd2-evaluation/README.md#investment-decision-and-re-entry)을
남긴다. Formal hypothesis·paper experiment·paper folder는 열지 않았다.

## Q4 Observation Selection 2026-09-18

**Decision:** Q4를 `feasibility_study`로 두고 Taskography의 작은 instance-selection
관찰 한 번을 선택한다. CD5는 동일 정보 round-trip control로 연결하고 Q3는 exploratory
reserve로 유지한다. Hypothesis formulation/paper-level promotion 결정이 아니다.

[비교 근거](robotics/related_work/policy-geometry.md#q3-q4-observation-comparison-2026-09-18)에서
Q3의 fixed-control-interval discretization 경로와 Q4의 공개 action contract, 강한 단순
대안과 준비 비용을 비교했다. Taskography SCRUB/SEEK 및 Scale-Plan은 dependency-aware
selection의 직접 선행이다. Q4를 새 방법으로 인정한 것이 아니라, 실제 test 문제에서
단순한 관계 보존과 instance 선택이 얼마나 설명하는지 볼 정보 가치 때문에 선택했다.

공식 test 문제 8개와 대응 SCRUB 입력을 결과와 독립적인 숫자 ID 순으로 확보했다.
Source/input 32개 파일의 크기·SHA256을 확인했으며 아직 planner/validator 실행은 없다.
Q3의 두 보유 PPO는 action interface가 달라 비교 해석을 좁히거나 common-interface
controller를 마련해야 한다. 이 제약은 연구 질문의 실패나 simulator 경로 전체의 차단이 아니다.

[Q4 question record](robotics/questions/task-relevant-spatial-state.md#first-observation)가
선정 ID, Full/SCRUB/ID순/거리순 대조, class multiplicity quota, 공통 closure,
full-problem validation, resource cap과 해석 원칙을 소유한다. 다음 TODO는 새 CPU Docker
준비·실행·검산·case 해석을 한 묶음으로 수행한다. Positive residual이나 추가 scene을
사전 통과 조건으로 요구하지 않는다. CD2/Q14/Q7 및 다른 후보의 기존 처분은 유지한다.

## Q4 First Observation 2026-09-18

**Decision:** Q4는 `refine` / `under_review`다. [CPU study](robotics/pilot_studies/q4-planning/README.md#results-2026-09-18)의
40개 조건을 실행·검산·해석했다. Primary Full 한 건의 timeout과 나머지 유효한 계획을
구분했고, 단순 selector+closure도 여섯 문제의 symbolic validity를 유지했다. 선택적 state가
항상 더 짧은 plan을 주지는 않았다. Runtime은 단일 실행 기술 통계이며 총 system 절감 주장은 아니다.

사후 plan transfer에서 b1이 길어진 일곱 사례 모두 더 짧은 b0 plan을 실행할 수 있었다.
그 악화는 정보 부족이나 optimal-cost 증가가 아니라 현재 satisficing search가 반환한 해의
차이다. 동시에 SCRUB plan에 사용된 개체가 Nearest에서 제외돼 단순 agent-distance 선택이
다른 유효한 binding을 잃는 것도 관찰했다. 이는 더 짧은 다른 plan의 부재 증명은 아니다.

다음 TODO는 goal-conditioned distance의 작은 수정 한 번이다. 기존 여섯 lifted 문제·
b0 quota·공통 closure·동일 planner에서 agent→item→goal receptacle 이동과 distinct binding을
고려한 단순 선택을 비교한다. 학습·scene 확대 없이 준비·실행·검산·해석으로 묶는다.
기존 자료를 재사용하는 탐색이며 새로운 독립 evidence로 세지 않는다. Method/hypothesis/paper
승격은 하지 않았다. Q3는 reserve, CD5는 동일 정보 control이며 다른 후보의 처분은 유지한다.

Source·plan·검산·진단을 보존하고 이번 생성 기록·mount·command를 확인한 종료 container
10개만 개별 정리했다. 초기 CLI 실패와 witness diagnostic의 두 수정도 지우지 않았다.
수치·분모·검사 개수·command와 cleanup 상세는 study owner가 소유한다.

## Q4 Goal-conditioned Observation 2026-09-18

**Decision: Q4 `under_review` 유지; 선택한 작은 수정은 완료, 추가 투자 비교가 다음 작업.**
[Goal-conditioned study](robotics/pilot_studies/q4-planning/README.md#goal-conditioned-observation-2026-09-18)의
구현·CPU Docker 실행·독립 검산·양방향 plan transfer 해석을 마쳤다. 같은 여섯 문제를
재사용했고 b0 quota·공통 closure·planner를 유지했다. 새 held-out evidence는 아니다.

사실: 여섯 조건 모두 full/pruned validation을 통과했다. Goal-conditioned 선택은 기존
Nearest보다 네 문제에서 짧고 하나는 같고 하나는 길었다. 같은 proxy optimum의 동점
선택에서 악화된 사례가 있어 이 proxy를 전체 계획 비용으로 해석할 수 없다. 또 짧은
기존/새 plan의 transfer를 통해 목표 state에 더 짧은 해가 존재하는데도 현재 search가
긴 해를 반환한 사례를 확인했다. 상세 수치·분모·반례는 study owner를 따른다.

에이전트 판단: 이번 수정은 목표까지의 이동을 고려하는 단순 대안의 설명력을 보탰다.
잔여 차이에는 binding 선택과 whole-route ordering, heuristic search가 함께 관여한다.
이들을 분리하지 않은 평균 개선을 새 contribution이나 learned selector 필요성으로
승격하지 않는다. 다만 후보 질문 전체를 반증한 것도 아니다.

다음 TODO는 이 설명과 직접 선행의 범위를 대조해 새로운 관찰의 정보 가치·준비 비용,
Q3 reserve와의 우선순위로 추가 투자 여부를 정하는 것이다. 같은 slice의 반복/확대나 새
module은 자동 선택하지 않는다. Q3/CD5와 다른 후보의 기존 처분, 최종 paper 기준은 유지한다.
기존·신규 출력과 로그를 보존한 뒤 이번 종료 container 네 개만 개별 삭제했다.

## Q4 Investment and Q3 Selection 2026-09-18

**Decision: Q4 현재 fully observable instance-selection 경로 `deferred`; Q3의 작은
단일-policy mechanism 관찰 한 번 선택 (`feasibility_study`).**
[Primary-source·추가 정보 가치·비용 비교](robotics/related_work/policy-geometry.md#q4-follow-up-investment-review-2026-09-18)를
완료했다. Taskography는 pruning과 optimal/satisficing plan quality를, PLOI는 원본 validation과
동종 copies 선택의 한계를 이미 다룬다. Scale-Plan도 dependency filtering의 직접 선행이다.

Q4의 두 관찰은 단순 선택의 개선, proxy tie의 반례, 더 짧은 feasible plan을 반환하지 못한
search 사례를 구분했다. 문제43의 optimal-cost 손실 여부는 미해결이고 작은 optimal 대조도
가능하다. 그러나 현재 fully observable 문제의 설명을 더 세분화하는 것보다 아직 보지 않은
controller–simulation 연결의 관찰이 다음 투자로 더 유익하다고 판단했다. Broad Q4의 반증이
아니며 [재검토 경로](robotics/questions/task-relevant-spatial-state.md#investment-decision-and-re-entry)를 남긴다.

Q3도 SIMPLER의 physics/ranking, Contact Models in Robotics의 timestep self-consistency,
2026 manipulation benchmark audit의 closed-loop propagation과 가깝다. Timestep 민감도나
feedback amplification 자체를 novelty로 주장하지 않는다. 기존 두 PPO의 action interface가
달라 첫 관찰을 **joint PPO 하나의 fixed-control timestep 대조**로 축소했다.

[선택한 관찰](robotics/questions/physics-ranking-stability.md#selected-first-observation)은 같은 초기
상태·control/PD 설정에서 closed loop와 absolute joint-target replay를 비교한다. 무엇이
달라지는지, 안정적인지부터 배우는 탐색이며 아직 policy ranking을 측정하지 않는다.
Source 9개와 작은 public checkpoint의 bytes/hash를 확인했지만 새 image/runtime은 실행 전이다.
이 차이를 준비 완료나 성능 근거로 바꾸지 않는다.

다음 TODO는 해당 관찰의 Docker 준비·실행·검산·해석 한 묶음이다. 결과에서 후속 정보 가치를
판단하며 새 학습·여러 task·최종 novelty를 진입 gate로 요구하지 않는다. 이번 투자 비교에는
새 수치 실험·container 생성/삭제가 없다. 기존 연구의 종료/보류 판정과 최종 paper 기준은 유지한다.

## Q3 Timestep Observation 2026-09-18

판단: **`refine` / Q3 `under_review`**. 선택한 GPU 관찰 96회와 CPU 독립 검산을
완료했다. [Study의 결과·한계·복구](robotics/pilot_studies/q3-timestep/README.md#results-2026-09-18)가
수치, 반복 대조, label/target 검증과 보존·cleanup을 소유한다.

관찰한 사실은 frequency 변경에 따른 trajectory 차이와 모든 조건의 성공 결과 유지다.
같은 조건 반복과 100 Hz reference-target replay는 기록한 cube/qpos/target에서 일치했다.
Closed loop의 더 큰 차이는 policy/relative-target 갱신의 관여와 부합하지만 완전한 원인
분해, 새로운 현상 또는 method의 필요성을 입증하지 않는다. 이번 단일 policy에서 ranking은
측정하지 않았으며 원래 broad 질문 전체를 반증한 결과도 아니다.

다음은 이 관찰을 직접 선행과 비교해 유용한 후속 질문 또는 현재 경로의 투자 보류를
판단하는 것이다. 같은 grid/seed 확대나 성공 기준 변경을 선택하지 않는다. 다른 후보와의
정보 가치·비용 비교를 유지하며 hypothesis 또는 paper로 자동 승격하지 않는다.

## Q3 Investment and Q15 Selection 2026-09-18

**Decision: Q3 현재 timestep-sensitivity 경로 `deferred`; Q15의 제한된 reward-training
관찰 선택 (`feasibility_study`).** [직접 선행·후보·비용 비교](robotics/related_work/policy-geometry.md#q3-investment-and-q15-selection-2026-09-18)를
완료했다. Q3 결과는 timestep self-consistency와 closed-loop 전파라는 기존 설명에 부합하고,
시험한 초기 상태에서는 성공 결과가 유지됐다. 넓은 ranking 질문의 반증은 아니다.

Q3 grid/정책 추가, Q4 partial-observation 확장, CD1 intervention과 Q15 학습 개입의
다음 정보 가치를 비교했다. Q15도 DrEureka의 reward-dependent transfer와 직접 겹친다.
Nominal 성능과 전이 성능의 차이를 새 현상으로 주장하지 않으며 reward를 직접 바꾸는
작은 관찰이 scale·학습 진행도·접촉 행동을 구분하는 데 유용하다고 판단했다.

[Q15 first observation](robotics/questions/reward-dynamics-transfer.md#first-observation)에
reward 식, training seeds/updates, 물성 대조, native 평가와 비용 상한을 고정했다.
공식 source 11개를 immutable remote와 bytes/SHA256으로 대조했다. Source 접근·설계
완료는 학습이나 물성 개입 runtime 검증을 뜻하지 않는다. 이번에 새 rollout·학습·Docker
생성/삭제는 없다. Q3의 결과·raw artifact와 다른 후보의 기존 판단은 유지한다.

다음 TODO는 선택한 Q15 관찰의 Docker 구현·실행·독립 검산·해석 한 묶음이다. 단순 대조가
충분한 결과도 수용한다. Uniform DR/PBRS/full benchmark를 모두 선행 gate로 요구하지
않으며 현상의 차이가 나올 때까지 reward나 물성 범위를 확대하지 않는다. Formal hypothesis,
새 contribution 또는 paper 승격은 선택하지 않았다.

## Q15 First Observation 2026-09-18

**Decision: `refine`; hypothesis promotion 없음.** 선택한 9 fits / 18 checkpoints /
2,304 episodes를 실행·독립 검산했다. [결과·실패 사례·수정 기록](robotics/pilot_studies/q15-reward/README.md#results-2026-09-18)이
수치의 owner다. Reward scale 변경도 최종 성능을 따라잡았고, 학습 시점에 따른 차이가 컸다.
시험한 물성 조건의 변화는 작아 grasp bonus 제거만의 robustness 이점을 지지하지 않는다.

Native nominal의 성공 후 goal 이탈은 다음 설명을 구체화할 관찰이다. Grasp를 유지하면서
목표 범위 밖에서 멈춘 사례가 있어 단순 grasp 소실과 구분된다. 다만 scale 대조도 여러
실패를 피했으며 세 training seeds / 단일 task만으로 shaping의 고유 기전을 확정하지 않는다.
직접 선행과 이 사례를 비교해 추가 관찰의 정보 가치를 판단하는 것을 다음 TODO로 둔다.
동일 grid 확대, 새 reward method 또는 full DR/PBRS 구현은 선택하지 않았다.

검산기의 native static 판정과 fractional filename 조회 오류를 원본 source/metadata에
맞게 수정했다. 실패 source/log와 원본 학습·평가 데이터를 보존했으며 성공 기준 변경이나
재학습·재평가는 없다. 보존 확인 후 이번 종료 container만 개별 정리했다. Q3와 다른
후보의 기존 판단, hypothesis/paper 진입 기준은 유지한다.

## Q15 Hold Observation Selection 2026-09-18

**Decision: Q15의 joint-position hold 관찰 한 번 선택 (`feasibility_study`); 재학습 없음.**
[문헌·source·대안 비교](robotics/related_work/policy-geometry.md#q15-follow-up-investment-2026-09-18)를
완료했다. PPO의 scale 민감도와 도달 후 상태 유지는 선행에 있으며, 이번 결과도 no-grasp의
고유 transfer 이점을 요구하지 않는다. 하지만 기존 trace는 동일한 성공 상태에서 단순한
유지 제어를 적용했을 때 실패를 피할 수 있는지 알려주지 않는다.

추가 학습, 물성 확대, 관측된 action/value 상관 분석과 비교해 기존 policy의 실행 제어를
바꾸는 작은 대조가 가장 싼 의사결정 근거라고 판단했다. 성공하면 새 reward 학습 투자를
줄일 수 있고, 실패하면 고정 관절 목표가 부족한 조건을 구체화할 수 있다. 어느 결과도
새 method의 필요성이나 접촉 동역학의 불가피한 실패를 자동으로 뜻하지 않는다.

[정한 관찰](robotics/pilot_studies/q15-reward/README.md#joint-position-hold-observation)은
기존 최종 checkpoint 9개, nominal, 공통 32 initial states와 두 execution routes의
576 episodes다. Privileged success-trigger를 쓰는 탐색이며 독립 held-out/실전 controller
검증이 아니다. Pinned source는 zero delta와 고정 reference의 차이를 확인할 수 있었지만
실제 hold adapter는 아직 실행하지 않았다. 구현·검사·관찰·해석을 다음 TODO 한 묶음으로 둔다.

Q15의 첫 결과와 검산 수정 이력, Q3/다른 후보의 기존 판단을 유지한다. 이번 작업은
primary literature와 읽기 전용 source/config 검토·설계·선택이며 container 생성/삭제,
새 학습/rollout, hypothesis/paper 승격은 없다.

## Q15 Hold Outcome 2026-09-22

**Decision: 현재 reward-selection/단순 hold 확장 경로는 `deferred`.** 선택했던
[576회 관찰](robotics/pilot_studies/q15-reward/README.md#hold-results-2026-09-22)을 완료했다.
Native의 주요 목표 이탈 8건을 단순 제어로 피했고, 전체 288 pair에서 9건 개선·3건 악화가
있었다. 288개 전환 전 일치와 원래 continued trace 재현, 실제 target 및 원본 label/reward
독립 검산을 통과했다. 재학습과 새 threshold/물성/seed 선택은 없었다.

첫 관찰의 scale·학습 진행도 설명에 더해, 기존 실패의 상당 부분은 실행 제어를 바꾸는
단순 대조로 피할 수 있었다. Hold의 나머지 실패는 성공 신호·관절 목표·물체 상태 유지가
같지 않다는 제한을 보여주지만 새로운 reward 기전이나 안정 제어 원리를 요구하지는 않는다.
따라서 현재 설정 확대보다 다음 질문을 비교하는 데 투자한다. 이는 broad reward-transfer
질문의 반증 또는 최종 novelty를 요구하는 새로운 gate가 아니다.

다음은 CD5의 동일 정보 표현, CD1의 개입 가치, Q8의 회복 가능성 질문과 재검토 조건을
먼저 비교해 작은 관찰의 정보 가치·접근성·비용으로 선택한다. 아직 새 후보나 실행은
선택하지 않았다. Q15는 구체적 행동 질문과 단순 유지·목표 여유·기존 안정화/피드백
대안의 다른 예측을 비교할 관찰이 생기면 재비교한다.

## CD5 Observation Selection 2026-09-22

**Decision: CD5의 동일 정보 symbolic robot planning 관찰 선택 (`feasibility_study`).**
[CD5/CD1/Q8 비교](robotics/related_work/policy-geometry.md#cd5-cd1-q8-comparison-2026-09-22)를
완료했다. CD1은 공개 modular-query의 synthetic 실행 경로를 확인해 접근성 설명을
갱신했지만, confidence-only/cost-aware 비교가 직접 선행에 있어 현재 우선순위로 선택하지
않았다. Q8은 정의·학습 데이터 연결·demo 복원의 기존 문제를 유지하며 같은 grid를 재개하지 않는다.

CD5도 표현 민감도나 symbolic verification 자체가 새 기여는 아니다. Q4가 동일 PDDL로
복원한 round trip과 달리, 실제 frozen model이 다른 표현을 읽고 생성한 계획의 실패를
비교한다. 단순 canonical ordering과 prerequisite correction으로 충분한 경우도 다음
방법 투자를 줄이는 정보다. 모델/scene를 대규모로 늘리기 전에 이 작은 대조를 한 번 선택한다.

[Study owner](cross_domain/pilot_studies/cd5-representation/README.md)에 입력·모델 revision,
6 development + 24 observation task, JSON/text × ordered/shuffled, strict/보정 평가와
비용 상한·판단 분기를 기록했다. 공식 symbolic JSON 178개와 source를 확보했고 개별
task 목록과 hash를 보존했다. 파일명/README의 task 수는 실제 평가 분모로 쓰지 않는다.

이번 완료 범위는 primary literature 비교, 읽기 전용 source/input audit와 관찰 선택이다.
새 Docker/model inference, 학습·physics rollout은 아직 없으며 runtime compatibility와
evaluator correctness는 미검증이다. 다음 TODO는 선택한 관찰의 Docker 구현·실행·독립
검산·해석이다. Q15 및 다른 후보의 보류 결과는 보존하며 hypothesis/paper 승격은 없다.


## Q16 Selection 2026-09-23

- **사용자 요청과 처분:** CD5 대신 다른 후보를 탐색·선택하라는 요청을 반영해 CD5를
  `deferred / not run`으로 변경했다. 미실행 입력·설계는 보존한다. 실험 반증에 따른 보류나
  사용자가 새 후보의 세부 방법까지 명시적으로 선택했다는 뜻은 아니다.
- **비교:** Action chunk 재계획, contact-rich demonstration augmentation, multi-frame policy,
  접촉 전후 action-conditioned motion prediction을 primary source로 대조했다.
  [비교·읽은 범위·접근 비용](robotics/related_work/policy-geometry.md#candidate-replacement-2026-09-23)이 근거다.
- **선택:** [Q16](robotics/questions/interaction-conditioned-motion.md)을 `exploratory`로 등록하고
  다음 작은 관찰 대상으로 정했다. 움직이는 물체를 잡을 때 예정 행동에 따른 물체 운동을
  예측하는 작은 model과 feedback/재계획을 비교한다. 약 2 working days, GPU 8시간 이내의
  첫 구현·관찰은 계획 추정이며 실제 resource feasibility는 미검증이다.
- **선택 이유 — 에이전트 판단:** Geometry, dynamics와 행동 성공을 직접 연결하며 제한된
  simulator construction과 작은 학습으로 방법 시도까지 가능하다. 공개 artifact 수나
  novelty 증명이 선택 이유는 아니다. State-based 관찰의 범위를 명시하고 vision/VLA 개선을
  미리 주장하지 않는다.
- **직접 선행:** SIDO의 pre-grasp augmentation 경계는 질문의 출발점이며 실패 증거가 아니다.
  DynamicVLA의 contact-induced 변화 대응, action-conditioned graph dynamics+MPC,
  RDP와 classical replanning을 인정한다. '접촉 예측을 추가했다'는 기여는 주장하지 않는다.
- **다음 작업:** 새 Docker에서 한 dynamic grasp-and-transport task, 단순 제어와 작은
  history-only/action-conditioned model을 구현·관찰한다. 결과에 따라 필요한 조건과 method
  form을 수정한다. 수치 결과 없이 가설·paper 단계로 넘기거나 전체 benchmark를 만들지 않는다.

Source README 텍스트 확인 외에 새 학습·inference·rollout·container 실행은 없다.
Q15와 그 이전의 결과·보류 판단은 변경하지 않았고 `research_overview.md`와 `PaperReview`도
수정하지 않았다. 이는 현재 후보 교체 완료이며 Q16의 empirical validation 완료가 아니다.


## Q16 First Observation 2026-09-23

새 CPU Docker에서 160 train/validation episodes, 7,299-parameter 모델 두 개와 240 evaluation
rollouts를 실행했다. 다섯 route 모두 static/sliding 각각 24/24 성공하고 release는 없었다.
접근/closing validation RMSE는 CV/history/action 4.029/4.634/0.527 mm였지만 행동 성공 이점은
관찰하지 못했다. CPU rendering material 오류를 collision-only actor로 수정한 이력도 보존했다.

Raw-state grasp/목표·action/feature·split 검산과 case diagnosis를 완료했다.
상세 설정·예측과 행동의 차이·분모·한계·복구는
[study owner](robotics/pilot_studies/q16-motion/README.md#results-2026-09-23)가 소유한다.

**판단:** `under_review / refine`. 현재 full-state 단일 cube에서 feedback는 충분했다.
Q16 전체의 반증, model의 일반적인 무용성 또는 final contribution으로 해석하지 않는다.
같은 성공 grid 확대 대신 접촉 후 행동 선택을 바꾸는 구체적인 조건과 예측 horizon을
선행·현재 trace로 검토해 다음 작은 관찰 또는 보류를 정한다.
이미 본 평가 사례는 탐색 근거이며 이후 독립 확증 split으로 재사용하지 않는다.

필요한 결과·로그·source/command/lock을 보존하고 이번 생성된 종료 container 7개만 정리했다.
다른 workload와 기존 image/cache는 변경하지 않았다. Formal hypothesis/paper 승격은 없다.

## Q16 Method Development 2026-09-23

**Decision: Q16을 Predictive Policy Adaptation 방향으로 계속 개발한다 (`feasibility_study`).**
사용자는 좁은 잔여 문제만 찾으면 주제를 발전시키기 어려우므로 시의성과 방향성이 있으면
진행할 것을 요청했다. 첫 cube 관찰의 `refine`을 추가 방법 개발로 연결한다. 이번 결정은
해당 관찰의 수치·실패 판정을 바꾸거나 방법의 신규성을 확정한 것이 아니다.

[직접 선행 검토](robotics/related_work/policy-geometry.md#q16-policy-adaptation-direction-2026-09-23)에서
DynaGuide, DyWA, Feedback World Model과 DynamicWAM을 비교했다. Policy를 future prediction으로
유도하고 실제 실행·물리 조건에 적응시키는 흐름이 확인된다. **에이전트 판단:** 중요한
capability와 작게 시작할 경로가 있어 개발할 가치가 있다. 가까운 선행은 차별점을 찾을
비교 기준으로 사용하며 주제의 자동 기각 사유로 삼지 않는다.

첫 source는 0.1 s 뒤 displacement, xy 후보 9개, 규칙 기반 phase/transport에 한정됐다.
예측 정확도 개선이 성공 이점으로 이어지지 않은 결과는 유효하지만, learned policy의
여러 step 행동 전체를 예측·수정하는 접근을 시험한 것은 아니다. 그 구현 범위를
넓혀 실제 policy adaptation을 시도하는 것이 다음 투자라고 판단했다.

다음은 nominal demonstration의 작은 Diffusion Policy를 기반으로 multi-step object/robot
dynamics와 실행 피드백을 연결한다. 잡기·운반에서 시작해 밀기를 추가하고, 단순 재계획·
geometric feedback과 비교하면서 실패 원인과 방법을 함께 발전시킨다. 최초 구현부터
모든 과업의 효과나 최종 novelty를 요구하지 않는다. 범위·데이터·대안·자원 배분과
첫 구현 산출물은 [study owner](robotics/pilot_studies/q16-motion/README.md#method-development-2026-09-23)가 소유한다.

운영 원칙은 `AGENTS.md`와 `docs/buildup.md`에 반영했다. 기존 후보의 보류를 일괄 철회하지
않으며 현재 Q16에 집중한다. 최종 paper 기준은 유지하고 `paper/`를 열지 않는다.
이번 완료 범위는 primary literature 조사, 읽기 전용 source 비교와 개발 선택·설계다.
새 학습·rollout·container 생성/삭제는 없다. 다음 TODO는 prototype 구현·실행·해석이다.

## Q16 Prototype Observation 2026-09-23

**Decision: Q16 방법 개발을 지속 접촉의 pushing으로 확장한다 (`feasibility_study`).**
[첫 정책 적응 prototype](robotics/pilot_studies/q16-motion/README.md#adaptation-results-2026-09-23)에서
학습 정책의 실제 action chunk와 8-step object/TCP 예측을 연결했다. 첫 diffusion 행동은
grasp 전에 gripper를 닫는 실패를 보였다. 이를 본 뒤 supervised action head를 추가했고,
처음 평가의 source와 수치는 그대로 보존했다.

수정한 `fit2`를 유지한 32개 새 초기 상태 × 세 조건 × 여섯 route의 576회에서 moving
성공은 learned policy 9/32, fixed predictive correction 32/32, feedback-adjusted 29/32,
단순 CV 32/32였다. Static은 모든 route 32/32, moving+friction 0.05는 CV와 두 correction이
32/32였다. Raw state 46,656개와 96개 condition별 paired initial state를 검산했다.

**확인 사실:** 예측 보정은 이 learned policy의 움직이는 물체 실패를 줄였다. 직전 예측
오차를 단순 bias로 더하는 방식은 fixed correction보다 세 사례 악화됐다. World model은
nominal policy 자료 외에 moving teacher 48 training episodes를 사용했다.

**에이전트 판단:** 작은 grasp task는 단순 CV가 전부 해결하므로 새로운 policy/world
조합의 기여를 입증하지 못한다. 더 빠른 재계획도 learned policy의 moving 실패를 줄이지
못했다. 가까운 선행과 결과를 고려하면 지속 접촉에서 정책의 역할·동일 데이터의 직접
policy update·예측의 계산 비용을 함께 살피는 쪽이 정보 가치가 크다. 작은 차이를 만들기
위해 첫 task의 성공 threshold를 좁히거나 임의 noise를 추가하지 않는다.

다음 작업은 pinned `PushCube-v1`의 native goal criterion에서 같은 방법을 발전시키고
단순 feedback 및 같은 추가 dynamics data로 갱신한 policy를 비교하는 것이다.
새 task가 양의 결과를 보인다는 약속이나 hypothesis/paper 승격은 아니다. 이번 결과·원본·
source/command/lock을 보존했고, 소유권이 확인된 이번 종료 container 11개만 정리했다.

## Q16 Pushing Observation 2026-09-23

**Decision: Q16의 작은 residual-bias 조정을 계속하지 않고 대표적인 관측 또는 물체 변화로 확장한다 (`feasibility_study`).**
[밀기 study](robotics/pilot_studies/q16-motion/README.md#revised-result-interpretation-and-preservation)는
pinned native goal criterion을 유지한 collision-only `PushCube-v1`에서 160개 시연,
동일 추가 데이터를 사용한 정책 갱신과 dynamics, 첫 192회와 수정 후 새 초기 상태 256회를
검산했다. 첫 평가를 보고 접촉 근접 조건과 작은 행동 보정으로 수정했으므로 두 평가를
독립 확증 반복으로 합산하지 않는다.

새 초기 상태에서 단순 feedback은 nominal/low-friction 각각 16/16, frozen 및 동일 데이터
갱신 정책은 13/16, 접촉 조건 예측 보정은 6/16이었다. 보정 route는 같은 초기 상태의
frozen 성공을 각 조건 7개씩 해쳤고 rescue는 없었다. 잡기에서 moving 9→32/32였던
예측 보정의 이점은 밀기로 이어지지 않았다. 시연 validation의 예측 오차가 작았던 것만으로
candidate action의 실제 접촉 결과를 가릴 수 없었다.

**에이전트 판단:** 현재 full-state single-cube 설정에서 예측 기반 보정이 단순 feedback을
넘는다는 근거가 없다. 그러나 두 작은 과업은 관측의 불완전성·물체 다양성·실제 센서
입력에서의 정책 적응을 판단하지 못한다. 사용자 요청에 따른 넓은 Q16 방향을 유지하되,
다음에는 같은 관측·추가 데이터를 받는 강한 단순 대안을 기본으로 하고 대표 조건 하나에서
실패 원인과 비용을 본다. 후보 행동 외삽과 접촉 기하는 잠정 설명이며, 필요하면 matched
action-branch 진단으로 구분한다. Formal hypothesis, paper claim, 새 연구용어는 열지 않는다.

## Q16 Delayed Observation 2026-09-23

**Decision: `PushCube-v1`의 같은 제어기에서 지연 길이와 목표 반경을 조정하지 않고, 계속적인 물체 상대 수정이 필요한 공개 과업을 고른다 (`feasibility_study`).**
[지연 관측 study](robotics/pilot_studies/q16-motion/README.md#delayed-observation-result-and-boundary)는
물체 pose/velocity만 4 control steps 늦추고 로봇 상태와 고정 목표를 현재로 둔 constructed
조건이다. 160개 시연, 새 초기 상태 16개 × 두 마찰 조건 × 여섯 route의 192회를
검산했다. 같은 지연 정보를 쓰는 단순 feedback와 velocity extrapolation은 양 조건 모두
16/16; frozen policy는 9/16, 동일 추가 데이터 갱신 policy는 10/16, model-guided policy는
nominal 6/16·저마찰 9/16이었다. 현재 true object state의 feedback 16/16은 비교 상한일
뿐 동일 정보의 baseline이 아니다.

**에이전트 판단:** 지연 입력은 정확히 적용됐지만 nominal의 지연/깨끗한 feedback의
최종 오차 차이는 평균 0.1 mm 미만이다. Object가 초기 접근 중 거의 정지해 있고, push
phase의 controller는 고정 goal 중심으로 움직이므로 이 task는 관측 지연에 대한 Q16의
핵심 설명을 구분하기 어렵다. 이 무차이를 prediction 일반의 반증으로 확대하지 않는다.
다음에는 pinned source의 `PushT-v1`(회전·영역 중첩 목표)과 `RollBall-v1`(굴러가는 구체와
무작위 목표)을 read-only source/metric·작은 CPU Docker smoke로 비교해 한 과업을 선택한다.
두 task 이름·기본 목표는 source 확인 사실이며, 특정 후보에서 model이 유용하다는 판단은
아직 없다. 같은 관측·학습 예산의 단순 feedback과 native success를 준비할 수 있어야
하며, baseline이 먼저 풀리는 상황도 결과로 기록한다. Formal hypothesis/paper로 승격하지 않는다.

## Q16 Contact Task Selection 2026-09-23

**Decision: `PushT-v1`을 Q16의 다음 개발 과업으로 잠정 선택하고, 직접 시연 재생의 호환성을 먼저 해결한다 (`feasibility_study`).**
[비교 study](robotics/pilot_studies/q16-motion/README.md#contact-task-comparison-and-selection)는
pinned ManiSkill의 collision-only CPU 변형을 별도 Docker에서 실행했다. 두 과업 모두
goal pose의 native 성공 판정과 8개 paired seed × 세 단순 route의 48개 최종 trace를
검산했다. 마지막 개발 제어기의 평균 최종 점수는 `PushT-v1` 영역 중첩률에서
hold 0.288, 현재 물체 상태 feedback 0.375, 초기 물체 상태 고정 0.331;
`RollBall-v1`의 XY 목표 거리는 각각 1.451/1.439/1.440 m였다. 모든 route의 native
성공은 0/8이므로 이 차이를 유의미한 feedback 이점이나 모델 필요성으로 해석하지 않는다.

**에이전트 판단:** T의 위치·회전·영역 중첩 목표는 계속적인 접촉 조정 질문에 더 잘
맞고 CPU에서 물체 반응과 native 점수를 함께 관찰할 수 있다. Ball은 현 단순 접근으로
접촉·이동이 거의 없지만 보류된 예비 과업이며 실패 판정은 아니다. 두 과업에 공식 시연이
있으나 확인한 `PushT-v1` ZIP은 다른 ManiSkill commit과 PhysX CUDA에서 만들어졌다.
현재 CPU 변형에서 초기 기록 상태를 복원해도 여덟 시연의 성공을 재현하지 못했다.
따라서 source-matched/native 재생과 동일 관측·데이터 policy 대안이 다음 투자 판단을
결정한다. 그 전에는 모델 보정 성능·data efficiency·generality를 주장하거나
formal hypothesis/paper로 승격하지 않는다. 기존 threshold는 유지한다.

## Q16 PushT Demonstration and Policy Route 2026-09-25

**Decision: `PushT-v1`을 Q16의 개발 과업으로 유지하되, 공식 시연의 행동 재생 성공을
데이터셋 전체에 일반화하지 않는다 (`feasibility_study`).** 생성 commit의 원본 CUDA
환경에서 초기 기록 상태를 복원한 여덟 source-success 시연 중 최종 성공은 2개였고,
공식 replay 도구가 같은 여섯 개를 실패로 분류했다. CUDA collision-only와 원본 scene의
trace는 여덟 개 모두 동일했으며, source-matched CPU의 첫 행동 관절 오차는 CUDA에서
사라졌다. 따라서 이전 변형의 큰 즉시 오차에는 backend 차이가 있었으나 남은 접촉
궤적 차이의 단일 원인은 확정하지 않는다.

기록 물리 상태에서 `state` 관측 31D와 행동 3D를 정렬해 별도 데이터 분할을 만들었다.
작은 64-demo behavioral cloning의 첫 새 seed 성공은 1/8, 확대된 792-demo 같은 MLP는
다른 새 seed 12/16이었다. 공식 pretrained PPO의 대응 성공은 8/8, 16/16이나 RL
interaction data가 달라 equal-data 대안은 아니다. 16-seed 평가의 zero action은 0/16;
후속 BC 실패 4개 seed에서 PPO는 모두 성공했다. [원본·검산·분모](robotics/pilot_studies/q16-motion/README.md#pusht-demonstration-compatibility-2026-09-25)를 따른다.

**에이전트 판단:** 같은 관측에서 실행 가능한 단순 imitation과 강한 외부 policy 경로가
생겼다. 하지만 PPO는 현재 작은 native-state 조건에서 이미 포화됐고, 첫 BC 결과를 보고
확대한 두 번째 실험은 탐색이다. 다음 개발 관찰은 BC 실패 접촉 상태에서 단순 feedback,
기본 행동, 예측 기반 대안의 후보 행동과 실제 결과를 짝지어 비교하는 것이다. 이후 같은
추가 시연을 받는 정책 갱신과 비교해야 모델의 독립적 가치를 판단할 수 있다. 이 과업의
성공 grid만 확대하거나 시연 재생률을 감춘 채 positive prediction claim을 만들지 않는다.
Formal hypothesis/paper 승격은 없다.

## Q16 Paired Action Validity 2026-09-26

**Decision: 현재 `PushT-v1` native CUDA의 중간 행동 분기 경로를 인과 비교에 사용하지
않는다. Q16 질문은 `feasibility_study`로 유지하고 다른 평가 경로를 비교한다.**
[진단 owner](robotics/pilot_studies/q16-motion/README.md#paired-action-diagnosis-2026-09-26-exploratory-protocol-before-execution)에서
기존 792/88개 시연의 within-episode 전이로 행동 조건 one-step model을 학습했다.
검증 XY/yaw 오차는 각각 0.00131/0.00179 m, 0.01624 rad였지만, 이는 기록 시연의
예측 오차다. 사전에 정한 BC 실패 seed 네 개의 같은 접촉 상태에서 후보 행동을
비교하려던 세 번의 실행은 유효한 paired table을 만들지 못했다. 첫 실행은 기존
trace와 BC 행동이 달랐고, 두 번째는 새 reset의 BC 이력이 달랐으며, 세 번째는
저장한 물리·제어기 상태를 복원해도 반복 BC 결과가 달랐다. 실패한 실행과
모델·원본 trace는 보존했다.

**에이전트 판단:** 이전 BC 12/16 및 PPO 16/16은 관측과 과업 기준으로 유지하되,
이 branch 시도로 prediction의 행동 이득·무용성·원인을 판단할 수 없다. 모델
보정이나 동일 grid의 seed 확대보다, 학습 정책 실패와 안정적인 반복 행동 분기를
함께 제공하는 공개 접촉 과업/평가 경로를 작은 비용으로 비교할 가치가 높다.
그 경로가 잡히면 단순 feedback 및 같은 추가 시연을 받은 정책 갱신과 비교한다.
현재 `PushT-v1` branch의 실패를 Q16 연구 질문 전체의 반증으로 세지 않는다.

## Q16 Repeatable Contact-Action Route 2026-09-27

**사실:** 공개 `gym-pusht` 2D 과업과 Diffusion Policy의 206-episode 원본 시연을
별도 CPU Docker에서 사용했다. 두 사전 구성 접촉 사례에서 동일 행동을 반복한
분기가 1e-8 이내로 재현됐다. 공식 시연의 같은 5D state/2D target action으로
학습한 단순 ridge BC는 새 16개 초기 상태에서 성공 0/16, 접촉 16/16이었다.
그중 관찰 후 선택한 실패 두 곳의 BC 행동 분기는 다시 2/2 재현됐고, 한 행동의
변경은 T의 후속 위치를 2.28/30.98 px 바꿨다. 변경 행동의 overlap 효과는
두 사례에서 서로 다른 방향이었다. [원본·검산](robotics/pilot_studies/q16-motion/README.md#alternative-contact-task-assessment-2026-09-26-protocol-before-execution).

**선택 (`feasibility_study`):** 이 경로를 Q16의 다음 **개발용 접촉 행동 진단**으로
선택한다. 현재 native CUDA `PushT-v1`은 반복 분기가 실패했고, 기존 PushCube의
시험 조건은 단순 feedback이 포화됐으며 RollBall에는 학습 정책 비교 경로가 없다.
2D 경로는 낮은 추가 비용으로 실제 실패 상태의 후보 행동을 짝지을 수 있다.
하지만 ridge BC는 약한 초기 기준선이고 두 실패는 탐색용이다. 공개된 강한
Diffusion Policy checkpoint의 현지 실패, 예측 보정의 이점, 3D 일반화 또는
논문 기여는 관찰하지 않았다. robomimic Can은 더 비싼 3D 확인 과업 후보로 남긴다.
다음 관찰은 같은 두 상태에서 단순 feedback과 모델 기반 후보 선택의 실제 행동
결과를 비교하는 것이다. 모델 차별성이 없으면 강한 정책/Can 경로의 비용과 정보를
재비교한다. Formal hypothesis 또는 paper 단계로 승격하지 않는다.

## Q16 Action Selection Contrast 2026-09-27

**사실:** 기존 2D `gym-pusht` 개발 실패 48007/48010에서 같은 상태의 여섯 행동을
고정하고, 별도 160/20 episode로 학습·검증한 행동 조건 32-neighbor 전이 모델로
후보를 선택했다. 원본 시연의 다음 물체 XY 검증 RMSE는 1.68 px였지만, 모델
선택 행동의 실제 11-step overlap은 각각 0.4237/0.3511이었다. 단순 기하
feedback은 0.4237/0.3449, frozen BC는 0.3962/0.3714였다. 첫 모델 선택은
접촉 없이 feedback과 같은 끝점을 냈다. 둘째 모델 선택은 1-step 위치·각도
점수가 가장 좋았어도 native overlap에서 BC보다 나빴고, 변경 행동 예측 오차가
15.38 px였다. 모든 후보와 반복 대조가 독립 검산을 통과했다.
[원본·표·한계](robotics/pilot_studies/q16-motion/README.md#same-state-action-selection-contrast-2026-09-27-exploratory-protocol-before-execution).

**에이전트 판단:** 이 두 *사후 선택된 약한 BC 실패*에서 현재 모델/pose-score 조합의
독립적인 행동 선택 가치는 보이지 않는다. 기록 행동의 평균 예측 오차가 낮아도
변경 행동의 오차와 native overlap/후속 접촉의 불일치를 가릴 수 있다. 최고 후보는
사후 oracle이며 방법 성능이 아니다. 같은 seed에서 score·offset을 고쳐 양성 결과를
찾기보다, [공개 Diffusion Policy의 low-dimensional checkpoint](https://github.com/real-stanford/diffusion_policy/blob/main/README.md)를
먼저 같은 관측·행동·환경에 맞출 수 있는지 확인한다. 동일 과업의 강한 policy라
비용이 낮고 기준선 결함을 줄일 가능성이 있다. 해당 policy가 포화되거나 adapter
호환이 막히면 [robomimic Can](https://github.com/ARISE-Initiative/robomimic/blob/master/docs/datasets/robomimic_v0.1.md)의
더 큰 3D 대표성/실행 비용을 비교한다. 어느 외부 policy의 실패도 아직 현지에서
관찰하지 않았다. Q16은 `feasibility_study`; hypothesis/paper 승격은 없다.

## Q16 Released Policy Contact Contrast 2026-09-27

**사실:** 공식 low-dimensional Diffusion Policy Push-T checkpoint를 pinned 원본 source와
별도 Docker에서 실행했다. 20D visible keypoint 관측, 2D 절대 목표 행동, 8-step chunk와
100-step diffusion 설정을 checkpoint에서 확인했다. 원본/maintained 환경의 두 물리
사례는 위치·속도·coverage가 정확히 일치했지만, 한 사례의 접촉점 *개수*는 달랐다.
따라서 평가·진단은 원본 환경으로 통일했다. 새 초기 상태 49000–49007에서 공식 정책
성공 4/8, 같은 초기 상태의 5D ridge BC 0/8이었다. 16개 평가 trace의 원본 행동
재생 검산이 통과했다. 두 정책의 관측 표현·훈련 데이터·구조는 같지 않으므로
equal-data 비교가 아니다. [원본·계약·개별 결과](robotics/pilot_studies/q16-motion/README.md#released-low-dimensional-policy-compatibility-2026-09-27-protocol-before-execution).

**선택 (`feasibility_study` 유지):** 공식 정책도 접촉 후 최고 overlap 0.938–0.947에서
실패한 세 초기 상태가 있었다. 사후 규칙으로 고른 그중 두 곳의 동일 prefix/정책
반복 분기는 1e-8 이내로 재현됐고 여덟 branch trace가 독립 검산됐다. 49005의 한
행동 변경은 진단용 simulator-state feedback과 임의 +40 px offset 양쪽 모두 성공으로
바뀌었으며, 49006은 둘 다 실패했다. 이는 행동 선택이 결과를 바꾸는 개발 사례지만
prediction method의 이득이나 observation-only feedback의 성능은 아직 아니다.
현재 2D 경로에서 강한 학습 정책과 유효한 분기를 얻었으므로 즉시 3D Can으로
갈아탈 필요는 없다. 다음에는 policy가 실제 보는 keypoint에서 계산하는 고정
feedback과 행동 조건 예측 대안을 같은 후보·새 seed에서 비교하고, 동일 추가 데이터
정책 갱신·추론 비용을 대조한다. 3D Can은 대표성/전이 확인 후보로 유지한다.
Formal hypothesis/paper 승격이나 일반화 주장은 없다.

## Q16 Observation-Matched Policy Continuation 2026-09-27

**사실:** 공식 Diffusion Policy의 원본 Push-T 환경, 동일한 live 20D keypoint 관측,
동일 초기 상태 49100–49115와 고정된 한 행동 개입 규칙을 사용했다. 64개
trajectory의 독립 재생·native 성공·개입 전 동일 prefix 검산이 통과했다.
Frozen EMA, 관측 기반 기하학적 feedback, 행동 조건 예측 선택, 160개 시연을
사용한 300-step EMA 갱신의 성공은 각각 **8/16, 8/16, 8/16, 4/16**이다.
기하학적 feedback은 실패 하나를 구하고 성공 하나를 해쳤다. 예측 선택은
9개 near-goal gate 중 네 행동을 바꿨지만 성공/실패를 바꾼 사례가 없다.
정책 갱신은 validation diffusion loss를 낮췄으나 성공은 감소했다.
공식 저장 keypoint와 기록 state 사이에 일부 불일치가 발견되어 state-derived
재생성 입력은 폐기했고, 갱신은 원본 dataset class의 저장 keypoint 계약을
사용했다. [검증·표·자료 한계](robotics/pilot_studies/q16-motion/README.md#observation-matched-policy-continuation-2026-09-27-exploratory-protocol-before-execution).

**선택 (`feasibility_study` 유지):** 이 고정 2D 비교에서 현재 예측 모델의
별도 행동 가치는 관찰되지 않는다. 단순 correction도 순 성공 이득이 없으며
300-step 정책 갱신도 강한 대안이 아니다. 네 가지 실패가 near-goal gate에
들어오지 않았으므로 이 무차이를 Q16 전체 반증으로 확장하지 않는다. 이미 본
seed에서 threshold나 offset을 조정하는 대신, 공식
[robomimic Can 데이터](https://github.com/ARISE-Initiative/robomimic/blob/master/docs/datasets/robomimic_v0.1.md)와
[Diffusion Policy 경로](https://robomimic.github.io/docs/tutorials/training_diffusion_policy.html)의
version/schema/관측 정보, 재현 가능한 정책·feedback, 실행 비용과 새로운 실패
조건의 정보 가치를 먼저 조사한다. Can은 다른 3D pick-and-place 과업이므로
2D 결과의 확인 실험으로 세지 않는다. 확인 전 데이터 다운로드·대규모 학습은
선택하지 않고 formal hypothesis/paper 승격도 하지 않는다.

## Q16 Can Source and Data Feasibility 2026-09-27

**사실:** 최신 공식 Can PH low-dimensional 데이터는 robosuite `v1.5.1`로
생성됐고, pinned 46.9 MB HDF5를 별도 CPU Docker에서 검사했다. 200개
시연·23,207행에 `object` 14D와 robot pose/gripper를 합친 23D 관측,
7D delta OSC pose/gripper 행동, 71D simulator state 및 episode별 XML이
있다. [robomimic v0.5.0의 `reset_to`](https://github.com/ARISE-Initiative/robomimic/blob/v0.5.0/robomimic/envs/env_robosuite.py)는
XML·state 복원을 지원하지만 **실제 행동 재생 일치는 아직 검사하지 않았다.**
[공식 모델 목록](https://robomimic.github.io/docs/model_zoo/robomimic_v0.1.html)의
Can PH BC-RNN은 구형 `offline_study` 환경을 요구하고, 공개 Diffusion Policy
Can checkpoint도 `robomimic 0.2`/`free-mujoco-py` 의존성을 쓴다. 두 공개
checkpoint의 높은 nominal 점수는 외부 주장이고 현재 v1.5.1 데이터의
동일-runtime 성능이 아니다. [자료·runtime 감사](robotics/pilot_studies/q16-motion/README.md#3d-can-route-feasibility-2026-09-27-exploratory-protocol-before-data-access).

**선택 (`feasibility_study` 유지):** 3D grasp/placement는 2D pushing과 다른
접촉·회복 실패를 볼 가능성이 있고 데이터는 작아 확인 비용이 낮다. 그러나
Can PH의 23D 관측에는 물체 pose가 직접 포함되고 고전적인 목표 bin은
고정돼 있으며, 현재 source의 정책 성능·재생 반복성·물성 변화 민감도는
미측정이다. 따라서 **v1.5.1 source-matched 두 시연의 행동 재생과 동일 prefix
반복 검사 한 번**만 다음 관찰로 선택한다. 이것이 통과해도 policy·feedback의
동일 관측 대조와 사전 정의한 새 실패 조건이 필요하다. 검증 없이 공개 구형
checkpoint를 혼합하거나 대규모 학습으로 확대하지 않는다. Can의 nominal
무차이나 기술적 호환 실패를 Q16 전체 반증으로 취급하지 않는다.

## Q16 Can Action Replay Decision 2026-09-27

**사실:** 미리 정한 `demo_0`·`demo_1`의 첫 32개 행동을 robosuite `v1.5.1`
Docker에서 재생했다. XML과 `states[0]` 복원은 정확했고, `demo_0`의 동일 초기 상태
반복은 32스텝 state·관측에서 정확히 일치했다. 그러나 저장된 다음 state와의
최대 오차는 두 시연 모두 `19.44885`, 23D 다음 관측은 각각 `9.959e-4`·
`8.981e-4`였다. 두 시연의 모든 32스텝이 사전 기준 `state ≤1e-5`,
`observation ≤1e-4`를 넘었다. Raw-state 최대 오차는 선택되지 않은
`Cereal_joint0` 속도에서 나왔지만 Can joint 위치도 각각 최대 `8.464e-4`·
`7.963e-4` 차이가 있다. [행동 재생·joint 진단](robotics/pilot_studies/q16-motion/README.md#can-action-replay-protocol-2026-09-27-before-simulator-execution).
앞 32스텝의 native 성공 0회는 전체 episode 성공률이 아니다.

**선택 (`Can PH 현재 경로 hold`):** 내부 반복성은 충분하지만 데이터셋의
recorded-action parity는 frozen 기준에서 실패했다. 원인이 공개되지 않은
generator 의존성인지 controller/physics 차이인지는 식별되지 않았다. 따라서 이
Can PH 파일에 새 정책을 학습하거나 예측 보정 효과를 주장하는 투자를 진행하지
않는다. 구형 checkpoint와의 version mismatch도 그대로다. Q16 전체를 반증한
것은 아니며, 더 좁은 Can 파라미터 조정 대신 Q16의 과업/기준선 가능성과 다른
연구 후보의 정보 가치를 함께 재비교한다. 이 파일로 재진입하려면 전체 generator
의존성 또는 별도 사전 지정 replay 계약을 먼저 확보해야 한다.

## Q16 and Reserve Candidate Reassessment 2026-09-27

**비교의 목적:** Can PH의 재생 불일치를 더 작은 simulator tolerance를 찾아
우회하지 않고, 다음 한 번의 관찰이 실제 연구 선택을 바꿀 수 있는지 판단한다.
아래는 완료된 local 결과와 공개 source의 범위를 비교한 탐색 결정이다.
선행 논문의 성능은 재현 결과로 취급하지 않는다.

| 경로 | 다음에 배울 수 있는 것과 준비 상태 | 현재 제약·선택 |
| --- | --- | --- |
| Q16의 공식 low-dimensional Push-T 정책 | 원본 checkpoint·20D 관측·native 성공 판정·반복 가능한 2D 행동 재생이 확보됐다. 16개 새 seed의 frozen/단순 feedback/예측 선택은 모두 8/16이고, 고정 교정 규칙은 frozen 실패 8개 중 4개에만 들어왔다. 같은 정책의 실행 chunk를 짧게 하면 이 실패가 단순 재계획 빈도로 설명되는지 직접 볼 수 있다. | **한 번의 고정 대조 선택.** 새 seed에서 8-step 실행과 2-step 실행만 비교한다. 이는 방법 후보가 아니라 Q16 투자의 강한 단순 대조다. |
| Q16의 기존 PushCube-v1·PushT-v1·RollBall-v1 | PushCube는 단순 feedback이 두 물성 조건에서 포화됐고, 원본 CUDA PushT-v1의 현재 중간 행동 분기는 반복 BC 대조가 달랐다. RollBall에는 관측 동일 학습 정책 경로가 없었다. 원본 PushT-v1의 공개 PPO는 이전 새 seed에서 16/16으로 실패 진단 여지가 작았다. | 같은 simulator parameter/seed 확대나 유효하지 않은 분기 복구를 우선하지 않는다. 새 과업을 만들기보다 현재 source-matched 강한 2D 정책의 단순 대조가 더 싸다. |
| Q16의 Can PH v1.5.1 | 3D grasp/placement라는 다른 대표 과업이나 저장 행동의 다음 state·정책 관측 parity가 사전 기준에서 실패했다. 같은 runtime의 검증된 강한 checkpoint도 없다. | 현재 데이터로 policy 학습·예측 효과 판단 보류. Generator 계약이 확보될 때만 재진입. |
| 공개 VLA/3D benchmark | [LeRobot v0.6.0](https://github.com/huggingface/lerobot/releases/tag/v0.6.0)은 여러 benchmark에 Docker·SmolVLA baseline을 제공하고 [LIBERO-plus](https://github.com/huggingface/lerobot/blob/v0.6.0/docs/source/libero_plus.mdx)에 source-matched 평가 경로가 있다. 그러나 일곱 변화 축은 주로 시각·배치·초기 상태로, Q16의 물체 운동/접촉 변화와 같지 않다. [LIBERO-plus](https://arxiv.org/abs/2510.13626)는 일반적인 취약성을 이미 조사했고 [Feedback World Model](https://arxiv.org/abs/2605.15705)은 그 benchmark에서 prediction feedback을 평가했다고 보고한다. | 시의성·접근성은 높지만 이 자료로 같은 feedback 주장을 반복하지 않는다. 새 질문과 비교 조건이 생기면 독립적으로 검토한다. |
| Q12 generated geometry / Q13 active perception | 3D 관측과 로봇 행동을 연결할 잠재력은 있으나 Q12는 검증된 geometry-to-action 대조, Q13은 matched checkpoint·matched-state 사례가 아직 없다. | 지금 추가 setup보다 각 재진입 조건을 충족하는 구체적 관찰이 먼저다. |
| Q15·Q3·Q4·Q8·CD1 및 나머지 reserve | 각 현재 경로는 단순 대안의 충분성, 직접 선행, label/replay 또는 counterfactual 자료 부족을 기록했다. CD5는 별개로 사용자 요청에 따라 보류 중이다. | 같은 seed/grid/자료 정리의 반복은 선택하지 않는다. 각 질문의 재진입 조건 유지. |

**선행과 경계:** [Diffusion Policy 원본](https://github.com/real-stanford/diffusion_policy/blob/main/README.md)은
action chunk 기반 정책·Push-T 경로를 제공한다. 더 잦은 재계획이나 adaptive chunking
자체도 [RA-DP](https://arxiv.org/abs/2503.04051),
[PACE](https://arxiv.org/abs/2606.00537),
[DVAC](https://arxiv.org/abs/2606.03847)의 범위다.
따라서 다음 대조에서 짧은 chunk가 성공해도 이를 신규 방법으로 제시하지 않는다.
Q16의 기존 `8/16`은 작은 탐색 결과이며, 짧은 chunk의 결과를 보고 기존 16개
seed나 frozen 판정을 소급 조정하지 않는다.

**선택 (`feasibility_study` 유지):** 공식 2D checkpoint의 새 paired 초기 상태
16개에서 **원래의 8-step 실행과 같은 8-step 예측의 첫 2개 행동만 실행한 뒤
다시 관측·계획하는 2-step 실행**을 한 번 비교한다. 상세한 seed, 관측·행동 계약,
검산과 비용 기록은 [Q16 study](robotics/pilot_studies/q16-motion/README.md#shorter-action-chunk-comparison-2026-09-27-prospective-protocol)가
소유한다. 2-step의 순구제가 있어도 현재 prediction rule의 기여는 아니며,
이 경우 단순 재계획을 Q16의 필수 대조로 둔다. 순구제가 없으면 같은 2D
offset/gate/model/seed 탐색을 종료하고 Q16을 보류할지 새 대표 과업이 있는지
재비교한다. 어느 결과든 이 2D 경로를 자동으로 formal hypothesis나 paper
experiment로 승격하지 않는다.

## Q16 Shorter Chunk Outcome and Investment Decision 2026-09-28

**사실:** 사전 지정한 공식 low-dimensional Diffusion Policy의 새 seed 49200–49215에서
원래 8-action 실행은 native 성공 7/16, 같은 8-target 예측의 앞 2-action만 실행하고
재계획한 경로는 6/16이었다. 2-action 경로는 실패 2건을 구제하고 성공 3건을
악화했다. 동일 초기 상태·첫 두 행동/상태와 32개 저장 궤적의 독립 재생 검증이
통과했다. 2-action 경로는 총 정책 호출 1,998회와 추론 496.05초로,
8-action의 480회·118.53초보다 각각 약 4.16배·4.19배 들었다.
[원본 결과·한계](robotics/pilot_studies/q16-motion/README.md#shorter-action-chunk-comparison-2026-09-27-prospective-protocol)를
따른다. 이는 한 2D 과업의 작은 탐색 split이며, 더 잦은 재계획 일반이나 Q16
전체의 효과에 대한 결론이 아니다.

**판단 (`deferred`):** 순구제가 없어 사전 중단 조건에 따라 이 shorter-chunk 경로를
종료한다. 앞선 동일 관측 예측 선택도 frozen 정책·단순 feedback 대비 고유 성공 이득이
없었으므로 같은 2D gate, offset, predictor, seed의 재조정에 추가 투자하지 않는다.
Can PH 자료 경로는 저장 행동 재생 parity 실패로 보류 상태다. 이 처분은 현재
방법·자료 경로의 투자 보류이며 예측 기반 정책 적응이라는 넓은 질문을 반증하거나
종료하지 않는다. Q16 재진입에는 **단순 관측 피드백·재계획이 설명하지 못하는
대표 실패 조건**, 같은 정보의 강한 정책 대안, 타당한 paired 평가와 제한된 비용이
함께 필요하다. 현재 그 구체적 조건이 없어 formal hypothesis로 선택하지 않는다.

**다음 비교:** 기존 reserve의 재진입 조건과 새 Robotics/cross-domain 방향을 함께
검토한다. 후보의 중요성·시의성, 가까운 선행과 구분할 잠정 설명, 작은 관찰의
정보 가치/비용을 비교한 뒤 하나의 다음 연구 질문을 고른다. CD5의 사용자 보류와
기존 후보의 frozen 판정은 그대로 유지한다. 준비가 쉬운 후보라는 이유만으로
Q16을 즉시 다른 단일 toy task로 옮기지 않는다.

## Q17 Selection 2026-09-28

**비교:** Q16의 현 2D/Can PH 경로가 보류된 상태에서 다음 연구 질문을 하나 고른다.
시의성·중요성은 단독 선정 근거가 아니며, 가까운 선행과 비교해 배울 수 있는 첫 관찰과
준비 비용을 함께 본다. 아래 source 주장은 각 공식 논문·artifact에 근거하고, 선택은
에이전트의 잠정 투자 판단이다.

| 방향 | 시의성·정보 가치 | 현재 제한 |
| --- | --- | --- |
| Q13 action-relevant view / Q9 spatial-memory refresh | 어느 정보를 새로 보거나 보존할지 중요한 결정이다. | DISaM·ActiveVLA·SaPaVe 및 Memory for Attention·ActiveArena가 가까운 질문을 다룬다. Q13의 matched action-value 경로, Q9의 단순 schedule과 다른 관찰은 아직 확보되지 않았다. 기존 재진입 조건 유지. |
| Q16 predictive adaptation / Q7 failure-source transfer | 정책 실패와 실행 오류를 다룰 수 있다. | Q16의 현재 2D 대조는 순구제가 없고 Can PH 재생은 불일치했다. Q7의 source-transfer에는 task-state와 construction의 인과적 분리가 필요하다. 같은 실행 반복으로 해결되지 않는다. |
| CD1 intervention value 및 다른 cross-domain reserve | 실패 판정을 실제 행동 가치로 연결할 수 있다. | 같은 상태의 retry/replan/defer 결과 자료가 없고 TDQC 등 직접 선행이 있다. CD5는 사용자 보류이므로 선택 대상에서 제외한다. |
| **새 Q17 evidence-conditioned action selection** | [ActiveArena](https://arxiv.org/html/2609.24124)는 정보 획득·기억·실행을 잇는 35개 과업과 최근 공개 [simulator](https://github.com/leeibo/ActiveArena), [정책 코드](https://github.com/leeibo/ActiveArena-VLA), [task별 데이터](https://huggingface.co/datasets/leeibo/ActiveArena-Data)를 제공한다. 저자의 실패 분해는 downstream reasoning과 execution이 섞인 상태를 드러내므로, 정보 확보 이후의 **목표 선택과 실행을 분리**하는 한 과업의 작은 관찰이 다음 방법 선택을 바꿀 수 있다. | `Context Retained`는 정보 획득의 증명이 아니다. 공개 LeRobot 자료에 논문의 rich HDF5 annotation이 그대로 있는지는 미확인이다. 공식 모델은 별도 base model과 약 4.97 GB checkpoint가 필요하며 Docker/simulator 동작은 아직 검증되지 않았다. [PALM](https://arxiv.org/abs/2601.07060)과 ActiveArena의 subtask/planner 대조가 가까운 선행이다. |

**선택 (`Q17 feasibility_study`):** 다음 질문은
[Evidence-Conditioned Action Selection](robotics/questions/evidence-conditioned-action-selection.md)으로
한다. 능동적 관찰로 얻은 단서가 다음 조작 대상·목표·행동에 반영되는지를 묻되,
오류의 존재와 원인을 미리 가정하지 않는다. 첫 경로는 hidden-color 조작 한 과업의
annotation/평가 계약과 소수의 같은 상태 대조다. 정보가 충분한지, 목표가 틀렸는지,
목표는 맞고 제어가 실패했는지를 가를 수 있어야 한다. 35-task 재현이나 전체 dataset
취득을 먼저 하지 않는다. Q13/Q9/Q7과 공유되는 자료는 있을 수 있지만 질문·기존 판정은
합치거나 소급 수정하지 않는다. Formal hypothesis, method contribution과 paper 승격은 없다.

## Q17 Task-Family Reassessment 2026-09-29

**Source 사실:** 같은 color-count ID `100000`에서 정답을 조기에 문장으로
제공해도 2번 버튼 press가 유지됐다. 이는 목표 선택과 실행의 원인을 가르지 못한다
([case 기록](robotics/pilot_studies/q17-evidence/README.md#earlier-answer-cue-decision-point-2026-09-28)).
[공식 과업 분류](../external/q17-activearena/docs/task_categories.md)는
`match_backside_two_blocks`와 `rank_backside_rgb_blocks`를 IA,
`blocks_ranking_rgb_rotate_view`를 ML, `count_target_press_button`을 MD로 둔다.
[IA source](../external/q17-activearena/envs/_match_backside_blocks.py)는 블록을
집어 뒷면을 확인한 뒤 맞는 pad에 놓으며 최종 성공은 각 블록 중심의 pad 포함 여부다.
따라서 이전 hidden-color 사례의 단서 획득 전 실패를 더 긴 조작으로 다시 만날
가능성이 높다. [MD sibling source](../external/q17-activearena/envs/count_target_press_button.py)는
녹색 블록 개수를 세어 1/2/3 버튼을 누르고 오답 버튼을 별도로 판정하므로,
답/버튼 계약이 기존 color-count와 실질적으로 같다.

**다른 과업군:** [ML source](../external/q17-activearena/envs/blocks_ranking_rgb_rotate_view.py)는
회전 시점에서 green 블록을 찾고 집은 다음 red의 오른쪽에 놓고, blue도 같은 방식으로
처리한다. 단계별 `search_target_keys`와 `action_target_keys`는 명시돼 있고 최종
성공은 세 블록의 상대 배치와 열린 gripper로 판정한다. 그러나
[공식 instruction](../external/q17-activearena/description/task_instruction/blocks_ranking_rgb_rotate_view.json)은
색·순서를 이미 이름으로 알려 준다. 이 과업은 **새로 획득한 색의 추론**이 아니라
시점 이동으로 발견한 물체를 첫 조작 대상으로 연결하는 경우에만 Q17에 유효하다.
집기 실패와 목표 물체 오인도 첫 동작에서 별도로 판독해야 한다.
[공식 ID manifest](../external/q17-activearena/eval_seed_lists/info_gathering_demo/blocks_ranking_rgb_rotate_view.json)의
첫 seed는 `100000`이다. [공식 평가 설정](../external/q17-activearena/README.md#evaluation)은
`info_gathering_demo`를 ID, `info_gathering_randomized`를 OOD로 정의한다.

| 비교 방향 | 지금 줄일 수 있는 불확실성 | 비용·가까운 대안 |
| --- | --- | --- |
| Q17 IA 두 블록/세 블록 | 숨은 색을 확인한 후 pad를 고르는지 | 집기·뒤집기 선행 장벽이 현재 세 사례보다 커진다. 우선순위 낮음. |
| Q17 MD count sibling | 정답 수와 물리 버튼의 불일치 | 같은 버튼 과업의 counting/언어/실행 모호성을 반복한다. 우선순위 낮음. |
| **Q17 ML 회전 시점** | 새 시점에서 찾은 물체가 첫 집기 대상이 되는지 | 기존 simulator·정책 경로를 재사용할 수 있다. 첫 화면에 이미 보이면 Q13의 시점 선택이나 일반 visual grounding과 구분하기 어렵다. |
| Q13/Q9 active view·memory | 관찰 선택·갱신 자체의 효과 | [ActiveVLA](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_ActiveVLA_Injecting_Active_Perception_into_Vision-Language-Action_Models_for_Precise_3D_CVPR_2026_paper.html), [SaPaVe](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_SaPaVe_Towards_Active_Perception_and_Manipulation_in_Vision-Language_Action_Models_CVPR_2026_paper.html), [HALO](https://www.roboticsproceedings.org/rss22/p010.html)가 가까우며 기존 matched action-value/단순 대조 재진입 조건은 아직 없다. |
| Q16 predictive adaptation / CD1 intervention value | 동역학·행동 비용을 다루는 더 넓은 질문 | Q16 현재 2D 효과·3D replay 계약이 막혔고, CD1은 같은 상태의 여러 intervention outcome이 없다. 기존 판정을 유지한다. |

**선행과 추론:** [ActiveArena](https://arxiv.org/abs/2609.24124)는 memory,
subtask supervision, planner-guided decision을 이미 비교하고
[PALM](https://arxiv.org/abs/2601.07060)은 object relevance·subtask progress를
다룬다. 따라서 첫 물체를 찾아 집는 성공만으로 Q17의 차별화나 새 방법 필요성을
주장할 수 없다. 현재 선택은 유망한 큰 방향에 대한 **저비용 판별 관찰**이며
formal hypothesis 선정이 아니다.

**다음 한 경로 (`Q17 ML screen`):** 공식 ID seed `100000` 하나에서 초기 정책
입력과 회전 후 입력의 green/red/blue 가시성을 먼저 판독하고, 공개 OFT 정책의
첫 green 집기 시도까지 물체 identity·실제 접촉/집기와 입력을 기록한다.
처음부터 green이 보이거나 모델이 탐색·집기까지 가지 못하면 이 경로로
정보 획득→목표 결합을 주장하지 않고 다른 질문을 재비교한다. 처음에는 보이지
않고 회전 뒤 보인 상태에서 잘못된 물체로 접근하거나 집으면 그때만 같은 상태의
단순 task-text 목표 위치 단서(oracle 진단) 대조 가치가 생긴다. 기존 OFT bridge는 subtask text를
행동 prompt로 쓰지 않으므로 subtask 문장만 바꾸는 대조는 선택하지 않는다.
단일 사례 결과를 빈도나 방법 효과로
일반화하지 않는다. 새 dataset·checkpoint 학습 없이 기존 workspace 전용 Docker와
고정 checkpoint로 짧게 관찰한다. IA/MD 확대, Q16 seed/grid 반복, CD5 실행은
선택하지 않는다.
