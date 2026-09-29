# CD5 Information-Budgeted Representation Utility

Updated: 2026-09-23

## Status

`deferred`

## Disposition 2026-09-23

사용자가 다른 후보 탐색·교체를 요청해 실행 선택을 철회했다. Model inference나 새로운
실험 결과에 따른 보류가 아니다. 2026-09-22의 입력·설계를 보존하며 그때의 선택은 아래
이력으로 남긴다. 현재 후보는 [Q16](../../robotics/questions/interaction-conditioned-motion.md)이다.
사용자가 CD5를 선호하지 않은 세부 이유는 명시하지 않았으므로 추정해 기록하지 않는다.

## Selected Observation 2026-09-22

**같은 initial facts의 표현·순서가 robot plan의 실제 실행 실패를 바꾸는지, 단순 정렬과
전제조건 보정으로 충분한지**를 다음 작은 관찰로 선택했다.
[직접 선행·후보 비교](../../robotics/related_work/policy-geometry.md#cd5-cd1-q8-comparison-2026-09-22)와
[설계·입력·비용 owner](../pilot_studies/cd5-representation/README.md)를 따른다.
Graph serialization 민감도와 verification/repair는 기존 연구에 있으며 새 기여로 주장하지 않는다.

공개 LookPlanGraph의 symbolic task 입력과 source를 읽기 전용으로 확보했다. 6개 development,
24개 observation에서 frozen local model 하나의 JSON/text × ordered/shuffled 입력을 비교한다.
Canonical PDDL로 복원한 Q4와 달리 model이 실제 다른 표현을 읽는다. 같은 정보와 공통
token 상한을 쓰되 실제 tokens/latency는 별도 보고하며 정확한 compute matching을 주장하지 않는다.
물리 simulator/부분 관측/real robot 결과가 아니고 아직 model inference도 없다.

아래 broad 원안의 raw/top-k/3-budget 및 cross-domain 비교는 이번 실행에 포함하지 않는다.
현재 선택은 정보 선택을 고정한 작은 form 비교다. 결과가 없거나 단순 대안으로 충분한
경우도 다음 투자 판단에 사용한다. Hypothesis formulation 또는 paper 승격은 없다.

## Review 2026-09-18

[Q4 관찰](../../robotics/questions/task-relevant-spatial-state.md#first-observation)의
same-information control로 연결했다. Taskography의 objects/init/goal을 losslessly
직렬화한 뒤 canonical PDDL로 복원하는 40개 대조를 통과했다.
[결과·검사 경계](../../robotics/pilot_studies/q4-planning/README.md#verification-and-repairs)를 따른다. Planner가 동일 입력으로
복원하는 구조이므로 독립적인 representation 성능 실험이나 LLM 개선 근거가 아니다.
Q4의 class별 instance quota는 closure 이전 budget이며 최종 fact/token 수의 matching과
구분한다. 아래 broad model/representation 비교는 미실행 원안이다.

## Review 2026-09-16

[Q4와 함께 재비교](../../robotics/related_work/policy-geometry.md#remaining-candidate-comparison-2026-09-16)했다.
이번 범위는 Robotics의 작은 scene/goal에서 **동일 facts의 serialization 대조**다.
Object를 고르는 selection과 같은 object/facts를 표현하는 form을 분리해야 한다.
Clio/ASHiTA의 task-driven representation이 직접 선행이며 RAG/LLM scope로 옮기지 않는다.
Q4와 함께 reserve로 유지하고 다음 관찰은 CD2를 선택했다. 아래 큰 원안은 실행하지 않았다.
Positive residual·exact novelty는 작은 관찰의 진행 gate가 아니다.

## Facts

- Q4의 Taskography canonicalization 대조는 완료했다. 현재는 위의 독립적인 frozen-model
  symbolic planning 비교를 선택했으며 실행 전이다.
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

Q4에서 Taskography의 공개 PDDL domain/test 입력을 확보했고 CPU Docker에서
same-information round trip을 확인했다. Long-context/RAG로 scope를 전환하지 않았다.

## Simplest Baseline Or Counterexample

Random/top-k relevance selection, raw serialization, shuffled structure, oracle relevance mask와
lossless field permutation을 비교한다. Top-k로 설명되는 차이와 form의 차이를 구분한다.

## Critical Assumptions

| assumption | disconfirming observation | cheaper measurement |
| --- | --- | --- |
| same-information control을 정의할 수 있다 | serialization마다 정보가 실질적으로 다르다 | invertibility/schema audit |
| structure form이 simple top-k 뒤에도 도움된다 | top-k가 성능을 모두 복원한다 | frozen-output probe |
| downstream evaluator가 공개된다 | representation metric만 있고 task metric이 없다 | artifact audit |

## Original Broad Pilot Outline — Not Selected

한 accessible public dataset에서 frozen model/policy와 3개 budget level을 사용해 raw,
top-k, shuffled-structure, structured input을 비교한다. 학습 없이 serialization/input
ablation만 먼저 한다. 다른 domain은 이후 rigorous evaluation path다.

## Observations To Interpret

동일 정보·compute control 뒤 downstream 차이가 남는지와 그 설명을 기록한다.
차이의 부재나 정보 matching의 실패도 후속 수정·투자 판단에 쓰며 효과를 요구하지 않는다.

## Expected Deliverable

Information-budget fairness protocol, representation×budget curve와 structure-specific
residual에 대한 selection decision.

## Timeline And Milestones

- week 1: prior/artifact and information-equivalence audit
- week 2: one-domain frozen-output kill test
- 위 일정은 초기 미실행 원안이다. 작은 후속 관찰·설명/방법 수정은 buildup 안에서 가능하다.

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
