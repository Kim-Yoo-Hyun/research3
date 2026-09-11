# Q10 Contact-Outcome Observability — Small RGB Audit v3

Created: 2026-09-06

## Status

`executed`, `MIXED_NEEDS_DENOMINATOR`

## Feasibility Question

In the four-file v2 subset, can a single reviewer distinguish every observed failure from a
pre-fixed successful control using only five external-RGB frames sampled over the action segment?

This is a qualitative visibility audit for Q10-C, not an accuracy estimate, classifier benchmark or
claim that RGB is sufficient. It uses public data only. The user explicitly allowed small manual
annotation if needed.

## Frozen Cases And Controls

Canonical machine-readable protocol: [`audit_v3.json`](audit_v3.json). All four matched v2 failures
are included. Before any images are decoded or viewed, controls are fixed as follows:

| pair | failure | success control | rule |
| --- | --- | --- | --- |
| pair01 | `2025-01-11-14-43-37:1`, pick square peg 3 | `2025-01-10-15-28-50:13`, pick square peg 4 | same verb and object family |
| pair02 | `2025-01-13-17-51-11:3`, remove bolt 4 | `2025-01-13-17-51-11:1`, remove D-SUB | only successful remove in subset |
| pair03 | `2025-01-11-15-35-08:14`, insert small gear | `2025-01-10-15-28-50:18`, insert small gear | exact action text |
| pair04 | `2025-01-10-15-28-50:4`, insert D-SUB | `2025-01-11-15-35-08:6`, insert D-SUB | exact action text |

For each segment, select the nearest external-RGB frame to fractions
`[0.15, 0.40, 0.65, 0.85, 0.97]` of its labeled interval. A/B order is deterministically concealed
with seed `q10-v3-20260906`. Images display only pair ID, A/B and action family. No force,
proprioception, success label, exact object label or issue metadata is shown.

## Annotation Protocol

One reviewer records for each comparison:

- `A_more_successful`, `B_more_successful`, `indistinguishable`, or `unjudgeable`;
- confidence 1--3;
- the visible cue, if any, and a short note.

The reviewer must fill `annotation.tsv` before opening `ground_truth_key.tsv`. This single-reviewer
audit is permitted only as qualitative feasibility evidence. It cannot provide inter-rater
reliability or a denominator-level performance estimate.

## Frozen Decision Rules

Count a pair as a confident correct distinction only when the reviewer selects the successful side
and confidence is at least 2.

- `RGB_VISIBLY_SEPARATES_SMALL_AUDIT`: at least 3/4 confident correct and at most one
  `unjudgeable`. This weakens Q10-C and requires a later, broader RGB baseline before Q10 can proceed.
- `RGB_AMBIGUOUS_SMALL_AUDIT`: at most 1/4 confident correct and at least two responses are
  `indistinguishable` or `unjudgeable`. This supports, but does not prove, Q10-C.
- `MIXED_NEEDS_DENOMINATOR`: every other outcome. A larger pre-fixed public subset is required;
  no learned method follows directly.

No threshold may be changed after viewing. Pair02 is deliberately imperfectly object-matched and
must be reported as a limitation rather than replaced.

## Docker And Output Boundary

- New image/tag: `research3-q10-rgb-audit:v3`; container: `research3-q10-rgb-audit-v3`.
- Base: the exact linux/amd64 Python digest used in v2.
- Dependencies: `requirements_v3.txt`; GPU is not used.
- Input HDF5 and v2 artifacts are mounted read-only.
- Output is a new `artifacts_v3/` directory and is never overwritten.
- Existing Docker/Isaac assets and `PaperReview` remain untouched.

## Verification Commands

```bash
docker build --pull --no-cache -t research3-q10-rgb-audit:v3 -f Dockerfile_v3 .

docker run --rm --name research3-q10-rgb-audit-v3 \
  -v /home/yoohyun/research3/datasets/q10_reassemble/v2:/input:ro \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability:/workspace:ro \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v3:/output:rw \
  research3-q10-rgb-audit:v3 --input-dir /input \
  --segments /workspace/artifacts_v2/segments.tsv --protocol /workspace/audit_v3.json \
  --output-dir /output
```

Actual image digest, command exits, annotation, decision and checksums are appended after execution.

## Execution Result — 2026-09-06 KST

- **Decision:** `MIXED_NEEDS_DENOMINATOR`
- Extraction opened the four public v2 HDF5 files in the new container and produced all 4/4
  comparison images (40 frames total). Docker build and extraction both exited `0`.
- The reviewer inspected only the four comparison PNGs and filled `annotation.tsv` before
  `ground_truth_key.tsv` was opened.
- Judgments were `A_more_successful`, `B_more_successful`, `A_more_successful`, and
  `indistinguishable`, all at confidence 2. After key reveal, the three directional judgments were
  all incorrect; the fourth pair was marked indistinguishable.
- Therefore confident-correct count is 0/4 and indistinguishable/unjudgeable count is 1/4. This
  matches neither extreme rule and deterministically yields `MIXED_NEEDS_DENOMINATOR`.

The visible retreat/contact-duration cues were not reliable in this tiny audit and in fact pointed
in the wrong direction for all three directional judgments. This is evidence that sparse external
RGB can mislead a simple human motion heuristic, but it is not a quantitative estimate of RGB-only
observability: the subset contains only four failures, one reviewer, sparse frames rather than
video, and pair02 has a different object between failure/control. Q10-C remains ambiguous. The next
study must expand a pre-fixed public denominator and compare full-video/RGB summaries before any
learned multimodal method. No additional annotation is justified until that denominator is fixed.

## Execution Provenance

- image ID/digest:
  `sha256:f47f62971adda6a431ebca80e6c1ba19a0bf36a7f335bfcf06c0006a7f6f5298`
- Docker build log and exit: `logs/20260906_q10_docker_v3.log`, exit `0`
- extraction log and exit: `logs/20260906_q10_rgb_v3.log`, exit `0`
- source/config SHA-256: `Dockerfile_v3`
  `04e47535e5169bc37f4f9c2b83f24b034cb3eac70026fb7402d1d70c49786f49`,
  `requirements_v3.txt`
  `34b3d23a46d735e7101c5d510d1ddb75fa0d850c56520837481bfd3558301c51`,
  `extract_visual_audit.py`
  `d13a57f70ce3e4dfc7b09b6853f0ad32e3f050aebd9f62edf4c134e7d7614e8a`,
  `audit_v3.json`
  `f696b958f47a9f16e8fdf38f3f2252d91d350e7406094c5dc532233d029f92e6`.
- annotation/key/metadata SHA-256: `annotation.tsv`
  `f93a4523b8ae5958a0b927b1fe64d2095649b8d35a4e0f8c670d1097b59b8884`,
  `ground_truth_key.tsv`
  `fe5503603de2529e639fa992b8ed1369ba2bb7dee03e18ebe8500f084652b36d`,
  `frame_metadata.json`
  `2df4f86a2c627542306a273157e6700c409805b86d84ab32e7315079ba1aa846`.
- comparison PNG SHA-256: pair01
  `2ae39e988e65e146802fdf59b621fddde0cc6969de3fade4a27f0e58329630a0`,
  pair02 `b3be14a8c95307e1782a0ed6085b2a74c4001b3f98553ebc26d640770ae04041`,
  pair03 `77f93b679279dc3d252168ec170eea3fc1ccf9e23f87839418f82445a4e06dcc`,
  pair04 `573052adcecf1fa2bb23e3f586d3f486189d3e53631000a73f99002301181742`.

The blank annotation file was created by the Docker process as root. An initial ownership change to
UID/GID 1000 did not make it writable because the workspace user is 1001. The project-specific v3
image then changed only that exact file to UID/GID 1001, after which `apply_patch` recorded the
review. No image, key, metadata or input artifact was modified.
