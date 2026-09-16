import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
def now(): return datetime.now(timezone.utc).isoformat()
def write_json(path, data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');temp.replace(path)
def read_json(path): return json.loads(Path(path).read_text())
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def revision(): return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def source_hashes():
    return {str(p.relative_to(ROOT)):digest(p) for pattern in ('smb3_rl/*.py','configs/*.json','requirements-lock.txt') for p in sorted(ROOT.glob(pattern))}
def identity(config):
    from gym_super_mario_bros._roms import smb3_rom_path
    import gym_super_mario_bros.smb3_env as installed
    return {'config_sha256':hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest(),
            'rom_sha256':digest(smb3_rom_path()), 'installed_environment_sha256':digest(installed.__file__),
            'adapter_sha256':digest(ROOT/'smb3_rl/env.py'),
            'versions':{n:importlib.metadata.version(n) for n in ['gym-super-mario-bros','nes-py','gymnasium','stable-baselines3','torch','numpy','pillow']}}
def require_validated(config):
    record=read_json(ROOT/config['validation_file'])
    if record.get('identity')!=identity(config) or record.get('status')!='passed':
        raise RuntimeError('SMB3 validation is missing, failed, or stale. Run python -m smb3_rl.validate.')
    return record
