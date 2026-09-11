# Task-Relevant Spatial State

Updated: 2026-09-04

## Status

`exploratory`

## Facts

- Public 3D scene graphs와 embodied task benchmarks를 연결할 수 있는 artifact가 있다.
- Clio는 task-driven open-set 3D scene graph와 pre-built graph를 공개한다.
- 이 workspace에서는 Clio data나 planner를 아직 실행하지 않았다.

## Source Claims

- [Clio](https://github.com/MIT-SPARK/Clio)는 task-relevant scene graph를 만들기 위한
  code, dataset와 pre-built graph를 제공하며 offline Python evaluation route가 있다.
- [VLA-Arena](https://vla-arena.github.io/)는 distractor와 long-horizon condition을
  명시적으로 포함한다.
- [FOCI](https://rffr.leggedrobotics.com/works/foci/)는 Gaussian Splats를 trajectory
  optimization의 collision representation으로 사용한다.

## Agent Inference

Dense 3D state가 항상 planner에 유리한 것은 아니다. Distractor가 많거나 context
budget이 제한될 때 task-conditioned compact state가 더 나을 수 있지만, 단순 top-k
semantic filtering으로 충분할 가능성도 높다. Clio가 task-dependent granularity를
직접 다루므로 overlap risk가 크다.

## Research Question Or Suspected Phenomenon

같은 object detections와 context/compute budget에서, task-conditioned compressed spatial
state가 dense all-object graph, top-k semantic retrieval와 2D state보다 downstream plan
validity 또는 execution success를 높이는 조건은 무엇인가?

## Significance

3D representation quality를 reconstruction metric이 아니라 robot decision utility로
평가할 수 있다. Negative result도 dense 3D preprocessing의 불필요한 비용을 줄이는
설계 근거가 된다.

## Current State Of The Art And Limitation

Clio는 task-aware graph compression을 직접 제안하므로 단순히 “task-relevant map이 더
좋다”는 주장은 점유됐을 가능성이 높다. 남을 수 있는 질문은 matched information
budget에서 downstream planner의 failure boundary와 simple retrieval residual이다.

## Evaluation Target

- primary: frozen planner의 executable plan rate 또는 simulator task success
- secondary: collision/precondition violation, prompt/state size, runtime
- denominator: scenes × task queries × state representations × fixed planner seeds
- matched controls: same detected objects, coordinate frame, context tokens and planner

## Available Data / Code / Evaluator

- Clio public dataset and pre-built scene graphs for offline schema/prompt studies
- VLA-Arena distractor tasks or a public simulator for downstream execution, subject to
  cross-dataset compatibility
- deterministic symbolic/spatial query evaluator를 first pilot으로 우선한다.

## Simplest Baseline Or Counterexample

1. All detected objects.
2. Text-embedding top-k objects.
3. Distance/reachability filtered objects.
4. Oracle task-relevant object subset.
5. 2D object list with the same token budget.

## Critical Assumptions

| Assumption | Disconfirming observation | Cheaper measurement |
| --- | --- | --- |
| Clio graph에 task query와 downstream-valid spatial facts가 있다. | mapping/evaluation에 필요한 ground truth가 없다. | pre-built graph schema audit |
| state representation만 바꾸고 planner를 고정할 수 있다. | planner마다 proprietary preprocessing이 강제된다. | open LLM or rule planner dry run |
| top-k baseline 뒤 residual이 있다. | simple semantic/spatial filtering이 oracle과 동률이다. | offline query subset |

## Feasibility Or Pilot Study

Pre-built graph의 소수 scene/task query를 사용해 all-object, semantic top-k,
distance-filtered, task-conditioned representation을 같은 budget으로 만든다. Frozen
rule-based 또는 lightweight language planner의 plan validity를 offline evaluator로
비교한다. External code 실행은 Docker 안에서만 한다.

## Preliminary Success Criteria

- strongest simple filter보다 task-conditioned representation이 preregistered task
  subset에서 practical margin만큼 높은 plan validity를 보인다.
- improvement가 shorter prompt 자체가 아니라 distractor/relational error 감소와
  연결된다.
- 두 번째 scene/task family로 확장할 mapping이 확인된다.

## Expected Deliverable

Matched-budget spatial-state benchmark slice, error taxonomy와 minimal downstream utility
plot. Method는 question selection과 hypothesis formulation 이후에만 고려한다.

## Timeline And Milestones

- day 1--2: Clio schema와 license/version audit
- day 3--4: representation baselines와 frozen evaluator
- day 5--7: small query set comparison과 overlap/kill decision

## Interpretation Of A Negative Result

Top-k 또는 reachability filter가 oracle 수준이면 learned task-conditioned 3D state를
만들지 않는다. Clio의 핵심 claim과 구분되지 않으면 candidate를 종료한다.

## Resource Requirements

Offline first pilot은 CPU 또는 소형 GPU로 가능할 수 있다. Online mapping, ROS와 real
robot은 필요하지 않으며 이 candidate의 initial scope에서 제외한다.

## Related-Work Overlap

`high`. Clio가 핵심 원리를 직접 점유했을 가능성이 있다. Candidate를 유지하려면
downstream planner failure boundary, matched budget 또는 uncertainty interaction 중
하나가 nearest prior와 실질적으로 달라야 한다.

## User Decision Needed

없음. GPU availability는 planner choice만 제한한다.
