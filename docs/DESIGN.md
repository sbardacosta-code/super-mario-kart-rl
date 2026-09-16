# Active architecture

`env.py` adapts the locally installed SMB3 emulator, corrects the World 1-1 false-clear signal, preprocesses pixels and measures high-water progress. `validate.py` collects repeatable real-game evidence before learning. `session.py` bounds local PPO training and saves stages. `evaluate.py` runs independent frozen-policy subprocesses and records action traces/clips. `report.py` generates English charts and galleries. `publish.py` checks public files and verifies model Release downloads.

Training and evaluation use separate emulator processes. The training environment pauses during evaluation. No GPT/API calls occur in these loops. Codex analyzes saved milestones in batches outside training.

Continuation restores model and optimizer state, starts a new session and resets the emulator. It does not reproduce RNG state or a discarded partial rollout exactly. Runtime configuration/source changes require a new documented experiment. Every stage, including failures and regression, stays in its own session folder.

The package can register other SMB3 levels, but only World 1-1 is validated here. Horizontal progress is appropriate to this initial side-scrolling course; it does not automatically extend to vertical, autoscrolling or branching levels. A small rightward action set limits recovery. The environment's setup code uses map-entry helpers before the saved starting point; no such RAM intervention happens in the PPO gameplay loop.

The former Kart architecture is preserved in `archive/kart`; it is not runnable with the active NES dependency environment without restoring its own lock separately.
