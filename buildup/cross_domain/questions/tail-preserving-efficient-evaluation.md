# CD2 Tail-Preserving Efficient Evaluation

Updated: 2026-09-17

## Status

`deferred` — LBM episode-level 후속 관찰·독립 검산·해석까지 완료했다.
현재 generic mean/profile-preservation 경로의 추가 투자는 보류한다.
[최신 판단](../../selection.md#cd2-episode-observation-2026-09-17) ·
[Episode 결과](../pilot_studies/cd2-evaluation/README.md#episode-results-2026-09-17).
[결과](../pilot_studies/cd2-evaluation/README.md#results-2026-09-17) ·
[처음 선택한 근거](../../selection.md#cd2-observation-selection-2026-09-16).

## Observation 2026-09-17

CPU Docker에서 선택한 두 budget·두 split·세 대조를 실행했다. 작은 overall error에도
Long Horizon이 전부 빠지는 greedy 사례를 확인했다. 단순 stratification은 누락을 없애고
uniform보다 평균 score 오차가 작았지만 profile 오차와 작은 reference gap의 순위 역전은
남았다. 모든 target score/profile·pair를 독립 재구성했고 원본 출력은 보존한다.

첫 관찰은 유한 평균표의 정보 보존에 한정됐다. Complex sampler나 rare-failure 보존을
정당화하지 않으며 당시 episode-level noise도 측정하지 않았다. 이후 선행·비용 비교와
아래 LBM 후속 관찰까지 완료했다. 같은 표의 자동 확대는 선택하지 않는다.

## Research Question And Significance

비용을 줄인 robot-policy evaluation이 전체 평균과 순위를 잘 보존해도 조건별 약점을
다르게 보이게 하는가? 그렇다면 단순 stratified sampling으로 충분한가?
평균 성능과 진단용 성능표를 함께 읽는 robot evaluation에서 유용한 질문이다.
현재 잠정 설명은 sampling objective가 조건별 정보 보존을 보장하지 않는다는 것이다.
그 일반론 자체나 stratification을 새로운 원리로 주장하지 않는다.

원래 CD2는 5–20% episode/item budget에서 rare-failure coverage와 prevalence를 물었다.
첫 관찰 자료는 **suite × level의 평균**이었다. Condition-wise performance preservation으로
질문을 좁혀 관찰한 뒤 LBM episode-level 후속까지 진행했다. 원래 rare-failure 질문은
미해결로 남기며 aggregate proxy 확대를 반복하지 않는다.

## Facts And Available Inputs

- [VLA-Arena 공식 website repository](https://github.com/vla-arena/vla-arena.github.io)의
  commit `4b344135920f44545d546d38aaefa36452cfdafb`에서 source/result 파일 12개를
  읽기 전용으로 취득했다. 합계 248,079 bytes이며 모델 weights나 episode dataset은 없다.
- 현재 model manifest는 29개다. 첫 관찰은 같은 commit의 legacy bundled JSON에 포함된
  8개 ID로 한정한다. Outcome으로 model을 고르지 않았으며 최신 29-model 전수 비교가 아니다.
  실제 값은 **같은 commit의 개별 model JSON**에서만 읽고 legacy table과 섞지 않는다.
- 8개 각각 11 suite × L0/L1/L2의 SR 33개가 있다. Safety 5 suites, Distractor 2,
  Extrapolation 3, Long Horizon 1이다. Safety에는 CC 15개도 있지만 첫 SR 비교에 섞지 않는다.
- 이 파일에는 `numEpisodes`와 개별 trial 결과가 없다. 확인한 website tree에는
  `data/runs/` 파일이 없다. 다른 release 전체에 episode가 없다는 판정은 아니다.
- 저장 위치는 `runs/candidate_review/20260916/source/`, local manifest는 같은 상위 폴더의
  `source_manifest.json`이다. URL·SHA256·schema와 읽은 범위의 durable record는
  [comparison_sources.json](../../robotics/related_work/comparison_sources.json)의
  `remaining_candidates_20260916`이 소유한다.
- Schema 조사 중 OpenVLA와 bundled table의 일부 숫자를 보았다. 이후 비교는 탐색이며
  blinded confirmation이나 공개 preregistration으로 부르지 않는다.

## Source Claims And Closest Alternatives

[선행 비교](../../robotics/related_work/policy-geometry.md#remaining-candidate-comparison-2026-09-16)가
상세 근거를 소유한다. [Active Experiment Selection](https://proceedings.mlr.press/v305/anwar25a.html)은
robot policy/task의 outcome distribution과 선택 비용을 직접 다룬다. 선행을 모두
mean/ranking-only라고 요약할 수 없다. [Beyond Binary Success](https://arxiv.org/html/2603.13616v1)는
sequential policy comparison의 통계적 판단을 다룬다. Efficient evaluation, uncertainty와
early stopping 자체는 contribution 후보가 아니다.

VLA-Arena 논문의 30-episode 설명을 현재 각 JSON cell의 trial count로 대입하지 않는다.
CC는 누적 constraint cost여서 rare-event probability나 severity label로 바꿀 수 없다.
Neyman allocation에 필요한 within-cell variance도 현재 입력으로 복원하지 않는다.

## First Observation

### Target and budget

한 cell은 `(suite, level)`이며 published SR을 고정된 유한 표의 값으로 취급한다.
Reference score는 **33개 cell의 동일 가중 평균**이다. 공식 leaderboard 집계의 재현이나
전체 170 task/episode 가중 평균이라고 부르지 않는다. Profile은 `category × level`의
12개 stratum별 cell 평균이다. 작은 stratum을 희귀한 실제 사건으로 해석하지 않는다.

Budget은 `{12, 18}`개 cell이며 full 33은 reference다. 이는 episode 수나 wall-clock 절감률이
아닌 aggregate cell 접근 수다. 선택한 subset은 해당 비교의 모든 target model에 공통 적용한다.

### Comparisons

1. **Uniform sampling without replacement:** seed 0–199, 선택 cell의 단순 평균.
2. **Category × level stratification:** 같은 200 seeds. Budget 12는 각 stratum 1개,
   budget 18은 level마다 Safety 2, Distractor 1, Extrapolation 2, Long Horizon 1개를
   stratum 안에서 비복원 추출한다. Overall estimator는 `sum_h (N_h/33) * sampled_mean_h`다.
   불균등 allocation의 단순 평균으로 estimand를 바꾸지 않는다.
3. **Greedy mean matching:** development model의 full 33-cell 평균과 selected-cell 평균
   사이 mean squared error를 가장 줄이는 cell을 빈 집합부터 하나씩 추가한다.
   Tie는 `(category, suite, level)` 사전순으로 처리한다. Target score는 subset의 단순 평균이다.
   단순 score-matching 대조이며 IRT, EIG 또는 위 논문의 reproduction이 아니다.

Greedy selection에 target-model 값이 들어가지 않도록 두 split을 별도로 사용한다.

| Split | Target model IDs | Development model IDs |
| --- | --- | --- |
| A | pi0, pi0-fast, pi0-full-parameters, pi0-fast-full-parameters | openvla, openvla-oft, univla, smolvla |
| B | openvla, openvla-oft | pi0, pi0-fast, pi0-full-parameters, pi0-fast-full-parameters, univla, smolvla |

이는 이름으로 정한 model-group holdout이다. Shared backbone/data 가능성이 있어 independent
model-family generalization이 아니며 두 split 결과를 독립 반복으로 합치지 않는다.
Development full matrix 취득 비용은 별도다. 이를 무료라 두고 end-to-end cost 우위를 주장하지 않는다.
Greedy는 split/budget마다 deterministic 1개 subset이며 200회 복제해 표본 수를 부풀리지 않는다.

### Readouts and missing strata

- Target model별 overall absolute error와 split 내 pairwise ordering: correct / reversed /
  predicted tie / reference tie를 분리한다. Tie tolerance는 부동소수점 처리용 `1e-12`이며
  practical equivalence나 실제 성능의 유의성 기준이 아니다.
- Model별 12-stratum reference profile과 관측된 stratum의 추정 오차, 최악 오차를 기록한다.
  미관측 stratum은 `missing`이다. 0 대입·평균 대입을 하지 않는다. Full-profile MAE는
  12개를 모두 관측할 때만 정의하고, partial MAE에는 관측 개수를 반드시 붙인다.
  서로 다른 coverage의 partial MAE만으로 방법 우열을 정하지 않는다.
- Budget별 reference profile, 선택 cell, stratum coverage, overall error와 ordering을
  함께 보는 compact table과 대표 사례를 만든다. Stratification의 coverage 보장은 설계상
  자명하다. 그 자체를 발견으로 쓰지 않고 score/ordering 오차와 profile 오차의 비용을 본다.
- 200 seeds는 이 **고정 표의 sampling variability**다. Episode, robot, task 또는 모델 모집단의
  독립 반복이 아니다. Binomial CI·실제 failure prevalence·population safety claim을 만들지 않는다.

## Execution And Verification Plan

선택한 준비·실행·검산·해석을 완료했다. Recipe, command/image/seed/mount와 output identity는
[study README](../pilot_studies/cd2-evaluation/README.md#commands)가 소유한다.
Source input은 read-only mount, 결과는 `runs/cd2-evaluation/20260917_001500/`, log는 `logs/`다.

사전 예상 작업량은 반나절 이내 준비·해석, CPU 실행 1시간 이내였다.
GPU, simulator, foundation training, 새 model download는 필요 없다. 실행에서 source hash,
common cell schema, subset 크기/중복, target leakage, stratified weights와 full-budget
reconstruction을 검사한다. 정렬/tie·한 stratum 누락 사례의 검산으로 해석에 필요한 구현을 확인한다.
이미 확정된 입력을 위한 별도 장기 readiness 단계는 추가하지 않는다.

## Interpretation And Next Decision

- **단순 stratification으로 충분:** 이 표에서 observed profile와 score를 보존하는 단순
  대안을 기록한다. Learned sampler의 필요성을 주장하지 않고 broad 질문의 축소/보류를 비교한다.
- **유의미한 trade-off 사례가 남음:** 특정 model group, stratum과 budget을 명시하고
  selection bias·allocation·development mismatch로 설명되는지 본다. 바로 새 module이나
  generality를 주장하지 않고 그 설명을 구별할 작은 다음 관찰을 제안할 수 있다.
- **표가 너무 거칠거나 ranking이 정보 부족:** 질문의 반증과 구분한다. Episode-level
  관찰에서 무엇을 추가로 배울지와 비용을 적고 추가 투자 또는 보류를 결정한다.

어느 결과든 이번 작은 관찰의 완료다. Positive residual, exact novelty, 두 번째 dataset과
최종 method는 진입 조건이 아니다. 2026-09-04의 미실행 5–20%/1000-seed 원안과
“exact novelty audit 없이는 진행하지 않는다” 조건을 이번 탐색 설계로 대체한다.
Formal hypothesis, paper contribution, rare-failure preservation 효과는 아직 선택·검증하지 않았다.

## Episode-level Follow-up

아래는 실행 전에 선택한 설계다. 입력 adapter의 NPY metric 가정을 정정했으며
cohort·budget·sampling·metric은 유지했다. 준비·실행·검산·해석은 완료했고
[입력 정정과 결과](../pilot_studies/cd2-evaluation/README.md#input-interpretation-correction)가
실행 기록을 소유한다.

### Question and information value

**고정된 task 집합을 모두 관측해도 전체 평균과 task별 성능 차이를 추정하는 표본 요구량은
얼마나 다른가? 단순 층화 뒤의 차이는 within-task variation으로 설명되는가?**

첫 평균표에서는 알 수 없던 trial variation을 관찰한다. 단순 층화·task별 uncertainty와
N-SCORE/STEP/PEAK의 비교 범위는 [후속 선행 검토](../../robotics/related_work/policy-geometry.md#cd2-follow-up-assessment-2026-09-17)가
소유한다. Global 평균의 보존과 모든 task gap의 보존은 서로 다른 목표다. 전자용 방법이
후자를 보장하지 않는다는 사실을 기존 방법의 오류나 새 발견으로 표현하지 않는다.

### Input contract

- Source: N-SCORE commit `68c0a3453248d16da0c3f0b96f229fb9daf9fe78`의
  `data/LBM/lbm_data.pkl`, 명시적 key `figure_4_hardware_tasks`.
  `policy_type`, `skill`, `success`, `task_progress`, `num_rollouts`, `n_questions`를
  이름으로 읽는다. 후보 policy type은 `DiT_DP_stage5_finetune`과 `DiT_DP_single_task`다.
- 후보 task는 BikeRotorInstall, CutAppleIntoSlices, CleanLitterBox,
  ClearKitchenCounter, SetUpBreakfastTable 전체다. 결과값으로 task를 고르지 않는다.
  예상 5 tasks × 2 policies × 50 trials를 container에서 확인한다. 현재까지는 source,
  pickle 문자열/schema 단서와 10개 NPY header를 확인했으며 실제 값의 정합성 검산은 남았다.
- DataFrame의 policy/task key, 중복·길이·binary/bounded outcome·progress grid와 NPY
  column mapping을 같은 실행의 첫 단계에서 대조하고 정규화 manifest를 남긴다.
  다른 count나 label이면 조용히 truncate/교체하지 않고 불일치를 기록해 해석을 수정한다.
- Success와 progress의 같은 episode 연결이 원본에서 확인되면 같은 subset indices를
  사용한다. 두 metric을 독립 trial로 합치지 않는다. 서로 다른 policy는 독립으로
  sampling하며 같은 row index를 matched initial-state pair라고 가정하지 않는다.

### Estimands and comparisons

공개된 trial들을 **고정 유한 표**로 취급한다. 각 policy/task의 full-record mean과
두 policy의 차이, 5-task 동일 가중 macro mean을 reference로 둔다. 이 reference는
미지의 실제 deployment success rate가 아니다. Binary success와 progress를 따로 읽는다.

Nominal budgets는 task/policy당 `n={5,10,25,50}`에 대응하는 총 `{50,100,250,500}`
record access다. Seed `0–199`에서 다음 대조를 수행한다. Full-budget 반복은 독립
evidence가 아니며 정확한 복원 대조다. 새 rollout·GPU·학습은 없다.

1. **Uniform without replacement:** policy마다 전체 250개에서 `5n`개를 추출한다.
   Overall은 selected mean이다. 균등한 원본 task count 때문에 full macro와 같은 estimand다.
   Task별 값은 관측된 trial의 평균이며 미관측 task는 `missing`으로 둔다.
2. **Equal task stratification:** policy/task마다 `n`개를 비복원 추출하고 5개 task mean을
   동일 가중한다. 두 방법의 총 record access를 맞춘다. 미관측 task에 0을 넣지 않는다.
3. **Full-task-mean substitution:** 위와 같은 선택 indices에서 각 outcome을 그
   policy/task의 full-record mean으로 대체해 task mix가 만드는 오차를 분리한다.
   실제 estimator와의 차이가 within-task sampling 항이다. Full input을 이미 읽은
   진단용 oracle이므로 저비용 방법이나 무료 prior로 비교하지 않는다. Stratified oracle의
   오차가 0인 것은 설계상 identity이며 empirical discovery가 아니다.

주 readout은 global mean/gap error, task mean/gap MAE와 최대 절대 오차, missing task 수,
reference gap 부호의 correct/reversed/tie 분리다. Task마다 실제 finite-reference gap과
sampling 변동을 함께 제시한다. Error decomposition을 record 수준에서 검산한다.
Global 오차가 작은 draw만 사후 골라 효과 크기를 주장하지 않고 전체 budget별 joint
분포를 보고한다. 승자/실패 여부를 정할 임의 threshold를 결과 후 추가하지 않는다.

Resampling quantile은 이 표에서의 sampling variability다. Population CI, statistical
significance, anytime-valid stopping 또는 실제 hardware cost 절감으로 부르지 않는다.
따라서 N-SCORE에 without-replacement 순서를 넣어 i.i.d. 보장과 직접 비교하지 않는다.
향후 순차 판단이 연구 목표가 되면 해당 가정·multiple testing을 정하고 기존 task별
검정/동시 interval과 실제 비교한다. 두 metric의 정보량 차이도 N-SCORE가 이미 다룬다.

### Investment and interpretation

한 번의 준비·실행·검산·해석으로 묶으며 예상 준비·해석은 반나절–하루, CPU 1시간 이내다.
이는 실행 전 추정이다. 같은 study의 기존 README를 결과 owner로 쓰며 source snapshot은
read-only로 mount한다. 별도의 readiness-only TODO나 report를 만들지 않는다.

- 단순 층화와 within-task sampling으로 설명되면 추가 sampler 개발의 근거가 약하다는
  판단을 기록한다. 더 많은 seed·동일 metric 반복을 자동 선택하지 않는다.
- 특정 task에서 해석이 다른 사례가 남으면 outcome 분포·gap·metric 의미를 읽어 다음
  질문을 구체화한다. 범용 tail-aware method의 효과로 바로 승격하지 않는다.
- 표본이 작아 미지 모집단의 약점을 말할 수 없다는 것은 연구 가설의 반증과 다르다.
  이번 유한 자료에서 얻은 정보와 다음 관찰 비용으로 재평가한다.
- 원래 rare/severe failure 질문은 계속 미해결이다. Positive residual, exact novelty,
  두 번째 dataset 또는 final method는 이 관찰의 진입 조건이 아니다.

## Episode Outcome And Investment Decision

500개 공개 기록을 사용한 후속 관찰을 완료했다. Task/policy당 n=25에서 전체 순위는
두 metric·두 sampling 모두 200/200 유지됐지만 작은 task gap의 순위는 흔들렸다.
단순 층화도 within-task sampling variation을 없애지 않으며, binary 작은 gap의 역전은
exact finite-population 계산으로 설명된다. Success/progress의 task별 reference 방향이
다른 사례도 있지만 두 metric의 목표 차이를 새 방법의 필요성으로 확대하지 않는다.

현재 경로는 `deferred`다. 이는 broad rare/severe failure 질문의 반증이나 통계적
비유의에 따른 탈락이 아니다. 이번 두 관찰이 추가 sampler를 만들 구체적 실패 원리를
제공하지 않았고 동일 자료 확대의 정보 가치가 낮다는 투자 판단이다. 세부 수치·한계·
[재검토 가능성](../pilot_studies/cd2-evaluation/README.md#investment-decision-and-re-entry)은 study owner에 둔다.
Formal hypothesis나 paper claim은 선택하지 않았다.

## User Decision Needed

없음. 기존 Robotics 범위의 다음 작은 관찰이며 LLM/RAG 평가로 scope를 전환하지 않는다.
