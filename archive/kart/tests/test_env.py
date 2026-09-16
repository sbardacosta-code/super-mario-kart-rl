import numpy as np
import gymnasium as gym
from kart_rl.env import KartEnv
from kart_rl.common import read_json, ROOT

class FakeRaw:
    buttons = ['B','LEFT','RIGHT']
    @property
    def data(self): return self
    def lookup_all(self):
        return {'checkpoint':(self.frames//2)%4,'laps':128+self.frames//8,'num_checkpoints':4,'backward':0}
    def reset(self, seed=None):
        self.frames=0
        return np.zeros((224,256,3),np.uint8), {}
    def step(self, action):
        self.frames+=1
        return np.full((224,256,3),self.frames,np.uint8), 999, False, False, self.lookup_all()
    def close(self): pass

def make():
    c=read_json(ROOT/'configs/mario-circuit-1.json')
    c.update(checkpoint_count=4,episode_frames=12,race_laps=5)
    return KartEnv(c,raw=FakeRaw())

def test_screen_stack_and_timeout_count_exact_frames():
    env=make()
    obs,info=env.reset(seed=3)
    assert obs.shape==(4,84,84) and obs.dtype==np.uint8
    for _ in range(3):
        obs,r,term,trunc,info=env.step(1)
    assert info['frames']==12 and info['decisions']==3
    assert trunc and not term and info['valid_laps']==1
    assert env.total_frames==12 and r<999
    obs,info=env.reset()
    assert info['frames']==0 and info['valid_laps']==0

def test_finish_can_stop_inside_action_repeat():
    env=make(); env.config['race_laps']=1
    env.config['action_repeat']=3
    env.reset()
    for _ in range(3):
        obs,r,term,trunc,info=env.step(1)
    assert term and not trunc and info['frames']==8 and info['frames_advanced']==2
