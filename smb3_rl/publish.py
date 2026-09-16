"""Audit public files, check Markdown links, and publish verified model Releases."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile
from urllib.parse import unquote
from .common import ROOT, read_json, write_json, digest

REPO = 'sbardacosta-code/super-mario-kart-rl'

def audit():
    names = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    errors = []
    text_types = {'.py','.md','.json','.jsonl','.log','.txt','.toml','.yml','.yaml','.sha'}
    for name in sorted(set(names)):
        p = ROOT/name
        if p.is_symlink() or not p.is_file():
            errors.append(f'Nonregular public file: {name}'); continue
        if name.startswith(('private/','.venv/','research/')) or p.suffix.lower() in {'.nes','.sfc','.smc','.rom','.bin','.state','.bk2','.zip','.pt','.pth'}:
            errors.append(f'Private/binary payload: {name}'); continue
        if p.stat().st_size > 90*1024*1024:
            errors.append(f'Too large for Git: {name}'); continue
        if p.suffix in text_types or p.name in {'.gitignore','.gitattributes','LICENSE'}:
            try:
                body = p.read_text()
                if '\x00' in body:
                    raise ValueError('NUL in text')
                if re.search(r'(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{30,})',body):
                    raise ValueError('Potential credential')
            except (UnicodeError,ValueError) as exc:
                errors.append(f'Invalid public text {name}: {exc}')
                continue
            if p.suffix=='.md':
                for target in re.findall(r'\]\(([^)]+)\)', body):
                    if target.startswith(('http://','https://','#','mailto:')):
                        continue
                    target = unquote(target.split('#')[0])
                    resolved = (p.parent/target).resolve()
                    if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():
                        errors.append(f'Broken/unsafe local link in {name}: {target}')
        elif p.suffix in {'.png','.gif'}:
            from PIL import Image
            try:
                with Image.open(p) as im:
                    im.verify()
            except Exception:
                errors.append(f'Invalid image: {name}')
        elif name.endswith('.jsonl.gz'):
            try:
                with gzip.open(p,'rt') as stream:
                    for line in stream:
                        json.loads(line)
            except Exception:
                errors.append(f'Invalid compressed trace: {name}')
        else:
            errors.append(f'File type is not allowlisted: {name}')
    if errors:
        raise RuntimeError('\n'.join(errors))
    print(f'Publication audit passed: {len(set(names))} files; local Markdown links checked.')

def release(session):
    audit()
    run = (ROOT/'sessions'/session).resolve()
    if run.parent != (ROOT/'sessions').resolve():
        raise ValueError('Invalid session directory')
    manifest = read_json(run/'manifest.json')
    tag = 'models-' + session
    existing = subprocess.run(['gh','release','view',tag,'--repo',REPO],capture_output=True)
    if existing.returncode == 0:
        raise ValueError('Release exists; immutable release assets are never overwritten.')
    if 'release not found' not in existing.stderr.decode().lower():
        raise RuntimeError('Could not safely confirm release absence: '+existing.stderr.decode())
    allowed = {'data','pytorch_variables.pth','policy.pth','policy.optimizer.pth','_stable_baselines3_version','system_info.txt'}
    assets = []
    rows = []
    for stage in manifest['stages']:
        path = (ROOT/stage['model_path']).resolve()
        if path.parent != run/'checkpoints' or path.suffix!='.zip' or digest(path)!=stage['model_sha256']:
            raise ValueError('Checkpoint path or hash mismatch')
        with zipfile.ZipFile(path) as z:
            if set(z.namelist()) != allowed:
                raise ValueError('Unexpected checkpoint ZIP contents; review before publication')
        assets.append(path)
        rows.append({'stage':stage['id'],'sha256':stage['model_sha256'],
                     'url':f'https://github.com/{REPO}/releases/download/{tag}/{path.name}'})
    if not assets:
        raise ValueError('No real checkpoints to publish')
    with tempfile.TemporaryDirectory() as temp:
        notes = Path(temp)/'notes.md'
        notes.write_text(f'# {session} model archive\n\nAll stages, including regressions, are retained. See the classroom session report for evaluation status. These models use gym-super-mario-bros 9.1.0 and nes-py 9.0.1. ROMs and emulator states are not included in these model assets.\n')
        subprocess.run(['gh','release','create',tag,'--repo',REPO,'--target',manifest['source_revision'],
                        '--title',f'{session}: classroom checkpoints','--notes-file',str(notes), *map(str,assets)],check=True)
        downloads = Path(temp)/'downloads'
        subprocess.run(['gh','release','download',tag,'--repo',REPO,'--dir',str(downloads)],check=True)
        for path in assets:
            if digest(downloads/path.name)!=digest(path):
                raise RuntimeError('Downloaded release asset does not match '+path.name)
    write_json(run/'release.json',{'tag':tag,'verified_downloads':True,'models':rows})
    print('Release downloads verified; commit release.json and add its link to the session report.')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['audit','release'])
    p.add_argument('--session')
    a = p.parse_args()
    if a.command=='release':
        if not a.session:
            p.error('--session is required')
        release(a.session)
    else:
        audit()
