# Completion Model Readiness

Updated: 2026-09-11 · actual CPU reference outputs executed and independently verified

## Current result

Frozen CPU reference protocol을 실제 네 입력에 두 process로 실행했다. **총 8 forward와
네 case의 독립 output 검증이 모두 통과**했다. 고정 판정은
`REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED`이며
[실제 결과](#verified-completion-results-2026-09-11)가 이번 실행의 범위를 소유한다.
Native CUDA 동등성·물리 연결은 미검증이다. 다음은 이 결과와 남은 연결 비용에 근거해
후속 action-linked 검증의 정보 가치 또는 refine/defer를 판단하는 것이다.

앞선 construction-only [schema result](schema_result.json)의
`STATE_COMPATIBLE_FORWARD_UNVERIFIED`와 [독립 metadata receipt](schema_verification.json)는
2026-09-10의 기록으로 보존한다. 기존 [input v1](../README.md#verified-input-results-2026-09-10),
schema 및 completion freeze는 변경하지 않았다.

| Checkpoint check | Observed result |
| --- | --- |
| state root | `base_model`; original loader가 허용하는 root |
| prefix | 모든 key의 leading `module.`만 제거 |
| tensor schema | 408개 key/shape/dtype 모두 일치 |
| model parameters | 42,104,454 |
| missing / unexpected / mismatched | 모두 0 |
| nonfinite tensor | 0 |
| strict load 후 tensor equality | 408/408 exact |
| checkpoint probe forward / native calls | 0 / 0 |

검사 전에 [schema protocol](schema_protocol.json)과 [schema freeze](schema_freeze.json)를
고정했다. Root ambiguity, mixed prefix, shape mismatch와 strict missing-key 거부 및 native
forward guard를 synthetic check로 확인했다. Model의 CUDA allocation 한 곳만 CPU로 바꾸고
native 연산을 호출 시 실패하는 placeholder로 둔 construction adapter다. 독립 verifier는
원본 checkpoint를 다시 읽어 metadata/finite 여부와 receipt를 확인하며 model forward를
독립 재현한 검사는 아니다. 원본 state를 삭제·reshape하거나 다른 weight를 사용하지 않았다.

## Runtime choice and limits

**사실:** source는 FPS/KNN/gather CUDA extension에 의존한다. 원래 dependency commit은
고정돼 있지 않다. 이번에 확인한 Pointnet2 source의 FPS는 index 0에서 시작하고 squared
magnitude `<= 1e-3`인 후보를 건너뛰며 thread reduction 순서가 동률 선택에 관여한다.
[Operator source receipt](operator_sources.json)에 pinned snapshot과 local hashes를 보존했다.
KNN_CUDA의 GitHub API/ref와 raw master URL은 이번 접근에서 HTTP 404를 반환했다.
Cached web page만으로는 native build source를 검증할 수 없다.

**판단:** 이번 output-provenance 검증은 [CPU reference operators](reference.py)를
사용했다. Audited FPS의 시작점·후보 제외·tie reduction을 반영하고 KNN은 squared Euclidean
거리와 stable reference-index tie 순서를 명시한다. Gather는 exact indexing이다.
학습 구조와 모든 weight는 유지하지만 CPU/native rounding과 KNN parity는 미검증이다.
따라서 **native CUDA/전체 3DSGrasp 재현이나 model quality 평가로 해석하지 않는다**.
이는 independent generated output의 shape·복사 위치·재현 가능성을 확인하는 제한된 경로다.
원래의 역사적 training operator version도 확인되지 않았다.

준비 snapshot에서 GPU는 30,301/32,607 MiB, utilization 100%였다. GPU 작업을 시작하거나
기존 작업을 중단·수정하지 않았다. 새 official Python base와 hash-locked PyTorch CPU image만
구성했고 큰 CUDA stack, ROS/GPD, simulator와 training dependency는 추가하지 않았다.

## Frozen completion protocol

[completion_protocol.json](completion_protocol.json), [input manifest](completion_inputs.json),
[completion_freeze.json](completion_freeze.json)이 실행 범위·source·environment를 고정한다.

- 기존 네 쌍을 그대로 사용한다. v1의 hash-verified sampled XYZ 2,048개를 partial-derived
  float64 centroid/radius로 정규화하고 float32로 변환한다. GT는 predictor에 mount하지 않는다.
- 같은 checkpoint, seed 12021, CPU 4/RAM 4 GiB에서 별도 process 두 번을 실행한다.
  총 8 forward, repeat당 10분, 독립 verifier 5분, output 합계 목표/검사 한도 64 MiB다.
  Runtime network, GPU, 학습, 추가 data 취득과 physical rollout은 없다.
- 원본 forward의 dense 8,192개 중 `[0,6144)`는 generated, `[6144,8192)`는 copied input이다.
  Sparse 192개 중 `[0,96)`는 generated, `[96,192)`는 reference FPS copied input이다.
  후자의 source indices를 보존한다. Generated point가 입력과 수치상 같아도 출처를 바꾸지 않는다.
- Dense/sparse shape·finite 값, strict loading, copied suffix의 bit equality, partial transform과
  inverse error, 두 process의 array equality를 검사한다. Independent NumPy verifier는
  model/torch/checkpoint를 import하거나 load하지 않는다. Model 실행 자체의 독립 구현은 아니다.
- GT의 supplied 8,192 rows를 모두 보존하며 FPS나 deduplication을 적용하지 않는다.
  Unique support와 generated/input exact coincidence는 descriptive count만 기록한다.
  새 reconstruction metric·성공 cutoff는 없다. 후속 distance 분석은 row-weighted와
  unique-support 진단을 별도로 사전 정의해야 한다.

Hash/global loading 오류나 timeout/OOM이면 보존 후 중단한다. Case 실패는 네 쌍의 denominator에
남기며 sample 교체·threshold 변경·자동 자원 확대를 하지 않는다. 모두 통과해도 판정은
`REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED`다. Native parity, object train/test
중복, checkpoint training manifest 부재, per-file metric frame/camera/ray/physical outcome
연결은 해결되지 않는다. Novelty, robotics benefit/harm 또는 hypothesis 승격을 뜻하지 않는다.

## Synthetic verification

[Operator/full-model preflight](preflight.json)는 origin exclusion·ties·strided FPS를 independent
scalar algorithm과 비교하고 KNN ties/gather를 검사했다. Synthetic weight/input의 전체 model
forward 두 번은 shape·finite·copied suffix·repeat equality를 통과했다.
[Pipeline test](pipeline_test.json)는 실제 predictor/verifier CLI를 synthetic checkpoint·네
synthetic 입력으로 두 process에 실행했다. Hash를 다시 맞춘 copied-coordinate 변조도 검출했고
나머지 세 case와 전체 denominator를 유지했다. 실제 checkpoint/XYZ는 이 테스트에 mount하지
않았다. Native CUDA parity 검사가 아니며 실제 네 completion의 성공을 예측하지 않는다.

## Jobs and recovery

2026-09-11 이 image는 active Q12의 재검사 환경으로 유지 권장이다. 지정 image들의
[cleanup assessment](../../../../../docs/reproducibility.md#image-cleanup-assessment--2026-09-11)에
삭제 가능성·동일 환경 복구 제약을 기록했고 실제 삭제나 frozen artifact 변경은 없다.

모든 command의 cwd는 `/home/yoohyun/research3`다. Source와 checkpoint/입력은 read-only,
output만 아래 전용 root에 쓴다. 원본 weight/data나 frozen result는 삭제하지 않는다.

| Job | Status | Owner/output |
| --- | --- | --- |
| CPU image build | completed | `image_id.txt`, `environment.txt`, `image_bytes.txt` |
| schema probe | completed | `runs/q12_model_schema/data/schema.json` |
| independent schema audit | completed; logging wrapper repaired and rechecked | `runs/q12_model_schema_audit_recheck/verification.json` |
| reference operator/full-model preflight | completed | `runs/q12_model_reference_preflight/preflight.json` |
| synthetic pipeline | completed | `runs/q12_model_reference_preflight/pipeline_test.json` |
| actual four-input completion + frozen NumPy verifier | completed 2026-09-11; exit 0 | `runs/q12_completion_reference_v1/` |
| post-run output byte audit | completed 2026-09-11; exit 0 | `runs/q12_completion_reference_v1_audit/audit.json` |

Image: `research3-q12-model-schema:v1`, immutable ID
`sha256:9977f452f5bb84734c210e911110d23a2dacf9fb38d94c260d864c65da1444d6`.
[Dockerfile](Dockerfile), [requirements](requirements.txt), [dependency receipt](dependencies.json),
[source receipt](sources.json)와 [preparation execution receipt](execution.json)가 준비 단계의
recovery 근거다. 실제 실행 command·log·11개 output hash는
[completion execution receipt](completion_execution.json)가 소유한다.
Build 한도 20분, dependency download 목표 500 MiB, image/build 저장 목표 4 GiB였으며 build가
완료됐다. `image_bytes.txt`는 Docker가 보고한 image size이며 전체 cache disk usage 측정은 아니다.

```bash
# 이미 완료된 단계: output이 있으면 그대로 덮어쓰지 않는다.
bash buildup/robotics/pilot_studies/q12-generated-geometry/model/build.sh
bash buildup/robotics/pilot_studies/q12-generated-geometry/model/probe.sh
bash buildup/robotics/pilot_studies/q12-generated-geometry/model/verify_schema.sh
bash buildup/robotics/pilot_studies/q12-generated-geometry/model/preflight.sh
bash buildup/robotics/pilot_studies/q12-generated-geometry/model/pipeline_test.sh

# 2026-09-11 완료한 실행: 기존 output이 있으면 거부한다.
tmux new-session -d -s research3_q12_completion_reference 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/model/run_completion.sh'

# 완료한 post-run byte audit: model forward 없이 저장된 출력만 읽는다.
tmux new-session -d -s research3_q12_output_bytes 'bash /home/yoohyun/research3/buildup/robotics/pilot_studies/q12-generated-geometry/model/audit_output.sh'
```

`run_completion.sh`는 기존 output root가 있으면 거부한다. Expected files는
`predictions/{0,1}/result.json`, 각 repeat의 `{0,1,2,3}.npz`, `verification/verification.json`이다.
실패 case는 npz가 없을 수 있으며 이를 완료로 간주하지 않는다. Log는
`logs/<timestamp>_q12_completion_reference.log` / `.exit`; 종료 후 exit status와 verifier의
네 case/decision 및 output hashes를 함께 확인한다. Container command·mount·timeout·cleanup은
[run_completion.sh](run_completion.sh)가 소유한다. Source/model/image/row-level 출력의 full
reproduction 보존과 compact 결과 보존을 구분하며 외부 사본 검증 없는 삭제는 하지 않는다.

## Verified completion results 2026-09-11

**Observed:** [completion result](completion_result.json)는 원본 frozen NumPy verifier output의
byte-identical copy다. 두 predictor process는 각각 네 입력에 strict loading·shape·finite·
copied-point 검사를 통과했다. Dense `(8192,3)`의 generated 6,144개와 copied 2,048개,
sparse `(192,3)`의 generated 96개와 copied 96개가 원본 forward의 구분과 일치했다.
네 case 모두 generated unique count는 6,144, generated/input exact coincidence는 0이었다.
이는 source상 generated 출처와 좌표 개수의 진단이며 shape의 정확도나 유용성 점수가 아니다.

| Object / test stem | Both processes / independent verifier | GT unique / supplied rows | Copied inverse scaled max error |
| --- | --- | ---: | ---: |
| banana / `_0_0_5_` | pass / pass | 4,025 / 8,192 | 2.780077e-08 |
| banana / `_0_0_7_` | pass / pass | 4,273 / 8,192 | 2.892758e-08 |
| binder / `_0_0_1_` | pass / pass | 8,074 / 8,192 | 2.972778e-08 |
| binder / `_0_0_2_` | pass / pass | 8,097 / 8,192 | 2.934487e-08 |

모든 copied inverse error는 frozen tolerance `2e-6` 이하다. GT는 predictor에 mount하지 않았고
추론 후 verifier에서만 읽었다. Supplied 8,192 rows를 그대로 유지했으며 기존 input v1과
unique-support count가 일치한다. GT sampling/deduplication이나 새 distance metric은 없다.

두 process 사이의 모든 output arrays와 case별 NPZ SHA-256이 일치했다. Frozen verifier의
`np.array_equal`은 수치 동일성을 검사하므로, literal bit equality도 확인하기 위해 별도
[standard-library byte audit](audit_output.py)을 Docker에서 실행했다. [Audit receipt](output_audit.json)는
NPZ 8개/NPY member 48개의 CRC·header·반복 bytes와 dense/sparse copied bytes가 모두 같음을
확인한다. Signed-zero 차이도 허용하지 않는 검사다. 이 post-run 감사는 저장된 출력만 읽으며
추가 forward·metric·threshold 변경을 하지 않았다.

실제 workload는 frozen CPU 4/RAM 4 GiB, seed 12021, 두 process/총 8 forward 한도 내에서
완료됐다. Main output은 11개 파일, 1,023,523 bytes로 64 MiB 이하다. Memory 수치는 cap이며
peak 사용량을 측정하지 않았다. `logs/20260911_094852_q12_completion_reference.log`와
`logs/20260911_095031_q12_output_bytes.log`의 exit는 모두 0이다. Checkpoint load를 포함한
end-to-end latency benchmark는 수행하지 않았다.

**Interpretation and next risk:** 이 CPU reference 경로에서 checkpoint 기반 completion을
GT 입력 없이 생성하고, copied/generated 출처와 좌표 복원·반복 재현성을 확인할 수 있다.
Native CUDA/역사적 training operator와의 동등성, GT의 물리적 정확성, per-file metric frame와
camera/ray 연결, object-disjoint generalization 및 로봇 action/outcome 효과는 미확인이다.
현재 결과로 completion bias·robotics benefit/harm·novelty를 주장하거나 hypothesis로 승격하지
않는다. 다음 TODO는 native parity와 physical/camera linkage를 확보하는 각 경로의 비용·정보
가치를 비교해 후속 검증 또는 refine/defer를 판단하는 것이다. 자동 재실행·학습 확대와 Q13
승계는 없다.

Compact 결과 보존에는 이 폴더의 result/audit/실행 manifest와 frozen source·protocol을,
현재 출력의 재검사에는 별도 보존된 NPZ·raw result JSON을 포함한다. 전체 재현에는 pinned
checkpoint, sampled/raw inputs 및 Docker image 또는 recipe/locks가 추가로 필요하다.
기존 input/schema/준비 receipt는 보존했고 원본·cache·image의 삭제나 외부 전송은 없었다.
