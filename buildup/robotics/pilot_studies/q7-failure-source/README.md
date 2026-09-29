# Q7 Failure-Source Observations

Updated: 2026-09-16

## Purpose and status

`completed`; exploratory first observation for [Q7](../../questions/failure-source-generalization.md).
Compare same-start grasp cases, source-supplied success/failure and an end=start construction.
Separate global image change, task-state evidence and missing temporal evidence. This is not a
Guardian reproduction, independent human annotation or a detector transfer benchmark.

First visual/CPU observation and the 30-prediction general-VLM comparison are completed.
The latter failed the requested output format. The END repetition control is also completed;
raw-verdict diagnostics and limitations are below. The subsequent
[investment comparison](../../related_work/policy-geometry.md#q7-q14-reassessment-2026-09-16)
selected Q14's next observation and deferred this Q7 route. No additional Q7 run is selected.

The question record owns the rationale; this folder owns execution, case annotations and results.
The selected source rows are exploratory dev cases. The first comparison is model-free; the
follow-up uses one pretrained VLM in Docker. No robot motion or training is involved.

## Input and scope

- Dataset: `paulpacaud/ur5fail_test_dataset`, revision `fedfcb3346b92f6a2bfeb14dc254635c9a5013f1`.
- `records.tar.gz`: 54,848,824 bytes; upstream LFS SHA256
  `ef56f7b0c4e196a758a8571ee24acafba5f27043102b55e25d32f423d79f45e1`.
- Metadata: `external/q7-sources/ur5_metadata.jsonl`; identity in
  [source record](../../related_work/comparison_sources.json), `q7_q14_review_20260915`.
- Four failure/success row pairs (1-based): 43/41, 72/73, 92/91, 126/127.
  Same instruction, subtask and three start image paths; neither independent rollouts nor matched
  duration/severity is established. Controls: rows 76, 121, 122, with repeated image paths.
- Per pair use source failure, source success and the same start image as a prospective end image.
  Assign constructed-negative interpretation only if the initial task is visibly unmet.
- Prepare images, inspect all three views, record observations **before computing numeric scores**,
  then run equality and global mean absolute RGB difference normalized by 255.
  No alignment, crop, image-resizing or label-dependent preprocessing enters the score.
  Each camera is compared within its own pair; camera index is not a universal physical viewpoint.
- Do not choose a threshold/accuracy claim using these cases. Record per-camera continuous scores
  and within-group order. A second implementation will check the metric's core calculation.
- Static evidence can support/contradict a source label or remain insufficient. It cannot prove
  secure grasp dynamics or autonomous failure provenance. Never change original labels.

## Environment and artifacts

New image `research3-q7-failure-source:v1`, public pinned Python base, NumPy and Pillow only.
All first-observation image decode/render/numerical evaluation runs inside this workspace's new CPU Docker image.
Runs use 2 CPUs, 2 GiB RAM, no network, read-only source/input and explicit writable output paths.
No random sampling; seed not applicable. No existing simulator/image is a research dependency.

Input archive is under ignored `datasets/q7-ur5/`; images and row-level scores under ignored
`runs/q7/`. Tracked files retain code, compact result, annotations and recoverable identities.
Commands run from `/home/yoohyun/research3`. New executions must use fresh output/container names.

## Commands and jobs

Download and build are background tmux jobs. Each writes a timestamped log and exit file under
`logs/`. Job identifiers and exact commands are recorded below as launched; completion requires
input SHA256 and expected output verification. The image archive remains unmodified.

Launched download/build: `20260915_141525`; status `launched`.

```bash
wget -c --timeout=30 --tries=3 -O datasets/q7-ur5/records.tar.gz https://huggingface.co/datasets/paulpacaud/ur5fail_test_dataset/resolve/fedfcb3346b92f6a2bfeb14dc254635c9a5013f1/records.tar.gz
docker build --pull --no-cache -t research3-q7-failure-source:v1 buildup/robotics/pilot_studies/q7-failure-source
```

Sessions: `research3_q7_download_20260915_141525`, `research3_q7_build_20260915_141525`.
Log/exit prefixes: `logs/20260915_141525_q7_download`, `logs/20260915_141525_q7_build`.
Expected input: archive bytes/hash above. Expected image: `research3-q7-failure-source:v1`.

Build setup correction: the initial lock generator assumed a single Pillow Linux wheel; PyPI
provides two compatible glibc variants. It stopped before writing the lock, so the first build
could not find `requirements.lock`. Both wheel hashes are now allowed for the same pinned version.
No data selection or measurement changed. The corrected build uses the same new v1 tag.

Corrected build launched: `20260915_141600`, session `research3_q7_build_20260915_141600`, log/exit prefix `logs/20260915_141600_q7_build`. Same build command above.

Runtime `prepare`: `research3-q7-prepare-20260915_141759`; log `logs/20260915_141759_q7_prepare.log`.

```bash
timeout 300s docker run --name research3-q7-prepare-20260915_141759 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 64 --user 1001:1001 --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/datasets/q7-ur5\,dst=/input\,readonly --mount type=bind\,src=/home/yoohyun/research3/external/q7-sources\,dst=/metadata\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7\,dst=/output research3-q7-failure-source:v1 /study/observe.py prepare --output /output/prepared 
```

Runtime `research3-q7-prepare-20260915_141759` exit `0`; status `completed; needs interpretation`.

Runtime `score`: `research3-q7-score-20260915_142014`; log `logs/20260915_142014_q7_score.log`.

```bash
timeout 300s docker run --name research3-q7-score-20260915_142014 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 64 --user 1001:1001 --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/datasets/q7-ur5\,dst=/input\,readonly --mount type=bind\,src=/home/yoohyun/research3/external/q7-sources\,dst=/metadata\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7\,dst=/output research3-q7-failure-source:v1 /study/observe.py score --prepared /output/prepared --output /output/scored 
```

Runtime `research3-q7-score-20260915_142014` exit `0`; status `completed; needs interpretation`.

## Post-score revision

After the pre-score visual notes and the first per-camera scores, some failure/success orderings
changed by camera. Add a **post hoc exploratory** mean/median across the same three views as a
cheap alternative explanation. Report both aggregations, not only the favorable one. This does
not add cases, change labels or turn the dev cases into held-out evidence. It tests whether the
single-camera reversals already disappear under a simpler multi-view rule before motivating a
state-conditioned verifier. No learned detector is evaluated.

Runtime `verify`: `research3-q7-verify-20260915_142056`; log `logs/20260915_142056_q7_verify.log`.

```bash
timeout 300s docker run --name research3-q7-verify-20260915_142056 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 64 --user 1001:1001 --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/datasets/q7-ur5\,dst=/input\,readonly --mount type=bind\,src=/home/yoohyun/research3/external/q7-sources\,dst=/metadata\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7\,dst=/output research3-q7-failure-source:v1 /study/verify.py --prepared /output/prepared --scored /output/scored --output /output/verification.json 
```

Runtime `research3-q7-verify-20260915_142056` exit `0`; status `completed; needs interpretation`.

Runtime `aggregate`: `research3-q7-aggregate-20260915_142056`; log `logs/20260915_142056_q7_aggregate.log`.

```bash
timeout 300s docker run --name research3-q7-aggregate-20260915_142056 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 64 --user 1001:1001 --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/datasets/q7-ur5\,dst=/input\,readonly --mount type=bind\,src=/home/yoohyun/research3/external/q7-sources\,dst=/metadata\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7\,dst=/output research3-q7-failure-source:v1 /study/aggregate.py 
```

Runtime `research3-q7-aggregate-20260915_142056` exit `0`; status `completed; needs interpretation`.

## Results 2026-09-15

**첫 관찰과 독립 계산 대조를 완료했다.** Download exit 0, corrected Docker build exit 0,
prepare/score/verify/aggregate도 모두 exit 0이다. 처음의 lock 준비 실패는 위에 보존했다.
입력 SHA256는 upstream LFS와 일치했다. 원본 11행에서 고유 256×256 이미지 45개를 읽었고,
constructed input 4개를 포함한 15개 입력 × 3 camera = 45 score rows를 계산했다.
Source label을 재작성하거나 사례를 제외하지 않았다.

[annotations.json](annotations.json)은 수치 실행 전에 작성한 agent의 시각 판독이다.
세 view에서 네 묶음의 초기 gripper는 비어 있어 constructed end=start를 **미달성 상태의
입력**으로 해석할 수 있었다. 이는 실제로 실행한 실패 trajectory가 아니다. Source failure의
종료에서는 hand가 이동했지만 fingers가 열린 상태였고, source success에서는 목표 물체를
감싸는 상태가 보였다. 접촉 상태는 source label과 일치하지만 grasp 안정성과 failure의
terminal 시점은 정지 영상으로 확인할 수 없다.

### Numeric observation

Metric은 native RGB에서 `sum(abs(start - end)) / (255 × number_of_RGB_elements)`다.
아래는 **failure score − success score**이며, 양수는 실패 쪽 영상 변화가 더 큼을 뜻한다.
Performance percentage나 accuracy가 아니다. 네 묶음과 세 camera는 독립 sample 12개가 아니다.

| group | view 0 | view 1 | view 2 | mean over views, post hoc | median over views, post hoc |
| --- | ---: | ---: | ---: | ---: | ---: |
| lemon | −0.005461 | −0.008654 | −0.019558 | −0.011225 | −0.015391 |
| drawer_ball | −0.015990 | −0.033499 | −0.020911 | −0.023467 | −0.015990 |
| sport_ball | +0.003619 | −0.008674 | −0.016903 | −0.007320 | −0.008674 |
| fruit | +0.002288 | +0.001961 | −0.002953 | +0.000432 | −0.001541 |

- Constructed inputs의 score는 모든 view에서 0이다. 이는 구성 방식의 결과이며 새로운 발견이 아니다.
- Source 실패·성공의 24개 view score는 모두 0보다 크다. 따라서 duplication 단서만으로
  source 실패까지 식별할 수는 없다. Learned detector가 이 단서를 쓴다는 증거는 아니다.
- 단일 view의 성공/실패 변화량 순서는 12개 비교 중 3개에서 예상 방향과 반대다. 그러나
  **three-view median은 네 묶음 모두 성공 쪽이 더 크다.** Mean에서는 fruit의 반대 순서가 남는다.
  사후 median 선택의 4/4를 generalization 또는 accuracy로 쓰지 않는다.
- 세 repeated-image control의 score도 전부 0이지만 source label은 success 2 / failure 1이다.
  영상에서는 이미 물체를 감싼 상태와 열린 gripper 상태가 달라 보인다. Input equality가
  같다는 이유만으로 label 오류라거나 task 상태가 같다고 결론 내릴 수 없다.

### Interpretation and next attempt

사실: 단일 view의 전역 변화량은 task label과 항상 같은 순서를 주지 않았고, 단순 multi-view
median이 네 paired 사례의 순서를 설명했다. 따라서 이 결과로 복잡한 state verifier의
필요성을 주장하지 않는다. Equal-image controls는 변화량만을 입력으로 쓰는 규칙의 적용
한계를 보여 주지만, 목표 조건부 VLM이 이미 해결할 수 있는 쉬운 문제일 가능성이 있다.

에이전트 추론: 다음에는 **작은 general VLM 하나를 그대로 사용해 instruction + 종료 상태만
보는 조건과 instruction + 시작/종료를 보는 조건을 비교**할 가치가 있다. 같은 15개 dev
입력·세 view·동일 decoding 설정으로 보고 three-view median을 단순 대안으로 유지한다.
Metadata의 `failure_reason`, reward, mode, CoT는 model 입력에서 제외한다. 두 조건의 출력과
case evidence를 비교하고, 모델/프롬프트를 반복 튜닝해 성공시키는 작업으로 만들지 않는다.

이를 Q7의 다음 bounded attempt로 선택한다. Small-model checkpoint pinning과 Docker 준비를
실제 소수 추론까지 묶는다. No training; first target at most 30 predictions, one modest model
that fits the available GPU. Model identity and actual resource use will be recorded when prepared.
VLM이 단순히 해결하면 그 baseline을 채택하고 더 복잡한 방법의 필요성을 낮춘다. 시각적으로
판독 불가능하면 information insufficiency를 기록한다. 미확정 provenance 때문에 current
observation을 natural-failure transfer 결과로 올리지 않으며, Q7 전체를 기각하지도 않는다.

### Verification and preservation

[verify.py](verify.py)는 NumPy를 import하지 않고 Pillow ImageChops histogram의 정수 합으로
45개 score와 row/view 연결을 재구성했다. 전부 일치했고 평균값의 최대 차이는
`1.39e-17`이다. 같은 image decoder를 쓰므로 source label이나 image decoding의 독립 검증은 아니다.

[결과·환경·source hash](outcome.json)에 실행 image digest, Python/NumPy/Pillow 버전, Git base,
미커밋 source 파일별 hash, compact metric과 output hash를 보존했다. Image immutable reference:
`research3-q7-failure-source@sha256:8879500c0f9da0f593ada4251ad592360c140defd1f01804fee8a29466c0d3c6`.
[selection.json](selection.json)이 원본 revision/입력 선택을, [requirements.lock](requirements.lock)이
dependency pin/hash를 소유한다.

Raw outputs와 원본 이미지는 `runs/q7/prepared/`, `runs/q7/scored/`에 있고 metric 검증은
`runs/q7/verification.json`이다. 진단 그림은 `runs/q7/prepared/{lemon,drawer_ball,sport_ball,fruit,controls}.png`;
그림 layout만 표시용이며 score는 원본 native pixel에서 계산했다. 원본 archive는
`datasets/q7-ur5/records.tar.gz`에 보존한다. 외부 backup/삭제 안전성 검증은 수행하지 않았다.

재실행: input/metadata를 pinned URL에서 복원·hash 확인하고 위 Dockerfile로 build한다.
`run.sh`의 절대 output mount를 새로운 빈 run directory로 지정한 뒤 `prepare`, `score`,
`verify`, `aggregate` 명령을 같은 순서로 실행한다. 현재 script 기본 출력은 첫 실행을
보호하기 위해 기존 경로가 있으면 실패한다. Annotation 원본은 새 판독을 뜻하지 않는다.

## General VLM Comparison

Status: `completed`; 30/30 task predictions and Docker output/input review completed.
Requested JSON compliance failed in all 30 outputs. This is a model-interface failure, not evidence
that the underlying research question is false. The first CPU results above remain unchanged.

### Model and pre-output design

Use [SmolVLM2-2.2B-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct), revision
`482adb537c021c86670beed01cd58990d01e72e4`. Its official card supports interleaved multi-image input.
This is a modest general baseline, not a strongest-model or Guardian replication claim.
Qwen2.5-VL-3B was considered but the smaller model better fits the currently shared GPU budget.

At preparation, the RTX 5090 had 21,735 / 32,607 MiB used and 100% utilization. Do not modify other
jobs. Use batch size 1, BF16, SDPA, at most 19% of device memory for the PyTorch allocator, 4 CPUs,
16 GiB container RAM and explicit GPU UUID. Recheck free memory before starting the dependent run;
if allocation is unavailable, retain the resource failure and use the same model in CPU Docker for
both conditions. A device change is recorded, not a reason to change examples or desired outcomes.

Pinned native images are 256×256. Set the same official processor to longest edge 384 and disable
image splitting for both conditions. Default 1536 splitting would substantially expand low-resolution
inputs and six-image token count. Record actual tensor shape and image/token counts. Use greedy
decoding, seed 0, `max_new_tokens=128`, KV cache enabled, one frozen prompt template.

- `end_only`: instruction/context + three END camera images.
- `start_end`: the same instruction/context and END images + three START images, matched view IDs.
- Ask whether the subtask is achieved in the END state. Allow `GOAL_MET`, `GOAL_NOT_MET`, `UNCERTAIN`
  plus one short visible-evidence sentence. Do not ask the model to infer terminal failure timing.
- Input builder uses only task text, subtask text and image pixels. Exclude source labels, group/row
  names, filenames, failure reason/mode and previous annotations from the prompt.
- Run all 15 dev cases under both conditions. Source labels are only evaluation references; the
  four constructions use the previous initial-state visual interpretation. Keep abstentions and
  malformed/truncated outputs in the denominator. No resampling of difficult examples.
- Report output changes, agreement with supplied/interpreted labels, original versus constructed
  strata, false positives/negatives and visible reasoning errors. These are descriptive counts on
  dependent dev cases, not held-out accuracy or natural-failure transfer.
- Keep image-change/three-view median as a separate score baseline; its within-pair ordering is
  not a binary classifier with a fitted threshold and cannot be directly called VLM accuracy.
- More input images also change token/attention cost. A difference is not a cost-matched temporal
  reasoning benefit. Report inference tokens, latency and peak allocated GPU memory.

Model cache: ignored `checkpoints/q7/smolvlm2-2.2b/`; output: ignored `runs/q7/vlm/`.
This owner records commands, model files and dependencies. All 30 raw model responses are preserved.

### Preparation jobs

Launched `20260915_184138`: download session `research3_q7_model_20260915_184138`, build session
`research3_q7_vlm_build_20260915_184138`; final build status `completed`, initial download
`failed` after the transport switch described below. Log/exit prefixes:
`logs/20260915_184138_q7_model`, `logs/20260915_184138_q7_vlm_build`. Working directory: repository root.

```bash
python3 buildup/robotics/pilot_studies/q7-failure-source/fetch_model.py
docker build --pull --no-cache -f buildup/robotics/pilot_studies/q7-failure-source/Dockerfile.vlm -t research3-q7-vlm:v1 buildup/robotics/pilot_studies/q7-failure-source
```

Expected model bytes and per-file upstream identities are in `model.json`; completion receipt:
`checkpoints/q7/smolvlm2-2.2b/download.json`. Expected image: `research3-q7-vlm:v1`.

Download transport revision: the two initial sequential checkpoint streams were slow. Stopped
only those workspace-owned wget processes, retaining their downloaded prefixes. Switched to eight
concurrent disjoint HTTP ranges, validating each Content-Range and the final upstream SHA256.
The file revision/content is unchanged. `ranges.json` tracks sparse-file completion; file size alone
must not be treated as completion. Only `download.json` after full hash verification is authoritative.
The interrupted initial downloader's failure is a transport event, not a model/evaluation failure.

Range download launched `20260915_184932`, session `research3_q7_ranges_20260915_184932`, log/exit prefix `logs/20260915_184932_q7_ranges`; command `python3 buildup/robotics/pilot_studies/q7-failure-source/fetch_ranges.py`.

VLM `check` launched: `research3-q7-vlm-check-20260915_185244`; log/exit prefix `logs/20260915_185244_q7_vlm_check`.

```bash
timeout 2400s docker run --name research3-q7-vlm-check-20260915_185244 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw\,size=512m --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/prepared\,dst=/prepared\,readonly --mount type=bind\,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b\,dst=/model\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7\,dst=/output research3-q7-vlm:v1 /study/check_inputs.py 
```

VLM `research3-q7-vlm-check-20260915_185244` exit `0`.

Build completed successfully. Resolved dependencies are preserved in `requirements.vlm.lock`;
`vlm_environment.json` records the executed image identity. The original recipe records direct
pins; for an exact rebuild use the resolved lock (CUDA packages from the PyTorch cu128 index)
or the recorded immutable image. The first CPU input check passed on all 15 cases: END pixel
 tensors are identical across conditions, with 243 versus 486 image tokens. It made zero task
predictions. A deprecated video-config location warning is harmless for the pinned image-only path;
the original model files were not modified.

Inference orchestration launched `20260915_185403`, session `research3_q7_infer_20260915_185403`; waiting for successful `logs/20260915_184932_q7_ranges.exit`, then `bash buildup/robotics/pilot_studies/q7-failure-source/run_vlm.sh infer`; final status `completed`, exit 0. Wrapper log/exit prefix `logs/20260915_185403_q7_infer_wait`.

Descriptive constant-label control: also retain agreement counts for always GOAL_MET and always
GOAL_NOT_MET on the same 15 reference labels. They diagnose the dev set's class balance; selecting
the majority using these labels is not training or a held-out baseline result.

VLM `infer` launched: `research3-q7-vlm-infer-20260915_190023`; log/exit prefix `logs/20260915_190023_q7_vlm_infer`.

```bash
timeout 2400s docker run --name research3-q7-vlm-infer-20260915_190023 --gpus device=GPU-90cacfcf-72fe-4b1c-1bd4-cffb389ff9ea --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw\,size=512m --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/prepared\,dst=/prepared\,readonly --mount type=bind\,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b\,dst=/model\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7\,dst=/output research3-q7-vlm:v1 /study/vlm.py --device cuda --output /output/vlm 
```

VLM `research3-q7-vlm-infer-20260915_190023` exit `0`.

VLM `review` launched: `research3-q7-vlm-review-20260915_190234`; log/exit prefix `logs/20260915_190234_q7_vlm_review`.

```bash
timeout 2400s docker run --name research3-q7-vlm-review-20260915_190234 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw\,size=512m --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/prepared\,dst=/prepared\,readonly --mount type=bind\,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b\,dst=/model\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7\,dst=/output research3-q7-vlm:v1 /study/review_vlm.py 
```

VLM `research3-q7-vlm-review-20260915_190234` exit `0`.

### VLM results 2026-09-15

**사실:** SmolVLM2-2.2B-Instruct로 같은 15개 dev 사례의 두 조건, 총 30개 추론을 한 번씩
완료했다. 고정한 JSON schema를 지킨 응답은 **0/30**이다. 모든 응답은 EOS로 정상 종료했으며
truncation은 없다. 29개는 판정 한 문장만, 1개는 UNCERTAIN과 짧은 이유를 출력했다.
실행 성공과 task-interface 성공을 구분한다. 요청한 evidence 문장이 대부분 없어 개별
오판을 object 인식·grasp 이해·task 해석 중 어느 원인으로 확정할 수 없다.

| 사전 정의한 JSON 평가 | END-only | START+END |
| --- | ---: | ---: |
| 전체 입력 | 15 | 15 |
| Valid JSON + schema | 0 | 0 |
| INVALID | 15 | 15 |
| Strict reference agreement, INVALID 포함 | 0/15 | 0/15 |
| Truncated output | 0 | 0 |

이는 모든 시각 판정이 틀렸다는 뜻이 아니다. 원문 확인 후 별도의 **사후 보조 분석**을 추가했다.
전체 응답이 `The verdict is ...` 형태임을 보고 anchored regex로 명시된 판정만 읽었다.
`review_vlm.py`에 규칙과 `post_hoc_diagnostic_only` 표시를 보존했다. JSON 평가를 수정하지
않았고 새 generation·prompt tuning·응답 선택·누락된 evidence의 생성은 없다.

| 원문 판정의 사후 진단 | END-only | START+END |
| --- | ---: | ---: |
| Reference agreement, 전체 15개 포함 | 2/15 | 6/15 |
| Source label과 일치 | 1/11 | 4/11 |
| Constructed reference와 일치 | 1/4 | 2/4 |
| UNCERTAIN | 12/15 | 5/15 |
| False positive / false negative | 0 / 1 | 1 / 3 |
| GOAL_MET / GOAL_NOT_MET | 0 / 3 | 2 / 8 |
| 명시적 이유 문장 있음 | 0/15 | 1/15 |

Source label은 source가 제공한 값이고 construction 4개는 기존 초기 영상 판독을 따른다.
Always GOAL_NOT_MET는 같은 reference에서 9/15, always GOAL_MET는 6/15다. 유보를 포함한
전체 일치 수의 비교이며 uncertainty calibration이나 selective risk 비교가 아니다.
START+END의 일치 수 증가를 강한 baseline 성능 또는 시간 추론 개선으로 쓰지 않는다.

아래는 원문 판정의 전 사례 대조다. `MET`, `NOT_MET`, `UNCERTAIN`은 각각 위 verdict의 약칭이다.

| case | reference | END-only | START+END |
| --- | --- | --- | --- |
| lemon source failure | NOT_MET | NOT_MET | NOT_MET |
| lemon source success | MET | NOT_MET | MET |
| lemon constructed | NOT_MET | NOT_MET | MET |
| drawer_ball source failure | NOT_MET | UNCERTAIN | NOT_MET |
| drawer_ball source success | MET | UNCERTAIN | UNCERTAIN |
| drawer_ball constructed | NOT_MET | UNCERTAIN | NOT_MET |
| sport_ball source failure | NOT_MET | UNCERTAIN | NOT_MET |
| sport_ball source success | MET | UNCERTAIN | NOT_MET |
| sport_ball constructed | NOT_MET | UNCERTAIN | NOT_MET |
| fruit source failure | NOT_MET | UNCERTAIN | UNCERTAIN |
| fruit source success | MET | UNCERTAIN | NOT_MET |
| fruit constructed | NOT_MET | UNCERTAIN | UNCERTAIN |
| control 76, tuna can | MET | UNCERTAIN | NOT_MET |
| control 121, hammer | NOT_MET | UNCERTAIN | UNCERTAIN |
| control 122, screwdriver | MET | UNCERTAIN | UNCERTAIN |

9/15개에서 판정이 바뀌었다. Reference 일치를 얻은 사례는 5개, 잃은 사례는 1개이며
나머지 3개는 UNCERTAIN에서 reference와 반대인 단정으로 바뀌었다. **이미 START=END인
7개 사례 중에도 4개가 바뀌었다:** lemon/drawer_ball/sport_ball construction과 control 76.
특히 lemon construction은 새로운 상태 정보 없이 NOT_MET에서 MET로 바뀌었다. 이 비교는
이미지 반복·token 수·phase 표기의 효과를 함께 포함하므로, 실제 과거 상태의 기여를 분리하지 못한다.
UNCERTAIN 출력 자체도 시각 증거가 객관적으로 부족하다는 증명은 아니다.

### Interpretation and next control

**에이전트 추론:** 이번 작은 모델은 신뢰할 task verifier로 채택할 근거가 부족하다. 그렇다고
새 structured verifier가 필요하거나 모든 general VLM이 실패한다고 결론 내리지 않는다.
형식 준수·기초 판정 능력·추가 관측의 효과가 섞여 있고, 이유 설명도 부족하다. 기존 three-view
median의 네 쌍 ordering은 단순 대안으로 남긴다. 이 score는 binary classifier가 아니다.

Q7의 다음 작은 질문은 **실제 START 이미지가 같은 END 이미지의 반복보다 추가적인 판정
정보를 제공하는가?**로 좁힌다. 다음 TODO는 이미 확보한 모델·입력·prompt를 그대로 이용해
`END+END` 대조를 추가하는 것이다. START 위치에 END의 세 view를 넣고 START/END 표기,
총 여섯 이미지·token 수·처리기·decoding을 START+END와 같게 둔다. 이는 물리적 trajectory가
아닌 입력 대조다. 모델에는 이 구성의 source label이나 역할을 알려주지 않는다.

- START와 END가 다른 source 8개에만 추가 추론한다. 나머지 7개는 기존 START+END와
  prompt 및 이미지 순서/hash가 같음을 확인한 뒤 기존 응답을 재사용한다. 최대 8개 새 prediction.
- JSON compliance는 계속 따로 기록한다. 원문 verdict의 anchored extraction 규칙은 이번에
  본 응답에서 정했음을 유지하고 다음 대조의 출력 전에 고정한다. 유보/파싱 실패를 제외하지 않는다.
- `START+END`와 `END+END`의 판정 변화·reference 일치 변화, 기존 END-only와의 관계를 본다.
  차이가 없으면 이번 apparent gain은 실제 START 없이 설명될 수 있다. 차이가 남아도
  과거 이미지 내용의 영향일 뿐 올바른 temporal reasoning이나 failure transfer의 입증은 아니다.
- 이 한 대조 후 설명과 투자 가치를 재평가한다. 형식 수리나 큰 모델 교체를 자동으로 이어가지
  않는다. 현재 Q7을 기각하거나 hypothesis로 승격하지 않으며 Q14 reserve를 유지한다.

### VLM verification and recovery

Model transfer `20260915_184932` completed, exit 0: 15 files / 8,992,153,791 bytes verified
against upstream LFS SHA256 or Git blob SHA1. `download.json` also records every file's SHA256.
GPU build, processor-only check, CUDA inference and independent review all exited 0.
The inference used BF16 on RTX 5090; CPU fallback was not needed. No task prediction rerun occurred.

| 실행 비용, 공유 GPU의 진단값 | END-only | START+END |
| --- | ---: | ---: |
| Image tokens | 243 | 486 |
| Total input tokens | 386–391 | 653–658 |
| Generated tokens, 15개 합계 | 141 | 162 |
| Median wall time / case | 0.223 s | 0.281 s |
| Maximum PyTorch allocated memory | 4,649,757,184 bytes | 4,700,638,720 bytes |

위 memory는 GPU 전체 사용량이 아니며 동시 실행 환경의 latency를 독점 성능으로 해석하지 않는다.
CPU processor 검사는 END tensor가 두 조건에서 동일함을 15개 모두 확인했다. 별도 Docker
review는 30개 case/condition 연결, 입력 image identity·phase/view 순서, prompt 경계,
3/6-image와 243/486-token 대응, 원문 파싱과 output hash를 대조해 PASS였다. Source label과
terminal timing의 독립 검증을 뜻하지 않는다. Review log prefix: `logs/20260915_190234_q7_vlm_review`.

[model.json](model.json), [vlm_config.json](vlm_config.json), [Dockerfile.vlm](Dockerfile.vlm),
[requirements.vlm.lock](requirements.vlm.lock), [vlm_environment.json](vlm_environment.json)과
[outcome.json](outcome.json)의 `vlm_comparison`이 pin·환경·compact 결과·source/output hash를 소유한다.
Immutable image: `research3-q7-vlm@sha256:0ceebb0f0fabbbfe4ab1d0ee7a29326ac99a210b51cc12faf0c6aa567d3f015e`.
원문 30개는 `runs/q7/vlm/predictions.jsonl`, 입력은 `inputs.json`, 환경은 `runtime.json`,
완료와 대조 결과는 `completion.json` / `review.json`이다. Processor 검사는 `runs/q7/vlm_input_check.json`이다.

재현은 `fetch_model.py`로 pinned checkpoint를 복원·hash 확인하고, 기록한 image 또는 recipe/lock을
사용한다. `run_vlm.sh`의 output mount와 `--output`을 새 빈 경로로 지정한 뒤 `check`, `infer`,
`review`를 실행한다. Reviewer의 `--run`과 check output도 같은 새 경로를 가리켜야 한다.
기존 output이 있으면 infer/review가 실패하는 것은 보존을 위한 동작이다. 다운로드 receipt만으로
weight를 대신할 수 없고 compact outcome만으로 원문 근거를 대신할 수 없다. 외부 backup과
삭제 안전성은 검증하지 않았다.

2026-09-16 [workspace 정리 검토](../../../../docs/reproducibility.md#workspace-file-cleanup--2026-09-16)는
두 weight shard를 외부 backup 검증 후 삭제할 후보로 분류했다. 두 shard는 중복이 아니며
삭제하면 재추론에 복원이 필요하다. 작은 model metadata와 기존 결과는 유지한다. 실제 삭제는 없다.


## END Repetition Control 2026-09-16

Status: `completed`. 아래 계획에 따라 8개 추가 추론·7개 입력 identity 재사용·독립 대조를 완료했다. 모델·원본 데이터·prompt·
processor·greedy decoding·seed·BF16/SDPA와 GPU memory cap을 유지한다. START 위치에 END를
넣는 조작만 수행한다. `vlm.py`와 기존 config/output은 보존하고 wrapper가 별도 config/case를
만들어 원래 inference 함수를 호출한다. 출력은 ignored `runs/q7/end_repeat/`다.

실행 전 CPU Docker에서 전체 15개의 prompt·image hash·input IDs·END tensor 대응과 여섯-image
입력의 두 절반이 같음을 검사한다. 원래 START+END와 전체 tensor가 같은 7개만 재사용하며,
나머지 source 8개에만 새 generation을 수행한다. 7개 재사용은 독립 재실행/재현성 검사가 아니다.
기존 JSON compliance와 이전에 정한 원문 verdict extraction을 별도로 보고, reference label과
유보/형식 실패를 유지한다. 주요 비교는 START+END 대 END+END의 case별 판정 및 일치 변화다.
기존 END-only와의 비교도 함께 기록한다. 새로운 prompt tuning·학습·case 추가는 없다.

실행 전 GPU snapshot: RTX 5090 32,607 MiB 중 1,161 MiB 사용, utilization 0%. 기존과 같은
project image digest와 GPU UUID를 사용한다. Device/runtime 변경이 필요하면 기록하고 비교
해석을 제한한다. 별도 run 사이 수치적 변동을 이 설계만으로 추정하지 못한다. 같은 seed의
단일 greedy 출력은 일반적인 deterministic-repeatability 증명도 아니다.

Batch launched `20260916_100415`, session `research3_q7_repeat_20260916_100415`, cwd repository root; log/exit `logs/20260916_100415_q7_repeat_batch`.
Command: `bash run_repeat.sh prepare`, then `infer`, then `review` from this study (script changes cwd to repository root). Dependent stages stop on failure.

END repetition `prepare` launched: `research3-q7-repeat-prepare-20260916_100415`; log/exit prefix `logs/20260916_100415_q7_repeat_prepare`.

```bash
timeout 1200s docker run --name research3-q7-repeat-prepare-20260916_100415 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw\,size=512m --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/prepared\,dst=/prepared\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/vlm\,dst=/previous\,readonly --mount type=bind\,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b\,dst=/model\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/end_repeat\,dst=/output research3-q7-vlm@sha256:0ceebb0f0fabbbfe4ab1d0ee7a29326ac99a210b51cc12faf0c6aa567d3f015e /study/repeat_end.py prepare 
```

END repetition `research3-q7-repeat-prepare-20260916_100415` exit `0`.

END repetition `infer` launched: `research3-q7-repeat-infer-20260916_100420`; log/exit prefix `logs/20260916_100420_q7_repeat_infer`.

```bash
timeout 1200s docker run --name research3-q7-repeat-infer-20260916_100420 --gpus device=GPU-90cacfcf-72fe-4b1c-1bd4-cffb389ff9ea --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw\,size=512m --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/prepared\,dst=/prepared\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/vlm\,dst=/previous\,readonly --mount type=bind\,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b\,dst=/model\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/end_repeat\,dst=/output research3-q7-vlm@sha256:0ceebb0f0fabbbfe4ab1d0ee7a29326ac99a210b51cc12faf0c6aa567d3f015e /study/repeat_end.py infer 
```

END repetition `research3-q7-repeat-infer-20260916_100420` exit `0`.

END repetition `review` launched: `research3-q7-repeat-review-20260916_100429`; log/exit prefix `logs/20260916_100429_q7_repeat_review`.

```bash
timeout 1200s docker run --name research3-q7-repeat-review-20260916_100429 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --cpus 4 --memory 16g --memory-swap 16g --pids-limit 128 --user 1001:1001 --tmpfs /tmp:rw\,size=512m --mount type=bind\,src=/home/yoohyun/research3/buildup/robotics/pilot_studies/q7-failure-source\,dst=/study\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/prepared\,dst=/prepared\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/vlm\,dst=/previous\,readonly --mount type=bind\,src=/home/yoohyun/research3/checkpoints/q7/smolvlm2-2.2b\,dst=/model\,readonly --mount type=bind\,src=/home/yoohyun/research3/runs/q7/end_repeat\,dst=/output research3-q7-vlm@sha256:0ceebb0f0fabbbfe4ab1d0ee7a29326ac99a210b51cc12faf0c6aa567d3f015e /study/repeat_end.py review 
```

END repetition `research3-q7-repeat-review-20260916_100429` exit `0`.


### Repetition results 2026-09-16

**사실:** 새로운 generation은 source 8개뿐이다. 나머지 7개는 prompt·image hash·input IDs·
전체 processor tensor가 이전 START+END와 같음을 확인해 응답을 재사용했다. 15개 전체에서
END tensor 보존, 두 이미지 묶음의 동일성, 기존 START+END와 동일한 text/token 수를 확인했다.
이전 30개 출력은 변경하지 않았다. 새 8개도 EOS로 종료했으며 모두 JSON 형식을 지키지 않았다.
누적 **38개 고유 generation의 JSON compliance는 0/38**이고 truncation은 없다.

다음 표의 원문 판정 규칙은 이전 30개를 본 뒤 정했으며, 이번 8개 출력 전에는 고정돼 있었다.
JSON 평가는 그대로 실패로 남긴다. 이 소수의 이미 본 사례를 held-out 성능으로 해석하지 않는다.

| 원문 판정의 진단 | END-only, 기존 | START+END, 기존 | END+END, 8개 신규 + 7개 재사용 |
| --- | ---: | ---: | ---: |
| Reference agreement | 2/15 | 6/15 | 6/15 |
| Source reference agreement | 1/11 | 4/11 | 4/11 |
| Constructed reference agreement | 1/4 | 2/4 | 2/4 |
| UNCERTAIN | 12/15 | 5/15 | 5/15 |
| False positive / false negative | 0 / 1 | 1 / 3 | 1 / 3 |
| Strict JSON reference agreement | 0/15 | 0/15 | 0/15 |

Always GOAL_NOT_MET의 9/15 기준은 유지한다. 새 추론을 수행한 8개만 보면 START+END와
END+END 모두 reference agreement 4/8, UNCERTAIN 2/8이다. **판정은 6/8개에서 같고 두 개에서
다르다.** 재사용 7개를 포함하면 13/15 일치지만, 그 7개를 반복 추론의 일치 증거로 세지 않는다.

| 실제 START 대 END 반복의 차이 | source reference | START+END | END+END | 실제 START 사용 시 |
| --- | --- | --- | --- | --- |
| drawer_ball source failure, row 72 | NOT_MET | NOT_MET | UNCERTAIN | reference 일치 +1 |
| fruit source failure, row 126 | NOT_MET | UNCERTAIN | NOT_MET | reference 일치 −1 |

두 조건 사이의 전체 일치 수 차이는 0이다. END-only 대비 +4개의 일치 증가와 유보 감소는
END 반복에서도 관찰됐다. **전체 일치 수의 증가는 실제 START 없이도 재현됐지만 모든 사례의
판정이 같은 것은 아니다.** 두 case의 차이를 무시해 완전한 동등성이나 START 무용성을
주장하지 않는다. 서로 다른 날의 한 번씩의 greedy run이며 실행 변동을 따로 추정하지 않았다.

### Interpretation and investment review

**에이전트 추론:** 이번 모델·prompt·dev 사례에서는 이전의 전체 일치 수 증가를 올바른 시간
정보 활용의 근거로 쓸 수 없다. 관측 형식과 이미지 반복의 영향부터 분리해야 한다는 진단을
얻었다. 과거 이미지가 모든 상황에서 불필요하다거나 failure-source generalization 문제가
없다는 결론은 아니다. 모델의 낮은 형식 준수·기초 판정 능력, source label/terminal timing의
미확정도 그대로 남는다. Case-level 오판의 시각적 원인을 설명할 evidence는 여전히 부족하다.

현재 **SmolVLM2 + 같은 15개 사례의 prompt/관측 변형 확대는 다음 투자로 선택하지 않는다.**
JSON 강제·더 큰 모델·frame/crop sweep으로 자동 확대해도 원래 failure-source 질문보다
baseline 수리의 비중이 커질 수 있다. 반대로 이 결과만으로 Q7 전체를 종료하지 않는다.
Q7 status를 `under_review`로 두고, 다음 TODO는 다음 두 초안을 기존 관찰·가까운 선행·
얻을 정보와 비용으로 비교해 하나의 연구 질문/다음 관찰을 선택하는 것이다.

- Q7 수정 초안: task 달성 증거를 맞췄을 때 constructed/execution failure 사이에 남는
  판정 차이는 무엇인가? 출력 형식·입력 중복·단순 상태 판정의 한계를 구분할 수 있는
  작은 관찰을 제시한다. 이번 약한 baseline의 실패만으로 새 verifier를 정당화하지 않는다.
- Q14 기존 초안: learned action/geometry 출력의 shared error가 실제로 상쇄되는가?
  기존 coordinate identity/noise 대조를 넘어서 무엇을 관찰할지 구체화한다.

이번 작업에서는 새 문헌 조사나 두 후보의 최종 비교를 완료했다고 주장하지 않는다. 이
재비교는 positive effect, full benchmark 또는 최종 method 완성을 요구하는 gate가 아니다.
더 많은 같은 추론을 수행하는 것보다 다음 관찰의 정보 가치를 먼저 판단하자는 투자 결정이다.
Q14는 exploratory reserve이며 hypothesis/experiment/paper 승격은 없다.

### Control verification and recovery

CPU prepare·CUDA inference·CPU review 및 wrapper batch가 모두 exit 0이다. 새 8개 case의
추론은 기존과 같은 model revision·image digest·Python/Torch/CUDA/Transformers·BF16·GPU·
SDPA·seed·processor를 사용했다. GPU는 덜 혼잡했으므로 latency를 이전 run과 성능 비교하지 않는다.
새 8개 총 generated tokens는 82, median wall time은 0.150 s/case, 최대 PyTorch allocated
memory는 4,700,943,360 bytes다. Runtime 전체 환경은 output에 보존한다.

`repeat_end.py`의 prepare는 입력 조작·재사용의 타당성을 확인한다. 별도 Docker review는 기존
출력 hash 보존, config에서 scope 관련 세 필드만 변경됐는지, 실제 inference 입력과 계획의
prompt·phase/view·image 연결, 환경 parity, 여덟 출력의 빠짐/중복과 파싱을 대조했다.
기존 JSON parser와 별도의 review parser를 비교했으며, 이전 두 조건의 일치 수도 기존
compact 결과와 같음을 확인했다. PASS는 source label/terminal timing의 검증을 뜻하지 않는다.

코드는 [repeat_end.py](repeat_end.py), 명령은 [run_repeat.sh](run_repeat.sh)와 위 launch 기록이
소유한다. 기존 `vlm.py`, `vlm_config.json`, 모델/처리기 파일과 이전 inference 출력은 그대로다.
새 output root는 `runs/q7/end_repeat/`: `plan.json`은 재사용/신규 구분과 입력 검사,
`config.json` / `cases.json`은 범위가 줄어든 입력, `predictions/`는 실제 여덟 원문·runtime·
completion, `review.json`은 15개 대응과 진단 결과다. 새 원문 record의 `condition=start_end`는
유지한 START/END prompt 위치를 뜻하며, 실제 영상은 END+END다. `plan.json`에 이를 명시했다.

[Compact outcome](outcome.json)의 `end_repetition_control`에 새 source/output identity와
요약을 추가했다. 재실행할 때 `run_repeat.sh`의 output host mount를 새 빈 경로로 바꾸고
`prepare`, `infer`, `review` 순서로 실행한다. `previous` read-only mount에는 보존된 원래
30개 비교가 필요하며 7개 재사용의 근거이므로 새 여덟 출력만으로 전체 비교를 복구할 수 없다.
외부 backup/삭제 안전성은 검증하지 않았고 dataset/checkpoint/raw 출력은 보존한다.

### Container cleanup 2026-09-16

사용자 요청으로 AGENTS.md에 workspace가 생성한 불필요한 container만 정리하는 규칙을 추가했다.
이번 prepare/infer/review container 3개의 생성 기록·정확한 image/command·workspace mount와
exit 0을 확인하고 결과/원문/로그/hash/재현 정보를 먼저 보존한 뒤 각 ID를 지정한 `docker rm`으로
삭제했다. 다른 container와 image·volume·cache는 변경하지 않았다. 삭제한 container의 ID·mount·
명령·완료 상태는 `outcome.json`의 `end_repetition_control.containers`가 소유한다.
Cleanup log: `logs/20260916_100804_q7_repeat_cleanup.log`.

## Docker cleanup review 2026-09-16

Image/container 삭제 후보와 재개·전체 재현에 미치는 영향은
[repository cleanup review](../../../../docs/reproducibility.md#docker-cleanup-review-2026-09-16)가 소유한다.
이번 검토는 읽기 전용이며 Docker 자산을 삭제하지 않았다. 기존 실행/보존 기록은 유지한다.
