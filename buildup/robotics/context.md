# Robotics Research Context

Updated: 2026-09-04

## Status And Evidence Boundary

2026-09-08 사용자 지정 learning/policy/diffusion/geometry/VLA 관심 논문에 따른 새 탐색은
[Policy and geometry search](related_work/policy-geometry.md)가 소유한다. 아래 landscape와
snapshot은 2026-09-04 기록이며, 새 Q11--Q15의 현재 비교 상태를 대체하지 않는다.

이 문서는 candidate research question을 만들기 위한 scoping map이다. 아직
candidate, hypothesis, novelty claim 또는 executable benchmark 승인을 뜻하지
않는다.

- `PaperReview`의 registry와 synthesis는 discovery 및 comparison cue로 사용했다.
- Paper별 note가 `FULL_TEXT_CHECKED`여도 사용자의 정독 상태와 동일시하지 않는다.
- 아래 최신 venue, artifact와 benchmark 상태는 2026-09-04에 official
  proceedings, project page 또는 official repository에서 다시 확인했다.
- 실제 실행 가능성은 Docker smoke test 전까지 `unverified`다.

## Facts

- Active scope는 Robotics이며 3D Vision은 downstream robot behavior를 바꾸는
  경우에만 우선한다.
- 정량 evidence는 simulation/dataset에서 먼저 만들고 real robot은 후반
  qualitative demonstration으로 제한한다.
- 새로운 foundation model 또는 heavy training은 범위 밖이다.
- `PaperReview` snapshot은 950편이며 7개 Robotics synthesis track으로 구성된다.
- IEEE Robotics and Automation Society는 IROS 2027 paper submission deadline을
  2027-03-01로 게시하고 있다.

## Research Landscape

| Track | Recent anchor and source claim | Public evaluation route | Agent inference / question pressure | Initial fit |
| --- | --- | --- | --- | --- |
| planning and control | [STELA](https://www.roboticsproceedings.org/rss21/p008.html)는 noisy trajectory estimation과 local control adaptation을 함께 최적화하고, [FOCI](https://rffr.leggedrobotics.com/works/foci/)는 Gaussian Splats 위에서 orientation-aware trajectory optimization을 수행한다. | FOCI code와 Dockerfile이 공개돼 있으나 MA27 solver license가 필요하다. | Learned component를 추가하는 것보다 uncertainty, feasibility와 replanning의 interface에서 재현 가능한 residual을 찾아야 한다. | `medium` |
| RL, IL and robot data | [ManiSkill3](https://www.roboticsproceedings.org/rss21/p021.html)는 GPU-parallel simulation, heterogeneous environments, demonstrations와 RL/IL baselines를 공개한다. | [Official repository](https://github.com/haosulab/ManiSkill)는 task, baseline, documentation과 sim-to-real example을 제공한다. | 새 대형 policy보다 data coverage, failure data, action timing 또는 evaluation protocol을 고정한 진단이 적합하다. | `high`, GPU 확인 필요 |
| manipulation, contact and tactile | [Reactive Diffusion Policy](https://www.roboticsproceedings.org/rss21/p052.html)는 slow action generation과 fast tactile feedback을 결합해 세 contact-rich task에서 평가한다. | Code/project가 공개됐지만 원 연구는 tactile hardware, dual-arm setup과 demonstration collection에 의존한다. | Slow–fast architecture 자체는 이미 점유됐다. Sensor drift, latency, contact-state observability 또는 simpler feedback baseline 뒤의 residual이 필요하다. | `low-to-medium` |
| VLA and generalist policies | [VLA-Arena](https://vla-arena.github.io/)는 Safety, Distractor, Extrapolation, Long Horizon의 170개 task와 L0–L2 difficulty, code/data/model/leaderboard를 제공한다. | 공개 framework와 dataset이 있으므로 frozen policy evaluation route가 유망하다. | “VLA가 실패한다”는 주장은 부족하다. 어떤 perturbation과 temporal condition에서 어떤 inexpensive intervention이 downstream consequence를 바꾸는지가 필요하다. | `medium-to-high`, inference budget 확인 필요 |
| world models, safety and recovery | [SAFE](https://vla-safe.github.io/)는 LIBERO·SimplerEnv와 real Franka에서 multitask VLA failure detection을 평가한다. [SafeVLA-Bench](https://safevla.org/)는 LIBERO·RoboCasa-365 rollout에 SR, Safety, SBU, VSI를 추가한다. [WorldGym](https://proceedings.iclr.cc/paper_files/paper/2026/hash/7f5e909ac0324db03506b380c695ffaf-Abstract-Conference.html)은 action-conditioned video world model을 policy-evaluation proxy로 제안한다. | Existing rollout과 frozen VLA를 사용하는 diagnostic route는 가능성이 있으나 각 code/checkpoint의 실제 실행성은 미확인이다. | Failure score, post-hoc safety metric, world-model evaluator 자체는 이미 직접 선행이 있다. Detection이 실제 stop/replan/recovery utility로 이어지는지와 simple monitor residual을 분리해야 한다. | `high` for diagnosis, `low` for world-model training |
| locomotion and whole-body control | [HOVER](https://research.nvidia.com/labs/lpr/publication/he2025hover/)는 여러 command mode를 하나의 humanoid controller에서 처리하고 IsaacGym과 Unitree H1에서 평가한다. | Project artifact는 있으나 registry상 code는 `project_only`; executable denominator와 hardware-independent reproduction은 미확인이다. | Generalist WBC 자체보다 high-level command rate, termination, mode switching, unsafe-command rejection과 low-level constraint의 contract가 남는다. | `low-to-medium`, GPU/robot 확인 필요 |
| robotics-enabling 3D perception | [Clio](https://github.com/MIT-SPARK/Clio)는 task-driven open-set 3D scene graph code, dataset와 pre-built graph를 제공한다. Offline Python evaluation route가 있지만 공개 실시간 pipeline에는 release regression이 명시돼 있다. FOCI는 3DGS-to-planning 연결을 이미 다룬다. | Clio offline data route는 비교적 가볍고, online route는 ROS와 version pinning이 필요하다. | 3D representation 자체보다 state staleness, uncertainty 또는 granularity가 planner/policy intervention과 task success를 바꾸는지 측정해야 한다. | `medium` |

`Initial fit`은 연구 가치 점수가 아니라 현재의 simulation/dataset-first,
non-foundation-scale, six-month constraint에 대한 scoping estimate다.

## Active Research Ecosystems

- ManiSkill/SAPIEN: scalable simulation, manipulation task와 reproducible RL/IL
  baseline substrate
- Peking University VLA-Arena: structured VLA stress evaluation과 leaderboard
- University of Toronto / TRI SAFE: VLA latent-based runtime failure detection
- Stanford / NYU / Google DeepMind WorldGym: world-model-based policy evaluation
- NVIDIA HOVER/SONIC line: generalist humanoid whole-body controller와 motion scale
- MIT SPARK Clio: task-relevant open-set 3D scene graph
- ETH Zürich Robotic Systems Lab FOCI: 3D Gaussian representation을 사용하는
  trajectory optimization

이 목록은 affiliation ranking이 아니라 candidate prior와 executable artifact를
추적하기 위한 anchor다.

## Cross-Track Synthesis

### Source-supported recurring gaps

1. **Temporal interface:** action chunk 또는 high-level command의 속도와
   closed-loop correction/contact feedback의 속도가 다르다.
2. **Detection-to-action gap:** failure, uncertainty 또는 safety violation을
   감지해도 stop, replan, fallback 또는 recovery가 downstream task utility를
   개선한다는 보장은 없다.
3. **Representation-to-control gap:** 3D map, scene graph, latent state 또는 world
   model의 quality가 실제 planning/control robustness와 일치하지 않을 수 있다.
4. **Learned–analytic boundary:** learned policy가 dynamics, contact, feasibility와
   safety constraint를 어디까지 맡고 controller/planner가 무엇을 보존해야 하는지
   명확하지 않다.
5. **Evaluation gap:** success rate만으로 unsafe success, rare event, intervention
   cost, latency와 recovery quality를 구분하기 어렵다.

### Direct-prior collision warnings

- Generic multitask VLA failure detector는 SAFE가 직접 다룬다.
- VLA의 structured stress benchmark는 VLA-Arena가 직접 다룬다.
- Native success와 post-hoc physical safety의 분리는 SafeVLA-Bench가 직접 다룬다.
- Slow visual planning과 fast tactile feedback의 hierarchy는 Reactive Diffusion
  Policy가 직접 다룬다.
- Unified multi-mode humanoid controller는 HOVER/SONIC line이 직접 다룬다.
- Task-dependent 3D scene granularity는 Clio가, Gaussian-Splat collision-aware
  planning은 FOCI가 직접 다룬다.
- Video world model을 policy-evaluation proxy로 쓰는 방향은 WorldGym이 직접
  다룬다.

따라서 위 method name이나 broad motivation을 그대로 candidate contribution으로
사용하지 않는다. 다음 question은 simple baseline 이후 남는 observable residual,
downstream consequence와 명확한 evaluation target을 가져야 한다.

## Candidate-Generation Priorities

다음 단계에서 서로 겹치지 않는 candidate questions 3--5개를 만들 때 아래
problem family를 비교한다. 이는 question registry가 아니라 생성 범위다.

1. Frozen policy rollout에서 failure/safety signal이 실제 intervention utility를
   예측하는 조건
2. Action chunk, observation latency와 feedback rate가 disturbance recovery에
   미치는 causal effect
3. 3D/spatial state의 granularity, uncertainty 또는 staleness가 downstream
   planning success에 미치는 영향
4. High-level learned command와 analytic controller/constraint layer 사이의
   feasibility 및 rejection contract
5. Simulation에서 얻은 evaluator ranking이 다른 task/domain 또는 real-robot
   qualitative behavior로 유지되는 조건

각 question은 public denominator, simplest baseline, negative-result value와
one-week-scale feasibility study를 별도로 확인한다. 초기 scoping에서 final method
architecture를 정하지 않는다.

## Accessible Substrate Shortlist

| Substrate | What is available | Status before local execution |
| --- | --- | --- |
| ManiSkill3 | simulation, tasks, demonstrations, RL/IL baselines, VLA evaluation support | `promising_unverified` |
| VLA-Arena | 170 structured tasks, code, datasets, models, leaderboard | `promising_unverified` |
| SAFE / LIBERO / SimplerEnv | failure labels, detector code and VLA evaluation routes | `promising_unverified` |
| SafeVLA-Bench / LIBERO / RoboCasa-365 | task-aware trajectory safety metrics layered on native rollouts | `promising_unverified` |
| Clio offline | public datasets, pre-built scene graphs and offline evaluation | `promising_with_version_risk` |
| FOCI | public code, Dockerfile and demo data | `promising_with_solver_license` |
| HOVER/SONIC | project artifacts and simulator-based WBC evidence | `denominator_unverified` |
| WorldGym | official paper/project and world-model policy-evaluation protocol | `compute_and_checkpoint_unverified` |

No substrate has been downloaded, built or executed in this workspace.

## Agent Inference

현재 제약에 가장 잘 맞는 출발점은 새 policy 학습이 아니라 **공개 simulator와
frozen policy/rollout 위의 controlled diagnosis**다. 특히 failure-to-intervention,
temporal feedback 또는 representation-to-control utility는 여러 track을 연결하면서도
dataset/simulation에서 정량화할 수 있다. 다만 이는 candidate selection이 아니며,
각 방향은 nearest primary papers와 simple heuristic baseline 압력을 먼저 받아야
한다.

Whole-body control과 tactile manipulation은 연구적 중요성은 높다. Local RTX 5090은
확인됐지만 pre-existing Isaac image는 사용할 수 없고 executable controller/checkpoint,
새 simulator environment, compatible embodiment와 sensing access가 확인되지 않아 첫
feasibility study로 선택하기에는 resource risk가 크다.

## Second-Round Context Expansion

첫 candidate set이 evaluation과 failure diagnosis에 편중됐다는 판단에 따라
[second-round frontier scan](related_work/frontier-scan-2.md)을 추가했다. Temporal
execution contract, constructed-to-natural failure transfer, recoverability-aware data
coverage, dynamic spatial memory와 contact-rich outcome observability를 서로 다른
problem family로 검토했다.

Broad action-chunk correction, learned scene-memory update와 generic demonstration
curation은 recent direct prior가 강하다. 현재 candidate-record priority는
constructed-to-natural failure transfer, recoverability-aware data coverage와 minimal
contact evidence이며, exact prior 및 artifact audit 전에는 선택하지 않는다.

## User Decisions Needed

- Local RTX 5090 한 장의 허용 가능한 총 compute 시간과 동시 작업 제한
- 접근 가능한 real robot embodiment와 sensor
- 새로 구성할 simulator 후보와 setup에 허용할 수 있는 시간
- public-data-only 여부와 annotation budget

이 정보는 candidate 생성 자체를 막지 않지만 feasibility와 우선순위 판정을 바꾼다.

## Official Sources Checked

- [IROS 2027 event and deadline](https://www.ieee-ras.org/event/2027-ieee-rsj-international-conference-on-intelligent-robots-and-systems-iros-70525/)
- [ManiSkill3 RSS 2025](https://www.roboticsproceedings.org/rss21/p021.html) and [official repository](https://github.com/haosulab/ManiSkill)
- [VLA-Arena](https://vla-arena.github.io/)
- [SAFE](https://vla-safe.github.io/)
- [SafeVLA-Bench](https://safevla.org/)
- [WorldGym, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/7f5e909ac0324db03506b380c695ffaf-Abstract-Conference.html)
- [HOVER](https://research.nvidia.com/labs/lpr/publication/he2025hover/)
- [Reactive Diffusion Policy, RSS 2025](https://www.roboticsproceedings.org/rss21/p052.html)
- [Clio official repository](https://github.com/MIT-SPARK/Clio)
- [FOCI project](https://rffr.leggedrobotics.com/works/foci/) and [official repository](https://github.com/leggedrobotics/foci)
