# Reproducibility Workflow

Updated: 2026-09-11

## Non-Negotiable Rules

- Paper, baseline, adapter, simulator, detector, smoke/evaluation은 Docker-only다.
- Host에서는 Markdown/source/Dockerfile 편집, Docker orchestration, download, checksum/manifest/log audit만 한다.
- Docker 실패를 host execution으로 우회하지 않는다.
- Pre-existing host image/container/volume/cache/simulator는 모두 read-only이며 research
  runtime으로 사용하지 않는다. 새 workload마다 workspace-owned Dockerfile/compose,
  고유 이름과 별도 cache/output root를 만든다.
- 기존 Docker 자산에 대한 `run`, `tag`, `commit`, `rm`, `rmi`, `prune` 또는 내용
  변경은 사용자 승인 없이는 금지한다.
- Dataset/source는 가능하면 read-only mount하고 derived output을 분리한다.
- GPU workload는 explicit `--gpus`와 device/mode를 기록한다.

## Required Run Record

- Dockerfile 또는 immutable image tag/digest
- source commit과 dependency lock
- build/run command, mount, working directory
- CPU/GPU mode, seed, split/manifest
- allowed input, evaluation-only input, leakage boundary
- output path와 independent verification command

## Current Data State

Q12 checkpoint/model 준비의 새 CPU image, source adapter와 command는
[model README](../buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md)가 소유한다.
Checkpoint strict loading 후 frozen CPU reference를 실제 네 입력에 실행했고 독립 NumPy
verifier와 post-run byte audit을 통과했다. 같은 owner가 source/환경 freeze, 실제 result/audit,
output hash manifest와 실행·재검사 command를 소유한다. Native CUDA parity와 물리 연결은
미검증이다. 기존 input v1 및 schema/준비 artifact는 보존한다. 실제 NPZ·raw result는
`runs/q12_completion_reference_v1/`에 별도 보존하며 전체 재현에는 checkpoint·입력과 image/recipe도
필요하다. 정확한 output 목록·검증·복구 명령은 model README를 따르며 삭제·외부 전송은 없다.

Q12 입력 준비의 download 한도·원본/선택 파일·복구 command는
[study README](../buildup/robotics/pilot_studies/q12-generated-geometry/README.md)가 소유한다.
`datasets/q12/`의 original ZIP/model·inner archives·선택 XYZ는 취득·checksum 검증을 완료했다.
Frozen v1은 selected XYZ만 read-only mount해 실제 입력 검사·독립 검증을 완료했다. 원본은
`runs/q12_input_v1/data/`와 `runs/q12_input_v1_audit/`, compact result/verification과 실행
manifest는 study에 있다. 같은 workspace CPU image와 frozen source를 유지했고 model
loading/inference는 하지 않았다. 결과 보존에는 sampled XYZ·원본 results·독립 receipt가,
전체 재현에는 pinned raw inputs와 image/recipe/locks가 필요하다. 복구 시 study의 hash와
Drive mutable-content 경계를 따르며 외부 사본 검증·삭제는 하지 않았다.

Q13의 source/metadata 복구는 [source manifest](../buildup/robotics/related_work/q13-sources.json)와
[Stage 4 기록](../buildup/robotics/related_work/policy-geometry.md#source-and-artifact-evidence)이 소유한다.
Pinned source URL의 byte length/SHA-256을 확인해 재취득할 수 있다. `/tmp/` cache 경로와
HF revision, Drive/Box page 접근 경계는 manifest를 따른다. Weight·dataset payload를
받거나 실행한 기록이 아니며, 공개 링크의 HTTP 200을 payload 검증으로 대체하지 않는다.

Q12의 read-only source/metadata 복구 정보는
[source manifest](../buildup/robotics/related_work/q12-sources.json)와
[Stage 4 기록](../buildup/robotics/related_work/policy-geometry.md#read-only-source-evidence)이 소유한다.
Manifest의 pinned URL로 source text를 다시 받아 byte length/SHA-256을 확인하고,
ZIP metadata는 기록된 byte range 및 SHA-256으로 복구한다. 임시 source cache는 manifest에
명시된 `/tmp/` 경로이며 method code를 import/실행하지 않았다. 이는 dataset/checkpoint
백업이나 full reproduction bundle이 아니다. 전체 ZIP/내부 파일·weight 검증을 대신하지
않으며 관련 대용량 payload의 삭제 근거로 쓸 수 없다.

Q11 Stage 6 measurement readiness는 완료·검증됐으며 Docker recipe, frozen config, source/input hashes와
exact commands는 [Q11 study README](../buildup/robotics/pilot_studies/q11-action-compression/README.md)가
소유한다. 새 image는 `research3-q11-readiness:v1`; `datasets/q11/fast/`는 pinned tokenizer
파일 6개의 read-only input, `runs/q11_v1/`는 새 raw output/cache다. Public ManiSkill source는
`external/q8/`에서 새 image로 copy하고, 기존 Q8 image/output은 dependency로 사용하지 않는다.
PhysX/Torch는 CPU, SAPIEN scene 생성은 explicit NVIDIA graphics를 사용한다. Policy training이나
compressed-action physical evaluation은 이 readiness 실행에 포함하지 않는다.

Q11 v2는 같은 [study README](../buildup/robotics/pilot_studies/q11-action-compression/README.md#controlled-physical-pilot-v2-preparation)가
별도 protocol/freeze, 실제 byte accounting, 새 image `research3-q11-pilot:v2`와 실행 command를
소유한다. 실제 pilot과 독립 감사가 완료됐으며 raw arrays/packets/manifests는
`runs/q11_v2/`, 별도 read-only CPU Docker 감사 receipt는 `runs/q11_v2_audit/verification.json`에
보존한다. Tracked `results_v2.json` / `verification_v2.json`과 `audit_v2.sh`는 study 폴더에 있다.
`logs/20260908_q11_v2_run.exit`와 `logs/20260908_q11_v2_audit.exit`는 모두 0이다.
Full reproduction에는 pinned inputs와 recipe, 결과 보존에는 raw output 및 hash manifest가
필요하다. 외부 사본을 검증하지 않았으므로 원본 data/output 삭제를 정당화하지 않는다.
Stage 7 JSON-only support 감사는 동일 image의 CPU-only Docker에서 완료했다.
`runs/q11_stage7/selection.json`과 tracked study `selection.json`이 receipt이며 정확한
command와 input/source hashes는 같은 study의 Stage 7 support audit 절에 있다.
Scientific v2 protocol/output과 기존 감사 receipt는 바꾸지 않았다.
V2 entrypoint는 immutable image ID, read-only source/input, 새 output 경로와 timestamped logs를
사용하며 기존 output 경로는 거부한다. V1 frozen code/결과와 기존 Docker 자산은 보존했다.

Q11 v3는 같은 study README의 [실행·독립 감사 기록](../buildup/robotics/pilot_studies/q11-action-compression/README.md#v3-execution-2026-09-10)이 protocol, code freeze와 commands를 소유한다.
기존 workspace-built Q11 v2 immutable image와 locks를 재사용해 실행·검증을 완료했다.
Raw state/action/packet/plan은 `runs/q11_v3/`, 별도 read-only CPU 감사 receipt는
`runs/q11_v3_audit/verification.json`에 보존한다. Study의 `results_v3.json` /
`verification_v3.json`은 tracked summary이며 `audit_v3.sh`로 감사를 재현한다.
`logs/20260910_q11_v3_run.exit`와 `logs/20260910_q11_v3_audit.exit`는 모두 0이다.
Calibration/preparation은 `runs/q11_v3_precheck/`와 `runs/q11_v3_contract/`에 별도 보존한다.
현재 method route는 종료됐고 실행 중인 job/재개 요청은 없다. 결과 보존에는 원본 raw bundle과
hash manifest가 필요하고, full reproduction에는 pinned input/source와 immutable image 또는
recipe/locks가 필요하다. V1/v2/v3 원본을 보존했으며 외부 사본 검증·삭제는 하지 않았다.

Q1 frozen CUDA feasibility의 environment, cache와 command는
[Q1 study README](../buildup/robotics/pilot_studies/q1-predicate-stability/README.md)가 소유한다.
후속 read-only source/metadata audit의 immutable URL과 checksum, raw JSON 복구 위치는
[Q1 artifact audit](../buildup/robotics/related_work/q1-artifact-schema.md#bounded-refinement-audit--2026-09-08)을 따른다.
`runs/q1_v3/`는 Q1만의 output/cache root이고, source/checkpoint는 Q8에서 checksum 검증된
public artifact를 read-only로 mount한다. Q8 raw results나 기존 host simulator는 dependency가 아니다.

Q8의 새 ManiSkill image, public checkpoint/demo input, Vulkan/EGL 복구와 반복 검증 command는
[Q8 study README](../buildup/robotics/pilot_studies/q8-recoverability/README.md)가 소유한다.
Source는 `external/q8/`, input은 `datasets/q8/`, row-level 결과는 `runs/q8/`다.
Physics/Torch CPU라도 현재 PickCube scene 생성에는 GPU graphics runtime과 `libegl1`이
필요하다. Q8 receipt는 Q1의 frozen PhysX CUDA protocol 실행을 대체하지 않는다.

Stage 7에서 종료한 Q10의 public subset과 Docker recovery는
[Q10 study README](../buildup/robotics/pilot_studies/q10-contact-observability/README.md)가
소유한다. 기존 v2/v4 dataset은 read-only로 재사용하고 v5 row-level output은 ignored
`runs/q10_v5/`에 둔다. V6 전 validation audit은 이 train feature 파일만 read-only로 mount하고
`runs/q10_validation_v6/`에 nested predictions를 기록했다. V6 probe는 새 CPU-only image에서
실행·검증했으며 ignored `runs/q10_v6/train/`와 `test/`에 row-level output을 보존한다.
학습에는 test feature를 mount하지 않고 final bundle 봉인 후 별도 container에서 평가했다.
Exact image, dependency inventory, freeze, run command와 verifier-only correction은 같은
study README의 v6 job/result를 따른다. 원래 failed verifier와 corrected verifier 기록을 함께
보존하며 재현 시 corrected verification command를 사용한다.
현재 Q10 workload는 실행 대상이 아니며 원본 dataset/cache/output은 provenance로 보존한다.
이번 종료 결정에서 asset을 삭제하거나 이동하지 않았다. Paper-level experiment나 active
hypothesis는 아직 없다.

새 hypothesis 또는 experiment가 named dataset/checkpoint를 요구할 때만
`local_dataset/`을 만들고 source, checksum, mount, derived-output boundary를
기록한다.

External dataset/source를 재사용할 때는 read-only mount를 기본으로 하고,
derived cache, prediction과 evaluation output은 active workspace의 명시된
artifact 경로에 분리한다.

## Cleanup Assessment — 2026-09-08

사용자가 지정한 research3 image와 다운로드 data에 대한 read-only 삭제 가능성 검토다.
이번 검토에서는 image, dataset, cache와 output을 삭제하지 않았다.

### Preservation goals

- **결과 보존:** 현재 paper result는 없지만 pilot의 source, frozen protocol, compact results,
  verifier, dependency/image/hash 기록은 `buildup/`에 보존한다. Docker image 제거만으로
  bind-mounted dataset이나 `runs/` 결과가 삭제되지는 않는다.
- **재분석/재개:** `runs/q10_v5/`의 train/test features, `runs/q10_validation_v6/`,
  `runs/q10_v6/`와 Q1/Q8 raw trajectories를 보존한다. Q10 v6는 저장된 features로 재실행할
  수 있지만 원본 HDF5를 지우면 feature extraction과 RGB/schema audit의 재검증은 불가능하다.
- **전체 재현:** 원본 dataset, source/build context, cache 또는 검증된 외부 사본과 recovery
  receipt가 필요하다. Dockerfile의 재빌드는 원래 image와 byte-identical함을 보장하지 않는다.
  동일 image 자체를 보존하려면 삭제 전에 별도 image export가 필요하다.

### Images

`research3-q1-predicate:v3`, `research3-q8-audit:v1` 및 Q10의
`schema:v2`, `rgb-audit:v3`, `denominator:v4`, `baselines:v5`, `validation:v6`, `probe:v6`
(모두 `research3-q10-` prefix)를 참조하는 container는 `docker ps -a`의 해당 ancestor
filters에서 0개였다. 여덟 image의 ID가 기존 연구 기록과 일치하고 각 Dockerfile과
dependency record가 남아 있다. 현재 study 실행에는 필요하지 않으므로 삭제 후보로 판단한다.
재실행하려면 build가 필요하며 Q8도 즉시 재진입 대상이 아니다. Shared layers/build cache
때문에 표시된 image size의 합을 실제 회수 용량으로 간주하지 않는다. 광범위한 Docker
prune은 이 검토 범위가 아니다.

### Data candidates

| Path | Local size / files | Recommendation |
| --- | --- | --- |
| `datasets/q10_reassemble/v4/*.h5` | 25.60 GiB, 16 recordings | 우선 삭제 후보; 종료한 Q10 원본. 외부 사본 검증 후 제거 |
| `datasets/q10_reassemble/v2/*.h5` | 2.20 GiB, 4 recordings | 같은 조건의 삭제 후보; v4와 별도 anchor files이므로 중복 사본이 아님 |
| `datasets/q10_reassemble/v1/`와 v2/v4 `download_manifest.json` | metadata, 매우 작음 | 보존; URL, archive member, CRC/SHA-256와 선택 기록이 복구에 필요 |
| `datasets/q8/` | 30.41 MiB, demo HDF5/JSON와 checkpoints 두 개 | 보존 권장; Q8이 refine이고 Q1/Q8 공통 input, 절약 효과 작음 |
| `runs/` | 약 312 MiB, 일부 cache 포함 | 결과와 재분석용 원본은 보존; dataset 삭제 대상으로 취급하지 않음 |

Q10 HDF5 후보 합계는 약 **27.80 GiB**다. 현재 확인한 workspace에 별도
`local_dataset/`은 없었다. Q1의 별도 대규모 dataset 다운로드도 없었다.
추가로 `external/q8/maniskill.tar.gz` 약 233 MiB는 source archive이고,
`runs/q1_v3/cache/` 약 226 MiB는 simulator cache다. Dataset이 아니며 우선 정리 대상으로
삼을 필요는 없다. Q1 cache 안 `.nv` 하위는 host 권한으로 읽히지 않아 cache 총량은 근사치다.

V2/v4 download manifests에는 원래 selective retrieval과 각 파일 SHA-256이 있다.
그러나 이번 검토에서 **외부 백업 사본의 존재·일치 여부는 확인하지 못했다.** Public URL과
과거 checksum 기록만으로 백업 검증을 대신하지 않는다. 실제 dataset 삭제 전에는
AGENTS.md의 Artifact Handoff And Cleanup Rules에 따라 외부 사본의 20개 파일, 크기,
checksum을 검증하고 해당 manifest와 검증 결과를 보존해야 한다. 삭제 권고는 이 조건부이며
새 public download의 현재 접근 가능성이나 전체 dataset의 향후 연구 가치를 판정한 것은 아니다.

## Image Cleanup Assessment — 2026-09-11

사용자가 지정한 네 image만 read-only로 검사했다. Image ID는 기존 연구 기록과 일치했고
각 `docker ps -a --filter ancestor=<full image ID>` 결과가 0개였다. Dockerfile, dependency
record, compact 결과와 Q11의 local ManiSkill build context 등 20개 recovery 파일의 존재를
확인했다. 실제 image 삭제·export·재빌드는 하지 않았다.

| Image | ID prefix | Recommendation | Effect of deletion |
| --- | --- | --- | --- |
| `research3-q11-readiness:v1` | `a60ff16758ac` | 우선 삭제 후보 | 종료된 Q11 readiness의 즉시 재실행 환경 제거 |
| `research3-q11-pilot:v2` | `fb9c530b6d66` | 우선 삭제 후보 | 종료된 Q11 v2와 v3가 공통 사용한 환경 제거; v3도 즉시 재실행 불가 |
| `research3-q12-input:v1` | `9cddc2624d3c` | 삭제 가능; 공간 여유가 있으면 보존 | 완료한 input v1의 동일 환경 재검사에는 복구 필요; completion runtime의 base가 아님 |
| `research3-q12-model-schema:v1` | `9977f452f5bb` | 현재 유지 권장 | active Q12의 CPU reference inference·output verification 환경 제거 |

- **결과 보존:** image만 제거해도 host의 `buildup/`, `datasets/`, `runs/` bind-mounted
  source·입력·checkpoint·결과는 남는다. 이 검토는 해당 데이터 삭제 권고가 아니다.
- **현재 연구 재개:** 다음 TODO는 Q12의 남은 연결 경로 비교다. 기존 completion을 다시
  실행·감사할 때 model-schema image가 필요하다. Q11의 현재 경로는 종료됐고 Q12 input
  audit도 완료돼 이 세 image는 즉시 실행 의존성이 낮다.
- **전체 재현:** recipe/lock/source를 보존해도 재빌드가 원래 image ID·OS package 상태를
  보장하지 않는다. 동일 environment 자체를 남겨야 하면 제거 전에 image export와 복구
  가능한 사본의 검증이 필요하다. 이번 검토에서 외부 image 사본은 확인하지 않았다.

Q12의 기존 build scripts는 frozen record 또는 `image_id.txt`가 있으면 의도적으로 거부한다.
삭제 후 복구할 때 frozen 파일을 지워 script를 통과시키지 않는다. Saved image 복원 또는
별도 recovery tag/runtime receipt를 사용하고 원래 image ID·protocol을 보존한다.
Q11 v1/v2 Dockerfile은 같은 recipe지만 별도 image ID이며, OS 설치 단계가 완전한 byte-level
재현을 보장하지 않는다. 표시된 image size 또는 unique-size 합을 실제 회수 용량으로
확정하지 않는다. Shared layers와 build cache 때문에 실제 회수량이 다를 수 있다.

복구 상세는 [Q11 study](../buildup/robotics/pilot_studies/q11-action-compression/README.md),
[Q12 input](../buildup/robotics/pilot_studies/q12-generated-geometry/README.md),
[Q12 model](../buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md)을 따른다.

## Data Activation Rule

1. Active hypothesis 또는 experiment가 named asset을 요구하는지 확인한다.
2. Source license, checksum, expected layout과 read/write boundary를 기록한다.
3. 필요한 asset만 준비하고 unrelated dataset/cache를 함께 활성화하지 않는다.
4. 새 run은 current Docker record와 independent verifier를 남긴다.

## Long Jobs

필요할 때 `logs/`를 만들고 download/build/render/inference를 background `tmux`에서 실행한다. Timestamped log, exact command, cwd, output, expected files와 verification command를 `TODO.md` 또는 experiment README에 기록한다.
