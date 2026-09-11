# Q8 CPU Feasibility Fixture v1

Created: 2026-09-08, before perturbation outcomes.

## Purpose and inputs

Test state intervention validity and repeatability, not predictive superiority or data coverage.
Pinned ManiSkill `a4a4f9272ad64b1564035874b605ceb687b63ed8`, PickCube-v1 Panda, state
observation, PhysX CPU, Torch CPU, official PPO-Joint checkpoint. PPO-EE is a separately
reported interface cross-check. Both use unchanged official Agent AST and clipped deterministic
actions. Seed grid 101--108. Horizon 50 control steps from reset.

Motionplanning demo schema/replay is checked separately: different source commit and absolute
joint-position actions cannot be relabeled as PPO training data or imitation loss targets.

## Restore checks

For both control modes, seeds 101 and 102, save nominal states at t=0,5,10,20,35.
Compare original next action/observation/state with:

1. direct `set_state_dict` after completing the original rollout;
2. reset + `set_state_dict` + explicit controller state + elapsed step;
3. reset with original seed + replay saved action prefix.

Three repetitions each, maximum absolute state/observation/action difference, and success label
agreement. Record continuous errors even when labels agree. Tolerance: `atol=1e-5, rtol=0`;
also report raw differences and failures rather than redefining tolerance. Do not attribute
intervention effects using a restore route that fails its zero-perturbation control.

## Perturbation grid

PPO-Joint only; seeds 101--108, anchors t=0,5,10. Each anchor has 13 proposed variants:
zero, ±x and ±y at radii 0.01,0.03,0.06 m. Same fixed world goal, cube orientation/velocity,
robot configuration, identity and episode clock. Continue to original t=50; record success_once
and success_at_end plus geometric and velocity constituents at every step. Exclude t=0 success
from future success_once so injection instant cannot trivially count as recovery.

Outcome-blind validity: cube center stays in official spawn xy square [-0.1,0.1]^2; cube remains
table-supported (bottom within 1 mm of table and tilt <0.01 rad); no grasp; cube linear speed
<0.02 m/s and angular speed <0.1 rad/s; robot qpos within joint limits; cube collision-mesh AABB
separated from every robot-link collision-mesh AABB by >1 mm along at least one axis. This is
a conservative sufficient no-robot-overlap check, not a complete solvability proof. Table contact
is intentional. No trajectory phase/grasp perturbation beyond this population is admitted.
For reset states, membership in official initializer support gives the strongest semantics;
later pre-contact states have only geometric validity, not guaranteed reachability.

Use reset + fixed action prefix for perturbation anchors, conditional on passing its zero control.
Three independent container processes repeat the complete grid. Deterministic repetitions do
not increase statistical sample size: maximum 312 proposed seed/anchor/variant combinations.
Invalid proposals remain in output with reasons. No post-outcome radius/seed/phase expansion.

## Interpretation

- Restore or nominal competence failure: report unavailable/refine; not evidence against Q8.
- All valid nonzero variants have one outcome: no discrimination on this specified route.
- Mixed outcomes reproducible across processes: feasibility only. Nominal failures, validity
  exclusions and seed-level counts are reported separately.
- No gain claim from scalar score versus the same success frequency. A later prediction study
  needs both a held-out state-group mapping and an equal-cost empirical-success baseline.
- No hypothesis promotion, VLA claim, true demonstration-density claim or backend equivalence.

## Candidate prediction design audit

Let Y_H(s,delta) be official success within fixed remaining horizon and valid perturbation law q.
R_q(s)=E_q[Y_H(s,delta)] is finite-horizon success probability under q. If score and target use q,
disjoint random draws remove direct label leakage but estimate the same conditional quantity.
This is calibration/repeatability, not evidence of a new predictive construct.

For a later refined question, estimate a direction/radius profile on anchor states of development
episodes; fit a score-prediction map using development groups only; evaluate on completely new
episode groups and held-out perturbation directions with no outcome fitting there. Compare
geometric state features, offline action drift, empirical success using the identical rollout
budget, and outcome classifiers trained on the same permitted observations/labels. A scalar
recoverability equal to the empirical success baseline is an identity, not an ablation win.
Return-to-demonstration requires a separate fixed predicate and needs a reason to predict task
success; official success alone does not certify return, controllability or a basin of attraction.
