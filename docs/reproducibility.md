# Reproducibility Workflow

Updated: 2026-09-28

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
- output path와 verification command; paper-level 결과와 새 evaluator/강한 claim의 핵심 계산은 독립 검증

## Exploratory Run Records

Buildup 탐색은 위 실행 identity와 실패·변경 이력을 보존하되, 매 준비 단계에 별도 full
freeze를 만들 필요는 없다. 관찰한 데이터, 변경 이유와 달라진 설정을 가까운 owner에 적고
새 출력 경로를 쓴다. 필요한 검사의 범위는 [buildup 규칙](buildup.md#validation-and-revision)을
따른다. Markdown 변경만으로 dataset/model이나 이미 검증한 artifact 전체를 재감사하지 않는다.

확증의 사전 고정과 독립 평가, paper-level 재현 기준은 유지한다. 기존 frozen protocol·결과·
실패 판정을 소급 변경하지 않으며, 탐색 허용은 기존 Docker 자산 사용·cleanup 승인을 뜻하지 않는다.

Workspace에서 생성한 image를 정리할 때는 해당 build log·Dockerfile·source revision·
dependency lock·image ID와 필요한 output이 보존됐는지 먼저 확인한다. 실행 중이거나
즉시 재개할 container, 또는 남겨 둔 Dockerfile의 base로 필요한 image는 유지한다.
`docker ps -a --filter ancestor=<exact ID>`와 image의 parent/child 관계를 확인하고,
소유가 확인된 불필요한 tag만 `docker image rm <exact tag>`로 개별 정리한다.
외부 image, 소유가 불명확한 image, 공유 cache, 다른 작업의 container는 건드리지 않으며
`image prune`이나 강제 삭제는 사용하지 않는다. 실제 정리 대상·ID·결과는 해당 study owner에 기록한다.

## Current Data State

Q17의 제한된 ActiveArena `check_block_color` 입력은 `datasets/q17/activearena/check_block_color/`의 공개 training metadata와 세 Parquet 시연, `datasets/q17/model/`의 pinned Qwen3-VL-2B base와 OFT checkpoint다. Source는 `external/q17-activearena/`와 `external/q17-activearena-vla/`, 실행 출력은 `runs/q17/evidence_20260928_*`에 있다. 두 큰 모델 파일과 세 Parquet의 byte/SHA256, source commit, 별도 Docker image ID·lock, 명령·검산·대체된 입력의 경계는 [Q17 study owner](../buildup/robotics/pilot_studies/q17-evidence/README.md)가 소유한다. 현재 raw output과 model/data의 외부 backup은 확인되지 않았다. 결과 보존에는 compact 해석과 `probe.json`, held-out `case.json`/request RGB/step trace 및 exact-replay 검증 manifest가 필요하다. 즉시 추론 재개에는 모델·base·source·현재 simulator/evaluator 및 policy image가 필요하며, training-row 대조에는 세 시연도 필요하다. 전체 복구에는 fetch script와 pinned revisions 및 Dockerfile/lock을 함께 보존한다. 공개 training demonstration 대조와 탐색용 bridge의 held-out 사례는 paper result나 공식 benchmark 재현이 아니다. 종료된 Q17 진단 image 네 개의 개별 정리와 유지 image의 근거는 [study cleanup](../buildup/robotics/pilot_studies/q17-evidence/README.md#workspace-owned-image-cleanup)을 따른다.

CD5 선택을 위한 읽기 전용 source/input은 `runs/reserve_review/20260922/`에 있다.
Immutable URL·byte·SHA256은 [comparison_sources.json](../buildup/robotics/related_work/comparison_sources.json)의
`cd5_cd1_q8_review_20260922.source_audit`가 소유한다. 복구 시 각 URL을 record의 path로
다운로드하고 bytes/hash를 대조한다. 실행할 task identity는
[inputs.json](../buildup/cross_domain/pilot_studies/cd5-representation/inputs.json),
모델 revision·계획 output/cache 경로는 [CD5 study](../buildup/cross_domain/pilot_studies/cd5-representation/README.md)를
따른다. 현재 입력 13개 약 1.5 MB만 확보했고 모델 weight와 Docker runtime은 아직 없다.
CD5는 실행 전 보류됐으며 입력·설계를 보존한다. Paper-result/raw prediction은 아직
생성되지 않았고 이 source snapshot만으로 model inference를 재현할 수는 없다. 이번 후보
변경에 따른 payload 삭제는 하지 않았다.

Q16 문헌 접근 시 확보한 DynamicVLA README는 `runs/reserve_review/20260923/`에 있다.
Immutable URL·commit·bytes·SHA256과 읽은 범위는
[comparison_sources.json](../buildup/robotics/related_work/comparison_sources.json)의
`candidate_replacement_20260923`이 소유한다. 복구 시 `source_audit.url`에서
`source_audit.path`로 받고 bytes/SHA256을 대조한다. 이것은 source-text snapshot이며
runtime/data/checkpoint bundle이 아니다. 이후 Q16의 별도 CPU Docker recipe와 output을
구성했다. 실행 복구는 [Q16 recovery](#q16-motion-observation-recovery)를 따른다.

현재 지정 image/container의 정리 판단은
[2026-09-16 cleanup review](#docker-cleanup-review-2026-09-16)를 따른다.

Q14의 synthetic keypoint study는 [실행·복구 owner](../buildup/robotics/pilot_studies/q14-frame-errors/README.md)가
새 CPU Docker recipe, dependency pins, source snapshot, seed/config, 명령과 검증을 소유한다.
외부 dataset/checkpoint는 필요하지 않다. `runs/q14/`의 실행별 input/prediction arrays, 네 작은
checkpoint, metric/verification과 source manifest는 ignored payload이며 compact outcome과
함께 보존한다. 재분석에는 배열·source가, 학습 재현에는 고정 package/base와 config가 필요하다.
External backup은 아직 검증하지 않았으므로 이 결과 payload의 삭제를 권하지 않는다.
Container 정리 범위와 실행별 확인 기록은 해당 study owner를 따른다.

Q14의 [real-keypoint 실행·복구 owner](../buildup/robotics/pilot_studies/q14-frame-errors/real/README.md)는
별도 CPU Docker recipe·compatibility edit·실행/검산/정정·cleanup을 소유한다.
`datasets/q14/dream/`의 official archive, frozen weights/YAML과 24-frame `selected/`를 보존한다.
실제 URL/byte/hash는 `acquisition.json`, 선택 identity는 `selected/manifest.json`이다.
`external/q14-dream/`은 pinned source이며 install/import는 Docker 안에서만 수행했다.
Raw outputs/source/command/image identity는 `runs/q14/real_20260916_113000/`에 있다.
결과 보존에는 raw output과 compact outcome, 재추론에는 선택 입력·weights·source·image/rebuild가
필요하다. 재실행은 fresh run ID를 쓰고 기존 결과를 덮지 않는다. GT-camera-frame 입력과
미사용 residual 표기 정정의 해석은 study owner를 따른다. External backup은 미검증이다.

이전 source-only review의 URL/path/hash는
[source record](../buildup/robotics/related_work/comparison_sources.json)의 `q14_geometry_review_20260916`에
남긴다. 당시의 payload 미검증 상태는 현재 취득 결과로 소급 덮지 않는다. Snapshot은
`runs/q14/20260916_geometry_review/source/`이며 복구 시 record의 URL과 SHA256을 대조한다.

Q9의 [CPU 관찰 owner](../buildup/robotics/pilot_studies/q9-refresh/README.md)는
Dockerfile·dependency lock·v1/v2 image identity·실행 명령과 point/surface 해석을 소유한다.
`datasets/q9/env1/`에는 고정 revision의 52.2 MiB pickle과 선택 annotation/time 파일이 있다.
`runs/q9/inspect_v1`은 누락 dependency 실패, `inspect_v2`는 성공한 schema 검사,
`observation_v1`과 `visual_v1`은 raw trace·결과·해석용 영상이다. Paper result는 없으며,
재개에는 입력·source·v2 image 또는 pinned rebuild가 필요하다. 기존 출력은 덮지 않는다.
전체 재현에는 원본 URL/registry 접근도 필요하며 외부 backup 검증·삭제는 없다.
후속 표면점 비교는 같은 workspace v2 image를 immutable ID로 실행했다.
`runs/q9/surface_20260915_115726/result/`는 최초 출력과 실행 source를 보존하고,
`surface_20260915_120106/result/`는 비용 표기 정정 후 동일 수치 결과와 control 영상,
`verification.json`을 소유한다. 재현 entrypoint·mount·로그·보존 경계는
[study 실행 절차](../buildup/robotics/pilot_studies/q9-refresh/README.md#execution-and-verification)를 따른다.
이후 [투자 재평가](../buildup/selection.md#q9-investment-decision-2026-09-15)로 Q9 추가 실행은
보류했다. 위 입력·출력·재현 경로는 유지하며 이번 문헌 검토에서 수치 실행이나 삭제는 없다.
아래 Q9 미취득 기록은 이 관찰 전의 source-only reassessment 시점 기록이다.

후보 비교의 source/metadata 접근 기록은
[comparison_sources.json](../buildup/robotics/related_work/comparison_sources.json)이 소유한다.
`/tmp/research3-comparison-20260915/`는 21개 text/metadata 파일의 cache이며 dataset/model
payload나 실행 환경이 아니다. Pinned source는 receipt의 immutable URL을 별도 staging path로
받아 Git blob/bytes/SHA-256을 확인한다. 원래 API listing의 bytes/hash는 snapshot 기록이며
mutable listing을 나중에 다시 받으면 달라질 수 있다. 위 comparison receipt는 당시의 GCS
generation/HEAD metadata 확인만을 기록하며 이후 payload 검증을 대신하지 않는다.

Q6 추가 source/level/lock의 immutable URL과 Git blob/bytes/SHA-256은
[q6_sources.json](../buildup/robotics/related_work/q6_sources.json)이 소유한다.
`/tmp/research3-q6-review-20260915/`는 read-only 검토용 source cache다. 새 파일 9개 중 두 개는
RTC level JSON이며 checkpoint/demonstration payload는 없다. 복구는 receipt URL을 별도 staging
path로 받아 identity를 확인한다. Level은 Kinetix의 유사 파일로 대체하지 않는다.

이후 Q6 CPU readiness는 source/weight payload와 numerical schema를 검증했으나 원본의
first-terminal 성공 판정 불일치로 보류됐다. 새 [study owner](../buildup/robotics/pilot_studies/q6-timing/README.md)는
Docker recipe·CPU lock·명령·완료/실패 job·독립 검증과 cleanup 조건을 소유한다.
`external/q6/`는 세 pinned source, `datasets/q6/policies/`는 generation-specific policy 두 개,
`runs/q6/readiness/`는 원본/adapter record와 실패 상태의 raw evidence다.
[Assets](../buildup/robotics/pilot_studies/q6-timing/assets.json)의 모든 Git blob/bytes/SHA-256과
두 policy의 MD5/CRC32c/SHA-256이 확인됐다. 새 CPU image는 기존 연구 image에 의존하지 않는다.

Q6 [preservation freeze](../buildup/robotics/pilot_studies/q6-timing/preservation.json)는 중단된 실행의
보존 묶음이며 pilot 실행 허가나 paper result가 아니다. 결과 보존에는 compact evidence와
전체 raw-output·로그, 감사 재개에는 frozen code·선택 source/weights·image, 전체 재현에는
pinned registry distributions와 취득 receipt도 필요하다. 기존 출력을 덮어 재실행하지 않는다.
외부 backup 검증이나 삭제는 없으며 기존 Q12 freeze/결과는 그대로 유지한다.

후속 [Q6 재평가와 Q9 선택](../buildup/selection.md#q6-reassessment-and-q9-selection-2026-09-15)은
기존 freeze를 수정하지 않는다. 재평가는 Q6 question record, 새 접근/검증 기록은
[reassessment_sources.json](../buildup/robotics/related_work/reassessment_sources.json)이 소유한다.
`/tmp/research3-q6-reassessment-20260915/`는 DynaMem source와 DynaBench annotation/time,
API metadata의 검토 cache다. Receipt에 source commit·dataset revision·immutable URL과
byte/Git blob/SHA-256, mutable listing의 snapshot identity를 기록했다. 복구는 별도 staging에
동일 revision 파일을 받아 receipt와 비교한다. 이 cache는 runtime이나 검증된 RGB-D 입력이
아니며 pickle은 받거나 열지 않았다. Listed LFS hash는 payload 검증을 대신하지 않는다.
Q9 입력 취득·replay를 진행하려면 Q9 record의 설계 뒤 별도 Docker/run owner를 준비한다.
새 paper result나 resume할 Q9 실행은 없으며 기존 Q6 실패의 보존/전체 재현 요구는 유지한다.

Q12 BOP 입력 감사의 [real owner](../buildup/robotics/pilot_studies/q12-generated-geometry/real/README.md)는
새 CPU Docker·dependency lock·선택 입력·두 단계 freeze·취득/합성/실제 실행·검증 command를
소유한다. Raw 입력과 Range cache는 `datasets/q12/bop_v1/`, 합성 출력과 실패 control은
owner에 지정된 `runs/q12_real_preflight_*`에 있다. `validate.py`는 host에서 byte/CRC/hash와
source syntax만 확인한다. 실제 수치 출력은 `runs/q12_real_input_v1/`이며 frozen producer와
독립 verifier가 `DEFER_RAY_SUPPORT`를 확인했다. Owner의 `execution.json`/`verification.json`은
raw receipt와 byte-identical하고 `outcome.json`은 case/실패의 compact 발췌다.
현재 진단 결과 보존에는 전체 raw output root와 source/input identity가 필요하다. 분석 재개에는
frozen code·선택 입력·image가, 전체 재현에는 pinned source/wheels와 취득 Range/CRC 기록도
필요하다. Runner는 기존 출력을 거부하며 현재 경로 보류를 재실행으로 덮지 않는다.
Paper result는 아직 없으며 외부 백업 검증·삭제는 없다.

후속 source/record 재평가의 근거와 byte 검증 receipt는 real owner의
[reassessment.json](../buildup/robotics/pilot_studies/q12-generated-geometry/real/reassessment.json)에 있다.
추가 source는 `real/sources/renderer_vispy.py` 한 파일이며 기존 freeze의 실행 dependency가 아니다.
복구 시 receipt의 immutable URL을 별도 staging path로 받아 bytes/SHA-256을 확인한다.
논문·표준의 웹 참고는 URL/section/access date만 기록했으며 local backup으로 간주하지 않는다.
재평가는 source text/기존 JSON/byte 검사만 사용했다. Q12가 보류되어 현재 필요한 runtime은
없지만, 이전 수치 검증을 재현하려면 해당 image와 위 원본/전체 output을 보존하거나 복구해야 한다.

Q12의 [대체 경로 비교](../buildup/robotics/pilot_studies/q12-generated-geometry/README.md#alternative-routes-2026-09-14)는
BOP YCB-V real-data 입력 감사 준비를 선택했다. 이번 source/metadata 전용 접근은
[route_sources.json](../buildup/robotics/pilot_studies/q12-generated-geometry/route_sources.json)이
official revision, URL/Content-Range, byte/hash, ZIP directory와 작은 JSON/Markdown member의
CRC를 소유한다. `/tmp/research3-q12-routes-20260914/`는 text/range/metadata cache이며 새로운
image/mesh dataset이나 runtime 환경이 아니다. Saved `route_access.py`와 위 owner에 exact
background command·상한·log·verification이 있다. 복구는 다른 staging directory로 동일
revision/range를 받아 길이·SHA-256·Content-Range·member CRC를 확인한다. LFS archive hash는
기록했지만 전체 archive를 받지 않았으므로 검증하지 않았다. 일부 metadata 검증을 전체
dataset·camera calibration·mesh validity 검증으로 취급하지 않는다. 이후 실제 입력 byte 취득과
Docker 준비는 위 real owner에서 완료했으며 기존 Google 16k/model assets는 그대로 보존한다.

Q12 camera/geometry 경로의 read-only source 접근은
[linkage manifest](../buildup/robotics/pilot_studies/q12-generated-geometry/linkage_sources.json)와
[study assessment](../buildup/robotics/pilot_studies/q12-generated-geometry/README.md#linkage-route-assessment-2026-09-11)가
소유한다. Manifest의 immutable source URL을 별도 staging path로 받아 bytes/SHA-256을
확인한다. `/tmp/` source cache는 실행 환경이나 dataset 백업이 아니다. 이후 두 YCB asset의
payload/hash를 검증했고 [geometry owner](../buildup/robotics/pilot_studies/q12-generated-geometry/geometry/README.md)에
새 CPU Docker·wheel locks·synthetic receipt와 실행 command를 고정했다. Asset 원본은
`datasets/q12/geometry/`, 실제 출력은 `runs/q12_geometry_v1/`이다. 실행 판정은 `REFINE_LINKAGE`이며
box 두 view의 raw NPZ/JSON과 mug 두 view의 조기 중단 기록을 모두 보존한다. 별도 mesh 감사는
`runs/q12_geometry_v1_mesh_audit/verification.json`, compact copies·검증 command는 geometry
README가 소유한다. 기존 `run.sh`는 기존 출력 경로를 거부한다. 이 결과 보존에는 raw 출력과
원본 mesh, 실행/독립 감사 receipt가 필요하다. 후속 surface-preservation 감사는 별도
`runs/q12_mesh_preservation_v1/`에 raw/derived mesh·mapping·여덟 case payload를 보존하고,
`runs/q12_mesh_preservation_v1_inspection/`에 잔여 실패의 독립 검증을 보존한다.
[감사 owner](../buildup/robotics/pilot_studies/q12-generated-geometry/geometry/README.md#preservation-outcome-2026-09-14)가
두 새 freeze, immutable image, run/verification commands, inventory와 compact receipts를 소유한다.
표면·고정 query가 같아도 edge gate 실패가 남아 현재 asset 경로를 보류했다. 기존 readiness v1은
변경하지 않았으며, 정리한 사본은 readiness 통과 입력으로 사용할 수 없다. 결과 보존에는 두
새 output root도 필요하고, 전체 재현에는 원본 asset·이전 출력·pinned image/recipe가 필요하다.
원본 물리 단위를 복원하지 않고 선언한 synthetic scale을 사용했다. 기존 input/model freeze는
보존한다. Source/준비 감사는 dataset/image 삭제나 기존 completion 재실행의 근거가 아니다.

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
- **현재 연구 재개:** Google 16k와 BOP 입력 경로의 평가 후 Q12 추가 투자를 보류했다. 기존 completion을 다시
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

## Docker Cleanup Assessment — 2026-09-14

이번 사용자가 지정한 종료 container 53개와 Q12 image 네 개를 읽기 전용으로 검사했다.
실제 삭제·container 시작·image 재빌드·export는 없다. 새로 나타난 `transfer-s4-*` 두 개와
목록 밖의 running/other container는 삭제 후보에 포함하지 않았다. Container의 종료 상태만으로
결과 보존을 확정하지 않고 `docker inspect`의 mount와 `docker diff`를 함께 확인했다.
선택한 metadata와 diff 기록은 `logs/20260914_124325_container_cleanup.log`에 보존했다.

### Q12 images

네 tag의 image ID는 각각 owning folder의 `image_id.txt`와 일치했고 container 참조는 모두
0개였다. 네 Dockerfile과 saved image identity가 있으며 input/completion/geometry/
preservation/BOP output inventory의 6/11/14/38/17개 파일 hash가 일치했다.

| Image | ID prefix | Current recommendation | Deletion consequence |
| --- | --- | --- | --- |
| `research3-q12-input:v1` | `9cddc2624d3c` | 삭제 가능 | 완료한 input v1의 즉시 재검증에는 환경 복구 필요 |
| `research3-q12-geometry:v1` | `0196da1a3a01` | 삭제 가능 | 보류한 Google 16k readiness/preservation의 즉시 재검증에는 복구 필요 |
| `research3-q12-model-schema:v1` | `9977f452f5bb` | 삭제 가능; model 재추론 예정이면 보존 | 기존 CPU reference completion과 schema 검증 환경 제거 |
| `research3-q12-real-input:v1` | `01331a0e031a` | 후속 재평가 완료로 즉시 의존성 없음; 재현 목적이면 보존 | 삭제하면 기존 BOP 수치 감사 재현에 환경 복구 필요 |

최초 이 검토에서는 다음 BOP 재평가를 위해 real-input 유지를 권했다. 이후 같은 날
[재평가](../buildup/robotics/pilot_studies/q12-generated-geometry/real/README.md#reassessment-2026-09-14)를
source/기존 record만으로 완료하고 Q12 추가 투자를 보류해 네 runtime의 즉시 의존성이 없어졌다.
앞의 container 참조 수는 최초 metadata 감사 시점의 기록이다. 삭제 시점에 참조를 다시 확인하고
아래 보존 목적을 구분한다. 이번 후속 작업에서도 실제 삭제나 image 백업 검증은 없다.

- **결과 보존:** image만 삭제하면 workspace의 원본 입력·checkpoint·raw output·compact
  record는 남는다. 이번 권고는 데이터나 `runs/` 삭제를 포함하지 않는다.
- **현재 연구 재개:** 다음 후보 비교는 이 네 runtime에 의존하지 않는다. 기존 Q12 수치
  검사를 재개하려면 해당 runtime이 필요하므로 즉시 재검증을 원하면 보존한다.
- **전체 재현:** recipe/lock만으로 동일 image ID 재생성을 보장하지 않는다. 동일 환경 자체가
  필요하면 image를 유지하거나 먼저 export 사본을 검증해야 한다. 외부 image 백업은 미확인이다.

실행할 경우의 명시적 대상은 다음과 같다. 이 검토에서는 실행하지 않았다.

```bash
docker image rm research3-q12-input:v1 research3-q12-geometry:v1 research3-q12-model-schema:v1
```

Frozen build script의 기존 freeze/image receipt 거부 조건은 그대로 둔다. 복구 시 freeze를
삭제하거나 현재 image ID 기록을 덮어쓰지 않고 별도 recovery environment receipt를 사용한다.
화면의 image size 합계는 shared layer/build cache를 고려한 실제 회수량이 아니다.

### User-listed containers

53개 모두 `exited`이며 mount는 모두 bind mount다. Research3 작업 container는 없고
`transfer-*`는 research2, 나머지는 `/home/user/...`의 별도 작업 경로에 연결돼 있다.

| User-listed group | Count | Recommendation and verified boundary |
| --- | ---: | --- |
| `transfer-s1-*`, `transfer-s2-*`, `transfer-s3-*`, `transfer-drift-*` | 14 | Container 삭제 후보. Root filesystem read-only; 출력은 research2 bind mount. 해당 host artifact 폴더와 파일 수를 확인했다. 필요 stdout/stderr 로그는 먼저 보존 |
| `isolation_final_*`, `isolation_analysis_*` | 17 | 조건부 삭제 후보. Read-only root, output/home bind mount는 확인했지만 이 환경에서 해당 `/home/user/...`의 실제 결과를 열람할 수 없어 소유 작업의 결과 확인 필요 |
| `revision_offline_*` | 7 | 조건부 삭제 후보. Output bind mount와 mount point/일부 Mesa cache 변경만 확인; host 결과는 위와 같이 미확인 |
| `phase2_eval_*`, `phase2_training_5090` | 9 | 조건부 삭제 후보. Evaluation output 및 training checkpoint/log bind mount는 확인; host의 실제 checkpoint·결과 확인 필요 |
| `twojy-*` | 6 | 결과/checkpoint·추가 container 파일 확인 후 삭제 판단. Root writable이며 GPU cache·임시 파일·추가 home 경로가 있고 host 결과는 직접 확인하지 못함 |

Transfer의 쓰기 mount는 총 10개이며 모두 현재 filesystem에서 접근 가능했다. 출력 root
`/home/yoohyun/research2/buildup/robotic-autonomy/pilot_studies/transfer/artifacts/`에서
245 files / 558,996,227 bytes를 확인했다. 여러 container가 같은 root 또는 그 하위 폴더를
mount하므로 이를 container별 독립 파일 수로 합산하지 않는다. 연구적 결과의 유효성,
전체 checksum 백업 또는 외부 전송 성공을 이 file-count 확인으로 대신하지 않는다.

다른 프로젝트의 67개 쓰기 mount는 Docker metadata에서 연결을 확인했지만 이 환경의 경로로
직접 접근할 수 없었다. 이는 데이터가 사라졌다는 뜻이 아니다. `docker diff`는 mount point와
runtime 설정 변경도 표시하므로 변경 개수 자체를 잃게 될 연구 결과 개수로 해석하지 않는다.
특히 exit 1/137 container의 필요 로그와 중간 checkpoint 보존 여부를 먼저 확인한다.

Container 삭제 시 container 고유 writable layer와 Docker 보관 로그는 제거된다. Bind-mounted
host 폴더 및 image를 함께 지우는 작업은 아니다. 같은 container를 그대로 재시작할 수는 없으므로
소유 프로젝트의 launch command와 image/config를 보존해야 한다. 무차별 `container prune`,
`rm -f` 또는 volume/image 일괄 정리는 이 권고에 포함하지 않는다.

## Workspace File Cleanup — 2026-09-15

사용자 요청으로 `/home/yoohyun/research3` 내부 파일만 읽기 전용으로 검토했다. 실제 삭제,
이동, backup 생성, Docker asset 변경은 없다. Q6의 다음 CPU readiness 우선순위는 유지한다.

### Scope and preservation goals

- **결과 보존:** `buildup/`의 frozen source/protocol/result/verifier/receipt와 `runs/`의 원본
  row-level 결과를 유지한다. 현재 paper-body result는 없지만 종료/보류 결정의 근거다.
- **현재 작업/재개:** Q6는 기존 Q1/Q8/Q11/Q12의 data/runtime cache를 요구하지 않는다.
  다만 이전 연구를 즉시 재실행하려면 각 원본 입력·checkpoint·runtime을 복구해야 한다.
- **전체 재현:** 작은 Markdown/metric 요약만으로 충분하지 않다. 원본 data·checkpoint·source와
  환경 identity를 보존하거나 검증한 외부 사본을 확보한다. Public URL이나 같은 disk의
  duplicate는 외부 backup 검증으로 취급하지 않는다.

읽을 수 있는 allocated space는 약 **4.97 GiB**다. `datasets/q12/` 약 3.98 GiB,
`external/q8/` 약 607.6 MiB, `runs/` 약 361.3 MiB가 대부분이다. 네 NVIDIA cache 하위는
권한 제한으로 읽지 못했으므로 합계는 하한에 가깝다. Directory/allocated bytes와 실제
file content size는 다르며, 아래 값은 반올림한 disk 사용량이다. Symlink는 발견되지 않았다.
현재 `research3`를 mount한 running container와 경로가 일치하는 연구 process는 확인되지 않았다.

### Candidates

| Path | Size | Recommendation and consequence |
| --- | --- | --- |
| `external/q8/maniskill.tar.gz` | 232.4 MiB | 삭제 가능한 source 중복 archive. 풀린 `ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8/`와 `source.sha256`·checkpoint metadata는 유지한다. 두 source 사본을 함께 삭제하지 않는다. |
| `runs/q1_v3/cache/.sapien/` | 225.8 MiB | 종료한 Q1의 PhysX runtime download cache. 결과/weight가 아니다. 정리 가능하지만 Q1 CUDA 재현에는 동일 hash의 binary 재취득이 필요하다. |
| `buildup/robotics/pilot_studies/q10-contact-observability/__pycache__/` | 96 KiB | Python bytecode만 있는 ignored directory. 삭제 가능하며 source 실행 시 재생성된다. |
| `datasets/q12/archives/` (`input.zip`, `gt.zip`) | 1.75 GiB | 우선 조건부 후보. 상위 `3dsgrasp_ycb_train_test_split.zip` 안의 두 member와 완전히 일치한다. 상위 ZIP·subset·index·acquisition/inputs manifest를 유지하면 다시 꺼낼 수 있다. Dataset 외부 backup은 미검증이다. |
| `datasets/q12/3dsgrasp_ycb_train_test_split.zip` | 1.71 GiB | Q12가 보류되어 현재 작업에는 불필요. 외부 backup 검증 뒤 삭제 후보. 위 inner archive까지 함께 지우면 local 원본 전체 dataset은 사라지며 약 3 MiB의 subset만으로 복구되지 않는다. |
| `datasets/q12/3dsgrasp_model.pth` | 482.3 MiB | Q12 completion checkpoint. 외부 backup 검증 뒤 삭제 후보. 제거하면 기존 completion/schema 실행에 다시 필요하며 결과 파일로 대체할 수 없다. |

앞의 source archive/runtime cache/bytecode만 합하면 약 **458 MiB**다. 큰 Q12 네 파일
(상위 ZIP, inner ZIP 두 개, checkpoint)은 합계 약 **3.93 GiB**의 조건부 후보이며,
외부 사본의 checksum 검증 전 실제 dataset/checkpoint 삭제 대상으로 확정하지 않는다.
상위/inner ZIP 둘 중 하나만 보존하는 deduplication과 양쪽 모두를 제거하는 data retirement를
구분한다. Q12 `subset/`, `geometry/`, `bop_v1/`, indexes와 manifests는 작고 기존 결과의
입력/provenance이므로 우선 정리에서 제외한다.

`external/q8/` 전체도 Q6에는 필요하지 않지만 Q1/Q8/Q11 image build context와 source
metadata를 함께 잃는다. 따라서 source archive 하나만 지우고 풀린 source는 유지하는 쪽을
우선한다. Q11 cache의 Hugging Face module 내용과 읽을 수 없는 NVIDIA cache는 일괄 삭제
가능하다고 판정하지 않았다. `.sapien/` 이외의 Q1 raw output도 삭제 후보에 포함하지 않는다.

### Verified identities and limits

Read-only byte audit completed. 상위 ZIP 및 checkpoint가 기존 `inputs.json`의 SHA-256과
일치했다. ZIP member를 끝까지 읽어 CRC를 확인하고 inner ZIP의 SHA-256/size와 비교했으며,
두 member 모두 동일하다. ManiSkill archive는 `external/q8/source.sha256`과 일치하고,
archive의 regular file **1,495개 / 388,705,530 bytes**가 풀린 source와 모두 같았다.
Q1 PhysX binary는 기존 `runtime.json`의 236,705,440 bytes/hash와 일치했다.
이들은 local identity 검사이며 외부 backup이나 현재 원격 download 접근성 검사가 아니다.

검증 로그: `logs/20260915_workspace_cleanup.log`. 검사 cwd는 repo root이며 임시 stdlib
프로그램 `/tmp/research3_cleanup_verify.py`를 `nohup timeout 180 python -u`로 실행했다.
`zipfile.ZipFile.open` / `tarfile.extractfile`로 stream hash를 비교했으며 디스크 추출,
model import, simulator 실행은 없었다. 복구 identity는 Q12 `inputs.json`, Q8 `source.sha256`,
Q1 `runtime.json`이 소유한다. 데이터 복구는 별도 staging path에서 검사하고 frozen 기록을
덮어쓰지 않는다. 동일 환경 전체 재현은 cache 재생성만으로 보장되지 않는다.

### Keep and historical correction

- `buildup/`, `docs/`, `README.md`, `TODO.md`, `summary.md`, `AGENTS.md`, `.git/`를 유지한다.
  `buildup/`는 약 7.1 MiB이며 미추적 Q12/Q6 artifact도 있어 통째로 지우면 연구 기록을 잃는다.
- `runs/`의 trajectory, prediction, feature, row-level JSONL, verifier 결과는 외부 backup 전
  유지한다. Q10 v6 두 큰 JSONL도 검증/분석 근거이므로 단순 로그로 취급하지 않는다.
- `logs/`는 약 3 MiB이며 592개 파일 중 555개가 Git tracked인 당시 snapshot이다.
  절약 효과가 작고 실패/완료 기록이 있어 우선 정리 대상이 아니다. 새 검증 로그 추가로
  file count는 변할 수 있다.
- `hypothesis/`, `experiments/`, `literature/`는 작은 README/workflow entry를 소유한다.
  현재 비활성이라는 이유로 제거하지 않는다.
- 2026-09-08 표의 Q10 HDF5 27.80 GiB는 **현재 존재하지 않는다**. `datasets/q10_reassemble/`에는
  v1 metadata 7개, 약 100 KiB만 남아 있다. 언제/누가 제거했는지 또는 backup 유무는 이 감사로
  판단하지 않았으며, 과거 용량을 이번 회수 가능량에 더하지 않는다.

## Data Activation Rule

1. Active hypothesis 또는 experiment가 named asset을 요구하는지 확인한다.
2. Source license, checksum, expected layout과 read/write boundary를 기록한다.
3. 필요한 asset만 준비하고 unrelated dataset/cache를 함께 활성화하지 않는다.
4. 새 run은 current Docker record와 independent verifier를 남긴다.

## Long Jobs

필요할 때 `logs/`를 만들고 download/build/render/inference를 background `tmux`에서 실행한다. Timestamped log, exact command, cwd, output, expected files와 verification command를 `TODO.md` 또는 experiment README에 기록한다.

## Q7 Source Metadata Recovery

Q7의 원본 execution metadata는 ignored `external/q7-sources/`에 있다.
Pinned download URL, local path, bytes와 SHA256는
[comparison_sources.json](../buildup/robotics/related_work/comparison_sources.json)의
`q7_q14_review_20260915.metadata`가 소유한다. URL에서 해당 local path로 복원한 뒤 크기와
SHA256를 대조한다. Raw metadata의 비표준 `NaN` 값을 임의로 고치지 않는다.

UR5 이미지 archive는 ignored `datasets/q7-ur5/records.tar.gz`, 원본 발췌와 첫 비교 출력은
`runs/q7/prepared/`, `runs/q7/scored/`, `runs/q7/verification.json`에 보존한다.
[Q7 study README](../buildup/robotics/pilot_studies/q7-failure-source/README.md#verification-and-preservation)가
archive revision/upstream checksum, Docker build/run command, immutable image와 복원 절차를 소유한다.
[Compact outcome](../buildup/robotics/pilot_studies/q7-failure-source/outcome.json)은 실행 source/output
hash와 결과를 보존한다. 재실행은 새로운 output directory와 container name을 사용한다.

Metadata manifest만으로 이미지와 실행 결과가 보존되지는 않는다. Git의 code/config/annotation/
compact outcome에 더해 현재 분석을 바로 재개하려면 ignored 원본과 출력이 필요하다. 전체 재현은
pinned 원본을 다시 취득해 Docker로 생성할 수 있다. 외부 backup/삭제 안전성은 검증하지 않았다.

Q7 general VLM의 복원 owner는 [VLM recovery](../buildup/robotics/pilot_studies/q7-failure-source/README.md#vlm-verification-and-recovery)다.
Pinned model 파일 목록/identity는 같은 폴더의 `model.json`, prompt/processor/decoding은
`vlm_config.json`, CUDA recipe·resolved dependency는 `Dockerfile.vlm` / `requirements.vlm.lock`,
실행 image identity는 `vlm_environment.json`에 있다. 다운로드는 `fetch_model.py`로 복원·hash
검증한다. `fetch_ranges.py`를 쓸 때 sparse 파일의 size를 완료 근거로 삼지 않는다.

- **결과 보존:** Git의 code/config/compact `outcome.json` 외에 ignored `runs/q7/vlm/`의
  30개 원문 prediction·input·runtime·completion·review와 `runs/q7/vlm_input_check.json`을 유지한다.
  이번 출력은 paper result가 아니지만 형식 실패와 사후 해석의 근거다.
- **현재 대조 재개:** 위 결과와 `runs/q7/prepared/`, ignored `checkpoints/q7/smolvlm2-2.2b/`의
  검증된 15개 model/tokenizer/processor 파일·`download.json`, project-specific VLM image가 필요하다.
- **전체 재현:** model/UR5의 pinned 원본과 Docker recipe 또는 immutable image를 복구하고
  새 output/container 경로에서 실행한다. Checkpoint는 약 9 GB이며 receipt만으로 대체되지 않는다.

실행 명령·container/log·세부 SHA256는 위 owner와 compact outcome에 있다. 기존 출력이 있는
경로를 재사용하지 않는다. 외부 backup/삭제 안전성은 미검증이며 이번 작업에서 삭제한 자산은 없다.


Q7 END 반복 대조의 복원은 [control recovery](../buildup/robotics/pilot_studies/q7-failure-source/README.md#control-verification-and-recovery)가 소유한다.
`repeat_end.py` / `run_repeat.sh`가 기존 VLM source/config를 보존하면서 별도 output을 만든다.
Ignored `runs/q7/end_repeat/`의 새 여덟 원문·입력 계획·config·runtime·review에 더해, 재사용한
일곱 응답의 근거인 원래 `runs/q7/vlm/`도 함께 필요하다. 새 output은 원래 30개를 대체하지 않는다.
정확한 명령·image와 source/output hash는 study README와 `outcome.json.end_repetition_control`에 있다.

사용자 요청의 [container 정리 규칙](../AGENTS.md#docker-only-reproduction)에 따라 2026-09-16의
Q7 prepare/infer/review container 3개만 정리했다. Workspace 생성 기록·mount·명령·exit 0과
host의 결과/로그 보존을 확인한 뒤 ID별 `docker rm`을 실행했다. Container가 없어도 당시
image ID·mount·command·상태는 위 outcome에 남는다. 다른 container, image, volume, cache는
변경하지 않았다. 상세 삭제 대상·로그는 [cleanup owner](../buildup/robotics/pilot_studies/q7-failure-source/README.md#container-cleanup-2026-09-16)를 따른다.


## Docker Cleanup Review 2026-09-16

사용자가 지정한 image 7개를 읽기 전용으로 조사했다. 실제 image/container 삭제·실행은 없다.
Image identity, 직접 참조 container의 상태·command·mount·filesystem diff, workspace 실행 기록과
결과 보존을 대조했다. 상세 조회 snapshot과 hash 검사는
`runs/docker_cleanup/20260916_105554/audit.json`에 있다. 관련 container 18개는 모두 exited다.

**보존 목적 구분:** 현재 자료는 buildup 진단 결과이며 paper result가 아니다. 결과 보존에는
workspace의 raw output·compact outcome·입력/source identity·로그를 유지한다. Image를 지워도
이 bind-mounted 파일은 지워지지 않는다. 재개에는 image 또는 재빌드가 필요하며, 전체 재현은
고정 source/data/model과 package/base 접근까지 필요하다. Recipe/lock은 존재하지만 향후
registry 접근이나 byte-identical rebuild를 이번에 검증하지 않았다. Frozen image ID/원본 기록을
새 build ID로 덮지 않는다. 외부 backup은 미검증이며 dataset/checkpoint/결과 삭제를 권하지 않는다.

| Image | 현재 container 수 | 판단 |
| --- | ---: | --- |
| `research3-q12-real-input:v1` | 0 | 삭제 가능. Q12 deferred, 실행 결과·recipe 보존 확인; 즉시 재개에는 재빌드 필요 |
| `research3-q14-frame-errors:v1` | 0 | 삭제 가능. 첫 관찰 완료; 가까운 후속 CPU 재실행 편의를 원하면 선택적으로 유지 |
| `research3-q6-readiness:v1` | 4 | 아래 네 container 정리 후 삭제 가능. 실패 결과·source·recipe 보존 확인 |
| `research3-q7-failure-source:v1` | 4 | 아래 네 container 정리 후 삭제 가능. Q7 deferred, 첫 관찰 결과 보존 |
| `research3-q7-vlm:v1` | 3 | 아래 세 container 정리 후 삭제 가능. 원문 예측·review·model/recipe 경로 유지 |
| `research3-q9-refresh:v1` | 1 | 우선 삭제 후보. PyTorch dependency 누락으로 실패한 구버전, v2로 대체 |
| `research3-q9-refresh:v2` | 6 | Image 자체의 결과 보존 의존성은 없으나, 아래 소유권 미확인 container를 먼저 해결해야 삭제 가능 |

삭제 후보 container 17개는 모두 workspace input/output/source mount와 해당 study의 실행
기록이 맞는다. Readiness 실패와 dependency 실패의 exit code도 실패 로그·결과 보존 뒤 정리
가능한 상태다. Container write layer에는 연구 결과가 남아 있다는 증거가 없고, 차이는 mount
경로·임시 font cache·GPU driver 주입 파일 등이다. 영속 result/data는 host bind mount에 있다.
다음 목록은 검토 시점의 후보이며 강제 삭제·prune·prefix 일괄 삭제를 사용하지 않는다.

| Container ID | Container | Exit |
| --- | --- | ---: |
| `bda4557bee9a` | `research3-q6-verify-20260915_101603` | 0 |
| `05b3b82c2771` | `research3-q6-readiness-20260915_101321` | 1 |
| `f299a0a84f32` | `research3-q6-preflight-20260915_101038` | 0 |
| `a01db91f316e` | `research3-q6-schema-20260915_100733` | 0 |
| `23e379984531` | `research3-q7-aggregate-20260915_142056` | 0 |
| `6db61db1b1ef` | `research3-q7-verify-20260915_142056` | 0 |
| `737b13192f8e` | `research3-q7-score-20260915_142014` | 0 |
| `7d06d8d1e908` | `research3-q7-prepare-20260915_141759` | 0 |
| `d51a738894c4` | `research3-q7-vlm-review-20260915_190234` | 0 |
| `60cb520403de` | `research3-q7-vlm-infer-20260915_190023` | 0 |
| `c235a7f36c98` | `research3-q7-vlm-check-20260915_185244` | 0 |
| `e08097ace189` | `research3-q9-inspect-v1` | 2 |
| `f7e96e4b38e1` | `research3-q9-surface-20260915_120106` | 0 |
| `246b9fedd4f2` | `research3-q9-surface-20260915_115726` | 0 |
| `27d2a368c344` | `research3-q9-visual-v1` | 0 |
| `e586ebed382d` | `research3-q9-observe-v1` | 0 |
| `a6b6e0e887c1` | `research3-q9-inspect-v2` | 0 |

**보류:** `3835659f18ae` / `research3-q9-dependencies-v2`, exit 0. Q9 v2 image에서 `pip freeze`만
실행했고 filesystem diff는 없다. stdout은 현재 `requirements.lock`과 일치하며 위 audit
디렉토리의 `q9_dependencies.log`에도 보존했다. 그러나 workspace mount/label 또는 별도 생성
기록을 찾지 못했다. 이름·image만으로 우리가 만든 container라고 확정하지 않는 규칙에 따라
삭제 후보 17개에서 제외한다. 해당 생성 주체가 확인되면 기술적으로 유지할 결과나 재개 작업은
없다. 이 container를 유지하는 동안 Q9 v2 image를 강제 삭제하지 않는다.

검사: Q6 raw-output inventory와 로그, Q7 CPU/VLM/END-control artifact hashes, Q12 실제 출력,
Q14 result manifest, Q9 주요 trace/result/image를 포함한 98개 file 검사에서 누락·기록된 checksum
불일치가 없었다. 전체 dataset/model을 다시 해시하거나 외부 backup으로 간주하지 않았다.
Docker logs는 해당 container의 끝 100줄을 보조 보존했고, dependency 출력은 전체를 보존했다.
Q12·Q14는 현재 직접 참조 container가 0개다. 표시된 image 크기의 합이 실제 회수 용량은 아니며
공유 layer와 build cache 때문에 차이가 난다. 다른 작업의 image/container/volume은 변경하지 않았다.

## Workspace File Cleanup — 2026-09-16

Q14 투자 보류 후 사용자 요청으로 workspace 내부의 현재 용량·파일·재현 의존성을 읽기 전용으로
확인했다. 실제 파일 삭제·이동·backup 생성·Docker 변경은 없다. 다음 연구 작업은 후보 비교이며
진행 중인 study는 없다. 조회 시 이 workspace를 mount한 running container도 없었다.

읽을 수 있는 allocated space는 **13.955 GiB**다. Checkpoints 약 8.375 GiB, datasets
약 4.552 GiB, external 약 633.3 MiB, runs 약 398.6 MiB다. Q1 `.nv` 및 Q11 v1/v2/v3의
`cache/nvidia` 네 하위 경로는 권한 때문에 읽지 못했다. 따라서 전체 용량은 하한이며 해당
cache의 삭제 가능성은 판단하지 않았다. Docker image/build cache는 이 폴더 용량에 포함하지 않는다.

### Preservation goals and deletion conditions

- **결과 보존:** 아직 paper-body result는 없다. Buildup 관찰·보류 판단의 근거인 source/config,
  compact outcome과 raw prediction/trajectory·검증·로그를 유지한다. 입력 모델만 제거하면
  저장 결과는 남지만 추론 재실행은 할 수 없다.
- **현재 작업/재개:** Q7/Q12/Q14는 `deferred`이고 다음 후보 비교에는 아래 대형 payload가
  즉시 필요하지 않다. 해당 관찰의 재개·재검증에는 원래 입력/weight/runtime 복원이 필요하다.
- **전체 재현:** 데이터·checkpoint·model cache를 실제 삭제하기 전 외부 사본의 hash/파일 수를
  검증한다. 기존 source URL, local checksum 또는 같은 disk의 중복 파일은 외부 backup이 아니다.
  이번에는 외부 사본을 검증하지 않았으므로 큰 payload는 **조건부 삭제 후보**다.

### Priority candidates

모든 경로는 `/home/yoohyun/research3/` 기준이며 회수량은 현재 allocated bytes의 반올림 값이다.
디렉터리 전체보다 표의 정확한 파일만 정리하고 작은 manifest/config는 유지한다.

| 대상 | 용량 | 판단·복구 영향 |
| --- | ---: | --- |
| `external/q8/maniskill.tar.gz` | 232.36 MiB | 우선 정리 후보. 풀린 source tree와 `source.sha256`·metadata를 유지한다. 09-15 byte audit에서 1,495개 regular file이 풀린 source와 일치했고 현재 양쪽이 존재한다. |
| `runs/q1_v3/cache/.sapien/` | 225.76 MiB | 우선 정리 후보. 종료한 Q1의 PhysX runtime binary cache이며 결과/학습 weight가 아니다. 재현 시 pinned binary 재취득 필요; 그 밖의 `runs/q1_v3/`는 유지한다. |
| `buildup/robotics/pilot_studies/q10-contact-observability/__pycache__/` | 96 KiB | Python bytecode만 있는 재생성 가능한 디렉터리. Source는 유지한다. |
| `checkpoints/q7/smolvlm2-2.2b/model-00001-of-00002.safetensors`, `model-00002-of-00002.safetensors` | **8.370 GiB** | Q7 보류로 최대 조건부 후보. 두 파일은 중복이 아니라 한 모델의 두 shard다. 삭제하면 Q7 VLM 재추론 불가. `model.json`과 local index/config/tokenizer, `download.json`·`ranges.json`을 유지한다. |
| `datasets/q12/archives/input.zip`, `gt.zip` | **1.752 GiB** | 조건부 중복 제거 후보. 상위 ZIP member와 byte identity가 09-15에 검증됐다. 상위 ZIP을 유지하면 다시 추출 가능하나 외부 backup 검증은 별도다. |
| `datasets/q12/3dsgrasp_ycb_train_test_split.zip` | **1.710 GiB** | Q12 보류로 조건부 후보. Inner ZIP까지 함께 제거하면 local full dataset을 잃는다. 약 3 MiB subset만으로 full dataset을 복구할 수 없다. |
| `datasets/q12/3dsgrasp_model.pth` | **482.25 MiB** | Q12 보류로 조건부 후보. 기존 completion을 재추론하려면 checkpoint 복원이 필요하다. |
| `datasets/q14/dream/panda-3cam_realsense.archive` | **342.48 MiB** | Q14 보류로 조건부 후보. `selected/` 49개 입력 파일·manifest를 유지하면 이미 선택한 24-frame 입력은 남지만 전체 archive를 대체하지는 않는다. |
| `datasets/q14/dream/panda_dream_vgg_q.pth` | **84.78 MiB** | Q14 보류로 조건부 후보. 제거하면 detector 재추론에 weight 재취득 필요. YAML·acquisition receipt·selected 입력은 유지한다. |

Source archive/runtime cache/bytecode 합계는 약 **458.2 MiB**다. 큰 Q7 weight, Q12 네 파일,
Q14 두 파일의 조건부 합계는 **12.720 GiB**이며, parent directory 용량을 다시 더하지 않는다.
Q12 중복 ZIP만 정리하는 것과 original dataset 전체를 없애는 것은 다른 선택이다.

### Keep and lower-priority inputs

- `buildup/` 약 9.3 MiB, `docs/`, `.git/`, root Markdown, stage README와 source/config를 유지한다.
  `runs/`는 위 `.sapien/`만 예외이며 나머지 약 173 MiB는 원본 결과·진단·source snapshots다.
  `logs/` 약 3.6 MiB도 절약 효과가 작고 실행/실패 근거가 있어 보존한다.
- Q12 `subset/`, `geometry/`, `bop_v1/`, indexes·acquisition/inputs manifest와 Q14 `selected/`,
  YAML·acquisition manifest는 기존 결과의 입력/provenance이므로 보존을 권한다.
- Q7 UR5 `datasets/q7-ur5/records.tar.gz` 약 52.31 MiB, Q9 `datasets/q9/env1/` 약 52.2 MiB와
  Q6 `datasets/q6/policies/` 약 23.5 MiB도 보류된 연구의 입력이라 외부 backup 후 정리할 수
  있지만 공간 효과가 작아 후순위다. Q8 `datasets/q8/` 약 30.4 MiB는 조건부 refine 및 공통
  재현 입력이라 보존을 권한다. Q10은 과거 27.8 GiB HDF5가 이미 없고 작은 metadata만 남아 있다.
- `external/` 전체 삭제는 권하지 않는다. Q8 source는 Q1/Q8/Q11 build context이며 Q3 비교에서
  참고할 수 있다. Q6·Q7·Q14의 작은 source checkout도 provenance와 복구에 유용하다.

검사 범위: `du -x -B1`, 파일 목록/크기, Q7 index의 두 shard 참조, 15-file download receipt의
현재 파일 크기 일치, 이전 cleanup byte-audit 기록, 각 study의 결과/복구 README 및 running
container mount 조회. 이번에는 대형 payload를 다시 전체 해시하거나 원격 재다운로드·외부
backup 검증을 수행하지 않았다. 삭제 시에는 진행 작업·남길 사본을 다시 확인한다.

## CD2 Source Snapshot Recovery

CD2 입력의 authoritative URL·pinned commit·byte size·SHA256 목록은
[`comparison_sources.json`](../buildup/robotics/related_work/comparison_sources.json)의
`remaining_candidates_20260916.input_snapshot.files`다. Research 범위와 estimator는
[question record](../buildup/cross_domain/questions/tail-preserving-efficient-evaluation.md)가 소유한다.
Local snapshot은 ignored `runs/candidate_review/20260916/source/`에 있으며 Git만으로 payload가
전달되지 않는다. 같은 상위 폴더의 `source_manifest.json`과 함께 보존하거나 manifest의
immutable URL에서 복구해 각 파일의 크기·SHA256을 대조한다. Floating branch의 최신 JSON으로
대체하지 않는다. 선택 cohort는 legacy bundled 파일의 ID만 사용하고 값은 개별 model 파일에서 읽는다.

이 snapshot에는 source/aggregate-result 파일 12개만 있으며 weights나 개별 episode는 없다.
향후 study를 이전할 때에는 이 입력과 해당 study의 recipe·출력·실행 manifest를 함께 확인한다.
집계 표만으로 원 논문의 robot rollout을 완전히 재현할 수 있다고 보지 않는다. Snapshot 복구와
paper-result 보존 또는 실행 중인 실험의 resume에 필요한 artifact는 구분한다.

CD2의 CPU 실행 recipe·pinned base·command·mount·output/verification manifest는
[study README](../buildup/cross_domain/pilot_studies/cd2-evaluation/README.md#commands)가 소유한다.
Scientific code는 해당 image/container 안에서만 실행한다. 재실행 시 기존 출력을 덮지 않는
새 run ID를 사용하고, image를 새로 build할 경우 기존 tag를 덮지 않는 새 tag를 정한다.

### Episode source recovery

후속 LBM 입력·비교용 RoboArena metadata의 복구 목록은 같은 source record의
`cd2_followup_20260917.acquisition.files`다. Ignored cache는
`runs/cd2-review/20260917/`이며 그 안의 `acquisition.json`도 함께 보존한다.
Git에는 compact manifest만 들어간다. 각 manifest URL을 취득해 `bytes`와 `sha256`을
대조하며 N-SCORE commit 또는 RoboArena revision을 floating 최신 버전으로 바꾸지 않는다.

LBM `lbm_data.pkl`은 원본 archive이고 `data/LBM/Part2/` 및 `data/PC_LBM/Part2/` NPY는
mapping 대조 입력이다. Pickle을 host에서 load하지 않는다. 후속 container에서 명시적
hardware/task/policy/metric key로 읽고 정규화 manifest와 column 대조를 남긴다.
후속 Docker 검증에서 두 NPY 폴더 모두 progress임을 확인했다. Binary는 원본 pickle의
명시적 `success` field를 사용하며 폴더 이름으로 metric을 추정하지 않는다.
실행 recipe와 결과 owner는 [같은 study README](../buildup/cross_domain/pilot_studies/cd2-evaluation/README.md#episode-execution)다.

연구 결과 보존에는 기존 VLA-Arena 결과·source/config·검산이 계속 필요하다. 후속 관찰의
재개에는 이 LBM 입력과 recipe/output이 필요하며, 이것만으로 저자의 robot 실험 전체를
재현할 수는 없다. Cache가 작고 다음 관찰에 필요하므로 보존한다. 원격 URL과 local hash는
외부 backup 검증을 대신하지 않는다. 이번 episode 실행의 종료 container만 별도 정리했으며
image·dataset·source와 결과는 유지한다.

실행/복구 manifest는 [`episodes/artifacts.json`](../buildup/cross_domain/pilot_studies/cd2-evaluation/episodes/artifacts.json)이다.
실패 `runs/cd2-episodes/20260917_005800/`와 정정 `runs/cd2-episodes/20260917_010607/`를
함께 보존한다. 정정 run의 `source/`가 실제 실행 code/config snapshot이고 ignored row-level
JSONL·정규화 입력·검산·사후 진단은 Git만으로 전달되지 않는다. Tracked CSV는 compact
결과 보존용이며 raw 결과의 재검산을 대체하지 않는다. Dockerfile/lock으로 새 tag를 build한 뒤
새 output에서 실행하고 기존 파일을 덮지 않는다. Image ID·wheel hash·명령·mount·seed·
CPU mode·검증 및 cleanup 조건은 study README와 manifest를 따른다.

## Q4 Taskography Source Recovery

선택한 test 입력과 read-only source snapshot의 authoritative manifest는
[comparison_sources.json](../buildup/robotics/related_work/comparison_sources.json)의
`q3_q4_comparison_20260918.acquisition.files`다. `selected_inputs`가 고정 test 목록을
소유하고 [question record](../buildup/robotics/questions/task-relevant-spatial-state.md#first-observation)가
연구 설계를 소유한다. Ignored cache는 `runs/reserve_review/20260918/`이다.

복구 시 각 record의 immutable `url`을 `path`로 받고 `bytes`/`sha256`을 확인한다.
Git만으로 PDDL payload가 전달되지 않는다. 공식 full/test와 대응 `scrub_test`를 모두
보존하며 train의 `no_scrub` 출력을 대체 입력으로 쓰지 않는다. 실패한 `LICENSE` 요청은
`LICENSE.md`와 `LICENSE-CC-BY`의 성공한 취득으로 대체한 기록이다. 원본 notice를 보존한다.

Q4 실행 recipe, pinned environment, command, raw-output manifest와 cleanup 영향은
[study README](../buildup/robotics/pilot_studies/q4-planning/README.md#preservation-and-cleanup)와
[artifacts.json](../buildup/robotics/pilot_studies/q4-planning/artifacts.json)이 소유한다.
Goal-conditioned 후속의 새 run·baseline reference mount·검산·개별 container cleanup은
[follow-up recovery](../buildup/robotics/pilot_studies/q4-planning/README.md#follow-up-verification-and-recovery)와
같은 artifact manifest의 `goal_followup`을 따른다. 새 run만 복사하고 baseline reference를
누락하면 결과 비교·transfer 검산을 재현할 수 없다. Raw output의 `code/`는 실행 당시
snapshot이므로 현재 수정된 source와 구분해 보존한다.
Raw plan/trace·실패 run·creation receipt는 별도 이전 후 manifest 검증이 필요하다.
Compact summary만으로 full result reproduction이 완성되는 것은 아니다. Manifest의 Q3 local audit 항목은 기존 workspace
source/recipe의 read-only 확인이며 external simulator image 사용을 허용한 기록이 아니다.
데이터 삭제는 이번 작업에 포함하지 않았다.

## Q3 Selected Input Recovery

Q3의 첫 timestep 관찰이 사용하는 source/checkpoint 위치·immutable URL·SHA256/bytes는
[comparison_sources.json](../buildup/robotics/related_work/comparison_sources.json)의
`q4_followup_review_20260918.source_audit`와 `checkpoint`가 소유한다. 설계는
[Q3 question](../buildup/robotics/questions/physics-ranking-stability.md#selected-first-observation)을 따른다.

기존 workspace에서 취득한 ManiSkill source와 작은 joint PPO checkpoint만 read-only로
재사용한다. 과거 Q1/Q8 image나 output을 새 Q3 실행 결과로 간주하지 않는다. 새
[Q3 study README](../buildup/robotics/pilot_studies/q3-timestep/README.md)가 Docker
recipe/image/cache/output, build/run/verify command와 runtime 검증 상태를 소유한다.
Git에는 checkpoint bytes가 포함되지 않으므로 이전 또는 재취득 뒤 manifest를 대조한다.
현재 선택의 입력이므로 해당 source/checkpoint는 보존한다. 외부 backup 검증이나 삭제는 없다.

## Docker and Workspace Cleanup Review 2026-09-18

사용자가 지정한 image 여섯 개와 workspace의 dataset/folder를 읽기 전용으로 검토했다.
실제 image/container/file 삭제는 없다. 상세 snapshot과 729개 저장 결과/runtime hash 검사는
`runs/docker_cleanup/20260918_130610/audit.json`, 요약 로그는
`logs/20260918_130610_cleanup_review.log`에 보존했다. 지정 image를 참조하는 running
container와 workspace를 mount한 running container는 없다.

### Images and remaining container

| Image | 직접 참조 container | 판단 |
| --- | ---: | --- |
| `research3-cd2-episodes:v1` | 0 | 삭제 가능. 관찰 완료·현재 경로 보류, 결과/recipe/lock 보존 확인 |
| `research3-cd2-evaluation:v1` | 0 | 삭제 가능. 첫 관찰 완료, 결과/recipe/lock 보존 확인 |
| `research3-q14-real-keypoints:v1` | 0 | 삭제 가능. 실제 keypoint 관찰 완료·현재 경로 보류 |
| `research3-q4-planning:v1` | 0 | 삭제 가능. 두 관찰 완료·현재 경로 보류 |
| `research3-q3-timestep:v1` | 0 | 삭제 가능. 실행·검산 완료, 다음 작업은 연구 가치 비교. 가까운 GPU 재실행 편의를 원하면 선택적으로 유지 |
| `research3-q9-refresh:v2` | 1, exited | 보류. 아래 container의 생성 주체 확인 전 image를 강제 삭제하지 않는다. |

유일한 관련 container는 `3835659f18ae` / `research3-q9-dependencies-v2`, exit 0이다.
Entrypoint `pip`, command `freeze`, read-only root, mount/label 없음, filesystem diff 없음이다.
stdout의 10개 package가 보존된 `requirements.lock`과 일치하며 이번 audit에도 출력 사본을
보존했다. 기술적으로 유실될 실험 결과는 발견하지 못했지만 workspace 생성 기록을 찾지 못해
기존 09-16의 소유권 보류 판단을 유지한다. 이름/image만으로 삭제 대상으로 확정하지 않는다.
Image 목록의 `U`는 이 종료 container의 참조와 일치하며 실행 중이라는 뜻은 아니다.

Image 삭제는 host의 data/result를 삭제하지 않는다. 현재 결과 보존에는 image가 필수는
아니지만 다시 실행하려면 재빌드 또는 보관한 image가 필요하다. Recipe/lock/source는 보존돼
있으며 향후 registry 접근과 byte-identical rebuild를 보장한 것은 아니다. 공유 layer와
build cache 때문에 표시된 image 용량을 실제 회수량으로 합산하지 않는다.

### Regenerable file candidates

경로는 repository root 기준이며 아래 네 항목의 합계는 **746.98 MiB**다.

| 대상 | 현재 allocated size | 삭제 영향과 유지할 것 |
| --- | ---: | --- |
| `external/q8/maniskill.tar.gz` | 232.36 MiB | Source 중복 압축본. 이번에도 regular file 1,495개가 풀린 tree와 일치함을 확인했다. 풀린 ManiSkill source·source identity는 Q3 재빌드에 필요하므로 유지한다. |
| `runs/q1_v3/cache/.sapien/` | 225.76 MiB | 종료 연구의 PhysX runtime cache. 원본 결과는 유지하며 재현 시 동일 binary를 다시 확보한다. |
| `runs/q3/timestep/cache/` | 288.77 MiB | PhysX runtime, NVIDIA ComputeCache와 matplotlib font cache. Data/model/result가 아니며 재생성 가능하다. 다음 GPU 실행에는 재다운로드/JIT가 필요하다. `v1/`과 `jobs/`는 유지한다. |
| `buildup/robotics/pilot_studies/q10-contact-observability/__pycache__/` | 0.09 MiB | 재생성 가능한 Python bytecode. Source는 유지한다. |

Q1/Q3 PhysX binary는 같은 기록된 SHA256과 일치했다. Q3 cache는 이 workspace의 이번
실행이 별도 경로에 생성한 것이다. 다른 작업의 runtime cache나 simulator installation은
이 목록에 포함하지 않는다.

### Conditional data and model candidates

아래는 현재 보류한 연구의 큰 입력으로 **합계 12.720 GiB**다. 다음 문헌/투자 검토에는
즉시 필요하지 않지만 원본 추론·전체 재현에 필요하다. **외부 사본의 checksum/파일 구성을
검증한 뒤 삭제 가능**하며 이번에는 외부 backup을 확인하지 않았다.

| 대상 | 현재 allocated size | 삭제 영향 |
| --- | ---: | --- |
| `checkpoints/q7/smolvlm2-2.2b/model-00001-of-00002.safetensors`, `model-00002-of-00002.safetensors` | 8.370 GiB | 두 shard 모두가 한 모델이다. Q7 VLM 재추론에는 복원 필요. Config/tokenizer/index/취득 기록은 유지한다. |
| `datasets/q12/archives/input.zip`, `gt.zip` | 1.752 GiB | 상위 ZIP의 중복 member. 상위 ZIP을 유지하면 다시 추출할 수 있다. 09-15 byte identity 검증 기록은 유지하되 외부 backup을 대신하지 않는다. |
| `datasets/q12/3dsgrasp_ycb_train_test_split.zip` | 1.710 GiB | Full dataset archive. 위 inner ZIP까지 함께 제거하면 소규모 subset만 남는다. |
| `datasets/q12/3dsgrasp_model.pth` | 482.25 MiB | Shape completion 재추론에는 checkpoint 복원 필요. |
| `datasets/q14/dream/panda-3cam_realsense.archive` | 342.48 MiB | 선택한 24-frame 입력을 유지해도 전체 archive를 대체하지는 않는다. |
| `datasets/q14/dream/panda_dream_vgg_q.pth` | 84.78 MiB | DREAM detector 재추론에는 weight 복원 필요. YAML·selected 입력·취득 기록은 유지한다. |

### Preserve and inspection limits

`buildup/`, `docs/`, `.git/`, root Markdown, `logs/`와 위 cache를 제외한 `runs/` 원본 결과는
유지한다. Q3 입력인 `datasets/q8/`와 풀린 `external/q8/ManiSkill-*/`도 유지한다.
Q12 subset/geometry/BOP·manifest, Q14 selected/YAML, Q7 index/config/tokenizer를 유지한다.
Q6/Q7-UR5/Q9의 작은 입력은 backup 후 후순위 정리 후보이며 이번 주요 회수량에 더하지 않았다.

읽을 수 있는 workspace allocated size는 약 14.31 GiB다. Q1 `.nv` 및 Q11 v1/v2/v3
`cache/nvidia` 네 경로는 권한 때문에 내부를 읽지 못했으므로 해당 경로는 삭제 후보에서 제외했다.
Docker storage는 이 workspace 용량과 별도이며 전체 `datasets/`, `checkpoints/`, `runs/`,
`external/` 일괄 삭제를 권하지 않는다.

## Q15 Reward Observation Recovery

Q15의 Docker command·mount·lock·검산·cleanup은
[study README](../buildup/robotics/pilot_studies/q15-reward/README.md#runtime-and-recovery)가 소유한다.
Pinned ManiSkill source는 기존 workspace의 `external/q8/ManiSkill-a4a4f9272ad64b1564035874b605ceb687b63ed8/`를
read-only build context로 사용하며 pretrained checkpoint나 새 dataset은 사용하지 않는다.
`runs/q15/reward/`의 raw evaluation state, training checkpoints/config/log와 별도 cache는 ignored다.
결과 해석에는 compact summary와 raw evaluation이, 재평가에는 checkpoints/runtime이 필요하다.
학습 중간의 저장물은 policy weights이며 optimizer/RNG/environment를 포함한 exact-resume
snapshot은 아니다. Full reproduction은 pinned recipe/source와 기록된 seeds로 다시 학습한다.
외부 backup 검증 없이 raw outputs/checkpoint 삭제를 권하지 않는다. 장시간 작업은 timestamp
로그와 job record를 남기는 background launcher를 사용한다. 상태와 연구 판단은 study/TODO에 둔다.
v1의 friction 0.5 trace는 최초 writer의 suffix 처리로 `f0.json/.npz` 이름에 저장됐다.
조건 식별에는 metadata의 실제 배율·checkpoint와 manifest를 사용한다. Verifier는 이
경로를 지원하며 이후 writer는 `.5`를 유지한다. 실패한 verifier source도 raw output에
보존돼 있으므로 재검산에는 study의 수정된 verifier 또는 `verification_source/`를 쓴다.
선택한 [joint-position hold 후속](../buildup/robotics/pilot_studies/q15-reward/README.md#joint-position-hold-observation)은
기존 세 reward·세 seeds의 최종 checkpoint 9개를 입력으로 쓰므로 해당 weight와 config/hash,
Q15 recipe/image provenance를 유지한다. 새 출력은 별도 attempt로 보존하며 기존 v1을 덮지 않는다.
후속 실행은 `runs/q15/reward/hold_v1/`에 저장했다. [명령·mount·검산·cleanup](../buildup/robotics/pilot_studies/q15-reward/README.md#execution-2026-09-22)과
[compact results](../buildup/robotics/pilot_studies/q15-reward/hold/summary.json)를 따른다.
Raw에는 18개 trace와 source/lock/input/output manifest, 독립 verifier와 사후 진단이 있다.
`hold_job.py`는 기존 v1을 read-only로 mount하고 GPU run/CPU verify·diagnose를 별도 실행한다.
새 rollout은 fresh attempt를 요구하며 기존 `hold_v1`에 덮어쓰지 않는다. 분석 복구에는
두 manifest와 보존한 verifier/diagnosis source를 사용한다. 71개 artifact entry의 SHA256/size
대조 후 이 workspace에서 생성한 종료 container 3개만 정리했다. Raw·checkpoint·cache의
외부 복사는 미검증이며 container 정리가 payload 삭제 가능성을 뜻하지 않는다.


## Q16 Motion Observation Recovery

[Study README](../buildup/robotics/pilot_studies/q16-motion/README.md#runtime-and-recovery)가
CPU Docker recipe, pinned dependencies/source, mount, seed/split, command와 verification을
소유한다. 새 image `research3-q16-motion:v1`은 public Python base에서 빌드했고 기존
workspace의 pinned ManiSkill source를 read-only build context로 사용했다. GPU/Isaac 자산을
사용하지 않았다. Simulator와 model 실행은 모두 container 내부다.

`runs/q16/motion/`에는 dev1 실패 기록, dev2 기본 제어, train1 원본/collection,
fit1 checkpoints/validation curve, eval1 원본, verify1 결과, diagnosis1 그림/state animation,
jobs의 command/source snapshot/container inspection과 별도 cache가 있다. Timestamp log/exit는
job record가 가리키는 `logs/` 파일에 있다. Tracked compact JSON/CSV/그림과 Python/OS locks는
study folder에 복사했다. Final source만으로 dev1 오류를 재현하려면 실패 당시 source snapshot이
별도로 필요하다.

- **결과 보존:** Compact summary·episode table·diagnosis, raw state/force/action와 provenance 유지.
- **현재 관찰 재분석:** train1/eval1, fit1 모델과 verify/diagnose source, Docker runtime 유지.
- **전체 재현:** pinned source·recipe·locks로 build 후 development/collection/fit/evaluate/verify를
  fresh attempt에 실행한다. `job.py`의 기존 eval1/verify1 참조를 새 attempt에 맞출 때 변경을
  기록하며 기존 output은 덮어쓰지 않는다. Source availability와 bit-identical rebuild를
  보장한 것은 아니다.

`preservation.json`은 cleanup 전 918개 파일의 bytes/SHA256 기록이다. 외부 backup 검증을
대신하지 않는다. Cleanup은 생성 record·labels·mount·image·exited 상태가 확인된 이번
container 7개에만 적용됐으며 image/data/model/cache는 보존했다. 원본 삭제는 별도 외부
사본 검증이 필요하다. 자세한 ID와 결과는 study의 cleanup log 링크를 따른다.

후속 정책 적응 개발의 runtime/data 계획은
[study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#method-development-2026-09-23)에 있다.
새 output은 기존 결과와 분리한다. 아래 후속 기록 이전에는 recipe·command·runtime이
구성되지 않았다.
위 복구 명령은 완료된 첫 관찰에만 적용되며 후속 prototype 실행 명령으로 해석하지 않는다.

후속 prototype의 workspace image를 새로 빌드했다. 별도 Dockerfile/command, 새 data/model
split과 output은 [첫 adaptation 기록](../buildup/robotics/pilot_studies/q16-motion/README.md#first-adaptation-prototype-2026-09-23)을
따른다. `runs/q16/motion/`과 `runs/q16/adaptation/`은 서로 다른 복구 경로다.

Q16 adaptation의 첫 CPU study는 [검산·결과](../buildup/robotics/pilot_studies/q16-motion/README.md#adaptation-results-2026-09-23)까지
완료했다. Workspace image `research3-q16-adaptation:v1`의 exact ID와 pinned source/lock,
`collect1`, `fit1/fit2`, `eval1/eval2/eval3`, `verify1/verify2/verify3`, 진단, command·mount·
source snapshot·log·exit의 재개 경로는 study README 및 `runs/q16/adaptation/jobs/`에 있다.
Tracked compact result는 `adaptation_first.json`, `adaptation_revision.json`,
`adaptation_summary.json`, `adaptation_episodes.csv`다. Raw trace/checkpoint/source snapshot은
ignored `runs/q16/adaptation/`에 남으며 외부 backup은 검증하지 않았다.
`preservation.json`의 2,275개 file bytes/SHA256 확인 후 이 작업의 종료 container 11개만
개별 삭제했다. Image·data·model·cache와 다른 작업 자산은 보존했다. 결과 보존에는 compact
summary/episode table과 raw trace가, 현재 방법 수정에는 `fit2` checkpoint와 실행 source가,
전체 재현에는 pinned Docker recipe/dependency/source 및 수집부터 검산까지의 job command가
필요하다. 기존 `motion/` 첫 관찰과 adaptation 결과의 분모·모델은 섞지 않는다.

### Q16 PushCube continuation and four-image review (2026-09-23)

Q16의 별도 `PushCube-v1` collision-only CPU study는 [방법·두 평가·복구](../buildup/robotics/pilot_studies/q16-motion/README.md#pushcube-extension-2026-09-23)가 소유한다. 새 `Dockerfile.push`는 pinned public Python base와 ManiSkill commit `a4a4f9272ad64b1564035874b605ceb687b63ed8`에서 `research3-q16-push:v1` (`sha256:24d557c58ecd8fc6d5fe050a2219412c42d0d0a5cad432c60f8761a15639b9b1`)을 빌드했다. 지정된 기존 연구 image를 base/runtime으로 참조하지 않았다. `runs/q16/push/jobs/`의 command, source snapshot/hash, image inspection, mounts, CPU device와 timestamp `logs/*_q16_push_*.log/.exit`를 따라 stage별로 복구한다. `collect1`, `fit1`, `eval1`/`verify1`, `eval2`/`verify2`는 독립 output이다. 첫 평가는 192 episodes, 수정 후 평가는 새 초기 상태 256 episodes를 검산했다. Compact 결과는 study 폴더 `push_summary.json` 및 `push_episodes.csv`, raw trace/checkpoint는 ignored `runs/q16/push/`이다. `preservation.json`에 1,380개 file bytes/SHA256를 보존했고 외부 backup은 확인하지 않았다. 이번 작업에서 생성한 종료 container 9개만 생성 기록·label·mount·image·상태를 대조해 개별 삭제했다. Image와 다른 작업의 container/asset은 유지했다.

사용자가 지정한 image 네 개는 tag/ID를 read-only 검사했고, 각 exact image ID를 참조하는 container는 `docker ps -a --filter ancestor=<ID>`에서 모두 0개였다. Q15 reward (`3ae1cf37d7c1`)와 Q3 timestep (`3b51ec5533d6`)은 연구 경로가 보류됐고 결과/recipe가 bind mount와 repository에 남아 있어 **결과 보존 목적에서는 먼저 정리할 후보**다. Q16 motion (`72073ab3d95d`)과 adaptation (`a8d5594837e8`)도 완료된 첫 prototype 결과를 읽는 데는 필요하지 않으나, 가까운 Q16 재실행의 편의 때문에 선택적으로 유지할 수 있다. 새 push 실험은 네 image 어디에도 의존하지 않는다. 네 image 모두 정확한 runtime identity의 외부 export 검증은 없으며 recipe/source/lock 재빌드가 동일 image ID를 보장하지 않는다. Image 삭제는 별도 승인을 받지 않았고 실행하지 않았다. 표시된 image 크기는 공유 layer/build cache 때문에 실제 회수량과 다르다.

### Q16 contact-task audit and demonstration compatibility (2026-09-23)

The [contact-task study](../buildup/robotics/pilot_studies/q16-motion/README.md#contact-task-comparison-and-selection) uses its own `Dockerfile.task_audit` and `research3-q16-task-audit:v2` image (`sha256:fb21fff0c73fffcaf618cfabe6ec65a923d7c90aa89120ea1e2cc866428cdf08`) from the pinned public Python base and ManiSkill commit `a4a4f9272ad64b1564035874b605ceb687b63ed8`. `runs/q16/task_audit/jobs/` contains each build/smoke/diagnose/verify/demo command, source snapshot/hash, image ID and Docker inspection; CPU logs/exits are `logs/*_q16_task_audit_*.log/.exit`. `verify2` checked 48 last-controller task traces. Compact summary, episode table and eight-demo replay are `task_audit_summary.json`, `task_audit_episodes.csv`, and `task_audit_demo.json` in the study folder. Earlier attempts and raw NPZ/HDF5 remain under ignored `runs/q16/task_audit/`.

The official PushT ZIP is `runs/q16/task_audit/demos/PushT-v1.zip` (35,715,188 bytes; SHA256 `c2960e5d5dcc99d04fb4506b8a6bb8d8232b54f75e9f4fd0462189256f84e851`) from dataset commit `bedb31208d5a03f343c2fbe329744856d7869724`. Its extracted `pd_ee_delta_pos` HDF5/JSON lies in `demos/extracted/`. Demo metadata names ManiSkill `baab60ede2e89167c1b7aaed41a9aa8e690a9d1e`/`physx_cuda`; action replay in the present CPU variant failed for eight episodes even when the recorded initial physical state was restored. The ZIP can be redownloaded from the pinned dataset commit; do not treat it as a verified policy-training baseline in this runtime. Source/backend-matched replay is the next recovery task. No external artifact backup is verified. `preservation.json` hashes 246 local files (cache excluded); `task_audit_cleanup.py` checked label, image, mounts and exited status before deleting only this audit's 12 containers. Images, other containers, volume and cache were untouched. For result preservation retain the compact tables plus raw traces; for resume also retain the ZIP/HDF5 and job snapshots; for full reproduction retain Docker recipe/locks, source revisions, pinned dataset URL and command receipts.

### Q16 PushT source-matched compatibility and imitation route (2026-09-25)

The [study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#pusht-demonstration-compatibility-2026-09-25) records the source/backend diagnosis, exact split, comparison and limits. The source archive for ManiSkill commit `baab60ede2e89167c1b7aaed41a9aa8e690a9d1e` is `external/q16/ManiSkill-baab60ede2e89167c1b7aaed41a9aa8e690a9d1e.tar.gz` (217,794,515 bytes, SHA256 `db7f1fb49038a1a11612876022ba31fdb8c9095e4e3f4a408728abf8b821f49e`); the extracted source is read-only input. The source archive download/extract commands and exits are `logs/*_q16_source_*.{log,exit}`. Runtime HDF5, JSON and official PPO checkpoint are in `runs/q16/task_audit/demos/extracted/`; the original ZIP and dataset commit/hash are described in the prior contact-task subsection. Do not delete local source/dataset/checkpoint without a verified external copy or working re-download route.

New workspace-owned CPU image `research3-q16-compat-cpu:v1` has ID `sha256:48d17bb6a8df489b03d32ccdf22c64b1432caafa3ca8ee0df85d4fdcce0de6fc`; CUDA image `research3-q16-compat-gpu:v1` has ID `sha256:8dc6f2ae072476b71d03cb5c26e9f6500bcb6e6dfd41e45d77d5848595785d39`. Both start from the pinned public Python base and install exact-source SAPIEN `3.0.0b1`. [CPU Dockerfile](../buildup/robotics/pilot_studies/q16-motion/Dockerfile.compat_cpu), [CUDA Dockerfile](../buildup/robotics/pilot_studies/q16-motion/Dockerfile.compat_gpu), direct [requirements](../buildup/robotics/pilot_studies/q16-motion/requirements.compat.lock), exported full [CPU lock](../buildup/robotics/pilot_studies/q16-motion/installed.compat_cpu.lock) and [CUDA lock](../buildup/robotics/pilot_studies/q16-motion/installed.compat_gpu.lock) preserve package identity. CUDA uses explicit `--gpus all` and source mount at `/opt/ManiSkillNative:ro` for the unmodified native task; collision-only GPU uses the copied source stripped of visual geometry only. Host scripts `compat_job.py`/`compat_gpu_job.py` orchestrate Docker and record timestamped source snapshots, exact commands, mounts, image IDs, device, exit and inspected container identity under `runs/q16/compat_{cpu,gpu}/jobs/`. No preexisting Docker image/container is a dependency.

GPU SAPIEN downloaded `105.1-physx-5.3.1.patch0` on the one-time `native_bootstrap` Docker bridge run into `runs/q16/compat_gpu/cache/.sapien/physx/`; later CUDA runs used `--network none`. This cache is necessary to resume GPU runtime without network, but can be regenerated by a separately recorded Docker download. Source and demonstrations are read-only mounts, outputs and cache isolated in ignored `runs/q16/compat_cpu/` and `runs/q16/compat_gpu/`. The source-matched CPU replay/verify/audit and native/collision CUDA replay/verify plus official helper logs are recorded there. The `compat_bc.py` `data1/fit1/eval1/verify1` and `data_full1/fit_full1/eval_full1/verify_full1` stages preserve reconstructed state/action data, two MLP checkpoints, 72 policy trace NPZ files, per-trace hashes and verification. [Compact summary](../buildup/robotics/pilot_studies/q16-motion/compat_summary.json) records results and image/lock identities; it does not replace raw data for case reanalysis.

For paper-result preservation, keep the compact summary, split/fit/evaluation manifests, and raw evaluation traces; these are exploratory, not paper results. For immediate resume, retain the two exact images, PhysX cache, source/HDF5/checkpoint and job snapshots. For full reproduction, retain Dockerfiles/locks, pinned source and dataset fetch routes, exact commands, mounts and original/derived artifact hashes; Docker rebuild alone does not guarantee identical image ID or bitwise GPU contact trajectories. Verify file counts, trace hashes, threshold labels, split/seed disjointness and the saved image IDs before deletion or transfer. `runs/q16/compat_gpu/preservation.json` records 453 local file hashes/sizes from `compat_preserve.py` (source archive, demo payload, cache, jobs, traces and logs); it is not an external backup. `compat_cleanup.py` checked exact creation records, labels, image, mounts and exited state before individually removing eight CPU and fifteen GPU completed run containers, with dated logs under `logs/*_q16_compat_*_cleanup.log`. Two temporary lock-export containers used `--rm`; no compatibility-labelled container remains. Images, caches and other studies' containers were not deleted. No external copy of current raw outputs or exact images has been verified.

### Q16 action-branch diagnostic and image review (2026-09-26)

[Study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#paired-action-diagnosis-2026-09-26-exploratory-protocol-before-execution) records the exploratory protocol, failed checks and decision. The branch study continued on the same workspace-owned native CUDA image `research3-q16-compat-gpu:v1` by exact ID `sha256:8dc6f2ae072476b71d03cb5c26e9f6500bcb6e6dfd41e45d77d5848595785d39`, pinned native source and SAPIEN/PhysX cache. From the repo root, `python buildup/robotics/pilot_studies/q16-motion/compat_branch_job.py fit` completed and `diagnose branch1`, `diagnose branch2`, `diagnose branch3` each failed a paired-state/repeatability check. The host launcher starts Docker in the background with explicit `--gpus all`, no network, read-only `/study`, `/previous`, `/demos`, `/opt/ManiSkillNative` mounts, and workspace-only writable `/output`/PhysX cache. Exact command, working directory, image, source hashes, mounts, logs, exits and container inspection are in `runs/q16/branches/jobs/`; `logs/*_q16_branches_*.log/.exit` are the bounded outputs. `validate` was not run because no valid `branches.json` was produced. Fit checkpoint/manifest and the two fresh BC traces plus selected physical/controller snapshot remain in ignored `runs/q16/branches/`. The predictor's validation RMSE is not an action-value result.

`python buildup/robotics/pilot_studies/q16-motion/compat_branch_preserve.py` locally verified 46 files/349,414 bytes in `runs/q16/branches/preservation.json`, including logs and the cleanup receipt. No external backup has been verified. `compat_branch_cleanup.py` individually removed four exited containers after comparing creation record, exact container/image ID, workspace/study labels, mounts, logs and exits; no Q16 branch container remains. It did not remove the image, source, cache, dataset or other workloads. Reusing the exact GPU image still requires preserving that image; rebuilding from the pinned recipe/locks does not guarantee the same image ID or PhysX contact path.

The user-listed seven Q16 image IDs were inspected read-only; each had zero direct descendant containers at inspection. Prior completed routes `research3-q16-adaptation:v1`, `research3-q16-delay:v1`, `research3-q16-push:v1`, `research3-q16-task-audit:v1`, `research3-q16-task-audit:v2` and `research3-q16-compat-cpu:v1` could be removed **for result preservation** while their bind-mounted results, source, recipes and locks remained; immediate exact-image rerun would be lost. At that stage, `research3-q16-compat-gpu:v1` was retained for the then-current Q16 branch. The later four-image review in this runbook supersedes that immediate-resume recommendation. No listed image was deleted. Displayed Docker image sizes share layers, so their sum is not recoverable disk space.

### Q16 delayed-object observation continuation (2026-09-23)

[지연 관측 study와 결과](../buildup/robotics/pilot_studies/q16-motion/README.md#delayed-object-observation-2026-09-23)는 별도 CPU Docker recipe/image `research3-q16-delay:v1` (`sha256:d08597a264007e3254686db6fb7cc8659b2ef1cb9ac00387df06d5dbe72fd421`)를 사용했다. Base는 pinned public Python image이고 ManiSkill source commit은 `a4a4f9272ad64b1564035874b605ceb687b63ed8`이다. 기존 연구 image를 base나 runtime으로 사용하지 않았다. `runs/q16/delay/jobs/`는 stage별 exact command, image inspection, source hash/snapshot, read-only `/study`, writable `/output`, 별도 cache mount와 CPU mode를 기록한다. Build/collect/fit/evaluate/verify의 timestamp logs/exit은 `logs/*_q16_delay_*.log/.exit`이다. `collect1` 시연 160개, `fit1` checkpoint/installed Python·OS locks, `eval1`의 192 trace, `verify1`의 checksum/지연 규약/native 판정 검산을 보존했다. Compact 요약과 episode table은 study folder의 `delay_summary.json`/`delay_episodes.csv`; raw ignored output은 `runs/q16/delay/`이다. `preservation.json`은 829개 파일의 bytes/SHA256를 기록하고 외부 backup은 미검증이다. 이 작업의 종료 container 다섯 개만 creation record·label·image·mount·status를 대조해 개별 삭제했다. Image와 타 작업의 container/volume/cache는 유지했다. 원본 결과 보존, 현재 실행 재개, exact image identity 재현은 서로 다른 보존 목표이며 recipe rebuild만으로 동일 image ID는 보장되지 않는다.

### Q16 repeatable 2D contact-action route (2026-09-27)

[Study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#alternative-contact-task-assessment-2026-09-26-protocol-before-execution) records the protocol, results and claim boundary. This route uses workspace-owned CPU image `research3-q16-pusht-repeat:v1` (exact ID `sha256:4b57a83527763027be3a4b4b1919b75a12248d294bd56ed5b257cfbc5cef6345`) from [Dockerfile.repeat](../buildup/robotics/pilot_studies/q16-motion/Dockerfile.repeat), [direct dependency pins](../buildup/robotics/pilot_studies/q16-motion/requirements.repeat.lock) and the installed lock `runs/q16/pusht_repeat/installed.repeat.lock` (SHA256 `f7bc0a33c3f4c0dd1c5b894af633f5b339f408a9de6f2acde1e97da6f2acde1`). The original Diffusion Policy `pusht.zip` is `runs/q16/pusht_repeat/demos/pusht.zip` (30,988,725 bytes; SHA256 `63d52a114a3f010861f0181309d165b7d69133ccae426ece2fc94caed147bdf9`). It has 206 episodes and 25,650 aligned state/action rows. Do not mix this 2D dataset or its action/coverage scale with the separate ManiSkill `PushT-v1` HDF5 route.

From repository root, `python buildup/robotics/pilot_studies/q16-motion/repeat_job.py <stage>` launches `build`, `fetch`, `lock`, `probe`, `verify`, `fitbc`, `evalbc`, `verifybc`, `failureprobe`, and `failureverify` in their recorded dependency order. The host launcher uses stdlib for download/orchestration; all simulator, model and verifier imports execute in Docker. Job JSON and per-job immutable source snapshots under `runs/q16/pusht_repeat/jobs/` contain exact command, image ID, working directory, read-only `/study` source mount, isolated `/output` write mount, CPU mode, timestamps, log and exit. Bounded logs are `logs/*_q16_pusht_repeat_*.log/.exit`. Raw results are under `probe1/`, `bc_fit1/`, `bc_eval1/`, `failure_branch1/`; each verification JSON passed its hash, state, split, contact and native-label checks. The selected 48007/48010 branches are exploratory development cases.

For result preservation keep the study's compact interpretation plus original ZIP, fit/evaluation manifests, model and branch traces; current resume also benefits from the exact image and all job/source snapshots. Full reproduction needs the pinned base and dependencies, original data, exact stage commands and fresh output names; rebuilding need not reproduce the exact image ID. `runs/q16/pusht_repeat/preservation.json` locally verified 151 files/31,812,966 bytes including original data, raw traces, model, jobs, logs and cleanup receipt. There is no verified external backup, so do not delete these payloads on the basis of this local hash manifest. `repeat_cleanup.py` removed only eight exited containers created by this study after exact ID/image/label/mount/log/exit checks; receipt: `logs/20260927_000430_q16_pusht_repeat_cleanup.log`. The image, data, model and other Docker assets remain.

### Q16 released low-dimensional Diffusion Policy route (2026-09-27)

The [study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#released-low-dimensional-policy-compatibility-2026-09-27-protocol-before-execution) records the compatibility contract, seed-level results, branch decision and limits; [compact verified summary](../buildup/robotics/pilot_studies/q16-motion/dp_reference_summary.json) indexes each raw trace. Official Diffusion Policy source commit is `5ba07ac6661db573af695b419a7947ecb704690f`; archive `external/q16/diffusion_policy-5ba07ac6661db573af695b419a7947ecb704690f.tar.gz` is 13,081,804 bytes, SHA256 `ce530dbf17f099b29945abf1fdced97be5b7ad38772f93ecea4e8e9a00b65931`. The public low-dimensional Push-T checkpoint at `runs/q16/dp_reference/checkpoint/epoch=0550-test_mean_score=0.969.ckpt` is 1,044,185,793 bytes, SHA256 `f804e16575e261fa0b7e981da3f67741fc8517817734320d550e43a4182bf876`. The score embedded in the filename is an external claim. Neither raw checkpoint nor source archive is Git-tracked or externally backed up.

The isolated v1 image `research3-q16-dp-reference:v1` has exact ID `sha256:0aa82464b3bff8483621c2a432305dcc5e7b486d1e460052c7b579a2291f96c0`. Its keypoint import required `matplotlib`; the corrected workspace-owned v2 image `research3-q16-dp-reference:v2` has ID `sha256:e7de793ef15f41922fc4851d42d5bf2c386783c61a6b22c0a83ac09dd5e455ed`. The [public-base recipe](../buildup/robotics/pilot_studies/q16-motion/Dockerfile.dp_reference), [workspace-parent patch](../buildup/robotics/pilot_studies/q16-motion/Dockerfile.dp_reference_patch), [direct pins](../buildup/robotics/pilot_studies/q16-motion/requirements.dp.lock) and Docker-exported full `runs/q16/dp_reference/installed.v2.lock` (SHA256 `e75ffa921bf6925f3f5b217a3f5fcf2f7ae28037ede8d81f34fad8b73b8a5208`) preserve the dependency contract. The historical v1 build job snapshot has the original direct lock before `matplotlib` was added; the current direct lock describes the corrected runtime. v1 was created within this study from the pinned public Python base, not from a preexisting external research image. Keep v2 for immediate evaluation rerun; the v1 image is needed only for exact historical schema inspection or rebuilding the patch path. Rebuilding may not reproduce exact IDs or bitwise GPU trajectories.

From the repository root, [host launcher](../buildup/robotics/pilot_studies/q16-motion/dp_job.py) runs `build_patch`, `parity`, `evaluate`, `verify`, `branch`, `branchverify`, `lock` after the already recorded v1 `build` and `inspect` stages. Start each only after predecessor exit/output verification; use fresh output names rather than overwrite old `inspect1/parity1/eval1/branch1`. The stage records under `runs/q16/dp_reference/jobs/` contain exact source snapshots, source/checkpoint hashes, image ID, command, working directory, read-only `/study`, `/source`, `/checkpoint`, `/previous` mounts, writable `/output`, CPU/GPU mode, logs and exits. Evaluation/branch explicitly use `--gpus all`; all runtime containers use `--network none`. `logs/*_q16_dp_reference_*.log/.exit` are bounded job logs. Inspect/parity/evaluation/branch manifests and 24 NPZ traces are in ignored `runs/q16/dp_reference/`; verifiers replayed all 24 in the source environment. One failed patch build used an unresolvable local digest reference; a later patch build uses the locally verified v1 ID, with both attempts logged. One branch verifier attempt found an intended-versus-float32-executed target mismatch; the repaired verifier checked the actual quantized target and passed, with both attempts logged.

For result preservation, keep the compact summary plus source/checkpoint identity, evaluation/branch JSONs and raw NPZs. For current resume, retain v2, checkpoint, extracted source, prior ridge BC model in `runs/q16/pusht_repeat/bc_fit1/ridge.npz` and job snapshots. Full reproduction additionally requires both Docker recipes, direct/full locks, source archive, exact download URL, checkpoint hash, ordered commands and the previous BC dataset/model recipe if repeating that contrast. `runs/q16/dp_reference/preservation.json` locally verified 179 files/1,058,825,580 bytes, including the final cleanup receipt; no local manifest proves an external copy. `dp_cleanup.py` checked creation records, exact container/image IDs, labels, mounts, exited state and preserved logs before removing only this route's eight containers (`logs/20260927_111824_q16_dp_reference_cleanup.log`). Other containers/images/caches were untouched. Do not delete the raw checkpoint, source, traces or prior BC model before verifying a separate backup or working re-download.

### Q16 observation-matched policy continuation and image review (2026-09-27)

The [study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#observation-matched-policy-continuation-2026-09-27-exploratory-protocol-before-execution) records the fixed comparison, two input-audit failures, protocol revision, verified table and claim boundary. [Compact continuation manifest](../buildup/robotics/pilot_studies/q16-motion/dp_continuation_summary.json) contains per-seed success, coverage, intervention/cost, source/data/model hashes and replay verification. The original `pusht.zip` and prior action-conditioned 32-neighbor model stay in `runs/q16/pusht_repeat/`; their bind-mounted files, **not** the old CPU image, are inputs to this continuation. The original source and 1,044,185,793-byte EMA checkpoint remain at the paths and hashes in the preceding subsection. The fixed update used the official stored-keypoint schema: `runs/q16/dp_reference/traincontract1/dataset.npz` SHA256 `fb67ce41d3f032cf70bb97120a246ded9def43d56e133f5b441038b3d2ce47f8`. Its 261,035,827-byte `finetune1/checkpoint.pt` has SHA256 `68ba7e02df70ee261bf9ac874c506185366219125d11fd46c2041213fbd488bd`. Neither is externally backed up.

From the repository root, `python buildup/robotics/pilot_studies/q16-motion/dp_job.py <stage>` launches Docker and records exact command, source snapshot/hash, pinned image ID, mounts, CPU/GPU mode, logs and exit under `runs/q16/dp_reference/jobs/` and `logs/*_q16_dp_reference_*.log/.exit`. The recorded order was `obsaudit` (failed original strict keypoint/state check), `obsresolve` (failed proposed state-derived adapter), `traincontract`, `finetune`, `compare`, `compareverify`; the first audit had a diagnostic rerun. `compare` evaluated 64 fresh-seed traces, and `compareverify` passed independent native replay, paired initial/prefix, observation-only gate, candidate and threshold checks with maximum replay drift 6.66e-16. Raw data and manifests are in ignored `runs/q16/dp_reference/{observation1,observation2,traincontract1,finetune1,compare1}/`. Use new output directories for any rerun; prior failed and completed artifacts are historical evidence. The host only orchestrates Docker and hashes artifacts.

For **result preservation**, keep the compact manifest, input/fit/evaluation/verification JSONs, raw NPZs and checkpoint/source identities. For **immediate resume**, retain the exact v2 image, checkpoint, original source, prior model and all job snapshots. For **full reproduction**, retain the two Docker recipes, direct/full dependency locks, pinned source/data/checkpoint download paths and hashes, and ordered Docker commands. `dp_preserve.py` locally reverified 395 files/1,324,005,909 bytes including source archive, checkpoint, raw outputs, source snapshots, logs and cleanup receipt; `runs/q16/dp_reference/preservation.json` is a local integrity manifest, not an external backup. `dp_cleanup.py` matched creation records, exact IDs, image, labels, mounts, log/exit and exited state before individually removing only this continuation's seven containers (`logs/20260927_135754_q16_dp_reference_cleanup.log`). Other containers and images were untouched.

The four user-listed image IDs were inspected again after cleanup; no container refers to any of them. `research3-q16-compat-gpu:v1` (`8dc6f2ae0724`) and `research3-q16-pusht-repeat:v1` (`4b57a8352776`) are **deletion candidates for preserving completed results**, because current manifests/data are bind-mounted and the next Can route needs its own runtime; deleting either loses immediate exact-image rerun of its old route. `research3-q16-dp-reference:v1` (`0aa82464b3bf`) is a conditional candidate: v2 already exists, but its patch Dockerfile names v1 as its build parent, so deleting the v1 tag complicates exact patch-path rebuilding and may reclaim little shared-layer space. **Keep** `research3-q16-dp-reference:v2` (`e7de793ef15f`) for current Q16 reruns. No image was deleted, retagged or pruned. Do not confuse deleting an image with deleting the unbacked-up source, dataset, model or traces.

### Q16 Can PH v1.5 metadata audit (2026-09-27)

The [study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#3d-can-route-feasibility-2026-09-27-exploratory-protocol-before-data-access) records the question, exact schema, version mismatch and next investment decision. The only downloaded Can payload is `runs/q16/can_audit/data/low_dim_v15.hdf5`, from `robomimic/robomimic_datasets` revision `74fa018461f479cd9fd15b924a16103012096203`, path `v1.5/can/ph/low_dim_v15.hdf5`; it is 46,889,752 bytes with SHA256 `3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962`. Fetch with [resumable script](../buildup/robotics/pilot_studies/q16-motion/can_fetch.sh); successful tmux log/exit `logs/20260927_141150_q16_can_fetch.*`. No external backup is verified. The 200 demonstrations expose 23D policy observation, 7D actions, 71D simulator state and per-episode XML; raw schema is ignored `runs/q16/can_audit/schema1/assessment.json`. The older released checkpoints do not have a verified v1.5.1 runtime contract.

The separate workspace-owned metadata image `research3-q16-can-schema:v1` has exact ID `sha256:bddee4d7aef95f0c9e3452c135acd912e71e77859249fa94fc39500b52f668d6`, built from a pinned public Python base with [Dockerfile](../buildup/robotics/pilot_studies/q16-motion/Dockerfile.can_schema) and [direct pins](../buildup/robotics/pilot_studies/q16-motion/requirements.can_schema.lock); its Docker-exported full lock is `runs/q16/can_audit/installed.can_schema.lock`. The [checker](../buildup/robotics/pilot_studies/q16-motion/can_schema.py) ran CPU-only with `--network none`, read-only `/study` and `/data` mounts, isolated `/output`, `--rm` and workspace/study labels. An independent [per-episode verifier](../buildup/robotics/pilot_studies/q16-motion/can_obs_verify.py) confirmed that all four 23D policy keys occur with matching row counts in both `obs` and `next_obs` for every one of the 200 demonstrations. Successful build/schema/observation logs/exits are `logs/20260927_141153_q16_can_build.*`, `logs/20260927_141230_q16_can_schema.*` and `logs/20260927_141808_q16_can_obs_verify.*`. Exact fetch/build/run commands, source tag commits (`robomimic v0.5.0` `ae5799f0fae05c4559ee1f9645b0f77eb5251929`, `robosuite v1.5.1` `51cc01785bab80ffeed20da15e67d7dd4140e76a`), image identity and 18 hashed input/source/output/lock/log files are in `runs/q16/can_audit/manifest.json`. Initial detached-shell attempts at 14:08 did not persist and have logs but no exit; the tmux jobs completed. All audit containers exited and were automatically removed by `--rm`; no other container/image/data was changed or deleted. This is a metadata audit, not simulator replay or policy reproduction. For immediate resume retain the exact image and HDF5; for full reproduction retain the Dockerfile/locks, source and dataset revisions, fetch script, command manifest and data SHA. Re-download is possible by pinned path but has not been tested after deletion.

### Q16 Can PH bounded action replay (2026-09-27)

The [study record](../buildup/robotics/pilot_studies/q16-motion/README.md#can-action-replay-protocol-2026-09-27-before-simulator-execution) owns the frozen criterion, two-episode result and decision. `runs/q16/can_replay/manifest.json` records exact source/data revisions, workspace-only image identity, fetch/build/run commands, read-only mounts, CPU mode, failed-attempt receipts, 39 file hashes and verification command. Source archives are `external/q16/robomimic-ae5799f0fae05c4559ee1f9645b0f77eb5251929.tar.gz` and `external/q16/robosuite-51cc01785bab80ffeed20da15e67d7dd4140e76a.tar.gz`, fetched by [script](../buildup/robotics/pilot_studies/q16-motion/can_replay_fetch.sh). The pinned dataset is the 46,889,752-byte HDF5 described above. The [Dockerfile](../buildup/robotics/pilot_studies/q16-motion/Dockerfile.can_replay) builds `research3-q16-can-replay:v2`, exact ID `sha256:7025e5c31a23becfd3d8447fd0e22c5b20f47909a7ae659acd9f226ca04e8d10`, from public Python and pinned robosuite source; direct Python pins are [here](../buildup/robotics/pilot_studies/q16-motion/requirements.can_replay.lock), installed Python/OS locks are `runs/q16/can_replay/installed.can_replay.{lock,os.lock}`. Robomimic v0.5.0 reset/replay files are pinned references in the image, not imported as a package, because its environment wrapper imports a CLIP loader for this language-free task. The canonical completed run/exit is `logs/20260927_151002_q16_can_replay_groups.*`, with row data `runs/q16/can_replay/replay6/result.json`; joint mapping is `runs/q16/can_replay/state_map.json`. Run [result verification](../buildup/robotics/pilot_studies/q16-motion/can_replay_verify.py) on the host; it reads JSON only and does not import the simulator. The v1 image is a failed build artifact lacking packaged robosuite assets; retain v2 for immediate exact-image rerun. All run, mapping, lock-export and permission-repair containers used workspace labels and `--rm`; no matching container remains and no other container was touched. The source archives, dataset and row results have no verified external backup; image deletion does not preserve them, and deleting them requires separate transfer verification.

### Q16 same-state action-selection continuation (2026-09-27)

[Study owner](../buildup/robotics/pilot_studies/q16-motion/README.md#same-state-action-selection-contrast-2026-09-27-exploratory-protocol-before-execution) contains the candidate rule, table and claim boundary. This continuation reuses the exact workspace-owned CPU image `research3-q16-pusht-repeat:v1` (`sha256:4b57a83527763027be3a4b4b1919b75a12248d294bd56ed5b257cfbc5cef6345`), the pinned `pusht.zip`, the previous ridge checkpoint and saved failure traces. It adds `repeat_action_model.py`, `repeat_action_contrast.py`, and `repeat_action_verify.py` as read-only source snapshots per job. From the repository root, run `python buildup/robotics/pilot_studies/q16-motion/repeat_job.py model`, then `contrast`, then `contrastverify`, each only after its predecessor's exit/output check and using a fresh output name if rerunning. All model/simulator imports and checks execute in Docker, with CPU, `--network none`, read-only `/study` source and workspace-only writable `/output`. Exact commands, source SHA256, image/container identity, mounts, stage status and log/exit paths are in `runs/q16/pusht_repeat/jobs/` and `logs/*_q16_pusht_repeat_*`.

Outputs are ignored `runs/q16/pusht_repeat/fit_model1/{model.npz,fit.json}` and `contrast1/{assessment.json,verification.json,*.npz}`. The verifier passed for 12 candidate traces and two repeated BC controls; neither source ZIP nor earlier evaluation is overwritten. `repeat_preserve.py` locally reverified 215 files/32,839,509 bytes in `runs/q16/pusht_repeat/preservation.json`, including old/new raw artifacts, source snapshots, logs and cleanup receipts. This is **not an external backup**. For immediate resume retain the exact image, ZIP, ridge/model checkpoints and all job records; for full reproduction retain the Dockerfile, direct/full dependency locks, pinned data URL/hash and source snapshots. Result interpretation also needs the raw branch traces, not only the compact README table. `repeat_cleanup.py` checked exact job-created container IDs, labels, image, mounts, log/exit and exited status before removing only the three containers from this continuation; receipt `logs/20260927_001755_q16_pusht_repeat_cleanup.log`. Other images, containers, caches and payloads were not removed.
