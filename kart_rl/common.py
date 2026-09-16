import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    temp.replace(path)

def read_json(path):
    return json.loads(Path(path).read_text())

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def revision():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()

def source_hashes():
    return {str(p.relative_to(ROOT)): digest(p) for pattern in ('kart_rl/*.py', 'configs/*.json', 'requirements-lock.txt', 'integrations/**/*.json') for p in sorted(ROOT.glob(pattern))}

def identity(config):
    folder = ROOT / config['integration_dir'] / config['game']
    return {'config_sha256': hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
            'rom_sha256': digest(folder / 'rom.sfc'),
            'state_sha256': digest(folder / (config['state'] + '.state')),
            'integration_files': {p.name: digest(p) for p in sorted(folder.iterdir()) if p.suffix in ('.json','.lua','.sha')},
            'installed_versions': {n: importlib.metadata.version(n) for n in ['stable-retro','gymnasium','stable-baselines3','torch','numpy','pillow']},
            'sources': source_hashes()}

REQUIRED_CHECKS = ['character_track_mode', 'controls', 'reset_repeatability', 'screen_observations',
                   'checkpoint_order', 'backward_no_reward', 'oscillation_no_reward',
                   'lap_vs_hud', 'five_lap_finish', 'termination_and_timeout', 'frame_timing']

def require_validated(config):
    path = ROOT / 'private/validation.json'
    if not path.exists():
        raise RuntimeError('Kart integration is NOT validated. Complete docs/VALIDATION.md before training.')
    record = read_json(path)
    if record.get('identity') != identity(config):
        raise RuntimeError('Validation is stale: ROM, state, configuration or source changed.')
    for key in REQUIRED_CHECKS:
        entry = record.get('checks', {}).get(key, {})
        if entry.get('passed') is not True or not entry.get('evidence'):
            raise RuntimeError('Missing validation evidence: ' + key)
        for proof in entry['evidence']:
            p = ROOT / proof['path']
            if not p.is_file() or digest(p) != proof['sha256']:
                raise RuntimeError('Missing/changed validation evidence: ' + key)
    if config['checkpoint_count'] is None:
        raise RuntimeError('Checkpoint count has not been calibrated.')
    return record
