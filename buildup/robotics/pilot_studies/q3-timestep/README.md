# Fixed-Control Timestep Observation

Updated: 2026-09-18

## Purpose and status

Q3의 [선택한 관찰](../../questions/physics-ranking-stability.md#selected-first-observation)을
실행한다. 탐색 연구이며 단일 정책의 수치·행동 민감도를 관찰한다. Policy ranking,
real-world fidelity 또는 새로운 method를 검증하는 실험이 아니다.

Status: completed and independently verified. Control 20 Hz, physics 100/200/400 Hz, 50 control steps, seed 20260918,
8 matched initial states, fresh-process repeats 0/1. Closed-loop PPO와 첫 100 Hz 실행의
absolute arm/gripper target replay를 비교한다. 총 96 episodes이며 독립 초기 상태는 8개다.
Mass/friction, solver, PD gains/limits와 interpolation을 고정한다. Replay에도 PD feedback은 남는다.

## Inputs and runtime

Source: `external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8`,
checkpoint: `datasets/q8/ppo_pd_joint_delta_pos_ckpt.pt` (read-only).
입력 SHA256과 immutable URL은
[source manifest](../../related_work/comparison_sources.json)의
`q4_followup_review_20260918`을 따른다. 기존 source/checkpoint만 사용하며 새 image를 빌드한다.
Dependency constraints는 성공한 workspace 실행의 버전을 기록한 `requirements.lock`이며
실제 설치 결과와 OS package 목록도 새 image에서 보존한다.

Build: repository root에서 `python3 buildup/robotics/pilot_studies/q3-timestep/job.py build`.
Run: `python3 buildup/robotics/pilot_studies/q3-timestep/job.py run`.
Verify: `python3 buildup/robotics/pilot_studies/q3-timestep/job.py verify`.
각 명령은 background process와 timestamped `logs/*_q3_*.log/.exit`를 만든다.
Exact command, image identity, working directory, mounts와 status는
`runs/q3/timestep/jobs/`의 launch record에 남긴다. GPU run은 explicit device 0,
별도 `runs/q3/timestep/cache/`, `runs/q3/timestep/` output을 사용한다.

2026-09-18 build: `logs/20260918_124419_751188_q3_build.log`; status/exit는 같은
timestamp의 launch record와 `.exit` 파일에서 확인한다. Build는 `--no-cache`이며
새 official-base image를 구성한다. 기존 workspace simulator image는 실행하거나 base로 쓰지 않는다.

Image: `research3-q3-timestep:v1`, immutable Docker ID
`sha256:3b51ec5533d6fd6bd999903a0b66938703c38fbf6ae685a4b163bdabc6b710f0`.
GPU run log: `logs/20260918_125407_767289_q3_run.log`; output: `runs/q3/timestep/v1/`.
초기 PhysX GPU library는 별도 `/cache`에 다운로드되므로 첫 run은 network를 사용한다.
GPU 실행은 download/process startup 포함 92.63초에 완료했다. 두 verify job은 CPU에서 실행했다.
최종 검산 log: `logs/20260918_125654_298780_q3_verify.log`.
Exact commands와 image, cache, output hashes는 [runtime.json](runtime.json),
설치 버전은 [installed.lock](installed.lock)과 [os-packages.lock](os-packages.lock)에 보존했다.

출력은 12 condition의 NPZ trajectories/JSON metadata, summary, verification,
dependency/OS locks와 checksum manifest다. 재실행은 `job.py run <new_attempt>`와
`job.py verify <new_attempt>`로 새 output을 사용한다. 기존 attempt는 덮어쓰지 않는다.
본 실행은 GPU wall 1시간 이내로 제한했다. Source/checkpoint는 read-only mount다.

## Results 2026-09-18

사실: 모든 mode/frequency/repeat에서 **success_at_end = success_once = 8/8**이다.
전체 96회가 성공했으나 8개 초기 상태의 반복이며 96개 독립 scene은 아니다.
최종 goal distance는 전체 7.05–14.91 mm로 원본 25 mm 기준 안쪽이었다.
기록된 물체 위치·관절 위치·drive target의 같은 조건 두 반복 차이는 0이었다.
100 Hz closed-loop reference와 같은 target replay의 해당 궤적 차이도 0이었다.

| Frequency comparison | Closed-loop cube RMS / maximum (mm) | Target-replay cube RMS / maximum (mm) | End / once outcome changes |
| --- | --- | --- | --- |
| 100–200 Hz | 2.590 / 13.100 | 1.073 / 2.661 | 0 / 0 |
| 100–400 Hz | 3.742 / 15.107 | 1.469 / 3.783 | 0 / 0 |
| 200–400 Hz | 1.414 / 5.124 | 0.452 / 1.137 | 0 / 0 |

RMS는 8개 초기 상태 × 50개 동일 control boundary에서의 cube position 거리의 RMS이며,
maximum은 그 400개 거리 중 최대다. 두 반복에서 수치가 같아 표에는 한 번만 기재했다.
Closed loop의 100–400 Hz 최대 차이는 initial state 3의 control step 10에서 관찰됐다.
이는 physical truth에 대한 오차가 아닌 두 실행 궤적 간 차이다.

## Verification and revision

- 원본 state에서 success 4,800개와 placement/static 각 4,800개를 NumPy로 재구성해
  총 14,400개 predicate가 일치했다. 초기 snapshot array 132개가 reference와 정확히 일치했다.
- GPU target buffer 43,200개 값을 controller target과 대조했고 replay target 21,600개가
  첫 100 Hz reference와 일치했다. Closed-loop target 21,600개도 원본 normalized-action
  변환과 초기 qpos로 별도 재구성했다.
- 실제 physics-step 수, 20 Hz 시간축, 50-step horizon, simulator/controller 설정,
  cube mass와 gripper material 설정이 지정한 대조와 일치했다.
- 첫 검산 뒤 joint/target RMS의 회전 관절(rad)과 gripper(m)를 분리했다. 혼합 단위의 RMS를
  물리적 크기로 해석하지 않기 위한 수정이며 cube 수치·success·raw rollout은 바뀌지 않았다.
  최초 분석은 `runs/q3/timestep/v1/analysis_v1/`에 보존했고 최종 verifier와 hash도 저장했다.

결과: [summary](summary.json), [96 episode summaries](episodes.csv),
[independent verification](verification.json). Raw NPZ/metadata와 script snapshot은
ignored `runs/q3/timestep/v1/`에 있으며 compact 결과만 이 폴더에 보존한다.

## Interpretation and next decision

에이전트 해석: 이 범위에서는 timestep 변경이 궤적과 policy target을 바꾸지만 성공 결과는
안정적이었다. Closed loop에서 더 큰 trajectory 차이는 policy/relative-target 갱신의 관여와
부합한다. Replay에도 PD feedback이 있으므로 완전한 원인 분해나 일반적인 증폭 법칙은 아니다.
또한 200–400 Hz 차이가 작다는 사실만으로 수렴·물리적 정확성을 입증하지 않는다.

관찰 직후 판단은 `refine`이었다. 이후 [직접 선행·추가 정보 가치 비교](../../related_work/policy-geometry.md#q3-investment-and-q15-selection-2026-09-18)를
완료해 현재 경로를 `deferred`로 두었다. Timestep self-consistency와 closed-loop 전파는
선행이 다루며, 이번 범위에서는 outcome 변화도 없었다. 새 method의 필요성, policy ranking
변화 또는 VLA generalization을 지지하는 결과는 아니다.

다음에는 Q15의 제한된 reward-training 관찰을 선택했다. Q3의 같은 grid 확대나 차이를
만들기 위한 seed/threshold 변경은 선택하지 않았다. 넓은 질문의 반증은 아니며
[재검토 조건](../../questions/physics-ranking-stability.md#investment-decision-and-re-entry)을 따른다.
이번 후속 검토에서는 새 rollout을 실행하거나 기존 수치·raw artifact를 변경하지 않았다.

## Preservation and cleanup

최종 결과·raw output 38개 파일의 checksum, timestamp logs와 container inspect를 보존했다.
생성 기록·workspace mount·image·실행 명령·종료 상태를 확인하고 이번 run/verify container
세 개만 삭제했다. 기록: `logs/20260918_125800_q3_cleanup.log`와 job JSON.
Image, source/checkpoint, 별도 PhysX cache와 출력은 유지한다. 기존/다른 작업 container는 건드리지 않았다.
