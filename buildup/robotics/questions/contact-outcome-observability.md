# Contact-Outcome Observability

Updated: 2026-09-08

## Status

`discontinued` — 2026-09-08 [Stage 7 decision](../../selection.md#q10--discontinue-2026-09-08).

현재 summary-only 연구 경로와 이 formulation의 active 진행을 종료했다. 아래 내용은
원래 question과 단계별 evidence의 provenance다. 더 넓은 RGB-relative observability question이
반증됐다는 뜻은 아니며, 새로운 explanation에 근거한 reformulation은 아직 선택하지 않았다.

## Facts

- Some manipulation outcomes cannot be determined reliably from coarse visual motion alone.
- REASSEMBLE publishes synchronized timestamps, segment-level outcome labels, RGB,
  proprioception and force/torque within one public contact-rich dataset.

## Source Claims

- [FailBench](https://arxiv.org/abs/2609.03611) reports near-saturated detection for visibly
  observable object motion but near-chance performance on contact-intensive assembly.
- RSS 2026 [OopsieVerse](https://robin-lab.cs.utexas.edu/oopsieverse/) turns simulator contact,
  heat and liquid signals into object-centric damage in RoboCasa and BEHAVIOR-1K.
- [ARMBench](https://www.armbench.com/) includes public stow-success and blade-insertion affordance
  datasets in addition to RGB-D manipulation data.
- RSS 2025 [REASSEMBLE](https://tuwien-asl.github.io/REASSEMBLE_page/) reports 4,551
  contact-rich action demonstrations, including 4,035 successful trials, across four actions and
  17 objects with multimodal sensing.
- RA-L 2024 [Multimodal Detection and Identification of Robot Manipulation Failures](https://arxiv.org/abs/2305.04639)
  reports learned RGB/depth/audio fusion for failure detection and classification.

## Agent Inference

The limiting factor may be outcome observability rather than VLM capacity. Minimal robot-state or
contact evidence could close the gap more reliably and cheaply than a larger visual evaluator.

## Research Question Or Suspected Phenomenon

What is the minimum additional signal beyond RGB that makes contact-rich manipulation outcomes
reliably verifiable across task instances?

## Significance

Reliable outcome labels are upstream of benchmark scoring, data filtering, reward learning and
recovery. Identifying signal sufficiency would directly guide dataset and evaluator design.

## Current State Of The Art And Limitation

FailBench exposes evidence-dependent visual failure, FINO-Net establishes learned multimodal
failure detection, and REASSEMBLE supplies a directly relevant public dataset. The remaining
question cannot be generic multimodal fusion. It is a split- and capacity-matched measurement of
the minimum physical signal and temporal window that resolve contact-outcome ambiguity.

## Evaluation Target

- balanced outcome accuracy and calibration across contact-rich task families;
- incremental value per modality and temporal window;
- generalization across object/task splits at matched evaluator capacity.

## Available Data / Code / Evaluator

[REASSEMBLE](https://researchdata.tuwien.ac.at/records/0ewrv-8cb44) provides the strongest
verified route: HDF5 trials, sensor timestamps, Boolean segment success, official train/test
file lists and loader/visualizer code. The main archive is 54.8 GiB compressed and about 246 GiB
uncompressed. Selective ZIP-member retrieval is executable: the fixed-hash 20-file denominator
yielded 524 matched target actions after one official issue exclusion, including 473 successes and
51 failures. Full-population matched counts remain unmeasured.

## Simplest Baseline Or Counterexample

Action-conditioned success prior; terminal gripper/robot-state change; force peak, impulse and
duration thresholds; regularized logistic regression on the same summaries; and a fixed visual
embedding plus RGB-only logistic probe. FINO-Net and the general-purpose visual VLMs in FailBench
are strongest adjacent learned references. If deterministic physical rules saturate, learned
multimodal evaluation is unnecessary.

## Critical Assumptions

### Q10-A. Matched Usable Denominator

- **Status:** `supported for the fixed evaluation population`; label-blind fixed-hash 20-file
  denominator가 고정됐으며 full-population count는 claim하지 않는다.
- **Necessity:** 같은 segment에서 RGB, proprioception, force/torque와 outcome을 결합하지
  못하면 modality increment를 비교할 수 없다.
- **Current evidence:** REASSEMBLE은 sensor별 timestamp, segment start/end와 Boolean success를
  명시하고 4,551 demonstrations를 보고한다. v4의 20개 공개 recording에서 524개 target
  action row가 matched됐고 success 473/failure 51, train failure 40/test failure 11이었다.
- **Disconfirming observation:** join 이후 실패 사례 또는 required modality가 한 action에만
  남거나, official split 한쪽의 class가 사실상 소멸한다.
- **Expected cost/duration:** repository loader와 archive/file index audit 0.5--1일. Full count에
  main archive가 필요하면 download와 indexing 비용은 별도다.
- **Cheaper proxy:** official schema, issue list, `splits.zip`과 archive member listing만으로
  file-level join 가능성과 split coverage를 먼저 확인한다.
- **Decision branch:** supported이면 Q10-B로 진행한다. 한 action만 충분하면 question을 그
  action으로 `refine`한다. 어느 action도 matched failure denominator가 없으면 REASSEMBLE route를
  중단하고 대체 public dataset이 없을 경우 Q10을 `discontinue`한다.

### Q10-B. Outcome-Label Construct Validity

- **Status:** `ambiguous`.
- **Necessity:** `success`가 action별로 재현 가능한 physical outcome을 뜻해야 signal
  sufficiency가 label convention 학습으로 바뀌지 않는다.
- **Current evidence:** official record는 high/low-level segment success와 manual review를
  설명하고 pick miss/drop, insert misalignment, remove jam과 place obstruction 예시를 든다.
- **Disconfirming observation:** 같은 observable terminal state가 annotator/action에 따라
  상반된 label을 받거나, label rule을 official material에서 재구성할 수 없다.
- **Expected cost/duration:** annotation definition 및 소수 official visualization의 blinded
  review 0.5일; 추가 annotation은 이 단계에서 허용하지 않는다.
- **Cheaper proxy:** README/paper의 failure taxonomy와 공개 visualization에서 label과 outcome
  correspondence만 확인한다.
- **Decision branch:** consistent하면 Q10-C로 진행한다. Action-dependent하지만 명시적이면
  action-stratified target으로 `refine`한다. 일관된 target을 만들 수 없으면 dataset route를
  중단한다.

### Q10-C. Dataset-Specific Visual Ambiguity

- **Status:** `ambiguous`; small RGB audit에서 단순 visual cue는 실패했지만 denominator evidence가
  아니다.
- **Necessity:** FailBench의 cross-source result만으로 REASSEMBLE RGB가 불충분하다고 가정할
  수 없다.
- **Current evidence:** FailBench는 contact-intensive assembly의 visual detector degradation을
  보고하지만 REASSEMBLE의 RGB-only outcome ceiling은 보고되지 않았다. v3에서 failure 4개와
  pre-fixed success control 4개를 sparse RGB frame으로 비교했을 때 한 reviewer의 방향 판단
  3개가 모두 틀렸고 나머지 1개는 indistinguishable이었다. 표본, reviewer와 frame sampling이
  너무 작아 정량 결론으로 해석하지 않는다.
- **Disconfirming observation:** action-conditioned RGB-only simple probe가 held-out split에서
  안정적으로 포화하거나, 실패가 RGB에서 명백히 보인다.
- **Expected cost/duration:** small stratified subset의 RGB-only probe와 error review 1일 이내.
- **Cheaper proxy:** success/failure video sample을 동일 temporal window로 가린 소규모
  qualitative audit. 이 결과를 quantitative evidence로 승격하지 않는다.
- **Decision branch:** non-trivial RGB error가 있으면 Q10-D로 진행한다. RGB-only가 포화하면
  outcome-observability phenomenon을 `discontinue`한다. 모든 modality에서 label 자체가
  모호하면 Q10-B로 돌아가 target을 수정한다.

### Q10-D. Incremental Physical Information Beyond Simple Rules

- **Status:** `ambiguous for information beyond RGB`; frozen summary-only probe route has v6
  `NO_USEFUL_SUMMARY_GAIN`.
- **Necessity:** physical channel이 RGB에 없는 information을 제공해야 하며, 그 효과가
  action/session identity나 model capacity 때문이어서는 안 된다.
- **Current evidence:** REASSEMBLE은 action-dependent force/torque pattern을 보여주지만
  success-conditioned modality ablation은 보고하지 않는다. v5 train-selected deterministic rule은
  test macro BA 0.5261로 practical sufficiency를 통과하지 못했고 prior 대비 gain interval은 0을
  포함했다. State depth-1의 descriptive test BA는 0.6976이지만 사후 선택하지 않는다.
  이는 bounded rule-library 결과이며 RGB 대비 physical information의 증거는 아니다.
  V6 state+force logistic probe의 nested macro BA는 0.5791로 동일 fold의 v5 procedure 0.7239보다
  낮았다. Gain interval은 [-0.2299, -0.0347]이며 state/force/state+force 어느 probe도 사전 고정
  useful-gain 조건을 충족하지 못했다. 기존 test의 0.6579는 exploratory로만 해석한다.
- **Disconfirming observation:** force peak, impulse, contact duration 또는 terminal robot-state
  threshold가 RGB error를 해소하지 못하거나, action/session ID만으로 같은 gain이 난다.
- **Expected cost/duration:** deterministic summaries와 regularized logistic probe 1--2일.
- **Cheaper proxy:** label-conditioned one-dimensional distribution와 threshold ROC를 먼저 본다.
- **Decision branch:** simple physical rule이 충분하면 learned evaluator를 금지하고 “simple
  evidence suffices”라는 measurement result의 depth를 Stage 7에서 판단한다. Rule도 probe도
  개선하지 못하면 Q10을 `discontinue`한다. Lightweight probe만 residual을 해소하면 그
  failure cases가 specific method question을 요구하는지 이후 hypothesis 단계에서 판단한다.

### Q10-E. Leakage-Resistant Transfer

- **Status:** `ambiguous`.
- **Necessity:** minimum signal claim이 recording session이나 object/action identity 암기가
  아니라 unseen instance에 유지돼야 한다.
- **Current evidence:** v4의 exact action text 68개가 모두 official train/test 양쪽에
  나타났고, 28개는 combined subset에서 양 outcome을 가진다. Pick/insert/remove는 양 split에
  failure가 있다. 이는 file-split evaluation을 지지하지만 object-disjoint split의 class
  sufficiency는 아직 확인하지 않았다. v5에서 remove test 19개/실패 2개가 한 recording에
  전부 집중된 것을 확인했다. 현재 denominator로 remove의 recording-independent transfer를
  주장할 수 없다. Train-only audit의 failure-bearing recording은 pick/insert/remove 5/9/5개로
  nested CV fitting은 가능하지만 remove의 선택 규칙은 action-bearing recording deletion
  6회 중 5회 바뀌었다. Recording을 session/operator independence로 간주하지 않는다.
- **Disconfirming observation:** random/file split gain이 session-, object- 또는 action-group
  holdout에서 사라진다.
- **Expected cost/duration:** metadata grouping과 alternative split construction 0.5--1일.
- **Cheaper proxy:** official split의 filename/session/action/object contingency table.
- **Decision branch:** group holdout이 가능하면 transfer question을 유지한다. 한 action 안의
  object holdout만 가능하면 claim을 그 population으로 `refine`한다. Group-independent test가
  불가능하면 within-dataset diagnostic으로 제한하고 hypothesis 후보로 승격하지 않는다.

### Q10-F. One-Week Resource Fit

- **Status:** `supported for bounded selective study`; full extraction은 현재 storage에 맞지 않는다.
- **Necessity:** 54.8 GiB archive의 download, decoding과 indexing이 measurement보다 큰 병목이면
  bounded feasibility study가 아니다.
- **Current evidence:** remote ZIP central directory와 per-member byte range가 동작한다. 4개
  HDF5의 542,354,675 compressed bytes를 선택적으로 받아 2,361,432,253 bytes로 추출했고
  CRC/size/SHA-256을 검증했다. 현재 filesystem 여유는 실행 후 약 165 GiB이므로 246 GiB
  전체 압축 해제는 허용하지 않는다.
- **Disconfirming observation:** subset/range access가 없고 compressed, extracted, cache와 output을
  위한 storage 또는 download time을 확보할 수 없다.
- **Expected cost/duration:** remote metadata audit 0.5일; full transfer/decode 시간은 연결과
  storage에 따라 미정이다.
- **Cheaper proxy:** bulk download 전에 repository code, record metadata와 archive access method를
  확인한다.
- **Decision branch:** resource가 충분하면 Stage 6 protocol을 고정한다. 부족하면 Q10을
  `deferred`하고 Q8 또는 다른 public small-artifact candidate와 비교한다.

### Stage 5 Risk Order

```text
Q10-A matched denominator
  -> Q10-B label validity
  -> Q10-F resource fit
  -> Q10-C RGB-only phenomenon
  -> Q10-D physical-signal residual
  -> Q10-E group-held-out transfer
```

앞 단계가 contradicted이면 뒤 단계의 model/probe를 실행하지 않는다. Q10-A/F는 bounded
evaluation에 대해 supported이고 Q10-B/C/D/E는 아직 unresolved다. Stage 6 당시 project
admission을 허용하지 않았으며, 이후 v6의 negative branch에 따른 Stage 7 종료 결정이
현재 상태를 소유한다.

## Feasibility Or Pilot Study

Completed [metadata/schema v1](../pilot_studies/q10-contact-observability/manifest_v1.md),
[bounded HDF5 schema v2](../pilot_studies/q10-contact-observability/manifest_v2.md) and
[small RGB audit v3](../pilot_studies/q10-contact-observability/manifest_v3.md).
[Larger denominator v4](../pilot_studies/q10-contact-observability/manifest_v4.md)는 524 target
rows와 51 failures로 `PASS_DENOMINATOR`였다.
[Deterministic baseline v5](../pilot_studies/q10-contact-observability/README.md)는 eligible 413개
row를 보존해 실행했으며 `UNCERTAIN_RESIDUAL`이었다. Train-only validation audit을 완료해
selection instability를 확인하고 [v6 protocol](../pilot_studies/q10-contact-observability/manifest_v6.md)을
고정해 Docker에서 실행·검증했다. V6 판정은 `NO_USEFUL_SUMMARY_GAIN`이다.
[Stage 7](../../selection.md#q10--discontinue-2026-09-08)에서 summary-only route와 현재 Q10
진행을 종료하고, 더 넓은 학술 질문은 미검증으로 남겼다. v5 test를 반복 사용한 결과는
exploratory로만 해석한다.

### Six-Condition Admission Checkpoint After v6

| condition | status | current evidence / missing evidence |
| --- | --- | --- |
| public executable benchmark and denominator | `PASS` | fixed public 20-file denominator has 524 target rows and 51 failures |
| no 2024--2026 direct-prior collision | `PROVISIONAL` | generic fusion is occupied; exact minimum-signal/window residue still needs final audit |
| survives strongest simple baseline | `NOT_SUPPORTED_FOR_SUMMARY_PROBES` | v6 nested regularized probes fail the pre-fixed gain over v5 rules; no matched RGB comparison |
| one-week kill test | `PASS` | selective range access and small Docker studies completed within one session |
| realistic two-dataset/task/domain path | `PARTIAL` | three REASSEMBLE actions have both classes, but remove test has one recording; second independent substrate is not pinned |
| diagnosis requires a specific method form | `NOT_DERIVED` | current evidence only motivates measurement, not a learned architecture |

Final disposition of this formulation: `discontinued`, not selected for hypothesis formulation.
Gate 1, Gate 2 and Gate 3 remain `NOT_RUN`. 위 checkpoint는 Stage 6 evidence의 기록이며
Stage 7 종료 결정의 기준이나 가설 진입 요건을 새로 정의하지 않는다.

## Preliminary Success Criteria

A minimal signal subset gives stable held-out improvement over RGB-only judgment and the
pre-specified deterministic physical rules do not already saturate the evaluator.

## Expected Deliverable

Outcome-observability curve, modality-cost table, failure cases and an evaluator-design hypothesis.

## Timeline And Milestones

Dataset/schema audit, deterministic baselines, lightweight probe, Stage 7 decision.

## Interpretation Of A Negative Result

If the matched usable denominator is too small, refine to one action/outcome. If simple physical
rules saturate, conclude that evaluator complexity is unnecessary.

## Resource Requirements

Public synchronized dataset, CPU analysis and at most lightweight single-GPU visual inference; no
new data collection or robot motion. The RTX 5090 availability changed during 2026-09-06, but
v1--v6 did not request or mount it.

## Related-Work Overlap

`medium-to-high`; multimodal failure detection is occupied, while reviewed work did not directly
claim nested minimal-signal/window sufficiency on held-out contact-rich outcomes. See the
[preliminary literature review](../related_work/q10-contact-outcome-observability.md).

## User Decision Needed

현재 종료 처리를 위해 추가 사용자 입력은 필요하지 않다. Public data 우선과 필요한 경우의
소규모 manual annotation 허용은 기존 연구의 resource boundary였다. 종료된 Q10에 새로운
annotation, probe 또는 download를 예약하지 않는다. 재검토에는 Stage 7에 명시한 새 근거가 필요하다.
