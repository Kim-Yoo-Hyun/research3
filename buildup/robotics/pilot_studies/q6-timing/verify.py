"""Independent saved-artifact audit and source-only reconstruction of a failed step.

No adapter, planner, instrumentation, readiness runner or their outcome helpers are imported.
No new rollout/seed is executed. Original physics is applied only to the saved terminal state.
"""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, "/source/jaxued/src")
import jax
import jax.numpy as jnp
import numpy as np
import kinetix.environment.env as kenv
from kinetix.environment.env_state import EnvParams, StaticEnvParams
from kinetix.util.saving import load_from_json_file
import train_expert

OUT = Path("/output")
STUDY = Path("/study")


def main():
    frozen = json.loads((STUDY / "pre_execution.json").read_text())
    for row in frozen["files"]:
        data = (STUDY / row["path"]).read_bytes()
        assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
    source = json.loads((STUDY / "assets.json").read_text())
    source_files = 0
    for repo in source["repositories"]:
        for row in repo["files"]:
            data = (Path("/source") / repo["name"] / row["path"]).read_bytes()
            assert hashlib.sha256(data).hexdigest() == row["sha256"] and len(data) == row["bytes"]
            source_files += 1
    for row in source["weights"]:
        data = Path(f"/data/policies/{row['level']}.pkl").read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"] and len(data) == row["bytes"]
    rows = [json.loads(p.read_text()) for p in sorted((OUT / "records").glob("*.json"))]
    assert len(rows) == 5, "This audit is fixed to the stopped run's five preserved records"
    failure = json.loads((OUT / "failure.json").read_text())
    assert set(failure["completed_record_ids"]) == {r["id"] for r in rows}
    arrays = {}
    audit, inconsistent = [], []
    for row in rows:
        assert row["seed"] in (0, 1) and row["level"] == "grasp_easy" and row["group"] == "parity"
        path = OUT / row["npz"]
        assert path.stat().st_size == row["bytes"] and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        with np.load(path, allow_pickle=False) as f:
            x = {k: f[k] for k in f.files}
        arrays[row["id"]] = x
        done = x["done"].reshape(256)
        idx = next(i for i, v in enumerate(done) if bool(v))
        label = bool(x["returned_episode_solved"][idx, 0])
        reward = x["q6_substep_reward"][idx, 0].tolist()
        assert int(x["returned_episode_lengths"][idx, 0]) == idx + 1
        assert np.array_equal(x["GoalR"], x["returned_episode_solved"])
        assert np.array_equal(x["q6_substep_goal"], x["q6_substep_reward"] > 0)
        for key, value in x.items():
            if value.shape and value.shape[0] == 256 and np.issubdtype(value.dtype, np.number):
                assert np.isfinite(value[:idx+1]).all(), (row["id"], key)
        assert x["q6_post_finite"][:idx+1].all()
        for t in range(256):
            h = hashlib.sha256()
            for state in row["state_keys"]:
                a = np.ascontiguousarray(x[state["key"]][t])
                h.update(str(a.dtype).encode()); h.update(str(a.shape).encode()); h.update(a.tobytes())
            assert h.hexdigest() == row["state_sha256"][t]
        mismatch = label != any(value > 0 for value in reward)
        assert (row["validity"] == "FAIL") == mismatch
        entry = {"id": row["id"], "first_terminal_step": idx+1,
                 "official_solved": label, "substep_reward": reward, "disagreement": mismatch}
        audit.append(entry)
        if mismatch:
            inconsistent.append((row, idx, x))
    assert len(inconsistent) == 1
    pair_checks = []
    for seed in (0, 1):
        a_id = f"parity_grasp_easy_naive_0_{seed}_original"
        b_id = f"parity_grasp_easy_naive_0_{seed}_adapter"
        a, b = arrays[a_id], arrays[b_id]
        end = next(i+1 for i, d in enumerate(a["done"].reshape(256)) if bool(d))
        assert next(i+1 for i,d in enumerate(b["done"].reshape(256)) if bool(d)) == end
        numeric = [k for k in a if k.startswith("state_")] + ["q6_command", "q6_obs", "q6_processed"]
        maximum = 0.
        for key in numeric:
            x, y = a[key][:end], b[key][:end]
            if np.issubdtype(x.dtype, np.inexact):
                delta = np.abs(x-y)
                assert np.all(delta <= 1e-6+1e-6*np.abs(y)), key
                maximum = max(maximum, float(delta.max()) if delta.size else 0.)
            else:
                assert np.array_equal(x, y)
        pair_checks.append({"seed": seed, "terminal_step": end, "max_abs": maximum, "status": "PASS"})

    row, idx, x = inconsistent[0]
    level, static, params = load_from_json_file(f"/source/rtc/worlds/l/{row['level']}.json")
    static = static.replace(screen_dim=(512, 512))
    env = kenv.make_kinetix_env_from_name("Kinetix-Symbolic-Continuous-v1", static_env_params=static)
    pairs, tree = jax.tree_util.tree_flatten_with_path(level)
    assert [jax.tree_util.keystr(p) for p, _ in pairs] == [r["path"] for r in row["state_keys"]]
    before = jax.tree_util.tree_unflatten(tree, [jnp.asarray(x[r["key"]][idx, 0]) for r in row["state_keys"]])
    command = jnp.asarray(x["q6_command"][idx, 0])
    root_key = jax.random.wrap_key_data(jnp.asarray(x["q6_step_key"][idx, 0]))
    one_env_key = jax.random.split(root_key, 1)[0]
    _, noisy_wrapper_key = jax.random.split(one_env_key)
    noise_key, physics_key = jax.random.split(noisy_wrapper_key)
    noisy = command + jax.random.normal(noise_key, command.shape)*train_expert.ACTION_NOISE_STD
    processed = env.action_type.process_action(noisy, before, static)
    np.testing.assert_allclose(np.asarray(noisy), x["noisy_command"][idx], atol=1e-6, rtol=1e-6)
    np.testing.assert_allclose(np.asarray(processed), x["q6_processed"][idx, 0], atol=1e-6, rtol=1e-6)
    # Entirely unmodified official engine and official noise wrapper.
    official = jax.jit(train_expert.NoisyActionWrapper(env).step_env)
    obs, after, reward, done, info = jax.block_until_ready(official(noisy_wrapper_key, before, command, params))
    assert bool(done) and not bool(info["GoalR"])
    assert all(np.isfinite(np.asarray(a)).all() for a in jax.tree.leaves(after))
    assert int(after.timestep) == idx+1

    # Independently expose both source physics substeps with a Python-unrolled loop.
    @jax.jit
    def substep_audit(state, action):
        rewards = []
        goals = []
        for _ in range(static.frame_skip):
            state, manifolds = env.physics_engine.step(state, params, action)
            r, i = env.compute_reward_info(state, manifolds)
            rewards.append(r); goals.append(i["GoalR"])
        return state, jnp.stack(rewards), jnp.stack(goals)
    replay_state, rewards, goals = jax.block_until_ready(substep_audit(before, processed))
    np.testing.assert_array_equal(np.asarray(rewards), x["q6_substep_reward"][idx, 0])
    np.testing.assert_array_equal(np.asarray(goals), x["q6_substep_goal"][idx, 0])
    assert np.any(np.asarray(rewards) > 0) and not bool(info["GoalR"])
    mutations = {"official_label_flip": label_mutation_rejected(rows, arrays),
                 "missing_record": set(failure["completed_record_ids"]) != {r["id"] for r in rows[:-1]},
                 "state_byte_change": state_mutation_rejected(row, x)}
    assert all(mutations.values())
    result = {"status": "VERIFIED_DEFER_TERMINAL_SEMANTICS", "source_files": source_files,
              "frozen_execution_files": len(frozen["files"]), "records": audit,
              "verified_parity_pairs": pair_checks, "mutation_rejections": mutations,
              "source_terminal_reconstruction": {"case": row["id"], "first_terminal_step": idx+1,
                  "official_done": bool(done), "official_GoalR": bool(info["GoalR"]),
                  "official_aggregated_reward": float(reward), "independent_substep_rewards": np.asarray(rewards).tolist(),
                  "independent_substep_goals": np.asarray(goals).tolist(), "all_finite": True,
                  "scope": "one saved step reconstructed with original engine; no new rollout"},
              "heldout_records_executed": 0, "readiness_records_completed": 5,
              "unexecuted_readiness_records": 135, "pilot_readiness": False}
    path = OUT / "verification.json"
    assert not path.exists()
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


def label_mutation_rejected(rows, arrays):
    row = next(r for r in rows if r["validity"] == "PASS")
    x = arrays[row["id"]]
    idx = next(i for i, d in enumerate(x["done"].reshape(256)) if bool(d))
    mutated = not bool(x["returned_episode_solved"][idx, 0])
    return mutated != bool(x["GoalR"][idx, 0])


def state_mutation_rejected(row, x):
    key = row["state_keys"][0]["key"]
    b = bytearray(np.ascontiguousarray(x[key][0]).tobytes())
    b[0] ^= 1
    return hashlib.sha256(b).hexdigest() != hashlib.sha256(np.ascontiguousarray(x[key][0]).tobytes()).hexdigest()


if __name__ == "__main__":
    main()
