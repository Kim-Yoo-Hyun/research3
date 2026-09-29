# Task-Relevant Spatial State

Updated: 2026-09-18

## Status

`deferred` — 첫 symbolic planning 관찰과 goal-conditioned 수정의 실행·검산·해석을 완료했고,
직접 선행·추가 정보 가치 비교 뒤 현재 fully observable instance-selection 경로의 추가 투자를 보류했다.
[후속 결과·반례·투자 판단](../pilot_studies/q4-planning/README.md#goal-conditioned-observation-2026-09-18)을 따른다.
[선택 근거](../../selection.md#q4-observation-selection-2026-09-18)와
[Q3 비교·직접 선행](../related_work/policy-geometry.md#q3-q4-observation-comparison-2026-09-18)을 따른다.

## Investment Decision and Re-entry

[후속 투자 비교](../related_work/policy-geometry.md#q4-follow-up-investment-review-2026-09-18)에서
Taskography의 pruning/plan quality 대조, PLOI의 multiplicity 한계와 원본 validation,
Scale-Plan의 dependency filtering을 확인했다. 현재 결과는 단순 선택·전체 route proxy·
satisficing search의 상호작용을 보여주지만 새 representation의 필요성을 지지하지 않는다.

판단은 **현재 경로의 투자 보류**이며 task-relevant state 질문 전체의 반증이 아니다.
문제43의 optimal cost를 추가 확인하는 작은 실험은 가능하지만, 이미 본 설명을 세분화하는
것보다 Q3의 아직 보지 않은 control/timestep 관찰을 우선한다. 기존 수치·반례·artifact는 보존한다.

재검토 가능성: robot action 또는 partial observation과 연결된 구체적 사례에서 단순
ancestor closure·goal-conditioned 선택·search 변경이 서로 다른 예측을 내고, 제한된
대조로 그 차이를 관찰할 수 있을 때 비용·정보 가치를 다시 비교한다. 새 dataset/LLM
module의 존재나 평균 plan 길이 개선만으로 재개하지 않는다. 완성된 novelty·positive
residual을 새 관찰의 entry gate로 요구하는 조건은 아니다.

## Research Question Or Suspected Phenomenon

Task-relevant state를 줄일 때 관계와 개체 구별의 손실이 downstream plan validity·비용에
어떤 영향을 주는가? 첫 관찰은 **목표 class에 속한 여러 instance 중 가까운 개체를 고르고
navigation/containment 관계를 보존하는 단순 대안으로 충분한가?**로 좁힌다.
원래의 dense 3D/2D/VLM 비교는 미실행이다. Symbolic state에서 선택의 영향을 먼저 분리한다.

## Significance And Prior Boundary

Compact state가 planning cost를 낮춰도 필요한 정보를 잃으면 utility가 줄어든다.
그러나 task-aware compression이나 dependency preservation 자체는 새 원리가 아니다.
Clio/ASHiTA뿐 아니라 [Taskography](https://proceedings.mlr.press/v164/agia22a.html)의
SCRUB/SEEK와 [Scale-Plan v1](https://arxiv.org/html/2603.08814v1)이 직접 선행이다.
SCRUB을 제외하고 semantic top-k만 이기는 비교로 contribution을 주장하지 않는다.

## Facts And Source Claims

- 사실: Taskography 공식 PDDL fork의 domain, test 문제와 대응하는 SCRUB 문제를
  pinned commit에서 취득했다. Source/hash/선정 목록의 owner는
  [comparison_sources.json](../related_work/comparison_sources.json)의
  `q3_q4_comparison_20260918`이다. 실행 결과·재현 artifact는
  [study owner](../pilot_studies/q4-planning/README.md)가 소유한다.
- 논문 주장: Taskography는 scene graph의 symbolic task planning benchmark이며
  SCRUB은 목표 관련 object 및 ancestor/연결 정보를 보존한다. Lifted goal에서는
  class를 만족하는 여러 instance가 남아 pruning이 보수적일 수 있다. PLOI/SEEK도
  이미 object selection과 planning을 다룬다. 이 현상 자체의 최초 발견을 기대하지 않는다.
- 범위: building graph에 symbolic task를 부여한 fully observable 문제다. Visual
  detection, noisy geometry, collision-free motion 또는 physical execution GT가 아니다.
- Clio relevance boxes와 VLA-Arena action/precondition을 연결하는 기존 경로는 미확인이다.
  이번 Taskography 경로가 그 연결을 입증한 것은 아니다.

## First Observation

아래는 실행 전에 정한 비교 설계다. CPU Docker의 실제 command·실패 수정·결과와 검산은
[study README](../pilot_studies/q4-planning/README.md)에 기록했으며 이 설계의 실험을 완료했다.

### Fixed inputs

공식 test 디렉터리의 **숫자 ID 오름차순**으로 lifted `taskographyv4tiny5`의
`problem40`–`problem45` 여섯 개를 primary slice로 선택했다. Grounded
`taskographyv2tiny1`의 `problem40`–`problem41` 두 개는 evaluator/SCRUB 대조용이다.
Planner 결과를 보기 전에 고정했다. 목표 개수가 다른 두 domain의 aggregate 성능을
서로 비교하지 않는다. Tiny slice이며 독립 scene 수나 generality를 가정하지 않는다.

Input contract는 원본 action/precondition/effect, full initial state와 goal이다.
Lifted goal의 `classrelation`을 instance-level physical predicate로 바꾸지 않는다.
원본 class predicate와 최종 `inreceptacle`/class facts의 witness 일치는 보조 점검으로
분리한다. 불일치가 있으면 source semantics와 selection의 효과를 구분한다.

### Simplest comparisons

| Condition | 선택과 목적 |
| --- | --- |
| Full | 원본 state/object set; 비용과 validity의 reference |
| SCRUB | 공식 배포된 해당 test 문제; 관계·ancestor 보존의 강한 단순 기준 |
| Lexical + closure, b=0/1 | Class 후보를 ID 순으로 선택; instance budget 자체의 효과 |
| Nearest + closure, b=0/1 | 초기 agent에서 static navigation graph의 unit-action shortest distance 순으로 선택; topology만으로 충분한지 |

Item class `c`의 quota는 goal에서 요구하는 서로 다른 receptacle class 수 `r(c)+b`,
receptacle class의 quota는 `1+b`이며 가능한 후보 수로 cap한다. 반복 class goal에 무조건
하나만 남기는 자명한 부족을 피하는 휴리스틱이며 최소 sufficient set 보장은 없다.
거리 동률은 ID 순으로 정한다. Full initial topology를 쓰되 reference plan/result는 쓰지 않는다.

두 selector에 **동일 closure**를 적용한다. Goal symbols, robot state, 선택된 개체의
현재 containment ancestor, place/location, 이동에 필요한 room/place 연결과 관련 class
facts를 보존한다. 공식 SCRUB source를 기준으로 구현·대조하되 selector에 붙이는 변형을
공식 SCRUB의 완전한 재현이라고 부르지 않는다. 실제 규칙과 object/fact 목록은 실행 전
manifest에 남긴다. 이번에는 relation 보존 규칙을 공통으로 두고 instance 선택을 비교한다.

Matched budget은 **closure 전 class별 instance quota**다. Closure 후 object/fact 수는
별도 비용으로 기록한다. 같은 token 수나 같은 최종 information budget을 달성했다고
주장하지 않는다. Selection이 full state를 입력으로 받는 preprocessing 비용도 포함한다.

### Planner and verification

- 새 CPU Docker recipe에서 Fast Downward `lama-first`와 VAL의 source commit/build
  dependency를 고정한다. Image는 `research3-q4-planning:v1`, container는 workspace/study/run
  label과 지정 output mount를 사용한다. 기존 외부 simulator/image는 사용하지 않는다.
- 동일 planner/config/seed, 호출당 **end-to-end 60초**, CPU 1개·4 GiB memory 상한으로
  translation/grounding/search를 포함한다. 실제 관찰 시간은 study 결과에 별도로 기록했다.
- Primary denominator: lifted 6문제 × 6조건 = 36개. Grounded 2문제 × Full/SCRUB =
  4개 sanity 호출은 따로 보고한다. Reference 실패를 denominator에서 지우지 않는다.
- Primary: 원본 full problem에서 검증된 plan 수/시도 수. Timeout, memory/build error,
  explicit unsolvable, invalid plan을 구분한다. Timeout을 unsatisfiable로 해석하지 않는다.
- Secondary: plan action 수, preprocessing/translation/search 시간, 남긴 item/receptacle 및
  전체 object/fact 수. Plan 길이 차이는 양쪽 모두 valid인 pair와 그 분모를 함께 적는다.
  `lama-first`의 plan 길이를 optimal cost로 부르지 않는다.
- Pruned problem뿐 아니라 **원본 full domain/problem**에서 VAL로 plan을 replay하고
  최초 violated precondition/goal 상태를 기록한다. 공식 full/scrub domain의 이름 외
  action semantics 일치도 확인한다.
- CD5는 동일 objects/init/goal의 lossless serialization→canonical PDDL round trip으로
  연결한다. Canonical facts/hash 동일성을 검사하며 이를 LLM representation 성능
  evidence로 쓰지 않는다. 별도 model 또는 추가 planner 호출이 필요한 비교는 아니다.

### Cost and next action

실행 전 에이전트 추정: 새 CPU image/adapter/validator 준비 **0.5–1 작업일**. 40회 planning의
serial timeout 합은 최대 40분이며 build/preprocessing/검산은 별도다. GPU, 학습, 추가
대형 dataset, simulator나 annotation은 필요하지 않다. 당시 미확인했던 build/runtime은
이번 실행에서 확인했고 CLI 설정 오류와 수정도 보존했다.

고정한 40개 조건의 실행·독립 검산·case 해석을 완료했다. CLI/diagnostic 수정을 별도
실패 기록으로 보존했다. 결과·로그·재현 정보를 확인한 뒤 이번 종료 container 10개를 정리했다.

## Observation and Revision 2026-09-18

사실: 단순 selector와 SCRUB은 primary 여섯 문제에서 모두 valid였고 Full 한 건은
timeout이었다. Nearest b0는 SCRUB보다 평균 계획이 길었으며, b1에서 길어진 일곱 사례의
더 짧은 b0 plan은 b1에서도 유효했다. 해당 악화에는 satisficing search의 영향이 있다.
반면 SCRUB이 사용한 일부 instance는 Nearest가 제외했다. 자세한 수치와 반례는
[case interpretation](../pilot_studies/q4-planning/README.md#case-interpretation)이 소유한다.

에이전트 판단: symbolic validity를 위한 learned selector의 필요성은 현재 지지되지 않는다.
다음 설명 수정은 **초기 agent 거리 대신 goal receptacle까지의 이동과 instance binding을
고려하면 단순 선택의 계획 비용을 줄일 수 있는가**다. 같은 여섯 문제·b0 quota·공통 closure·
동일 planner의 작은 대조 한 번으로 확인한다. 이미 본 자료의 탐색이며 새 held-out이나
새 method novelty를 주장하지 않는다. 큰 dataset/학습/두 번째 domain으로 확대하지 않는다.

### Goal-conditioned follow-up

위 수정을 실행·검산했다. 목표 receptacle까지의 이동과 distinct assignment를 고려한
단순 선택은 여섯 문제 모두 valid였고 Nearest보다 네 문제의 계획을 줄였다. 동일 proxy의
선택 동점에서 계획이 길어진 반례도 있었다. 구체적 수치·분모·선택 규칙은
[study owner](../pilot_studies/q4-planning/README.md#goal-conditioned-observation-2026-09-18)가 소유한다.

양방향 transfer는 두 영향을 구분한다. 일부 기존 계획은 선택에서 제외된 instance 때문에
옮길 수 없었다. 반면 문제40에서는 기존 짧은 SCRUB plan이 새 state에서도 실행됐고,
네 문제의 더 짧은 새 plan은 SCRUB에서도 실행됐다. 이 다섯 차이에는 현재 satisficing
search가 더 긴 해를 반환한 영향이 명확하다. 옮기지 못한 계획은 그 구체적 plan의 제외를
뜻하며 해당 state의 optimal cost 증가를 증명하지 않는다.

에이전트 해석: 목표까지의 이동은 초기 거리만 보는 설명을 개선하지만 additive proxy와
전체 route/search를 구분해야 한다. 새 학습의 필요성은 아직 나오지 않았다. 다음은 직접
선행과 비교해 남은 질문의 정보 가치·추가 투자 또는 Q3 재비교를 판단하는 작업이다.

## Interpretation And Next Investment

사전 예상: closure와 class multiplicity를 고려한 가까운 instance 선택이 대부분의
계획을 보존할 수 있다. **에이전트의 예상이며 결과가 아니다.**

- Nearest+closure가 SCRUB 대비 validity를 유지하면서 비용을 줄이면 단순 대안의
  충분성을 기록한다. 새로운 module의 필요성을 만들어내지 않는다.
- 차이가 남으면 instance/containment 누락, 여러 goal의 binding, 탐색 시간 초과,
  원본 class semantics로 사례를 구분한다. 관찰에서 요구되는 작은 설명/방법 수정
  한 번과 보류를 비용·정보 가치로 비교한다.
- 차이가 없거나 모두 풀리지 않아도 그대로 보고한다. 더 큰 dataset, 두 번째 scene
  family, learned selector 또는 positive residual을 자동 후속 조건으로 삼지 않는다.
- Physical robot/VLA utility나 contribution으로 확장하려면 별도의 관측·action 연결과
  직접 선행 대비 설명이 필요하다. 이번 선택은 hypothesis/paper 승격이 아니다.

## User Decision Needed

없음. 기존 Robotics scope의 작은 buildup 관찰이다.
