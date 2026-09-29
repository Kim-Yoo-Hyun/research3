"""Docker fixtures that exercise causal timing and reject invalid accounting."""
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0, "/source/jaxued/src")
import jax
import numpy as np
from adapter import keys
from timing import plan, select, PROFILES
import checks


def rejected(call):
    try:
        call()
    except (AssertionError, ValueError):
        return
    raise AssertionError("mutation accepted")


def main():
    assert json.loads(Path("/output/schema.json").read_text())["status"] == "SOURCE_SCHEMA_PASS"
    results = []
    for profile in PROFILES:
        for order in ("interleaved", "clustered"):
            meta = plan(0, profile, order)
            old, new, commands, events = [], [], [], []
            buffer = np.full((1, 8, 6), -1., np.float32)  # distinct common startup
            observed = np.repeat(np.arange(256)[:, None], 3, axis=1)
            for k in range(64):
                generated = np.arange(k * 48, (k + 1) * 48, dtype=np.float32).reshape(1, 8, 6)
                old.append(buffer.copy()); new.append(generated)
                commands.append(np.asarray(select(buffer, generated, meta["switches"][k])))
                events.append({"request": k, "capture": 4*k, "observation_time": 4*k,
                               "arrival": 4*k + meta["delays"][k],
                               "switch": 4*k + meta["switches"][k], "estimate": meta["estimates"][k]})
                buffer = np.concatenate((generated[:, 4:], np.zeros((1, 4, 6))), axis=1)
            # Event checker uses arbitrary observation width, but physical action width is fixed at six.
            def check(ev=events, cmd=commands, obs=observed[::4]):
                return checks.events(meta, ev, cmd, old, new, observed, obs)
            check()
            for field, value in [("switch", events[0]["arrival"] - 1), ("arrival", 99),
                                 ("observation_time", 1), ("estimate", 99)]:
                mutation = copy.deepcopy(events); mutation[0][field] = value
                rejected(lambda: check(ev=mutation))
            mutation = np.asarray(commands).copy(); mutation[0, 0, 0] = new[0][0, 0]
            rejected(lambda: check(cmd=mutation))
            rejected(lambda: check(obs=observed[1::4]))
            results.append(profile + ":" + order)
    # Separate RNG allocation agrees regardless of termination or arrival sequence.
    for seed in (0, 1):
        envkeys = keys(seed)[3]
        np.testing.assert_array_equal(np.asarray(jax.random.key_data(envkeys)).reshape(256, 2), checks.step_keys(seed))
    good = checks.outcome([False, True, True], [False, True, False], [[0, 0], [1, 1], [-1, -1]], [True]*3)
    assert good == {"terminal_step": 2, "success": True, "failure_penalized_steps": 2}
    assert checks.outcome([True], [False], [[-1, 0]], [True])["failure_penalized_steps"] == 256
    rejected(lambda: checks.outcome([True], [False], [[1, 0]], [True]))
    rejected(lambda: checks.outcome([False], [False], [[0, 0]], [True]))
    rejected(lambda: checks.outcome([True], [True], [[1, 1]], [False]))
    # No post-terminal replay contributes to validity or outcome.
    checks.outcome([True, False], [True, False], [[1, 1], [0, 0]], [True, False])
    report = {"status": "SYNTHETIC_PASS", "timing_profiles_orders": results,
              "timing_mutations_rejected": 6*len(results), "rng_seeds": [0, 1],
              "terminal_fixtures": 6, "scope": "synthetic controls only; no physical rollouts"}
    Path("/output/preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
