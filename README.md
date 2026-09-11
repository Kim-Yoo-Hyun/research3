# Research Workspace

업데이트: 2026-09-11

## Current State

현재 phase는 `research scoping active`이다. Active research scope는 Robotics이며
3D Vision은 robot state estimation과 behavior에 기여하는 부차적 축으로 다룬다.
Robotics와 cross-domain candidate 20개를 기록했다. Q12/Q13의 Stage 4–5 검토와 비교를 마치고,
Q12의 CPU input/schema/coordinate protocol v1을 실제 네 쌍에 실행·독립 검증했다.
입력 controls는 통과했으나 physical frame은 미확정이다. Q12는 `feasibility_study`,
Q13은 `deferred`, Q14는 reserve다. Checkpoint strict loading 후
[실제 네 입력의 CPU reference completion](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11)을
실행·독립 검증했다. Output provenance와 반복 재현성은 통과했으며 native CUDA 동등성과
physical/camera 연결은 미검증이다. 다음은 이 연결 경로의 비용·정보 가치 비교다.
종료된 후보들의 결과 요약은 아래 `literature/README.md`를 따른다.
최신 선택 결정은
[buildup/selection.md](buildup/selection.md), 종료된 연구 요약은
[literature/README.md](literature/README.md)가 소유한다. 선택된 hypothesis,
experiment와 paper claim은 아직 없다.

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

## Active Workspace

| Path | Role |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 작업 규칙, novelty discipline, Docker-only 원칙 |
| [TODO.md](TODO.md) | 현재 상태와 다음 승인 경계 |
| [summary.md](summary.md) | 현재 active research의 top-level summary |
| [docs/](docs/) | buildup, literature, hypothesis, experiment, paper, reproducibility workflow |
| [buildup/](buildup/) | research scope, candidate questions, related work, feasibility studies와 selection decision |
| [hypothesis/](hypothesis/) | selected question의 formal hypothesis와 focused validation |
| [experiments/](experiments/) | validated hypothesis의 paper-level work |
| [literature/](literature/) | 종료된 연구의 유일한 compact summary |

## Next

1. [Q12 출력 검증 결과](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11)와 native CUDA parity·physical/camera 연결의 남은 비용을 비교해 후속 검증 또는 수정·보류를 판단한다.
2. 진행 근거가 있는 경로만 다음 검증 protocol로 구체화한다.
3. Entry To Hypothesis Formulation 조건을 충족하고 선택한 question만 `hypothesis/`로 넘긴다.
