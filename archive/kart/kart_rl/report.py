"""Generate English charts and a gallery without external API calls."""
import argparse
from pathlib import Path
import os
import statistics
from .common import ROOT, read_json

def link(path, report):
    return os.path.relpath(path, report.parent).replace(os.sep, '/')

def build(run):
    run = Path(run)
    m = read_json(run/'manifest.json')
    target = run/'REPORT.md'
    text = [f"# Session {m['session_id']}", '', f"Status: **{m['status']}**.", '',
            'All stages are retained, including regressions and incomplete evaluations.', '',
            f"Active training: {m['training_seconds']:.2f} s. Evaluation processes: {m['evaluation_seconds']:.2f} s.",
            f"Rollout collection: {m['rollout_seconds']:.2f} s. Learning: {m['learning_seconds']:.2f} s.",
            f"Training frames: {m['training_game_frames']}; decisions: {m['training_agent_decisions']}; optimizer steps: {m['optimizer_steps']}.", '',
            '[Full manifest](manifest.json) · [Configuration](config.json) · [Dependencies](requirements.txt)', '',
            'Finishing time is measured from the validated reset using emulated frames, and only for completed races. '
            'It is not wall-clock time or automatically the exact in-game timer.', '',
            '## Progress charts', '', '![Progress by stage](progress.png)', '', '## Stage comparison gallery', '']
    points = []
    previous = None
    for stage in m['stages']:
        text += [f"### {stage['id']}", '', f"Additional active training: {stage['training_seconds']/60:.2f} minutes. Model SHA-256: `{stage['model_sha256']}`.", '']
        evaluation = ROOT/stage['evaluation'] if stage.get('evaluation') else None
        if evaluation is None or not evaluation.exists():
            text += ['**Evaluation pending.** No outcome or visible improvement is claimed.', '']
            continue
        e = read_json(evaluation)
        text += [f"Evaluation: **{e['status']}**; {len(e['episodes'])}/{len(e['seeds'])} completed trials. [Measurements]({link(evaluation, target)}).", '']
        comparable = e['status']=='complete' and e['protocol']==m['config'] and e['seeds']==m['config']['evaluation_seeds'] and e['model_sha256']==stage['model_sha256']
        if comparable:
            episodes = e['episodes']
            rate = sum(x['race_complete'] for x in episodes)/len(episodes)
            laps = statistics.mean(x['valid_laps'] for x in episodes)
            progress = statistics.mean(x['track_progress_laps'] for x in episodes)
            times = [x['finish_seconds'] for x in episodes if x['race_complete']]
            point = (stage['training_seconds']/60, rate, laps, progress, statistics.mean(times) if times else None)
            points.append(point)
            text += [f"**Measured:** mean valid laps {laps:.2f}; race completion {rate:.0%}; mean furthest progress {progress:.2f} laps.", '']
            if previous:
                text += [f"Compared with the previous complete stage, completion changed by {(rate-previous[1])*100:+.0f} percentage points and mean valid laps by {laps-previous[2]:+.2f}. This small sample can fluctuate.", '']
            previous = point
        else:
            text += ['Excluded from comparison charts. Missing trials are not zeros, and protocol changes are not treated as comparable.', '']
        text += ['**Visible behavior:** review pending. These measurements alone do not identify why Mario made a mistake. '
                 'Add a dated visual review with trial, frame range, observed movement, and separately labeled hypotheses.', '']
        for episode in e['episodes'] + ([e['partial_episode']] if e.get('partial_episode') else []):
            text += [f"Trial {episode['seed']}: {'complete trial' if episode['complete_trial'] else 'partial trial'}; [full action trace]({link(evaluation.parent/episode['trace'], target)}).", '']
            for clip in episode.get('media', []):
                text += [f"![Trial {episode['seed']} — {Path(clip).stem}]({link(evaluation.parent/clip, target)})", '']
    text += ['## Baselines and final audit', '']
    for key in ['accelerate_baseline','overhead_without_recording','overhead_with_recording','final_additional_trials']:
        if m.get(key):
            epath = ROOT/m[key]
            e = read_json(epath)
            text += [f"- [{key.replace('_', ' ').capitalize()}]({link(epath,target)}): {e['status']}, {len(e['episodes'])}/{len(e['seeds'])} trials."]
    text += ['', 'Additional seeds are additional action samples on the same track and saved start; they do not establish transfer to new tracks.', '']
    target.write_text('\n'.join(text))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2,2,figsize=(10,7),layout='constrained')
    labels = ['Race completion rate','Mean valid laps','Mean furthest progress (laps)','Mean finish time — completed races (s)']
    for i, ax in enumerate(axes.flat,1):
        available = [(p[0],p[i]) for p in points if p[i] is not None]
        if available:
            ax.plot(*zip(*available), marker='o')
        else:
            ax.text(.5,.5,'No complete comparable measurements',ha='center',va='center',transform=ax.transAxes,wrap=True)
        ax.set(xlabel='Additional active training (minutes)',ylabel=labels[i-1])
        ax.grid(alpha=.2)
    fig.suptitle(f"Session {m['session_id']} — all comparable stages")
    fig.savefig(run/'progress.png', dpi=150)
    plt.close(fig)
    update_index()

def update_index():
    text = ['# Super Mario Kart RL — classroom index', '',
            '**Current status: awaiting the user-supplied ROM and validated Kart integration.**', '',
            'This permanent index stays at the same URL as new sessions are added. No Kart training or gameplay results exist yet.', '',
            '[Teacher guide](../TEACHER_GUIDE.md) · [Setup](../SETUP.md) · [ROM requirements](../ROM.md) · [Experiment journal](../JOURNAL.md) · [Evaluation protocol](../PROTOCOL.md)', '',
            '## Archived sessions', '',
            '| Session | Status | Report |', '|---|---|---|',
            '| 2026-09-16 setup | ROM missing; native smoke test passed | [Setup report](../../sessions/2026-09-16-setup/REPORT.md) |']
    for manifest in sorted((ROOT/'sessions').glob('*/manifest.json')):
        m = read_json(manifest)
        text.append(f"| {m['session_id']} | {m['status']} | [Report and gallery](../../sessions/{m['session_id']}/REPORT.md) |")
    if list((ROOT/'sessions').glob('*/manifest.json')):
        text[2] = '**Session archive:** consult each report for validation status, incomplete evaluations, and results.'
        text[4] = 'This permanent index stays at the same URL as new sessions are added.'
    text += ['', '## Access', '', 'Reading this public GitHub index, reports, charts, and GIFs requires only a browser and internet access; no GitHub account or ROM is needed. '
             'Download release assets for checkpoints. Running the emulator requires a compatible local ROM and validated local save state, Python dependencies, and a Mac or another tested platform. '
             'Models alone do not include the game. No paid service is required.', '']
    (ROOT/'docs/classroom/README.md').write_text('\n'.join(text))

def setup_chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder = ROOT/'sessions/2026-09-16-setup'
    r = read_json(folder/'compatibility.json')
    fig, ax = plt.subplots(figsize=(9,4),layout='constrained')
    values = [r['test_game_step_seconds'],r['test_ppo_seconds']]
    bars = ax.barh(['600 test-game frames\n(with preprocessing)',
                   '128-decision PPO smoke run\n(collection + learning)'], values,
                   color=['#286b8f','#b26227'])
    ax.bar_label(bars,labels=[f'{v:.3f} s' for v in values],padding=8)
    ax.set_xlim(0,max(values)*1.35)
    ax.set_xlabel('Measured wall time (seconds)\nDifferent short workloads; excludes startup and model construction.\nNot a sustained Kart benchmark.',fontsize=10)
    ax.set_title('Native Mac compatibility smoke test — Airstriker, not Mario Kart')
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(folder/'smoke-durations.png',dpi=150,bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('session', type=Path, nargs='?')
    p.add_argument('--setup-chart', action='store_true')
    a = p.parse_args()
    if a.setup_chart:
        setup_chart()
    else:
        build(a.session) if a.session else update_index()
