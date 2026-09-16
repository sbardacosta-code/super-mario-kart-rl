# Reference inspection and provenance

Inspected on September 16, 2026. These are integration leads, not claims that their installations work unchanged.

| Source | Finding and use |
|---|---|
| [Original Mario teaching project](https://github.com/sbardacosta-code/mario-rl) | Local revision `f9820ba672197e4a21d6e72285bf9da3abc02d78`. Read `lesson_session.py`, `lesson_eval.py`, `lesson_report.py`, and release-publishing logic. Reused design ideas: immutable stage directories, model hashes, action traces, beginning/end clips, protocol comparison, explicit incomplete results, and a permanent teacher index. Original files were not modified or copied wholesale. The reference's long-session default was not carried over. |
| [Stable-Retro](https://github.com/Farama-Foundation/stable-retro) | Current source supports native Apple Silicon; [official Mac instructions](https://github.com/Farama-Foundation/stable-retro/blob/main/docs/macos_installation.md). Installed wheel 1.0.1, using `stable_retro` and `rgb_array`. The installed source shows reset returns empty info; this adapter reads `data.lookup_all()` after reset. |
| [arvganesh/super-mario-kart-ppo](https://github.com/arvganesh/super-mario-kart-ppo) | Revision `5a731f36883b4a7425965c6909dc08f33a82ef57`. Tianshou-era PPO and 2023 Docker guidance are not the new SB3 stack. Candidate checkpoint/lap RAM addresses and ROM hash informed the validation template. Its named start is described as Mario / Time Trials / Mario Circuit, but the state was not downloaded or validated. Its Lua reward was inspected, not reused. |
| [esteveste/gym-SuperMarioKart-Snes](https://github.com/esteveste/gym-SuperMarioKart-Snes) | Legacy gym-retro, TensorFlow 1.13.2, and stable-baselines instructions are not compatible evidence for modern SB3. Its ROM hash matches the other reference. State names alone do not verify gameplay settings. No binaries downloaded. |
| [Gymnasium](https://gymnasium.farama.org/api/env/) | Modern reset and five-value step API; terminated and truncated have different meanings. Locally tested version 1.3.0. |
| [Stable Baselines3 PPO](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) | PPO configuration and pixel-policy implementation; locally tested version 2.9.0. |

`integrations/MarioKart-Snes-v0/data.json` reproduces candidate RAM metadata from the MIT-licensed arvganesh integration. Its license is preserved in [THIRD_PARTY_LICENSES.txt](../THIRD_PARTY_LICENSES.txt). The ROM hash is compatibility metadata only. No ROM, save state, reference gameplay media, or reference trained policy is distributed.
