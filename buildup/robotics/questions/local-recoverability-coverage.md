# Local Recoverability Coverage

Updated: 2026-09-08

## Status

`under_review`

Stage 7 decision: `refine`. 다음 Stage 6 후보는 Q1이며, 현재 PPO/pre-contact grid의
확대는 중단한다. [반복 검증](../pilot_studies/q8-recoverability/README.md#final-verified-results)과
[Q8/Q1 비교](../../selection.md#q8q1--stage-6-selection-2026-09-08)가 최신 근거다.

## Current Assumption Assessment — 2026-09-08

| Assumption | Current evidence | Decision boundary |
| --- | --- | --- |
| Q8-A restore | fresh scene + prefix 450/450 next-step checks; full zero control 9/13 groups pass; public demo middle-state replay 0/18 pass | selected prefix fixture만 supported; arbitrary demonstration restore는 미확립 |
| Q8-B perturbation validity | unchanged AABB/support/velocity/phase rules로 312 중 144 admitted | pre-contact subset만 지원; expert action equality나 general solvability는 요구/주장하지 않음 |
| Q8-C recovery target | fixed-horizon official success는 재현 가능하지만 scalar는 empirical success와 동일 | return-to-demonstration 또는 transfer target 없이 새 construct라고 주장할 수 없음 |
| Q8-D profile | full-zero-qualified 98/98 rows (nonzero 89) 모두 성공, 3 process 동일 | tested route uninformative; 실패를 얻기 위한 radius/seed 탐색 금지 |
| Q8-E independent prediction | separate draws만으로 같은 conditional probability의 두 추정량 문제가 해결되지 않음 | episode-group mapping과 distinct perturbation-family target이 필요 |
| Q8-F residual | equal-budget empirical success baseline과 scalar identity; training-data-linked density/loss 미확립 | residual을 측정하거나 발견했다고 주장하지 않음 |
| Q8-G resource | bounded v2 process 약 75--77초; new Docker/CPU physics 가능, GPU graphics dependency 해결 | small fixture feasible; second task/general VLA route는 미검증 |

사실은 위 execution/verification 결과다. Q8 재정의와 Q1 우선순위는 그 근거에 따른
에이전트 판단이며 Q8의 일반적 불가능성이나 Q1의 논문 novelty 확정이 아니다.

## Facts

- Public simulators can reset object and robot state near demonstration trajectories.
- Nominal demonstration diversity does not directly measure whether a learned policy returns to
  task progress after a nearby state perturbation.

## Source Claims

- RSS 2025 [Demo-SCORE](https://www.roboticsproceedings.org/rss21/p071.html) uses online policy
  experience to filter unreliable demonstration strategies and improves downstream policy success.
- [Not All Errors Are Made Equal](https://proceedings.mlr.press/v270/nakamura25a.html) finds that
  high downstream-regret interaction data can be more informative than the full deployment set.
- RSS 2024 [Data Collection Strategies for Generalisable Robot Learning](https://www.roboticsproceedings.org/rss20/p013.html)
  shows that structured environment variation in data collection strongly affects transfer.
- 2026 [Counterfactual Action Sensitivity Coverage](https://arxiv.org/abs/2607.27261) uses
  task-preserving visual counterfactuals and frozen-policy action drift to select a compact,
  policy-specific robustness repair set.
- ICLR 2024 [CCIL](https://personalrobotics.github.io/CCIL/) uses local dynamics continuity to
  synthesize corrective labels that guide policies back toward expert states.

## Agent Inference

A demonstration can be nominally high quality yet lie near a state from which the policy cannot
recover. Local closed-loop returnability may predict robustness beyond visual diversity, trajectory
likelihood or nominal success labels.

## Research Question Or Suspected Phenomenon

Does closed-loop return probability after task-preserving physical state perturbations around
demonstrations predict frozen-policy robustness better than nominal data density, imitation loss,
CFNBC-style action drift or success-only quality scores?

## Significance

This would connect robot-data coverage to closed-loop controllability and could improve data
selection without training a foundation model.

## Current State Of The Art And Limitation

CFNBC already occupies broad policy-specific sensitivity coverage under visual nuisances. CCIL and
Demo-SCORE occupy local corrective augmentation and online-experience curation. The only remaining
question under review is whether actual closed-loop return probability after task-preserving
**physical state perturbation**, measured before retraining, predicts held-out physical robustness
beyond action drift, density and loss.

## Evaluation Target

- recovery probability and time after bounded state perturbations;
- correlation with held-out perturbation success;
- predictive gain beyond distance/diversity/loss baselines.

## Available Data / Code / Evaluator

Pinned ManiSkill3 task, public PPO checkpoints and demonstration schema were verified in a new
Docker runtime. Physical interventions were tested on clean PPO rollouts; those are not expert
demonstrations or the PPO training dataset. See the current assessment and owning study above.

## Simplest Baseline Or Counterexample

Euclidean/task-normalized state distance, k-nearest-neighbor density, local action variance,
imitation loss and random demonstration ranking. CFNBC-style action drift is the strongest adjacent
offline baseline; a Demo-SCORE-style rollout-outcome classifier is the strongest online curation
reference. If these explain held-out robustness, recoverability adds no insight.

## Initial Stage 5 Assumptions — 2026-09-05

다음은 실행 전 risk register다. 당시의 `ambiguous`/`untested`와 resource 확인 요구는
historical entry이며 최신 판정은 위 `Current Assumption Assessment`가 우선한다.

### Q8-A. Exact State Restore And Frozen-Policy Execution

- **Status:** `ambiguous`; public API support는 documented됐지만 selected runtime은 미실행이다.
- **Necessity:** demonstration state와 policy를 정확히 재생하지 못하면 local neighborhood의
  차이를 perturbation 효과로 귀속할 수 없다.
- **Current evidence:** ManiSkill3는 environment state dictionary와 state-based demonstration
  replay를 문서화한다. Q1 audit에는 pinned version, demonstration revision과 두 public PPO
  checkpoint가 기록돼 있다.
- **Disconfirming observation:** 새 project-specific Docker에서 checkpoint가 load되지 않거나,
  restored state의 next-step transition이 reference replay와 일치하지 않는다.
- **Expected cost/duration:** 새 container recipe와 one-state deterministic replay 1--2일.
- **Cheaper proxy:** pinned source에서 state fields, replay path와 checkpoint observation/control
  mode compatibility를 static audit한다.
- **Decision branch:** exact replay가 되면 Q8-B로 진행한다. Missing custom state를 보완할 수
  있으면 protocol을 `refine`한다. Deterministic attribution이 불가능하면 Q8 route를
  `discontinue`한다.

### Q8-B. Task-Preserving Physical Perturbation

- **Status:** `ambiguous`; Q8의 가장 중요한 scientific risk다.
- **Necessity:** task identity/goal 변경 또는 infeasible state의 failure를 recovery failure와
  구분해야 한다. 2026-09-08 수정: physical perturbation은 적절한 action을 바꿀 수 있으므로
  visual nuisance처럼 intended expert action equality를 요구하지 않는다.
- **Current evidence:** selected ManiSkill tasks는 object/robot state와 explicit success
  constituents를 노출한다. 그러나 task-preserving radius와 collision-free validity criterion은
  official benchmark에 정의돼 있지 않다.
- **Disconfirming observation:** small pose displacement가 contact topology, grasp state, subtask
  phase 또는 kinematic feasibility를 바꾸며 이를 deterministic validity check로 걸러낼 수 없다.
- **Expected cost/duration:** one task의 state variables, contacts와 feasibility checks를
  정리하는 schema audit 0.5--1일.
- **Cheaper proxy:** training이나 rollout 전에 saved state에 one-axis perturbation을 적용한 뒤
  collision, joint limit, object support와 official task condition만 검사하는 synthetic fixture를
  설계한다.
- **Decision branch:** validity predicate를 정의할 수 있으면 Q8-C로 진행한다. 특정 phase에서만
  가능하면 population을 그 phase로 `refine`한다. Valid perturbation과 task change를 분리하지
  못하면 Q8을 `discontinue`한다.

### Q8-C. Reproducible Recovery Target

- **Status:** `ambiguous`.
- **Necessity:** “task progress로 돌아온다”가 연구자 주관의 trajectory-distance threshold이면
  recoverability score가 사후 조정될 수 있다.
- **Current evidence:** official task success와 continuous geometric constituents는 공개돼 있지만
  local return-to-trajectory predicate는 official metric이 아니다.
- **Disconfirming observation:** reasonable official-state criteria가 서로 다른 recovery ordering을
  만들거나 reference trajectory proximity가 실제 task success와 무관하다.
- **Expected cost/duration:** official success, successor-state distance와 finite-horizon success
  후보의 small counterexample audit 0.5일.
- **Cheaper proxy:** primary target을 fixed-horizon official success로 두고 trajectory-return은
  diagnostic으로만 두는 specification comparison.
- **Decision branch:** official success 기반 target으로 충분하면 Q8-D로 진행한다. Local return이
  꼭 필요하지만 안정적 정의가 없으면 final-success robustness question으로 `reformulate`한다.

### Q8-D. Non-Degenerate Recovery Profile

- **Status:** `ambiguous`.
- **Necessity:** 모든 valid perturbation이 pass 또는 fail이면 local recoverability는 data point를
  구분하는 coverage measure가 아니다.
- **Current evidence:** public policy의 nominal competence는 기대할 수 있지만 perturbation
  radius별 recovery curve는 측정되지 않았다.
- **Disconfirming observation:** pre-specified coarse radii와 phases 전체에서 recovery가 all-pass,
  all-fail 또는 seed noise 수준이다.
- **Expected cost/duration:** few-state, few-radius coarse sweep 0.5--1 GPU day.
- **Cheaper proxy:** 한 trajectory의 early/mid/late state와 한 perturbation axis만 사용한
  deterministic small grid.
- **Decision branch:** non-degenerate profile이면 Q8-E로 진행한다. 한 phase/axis에서만
  non-degenerate하면 그 population으로 `refine`한다. 전부 degenerate하면 Q8을 `discontinue`한다.

### Q8-E. Non-Circular Held-Out Prediction

- **Status:** `ambiguous`.
- **Necessity:** 같은 perturbation rollout으로 recoverability score와 evaluation label을 만들면
  robustness prediction이 tautology가 된다.
- **Current evidence:** direction, radius, state, seed와 task를 분리할 수 있는 simulator design은
  가능하지만 아직 split이 고정되지 않았다.
- **Disconfirming observation:** estimation perturbation과 held-out perturbation이 seed 또는
  near-duplicate state를 공유해야만 correlation이 남는다.
- **Expected cost/duration:** group/split specification과 leakage audit 0.5일.
- **Cheaper proxy:** rollout 전에 state group × perturbation direction × radius × seed의 disjoint
  table을 만들고 score용 group과 evaluation group을 분리한다.
- **Decision branch:** disjoint evaluation이 가능하면 Q8-F로 진행한다. 한 축만 holdout 가능하면
  claim을 그 축으로 제한한다. 독립 target을 만들 수 없으면 predictive claim을 중단한다.

### Q8-F. Residual Beyond Strong Simple Baselines

- **Status:** `ambiguous`.
- **Necessity:** state density, imitation loss 또는 CFNBC-style action drift가 같은 held-out
  robustness를 설명하면 rollout-based recoverability의 추가 비용과 insight가 정당화되지 않는다.
- **Current evidence:** CFNBC는 visual nuisance에서 action drift와 failure correlation을 이미
  보고한다. Physical perturbation에서의 상대 성능은 알려지지 않았다.
- **Disconfirming observation:** distance/density, expert-action error, finite-difference action drift
  중 하나가 recoverability와 같은 held-out ordering 또는 predictive performance를 낸다.
- **Expected cost/duration:** 동일 frozen policy와 split에서 scalar baseline table 1일.
- **Cheaper proxy:** learned classifier 없이 Spearman correlation, rank agreement와 simple
  regularized regression만 비교한다.
- **Decision branch:** simple baseline이 동등하면 Q8을 `discontinue`한다. Recoverability residual이
  남으면 Stage 7에서 hypothesis formulation 가능성을 판단한다. Learned data-selection method는
  이 결과만으로 허용하지 않는다.

### Q8-G. Scale And Resource Fit

- **Status:** `ambiguous`.
- **Necessity:** one-task fixture에서만 정의되는 score는 simulator diagnostic을 넘기 어렵고,
  rollout budget이 크면 6개월 연구와 맞지 않는다.
- **Current evidence:** local RTX 5090과 Docker runtime은 확인됐고 ManiSkill은 vectorized
  simulation을 지원한다. 허용 GPU 시간과 새 environment setup budget은 미확정이다.
- **Disconfirming observation:** one-task coarse sweep도 1주를 넘거나 second task에서 동일
  perturbation semantics를 정의할 수 없다.
- **Expected cost/duration:** Stage 6 one-task study 최대 1주; second-task extension은 pilot 성공
  뒤에만 산정한다.
- **Cheaper proxy:** source-level API count와 very small rollout timing으로 full grid runtime을
  extrapolate한다.
- **Decision branch:** bounded one-task study가 가능하면 Stage 6 후보로 유지한다. GPU/setup
  budget이 맞지 않으면 `deferred`한다. Second-task path가 없으면 generality claim을 금지한다.

### Stage 5 Risk Order

```text
Q8-A exact replay
  -> Q8-B valid physical perturbation
  -> Q8-C recovery target
  -> Q8-D non-degenerate profile
  -> Q8-E independent prediction split
  -> Q8-F strongest-baseline residual
  -> Q8-G scale/resource fit
```

특히 Q8-B 또는 Q8-E가 contradicted이면 simulator experiment를 늘리지 않는다. 현재는 API
documentation만 있고 physical perturbation semantics가 없으므로 Stage 6 admission은 아직
결정하지 않는다.

## Feasibility Or Pilot Study

For one public task and policy, select a few demonstration states, apply a fixed position/pose grid
within task feasibility and measure return to the official success path.

## Preliminary Success Criteria

Non-degenerate recovery curves and predictive information beyond the pre-specified density, loss
and CFNBC-style action-drift baselines on disjoint held-out perturbation groups.

## Expected Deliverable

Local recovery profiles, comparison to nominal coverage metrics and a data-selection hypothesis
decision.

## Timeline And Milestones

State/API audit, small perturbation grid, simple-baseline comparison, Stage 7 decision.

## Interpretation Of A Negative Result

If local recovery is binary, ill-defined or equivalent to state density, discontinue or reduce the
output to a simulator diagnostic.

## Resource Requirements

One lightweight simulator task, one public policy and short single-GPU rollouts in a new container;
no annotation or hardware.

## Related-Work Overlap

`high`; broad policy-specific coverage collides with CFNBC pressure. Reviewed work did not directly
occupy the narrower frozen-policy, physical-state, closed-loop diagnostic. See the
[preliminary literature review](../related_work/q8-local-recoverability-coverage.md).

## User Decision Needed

이번 bounded 검증은 사용자가 요청한 범위에서 완료했다. 새 data-coverage/transfer study는
먼저 question과 denominator를 재정의해야 하며 현재 즉시 실행 대상으로 선택하지 않았다.
