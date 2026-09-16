# Setup and operation

## Tested machine and dependencies

Apple M4 MacBook Pro, 10 CPU cores, 16 GB memory, macOS 26.6.2, arm64 Python 3.13.15. Native wheel installation succeeded for Stable-Retro 1.0.1, Gymnasium 1.3.0, Stable Baselines3 2.9.0, PyTorch 2.14.0, and NumPy 2.5.3. Full versions are pinned in [requirements-lock.txt](../requirements-lock.txt). CPU with one PyTorch thread is the initial reproducible setting. MPS was unavailable in the tested process; no GPU performance claim is made.

Use Python 3.13 from your local Python installation, then run the setup commands in the README. The project's existing `.venv` on the preparation Mac is already installed. It uses a Python runtime from the earlier local teaching workspace; do not delete that runtime without recreating this virtual environment using another Python 3.13 installation. The lock is the tested Mac environment, not a promise of cross-platform support.

Stable-Retro now uses `import stable_retro`; `import retro` emits a deprecation warning. Always specify `render_mode='rgb_array'` in headless scripts. The default human display failed in this execution context. There is no need to install Docker for the successful smoke test.

## Supply and validate the game

1. Read [ROM requirements](ROM.md). Import your local file:

   ```sh
   .venv/bin/python -m kart_rl.integration import-rom /absolute/path/to/your-game.sfc
   ```

2. Create a local start state for Mario / Mario Circuit 1 / Time Trial. Use a copy of the configuration with `state: null` under `private/` to boot the game. `kart_rl.integration probe` runs a JSON button/frame plan and can save a state with `--save-state private/integrations/MarioKart-Snes-v0/MarioCircuit1-Mario-TimeTrial.state`. No menu timing is assumed before observing this ROM. A suitable start is the beginning of lap one with the countdown finished; verify it visually and calibrate lap/checkpoint values.
3. Complete [validation](VALIDATION.md). Calibrate `checkpoint_count`, checkpoint numbering/order, `lap_start`, and frame timing. If mapping is noncontiguous or direction is reversed, change the adapter and tests; do not guess a count to bypass the gate.
4. Commit the tested source/configuration, record validation with file hashes, and rerun the tests. Training rejects missing or stale evidence.

## Authorized next step: bounded pilot

Only after the game checks pass:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python -m kart_rl.session \
  --session YYYY-MM-DD-pilot --pilot \
  --budget-note 'User requested a 10–15-minute benchmark and training pilot'
```

The pilot targets a 12-minute total wall-clock session, reserving time for evaluation. It includes a fresh PPO initial checkpoint, baseline evaluations, paired recording-overhead attempts, one training segment, a stage checkpoint, and a final checkpoint. Training time is whatever remains after baseline costs, capped at 10 minutes; the pilot can be shorter if stopped or if prerequisites fail. Finishing the current optimizer update, saving, and report generation can add a small shutdown tail. Evaluations have wall limits and may be incomplete. Report actual duration, never label requested duration as observed training time. No long training follows automatically.

After reviewing the pilot, ask the user to choose the longer active training budget. There is deliberately no default long budget and no automatic three-hour run. Once chosen, replace `MINUTES` and the note:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python -m kart_rl.session \
  --session YYYY-MM-DD-session-01 --active-minutes MINUTES \
  --budget-note 'User selected MINUTES active training minutes after reviewing the pilot'
```

Evaluation, saving, and reporting add wall time beyond that active-training budget. A 15-minute stage boundary may finish a PPO update just after the target time. Checkpoints do not depend on a guessed frames-per-second rate. Keep the Mac awake and connected to power; optional `caffeinate -i` can prefix the Python command. Training is entirely local.

## Stop, save, resume

- Press Ctrl-C once, or create `sessions/SESSION/STOP` from another terminal. The runner stops at the next decision, saves a final checkpoint, and retains pending evaluation labels. During an update it finishes that update before checking the stop signal. During evaluation it interrupts the child process and preserves partial evidence.
- Do not use force quit if a normal stop is possible. Sudden power loss can lose the current segment, but earlier checkpoint stages remain available.
- Resume in a **new session directory** with an explicit newly approved budget:

  ```sh
  .venv/bin/python -m kart_rl.session --session YYYY-MM-DD-session-02 \
    --resume sessions/PRIOR/checkpoints/final.zip --active-minutes MINUTES \
    --budget-note 'User selected this additional budget'
  ```

- Model weights and optimizer state load from the checkpoint. The emulator resets and RNG state/partial rollout are not restored bit-for-bit. This is a documented continuation, not an exact replay. `parent_model_sha256` links the sessions. The original fresh untrained baseline remains archived.
- Incomplete evaluations can be rerun into a **new** directory using `kart_rl.evaluate`; preserve the original attempt and document the replacement. Do not overwrite past evidence.
- Rebuild a session report with `.venv/bin/python -m kart_rl.report sessions/SESSION`. Add a human/Codex visual analysis after examining saved clips and traces. No analysis runs inside gameplay.

Use `--help` on each module for flags. When a gate fails, follow the named prerequisite; do not disable validation to produce results.
