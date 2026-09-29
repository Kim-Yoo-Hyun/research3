# Coordinate-Frame Error Propagation

Updated: 2026-09-16 · ID: Q14

## Status

`deferred` — 첫 synthetic study와 [실제 keypoint 관찰](../pilot_studies/q14-frame-errors/real/README.md#results-2026-09-16)을
완료·검증한 뒤 잔여 사례·단순 대안·선행을 비교해 현재 경로의 추가 투자를 보류했다.
[판단·재진입](#investment-decision-and-re-entry)을 따른다. 기존 `refine`은 관찰 당시 판단으로 보존한다.
원래 **action/calibration prediction errors의 statistical dependence** 질문은 보존하되,
실제 관찰은 그중 measurement/calibration 측면의 진단이다. Formal hypothesis 선택은 없다.

## Question and significance

**각 head의 오차 분포를 고정했을 때, 같은 관측에서 예측한 camera-frame action과 camera
rotation의 의존성이 최종 base-frame action 오차를 얼마나 바꾸는가? 그 차이가 단순한
geometric estimator에서도 설명되는가?**

두 component의 정확도를 별도로 높이는 판단이 실제로 실행할 action의 정확도와 어떻게
연결되는지 묻는다. Cancellation·amplification·차이 없음 모두 가능한 결과다. 단순한 공유
좌표변환의 상쇄나 covariance를 고려해야 한다는 일반론을 새 contribution으로 쓰지 않는다.

## Evidence and nearest alternatives

사실: Q14의 작은 learned prediction 관찰은 완료했으며 실제 VLA/robot 행동은 관찰하지 않았다.
[Primary comparison](../related_work/policy-geometry.md#primary-sources-and-what-changed)이
CamVLA의 GT/noise 대조, OC-VLA의 calibrated conversion과 correlated-pose uncertainty의
선행을 소유한다. CamVLA의 공개 결과는 oracle calibration의 우세이며, calibration 교체가
실제 VLA를 해친다는 관찰로 사용하지 않는다. 2026-09-16 official project page는
`Code (Coming Soon)`이며 실행 가능한 joint-output 경로는 미확인이다.

에이전트 추론: 실제 모델의 원래 paired prediction을 봐야 learned dependence를 말할 수 있다.
공개 joint prediction을 기다리는 대신 작은 supervised regression에서 이 측정이 어떤
설명을 구분하는지 볼 수 있다. Classical geometry·direct base-frame regression이 더 간단한
대안이다. 이 proxy의 결과를 CamVLA 성능·실제 로봇 성공률로 옮기지 않는다.

## Analytic control

다음은 실험 결과가 아닌 수식상의 정확한 분해다. Camera-to-base rotation을 R, true camera
translation increment를 a, 같은 관측에서 예측한 출력을 R_hat, a_hat으로 둔다.
Base-frame prediction error는 다음과 같다.

```text
e = R_hat a_hat - R a = G + A
G = (R_hat - R) a
A = R_hat (a_hat - a)
||e||² = ||G||² + ||A||² + 2 GᵀA
||A||² = ||a_hat - a||²
```

같은 true R·a의 반복 관측 안에서 R_hat과 a_hat의 pairing만 바꾸면 각 head의 marginal
sample과 두 norm 항의 평균이 유지된다. 합성 MSE의 변화는 cross term 변화와 정확히 같다.
Mean cross term에는 bias의 결합도 포함되므로 이를 바로 covariance라고 부르지 않는다.
Mean product와 centered cross-covariance 항을 구분해 진단한다.

R을 oracle로 교체하면 G=0이다. 원래 joint MSE와 oracle MSE의 차이는 mean(||G||² + 2GᵀA)다.
따라서 oracle가 항상 좋아진다고도, 상쇄를 깨서 반드시 나빠진다고도 가정하지 않는다.
예를 들어 R_hat=R Q, a_hat=Q⁻¹a를 의도적으로 만들면 합성은 정확하지만 이것은 **만들어 넣은
positive control**일 뿐 learned evidence가 아니다. 실제 학습에서는 이런 출력 오차를 주입하지 않는다.

범위는 free translation vector다. Absolute pose, SE(3) twist, body/spatial delta pose나 Euler
increment의 변환 규칙을 혼용하지 않는다. 첫 관찰은 SO(2) planar proxy만 다룬다.

## First study design

### Observable system

Known unit-scale planar reaching을 사용한다. Base origin O=0, nonzero end-effector 위치 e,
goal 위치 g, camera-to-base rotation R과 image-plane offset t를 생성한다. 입력은 다음 noisy
2D keypoints와 exact proprioception e다.

```text
u_O = t + eta_O
u_E = Rᵀ e + t + eta_E
u_G = Rᵀ g + t + eta_G
input = (u_O, u_E, u_G, e)
targets = camera rotation R, camera action a = Rᵀ(g-e)
base action = g-e
```

Origin/end-effector/goal의 역할은 알려져 있다. 이미지 semantic recognition, depth ambiguity,
language grounding, contact·grasp 안정성은 이 proxy에 없다. Noise는 keypoint 위치에만 넣고
정답 label은 geometry에서 생성한다. World goal g나 R을 추론 입력에 직접 넣지 않는다.
True state와 camera가 같은 반복들끼리만 비교하며, 서로 다른 scene의 action을 섞지 않는다.

### Estimators and comparisons

- Closed-form estimator: angle(e)와 angle(u_E-u_O)의 차이로 rotation을 추정하고,
  a_hat=u_G-u_E로 local action을 얻는다. 공유된 end-effector observation noise만으로
  발생하는 dependence를 보여 주는 가장 단순한 대안이다. Degenerate direction은 표시한다.
- Small supervised two-head MLP: 같은 keypoint/proprio input에서 camera rotation의 sin/cos와
  local action을 예측한다. 두 개의 64-wide hidden layer를 시작안으로 사용한다. Component의
  GT supervision만 쓰며 cancellation을 유도하는 composition loss나 사후 fitting은 넣지 않는다.
  Rotation은 SO(2)로 복원하며 정의 불가능한 출력을 숨기지 않는다.
- Direct base-frame MLP: 같은 input·hidden width·data·update budget에서 g-e를 직접 회귀한다.
  두 출력의 분해가 필요 없는 단순 학습 대안이다. Head 구조가 달라 exact parameter match는 아니다.
- Zero-action prediction은 elementary competence 참고값, exact noiseless conversion은
  구현 sanity control이다. 이 값에 못 미치는 모델의 상쇄를 유용한 robot capability로 포장하지 않는다.

원래 paired prediction, fixed-state empirical product of marginals, oracle R replacement를
비교한다. Product 대조는 한 scene의 모든 rotation prediction과 모든 action prediction을
조합해 각 empirical marginal을 정확히 유지한다. Learned/closed-form estimator 각각에 적용한다.
원래 MSE·두 component 항·cross term·oracle MSE와 direct-policy MSE를 scene별로 기록한다.
Output recombination은 offline diagnostic이며 실제로 가능한 관측 변경이나 closed-loop rollout을
재현하는 개입으로 간주하지 않는다.

### Bounded first attempt

아래 제안은 실행 전에 [study README/config](../pilot_studies/q14-frame-errors/README.md)로 구체화했다.
정확한 architecture·loss·seed·분포·optimizer·command는 study owner가 소유한다.

- Synthetic training pool 약 8,192개; two-head/direct MLP 각 seeds 0,1로 **최대 네 fit**.
  시작 budget은 fit당 batch 128, 1,000 updates다. 첫 결과를 보고 width/seed/loss를 골라 재학습하지 않는다.
- Camera training angles는 예를 들어 −60°~60°, 고정 평가 8개 새 layout 각각에 0°와 90°를
  사용해 총 16개 true scene/camera를 둔다. 후자는 이 proxy에서의 angle extrapolation일 뿐이다.
- Nondegenerate e의 길이를 0.5~1로 두고 action/offset은 bounded unit-scale 좌표로 만든다.
  Train에서 isotropic keypoint noise sigma=0.01을 사용한다. Eval은 noiseless control과 scene당
  같은 sigma의 64개 독립 noise observations다. 각 scene 안의 empirical product 비교에만 쓴다.
- Noise replicas는 64개의 독립 task가 아니다. 성능을 task 수로 부풀리거나 이 작은 설계로
  population CI·VLA generality를 주장하지 않는다. Component distribution identity와 정확한
  squared-error decomposition을 독립적인 수치 계산으로 대조한다.
- 새 project-specific Docker에서 CPU로 준비·실행·해석을 묶는다. 준비/해석 반나절–1일,
  runtime 1시간 이내를 계획값으로 둔다. 큰 VLA·simulator·checkpoint download가 필요하지 않다.
  Source/config/seed/output과 종료 container 정리는 AGENTS.md를 따른다.

이는 처음부터 empirical effect를 보장하는 설계가 아니다. 같은 데이터로 관측한 뒤 더 유익한
수정이 필요하면 그 이유와 비용을 별도로 판단하고 탐색임을 기록한다.

## Interpretation and method sketch

### First observation 2026-09-16

네 fit·16개 scene에서 원래 pairing과 empirical product의 평균 차이는 작고 seed/angle에 따라
부호가 달랐다. 장면별 효과는 남으며, 기하 추정기에서도 8개 layout의 방향에 따라 상쇄·증폭이
나뉜다. 사후 shared-noise 1차 근사가 기하 대조의 16개 부호를 설명했다. 학습 모델의 모든
잔여 오차를 이 근사가 설명한다는 결론은 아니다.

90°에서 joint MLP의 큰 오차는 rotation component가 주로 설명했고 noiseless 입력에서도
남았다. Oracle rotation은 모든 angle/seed의 평균 오차를 낮췄으며 일부 개별 scene은 반대였다.
단순 geometric estimator는 관찰한 모든 angle의 평균에서 MLP들보다 좋았다.
[수치·검증·한계](../pilot_studies/q14-frame-errors/README.md#results-2026-09-16)가 상세를 소유한다.

에이전트 추론: beneficial learned dependence만을 이유로 새 보정 모듈을 만드는 우선순위를
낮춘다. 잠정 수정 초안은 **explicit geometry 기반 예측에 필요한 부분만 학습으로 보정**하는
표현이다. 이 toy input에서는 기하 대안이 강하므로 먼저 어떤 관측 조건에서 그 가정이
깨지는지, 단순 calibration/input 표현 수정으로 해결되는지, 가까운 선행과 무엇이 다른지를
비교한다. 이 초안의 효용·novelty나 추가 학습을 확정하지 않는다. 질문 전체의 반증도 아니다.

### Pre-observation branches

가능한 method 초안은 camera-frame policy를 사용할 때 **개별 head 오차와 joint execution
error를 함께 고려하는 학습/보정**이다. 아직 새 loss나 adapter를 제안한 것은 아니다.

- Dependence 영향이 없으면 이 proxy에서의 dependence 설명을 낮추고 단순 component accuracy를 채택한다.
- Classical estimator에도 같은 현상이 있으면 shared measurement geometry가 먼저 설명한다.
  Generic covariance/cross-term 원리를 새 learning contribution으로 쓰지 않는다.
- Learned model에서 다른 조건별 영향이 남으면 왜 생기는지와 직접 회귀 대안의 cost/error를 보고
  다음 supervision/representation 질문을 정한다. 그때도 실제 VLA에서 일어난다는 증거는 별도다.
- 두 MLP가 기초 회귀를 못 하거나 geometric input이 퇴화하면 baseline/measurement 한계로
  기록한다. Q14 전체의 반증도, 유의해질 때까지 자동 확대할 이유도 아니다.

중요한 것은 per-head metric이나 원래 pairing의 이점만 보고 새로운 representation을 정당화하지
않는 것이다. 실제 VLA로 확장하려면 joint outputs, GT transform, 재관측/paired state와 common
physical-frame action 평가가 필요하다. 그 경로는 후속 투자 대상이며 첫 관찰의 선행조건이 아니다.

## Resource and decision boundary

Synthetic observation generation, 네 작은 fit·기하 대조·검증·해석을 완료했다.
수정 방향의 가치·선행 비교와 아래 real-keypoint 관찰도 완료했다. 자동 추가 fit은 없다.
Execution status와 결과·container 정리는 [study owner](../pilot_studies/q14-frame-errors/README.md)를 따른다.
Existing Isaac/외부 container를 사용하지 않는다.
Full benchmark, 실제 robot motion, CamVLA reproduction, hypothesis/experiment/paper 승격은
선택하지 않았다. Q7의 보류·재진입은 해당 question과 selection record가 소유한다.

## Real keypoint observation

선택·실행일: 2026-09-16. 상태: **completed; verified**. 아래 실행 전 설계를 보존한다.
Synthetic regression의 후속 진단이며
새 residual method 실험이나 실제 VLA의 joint-error 실험이 아니다. 이 구분을 결과에도 유지한다.

### Question and input

실제 RGB keypoint 검출에서 생기는 calibration error는 robust solver만으로 줄어드는가,
아니면 correspondence 누락·오검출 또는 geometry/annotation 조건이 주된 한계인가?
가장 단순한 대안으로 해결되는 사례와 추가 정보가 필요한 사례를 찾는다. 이전 toy의
Gaussian noise 가정을 벗어나 보는 것이 목적이며 새 method의 개선을 보장하지 않는다.

- DREAM official Panda VGG-Q checkpoint 한 개와 Panda-3Cam RealSense split 한 개만 사용한다.
  Source revision·선택한 payload ID·안내 용량은 related-work source record가 소유한다.
- Release의 RGB sample ID를 정렬한 N개에서 `floor(k*(N-1)/23)`, k=0,…,23으로
  **24 frame**을 고른다. N<24면 전부 사용한다. 모델 결과를 보기 전에 ID/파일 hash를 기록하고,
  annotation/이미지 누락도 해당 선택의 실패 행으로 남긴다. 좋은 검출 사례로 교체하지 않는다.
- 공식 checkpoint의 keypoint 순서, resize/crop, original-pixel 좌표 mapping을 그대로 따른다.
  기존 모델의 공개 preprocessing 재현과 dtype/device 등 호환성 수정은 구분해 기록한다.
- Camera intrinsics와 GT 3D/2D annotations를 사용한다. GT 3D는 official offline 평가처럼
  exact articulated geometry로 제공하는 privileged input이다. GT-2D는 아래 oracle 대조에만 쓴다.
  Learned detector에는 RGB만 입력한다. Depth/kinematic noise나 base-frame pose는 검증하지 않는다.
- 고정 camera의 robot configuration 변화 자료다. 24개 독립 task, 새로운 시점 24개 또는
  OOD camera benchmark라고 부르지 않는다. 종속된 video frame의 population CI도 만들지 않는다.

### Comparisons and measurements

모델은 frame당 한 번 추론해 모든 solver가 같은 predicted keypoints를 사용한다.

1. **Official geometry:** EPnP + iterative refinement. Detected/missing의 공식 convention과
   예외 반환을 보존하고 실제 solver에 제공한 point ID를 저장한다.
2. **Robust geometry:** 같은 점에서 RANSAC, official helper의 5-pixel threshold와 고정 RNG seed,
   지원되는 inlier 수일 때 같은 iterative refinement. RANSAC 단독 결과도 저장하여 refinement의
   효과를 구분한다. Iteration/confidence/API version은 실행 전 config로 고정하고 tuning하지 않는다.
   Inlier가 부족하거나 refinement가 실패하면 그 상태를 남기며 oracle 점으로 채우지 않는다.
3. **GT-2D, common points:** 1번에 사용한 동일 ID의 2D 위치만 GT로 교체하고 같은 solver를 쓴다.
   검출 localization의 영향과 point availability를 섞지 않기 위한 privileged control이다.
4. **GT-2D, all in-frame points:** GT projection이 frame 안에 있는 모든 correspondence를 사용한다.
   3번과의 차이는 point support를 보는 단서다. Occlusion label의 대체가 아니며 unavailable
   observations를 runtime에 제공한 것처럼 보고하지 않는다.

GT-2D 교체는 실제로 가능한 방법이 아니다. Common/all 대조의 point set과 in-frame/out-of-frame
구성을 함께 기록하고, 두 solver가 성공한 행만 골라 전체 성능을 계산하지 않는다.
Frame별로 missing/available/inlier 수, keypoint pixel error, used/all-point reprojection error,
pose-error rotation angle와 ADD, solver 성공/실패 상태를 남긴다. ADD는 비교 간 point subset이
바뀌어 유리해지지 않도록 **모든 annotated 3D keypoints에 평가**하고, official retained-point
ADD는 별도 참고값으로 구분한다. 단위는 annotation과 원본 evaluator를 확인해 명시한다.

시각적 case review는 predicted/GT overlay와 원본 RGB를 함께 보고 오검출·누락·투영된 점의
배치·좌표 mapping 문제·불명으로 구분한다. 낮은 reprojection residual을 낮은 pose error의
증명으로 쓰지 않고, 외관만으로 occlusion 원인이나 kinematic truth를 확정하지 않는다.

### Coordinate check and interpretation

[Source coordinate contract](../related_work/policy-geometry.md#public-input-route-and-coordinate-contract)에
따라 평가한 transform Δ의 GT는 identity다. Δ를 camera-to-base calibration 그 자체로 보고하지
않는다. Known K·nondegenerate 3D 점·known rigid transform의 작은 synthetic case로 projection,
transform 방향과 ADD를 검산한다. 좌표계를 바꾼 PnP 결과도 transform composition으로 대조하되
finite solver/RANSAC의 수치 차이와 analytic equivalence를 구분한다. 이 검산은 Docker에서 한다.

관찰 뒤에는 다음과 같이 설명을 수정한다. 아래는 통계적 통과 gate가 아니다.

- Robust geometry로 큰 오류가 줄면 naive least-squares/outlier 설명을 먼저 채택한다.
  새 residual 학습을 정당화하지 않는다.
- 같은 point ID의 GT-2D 교체에서 개선되면 detector localization이 후보 원인이다.
  Learned correspondence/confidence는 DREAM·EPro-PnP 등 기존 방향이므로 남는 사례의 추가
  정보와 action 질문의 연결이 있어야 후속 방법을 구체화한다.
- All-point oracle만 개선되면 support/missingness를 검토한다. Common oracle가 실패하는
  이유를 visibility 하나로 단정하지 않는다.
- Oracle에서도 큰 오류·불안정이 있으면 camera model, geometry conditioning 또는 annotation을
  검토한다. DREAM GT는 depth-based DART 추정치여서 무오류로 보장하지 않는다.
- 유용한 잔여 사례가 없거나 일반 calibration 문제만 남으면 현재 Q14의 추가 투자를 보류한다.
  작은 표본에서 실패를 못 찾았다는 사실은 실제 VLA에서도 문제가 없다는 반증이 아니다.

### Bounded execution

다음 TODO는 선택한 입력 취득·별도 project Docker 준비·24회 추론·solver 대조·검산·해석을
한 묶음으로 진행한다. 준비/해석 약 1일, model inference 1시간 이내는 **계획 추정**이다.
Dataset+weight 안내 용량은 약 428 MB이며 Docker base/dependency 다운로드는 별도다.
CPU를 우선하며 runtime 호환성과 실측 비용은 미확인이다. 느리면 같은 checkpoint/입력의
명시적 GPU 실행을 검토하고 변경을 기록한다. 외부 simulator나 기존 unrelated image는 사용하지 않는다.

Access/dependency 문제가 있으면 같은 경로의 제한된 복구를 먼저 하되 다른 모델·대규모
training set·Panda-Orb·장기 benchmark로 자동 확대하지 않는다. 기술 실패를 연구 질문의
반증으로 쓰지 않는다. 실제 취득/실행 시 recipe, command, output와 recovery 정보는 study
README 및 docs/reproducibility.md에 기록하고 종료 container는 workspace 소유 확인 후 정리한다.

### Outcome and next interpretation

실제 24회 추론·96개 solver 대조를 완료했다. RANSAC은 4개 frame에서 ADD를 낮추고
6개에서 높였으며 14개는 1e-8 이내였다. 001033/001808에서 서로 다른 solver의 큰 회전
오차가 나타났고, 저장된 pose를 all-available-point reprojection MSE로 고르는 사후 대조가
두 실패를 피했다. Mean ADD는 official 0.029509 → 사후 선택 0.016954다(annotation 단위).
새 detector inference/학습 없이 같은 결과에서 계산한 탐색적 대조이며 held-out 개선은 아니다.

GT-in-frame keypoint는 모두 검출됐다. 002583의 두 missing point는 GT도 out-of-frame이며
common/all oracle가 사용하는 점이 같으므로 in-frame missingness 효과는 식별하지 못했다.
GT 2D가 같은 3D/K의 projection과 일치해 oracle ADD가 거의 0인 것은 내부 좌표 일관성의
확인이다. DART reference가 실제 물리 상태와 정확히 같다는 독립 증거가 아니다.

사후 선택에도 세 사례에서 reprojection/ADD 순위가 다르다. 이것만으로 covariance-aware
action method나 learned residual을 정당화하지 않는다. 다음은 이 잔여 사례가 실제
action/calibration 질문과 어떤 구별 가능한 관찰을 만들 수 있는지, 단순 pose estimation
대안과 현재 경로의 투자 보류를 비교하는 것이다. 더 큰 dataset이나 module 학습을
자동 실행하지 않는다. [실행·검산·정정·정리](../pilot_studies/q14-frame-errors/real/README.md)가
수치와 복구 정보를 소유한다.

## Investment decision and re-entry

2026-09-16 판단은 **현재 경로의 추가 투자 보류, `deferred`**다.
[사례·수식·선행 비교](../related_work/policy-geometry.md#q14-action-relevance-review-2026-09-16)가
상세 근거를 소유한다. 큰 solver 실패는 단순 사후 선택으로 피했고, 잔여 ADD/reprojection
순위 차이는 action metric의 순위를 정해 주지 않는다. Free translation vector에서는
calibration translation이 사라지고 rotation axis와 action 방향이 중요하다. 현재 real study에는
learned action/GT action이 없어 이 관계를 실제 행동이나 joint dependence로 확인할 수 없다.

첫 synthetic study의 learned pairing 평균 이점은 일관되지 않았다. 실제 관찰에서도 지금
선택할 task-specific residual target은 얻지 못했다. Image/pose/control uncertainty와
uncertainty-aware PnP는 기존 대안이므로 일반적인 residual·covariance module 또는 solver
확대를 다음 방법으로 선택하지 않는다. Broad Q14의 효과 부재나 learning의 열세 판정은 아니다.

재진입 초안은 작은 reaching 관찰에서 의미가 명시된 camera-frame action/rotation의 paired
출력을 확보해 component-supervised heads, direct action regression, explicit geometry의
설명을 구분하는 것이다. 실제 goal/end-effector 측정 또는 명시적 synthetic construction으로
어떤 새로운 조건을 관찰할지 구체화하면 다시 비교할 수 있다. Full VLA나 positive effect,
최종 novelty는 첫 시도의 필수조건이 아니다. Seed/width/frame 확대나 code 공개만으로
자동 재개하지 않는다. 지금은 Q3, Q4와 관련 CD5, CD2의 작은 관찰을 비교하는 작업으로 옮긴다.
