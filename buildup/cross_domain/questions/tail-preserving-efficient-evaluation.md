# CD2 Tail-Preserving Efficient Evaluation

Updated: 2026-09-04

## Status

`exploratory`

## Facts

- 이 workspace에서는 model-by-item score matrix를 내려받거나 resampling하지 않았다.
- Candidate의 rare-failure taxonomy, severity threshold와 sample budget은 미정이다.
- Offline score matrix가 있으면 새 model training 없이 평가할 수 있다.

## Source Claims

- NeurIPS 2024 [Collaborative Computerized Adaptive Testing](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ad48f017e6c3d474caf511208e600459-Abstract-Conference.html)은
  adaptive testing에서 ability estimation뿐 아니라 ranking consistency를 직접 최적화한다.
- NeurIPS 2024 [Easy2Hard-Bench](https://proceedings.neurips.cc/paper_files/paper/2024/hash/4e6f22305275966513990f53cec908e0-Abstract-Datasets_and_Benchmarks_Track.html)는
  human/LLM performance와 IRT/Glicko-2를 이용해 six-domain item difficulty를 제공한다.

## Agent Inference

평균 score와 model ranking을 잘 보존하는 subset도 low-frequency/high-severity failure
stratum을 충분히 관측하지 않을 수 있다. Efficient ranking과 failure discovery는 다른
sampling objective일 가능성이 있다.

## Research Question Or Suspected Phenomenon

전체 benchmark의 5--20%만 평가할 때 uniform, difficulty-stratified, IRT-adaptive sampling
중 어느 방식이 model ranking과 preregistered rare-failure prevalence/coverage를 동시에
보존하는가?

## Significance

비용이 큰 VLA/agent/LLM evaluation에서 적은 sample로 leaderboard를 복원하면서도 중요한
failure를 숨기지 않는 평가 설계를 제공할 수 있다.

## Current State Of The Art And Limitation

Adaptive testing과 efficient model ranking은 성숙한 prior다. Candidate가 성립하려면 rank
fidelity만이 아니라 held-out rare-failure recall, prevalence estimation과 severity
coverage를 joint constraint로 둔 명확한 residue가 있어야 한다.

## Evaluation Target

- primary: full-matrix ranking Kendall tau subject to rare-stratum recall/prevalence error
- secondary: budget, worst-stratum coverage, maximum rank shift와 confidence interval
- denominator: models × items × sampling budgets × repeated sampling seeds

## Available Data / Code / Evaluator

완전한 model-by-item 결과와 사전 failure metadata가 있는 LLM reasoning/agent benchmark
또는 robotics/VLA condition matrix가 필요하다. 첫 accessible matrix는 미확인이다.

## Simplest Baseline Or Counterexample

Uniform sampling, difficulty/severity proportional stratification, Neyman allocation과
coverage-constrained greedy selection을 먼저 비교한다. 이들이 충분하면 learned sampler나
IRT extension을 만들지 않는다.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| public full result matrix가 있다 | aggregate leaderboard만 공개된다 | schema audit |
| rare stratum을 outcome 전에 정의할 수 있다 | result를 본 뒤 label을 만들어야 한다 | metadata audit |
| rank-efficient sampler가 tail을 놓친다 | 모든 sampler의 tail coverage가 동일하다 | offline 10% resampling |
| simple stratification 뒤 residual이 있다 | stratification이 joint target을 충족한다 | strongest baseline first |

## Feasibility Or Pilot Study

한 공개 score matrix에서 budget `{5, 10, 20}%`, 1000 resampling seeds와 frozen failure
strata로 learning-free comparison을 수행한다. 다른 benchmark는 이후 rigorous evaluation
path로만 기록한다.

## Preliminary Success Criteria

Adaptive rank baseline이 높은 rank fidelity에도 rare-stratum coverage 또는 prevalence에서
practical margin을 넘게 실패하고, simple stratification 뒤에도 joint constraint residual이
남아야 한다.

## Expected Deliverable

Budget-rank-tail Pareto curve, missed-failure audit와 constrained allocation 필요성 판정.

## Timeline And Milestones

- day 1--2: direct prior, matrix와 metadata audit
- day 3: failure strata/budget manifest
- day 4--6: offline resampling/simple baselines
- day 7: selection decision

## Interpretation Of A Negative Result

Uniform 또는 severity-stratified sampling이 rank와 tail을 모두 보존하면 새 method 없이
종료하고, 해당 simple protocol만 evaluation recommendation으로 남긴다.

## Resource Requirements

Public matrix, CPU/RAM 중심 computation. Model inference, human annotation과 hardware는
필요하지 않아야 한다.

## Related-Work Overlap

`high`. Efficient/adaptive ranking은 direct prior가 점유한다. Tail-preservation의 exact
novelty audit 없이는 진행하지 않는다.

## User Decision Needed

없음.
