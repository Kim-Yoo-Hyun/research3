# CD5 Information-Budgeted Representation Utility

Updated: 2026-09-04

## Status

`exploratory`

## Facts

- 현재 선택된 representation, downstream policy, dataset 또는 information-budget 정의는
  없다.
- Robotics 3D route는 Q4 Task-Relevant Spatial State와 일부 겹친다.
- 새 foundation model training은 허용 범위가 아니다.

## Source Claims

- NeurIPS 2024 [Paloma](https://proceedings.neurips.cc/paper_files/paper/2024/hash/760b2d94398aa61468aa3bc11506d9ea-Abstract-Datasets_and_Benchmarks_Track.html)는
  단일 distribution perplexity가 다른 domain fit을 대표한다고 가정하지 않고 546개
  English/code domain을 평가한다.
- Q4의 prior audit에는 task-dependent 3D scene representation이 가까운 overlap으로
  기록돼 있다.

## Agent Inference

Raw observation/retrieved context/dense 3D map와 structured graph를 비교할 때 input length,
oracle preprocessing, field of view, update rate와 compute가 같이 변하면 representation
form의 이득과 추가 task-relevant information의 이득이 혼동된다.

## Research Question Or Suspected Phenomenon

동일한 task-relevant information, byte/token budget, latency와 downstream policy를 matched
control로 고정했을 때 structured state가 raw 또는 relevance-ranked top-k summary보다
closed-loop/task accuracy를 실제로 개선하는가?

## Significance

Representation 논문의 개선이 구조 자체에서 오는지 evaluator/teacher privilege와 더 큰
정보 budget에서 오는지 분리한다. Robotics 3D state와 RAG/agent context를 같은
information-allocation question으로 연결할 수 있다.

## Current State Of The Art And Limitation

Task-centric 3D representation, RAG, context compression과 feature selection prior가 모두
강하다. 남는 gap은 새 representation이 아니라 matched information/compute control에서
downstream utility residual이 존재하는지다.

## Evaluation Target

- primary: fixed information and latency budget의 downstream task success/accuracy
- secondary: bytes/tokens, FLOPs/latency, robustness under irrelevant information
- denominator: tasks × frozen policies/models × budget levels × representation forms

## Available Data / Code / Evaluator

Embodied 3D state selection 또는 long-context/RAG evidence selection의 public frozen
outputs가 후보다. 첫 domain에서 동일 정보를 losslessly cross-serialize할 수 있는
artifact는 미확인이다.

## Simplest Baseline Or Counterexample

Random/top-k relevance selection, raw serialization, shuffled structure, oracle relevance mask와
lossless field permutation을 비교한다. Relevance-ranked top-k가 structured form의 이득을
없애면 종료한다.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| same-information control을 정의할 수 있다 | serialization마다 정보가 실질적으로 다르다 | invertibility/schema audit |
| structure form이 simple top-k 뒤에도 도움된다 | top-k가 성능을 모두 복원한다 | frozen-output probe |
| downstream evaluator가 공개된다 | representation metric만 있고 task metric이 없다 | artifact audit |

## Feasibility Or Pilot Study

한 accessible public dataset에서 frozen model/policy와 3개 budget level을 사용해 raw,
top-k, shuffled-structure, structured input을 비교한다. 학습 없이 serialization/input
ablation만 먼저 한다. 다른 domain은 이후 rigorous evaluation path다.

## Preliminary Success Criteria

동일 정보·compute control 뒤에도 structured representation의 practical downstream
residual이 나타나야 한다.

## Expected Deliverable

Information-budget fairness protocol, representation×budget curve와 structure-specific
residual에 대한 selection decision.

## Timeline And Milestones

- week 1: prior/artifact and information-equivalence audit
- week 2: one-domain frozen-output kill test
- 이후는 `select for hypothesis formulation` 결정이 있을 때만 진행

## Interpretation Of A Negative Result

Top-k relevance 또는 matched raw serialization이 성능을 복원하면 새 representation을
만들지 않는다. Same-information condition 자체가 불가능하면 question을 reformulate한다.

## Resource Requirements

Public frozen outputs/evaluator, CPU 또는 moderate inference. Training, human annotation과
hardware 불필요.

## Related-Work Overlap

`high`. Q4, task-centric representations, RAG와 context compression에 direct prior가 많다.

## User Decision Needed

없음.
