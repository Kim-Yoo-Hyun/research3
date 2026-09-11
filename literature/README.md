# Retired Research Summary

Updated: 2026-09-10

이 문서는 종료된 연구의 핵심 결론을 남기는 유일한 active-workspace
summary다. Active literature reading과 prior audit은 현재 단계의
`buildup/`, `hypothesis/`, `experiments/` 아래에 기록한다.

## Core Outcome

이전 semantic memory/mapping 및 3D Vision/Robotics direction search에서는
다섯 independent route를 검토했지만 당시 public-artifact/resource contract
아래 strict paper admission은 `0/5`였다. Exact novelty,
simple-baseline-resistant residual과 failure-forced method principle을 함께
입증한 active candidate는 남지 않았다.

이 결과는 당시 route와 resource contract에 대한 종료 판단이며, 새로운
home base나 research scope를 제한하지 않는다.

## Reusable Lessons

- Topic buildup과 paper-level admission을 분리한다.
- 가장 단순한 baseline과 competence/evaluator validity를 먼저 확인한다.
- Public code나 simulator의 존재를 executable denominator의 존재로
  간주하지 않는다.
- 실패는 threshold 조정으로 구제하지 않고 다음 branch의 조건으로 남긴다.

## Q10 Contact-Outcome Observability — 2026-09-08

Public REASSEMBLE subset에서 deterministic rules와 regularized physical-summary probes를
검증했지만 v6는 `NO_USEFUL_SUMMARY_GAIN`이었다. [Stage 7 decision](../buildup/selection.md#q10--discontinue-2026-09-08)에
따라 summary-only route와 현재 Q10 formulation의 진행을 종료했다. 이는 physical signal의
RGB 대비 가치가 없다는 증명이 아니며, 새 explanation에 근거한 reformulation은 선택하지 않았다.
반복 tuning이나 모델 확대로 negative result를 구제하지 않는 것이 이 연구의 재사용 가능한 교훈이다.

원래 [question](../buildup/robotics/questions/contact-outcome-observability.md)과
[study artifacts](../buildup/robotics/pilot_studies/q10-contact-observability/README.md)는
원위치에 provenance로 보존한다. 새 retired report로 복제하거나 dataset/cache를 삭제하지 않았다.

## Q1 Success-Predicate Stability — 2026-09-08

Frozen PickCube v3은 동일 초기 상태의 16 trajectories와 96 labels를 독립 검증했지만
성공 판정·순위 변화가 없었다. 이후 task semantics, public artifact metadata와 primary work의
[bounded audit](../buildup/robotics/related_work/q1-artifact-schema.md#bounded-refinement-audit--2026-09-08)에서도
의미상 동등한 specification family와 informative population을 정당화하지 못해 현재 Q1을
[discontinue](../buildup/selection.md#q1--discontinue-2026-09-08)했다. 실행 가능한 checkpoint의
존재와 연구 질문을 뒷받침하는 근거는 구별해야 한다는 교훈을 남긴다.

이는 모든 task에서 predicate sensitivity가 없다는 증명이 아니다. 새 의미적 calibration이나
별도의 measurement failure가 생기면 새로운 비교가 가능하다. [원래 question](../buildup/robotics/questions/success-predicate-stability.md)과
[v3 study](../buildup/robotics/pilot_studies/q1-predicate-stability/README.md)는 원위치에 보존하며,
threshold/seed 변경, 추가 evaluation과 artifact 삭제는 하지 않았다.

## Q11 Contact-Preserving Action Compression — 2026-09-10

Readiness, v2 physical pilot과 한 번의 제한된 v3 revision을 완료했다. V3는 measurement와
비용/MSE 비교 조건을 통과했지만, 접촉 위치에 오차를 넣었을 때만 실패한 grasp 1쌍과
release 4쌍의 정확 검정은 사전 alpha .025를 충족하지 못했다. 관측 차이는 보존하며
“접촉 효과가 없다”는 결론으로 해석하지 않는다. [고정된 중단 규칙에 따른 Stage 7 종료](../buildup/selection.md#q11--discontinue-current-route-2026-09-10)로
현재 contact-sensitive method formulation과 physical route를 `discontinued`로 정리했다.
추가 seed/perturbation/grid/task 확대로 결과를 구제하거나 hypothesis로 승격하지 않았다.

[원래 question](../buildup/robotics/questions/contact-action-compression.md),
[study와 독립 감사](../buildup/robotics/pilot_studies/q11-action-compression/README.md#v3-verified-results)는
원위치에 보존한다. 이 판단은 현재 제한된 경로에 적용되며 Robotics scope 전체나
향후 독립된 접촉 연구를 종료하는 것이 아니다. 현재 raw data/image/cache는 삭제하지 않았다.

## Recovery

2026-09-01에 보관한 이전 연구의 상세 source, reports, probes, experiments, datasets와 logs는
`/home/yoohyun/research3_retired_260901` 및 Git history에서 복구할 수 있다.
Active workspace에는 그 archived report를 중복 보존하지 않는다. Q10의 원본 경로와 복구 명령은
위 study README를 따른다.
