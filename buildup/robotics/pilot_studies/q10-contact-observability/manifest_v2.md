# Q10 Contact-Outcome Observability — Bounded HDF5 Schema Study v2

Created: 2026-09-06

## Status

`executed`, `PASS_SCHEMA`

This Stage 6 study follows the v1 `REFINE_SUBSET` decision. It tests row-level join and issue
handling on four files. It does not estimate full-dataset performance or choose examples using
outcome labels.

## Feasibility Question

Can a preselected public four-file subset be retrieved independently from `data.zip` and parsed into
a reproducible segment table that joins outcome, RGB availability, force/torque, proprioception and
timestamps while respecting official sensor-issue exclusions?

## Frozen Selection

Canonical selection: [`subset_v2.json`](subset_v2.json)

Selection was made before any HDF5 outcome label was read:

1. smallest compressed issue-free test member: `2025-01-11-14-43-37.h5`;
2. smallest compressed issue-free train member: `2025-01-13-17-51-11.h5`;
3. smallest compressed train member marked `force/torque not valid for last action`:
   `2025-01-11-15-35-08.h5`;
4. smallest compressed train member marked `hand camera missing at beginning`:
   `2025-01-10-15-28-50.h5`.

Total expected transfer is 542,354,675 compressed bytes; total extracted size is 2,361,432,253
bytes. No adaptive or label-conditioned file addition is allowed in v2.

## Frozen Dataset And Source

- All dataset/source identifiers, checksums and URLs are inherited from `manifest_v1.md`.
- ZIP member sizes, offsets and CRC32 values come from the immutable valid v1
  `archive_members.tsv`.
- The official issue descriptions are treated as evaluator-only exclusion metadata, not learned
  input features.

## New Docker Boundary

- base index digest: `python:3.11-slim-bookworm@sha256:528257d48c1da0dcecc2e725d1ae34498d60c965f1241e39cd6a85a8859bdf84`
- linux/amd64 manifest digest:
  `sha256:b1add8a6f2aca6bcfcf0b9c9b522352f7ce0d62a3d556a2f2f32511aa0cca250`
- Python reported by the image registry: `3.11.16`
- dependencies: `numpy==2.1.3`, `h5py==3.12.1`
- project image tag: `research3-q10-schema:v2`
- project container name: `research3-q10-schema-v2`
- build must use `--pull --no-cache`; no pre-existing image, container, volume, Isaac asset or
  external repository Dockerfile is used.
- GPU is not used.

## Input And Output Boundary

- Extracted public subset: `/home/yoohyun/research3/datasets/q10_reassemble/v2/`
- HDF5 inputs are mounted read-only at `/input`.
- Script/config source is mounted read-only at `/workspace`.
- Generated outputs:
  `/home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v2/`
  mounted read-write at `/output`.
- Existing v1 inputs/results are never overwritten.

## Required Inspection

For every selected file, record without loading encoded media payloads:

1. top-level group/dataset names, shapes and dtypes;
2. available RGB streams and their timestamp arrays;
3. force/torque, pose, gripper and joint-state arrays and timestamps;
4. every high-level segment's start, end, Boolean success and action text;
5. per-segment sample counts for each candidate signal;
6. official-issue exclusion, including the final action of the marked force/torque file;
7. success/failure and action-text counts for this subset only.

## Metrics

- selected files downloaded / 4, CRC-valid / 4 and openable / 4;
- required schema fields present per file;
- high-level segment count and success/failure count per file/split/action text;
- segment count with at least one sample from external RGB, force/torque and proprioception;
- segment count excluded by official issue metadata;
- matched usable segment count in this four-file subset;
- raw transfer bytes, extracted bytes and peak output footprint.

## Frozen Decision Rules

- `PASS_SCHEMA`: all four files verify/open, both clean files contain joinable required modalities
  and segments, official issue exclusions can be applied deterministically, and at least one success
  and one failure remain in the matched subset.
- `REFINE_DENOMINATOR`: schema/join works but the outcome classes are degenerate or too sparse in
  this label-blind subset. A later denominator protocol may use a fixed random or complete-file
  expansion, never cherry-pick individual labels.
- `REFINE_TARGET`: only a stable subset of modalities or action types is joinable; narrow Q10 before
  any probe.
- `REJECT_ROUTE`: selected files cannot be independently retrieved/opened, or outcome and required
  signals cannot be joined even in the clean files.

Regardless of outcome, no classifier, visual encoder, manual annotation or learned method is run in
v2. Any ambiguous label review requires a separately fixed small manual-annotation protocol.

## Verification Commands

```bash
python3 fetch_members.py --selection subset_v2.json --archive-members artifacts_v1_rerun1/archive_members.tsv --output-dir ../../../../datasets/q10_reassemble/v2

docker build --pull --no-cache -t research3-q10-schema:v2 -f Dockerfile .

docker run --rm --name research3-q10-schema-v2 \
  -v /home/yoohyun/research3/datasets/q10_reassemble/v2:/input:ro \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability:/workspace:ro \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v2:/output:rw \
  research3-q10-schema:v2 --input-dir /input --selection /workspace/subset_v2.json --output-dir /output
```

Commands are run from the pilot-study directory where relative paths are used. Actual image digest,
command exit status and output checksums must be appended after execution.

## Execution Result — 2026-09-06 KST

- **Decision:** `PASS_SCHEMA`
- Selective transfer completed for 4/4 members: 542,354,675 compressed bytes and
  2,361,432,253 extracted bytes. The fetcher validated each ZIP central-directory record, CRC32,
  extracted size and SHA-256; an independent post-download SHA-256 pass also succeeded.
- All 4/4 HDF5 files opened. Both clean files contained every pre-specified required field; all four
  exposed `timestamps/hama1`, `timestamps/measured_force`, `timestamps/pose` and high-level
  `segments_info`.
- There were 45 high-level segments. The pre-specified last segment of
  `2025-01-11-15-35-08.h5` was excluded because the official README marks its force/torque invalid.
  The remaining 44 segments all had at least one external-RGB, force/torque and proprioception
  sample in their timestamp windows.
- The matched subset contains 40 successful and 4 failed segments. Each selected recording
  contributes exactly one matched failure; one failure is in `test_split1.txt` and three are in
  `train_split1.txt`.
- The four failed action labels are `Pick square peg 3.`, `Remove bolt 4.`,
  `Insert small gear.` and `Insert D-SUB.` This is a subset observation, not a population estimate.
- The hand-camera issue file remained joinable because external RGB was the required visual stream;
  v2 makes no claim about hand-camera completeness.

The result supports row-level public-data access, required-signal alignment and bounded resource
fit for Q10-A/Q10-F. It does not establish label construct validity, RGB-only ambiguity, a fair
denominator for classifier comparison or cross-domain generality. No classifier, visual encoder,
manual annotation or GPU was used. Q10 therefore remains a feasibility study and is not admitted as
an active research project.

## Execution Provenance

- download log: `logs/20260906_214457_q10_subset_v2.log`
- Docker build log and exit: `logs/20260906_214457_q10_docker_v2.log`, exit `0`
- schema inspection log and exit: `logs/20260906_q10_inspect_v2.log`, exit `0`
- built image ID/digest:
  `sha256:fd9d231c80b85653c7270165384e3691cdbd8244f66af0aaabfa58e96eb8ea0b`
- `download_manifest.json` SHA-256:
  `e463303f0e4c400a1c03a38f12828767b336d24240d28860b2b1a7bf031fd044`
- `artifacts_v2/files.json` SHA-256:
  `e4fb1ef7a7160f7d7f6fd06e2657684a0ef52befb9f63bea20a60bffd0f96db5`
- `artifacts_v2/segments.tsv` SHA-256:
  `568c27718e3d3c277f2af117606c572256fc86fd844c2f3f2914ac2d0faa0951`
- `artifacts_v2/summary.json` SHA-256:
  `5db4bcf366a0412ebf5ef750ddf70905646afd48ed4a634249a12fa1d60c24c7`
- source/config SHA-256 values: `Dockerfile`
  `a041628e09f725a1ac95fadfe6aed392465f5d0afe7f4fa4218dfcff7712b01a`,
  `requirements_v2.txt`
  `5a545dcb9f0a7f4379327183b03c4282f398c5b5cde5c06c707e9a696573e5a7`,
  `fetch_members.py`
  `92dad320c49c8138c01706e3b7b8eaabee356c4a249ab422bae53fc5c963220c`,
  `inspect_h5.py`
  `87a2d1f09489950528c25248d5527a663ccfcdb36e2bdc96554e372b09624b6d`,
  `subset_v2.json`
  `2a9f674fc69d75ff2b150bd3465ece604b574a4b08ba84b021f2d2ccce65b700`.

The first independent verification command used a wrong local JSON key (`files` rather than the
fetcher's actual `members`) and stopped before hashing. It did not affect the already downloaded
files or the Docker run. The corrected verification used `members` and completed successfully;
no artifact was edited or replaced.
