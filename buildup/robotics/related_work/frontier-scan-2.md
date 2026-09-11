# Second-Round Robotics Frontier Scan

Updated: 2026-09-04

## Purpose And Boundary

첫 candidate set이 evaluation, calibration과 failure attribution에 치우쳤기 때문에
`docs/buildup.md` Stage 1을 확장한다. 이 문서는 candidate selection, exact novelty audit
또는 실행 승인이 아니다. `PaperReview`는 discovery source로만 읽었고, 아래 내용은
primary paper, official proceedings, project 또는 repository에서 다시 확인했다.

## Facts

- Q1은 public artifact와 bounded study가 있지만 scientific depth는 아직 확인되지 않았다.
- CD1/CD4는 2024--2026 direct prior overlap과 public denominator 부재 때문에 보류됐다.
- 이 workspace에서는 simulator, policy, dataset, checkpoint 또는 external code를 실행하거나
  내려받지 않았다.
- 2026-09-03 공개된 FailBench까지 포함해 최신 source를 2026-09-04에 확인했다.

## Frontier 1: Temporal Execution Contracts

### Source Claims

- ICLR 2026 [REMAC](https://arxiv.org/abs/2601.20130)은 asynchronous action-chunk
  execution의 failure를 inter-chunk discontinuity뿐 아니라 perception과 inherited action
  prefix 사이의 intra-chunk inconsistency로 설명하고 masked fine-tuning을 제안한다.
- 2026 [Why Does Action Chunking Improve Behavioral Cloning Performance?](https://arxiv.org/abs/2608.02547)는
  temporal consistency, horizon reduction과 representation learning만으로 chunking 이득이
  설명되지 않으며 delayed policies와 implicit ensembling이 중요한 원인이라고 보고한다.
- REMAC의 [official repository](https://github.com/hatchetProject/REMAC)는 simulation
  training/evaluation code를 공개하지만 base policy training과 LoRA fine-tuning을 요구한다.

### Candidate Pressure

“Latency가 VLA를 망친다” 또는 “chunk boundary를 고친다”는 질문은 이미 점유됐다. 남는
scoping question은 같은 frozen policy와 executed-action budget에서 observation age,
committed prefix, boundary blending을 독립적으로 조작했을 때 어느 mismatch가 downstream
failure를 만드는지에 대한 **factorized temporal contract**다. Fixed hold, linear blend와
fresh-observation oracle이 simple controls다.

### Main Risk

REMAC이 이미 intra/inter-chunk factor를 충분히 분리했을 수 있다. Frozen checkpoint로
각 factor만 재생할 public simulator route가 없으면 후보로 만들지 않는다.

## Frontier 2: Constructed Versus Naturally Occurring Failures

### Source Claims

- 2026-09-03 preprint [FailBench](https://arxiv.org/abs/2609.03611)는 14개 public source의
  2,197개 manipulation attempt를 모으며 failure의 75%가 naturally occurring이라고
  보고한다. 13개 VLM detector 중 최고 mean balanced accuracy가 0.77이고, specialist가
  base general-purpose model보다 나쁜 cross-source 결과도 보고한다.
- FailBench는 deliberately constructed failure가 특정 data-generation procedure의
  인식 문제로 바뀔 수 있다고 지적한다.
- RSS 2025 [FAIL-Detect](https://www.roboticsproceedings.org/rss21/p073.html)는 failure
  data 없이 successful demonstration으로 runtime failure detection을 학습하는 문제를
  다룬다.

### Candidate Pressure

새로 열린 질문은 injected/constructed validation 성능이 naturally occurring failure에서
detector 또는 evaluator의 **상대 순위**를 예측하는지다. 동일 task, outcome evidence와
failure severity를 맞춘 source-stratified comparison이 필요하다. Source ID만으로 만든
classifier와 general-purpose VLM이 가장 싼 counterexamples다.

### Main Risk

FailBench 자체가 이 constructed-to-natural transfer를 이미 충분히 분석했을 수 있다.
또한 arXiv page에서 official code/data release route를 확인하지 못했으므로 full paper와
artifact audit 전에는 executable candidate가 아니다.

## Frontier 3: Recoverability-Aware Demonstration Coverage

### Source Claims

- RSS 2025 [Demo-SCORE](https://www.roboticsproceedings.org/rss21/p071.html)는 online policy
  experience로 unreliable/underrepresented demonstration strategy를 판별해 dataset을
  filtering하고 simulated 및 real manipulation에서 downstream policy success를 높인다.
- CoRL 2024 proceedings의 [Not All Errors Are Made Equal](https://proceedings.mlr.press/v270/nakamura25a.html)은
  downstream closed-loop regret가 큰 human-prediction error를 mining하고, 더 작은 high-regret
  subset을 사용한 fine-tuning이 full deployment data와 경쟁할 수 있다고 보고한다.
- RSS 2024 [Data Collection Strategies for Generalisable Robot Learning](https://www.roboticsproceedings.org/rss20/p013.html)은
  environment-factor composition을 고려한 demonstration collection이 unseen combinations의
  policy transfer를 크게 바꿀 수 있음을 보인다.

### Candidate Pressure

Quality filtering, visual diversity 또는 high-regret sampling 자체는 점유됐다. 가능한 다른
질문은 demonstration 근처의 small state perturbation에서 frozen policy가 task로 돌아오는
**local recoverability**가 nominal data diversity/likelihood보다 robustness를 더 잘 예측하는지다.
State-space distance, random diversity와 official success-only filtering이 simple baselines다.

### Main Risk

State perturbation의 의미와 크기를 task마다 공정하게 정의하기 어렵고 policy rollout을
필요로 한다. Local recoverability가 단순 state coverage와 같다면 독립적인 scientific
question이 아니다.

## Frontier 4: Dynamic Spatial Memory

### Source Claims

- RSS 2026 [Multi-modal Interaction Field](https://www.roboticsproceedings.org/rss22/p023.html)은
  locomotion-induced perceptual distortion과 environment change로 생기는 map--reality
  mismatch를 다룬다. Multi-modal discrepancy로 obsolete memory의 local update를 trigger해
  dynamic relocation에서 static HOV-SG보다 높은 success를 보고한다.
- ICLR 2025 [PARTNR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a3cf318fbeec1126da21e9185ae9908c-Abstract-Conference.html)은
  60개 house, 100,000 language task의 human--robot embodied planning benchmark를 제공한다.

### Candidate Pressure

Dynamic scene graph 또는 learned update module 자체는 새 후보가 아니다. 검토할 수 있는
질문은 fixed sensing/query budget에서 periodic refresh, time-to-live, geometric change
threshold와 learned discrepancy가 downstream planning success와 stale-belief duration에서
어떻게 다른가이다.

### Main Risk

MIF가 이 baseline comparison을 이미 포함했을 수 있으며, PARTNR의 public state interface가
memory staleness intervention을 허용하는지도 미확인이다. Simple TTL/change threshold가
충분하면 method contribution으로 확장되지 않는다.

## Frontier 5: Minimal Evidence For Contact-Rich Outcome Verification

### Source Claims

- [FailBench](https://arxiv.org/abs/2609.03611)는 observable object motion으로 판정 가능한
  outcome에서는 detector가 포화에 가까워지지만 contact-intensive assembly에서는 best
  models도 near-chance 수준으로 떨어진다고 보고한다.
- RSS 2026 [OopsieVerse](https://robin-lab.cs.utexas.edu/oopsieverse/)는 contact force,
  temperature와 liquid exposure를 object-centric damage로 변환하며 RoboCasa와
  BEHAVIOR-1K에 구현된 cross-platform benchmark를 공개한다.
- [ARMBench](https://www.armbench.com/)는 2025 stow success prediction과 2026 blade
  insertion affordance prediction data를 포함해 RGB-D와 manipulation outcome 평가를
  확장했다.

### Candidate Pressure

VLM을 더 크게 만드는 대신, ambiguous contact outcome을 검증하는 데 필요한 최소 추가
signal이 무엇인지 묻는다. RGB/RGB-D, proprioceptive terminal state, contact event와
short temporal window를 information/cost-matched하게 비교할 수 있다. Geometry threshold,
contact-count rule과 logistic probe가 가장 단순한 baselines다.

### Main Risk

서로 다른 dataset의 label semantics와 modality timestamp가 맞지 않을 수 있다. Public
row-level modalities와 outcome label을 한 dataset 안에서 확인하지 못하면 후보를
reformulate하거나 중단한다.

## Comparative Scoping Outlook

이 표는 Stage 3 판정이 아니라 정식 candidate record를 만들 우선순위를 정하는 Stage 1
요약이다.

| frontier | observed pressure | empirical opportunity | collision/resource risk | candidate-record priority |
| --- | --- | --- | --- | --- |
| temporal execution contract | asynchronous execution의 원인 분해 | REMAC simulation code | direct overlap, training cost | `medium` |
| constructed-to-natural failure transfer | cross-source specialist reversal | FailBench 14-source corpus claim | brand-new preprint, release unverified | `high` |
| recoverability-aware data coverage | nominal quality와 closed-loop returnability 차이 | public simulator demos/policies | perturbation semantics | `high` |
| dynamic spatial memory | stale map이 interaction failure 유발 | PARTNR/MIF task structures | MIF direct overlap, artifact risk | `low-to-medium` |
| minimal contact evidence | visual detector near chance on assembly | FailBench/OopsieVerse/ARMBench | modality alignment | `high` |

## Next Buildup Action

상위 세 축을 포함해 서로 다른 candidate question 3--5개를 정식 record로 작성하고
`docs/buildup.md` Stage 3의 8개 comparative criterion으로 기존 Q1과 함께 비교한다.
그 전에는 Docker build, model inference 또는 feasibility rollout을 시작하지 않는다.

## User Decision Needed

없음. Candidate generation과 preliminary comparison은 현재 resource 정보 없이도 진행할
수 있다. GPU, robot와 annotation availability는 feasibility priority를 확정하기 전에
다시 반영한다.
