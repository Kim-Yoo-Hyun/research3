# Cross-Domain Research Buildup

Updated: 2026-09-04

## Status

`active_scoping`

이 scope는 Robotics를 출발점으로 유지하되 연구 질문의 원리를 Robotics에 가두지
않는다. 6개월, 공개 benchmark, 한 장의 workstation GPU, simulation/dataset-first,
foundation-scale training 제외라는 실행 경계는 그대로 적용한다.

## Gap-First Abstraction

최근 benchmark와 agent/robot 연구를 가로질러 반복되는 문제는 다음과 같다.

1. 최종 scalar score는 evaluator specification과 temporal aggregation에 의존한다.
2. confidence와 diagnosis는 실제 retry/replan/defer 행동의 가치와 동일하지 않다.
3. 저비용 adaptive evaluation은 평균 순위를 보존해도 희귀한 failure mode를 놓칠 수
   있다.
4. trajectory의 관찰적 failure label은 그 요인이 실패 원인이라는 반사실적 증거가
   아니다.
5. richer representation의 이득은 추가 정보량, compute와 interface 변화에서 올 수
   있어 “representation form”의 이득과 혼동된다.

이들은 새 architecture보다 먼저 frozen outputs/trajectories에 대한 matched control,
simple baseline과 oracle test로 기각할 수 있는 gap이다.

## Candidate Registry

| ID | candidate | core gap | status |
| --- | --- | --- | --- |
| CD1 | [Intervention-Value Calibration](questions/intervention-value-calibration.md) | calibrated confidence does not imply useful retry/replan/defer decisions | `deferred` |
| CD2 | [Tail-Preserving Efficient Evaluation](questions/tail-preserving-efficient-evaluation.md) | rank-efficient sampling may erase rare failure coverage | `exploratory` |
| CD3 | [Temporal Outcome Semantics](questions/temporal-outcome-semantics.md) | first-hit, terminal and sustained success may support different conclusions | `deferred` |
| CD4 | [Counterfactual Failure Attribution](questions/counterfactual-failure-attribution.md) | trajectory diagnosis is correlational without minimal replay interventions | `deferred` |
| CD5 | [Information-Budgeted Representation Utility](questions/information-budgeted-representation-utility.md) | structured/raw representation comparisons often mismatch information budget | `exploratory` |

## Recent-Prior Anchors And Collision Warnings

- NeurIPS 2024 [Collaborative Computerized Adaptive Testing](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ad48f017e6c3d474caf511208e600459-Abstract-Conference.html)
  directly addresses adaptive testing for ranking consistency. CD2 must add tail-failure
  preservation rather than claim efficient ranking itself.
- NeurIPS 2024 [Easy2Hard-Bench](https://proceedings.neurips.cc/paper_files/paper/2024/hash/4e6f22305275966513990f53cec908e0-Abstract-Datasets_and_Benchmarks_Track.html)
  supplies difficulty-aware evaluation prior. Difficulty stratification is a baseline for
  CD2, not a contribution.
- 2026 [TDQC](https://arxiv.org/abs/2604.20472) already connects sequential calibration to
  conformal early stopping and simulator-guided action search. ICLR 2026
  [Epistemic UQ for Decisions](https://proceedings.iclr.cc/paper_files/paper/2026/hash/51b3bf54f2a06c3c844b09d20b70eadb-Abstract-Conference.html)
  also shows that calibration-only risk can be decision-suboptimal for cost-aware deferral.
  CD1's broad premise is therefore occupied.
- 2025 [AgenTracer](https://arxiv.org/abs/2509.03312), 2026
  [Causal Agent Replay](https://arxiv.org/abs/2606.08275) and
  [AgenticRAG-FP](https://arxiv.org/abs/2608.20627) directly use intervention and downstream
  re-execution for causal failure attribution. CD4's current core is a direct collision.
- ManiSkill distinguishes `success_once` and `success_at_end` and exposes per-step success.
  This makes CD3 executable but also turns it into a direct generalization of active Q1,
  so it is not a separate project yet.

These are collision anchors from the completed preliminary review, not a complete novelty audit.

## Comparative Assessment

`H/M/L`은 높음/중간/낮음이며 overlap만 H가 위험하다.

| candidate | significance | empirical access | feasibility | information | resource fit | depth | overlap | rigorous path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CD1 intervention value | H | M | M | H | H | H | H | M |
| CD2 tail-preserving eval | H | H | H | H | H | M | H | H |
| CD3 temporal semantics | M | H | H | H | H | M | H | H |
| CD4 causal attribution | H | M | M | H | H | H | H | M |
| CD5 information budget | H | M | M | H | M | H | H | M |

### Evidence Behind The Ratings

- **CD1:** frozen trace로 detector와 decision utility를 비교할 수 있어 informational
  value와 resource fit은 높지만 counterfactual outcome artifact와 exact-prior residue가
  미확인이다.
- **CD2:** full score matrix가 있으면 offline resampling만으로 실행 가능하나 efficient
  ranking prior가 강하고 simple stratification으로 끝날 수 있어 depth는 중간이다.
- **CD3:** ManiSkill evaluator로 쉽게 측정되지만 Q1과 거의 같은 질문이라 overlap이 높다.
- **CD4:** diagnosis의 actionable validity를 직접 검증해 depth가 높지만 exact replay와
  local intervention interface가 없으면 empirical access가 낮아진다.
- **CD5:** Robotics와 RAG를 잇는 일반성은 있으나 same-information control과 첫
  accessible evaluator를 구성하기 어렵다.

## Stage 3 Preliminary Priority

1. **CD4 Counterfactual Failure Attribution** — 가장 강한 scientific question이다.
   기존 diagnosis score가 실제 cause인지 최소 intervention으로 반증할 수 있다. 단,
   executable replay artifact가 핵심 feasibility uncertainty다.
2. **CD1 Intervention-Value Calibration** — 가장 싼 kill test 후보다. 기존 prediction과
   trace만으로 confidence calibration과 actual intervention utility의 괴리를 볼 수 있다.
   다만 decision-focused/conformal prior가 강해 sequential setting의 exact novelty를
   먼저 확인해야 한다.
3. **CD2 Tail-Preserving Efficient Evaluation** — 공개 score matrix가 있으면 즉시
   실행되지만 stratified sampling으로 해결될 가능성이 높다. 그 경우 좋은 negative
   result로 종료한다.
4. **CD5 Information-Budgeted Representation Utility** — Robotics/3D와 RAG/agent를
   잇지만 fair information matching이 어렵고 direct prior가 많다.
5. **CD3 Temporal Outcome Semantics** — 독립 question으로 선택하지 않고 Q1과의 중복을
   해소할 때까지 deferred한다.

## Stage 4 Preliminary Review Result

- **CD4:** [Focused audit](related_work/cd4-counterfactual-failure-attribution.md)에서
  AgenTracer, Causal Agent Replay와 AgenticRAG-FP가 single-step intervention,
  downstream re-execution과 outcome-based attribution이라는 현재 core를 이미 점유함을
  확인했다. Continuous-control intervention validity만 possible residue이며 public
  denominator는 아직 없다.
- **CD1:** [Focused audit](related_work/cd1-intervention-value-calibration.md)에서 TDQC가
  sequential calibration을 early stop/action search에 연결하고, ICLR 2026 work가
  calibration-only decision risk와 cost-aware deferral을 직접 다룸을 확인했다. 같은
  sequential state에서 multiple intervention actions를 cost-match하는 residue만 남았지만
  public counterfactual artifact는 아직 없다.
- 두 후보 모두 broad framing으로는 hypothesis formulation에 넘길 수 없다. Stage 7에서
  CD4는 `reformulate`, CD1은 `refine`으로 판정했으며 둘 다 `deferred`다.

## Stage 7 Selection Result

[Cross-scope selection decision](../selection.md)에서 CD4는 direct collision 때문에
`reformulate`, CD1은 executable multi-action denominator가 없어 `refine`으로 판정했다.
두 candidate 모두 status는 `deferred`이며 reactivation condition을 만족하기 전에는
feasibility protocol을 만들지 않는다.

## Current Decision

Cross-domain candidate 중 `ready_for_hypothesis`는 없다. CD1/CD4와 CD3는 `deferred`,
CD2/CD5는 `exploratory`다. `PaperReview`는 read-only로만 참조했고 수정하지 않았다.
