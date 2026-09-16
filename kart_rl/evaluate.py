"""Fixed-protocol evaluation with full decision traces and beginning/end clips."""
import argparse
from collections import deque
from pathlib import Path
import time
import numpy as np
import torch
from PIL import Image
from stable_baselines3 import PPO
from stable_baselines3.common.utils import set_random_seed
from .common import ROOT, read_json, write_json, digest, now, identity
from .env import KartEnv

def evaluate(config, output, model_path=None, seeds=None, max_seconds=120, record=True):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    seeds = seeds or config['evaluation_seeds']
    start = time.perf_counter()
    deadline = start + max_seconds
    torch.set_num_threads(1)
    result = {'status': 'running', 'at': now(), 'protocol': config, 'identity': identity(config),
              'policy': 'ppo' if model_path else 'hold accelerate',
              'model_sha256': digest(model_path) if model_path else None,
              'seeds': seeds, 'sampling': 'stochastic PPO; seeds change action sampling, not the track',
              'learning_updates': 0, 'record': record, 'episodes': [], 'partial_episode': None,
              'recording_seconds': 0.0, 'max_seconds': max_seconds}
    write_json(output / 'evaluation.json', result)
    env = None
    try:
        env = KartEnv(config)
        model = PPO.load(model_path, device='cpu') if model_path else None
        for seed in seeds:
            if time.perf_counter() >= deadline:
                break
            set_random_seed(seed)
            obs, info = env.reset(seed=seed)
            beginning, ending = [], deque(maxlen=75)
            first = Image.fromarray(env.render()) if record else None
            total_reward = 0.0
            episode_start = time.perf_counter()
            completed = False
            import json
            trace = output / f'trial-{seed}.jsonl'
            result['partial_episode'] = {'seed': seed, 'trace': trace.name, 'complete_trial': False,
                                         **info, 'training_reward_sum': 0.0}
            with trace.open('x') as stream:
                stream.write(json.dumps({'event': 'reset', 'seed': seed, 'info': info}, default=lambda x:x.item()) + '\n')
                while time.perf_counter() < deadline:
                    action = int(model.predict(obs, deterministic=False)[0]) if model else 1
                    obs, reward, term, trunc, info = env.step(action)
                    total_reward += float(reward)
                    result['partial_episode'].update(**info, training_reward_sum=total_reward,
                                                     evaluation_seconds=time.perf_counter()-episode_start)
                    stream.write(json.dumps({'action': action, 'action_name': config['action_names'][action],
                                             'reward': float(reward), **info}, default=lambda x:x.item()) + '\n')
                    if record:
                        tick = time.perf_counter()
                        frame = Image.fromarray(env.render())
                        if len(beginning) < 150:
                            beginning.append(frame)
                        ending.append(frame)
                        result['recording_seconds'] += time.perf_counter() - tick
                    if term or trunc:
                        completed = True
                        break
            episode = {'seed': seed, 'trace': trace.name, 'complete_trial': completed, **info,
                       'training_reward_sum': total_reward, 'evaluation_seconds': time.perf_counter()-episode_start}
            if record:
                tick = time.perf_counter()
                first.save(output / f'trial-{seed}-start.png')
                Image.fromarray(env.render()).save(output / f'trial-{seed}-end.png')
                episode['media'] = []
                for label, frames in [('beginning', beginning), ('ending', list(ending))]:
                    if frames:
                        name = f'trial-{seed}-{label}.gif'
                        frames[0].save(output / name, save_all=True, append_images=frames[1:], loop=0,
                                       duration=round(1000*config['action_repeat']/config['fps']))
                        episode['media'].append(name)
                result['recording_seconds'] += time.perf_counter() - tick
            if completed:
                result['episodes'].append(episode)
                result['partial_episode'] = None
            else:
                result['partial_episode'] = episode
            write_json(output / 'evaluation.json', result)
        result['status'] = 'complete' if len(result['episodes']) == len(seeds) else 'incomplete'
        if any(e['telemetry_invalid'] for e in result['episodes']):
            result['status'] = 'invalid_telemetry'
    except BaseException as exc:
        result.update(status='incomplete', error=repr(exc))
        raise
    finally:
        if env:
            env.close()
        result['wall_seconds'] = time.perf_counter()-start
        result['game_frames'] = sum(e['frames'] for e in result['episodes']) + (result['partial_episode'] or {}).get('frames', 0)
        result['agent_decisions'] = sum(e['decisions'] for e in result['episodes']) + (result['partial_episode'] or {}).get('decisions', 0)
        write_json(output / 'evaluation.json', result)
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--model')
    p.add_argument('--seconds', type=float, default=120)
    p.add_argument('--seeds', nargs='+', type=int)
    p.add_argument('--no-record', action='store_true')
    a = p.parse_args()
    if a.seconds <= 0 or not np.isfinite(a.seconds):
        p.error('seconds must be positive and finite')
    evaluate(read_json(a.config), a.output, a.model, a.seeds, a.seconds, not a.no_record)

if __name__ == '__main__':
    main()
