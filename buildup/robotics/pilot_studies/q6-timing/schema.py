"""First gate. Execute only inside the Q6 CPU container."""
import dataclasses
import hashlib
import json
from pathlib import Path
import pickle
import sys
import time

sys.path.insert(0, "/source/jaxued/src")
import jax
import jax.numpy as jnp
import numpy as np
from flax import nnx
import model
import train_expert
import kinetix.environment.env as kenv
from kinetix.environment.env_state import EnvParams, StaticEnvParams

OUT = Path("/output")


def load():
    params = EnvParams()
    static = StaticEnvParams(**train_expert.LARGE_ENV_PARAMS, frame_skip=2)
    names = ["grasp_easy", "catcher_v3"]
    paths = [f"/source/rtc/worlds/l/{n}.json" for n in names]
    levels = train_expert.load_levels(paths, static, params)
    static = static.replace(screen_dim=train_expert.SCREEN_DIM)
    env = kenv.make_kinetix_env_from_name("Kinetix-Symbolic-Continuous-v1", static_env_params=static)
    obs_dim = jax.eval_shape(env.reset_to_level, jax.random.key(0),
                             jax.tree.map(lambda x: x[0], levels), params)[0].shape[-1]
    action_dim = env.action_space(params).shape[0]
    policies = {}
    schemas = {}
    for name in names:
        policy = model.FlowPolicy(obs_dim=obs_dim, action_dim=action_dim,
                                  config=model.ModelConfig(), rngs=nnx.Rngs(jax.random.key(0)))
        graph, state = nnx.split(policy)
        expected = state.to_pure_dict()
        with open(f"/data/policies/{name}.pkl", "rb") as f:
            weights = pickle.load(f)
        expected_paths, expected_tree = jax.tree_util.tree_flatten_with_path(expected)
        weight_paths, weight_tree = jax.tree_util.tree_flatten_with_path(weights)
        assert expected_tree == weight_tree, f"{name}: tree mismatch"
        leaves = []
        for (kp, a), (_, b) in zip(expected_paths, weight_paths, strict=True):
            assert a.shape == b.shape and a.dtype == b.dtype, (kp, a.shape, b.shape)
            assert np.isfinite(np.asarray(b)).all(), kp
            leaves.append({"path": jax.tree_util.keystr(kp), "shape": list(b.shape), "dtype": str(b.dtype)})
        state.replace_by_pure_dict(weights)
        policies[name] = nnx.merge(graph, state)
        schemas[name] = leaves
    return names, levels, policies, env, params, static, {
        "obs_dim": obs_dim, "action_dim": action_dim, "env_params": dataclasses.asdict(params),
        "static_env_params": dataclasses.asdict(static), "model": dataclasses.asdict(model.ModelConfig()),
        "checkpoint_leaves": schemas}


def main():
    started = time.monotonic()
    assets = json.loads(Path("/study/assets.json").read_text())
    checked = 0
    for repo in assets["repositories"]:
        for row in repo["files"]:
            data = (Path("/source") / repo["name"] / row["path"]).read_bytes()
            assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
            checked += 1
    for row in assets["weights"]:
        data = Path(f"/data/policies/{row['level']}.pkl").read_bytes()
        assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
    assert jax.default_backend() == "cpu"
    *_, schema = load()
    schema.update(status="SOURCE_SCHEMA_PASS", source_files=checked,
                  python=sys.version, jax=jax.__version__, devices=[str(x) for x in jax.devices()],
                  elapsed_seconds=time.monotonic() - started)
    (OUT / "schema.json").write_text(json.dumps(schema, indent=2, default=str) + "\n")
    print(json.dumps({k: v for k, v in schema.items() if k not in ["checkpoint_leaves", "static_env_params", "env_params"]}), flush=True)


if __name__ == "__main__":
    main()
