# Super Mario Bros. 3 RL classroom lab

**[Permanent classroom index](https://github.com/sbardacosta-code/super-mario-kart-rl/blob/main/docs/classroom/README.md)**

This repository now teaches **Super Mario Bros. 3, World 1-1**. At the user's request, it reuses the existing `super-mario-kart-rl` folder, GitHub repository, and classroom index URL. The separate Super Mario Bros. 1 project and task are not modified.

The original Kart preparation is preserved in [archive/kart](archive/kart/README.md), the historical setup session, and Git tag `kart-pre-smb3-20260916`. No Kart training occurred. Current code lives in `smb3_rl/`; the archived Kart scripts are historical, not the active workflow.

## First pilot completed

The 10.37-minute pilot included 9.46 minutes of active training. Mean progress on five fixed evaluation seeds increased from 573.6 to 754.4 pixels, but the trained policy cleared 0/5 levels and 0/10 additional-seed trials. Two paired trials regressed. [Read the report and watch the gameplay](sessions/2026-09-16-smb3-pilot/REPORT.md). The memory measurement has partial coverage, documented in the report. No longer run has been started.

## Classroom materials

- [Session reports, charts and gameplay gallery](docs/classroom/README.md)
- [Teacher guide and discussion questions](docs/TEACHER_GUIDE.md)
- [Setup, pilot, stop/save/resume](docs/SETUP.md)
- [Evaluation and timing protocol](docs/PROTOCOL.md)
- [Validation evidence](sessions/2026-09-16-smb3-validation/REPORT.md)
- [Experiment journal](docs/JOURNAL.md)
- [Publication and model downloads](docs/PUBLISHING.md)

## Local setup

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pytest -q
```

The installed `gym-super-mario-bros==9.1.0` package includes the game data locally. There is no separate ROM-import step for this experiment. No ROM, emulator state, or bundled game package is uploaded to this repository or model Releases.

The agent learns from screenshots with a fresh PPO CNN policy. Evaluation records all trials, including failures, incomplete attempts and regressions. The bounded pilot is followed by a user choice of the longer training budget; no three-hour run is assumed.

Training, evaluation, recording, checkpointing and chart generation are self-contained local scripts. There are no GPT/API calls in the gameplay loop and no paid cloud computing.
