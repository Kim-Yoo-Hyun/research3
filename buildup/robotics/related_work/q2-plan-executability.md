# Q2 Plan Executability: Focused Prior Audit

Updated: 2026-09-04

## Audit Boundary

- Candidate: [Plan Executability Decomposition](../questions/plan-executability-decomposition.md)
- Exact question: frozen embodied plans의 실패를 symbolic precondition, spatial
  reachability와 interaction feasibility로 분해하고 simple validators 이후 residual을
  측정할 수 있는가?
- Search window: 2024--2026 primary papers, official proceedings/project/code
- This is a direct-prior screen, not an exhaustive related-work survey.

## Facts

- Embodied Agent Interface는 NeurIPS 2024 Datasets and Benchmarks paper이며 official
  code, data, documentation과 Docker route를 공개한다.
- ET-Plan-Bench는 IROS 2025 paper이고 public repository에 benchmark 및 evaluation
  generation code가 있다.
- ProcWorld의 canonical record는 EMNLP 2025 ACL Anthology ID
  `2025.emnlp-main.635`다.
- SIMPACT는 CVPR 2026 paper다.
- 어떤 external artifact도 local에 checkout, pull, build 또는 run하지 않았다.

## Nearest Primary Work

### Embodied Agent Interface — NeurIPS 2024

Official sources: [proceedings](https://papers.nips.cc/paper_files/paper/2024/hash/b631da756d1573c24c9ba9c702fde5a9-Abstract-Datasets_and_Benchmarks_Track.html),
[code](https://github.com/embodied-agent-interface/embodied-agent-interface)

**Paper claim.** Goal interpretation, subgoal decomposition, action sequencing and transition
modeling을 standardized interface에서 각각 평가하고, hallucination, affordance와 planning
error를 fine-grained metric으로 분해한다. Action sequence에는 simulator trajectory
feasibility, goal satisfaction와 partial goal satisfaction를 사용한다.

**Collision.** `direct`. Q2의 “final success를 planning/execution components로 분해하고
symbolic feasibility로 진단한다”는 핵심 research question과 principle을 이미 점유한다.
Q2의 spatial/contact subdivision만으로는 substantive difference가 되지 않는다.

### ET-Plan-Bench — IROS 2025

Official sources: [paper](https://arxiv.org/abs/2410.14682),
[code](https://github.com/ET-Plan-Bench/ET-Plan-Bench)

**Paper claim.** Foundation model의 embodied task planning을 spatial constraints,
occlusion, temporal/causal ordering과 simulator feedback이 있는 task로 진단한다.

**Collision.** `strong_adjacent`. Q2가 제안한 spatial/temporal error families와 public
simulator denominator가 상당 부분 이미 존재한다.

### ProcWorld — EMNLP 2025

Official source: [ACL Anthology](https://aclanthology.org/2025.emnlp-main.635/)

**Paper claim.** Partially observable navigation/manipulation planning을 16 task types,
5,000 rooms와 1,000만 개 이상의 evaluation trajectory로 평가하며, active information
gathering, spatio-temporal state tracking와 physical reachability-constrained reasoning을
핵심 난제로 제시한다.

**Collision.** `strong_adjacent`. Reachability failure를 분리할 public denominator와
대규모 model comparison이 이미 있다. Official code availability는 이번 audit에서
확인하지 못했다.

### SIMPACT — CVPR 2026

Official source: [CVF paper](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_SIMPACT_Simulation-Enabled_Action_Planning_using_Vision-Language_Models_CVPR_2026_paper.html)

**Paper claim.** RGB-D observation에서 physics simulation을 만들고 VLM proposal을
simulated outcome으로 반복 수정해 fine-grained rigid/deformable manipulation의 physical
reasoning을 개선한다.

**Collision.** `direct_for_intervention`. Q2가 oracle/validator 이후 자연스럽게 갈 수
있는 simulation-in-the-loop corrective method는 이미 점유됐다.

## Agent Inference

네 prior의 합집합은 Q2의 problem, denominator, diagnosis와 가장 자연스러운 intervention을
모두 압박한다. “exclusive/overlapping causal attribution” 자체는 동일하지 않을 수 있지만,
그 분석만으로 failure-derived non-substitutable method를 요구한다고 보기 어렵다.

## Decision

- Related-work overlap: `direct_collision`
- Selection decision: `reformulate`
- Artifact/schema audit: 수행하지 않음
- Feasibility/pilot: 수행하지 않음

현재 형태로는 pilot이나 implementation으로 보내지 않는다. Revision은 단순히 새로운
failure taxonomy를 추가하는 것이 아니라, EAI의 modular isolation과 SIMPACT의 simulator
correction 뒤에도 남는 새로운 observable residual을 먼저 정의해야 한다.

## User Decision Needed

없음. 새 residual이 문헌 또는 inexpensive observation에서 발견되기 전까지 deferred다.
