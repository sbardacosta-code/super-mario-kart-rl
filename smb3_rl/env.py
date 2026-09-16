"""Screen-only SMB3 policy input; conservative high-water progress reward."""
from collections import deque
import time
import numpy as np
import gymnasium as gym
from PIL import Image
from .common import require_validated

class HighWater:
    def __init__(self,x): self.start=self.maximum=int(x)
    def update(self,x,in_level=True):
        if not in_level: return 0
        x=int(x);delta=max(0,x-self.maximum)
        self.maximum=max(self.maximum,x)
        return delta

class MarioEnv(gym.Env):
    metadata={'render_modes':['rgb_array'],'render_fps':15}
    def __init__(self,config,validate=True):
        if validate: require_validated(config)
        from gym_super_mario_bros.smb3_env import SuperMarioBros3Env
        class Stage11(SuperMarioBros3Env):
            @property
            def _flag_get(self):
                # The upstream time==0 test mistakes death fade-outs for map returns.
                # For this one-stage task the genuine map panel has fixed coordinates.
                return super()._flag_get and self._map_position == (0x20, 0x40)
        from nes_py.wrappers import JoypadSpace
        self.config=config
        self.raw=JoypadSpace(Stage11(target=(1,1),render_mode='rgb_array'),config['actions'])
        self.action_space=gym.spaces.Discrete(len(config['actions']))
        self.observation_space=gym.spaces.Box(0,255,(4,84,84),np.uint8)
        self.stack=deque(maxlen=4)
        self.total_frames=self.total_decisions=self.reset_calls=0
        self.simulation_seconds=0.0
    def pixel(self,rgb):
        return np.asarray(Image.fromarray(rgb).convert('L').resize((84,84),Image.Resampling.BILINEAR))
    def reset(self,*,seed=None,options=None):
        super().reset(seed=seed)
        rgb,info=self.raw.reset(seed=seed)
        self.reset_calls+=1
        self.last_rgb=rgb.copy();self.frames=self.decisions=0
        if (info['world'],info['stage'])!=(1,1) or not info['in_level']:
            raise RuntimeError('Unexpected SMB3 reset state')
        self.progress=HighWater(info['x_pos']);self.last_x=int(info['x_pos'])
        self.invalid=False;self.clear=False;self.death=False;self.initial_lives=info['life']
        self.stack.clear();self.stack.extend([self.pixel(rgb)]*4)
        self.info=self.metrics(info,0,False,False)
        return np.stack(self.stack),self.info
    def metrics(self,info,advanced,terminated,truncated):
        return {**info,'frames':self.frames,'decisions':self.decisions,'frames_advanced':advanced,
                'max_x':self.progress.maximum,'progress_pixels':self.progress.maximum-self.progress.start,
                'milestones_reached':sum(self.progress.maximum-self.progress.start>=x for x in self.config['milestones_pixels']),
                'level_complete':self.clear,'death':self.death,'telemetry_invalid':self.invalid,
                'finish_seconds':self.frames/self.config['fps'] if self.clear else None,
                'termination_reason':'clear' if self.clear else 'death' if self.death else 'invalid_telemetry' if self.invalid else 'frame_limit' if truncated else 'native_terminal' if terminated else None,
                'terminated':bool(terminated),'truncated':bool(truncated)}
    def step(self,action):
        self.decisions+=1;self.total_decisions+=1
        reward=0.0;native_reward=0.0;advanced=0;terminated=truncated=False
        for _ in range(self.config['action_repeat']):
            tick=time.perf_counter()
            rgb,native,term,trunc,info=self.raw.step(int(action))
            self.simulation_seconds+=time.perf_counter()-tick
            self.frames+=1;self.total_frames+=1;advanced+=1;native_reward+=float(native)
            x=int(info['x_pos'])
            # Death animation and map return do not grant horizontal progress.
            in_level=bool(info['in_level']) and not bool(info['death'])
            if in_level and abs(x-self.last_x)>16:
                self.invalid=True
            gained=self.progress.update(x,in_level and not self.invalid)
            self.last_x=x
            self.clear=bool(info['clear']) and not bool(info['death'])
            self.death=bool(info['death'])
            r=self.config['reward']
            reward+=gained*r['progress_scale']-r['frame_cost']
            if self.death: reward-=r['death_penalty']
            if self.clear: reward+=r['clear_bonus']
            terminated=bool(term or self.clear or self.death)
            truncated=bool(trunc or self.invalid or self.frames>=self.config['episode_frames'])
            self.last_rgb=rgb.copy()
            if terminated or truncated:break
        self.stack.append(self.pixel(self.last_rgb))
        self.info=self.metrics(info,advanced,terminated,truncated)
        self.info['native_reward']=native_reward
        return np.stack(self.stack),reward,terminated,truncated,self.info
    def render(self):return self.last_rgb.copy()
    def close(self):self.raw.close()
