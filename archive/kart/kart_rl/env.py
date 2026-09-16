from collections import deque
import time
import numpy as np
import gymnasium as gym
from PIL import Image
from .common import ROOT, require_validated
from .progress import Progress

def raw_env(config):
    import stable_retro as retro
    retro.data.Integrations.add_custom_path(str(ROOT / config['integration_dir']))
    return retro.make(config['game'], state=config['state'], inttype=retro.data.Integrations.CUSTOM,
                      use_restricted_actions=retro.Actions.ALL, render_mode='rgb_array')

class KartEnv(gym.Env):
    metadata = {'render_modes': ['rgb_array'], 'render_fps': 15}

    def __init__(self, config, raw=None):
        self.config = config
        if raw is None:
            require_validated(config)
            raw = raw_env(config)
        self.raw = raw
        self.action_space = gym.spaces.Discrete(len(config['actions']))
        self.observation_space = gym.spaces.Box(0, 255, (4, 84, 84), np.uint8)
        self.buttons = []
        for names in config['actions']:
            if not set(names).issubset(raw.buttons):
                raise ValueError('Configured button missing from emulator')
            self.buttons.append(np.array([int(b in names) for b in raw.buttons], dtype=np.int8))
        self.stack = deque(maxlen=4)
        self.total_frames = self.total_decisions = 0
        self.simulation_seconds = 0.0
        self.reset_calls = 0

    def pixel(self, rgb):
        return np.array(Image.fromarray(rgb).convert('L').resize((84, 84), Image.Resampling.BILINEAR))

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        rgb, info = self.raw.reset(seed=seed)
        self.reset_calls += 1
        # Stable-Retro 1.0.1 reset returns an empty info mapping.
        info = {**self.raw.data.lookup_all(), **info}
        self.last_rgb = rgb
        self.frames = self.decisions = 0
        cp = int(info['checkpoint']) - self.config['checkpoint_offset']
        if int(info['num_checkpoints']) != self.config['checkpoint_count']:
            raise RuntimeError('Unexpected checkpoint count; recalibrate integration')
        if int(info['laps']) != self.config['lap_start']:
            raise RuntimeError('Start state must be calibrated at the beginning of lap one')
        self.progress = Progress(self.config['checkpoint_count'], cp, int(info['laps']), self.config['race_laps'])
        self.stack.clear()
        self.stack.extend([self.pixel(rgb)] * 4)
        self.info = self.metrics(info, 0, False, False)
        return np.stack(self.stack), self.info

    def metrics(self, info, advanced, terminated, truncated):
        return {**info, 'frames': self.frames, 'decisions': self.decisions,
                'frames_advanced': advanced, 'valid_laps': self.progress.valid_laps,
                'track_progress_laps': self.progress.maximum / self.progress.count,
                'signed_progress_laps': self.progress.position / self.progress.count,
                'race_complete': self.progress.complete, 'telemetry_invalid': self.progress.invalid,
                'finish_seconds': self.frames / self.config['fps'] if self.progress.complete else None,
                'terminated': bool(terminated), 'truncated': bool(truncated)}

    def step(self, action):
        self.decisions += 1
        self.total_decisions += 1
        reward = 0.0
        terminated = truncated = False
        advanced = 0
        for _ in range(self.config['action_repeat']):
            tick = time.perf_counter()
            rgb, _, native_done, native_truncated, info = self.raw.step(self.buttons[int(action)])
            self.simulation_seconds += time.perf_counter() - tick
            self.frames += 1
            self.total_frames += 1
            advanced += 1
            reward += self.progress.update(int(info['checkpoint']) - self.config['checkpoint_offset'],
                                           int(info['laps']), int(info['backward']) == 16)
            reward -= 0.0001  # Time cost per emulated frame; not a race outcome.
            terminated = bool(self.progress.complete or native_done)
            truncated = bool(native_truncated or self.progress.invalid or self.frames >= self.config['episode_frames'])
            self.last_rgb = rgb
            if terminated or truncated:
                break
        self.stack.append(self.pixel(self.last_rgb))
        self.info = self.metrics(info, advanced, terminated, truncated)
        return np.stack(self.stack), reward, terminated, truncated, self.info

    def render(self):
        return self.last_rgb.copy()

    def close(self):
        self.raw.close()
