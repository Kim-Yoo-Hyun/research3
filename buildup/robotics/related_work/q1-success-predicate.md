# Q1 Success Predicate: Focused Prior Audit

Updated: 2026-09-08

The original audit below records the 2026-09-04 assessment. Current disposition follows
the [refinement review](#refinement-pressure--2026-09-08).

## Audit Boundary

- Candidate: [Success-Predicate Stability](../questions/success-predicate-stability.md)
- Exact question: 같은 stored rollout에 의미상 동등한 success-predicate/tolerance family를
  적용할 때 manipulation policy ranking이 뒤집히는가?
- Search window: 2024--2026 primary papers and official project/code pages
- This audit distinguishes predicate-specification sensitivity from generic robustness,
  statistics, safety metrics and fine-grained behavior metrics.

## Facts

- Reviewed nearest works all question binary success or benchmark validity.
- None of the reviewed official descriptions reports a preregistered family of semantically
  equivalent task-success predicates and policy-pair rank-reversal rate.
- This absence is limited to the sources reviewed here and is not proof of final novelty.
- 어떤 external artifact도 local에 checkout, pull, build 또는 run하지 않았다.

## Nearest Primary Work

### What Are We Actually Benchmarking in Robot Manipulation? — 2026

Official sources: [paper](https://arxiv.org/abs/2606.04233),
[project and artifacts](https://ripl.github.io/manipulation_benchmark_audit/)

**Paper claim.** LIBERO, CALVIN, SimplerEnv, RoboCasa와 RoboTwin 2.0을 shortcut
solvability, statistical significance, creeping overfitting와 data-source dependence의 네
diagnostic으로 audit한다.

**Minimum difference.** 이 paper는 fixed evaluation setup의 capability validity를
감사하지만 success predicate 자체를 controlled variable로 바꾸지 않는다. Q1은 같은
rollout과 task semantics 아래 predicate family만 조작하고 ranking stability를 본다.

### RoboEval — 2025

Official sources: [paper](https://arxiv.org/abs/2507.00435),
[project and code](https://robo-eval.github.io/)

**Paper claim.** Bimanual manipulation task를 skill stage로 나누고 task progression,
trajectory efficiency, coordination, collision, slip와 jerk 같은 fine-grained metric을
추가해 binary success가 숨기는 policy 차이를 드러낸다.

**Minimum difference.** RoboEval은 metric vector와 task variation을 확장하지만 동일한
task-success semantics를 나타내는 alternative predicates가 policy ordering을 바꾸는지
평가하지 않는다.

### SafeVLA-Bench — 2026

Official source: [project and paper link](https://safevla.org/)

**Paper claim.** LIBERO와 RoboCasa-365의 native success와 별도로 STL-based Safety,
Succ-But-Unsafe와 Violation Severity Index를 post hoc으로 계산한다.

**Minimum difference.** Official protocol은 host observations, actions, seeds와 **native
success predicate를 보존**한다. 따라서 safety-success gap은 Q1의 task-success predicate
sensitivity와 다른 축이다.

### Embodied Agent Interface — NeurIPS 2024

Official source: [proceedings](https://papers.nips.cc/paper_files/paper/2024/hash/b631da756d1573c24c9ba9c702fde5a9-Abstract-Datasets_and_Benchmarks_Track.html)

**Paper claim.** Domain별 goal specification과 success criteria 차이를 표준 interface로
정리하고 LLM decision modules를 fine-grained error로 평가한다.

**Minimum difference.** Cross-domain goal formalization은 매우 가까운 motivation이지만,
within-task predicate-equivalence class와 induced policy rank reversal은 audit 대상이 아니다.

## Agent Inference

Q1의 exact manipulation은 현재 reviewed direct prior와 구분된다. 다만 benchmark audit,
graded metric, safety predicate와 goal formalization이 빠르게 밀집된 영역이라 contribution을
“binary success보다 richer metric”으로 쓰면 즉시 충돌한다. 살아남는 claim boundary는
오직 **predicate specification uncertainty가 comparative policy conclusion을 바꾸는지**와
그 simple continuous-margin control이다.

## Decision

- Related-work overlap: `medium`; exact collision was not found in this preliminary review
- Final novelty: `NOT_ESTABLISHED`
- Artifact/schema audit: [completed separately](q1-artifact-schema.md)
- Candidate status: `under_review`

다음 단계에서는 public benchmark가 state trajectory와 constituent success margins를
저장하거나 재계산할 수 있는지 확인하고, comparable input을 선택한 뒤 continuous margin,
temporal persistence와 bootstrap uncertainty를 feasibility protocol에 고정한다.

## User Decision Needed

없음. 모든 환경은 pre-existing local image를 참조하지 않는 새 Dockerfile과 새
project-specific image로만 구성한다.

## Refinement Pressure — 2026-09-08

**New primary source reviewed:** [Beyond Binary Success: Sample-Efficient and Statistically
Rigorous Robot Policy Comparison](https://arxiv.org/html/2603.13616v1), 2026-03-13, sections
I, IV--VI. **Paper claim:** N-SCORE uses safe, anytime-valid inference to compare policies with
binary, partial-credit and continuous performance measures while controlling Type-1 error.
This concerns efficient inference for defined metrics, not uncertainty about which success
specifications describe the same task. Merely replacing Q1 with richer metrics or sequential
ranking would face this adjacent method directly; exact collision with Q1 is not established.

**Rechecked primary descriptions:** [SafeVLA-Bench](https://safevla.org/) retains host success
while adding safety; [What Are We Actually Benchmarking in Robot Manipulation?](https://ripl.github.io/manipulation_benchmark_audit/)
audits shortcut solvability, significance, overfitting and data-source dependence. Neither
description provides the independent semantic calibration missing from the proposed Q1 refinement.
This bounded search is not an exhaustive novelty proof.

**Agent inference:** the original question remains distinct at the formulation level, but
distinction alone does not establish an informative next experiment after the negative v3.
The [artifact and semantics review](q1-artifact-schema.md#bounded-refinement-audit--2026-09-08)
found no grounded continuation. Current Q1 is `discontinued`; no paper contribution or formal
hypothesis is claimed, and no alternative is automatically promoted.
