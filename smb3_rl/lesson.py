"""Teaching-first stage comparison, generated solely from saved evidence."""
from pathlib import Path
import statistics
from .common import ROOT, read_json


def comparable(e, stage, config):
    return (e.get('status') == 'complete' and e.get('protocol') == config
            and e.get('model_sha256') == stage['model_sha256']
            and e.get('seeds') == config['evaluation_seeds']
            and [x['seed'] for x in e.get('episodes', [])] == config['evaluation_seeds']
            and all(x.get('complete_trial') for x in e['episodes']))


def clip_pair(e, path, target, seed):
    from .report import link
    ep = next((x for x in e['episodes'] if x['seed'] == seed), None)
    if ep is None:
        return [f'Comparable seed {seed}: complete trial unavailable; no substitute chosen.', '']
    clips = {Path(x).stem.split('-')[-1]: x for x in ep.get('media', [])}
    if not all(k in clips for k in ('beginning', 'ending')):
        return [f'Comparable seed {seed}: recording unavailable.', '']
    n = ep['decisions']; end_start = max(1, n - 74); begin_end = min(150, n)
    return [f'| Beginning · seed {seed} · decisions 1–{begin_end} | Ending · seed {seed} · decisions {end_start}–{n} |',
            '|---|---|',
            f"| ![Beginning, seed {seed}]({link(path.parent/clips['beginning'], target)}) | ![Ending, seed {seed}]({link(path.parent/clips['ending'], target)}) |", '',
            ('These excerpts overlap; they are two views of the same trial.' if end_start <= begin_end else
             'The middle of this trial is omitted from these excerpts; the full action trace is retained.'), '']


def build_lesson(run):
    from .report import link, summary
    run = Path(run); m = read_json(run/'manifest.json'); target = run/'LESSON.md'
    notes_path = run/'stage-notes.json'
    notes = read_json(notes_path) if notes_path.exists() else {}
    lines = ['# Watching Mario learn — Super Mario Bros. 3', '',
             '## Use this in class', '',
             '1. Watch the initial policy and predict where Mario will fail.',
             '2. Compare the same seed’s beginning and ending at each checkpoint.',
             '3. Check your impression against every trial, including regressions.',
             '4. Separate what the clips show from hypotheses about why it happened.', '',
             '[Detailed measurements and all trials](REPORT.md) · [Visual analysis](ANALYSIS.md)' if (run/'ANALYSIS.md').exists() else '[Detailed measurements and all trials](REPORT.md)', '',
             '## Learning timeline', '',
             'Longer sessions save checkpoints approximately every **15 minutes of additional active training**, plus the initial and final models. Evaluation and recording time are measured separately. The table uses actual times, not rounded checkpoint targets. Seeds change sampled actions on the same World 1-1; they do not create new levels.', '',
             '| Stage | Active minutes in this session | Cumulative model decisions | Mean progress | Median | Min–max | Clears |',
             '|---|---:|---:|---:|---:|---:|---:|']
    rows=[]
    for stage in m['stages']:
        path=ROOT/stage['evaluation'] if stage.get('evaluation') else None
        e=read_json(path) if path and path.exists() else None
        valid=e is not None and comparable(e,stage,m['config'])
        s=summary(e) if valid else None
        label=('Initial policy' if stage['id'].startswith('00-') else 'Final saved policy' if stage['id']=='final' else stage['id'])
        metrics=f"{s['mean']:.1f} | {statistics.median(x['progress_pixels'] for x in e['episodes']):.1f} | {s['min']}–{s['max']} | {s['clears']}/{s['n']}" if s else 'Pending or noncomparable | — | — | —'
        lines.append(f"| {label} | {stage['training_seconds']/60:.2f} | {stage['total_model_decisions']:,} | {metrics} |")
        rows.append((stage,path,e,s,label))
    lines += ['', 'Progress is furthest horizontal displacement in pixels, not a completion percentage. Missing or incompatible evaluations are excluded, never scored as zero. Cumulative model decisions include previous sessions when resuming.', '',
              '![Progress, completion and reward across checkpoints](progress.png)', '',
              'Range bars show trial variability, not confidence intervals. Reward is a separate training signal; it does not establish successful play.', '']
    previous=None
    for stage,path,e,s,label in rows:
        lines += [f"## {label} · {stage['training_seconds']/60:.2f} active minutes", '',
                  f"Saved stage: `{stage['id']}`. Model identifier: `{stage['model_sha256']}`.", '']
        if not s:
            lines += ['**Evaluation incomplete, unavailable, or noncomparable.** No learning claim is made.', ''];continue
        if previous:
            old={x['seed']:x for x in previous['episodes']}
            deltas=[(x['seed'],x['progress_pixels']-old[x['seed']]['progress_pixels']) for x in e['episodes']]
            lines += [f"**Measured change:** mean progress {s['mean']-summary(previous)['mean']:+.1f} pixels; {s['clears']}/{s['n']} level clears.", '',
                      '| Seed | Progress change since previous stage |','|---|---:|']
            lines += [f'| {seed} | {d:+d}' + (' · regression' if d<0 else '') + ' |' for seed,d in deltas]
            lines += ['', 'Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.', '']
        previous=e
        note=notes.get(stage['id'])
        if note and note.get('model_sha256')==stage['model_sha256']:
            for field,title in [('changed','What changed'),('observed','What visibly improved or happened'),('fails','What still fails'),('uncertain','Hypotheses and limits')]:
                lines += [f"**{title}:** {note[field]}", '']
        else:
            lines += ['**Visual explanation pending review.** The measurements above are observed outcomes; they do not explain the network’s reasoning. Review the clips and traces before adding a learning claim.', '']
        lines += clip_pair(e,path,target,m['config']['evaluation_seeds'][0])
        lines += [f"[All trial measurements]({link(path,target)}) · [Every trial’s clips and traces](REPORT.md)", '',
                  '**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?', '']
    lines += ['## Read the failures, too', '',
              'The detailed report preserves the hold-run-right baseline and the final additional-seed evaluation. Additional seeds test action variation on this same level, not generalization to unseen levels. A final save at the same training time is not another learning interval.', '',
              'Regenerate this page locally with `python -m smb3_rl.report sessions/SESSION_ID`. Reviewed explanations live in `stage-notes.json`, keyed to the checkpoint hash; generation preserves them and refuses to reuse notes for another model. Future stages are explicitly marked pending visual review until their saved evidence has been inspected.', '']
    target.write_text('\n'.join(lines)+'\n')
