"""Surgical, asserted instrumentation of pinned original numeric code.

Original source is never edited. Only diagnostic returns are added; rendering is omitted.
The entire transformed text and a unified diff are saved before execution.
"""
import difflib
import functools
import inspect
from pathlib import Path
import textwrap
import types

import jax
import jax.numpy as jnp
import eval_flow
import kinetix.environment.env as kenv


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def save(name, old, new):
    out = Path("/output/instrumentation")
    out.mkdir(exist_ok=True)
    for suffix, value in [(".py", new), (".diff", "".join(difflib.unified_diff(
        old.splitlines(True), new.splitlines(True), fromfile=f"pinned/{name}", tofile=f"instrumented/{name}")))]:
        path = out / (name + suffix)
        if path.exists():
            assert path.read_text() == value
        else:
            path.write_text(value)


def diagnostic_env(env):
    old = textwrap.dedent(inspect.getsource(kenv.BasePhysicsEnv.engine_step))
    new = replace_once(old, "info = jax.tree.map(lambda x: x[-1], infos)",
        "info = jax.tree.map(lambda x: x[-1], infos)\n"
        "    info['q6_substep_reward'] = rewards\n"
        "    info['q6_substep_goal'] = infos['GoalR']\n"
        "    info['q6_post_finite'] = jax.tree.reduce(jnp.logical_and, jax.tree.map(lambda x: jnp.isfinite(x).all(), env_state), True)\n"
        "    info['q6_processed'] = action_to_perform")
    namespace = vars(kenv).copy()
    exec(compile(new, "q6_engine_instrumentation", "exec"), namespace)
    # Subclass retains the original equations and decorators, adding diagnostics only.
    cls = type("Diagnostic" + type(env).__name__, (type(env),), {"engine_step": namespace["engine_step"]})
    env.__class__ = cls
    save("engine", old, new)
    return env


def original_eval():
    old = inspect.getsource(eval_flow.eval)
    new = replace_once(old,
        "    render_video = train_expert.make_render_video(renderer_pixels.make_render_pixels(env_params, static_env_params))\n", "")
    new = replace_once(new,
        "            return (rng, next_obs, next_env_state), (done, env_state, info)",
        "            info = info | {'q6_command': action, 'q6_obs': obs, 'q6_step_key': jax.random.key_data(key)[None]}\n"
        "            return (rng, next_obs, next_env_state), (done, env_state, info)")
    new = replace_once(new, "    video = render_video(jax.tree.map(lambda x: x[:, 0], env_states))\n    return return_info, video",
        "    return return_info, (dones, env_states, infos)")
    namespace = vars(eval_flow).copy()
    exec(compile(new, "q6_original_eval_instrumentation", "exec"), namespace)
    save("original", old, new)
    return namespace["eval"]
