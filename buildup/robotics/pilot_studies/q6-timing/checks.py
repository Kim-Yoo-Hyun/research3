"""Independent outcome/event checks; does not import adapter or timing planner."""
import hashlib
import math
import numpy as np


def outcome(done, goal, substeps, finite):
    done, goal = np.asarray(done, bool).reshape(-1), np.asarray(goal, bool).reshape(-1)
    substeps = np.asarray(substeps).reshape(len(done), 2)
    hits = np.flatnonzero(done)
    if not len(hits):
        raise ValueError("MISSING_TERMINAL")
    end = int(hits[0]) + 1
    if not np.asarray(finite, bool).reshape(-1)[:end].all():
        raise ValueError("NONFINITE_SCORED_TRAJECTORY")
    success = bool(goal[end - 1])
    if success != bool(np.any(substeps[end - 1] > 0)):
        raise ValueError("FIRST_TERMINAL_SUBSTEP_DISAGREEMENT")
    return {"terminal_step": end, "success": success,
            "failure_penalized_steps": end if success else 256}


def events(meta, events, commands, old, new, observed, captured):
    assert len(events) == 64
    commands = np.asarray(commands).reshape(64, 4, 6)
    old, new = np.asarray(old).reshape(64, 8, 6), np.asarray(new).reshape(64, 8, 6)
    observed, captured = np.asarray(observed).reshape(256, -1), np.asarray(captured).reshape(64, -1)
    phase = hashlib.sha256(f"q6-phase-v1:{meta['seed']}".encode()).digest()[0] % 8
    assert meta["phase"] == phase
    history = [2]
    for k, event in enumerate(events):
        t = 4 * k
        assert event["request"] == k and event["capture"] == t and event["observation_time"] == t
        if meta["constant"] is not None:
            d = meta["constant"]
        else:
            idx = (k + phase) % 8
            d = (1 if idx % 2 == 0 else 3) if meta["order"] == "interleaved" else (1 if idx < 4 else 3)
        assert event["arrival"] == t + d
        profile = meta["profile"]
        if meta["constant"] is not None:
            estimate = d
        elif profile == "hard-last":
            estimate = history[-1]
        elif profile in ("hard-recent", "soft-recent"):
            estimate = max(history[-4:])
        elif profile == "hard-oracle":
            estimate = d
        else:
            estimate = 3
        assert event["estimate"] == estimate
        b = 3 if profile == "hard-buffer" and meta["constant"] is None else d
        assert event["switch"] == t + b and event["arrival"] <= event["switch"]
        np.testing.assert_array_equal(captured[k], observed[t])
        for j in range(4):
            expected = old[k, j] if t + j < event["switch"] else new[k, j]
            np.testing.assert_array_equal(commands[k, j], expected)
        if k:
            np.testing.assert_array_equal(old[k, :4], new[k - 1, 4:])
            np.testing.assert_array_equal(old[k, 4:], np.zeros((4, 6)))
        history.append(d)
    return True


def step_keys(seed):
    # Separate literal reference traversal of the original evaluator's split stream.
    import jax
    rng = jax.random.key(seed)
    rng, _ = jax.random.split(rng)  # reset
    rng, _ = jax.random.split(rng)  # initial chunk
    answer = []
    for step in range(256):
        if step % 4 == 0:
            rng, _ = jax.random.split(rng)  # new request
        rng, key = jax.random.split(rng)
        answer.append(np.asarray(jax.random.key_data(key)))
    return np.stack(answer)
