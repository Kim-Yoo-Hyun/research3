# Q10 Contact-Outcome Observability: Preliminary Literature Review

Updated: 2026-09-06

## Audit Boundary

- Candidate: [Contact-Outcome Observability](../questions/contact-outcome-observability.md)
- Exact question under review: synchronized RGB와 robot-state/contact channel이 있는
  contact-rich action에서, RGB-only 및 deterministic geometry/contact rule보다 held-out
  outcome verification을 안정적으로 개선하는 **최소 추가 signal과 temporal window**는
  무엇인가?
- Search boundary: task-outcome/failure detection, contact-rich multimodal manipulation data와
  official artifact를 공개한 nearest primary work
- 이 review는 final novelty audit, dataset download 또는 feasibility result가 아니다.

## Facts

- REASSEMBLE은 하나의 공개 dataset 안에 RGB, proprioception, force/torque와 segment-level
  success label을 timestamp와 함께 제공한다.
- 공식 집계는 4,551 demonstrations 중 4,035 success이므로 전체 unsuccessful denominator는
  516이다. 이는 official train/test split 내부의 action/object별 class balance를
  보장하지 않는다.
- FailBench는 visual evidence가 불충분한 contact-intensive assembly에서 failure judgment가
  특히 어렵다는 현상을 보고하지만, audit 시점 arXiv page에서 official code/data release
  link를 확인하지 못했다.
- FINO-Net 계열은 RGB/depth/audio fusion으로 manipulation failure detection/classification을
  이미 다룬다. 따라서 “multimodal fusion이 failure detection을 개선한다”는 Q10의 남는
  contribution이 아니다.
- Preliminary review 이후 별도 Stage 6 study에서 official public artifacts를 선택적으로
  내려받아 실행했다. 이 문단의 literature claim과 feasibility result는 섞지 않으며, 실행
  결과는 `pilot_studies/q10-contact-observability/`가 소유한다.

## Nearest Primary Work

### FailBench — 2026

Official source: [paper](https://arxiv.org/abs/2609.03611)

**Exact question and claim.** 14개 public source의 2,197 manipulation attempts에서 13개
VLM-based detector의 cross-source robot-success judgment를 비교한다. Best mean balanced
accuracy는 0.77이며, observable object motion에서는 거의 포화되지만 contact-intensive
assembly에서는 0.60 미만으로 떨어진다고 보고한다. Outcome-relevant crop은 top detector를
2.4 percentage points 개선한다.

**Boundary.** Instruction과 visual observation으로 binary outcome을 판정하는 benchmark다.
동일 episode의 proprioception, force/torque 또는 contact channel을 추가해 최소 sufficiency를
측정하지 않는다.

**Artifact status.** Paper가 대상으로 삼은 source들은 public이라고 명시하지만, 2026-09-04
arXiv page에는 FailBench 자체의 official code/data/evaluator link가 없다. 따라서 Q10의 첫
실행 substrate로 간주하지 않는다.

**Minimum difference.** Q10은 더 큰 VLM이나 visual prompt를 비교하는 것이 아니라 같은
contact-rich episodes에서 physical channel 하나와 짧은 window가 주는 incremental value를
capacity- and split-matched하게 측정한다.

### REASSEMBLE — RSS 2025

Official sources: [project](https://tuwien-asl.github.io/REASSEMBLE_page/),
[dataset](https://researchdata.tuwien.ac.at/records/0ewrv-8cb44),
[code](https://github.com/TUWIEN-ASL/REASSEMBLE)

**Exact question and claim.** NIST Assembly Task Board 1에서 17개 object와 pick, insert,
remove, place의 네 action을 수집한 contact-rich multimodal dataset이다. Multi-view RGB,
event, audio, robot proprioception과 wrist force/torque를 native frequency로 저장하며,
각 sensor timestamp와 hierarchical action segment의 Boolean success label을 제공한다.
Paper는 temporal action segmentation, DMP execution과 ConditionNET-based execution-monitoring
demonstration을 포함한다.

**Boundary.** Dataset와 representative downstream experiment가 contribution이다. Official
description에는 nested modality set의 outcome classification, minimum sufficient sensor,
sensor-cost curve 또는 object/action-held-out sufficiency comparison이 없다.

**Artifact status.** Public `data.zip`은 54.8 GiB이며 MD5는
`812103a652ca9201e87a3bcecfee4ef3`이다. `poses.zip`은 87.3 KiB, `splits.zip`은 1.1 KiB이고
official loader/visualizer code가 있다. 공식 page는 일부 camera, force/torque와 pose가
누락된 recording을 열거한다. 이후 Stage 6 audit에서 remote ZIP-member range retrieval이
가능함을 확인했으며, 4개 HDF5 subset을 CRC/size/SHA-256 검증해 받았다.

**Minimum difference.** Q10은 REASSEMBLE을 새 dataset contribution으로 재포장하지 않는다.
Success label을 target으로 고정하고 nested signal sets와 simple rules를 비교해 어느 physical
evidence가 visual ambiguity를 실제로 해소하는지를 묻는다.

### Multimodal Detection and Identification of Robot Manipulation Failures — RA-L 2024

Official sources: [paper](https://arxiv.org/abs/2305.04639),
[code and FAILURE dataset](https://github.com/ardai/fino-net)

**Exact question and claim.** FINO-Net이라는 deep multimodal fusion classifier로 tabletop
manipulation 및 post-manipulation failure를 detection/classification한다. Extended FAILURE
dataset에 99개 새 multimodal recording을 추가하고 detection F1 0.87, classification F1
0.80을 보고한다.

**Boundary.** RGB, depth와 audio를 learned fusion해 failure type을 식별하는 문제다. 최소
추가 modality, force/proprioceptive sufficiency, modality acquisition cost 또는 contact-rich
assembly action/object holdout을 연구 질문으로 두지 않는다.

**Artifact status.** MIT-licensed code와 annotation이 있고, repository는 FAILURE dataset을
약 9.5 GB compressed, 약 20 GB decompressed로 안내한다. 실제 download integrity와 full
reproduction은 이번 review에서 검증하지 않았다.

**Minimum difference.** FINO-Net은 Q10의 strongest adjacent learned baseline이다. Q10이
살아남으려면 fusion architecture 성능이 아니라 deterministic/simple probe를 포함한
**minimal evidence sufficiency**와 held-out transfer가 중심이어야 한다.

## Baseline Boundary

### Simplest baselines

1. Action-conditioned success prior / majority prediction
2. Terminal end-effector, gripper와 joint-state change를 사용한 fixed threshold rule
3. Force peak, impulse/integral와 contact-duration threshold
4. 같은 summary feature를 사용한 regularized logistic regression
5. Fixed visual embedding 위의 RGB-only logistic probe

각 baseline은 같은 segment, split과 temporal window를 사용해야 한다. REASSEMBLE에는
continuous object pose가 없으므로 “terminal object geometry oracle”를 public input으로
가정하지 않는다.

### Strongest adjacent baselines

- FailBench가 비교한 general-purpose visual VLM detector: RGB-only outcome judgment의 current
  reference지만 official corpus/evaluator release 전에는 직접 reproduction 대상이 아니다.
- FINO-Net: public code/data가 있는 learned multimodal failure detector. Q10 probe와 task,
  modality 및 split이 다르므로 reported number를 직접 비교하지 않고 method-family reference로
  사용한다.

## Candidate Residue

Reviewed sources에서 다음 exact combination의 direct owner는 확인하지 못했다.

> 같은 contact-rich execution과 official outcome label에서 nested physical signal sets를
> 비교하고, simple rules 및 capacity-matched probes 뒤에도 남는 held-out value로 최소
> observable signal/window를 식별한다.

이는 final novelty claim이 아니다. “Multimodality helps,” “failure detection,” “contact-rich
dataset” 중 하나로 claim을 넓히면 reviewed prior와 충돌한다.

## Empirical Uncertainty Before Novelty

1. Segment-level `success`가 네 action에서 동일한 semantic reliability를 갖는가?
2. Official split에 failure가 충분하며 action/object별로 non-degenerate한가?
3. Missing-sensor recording을 제거한 뒤에도 RGB + force/torque + proprioception의 matched
   denominator가 충분한가?
4. Timestamp alignment와 encoded video decoding이 1주 내 low-cost study를 허용하는가?
5. Robot-state 또는 force threshold만으로 이미 포화되는가?
6. Improvement가 object/action identity나 recording-session leakage가 아니라 unseen
   object/action transfer에서도 남는가?

## Preliminary Decision

- Related-work overlap: `medium-to-high`
- Exact collision in reviewed sources: `not found`
- Public empirical route: `credible`, led by REASSEMBLE
- Final novelty: `NOT_ESTABLISHED`
- Candidate status: `under_review`

Q10은 Stage 5로 진행할 가치가 있다. 가장 싼 다음 판단은 full archive를 받기 전에 official
split, label distribution, missing-sensor denominator와 loader path가 위 uncertainty를 측정할
수 있는지 명시하는 assumption/decision tree다.

## User Decision Needed

없음. 54.8 GiB archive download 또는 code execution 전에는 storage/time boundary를 별도로
확인한다.
