# Literature Workflow

Updated: 2026-09-15

## Purpose

문헌 조사는 두 가지 mode를 지원한다.

1. `Scoping Literature Review`: 사용자가 정한 research scope에서 candidate
   research questions, nearest related work와 accessible study design을 찾는다.
2. `Admission Audit`: focused validation 근거가 생긴 hypothesis의 기여 차이,
   평가 타당성과 paper claim에 필요한 비교를 검토한다.

Early buildup에 paper-level admission criteria를 미리 적용하지 않는다.
Topic discovery의 stage와 산출물은 `docs/buildup.md`를 따른다.

## Scoping Literature Review Start Condition

사용자가 research scope와 resource constraints를 정한 뒤 review를 연다.
Research scope가 정해지기 전에는 특정 과거 연구 방향을 새 review의
기본값으로 사용하지 않는다.

다음 내용으로 질문 초안을 구체화한다. 형식과 항목 수를 별도 gate로 삼지 않고
미확정 사항은 첫 관찰에서 알아낼 내용으로 남긴다.

1. existing limitation
2. 선택한 research area에서 왜 중요한가
3. 관찰하려는 phenomenon 또는 disagreement
4. accessible artifact, data, evaluator 또는 preliminary study
5. 가장 단순한 baseline 또는 counterexample
6. 실패하면 무엇을 배우는가

Exact novelty, 세 개의 controls, multi-domain generalization과 forced method는
scoping literature review의 entry condition이 아니다.

## Scoping Literature Review Order

1. Research scope의 representative recent work, active groups와 benchmark를
   얕게 map한다.
2. anomaly, limitation, conflicting result, missing evaluation과 resource
   opportunity에서 후보를 비교한다. 보통 3–5개로 시작하지만 이미 선택한 질문에
   새 후보 수를 채우기 위한 탐색을 요구하지 않는다.
3. 각 question의 nearest primary papers부터 읽는다(보통 1–3개). Official artifact나
   허용된 작은 study construction 경로를 확인한다.
4. observable target, simplest baseline, critical assumption과
   feasibility를 기록한다.
5. 소수의 질문에 집중해 문헌과 작은 관찰·설명 수정을 오간다.

Broad survey의 완료를 feasibility study의 선행조건으로 삼지 않는다. 반대로 novelty와
artifact readiness의 최종 판단은 primary paper, appendix, official code/data로
재검증한다.

가까운 선행의 존재는 기각 근거가 아니다. 질문·조건·대안·새로 배울 내용의 실제 중복을
설명한다. 자료를 얻지 못하면 확인한 판본과 미확정 범위를 남긴다. 그 자료가 다음 관찰의
타당성을 좌우하지 않으면 전체 review/실행을 막지 않는다.

## Admission Audit Start Condition

Hypothesis의 focused validation 근거로 paper-level 투자를 판단할 때 다음을 고정한다.
이 admission audit을 buildup 진입이나 설명 초안 작성에 적용하지 않는다.

1. exact existing limitation과 nearest prior
2. selected research area에서의 substantive relevance
3. executable denominator와 evaluator
4. 가장 단순한 세 controls
5. 실패하면 무엇을 배우는가

## Admission Audit Order

1. Official benchmark/data/code로 executable denominator를 확인한다.
2. 2024--2026 exact problem/principle prior를 확인한다.
3. Data coverage, task/context, model capacity, training/evaluation protocol,
   resource cost와 domain-relevant confounder를 단순 control로 먼저 정의한다.
4. Claim에 맞는 independent split, task, domain 또는 external-baseline
   generalization path를 확인한다.
5. Residual이 특정 representation/inference/control form을 강제하는지 판정한다.
6. 위 조건이 남을 때만 one-week no-outcome contract를 쓴다.

## Evidence Labels

문서에서 다음을 분리한다.

- 사실: source, schema, released artifact, measured result
- 논문 주장: 저자가 paper에서 주장한 범위
- 에이전트 추론: source를 바탕으로 한 novelty/feasibility 판단
- 사용자 판단 필요: scope, resource 또는 irreversible choice

## Source Rules

- PaperReview나 survey는 discovery source로만 사용한다.
- Novelty와 artifact readiness는 primary paper, appendix, official code/data에서 재검증한다.
- Latest result가 중요한 경우 web search로 current source를 확인한다.
- Paper title, method, dataset, metric, benchmark 이름은 English original을 유지한다.

## Output

- Scoping literature review와 synthesis:
  `buildup/<short-scope>/related_work/`
- Selected research question의 exact-prior audit: 해당 `hypothesis/CAND-<number>/`
- Paper-level baseline/source audit: 해당 `experiments/E<number>_<short-title>/`
- `literature/README.md`는 종료된 연구의 compact summary만 소유한다. Active
  search payload를 그곳에 추가하지 않는다.

같은 literature payload를 stage folder와 다른 문서에 중복하지 않는다.

## Paper-Oriented Admission Rule

다음 기준은 candidate research question을 만들거나 Draft hypothesis로 넘기기
위한 조건이 아니다. Focused validation evidence가 생긴 hypothesis를 top-tier
contribution candidate로 검토할 때 적용한다.

모두 통과해야 paper contribution candidate로 승격한다.

1. executable denominator: public artifact 또는 사용자가 승인한 construction route
2. unoccupied exact problem/principle
3. residual after at least three simple controls
4. one-week decisive disconfirmation path
5. credible independent generalization route
6. failure-derived, non-substitutable method principle

Threshold나 denominator를 outcome 뒤에 바꿔 claim을 구제하지 않는다.
