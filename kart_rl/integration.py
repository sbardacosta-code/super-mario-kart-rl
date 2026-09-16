"""Import a user-supplied ROM locally, or capture frame-level validation evidence."""
import argparse
import gzip
import hashlib
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
from .common import ROOT, read_json, write_json, digest, now
from .env import raw_env

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='configs/mario-circuit-1.json')
    sub = p.add_subparsers(dest='command', required=True)
    imp = sub.add_parser('import-rom')
    imp.add_argument('rom', type=Path)
    probe = sub.add_parser('probe')
    probe.add_argument('--plan', type=Path, required=True, help='JSON list of {buttons: [...], frames: N}')
    probe.add_argument('--output', type=Path, required=True)
    probe.add_argument('--save-state', type=Path, help='Local .state at the end; never published')
    args = p.parse_args()
    config = read_json(ROOT / args.config)
    dest = ROOT / config['integration_dir'] / config['game']
    if args.command == 'import-rom':
        data = args.rom.read_bytes()
        if hashlib.sha1(data).hexdigest() != config['rom_sha1']:
            p.error('ROM checksum mismatch. No patching or header stripping was performed. See docs/ROM.md.')
        dest.mkdir(parents=True, exist_ok=True)
        if (dest / 'rom.sfc').exists():
            p.error('Local ROM already exists; it was preserved.')
        for src in (ROOT / 'integrations' / config['game']).glob('*'):
            if src.suffix in ('.json', '.sha'):
                shutil.copy2(src, dest / src.name)
        (dest / 'rom.sfc').write_bytes(data)
        print('ROM verified and stored locally. State creation and validation are still required.')
        return
    args.output.mkdir(parents=True, exist_ok=False)
    # Before a state exists, use a separate config with state=null to boot ROM.
    env = raw_env(config)
    report = {'status': 'running', 'at': now(), 'plan': read_json(args.plan), 'samples': [],
              'buttons': env.buttons, 'config': config}
    try:
        image, info = env.reset(seed=123)
        info = {**env.data.lookup_all(), **info}
        Image.fromarray(image).save(args.output / 'start.png')
        report['reset_info'] = info
        frame = 0
        for segment in report['plan']:
            if not set(segment['buttons']).issubset(env.buttons) or not 0 < segment['frames'] <= 36000:
                raise ValueError('Invalid plan segment')
            buttons = np.array([int(b in segment['buttons']) for b in env.buttons], dtype=np.int8)
            for _ in range(segment['frames']):
                image, reward, term, trunc, info = env.step(buttons)
                frame += 1
                report['samples'].append({'frame': frame, 'buttons': segment['buttons'], **info,
                                          'terminated': bool(term), 'truncated': bool(trunc)})
                if frame % 60 == 0:
                    Image.fromarray(image).save(args.output / f'frame-{frame:06d}.png')
                if term or trunc:
                    raise RuntimeError('Unexpected raw termination during probe')
        Image.fromarray(image).save(args.output / 'end.png')
        if args.save_state:
            target = args.save_state.resolve()
            if not target.is_relative_to((ROOT / 'private').resolve()) or target.exists():
                raise ValueError('Save states must be new files under private/')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(gzip.compress(env.em.get_state()))
        report['status'] = 'complete'
    except Exception as exc:
        report.update(status='incomplete', error=repr(exc))
        raise
    finally:
        env.close()
        # Convert numpy scalar telemetry to JSON primitives.
        import json
        report = json.loads(json.dumps(report, default=lambda x: x.item()))
        write_json(args.output / 'probe.json', report)

if __name__ == '__main__':
    main()
