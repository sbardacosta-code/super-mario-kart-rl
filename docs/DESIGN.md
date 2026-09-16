# Architecture and current limits

`integration.py` imports a checksum-matched local game and probes raw frame-level controls/RAM. `env.py` converts pixels into the policy's observation and translates four actions into emulator button masks. `progress.py` measures ordered progress, valid laps, and completion. `session.py` bounds training, saves stages, launches isolated evaluation processes, and captures provenance. `evaluate.py` freezes a model and records comparable trials. `report.py` builds English charts and galleries from saved measurements. `publish.py` audits source/results and uploads verified checkpoint assets when requested.

Training and evaluation use separate processes because emulator cores can have global state; evaluation never mutates the training policy. The training environment remains paused during evaluation. PPO weights are saved before evaluation. Resume is a new session and begins from the reset state, not the previous emulator frame. Checkpoints approximately every 15 active minutes are independent of evaluation costs.

## Verified without a Kart ROM

- Native dependency installation and version resolution.
- Stable-Retro's included Airstriker core can reset and step using RGB arrays.
- Gymnasium's environment checker and a small SB3 CNN PPO update pass on that test game.
- Synthetic ordered-progress tests reject backward/repeated-boundary reward farming.
- Synthetic screen-wrapper tests verify stacking, reset bookkeeping, timeout, and terminal frame accounting.
- Documentation, archival layout, CLI prerequisites, and publication checks can be prepared.

## Still requires the game

Actual SNES core/game operation; exact ROM revision; character/mode/track state; controls; checkpoint/lap addresses and semantics; reset reliability; regional frame timing; finish detection; full PPO session behavior; real clips and traces; 10–15-minute pilot throughput, memory and overhead; learning outcomes. No test above substitutes for these.

The integration's candidate addresses come from a prior project, not from measurements on this Mac. Strict adjacency can reject legitimate skipped checkpoints if the map differs; treat that as a validation issue, not a failed driving policy. Full circuit accounting is conservative and may undercount if the saved start is misaligned. Validation must resolve such discrepancies before learning.

Automatic explanations deliberately cover numerical comparisons only. Visual analysis remains pending until a person or Codex reviews the clips outside the gameplay loop. Changes to a policy's behavior are observations; causal claims require controlled comparisons. All config/source changes invalidate the local validation fingerprint.

The reporting index uses GitHub's built-in Markdown rendering. There is no custom hosted website, GitHub Pages deployment, paid cloud service, or API dependency in gameplay. The permanent index links to separately archived sessions. Binary models go to Releases after their ZIP contents and downloaded hashes are verified.
