# Taskography Instance Selection

Updated: 2026-09-18

## Status and ownership

`completed` / current route `deferred`. 첫 관찰과 [goal-conditioned 후속](#goal-conditioned-observation-2026-09-18)을
CPU Docker에서 구현·실행·검산하고 사례 해석을 완료했다. [후속 투자 판단](#follow-up-investment-decision)에서
현재 경로는 보류하고 Q3의 작은 관찰을 선택했다.
이 README는 실행 규칙·artifact·결과의 owner다.
새 report나 paper-level experiment가 아니다. 코드와 compact summaries는 여기,
row-level output은 ignored `runs/q4-planning/`에 둔다.

## Protocol

Lifted tiny5 test 40–45 × Full/SCRUB/Lexical b0,b1/Nearest b0,b1 = 36회,
grounded tiny1 test 40–41 × Full/SCRUB = 4회를 분리한다. 원본 goal/action을 보존하고
Fast Downward `lama-first`, seed 0, CPU 1개/4 GiB, end-to-end 60초를 공통 적용한다.
VAL은 원본 full state와 축약 state 양쪽에서 검산한다. CD5는 같은 state의 lossless
round trip이며 별도 LLM 성능 실험이 아니다. Timeout을 unsatisfiable로 바꾸지 않는다.

Selector는 quota를 먼저 적용한 뒤 공통 closure를 적용한다. Closure는 선택 instance의
containment chain과 location/place/room ancestor, 모든 room과 room의 center place/location,
agent의 초기 place/location, 선택 place의 center location을 보존한다. Class symbol과
그에 관한 facts도 유지한다. Official SCRUB의 단순 관계 보존을 참고한 selector adapter이며
공식 SCRUB 자체는 배포 test 문제를 그대로 사용한다. 실제 선택 목록을 각 case에 기록한다.

## Sources and environment

- Input/source manifest: [comparison_sources.json](../../related_work/comparison_sources.json),
  `q3_q4_comparison_20260918`; mount `runs/reserve_review/20260918/pddlgym` read-only.
- Fast Downward release-24.06.1: `1eef26b2cbf599a1894606aa898d9d49e1034cb9`.
- VAL: `3c7a1f330bdab0ba28a4762bb45c3f06c27fb6d4`.
- Python public base digest와 Debian snapshot은 Dockerfile에 고정한다.
  Installed package inventory는 [dependencies.lock](dependencies.lock), source/binary hash는
  image `/opt/environment/`와 output의 `environment/`에 보존했다.
- Image `research3-q4-planning:v1`; CPU only. 기존 external image/container는 사용하지 않는다.

## Commands and job record

Working directory: `/home/yoohyun/research3`.

```bash
bash buildup/robotics/pilot_studies/q4-planning/build.sh
```

Build는 별도 tmux job에서 실행하며 timestamp log/exit file은 `logs/`에 둔다.
Run/verify 명령과 실제 image ID는 아래 launch record와 [artifacts.json](artifacts.json)에 기록했다. Input/source는 read-only,
output은 새 run ID 경로를 쓰고 기존 출력을 덮지 않는다. 결과·로그·재현 정보 보존 후
이번 생성 기록과 mount/command가 확인되는 불필요한 container만 개별 삭제한다.

### Launch 2026-09-18

Build completed: `logs/20260918_102221_q4_build.log`, exit 0.
Image ID / repository digest: `sha256:cf36dd836af9c48a0d96326124b4f13363e8b44ce5c77446cae639ce8fc6db95`.
Build의 config digest는 `sha256:ed54b52e89f20b25c780d6ef829e312ef2b7f01b58e2215593828313f697347f`이며 image ID와 구분한다.
Output: `runs/q4-planning/20260918_v1/observation/`; creation/inspect receipts:
`runs/q4-planning/20260918_v1/containers/`.

```bash
python3 buildup/robotics/pilot_studies/q4-planning/orchestrate.py prepare --run-id 20260918_v1
python3 buildup/robotics/pilot_studies/q4-planning/orchestrate.py run --run-id 20260918_v1
python3 buildup/robotics/pilot_studies/q4-planning/orchestrate.py verify --run-id 20260918_v1
python3 buildup/robotics/pilot_studies/q4-planning/orchestrate.py analyze --run-id 20260918_v1
```

Host script는 Docker 생성·mount·log/inspect 보존만 수행한다. 모든 PDDL 처리, selection,
planning, 검산과 분석은 container 내부다. 각 command와 image ID는 해당 receipt에 남는다.
Fast Downward `lama-first`의 공식 alias를 그대로 펼치고 `--random-seed 0`을 더한다.
Container 4 GiB 내 orchestration 공간을 위해 planner 자체 memory cap은 `3900M`이다.
Input/source byte hash와 round-trip equality를 포함한 40개 case 준비는 통과했다.

### CLI repair before interpretation

`20260918_v1`은 Fast Downward 24.06.1에서 제거된 전역 `--random-seed` 인자로 search
시작 전에 exit 33을 냈다. 진행 중인 해당 study container를 중단하고 입력/로그를 보존했다.
동일 image의 `utils/rng_options.cc`, `search_algorithms/plugin_lazy_greedy.cc`를 읽어
`lazy_greedy(...,random_seed=0)`으로 수정했다. Heuristic/alias의 다른 설정은 그대로다.
이는 구현 실패이며 invalid plan이나 연구 질문의 실패로 세지 않는다. 다음부터 동일한
infrastructure error는 첫 case에서 중단한다. 원래 40개 설정을 변경하지 않고 새 run ID
`20260918_v2`로 실행한다. v1의 실패 호출/중단과 그 추가 비용은 별도 기록한다.

실제 수정 후 명령은 위 네 command의 run ID를 `20260918_v2`로 바꾼 것이다.

## Results 2026-09-18

**사실:** 수정 후 고정한 40개 조건을 완료했다. Primary 36개에서 35개 valid, Full의
problem41 한 개는 end-to-end 60초 timeout이다. Grounded sanity 4개는 모두 valid다.
Timeout을 unsolvable/invalid로 바꾸거나 분모에서 제외하지 않았다.

| Primary condition | Full-problem valid / 6 | Mean plan length (valid only) | Mean planning wall seconds (all 6) | Mean retained PDDL objects |
| --- | --- | --- | --- | --- |
| Full | 5/6 | 63.4 (n=5) | 14.42 | 312.5 |
| SCRUB | 6/6 | 71.2 (n=6) | 3.90 | 242.2 |
| Lexical b0 | 6/6 | 105.2 (n=6) | 0.29 | 139.5 |
| Lexical b1 | 6/6 | 118.3 (n=6) | 0.37 | 159.0 |
| Nearest b0 | 6/6 | 77.7 (n=6) | 0.29 | 139.3 |
| Nearest b1 | 6/6 | 84.8 (n=6) | 0.33 | 158.2 |

PDDL objects는 item/receptacle뿐 아니라 room/place/location/class symbol을 포함한다.
Full의 plan 길이는 5개 성공 조건부 평균이라 다른 행의 6개 평균과 직접 순위를 매기지 않는다.
SCRUB–Nearest b0는 동일 여섯 문제에서 비교 가능하며 Nearest가 평균 6.5 actions 길다.
Nearest b0는 Lexical b0보다 5/6 문제에서 짧지만 모든 문제에서 우월하지는 않다.

Timing은 CPU quota 1개의 단일 serial 실행 관찰이다. Planner startup/translation/search가
포함되고 timeout도 포함한다. Warm-up 반복·hardware 고정·통계적 latency 비교는 하지
않았다. `preprocess_seconds`는 adapter와 serialization/file I/O 시간이며, 원본 공통 parsing과
배포 SCRUB를 만드는 offline preprocessing 비용을 포함하지 않는다. 따라서 표의 wall time을
전체 system cost 절감률로 해석하지 않는다. 수정 후 planning wall 합은 약 131.7초다.

### Case interpretation

| Problem | Full | SCRUB | Lexical b0 / b1 | Nearest b0 / b1 |
| --- | --- | --- | --- | --- |
| 40 | 38 | 38 | 106 / 90 | 70 / 89 |
| 41 | timeout | 110 | 169 / 221 | 118 / 108 |
| 42 | 66 | 67 | 61 / 85 | 72 / 67 |
| 43 | 79 | 79 | 101 / 103 | 51 / 73 |
| 44 | 78 | 78 | 115 / 102 | 88 / 87 |
| 45 | 56 | 55 | 79 / 109 | 67 / 85 |

값은 유효한 plan의 action 수다. 다음은 **사후 진단**이며 새 planner 호출을 추가하지 않았다.

- b0→b1에서 plan이 길어진 7/12 비교 모두, 더 짧은 b0 plan이 b1 state에서도 VAL과
  독립 replay를 통과했다. 예: problem43 Nearest 51→73. 따라서 이 증가를 더 큰 state의
  intrinsically worse optimal cost로 해석할 수 없다. 현재 satisficing search가 더 긴 해를
  반환한 것이다. `more objects → better plan`의 단조성도 이 planner에는 보장되지 않는다.
- SCRUB의 plan을 Nearest b0에 옮기면 여섯 개 모두 제외된 instance/location 때문에
  실행할 수 없었다. Problem40의 38-action plan에는 Nearest가 제외한 vase/potted plant와
  chair/couch가 쓰였다. 이것은 해당 구체적 대안이 빠졌다는 사실이며, 남은 state에 다른
  짧은 계획이 없다는 증거는 아니다.
- Problem43에서는 Nearest b0 자체가 SCRUB보다 짧다. Plan quality 차이를 단순히
  정보 손실량 하나로 설명할 수 없으며 instance 선택과 heuristic search를 함께 보아야 한다.
- 여섯 primary 문제는 static layout hash가 두 종류(5+1)이고 initial-state hash가 다섯
  종류다. 여섯 독립 scene/domain을 관찰했다고 쓰지 않는다.

자세한 plan transfer, 최초 missing object/precondition과 navigation/manipulation action
counts는 ignored output의 `diagnosis.json`, `analysis.json`, `diagnostics/*.log`에 보존했다.

### Verification and repairs

- 원본 full/pruned PDDL에 대한 VAL과 별도 transition replay가 39개 plan에서 일치했다.
  40개 attempt의 outcome/denominator를 보존하고 61,511개 precondition/goal 검사를 통과했다.
- 원본 PDDL 24개 bytes/hash, 모든 case의 source/output identity·goal·subset·counts,
  40개 same-information round trip을 확인했다.
- Broken last-action-only plan과 empty plan을 VAL/별도 replay가 모두 거절했다.
- Nearest의 550개 candidate distance를 BFS 구현과 다른 room all-pairs/center 경유 공식으로
  대조해 모두 일치했다. Positive class goal와 최종 instance witness의 불일치는 관찰되지 않았다.
- Witness diagnostic의 첫 구현은 class annotation이 없는 grounded domain과 SCRUB가
  제거한 비목표 class를 처리하지 못했다. 두 failed verify log와 당시 코드를 보존하고,
  grounded에서는 해당 diagnostic을 제외하며 pruned state의 class 해석에는 원본 static
  catalog를 명시적으로 사용하도록 수정했다. 이는 사후 해석용이며 planner input/goal,
  40개 planning 결과 또는 primary validity label을 바꾸지 않았다.
- 초기 CLI 실패는 search 전 exit 33이 기록된 34개와 진행 중 중단한 다음 호출로 보존했다.
  완료된 실패 호출의 기록 시간은 약 54.3초다. 연구 denominator 40개의 새 조건을 추가한
  것이 아니라 동일 설정의 infrastructure 재시도다. 이 overhead를 성공 실행에서 숨기지 않는다.

## Investment Decision and Next Observation

**첫 관찰 당시 판단: `refine`, question은 `under_review`.** 당시 작은 symbolic slice의 validity는 단순
selection+closure로 유지됐다. 새 learned module의 필요성은 지지하지 않는다. 남은 질문은
계획 비용과 search behavior이며 physical/VLA utility나 paper novelty로 승격하지 않는다.

다음 작은 수정은 **goal-conditioned distance**다. 초기 agent에 가까운 개체만 고르는 대신
agent→item→goal receptacle의 이동을 고려하는 단순 선택을, 기존 six lifted 문제·b0 quota·
공통 closure·동일 planner와 비교한다. 같은 class의 여러 goal에는 distinct item binding을
고려한다. 이미 본 자료의 탐색적 수정이며 새 held-out evidence가 아니다. 새 학습이나 scene
확대 없이 한 번의 구현·실행·검산·해석으로 묶고, 이것이 설명하는 범위와 선행 대비 추가
투자 가치를 다시 판단한다. b1의 악화를 정보 손실로 고치려는 module은 선택하지 않는다.

## Goal-conditioned follow-up protocol

2026-09-18 실행 전 고정. Goal의 receptacle class마다 하나의 instance를 공유 선택하고,
같은 item class의 서로 다른 goal에는 서로 다른 item을 할당한다. 다음 additive proxy를
최소화한다: `sum_goal [d(agent_initial, item_initial) + d(item_initial, receptacle)]`.
`d`는 기존 Nearest와 같은 static navigation action graph의 최단 거리다. Receptacle
조합을 열거하고 각 item class의 distinct assignment는 subset dynamic programming으로
푼다. 동점은 정렬된 receptacle tuple, 정렬된 goal별 item tuple의 사전순이다.
이 binding은 선택에만 쓰며 원본 existential class goal을 ground goal로 바꾸지 않는다.

이는 전체 multi-goal route의 최적화가 아니다. Goal 사이 이동·수행 순서·pick/place 비용을
무시하고 매 goal마다 초기 agent 거리를 더한다. 이미 만족된 goal도 같은 proxy로 처리한다.
이 한계를 사후 결과에 맞춰 수정하지 않는다. 기존 b0 quota와 동일 closure를 적용하되
closure 후 object 수는 위치/containment에 따라 달라질 수 있다.

기존 test40–45에 새 condition `goal_b0`만 여섯 번 실행한다. Planner/image/seed/제한은
수정된 v2와 같고 이전 baseline 결과를 read-only로 재사용한다. Selection은 baseline plan을
읽지 않는다. 기존 output hash 보존, 기존 selector의 closure 결과 재현, 거리의 독립 공식,
distinct assignment의 완전 열거, VAL와 별도 replay를 검산한다. 새/기존 plan의 양방향
transfer로 search와 선택의 영향을 진단하며 추가 planner 호출은 하지 않는다.

Run ID `20260918_goal_v1`; output `runs/q4-planning/20260918_goal_v1/observation/`.
Status: `completed`. 새 code는 read-only mount하며 기존 image를 immutable ID로 썼다.
준비 단계 wall budget 300초, planning 각 60초, 검산/분석 각각 300초다. 입력 source, quota,
proxy 또는 condition을 관찰 후 바꾸지 않는다. 이미 본 여섯 문제의 탐색이며 held-out
일반화·optimal plan·learned selection 필요성의 증거로 쓰지 않는다.

## Goal-conditioned Observation 2026-09-18

**사실:** 새 `goal_b0` 여섯 조건을 모두 완료했고 원본 full/pruned state 양쪽에서 6/6
valid다. 기존 baseline은 v2 결과를 재사용했다. 같은 문제·선택 전 quota·closure·planner
설정이며 새로운 held-out 결과가 아니다. Compact 수치와 검산은 [goal_results.json](goal_results.json),
전체 plan transfer는 raw output `summary.json`에 있다.

| Problem | Nearest b0 proxy → Goal b0 proxy | Nearest b0 actions | Goal b0 actions | SCRUB actions |
| --- | --- | --- | --- | --- |
| 40 | 44 → 38 | 70 | 48 | 38 |
| 41 | 45 → 45 | 118 | 118 | 110 |
| 42 | 68 → 56 | 72 | 65 | 67 |
| 43 | 33 → 33 | 51 | 71 | 79 |
| 44 | 55 → 53 | 88 | 64 | 78 |
| 45 | 52 → 42 | 67 | 50 | 55 |
| Mean actions, n=6 | — | 77.7 | 69.3 | 71.2 |

Goal b0는 Nearest b0보다 4개 짧고 1개 같고 1개 길다. 평균 차이는 −8.33 actions다.
SCRUB보다 4개 짧고 2개 길며 평균 차이는 −1.83 actions다. 같은 자료로 설명을 수정한
탐색적 관찰이므로 통계적 우월성·일반화 성능으로 쓰지 않는다. Lexical b0와는 5개 짧고
1개 길다. Proxy는 단위 navigation 거리의 합이고 실제 plan에는 manipulation도 포함된다.

Closure 후 PDDL objects 평균은 140.5개(Nearest b0 139.3개)다. 초기 quota는 같지만 모든
최종 state 크기를 정확히 맞춘 실험은 아니다. 새 selection 평균 약 3.72 ms, serialization/
file I/O 포함 preprocessing 약 4.28 ms, planning wall 약 0.298초다. 공통 원본 parsing은
preprocessing 밖이며 baseline은 이전 실행이다. 반복 latency나 total-system 비용 비교가 아니다.

### What the follow-up explains

- **관찰:** Proxy가 내려간 네 문제에서 이번 plan도 짧아졌다. 문제41은 선택 목록과
  canonical PDDL 자체가 이전과 같고 계획 길이도 같다.
- **반례:** 문제43의 proxy optimum은 기존과 같은 33인데 사전 고정 lexicographic tie로
  bottle 하나가 `item36`에서 `item33`으로 바뀌어 plan은 51→71이 됐다. 같은 proxy가
  같은 plan quality를 보장하지 않는다. 기존 51-action plan은 제외된 object/location을
  참조해 새 state에서 실행 불가다. 새 state의 최단 계획이 더 길다는 증거는 아니다.
- **탐색 영향의 직접 증거:** 문제40의 SCRUB 38-action plan은 새 Goal state에서도
  VAL/replay를 통과하지만 새 planner output은 48 actions다. 남은 10 actions 차이를
  필요한 instance 부족으로 설명할 수 없다.
- **반대 방향의 증거:** 새 여섯 plan은 모두 SCRUB state에서 실행 가능하다. 특히
  문제42–45의 더 짧은 새 plan도 가능하므로, 이 네 문제에서 SCRUB의 더 긴 output을
  더 높은 optimal cost나 불충분한 정보로 해석할 수 없다.

**에이전트 해석:** 목표까지의 이동을 고려한 단순 선택이 이번 비용 차이의 일부를
설명했다. 그러나 additive proxy는 multi-goal 경로 순서·binding 후 실제 search를
충분히 설명하지 못한다. Proxy 최적화 성공을 planning optimum으로 바꾸거나, 그 잔차를
곧바로 새 learned module의 필요성으로 읽지 않는다. 선택된 binding은 원래 class goal을
제약하지 않으므로 planner가 다른 binding/순서로 해결할 수 있다.

관찰 직후 Q4는 `under_review`를 유지했다. 당시 다음 TODO는 이 관찰과 직접 선행을 비교해 추가 투자의
정보 가치와 Q3 대비 우선순위를 정하는 것이다. 이번 결과만으로 새 학습·같은 slice 확대·
hypothesis/paper 승격을 선택하지 않았다.

### Follow-up investment decision

직접 선행·정보 가치·준비 비용의 [후속 비교](../../related_work/policy-geometry.md#q4-follow-up-investment-review-2026-09-18)를
완료해 현재 fully observable instance-selection 경로를 `deferred`로 판단했다. Problem43의
optimal/search gap은 여전히 미해결이고 bounded optimal 대조도 가능하지만 지금은 추가
실행하지 않는다. 기존 관찰을 세분화하는 것보다 Q3의 fixed-control timestep 관찰을 우선한다.
Q4 전체의 반증이나 횟수 제한에 따른 종료가 아니다. [재검토 조건](../../questions/task-relevant-spatial-state.md#investment-decision-and-re-entry)을
남기며 결과·입력·image를 보존한다. 이번 투자 비교에서 새 수치 실행·container 생성/삭제는 없다.

### Follow-up verification and recovery

- 기존 reference의 **447개 파일**과 source PDDL 24개의 SHA256/bytes를 대조했다.
  공통 closure 추출 뒤 기존 Lexical/Nearest b0/b1 **24조건의 PDDL와 selection metadata**가
  이전 결과와 정확히 일치했다.
- BFS와 독립 room-center/Floyd 공식의 거리 **30,670개**가 일치했다. Selector의 dynamic
  programming 결과를 별도 완전 열거 **6,254개 assignment**로 대조해 objective와
  deterministic tie를 확인했다. 이 수에는 기존 Nearest 선택 집합의 proxy 검산이 포함된다.
- 여섯 plan의 full/pruned VAL와 독립 transition replay가 일치했고 **8,052개**
  precondition/goal 검사를 통과했다. 최종 class goal와 instance witness 불일치는 없다.
  모든 quota·goal·subset·round trip과 planner option 일치도 확인했다.
- Nearest/SCRUB과 새 plan의 양방향 **24회 transfer**를 VAL/replay로 대조했다.
  이들은 추가 planner 호출이 아니다. 공유 PDDL tokenizer의 한계와 physical semantics
  검증이 아니라는 경계를 유지한다.
- 새 raw output **113개 파일**을 manifest로 보존한 뒤 이번 run의 종료 container **4개**만
  exact creation receipt·mount·image·command·log를 확인하고 삭제했다. 입력·image·이전
  run과 다른 container는 유지했다. 외부 backup을 확인한 기록은 아니다.

실행한 host orchestration 명령(각 stage 내부는 Docker):

```bash
bash buildup/robotics/pilot_studies/q4-planning/goal_run.sh 20260918_goal_v1
python3 buildup/robotics/pilot_studies/q4-planning/cleanup.py --run-id 20260918_goal_v1
```

첫 명령은 tmux job에서 `goal_prepare → run → goal_verify → goal_analyze`로 실행됐다.
네 stage 모두 exit 0이며 각 생성 명령·image inspect·로그는 run의 `containers/` receipt에
있다. Job log는 `logs/20260918_110000_q4_goal_job.log`, cleanup log는
`logs/20260918_110124_q4_cleanup.log`다. 외부 zsh wrapper가 예약 변수 `status`를 사용해
aggregate exit 파일은 만들지 못했으며 완료 판단은 보존된 네 stage의 exit/receipt를 따른다.
재실행에는 새 run ID를 쓰고 `goal_run.sh`를 Bash에서 호출한다. 바깥 wrapper가 필요하면
예약 변수가 아닌 `q4_job_rc`로 종료 상태를 보존한다. 기존 출력은 덮어쓰지 않는다.

## Preservation and Cleanup

Compact result: [results.json](results.json). Image, paths, digest와 exact cleanup 기록:
[artifacts.json](artifacts.json). Raw output은 `runs/q4-planning/20260918_v2/observation/`의
447개 파일이며 `output_manifest.json`에 bytes/SHA256을 기록했다. 진단 전 428개 파일이
그대로 유지됐는지도 확인했다. Failed v1과 모든 생성/inspect receipt, 로그를 보존한다.
Git에는 raw PDDL/plan/trace가 자동 전달되지 않으므로 full result 이전에는 별도 복사 후
manifest를 대조한다. 외부 backup을 검증한 기록은 아니다.

결과·로그·code/environment와 mount 보존을 확인한 뒤 이번 생성 기록이 있는 종료 container
10개만 exact ID로 삭제했다. Image, dataset과 다른 작업의 container는 그대로다.

추가 사후 검산·보존 명령:

```bash
python3 buildup/robotics/pilot_studies/q4-planning/orchestrate.py diagnose --run-id 20260918_v2
python3 buildup/robotics/pilot_studies/q4-planning/orchestrate.py finalize --run-id 20260918_v2
python3 buildup/robotics/pilot_studies/q4-planning/cleanup.py
```

위 명령은 이번 실행 기록이다. 기존 run/output을 재사용해 덮어쓰지 말고 재현에는 새 run ID를
사용한다. Cleanup은 해당 두 run의 creation receipt와 현재 상태를 다시 검사하는 코드이며
다른 container에 이름만 대입해서 쓰지 않는다. Image 재build는 Dockerfile과 별도 새 tag를 쓴다.
