# Whole-Body Command Admissibility

Updated: 2026-09-04

## Status

`deferred`

## Facts

- Whole-body controller는 특정 command representation과 training/support region 안에서
  동작한다.
- Publicly described generalist humanoid controllers가 있지만 local executable
  checkpoint와 denominator는 아직 확인하지 않았다.
- 이 workspace에는 humanoid simulator image나 robot hardware configuration이 없다.

## Source Claims

- [HOVER](https://research.nvidia.com/labs/lpr/publication/he2025hover/)는 여러 command
  mode를 하나의 humanoid controller에서 처리하고 Isaac Gym과 Unitree H1에서
  평가한다.
- [HumanoidBench](https://humanoid-bench.github.io/)는 15개 whole-body manipulation과
  12개 locomotion task를 포함하는 공개 benchmark를 제시한다.

## Agent Inference

새 WBC를 학습하는 대신 upstream planner가 생성한 command가 frozen WBC의 feasible
또는 supported region에 들어오는지를 진단하는 연구가 compute constraint에 더 맞다.
다만 generic safety shield나 command clipping은 retired 방향과 인접하므로 이 candidate는
**admissibility measurement**에 한정한다.

## Research Question Or Suspected Phenomenon

Frozen learned whole-body controller에서 upstream high-level command의 어느 특성이
tracking failure, fall 또는 actuator saturation을 예측하는가? Kinematic feasibility,
command norm와 training-support distance 같은 단순 score 이후에도 mode-dependent
residual이 남는가?

## Significance

Language/semantic planner와 low-level WBC 사이의 contract를 측정할 수 있으면 새로운
controller를 학습하지 않고도 hierarchical robot system의 failure boundary를 명확히 할
수 있다.

## Current State Of The Art And Limitation

HOVER 같은 generalist controller는 multi-mode command following 자체를 다룬다.
Candidate의 최소 차이는 controller architecture가 아니라 upstream command의
admissibility와 failure predictability다. 공개 checkpoint와 command-distribution metadata가
없으면 empirical question 자체가 성립하지 않는다.

## Evaluation Target

- primary: fixed-horizon fall/tracking failure/saturation prediction AUROC and calibration
- downstream: reject 없이 실행했을 때 task completion과 failure rate
- denominator: commands × modes × initial states × seeds
- matched controls: identical frozen controller, simulator, command horizon and observations

## Available Data / Code / Evaluator

- candidate substrate: executable HOVER artifact if available
- fallback substrate: HumanoidBench-compatible public policies
- privileged oracle: simulator feasibility or future rollout outcome, used only as evaluator

## Simplest Baseline Or Counterexample

1. Command magnitude/rate threshold.
2. Joint-limit and center-of-mass kinematic check.
3. Nearest-neighbor distance to training commands, if metadata is public.
4. Short open-loop rollout oracle.
5. Simple clipping이 failure를 제거하면 learned admissibility method를 만들지 않는다.

## Critical Assumptions

| Assumption | Disconfirming observation | Cheaper measurement |
| --- | --- | --- |
| Public frozen controller/checkpoint가 실행 가능하다. | project page만 있고 compatible code/checkpoint가 없다. | repository/artifact audit |
| command interface와 training support를 식별할 수 있다. | interface가 undocumented이거나 data가 비공개다. | config/document audit |
| failures가 충분히 발생하면서 task가 nominally solvable하다. | 모든 command가 성공하거나 전부 실패한다. | published demo/config smoke test |

## Feasibility Or Pilot Study

코드와 checkpoint 존재 여부를 먼저 audit한다. 통과할 때만 Docker에서 한 mode와 작은
command grid를 실행해 analytic scores, outcome과 failure trace를 기록한다. Artifact가
없거나 일주일 내 build가 불가능하면 즉시 defer/discontinue한다.

## Preliminary Success Criteria

- 공개 artifact로 nominal success와 controlled failure를 모두 재현한다.
- strongest analytic score 이후 mode/transition에 구조화된 residual이 남는다.
- privileged feasibility oracle가 downstream action selection에 practical improvement
  가능성을 보인다.

## Expected Deliverable

Command-outcome dataset slice, analytic admissibility baseline과 failure-boundary map.

## Timeline And Milestones

- day 1: code/checkpoint/license/compute audit
- day 2--3: Docker build and one nominal rollout
- day 4--6: command grid if and only if nominal rollout succeeds
- day 7: kill/defer decision

## Interpretation Of A Negative Result

Artifact가 없거나 analytic thresholds가 failure를 충분히 설명하면 controller 또는
detector를 새로 학습하지 않는다. WBC를 first project로 선택하지 않는다.

## Resource Requirements

Local RTX 5090과 NVIDIA Docker runtime은 확인됐다. Pre-existing Isaac Sim/Isaac Lab
image는 연구에서 사용·수정·삭제할 수 없으며 새 environment가 필요하다. 또한
HOVER-compatible code/checkpoint, command metadata와 사용 가능한 robot embodiment는
미확정이다. Unitree H1 access는 pilot에 필요하지 않다.

## Related-Work Overlap

`medium-to-high`. Generalist command following, safety filters와 feasibility checking에
인접한다. Generic shield contribution은 제외하며 direct-prior audit가 필요하다.

## User Decision Needed

Local Isaac stack 중 사용할 수 있는 version, 허용 compute 시간과 향후 사용할 수 있는
humanoid embodiment가 있는지 확인해야 한다.
