# CD1 Intervention-Value Calibration

Updated: 2026-09-04

## Status

`deferred`

Stage 7 decision은 `refine`이다. Named sequential system, finite intervention set,
common cost unit과 counterfactual evaluator를 공개 artifact로 고정할 수 있을 때만
다시 진행한다.

## Facts

- 이 workspace에서는 sequential intervention dataset이나 simulator를 아직 실행하지
  않았다.
- 한 장의 workstation GPU와 6개월 일정 안에서 frozen trace 또는 lightweight
  simulation을 우선해야 한다.
- 현재 candidate에 선택된 benchmark, policy와 intervention cost는 없다.

## Source Claims

- [TDQC](https://arxiv.org/abs/2604.20472)는 sequential Brier score와 value function을
  연결하고 calibrated VLA success predictor를 conformal early stopping 및 simulator-guided
  action search에 적용한다.
- ICLR 2026 [Epistemic UQ for Decisions](https://proceedings.iclr.cc/paper_files/paper/2026/hash/51b3bf54f2a06c3c844b09d20b70eadb-Abstract-Conference.html)는
  calibration metric이 grouping loss를 놓침을 보이고 excess decision risk로 LLM cascade
  deferral을 개선한다.
- [Utility-Directed Conformal Prediction](https://arxiv.org/abs/2410.01767)은 downstream
  cost를 반영하는 prediction set을 제안한다.

## Agent Inference

Broad premise는 recent prior에 점유됐다. 아직 미확인인 부분은 하나의 frozen sequential
system에서 detector/information을 고정하고 `retry / replan / defer` 여러 action을 같은
budget으로 비교할 때 metric ordering과 realized utility ordering이 뒤집히는지다.

## Research Question Or Suspected Phenomenon

Frozen agent/robot trajectories에서 같은 intervention budget을 줬을 때 ECE/AUROC가 더
좋은 monitor가 실제 cost-adjusted downstream success도 더 높이는가?

## Significance

Monitor 연구를 detection metric에서 실제 closed-loop decision utility로 연결한다.
괴리가 재현되면 “confidence를 높였다”는 결과와 “system을 더 안전하거나 성공적으로
만들었다”는 결과를 구분할 수 있다.

## Current State Of The Art And Limitation

Decision-aware uncertainty와 cost-sensitive deferral뿐 아니라 sequential VLA early stop 및
action search도 이미 다뤄졌다. 남을 수 있는 gap은 frozen sequential system의 **multiple
intervention actions**를 matched cost와 horizon 아래 비교하는 것으로 좁혀진다. 상세 근거는
[preliminary prior audit](../related_work/cd1-intervention-value-calibration.md)에 있다.

## Evaluation Target

- primary: fixed intervention-rate 또는 cost budget에서 final task success minus action cost
- secondary: regret to privileged intervention oracle, coverage-risk curve, latency
- diagnosis: ECE/AUROC ordering과 intervention-utility ordering의 pairwise reversal
- denominator: traces × monitors × intervention actions × preregistered cost settings

## Available Data / Code / Evaluator

TDQC/SAFE code와 일부 rollout data는 공개됐지만, alternative retry/replan/defer outcome을
같은 state에서 비교할 counterfactual log는 확인하지 못했다. Public simulator에서 이를
새로 생성하려면 VLA inference와 state restore가 필요하며 resource 확인 전에는 실행하지
않는다.

## Simplest Baseline Or Counterexample

1. raw confidence threshold;
2. temperature/isotonic calibration 후 threshold;
3. remaining-horizon 및 fixed action-cost heuristic;
4. tabular dynamic programming 또는 empirical expected-value lookup;
5. TDQC Q-value-guided action selection;
6. privileged best-action oracle.

Cost-sensitive threshold나 lookup이 oracle gap을 대부분 제거하면 learned method를 만들지
않는다.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| public trace에서 intervention outcome을 측정할 수 있다 | alternative action replay가 불가능하다 | artifact/API audit |
| detector ranking과 utility ranking이 다르다 | 모든 cost/horizon에서 순위가 같다 | 작은 logged subset cost sweep |
| simple cost-aware rule 뒤 residual이 남는다 | lookup/DP가 oracle에 근접한다 | tabular baseline |

## Feasibility Or Pilot Study

Public multi-action counterfactual denominator가 확인되지 않아 protocol을 고정하지 않는다.
Stage 7의 `refine` 결정에 따라 reactivation condition이 충족된 경우에만 exact
input/output/metric과 disconfirmation rule을 먼저 작성한다.

## Preliminary Success Criteria

- detector metric ordering과 downstream utility ordering의 statistically stable reversal;
- strongest simple cost-aware baseline 뒤 practical oracle regret가 남음;
- residual의 원인이 state-dependent intervention value와 연결됨.

## Expected Deliverable

Detector-versus-decision utility matrix, cost/coverage curve, failure regimes와 question
selection decision.

## Timeline And Milestones

- completed: nearest primary papers와 official artifact audit
- finding: broad premise의 overlap과 narrow residue의 public denominator 부재 확인
- completed: Q1/CD4와 Stage 7 비교 후 `refine` 결정
- deferred: trace/intervention/cost denominator를 갖춘 public artifact 확인
- reactivation 시에만 exact protocol과 timeline 작성

## Interpretation Of A Negative Result

Calibration quality가 intervention utility를 일관되게 예측하거나 simple expected-value
lookup이 oracle gap을 제거하면 candidate를 종료한다. 이는 별도 learned controller가
필요 없다는 유용한 결과다.

## Resource Requirements

Public trace/replay environment, CPU 중심 analysis와 필요 시 짧은 single-GPU inference.
Human annotation과 real robot은 필요하지 않다.

## Related-Work Overlap

`high`. [Preliminary prior audit](../related_work/cd1-intervention-value-calibration.md)에서
calibration insufficiency, cost-aware deferral, sequential VLA early stopping/action search의
직접 overlap을 확인했다. Multi-action/cost-matched residue만 미확인이다.

## User Decision Needed

없음. Reactivation condition을 만족하기 전에는 진행하지 않는다.
