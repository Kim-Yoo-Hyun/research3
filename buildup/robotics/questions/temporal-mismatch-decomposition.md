# Temporal Mismatch Decomposition

Updated: 2026-09-15 · ID: Q6

## Status

`deferred`; CPU measurement-readiness reached the prespecified terminal-validity stop condition.
Five of 140 readiness records were executed; no held-out pilot or formal hypothesis was opened.
The prospective specification below is preserved. Execution, independent source reconstruction
and the preservation freeze are owned by the [study](../pilot_studies/q6-timing/README.md#verified-outcome-2026-09-15).
[Prior review](../related_work/policy-geometry.md#q6-stage-4-review-2026-09-15) owns literature claims;
[q6_sources.json](../related_work/q6_sources.json) owns exact sources and access limits.
The [source/record reassessment](#source-and-record-reassessment-2026-09-15) keeps Q6 deferred;
Q9 was selected for the next review after an explicit reserve comparison.

## Facts

Official RTC source exposes chunk generation, delay conditioning and execution splice. Two
generation-specific checkpoint payloads and matching RTC levels passed hash and numerical schema
checks in a new CPU Docker. The original evaluator then exhibited a first-terminal success-label
disagreement with its substep event. Full parity, two-level competence and delay-order effects
remain unverified; the current outcome definition cannot pass the declared readiness gate.
Kinetix here is symbolic 2D force control, not a visual-language or 3D manipulation benchmark.

## Source Claims

RTC, REMAC and the unified asynchronous-inference comparison already address stale observations,
chunk inconsistency and delay-aware execution. Armory studies network jitter; classical networked
predictive control studies temporal correlation. Generic delay sensitivity or a new failure taxonomy
is not the contribution. REMAC's final OpenReview PDF remains inaccessible; only its explicit arXiv
version supports this review. Details and primary links are in the prior review above.

## Agent Inference

The delay-order contrast is identifiable as a total effect of a specified execution system.
Actual delay has no independent behavioral effect if both conditioning and effective action-switch
times are fixed and all chunks arrive before those switches. That structural identity replaces
the earlier suggestion that observation age, prefix commitment and arrival can be freely separated.
One small measurement can determine whether a simple conservative execution rule is sufficient,
or whether a learned-policy interaction merits focused diagnosis.

## Research Question Or Suspected Phenomenon

같은 frozen action-chunk policy와 inference cadence에서 동일한 실제 지연값 집합의 순서가
실패율을 바꾸는가? 그 차이가 단순한 causal delay estimator와 보수적인 action 교체 규칙으로
설명되는가? 보수적 규칙이 순서 민감도를 없애더라도 task performance 비용이 큰가?

## Significance

This asks when a delay histogram is an insufficient description of a learned chunk policy's
execution conditions. A surviving effect would require diagnosis before any new method; an
inexpensive sufficient estimator/execution rule would stop the learned-mechanism route.

## Current State Of The Art And Limitation

Nearest priors already cover the main mechanisms. The remaining limited contrast holds the
planned delay multiset and request schedule fixed while changing order, with the estimator and
execution rule explicitly specified. Runtime feasibility and exact novelty are open.

## Evaluation Target

Official first-episode success is primary. Failure-penalized completion time, first termination,
command discontinuity, timing/estimation history and consumed traces are secondary diagnostics.
The target population is stochastic rollouts from two fixed level states and two fixed policies;
seeds are not additional scenes, tasks or training runs.

## Available Data / Code / Evaluator

Use RTC commit `9296f31d62d5bfeb5779dcb2f9bcf71ca37f448b` with Kinetix submodule
`cf7453ea103fa0b77348af1a39f689c658161613`. Both `worlds/l/grasp_easy.json` and
`worlds/l/catcher_v3.json` must come from the RTC repository. The latter is not in this Kinetix tree.
Use their corresponding `bc/31/policies/worlds_l_<level>.pkl` files, with the generation-specific
URLs and listed hashes in q6_sources. Each is 12,290,914 bytes. Names and metadata match the source;
weights subsequently passed payload verification and strict schema loading in the linked study.
No trained REMAC/TT-RTC/VLASH checkpoint is implied.

## Simplest Baseline Or Counterexample

Naive asynchronous execution; last-delay, recent-maximum and fixed-maximum estimators; fixed
conservative switch. Hard/soft inference-time RTC use the same base checkpoint. A known-next-delay
oracle is diagnostic only. A fixed estimate plus fixed switch is a structural negative control.

## Stage 5 assessment 2026-09-15

### Critical assumptions and decisions

| Assumption / necessity | Evidence now | Disconfirmation and branch | Cheapest check / cap |
| --- | --- | --- | --- |
| The timing contrast changes only declared information/execution paths | Source separates splice and conditioning calls, but uses one delay variable | Any future observation, early chunk access or changed request cadence invalidates the adapter | Hand-checked timeline and synthetic Docker assertions before rollouts; one readiness task |
| Fixed timing control removes arrival-order effects | Structural argument below | A trajectory difference with fixed estimate/switch is an implementation or RNG failure, not evidence | Two seeds per level, both trace orders; no statistics needed |
| The official level/checkpoint pair can run without learning | Matching filenames, generation metadata, source/lock and two level JSONs | Loading/parity failure or incompetent baseline: defer this route; do not change checkpoint or drop a level after results | Two CPU Docker working days maximum |
| The outcome label denotes the intended benchmark event | Source exposes first-terminal label and substep aggregation | Nonfinite states, missing terminal, or GoalR disagreement with any-positive substep undermines task interpretation | Explicit terminal fixtures and first-episode audit before pilot; no label patch |
| Any measured effect is more informative than known generic jitter | Priors leave this exact restricted contrast unverified | Simple controls suffice, or exact prior answers the same question: stop the mechanism route | Fixed analysis and stop rules below |

### Event model and causal boundary

Use a discrete **control-step** index `t`; each control step has two physics substeps. Keep
`H=8`, request spacing `s=4`, five flow steps, guidance cap 5, original force interface and
noise SD 0.1. With source `dt=1/60` and frame skip 2, a control step represents 1/30 simulated
second; this is not a measurement of inference wall time.

At request `k`, `t_k=4k`, capture `o_k` and the aligned remainder `B_k` of the previous chunk.
Compute a new chunk `C_k` solely from this capture, its preassigned inference RNG and the selected
estimate `e_k`. The evaluator may calculate it ahead computationally, but it becomes available to
the simulated executor only at `t_k+d_k`. No observation at arrival is supplied to this inference.
For offsets `j=0..3`, execute `B_k[j]` if `j < b_k`, otherwise `C_k[j]`. At `t_k+4`, shift `C_k`
by four and right-pad with zeros exactly as RTC does. Since `d_k <= 3 < s` and `H-s=4`, there is
always enough old-chunk support and no request overlap, queue starvation, dropout or packet disorder.
Those regimes are outside this pilot, not implicitly solved.

For immediate replacement, `b_k=d_k`. For the conservative control, `b_k=3`. Delays are integer
availability offsets; fractional-delay rounding and CPU sleep are not used. Historical estimates
can use only acknowledgments preceding the request. All primary delays arrive before the next
request. Startup follows the source: one common unconditioned initial chunk at the initial state,
computed before the scored clock starts. This idealized warm start is disclosed and shared.

**Structural negative control:** with `e_k=3` and `b_k=3` at every request, changing `d_k` within
`{1,3}` changes only arrival bookkeeping. From equal initial state/chunk and RNG, induction over
requests gives equal observations, generated chunks, commands and outcomes. A residual effect in
this control is impossible under the specified model. This is a design argument, not new control
theory or an empirical finding. It also means a residual "after holding commitment fixed" cannot
be the success criterion. The informative comparison includes the performance cost of that rule.

### Cases, traces and randomization

- Levels: `grasp_easy` and `catcher_v3`, fixed RTC files and directory-31 policies above. These
  are two contrasting source-named tasks, not selected on delayed outcomes. No substitute level.
- Readiness seeds: `0..15`; paired source/adapter parity uses `0,1`. Readiness labels never enter
  the scientific denominator or choose a delay/profile. Held-out seeds: `1000..1063` (64 per level).
- Scored maximum: 256 control steps, 64 requests. Interleaved period is `[1,3,1,3,1,3,1,3]`;
  clustered period is `[1,1,1,1,3,3,3,3]`. Repeat each eight times and rotate each period by the
  same seed-specific phase. Each planned trace has exactly 32 delays of each value, mean 2,
  minimum 1 and maximum 3. A constant-delay run is only a reference, not an equal-histogram pair.
- Phase is `SHA256("q6-phase-v1:<seed>").digest()[0] % 8`. It is a predeclared pseudorandom
  uniform phase, shared across orders/profiles and both levels, independent of the JAX policy
  stream. Record its realized counts; no phase balancing or outcome-based adjustment.
- Allocate the original evaluator's RNG split sequence in advance for the full 256 steps at
  fixed `s=4`, separately for each level and seed. Use `jax.random.key(seed)` as each eval root;
  keep its reset/startup/inference/environment split ordering and `num_evals=1` semantics.
  Vectorization must map over these per-seed roots, rather than replace them with batch-size-
  dependent splits. Inference noise matches by request index; environment noise by control-step
  index, including the original wrapper splits. There is one noisy command per two physics
  substeps. The previous draft's per-physics-substep noise proposal is superseded.
- Retain all 64 seeds, early failures and timeouts. Stop outcome accounting at first terminal;
  replayed states can be computed for original parity but never contribute to the score. Record
  both planned and consumed delay histories. Do not force equal consumed histories by filtering
  episodes or changing termination; differences caused by early termination are part of the effect.

### Fixed profile matrix

Every profile receives both trace orders on both levels. `zeros` means RTC hard prefix **weights**;
`exp` means its soft overlap weights, with attention end `H-s=4`. Both are inference-time guidance
on the base model (`simulated_delay=None`), not exact prefix clamping or trained Soft RTC.

| Profile | Chunk generator / schedule | Estimate supplied at request | Effective switch offset |
| --- | --- | --- | --- |
| naive | `policy.action` | unused | actual `d_k` |
| hard-last | `realtime_action`, `zeros` | most recent completed actual delay; initialize 2 | actual `d_k` |
| hard-recent | `realtime_action`, `zeros` | maximum of last four acknowledgments; queue initially `[2]` | actual `d_k` |
| hard-fixed | `realtime_action`, `zeros` | constant 3 | actual `d_k` |
| soft-recent | `realtime_action`, `exp` | same recent maximum | actual `d_k` |
| soft-fixed | `realtime_action`, `exp` | constant 3 | actual `d_k` |
| hard-oracle | `realtime_action`, `zeros` | actual next `d_k`, privileged diagnostic | actual `d_k` |
| hard-buffer | `realtime_action`, `zeros` | constant 3 | fixed 3 |

This is 2 levels × 64 seeds × 2 orders × 8 profiles = **2,048 rollout records**, at most 524,288
scored control steps. No additional delay, seed, window or guidance-weight sweep. Fixed estimate
3 uses the declared artificial delay bound; deployment under an unknown bound is not implied.
Hard/soft RTC incur VJP computation; equal flow-step count and simulated availability are not
FLOP or wall-clock parity with naive. Record warmed generation latency and call counts separately.
Cross-profile comparisons diagnose this imposed timing system, not real deployment speed.

### Outcomes, uncertainty and continuation

1. Primary outcome: `GoalR` / `returned_episode_solved` at the first `done`, preserving official
   label semantics. Store first-terminal index and label per seed, not just averages. Because
   frame-skip aggregation can disagree, independently retain per-substep rewards/GoalR for audit.
   Nonfinite state/action, no terminal by step 256, or a first-terminal label differing from
   any-positive substep event invalidates task interpretation and stops this route for review.
   Do not silently switch to an easier success predicate or discard the affected seed.
2. Secondary time: success terminal step (`index+1`) if solved, otherwise 256. Report its mean
   over all seeds as **failure-penalized completion time**. Also show raw first-terminal steps and
   success-only time descriptively. A quick failure never counts as fast completion. Preserve
   commanded, noisy and actuator-processed actions for discontinuity/clip diagnostics; no jerk-
   only continuation. These are simulated control times, not deployment or energy measurements.
3. Predeclared primary contrast, separately for each level: success rate(clustered) minus
   success rate(interleaved) for **hard-fixed**. This removes estimator-history changes while
   allowing the actual prefix duration to vary. Use the 64 paired seeds; no pooling of timesteps
   or checkpoints as independent samples. Two-sided exact McNemar tests use discordant pairs,
   with Holm correction across the two levels at family alpha 0.05. With zero discordance, p=1.
4. Report conservative simultaneous confidence intervals: for each level, estimate probabilities
   of positive and negative discordance. For each of the four binomial probabilities (two signs
   × two levels), use a two-sided 98.75% Clopper–Pearson interval. Subtract the negative upper/lower
   bound from the positive lower/upper bound, clipped to [-1,1]. The union bound gives at least
   95% simultaneous coverage for the two differences under independent seed/phase draws. This is
   conservative and may be inconclusive with 64 seeds; it is not a promise of statistical power.
5. A material ordering signal requires absolute difference at least **0.10** (10 percentage
   points) and a Holm-significant test. Same direction on both levels permits focused diagnosis;
   one level alone permits only a task-limited refinement decision. Neither admits a hypothesis
   or a method automatically. If both simultaneous intervals are contained in (-0.10,0.10), stop
   this delay-order route at the declared resolution. Wider intervals without a signal mean
   inconclusive; do not claim equivalence or automatically add seeds.
6. Other profiles, hard-vs-soft interactions and time metrics are exploratory and reported for
   all cases. No minimum-p-value selection across them. `hard-buffer` must produce identical
   trajectories for both orders and is an integrity test. Compare its paired success/time with
   immediate switching in each order to expose its cost; removal of order dependence alone is
   not an improvement. A difference explained by simple estimation or buffering does not justify
   a learned module. Any diagnostic-only signal requires a new prospective design before testing.

The 10-point resolution and 64-seed allocation are planning choices for a bounded pilot, not
thresholds from observed data or top-tier paper sufficiency. Future rigorous scale-up would need
independent policy/task evidence, trained adjacent baselines and deployment timing validation.

### Readiness gates and resource cap

The next task prepares a new Docker and executable freeze; it does not start the 2,048-record
pilot. Before that pilot, require the following in order:

1. Verify the two generation-specific weight payload hashes, source/level hashes, exact loading,
   model dimensions and original loader defaults. Keep all dataset/source mounts read-only.
2. In Docker, synthetic timeline fixtures cover startup, availability before/at switch, under/
   overestimated delay, no future-observation access, RNG independence, first-terminal masking,
   substep-success disagreement, missing terminal and nonfinite values. An independent event
   checker must reject early replacement and mismatched timestamp edits.
3. Original-vs-adapter parity: both levels × naive/hard/soft × constant delays `0,1,2,3` × seeds
   `0,1` × two implementations = 96 rollouts, all with `s=4`. Match pre-terminal commands/states
   within `atol=rtol=1e-6`, and match all terminal labels/times exactly. Use explicit constant delay
   estimates for this parity. The original full-grid CLI is not the entry point. Repeat the
   level/delay-2/hard/seed-0 pair in another process (four additional rollouts).
4. Check hard-buffer order invariance with seeds `0,1` on both levels (eight rollouts); numerical
   trajectories must match exactly apart from arrival metadata. Constant-delay parity alone does
   not establish a causal intervention.
5. Zero-delay naive competence on seeds `0..15` for both levels (32 rollouts): at least 8/16 official
   successes on **each** level, with all validity checks passing. No replacement of a failed level,
   checkpoint search or training. These 140 readiness rollout records are separate from held-out
   outcomes. Estimate pilot cost from readiness timings before opening any held-out results.

Planning caps: at most **two working days (16 hours of preparation effort)**; new CPU container,
Python 3.11, 8 CPUs and 24 GiB RAM, no GPU for the first route. Start from JAX 0.4.35, jaxlib 0.4.34,
Flax 0.10.2, NumPy 1.26.4 and the pinned source lock. Removing CUDA extras is an explicit CPU
projection, not an unchanged full upstream environment; record exact resolved hashes and run
parity before claiming reproduction. One bounded dependency repair is allowed within the cap.
Do not upgrade the numerical stack or switch simulators/checkpoints to rescue a result.

Cap new image/dependency storage at 12 GiB, weights at 25 MiB and study output at 512 MiB (store
state hashes per step and full readiness/failure diagnostics within that cap). Build/pull wall time
cap 2 hours; readiness execution cap 2 hours after build; prospective held-out pilot cap 4 hours.
Each launch must use a background job, timestamped `logs/` files and explicit timeout, with commands
and verification owned by the future study README. If timing extrapolation exceeds the pilot cap,
record infeasibility before evaluation, without cutting the seed/profile denominator. Preserve
partial outputs if a cap is reached; an incomplete run cannot supply the declared inference.

### Required handoff and stop rules

Readiness must create a small study under `pilot_studies/` with its README, Dockerfile, CPU lock,
source/weight/level manifests, measurement config, original-parity route, independent verifier,
output schema and freeze hashing all execution-relevant files. Record image identity, commands,
mounts and device. No host baseline import or numerical rollout is allowed.

Proceed to the held-out pilot only after readiness and freeze verification. If parity, terminal
meaning, source linkage or the resource cap fails, defer this route and retain the failure record.
If a subsequent verified exact prior already answers this controlled question, discontinue it.
Q9 is a reserve requiring a new comparison decision, not an automatic successor.

## Expected Deliverable

A verified timing intervention and bounded paired outcome study, or a documented infeasibility/
stop decision. Readiness produced the latter: independently verified terminal-semantics failure.
This is not a result about the effect of delay order or a completed two-level baseline evaluation.

## Related-Work Overlap

`high`. Actual arrival, estimator input and commitment cannot be treated as unconstrained causal
factors. Delayed-control theory and RTC/REMAC/Armory/unified-comparison findings constrain any future
contribution. The final REMAC version and empirical effect remain unresolved.

## User Decision Needed

None for preserving the failed readiness and a bounded source/record reassessment. Any proposed
new outcome definition requires an explicit prospective design; the stopped pilot cannot resume
by silently changing its label or seed allocation.

## Source and record reassessment 2026-09-15

**Decision:** keep Q6 `deferred`; close the one bounded reassessment and select Q9 for the next
preliminary review on the basis of the [updated comparison](../related_work/policy-geometry.md#q6-reassessment-and-reserve-comparison-2026-09-15).
Q6's event-based reformulation remains a possible re-entry route, not an executed revision.
The original design, labels, five records and preservation freeze remain unchanged. No new
rollout, model import, label rewrite or hypothesis was performed in this reassessment.

### What the failure establishes

**Fact:** the preserved original case has first-terminal rewards `[1, 0]`, official solved=false,
and finite state/actions. The earlier independent engine reconstruction supports the observation;
the current task rechecked artifact identity without rerunning physics. The preceding four records
are two paired seeds, not four independent successes or a two-task competence test.

**Paper definition:** [Kinetix §3.2](https://arxiv.org/html/2410.23208v1#S3.SS2) defines positive
green–blue contact as a terminal reward and green–red contact as negative termination. It does not
require positive contact to persist through the end of the two-substep control interval.
**Source fact:** the pinned `compute_reward_info` gives negative contact precedence within one
physics substep, while `engine_step` reduces reward by maximum and keeps final-substep info.

**Agent inference:** a prospective first-event endpoint is defensible, but changing to
`max(substep_reward)>0` is insufficient. In a hypothetical `[-1,+1]` interval it would count success
after an earlier failure. The following are hand-derived semantic cases, not new simulations:

| Ordered substep rewards | Original final-substep GoalR | Any-positive rule | First nonzero event positive |
| --- | --- | --- | --- |
| `[+1,0]` | false | true | true |
| `[0,+1]` | true | true | true |
| `[-1,+1]` | true | true | false |
| `[+1,-1]` | false | true | true |
| `[-1,0]` | false | false | false |
| `[0,0]` at timeout | false | false | false |

The two mixed-sign rows require an explicit convention: first-event termination treats later
substeps as unscored. A safety-over-the-whole-control-interval endpoint would instead reject any
negative contact. Those are different estimands; no observed rate or preferred numerical result
justifies choosing between them. Simultaneous positive/negative contacts retain the source's
negative precedence. Event labels are tied to source collision semantics, not real grasp stability.

### Compared measurement routes

| Route | What it would answer | Compatibility / cost / disposition |
| --- | --- | --- |
| Keep original solved as the only endpoint | Sensitivity of the released evaluator's label to delay order | Exact source-label compatibility, but unresolved task-event interpretation; low additional scientific information. Do not resume the failed design. |
| First nonzero terminal event, plus original label as an obligatory descriptive endpoint | Whether delay ordering changes goal-versus-failure events, and how much published-label bookkeeping changes the interpretation | Technically plausible without changing pre-event dynamics. One new measurement contract, synthetic mixed-sign fixtures, both-level parity/competence and cost checks are still required. A reasonable reserve, not yet ready. |
| Reduce frame skip, change simulator/level, or retrain | Performance under a different control/distribution setting | Alters the action hold time, observation distribution or policy competence; no longer an endpoint-only repair. Defer at the present scope. |
| Treat the evaluator discrepancy itself as a new method | A source-label inconsistency already demonstrated by one saved case | Useful reproducibility finding, insufficient control/learning contribution. Do not expand into a new method claim. |

A future event-based contract would keep the two levels/checkpoints, timing/RNG rules, eight
profiles and disconfirmation logic prospectively specified. The first nonzero substep defines
event sign and time; timeout without an event is failure; nonfinite values invalidate the case.
It must independently verify that first control-step `done` contains that event and that the
source state/action path is unchanged through it. Later replay states never contribute. Preserve
the official endpoint for every case and a full disagreement table; do not select whichever
endpoint yields significance. If both endpoints receive inferential tests, predeclare the larger
multiple-testing family rather than reuse the old two-test correction.

Preparation is estimated at 1–2 working days within the earlier CPU/storage limits, not measured
readiness or a promised pilot runtime. No event endpoint, fresh seed set or new execution freeze
is adopted here. The old held-out set remains unopened. The observed discrepancy says nothing
about delay-order effect size, generality or nearest-prior novelty.

### Why Q9 now receives the next review

Q6 still offers the cheapest eventual policy execution. However, a public DynaBench release now
provides a concrete, modest-sized route to Q9's within-scene memory question; the earlier 33.5 GB
MemoryVLA route is not its minimum requirement. A bounded audit can test whether budgeted causal
updates can be studied from recorded RGB-D sequences, with task-relevant 3D query labels and no
new robot operation. This reduces a different research uncertainty and directly matches the
Robotics-enabling 3D Vision scope. The comparison does not prove Q9 novelty or readiness.

**Re-entry:** reconsider Q6 only with an explicit event/official-label contract, evidence that its
controlled delay-order contrast has information value relative to the priors and reserve questions,
and a bounded new readiness plan. A label fix alone is not the reason to reopen it. Q9 failure
would trigger a new comparison, not automatic Q6 resumption.
