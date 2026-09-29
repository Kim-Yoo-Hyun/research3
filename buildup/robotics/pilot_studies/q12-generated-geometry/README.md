# Generated Geometry Readiness

Updated: 2026-09-14 · Q12 deferred; BOP and Google 16k frozen outcomes retained

Runtime 정리·복구 조건은 [Docker cleanup assessment](../../../../docs/reproducibility.md#docker-cleanup-assessment--2026-09-14)를 따른다. Image 실제 삭제는 없다.

Dataset/checkpoint의 [2026-09-16 정리 검토](../../../../docs/reproducibility.md#workspace-file-cleanup--2026-09-16)는
대형 ZIP 세 개와 checkpoint를 외부 backup 검증 후 조건부 후보로 둔다. Subset·index·manifest와
결과는 유지하며 실제 파일 삭제는 없다.

## Purpose and status

현재 Q12는 [한 번의 실패/calibration 재평가](real/README.md#reassessment-2026-09-14) 후
`deferred`다. 추가 실험은 없으며 Stage 7 `refine`은 미해결 formulation의 기록으로 남긴다.
새 연구 설계의 재진입 조건은 real owner, 다음 후보 비교는 root TODO가 소유한다.

Q12의 첫 Stage 6 **CPU input/schema/coordinate audit**을 실제 네 partial/GT 쌍에 실행하고
독립 검증했다. 네 쌍 모두 통과했으며 고정 판정은
`INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`다. 이후 checkpoint strict loading과
synthetic CPU reference 검증 후 실제 네 입력의 completion을 실행·독립 감사했다. Policy/physics
실행은 없으며 native CUDA parity·물리 연결은 미검증이다. Model 실행 결과의 owner는
[model README](model/README.md), 후속 경로 비교·준비 결정은 이 문서의
[linkage assessment](#linkage-route-assessment-2026-09-11)가 소유한다. Research question은
[Q12](../../questions/generated-geometry-reliance.md), 현재 protocol은 [protocol.json](protocol.json),
고정된 source·input·environment hash는 [freeze.json](freeze.json)이 소유한다.
Coordinate-control 통과를 useful completion, robotics outcome 또는 novelty의 증거로
해석하지 않는다. [검증 결과](#verified-input-results-2026-09-10)가 이번 실행의 범위를 소유한다.

후속 [camera/geometry 준비](geometry/README.md)는 두 mesh 취득·새 CPU Docker·synthetic
preflight를 마치고 20개 파일을 고정했다. 이후 실제 YCB 적용은
[REFINE_LINKAGE](geometry/README.md#verified-readiness-results-2026-09-11)로 종료됐다.
Box 두 view는 검증됐지만 mug 두 view는 mesh gate에서 중단됐고 별도 감사가 실패를 확인했다.
후속 [표면 보존 감사](geometry/README.md#preservation-outcome-2026-09-14)에서도 정리한 mug의
edge gate 실패가 남아 현재 asset 경로를 보류했다. [대체 경로 비교](#alternative-routes-2026-09-14)에서
BOP YCB-V의 [별도 입력 감사](real/README.md#verified-real-input-results-2026-09-14)를 실행·독립 검증했다.
Mesh·입력/좌표 검사는 통과했지만 일부 고정 ray가 model과 교차하지 않아 `DEFER_RAY_SUPPORT`다.
실패 기록과 sensor/pose calibration 근거의 재평가를 마치고 Q12 추가 투자를 보류했다.
원본 XYZ의 camera 복원이나 실제 completion의 collision 효과를 확인한 것은 아니다.

## Access and bounded acquisition

공식 pinned [3DSGrasp README](https://github.com/NunoDuarte/3DSGrasp/blob/d6763d85e063db675d433dd119837a93e3657a29/README.md)의
Drive 링크를 확인했다. HTTP 206과 Content-Range가 실제 크기와 일치했다. Outer ZIP에는
DEFLATE된 `gt.zip`과 `input.zip`만 있어 내부 XYZ에 직접 byte-range 접근할 수 없었다.
그래서 전송 전에 전체 ZIP 비용을 재평가해 성공한 payload 3 GiB, 재시도 포함 network body
4 GiB, 저장 6 GiB, wall time 30분을 한도로 정했다. 당시 free space는 약 151 GiB였다.
전체 XYZ extraction은 필요하지 않았다.

| Artifact | Bytes | Verification |
| --- | ---: | --- |
| original dataset ZIP | 1,836,233,634 | bounded Range/length, SHA-256; both outer members CRC |
| original checkpoint | 505,668,417 | bounded Range/length, SHA-256; later strict-load receipt in model README |
| inner `gt.zip` | 1,388,709,954 | outer ZIP CRC, length, SHA-256 |
| inner `input.zip` | 492,023,401 | outer ZIP CRC, length, SHA-256 |
| selected XYZ, 8 files | 3,132,024 | inner member CRC, length, SHA-256 independently rechecked |

Acquisition completed in about 199 seconds: 2,341,902,051 successful payload bytes (2.18 GiB).
Metadata range probes were separately 131,114 bytes. Stored assets/index/subset at verification
were 4,237,747,572 bytes (3.95 GiB), within the cap. No published full-file checksum was found;
local SHA-256 pins the retrieved content and is not independent publisher authentication.
Detailed hashes, indexes and selection receipt: [inputs.json](inputs.json), [sources.json](sources.json).
The full archive lists about 32.25 GB of XYZ content; this content was not fully extracted.

Selection was persisted before extracting/reading XYZ: lexicographically first two test objects
with at least two basename-matched pairs; then first two partials per object. The source loader
maps a final `x` to `y`, preserving object/split/stem. All 56 eligible objects were considered in
the index; no test partial lacked its corresponding GT basename. Each inner archive has 41,360
members, including directories. Index correspondence is not a numerical alignment check.

| Object | Test stems | Archive train/test file counts |
| --- | --- | --- |
| `banana_poisson_002` | `_0_0_5_`, `_0_0_7_` | 593 / 133 |
| `binder_poisson_004` | `_0_0_1_`, `_0_0_2_` | 583 / 143 |

The actual paths and hashes are in `inputs.json`; four pairs remain the denominator even if
one fails. Both objects appear in the source's train/test class lists and in both archive splits.
This is **not an object-disjoint test**, and a checkpoint-specific training manifest is absent.
Neither archive index contains a README/license or named pose/camera/transform metadata file.
Repository MIT terms are retained with source; separate weight/data redistribution terms are not
established. Publicly shared files are used for local feasibility inspection; do not relabel
repository licensing as dataset/model licensing.

## Why input controls precede inference

This narrowing was recorded before array inspection. The [paper §III-A](https://arxiv.org/html/2301.00866v2#S3.SS1)
describes applying partial-derived centroid/radius to both partial and GT, then FPS to 2,048/8,192
points. The pinned loader returns supplied XYZ directly, while the current inference wrapper
performs FPS followed by normalization. Source establishes different processing orders. In the four inspected inputs, FPS retained every
unique point and the supplied centroid/radius were already numerically near zero/one, respectively;
this check does not reveal a substantive normalization-order discrepancy. Per-file original metric transforms
and camera rays are missing, so a plausible normalized cloud cannot establish a physical frame.

The original CUDA 11.3/PyTorch 1.11 native stack remains unverified on RTX 5090. The initial input
audit therefore preceded model work. The subsequent model stage established strict loading and
output provenance in a separately qualified CPU reference Docker runtime. It did not establish
native parity or reproduce the unreleased 2025 uncertainty extension.

## Frozen measurement and interpretation

- Input: the four fixed partial/GT pairs. Expected shapes 2,048×3 and 8,192×3 come from the paper;
  a mismatch is a schema finding, not permission to resample or replace a case. Require finite,
  nondegenerate coordinates, correct names/hashes and retention of unique points through FPS.
- Seed: `12001 + pair index`, original NumPy FPS function extracted from pinned source inside
  Docker. Retain supplied XYZ and sampled points; use only partial-derived centroid/radius.
- Controls: float64/float32 inverse round trip, original online `7/6` restoration on the same
  copied points, and GT transformed by the same partial-derived parameters. No GT-fitted alignment.
- Tolerances: relative maximum-coordinate error `1e-12` for float64, `2e-6` for float32;
  scale is `max(radius, maximum absolute coordinate, 1)`, with GT scale included for its round trip.
  These are numerical implementation checks, not thresholds for acceptable shape error.
- Diagnostics: supplied centroid/radius, unique point counts and directed nearest-point mean/p95/max
  in supplied coordinates. No diagnostic quality cutoff, hidden-surface/free-space labels or
  model-error attribution. Copied-point restoration controls are not generated predictions.
- Resources: CPU 2, RAM 2 GiB, audit 10 minutes, verification 10 minutes, output ≤64 MiB.
  Runtime network disabled; only selected XYZ is mounted, read-only. No checkpoint/model runtime.

Decision branches are fixed in `protocol.json`. Integrity failure stops interpretation; schema
or coordinate-control failure requires refinement without changing the denominator. All input
controls passing yields `INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`: assess model readiness
and missing physical/camera linkage separately. It cannot select a hypothesis or establish a
scientific effect. A verification failure remains unresolved and needs a case-specific audit.

## Docker preparation and verification

2026-09-11 input/model image의 정리 가능성과 복구 제약은
[cleanup assessment](../../../../docs/reproducibility.md#image-cleanup-assessment--2026-09-11)이 소유한다.
실제 삭제는 없으며 아래 frozen input environment 기록은 보존한다.

New image `research3-q12-input:v1`; immutable identity is in [image_id.txt](image_id.txt).
The Dockerfile pins a freshly obtained official Python 3.11.13 Linux amd64 digest; NumPy 1.26.4's
wheel hash is in [requirements.txt](requirements.txt), installed inventory in
[environment.txt](environment.txt). No pre-existing external Docker/simulator asset was used.
Source receipt retains upstream URLs/commit/hash and the MIT license. Only the audited pure-NumPy
FPS function is executed; importing the full upstream module would start unrelated dependencies.

Build and synthetic verification: **completed**. Final preflight tested malformed/degenerate input
rejection, exact/float32/7/6 controls, FPS against exhaustive reference, four-pair end-to-end
receipts, schema-failure denominator preservation, corrupted-input rejection and the independent
standard-library verifier. Synthetic fixtures lived in container `/tmp`; no dataset was mounted.
These checks verify implementation contracts, not actual input validity.

- Acquisition: `logs/20260910_134730_q12_inputs.log` / `.exit` = 0.
- Fresh build/initial synthetic preflight: `logs/20260910_135134_q12_build.log` / `.exit` = 0.
- Final synthetic receipt and command: [preflight.json](preflight.json).

Freeze SHA-256: `7b9ad1db49e2138f5c635e477af8a3ff26834926a325d5ed8fff5e7bd99c946c`.
Final preparation validation: frozen files 17/17 and selected raw hashes 8/8 matched;
10 updated Markdown documents, 177 local links (79 heading links) and Q12/Q13/TODO status
consistency passed. Python AST, JSON and shell syntax checks passed. No real-input output root
existed at this verification. These checks close preparation, not the next actual-data audit.

## Commands, outputs and recovery

All commands use cwd `/home/yoohyun/research3`. Completed preparation launches:

```bash
tmux new-session -d -s research3_q12_inputs_20260910 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/acquire.sh'
tmux new-session -d -s research3_q12_input_build_20260910 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/build.sh'
```

Actual-input execution job: **completed and verified** on 2026-09-10 after frozen files 17/17 and
raw input hashes 8/8 matched. The named workspace-built image was present and both output roots were absent.
Launch command:

```bash
tmux new-session -d -s research3_q12_input_v1 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/run.sh'
```

`run.sh` uses the frozen image ID, validates frozen files inside Docker, refuses existing output
roots, records timestamped `logs/<YYYYMMDD_HHMMSS>_q12_input_v1.log` / `.exit`, and runs
`audit.py` followed by `verify.py` with separate read/write mounts. Verified artifacts:

- `runs/q12_input_v1/data/results.json` and up to four sampled XYZ files.
- `runs/q12_input_v1_audit/verification.json` with the same four-pair denominator and decision.
- Every input/source hash must match; verifier receipt must be `VERIFIED`; exit must be 0.

`prepare_inputs.py` is host-only public transfer/index/checksum work; it does not import model or
array dependencies. Downloads resume `.part` with exact ranges. Extraction refuses overwrites.
Do not blindly rerun a completed acquisition or rebuild over a frozen environment record. For
recovery, reconstruct missing files in a separate staging path from recorded public URLs, verify
against `inputs.json`, then restore only matching raw files. Mutable Drive contents that differ
from recorded hashes are a new input revision. A rebuilt image also requires a separate runtime
receipt; preserve the frozen image ID and protocol record.

## Preservation

- `datasets/q12/`: original ZIP/model, inner archives, selected raw XYZ, full index and receipt.
- This study folder: compact source/input manifests, protocol/freeze, Docker recipe, code and locks.
- `runs/q12_*/`: original sampled points/results and independent audit receipt; `logs/`: job logs and exit files.

Current resume needs the frozen image and selected XYZ; later inference also needs the checkpoint.
Full reproduction needs source/recipe/locks plus pinned assets or verified matching downloads.
Result preservation now needs the original sampled-point output/results, independent receipt and
execution manifest; compact JSON copies are retained here. These are input-audit results, not model
predictions. No external backup was verified and no original data, image or artifact was deleted.


## Verified input results 2026-09-10

**Observed facts:** the frozen run and independent verifier both completed successfully, with
`logs/20260910_140916_q12_input_v1.exit == 0`. Four of four partial arrays were 2,048×3, four of
four GT arrays were 8,192×3, all were finite/nondegenerate, and each partial retained all 2,048
unique coordinates through FPS. Source/input identity, pair names and the four-case denominator
were preserved. Execution used only the selected raw XYZ, CPU 2/RAM 2 GiB limits and no network.
No model or checkpoint was mounted. [execution.json](execution.json) owns identity, command,
log and the six output file hashes; total output was 473,350 bytes, within the 64 MiB cap.

The observed maximum relative errors were `8.674e-19` for float64 inverse, `2.973e-08` for float32
inverse and `8.212e-08` for the online-restoration analytic control. The frozen limits were
`1e-12`, `2e-6` and `2e-6`, respectively. The independent standard-library verifier recomputed
input support, centroid/radius, restoration controls and twelve partial-to-GT sentinel distances.
It confirmed the same decision and linked the exact result hash. It did not independently
recompute the full distance distributions or establish their physical meaning.

| Object / test stem | Unique partial / sampled | Unique GT / 8,192 rows | Mean partial→GT | Mean GT→partial |
| --- | ---: | ---: | ---: | ---: |
| banana / `_0_0_5_` | 2,048 / 2,048 | 4,025 | 0.010341 | 0.024775 |
| banana / `_0_0_7_` | 2,048 / 2,048 | 4,273 | 0.010274 | 0.025422 |
| binder / `_0_0_1_` | 2,048 / 2,048 | 8,074 | 0.011622 | 0.215546 |
| binder / `_0_0_2_` | 2,048 / 2,048 | 8,097 | 0.012412 | 0.202438 |

Full object IDs and case metrics are in [results.json](results.json); the byte-identical compact
copy of the independent receipt is [verification.json](verification.json). Distances use supplied
normalized coordinates, not metres or physical error. GT has repeated rows in every case; these
are direct counts from the frozen audit and do not establish a corruption or padding mechanism.
The row-weighted GT→partial diagnostics can depend on duplicate multiplicity. We preserve all
rows, counts and original metrics; no deduplication, resampling or threshold change was applied.
Any future geometry-quality comparison must declare its sampling/density treatment in advance.

**Interpretation:** the largest supplied centroid norm was `8.233e-12` and the largest radius
change from one was `2.110e-11`. These particular partials are already numerically centered and
unit-radius, so the additional normalization is near identity; differing source operation order
alone is not an observed failure here. The online wrapper still produces the expected 7/6 radial
expansion on copied input points. That is an analytic wrapper control, not learned completion
bias or measured robotics harm.

**Remaining boundary:** passing name/schema/numerical checks does not certify the actual partial/GT
physical frame, original metric transform, camera/free-space provenance, training disjointness or
independent generated geometry. This result therefore remains
`INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`. Frozen protocol/source 17 files and all eight
raw input hashes still match; the original freeze digest, denominator and thresholds are unchanged.

Closing verification also matched all six output hashes and both compact JSON copies. The ten
updated Markdown documents passed 185 local-link checks (87 heading links) and current-state/TODO
consistency checks. This was artifact/document validation; no additional measurement was run.

## Next bounded task

Checkpoint strict loading과 독립 metadata audit을 마쳤다. Native dependency의 접근/동등성
제약을 기록하고 CPU reference completion protocol을 실제 입력 추론 전에 고정했다.
같은 네 입력을 두 process로 실행했고 output provenance·repeat equality를 독립 감사했다.
후속 경로 비교 후 known geometry/camera와 고정 gripper pose의 collision 진단을 위한
[readiness protocol](geometry/README.md)을 준비·고정하고 실제 YCB에 적용했다. 결과는
`REFINE_LINKAGE`다. 후속 exact-coordinate/zero-area 정정 감사는 표면·고정 query 동등성을
확인했지만 잔여 edge gate 실패로 Google 16k asset 경로를 보류했다. 이후 대안을 비교하고
BOP YCB-V의 real-data camera/model 입력 감사 준비를 선택했다. 범위·근거는 아래
[최신 비교](#alternative-routes-2026-09-14)가 소유한다. 원본/threshold/case를 바꾸거나 이 정정으로
기존 readiness를 재개하지 않는다.
[Model README](model/README.md)가 결과·source adapter·synthetic 검사·freeze·자원 한도·
명령을 소유한다. GT row multiplicity, native CUDA parity와 physical/camera linkage는 별도
조건이며 Q13을 자동 승계하지 않는다. 위 input v1의 frozen source/result는 보존한다.

## Linkage route assessment 2026-09-11

**Decision — agent assessment:** Stage 7은 `refine`이다. Q12는 `feasibility_study`로 유지하고,
**알려진 geometry와 camera로 새 관측을 만들고, 공통 gripper pose 후보의 collision 판정을
비교하는 작은 CPU 경로**를 다음 protocol 준비 대상으로 선택한다. 기존 네 XYZ의 camera를
복원한 것으로 취급하지 않는다. Native CUDA parity와 full learned-policy 연구는 보류한다.
이번 결정은 경로의 source-level 가능성에 관한 것으로, 새 renderer·collision evaluator의
실행 검증이나 completion의 행동 효과를 확인한 결과가 아니다.

### Evidence obtained

- **Verified existing result:** checkpoint-derived CPU reference 출력과 generated/copied 분리는
  [model 결과](model/README.md#verified-completion-results-2026-09-11)로 확보했다. 원본 XYZ에는
  per-file metric inverse·camera rays가 없다. Native operator를 복구해도 이 metadata가 생기지는 않는다.
- **Original-data recovery:** [3DSGrasp §IV-A와 reference 4](https://arxiv.org/html/2301.00866v2)
  는 Varley et al.의 *Shape Completion Enabled Robotic Grasping*을 dataset 출처로 명시한다.
  원 논문은 mesh에서 여러 depth view를 만드는 과정을 설명하지만, 현재 네 XYZ와 해당
  renderer pose/scale을 잇는 record는 확보하지 못했다. 기존 pinned repository tree의
  data/camera/transform/generate/pose 관련 경로와 loader를 재검토했으나 그 mapping을 찾지
  못했다. 이는 모든 외부 archive에 metadata가 없다는 증명이 아니다. Filename 숫자를 camera
  pose로 해석하거나 GT에 ICP/scale을 맞춰 원본 camera를 복구했다고 주장할 수 없다.
- **Native recovery:** GitHub는 [unique1i/knn_cuda](https://github.com/unique1i/knn_cuda/tree/8b21dbfc86988f56588a5ed8ca3cc354122c5656)를
  `unlimblue/KNN_CUDA`의 fork로 표시하며 API parent도 일치했다. Python wrapper와 CUDA/C++
  source를 고정·확인했다. Wrapper는 import 시 JIT compile을 수행한다. 따라서 원본 URL의
  404를 source 복구 불가능으로 일반화하지 않는다. 다만 이 fork가 checkpoint training 때의
  정확한 version인지, 현대 CUDA에서 같은 이웃/tie/FPS와 model output을 만드는지는 미검증이다.
  기존 CPU reference나 frozen operator receipt는 바꾸지 않는다.
- **Real-data alternative:** [GraspNet 공식 data schema](https://graspnet.net/datasets.html)는
  RGB-D·object pose·camera intrinsics/poses와 object models를 제공한다. 공식 test image
  archive 하나는 19–20 GB, models는 4.3 GB이며 작은 subset의 실제 접근 비용은 아직
  검증하지 않았다. [Pinned evaluator](https://github.com/graspnet/graspnetAPI/blob/eb57dd2092d8dbe05312a29c3d0c22f3226efbfc/graspnetAPI/graspnet_eval.py)와
  [evaluation utilities](https://github.com/graspnet/graspnetAPI/blob/eb57dd2092d8dbe05312a29c3d0c22f3226efbfc/graspnetAPI/utils/eval_utils.py)는
  full model을 camera frame으로 옮겨 collision 및 Dex-Net force-closure를 평가한다.
  실제 robot execution 성공과는 다른 analytic outcome이다. 전체 archive 취득이 필수라고
  단정하지 않으며 selective retrieval이 확인되면 후속 real-data 후보로 재비교한다.
- **Controlled route:** [PyBullet 공식 guide](https://github.com/bulletphysics/bullet3/blob/63c4d67e337017f9d8b298c900e9aabdb69296e7/docs/pybullet_quickstart_guide/PyBulletQuickstartGuide.md.html)는
  DIRECT의 software rendering과 static concave triangle mesh를 지원한다고 명시한다.
  [Camera example](https://github.com/bulletphysics/bullet3/blob/63c4d67e337017f9d8b298c900e9aabdb69296e7/examples/pybullet/examples/getCameraImageTest.py)은
  view/projection, near/far와 depth-buffer 변환을 보여주고,
  [Python binding](https://github.com/bulletphysics/bullet3/blob/63c4d67e337017f9d8b298c900e9aabdb69296e7/examples/pybullet/pybullet.c)은
  `getClosestPoints`를 제공한다. Source 확인이며 이 workspace에서의 작동 증명은 아니다.
- **Bounded asset access:** [YCB 공식 index](https://ycb-benchmarks.s3.amazonaws.com/index.html)의
  `003_cracker_box`와 `025_mug` Google 16k archive에 HEAD 200을 확인했다. Content-Length는
  각각 11,434,893 / 7,658,239 bytes, 합계 19,093,132 bytes(18.21 MiB)다. 새 asset payload는
  받지 않았다. HTTP length와 ETag는 mesh integrity·단위·watertightness 검증을 대신하지 않는다.
  이들은 작은 접근 경로의 예시이며 기존 banana/binder와 같은 instance라는 근거는 없다.
- **Prior boundary:** [Single-View Shape Completion for Robotic Grasping in Clutter](https://github.com/OrebroUniversity/shape_comp/tree/4b7a1f4eff01bea994b319509ab0b8d240cf650a)는
  category-conditioned completion checkpoint와 partial-point-cloud inference를 공개한다.
  Completion을 grasping에 쓰는 넓은 방향은 이미 선행이다. 이 source의 존재만으로 현재
  Q12의 input/camera/evaluator 연결이 해결되지는 않아 model 교체를 선택하지 않는다.

Source 4개 repository의 13개 text file(536,990 bytes), YCB index와 두 HEAD receipt는
[linkage_sources.json](linkage_sources.json)에 commit·URL·hash·접근 경계를 기록했다.
원본 text cache는 `/tmp/research3-q12-linkage-20260911/`이다. 새 source는 read-only로
검사했으며 import/install/build/inference/simulation은 수행하지 않았다.

### Cost and information comparison

아래 기간은 **agent planning estimate**이며 측정된 runtime이나 작업 보장이 아니다.
각 경로의 결과를 보기 전에 다음 준비의 비용을 비교한 것이다.

| Route | Next cost / dependency | Information gained and remaining limit | Disposition |
| --- | --- | --- | --- |
| 원본 3DSGrasp camera/metric mapping 복원 | 저렴한 source audit은 완료; 이후 기간 불명, 원본 mapping 필요 | 기존 네 쌍을 유지할 수 있으나 지금은 구체적인 복원 파일이 없음 | mapping record가 생길 때 재개; 이름 추정·GT fitting으로 대체하지 않음 |
| Native KNN/FPS/CUDA parity | 새 GPU Docker·source adaptation, 약 0.5–2일 예상; historical version 불명 | reference 구현 차이를 분리할 수 있음; physical frame과 action label은 여전히 없음 | native-original attribution 또는 operator-sensitive effect 검증 때 재개 |
| GraspNet의 real RGB-D + full-model evaluator | subset access·frame·legacy evaluator 감사 약 1–2일 예상; 공식 큰 archive 경로만 확인 | 실제 camera와 독립 model geometry 확보 가능; sensor/pose noise, analytic label과 training overlap 별도 | real-data reserve; 작은 취득 경로가 확인되면 재비교 |
| Known geometry + CPU renderer + fixed gripper poses | 두 example mesh compressed 18.21 MiB; 새 Docker/calibration 약 0.5–1일 준비 예상 | camera·metric transform·평가 geometry를 명시하고 input만 바꿀 수 있음; synthetic shift와 static collision proxy에 한정 | **다음 준비로 선택** |
| G3Flow/DP3 learned policy 연결 | independent completion adapter·matched demos/weights·training과 simulator 준비, 현재 총비용 미정 | 실제 policy reliance 질문에 가장 직접적; shared-asset/extra-view/semantic confound부터 해소 필요 | 작은 diagnostic의 유효성과 정보 가치가 확보될 때 재개 |

선택 이유는 native parity를 불필요하다고 보기 때문이 아니다. 현재 가장 큰 식별 문제는
**completion과 독립적인 truth 및 camera를 연결할 수 있는가**다. 알려진 새 scene에서
명시적으로 `CPU reference completion`만 평가하는 진단은 historical native 동등성을 먼저
주장하지 않고도 이 문제를 검사할 수 있다. Native parity를 하지 않은 결과를 원래 3DSGrasp의
실패로 귀속하거나 native 방법보다 좋은 새 방법의 증거로 사용할 수는 없다.

### Next bounded preparation

다음은 경로 비교 시의 **역사적 준비 범위**다. 이후의 실제 frozen constants, 한 차례의
synthetic preparation revision, 검증 결과와 실행 command는 [geometry owner](geometry/README.md)가
소유한다. 이 초안을 현재 frozen protocol 대신 실행하지 않는다.

1. **먼저 연결을 검증한다.** 두 public mesh 이내와 analytic box/plane controls로 시작한다.
   Mesh hash·use terms·단위를 확인하고, 원래 단위를 확인할 수 없으면 사전에 선언한 synthetic
   metric scale로 한정한다. Render/collision에 동일한 mesh·transform을 사용하고 concave mesh의
   convex-hull 대체를 금지한다. Object는 static, gripper는 명시된 rigid geometry다. Known
   depth/plane의 back-projection, handedness, camera→world→camera와 metric inverse, 알려진
   충돌/비충돌 fixture를 독립 계산과 비교한다. Runtime은 새 workspace CPU Docker에서만 한다.
2. **새 observation lineage를 만든다.** 같은 physical mesh/pose·camera의 한 snapshot을 모든
   조건에 공유한다. Renderer의 oracle segmentation은 모든 조건에 동일하게 주고 그 가정을
   명시한다. Completion에는 partial-derived normalization만 적용하며 camera-aligned axes와
   정확한 inverse를 기록한다. GT mesh를 completion이나 후보 생성에 넘기지 않는다. 기존 네
   XYZ/NPZ는 새 scene에 끼워 맞추지 않고 보존한다. 새 관측의 checkpoint training support는
   미확인이므로 synthetic distribution shift와 학습된 bias를 구분해야 한다.
3. **작은 action proxy로 한정한다.** 최대 두 object × 두 view, case당 최대 32개의 고정 gripper
   pose를 목표로 한다. Candidate frame/region·공통 utility는 관측과 선언된 task constraint만
   사용해 생성하고 completion/GT를 보기 전에 보존한다. Static pose collision/clearance와
   선택·거부 차이를 평가하며 grasp closure, swept-path safety, force closure, lift success나
   learned-policy 행동을 검증했다고 부르지 않는다.
4. **가장 단순한 controls부터 비교한다.** Observed-only, observed+completion, generated points에
   observation/free-space consistency를 적용한 completion, 제한된 task region의 unknown space를
   보수적으로 처리하는 baseline을 같은 후보/utility로 비교한다. Invalid depth와 image 밖은
   known-free로 처리하지 않는다. 전부 거부하는 baseline은 collision 0만 보고하지 않고
   abstention·유효 후보 손실을 함께 기록한다. GT는 evaluator와 명시된 oracle control에만 쓴다.
   Oracle full-geometry point representation도 같은 sampling/occupancy interface로 검사해
   point density·representation 손실을 completion error와 구분한다.
5. **정보가 없으면 멈춘다.** Frame/renderer/collision controls 실패 → 연결 경로 refine/defer.
   독립 truth에서 충돌/비충돌 후보 양쪽의 support가 없거나 oracle representation이 evaluator와
   맞지 않음 → `uninformative`, 유리한 case/threshold를 찾아 바꾸지 않는다. 실제 generated
   output을 넣어도 후보 판정·선택 차이가 없음 → 이 작은 route를 확대하지 않는다. 차이가
   좌표·density·consistency 또는 보수적 baseline으로 설명됨 → 그 진단을 기록하고 새 method
   승격을 하지 않는다. Controls 이후 실제 completion의 benefit/harm 차이가 남으면 case-level
   mechanism과 native/real-data/matched-policy 중 어떤 검증이 필요한지 한 번 재평가한다.

준비 예산 제안은 source/asset 작업과 새 CPU Docker 포함 한 working day, asset payload ≤64 MiB,
extracted asset ≤256 MiB, 새 image/storage ≤4 GiB다. 다음 실행 protocol에는 CPU 4/RAM 4 GiB,
전체 측정·독립 검증 30분, output ≤128 MiB를 상한으로 검토한다. 이는 이번 실행의 사용량이
아니다. Dependency wheel·extraction 크기와 실제 recipe가 cap을 만족하는지 먼저 확인하며,
충족하지 못하면 비용 근거를 갱신한다. Native CUDA build·GraspNet 전체 취득·GPD/ROS integration·
policy training을 이 준비에 추가하지 않는다.

이 pilot은 제한된 측정 도구를 마련하는 단계다. 고정 후보의 collision 차이만으로 원래의
learned-policy reliance 질문에 답하거나 novelty·일반화·hypothesis admission을 주장할 수 없다.
현상이 관측되지 않았다는 이유로 artificial hallucination을 넣어 성공 조건을 만들지 않는다.

**Closing verification:** source/index 14개 파일, 642,925 bytes의 length/SHA-256이 receipt와
일치했다. 기존 input/schema/completion freeze digest 및 17/17/43개 frozen 파일은 모두
유지됐다. 갱신한 Markdown 10개의 local link 228개(heading 106개)와 Q12/Q13·TODO 상태
일관성을 검사했고 오류가 없었다. 이는 source·artifact·문서 검사이며 새 method 실행 검증이 아니다.

## Alternative routes 2026-09-14

Selected route implementation, preparation and verified real execution are owned by [real/README.md](real/README.md).
The comparison below is the pre-acquisition decision record. The frozen audit can diagnose numerical
input failures; its actual outcome is `DEFER_RAY_SUPPORT`. Physical/free-space admission remains
deferred with unresolved sensor/pose calibration. The subsequent
[single reassessment](real/README.md#reassessment-2026-09-14) deferred further Q12 investment.
The comparison and metadata-access evidence below remain the selection provenance.

Status: `completed`. Compared real RGB-D with annotated camera/models (BOP YCB-V, GraspNet),
analytic constructed solids, original-frame/native recovery, and further deferral. The failed
YCB Google 16k route and its four cases remain frozen. Only source/metadata inspection ran during
this comparison. The selection below is one bounded follow-up preparation; it is not an input
replacement in the failed study.

The read-only access audit pins official source revisions, verifies metadata/ZIP directory range
access, and may inspect small JSON/Markdown members only. No image/mesh member is extracted or
interpreted. Host execution is limited to HTTP download, checksums and archive/schema inspection;
no method imports. Source body cap 4 MiB, archive-range body cap 4 MiB, per-request timeout 20 s,
whole job 600 s. Refuse full archive fallback when HTTP Range is ignored. Dataset members, even
if reachable, are not certified by a ZIP index. Logs and commands:

```bash
tmux new-session -d -s research3_q12_routes_20260914 'cd /home/yoohyun/research3 && stamp=$(date +%Y%m%d_%H%M%S); timeout 600 python3 buildup/robotics/pilot_studies/q12-generated-geometry/route_access.py > logs/${stamp}_q12_routes.log 2>&1; rc=$?; echo "$rc" > logs/${stamp}_q12_routes.exit'
```

Text/range cache: `/tmp/research3-q12-routes-20260914/`; tracked receipt:
[route_sources.json](route_sources.json) beside this README. The job completed with no access errors;
`logs/20260914_113631_q12_routes.log` has `.exit == 0`. The saved launcher source is
[route_access.py](route_access.py); it refuses an existing cache root or receipt. Verify all
cached lengths/SHA-256, exact revision, checked Content-Range, central-directory/member CRC when
extracted, required paths and explicit errors. Existing freeze/assets/outputs must remain unchanged.

### Decision and evidence

**Agent decision:** select **one bounded preparation of a BOP YCB-V real-data camera/model audit**.
Q12 remains `feasibility_study` / `refine`; the previous Google 16k asset route remains deferred.
This selects an input-validation route, not a new method, a completed readiness protocol, or a
completion/action experiment. The new advantage is accessible real depth with explicit camera and
annotated model poses. It is not evidence that BOP meshes satisfy the failed solid-geometry gate.

**Official-source statements:** [BOP's YCB-V description](https://bop.felk.cvut.cz/datasets/#YCB-V)
identifies real test images and a curated 75-frame subset from each of 12 scenes. Models were
converted from meters to millimeters and centered with corresponding pose changes. The BOP
version must therefore use its own model/pose pair, not an original Google OBJ with a fitted
transform. The base archive's `dataset_info.md` identifies `models` as converted
`textured_simple.obj` and `models_fine` as converted `textured.obj`; the dataset page/base metadata
provide the MIT license notice. Neither source claims a closed-solid collision certificate.

The [pinned BOP format](https://github.com/thodan/bop_toolkit/blob/cea62d651c7e395b2e1962b9749e4e89693c6ac4/docs/bop_datasets_format.md)
defines per-image `cam_K`, `depth_scale`, model-to-camera `cam_R_m2c`/`cam_t_m2c`, and
`IMID_GTID` masks. Depth scaling gives millimeters; numerical code must explicitly convert to
meters. Root `camera_uw.json`/`camera_cmu.json` describe sensor simulation and must not replace
per-frame camera records. `models_eval` is resampled/decimated for pose-error evaluation; its
presence does not justify adopting it as continuous collision truth.

**Measured access/schema facts:** the pinned official
[HF dataset revision](https://huggingface.co/datasets/bop-benchmark/ycbv/tree/5c2c4aa229800355648cd268040aa814f8dc94f0)
contains the following archives. Exact HTTP 206/Content-Range was checked for every range read;
ZIP central directories and ten small text/JSON members were obtained, with member CRC checks.

| Archive | Entire archive bytes | Directory entries | What was inspected |
| --- | ---: | ---: | --- |
| `ycbv_base.zip` | 15,805 | 5 | dataset info, two root camera files, target list |
| `ycbv_models.zip` | 524,634,729 | 108 | member paths/sizes and three model-info JSON files |
| `ycbv_test_bop19.zip` | 660,198,701 | 10,087 | member paths/sizes and first scene's camera/GT/info JSON |

Network body read by the saved audit was 177,128 source bytes plus 910,437 range bytes, totaling
1,087,565 bytes (about 1.04 MiB). This is not a complete dataset download. The official target
list contains 4,123 object-target rows, 900 distinct scene/frame pairs and 12 scenes. The first
scene, `000048`, has 75 matching camera/GT/info frame keys. The earliest two frame IDs are
`000001` and `000036`; each annotation lists object IDs `1, 6, 14, 19, 20`. Required camera/pose
fields exist. No depth/image or mesh member was extracted, decoded, rendered or numerically
validated; presence of JSON fields does not establish calibration accuracy or geometric validity.

The ZIP index gives 2,019,101 compressed bytes / 5,392,033 unpacked bytes for **all five** standard
`models/obj_*.ply` files in this scene. Both frames' RGB, depth and full/visible masks add
1,283,805 compressed / 1,303,623 unpacked bytes. Thus the proposed members total 3,302,906
compressed / 6,695,656 unpacked bytes before metadata, HTTP/header overhead, dependencies or
derived output. These are directory-based estimates, not completed member transfers. Model
ID 14 is `025_mug`; it remains in the proposed scene audit alongside both clamp models, with no
mesh-quality filtering. A valid partial download will need member SHA/CRC/length receipts;
partial ranges cannot verify the full archive's published LFS SHA-256.

### Comparison and why this next step

Times below are **agent planning estimates**, not measured runtimes or delivery guarantees.

| Route | Camera/GT separation and geometry | Access / next cost | Expected information / disposition |
| --- | --- | --- | --- |
| BOP YCB-V real RGB-D + annotated standard models | Camera and model poses supplied independently of the completion checkpoint; real depth. Mesh validity, sensor residuals and annotation bias remain unverified. | Selective metadata access verified; proposed members about 3.3 MB compressed. At most one working day for bounded protocol/Docker preparation. | Tests whether real camera/model linkage is viable at low transfer cost. **Select this one preparation**, with explicit stop conditions. |
| GraspNet real RGB-D + native analytic evaluator | Real camera/poses/models and grasp labels. Native collision/empty-grasp/force-closure semantics differ from our continuous-solid proxy. | Official test archive 19–20 GB, models 4.3 GB; exact small-member access not verified here. Legacy evaluator/Dex-Net dependencies; approximately 1–2 days for a first access/runtime audit. | More direct grasp benchmark path, retained as reserve. Do not substitute its point test solely to bypass the current mesh gate. |
| New analytic solids + independent ray/occupancy formulas | Known camera/solid by construction; separate observation/evaluator implementations still need verification. | No external asset transfer; roughly 0.5–1 day of implementation/control work. | Useful unit/measurement controls. Synthetic shape/input shift would still dominate attribution to the pretrained completion, so not selected as the sole next scientific route. |
| Original XYZ camera recovery / native KNN-FPS parity | Existing four inputs preserved, but no recovered per-file camera/scale mapping. Native parity does not create it. | No new concrete mapping source identified in this comparison; GPU/native work separately costs approximately 0.5–2 days. | Conditional re-entry for original-method attribution or a concrete mapping record; not the current linkage solution. |
| Further deferral of Q12 | Avoids an unverified measurement claim and further engineering expense. | No new runtime/data cost. | Reasonable if the bounded real-data audit cannot establish valid inputs. Not selected immediately because small official camera/pose access is now directly verified. |

The [official GraspNet schema/download page](https://graspnet.net/datasets.html) was rechecked;
the [evaluator source](https://github.com/graspnet/graspnetAPI/blob/eb57dd2092d8dbe05312a29c3d0c22f3226efbfc/graspnetAPI/utils/eval_utils.py)
remains at the earlier audited commit. Source inspection shows point membership in gripper regions
and an empty-grasp condition in its collision mask, followed by separate grasp-quality evaluation.
These are legitimate benchmark semantics, but they do not independently certify a continuous
solid or physical grasp success. No GraspNet payload, dependency install or evaluation ran here.

BOP wins this **preparation priority**, not a benchmark comparison: it adds a concrete real-camera
link and verified small access. It does not solve topology automatically, establish object-disjoint
training support, or supply action labels. The YCB model ancestry and possible 3DSGrasp training
overlap remain explicit. One scene/two nearby frames cannot support generality or independent splits.

### Risks and bounded preparation selected

**Mask and pose dependence:** the [pinned mask generator](https://github.com/thodan/bop_toolkit/blob/cea62d651c7e395b2e1962b9749e4e89693c6ac4/scripts/calc_gt_masks.py)
renders the standard model at its annotated pose and uses measured depth to form visible masks.
It uses a default 15 mm visibility tolerance for this dataset class. That is a mask-construction
parameter, **not** permission to adopt 15 mm collision/free-space tolerance. Supplied masks are
annotation-dependent; if later used as oracle segmentation they must be shared by all baselines.
GT model/pose must remain outside completion, normalization, candidate generation and selection
except for that explicitly declared common mask. A later observed-mask sensitivity check would
still be needed before a learned-perception claim.

**Prospective preparation scope:** first scene by numeric scene ID and its first two official
target frames; include every object instance in their annotations, including clutter models.
This gives two real RGB-D frames, five distinct model assets and ten object/frame records for
input readiness. These are not ten completion/grasp trials and do not replace the four synthetic
v1 cases. IDs were identified using metadata only; a separate acquisition/input protocol must
freeze them before any image/model payload inspection. Use standard `models`, as the inspected
mask generator does. Do not silently switch to `models_fine`, `models_eval`, another scene or a
hand-repaired model if the first audit fails.

The next TODO is to prepare that separate protocol, pinned CPU Docker, selective-download
manifest and independent checks. Suggested caps to freeze: one working day preparation,
dataset response bodies <=16 MiB (including metadata and repeated range bytes), unpacked selected files <=64 MiB,
new image/storage <=4 GiB, CPU 4 / RAM 4 GiB, numerical runtime plus verification <=30 minutes.
These are proposed ceilings, not an existing runtime freeze. No checkpoint, training, native CUDA,
gripper ranking or model completion belongs in this input audit.

Preparation must separate the following gates before execution:

1. Exact source/member identity, per-frame camera/pose/mask associations, permitted input paths,
   and all ten object/frame records. Access/cap failure stops acquisition; no full-archive fallback.
2. Depth encoding/invalid pixels, explicit mm-to-m conversion, camera projection/back-projection
   and model-to-camera transformations. Do not recenter/scale/ICP against GT to obtain agreement.
3. All five original standard meshes: finite coordinates, nonzero-area triangles and original
   opposite-edge incidence checks at the declared physical units; retain failures. Closed-edge
   checks still do not prove absence of self-intersection or global physical fidelity.
4. Sensor/model residuals and mask provenance, reported independently of the completion model.
   The old synthetic 0.75 mm ray bound is not a real-sensor calibration specification. A new
   numerical/sensor acceptance rule needs source/control justification **before** outcome inspection;
   without one, do not admit physical/free-space claims from residual statistics.

Missing calibration support, failed asset gates or excessive setup cost → defer this real-data
route and reassess further Q12 work once, rather than add another repair/sampling loop. Passing
input checks → prepare a separate collision/evaluator validation next; it does not immediately
admit completion comparison. For a later model comparison, retain observed-only, generated/copied
provenance, observation consistency, conservative unknown-space control and oracle representation
checks. If real completion effects are absent or explained by simple controls, retain that negative
result. No manufactured hidden-shape perturbation may be used to manufacture a Q12 effect.

**Preservation:** all previous input/model/geometry/preservation freezes, source assets and
numerical outputs remain unchanged. This turn performed source, byte-range, archive and metadata
inspection only. The current authoritative task board is the root TODO; Q13 remains deferred.

Closing verification: all 48 source/range file hashes and lengths, 10 extracted metadata member
hashes/lengths/CRCs, and 3 serialized ZIP directories matched (61 cache files, 3,488,203 bytes).
All six earlier freeze digests and their 17/17/43/20/9/5 entries matched; original asset hashes,
14 readiness outputs, 38 paired outputs and both independent inspection receipts were preserved.
Eleven Markdown documents passed 304 local-link checks including 141 heading links. Python AST,
JSON, Q12/Q13/TODO status and diff whitespace checks passed. These are artifact/schema checks;
no new model, renderer, numerical mesh, camera or action-evaluator validation occurred.
