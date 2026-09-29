# Reward Shaping and Dynamics Observation

Updated: 2026-09-22

## Purpose and status

Q15의 [선택한 관찰](../../questions/reward-dynamics-transfer.md#first-observation)을 실행한다.
탐색이며 새 reward method나 sim-to-real 성능 주장이 아니다. Status: completed and independently verified; `refine`.
Protocol은 결과를 보기 전에 정한 question record를 따른다. Implementation 수정과 실제
학습/평가·검산 결과는 이 파일에 누적한다.
첫 관찰 이후의 [투자 비교](../../related_work/policy-geometry.md#q15-follow-up-investment-2026-09-18)에서
아래 joint-position hold 관찰을 선택했다. 이후 [576회 실행·독립 검산](#hold-results-2026-09-22)을
완료했으며 현재 reward-selection/hold 경로의 추가 투자는 `deferred`다.

## Runtime and recovery

Source: workspace의 `external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8/`.
새 image `research3-q15-reward:v1`을 official Python base에서 빌드한다. 외부/기존 simulator
image는 사용하지 않는다. Dependency constraints는 `requirements.lock`, 실제 설치와 OS
package는 build가 저장하는 `/recipe/installed.lock`, `/recipe/os-packages.lock`을 보존한다.
Source immutable URL/SHA256은 ../../related_work/comparison_sources.json의 Q15 selection을 따른다.

Repository root에서 host stdlib orchestration으로 실행한다:

```bash
python3 buildup/robotics/pilot_studies/q15-reward/job.py build
python3 buildup/robotics/pilot_studies/q15-reward/job.py ready ready_v1
python3 buildup/robotics/pilot_studies/q15-reward/job.py run v1
python3 buildup/robotics/pilot_studies/q15-reward/job.py verify v1
python3 buildup/robotics/pilot_studies/q15-reward/job.py cases v1
```

각 명령은 별도 background process로 실행하고 exact command, image ID, working directory,
mount, container inspect와 status를 `runs/q15/reward/jobs/`에 기록한다. Timestamped log/exit는
`logs/*_q15_*.log/.exit`다. All method imports/training/evaluation/verification are in Docker.
GPU는 explicit device 0, CPU 검산은 GPU 없이 수행한다. Study source는 `/study:ro`,
`runs/q15/reward/`는 `/output:rw`, 별도 cache는 container user home에 mount한다.
`cases`는 검산을 통과한 기존 trace의 사후 실패 분석이며 새 학습/rollout은 없다.
`run`과 `cases`는 기존 출력을 덮어쓰지 않는다. 새 관찰은 별도 attempt를 쓴다.

예상 출력: 9 fits의 checkpoint 18개·training logs/config, 72 evaluation traces/metadata,
원본 state 기반 독립 verification, episode table, summary 및 artifact manifest.
Ready는 reward/물성/원본 parity와 training adapter를 검사하는 작은 기술 대조다.
Run budget: 각 fit 20분·총 training 3시간, evaluation/verification 1시간. Build는 별도다.
결과 선택을 위해 실패한 seed를 다른 seed로 바꾸지 않는다.

## Preservation and cleanup

결과 해석에는 compact summary/verification과 raw evaluation state가 필요하다. 재평가에는
checkpoint/config/source/runtime이, 전체 재학습에는 pinned source/recipe/seed가 필요하다.
`runs/q15/`의 raw traces/checkpoints/cache는 ignored payload이며 외부 backup은 미검증이다.
보존 확인 뒤 생성 기록·workspace mount·image·명령·label이 일치하는 이번 종료 container만
개별 삭제한다. 다른 container와 image에는 손대지 않는다.

Build log: `logs/20260918_135306_663399_q15_build.log`. Initial build tag had a recipe-copy
typo (`research3-q15-timestep:v1`); the newly built image received the intended
`research3-q15-reward:v1` tag; only the mistaken alias was removed after verifying both tags had the same ID.
The exact correction/removal is recorded in the build job.

## Implementation corrections

첫 readiness에서 원본/보상 variant의 물리·관측 parity와 물성 7조건 검사를 통과했다.
이후 constructed reward formula의 dummy agent에 `tcp_pose` 속성이 없어 실패했다.
누락 속성만 추가했으며 simulator/reward/policy 코드는 바꾸지 않았다. 기존 probe trace의
hash를 검증해 재사용하고 formula와 아직 실행하지 않은 training smoke만 이어서 검사한다.
실패 로그는 `logs/20260918_140257_065793_q15_ready.log`에 보존한다.

Readiness retry: `logs/20260918_140506_694573_q15_ready.log`; passed original/variant
state parity, seven material configurations, 24 constructed reward cases and two PPO updates.
Compact preparation record: [readiness.json](readiness.json).
Main run: `logs/20260918_140535_277414_q15_run.log`, output `runs/q15/reward/v1/`.
Readiness seed 909 and scripted probes are excluded from the 9-fit / 2,304-episode result.

Built image ID: `sha256:3ae1cf37d7c199cf6e78f521e44b2596f834e2c6a4e4e9a136915b18e11cb17a`. The intended Q15 reward tag retains this image; the initial typo alias was removed.

## Verified preparation

Original environment and native/no-grasp/half-scale variants had identical scripted probe states,
observations, actions and native labels; native reward was identical too. The cube mass is
0.064 kg and becomes 0.128 kg with twice the inertia at unchanged geometry/COM. Cube static
and dynamic friction change from 0.3 to 0.15, while finger materials remain 2.0 and table 0.3.
SAPIEN 3.0.2 does not expose the combine-mode properties used by this inspection; effective
contact friction is not inferred to be halved. Raw per-body values are in the readiness metadata.

First completed fit's 195 updates / 9,984,000 transitions, two checkpoint hashes/step counts,
and 64 captured reward samples passed independent container-side reconstruction. Record:
`logs/20260918_141358_q15_first_fit_verify.log`. This is an early artifact check; full cohort
verification follows the remaining fits/evaluation. Readiness containers were removed only after
outputs/logs/launch metadata were preserved. 아래 최종 기록이 이 중간 상태를 대체한다.

## Reading the results

첫 full-cohort 검산은 training audit의 robot-static 대조에서 중단됐다. 검산기가 원본
Panda의 `max(abs(qvel[:-2])) <= 0.2` 대신 L2 norm을 사용한 오류였다. Native evaluator와
학습·평가 adapter는 원본 판정을 사용했으며 변경하지 않았다. 실패 검산 source는
`v1/verification_source_failed_static_l2/`, 로그는
`logs/20260918_151757_542531_q15_verify.log`에 보존한다. 검산기의 static predicate만 원본에
맞추고 재실행한다. Dense reward의 static shaping은 원래 L2 norm을 쓰므로 유지한다.
Episode table에는 L2 norm과 최대 절대 관절 속도를 구분해 저장한다.

두 번째 검산은 training 대조를 통과한 뒤 fractional filename 조회에서 중단됐다.
v1 writer의 `Path.with_suffix`가 `f0.5`의 `.5`를 extension으로 처리해 JSON/NPZ를
`f0.json/.npz`로 저장했다. 72개 trace/metadata는 모두 있으며 metadata의 friction 값은
0.5다. 원본 파일을 보존하고 검산기가 이 경로를 명시적으로 읽되 각 파일의 고유성·물성·
checkpoint/hash를 확인한다. 이후 writer는 extension을 붙이는 방식으로 수정했다.
실제 v1 실행 source와 실패 verifier 두 버전은 raw output에 보존하며 재학습·재평가는 없다.
두 번째 실패 로그: `logs/20260918_151918_167233_q15_verify.log`.

각 표의 한 cell은 training seed 3개 × 공통 초기 상태 32개다. 합산 96회는 기술 통계이며,
독립 학습 반복은 reward마다 3개다. 두 checkpoint도 같은 학습에서 나왔으므로 별개의
반복으로 세지 않는다. Seed별 성공 수와 nominal에서 성공했지만 shift에서 실패한
동일 초기 상태를 함께 보존한다.

물성 변경에 따른 감소는 각 policy의 nominal 결과와 비교한다. Reward 간 절대 성공률
차이만으로 transfer robustness를 판정하지 않는다. Half-scale 대조와 중간/최종 변화는
최적화에 대한 제한된 대조이며 모든 reward scaling이나 수렴 설명을 배제하지 않는다.
동일한 것은 환경 transition 예산과 PPO 설정이다. 원본의 `target_kl=0.1` 조기 중단을
유지하므로 `update_epochs=8`은 상한이며 실제 gradient update 횟수가 같다는 뜻은 아니다.
`left_after_success`, `placed_nonstatic`, `goal_not_reached_at_end`는 저장된 native
predicate에 따른 결과 분류다. Grasp flag의 빈도만으로 접촉력·grasp 품질이나 실패의
인과 기전을 확정하지 않는다.

## Results 2026-09-18

9 fits × 9,984,000 transitions를 완료하고 고정된 checkpoint 18개를 모두 평가했다.
총 72 conditions / 2,304 episodes다. Training wall time은 3,975.69초(66.26분), evaluation은
361.18초(6.02분)였다. 각 fit은 428.30–452.63초로 상한 안에 있었다. 검산 재시도와
사후 분석을 포함해 evaluation/verification 1시간 예산을 넘지 않았다.

다음은 `success_at_end` 수이며 각 cell의 분모는 **96**이다. Density는 geometry를 유지한
mass/inertia의 동일 배율, friction은 cube material의 배율이다.

| Reward | Update | Nominal | Density ×2 | Friction ×0.5 | Both |
| --- | ---: | ---: | ---: | ---: | ---: |
| Official normalized dense | 97 | 79 | 81 | 82 | 79 |
| Without grasp bonus | 97 | 88 | 87 | 89 | 89 |
| Half scale | 97 | 65 | 66 | 65 | 65 |
| Official normalized dense | 195 | 86 | 89 | 86 | 89 |
| Without grasp bonus | 195 | 94 | 92 | 95 | 93 |
| Half scale | 195 | 93 | 94 | 94 | 94 |

최종 checkpoint의 seed별 수는 다음과 같다. Tuple 순서는 seeds 101/202/303이고 각 수의
분모는 32다. 중간 checkpoint의 seed별 결과도 [summary.json](summary.json)에 모두 남겼다.

| Reward | Nominal | Density ×2 | Friction ×0.5 | Both |
| --- | --- | --- | --- | --- |
| Official normalized dense | 32 / 24 / 30 | 32 / 27 / 30 | 32 / 25 / 29 | 32 / 28 / 29 |
| Without grasp bonus | 32 / 31 / 31 | 31 / 31 / 30 | 32 / 32 / 31 | 32 / 31 / 30 |
| Half scale | 30 / 32 / 31 | 31 / 32 / 31 | 31 / 32 / 31 | 31 / 32 / 31 |

**관찰 사실:** Nominal에서 중간→최종 성공은 native 79→86, no-grasp 88→94,
half-scale 65→93이다. 특히 half-scale seed 303은 5→31/32로 변해 학습 시점의 영향이
크다. 최종 no-grasp와 half-scale의 차이는 조건별 1–2건이며 우세 방향도 바뀐다.
Native 대비 두 대조의 이점은 nominal에서도 존재한다.

각 policy의 최종 nominal 대비 shifted 조건의 합산 변화는 native 0~+3건,
no-grasp −2~+1건, half-scale +1건이다. 같은 초기 상태의 성공 소실/획득을 직접 비교하면
native의 density-only는 0/3, friction-only는 1/1, joint는 1/4건이다. No-grasp는 각각
2/0, 0/1, 1/0건이며 half-scale은 세 조건 모두 0/1건이다. 따라서 더 높은 shifted
성공률만 보고 grasp bonus 제거가 물성 변화에 더 강하다고 해석하지 않는다.

### Failure inspection

최종 1,152회 중 실패 53건을 전부 기존 state trace에서 사후 분해했다.
[cases.json](cases.json)은 각 실패의 초기 상태, seed, 최초/마지막 성공 step, 최종
goal 거리·최대 절대 관절 속도·grasp flag와 trace hash를 보존한다.

- Nominal native는 `success_once=95/96`, `success_at_end=86/96`이다. 성공 후 실패로
  바뀐 9건 중 seed 202의 8건은 마지막에도 grasp/static 판정을 만족하지만 goal 거리
  25.184–36.945 mm로 원본 25 mm 범위를 벗어났다. 단순 grasp 소실로 설명되지 않는다.
- 같은 seed/state 중 202/7은 step 49까지 성공했으나 step 50에서 25.184 mm로 실패했다.
  202/14는 마지막 성공이 step 37이고 최종 36.945 mm다. Threshold와 종료 시점을 조정해
  성공으로 재분류하지 않았다. 이것은 물체의 이탈 원인을 확정하는 분석은 아니다.
- Nominal no-grasp는 once/end가 모두 94/96이고, half-scale은 95/93이다. No-grasp의
  남은 두 실패는 마지막 grasp flag도 false다. Half-scale은 goal 안의 nonstatic 1건과
  성공 후 goal 밖으로 나간 2건이 있다. Reward별 실패 구성이 다르지만 scale 대조도
  native의 상당수 실패를 피하므로 특정 shaping 항의 고유 효과로 단정하지 않는다.
- Nominal 최종 grasp flag 비율 평균은 native 0.8723, no-grasp 0.8581, half-scale 0.8744다.
  Reward에서 bonus를 제거해도 observation과 placement gate에는 grasp 정보가 남는다.
  이 빈도는 접촉력/실제 grasp 품질의 검증값이 아니다.

### Verification and preservation

수정 후 [verification.json](verification.json)의 검산을 통과했다. Raw-state label 345,600개,
평가 reward 115,200개, training reward sample 576개, 초기 상태 배열 576개를 대조했다.
18개 checkpoint의 hash/step과 실제 물성·불변 robot/table 설정도 확인했다. 실패한 최초
검산의 L2 static 가정은 training sample 14개와 평가 step 6,530개의 static 판정에서
원본과 달랐다. 최종 수치는 원본의 max-absolute 판정과 전부 일치한다.

최종 검산 로그: `logs/20260918_152028_145317_q15_verify.log`.
실패 분석 로그: `logs/20260918_152154_280535_q15_cases.log`.
Raw manifest 345개 entry와 사후 분석 source/result manifest를 SHA256/size로 확인하고
compact result·episode table·runtime·dependency locks를 이 폴더에 복사했다. `source/`는
실제 학습/평가 당시 코드이며 `verification_source/`는 수정된 최종 검산 코드다.
Background `finish`의 첫 시도는 검산 오류로 중단됐고, 수정 후 별도 job으로 검산·보존·
정리를 완료했다. 이전 실패 log/source는 보존한다.

`logs/20260918_152242_q15_cleanup.log`에 정리 전 생성 기록·mount·image·command·파일
보존을 기록했다. 이번 종료 run/verify/cases container 5개만 개별 삭제했고, 앞서 정리한
readiness 2개를 포함해 총 7개다. Image, raw state, checkpoint, cache와 다른 작업의
container는 유지했다. Raw payload의 외부 backup은 아직 검증하지 않았다.

## Interpretation and next decision

**에이전트 판단: `refine`.** Reward 변경에 따른 학습 진행과 최종 행동 차이는 관찰했지만,
grasp bonus 제거만의 transfer robustness 이점은 지지하지 않는다. Half-scale 대조가
최종 성능을 대부분 따라잡고, 시험한 물성 변경은 큰 공통 성능 하락을 만들지 않았다.
따라서 이번 결과로 robust reward-selection method의 필요성이나 새 원리를 주장하지 않는다.

남은 설명은 성공 후 목표 위치 유지, reward scale에 따른 최적화, 학습 진행도/seed 차이다.
이후 이 사례와 직접 선행을 대조해 **작은 추가 관찰의 정보 가치**를 검토했고 아래
joint-position hold 대조를 선택했다. 같은 grid/seed나 DR/PBRS 전체 구현으로 확대하지 않는다.
실패가 나온다는 사실이나 위 검산기 수정 자체를 novelty로 쓰지 않으며 hypothesis/paper로
승격하지 않았다. Sim-to-sim 단일 과제 관찰이라는 범위는 유지한다.

## Joint-position hold observation

Selected: 2026-09-18. Status: completed and independently verified, 2026-09-22. 첫 관찰과 53건의 실패 분석을 본 뒤
정한 exploratory intervention이다. 기존 결과·threshold·분모는 수정하지 않는다.

### Question and comparison

**성공 후에도 학습 정책을 계속 실행할 때 나타나는 목표 이탈을, 재학습 없이 단순한
joint-position hold로 피할 수 있는가?** 이 비교는 reward가 왜 그 정책을 학습시켰는지를
식별하는 실험은 아니다. 성공한 동일 상태에서의 실행 제어 선택이 현재 실패를 바꾸는지
확인해 추가 학습의 필요성을 판단한다.

- 기존 세 reward × 세 seeds의 **최종 update 195 checkpoint 9개 전부**를 사용한다.
  `runs/q15/reward/v1/fits/{native,no_grasp,half}_{101,202,303}/checkpoint_195.pt`와
  해당 metadata/hash가 입력이다. 중간/best checkpoint나 실패 seed만 선택하지 않는다.
- Nominal density/friction만 사용한다. 기존 reset seed `2026091901`과 32 initial states,
  Panda/state/`pd_joint_delta_pos`, physics 100 Hz/control 20 Hz, horizon 50 steps를 유지한다.
- 두 route: **continued policy**와 **joint-position hold after first success**.
  각 route를 처음부터 별도로 실행하며, 기존 trace에서 상태만 복원한 것처럼 취급하지 않는다.
  두 route 모두 첫 native success까지 같은 frozen policy를 deterministic하게 실행한다.
- 총 **9 checkpoints × 2 routes × 32 initial states = 576 episodes**다. Reward당 독립
  학습 반복은 기존 3개뿐이며 새 학습은 없다. 이미 본 상태를 재사용하므로 held-out 검증이 아니다.

### Exact intervention

Control step `tau`의 원본 `success`가 처음 true이면 그 step 종료 후 실제 arm joint
position `q_hold=qpos[tau,:7]`과 그때까지 적용한 gripper action을 저장한다. `tau+1`부터
step 50까지 다음 규칙을 적용한다. 한번 전환하면 success가 false가 돼도 되돌아가지 않는다.
성공하지 않은 episode는 끝까지 원래 policy를 실행한다. Step 50에서 처음 성공한 경우
후속 action이 없으므로 별도 표시한다.

Pinned controller와 실제 v1 config는 arm에 `use_delta=True`, `use_target=False`,
normalized range `[-0.1,0.1] rad`, `interpolate=False`를 사용한다. 따라서:

```text
continued policy: a_arm = clipped frozen policy output
hold:             a_arm = clip((q_hold - current_qpos[:7]) / 0.1, -1, 1)
                  a_gripper = gripper action applied at first success
actual target:    current_qpos[:7] + 0.1 * a_arm
```

즉 매 step의 zero delta는 움직인 현재 위치를 다시 target으로 삼으므로 고정 reference와
같지 않다. 반복해서 내는 action도 동일한 absolute target을 뜻하지 않는다. Gripper는
원래 absolute-position mimic controller이므로 성공 시 command를 유지한다. Arm/gripper의
gain, force limit, mode와 physics는 바꾸지 않는다. 이 비교는 두 command를 함께 고정하므로
arm과 gripper 각각의 독립적인 원인 효과로 해석하지 않는다.

Action clipping이 발생하면 requested reference와 actual target의 차이·포화 횟수를
기록한다. 해당 episode를 버리지 않으며 고정 reference가 정확히 구현된 범위와 제한된
servo action의 결과를 구분한다. 목표 오차를 본 뒤 hold 위치를 옮기거나 gain을 조정하지 않는다.

### Readout and validity

주 readout은 두 route의 원본 `success_at_end`와 초기 상태별 paired 개선/악화다.
Reward/seed별 결과를 유지한다. First-success 전환 수, 남은 step 수, 성공 후 지속 여부,
goal 거리·arm 최대 절대 속도·grasp·cube-to-TCP 상대 운동을 보조로 읽는다. 조건부 유지율은
같은 policy의 paired route 사이에서 해석하며 reward마다 다른 성공 상태 집합을 같은
모집단으로 간주하지 않는다.

최소 검사는 다음 구현 작업에 묶는다:

1. Checkpoint identity, 초기 상태와 전환 전 observation/action/state/native label의 일치를
   확인한다. Prefix가 다르면 해당 pair의 인과 해석을 멈추고 차이와 구현/재현성 원인을 기록한다.
2. 실제 controller target을 기록해 고정 reference 또는 명시된 clipping과 일치하는지
   확인한다. Source를 읽었다는 사실만으로 runtime hold 성공을 가정하지 않는다.
3. 원본 goal/static/success를 raw state에서 별도로 계산한다. Static은
   `max(abs(qvel[:7])) <= 0.2`, goal 거리는 `<= 0.025 m`다. 원본 reward도 유지한다.
4. Continued-policy 결과를 기존 nominal trace와 대조한다. 재현 차이가 있으면 보존하고
   새 paired run의 효과와 분리한다. 기존 점수를 맞추기 위해 threshold/seed를 바꾸지 않는다.

### Cost, artifacts and decision branches

Source와 기존 workspace 소유 Q15 image/recipe 및 checkpoint를 활용할 수 있다. Input은
read-only로 mount하고 새 raw output은 `runs/q15/reward/hold_v1/`에 둔다. 실제 command,
image ID, mounted paths, source snapshot과 timestamp log는 구현·실행 때 이 owner에
추가한다. 이번 검토에서는 container 생성/실행/삭제나 numerical experiment를 하지 않았다.

계획 추정은 준비 약 0.5–1 작업일, 전체 GPU rollout 15분·CPU 검산/정리까지 1시간 상한이다.
기존 72조건 평가의 약 6분을 비용 기준으로 삼았지만 새 adapter의 실행 시간은 아직 측정하지
않았다. 상한 초과/불일치는 부분 기록과 원인을 보존하고 자동 재학습으로 우회하지 않는다.

- Hold로 현재 실패가 줄면 먼저 단순 실행 제어로 충분한 범위를 기록한다. 새 reward method의
  필요성은 약해지며 hold 자체를 contribution으로 쓰지 않는다.
- Hold에서도 실패하거나 새 실패가 생기면 relative motion·target tracking·전환 시 상태로
  다음 설명을 좁힌다. 불가피한 물리 실패, 안정성 보장 실패 또는 reward 원인으로 단정하지 않는다.
- 차이가 작거나 이미 알려진 설명의 반복이면 현재 경로를 보류하고 다른 질문과 재비교한다.
  효과가 나올 때까지 같은 grid/seed를 늘리지 않는다.

Native success를 쓰는 oracle-assisted diagnostic이며 deployable success detector가 아니다.
Nominal에서의 유한 horizon 비교는 일반적인 reach-and-stay 보장, 물성 transfer robustness,
VLA/real-robot 일반성을 검증하지 않는다. RAS/DR/PBRS 전체 재현은 이번 범위에 포함하지 않는다.

### Execution 2026-09-22

Status: completed and independently verified. 위 2026-09-18 설계와 576회 분모를 유지했다.
기존 workspace 소유 image ID `sha256:3ae1cf37d7c199cf6e78f521e44b2596f834e2c6a4e4e9a136915b18e11cb17a`를
사용한다. 작업 디렉토리는 `/home/yoohyun/research3`이며 명령은 다음과 같다.

```bash
python3 buildup/robotics/pilot_studies/q15-reward/hold_job.py run hold_v1
python3 buildup/robotics/pilot_studies/q15-reward/hold_job.py verify hold_v1
python3 buildup/robotics/pilot_studies/q15-reward/hold_job.py diagnose hold_v1
python3 buildup/robotics/pilot_studies/q15-reward/hold_cleanup.py hold_v1
```

Run/verify/diagnose는 별도 background worker로 실행한다. `/input:ro`는 `runs/q15/reward/v1/`,
`/output:rw`는 `runs/q15/reward/hold_v1/`, `/study:ro`는 이 study source다.
별도 workspace cache `runs/q15/reward/cache/`를 `/home/research:rw`로 사용한다.
GPU run은 device 0, CPU 검산은 GPU 없이, network는 둘 다 none으로 실행한다.
Timestamped command/image/container inspection은 `runs/q15/reward/jobs/`, log/exit는
`logs/*_q15_hold_*.log/.exit`에 기록한다. GPU rollout 상한 900초, 검산 상한 3600초다.
예상 출력은 18개 trace/metadata/log, source snapshot, input manifest, 576행 episode table,
summary, independent verification과 output manifest다. 기존 v1 결과는 변경하지 않는다.

## Hold Results 2026-09-22

**사실:** 9개 최종 정책 × 두 route × 공통 32초기 상태의 576회를 모두 완료했다.
18개 fresh-process 조건 실행은 총 91.80초로 15분 상한 안에 있었다. 새 학습·물성 변경은
없으며 입력 45개 파일의 checksum을 실행 전후 대조했다. Run, CPU 검산, 사후 사례 분석은
모두 exit 0이다. [정확한 명령·image·로그](hold/runtime.json)를 보존했다.

각 row/route의 분모는 96이며 독립 학습 반복은 기존 3개다. 개선/악화는 같은 정책·초기
상태의 **종료 시 성공**을 비교한다. Seed tuple 순서는 101/202/303, 각 수의 분모는 32다.

| 학습 reward | Continued end | Hold end | 개선 / 악화 | Continued seed별 | Hold seed별 |
| --- | ---: | ---: | ---: | --- | --- |
| Official normalized dense | 86 | 93 | 8 / 1 | 32 / 24 / 30 | 32 / 32 / 29 |
| Without grasp bonus | 94 | 93 | 0 / 1 | 32 / 31 / 31 | 32 / 31 / 30 |
| Half scale | 93 | 93 | 1 / 1 | 30 / 32 / 31 | 31 / 32 / 30 |

성공을 한 번이라도 달성한 수는 두 route에서 동일하게 95/94/95다. 따라서 같은 정책 내
조건부 종료 유지 수는 native 86/95→93/95, no-grasp 94/94→93/94, half 93/95→93/95다.
Reward마다 성공 상태의 모집단이 다르므로 이 비율로 reward의 유지 능력 순위를 일반화하지
않는다. 마지막 step에 처음 성공한 사례는 없었다. 처음부터 성공하지 못한 4개 pair는
개입 없이 원래 동작을 유지했다. [전체 요약](hold/summary.json), [576행](hold/episodes.csv).

### Verification

- 288개 pair 전부에서 초기 상태와 첫 성공까지 observation/action/state/label이 정확히
  일치했다. 9개 continued trace는 2026-09-18 nominal trace와 공통 필드 전체가 동일했다.
- Raw state의 goal/static/success 86,400개와 reward 28,800개를 CPU에서 독립 재구성했다.
  기존 threshold·horizon·분모를 바꾸지 않았다. Grasp flag는 별도 contact-force 검증이 아니다.
- Controller 설정·물성은 원래 nominal과 같았으며 실제 drive target 259,200개를 검사했다.
  Hold가 적용된 9,266 control steps에서 arm action clipping은 0이었다. 고정 reference와
  실제 target의 최대 차이는 4.66e-10 rad였다. 이는 **목표 명령** 검사이며 실제 관절 위치가
  완벽하게 고정되거나 물체가 정지한다는 뜻은 아니다.
- [독립 검산](hold/verification.json)은 rollout/policy를 import하지 않는다. Source snapshot,
  raw traces, input/output manifest와 실패 사례를 `runs/q15/reward/hold_v1/`에 보존했다.

### Improved and remaining cases

**관찰 사실:** Native seed 202의 기존 목표 이탈 8건을 모두 피했다. 이 여덟 건은 첫 성공
이후 종료까지 성공을 유지했으며 최종 goal 거리는 4.827–23.251 mm였다. 이 사례에는
추가 학습 없이 고정 joint reference와 gripper command를 적용하는 대조로 충분했다.

그러나 새 악화는 3건이다. [paired 사례](hold/cases.json)와 [기존 trace의 사후 진단](hold/diagnosis.json)에
개선 9건과 hold 종료 실패 9건의 합집합 18개를 보존했다. 사후 진단의 새 rollout은 0이다.

| 악화 사례 | 첫 성공 → hold 종료 goal 거리 | 동반 관찰 |
| --- | --- | --- |
| Native seed 303 / initial state 31 | 24.641 → 25.346 mm | Grasp/static 유지. Arm 실제 위치의 최대 변화 0.000561 rad, TCP와 cube가 작게 함께 이동. Continued는 11.485 mm로 성공. |
| No-grasp seed 303 / initial state 9 | 22.818 → 43.485 mm | Hold 종료 grasp false; TCP 좌표계에서 cube 상대 위치 변화 40.383 mm. Continued는 14.247 mm로 성공. |
| Half-scale seed 303 / initial state 14 | 23.419 → 27.062 mm | Grasp/static 유지에도 cube 상대 위치가 7.125 mm 변함. Continued는 12.198 mm로 성공. |

Hold 종료 실패 9건은 처음 성공하지 못한 4건과 성공 후 실패 5건이다. 후자에는 위 악화
3건과 두 route 모두 실패한 2건이 있다. Native seed 303/state 16은 최초 success 시점에도
grasp false였고, half seed 303/state 30은 hold 뒤 grasp를 잃었다. 원본 success는
goal와 arm velocity 기준이므로 성공 신호가 물체의 안정적 파지를 보장하지 않는다.
이 기록만으로 contact-force 원인이나 reward 학습 기전을 확정하지 않는다.

### Investment decision and preservation

**에이전트 판단: 현재 reward-selection/단순 hold 확장 경로의 추가 투자를 보류한다
(`deferred`).** 첫 관찰의 성능 차이는 scale/학습 진행도와 양립했고, 이번에는 핵심 8건을
단순 실행 제어로 피했다. 반면 hold는 세 정책군 모두에 보편적 이득을 주지 않았고 상태 유지도
보장하지 않았다. 이는 성공 신호·관절 target·물체 유지의 차이를 보여주는 제한된 관찰이며
새 reward method 또는 새로운 안정 제어 원리를 요구하는 증거는 아직 아니다.

단일 nominal task·이미 본 초기 상태·oracle trigger·2.5초 범위를 유지한다. 93/96이라는
동일 합계는 실패 사례나 세 reward의 일반적인 동등성을 뜻하지 않는다. Re-entry에는
성공 후 제어 선택이 중요한 구체적 행동 질문과, 단순 유지·더 안쪽 목표·기존 안정화/피드백
대안의 서로 다른 예측을 비교할 작은 관찰이 필요하다. 최종 novelty 증명을 진입 gate로
추가하지 않으며 같은 threshold/seed/물성 grid 확대는 자동 선택하지 않는다.

Run log: `logs/20260922_105848_874874_q15_hold_run.log`.
Verification log: `logs/20260922_110119_815984_q15_hold_verify.log`.
Case diagnosis log: `logs/20260922_110247_677571_q15_hold_diagnose.log`.
71개 artifact entry의 SHA256/size 및 compact copy를 확인한 뒤 이번 생성·종료 container
3개만 정리했다. [정리 명령](hold_cleanup.py)의 provenance 대조와 삭제 결과는
`logs/20260922_110416_q15_hold_cleanup.log`에 보존했다. Image·기존 input·새 raw output·cache와
다른 작업의 container는 유지했다. Raw output은 약 13 MiB이며 외부 backup은 미검증이다.
