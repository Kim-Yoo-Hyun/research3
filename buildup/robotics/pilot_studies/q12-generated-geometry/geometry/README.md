# Camera and Geometry Readiness

Updated: 2026-09-14 · surface-preserving cleanup insufficient; current asset route deferred

Runtime 정리·복구 조건은 [Docker cleanup assessment](../../../../../docs/reproducibility.md#docker-cleanup-assessment--2026-09-14)를 따른다. Image 실제 삭제는 없다.

Q12의 frozen camera/geometry readiness를 실제 두 YCB mesh에 실행했다. 고정 판정은
**`REFINE_LINKAGE`**다. Box 두 view는 검증됐지만 mug 두 view는 mesh gate에서 중단됐다.
[실제 v1 결과](#verified-readiness-results-2026-09-11)를 보존했다. 후속
[표면 보존 감사](#preservation-outcome-2026-09-14)에서도 mug의 edge gate 실패가 남아
현재 asset 경로를 보류한다. 표면·고정 query 동등성은 readiness 통과를 대체하지 않는다.
이 폴더는 CPU Docker,
asset receipt, synthetic preflight, frozen protocol과 실행 command의 owner다. 기존
input/model freeze와 실제 네 XYZ/NPZ는 유지한다. Completion comparison은 보류한다.
후속 [BOP 실패/calibration 재평가](../real/README.md#reassessment-2026-09-14)로 Q12 전체의 추가
투자도 보류했다. 이 폴더의 과거 next-step 기록은 현재 실행 queue가 아니다.

- Asset selection before payload inspection: YCB Google 16k `003_cracker_box`, `025_mug`.
- Built image: `research3-q12-geometry:v1`, official pinned Python base, PyBullet 3.2.7/NumPy 1.26.4.
- Runtime: CPU-only; no policy training or native CUDA operator build.
- Input cache: `datasets/q12/geometry/`; actual outputs: `runs/q12_geometry_v1/`.
- Source and prior decision: [parent assessment](../README.md#linkage-route-assessment-2026-09-11).

## Preparation jobs

Cwd `/home/yoohyun/research3`. Asset/build status: `completed`; both jobs write timestamped
`logs/<stamp>_q12_geometry_{assets,build}.log` and `.exit`.

```bash
tmux new-session -d -s research3_q12_geometry_assets 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/geometry/acquire.sh'
tmux new-session -d -s research3_q12_geometry_build 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/geometry/build.sh'
```

Acquisition expects two `.tgz` archives and two selected `.obj` files under the fixed dataset
path, plus `assets.json` with archive/member hashes, gzip CRC and original member inventory.
Verify bytes/SHA-256 against that receipt. Selection is written before payload inspection;
total network body is capped at 64 MiB and decompression at 256 MiB. The public index states
CC BY 4.0 for data and MIT for code. Local hashes do not establish publisher authentication.
Build expects `image_id.txt`, `image_bytes.txt`, `environment.txt`, and exit 0; synthetic method
preflight follows after the implementation is ready. No host method import/install is allowed.

Both jobs completed with exit 0: `logs/20260911_104214_q12_geometry_assets.log` and
`logs/20260911_104214_q12_geometry_build.log`. Original asset transfer was 19,093,132 bytes;
only the two OBJ members were extracted (2,921,244 bytes). Archive contents remain preserved.
The image's immutable reference is [image_id.txt](image_id.txt), Docker-reported size is in
[image_bytes.txt](image_bytes.txt); this is not a measurement of peak disk or memory usage.
Pinned wheel URLs/bytes/hashes are in [dependencies.json](dependencies.json), installed versions
in [environment.txt](environment.txt), and source-identity limits in [provenance.json](provenance.json).
The freshly installed wheel was exercised in Docker; the inspected upstream documentation commit
is not asserted to be its exact build commit.

## Frozen measurement scope

[protocol.json](protocol.json) owns all exact constants, grids and decision precedence.
[freeze.json](freeze.json) fixes the code, protocol, asset/dependency receipts and synthetic evidence.
This is **measurement readiness**, without any checkpoint or generated geometry mounted.

- Four cases: two selected YCB meshes × two fixed views. The longest mesh extent is assigned
  **0.12 m synthetic scale**, with a fixed world pose. This does not restore the physical units,
  training coordinate convention or camera of the original four 3DSGrasp XYZ files.
- DIRECT/TinyRenderer, 256×256 depth/mask, known camera axes and near/far. Two renders share the
  unchanged world; no physics steps occur. Retain both raw buffers and segmentation for verification.
  Oracle instance segmentation is shared by all future baselines.
- FPS selects 2,048 observed optical-frame points with fixed start index 0. Record the full depth,
  pixel selection, partial-derived normalization and inverse. This sampler is a declared new
  measurement adapter, not historical native operator parity.
- Each case has 32 gripper poses from observed-cloud centroid, camera axes and a fixed pose grid.
  Candidate JSON is written before GT labels/samples. The fixed 10 cm retreat is a clearance
  fallback, not a successful grasp. No table, robot arm, motion trajectory or force/lift outcome is modeled.
- Full-triangle-mesh queries provide surface contact. Solid-angle containment handles a gripper
  wholly inside a closed surface, which a surface-contact query alone can miss. The independent
  verifier uses triangle clipping and three ray-parity queries without importing PyBullet or
  `scene.py`. Opposite edge-incidence checks and queried-point agreement do not certify all
  self-intersections or real-object physical accuracy.
- Near-contact candidates within 0.5 mm are retained but excluded from robust comparisons under
  the fixed rule. Both collision and clear candidates must remain in every case. Both 8,192 and
  32,768 area-uniform GT surface-point controls must match the robust full-geometry labels; an
  occupancy/density failure is a measurement finding, not completion harm.

| Gate outcome | Fixed decision / next action |
| --- | --- |
| Source or asset identity failure | `INVALID_INTEGRITY`; stop before interpretation; nonzero integrity exit is preserved |
| Mesh/frame/ray/collision control failure | `REFINE_LINKAGE`; preserve all four case records and concrete failure |
| A case lacks robust collision or clear support | `UNINFORMATIVE_CANDIDATE_SUPPORT`; no data-dependent pose-grid expansion |
| Either oracle surface-point density disagrees with robust geometry truth | `REFINE_POINT_REPRESENTATION`; no completion attribution |
| All gates pass | `READY_FOR_BOUNDED_COMPLETION_DIAGNOSTIC`; prepare a separate completion adapter/execution freeze |

The future comparison is defined in `baseline_plan`: observed-only, observed+generated points,
free-space-consistent completion, and a conservative control that treats unknown space as occupied
on a fixed 2 mm gripper lattice. The lattice is a discrete control, not continuous-volume safety
certification. Share candidate utility and record false-clear/false-collision, selected-candidate
truth, abstention and useful-candidate rejection. Invalid/out-of-frame depth stays unknown. GT
serves only the evaluator and explicitly named oracle controls. No completion baseline is run here.

## Synthetic verification and preparation revision

[preflight.json](preflight.json) records **synthetic implementation checks**, not results on YCB.
The original near-surface-only draft lacked both candidate classes on analytic boxes. A single
pre-freeze revision replaced the −2.5 cm depth offset with a fixed −10 cm retreat; candidate count,
other pose dimensions, all thresholds and oracle densities were retained. The original draft,
negative synthetic receipt and rationale are preserved in [preparation_revision.json](preparation_revision.json).
No actual YCB mesh was rendered or numerically inspected to make that change.

The final synthetic preflight passed analytic plane depth, closed-edge/missing-face controls,
clear/surface-overlap/full-containment cases, two-view pipeline checks, and four-case command-line
execution followed by the independent verifier. The two-view camera sentinel maximum error was
0.000234772 m, below the predeclared 0.00075 m bound. Each of the four synthetic entrypoint cases
has 16 collision and 16 clear candidates; both oracle densities agree. Normalized-point tampering,
candidate-pose tampering with a refreshed hash, source mutation and output overwrite were rejected.
These are implementation and negative-path controls, not evidence of a useful completion effect.

Final job: `logs/20260911_105742_q12_geometry_preflight.log` / `.exit = 0`; raw receipt:
`runs/q12_geometry_preflight/20260911_105742/preflight.json`. Earlier preflights are preparation
history, including the retained negative candidate-support result.

```bash
tmux new-session -d -s research3_q12_geometry_revision_preflight 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/geometry/check.sh'
```

This completed pre-freeze command refuses to run once `freeze.json` exists. The checked code is
mounted read-only; no YCB assets/checkpoint are mounted in preflight. Synthetic scratch files are
container-local `/tmp` files; the compact receipt is copied back by the host orchestrator.

## Actual readiness command and verification

Status: **completed and audited** on 2026-09-11 after frozen files 20/20, asset hashes 4/4 and immutable
Docker identity matched; the output root was absent. Cwd `/home/yoohyun/research3`; command:

```bash
tmux new-session -d -s research3_q12_geometry_v1 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/geometry/run.sh'
```

`run.sh` refuses an existing `runs/q12_geometry_v1/`, checks frozen hashes and uses the immutable
image. Source/assets are mounted read-only; inference/GT/model directories from earlier stages
are not mounted. The producer writes `runs/q12_geometry_v1/data/`; a separate verifier reads it
read-only and writes only `runs/q12_geometry_v1/audit/`. Both processes run as the host UID with
network disabled, read-only container root, CPU 4/RAM 4 GiB and a combined 1,800 s timeout.
Output cap is 128 MiB. No GPU or training is involved. Runtime option/path details live in `run.sh`.

Expected files: four case records including failures, per-success-case raw observation/geometry
NPZ, candidate/result JSON, object geometry receipts, `data/result.json`, `audit/verification.json`,
`execution.json`, and timestamped `logs/<stamp>_q12_geometry_v1.log` / `.exit`. Check the exact
decision, four-case denominator, verifier error lists and every file hash in `execution.json`;
exit 0 alone is not readiness success. Integrity failures stop with a nonzero exit before a
scientific decision and remain `INVALID_INTEGRITY` in interpretation.

The frozen run completed with `REFINE_LINKAGE`: box views reached the independent verifier,
while both mug views stopped at the mesh gate. The frozen verifier copies producer errors for
such pre-render failures, so a separate post-run mesh audit independently recomputed those
edge/area checks. It did not repair the mesh or rerun rendering/collision/completion.
Post-run audit status: `completed`; command from the same cwd:

```bash
tmux new-session -d -s research3_q12_mesh_audit 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/geometry/verify_mesh.sh'
```

Expected output: `runs/q12_geometry_v1_mesh_audit/verification.json`; timestamped
`logs/<stamp>_q12_mesh_audit.log` / `.exit`. Verify independently computed counts against both
producer mesh receipts, case identity, frozen result/asset hashes and the final decision.

## Preservation and recovery

No external backup or deletion occurred. Preserve the two original archives and extracted OBJ
hashes for reproduction; a HEAD/ETag or local source cache cannot replace an asset backup.
Re-download into a separate staging directory using `assets.json` URLs, then verify bytes/SHA-256
before restoring a missing file. A changed public file is a new input revision. `acquire.py`
refuses an existing receipt; `build.sh` refuses the saved image/freeze records. Rebuilding must use
a new environment receipt and preserve the frozen image identity. Source hashes, protocol and
compact receipts suffice for documenting preparation, not for reproducing missing assets/runtime.
Actual readiness result preservation additionally requires the row-level NPZ/JSON and
execution/verification receipts. The former input/schema/completion freezes remain unchanged.

## Surface preservation audit 2026-09-14

Status: paired diagnostic and failure-detail inspection `completed`. This bounded post-failure assessment asks whether an explicit input revision
is justified; it does not change readiness v1 or admit completion inference. The raw mug's mesh
gate is bypassed **only inside this separate paired diagnostic** to inspect representation
sensitivity, never to relabel its failed v1 cases as successful.

Before execution, freeze [preservation_protocol.json](preservation_protocol.json), producer,
independent verifier and launcher. Use exact coordinate equality, retain first-occurrence vertex
order, and remove only exactly zero-area faces whose coordinates repeat. No positive-area face
may move, flip, disappear or change multiplicity/order. The verifier uses exact rational OBJ
coordinates and must prove every removed point/segment is already part of a retained triangle
edge/vertex; otherwise positive-area equality alone is insufficient. Preserve the original AABB
transform. Inspect corrected topology with the existing area/edge requirements.

For both objects and the same two views, compare raw and derived representations using the frozen
camera, candidate grid, samplers and seeds. Require exact depth/mask/FPS/candidate and oracle-point
equality, unchanged collision/near-contact decisions, and distances/winding within the existing
`1e-10` numerical bound. Independently recompute triangle-clipping labels and three-direction
containment on the same queries, including all gripper-box centers. These finite checks do not
prove all PyBullet queries, textured rendering, continuous safety, vertex-manifold topology or
absence of self-intersection. Exceptions/disagreements are retained and block a revision claim;
do not tune thresholds or replace cases. No checkpoint is mounted.

Cwd `/home/yoohyun/research3`; CPU 4 / RAM 4 GiB, no network, 1,800 s total timeout and 128 MiB
output cap. Run in the existing workspace-owned immutable geometry image using:

```bash
tmux new-session -d -s research3_q12_preservation_v1 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/geometry/preservation.sh'
```

Expected output: `runs/q12_mesh_preservation_v1/{data,audit}/` with separate derived OBJ/mappings,
eight raw/derived case payloads, a comparison receipt and independent verification; plus
`execution.json`. Logs: `logs/<stamp>_q12_preservation.log` and `.exit`. Inputs and old outputs are
read-only; only the separate output mount is writable. The launcher refuses an existing output
root. Verify all input/freeze/output hashes, four paired-case identities, independent exact
surface proofs, recorded runtime comparisons and exit status. A justified correction leads to
preparing a separate readiness revision; any unresolved surface/query change requires assessment
before further runtime. V1's `REFINE_LINKAGE` remains historical evidence.

The first audit completed with exit 0 but withheld revision support: all four producer pairs
matched, while mug still failed the corrected edge gate (3 remaining bad edges). Its exact
surface proof ran before that assertion, but the verifier did not serialize the intermediate
proof or run mug query checks after failure. Preserve that negative receipt. A separate
[inspection plan](inspection_plan.json) now records those omitted details and completes only
the skipped mug queries from saved arrays, without rerendering or modifying the correction.
CPU 2 / RAM 2 GiB, 600 s cap; original and paired outputs remain read-only.

```bash
tmux new-session -d -s research3_q12_preservation_inspection 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/geometry/inspection.sh'
```

Expected output: `runs/q12_mesh_preservation_v1_inspection/verification.json`; logs
`logs/<stamp>_q12_preservation_inspection.{log,exit}`. Verify independent exact-surface witnesses,
remaining edge/face identities and the saved-query results against the immutable paired inputs.
Any remaining edge failure defers this asset route even if finite query comparisons agree.

## Closing verification

Freeze SHA-256: `014e3edac4c4456afc3efc1c3622cc72b6150358feae1b15945394c647523e1c`.
All 20 new frozen files and all entries in the earlier input/schema/completion freezes (17/17/43)
matched. The four archive/OBJ hashes and immutable Docker identity matched. Python AST, JSON and
shell syntax checks passed. Eleven updated Markdown documents passed 250 local-link checks,
including 108 heading links, and Q12/Q13/TODO status checks. The actual output root was absent;
all preparation jobs had completed. No model inference, actual YCB scene run, artifact deletion or
hypothesis promotion occurred in this preparation task.

## Verified readiness results 2026-09-11

**Observed result:** the frozen producer and verifier completed in the pinned CPU Docker with
`logs/20260911_112642_q12_geometry_v1.exit == 0`. The scientific decision is
**`REFINE_LINKAGE`**, not readiness success. Both objects and all four case records were retained.
The box produced two sets of observations/candidates; mug stopped at the mesh gate before any
rendering or candidate creation. The original 32-candidate grid and thresholds were unchanged.

| Object / view | Camera max ray-depth error | Robust collision / clear | Near-contact | Outcome |
| --- | ---: | ---: | ---: | --- |
| `003_cracker_box` / v0 | 0.551784 mm | 15 / 16 | 1 | camera, independent geometry and both oracle densities passed |
| `003_cracker_box` / v1 | 0.449868 mm | 10 / 22 | 0 | camera, independent geometry and both oracle densities passed |
| `025_mug` / v0 | not measured | not generated | not measured | stopped: mesh solid topology unresolved |
| `025_mug` / v1 | not measured | not generated | not measured | stopped: mesh solid topology unresolved |

Box observations passed the predeclared 0.75 mm ray-depth bound, 32 ray sentinels per view,
depth/segmentation repeat equality, observed-point normalization/inverse and candidate provenance
checks. The independent clipping/ray verifier evaluated 64 candidate labels; the 63 robust
candidates matched the producer, and both 8,192/32,768-point oracle controls matched on those
63 candidates. The near-contact candidate remains recorded and excluded under the original rule.
Two successful views of one object do not establish the planned two-object readiness or generality.

### Independent confirmation of the mesh failure

The frozen verifier independently checked successful cases but copied the producer's early mug
errors. To verify that failure rather than merely repeat its message, [verify_mesh.py](verify_mesh.py)
re-read both raw OBJ files inside the same CPU image using scalar tuples, `Counter` and triangle
area arithmetic. It imports neither `scene.py`, NumPy nor PyBullet. Input/raw-output mounts were
read-only; it checked frozen/asset/output hashes and compared independent counts to the producer.
[mesh_audit.json](mesh_audit.json) reports `VERIFIED` with the same `REFINE_LINKAGE` decision.

| Mesh diagnostic | Cracker box | Mug |
| --- | ---: | ---: |
| raw vertices / exact coordinate classes | 8,194 / 8,194 | 8,188 / 8,185 |
| faces | 16,384 | 16,384 |
| raw-index edges: degree 2 | 24,576 | 24,576 |
| exact-coordinate edges: degree 2 / degree 4 | 24,576 / 0 | 24,558 / 9 |
| orientation-sum failures after exact merging | 0 | 3 |
| faces below the fixed `1e-14 m²` area bound | 0 | 6, all exactly zero area with repeated coordinates |

Mug's raw index graph passes the edge-incidence test, but coincident geometry and six collapsed
faces violate the coordinate-based solid gate. The exact face IDs and edge examples are retained
in the audit receipt. This is not evidence that a mesh hole, a camera error or a completion failure
caused robot harm. The first failed gate was topology; the separate audit also confirms that the
area gate would fail. No welding/removal/repair was applied to the stored mesh or runtime input.

Post-run audit command is recorded above and in [verify_mesh.sh](verify_mesh.sh). It used CPU 2/
RAM 1 GiB, a 300 s cap and no network. `logs/20260911_112907_q12_mesh_audit.exit == 0`;
the original receipt is `runs/q12_geometry_v1_mesh_audit/verification.json` (3,873 bytes).
Image/command, auditor and launcher hashes, resource limits and output identity are retained in
[mesh_execution.json](mesh_execution.json).
This is a post-run verification of the failure, not a revision of the frozen study.

### Artifacts and next decision

Compact byte-identical copies: [result.json](result.json), [verification.json](verification.json),
[execution.json](execution.json), and the mesh audit above. The producer/verifier output inventory
contains 14 files totaling 4,149,908 bytes before the execution receipt, below the 128 MiB cap.
Raw observation/geometry NPZ, candidates, object receipts and logs remain at the recorded runtime
paths; they must accompany compact summaries for reinspection. CPU/RAM figures are configured
caps, not measured peak consumption. This was not a latency benchmark.

**Interpretation and next task at the time:** retain Q12 `feasibility_study` / `refine` and withhold completion
comparison. A bounded next audit should determine whether exact-coordinate merging and removal
of these zero-area faces can be justified while preserving the positive-area surface, transforms
and independent geometric labels. This is a proposed measurement repair, not an established
equivalence or a new method. Any justified change needs an explicit separate revision preserving
v1 and its four-case denominator; otherwise defer this asset route. Do not replace the mug, relax
thresholds, fit to GT, or infer absence of the Q12 phenomenon from this operational failure.
Q13 is not automatically inherited. Native operator parity, completion benefit/harm, robot success,
learned-policy reliance and hypothesis admission remain unverified.

Closing artifact verification matched all four original freeze digests and their 17/17/43/20
entries, four asset hashes, fourteen producer/verifier output hashes, four byte-identical compact
copies and the post-run auditor/launcher/output identities. Both exit files were 0. Eleven Markdown
documents passed 265 local-link checks (116 heading links) and Q12/Q13/TODO consistency checks;
JSON, new-auditor AST, shell syntax and diff whitespace checks passed. Original assets, protocol,
candidate grid and all outputs were preserved.

## Preservation outcome 2026-09-14

**Decision — agent assessment: `DEFER_CURRENT_ASSET_ROUTE`.** Exact-coordinate merging and
removing the six repeated-coordinate, exactly zero-area mug faces preserves the represented
surface and the tested queries, but does **not** satisfy the original mesh edge gate. Do not
prepare readiness v2 from this correction, remove further faces, or start completion inference.
Q12 remains `feasibility_study` / Stage 7 `refine`; this asset route is deferred, without a claim
that generated geometry cannot affect actions. Q13 remains deferred independently.

### Exact surface and remaining failure

[Independent inspection](inspection_result.json) proves equality using rational numbers parsed
from the original OBJ coordinate literals. The retained positive-area oriented triangle sequence
is exactly equal in coordinates, order and multiplicity. Every removed face is a segment that is
also an edge of a retained triangle; all six witness pairs are in the receipt. Thus this establishes
equality of the represented triangle surface set, including removed zero-area support, rather than
only an area/volume statistic. Exact-coordinate classes retain first-occurrence order, and the
original AABB/transform and world triangle coordinates are unchanged. Textures/normals/UVs are not
part of this claim: the frozen renderer uses explicit vertex/index arrays with constant color.

| Mug diagnostic | Original | Derived audit copy |
| --- | ---: | ---: |
| coordinate vertices | 8,188 raw / 8,185 distinct | 8,185 |
| triangles | 16,384 | 16,378 |
| degree-2 / degree-4 coordinate edges | 24,558 / 9 | 24,561 / 3 |
| orientation-sum failures | 3 | 0 |
| exactly zero-area triangles | 6 | 0 |
| minimum triangle area at declared scale | 0 | approximately `7.155919e-11 m²` |

The area gate (`1e-14 m²`) passes after correction; the edge gate still fails. Independent
incidence counting identifies the remaining edges and **all four incident positive-area faces**:

| Derived vertex edge, zero-based | Original incident face IDs, zero-based |
| --- | --- |
| 1708–1709 | 3006, 3570, 3571, 3573 |
| 5271–5272 | 9917, 9918, 9920, 9924 |
| 6287–6288 | 12327, 12330, 12331, 12337 |

Three unoriented positive-area duplicate triangle pairs also remain: original face pairs
`3570/3571`, `9918/9920`, `12330/12331`. They are not the zero-area faces. Deleting positive-area
triangles or changing their oriented multiplicity is outside the tested correction and its proof;
these results do not justify that additional operation. No hole filling, remeshing, vertex motion,
epsilon welding, threshold relaxation or case replacement was attempted. No global vertex-manifold,
self-intersection or physical-object fidelity certificate is claimed.

### Fixed-query comparison

The paired producer reused frozen `scene.py` for raw/derived representations of both objects and
both views; all four pairs matched. Each variant retained the original repeat depth/segmentation
render check. Full saved depth/segmentation/masks, FPS indices/points/normalization, candidate JSON
bytes, oracle points/barycentric weights and mapped sampled triangle IDs were exactly equal.
All 128 candidate collision/near-contact/oracle flags were unchanged. Maximum recorded contact
distance difference was 0; maximum absolute-winding difference was `2.220446049250313e-16`, below
the original `1e-10` numerical bound. All near-contact records remain present.

The independent checker imports neither `scene.py` nor PyBullet. Its first run checked the box
cases but stopped mug at the corrected edge assertion, preserving the negative result in
[preservation_verification.json](preservation_verification.json). The separately frozen failure
inspection retained the missing exact-surface proof and completed the previously skipped mug
queries from saved arrays. Across the two receipts, raw/derived triangle-clipping/ray labels agree
on all 128 candidates, the 125 robust candidates agree with producer labels, and all 384 paired
box-center containment queries agree with solid-angle flags. The 3 near-contact candidates were
excluded only under the original robustness rule. The supplemental inspection does not overwrite
the first audit or declare readiness success.

This verifies finite-query representation sensitivity only. The mug readiness camera sentinel and
oracle-support gates have not been admitted by a valid mesh gate. Finite equal labels cannot
establish global solid topology, grasp success, continuous safety, native operator parity,
completion benefit/harm or learned-policy reliance.

### Execution, preservation and next task

The commands above ran in immutable CPU image
`sha256:0196da1a3a01ca07186c5c2c605d7e8993193ca810b2b6401dc95943dc0b0adb`.
[Preservation freeze](preservation_freeze.json) fixed 9 files before derived meshes or paired
outcomes; its SHA-256 is `2e2328e2c941c62b75fd1f1087960922ec5afc61906840d9c5c64cd6cc040072`.
It was explicitly informed by the earlier v1 failure, not a claim of outcome-blind research
selection. [Inspection freeze](inspection_freeze.json) fixed the follow-up's 5 files after the
first audit failed, before inspection execution; SHA-256
`7cff27eecd1e0074806bd890be2c366dc540394c8d6aff7aaaba7f1c8b398bcb`.

Closing verification matched all six freeze digests and their 17/17/43/20/9/5 entries, original
asset hashes, 14 original and 38 paired output hashes, compact byte copies and inspection/source
identities. The independent exact-proof positive control passed and five negative controls rejected
coordinate motion, orientation reversal, positive-face removal/duplication and uncovered degenerate
support. Eleven Markdown documents passed 288 local-link checks (128 heading links), with matching
Q12/TODO disposition; JSON, Python AST, shell syntax and whitespace checks passed. Both new jobs
completed with no matching container left running.

Byte-identical compact receipts: [paired result](preservation_result.json),
[first independent verification](preservation_verification.json),
[paired execution/inventory](preservation_execution.json), [inspection result](inspection_result.json).
[Inspection execution](inspection_execution.json) records its launcher, image, input/output hashes
and limits. Exact runtime/dependency lineage remains the frozen Dockerfile, wheel lock and
`scene.py`/`verify.py`; no new package or model was installed.

`logs/20260914_111854_q12_preservation.log` and
`logs/20260914_112130_q12_preservation_inspection.log` each have exit 0. The paired output inventory
contains 38 files / 17,837,347 bytes before `execution.json`, below 128 MiB. The independent
inspection output is separate and preserved. Exit 0 means completed diagnostics, **not** a passed
scientific gate. Resource limits are configured caps, not measured peak use or a latency benchmark.

For reinspection preserve both `runs/q12_mesh_preservation_v1/` (derived OBJ/mapping plus eight
case payloads) and `runs/q12_mesh_preservation_v1_inspection/` along with their original assets and
v1 outputs. Source/compact receipts alone preserve the decision but not all numerical evidence.
To reproduce, use the immutable source/recipe and a separately named output/container/log path;
the recorded launchers intentionally refuse existing roots. No external backup, deletion, input
overwrite, original v1 rerun or full-reproduction cleanup was performed.

**Next at this decision:** compare a bounded alternative measurement route with deferring Q12 further, using
camera/GT independence, valid geometry, artifact access, cost and expected information as the
criteria. Do not silently substitute another object into the failed four-case study or continue
trial-and-error mesh repair. Any new measurement needs a prospective scope/protocol and the same
baseline/claim discipline; Q13 is not an automatic successor.

The subsequent [route comparison](../README.md#alternative-routes-2026-09-14) selected preparation
of a separate BOP YCB-V real-data camera/model audit. That parent owner contains its source-access
evidence and current scope. The frozen Google 16k assets, diagnostics and deferral above remain intact.
