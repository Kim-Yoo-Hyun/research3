# Research Scoping and Topic Development

Updated: 2026-09-29

## Purpose

이 폴더는 research scope를 정하고 candidate research questions를 비교해
formal hypothesis로 발전시킬 질문을 선택하는 작업의 유일한 저장 위치다.
`buildup/`은 repository 경로명이며, 연구 문서에서는 `Research Scoping and
Topic Development`를 stage 명칭으로 사용한다.

- Stable workflow와 entry criteria: `docs/buildup.md`
- Research scope, candidate questions, preliminary literature review,
  feasibility/pilot studies와 selection decision: `buildup/`
- 선택된 research question의 hypothesis formulation과 focused validation:
  `hypothesis/`
- 충분히 검증된 hypothesis의 paper-level evaluation: `experiments/`

`docs/buildup.md`에는 절차만 기록한다. 현재 scope, 조사 결과, feasibility
evidence와 selection decision은 이 폴더 밖에 중복하지 않는다.

## Basis In Official Research Guidance

연구 제안·탐색/확증 지침과 적용 범위는
[workflow의 근거](../docs/buildup.md#basis-in-research-guidance)가 소유한다.
[기존 운영과의 비교](selection.md#buildup-gate-assessment-2026-09-15)와
[규칙 반영 기록](selection.md#buildup-workflow-update-2026-09-15)을 구분한다.
연구 문서에서는 `research scope`, `candidate research question`,
`feasibility/pilot study`, `selection for hypothesis formulation`을 사용한다.

## Current State

- Research scopes: [`robotics`](robotics/README.md) and
  [`cross_domain`](cross_domain/README.md), both `active_scoping`
- Primary area: Robotics; secondary area: Robotics-enabling 3D Vision
- Candidate research questions: Robotics 17개 + cross-domain 5개
- Selected next exploratory question: [Q17 Evidence-Conditioned Action Selection](robotics/questions/evidence-conditioned-action-selection.md)
- Latest selection: [Q17 과업군·다른 후보 재비교](selection.md#q17-task-family-reassessment-2026-09-29); ML 회전 시점의 첫 ID 사례를 단서 가시성→첫 집기 대상 판별 관찰로 선택
- Q16 현 방법·자료 경로와 CD5 실행은 각각 별도 이유로 보류; formal hypothesis와 실행 중인 study는 없음

현재 작업은 [TODO](../TODO.md), 후보 간 판단의 이력은 [selection record](selection.md),
개별 관찰·검산 근거는 해당 question과 study owner가 소유한다. 종료된 연구의 요약은
[literature/README.md](../literature/README.md)를 따른다.

## Stage Flow

```text
buildup/
  research scope and constraints
  -> candidate research questions
  -> preliminary literature review ↔ observation / explanation / method attempt
  -> feasibility or pilot study ↔ revision
  -> question selection
    ↓ Hypothesis Formulation Entry Criteria 통과
hypothesis/
  formal hypothesis and focused validation
    ↓ Experiment Handoff Gate 통과
experiments/
  paper-level evaluation and reproducible evidence
```

Buildup 내부의 단계는 반복할 수 있으며 각각 별도 통과 gate가 아니다. 설명과 method
sketch는 question record에서 시작한다. Stage 사이의 ownership과 handoff는 유지한다.
선택되지 않은 question을 `hypothesis/`에 만들거나, 충분히 검증되지 않은 hypothesis를
`experiments/`로 넘기지 않는다.

## Folder Convention

Research scope가 정해진 뒤 필요한 항목만 만든다.

```text
buildup/
  README.md
  <short-scope>/
    README.md
    questions/
      <short-question>.md
    related_work/
    pilot_studies/
```

- Scope `README.md`가 research area, significance, resource constraints,
  available time, expected research output, candidate-question registry와
  current decision의 authoritative owner다.
- `questions/`에는 candidate research question record를 둔다.
- `related_work/`에는 question selection과 prior-work overlap 판단에 직접
  필요한 preliminary literature review를 둔다.
- `pilot_studies/`에는 feasibility/pilot study의 protocol, success criteria,
  milestones와 result를 둔다.
- 빈 하위 folder는 미리 만들지 않는다.

## Hypothesis Formulation Entry Criteria

[Entry To Hypothesis Formulation](../docs/buildup.md#entry-to-hypothesis-formulation)에 따라
중요한 질문과 타당한 첫 검증 경로를 근거로 선택해 `hypothesis/`로 넘긴다.
이 README에는 selection result,
source question record, target hypothesis directory와 selection date만 registry로
남긴다.

선택할 때 `hypothesis/CAND-<number>/`를 만들고 source scope, candidate
question과 feasibility evidence를 기록한다. 이후 hypothesis와 validation
result는 `hypothesis/`에서만 갱신하며, source record는 provenance로 동결한다.

## Status Values

- `exploratory`: preliminary research question
- `under_review`: comparative review와 preliminary literature review 진행 중
- `feasibility_study`: feasibility 또는 pilot study 진행 중
- `ready_for_hypothesis`: hypothesis formulation entry criteria 통과
- `discontinued`: question 또는 observed phenomenon을 더 진행하지 않음
- `deferred`: resource, evidence 또는 user decision을 기다림

현재 research scope, question registry와 바로 다음 action은 이 README와
`TODO.md`에 짧게 반영한다.
