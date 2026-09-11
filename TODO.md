# TODO

Updated: 2026-09-11

## Now

- [ ] [Q12 출력 검증 결과](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11)를
  근거로 native operator parity·physical/camera 연결 경로의 비용과 정보 가치를 비교한다.
  작은 action-linked 검증의 실행 가능성 또는 refine/defer를 판단하며 Q13을 자동 승계하지 않는다.

## Next

- [ ] 후속 비교에서 선택한 경로만 검증 protocol로 구체화한다. 진행 근거가 없으면
  Q12의 수정·보류 조건을 기록하며 같은 입력 반복이나 학습 확대로 대체하지 않는다.

## Deferred Reassessment

- [ ] Q13은 matching checkpoint·작은 matched-state/action-value 사례 또는 구체적인
  source-grounded failure case가 생기면 재비교한다. [재진입 조건](buildup/selection.md#q13-disposition-and-re-entry).

- [ ] Q8의 distinct perturbation-transfer target, equal-cost empirical-success control,
  training-data-linked policy와 valid demonstration restart가 구체화될 때만 재진입을 검토한다.

## Recently Completed

- [x] 지정한 Q11/Q12 Docker image 네 개의 삭제 가능성을 검토했다. Container 참조는 모두
  0개다. Q11 두 개는 우선 삭제 후보, Q12 input은 삭제 가능, active Q12 model은 유지 권장이다.
  실제 삭제는 없으며 [결과 보존·재개·전체 재현의 차이](docs/reproducibility.md#image-cleanup-assessment--2026-09-11)를 기록했다. (2026-09-11)

- [x] Q12 frozen CPU reference protocol을 실제 네 입력에 두 process/총 8 forward로 실행했다.
  네 case의 독립 verifier와 NPZ 8개/NPY 48개의 byte 감사를 통과해
  `REFERENCE_OUTPUT_VERIFIED_NATIVE_AND_PHYSICAL_UNRESOLVED`다. GT row·기존 freeze를
  보존했으며 native/물리 검증·새 metric·hypothesis 승격은 없다.
  [결과·artifact·한계](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md#verified-completion-results-2026-09-11). (2026-09-11)

- [x] Q12 checkpoint의 408개 tensor schema·strict loading과 독립 metadata 검증을 완료했다.
  새 CPU Docker와 reference completion protocol을 준비하고 synthetic forward·pipeline 및
  copied-point 변조 검출을 확인했다. 실제 네 입력 추론 전 43개 파일을 고정했으며 native
  CUDA parity·물리 연결은 미검증이다. [결과·protocol·command](buildup/robotics/pilot_studies/q12-generated-geometry/model/README.md). (2026-09-10)

- [x] Q12 frozen input v1을 실제 네 쌍에 CPU Docker로 실행·독립 검증했다. 네 쌍의 schema·좌표
  controls와 원본 hash가 통과해 `INPUT_CONTROLS_VALID_PHYSICAL_FRAME_UNRESOLVED`다.
  GT 반복 좌표와 train/test 중복을 기록했으며 protocol 변경·model inference·hypothesis 승격은 없다.
  [결과·검증·경계](buildup/robotics/pilot_studies/q12-generated-geometry/README.md#verified-input-results-2026-09-10). (2026-09-10)


- [x] Q12 공개 dataset/model 취득, 네 partial/GT 쌍의 name/CRC/SHA-256 검증과 CPU input
  protocol v1 고정을 완료했다. 새 Docker의 synthetic end-to-end·독립 verifier 검증을 통과했다.
  실제 XYZ array 검사와 model inference는 미실행이며 train/test object 중복·물리 좌표 metadata
  부재를 명시했다. [준비·protocol·다음 실행](buildup/robotics/pilot_studies/q12-generated-geometry/README.md). (2026-09-10)


- [x] Q12/Q13을 여덟 기준과 다음 측정의 정보 가치·비용으로 비교했다. Q12의 독립 입력/좌표
  검증 준비를 선택하고 Q13은 `deferred`로 두었다. 두 후보의 novelty와 empirical effect는
  미확정이며 protocol 고정·실행·학습은 시작하지 않았다.
  [비교·선택·다음 분기](buildup/selection.md#q12q13-measurement-selection-2026-09-10). (2026-09-10)

- [x] Q13 Stage 4–5를 완료했다. DISaM/GCNGrasp-VP의 직접 선행, virtual view와 새 관측의
  차이, 공개 evaluator의 상태·비용·성공 판정 한계를 확인했다. 기존 score와 decision value의
  제한된 진단으로 좁히고 조건부 검증안을 기록했다. Source/metadata만 검사했다.
  [근거](buildup/robotics/related_work/policy-geometry.md#q13-stage-4-review-2026-09-10) ·
  [가정·검증안](buildup/robotics/questions/action-relevant-view-selection.md#stage-5-assessment-2026-09-10). (2026-09-10)

- [x] Q12 Stage 4–5를 완료했다. G3Flow의 shared physical/virtual asset 경로와
  3DSGrasp의 좌표 복원 차이를 확인하고, independent completion/GT 입력 검증안을 정했다.
  Source/metadata만 검사했으며 Q12는 `under_review`; 다음 검토는 Q13이다.
  [근거](buildup/robotics/related_work/policy-geometry.md#q12-stage-4-review-2026-09-10) ·
  [가정·검증안](buildup/robotics/questions/generated-geometry-reliance.md#stage-5-assessment-2026-09-10). (2026-09-10)

- [x] Q12/Q13/Q14를 primary source와 공개 artifact 기준으로 재비교해 Q12 1순위,
  Q13 2순위, Q14 reserve로 정했다. G3Flow의 별도 encoding/consistency를 반영해 Q12의
  초기 가정을 수정하고 Q13의 기존 action-guided sensing 충돌을 기록했다. 문헌·source·
  metadata만 검사했으며 새 실행/학습·hypothesis 승격은 없다.
  [비교와 후속 과제](buildup/robotics/related_work/policy-geometry.md#reserve-reassessment-2026-09-10). (2026-09-10)

- [x] Frozen Q11 v3를 실행·독립 검증했다. 202 trajectories, 642 hashes, 85,472 labels와
  codec 411 chunks 검증 통과. Support는 충족했지만 grasp 1쌍/release 4쌍의 방향성 있는
  차이가 사전 alpha .025를 충족하지 못해 `STOP_NO_CONTACT_LOCALIZATION_SIGNAL`이다.
  고정 규칙대로 현재 method route를 종료했고 reserve 재비교를 다음에 두었다.
  [결과](buildup/robotics/pilot_studies/q11-action-compression/README.md#v3-verified-results) ·
  [종료 경계](buildup/selection.md#q11--discontinue-current-route-2026-09-10). (2026-09-10)

- [x] Q11의 한 번의 제한된 v3 revision을 구현·고정했다. Calibration 8개 / codec 144
  chunks에서 독립 복원 오차 0, joint/Linear rate·MSE overlap, 자연 residual grasp 5쌍 /
  release 3쌍을 확인했다. Contract test 3개 군을 통과하고 새 seed·support gate·중단 기준을
  freeze했다. 기존 v1/v2 변경, 새 physical episode·fit·grid 확대는 없었다.
  [Frozen v3](buildup/robotics/pilot_studies/q11-action-compression/v3/freeze.json). (2026-09-08)

- [x] Q11 Stage 7을 `refine`으로 결정했다. CPU Docker에서 기존 calibration 45개 점을
  감사해 6-bit/3-knot의 symmetric rate/MSE overlap과 strict-cap 초과를 구분했다.
  Held-out 동시 support 부재와 성공한 quantile residual만 사용한 localization 한계를
  근거로 제한된 수정·종료 조건을 기록했다. 새 rollout/refit/grid 확대·hypothesis 승격 없음.
  [결정](buildup/selection.md#q11--refine-2026-09-08). (2026-09-08)

- [x] Frozen Q11 v2를 Docker에서 실행하고 별도 감사했다. 194 trajectories, 617 hashes,
  83,056 labels와 held-out codec 460 chunks를 검증했다. Joint FAST 2/16 vs quantile
  16/16; exact gripper 후 총 성공 수는 같지만 joint 두 case가 반대로 바뀌었다.
  Grasp 9쌍/release 12쌍 모두 event/free 성공 차이 없음. Uniform byte cap support 부재로
  `INCOMPLETE_CODEC_SUPPORT`; protocol 변경·재실행 없음.
  [결과·감사](buildup/robotics/pilot_studies/q11-action-compression/README.md#v2-verified-results). (2026-09-08)

- [x] Q11 v2 physical pilot protocol·실행/분석 코드·source hash를 결과 전에 고정했다.
  8 calibration/16 held-out seeds, actual byte cap, exact gripper/scaling/interpolation controls와
  동일 arm-error localization을 정의했다. 새 Docker를 빌드하고 synthetic preflight 6개
  검사군을 통과했다. 실제 v2 episode/outcome은 아직 없으며 v1 자료는 보존했다.
  [Frozen v2](buildup/robotics/pilot_studies/q11-action-compression/v2/freeze.json). (2026-09-08)

- [x] Q11 Stage 6 measurement readiness v1을 새 Docker에서 실행·독립 검증했다.
  StackCube 8개 seed/859 actions, 원본 replay 16회와 공식 label 10,404개가 일치했고
  FAST 92 chunks 및 output hash 96개를 검증했다. `READY_FOR_CONTROLLED_PILOT`;
  압축 action의 물리 실행·학습·hypothesis 승격은 아직 없다.
  [Study](buildup/robotics/pilot_studies/q11-action-compression/README.md). (2026-09-08)

- [x] 사용자 선택에 따라 Q11을 단일 active buildup question으로 반영하고 Stage 4--5를
  완료했다. OAT 확장판/SA-VLA/MoEActok과 FASTer를 비교하고, FAST의 clamp/zero-fallback,
  mixed-unit controller와 sampled-contact 한계를 분리했다. Pinned source 9개 원격 일치와
  FAST 2개 파일 hash를 확인해 StackCube measurement-readiness 초안을 정했다.
  Runtime/학습은 미실행이며 Q12는 reserve다. [Q11](buildup/robotics/questions/contact-action-compression.md). (2026-09-08)

- [x] 사용자 관심 논문 63개를 PaperReview와 연결하고 대표 16개 insights 발췌 및 공식
  source를 참고해 Q11--Q15를 작성·비교했다. Q11 action compression과 Q12 generated
  geometry를 Stage 4--5 우선순위로 선택했다. Novelty/Stage 6/hypothesis는 미확정이며
  PaperReview 수정, 새 학습·실행·대규모 download는 없었다.
  [관심 mapping·근거·비교](buildup/robotics/related_work/policy-geometry.md). (2026-09-08)

- [x] 지정된 research3 Docker image 8개와 다운로드 data의 정리 가능성을 검토했다.
  Container 참조는 없고 recipe는 보존돼 있다. Q10 원본 27.80 GiB는 외부 사본 검증 후
  삭제 후보, Q8의 작은 공통 input과 결과는 보존 권장이다. 실제 삭제는 하지 않았다.
  [보존 목적·삭제 조건](docs/reproducibility.md#cleanup-assessment--2026-09-08). (2026-09-08)

- [x] Q1 refinement audit을 완료했다. Pinned task source, public tree의 26 checkpoints,
  열 개 metadata와 primary work를 확인했으나 grounded continuation을 정당화하지 못해
  현재 formulation을 `discontinue`했다. V3 원본을 보존하고 추가 실행은 하지 않았다.
  [Audit](buildup/robotics/related_work/q1-artifact-schema.md#bounded-refinement-audit--2026-09-08) ·
  [Stage 7](buildup/selection.md#q1--discontinue-2026-09-08). (2026-09-08)

- [x] Q1 v3을 새 CUDA Docker에서 실행하고 8쌍의 exact initialization, 16 trajectories,
  96 predicate labels와 800 official step labels를 독립 검증했다. 여섯 조건 모두 PPO-EE
  4/8, PPO-Joint 8/8로 label/rank 변화가 없어 `NO_LABEL_CHANGES_UNINFORMATIVE`다.
  Stage 7은 `refine`; 현재 two-policy/PickCube route 확대와 hypothesis 승격은 하지 않았다.
  [Study와 plot](buildup/robotics/pilot_studies/q1-predicate-stability/README.md). (2026-09-08)

- [x] Q8 심화 감사와 Docker 반복 검증 뒤 Q1을 다음 Stage 6 후보로 선택했다. 두 protocol의
  restore 비교 1,800회와 public demo transition 27회를 확인했다. Reset/contact-history
  문제를 scene reconstruction으로 보완했으며, v2 full-zero-qualified 98개 조건은 3회 모두
  성공해 recovery 차이를 구분하지 못했다. Demo middle-state replay는 0/18 통과했고 scalar
  recovery/empirical-success identity도 확인해 Q8은 `refine`이다. Q1 v3은 변경·실행하지
  않았다. [검증 기록](buildup/robotics/pilot_studies/q8-recoverability/README.md). (2026-09-08)

- [x] Q10 [Stage 7 decision](buildup/selection.md#q10--discontinue-2026-09-08)을 완료했다.
  Summary-only route와 현재 formulation은 `discontinue`, 더 넓은 RGB-relative question은
  미검증으로 구분했다. 근거 있는 reformulation이 없어 Q10을 active priority에서 제외하고
  종료 요약은 `literature/README.md`로 모았다. Q8/Q1은 비교 대상으로 남겼으며 실행·재개·
  artifact 삭제는 하지 않았다. (2026-09-08)
- [x] Q10 v6 regularized probe를 frozen protocol 그대로 CPU-only Docker에서 실행·검증했다.
  Nested primary macro BA 0.5791 vs v5 0.7239, gain interval [-0.2299, -0.0347]로
  `NO_USEFUL_SUMMARY_GAIN`이다. 기존 test의 0.6579는 exploratory로 유지했다. 16,488 fits,
  111,240 inner와 7,021 nested/test predictions를 독립 검증했다. Verifier의 log-loss clipping
  순서만 수정했고 refit/test 재실행·protocol 변경은 없었다. 상세 provenance는
  [study README](buildup/robotics/pilot_studies/q10-contact-observability/README.md)가 소유한다. (2026-09-08)
- [x] Q10 train-only validation audit을 새 Docker에서 완료하고 v6 regularized probe protocol을
  SHA-256으로 고정했다. 실패를 포함한 train recording은 pick/insert/remove 5/9/5개이며,
  모든 nested fitting partition에 양 class가 남았다. Remove는 action-bearing deletion
  6회 중 5회 선택이 바뀌고 CV BA가 0.6146에서 nested 0.4917로 하락했다. 675 fold count와
  309 nested prediction 독립 검증을 통과했다. Logistic probe는 아직 실행하지 않았다.
  [Audit와 protocol 기록](buildup/robotics/pilot_studies/q10-contact-observability/README.md#validation-audit-before-v6). (2026-09-07)
- [x] Q10 deterministic baseline v5를 결과 전에 고정하고 새 CPU-only Docker에서 실행·검증했다.
  413개 row(official train 309/test 104)를 보존했다. Train-CV-selected rule의 test macro BA는
  0.5261, prior는 0.5000, gain bootstrap interval은 [-0.0593, +0.0556]으로
  `UNCERTAIN_RESIDUAL`이다. Remove test가 한 recording에 집중된 한계를 기록했다.
  Invariant test 5개와 독립 1,144 prediction 검증을 통과했고 추가 probe는 실행하지 않았다.
  상세 결과·command·log는 [study README](buildup/robotics/pilot_studies/q10-contact-observability/README.md)가 소유한다. (2026-09-07)
- [x] Q10 larger denominator v4를 label-blind fixed-hash protocol로 실행했다. 기존 v2 anchor
  4개와 issue-free train 12/test 4개를 합친 20개 공개 recording 모두 열렸고, 570 segments 중
  569개가 matched였다. `No action.`을 제외한 524 target rows는 success 473/failure 51이며
  train failure 40, test failure 11이다. Pick 10, insert 29, remove 11 failure로 세 action이
  양 split에서 비교 가능해 `PASS_DENOMINATOR`; place는 failure 1개라 다음 baseline에서
  제외한다. 새 16개 transfer는 6.16 GB compressed/27.49 GB extracted였고 CPU-only Docker로
  실행했다. (2026-09-06)
- [x] Q10 Stage 6 v1--v3를 실행했다. v1은 official train 111/test 37 split과 148개 assigned
  HDF5, per-member byte range access를 확인했다. v2는 label-blind four-file subset 4/4를
  CRC/size/SHA-256 검증해 받고 45개 segment 중 공식 F/T issue 1개를 제외한 44개를
  RGB+F/T+proprioception으로 join했다(40 success/4 failure, `PASS_SCHEMA`). v3는 failure
  4개와 pre-fixed success control 4개의 sparse RGB를 소규모 manual audit했고, 세 방향 판단
  모두 오답/한 pair indistinguishable로 `MIXED_NEEDS_DENOMINATOR`였다. GPU는 사용하지
  않았고 종료 시 RTX 5090은 405/32,607 MiB, 0% utilization이었다. Public data만 사용했으며
  추가 annotation/learned method/three-gate는 시작하지 않았다. (2026-09-06)
- [x] Q10을 단일 Stage 6 candidate로 선택하고 resource boundary를 확인했다. REASSEMBLE
  전체는 54.8 GiB compressed/약 246 GiB extracted라 현재 storage에서 full extraction을
  금지하고 selective retrieval route를 택했다. 사용자는 public data 우선과 필요한 경우
  소규모 manual annotation을 허용했다. Q8은 `under_review`, Q1은 paused로 유지했다.
  (2026-09-06)

- [x] Q10/Q8의 Stage 5 critical-assumption analysis를 완료했다. 각 assumption에 scientific/
  operational necessity, current evidence, disconfirming observation, cost/duration, cheaper proxy와
  supported/contradicted/ambiguous decision branch를 기록했다. Q10은 matched usable denominator,
  Q8은 task-preserving physical perturbation을 first risk로 정했다. Q10을 resource 확인 전
  provisional Stage 6 priority로 두되 어느 후보도 아직 선택하거나 실행하지 않았다. Disk/GPU
  상태는 read-only로만 확인했고 기존 image/container는 조회하거나 사용하지 않았다.
  (2026-09-05)
- [x] Q10/Q8의 Stage 4 preliminary literature review를 완료했다. Q10은 REASSEMBLE의
  4,551 contact-rich demonstrations, synchronized RGB/state/force와 segment success label로
  public empirical route가 확인됐지만 generic multimodal fusion claim은 FINO-Net 계열이
  점유한다. Q8은 CFNBC와 broad claim이 충돌해 frozen-policy physical-state closed-loop
  return-probability diagnostic으로 경계를 좁혔다. 두 후보 모두 final novelty나 hypothesis로
  확정하지 않았고 외부 artifact를 내려받거나 실행하지 않았다. (2026-09-04)
- [x] Second-round frontier에서 Q6--Q10의 정식 candidate record를 작성하고 기존
  candidate와 Stage 3의 8개 기준으로 비교했다. Q10 Contact-Outcome Observability와
  Q8 Local Recoverability Coverage를 preliminary literature review 우선순위로 정했다.
  어떤 candidate도 hypothesis로 선택하지 않았고 실행도 시작하지 않았다. (2026-09-04)
- [x] 첫 candidate set의 evaluation/diagnosis 편향을 보완하기 위해 Stage 1을 확장했다.
  Temporal execution, constructed-to-natural failure transfer, recoverability-aware data
  coverage, dynamic spatial memory와 contact-rich outcome observability의 recent frontier,
  direct collision pressure와 empirical opportunity를 official source로 정리했다. Q1 실행은
  추가 candidate 비교 전까지 일시 정지했다. (2026-09-04)
- [x] Q1/CD4/CD1을 `docs/buildup.md`의 Entry To Hypothesis Formulation 8개 항목으로
  비교했다. Q1은 8개 조건을 문서상 충족하지만 실행되지 않은 measurement uncertainty
  때문에 `repeat feasibility study`, CD4는 direct collision로 `reformulate`, CD1은
  public multi-action denominator 부재로 `refine`을 선택했다. 어떤 후보도
  `ready_for_hypothesis`로 넘기지 않았다. (2026-09-04)
- [x] CD4/CD1의 Stage 4 preliminary literature review를 완료했다. CD4의 counterfactual
  replay core는 AgenTracer/CAR/AgenticRAG-FP와 direct collision이고, CD1의 broad
  calibration-to-utility framing도 TDQC와 decision-risk/utility-directed work가 이미
  점유함을 확인했다. 각 후보의 official artifact 상태, 최소 차이와 strongest adjacent
  baseline을 기록했으며 외부 artifact는 내려받거나 실행하지 않았다. (2026-09-04)
- [x] Q1의 source/license와 comparable pairwise input을 read-only로 확인했다. ManiSkill3
  `v3.0.1` full commit, public demonstration revision과 두 public PPO checkpoint checksum을
  기록하고, 16-rollout small-subset [protocol v3](buildup/robotics/pilot_studies/q1-predicate-stability/manifest_v3.md)를
  결과 전에 고정했다. 외부 artifact는 내려받거나 실행하지 않았다. (2026-09-04)
- [x] Q1의 public artifact/state-log/evaluator schema를 read-only audit했다. 근거 없는
  추가 hard rule을 폐기하고
  [feasibility protocol v2](buildup/robotics/pilot_studies/q1-predicate-stability/manifest_v2.md)를
  `docs/buildup.md` 기준으로 다시 작성했다. (2026-09-04)
- [x] Robotics에 한정하지 않은 cross-domain context map과 서로 다른 research-gap
  candidate 5개를 도출하고 Stage 3 비교로 CD4/CD1을 preliminary review 대상으로
  정했다. 아직 `ready_for_hypothesis`인 question은 없다. (2026-09-04)

- [x] 현재 workspace의 `AGENTS.md`, `docs/` workflow와 stage 상태를 확인했다. (2026-09-02)
- [x] Robotics 중심의 initial research scope와 high-level constraints를 기록했다. (2026-09-04)
- [x] `PaperReview`와 official sources를 사용해 7개 track의 initial research context와 accessible substrate를 정리했다. (2026-09-04)
- [x] 서로 다른 candidate research question 5개를 작성·비교하고 Q2/Q1을 preliminary-review priority로 정했다. (2026-09-04)
- [x] Local compute/runtime을 확인했다: RTX 5090 32,607 MiB, Docker 29.6.1,
  NVIDIA runtime, 20 CPU와 약 67 GB RAM. 당시 local Isaac image는 목록만 확인했으며,
  이후 사용자 결정에 따라 전부 연구 범위 밖 read-only 자산으로 제외했다. Workload
  GPU smoke test는 실행하지 않았다. (2026-09-04)
- [x] Pre-existing Docker/simulator 자산을 research에서 사용·수정·삭제하지 않고 모든
  environment를 project-specific Dockerfile과 새 이름으로 구성하는 boundary를 고정했다.
  (2026-09-04)
- [x] Q2/Q1의 2024--2026 focused prior audit를 완료했다. Q2는 direct-prior collision으로
  `reformulate` 후 `deferred`, Q1은 exact predicate-stability question을 직접 점유한
  prior를 이번 preliminary review에서 확인하지 못해 `under_review`다. (2026-09-04)
