# Research Workspace

업데이트: 2026-09-28

## Current State

현재 phase는 `research scoping active`이다. 사용자가 선택한 주 연구 범위는
Robotics이며, 3D Vision은 robot behavior에 기여하는 부차적 축이다. Robotics와
cross-domain의 candidate question 22개를 기록했다.

최근 개발 후보 [Q16 Predictive Policy Adaptation](buildup/robotics/questions/interaction-conditioned-motion.md)의
현재 2D 방법 경로는 [8-step 대 2-step 대조](buildup/robotics/pilot_studies/q16-motion/README.md#shorter-action-chunk-comparison-2026-09-27-prospective-protocol)에서
순구제가 없고 비용이 늘어 보류했다. Can PH 자료의 행동 재생 경로도 사전 일치
기준을 통과하지 못해 보류 중이다. 이는 예측 기반 적응 질문 전체의 반증이 아니다.
[최신 선택](buildup/selection.md#q17-selection-2026-09-28)에
따라 [Q17 Evidence-Conditioned Action Selection](buildup/robotics/questions/evidence-conditioned-action-selection.md)의
작은 관찰을 다음으로 진행한다. 선택된 formal
hypothesis, paper experiment 또는 contribution claim은 없다. 자세한 근거는
[summary](summary.md)와 각 study owner가 소유한다.

## Research Pipeline

```text
buildup/     research scoping, candidate questions, feasibility studies
    ↓ Hypothesis Formulation Entry Criteria
hypothesis/  formal hypothesis와 focused validation
    ↓ experiment-ready gate
experiments/ paper-level scale, baselines, ablation, robustness, artifacts
```

- Research scoping과 topic development는 `buildup/`에서만 진행한다.
- Entry criteria를 충족해 선택된 research question만 `hypothesis/`로 넘긴다.
- 충분히 검증된 hypothesis만 `experiments/`로 넘겨 paper-level 작업을 한다.
- 각 단계의 live 내용과 결과는 다음 단계나 다른 index에 중복하지 않는다.

Buildup은 작은 관찰과 설명·방법 수정을 반복한다. [운영 기준](docs/buildup.md)을 따르며,
최종 paper 기준은 유지한다. `paper/`는 최종 실험 완료 후 실제 논문 작성 시
[일곱 조건](docs/paper.md#paper-folder-gate)을 모두 충족해 연다.

## Active Workspace

| Path | Role |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 작업 규칙, novelty discipline, Docker-only 원칙 |
| [TODO.md](TODO.md) | 현재 과제와 다음 작업 |
| [summary.md](summary.md) | 현재 active research의 top-level summary |
| [docs/](docs/) | buildup, literature, hypothesis, experiment, paper, reproducibility workflow |
| [buildup/](buildup/) | research scope, candidate questions, related work, feasibility studies와 selection decision |
| [hypothesis/](hypothesis/) | selected question의 formal hypothesis와 focused validation |
| [experiments/](experiments/) | validated hypothesis의 paper-level work |
| [literature/](literature/) | 종료된 연구의 유일한 compact summary |

## Next

ActiveArena의 첫 hidden-color 사례는 정보 획득 이전에서 멈춰,
색 종류 확인 뒤 버튼 선택을 살필 대체 과업의 작은 관찰을 진행한다. 현재 작업은
[TODO.md](TODO.md)를 따른다.
