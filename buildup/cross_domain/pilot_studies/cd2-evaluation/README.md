# Condition-wise Evaluation Preservation

Updated: 2026-09-17

## Scope

CD2의 aggregate-result 관찰과 episode-level 후속 관찰을 기록한다. 아래 첫 실행은
[선택한 protocol](../../questions/tail-preserving-efficient-evaluation.md#first-observation)의
8-model × 33-cell VLA-Arena SR 표, 두 model split, budgets 12/18, 200 sampling seeds와
세 대조를 그대로 사용한다. Reference는 33개 cell macro mean이며 episode 통계가 아니다.
질문은 전체 score/ordering과 조건별 profile의 보존이다. Rare-event prevalence, population
confidence interval, 실제 rollout 절감률은 계산하지 않는다.

## Runtime And Outputs

Status: `completed`; 독립 검산·사례 해석 완료. 새 CPU 전용 Docker image
`research3-cd2-evaluation:v1`을 사용했다.
Base는 public Python 3.11.14 image의 digest로 고정하며 standard library만 사용한다.
Host에서 baseline이나 수치 분석을 실행하지 않는다. Run과 verifier는 서로 다른 container다.
입력/source는 read-only, 결과 경로만 writable이다. Network, GPU와 새 모델은 필요 없다.

- Input: `runs/candidate_review/20260916/source/` 및 상위 `source_manifest.json`.
- Source identity: `4b344135920f44545d546d38aaefa36452cfdafb`; snapshot의 SHA256을 실행에서 검사한다.
- Code/config: 이 폴더의 `run.py`, `verify.py`, `protocol.json`, `Dockerfile`, `requirements.lock`.
- Output: `runs/cd2-evaluation/<run-id>/`; container inspect·image identity·실행 command도 보존한다.
- Logs: `logs/<run-id>_cd2_{build,run,verify}.log`와 대응 exit file.

`reference.json`은 전체 표와 profile, `subsets.jsonl`은 공통 선택 cell·weight·seed,
`scores.jsonl`은 target별 score/profile와 missing mask, `pairs.jsonl`은 모든 target pair의
ordering이다. `summary.json`/`summary.csv`는 split/budget/method별 집계다. Greedy는
deterministic 1개 subset이며 반복 표본으로 복제하지 않는다. Complete-profile MAE는
coverage가 12인 draw에서만 계산하고 그 denominator를 같이 기록한다.

## Implementation Details Before Execution

- Cell/stratum은 category, suite, level 사전순이다. Random sampling은 Python의
  `random.Random(seed)`를 매 method/budget에 새로 만든다. 두 split은 같은 random subset을
  공유한다. Stratified sampling은 stratum 사전순으로 수행한다.
- Greedy objective는 development 모델별 full mean과 subset mean의 squared error 평균이다.
  JSON의 decimal 값을 rational로 읽어 exact objective tie를 사전순으로 처리한다.
  각 budget은 빈 집합에서 시작하므로 budget 12 subset은 budget 18의 prefix다.
- Overall score의 정렬 tie tolerance는 1e-12다. Reference tie는 separately 기록하고
  reversal rate의 denominator에서 제외한다. Predicted tie도 reversal과 분리한다.
- Summary의 score MAE는 해당 split의 target 모델과 draw 전체 평균이다. Draw 반복에 대한
  population inference는 하지 않는다. 두 split을 독립 실험처럼 합치지 않는다.
- 독립 verifier는 source decimal의 rational arithmetic으로 weighted score, profile,
  ordering, full-budget reference와 greedy 선택을 재구성한다. Missing stratum, unequal
  stratum size, exact tie와 full-budget reconstruction을 별도 작은 대조로 확인한다.

## Commands

Run ID: `20260917_001500`; working directory: `/home/yoohyun/research3`.

```bash
tmux new-session -d -s research3_cd2_20260917_001500 'cd /home/yoohyun/research3 && bash buildup/cross_domain/pilot_studies/cd2-evaluation/execute.sh 20260917_001500 > logs/20260917_001500_cd2_job.log 2>&1'
```

[`execute.sh`](execute.sh)가 exact build/create/start command를 output `commands.txt`에 남긴다.
Image ID는 `image.id`/`image.json`, command·mount·label·exit status는 각 `*.container.json`에
보존한다. Base digest는 Dockerfile이 소유한다. Run은 `/output`만 writable, verifier는
saved output도 read-only이며 별도 `/verification` receipt mount만 writable이다.
Host의 `id -u`/`id -g`를 사용하고 network 없음, CPU 2개·RAM 1 GiB로 제한한다.
Build는 `tmux` background job으로 시작하며 input/output 완료는 필요한 의존 시점에 확인한다.
실행·검산 완료 후 결과/로그/inspect를 보존하고 이번 workspace에서 생성한 종료 container만
명시적으로 삭제한다. 기존 image/container/volume과 build cache는 정리하지 않는다.

## Results 2026-09-17

**판단: `refine`; question registry `under_review`.** 평균 보존과 조건별 정보 보존의 차이를
관찰했다. 단순 stratification으로 조건 누락은 해결했지만 profile 추정 오차와 작은 score gap의
순위 역전이 남는다. 이를 새 sampler의 필요성이나 rare-failure preservation 효과로 해석하지 않는다.

Run `20260917_001500`에서 1,604개 subset, target score 4,812개와 pair ordering 5,614개를
계산했다. Split A target은 π₀ 계열 4개, split B는 OpenVLA/OpenVLA-OFT 2개다.
각 random method/budget/split은 200 seeds, greedy는 deterministic 1회다.
관찰 코드의 측정 시간은 약 0.31초이며 build·검산·해석 시간은 포함하지 않는다.

### Overall score, ordering and coverage

Score MAE 단위는 percentage points(pp)이며 target 모델과 draw 전체 평균이다.
Ordering denominator는 reference가 다른 모든 pair × draw다. 두 split을 합산하지 않는다.
관측 stratum은 category × level 총 12개 중 평균 개수다.

| Split | Cells | Method | Score MAE (pp) | Reversed / distinct pairs | Predicted ties | Observed strata / 12 | Complete draws |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | 12 | Uniform | 6.477 | 205 / 1,200 | 5 | 7.845 | 0 / 200 |
| A | 12 | Stratified | 4.850 | 208 / 1,200 | 0 | 12 | 200 / 200 |
| A | 12 | Greedy | 5.860 | 2 / 6 | 0 | 6 | 0 / 1 |
| A | 18 | Uniform | 4.542 | 162 / 1,200 | 4 | 9.735 | 7 / 200 |
| A | 18 | Stratified | 3.712 | 144 / 1,200 | 3 | 12 | 200 / 200 |
| A | 18 | Greedy | 3.221 | 1 / 6 | 0 | 9 | 0 / 1 |
| B | 12 | Uniform | 5.995 | 87 / 200 | 5 | 7.845 | 0 / 200 |
| B | 12 | Stratified | 4.939 | 88 / 200 | 0 | 12 | 200 / 200 |
| B | 12 | Greedy | 3.636 | 1 / 1 | 0 | 7 | 0 / 1 |
| B | 18 | Uniform | 4.379 | 78 / 200 | 1 | 9.735 | 7 / 200 |
| B | 18 | Stratified | 3.634 | 88 / 200 | 1 | 12 | 200 / 200 |
| B | 18 | Greedy | 0.965 | 1 / 1 | 0 | 9 | 0 / 1 |

Reference tie는 이 cohort에서 0개다. 동일 seed의 random subset은 A/B에 공통이므로 같은
coverage가 두 번 나타나는 것은 독립 반복 evidence가 아니다. Greedy의 1/1을 model 모집단의
100% 실패율로 쓰지 않는다. [정밀 값과 denominator](summary.csv)를 보존한다.

Stratification은 설계대로 모든 stratum을 관측했다. Full-profile MAE는 12-cell budget에서
A 10.282 / B 10.557 pp, 18-cell에서 A 7.384 / B 7.613 pp다. **Coverage가 완전하다는 사실은
profile를 정확히 복원했다는 뜻이 아니다.** Uniform의 18-cell full-profile MAE는 완전한
7/200 draw에만 정의되므로 이를 stratified의 200/200 평균과 직접 비교하지 않는다.
Missing 조건을 제외한 partial MAE만으로 방법의 우열을 정하지 않았다.

### Case-level explanation

Split B, 18-cell greedy에서 OpenVLA의 macro score는 39.273% → 39.000%, OpenVLA-OFT는
39.879% → 38.222%다. 두 target의 평균 absolute error는 0.965 pp지만 두 모델의 순위가
뒤집히고 **Long Horizon의 L0/L1/L2가 모두 빠졌다**. OpenVLA-OFT의 Distractor/L1 profile은
27%인데 선택된 suite만 보면 0%다. 이 사례는 작은 overall error가 조건별 정보 보존을
보장하지 않는다는 실제 공개 표의 예이며 learned sampler의 이점에 대한 증거는 아니다.

결과를 본 뒤 [`diagnose.py`](diagnose.py)로 모든 greedy target case와 모든 pair를 검토했다.
새 subset·threshold·metric을 선택하지 않고 원래 출력은 유지했다. `verification/diagnosis.json`은
12개 greedy case에 대해 다음 signed-error 분해를 원본 decimal의 rational arithmetic으로 확인한다.

```text
overall error = sum_h [ q_h (sampled_mean_h - full_mean_h)
                       + (q_h - p_h) full_mean_h ]
p_h = N_h / 33, q_h = selected_count_h / budget
```

Missing stratum은 q=0이어서 첫 항만 0이며 full mean을 0으로 대입하지 않는다. 이 분해는
within-stratum 추정 오차와 allocation 차이가 전체 평균에서 상쇄될 수 있음을 설명한다.
새 방법이나 새로운 통계 원리로 주장하지 않는다.

순위 역전은 gap과 함께 읽어야 한다. 18-cell split A에서 차이가 16.667–19 pp인 π₀-FAST와
다른 세 모델의 pair는 세 방식 모두 역전이 없었다. Stratified의 역전 144개는 reference gap
0.212 pp pair의 81개, 2.121 pp pair의 52개, 2.333 pp pair의 11개다. Split B는 reference gap이
0.606 pp인 한 pair뿐이며 stratified는 88/200 역전, 1/200 tie다. 이는 **정해진 유한 표의
순위 재현** 결과이며 실제 policy 간 유의한 우열·동등성이나 CI를 알려 주지 않는다.

### Interpretation and next decision

사실: 단순 stratification은 누락을 없애고 이 표의 두 split·두 budget 모두에서 uniform보다
score MAE가 작았다. 모든 ranking을 더 잘 복원하지는 않았고 profile 오차도 남았다.
Greedy가 모든 상황에서 uniform보다 좋거나 나쁘다는 일관된 결과도 아니다.

에이전트 추론: 현재 관찰은 평균 보존만을 진단용 표 보존으로 대체할 수 없다는 사례를 준다.
그러나 coverage 문제는 단순 층화로 처리할 수 있고, 잔여 순위 차이는 작은 reference gap을
포함한다. 이를 근거로 복잡한 learned sampler·tail-aware method를 바로 제안할 수는 없다.
Published means만으로 rare-event prevalence와 trial noise를 구분하지 못한다.

이 결과 직후에는 episode-level 관찰에서 구분할 질문, 단순 stratification과 기존
sequential comparison의 설명 범위·비용을 다음 투자 판단으로 정했다. 이후 해당 비교를
완료했고 [LBM 후속 관찰을 선택](#follow-up-decision-2026-09-17)했다.
같은 aggregate table의 model·seed·budget 확대는 다음 TODO로 선택하지 않았다.
이는 정보 부족과 투자 판단이며 broad CD2의 반증이나 최종 novelty gate가 아니다.

## Verification And Reproduction

Independent verifier가 원본 decimal을 exact rational로 읽어 모든 target score·profile·pair와
greedy step을 재구성했다. 12개 summary, seed/공통 subset, unequal stratum weights,
missing/tie 처리와 full-budget 대조를 통과했다. 검사 수 312,860은 독립 scientific 표본 수가
아니다. 사후 진단의 exact error 분해 12개도 일치했다.

Image immutable reference: `sha256:f06bf7c80a1a517630f65e190f96b190c4c53ae6a6ccabf88978043ed122594e`.
Python 3.11.14, standard library, CPU 2 / RAM 1 GiB다. 실제 image metadata와 source hash는
output의 `image.json`/`execution.json`, 요약과 artifact hashes는 [artifacts.json](artifacts.json)에 둔다.
원래 관찰을 바꾸지 않은 추가 진단 command는 output `diagnose.command.json`이다.

검산 재실행은 기록된 image로 `verify.py --input /input --output /output --receipt
/verification/receipt.json`을 수행하며 source와 기존 output은 read-only로 mount한다.
정확한 container options는 `commands.txt`와 saved inspect를 따른다. 새 receipt를 쓸 별도
폴더/경로를 사용하고 기존 검증 기록을 덮지 않는다. Image를 잃었으면 새 tag로 pinned recipe를
build하고 manifest의 code/input identity를 확인한다. 모든 실행은 Docker 안에서 한다.

## Container Cleanup

결과·입력·source·로그·image identity·inspect와 hash를 보존한 뒤 이번 workspace의 종료
container 세 개(`run`, `verify`, `diagnose`)만 삭제했다. CID file, 생성 command, workspace/
study/run labels, input/output mounts, 종료 상태와 exit 0을 모두 대조했다. 다른 container,
image, volume과 build cache는 건드리지 않았다. 실행 image와 모든 결과는 유지한다.
Full CID와 삭제 근거는 output `cleanup.json`, `logs/20260917_001500_cd2_cleanup.log` 및
[compact manifest](artifacts.json)에 기록했다.

## Follow-up Decision 2026-09-17

첫 aggregate-result 실행은 위 기록대로 완료됐다. 이후 [선행·입력·비용 비교](../../../robotics/related_work/policy-geometry.md#cd2-follow-up-assessment-2026-09-17)에서
LBM의 task별 episode 관찰 한 번을 선택했다. 선택 당시 question status는 `feasibility_study`,
후속 실행 status는 `not_started`였다. 이후 [실행·해석](#episode-results-2026-09-17)을 완료했다.
[구체적 설계](../../questions/tail-preserving-efficient-evaluation.md#episode-level-follow-up)에
따라 task mix와 within-task variation을 분리한다. 위 VLA-Arena 결과와 분모를 섞지 않는다.

Input cache는 `runs/cd2-review/20260917/nscore/`이며
[source record](../../../robotics/related_work/comparison_sources.json)의 `cd2_followup_20260917`이
immutable URL·SHA256을 소유한다. 원본 pickle을 읽거나 numerical analysis를 하는 단계는
Docker 안에서 수행한다. Pickle provenance·schema와 NPY mapping을 확인한 뒤 정규화된
입력으로 실행한다. 현재까지 host에서 한 일은 다운로드·source/byte/header 검토뿐이다.

후속 구현 때 이 폴더의 별도 episode entrypoint/config와 새 image tag·run ID를 사용하고
정확한 build/run/verification 명령을 여기에 추가한다. 준비·실행·검산·해석을 하나의 TODO로
묶으며 첫 실행의 recipe·output·image identity를 덮어쓰지 않는다. 이번 검토에서는 container를
생성·실행·삭제하지 않았다. Episode-level empirical 결과와 원 논문 재현은 아직 없다.

## Episode Execution

Status: `completed`. 선택한 LBM 후속 관찰의 준비·실행·검산·해석을 완료했다.
Code/config는 `episodes/`, input은 `runs/cd2-review/20260917/`, 새 output은
`runs/cd2-episodes/<run-id>/`다. Source manifest를 먼저 검사하고 Docker 안에서 pickle을
정규화한다. 기존 VLA-Arena 출력·image tag는 유지한다. 새 image는
`research3-cd2-episodes:v1`이며 pinned public Python base와 고정 NumPy/pandas를 사용한다.
Input/code는 read-only, output만 writable이고 CPU 2 / RAM 1 GiB / network none으로 실행한다.
실행 명령·image identity·dependency versions·source hashes와 검산 결과를 output에 보존한다.

Implementation clarification before results: 두 policy의 RNG stream은 분리하며 task는
사전순으로 정렬한다. 두 metric은 같은 record indices를 사용한다. Budget별 subset은
동일 permutation의 prefix다. 비교 seed는 고정 자료의 Monte Carlo 반복이며 robot trial
반복이 아니다. Sign tolerance는 `1e-12`이고 practical equivalence 기준이 아니다.
Full-profile metric은 필요한 모든 task를 관측했을 때만 계산하며 partial metric의 denominator를
함께 보존한다. 두 metric 또는 두 policy의 반복을 독립 연구 evidence로 합치지 않는다.

Run ID: `20260917_005800`; working directory `/home/yoohyun/research3`.
Build는 같은 Dockerfile에 `docker build --pull --iidfile
runs/cd2-episodes/20260917_005800/image.id -t research3-cd2-episodes:v1
buildup/cross_domain/pilot_studies/cd2-evaluation/episodes`로 시작했다.
후속 phase의 재현 명령은 아래와 같으며 fresh run에서 `build` phase는 새 image tag를 요구한다.

```bash
tmux new-session -d -s research3_cd2_ep_inspect_20260917_005800 'cd /home/yoohyun/research3 && bash buildup/cross_domain/pilot_studies/cd2-evaluation/episodes/execute.sh 20260917_005800 inspect > logs/20260917_005800_cd2_ep_inspect.log 2>&1'
tmux new-session -d -s research3_cd2_ep_run_20260917_005800 'cd /home/yoohyun/research3 && bash buildup/cross_domain/pilot_studies/cd2-evaluation/episodes/execute.sh 20260917_005800 run > logs/20260917_005800_cd2_ep_run.log 2>&1'
tmux new-session -d -s research3_cd2_ep_verify_20260917_005800 'cd /home/yoohyun/research3 && bash buildup/cross_domain/pilot_studies/cd2-evaluation/episodes/execute.sh 20260917_005800 verify > logs/20260917_005800_cd2_ep_verify.log 2>&1'
```

예상 outputs: `schema.json`, `normalized.json`, `reference.json`, `subsets.jsonl`,
`scores.jsonl`, `gaps.jsonl`, `summary.csv/json`, `task_summary.csv/json`, `execution.json`,
`verification/receipt.json`; phase log/exit는 `logs/20260917_005800_cd2_ep_*`다.
수치 검산은 별도 `verify` container에서 원본 NPY와 Fraction 연산으로 재구성한다.

### Input interpretation correction

첫 run `20260917_005800`은 수치 sampling 전에 NPY mapping assertion으로 종료했다.
Adapter가 `LBM/Part2`를 binary success, `PC_LBM/Part2`를 progress로 예상한 것이 원인이다.
같은 image의 `diagnose` phase에서 10개 파일을 원본 pickle과 대조해 두 폴더 모두 progress
sequence임을 확인했다. 각 파일의 column 0/1은 finetune/single-task 순서다.
폴더 이름만으로 metric을 정한 **우리 adapter의 가정**을 수정하며 upstream label 오류라고
단정하지 않는다. Binary outcome은 원본 pickle의 명시적 `success` field만 사용한다.

실패 당시 source snapshot·container inspect·log와 `input_diagnosis.json`을 보존한다.
정정 adapter는 모든 NPY를 이름에 무관하게 원본 metric/column과 대조한다. 입력 cohort,
budget, seed, metric definition과 estimator는 바꾸지 않는다. Diagnosis에서 full task means를
이미 보았으며 후속 결과는 원래 계획대로 탐색이다. 새 run ID에서 실행해 실패 기록을 덮지 않는다.

정정 run ID는 `20260917_010607`이다. 위 `run`/`verify` 명령의 run ID와 log/session 이름을
이 값으로 바꿔 실행한다. Image는 이번 study에서 생성한 동일 immutable image를 사용하며
실제 build origin·변경 범위는 새 output의 `revision.json`에 보존한다. Status: `completed`.

### Post-observation diagnosis

Sampling 결과와 전체 Fraction 검산을 본 뒤 global/task gap의 차이를 해석하기 위해
`analyze` phase를 추가했다. 설계 변경·재추출 없이 동일 공개 표의 finite-population mean
variance와 binary task의 exact hypergeometric ordering probability를 계산한다.
목적은 작은 gap에서 관측한 sign 변동이 단순 sampling 설명과 맞는지 확인하는 것이다.
Population parameter의 CI나 신규 baseline 결과가 아니다. Analysis code와
`diagnostics.json`을 별도 보존하고 budget/seed/원래 결과를 변경하지 않는다.

```bash
tmux new-session -d -s research3_cd2_ep_analyze_20260917_010607 'cd /home/yoohyun/research3 && bash buildup/cross_domain/pilot_studies/cd2-evaluation/episodes/execute.sh 20260917_010607 analyze > logs/20260917_010607_cd2_ep_analyze.log 2>&1'
```

## Episode Results 2026-09-17

**판단: 현재 generic mean/profile-preservation 경로의 추가 투자는 `deferred`.**
단순 task stratification 뒤에도 작은 task gap의 순위는 흔들렸지만, 이 기록에서는 유한
표본 변동과 서로 다른 평가 목표로 설명된다. 새 sampler의 필요성을 지지하는 관찰은 아니다.
원래 rare/severe failure 질문의 반증이나 실제 deployment policy 우열 판정과 구분한다.

### Inputs and verification

5 tasks × 2 policies × 50 trials = **500개 원본 기록**을 사용했다. Success/progress는
같은 기록의 두 metric이며 1,000개 독립 trial로 합치지 않는다. 200 seeds × 2 methods ×
4 budgets의 1,600개 subset 설정, 6,400개 policy/metric score, 3,200개 policy gap을 계산했다.
Run `20260917_010607`의 수치 실행은 약 0.28초이며 build·입력 진단·검산 시간은 별도다.
GPU·새 rollout·학습은 없었다.

독립 verifier는 원본 pickle의 명시적 label, progress NPY column, rational progress grid,
모든 score/profile/gap·signed-error decomposition과 summary/CSV를 재구성했다.
230,293개 구현 검사를 통과했다. 사후 분석의 확률질량·moment·variance identity 180개도
일치했다. 검사 수와 resampling seeds는 독립 scientific 표본 수가 아니다.
Binary는 pickle을 별도로 읽어 검산했으며 NPY의 독립 binary label 대조라고 보고하지 않는다.

Image immutable reference는 `sha256:30d669fb7787bc37e92a2152e79bf84e4f72b4576d649a4308a656bfafd27030`이다.
Python 3.11.14, NumPy 1.26.4, pandas 2.2.3을 사용했고 모든 dependency version은
[lock](episodes/requirements.lock), wheel URL/hash는 output `install.json`에 남겼다.
입력·source·raw outputs·실패 기록·검산·image identity는 [compact manifest](episodes/artifacts.json)가 연결한다.

### Finite-record reference

Gap은 `finetune − single-task`, 단위는 pp다. 각 task의 50개 기록 평균이 reference이며
미지의 모집단 성능이나 policy의 통계적 우월성을 의미하지 않는다.

| Task | Success single / fine (%) | Success gap (pp) | Progress gap (pp) |
| --- | ---: | ---: | ---: |
| BikeRotorInstall | 28 / 18 | −10 | −2.923 |
| CleanLitterBox | 8 / 6 | −2 | +21.143 |
| ClearKitchenCounter | 14 / 44 | +30 | +37.143 |
| CutAppleIntoSlices | 8 / 18 | +10 | +16.714 |
| SetUpBreakfastTable | 0 / 38 | +38 | +38.500 |
| Equal-task macro | 11.6 / 24.8 | +13.2 | +22.115 |

CleanLitterBox에서 두 metric의 reference 방향이 다른 것은 sampling error가 아니다.
Success와 partial progress가 다른 대상을 측정한다는 사실이며 partial-credit 자체는
이미 검토한 N-SCORE의 범위다. 이 숫자만으로 어느 metric이 robot task의 올바른 목표인지
정하거나 failure severity를 추론하지 않는다. 같은 array position의 metric linkage는
저자 record 구조를 따르며 별도 episode ID/영상으로 physical trial을 감사한 것은 아니다.

### Global versus task-level errors

아래 모든 row는 complete task-gap profile 200/200이다. Task gap MAE는 draw마다
5-task 절대 오차를 평균한 값, Max task gap error는 draw별 최대 절대 오차의 평균이다.
전체 distribution과 모든 budget은 [summary](episodes/summary.csv), task별 값은
[task summary](episodes/task_summary.csv)에 둔다. 표본 수는 **task/policy당 n**, total access는 `10n`이다.

| n | Metric | Sampling | Global gap MAE (pp) | Task gap MAE (pp) | Max task gap error (pp) | Correct global order / 200 |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 10 | Success | Uniform | 5.344 | 11.472 | 24.160 | 194 |
| 10 | Success | Stratified | 5.336 | 11.108 | 22.620 | 195 |
| 10 | Progress | Uniform | 4.122 | 9.281 | 18.811 | 200 |
| 10 | Progress | Stratified | 4.159 | 8.929 | 17.568 | 200 |
| 25 | Success | Uniform | 2.568 | 5.710 | 11.528 | 200 |
| 25 | Success | Stratified | 2.720 | 6.016 | 11.480 | 200 |
| 25 | Progress | Uniform | 1.890 | 4.236 | 8.698 | 200 |
| 25 | Progress | Stratified | 1.976 | 4.198 | 8.401 | 200 |

최소 budget n=5에서는 Uniform의 400 policy draws 중 8개에 missing task가 있으며
complete gap profiles는 192/200이다. Stratified는 200/200으로 누락을 없앤다.
이 budget의 conditional profile error를 동일 coverage 결과처럼 비교하지 않는다.
Full n=50은 원본 평균·모든 profile을 exact rational 기준 완전히 복원했다.
Floating output의 약 1e−15 pp는 roundoff이며 실제 잔여 오차가 아니다.

### What explains the remaining reversals

Stratified n=25에서 전체 순위는 success/progress 모두 200/200 유지했지만,
BikeRotorInstall의 progress 순위는 55회 역전·6회 tie였다. Reference gap이 −2.923 pp로 작다.
CleanLitterBox success는 47회 역전·65회 tie·88회 correct였으며 원본 성공 수 차이는
4/50 대 3/50뿐이다. Global +13.2/+22.115 pp와 이 task gap을 같은 난이도의 비교로 볼 수 없다.

사후 exact hypergeometric 계산에서 CleanLitterBox의 n=25 success 순위 확률은
correct **50.000%**, reversed **21.918%**, tie **28.082%**다. 실제 200-draw 빈도는
44.0%, 23.5%, 32.5%였다. BikeRotorInstall success의 예상 reversed는 7.611%, 관찰은
15/200 = 7.5%다. 이는 이 유한 표에 대한 sampling 법칙이며 population hypothesis test가 아니다.

Uniform의 global-gap variance 중 task mix 항은 success **9.853%**, progress **11.399%**다.
나머지는 within-task 항이며 두 항의 covariance가 0임을 exact arithmetic으로 확인했다.
이는 variance 비율이고 MAE끼리 더한 비율이 아니다. Stratification은 mix 항을 없애지만
within-task variation을 없애지는 않는다. n=25의 예상 global-gap SD는 success
Uniform 3.407 / Stratified 3.261 pp, progress 2.622 / 2.488 pp다. 200개의 Monte Carlo
draw에서 MAE가 조금 역전됐다는 이유로 Uniform의 population 우세를 주장하지 않는다.

### Investment decision and re-entry

에이전트 판단: 첫 aggregate 관찰의 coverage 문제에는 stratification이 단순 대안이고,
이번 episode 관찰의 잔여 순위 변화에는 작은 task gap·within-task variation이라는 설명이
있다. 두 metric의 목표 차이는 실제 관찰이지만 새 algorithm을 요구하는 실패 원리는 아직 아니다.
이 조합에서 같은 data의 seed/budget 확대나 새 sampler를 다음 작업으로 선택하지 않는다.
현재 경로를 보류하고 Q3, Q4와 관련 CD5의 작은 관찰을 다음 투자 대상으로 비교한다.

보류는 positive residual·두 번째 dataset·최종 novelty gate의 미통과 판정이 아니다.
현재 자료가 답하는 문제가 기존 sampling/metric 구분을 넘어서지 않아 추가 정보 가치가
낮다는 투자 판단이다. 원래 rare/severe failure의 prevalence/coverage는 계속 미해결이다.
실제 평가 결정을 바꾸는 조건별 loss나 명시적 failure severity를 가진 작은 공개/constructed
사례가 구체화되면 다시 비교할 수 있다. 데이터 공개나 label 추가만으로 자동 재개하지 않는다.

### Episode container cleanup

실패 run의 inspect/run/diagnose와 정정 run의 run/verify/analyze, 총 6개 종료 container를
삭제했다. CID file·생성 command·workspace/study/run/phase labels·image ID·mount·종료 상태를
모두 대조했고, source/output 52개와 log/exit 14개를 보존·hash 확인했다. 실패 run의 exit 1도
그대로 남긴다. 삭제 명령·소유권 확인·보존 근거는 두 output의 `cleanup.json`과
`logs/20260917_010607_cd2_ep_cleanup.log`에 있다. 이 image와 입력·결과는 유지했으며
다른 container/image/volume/cache는 건드리지 않았다.
