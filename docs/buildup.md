# Research Scoping and Topic Development Workflow

Updated: 2026-09-28

## Purpose

Broad research interest에서 중요한 질문을 찾고 작은 관찰·설명·방법 시도를 통해
검증할 가설로 발전시킨다. Buildup은 탐색이 기본이며 완성된 paper claim을 요구하지 않는다.

```text
research scope -> candidate questions
                      ↕
            literature ↔ observation ↔ explanation / method attempt
                      ↓ selection for focused validation
                  hypothesis/ -> experiments/
```

Stage 1–7은 작업 위치를 설명하는 순서다. 각 번호를 독립적인 합격 gate로 만들지 않는다.
특히 Stage 4–6은 작은 관찰과 문헌 검토를 오가며 진행한다. Hypothesis/experiment handoff는
구분하되, unresolved question과 수정 가능한 가설 초안을 허용한다.

## Basis In Research Guidance

[Stanford CS231n Spring 2026](https://cs231n.stanford.edu/project.html)과
[MIT Underactuated Robotics Spring 2024](https://underactuated.csail.mit.edu/Spring2024/project.html)는
짧은 제안과 점진적인 방법/예비 결과 발전을 안내한다. Course project의 novelty 기준을
논문 채택 기준으로 옮기지 않는다. [DARPA](https://www.darpa.mil/about/heilmeier-catechism)는
중요성·차별화 가능성·위험·비용·검증 계획을 묻는다.
[COS](https://www.cos.io/initiatives/prereg)는 탐색과 확증을 구분하며 투명한 변경과 후속
독립 검증을 안내한다. 이 문서의 절차는 이를 현재 연구 범위에 적용한 내부 운영 규칙이다.
논문 수준의 기여/증거 기준은 [paper.md](paper.md)가 소유한다.

## Scope Boundary

- Research scope는 사용자가 선택한다. 기존 대화에서 정한 scope와 자원 범위를 승계한다.
- Public artifact, 소규모 annotation, constructed study, hardware의 허용 범위를 기록한다.
  Resource가 미확정이면 추정으로 확보했다고 쓰지 않고, 그 답이 필요한 작업만 제한한다.
- Method/data 하나를 scope 자체로 고정하지 않는다. 같은 질문을 더 싸게 관찰할 수 있는
  toy model, analytic example, 작은 data slice를 허용하며 실제 적용 범위와 구분한다.

## Storage Rule

- Stable rule/template: `docs/buildup.md`; 문헌 절차: `docs/literature.md`
- Scope/registry: `buildup/README.md`, `buildup/<scope>/README.md`
- Question/탐색 기록: `buildup/<scope>/questions/`; 선택적 선행 상세: `related_work/`
- 실행 recipe/input/output/결과: 해당 `pilot_studies/` owner; 상태/다음 작업: `TODO.md`

초안과 소규모 관찰을 가장 가까운 기존 owner에 누적한다. 단계마다 새 report, receipt,
freeze 묶음을 만들지 않는다. 큰 데이터·raw output은 ignored 경로에 두고 위치를 기록한다.

## Entry Requirements

시작할 때 연구 분야/문제군, 관심 이유, 기간과 자원·제외 범위를 현재 대화와 scope record로
확인한다. 이미 정해진 사항을 다시 승인받지 않는다. Research question, method, dataset,
venue를 전부 확정하거나 모든 resource 불확실성을 해소할 필요는 없다.

## Stage 1: Research Context

관심 문제, 대표 연구, 접근 가능한 도구/자료, 보고된 한계와 주요 자원 제약을 짧게 정리한다.
목표는 질문과 첫 관찰을 찾는 것이며 exhaustive survey가 아니다. Context가 이미 있으면
다시 작성하지 않고 달라진 근거만 갱신한다.

## Stage 2: Candidate Research Questions

초기에는 서로 다른 질문 몇 개를 비교한다(보통 3–5개; 최소 개수 gate는 아니다).
Failure, conflicting result, 새 자료, 기존 방법의 다른 적용, 재현 중의 이상 현상,
theoretical counterexample, 예상보다 강한 baseline에서 시작할 수 있다.

중요한 질문과 관찰할 대상이 있으면 잠정 candidate로 적는다. Phenomenon이 이미
입증됐거나 방법이 완성돼 있어야 하는 것은 아니다. 사용자 선택이나 충분한 비교가 있으면
새 후보 수를 채우기 위해 탐색을 다시 시작하지 않는다.

## Candidate Research Question Record

처음에는 한 문단 또는 다음의 짧은 기록이면 된다. 모르는 항목은 미확정으로 두고 다음에
알아낼 내용을 적는다. 모든 heading을 채우는 것을 아이디어 등록 조건으로 삼지 않는다.

```md
# <Short Research Question>
Status: exploratory

- 질문과 중요성:
- 근거: 관찰한 사실 / 논문 주장 / 잠정 설명을 구분하고 가까운 선행을 연결
- 첫 관찰: 가장 작은 사례·자료/구성 방법, 간단한 baseline 또는 counterexample
- 다음에 배울 것: 관찰할 결과, 가장 중요한 불확실성, 가능한 후속 판단
- 범위: 필요한 자원·비용/기간 추정과 아직 확보하지 못한 사항
```

설명 후보와 method sketch는 여기서 바로 작성할 수 있다. 예비 관찰과 변화 이유도 같은
record에 추가한다. 자세한 protocol·source inventory는 실행이 구체화될 때 study owner에 둔다.
기존의 긴 question 형식은 유지해도 되며 모든 후보를 새 형식으로 재작성하지 않는다.

## Stage 3: Comparative Assessment

다음 과제가 줄일 uncertainty와 비용으로 후보를 비교한다. 다음 항목은 판단을 돕는 질문이며
모두 H를 받아야 하는 gate가 아니다. 간단한 비교로 선택이 가능하면 전체 점수표를 만들지 않는다.

| Criterion | Assessment question |
| --- | --- |
| significance | 무엇을 알게 되거나 가능하게 하는가? |
| empirical accessibility | 현재 자료나 제한된 construction으로 관찰할 수 있는가? |
| feasibility | 기간 안에 중요한 uncertainty를 줄일 수 있는가? |
| informational value | 예상과 달라도 다음 판단에 도움이 되는가? |
| resource fit | compute·data·expertise·비용에 맞는가? |
| scientific depth | 단일 구현을 넘어 어떤 지식/유용한 capability로 발전할 수 있는가? |
| related-work overlap | 가까운 선행과 무엇이 같고 무엇이 아직 열려 있는가? |
| rigorous evaluation path | 유망하면 주장을 더 엄밀히 검증할 경로가 있는가? |

집중할 소수의 질문을 선택한다(보통 1–2개). 선행이 가깝다는 사실만으로 기각하지 않는다.
질문·조건·비교·얻을 insight가 실제로 겹치는지 확인한다. Artifact가 잘 준비돼 있다는
이유만으로 그 연구의 정보 가치가 더 높다고 가정하지 않는다.

### Direction And Method Development

시의성과 중요한 capability, 접근 가능한 개발 경로가 보이면 초기 효과가 불명확해도
방법을 발전시키는 작업을 선택할 수 있다. 관심 분야에서 여러 연구가 같은 문제를 다룬다는
사실은 relevance의 근거가 될 수 있으며, 자동 기각 사유나 신규성 증명으로 쓰지 않는다.

활성 후보의 후속 투자를 판단할 때는 가까운 question record에 한 문단으로
**중요한 문제, 잠정적인 핵심 설명/방법 원리, 가장 가까운 선행과의 예상 차이 또는
아직 모르는 차이, 그 차이를 가를 다음 관찰**을 연결한다. 이는 바뀔 수 있는
working statement다. 첫 후보 등록이나 작은 관찰의 합격 gate가 아니며,
선행과의 차이가 아직 불명확하면 무엇을 보면 구분되는지 적고 제한된 탐색을 할
수 있다. 유효한 관찰 뒤에도 구별할 설명이 나오지 않으면 실행이 쉬운 자료라는
이유만으로 같은 경로를 이어가지 않고 다른 후보와 정보 가치·비용을 재비교한다.

작은 pilot은 그 설정의 구현·baseline·작동 범위를 알려준다. 단일 toy task의 성공 포화나
무차이를 연구 방향 전체의 판정으로 확대하지 않는다. 좁은 예외를 계속 찾기보다, 학습된
정책·대표 과업·실제 적용 조건으로 연결해 방법을 수정하는 편이 유익할 수 있다.

이때 가까운 owner에 목표 capability, 초기 method sketch, 다음에 배울 내용과 제한된
개발 예산을 적고 진행한다. 예산은 작업 관리 기준이며 매 실험의 합격 gate가 아니다.
대표 과업도 단계적으로 추가할 수 있고 처음부터 모두 재현할 필요는 없다. 설정 변경은
변경 이유와 이미 본 결과를 기록하며, 특정 방법에 유리한 경우만 사후 선택하지 않는다.
데이터가 부족하거나 구성 요소가 아직 미완성이면 먼저 수정·학습할 여지를 검토한다.

최종 novelty, strong baseline, 독립 평가와 paper claim 기준은 기존대로 적용한다. 이 절은
초기 개발을 허용하는 운영 기준이며 효과가 없는 방법을 우수하다고 쓰는 예외가 아니다.

## Stage 4: Preliminary Literature Review

가장 가까운 primary papers부터 읽는다(보통 1–3개로 시작). 현재 질문과의 차이, 간단한
baseline, 쓸 자료/코드 또는 대체 study design, 아직 확인할 uncertainty를 정리한다.
Strongest adjacent baseline은 먼저 식별하고, 첫 관찰에 꼭 필요하지 않으면 구현은 뒤로 둔다.

전체 survey, 모든 최신 paper의 최종판 취득, 공식 checkpoint의 완전한 재현을 첫 관찰의
선행조건으로 삼지 않는다. 접근하지 못한 내용은 미확정으로 남긴다. Exact novelty와
artifact readiness를 주장할 때는 primary evidence로 뒷받침한다.

## Stage 5: Assumptions And Research Risks

지금 필요한 가장 중요한 assumption부터 다룬다. 그것이 틀리면 **다음 관찰을 해석할 수
없는지**, 아니면 **나중의 더 큰 주장을 제한하는지** 구분한다. 전자는 먼저 검사하고 후자는
한계로 남긴다. 위험 목록 전부를 해소할 때까지 아이디어를 보류하지 않는다.

지원/반박/정보 부족 각각에서 다음에 무엇을 배울지, 더 싼 측정이 있는지 적는다.
이때 반증 가능한 설명 초안을 만들 수 있으며 가설이 이미 맞다는 증명을 요구하지 않는다.

## Stage 6: Feasibility Or Pilot Study

첫 목표는 질문과 연결된 작은 관찰이다. One-case replay, simple baseline, 작은 data slice,
synthetic/analytic counterexample, 최소 재현, 관련 schema/evaluator audit를 사용할 수 있다.
실행과 method import는 `AGENTS.md`의 Docker-only rule을 따른다.

실행 전에 질문, 허용된 입력, 비교/관찰할 결과, 비용 범위, 출력 위치와 **탐색/확증 목적**을
기존 owner에 적는다. Environment·source/input version·command·seed·출력을 식별할 수 있어야
한다. 탐색 실행의 가설/parameter/metric을 영구 고정하거나 별도 full freeze를 요구하지 않는다.
변경·실패·제외 사례를 기록하고, 실행 후 주장에 필요한 검사를 완료한다.
한 관찰에 필요한 준비·실행·검산·해석은 가능한 한 한 작업 묶음으로 진행한다.
명령·hash·image·입력 identity 같은 재현 정보는 Docker-only 규칙대로 실행 manifest에
한 번 기록하고, Markdown에는 연구 판단에 필요한 요약과 위치만 남긴다. 모든
준비 성공을 별도의 연구 선택이나 문서 갱신으로 만들지 않는다.

### Exploration And Confirmation

| 목적 | 운영 | 결과의 의미 |
| --- | --- | --- |
| 탐색 | 관찰 → 설명 후보 → 간단한 방법/비교 → 수정. 본 데이터와 변경 이유를 기록한다. | 가설 생성과 다음 투자 판단; 사후 선택한 효과를 사전 확증으로 보고하지 않는다. |
| 확증 | Hypothesis·sampling/exclusion·endpoint·분석·중단 규칙을 결과 전에 고정한다. 탐색에 쓰지 않은 적절한 independent/held-out 자료로 검사한다. | 고정한 claim과 모집단에 한정한 evidence. 다른 analysis는 탐색으로 표시한다. |

확증을 buildup에서 수행할 수도 있지만 모든 pilot에 의무화하지 않는다. 반복적으로
held-out을 열어 선택에 이용했다면 새 확증이라고 부르지 않는다. 이론/결정론적 counterexample은
통계적 유의성 대신 해당 논증에 필요한 정확성을 검사한다. 내부 freeze는 공개 preregistration과 다르다.

### Validation And Revision

- 다음 추론을 바꿀 수 있는 입력 identity, label, causal access, baseline competence와 핵심
  계산을 검사한다. 작은 사례 관찰 전에 모든 scene/parity/baseline을 완료할 필요는 없다.
- 어떤 검사가 **지금 관찰의 해석을 좌우하는지**와 paper-level 주장에 앞서 나중에
  필요한지를 구분한다. 현재 입력·label·행동 비교가 무효라면 그 추론은 멈추고,
  다른 과업이나 더 작은 proxy의 정보 가치와 수리 비용을 비교한다. 미완료된
  후속 검증을 후보 전체의 반증이나 무기한 준비 목록으로 바꾸지 않는다.
- 새 evaluator/변환의 핵심 계산이나 강한 주장에는 독립적인 대조·재구성을 사용한다.
  검사를 통해 어떤 오해를 막는지 설명할 수 없는 중복 hash/문서 감사는 추가 gate로 삼지 않는다.
- Tool/evaluator 수리는 연구 수단이다. 수리 자체의 novelty가 아니라 열어주는 관찰과
  소요 비용으로 판단한다. 긴 준비가 이어지면 작은 proxy와 질문 재설계의 가치를 비교한다.
- Revision은 무엇을 보고 왜 바꾸는지, 무엇이 달라지고 비교가 어떻게 제한되는지,
  새 출력과 후속 검사 범위를 기존 owner에 기록한다. 기존 raw/frozen 결과를 덮지 않는다.
- 과거 frozen stop과 종료 판정은 그대로 보존한다. 새 규칙은 이를 자동으로 통과/재개시키지
  않는다. 과거 데이터를 새 탐색에 쓰면 이미 관찰한 자료임을 명시한다.

## Stage 7: Selection Decision

다음 판단을 구분해 기록한다. 작은 pilot의 비유의만으로 현상의 부재를 결론 내리지 않는다.

| 관찰/판단 | 다음 행동 |
| --- | --- |
| 측정/구현이 타당하지 않음 | 영향을 받는 추론을 멈추고, 수리 또는 다른 작은 study의 가치/비용을 판단한다. 질문의 반증으로 세지 않는다. |
| 정보 부족·불확실함 | 더 배울 수 있는지와 effect uncertainty/검정력·비용을 보고 refine/repeat/defer한다. 유의해질 때까지 자동 확대하지 않는다. |
| 설명에 반하는 유효한 증거 | 해당 설명을 discontinue하거나 근거 있는 다른 설명으로 reformulate한다. |
| 다른 질문의 투자 가치가 높음 | deferred와 재검토 근거를 남긴다. 과학적 반증과 구분한다. |
| 구체적인 가설과 타당한 첫 검증 경로가 있음 | select for hypothesis formulation; 정식 handoff를 기록한다. |

`refine`, `reformulate`, `repeat feasibility study`, `discontinue`는 대상과 이유를 명시한다.
가설을 한 번 바꿨다는 사실이나 정해진 횟수만으로 모든 연구를 종료하지 않는다. 명시적으로
정한 개별 study의 비용/stop은 지키며, 추가 투자는 다음 uncertainty와 비용으로 판단한다.

유효한 작은 관찰이나 의미 있는 준비 실패 뒤에는 **그 결과가 문제의 중요성, 잠정
설명, 단순 대안, 실행 가능성 중 무엇을 바꾸었는지**를 먼저 판단한다. 계속할 경우
다음 작업이 가르는 서로 다른 결과와 선택, 예상 비용을 적는다. 어느 결과에서도
같은 선택만 남는 미세 대조는 우선하지 않는다. 반복 pilot을 자동 queue로 만들지
않으며, 과학적 불확실성과 runtime·자료 호환성 위험을 구분한다. 후보를 오래
붙들지 여부는 고정 횟수 대신 새로 배울 내용과 대안 후보의 기회비용으로 판단한다.

## Entry To Hypothesis Formulation

Handoff는 **중요한 검증 가능 질문과 현실적인 첫 검증 경로가 있는지** 판단하는 결정이다.
Question record에 잠정 설명/예상 효과, 관찰·비교 대상, 가까운 선행과의 관계, 첫 검증의
타당성·비용 및 결과별 의미를 짧게 적는다. 예비 관찰 또는 documented feasibility assessment로
이 경로를 뒷받침하면 된다. 가설이 참이라는 결과나 모든 실행 준비의 완료는 필요하지 않다.

설명 초안은 handoff 전부터 question record에 적는다. 선택되면 source question, 기존 근거,
아직 해결할 위험과 첫 focused validation을 `hypothesis/`로 넘긴다. `ready_for_hypothesis`는
가설을 검증하기로 했다는 뜻이며 논문 방향 확정이나 효과 입증을 뜻하지 않는다.
효과가 아직 양성으로 나오지 않았다는 이유만으로 구체적이고 검증 가능한 설명의
focused validation을 계속 `buildup/`에 남겨두지 않는다. 반대로 넓은 관심 방향만 있고
서로 다른 결과를 예측하는 설명이나 타당한 첫 검증이 없다면 pilot 수가 많아도
자동 승격하지 않는다.

다음은 entry 필수조건이 아니다: final architecture, complete exact-prior survey,
publication-ready novelty, full benchmark, multi-domain evidence, 양의 통계 유의성,
failure-derived method principle, 고정된 논문/baseline/metric 개수, paper folder.
측정 자체가 해석 불가능하면 그 결과를 evidence로 쓰지 말고 타당한 검증 경로를 먼저 제시한다.

## Discontinuation Criteria

다음 판단을 지지하는 근거가 있고 값어치 있는 수정/작은 study가 남지 않으면 현재 질문이나
method route를 종료할 수 있다: 관련 현상에 반하는 증거, 단순 대안의 충분한 설명,
질문과 insight의 실질적인 선행 중복, 또는 허용된 자원에서 관찰 불가능함.
효과 미검출·불완전한 source release·설정 오류만으로 질문 전체를 반증하지 않는다.
Scope 전체의 종료는 개별 question의 종료와 구분한다.

## Hypothesis And Paper-Level Boundary

`hypothesis/`는 selected question의 focused validation, `experiments/`는 그 근거를 바탕으로
claim에 맞는 scaled evaluation·strong baseline·ablation·robustness·reproducibility를 다룬다.
최종 paper의 기존 novelty·failure-derived method·baseline·generality 기준은 유지한다.
이 기준의 완료를 buildup 진입으로 앞당기지 않는다. `paper/`는 최종 실험 완료 후 실제 논문을
작성할 때만 연다. 자세한 handoff와 일곱 생성 조건은 [hypothesis.md](hypothesis.md),
[paper.md](paper.md#paper-folder-gate)가 소유한다.

## Update Rules

규칙은 이 문서, scope/registry는 해당 README, 탐색과 선택 근거는 가까운 question/study/
selection record, 현재 과제는 `TODO.md`에 둔다. Live result를 workflow 문서에 누적하지 않는다.
승인된 작은 준비·검사·수정을 유의미한 관찰 또는 선택 판단까지 묶어 진행한다. 다음 TODO는
어느 파일을 검증할지보다 **무엇을 알아낼지**를 먼저 적고 필요한 기술 작업을 함께 설명한다.
일반 pilot 결과는 해당 study owner와 `TODO.md`에만 요약한다. 후보 간 우선순위나
`ready_for_hypothesis` 선택이 바뀔 때 `selection.md`와 scope registry를 갱신하고,
root README·`summary.md`는 상위 방향이 바뀔 때만 갱신한다. 긴 이력은 선택 기록과
study owner에 두며 색인·현재 상태 문서에는 최신 판단과 링크만 남긴다.
