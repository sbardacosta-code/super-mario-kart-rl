"""ROM-free compatibility check. This is NOT a Kart benchmark."""
import argparse
import importlib.metadata
import platform
import time
from pathlib import Path
import numpy as np
import gymnasium as gym
import psutil
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from PIL import Image
from .common import write_json, now

class TestPixels(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.observation_space = gym.spaces.Box(0, 255, (1, 84, 84), np.uint8)
        self.action_space = gym.spaces.Discrete(2)
    def convert(self, obs):
        return np.asarray(Image.fromarray(obs).convert('L').resize((84,84)))[None]
    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        return self.convert(obs), info
    def step(self, action):
        keys = np.zeros(len(self.env.buttons), dtype=np.int8)
        if action:
            keys[self.env.buttons.index('B')] = 1
        obs, reward, term, trunc, info = self.env.step(keys)
        return self.convert(obs), reward, term, trunc, info

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error('Output exists; preserve the earlier check with a new filename.')
    import stable_retro as retro
    report = {'at': now(), 'purpose': 'ROM-free compatibility check; not Super Mario Kart training',
              'python': platform.python_version(), 'architecture': platform.machine(),
              'macos': platform.mac_ver()[0], 'device': 'cpu',
              'mps_available_in_this_process': torch.backends.mps.is_available(),
              'versions': {n: importlib.metadata.version(n) for n in ['stable-retro','gymnasium','stable-baselines3','torch','numpy']},
              'status': 'running'}
    write_json(args.output, report)
    env = None
    try:
        torch.set_num_threads(1)
        env = TestPixels(retro.make('Airstriker-Genesis-v0', render_mode='rgb_array'))
        check_env(env, warn=True)
        report['gymnasium_check'] = 'passed'
        obs, _ = env.reset(seed=123)
        started = time.perf_counter()
        for i in range(600):
            obs, _, term, trunc, _ = env.step(i % 2)
            if term or trunc:
                obs, _ = env.reset()
        report['test_game_frames'] = 600
        report['test_game_step_seconds'] = time.perf_counter() - started
        model = PPO('CnnPolicy', env, n_steps=64, batch_size=32, n_epochs=1, device='cpu', seed=123, verbose=0)
        before = {k: v.clone() for k, v in model.policy.state_dict().items()}
        started = time.perf_counter()
        model.learn(128)
        report['test_ppo_seconds'] = time.perf_counter() - started
        report['test_ppo_decisions'] = model.num_timesteps
        report['weights_changed'] = any(not torch.equal(v, before[k]) for k,v in model.policy.state_dict().items())
        report['finite_weights'] = all(torch.isfinite(v).all().item() for v in model.policy.parameters())
        report['rss_bytes_after_check'] = psutil.Process().memory_info().rss
        report['status'] = 'passed' if report['weights_changed'] and report['finite_weights'] else 'failed'
    except Exception as exc:
        report.update(status='failed', error=repr(exc))
        raise
    finally:
        if env is not None:
            env.close()
        write_json(args.output, report)

if __name__ == '__main__':
    main()
