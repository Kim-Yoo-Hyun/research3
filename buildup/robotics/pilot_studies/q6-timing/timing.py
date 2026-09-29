"""Prospective discrete timing intervention; no wall-clock simulation."""
import hashlib

PROFILES = ["naive", "hard-last", "hard-recent", "hard-fixed", "soft-recent",
            "soft-fixed", "hard-oracle", "hard-buffer"]


def plan(seed, profile, order=None, constant=None):
    assert profile in PROFILES
    phase = hashlib.sha256(f"q6-phase-v1:{seed}".encode()).digest()[0] % 8
    if constant is not None:
        assert constant in range(4)
        delays = [constant] * 64
    else:
        assert order in ("interleaved", "clustered")
        base = [1, 3] * 4 if order == "interleaved" else [1] * 4 + [3] * 4
        delays = (base[phase:] + base[:phase]) * 8
    history, estimates, switches = [2], [], []
    for delay in delays:
        if constant is not None:
            estimate = constant
        elif profile == "hard-last":
            estimate = history[-1]
        elif profile in ("hard-recent", "soft-recent"):
            estimate = max(history[-4:])
        elif profile == "hard-oracle":
            estimate = delay
        else:
            estimate = 3
        estimates.append(estimate)
        switches.append(3 if profile == "hard-buffer" and constant is None else delay)
        history.append(delay)
    return {"seed": seed, "profile": profile, "order": order, "constant": constant,
            "phase": phase, "delays": delays, "estimates": estimates, "switches": switches}


def select(old, new, switch):
    import jax.numpy as jnp
    return jnp.where((jnp.arange(4) < switch)[None, :, None], old[:, :4], new[:, :4])
