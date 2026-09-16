"""English measurements, charts and comparable gameplay galleries."""
import argparse
from pathlib import Path
import statistics as stats
import os
from .common import ROOT,read_json

def link(path,report):return os.path.relpath(path,report.parent).replace(os.sep,'/')
def summary(e):
    episodes=e['episodes'];times=[x['finish_seconds'] for x in episodes if x['level_complete']]
    return {'n':len(episodes),'clears':sum(x['level_complete'] for x in episodes),
            'mean':stats.mean(x['progress_pixels'] for x in episodes),
            'min':min(x['progress_pixels'] for x in episodes),'max':max(x['progress_pixels'] for x in episodes),
            'reward':stats.mean(x['training_reward_sum'] for x in episodes),
            'finish':stats.mean(times) if times else None,
            'deaths':sum(x['death'] for x in episodes)}
def gallery(e,path,target):
    lines=['| Trial | Progress (pixels) | Outcome | Evidence |','|---|---:|---|---|']
    for ep in e['episodes']+([e['partial_episode']] if e.get('partial_episode') else []):
        evidence=[f"[Trace]({link(path.parent/ep['trace'],target)})"]
        for clip in ep.get('media',[]):
            evidence.append(f"[{Path(clip).stem.split('-')[-1]}]({link(path.parent/clip,target)})")
        lines.append(f"| {ep['seed']} | {ep['progress_pixels']} | {ep.get('termination_reason') or 'partial'} | {' · '.join(evidence)} |")
    if e['episodes']:
        ep=e['episodes'][0]
        lines+=['',f"Comparable example: seed {ep['seed']} (fixed first seed, not selected for best performance).",'']
        for clip in ep.get('media',[]):
            lines += [f"![Seed {ep['seed']} — {Path(clip).stem.split('-')[-1]}]({link(path.parent/clip,target)})",'']
    return lines

def build(run):
    run=Path(run);m=read_json(run/'manifest.json');target=run/'REPORT.md'
    memory_text=f"{m['peak_sampled_rss_bytes']/2**20:.1f} MiB ({m.get('memory_sampling',{}).get('scope','parent_and_children')})"
    if (run/'memory-partial.json').exists():
        memory_text='Full-run peak unavailable: original monitor failed; see partial-coverage measurement below'
    lines=[f"# SMB3 World 1-1 — {m['session_id']}",'',f"Session status: **{m['status']}**. This is a local CPU experiment.",'',
           '[Manifest](manifest.json) · [Configuration](config.json) · [Dependencies](requirements.txt)','',
           '## Time and work measured','',
           '| Measurement | Value |','|---|---:|',
           f"| Session wall time before chart generation | {m.get('wall_seconds',0):.2f} s |",
           f"| Active training | {m['training_seconds']:.2f} s |",
           f"| Rollout collection (includes inference and traces) | {m['rollout_seconds']:.2f} s |",
           f"| Raw emulator stepping inside collection | {m.get('simulation_seconds',0):.2f} s |",
           f"| Learning updates | {m['learning_seconds']:.2f} s |",
           f"| Evaluation subprocesses (includes recording/startup) | {m['evaluation_seconds']:.2f} s |",
           f"| Checkpoint saving | {m['checkpoint_seconds']:.2f} s |",
           f"| Training game frames | {m['training_game_frames']:,} |",
           f"| Agent decisions | {m['training_agent_decisions']:,} |",
           f"| PPO train calls / optimizer steps | {m['learning_update_calls']} / {m['optimizer_steps']} |",
           f"| Sampled peak RSS | {memory_text} |",'',
           'Nested timing fields overlap: raw stepping is part of collection, and collection/learning are part of active training. RSS is sampled every 100 ms; shared pages may be counted twice. Reset/setup frames are excluded from action-frame counters.', '']
    if (run/'memory-partial.json').exists():
        memory=read_json(run/'memory-partial.json')
        lines += [f"**Memory limitation:** the built-in sampler failed on macOS child-process enumeration. The independent monitor observed a peak of {memory['parent_and_children_peak_rss_bytes']/2**20:.1f} MiB across {memory['observed_seconds']:.1f} seconds of late training/evaluation/reporting, starting at {memory['started_at']}. Earlier samples are missing. [Raw partial measurement](memory-partial.json) · [Failure log](logs/memory-monitor-failure.txt).",'']
    if m.get('simulation_seconds'):
        lines += [f"Raw simulation: {m['simulated_frames_per_second']:.0f} frames/s; end-to-end training: {m['training_game_frames']/m['training_seconds']:.0f} frames/s; learning: {m['optimizer_steps_per_second']:.1f} optimizer steps/s.",'']
    lines += ['## Outcomes across stages','','![Outcome and reward charts](progress.png)','',
              'Error bars show the range across the five trials, not confidence intervals. Progress is furthest horizontal displacement from the start, in pixels, not a percentage of the level. Completion is measured independently. Finishing time uses action frames / 60, only for completed levels. Training reward is plotted separately and is not a success rate.','']
    points=[];previous=None
    for stage in m['stages']:
        lines += [f"## {stage['id']}",'',f"{stage['training_seconds']/60:.2f} additional active minutes. Model SHA-256: `{stage['model_sha256']}`.",'']
        path=ROOT/stage['evaluation'] if stage.get('evaluation') else None
        if path is None or not path.exists():
            lines+=['**Evaluation pending.** Missing results are not zeros.',''];continue
        e=read_json(path)
        lines += [f"Evaluation **{e['status']}**: {len(e['episodes'])}/{len(e['seeds'])} finished trials. [Full measurements]({link(path,target)}).",'']
        comparable=e['status']=='complete' and e['protocol']==m['config'] and e['model_sha256']==stage['model_sha256'] and e['seeds']==m['config']['evaluation_seeds']
        if comparable:
            s=summary(e);points.append((stage['training_seconds']/60,s,stage['id']))
            lines += [f"**Observed measurements:** {s['clears']}/{s['n']} clears; {s['deaths']} deaths; mean progress {s['mean']:.1f} pixels (range {s['min']}–{s['max']}); mean shaped reward {s['reward']:.3f}.",'']
            if previous:
                lines += [f"Mean progress changed by {s['mean']-previous['mean']:+.1f} pixels; completion count changed by {s['clears']-previous['clears']:+d}. Improvement is not assumed, and five action samples are a small evaluation.",'']
            previous=s
        else:lines += ['Excluded from comparable charts because evaluation is incomplete, invalid, or uses a different protocol.','']
        lines += gallery(e,path,target)+['']
    for key in ['run_right_baseline','final_additional_trials']:
        if not m.get(key):continue
        path=ROOT/m[key];e=read_json(path)
        lines += [f"## {key.replace('_',' ').capitalize()}",'',f"Status: {e['status']}. [Measurements]({link(path,target)}).",'']
        if e['episodes']:
            s=summary(e);lines += [f"{s['clears']}/{s['n']} clears; mean progress {s['mean']:.1f} pixels. Additional seeds are action samples on the same level, not unseen levels.",'']
        lines += gallery(e,path,target)+['']
    lines += ['## Recording overhead','']
    overhead=[]
    for key in ['overhead_without_recording','overhead_with_recording']:
        if m.get(key):
            p=ROOT/m[key];e=read_json(p);overhead.append(e)
            lines += [f"- [{key.replace('_',' ')}]({link(p,target)}): {e['status']}, {e['game_frames']} frames, {e['wall_seconds']:.3f} s total; {e['recording_seconds']:.3f} s image handling/encoding."]
    if len(overhead)==2 and all(e['status']=='complete' for e in overhead) and overhead[0]['game_frames']==overhead[1]['game_frames']:
        lines += ['',f"Matched-trial wall-time difference: {overhead[1]['wall_seconds']-overhead[0]['wall_seconds']:+.3f} s. This single pair includes cache and scheduling noise; it is an estimate, not a stable benchmark."]
    lines += ['','## Interpretation','']
    if (run/'ANALYSIS.md').exists():lines += ['[Read the visual stage-by-stage analysis](ANALYSIS.md).']
    else:lines += ['Visual review pending. Measurements alone do not establish why Mario made a mistake. No causal story is invented.']
    if (run/'release.json').exists():lines += ['','[Verified downloadable model checkpoints](release.json).']
    target.write_text('\n'.join(lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    fields=[('mean','Mean furthest progress (pixels)'),('clears','Level clears (out of 5)'),('finish','Mean finish time, successes only (s)'),('reward','Mean shaped reward — separate signal')]
    for ax,(field,label) in zip(axes.flat,fields):
        pairs=[(t,s[field]) for t,s,_ in points if s[field] is not None]
        if pairs:
            ax.plot(*zip(*pairs),marker='o')
            if field=='mean':
                ax.errorbar([t for t,_,_ in points],[q['mean'] for _,q,_ in points],
                            yerr=[[q['mean']-q['min'] for _,q,_ in points],[q['max']-q['mean'] for _,q,_ in points]],
                            fmt='none',capsize=5,alpha=.5)
                ax.set_ylim(bottom=0)
            if field=='clears':ax.set_ylim(0,5)
        else:
            ax.text(.5,.5,'No completed levels' if field=='finish' else 'No comparable evaluations',ha='center',transform=ax.transAxes)
            ax.set_yticks([])
            ax.set_xlim(0,max([p[0] for p in points],default=1) or 1)
        ax.set(xlabel='Additional active training (minutes)',ylabel=label);ax.grid(alpha=.25)
    fig.suptitle('SMB3 World 1-1 — all stages, including regressions')
    fig.savefig(run/'progress.png',dpi=150);plt.close(fig)
    update_index()

def update_index():
    text=['# Super Mario Bros. 3 — classroom index','',
          'This project now teaches **Super Mario Bros. 3, World 1-1**. The original repository name and this permanent URL are retained at the user’s request. The separate Mario Bros. 1 project is untouched.','',
          '[Teacher guide](../TEACHER_GUIDE.md) · [Setup and resume](../SETUP.md) · [Journal](../JOURNAL.md) · [Protocol](../PROTOCOL.md)','',
          '## Session archive','','| Session | Status | Evidence |','|---|---|---|',
          '| Kart preparation (historical) | Archived; no Kart training | [Original archive](../../archive/kart/README.md) |',
          '| SMB3 validation | See validation report | [Controls, resets, and false-clear correction](../../sessions/2026-09-16-smb3-validation/REPORT.md) |']
    for p in sorted((ROOT/'sessions').glob('*/manifest.json')):
        m=read_json(p);text.append(f"| {m['session_id']} | {m['status']} | [Report, chart, and gameplay](../../sessions/{m['session_id']}/REPORT.md) |")
    text += ['','## Teacher access','','Public reports, charts, GIFs and model Releases need only a browser and internet access; no GitHub account is required. '
             'Local replay/training uses the pinned Python packages. The installed gym-super-mario-bros package supplies the game data locally; no game ROM is uploaded to this repository or its Releases. '
             'No paid cloud computing or GPT/API calls are used in the gameplay loop.','',
             'A longer training budget must be chosen after the bounded pilot; no three-hour run is assumed.']
    (ROOT/'docs/classroom/README.md').write_text('\n'.join(text)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('session',type=Path,nargs='?');a=p.parse_args()
    build(a.session) if a.session else update_index()
