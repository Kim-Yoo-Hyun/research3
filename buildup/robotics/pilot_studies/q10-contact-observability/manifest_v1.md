# Q10 Contact-Outcome Observability — Artifact/Schema Feasibility Study v1

Created: 2026-09-06

## Status

`executed`, `REFINE_SUBSET`

This is a Stage 6 feasibility study under
[`docs/buildup.md`](../../../../docs/buildup.md). It reduces Q10-A matched-denominator and
Q10-F access-cost uncertainty. It does not train or evaluate an outcome detector and cannot
establish the Q10 phenomenon or novelty.

## Selection Decision

Q10 is selected as the only new Stage 6 candidate for this study. Q8 remains `under_review`, and
the existing Q1 study remains paused. The reason is that Q10 has a public, labeled, multimodal
substrate and its first uncertainty can be reduced without GPU use or a bulk download.

## Feasibility Question

Can the immutable public REASSEMBLE record, its small official artifacts, HTTP byte-range access
and pinned loader source establish all of the following before downloading the 58.9 GB data ZIP?

1. exact official train/validation file membership;
2. disjoint file-level split membership and correspondence with ZIP members;
3. a code path from each HDF5 file to RGB, force/torque, proprioception, timestamps and
   segment-level Boolean success/text/start/end;
4. whether exact matched success/failure counts require reading HDF5 payloads;
5. whether a bounded per-file or small-subset download is technically possible.

## Frozen Public Inputs

Dataset record:

- DOI: `10.48436/0ewrv-8cb44`
- record ID: `0ewrv-8cb44`
- version: `1.0.0`
- API revision observed before specification: `6`
- license: `CC BY 4.0`
- record API: `https://researchdata.tuwien.ac.at/api/records/0ewrv-8cb44`

Official files:

| file | exact bytes | official MD5 |
| --- | ---: | --- |
| `data.zip` | 58,881,334,586 | `812103a652ca9201e87a3bcecfee4ef3` |
| `poses.zip` | 89,431 | `2f3f86b65dc6312b504072a2460314c2` |
| `README.txt` | 8,138 | `2e1394a2fa65e4ebb6c1fd64136cb0a0` |
| `splits.zip` | 1,094 | `641882928ef3a8b2c3db41ac7c60b994` |

Official source:

- repository: `https://github.com/TUWIEN-ASL/REASSEMBLE.git`
- branch used only for provenance: `master`
- pinned commit: `432cc15ce3e028edc2f98a786f28bf6baf31ac6f`
- primary schema/loader file: `REASSEMBLE/io.py`, Git blob
  `2d4f94b834c880ae857fad2257b1789d5c517a3d`
- supporting files: `README.md`, `scripts/statistics/stats_high_level.py`,
  `scripts/labeling/check_high_level.py`

No moving branch or latest dataset version may silently replace these inputs.

## Allowed Actions

- Fetch the record JSON, `README.txt`, `splits.zip` and exact pinned text source files.
- Verify every available checksum before inspection.
- Issue HTTP `HEAD` and byte-range `GET` requests against `data.zip`.
- Read only the ZIP end record, central directory and member headers needed to list archive members.
- Use Python standard-library code on the host for metadata parsing; this is permitted lightweight
  artifact inspection, not external method execution.

## Forbidden Actions In v1

- Do not download the complete `data.zip` or extract HDF5/video payloads.
- Do not train a probe, decode video, run REASSEMBLE code or install its dependencies on the host.
- Do not use, run, modify, retag or delete any pre-existing Docker image/container/volume or Isaac
  asset.
- Do not create manual labels in this metadata-only study.
- Do not change the required modality set after seeing counts.

Any later HDF5 parsing or model execution requires a new protocol version and a new
project-specific Docker image/cache/output boundary.

## Required Fields And Checks

### Record integrity

- record/version/revision, public-access flag and license;
- exact filename, byte size, checksum and content URL for all four files;
- `Accept-Ranges`, `Content-Length`, ETag/MD5 and last-modified response fields for `data.zip`.

### Split structure

- filenames contained in each split file;
- count per split, duplicates within a split and overlap across splits;
- split filenames absent from the central-directory HDF5 member list;
- HDF5 members not assigned to an official split.

### HDF5 join schema

The pinned source or official README must expose paths/accessors for:

- at least one RGB stream and its timestamps;
- measured or compensated force/torque and timestamps;
- robot pose, gripper or joint state and timestamps;
- high-level segment start, end, success and text;
- file or segment identity needed to join these fields.

### Access granularity

- number and names of members in `data.zip`;
- compression method, compressed/uncompressed size and local-header offset per HDF5 member;
- whether individual member byte ranges can be derived from the ZIP structure;
- whether exact segment labels/counts are present outside the HDF5 payload.

## Metrics

1. `split_count_train`, `split_count_validation`, duplicate count and overlap count
2. `archive_h5_count`, split-to-archive missing count and unassigned HDF5 count
3. required schema fields found / required schema fields listed above
4. bytes transferred for metadata inspection / 58,881,334,586 bytes
5. exact matched segment denominator available without HDF5 payload: `yes/no`
6. bounded member/subset retrieval technically derivable: `yes/no/ambiguous`

No classifier metric, accuracy, calibration or scientific effect size is reported in v1.

## Frozen Decision Rules

### `PASS_METADATA`

All small official artifacts verify, official splits are non-empty and disjoint, every split HDF5
file maps to an archive member, all required modality/label access paths are documented, the ZIP
metadata permits bounded member retrieval, **and** exact matched segment counts are available without
reading HDF5 payloads.

### `REFINE_SUBSET`

All structural checks for `PASS_METADATA` succeed, but exact matched counts require HDF5 content.
Freeze a v2 protocol that downloads the smallest pre-selected file subset spanning train/validation
and documented sensor-issue conditions. Do not select files by observed labels.

### `REFINE_TARGET`

Only a subset of RGB, force/torque, proprioception or segment outcome is jointly available, but one
scientifically meaningful action/modality target remains. Narrow Q10 before any bulk download.

### `REJECT_ROUTE`

Use this if split membership cannot be mapped to data, required modalities/outcomes cannot be joined,
or bounded inspection is impossible and a full download is incompatible with available storage.
Do not proceed to a detector or learned method.

## Resource And Output Boundary

- GPU: not used; the 2026-09-06 snapshot showed RTX 5090 at 0% utilization and 405 MiB used.
- Filesystem: 168 GiB available at specification time; full ZIP/extraction is forbidden in v1.
- Raw small artifacts: `/home/yoohyun/research3/datasets/q10_reassemble/v1/`
- Versioned generated outputs:
  `/home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v1/`
- The ignored `datasets/` input cache is never overwritten; checksum mismatch stops inspection.
- Generated JSON/TSV/log outputs are immutable inputs to the result section and are not edited to
  fit a desired conclusion.

## Expected Deliverable

The manifest result section must contain:

- exact integrity and split counts;
- archive-member and split correspondence;
- required-field evidence with pinned source line/path references;
- transferred-byte cost and access-granularity result;
- one of `PASS_METADATA`, `REFINE_SUBSET`, `REFINE_TARGET` or `REJECT_ROUTE`;
- the next bounded action, if any.

## Execution Result — 2026-09-06

### Run validity

- `artifacts_v1/` is an invalid first run preserved without modification. The script compared
  extensionless official split IDs with `.h5` archive basenames and therefore falsely reported all
  split members missing.
- The normalization bug was fixed to compare `Path(value).stem` and rerun once into immutable
  `artifacts_v1_rerun1/`.
- Valid result source: [`artifacts_v1_rerun1/result.json`](artifacts_v1_rerun1/result.json)

### Observed facts

- `README.txt` and `splits.zip` match their official MD5 checksums.
- The actual split artifact contains `train_split1.txt` with 111 unique recording IDs and
  `test_split1.txt` with 37. There are no within-split duplicates or cross-split overlap.
- `data.zip` contains 149 HDF5 members. All 148 split IDs map to members after the documented
  extension normalization.
- The one unassigned member is `2025-01-10-16-17-40.h5`, which the official issue table marks as
  missing the hand camera.
- Nine other issue-listed recordings remain in official splits: six train and three test. They
  include partial hand-camera, invalid-last-action force/torque, missing-last-action pose,
  no-empty-action and broken-gripper conditions.
- Pinned `REASSEMBLE/io.py` exposes high-level `start`, `end`, `success` and `text`, and the official
  README/source expose RGB, timestamps, force/torque, pose, gripper and joint-state paths.
- Exact segment-level matched success/failure counts are stored inside HDF5 payloads and are not
  available in the record, split files or ZIP central directory.
- Five HTTP range requests transferred 17,536 bytes, approximately `2.98e-7` of the full ZIP, and
  were sufficient to list every member and derive individual compressed-member byte ranges.
- The HDF5 members total about 55 GiB compressed and 246 GiB uncompressed. Full extraction exceeds
  the 168 GiB free filesystem observed at execution time.

### Decision

`REFINE_SUBSET`

The public route, split mapping and join schema are supported, while the exact matched denominator
requires HDF5 reads. Full download/extraction is neither necessary nor safe on the current
filesystem. A v2 protocol must preselect a small train/test and sensor-issue subset without using
outcome labels, retrieve only those ZIP members, and inspect them in a new project-specific Docker
environment.
