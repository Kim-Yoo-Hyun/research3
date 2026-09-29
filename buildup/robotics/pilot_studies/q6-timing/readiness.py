"""Ordered readiness gates, never held-out pilot evaluation. Docker only."""
import functools
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

sys.path.insert(0, "/source/jaxued/src")
import jax
import jax.numpy as jnp
import numpy as np
import eval_flow
import schema
from adapter import make_runner, keys
from instrument import diagnostic_env, original_eval
from timing import plan
import checks

OUT = Path("/output")
START = time.monotonic()
REPEAT = "--repeat" in sys.argv
RECORDS = []


def write(name, data):
    path = OUT / name
    assert not path.exists(), f"Refusing to overwrite {path}"
    path.write_text(json.dumps(data, indent=2, default=str) + "\n")


def store_trace(identifier, meta, trace, elapsed, request_data=None):
    dones, states, info = jax.device_get(trace)
    arrays = {"done": np.asarray(dones), **{k: np.asarray(v) for k, v in info.items() if v is not None}}
    raw = states.env_state.env_state
    paths, _ = jax.tree_util.tree_flatten_with_path(raw)
    state_keys = []
    for index, (path, value) in enumerate(paths):
        key = f"state_{index:03d}"
        state_keys.append({"key": key, "path": jax.tree_util.keystr(path)})
        arrays[key] = np.asarray(value)
    hashes = []
    finite = np.asarray(info["q6_post_finite"]).reshape(256).copy()
    for value in arrays.values():
        if value.shape and value.shape[0] == 256 and np.issubdtype(value.dtype, np.number):
            finite &= np.isfinite(value).reshape(256, -1).all(axis=1)
    for t in range(256):
        h = hashlib.sha256()
        for row in state_keys:
            a = np.ascontiguousarray(arrays[row["key"]][t])
            h.update(str(a.dtype).encode()); h.update(str(a.shape).encode()); h.update(a.tobytes())
        hashes.append(h.hexdigest())
    arrays["scored_finite"] = finite
    rawkeys = np.asarray(info["q6_step_key"]).reshape(256, 2)
    np.testing.assert_array_equal(rawkeys, checks.step_keys(meta["seed"]))
    # Independently reconstruct the source wrappers' one command-noise draw per control step.
    def noisy(rawkey, command):
        batch_key = jax.random.split(jax.random.wrap_key_data(rawkey), 1)[0]
        _, step_key = jax.random.split(batch_key)
        noise_key, _ = jax.random.split(step_key)
        return command + jax.random.normal(noise_key, command.shape) * 0.1
    arrays["noisy_command"] = np.asarray(jax.vmap(noisy)(jnp.asarray(rawkeys),
        jnp.asarray(info["q6_command"]).reshape(256, 6)))
    ev = None
    if request_data is not None:
        (observed, old, new), initial = jax.device_get(request_data)
        arrays.update(captured_observation=observed, old_chunk=old, new_chunk=new, initial_chunk=initial)
        ev = [{"request": k, "capture": 4*k, "observation_time": 4*k,
               "arrival": 4*k+meta["delays"][k], "switch": 4*k+meta["switches"][k],
               "estimate": meta["estimates"][k]} for k in range(64)]
        checks.events(meta, ev, info["q6_command"], old, new, info["q6_obs"], observed)
        np.testing.assert_array_equal(old[0], initial)
    record = {"id": identifier, **meta, "elapsed_seconds_including_first_compile": elapsed,
              "generation_calls": 65, "flow_steps_per_call": 5, "state_keys": state_keys,
              "state_sha256": hashes, "events": ev, "validity": "unchecked"}
    try:
        record.update(checks.outcome(dones, info["returned_episode_solved"], info["q6_substep_reward"], finite))
        end = record["terminal_step"]
        assert int(np.asarray(info["returned_episode_lengths"])[end - 1, 0]) == end
        assert np.array_equal(np.asarray(info["q6_substep_goal"]), np.asarray(info["q6_substep_reward"]) > 0)
        record.update(validity="PASS", consumed_delays=meta["delays"][:(end + 3)//4])
    except (AssertionError, ValueError) as exc:
        record.update(validity="FAIL", failure=str(exc))
    folder = OUT / "records"
    folder.mkdir(exist_ok=True)
    path = folder / (identifier + ".npz")
    assert not path.exists()
    np.savez_compressed(path, **arrays)
    record.update(npz=str(path.relative_to(OUT)), bytes=path.stat().st_size,
                  sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    write("records/" + identifier + ".json", record)
    RECORDS.append(record)
    print(json.dumps({k: record[k] for k in ("id", "validity", "elapsed_seconds_including_first_compile")}
                     | {k: record[k] for k in ("terminal_step", "success", "failure") if k in record}), flush=True)
    if record["validity"] != "PASS":
        raise ValueError(f"TERMINAL_GATE:{identifier}:{record['failure']}")
    if sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) > 512*1024**2:
        raise ValueError("OUTPUT_CAP_EXCEEDED")
    return record, arrays


def compare(a, b, exact=False):
    ra, xa = a; rb, xb = b
    for key in ("terminal_step", "success", "failure_penalized_steps"):
        assert ra[key] == rb[key], f"{key}: {ra['id']} / {rb['id']}"
    n = ra["terminal_step"]
    keys_to_check = [x["key"] for x in ra["state_keys"]] + ["q6_command", "q6_obs", "q6_processed", "noisy_command"]
    max_abs = 0.
    for key in keys_to_check:
        x, y = xa[key][:n], xb[key][:n]
        if exact or not np.issubdtype(x.dtype, np.inexact):
            np.testing.assert_array_equal(x, y, err_msg=f"{key}: {ra['id']} / {rb['id']}")
        else:
            np.testing.assert_allclose(x, y, atol=1e-6, rtol=1e-6,
                                       err_msg=f"{key}: {ra['id']} / {rb['id']}")
            max_abs = max(max_abs, float(np.max(np.abs(x-y))) if x.size else 0.)
    return {"a": ra["id"], "b": rb["id"], "status": "PASS", "exact": exact, "max_abs": max_abs}


def main():
    assert json.loads((OUT / "preflight.json").read_text())["status"] == "SYNTHETIC_PASS"
    names, levels, policies, env, params, static, _ = schema.load()
    env = diagnostic_env(env)
    original = original_eval()
    compiled_original, compiled_adapter = {}, {}
    comparisons = []

    def run(name, profile, delay, seed, implementation, group="parity", order=None):
        assert seed in range(16), "Held-out seeds cannot be executed by this entry point"
        meta = plan(seed, profile, order=order, constant=delay)
        meta.update(level=name, implementation=implementation, group=group, process_repeat=REPEAT)
        identifier = f"{group}_{name}_{profile}_{delay if delay is not None else order}_{seed}_{implementation}"
        level = jax.tree.map(lambda x: x[names.index(name)], levels)
        policy = policies[name]
        if implementation == "original":
            cachekey = (name, profile, delay)
            if cachekey not in compiled_original:
                method = eval_flow.NaiveMethodConfig() if profile == "naive" else eval_flow.RealtimeMethodConfig(
                    prefix_attention_schedule="exp" if profile.startswith("soft") else "zeros")
                config = eval_flow.EvalConfig(num_evals=1, execute_horizon=4, inference_delay=delay, method=method)
                compiled_original[cachekey] = jax.jit(functools.partial(original, config, env,
                    level=level, policy=policy, env_params=params, static_env_params=static))
            started = time.monotonic()
            summary, trace = jax.block_until_ready(compiled_original[cachekey](jax.random.key(seed)))
            elapsed = time.monotonic() - started
            record = store_trace(identifier, meta, trace, elapsed)
            assert bool(summary["returned_episode_solved"]) == record[0]["success"]
            return record
        cachekey = (name, profile)
        if cachekey not in compiled_adapter:
            compiled_adapter[cachekey] = make_runner(env, params, policy, profile)
        rng_keys = keys(seed)
        started = time.monotonic()
        trace, requests, initial = jax.block_until_ready(compiled_adapter[cachekey](level, rng_keys,
            jnp.asarray(meta["estimates"]), jnp.asarray(meta["switches"])))
        elapsed = time.monotonic() - started
        return store_trace(identifier, meta, trace, elapsed, (requests, initial))

    if REPEAT:
        for name in names:
            a = run(name, "hard-fixed", 2, 0, "original", "repeat")
            b = run(name, "hard-fixed", 2, 0, "adapter", "repeat")
            comparisons.append(compare(a, b))
            for row in (a, b):
                earlier = json.loads((OUT / "records" / (row[0]["id"].replace("repeat_", "parity_", 1) + ".json")).read_text())
                assert row[0]["state_sha256"] == earlier["state_sha256"]
        write("repeat.json", {"status": "REPEAT_PASS", "comparisons": comparisons, "records": len(RECORDS)})
        return

    for name in names:
        for profile in ("naive", "hard-fixed", "soft-fixed"):
            for delay in range(4):
                for seed in (0, 1):
                    a = run(name, profile, delay, seed, "original")
                    b = run(name, profile, delay, seed, "adapter")
                    comparisons.append(compare(a, b))
    write("parity.json", {"status": "PARITY_PASS", "comparisons": comparisons, "records": len(RECORDS)})
    subprocess.run([sys.executable, "-B", "-u", __file__, "--repeat"], check=True)
    for name in names:
        for seed in (0, 1):
            a = run(name, "hard-buffer", None, seed, "adapter", "buffer", "interleaved")
            b = run(name, "hard-buffer", None, seed, "adapter", "buffer", "clustered")
            comparisons.append(compare(a, b, exact=True))
    competence = {}
    for name in names:
        rows = [run(name, "naive", 0, seed, "adapter", "competence")[0] for seed in range(16)]
        competence[name] = sum(x["success"] for x in rows)
    assert all(x >= 8 for x in competence.values()), f"COMPETENCE_GATE:{competence}"
    # Conservative per-profile observed worst warmed time; pilot compilation reserve is explicit.
    adapter_times = [r["elapsed_seconds_including_first_compile"] for r in RECORDS
                     if r["implementation"] == "adapter" and r["seed"] == 1]
    prediction = max(adapter_times)*2048 + 900
    if prediction > 4*3600:
        raise ValueError(f"PILOT_COST_CAP:{prediction}")
    write("readiness.json", {"status": "READINESS_PASS", "main_records": len(RECORDS), "repeat_records": 4,
          "comparisons": comparisons, "competence": competence, "pilot_upper_seconds": prediction,
          "wall_seconds": time.monotonic() - START, "heldout_records_executed": 0})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        failure = {"status": "DEFER_READINESS", "error": str(exc), "type": type(exc).__name__,
                   "completed_record_ids": [x["id"] for x in RECORDS],
                   "wall_seconds": time.monotonic() - START, "heldout_records_executed": 0,
                   "traceback": traceback.format_exc()}
        write("repeat_failure.json" if REPEAT else "failure.json", failure)
        print(json.dumps(failure), flush=True)
        raise
