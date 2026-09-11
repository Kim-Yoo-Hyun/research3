# Q8 Local Recoverability Coverage: Preliminary Literature Review

Updated: 2026-09-08

## Audit Boundary

2026-09-08 심화 재감사와 실행 evidence는 이 문서의 `Repeated Audit`와
[study README](../pilot_studies/q8-recoverability/README.md)가 소유한다.
아래 initial review의 artifact 미실행 및 provisional priority는 당시 상태다.

- Candidate: [Local Recoverability Coverage](../questions/local-recoverability-coverage.md)
- Exact question under review: demonstration 인근의 task-preserving **physical state
  perturbation**에서 frozen policy가 task progress로 돌아오는 closed-loop probability가
  held-out physical robustness를 nominal density, policy loss와 counterfactual action drift보다
  더 잘 예측하는가?
- Search boundary: policy-specific robustness/data selection, local corrective imitation과
  online-experience demonstration curation의 nearest primary work
- Visual nuisance, corrective-data generation과 retrained-policy improvement를 Q8의 exact
  phenomenon과 구분한다.

## Facts

- 2026 CFNBC는 “특정 trained policy에 어떤 additional data가 유용한가”를 action sensitivity로
  측정한다. 따라서 broad한 policy-specific coverage/robustness claim은 이미 충돌 압력이 높다.
- CCIL은 demonstration 인근의 local dynamics continuity를 corrective label generation에
  사용하며, Demo-SCORE는 policy rollout outcome으로 demonstration을 curate한다.
- Reviewed work는 frozen policy의 physical state perturbation rollout에서 **local return
  probability 자체를 diagnostic target**으로 삼는 exact combination을 official description에서
  보고하지 않는다.
- 어떤 external artifact도 local에 download, checkout, build 또는 run하지 않았다.

## Nearest Primary Work

### Counterfactual Action Sensitivity Coverage / CFNBC — 2026

Official source: [paper](https://arxiv.org/abs/2607.27261)

**Exact question and claim.** Nominal visuomotor policy에 어떤 additional demonstration이
targeted robustness repair에 유용한지를 묻는다. Clean/nuisance paired observation에서 expert
action은 보존하고 policy action drift를 계산한 뒤, response-diverse repair set을 offline으로
선택한다. MuJoCo bimanual cube transfer와 SimplerEnv cube stacking에서 action drift가
nuisance-induced failure와 상관하고 20--30 selected candidates가 matched random selection보다
좋으며 훨씬 큰 random budget에 접근한다고 보고한다.

**Boundary.** Lighting, color, texture와 distractor 같은 visual nuisance를 다룬다. Environment
physical state를 perturb한 closed-loop returnability를 측정하지 않으며, 최종 목표는 selected
counterfactual data로 policy를 fine-tune하는 것이다.

**Artifact status.** Paper는 implementation detail과 experiment scale을 제공하지만
2026-09-04 arXiv page에는 official code/data link가 없다. Workshop paper이므로 direct
reproduction substrate로는 아직 불확실하다.

**Minimum difference.** Q8은 paired-image action sensitivity나 repair-set selection을 다시
제안하지 않는다. 같은 frozen policy를 실제 simulator state에서 rollout해 recovery basin을
측정하고, retraining 전에 held-out physical perturbation robustness에 대한 diagnostic value만
검증한다. CFNBC action drift는 반드시 strongest adjacent baseline에 포함해야 한다.

### CCIL — ICLR 2024

Official sources: [project and papers](https://personalrobotics.github.io/CCIL/),
[code](https://github.com/personalrobotics/CCIL)

**Exact question and claim.** Expert demonstration 근처의 local dynamics continuity를 이용해
expert state로 돌아가도록 하는 corrective state-action labels를 합성할 수 있는지 묻는다.
Learned dynamics model, Lipschitz regularization과 error-based filtering을 사용하며 simulation과
real robot에서 augmented behavior cloning의 robustness improvement를 보고한다.

**Boundary.** Local neighborhood가 등장하지만 target은 trustworthy corrective label과 retrained
policy performance다. Frozen policy의 return probability를 data-coverage diagnostic으로 측정하거나
그 predictive value를 nominal density와 비교하지 않는다.

**Artifact status.** Official repository는 Python 3.8.10, custom dependency forks, configuration,
data format과 Pendulum/MuJoCo/MetaWorld/drone/F1Tenth experiment scripts를 공개한다. Vanilla BC와
NoiseBC도 실행 가능하다. Q8의 simulator/policy와 직접 호환된다는 뜻은 아니다.

**Minimum difference.** CCIL의 continuity radius나 generated-label trust region을 local
recoverability로 부르지 않는다. Q8 metric은 learned dynamics의 smoothness가 아니라 actual
frozen-policy closed-loop outcome으로 정의돼야 한다.

### Demo-SCORE — RSS 2025

Official sources: [proceedings](https://www.roboticsproceedings.org/rss21/p071.html),
[project](https://anniesch.github.io/demo-score/),
[code](https://github.com/alessing/demo-score)

**Exact question and claim.** Heterogeneous demonstration strategy 중 unreliable 또는
underrepresented strategy를 online policy experience로 자동 식별할 수 있는지 묻는다. Successful
대 unsuccessful policy rollouts를 구분하는 cross-validated classifier로 demonstration을 filter해
simulation과 real manipulation에서 base policy보다 15--35 percentage points 높은 absolute
success를 보고한다.

**Boundary.** Demonstration quality/strategy classification과 post-filter retraining이 target이다.
각 demonstration state 주위의 bounded recovery curve나 held-out perturbation prediction을 직접
측정하지 않는다.

**Artifact status.** Official code는 Demo-SCORE package와 LeRobot, ACT, Diffusion Policy forks,
example experiment scripts를 제공한다. 여러 Conda environment와 policy training을 요구하므로
one-week diagnostic의 직접 substrate보다 strongest data-curation baseline/reference에 가깝다.

**Minimum difference.** Q8은 rollout-success classifier가 구분하는 broad strategy quality가
아니라 task-progress trajectory의 어느 local physical neighborhood가 frozen policy에 닫혀
있는지 측정한다. Demo-SCORE score가 같은 held-out robustness를 설명하면 Q8의 추가 metric은
필요하지 않다.

## Baseline Boundary

### Simplest baselines

1. Demonstration state까지의 Euclidean 또는 task-normalized distance
2. k-nearest-neighbor density / local occupancy count
3. Frozen-policy imitation loss 또는 expert-action error
4. Local action variance와 Jacobian-free finite-difference sensitivity
5. Nominal trajectory success 또는 random demonstration ranking

### Strongest adjacent baselines

- CFNBC의 paired counterfactual action-drift summary: policy-specific fragility를 rollout 없이
  측정하는 가장 가까운 baseline
- Demo-SCORE의 rollout-outcome classifier: online experience를 사용해 demonstration quality를
  점수화하는 강한 curation baseline
- CCIL/NoiseBC는 local support expansion이 실제 retraining 목표가 될 때의 method-family
  references이며, initial diagnostic pilot의 필수 training baseline은 아니다.

## Candidate Residue

Broad claim은 살아남지 않는다. Reviewed prior 뒤에 남을 수 있는 질문은 다음으로 제한한다.

> task-preserving physical state perturbation에서 측정한 frozen-policy closed-loop return
> probability가, retraining 없이, held-out physical robustness에 CFNBC-style action drift와
> nominal data-coverage score를 넘는 predictive information을 주는가?

이 distinction이 empirical result에서 사라지면 Q8은 CFNBC/CCIL/Demo-SCORE와 구별되는 연구
질문이 아니다.

## Empirical Uncertainty Before Novelty

1. Demonstration state를 simulator에 정확히 restore하고 dynamically feasible한 perturbation을
   적용할 수 있는가?
2. Perturbation이 object identity, subtask stage 또는 solvability를 바꾸지 않는다는 것을
   cheap하게 판정할 수 있는가?
3. Radius sweep에서 recovery probability가 all-pass/all-fail이 아닌가?
4. “Return to task progress”가 official success와 별개로 재현 가능하게 정의되는가?
5. 같은 frozen policy로 score와 held-out outcome을 만들 때 circularity나 seed leakage를
   split으로 차단할 수 있는가?
6. State density, action drift 또는 simple loss가 이미 held-out robustness를 설명하는가?
7. Rollout count가 local RTX 5090 한 장과 새 container setup으로 bounded study 안에 드는가?

## Preliminary Decision

- Related-work overlap: `high`
- Broad policy-specific coverage claim: `collides with CFNBC pressure`
- Narrow physical-state closed-loop diagnostic: `not directly occupied in reviewed sources`
- Public empirical route: `plausible but unverified`
- Final novelty: `NOT_ESTABLISHED`
- Candidate status: `under_review`

Q8은 중단할 단계는 아니지만 Q10보다 좁고 실행 risk가 크다. Stage 5에서는 physical
perturbation semantics와 non-circular held-out prediction을 먼저 decision branch로 고정해야
한다. 이것이 성립하지 않으면 implementation 대신 `refine` 또는 `discontinue`한다.

## User Decision Needed

없음. Feasibility study를 선택할 때 GPU 사용 가능 시간과 새 simulator setup budget을
확인해야 한다.

## Repeated Audit — 2026-09-08

### Primary-source revalidation

CFNBC [v1 full text](https://arxiv.org/html/2607.27261v1)의 task-preserving nuisance와
action drift 정의, [CCIL official project](https://personalrobotics.github.io/CCIL/)의
corrective-label target, [Demo-SCORE project](https://anniesch.github.io/demo-score/)의
success/failure experience 기반 curation을 다시 확인했다. CFNBC의 visual nuisance는
expert action을 보존하지만 cube translation은 적절한 action을 바꿀 수 있다. 따라서
physical action drift는 comparator feature일 뿐 동일한 fragility 해석을 상속하지 않는다.

추가 nearest-principle 및 task-family 점검:

| Primary source | Source claim | Q8에 대한 에이전트 추론 |
| --- | --- | --- |
| [How basin stability complements the linear-stability paradigm, Nature Physics 2013](https://www.nature.com/articles/nphys2516) | basin volume에 기반한 nonlinear stability를 측정 | perturbation 후 return probability 자체는 새 원리가 아니다 |
| [Potentials and Limits to Basin Stability Estimation, 2016](https://arxiv.org/abs/1603.01844) | Monte Carlo basin estimation의 geometry/numerical limits를 분석 | finite-horizon success와 asymptotic attraction을 구분해야 한다 |
| [SEDS official author page](https://cs.stanford.edu/people/khansari/DSMotions.html) | demonstration으로 안정적인 autonomous dynamics와 basin을 학습 | demonstration/recovery/basin의 broad 연결도 이미 성숙한 주제다 |
| [SAFE, NeurIPS 2025](https://arxiv.org/abs/2506.09937) | success/failure rollout으로 failure detector를 학습하고 unseen tasks 평가 | held-out outcome prediction 자체도 새 질문이 아니다; outcome-feature predictor가 comparator다 |

이는 Q8의 exact combination이 완전히 점유됐다는 증거는 아니다. 그러나 초기 문헌의
CFNBC/CCIL/Demo-SCORE 세 편만으로 narrow question의 novelty를 긍정할 수는 없다.

### Formal target and baseline audit

**에이전트 분석:** finite-horizon official success를 Y_H, perturbation law를 q라 하면
R_q(s)=E_q[Y_H(s,delta)]다. 동일 q의 separate rollout에서 얻은 success frequency를
예측하면 score와 target은 같은 조건부 확률의 두 추정량이다. Independent seeds는 label
leakage를 줄이지만 이 identity를 없애지 않는다. 서로 다른 q에서의 transfer는 별도 질문이다.

따라서 다음 두 comparator를 제외한 density/action-drift 승리는 불충분하다.

1. 같은 state/perturbation law와 동일 rollout budget의 empirical success estimate.
   Scalar R_q는 이 baseline과 정확히 같다.
2. 동일 development rollout/feature 예산으로 학습한 outcome predictor. Demo-SCORE/SAFE
   전체 system 재현과 구분해 `outcome classifier control`이라고 부른다.

PPO critic value와 current geometric progress도 거의 추가 rollout 비용이 없는 controls다.
공개 motionplanning demonstration은 PPO training dataset provenance가 없어 density를
`training coverage`라고 부를 수 없고, absolute joint-position expert action과 delta-position
policy output의 subtraction은 imitation loss가 아니다.

### Remaining reformulation

고정된 sampling budget에서 phase/direction별 physical perturbation response가 pooled success
frequency와 geometric/action/critic controls보다 **새 episode group 및 다른 perturbation
family**의 실패를 더 잘 설명하는가? 이는 testable refinement이나 current evidence가
요구한 failure-derived principle은 아직 없다. 먼저 implementation feasibility를 판정하고,
같은 scalar metric의 이름만 바꿔 hypothesis로 넘기지 않는다. Final novelty remains
`NOT_ESTABLISHED`.
