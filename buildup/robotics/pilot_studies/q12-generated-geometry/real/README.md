# Real RGB-D Input Audit

Updated: 2026-09-14 · Q12 deferred after reassessment; frozen audit: DEFER_RAY_SUPPORT

최신 runtime 정리·복구 판단은 [Docker cleanup review](../../../../../docs/reproducibility.md#docker-cleanup-review-2026-09-16)를 따른다. 이전 유지 권고는 보존 기록이며, 현재는 재빌드를 감수하면 image 삭제 가능하다. 실제 삭제는 없다.

This folder owns the separate BOP YCB-V input audit selected in the
[route comparison](../README.md#alternative-routes-2026-09-14). Scene 48, frames 1/36, all five
standard object models (1/6/14/19/20) and ten object/frame records are retained. This does not
replace the failed Google 16k study. Q12 is now `deferred`; the unresolved formulation retains
Stage 7 `refine` without an active follow-up study. The [reassessment](#reassessment-2026-09-14)
owns the current decision and re-entry conditions.
The [real audit outcome](#verified-real-input-results-2026-09-14) pauses this separate route under
the frozen ray-support rule. Sensor/pose calibration remains unresolved.

## Boundary and frozen criteria

Freeze the acquisition selection and protocol before downloading image/model members. A later
execution freeze additionally pins the built image, acquired bytes, code and synthetic checks
before any real numerical execution. During preparation real files are downloaded/checksummed
only; synthetic fixtures alone exercise the numerical pipeline. No checkpoint or action selector
is used. Originals are read-only, with derived outputs at separate workspace paths.

The official BOP format supplies camera K, depth scale and model-to-camera pose. Pinned
`misc.py` uses integer pixel centers and Z-depth. Pinned `visibility.py` permits missing-depth
pixels in `bop19` visible masks. Therefore mask membership never makes invalid depth known-free.
Mask derivation depends on GT geometry/pose and the source's 15 mm visibility parameter, which
is not a collision tolerance. Exact source identities are recorded in `sources.json`.

Numerical identity/coordinate checks and mesh edge/area tests can establish input consistency.
They cannot bound real sensor or annotated-pose errors. No defensible physical-error upper bound
has been established for these two frames. Predeclare **calibration unresolved** even if numerical
controls pass; do not fit a threshold from their residuals. Residuals are diagnostic observations,
not collision labels or evidence of completion harm. Preparation may still yield a frozen input
audit to locate the remaining failure, but cannot yield physical/free-space admission.

[Protocol](protocol.json) owns the numerical bounds, diagnostic pixel selection, fields and decisions.
No mesh welding/removal, model variant substitution, frame replacement, recentering or GT fitting
is allowed. A mesh failure is retained for both object/frame records; other input checks may run
for diagnosis without turning it into a passing physical case.

## Jobs and resources

Cwd `/home/yoohyun/research3`. Image `research3-q12-real-input:v1` is built from a pinned official
Python base with locked NumPy/Pillow/plyfile wheels; no prior simulator/image is a research base.
Dataset path `datasets/q12/bop_v1/`; acquisition response bodies <=16 MiB and unpacked selected
members <=64 MiB. Configured CPU 4 / RAM 4 GiB; numerical producer/verifier <=1,800 s and output
<=128 MiB. Network is disabled for numerical work. No GPU, training or model inference.

```bash
tmux new-session -d -s research3_q12_real_build 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/real/build.sh'
tmux new-session -d -s research3_q12_real_assets 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/real/acquire.sh'
tmux new-session -d -s research3_q12_real_preflight 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/real/check.sh'
```

All three jobs are `completed` with exit 0. Build stamp `20260914_115314`, acquisition stamp
`20260914_115528`, final synthetic check stamp `20260914_121224`; each has the corresponding
`logs/<stamp>_q12_real_{build,assets,preflight}.log` and `.exit`. The final synthetic output is
`runs/q12_real_preflight_20260914_121224/`. Earlier successful checks at `120934` (eight groups)
and `121120` (nine groups) remain preserved; the final pass also explicitly checks process import
isolation. No real mesh coordinates or real image arrays were inspected during preparation.

## Preparation evidence 2026-09-14

**Verified facts:** [selection](selection.json) retains scene 48, frames 1/36, models 1/6/14/19/20
and all ten records. [Asset receipt](assets.json) and saved HTTP bodies verify 37 selected members,
74 exact Range responses, 3,384,724 response bytes and 7,173,658 unpacked bytes. Member CRC/SHA-256
and compressed-byte hashes agree. The receipt includes PNG IHDR metadata only, not decoded pixels.
The earlier route-search response bodies (1,087,565 bytes) are separate; together the two acquisition
stages remain below 16 MiB. Full archive LFS hashes are not verified by these selective downloads.

The new image is `research3-q12-real-input:v1`, immutable ID
`sha256:01331a0e031a47b013f8b7d26e2c24d284a8803f9b47827c56551c79ffcd55b2`.
Docker reports 82,234,923 image bytes; this is not the total host cache/disk footprint.
[Dockerfile](Dockerfile), [wheel lock](requirements.txt), [dependency sources](dependencies.json)
and [environment](environment.json) pin Python 3.11.13, NumPy 1.26.4, Pillow 12.3.0 and plyfile 1.1.3.
The BOP toolkit commit and copied read-only source hashes are in [sources.json](sources.json);
no BOP toolkit or simulator was executed.

[Synthetic receipt](preflight.json) passes nine groups. The positive fixture has ten records,
ASCII/little-endian/big-endian PLY, nonidentity rigid poses, two depth scales and one visible pixel
with missing depth per case. Separate producer and verifier processes agree; the verifier process
does not import the producer, Pillow or plyfile. Its PNG filters/CRC and PLY scalar parser, edge
counts, homogeneous transforms and plane/barycentric rays are independent implementations.

| Control | Verified outcome |
| --- | --- |
| Closed synthetic boxes, correct poses and images | Ten records; numerical controls pass; calibration remains unresolved |
| Five PNG filters for RGB8 and depth16, followed by CRC corruption | Both encodings agree with known arrays and Pillow; corruption rejected |
| One omitted triangle | `DEFER_GEOMETRY`; all ten records retained |
| Reflected pose | `DEFER_INPUT_LINKAGE`; independently confirmed |
| Rigid pose translated outside observed rays | `DEFER_RAY_SUPPORT`; independently confirmed |
| Half-pixel offset in saved camera points | Verifier rejects output |
| Modified signed residual | Verifier rejects output |
| Modified GT index | Verifier rejects output |
| Fabricated input failure on valid input | Verifier rejects output |

The [acquisition/criteria freeze](preparation_freeze.json) predates image/model member acquisition.
The final [execution freeze](freeze.json) pins 29 files before real numerical execution; SHA-256
`30398fce4e7aa90a79219e54ba45020c323d6b432501d0bbd0cfe93523b60d8f`.
[Byte/source validation](validation.json) confirms all six prior study freezes and the acquisition
freeze unchanged; the command below additionally verifies the final execution freeze.

A packaging attempt created an empty JSON file by redirecting validation output into the directory
being validated. Its invalid freeze and empty payload are retained in [packaging.json](packaging.json),
[freeze_attempt.json](freeze_attempt.json) and `validation.empty`. The corrected package was created
only after successful validation through a temporary file outside this folder. No selection,
threshold, numerical implementation or real-data outcome changed in this packaging correction.

**Interpretation at preparation completion:** the prepared numerical diagnostic could identify
schema, geometry and ray-support failures. Physical/free-space admission was deferred because
sensor/pose uncertainty remained unresolved; even a numerical pass could not justify starting a
collision/evaluator study. The actual result and next requirement are recorded below.

## Execution and recovery

Execution status: `completed` and independently `VERIFIED` on 2026-09-14. Log:
`logs/20260914_122659_q12_real_input.log`, matching `.exit` = 0. The frozen runner reports 3 seconds
for producer plus verifier, within the 1,800-second cap. A completed audit with `DEFER_RAY_SUPPORT`
does not mean the input route passed. All ten records and the calibration boundary are retained.

[run.sh](run.sh) ran in Docker with inputs read-only,
producer outputs at `runs/q12_real_input_v1/data/`, verifier at `runs/q12_real_input_v1/audit/`
and a final execution inventory. The runner refuses the now-existing output root. The actual
numerical execution followed the completed preparation as a separate TODO.

```bash
# Byte/manifest/syntax checks only; safe on host, no method imports.
python buildup/robotics/pilot_studies/q12-generated-geometry/real/validate.py

# Executed command; refuses the existing output root and must not overwrite it.
tmux new-session -d -s research3_q12_real_input 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/real/run.sh'
```

`run.sh` uses the immutable image ID, 4 CPUs / 4 GiB, no network, the current user's UID/GID,
read-only root/source/dataset and separate output mounts. It enforces a combined producer/verifier
1,800-second cap, a 128 MiB per-file OS limit and a final aggregate output cap. The verifier receives
producer output read-only. `execution.json` records output sizes/hashes, mounts, image, elapsed time,
unchanged input hashes and the verified decision. Integrity failure aborts with `INVALID_INTEGRITY`;
failed/partial runs and logs must be retained, not overwritten or counted as successful cases.
There are 18 output files totaling 1,136,510 bytes, including `execution.json`. Its 17 payload
entries comprise five raw-model NPZs, ten case NPZs, producer JSON and independent verification JSON.
Post-run byte inspection confirms the complete inventory and unchanged inputs/freezes.

To repeat verification when justified, use a fresh empty audit directory with this command
(it reads the existing producer output only):

```bash
study=buildup/robotics/pilot_studies/q12-generated-geometry/real
stamp=$(date +%Y%m%d_%H%M%S)
audit="runs/q12_real_input_audit_${stamp}"
mkdir "$audit"
timeout 1800 docker run --rm --name "research3-q12-real-audit-${stamp}" --network none --read-only \
  --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 4g --memory-swap 4g \
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  -v "$PWD/$study:/study:ro" -v "$PWD/datasets/q12/bop_v1:/input:ro" \
  -v "$PWD/runs/q12_real_input_v1/data:/producer:ro" -v "$PWD/$audit:/output:rw" \
  "$(cat "$study/image_id.txt")" /study/verify.py --data /input --input /producer --output /output
```

Run that command as a timestamped background job if needed; the initial runner already performs
independent verification, so an additional repeat is warranted only by a new unresolved concern.

Retain selected member bytes, partial compressed transfers, selection/acquisition receipts, source
and environment pins. Partial acquisition verifies member CRC/length/local SHA-256, not the full
archive LFS hash. Recovery fetches exact immutable URL/ranges into a separate staging root and
checks the receipt before restoring; no full archive fallback or automatic changed-input reuse.
Recipe/source/compact receipts document the study, while full reproduction also requires assets
and the runtime image or rebuilding it with a new identity record. For preservation of the current
diagnostic, retain the complete output root and input/source identities; this is not a paper result.
For resuming further analysis, also retain the original selected RGB-D/masks/models and image.
No deletion or external backup was performed.

## Verified real input results 2026-09-14

**Verified facts:** the frozen producer and separate independent verifier both return
**`DEFER_RAY_SUPPORT`**, with denominator 10 and `physical_admission: false`.
[Outcome excerpts](outcome.json), [independent verification](verification.json) and
[execution inventory](execution.json) are the compact records. The latter two are byte-identical
copies of their raw output receipts. Full per-ray signed values, selected pixel indices and
coordinate arrays remain in the output root above.

- All five original standard model assets pass finite/indexed triangle, physical-unit AABB,
  positive-area and opposite-edge incidence checks. This includes object 14 (mug). No vertices
  or faces were removed/merged and no model variant was substituted. Coordinate equivalence
  classes are used for topology diagnosis only. This does not change the Google 16k mug result
  or prove absence of self-intersection or physical calibration error.
- All ten cases pass RGB/depth/mask schema, GT-index association, camera/rigid-pose structure and
  coordinate round trips. Maximum producer projection error is `5.684341886080802e-14` pixels;
  maximum inverse-transform error is `4.440892098500626e-16` m. Every case has at least 2,048
  valid observed pixels. These checks confirm numerical consistency, not sensor accuracy.
- Every case retains 32 fixed diagnostic rays. Six rays, in six distinct cases, have no positive
  intersection with their selected object model. The other 314 rays intersect. Four cases have
  all 32 intersections, so the frozen all-case ray-support gate fails. The independent plane/
  barycentric implementation reproduces every hit/miss; maximum common-hit depth difference
  from the producer is `5.551115123125783e-16` m.

| Frame | Object ID | Valid visible depth pixels | Visible pixels with missing depth | Missing rays / 32 | Median absolute residual (mm) | Maximum absolute residual (mm) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 19,811 | 1,918 | 0 | 3.471 | 24.290 |
| 1 | 6 | 4,775 | 2,541 | 1 | 0.930 | 16.708 |
| 1 | 14 | 10,621 | 1,585 | 1 | 1.325 | 8.721 |
| 1 | 19 | 5,004 | 2,444 | 1 | 1.461 | 9.737 |
| 1 | 20 | 16,501 | 8,543 | 0 | 1.420 | 38.734 |
| 36 | 1 | 19,885 | 2,360 | 0 | 3.449 | 13.261 |
| 36 | 6 | 4,406 | 3,005 | 1 | 0.962 | 26.182 |
| 36 | 14 | 11,126 | 1,256 | 1 | 0.791 | 8.197 |
| 36 | 19 | 5,442 | 2,239 | 0 | 1.152 | 1,943.245 |
| 36 | 20 | 18,209 | 7,206 | 1 | 1.860 | 92.743 |

Residual summaries use only the 31 or 32 defined model intersections as specified before execution;
missing intersections remain explicit missing values. All 320 selected rays remain in the denominator,
and no finite residual was removed. Missing-depth mask pixels are separately counted as unknown.
The millimeter values above are rounded displays of the raw meter-valued diagnostics, not new metrics
or sensor acceptance thresholds.

**Failure excerpts:** five of the six missing rays are sample index 0 (the first row-major valid
visible pixel); frame 1/object 19 is index 24. Their `(v,u)` pixels are `(280,328)`, `(45,283)`,
`(270,374)`, `(277,307)`, `(40,262)` and `(327,131)` in table order. Exact case/depth associations
are retained in `outcome.json`. The largest defined residual occurs at frame 36/object 19,
index 0, pixel `(114,342)`: observed Z = `2.7840000000000003` m, model Z =
`0.840754565694811` m, signed residual = `+1.9432454343051893` m. Ray intersection support alone
therefore does not establish consistent measured depth. These are excerpts from the already
verified fixed outputs, not additional sampling or a new fitted criterion.

**Agent interpretation and next requirement:** mesh-edge failure is not the immediate limiting
gate for these five BOP assets. Visible-mask membership plus positive sensor depth does not ensure
that every frozen camera ray intersects the annotated model, and small median residuals do not
bound the observed tail. This audit does not identify the cause of each discrepancy. Pixel/raster
conventions, mask provenance and sensor/pose correspondence need a bounded source/record assessment;
do not infer any one cause from sample position alone.

This execution paused the real-data measurement route under the predeclared rule. The next selected
task was the single assessment below of these failures and unresolved calibration evidence.
Do not repair meshes, move samples, replace frames/objects, relax the all-ray criterion, fit a sensor
threshold, or proceed to collision/evaluator/completion comparison from this failed audit. Q12
remains a feasibility question with no demonstrated completion-specific action effect; no automatic
Q13 succession or hypothesis admission follows.

## Reassessment 2026-09-14

**Decision: defer further Q12 investment.** Status is `completed`; question status changes from
`feasibility_study` to `deferred`. Stage 7 remains an unresolved `refine`, with no active study or
hypothesis admission. The frozen `DEFER_RAY_SUPPORT` and `physical_admission: false` are unchanged.
This decision concerns the currently evidenced measurement routes, not absence of the proposed
completion-specific action phenomenon. [Source and record receipt](reassessment.json) separates
new source inspection from the already verified numerical outputs.

### Source evidence and failure interpretation

**Verified source fact:** [pinned visibility code](https://github.com/thodan/bop_toolkit/blob/cea62d651c7e395b2e1962b9749e4e89693c6ac4/bop_toolkit_lib/visibility.py#L9-L38)
uses `D_model - D_test <= delta` for positive distances. The `bop19` branch additionally permits
missing test depth. Both modes are one-sided. Here D is camera distance; our residual table uses Z.
The [mask generator](https://github.com/thodan/bop_toolkit/blob/cea62d651c7e395b2e1962b9749e4e89693c6ac4/scripts/calc_gt_masks.py)
renders the annotated model/pose, converts depth to distance and uses a default delta of 15 mm.
**Inference:** any positive measurement farther than a positive rendered distance passes this
visibility inequality, however large their difference. Visibility is therefore not an absolute
depth-agreement certificate. The retained large positive residual is compatible with that
semantics; its physical cause is not identified. The source default is not evidence of the exact
archive-producing revision, renderer or settings.

**Verified source fact:** cached `misc.py` back-projects an integer array grid. Newly inspected
[pinned Vispy source](https://github.com/thodan/bop_toolkit/blob/cea62d651c7e395b2e1962b9749e4e89693c6ac4/bop_toolkit_lib/rendering/renderer_vispy.py)
uses K without an explicit half-pixel correction, a full-image viewport and a vertically flipped
depth readback. [Khronos](https://registry.khronos.org/OpenGL/extensions/ARB/ARB_fragment_coord_conventions.txt)
specifies half-integer default OpenGL pixel centers; changing the fragment-coordinate qualifier
alone does not change rasterization.
**Inference:** raster/ray sampling conventions are a plausible contributor to model-support
disagreement. Five misses are the first row-major valid pixel, but the sixth is sample 24.
Neither sample position nor source inspection establishes the cause of any particular miss.
Archive-generation lineage and raster parity remain unverified; no shifted-ray test was run.

**Paper statements:** [PoseCNN §IV-A/B](https://rse-lab.cs.washington.edu/papers/posecnn_rss18.pdf)
describes first-frame manual pose initialization, SDF refinement against depth, depth-video camera
tracking and joint optimization. It identifies rolling shutter, model inaccuracy, RGB/depth timing
and camera-parameter uncertainty as annotation-error sources.
**Official dataset statement:** [BOP's YCB-V description](https://bop.felk.cvut.cz/datasets/#YCB-V)
reports manually curating test frames to avoid erroneous poses and transforming models/poses
consistently. **Inference:** these references are independent of our completion checkpoint, but
not independent physical metrology of the same depth. The inspected sources and selected-frame
metadata do not supply a justified sensor/pose error bound for this audit. Curation, ADD thresholds,
the visibility delta and our small coordinate round trips cannot supply it.

### Follow-up value and stop decision

| Possible follow-up | What it could establish | Current decision |
| --- | --- | --- |
| Recover mask-renderer lineage and compare raster conventions | Numerical agreement between a particular renderer and fixed rays | A valid engineering question, but does not resolve sensor/model/pose uncertainty or test Q12 action reliance; no new renderer branch |
| Erode masks, remove large residuals, shift samples or fit poses against these frames | Agreement on a changed, GT-selected subset | Would change the frozen study or condition on the reference being tested; no such revision |
| Use the five BOP models in a new controlled synthetic study | Known modeled geometry/camera; independent collision controls can be designed | Potential future route, not ruled out. Requires a separate observable action contrast and completion input/representation controls; mesh-gate success alone does not justify another preparation cycle |
| GraspNet, analytic solids or native/original-frame recovery | Different benchmark semantics, constructed controls or operator/frame evidence | Earlier access, attribution and setup limits remain in the [route comparison](../README.md#comparison-and-why-this-next-step); no new evidence warrants automatic expansion |
| Defer Q12 and compare other questions | Redirect effort after the bounded measurement assessment | Selected; existing evidence is useful for re-entry and is preserved |

This is an information-value decision, not a demand for perfect real-data calibration or a final
method before a candidate can be studied. A future modeled-geometry claim can use a declared
reference and uncertainty treatment appropriate to that claim. At present, further mask/raster
work alone would not test the proposed phenomenon, and no completion-specific action contrast
has been observed. Small median residuals do not justify ignoring undefined rays or the tail.

**Conditional re-entry:** a concrete source/control-supported observation–geometry–action study
must specify its intended claim (modeled collision or physical outcome), how reference uncertainty
or construction is handled, an accessible completion route with input/representation controls,
observed-only/consistency/conservative baselines, and a bounded cost and stop rule. This requires
a reviewable study design, not positive results in advance. Compare its expected information
against other candidates before activating it. Original-frame metadata or archive-renderer
provenance can support such a proposal, but alone does not reopen Q12.

**Work and preservation:** this reassessment inspected source text and existing JSON records only;
the only new source download was the 21,453-byte pinned renderer, never imported or executed.
No images/meshes were decoded, and no numerical/model/evaluator run or input/output mutation was
performed. The eight prior freezes, selected input bytes and complete BOP output inventory are
checked by the artifact verification recorded in `reassessment.json`. New source is outside the
frozen audit and does not retroactively change its provenance. No asset/image deletion or external
backup occurred. Next work is comparative Robotics question assessment under the existing scope;
Q13 remains conditional, and no candidate is automatically selected.
