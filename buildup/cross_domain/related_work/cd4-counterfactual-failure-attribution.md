# CD4 Counterfactual Failure Attribution: Preliminary Prior Audit

Updated: 2026-09-04

## Audit Boundary

- Candidate: [Counterfactual Failure Attribution](../questions/counterfactual-failure-attribution.md)
- Exact question under audit: failed trajectory의 한 step을 수정하고 downstream suffix를
  다시 실행했을 때의 outcome change로 post-hoc diagnosis의 causal validity를 평가하는가?
- Search window: 2025--2026 primary papers, official paper pages and official repositories
- 이 문서는 `docs/buildup.md` Stage 4의 preliminary review다. Final novelty 판정이나
  hypothesis selection은 아니다.

## Facts

- 현재 CD4의 핵심 조작인 **single-step intervention + downstream re-execution + outcome
  change에 의한 attribution**은 아래 direct prior에서 명시적으로 사용된다.
- CAR만 public executable implementation을 즉시 확인했다. AgenTracer와
  AgenticRAG-FP는 paper/project claim은 확인했지만 이번 audit에서 공식 executable
  repository와 complete public dataset을 확인하지 못했다.
- 어떤 external repository, model 또는 dataset도 내려받거나 실행하지 않았다.

## Nearest Primary Work

### AgenTracer — 2025

Official sources: [paper](https://arxiv.org/abs/2509.03312),
[project](https://bingreeky.github.io/atracer/)

**Exact question and contribution.** Failed multi-agent trajectory에서 oracle action으로
한 step을 교체하고 suffix를 다시 실행해 success로 바뀌는 가장 이른 action을 decisive
error로 정의한다. 이 counterfactual replay와 successful-trace fault injection으로
TracerTraj-2.5K를 만들고 Qwen3-8B tracer를 학습한다.

**Boundary.** LLM multi-agent coding, math와 general-agent tasks가 대상이다. Oracle
correction은 analyzer LLM과 ground-truth solution에 의존하고, reported training은
8×H100을 사용한다. 이번 audit에서는 official code/data download route를 확인하지 못했다.

**Relevant baselines.** Qwen/Llama direct attribution과 GPT-4.1, DeepSeek-R1,
Gemini-2.5-Pro, Claude-Sonnet-4 같은 prompted LLM attribution이 adjacent baselines다.

### Causal Agent Replay (CAR) — 2026

Official sources: [paper](https://arxiv.org/abs/2606.08275),
[code](https://github.com/jaineet17/causal-agent-replay)

**Exact question and contribution.** Recorded LLM-agent run을 structural causal model로
표현하고 `do_resample`, forced action/observation/context/policy intervention 뒤 suffix를
재실행해 outcome distribution의 변화를 측정한다. Single-step contrastive estimator,
point-of-commitment rule, Monte-Carlo Shapley와 confidence interval을 제공한다.

**Boundary.** Pivotal-step와 interaction validation은 planted synthetic SCM이고 실제
side effect가 있는 tool은 제외한다. Hosted-model nondeterminism은 제거하지 않고 replay
action-match rate와 outcome distribution으로 보고한다.

**Artifact access.** Public Apache-2.0 repository의 audit 당시 HEAD는
`db90fa28b97164c35e7c524e4597b8cbdb3035af`다. Core code, tests, synthetic demo,
Who&When data folder와 local-model route가 보인다. 이 사실은 실행 가능성을 뜻하지만
real robot/continuous-control validity를 뜻하지 않는다.

### AgenticRAG-FP — 2026

Official source: [paper](https://arxiv.org/abs/2608.20627)

**Exact question and contribution.** Multi-hop RAG의 특정 hop에 certified retrieval/content
fault를 주입하고 suffix를 재실행한 뒤, post-hoc diagnoser가 injected hop을 회복하는지
평가한다. Coverage, LLM judge, frozen-hop repair와 suffix-regeneration repair를 비교하고
recovery와 attribution denominator를 분리한다.

**Boundary.** RAG retrieval/content corruption에 국한되고 main cells도 complete factorial
sweep가 아니다. Content-fault depth-2 비교는 exploratory이며 depth-3은 failed case가
3개라 descriptive로 제한한다. ArXiv page에는 official code/data link가 없다.

## Minimum Difference From The Candidate

현재 CD4의 domain-general question과 method principle은 AgenTracer와 CAR에 직접
점유됐고, AgenticRAG-FP는 certified intervention과 suffix re-execution으로 empirical
benchmark gap까지 일부 점유한다. 따라서 다음은 novelty가 아니다.

- observational diagnosis보다 intervention이 더 causal하다는 주장;
- 한 step을 oracle-correct하고 suffix를 다시 실행하는 protocol;
- random/neighbor correction 대비 recovery lift로 attribution을 검증하는 것;
- earliest recovered step 또는 point of commitment를 root cause로 삼는 것.

확인되지 않은 최소 residue는 **continuous-control robotics에서 local action intervention의
물리적 유효성과 attribution identifiability**다. 그러나 off-manifold correction,
contact-state divergence와 action-interface dependence를 분리할 public denominator를 아직
찾지 못했으므로 새로운 candidate로 인정하지 않는다.

## Baseline Consequence

향후 robotics-specific reformulation을 검토한다면 최소 비교군은 다음이어야 한다.

1. random, temporal-neighbor와 last-action correction;
2. AgenTracer식 earliest oracle correction with suffix re-simulation;
3. CAR `do_resample` effect와 point-of-commitment rule;
4. full privileged correction 및 no-intervention control.

이보다 약한 post-hoc LLM judge만 비교해서는 현재 prior를 넘지 못한다.

## Preliminary Decision Evidence

- Related-work overlap: `high / direct collision`
- Original CD4 formulation: reformulation 없이는 유지할 근거가 없음
- Public executable substrate for the original idea: CAR가 있으나 이미 prior 자체임
- Robotics-specific residue feasibility: `NOT_ESTABLISHED`
- Final Stage 7 decision: `reformulate`; candidate status `deferred`

## User Decision Needed

없음. [Stage 7 selection decision](../../selection.md)에 따라 public continuous-control
substrate가 확인되기 전에는 진행하지 않는다.
