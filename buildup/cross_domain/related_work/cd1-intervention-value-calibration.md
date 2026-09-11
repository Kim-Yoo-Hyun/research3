# CD1 Intervention-Value Calibration: Preliminary Prior Audit

Updated: 2026-09-04

## Audit Boundary

- Candidate: [Intervention-Value Calibration](../questions/intervention-value-calibration.md)
- Exact question under audit: confidence/calibration metric이 실제 cost-adjusted intervention
  utility를 예측하는가, 특히 sequential system의 retry/replan/defer 선택에서 그러한가?
- Search window: 2024--2026 primary papers, official proceedings and repositories
- 이 문서는 `docs/buildup.md` Stage 4의 preliminary review다. Final novelty 판정이나
  hypothesis selection은 아니다.

## Facts

- Calibration만으로 decision quality를 판단할 수 없다는 broad premise는 recent direct
  prior에 점유됐다.
- Sequential VLA에서 calibrated score를 early stopping과 test-time action search에 쓰는
  것 역시 TDQC가 직접 평가한다.
- 이번 audit에서 **동일 detector set과 동일 cost budget 아래 retry/replan/defer 여러
  intervention action의 utility ordering을 counterfactual outcome으로 비교한 public
  denominator**는 확인하지 못했다.
- 어떤 external repository, model 또는 dataset도 내려받거나 실행하지 않았다.

## Nearest Primary Work

### Temporal Difference Calibration in Sequential Tasks (TDQC) — 2026

Official sources: [paper](https://arxiv.org/abs/2604.20472),
[code](https://github.com/shellytechnion/TDQC)

**Exact question and contribution.** Episodic task에서 partial trajectory마다 terminal
success confidence를 어떻게 calibrate할지 묻고 sequential Brier score의 minimizer가
policy value function임을 보인다. TD loss로 success predictor를 학습하고 functional
conformal early stopping 및 one-step simulator-guided action search에 적용한다.

**Boundary.** Outcome은 binary episodic success다. Guided search는 accurate simulator의
one-step lookahead를 요구하며 real-world dynamics model은 future work다. Predictor는
environment, embodiment와 action parameterization 사이에 잘 transfer되지 않는다고
보고한다. Action-search experiment는 LIBERO-10의 unseen 3 tasks, task당 50 rollouts와
3 seeds이며 success와 additional simulator compute를 함께 보고한다.

**Baselines.** Max/average/running-average probability와 entropy가 simplest baselines이고,
SAFE-MLP/RNN 및 BCE-trained MLP/RNN이 strongest adjacent learned baselines다. TDQC는
Brier와 ROC-AUC의 상관도 분석하고 BCE/TDQC-guided action-selection success를 비교한다.

**Artifact access.** Public MIT repository의 audit 당시 HEAD는
`451b5a6ff49e65724620e1daaec274f53938e289`다. Training/evaluation/plot scripts와
OpenVLA, OpenPI, UniVLA submodule routes가 있다. Simulation rollout은 별도 VLA inference가
필요하고, README가 제공하는 precomputed downloads는 real-robot WidowX/Franka data다.
그 logged data만으로 alternative intervention outcome을 만들 수 있다고 확인되지는 않았다.

### Epistemic Uncertainty Quantification To Improve Decisions — ICLR 2026

Official sources: [proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/51b3bf54f2a06c3c844b09d20b70eadb-Abstract-Conference.html),
[repository](https://github.com/soda-inria/epistemic-uq-decision)

**Exact question and contribution.** ECE 같은 calibration metric이 within-bin error
heterogeneity, 즉 grouping loss를 놓치므로 confidence가 decision-optimal인지 충분히
말하지 못한다는 문제를 다룬다. Grouping loss와 excess decision risk estimator를 제안하고,
이를 사용해 stronger LLM으로 defer하는 cascade의 accuracy-cost trade-off를 개선한다.

**Boundary.** Binary classification/LLM answering의 model cascade가 대상이며 embodied
within-episode retry/replan은 다루지 않는다. Baselines는 largest model, calibration-loss-only
cascade, confidence threshold와 matched predictive router다.

**Artifact access.** Public MIT repository의 audit 당시 HEAD는
`34ca088fb67ed0a2f586697cbd21668658d34ee2`지만 README, license와 figure만 있고
README도 estimator package가 “coming soon”이라고 명시한다. 현재 executable artifact로
간주할 수 없다.

### Utility-Directed Conformal Prediction — 2024/2025

Official source: [paper](https://arxiv.org/abs/2410.01767)

**Exact question and contribution.** Fixed classifier의 prediction set에 user-specified
downstream cost를 포함하면서 marginal coverage를 유지하는 utility-directed conformal
procedure를 제안한다. Base conformal, penalized conformal과 greedy optimizer를 image
classification 및 dermatology hierarchy에서 비교한다.

**Boundary.** Static finite-label classification이며 sequential intervention, state-dependent
recovery 또는 action timing을 다루지 않는다. 이번 audit에서 official code repository는
확인하지 못했다.

## Minimum Difference From The Candidate

다음 broad claim은 이미 prior와 충돌한다.

- calibration/detection metric이 decision utility를 보장하지 않는다는 주장;
- uncertainty를 cost-aware deferral에 사용하는 것;
- sequential VLA success predictor를 early stop 또는 action search에 연결하는 것;
- confidence threshold를 stronger cost-aware router와 비교하는 것.

남을 수 있는 최소 차이는 **하나의 frozen sequential system에서 detector와 information을
고정하고, retry/replan/defer처럼 서로 다른 intervention action을 동일 budget으로 평가했을
때 detector-metric ordering과 realized utility ordering이 뒤집히는가**이다. 이 residue는
TDQC의 single intervention application과 ICLR 2026의 static model cascade 사이에 있지만,
public counterfactual outcome artifact가 없으므로 아직 executable question이 아니다.

## Baseline Consequence

이 residue를 검토할 경우 다음이 최소 비교군이다.

1. raw confidence와 calibrated confidence threshold;
2. remaining horizon와 fixed action cost를 쓰는 analytic expected-value rule;
3. tabular empirical utility lookup 또는 finite-horizon dynamic programming;
4. TDQC Q-value-guided action selection 또는 해당 domain의 strongest value estimator;
5. privileged best-intervention oracle.

Simple expected-value/DP가 oracle gap을 제거하면 별도 learned method의 근거가 없다.

## Preliminary Decision Evidence

- Related-work overlap: `high`
- Broad CD1 formulation: direct conceptual and application overlap
- Narrow multi-action sequential residue: `UNRESOLVED`
- Public denominator for that residue: `NOT_FOUND`
- Final Stage 7 decision: `refine`; candidate status `deferred`

## User Decision Needed

없음. [Stage 7 selection decision](../../selection.md)에 따라 multi-action counterfactual
denominator가 확인되기 전에는 진행하지 않는다.
