# Research Summary

Updated: 2026-09-11

## Current State

### Facts

- Current phase: `research scoping active`
- Active research scope: Robotics 중심, Robotics-enabling 3D Vision 부차적
- Active execution/hypothesis/paper-level experiment: 없음
- Latest disposition: [Q11 current route discontinued](buildup/selection.md#q11--discontinue-current-route-2026-09-10), frozen v3 실행·독립 검증과 사전 중단 규칙 적용
- Completed preliminary-review sequence: [Q12 → Q13](buildup/robotics/related_work/policy-geometry.md#reserve-reassessment-2026-09-10)
- Q12 Stage 4–5: 완료. Source audit에서 physical/virtual asset 공유와 대안 completion wrapper의 좌표 복원 차이를 확인했다. [근거](buildup/robotics/related_work/policy-geometry.md#q12-stage-4-review-2026-09-10)
- Q13 Stage 4–5: 완료. DISaM/GCNGrasp-VP의 직접 선행과 공개 input/action/evaluator의 제약을 확인했다. [근거](buildup/robotics/related_work/policy-geometry.md#q13-stage-4-review-2026-09-10)
- Current selection: Q12 `feasibility_study`, Q13 `deferred`, Q14 reserve. [비교 결정](buildup/selection.md#q12q13-measurement-selection-2026-09-10)
- Q12 입력 실행 완료: 실제 네 쌍의 schema·좌표 controls와 독립 검증 통과; physical frame은 미확정이다. [현재 study](buildup/robotics/pilot_studies/q12-generated-geometry/README.md#verified-input-results-2026-09-10)
- Q12 model 준비 완료: checkpoint strict loading·독립 metadata 검사와 synthetic CPU reference 검증을 통과했다. [결과와 frozen protocol](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md)
- Q12 실제 출력 실행 완료: frozen CPU reference의 네 입력/두 process가 output provenance·repeat equality와 독립 검증을 통과했다. [결과·한계](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11)
- Next work: native CUDA parity와 physical/camera linkage 확보의 비용·정보 가치를 비교해 후속 검증 또는 refine/defer를 판단한다.
- Retired research evidence and limitations: [종료 요약](literature/README.md)
- Q8: `under_review` / `refine`; 재진입 조건 전 실행 없음
- Latest selection record: [buildup/selection.md](buildup/selection.md)

### Agent Inference

- Q11 종료는 제한된 현재 method route의 판단이며 접촉 효과의 부재나 Robotics scope의 종료를 뜻하지 않는다.
- Q12는 관측과 생성 입력을 구분해도 잘못된 geometry에 의존하는 조건을 묻는다. Q13은
  기존 task-aware view score와 action uncertainty가 실제 decision value를 설명하지 못하는
  조건으로 좁혔다. Learned action uncertainty 자체는 DISaM이 이미 다룬다. 두 질문의
  empirical residue와 novelty는 아직 미확인이다.
- Q12의 [작은 입력 검증](buildup/robotics/questions/generated-geometry-reliance.md#bounded-measurement-task-draft)은
  policy/simulator 준비에 앞서 입력과 좌표 문제를 확인할 수 있어 우선한다. Raw pairing은
  확보했지만 두 object의 train/test가 겹치고 per-file physical/camera metadata는 없다.
  CPU 입력 controls는 통과했지만 native model-stack 호환성을 입증한 것은 아니다. 실제 GT의
  반복 좌표는 후속 sampling/density control을 요구하며 기존 진단 metric은 그대로 보존했다.
- CPU reference 출력 검증은 checkpoint 기반의 generated/copied provenance와 반복 재현성을
  확인했다. Native operator와의 동등성 또는 completion quality, action effect를 판정하지 않는다.
- Q12의 첫 성공 조건은 유효한 측정 입력이다. Wrapper 보정이나 reconstruction distance를
  robotics contribution으로 해석하지 않는다. 이후 고정 physical geometry와 독립 action
  evaluator, 공정한 observed-only/consistency/uncertainty baseline으로 이어지는 근거가 필요하다.
- Q13은 직접 선행과 checkpoint·상태·value 연결 비용 때문에 보류했다. 구체적인 작은 사례나
  접근 개선이 생기면 재비교하며, 현상 부재를 판정하거나 Q12의 자동 대체자로 두지 않는다.

### User Decision Needed

- 향후 real-robot work의 embodiment/access와 annotation budget은 해당 후보의 요구가 구체화될 때 확인한다.

## Stage Ownership

- Research scoping, candidate-question assessment와 feasibility studies: `buildup/`
- Formal hypothesis와 focused validation: `hypothesis/`
- 충분히 검증된 hypothesis의 paper-level work: `experiments/`

Active research가 생기면 이 문서에는 top-level problem, hypothesis,
contribution, primary metric/baseline, current evidence와 claim boundary만
요약한다. 세부 기록은 각 stage의 가장 작은 owner에 둔다.
