# Chronological experiment journal

## 2026-09-16 — Session 00: prepare without a ROM

**Question:** Can the classroom infrastructure and native Mac stack be prepared while the game file is missing?

**Inspection:** Read the earlier local Mario project at revision `f9820ba672197e4a21d6e72285bf9da3abc02d78`, preserving it. Adapted archival, reporting, clips, and provenance ideas in new English-language code. GitHub inspection found no existing `sbardacosta-code/super-mario-kart-rl` repository. Prepared a separate nested folder with its own Git history, leaving the current Pac-Man project untouched.

**Machine:** Apple M4, 10 CPU cores, 16 GB memory, macOS 26.6.2. Installed a fresh arm64 Python 3.13.15 environment. Chose CPU/one thread for an initial reproducible profile. MPS was not available to the smoke-test process; no GPU workaround was assumed.

**Compatibility investigation:** Current Stable-Retro supplied a native Mac arm64 wheel. Older reference projects use different RL libraries and older installation paths. No Docker was necessary for the successful included-game test. Both Kart references list the same SHA-1, but their RAM addresses and save states remain unverified candidates. Only text metadata was fetched, despite ROM entries being present upstream.

**Setup failures and fixes:** Initial shell network access was sandbox-restricted; authorized dependency/GitHub operations used the network-enabled tool path. The default human renderer could not find a display and raised `IndexError`; explicitly selecting RGB arrays fixed the smoke test. Inspection of installed Stable-Retro showed an empty info dictionary at reset, so the adapter reads current RAM telemetry through the data interface. The deprecated `retro` import was replaced by `stable_retro`.

**Observed results:** The included Airstriker environment passed the Gymnasium check and 600 measured frame steps. A 128-decision CNN PPO smoke run changed finite policy weights. See [raw compatibility measurements](../sessions/2026-09-16-setup/compatibility.json). This is not SNES/Mario Kart validation or the requested 10–15-minute pilot.

**Parameter choices:** Four initial driving actions, four repeated frames, four 84×84 grayscale observations, a small PPO rollout, one thread, conservative ordered-progress reward. These simplify inspection and reduce early configuration complexity; their effectiveness is untested. Repeated boundary crossings must not renew reward, and a lap needs both circuit traversal and game evidence. Synthetic tests cover these rules and exact terminal-frame counts.

**Recording decisions:** Archive initial, approximately 15-minute, and final checkpoints; fixed action-seed trials; start/end screenshots and GIF excerpts; full decision traces; independent outcome metrics; separate collection/update/evaluation/recording counters. Store models in verified Releases later. Never silently replace a failed stage. The runner creates measurement summaries and explicitly leaves visual interpretation pending.

**Current lesson:** A working ML package installation is only one layer of evidence. A reward implementation can pass synthetic tests while the game's memory mapping is wrong. The missing ROM blocks all claims about Kart behavior.

**Next actions:** Supply checksum-matched ROM; create and verify the exact start; validate controls/resets/observations/checkpoints/laps/termination and timing; run the bounded pilot; publish measured evidence; ask the user to choose a longer budget. No three-hour run is authorized or scheduled.

## Future entries

Append a dated section for each setup change, pilot, training session, evaluation correction, parameter change, failure, or regression. Include links to immutable session evidence, the decision made, what was observed, hypotheses clearly labeled, and what remains unknown. Rebuilding a chart does not rewrite historical conclusions.
