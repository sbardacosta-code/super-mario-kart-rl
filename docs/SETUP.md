# Setup, pilot, stop and resume

The active project is SMB3, despite the retained `super-mario-kart-rl` folder and GitHub name. Run commands from that folder. The Mario Bros. 1 repository is not needed.

## Environment

Test machine: Apple M4, 16 GB RAM, macOS 26.6.2, arm64 Python 3.13.15. CPU / one PyTorch thread is used. Install `requirements-lock.txt` in `.venv`; run `pip check` and the tests. The active NES dependencies are gym-super-mario-bros 9.1.0, nes-py 9.0.1, Gymnasium 1.3.0 and Stable Baselines3 2.9.0. Stable-Retro was removed from this environment because its pyglet requirement conflicts with nes-py. Its old dependency lock remains in the Kart archive.

The existing `.venv` uses a pre-existing Python runtime. To make the project independent of that runtime's location, recreate `.venv` using any compatible arm64 Python 3.13 installation. No game files need to be taken from the Mario Bros. 1 project.

## Validation

```sh
.venv/bin/python -m smb3_rl.validate
```

The validation suite checks ten repeatable resets/replays, controls, pixels, exact timeout frames, death and completion, reward reuse, and a regression for the upstream false-clear bug. It uses a saved scripted validation action sequence to reproduce a genuine successful run; this controller is not PPO and is not used to train the model. See the validation report for evidence and limitations. The archived JSON contains the exact runtime/ROM/adapter/configuration fingerprints. A changed adapter or configuration requires revalidation. If revalidating on a new machine, copy the published scripted action list into `.cache/clear-controller-actions.json` first. Do not overwrite published evidence: run in a new validation folder and update the configuration for a new protocol when changes are substantive.

## Bounded pilot

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python -m smb3_rl.session \
  --session YYYY-MM-DD-smb3-pilot --pilot \
  --budget-note 'User requested the bounded 10–15-minute local pilot'
```

This targets a 12-minute overall session, with at most ten active training minutes and time reserved for evaluation. Setup, baseline and recording costs reduce available training time. An optimizer update/save can add a small shutdown tail. Actual time is recorded; the requested budget is never reported as time measured. A short aborted run is labeled accordingly.

After the pilot, the user chooses the longer active-training budget. There is no default long budget:

```sh
.venv/bin/python -m smb3_rl.session --session YYYY-MM-DD-smb3-session-02 \
  --resume sessions/PRIOR/checkpoints/final.zip --active-minutes MINUTES \
  --budget-note 'User selected MINUTES additional active training minutes after the pilot'
```

To start a new fresh-policy experiment, omit `--resume`. Continue only with the same configuration, environment identity and source hash; a change requires a new documented experiment. The runner checks for committed source before starting. Do not edit runtime code while a session is running.

## Stop and save

Press Ctrl-C once, or create `sessions/SESSION/STOP`. The runner checks at the next decision, saves a final model atomically, and marks skipped evaluations pending. During a PPO update, it finishes the current update first. During evaluation it interrupts the child and retains partial evidence. Avoid force quit: the current segment can be lost, although previously saved checkpoints remain.

Resume always uses a **new session directory** with an explicit additional budget. Weights and optimizer state load; the emulator resets and the random-number/partial-rollout state is not restored exactly. This is continuation, not bit-for-bit replay. The parent checkpoint SHA-256 links the sessions.

## Evaluate and report

```sh
.venv/bin/python -m smb3_rl.evaluate --config sessions/SESSION/config.json \
  --model sessions/SESSION/checkpoints/final.zip --output sessions/SESSION/evaluation-retry-01 --seconds 300
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python -m smb3_rl.report sessions/SESSION
```

Always use a new evaluation output directory. Keep the original failed/incomplete attempt and journal the retry. Add visual interpretation in that session's `ANALYSIS.md`; the report links it without overwriting it. No GPT calls are made automatically. Publication is a separate deliberate step after reviewing saved evidence.
