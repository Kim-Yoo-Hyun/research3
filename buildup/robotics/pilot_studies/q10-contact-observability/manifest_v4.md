# Q10 Contact-Outcome Observability — Larger Denominator Study v4

Created: 2026-09-06

## Status

`executed`, `PASS_DENOMINATOR`

## Feasibility Question

Does a label-blind, fixed-hash 20-recording public subset contain enough matched contact-action
successes and failures across the official train/test split to run strongest simple baselines
without outcome-conditioned sampling?

This repeats Stage 6 after v3 `MIXED_NEEDS_DENOMINATOR`. It measures denominator adequacy only; it
does not train a classifier, change Q10's admission status or start the three gates.

## Frozen Selection

Canonical selection: [`selection_v4.json`](selection_v4.json), SHA-256
`c9528a26bb08f8baea0f299a42507377672fc670c146891979aa1230fe5beb35`.

- Preserve the four v2 recordings as anchors: 3 train and 1 test.
- Exclude those anchors and all ten recording IDs in the official issue table from the new pool.
- Within each official split, sort by
  `SHA256("q10-v4-20260906:" + recording_id)`, with recording ID as tie-breaker.
- Take the first 12 train and first 4 test recordings. No HDF5 action or outcome label was read in
  selection.
- Final denominator: 15 train and 5 test recordings. New transfer: 16 files,
  6,164,041,523 compressed bytes and 27,486,794,802 extracted bytes.

Action coverage cannot be used for label-blind file selection because action labels live inside the
HDF5 payload. It is a measured v4 outcome, not a post-hoc selection criterion. No file may be added,
removed or replaced after labels are observed.

## Storage And Execution Boundary

- Free space before specification: 175,884,099,584 bytes. Abort before download if free space is
  below 100 GiB; do not extract the full 246 GiB archive.
- Existing v2 HDF5 files are mounted read-only and not copied or downloaded again.
- New cache: `/home/yoohyun/research3/datasets/q10_reassemble/v4/`.
- New immutable output:
  `/home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v4/`.
- HDF5 parsing uses new image `research3-q10-denominator:v4` and container
  `research3-q10-denominator-v4`, without GPU.
- Base and pinned `numpy==2.1.3`, `h5py==3.12.1` match v2. No existing image, Isaac asset,
  `PaperReview` file or hardware is used or modified.

## Target Rows And Metrics

- Apply the v2 official exclusion to the final action of `2025-01-11-15-35-08`.
- A matched row has at least one external-RGB, measured-force and pose timestamp inside its segment.
- Target rows are matched `pick`, `insert`, `remove` or `place` segments; exclude `No action.` from
  the scientific denominator.
- Report total/success/failure by official split and action family, object counts, exact action texts
  with both outcomes, exact texts shared across splits and action families with failures in both
  splits.

## Frozen Decision Rules

- `PASS_DENOMINATOR`: all 20 files open with required schema; at least 300 target rows, 30 failures,
  20 train failures and 8 test failures; at least three action families each have at least three
  successes and three failures; at least two families each have at least two failures in both
  splits.
- `REFINE_ACTIONS`: schema works and there are at least 300 target rows, 20 failures, 5 failures in
  each split, and at least two action families with at least three successes/failures. Restrict any
  next baseline to the qualifying pre-reported families.
- `EXPAND_FIXED`: access/schema works but neither denominator rule passes. Do not select failures;
  only a separately specified next batch in the same hash order is allowed.
- `REJECT_ROUTE`: any selected file cannot open or required RGB/F/T/proprioception/segment schema is
  absent.

Whatever the outcome, do not run learned models or add manual annotations in v4.

## Verification Commands

```bash
python3 fetch_members.py --selection selection_v4.json \
  --archive-members artifacts_v1_rerun1/archive_members.tsv \
  --output-dir ../../../../datasets/q10_reassemble/v4

docker build --pull --no-cache -t research3-q10-denominator:v4 -f Dockerfile_v4 .

docker run --rm --name research3-q10-denominator-v4 \
  -v /home/yoohyun/research3/datasets/q10_reassemble/v2:/input-v2:ro \
  -v /home/yoohyun/research3/datasets/q10_reassemble/v4:/input-v4:ro \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability:/workspace:ro \
  -v /home/yoohyun/research3/buildup/robotics/pilot_studies/q10-contact-observability/artifacts_v4:/output:rw \
  research3-q10-denominator:v4 --input-dir /input-v2 --input-dir /input-v4 \
  --selection /workspace/selection_v4.json --output-dir /output
```

The image digest, exits, checksums and decision are appended after execution.

## Execution Result — 2026-09-06 KST

- **Decision:** `PASS_DENOMINATOR`
- Selective download completed for 16/16 new files: 6,164,041,523 compressed bytes and
  27,486,794,802 extracted bytes. Central metadata, CRC32, exact extracted size and streaming
  SHA-256 checks succeeded; no `.part` file remained.
- The new Docker inspector opened all 20/20 frozen recordings with required schema. Of 570 total
  segments, 569 were matched after the one pre-specified official F/T exclusion. Removing 45
  `No action.` rows leaves 524 target action segments: 473 successes and 51 failures.
- Train has 400 target rows with 40 failures; test has 124 target rows with 11 failures.
- Pick has 153 rows / 10 failures, insert 152 / 29, remove 108 / 11, and place 111 / 1. Pick,
  insert and remove each meet the combined-class threshold and each has at least two failures in
  both train and test. Place does not qualify for the next baseline.
- All 68 exact action texts occur in both train and test; 28 have both outcomes in the combined
  subset. This supports file-split evaluation and action/object-stratified diagnosis, but does not
  by itself establish object-disjoint generalization.

The result passes the pre-fixed denominator rule exactly as written. The next feasibility study may
compare action-conditioned priors and deterministic terminal-state/F/T rules on only pick, insert
and remove. It must keep the official file split, fit/tune on train only, report macro balanced
accuracy and calibration, and preserve place as an explicitly unsupported action rather than
silently merging or resampling it. No learned model or manual annotation was run in v4.

## Execution Provenance

- download, Docker-build and denominator exit codes: `0`, `0`, `0`
- logs: `logs/20260906_q10_subset_v4.log`, `logs/20260906_q10_docker_v4.log`,
  `logs/20260906_q10_denominator_v4.log`
- image ID/digest:
  `sha256:38b94b1790ad2411be707a699f822416eb031884bf8787e92427cb013a8a83a1`
- input/download manifest SHA-256: `selection_v4.json`
  `c9528a26bb08f8baea0f299a42507377672fc670c146891979aa1230fe5beb35`,
  `download_manifest.json`
  `7dadf6a830c2de36e8f40a34ac21c1657f6d6a29e7e7d19a2d8ebd705d41d146`.
- source SHA-256: `make_selection_v4.py`
  `dacf26297d583c729ca96df739fc1a897b9cc1ae2de43a3f4e96a3f255af0045`,
  `inspect_denominator.py`
  `20bc8f7f1621f7bef7455800ad480c689db6dee3d22deee61a77b6f565eb88ca`,
  `Dockerfile_v4`
  `a3861d07eeaa0e990df629574a50e95135d35663ab1626cdf4e49398facc701d`.
- output SHA-256: `action_counts.tsv`
  `3d7c059565d0f0a4233947002b19526666b2d610ce4f68ab83768a2727c5b8e4`,
  `files.json`
  `7c38f8eb9c92caf14634e37852819aa60e23c6e80c2b43ace0277a5fb3c03ff7`,
  `segments.tsv`
  `af70e84261c254b295d56c7e53b0fcfb966f450703a958ecd1d5a7d4ee3fc4dc`,
  `summary.json`
  `42eb3723bbe1a2a5ad4c09876745c2604a5c65f2fe59533edd65988c537a078a`.

An independent artifact-only count reproduced 570 total, 569 matched, 524 target, 473 success and
51 failure rows. Available space after execution was 152,297,947,136 bytes. The final GPU snapshot
showed 4,090/32,607 MiB and 4% utilization from activity outside this CPU-only study; v4 did not
request or mount a GPU.
