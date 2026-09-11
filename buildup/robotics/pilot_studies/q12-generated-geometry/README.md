# Generated Geometry Readiness

Updated: 2026-09-11 · Q12 · input v1 and CPU reference output verified

## Purpose and status

Q12의 첫 Stage 6 **CPU input/schema/coordinate audit**을 실제 네 partial/GT 쌍에 실행하고
독립 검증했다. 네 쌍 모두 통과했으며 고정 판정은
`INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`다. 이후 checkpoint strict loading과
synthetic CPU reference 검증 후 실제 네 입력의 completion을 실행·독립 감사했다. Policy/physics
실행은 없으며 native CUDA parity·물리 연결은 미검증이다. Model 실행 결과·다음 작업의 owner는
[model README](model/README.md)다. Research question은
[Q12](../../questions/generated-geometry-reliance.md), 현재 protocol은 [protocol.json](protocol.json),
고정된 source·input·environment hash는 [freeze.json](freeze.json)이 소유한다.
Coordinate-control 통과를 useful completion, robotics outcome 또는 novelty의 증거로
해석하지 않는다. [검증 결과](#verified-input-results-2026-09-10)가 이번 실행의 범위를 소유한다.

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

The original CUDA 11.3/PyTorch 1.11 native stack remains unverified on RTX 5090. We do not replace
native operators or start that build before checking the input risk. A later completion-readiness
revision must separately establish checkpoint keys/strict loading, valid output provenance and a
compatible Docker runtime. The available checkpoint is not evidence that the unreleased 2025
uncertainty extension has been reproduced.

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
다음은 이 결과와 native parity·physical/camera 연결 경로의 비용·정보 가치를 비교해 후속
action-linked 검증 또는 refine/defer를 판단하는 것이다.
[Model README](model/README.md)가 결과·source adapter·synthetic 검사·freeze·자원 한도·
명령을 소유한다. GT row multiplicity, native CUDA parity와 physical/camera linkage는 별도
조건이며 Q13을 자동 승계하지 않는다. 위 input v1의 frozen source/result는 보존한다.
