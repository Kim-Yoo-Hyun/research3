# Q8 Reset Refinement v2

Created: 2026-09-08 after v1 audit 0, before v2 outcomes.

## Trigger

V1 PPO-Joint seed 101 reset + empty action prefix has exactly equal saved physical state but
observation maximum error 1.0 and clipped-action error 1.13089955 relative to fresh nominal reset.
At t=5,10,20,35 its prefix next-state errors are zero. This points to contact-derived observation
history at reset, not failure of physical state initialization. Seed, radius, phase, success
threshold and validity denominator must not be tuned in response.

## Single change and validation

Keep v1 input pins, 312 proposed grid combinations, 50-step horizon, validity predicates,
3 process repetitions, baseline/claim boundary and error tolerance unchanged. Every nominal
start and grid prefix now uses `reset(seed=seed, options={'reconfigure': True})` to recreate the
scene and discard contact caches. V1 direct/state-only restore failures remain recorded.

V2 repeats only the repaired prefix route: both policies, seeds 101--102 at t=0,5,10,20,35,
plus PPO-Joint seeds 103--108 on the same anchors, three checks each = 150 comparisons per
process. Skip the unchanged direct/state-only routes. Also compare a no-injection full nominal
continuation against each admitted zero grid control through t=50, not only the next step.

No learning or prediction fitting. If zero intervention fails under this refinement, do not
extend the grid to recover a positive outcome. Mixed reproducible outcomes are feasibility,
not generalization, density residual or a new recovery principle.

## Public demonstration check

Using the already downloaded motionplanning data, inspect traj_0..2 at t=0,5,20 in the
documented absolute joint-position control mode. Fresh scene + stored state + corresponding
expert action are compared with the saved next state at the same 1e-5 tolerance, three times.
This is 27 one-step comparisons; older recording source remains a mismatch. A mismatch is
reported, not repaired by silently treating PPO rollouts as expert demonstrations.
