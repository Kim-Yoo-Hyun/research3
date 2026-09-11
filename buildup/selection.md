# Research Question Selection

Updated: 2026-09-11

## Decision Boundary

이 문서는 [`docs/buildup.md`](../docs/buildup.md) Stage 7 selection decision을 누적한다.
Entry criteria와 연구를 계속할 가치에 대한 판단을 구분한다. Criterion을 충족한다고
자동으로 question을 선택하지 않으며, final architecture·second dataset·publication-ready
novelty를 hypothesis entry의 추가 필수조건으로 만들지 않는다.

최신 Stage 7 처분은 [Q11 — discontinue current route](#q11--discontinue-current-route-2026-09-10)다.
Stage 3의 문헌 검토 순서는 [Q12 → Q13](#reserve-review-priority-2026-09-10)이다.
[Q12 Stage 4–5 검토](#q12-stage-45-assessment-2026-09-10)와
[Q13 Stage 4–5 검토](#q13-stage-45-assessment-2026-09-10)는 완료했다.
[후속 비교](#q12q13-measurement-selection-2026-09-10)에서 Q12의 작은 입력 검증 준비를 선택하고
Q13은 `deferred`로 두었다. Hypothesis나 실행 결과에 대한 Stage 7 판정은 아니다.
이후 [Q12 input protocol 준비](#q12-input-protocol-preparation-2026-09-10)와
[실제 입력 검증](#q12-input-audit-outcome-2026-09-10)을 완료했다. 이후
[model 준비](#q12-model-readiness-preparation-2026-09-10)를 마치고
[실제 completion 출력 검증](#q12-completion-output-outcome-2026-09-11)을 통과했다. 다음은
native parity·physical/camera 연결 경로의 비용·정보 가치 비교다.
아래 Q1/CD4/CD1 비교는
2026-09-04의 기록이며 Q1 실행 재개나 현재 독점 우선순위를 뜻하지 않는다.

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
