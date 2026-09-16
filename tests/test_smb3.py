from pathlib import Path
import numpy as np
from smb3_rl.common import ROOT,read_json
from smb3_rl.env import HighWater,MarioEnv

def config():return read_json(ROOT/'configs/smb3-1-1.json')

def test_reward_cannot_be_farmed_by_revisiting_positions():
    p=HighWater(24)
    assert sum(p.update(x) for x in [40,24]*100)==16
    assert p.update(1000,False)==0
    assert p.maximum==40

def test_exact_timeout_and_reset_stack():
    e=MarioEnv({**config(),'episode_frames':7},validate=False)
    try:
        first,_=e.reset(seed=1);e.step(1);last,_,t,tr,i=e.step(1)
        assert tr and not t and i['frames']==7 and i['frames_advanced']==3
        again,i=e.reset(seed=5)
        assert np.array_equal(first,again) and i['frames']==0
    finally:e.close()

def test_false_clear_regression_ends_as_death():
    e=MarioEnv(config(),validate=False)
    try:
        e.reset()
        for n in range(200):
            _,_,t,tr,i=e.step(4 if n%6<2 else 3)
            if t or tr:break
        assert t and i['death'] and not i['level_complete']
        assert i['frames']==370 and i['max_x']==352
    finally:e.close()

def test_real_goal_replay_is_clear_and_preserves_progress():
    e=MarioEnv(config(),validate=False)
    try:
        e.reset()
        for a in read_json(ROOT/'sessions/2026-09-16-smb3-validation/scripted-clear-actions.json'):
            _,_,t,tr,i=e.step(a)
            if t or tr:break
        assert t and not tr and i['level_complete'] and not i['death']
        assert i['max_x']==2844 and i['progress_pixels']==2820
        assert (i['map_y'],i['map_x'])==(32,64)
    finally:e.close()

def test_evaluation_records_complete_trace_and_clips(tmp_path,monkeypatch):
    import smb3_rl.evaluate as module
    monkeypatch.setattr(module,'MarioEnv',lambda c:MarioEnv(c,validate=False))
    result=module.evaluate(config(),tmp_path/'baseline',seeds=[101],max_seconds=20)
    assert result['status']=='complete' and result['learning_updates']==0
    ep=result['episodes'][0]
    assert ep['death'] and not ep['level_complete']
    assert len((tmp_path/'baseline'/ep['trace']).read_text().splitlines())==ep['decisions']+1
    assert len(ep['media'])==2

def test_timed_ppo_changes_finite_weights_and_roundtrips(tmp_path):
    import torch
    from smb3_rl.session import TimedPPO
    torch.set_num_threads(1)
    e=MarioEnv(config(),validate=False)
    try:
        model=TimedPPO('CnnPolicy',e,n_steps=32,batch_size=16,n_epochs=1,seed=321,device='cpu')
        model.rollout_seconds=model.update_seconds=0.;model.update_calls=0
        before=[p.detach().clone() for p in model.policy.parameters()]
        model.learn(64)
        assert model.update_calls==2
        assert any(not torch.equal(a,b) for a,b in zip(before,model.policy.parameters()))
        assert all(torch.isfinite(p).all() for p in model.policy.parameters())
        model.save(tmp_path/'smoke.zip')
        loaded=TimedPPO.load(tmp_path/'smoke.zip',device='cpu')
        assert all(torch.equal(a,b) for a,b in zip(model.policy.parameters(),loaded.policy.parameters()))
    finally:e.close()
