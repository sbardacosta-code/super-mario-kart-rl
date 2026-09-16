"""Local PPO sessions, bounded pilot, wall-clock stage checkpoints and provenance."""
import argparse
import gzip
import json
import fcntl
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
import psutil
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from .common import ROOT, read_json, write_json, now, digest, revision, source_hashes, require_validated
from .env import KartEnv

class TimedPPO(PPO):
    def collect_rollouts(self, *args, **kwargs):
        start = time.perf_counter()
        try:
            return super().collect_rollouts(*args, **kwargs)
        finally:
            self.rollout_seconds += time.perf_counter() - start
    def train(self):
        start = time.perf_counter()
        try:
            return super().train()
        finally:
            self.update_seconds += time.perf_counter()-start
            self.update_calls += 1

class Budget(BaseCallback):
    def __init__(self, seconds, stopped, trace):
        super().__init__()
        self.deadline = time.perf_counter() + seconds
        self.stopped = stopped
        self.trace = trace
    def _on_step(self):
        self.trace.write(json.dumps({'model_decision': self.num_timesteps,
                                    'action': int(self.locals['actions'][0]),
                                    'reward': float(self.locals['rewards'][0]),
                                    **self.locals['infos'][0]},
                                   default=lambda x: x.tolist() if hasattr(x,'tolist') else str(x)) + '\n')
        if self.locals['infos'][0].get('telemetry_invalid'):
            raise RuntimeError('Invalid training telemetry; integration must be investigated before continuing.')
        return time.perf_counter() < self.deadline and not self.stopped()

def run(args):
    config = read_json(ROOT / args.config)
    validation = require_validated(config)  # Before creating any session or model.
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip():
        raise ValueError('Commit source changes before training so the source revision is reproducible.')
    if args.resume:
        parent_model = Path(args.resume).resolve()
        parent_manifest = read_json(parent_model.parent.parent / 'manifest.json')
        if parent_manifest['config'] != config or parent_manifest['source_hashes'] != source_hashes():
            raise ValueError('Resume requires the same source and configuration; document a new experiment for changes.')
        if parent_manifest['validation']['identity'] != validation['identity']:
            raise ValueError('Resume environment identity differs from the parent session.')
        if digest(parent_model) not in [s['model_sha256'] for s in parent_manifest['stages']]:
            raise ValueError('Resume checkpoint is not in the parent session manifest.')
    run = ROOT / 'sessions' / args.session
    if run.parent != ROOT / 'sessions' or not args.session or args.session.startswith('.'):
        raise ValueError('Use a simple new session name')
    run.mkdir(exist_ok=False)
    (run / 'checkpoints').mkdir()
    (run / 'logs').mkdir()
    start = time.perf_counter()
    pilot_deadline = start + 720 if args.pilot else float('inf')
    training_limit = 600 if args.pilot else args.active_minutes * 60
    stopped = [False]
    signal.signal(signal.SIGINT, lambda *_: stopped.__setitem__(0, True))
    signal.signal(signal.SIGTERM, lambda *_: stopped.__setitem__(0, True))
    def should_stop():
        return stopped[0] or (run / 'STOP').exists()
    manifest = {'status': 'running', 'at': now(), 'session_id': args.session, 'config': config,
                'kind': '12-minute pilot' if args.pilot else 'approved training',
                'budget_note': args.budget_note, 'requested_active_seconds': training_limit,
                'source_revision': revision(), 'source_hashes': source_hashes(), 'validation': validation,
                'parent_model_sha256': digest(args.resume) if args.resume else None,
                'stages': [], 'training_seconds': 0.0, 'evaluation_seconds': 0.0,
                'rollout_seconds': 0.0, 'learning_seconds': 0.0, 'optimizer_steps': 0,
                'learning_update_calls': 0, 'training_game_frames': 0, 'training_agent_decisions': 0,
                'checkpoint_seconds': 0.0, 'peak_sampled_rss_bytes': 0}
    write_json(run / 'config.json', config)
    write_json(run / 'manifest.json', manifest)
    (run / 'requirements.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'], text=True))
    peak = [0]
    sampling_done = threading.Event()
    def sample_memory():
        process = psutil.Process()
        while not sampling_done.wait(.1):
            try:
                peak[0] = max(peak[0], process.memory_info().rss + sum(c.memory_info().rss for c in process.children(recursive=True)))
            except psutil.Error:
                pass
    sampler = threading.Thread(target=sample_memory, daemon=True)
    sampler.start()
    torch.set_num_threads(1)
    env = model = None
    def persist():
        manifest['wall_seconds'] = time.perf_counter()-start
        manifest['peak_sampled_rss_bytes'] = peak[0]
        write_json(run / 'manifest.json', manifest)
    def checkpoint(label):
        tick = time.perf_counter()
        path = run / 'checkpoints' / (label + '.zip')
        if path.exists():
            raise RuntimeError('Refusing to overwrite a checkpoint: '+str(path))
        temporary = path.with_name(path.stem+'.tmp.zip')
        model.save(temporary)
        temporary.replace(path)
        manifest['checkpoint_seconds'] += time.perf_counter()-tick
        stage = {'id': label, 'model_sha256': digest(path), 'model_path': str(path.relative_to(ROOT)),
                 'training_seconds': manifest['training_seconds'], 'status': 'evaluation_pending',
                 'total_model_decisions': model.num_timesteps, 'evaluation': None}
        manifest['stages'].append(stage)
        persist()
        return stage, path
    def evaluate(label, path=None, seeds=None, record=True, max_seconds=120):
        remaining = pilot_deadline-time.perf_counter()
        if should_stop() or remaining < 15:
            return None
        output = run / label
        seconds = min(max_seconds, remaining-10)
        cmd = [sys.executable, '-m', 'kart_rl.evaluate', '--config', str(run/'config.json'),
               '--output', str(output), '--seconds', str(seconds)]
        if path:
            cmd += ['--model', str(path)]
        if seeds:
            cmd += ['--seeds', *map(str, seeds)]
        if not record:
            cmd += ['--no-record']
        tick = time.perf_counter()
        with (run / 'logs' / (label + '.log')).open('x') as log:
            child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
            try:
                while child.poll() is None:
                    if should_stop() or time.perf_counter() > tick+seconds+15:
                        child.send_signal(signal.SIGINT)
                        try:
                            child.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            child.kill(); child.wait()
                        break
                    time.sleep(.1)
            finally:
                manifest['evaluation_seconds'] += time.perf_counter()-tick
                persist()
        report = output / 'evaluation.json'
        return str(report.relative_to(ROOT)) if report.exists() else None
    def eval_stage(stage, path, seeds=None):
        stage['evaluation'] = evaluate(stage['id'], path, seeds, max_seconds=60 if args.pilot else args.eval_seconds)
        stage['status'] = read_json(ROOT/stage['evaluation'])['status'] if stage['evaluation'] else 'evaluation_pending'
        persist()
        if stage['status']=='invalid_telemetry':
            raise RuntimeError('Invalid evaluation telemetry; refusing further training.')
    try:
        env = KartEnv(config)
        model = TimedPPO.load(args.resume, env=env, device='cpu') if args.resume else TimedPPO('CnnPolicy', env, seed=config['seed'], device='cpu', verbose=0, **config['ppo'])
        model.rollout_seconds = model.update_seconds = 0.0
        model.update_calls = 0
        optimizer_steps = [0]
        hook = model.policy.optimizer.register_step_post_hook(lambda *_: optimizer_steps.__setitem__(0, optimizer_steps[0]+1))
        initial, path = checkpoint('00-resumed' if args.resume else '00-untrained')
        eval_stage(initial, path)
        manifest['accelerate_baseline'] = evaluate('hold-accelerate', max_seconds=60 if args.pilot else args.eval_seconds)
        if args.pilot:
            manifest['overhead_without_recording'] = evaluate('overhead-no-record', path, [101], False, 30)
            manifest['overhead_with_recording'] = evaluate('overhead-record', path, [101], True, 30)
        index = 1
        while manifest['training_seconds'] < training_limit and not should_stop():
            budget = min(900, training_limit-manifest['training_seconds'], pilot_deadline-time.perf_counter()-90)
            if budget < 1:
                break
            tick = time.perf_counter()
            try:
                with gzip.open(run/'logs'/f'{index:02d}-training-trace.jsonl.gz','xt') as trace:
                    model.learn(total_timesteps=10**9, callback=Budget(budget, should_stop, trace), reset_num_timesteps=False)
            finally:
                manifest['training_seconds'] += time.perf_counter()-tick
                manifest.update(rollout_seconds=model.rollout_seconds, learning_seconds=model.update_seconds,
                                learning_update_calls=model.update_calls, optimizer_steps=optimizer_steps[0],
                                training_game_frames=env.total_frames, training_agent_decisions=env.total_decisions)
                manifest.update(simulation_seconds=env.simulation_seconds, training_reset_calls=env.reset_calls,
                                simulated_frames_per_second=env.total_frames/env.simulation_seconds if env.simulation_seconds else None,
                                optimizer_steps_per_second=optimizer_steps[0]/model.update_seconds if model.update_seconds else None)
                persist()
            stage, path = checkpoint(f'{index:02d}-stage')
            if not all(torch.isfinite(p).all().item() for p in model.policy.parameters()):
                raise RuntimeError('Nonfinite policy weights; stage retained for diagnosis')
            eval_stage(stage, path)
            index += 1
            if args.pilot:
                break
        final, path = checkpoint('final')
        eval_stage(final, path)
        if not args.pilot and not should_stop():
            manifest['final_additional_trials'] = evaluate('final-additional-trials', path, config['final_seeds'], max_seconds=args.eval_seconds*2)
        manifest['status'] = 'stopped' if should_stop() else 'completed'
        hook.remove()
    except BaseException as exc:
        manifest.update(status='failed', error=repr(exc))
        if model is not None:
            checkpoint('emergency')
        raise
    finally:
        if env:
            env.close()
        sampling_done.set(); sampler.join(timeout=1)
        persist()
        from .report import build
        build(run)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='configs/mario-circuit-1.json')
    p.add_argument('--session', required=True)
    budget = p.add_mutually_exclusive_group(required=True)
    budget.add_argument('--pilot', action='store_true')
    budget.add_argument('--active-minutes', type=float)
    p.add_argument('--budget-note', required=True, help='Who chose this budget and when')
    p.add_argument('--resume', type=Path)
    p.add_argument('--eval-seconds', type=float, default=300)
    args = p.parse_args()
    import math
    if (args.active_minutes is not None and (not math.isfinite(args.active_minutes) or args.active_minutes<=0)) or not math.isfinite(args.eval_seconds) or args.eval_seconds<=0:
        p.error('Budgets must be finite and positive')
    (ROOT / '.cache').mkdir(exist_ok=True)
    with (ROOT / '.cache/session.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args)

if __name__ == '__main__':
    main()
