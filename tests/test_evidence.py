import json
import torch
from kart_rl.common import read_json, ROOT
from kart_rl.session import TimedPPO
from tests.test_env import make

def test_real_ppo_save_load_and_evaluation_evidence(tmp_path, monkeypatch):
    import kart_rl.evaluate as evaluation
    torch.set_num_threads(1)
    env=make()
    model=TimedPPO('CnnPolicy',env,n_steps=8,batch_size=4,n_epochs=1,device='cpu',seed=1)
    model.rollout_seconds=model.update_seconds=0.0
    model.update_calls=0
    model.learn(16)
    assert model.update_calls==2 and model.rollout_seconds>0 and model.update_seconds>0
    checkpoint=tmp_path/'test.zip'
    model.save(checkpoint)
    monkeypatch.setattr(evaluation,'KartEnv',lambda config: make())
    monkeypatch.setattr(evaluation,'identity',lambda config: {'synthetic_test':True})
    result=evaluation.evaluate(env.config,tmp_path/'evaluation',checkpoint,seeds=[1,2],max_seconds=30)
    assert result['status']=='complete' and len(result['episodes'])==2
    assert result['learning_updates']==0
    for episode in result['episodes']:
        assert episode['frames']==12 and episode['valid_laps']==1
        trace=tmp_path/'evaluation'/episode['trace']
        assert len(trace.read_text().splitlines())==4
        assert len(episode['media'])==2
        for media in episode['media']:
            assert (tmp_path/'evaluation'/media).is_file()
    assert result['model_sha256'] and result['recording_seconds']>0

def test_evaluation_deadline_is_incomplete_not_a_zero_score(tmp_path,monkeypatch):
    import kart_rl.evaluate as evaluation
    monkeypatch.setattr(evaluation,'KartEnv',lambda config: make())
    monkeypatch.setattr(evaluation,'identity',lambda config: {'synthetic_test':True})
    result=evaluation.evaluate(make().config,tmp_path/'partial',max_seconds=0.000001)
    assert result['status']=='incomplete' and result['episodes']==[]
