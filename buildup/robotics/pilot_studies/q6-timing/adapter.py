"""Capture-time generation and independently specified availability/switch/estimate."""
import jax
import jax.numpy as jnp
import train_expert
import kinetix.environment.wrappers as wrappers
from timing import select


def keys(seed):
    rng = jax.random.key(seed)
    rng, reset = jax.random.split(rng)
    rng, startup = jax.random.split(rng)
    inference, environment = [], []
    for _ in range(64):
        rng, key = jax.random.split(rng)
        inference.append(key)
        for _ in range(4):
            rng, key = jax.random.split(rng)
            environment.append(key)
    return reset, startup, jnp.stack(inference), jnp.stack(environment).reshape(64, 4)


def make_runner(env, params, policy, profile):
    wrapped = train_expert.BatchEnvWrapper(
        wrappers.LogWrapper(wrappers.AutoReplayWrapper(train_expert.NoisyActionWrapper(env))), 1)

    def run(level, rng_keys, estimates, switches):
        reset, startup, inference_keys, environment_keys = rng_keys
        obs, state = wrapped.reset_to_level(reset, level, params)
        initial = policy.action(startup, obs, 5)

        def request(carry, item):
            obs, state, old = carry
            key, envkeys, estimate, switch = item
            if profile == "naive":
                new = policy.action(key, obs, 5)
            else:
                new = policy.realtime_action(key, obs, 5, old, estimate, 4,
                    "exp" if profile.startswith("soft") else "zeros", 5.0)
            commands = select(old, new, switch)

            def step(carry, item):
                obs, state = carry
                key, action = item
                next_obs, next_state, reward, done, info = wrapped.step(key, state, action, params)
                info = info | {"q6_command": action, "q6_obs": obs,
                               "q6_step_key": jax.random.key_data(key)[None]}
                return (next_obs, next_state), (done, state, info)

            (next_obs, next_state), trace = jax.lax.scan(step, (obs, state),
                (envkeys, commands.transpose(1, 0, 2)))
            remainder = jnp.concatenate([new[:, 4:], jnp.zeros((1, 4, policy.action_dim))], axis=1)
            return (next_obs, next_state, remainder), (trace, (obs, old, new))

        _, (traces, requests) = jax.lax.scan(request, (obs, state, initial),
            (inference_keys, environment_keys, estimates, switches))
        trace = jax.tree.map(lambda x: x.reshape(-1, *x.shape[2:]), traces)
        return trace, requests, initial

    return jax.jit(run)
