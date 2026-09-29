# Equivalent State Representations for Robot Planning

Updated: 2026-09-23

## Status

`deferred / not run`. 2026-09-23 사용자 요청으로 실행 선택을 철회했다.
아래 protocol과 입력은 미실행 초안으로 보존하며 model 취득·추론을 진행하지 않는다.
현재 후보는 [Q16](../../../robotics/questions/interaction-conditioned-motion.md)이다.
2026-09-22 [후보 비교와 선택](../../../selection.md#cd5-observation-selection-2026-09-22)을
마쳤다. 공식 source와 작은 JSON 입력의 읽기 전용 확인만 완료했으며 model inference,
evaluator runtime, Docker build는 아직 실행하지 않았다. 현재 범위는 완전히 관측된
symbolic household planning이다. BEHAVIOR physics, perception 또는 실제 robot 성능을
측정하는 실험이 아니다.

선택 단계의 JSON identity·30개 task record hash와 문서 링크 검사를 통과했다.
[검증 기록](../../../../logs/20260922_113407_cd5_selection_validation.log)은 source/schema
확인만 다루며 아래 계획한 model/evaluator 검증과 구분한다.

## Question and informational value

**같은 상태 정보를 표현하는 방식·순서에 따라 생성 계획의 실행 가능성과 목표 달성이
달라지는가? 그 차이를 canonical ordering 또는 단순 행동 전제조건 보정으로 설명할 수 있는가?**

문자열이나 action sequence가 다르다는 사실만으로 실패를 세지 않는다. 서로 다른 valid
plan도 허용한다. 실패하면 object 식별, 관계 해석, 전제조건 누락, 잘못된 목표 해석과
출력 형식 오류를 구분한다. 표현 민감도와 symbolic correction 자체는 이미 알려진
선행이며, 이 작은 관찰의 목적은 다음 방법을 정할 구체적 실패 또는 단순 해결 사례를
얻는 것이다. 새로운 representation의 이점을 가정하지 않는다.

## Sources and inputs

- Source: [LookPlanGraph](https://github.com/Onishenko-sci/LookPlanGraph), commit
  `a2967bd33e15196ff139e3c62d8a7356bfdb65e3`.
- Public input: `benchmarks/grasif/behaviour1k/behaviour177.json`, 1,435,056 bytes,
  SHA256 `e261117a1d21844ad73aabd976e2c1d1573f5cb86afda069f5a90a470e524ce7`.
  실제 JSON은 **178개**의 고유 task name을 갖는다. 파일명 177, README 186,
  논문 설명의 177을 현재 파일의 분모로 사용하지 않는다.
- `init`, 자연어 `task`만 planner 입력으로 사용한다. `goal`은 evaluator 전용이다.
  `name`의 과제명이나 goal에서 만든 관련 object 목록을 prompt에 추가하지 않는다.
- [inputs.json](inputs.json): initial node 수 6–18의 159개 중
  `SHA256("cd5-20260922:" + name)` 순서로 최초 30개를 선택했다. 첫 6개는 development,
  다음 24개는 observation이다. 출력 성공 여부를 보고 뽑거나 대체하지 않는다.
  이는 protocol 개발용 분리이며 benchmark contamination 또는 독립 일반화 검증을 뜻하지 않는다.
- Source download/hash와 접근 한계는
  [comparison_sources.json](../../../robotics/related_work/comparison_sources.json)의
  `cd5_cd1_q8_review_20260922`가 소유한다. Source 전체의 license 파일은 해당 tree에서
  발견하지 못했으며 외부 code/data를 tracked artifact에 복사하지 않았다.

## Comparison fixed before inference

한 frozen [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), revision
`aa8e72537993ba99e69dfaafa59ed015b17504d1`, BF16, greedy decoding을 사용한다.
Model card의 license는 `qwen-research`다. Weight는 아직 취득하지 않았고 GPU compatibility와
실제 memory/throughput은 미검증이다. 작은 local baseline이며 최신 strongest planner의
대표 또는 LookPlanGraph 논문의 재현이라고 주장하지 않는다.

| 조건 | 같은 initial state를 제시하는 방법 | 구분할 설명 |
| --- | --- | --- |
| JSON ordered | entity의 name/id 순서, 정렬된 field의 JSON | 단순 canonical serialization |
| JSON shuffled | 동일 entity record를 고정 seed 20260922로 섞음 | 정보와 field 형식을 바꾸지 않는 순서 효과 |
| Text ordered | 같은 field/value를 빠짐없이 읽는 고정 문장 template, 같은 entity 순서 | 표면 형식의 효과 |
| Text shuffled | Text의 entity block만 동일 permutation으로 섞음 | 형식별 순서 민감도 |

Task instruction, action vocabulary/preconditions, 출력 JSON schema와 generation limit는
네 조건에 공통이다. Template는 추론·요약·관련성 선택을 하지 않고 역변환 가능한
field/value 표현으로 만든다. Affordance, closed/open, containment와 agent location도
모두 보존한다. 같은 원본 fact set으로 돌아오는 검사를 Docker에서 수행한다.

공통 최대 input 8,192 tokens, output 1,024 tokens, 최대 128 primitive actions를 쓴다.
입력을 자르지 않는다. 초과/변환 오류는 네 조건 공통의 unavailable task로 기록하고
원래 30개 분모와 실제 평가 분모를 함께 남긴다. **정보와 상한은 같지만 실제 token 수·
latency가 같다고 주장하지 않는다.** Tokens/latency를 조건별 보고하며 순수한 구조 효과와
비용 효과를 완전히 분리했다는 해석을 피한다.

Development 6 × 4 = 24, observation 24 × 4 = 96으로 최대 **120 plan generations**다.
Development에서 schema/prompt 오류를 수정하면 변경 이유·기존 출력과 최종 설정을 보존한다.
Observation을 본 뒤 유리한 prompt나 task로 바꾸지 않는다. Development에서 모든 조건이
계획을 전혀 수행하지 못하면 model/interface feasibility 문제로 기록하고 모델 확대 없이
이 관찰을 마친다. 낮은 성공률을 representation 효과로 해석하지 않는다.

## Execution and simple correction

각 생성 계획을 다음 두 방식으로 평가한다. 새 LLM call이나 goal 정보는 보정에 쓰지 않는다.

1. **Strict:** 명시한 primitive action을 순서대로 수행하고 최초 invalid action에서 멈춘다.
   실패 전의 유효 prefix, 최초 오류와 최종 goal 만족을 보존한다.
2. **Prerequisite correction:** 같은 출력에 현재 graph의 room 이동·closed ancestor 열기만
   필요한 순서로 삽입한 뒤 strict evaluator로 재검사한다. Object 선택이나 목표를 바꾸거나
   임의 pick/place를 추가하지 않는다. Insertion 종류·수와 원래/최종 action 수를 기록한다.

이는 LookPlanGraph의 `correct_action`에 있는 location/access correction을 좁힌 단순
baseline이다. 전체 method reproduction이 아니며 symbolic state privilege는 모든 조건에
공통이다. Canonical serialization, lossless text, deterministic prerequisite correction이라는
세 단순 대안을 먼저 비교한다. 추가 LLM verifier나 학습 모듈은 이 관찰에 포함하지 않는다.

## Evaluator contract and verification

공식 `validator.py`는 action error가 있어도 뒤 action을 계속 평가하지만 strict 성공에는
error가 없어야 한다. Object goal은 관련 object class의 상태·관계 count로 평가하므로
instance별 exact graph equality와 다르다. 이 class-equivalence 의미를 기록하고 동일하게
적용한다. 목표를 model에 제공하지 않으며 source의 부분 점수를 성공률로 대체하지 않는다.

Source의 `put_inside` self-placement 검사는 tuple인 holding과 node dictionary를 비교한다.
따라서 실행 전 adapter에서 self-containment/cycle, invalid reference, hand state를 별도
검사한다. 원본을 조용히 바꾸지 않고 native 판정과 보강한 유효성 판정의 차이를 남긴다.
`create_pkl.py`의 전역 task 참조와 agent 기본값도 explicit schema conversion으로 처리한다.

검증은 생성 결과를 요약하는 코드와 별도로 initial facts 복원, state transition,
goal predicate/class counts를 대조한다. 손으로 확인한 valid plan, missing-open/wrong-room,
self-placement 사례를 먼저 검사한다. 원본 goal이 표현할 수 없거나 모순된 task는 오류로
보존하며 실행 결과를 보고 제외하지 않는다. 이 검사는 benchmark의 물리 타당성 보장이 아니다.

## Readout and interpretation

- Primary: 24개 observation task의 paired strict/corrected task success와 개선·악화 case.
- Secondary: valid-prefix length, unmet precondition 종류, parser/schema failure, goal failure,
  inserted actions, input/output tokens와 latency. 같은 plan의 두 replay를 독립 표본으로 세지 않는다.
- 다른 valid plan만 나온 경우: 행동 실패가 아니라 harmless variation이다.
- Canonical ordering 또는 prerequisite correction으로 차이가 사라진 경우: 해당 단순 대안이
  충분한 범위로 해석하고 richer representation을 자동 개발하지 않는다.
- 차이가 남은 경우: 동일 정보 확인과 실패 사례를 먼저 읽는다. One-model/작은 task subset의
  잔여 차이만으로 새 원리, 일반성 또는 학습 module의 필요성을 주장하지 않는다.
- 모두 성공하거나 interface 실패가 지배하는 경우도 유효한 투자 판단이다. 실패를 찾기 위해
  scene·model·prompt grid를 자동 확대하지 않는다.

## Execution budget and next work

다음 TODO는 **새 workspace Docker recipe → source/model acquisition → 6개 development →
24개 observation → 독립 검산·사례 해석** 한 묶음이다. 준비 약 1작업일, GPU inference
4시간·CPU 검산 1시간, model payload 약 6.2 GB의 계획 상한/추정이며 실측이 아니다.
GPU 점유 상황을 읽기 전용 확인한 뒤 사용 가능한 device 하나를 명시한다. 추가 학습은 없다.

Recipe/config/lock/실행 명령은 구현 시 이 폴더에 둔다. 외부 source와 입력은 read-only로
mount하고 새 output은 `runs/cd5/representation/<run-id>/`, checkpoint는
`checkpoints/cd5/`에 분리한다. Long job은 timestamped `logs/`와 background session으로
관리한다. 결과·로그·실행 identity를 보존한 뒤 이 작업에서 만든 불필요한 종료 container만
개별 정리한다. 현재 Docker asset 생성·삭제와 새 inference 결과는 없다.
