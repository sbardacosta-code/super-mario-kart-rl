from copy import deepcopy
from pathlib import Path
from smb3_rl.common import ROOT, read_json
from smb3_rl.lesson import comparable, clip_pair, build_lesson

RUN=ROOT/'sessions/2026-09-16-smb3-pilot'

def test_comparison_rejects_missing_or_duplicate_trials():
    m=read_json(RUN/'manifest.json');s=m['stages'][0];e=read_json(ROOT/s['evaluation'])
    assert comparable(e,s,m['config'])
    broken=deepcopy(e);broken['episodes'].pop()
    assert not comparable(broken,s,m['config'])
    broken=deepcopy(e);broken['episodes'][1]=broken['episodes'][0]
    assert not comparable(broken,s,m['config'])

def test_fixed_seed_and_clip_boundaries():
    p=RUN/'00-untrained/evaluation.json';e=read_json(p)
    text='\n'.join(clip_pair(e,p,RUN/'LESSON.md',101))
    n=e['episodes'][0]['decisions']
    assert f'decisions {max(1,n-74)}–{n}' in text
    assert 'excerpts overlap' in text
    assert 'no substitute' in '\n'.join(clip_pair(e,p,RUN/'LESSON.md',999))

def test_review_notes_persist_and_mismatch_is_not_reused(tmp_path):
    import json
    m=read_json(RUN/'manifest.json');(tmp_path/'manifest.json').write_text(json.dumps(m))
    notes=read_json(RUN/'stage-notes.json');notes['00-untrained']['model_sha256']='wrong'
    p=tmp_path/'stage-notes.json';p.write_text(json.dumps(notes));before=p.read_bytes()
    build_lesson(tmp_path);text=(tmp_path/'LESSON.md').read_text()
    assert p.read_bytes()==before
    assert 'Visual explanation pending review' in text
    assert '9.46' in text and '202 | -7 · regression' in text
    assert 'No additional learning after 01-stage' in text
