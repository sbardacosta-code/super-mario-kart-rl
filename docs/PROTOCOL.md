# Evaluation, recording, and timing protocol

## Task and learning policy

Use Mario on Mario Circuit 1 in Time Trial from one verified local state. Begin with a **fresh** PPO CNN policy, CPU, one thread, seed 123. Four actions: coast, accelerate, accelerate-left, accelerate-right. Each decision repeats its buttons for up to four emulator frames, checking telemetry after each frame. Policy observations are four grayscale 84×84 screenshots. RAM is used only by measurement, reward, and termination logic.

Initial PPO settings: rollout 512 decisions, batch 64, four epochs, learning rate 0.00025, discount 0.99, GAE 0.95, clip 0.2, entropy 0.01, target KL 0.02. These are starting choices, not tuned or proven for this game. A small action space makes early behavior easier to interpret, but omits braking, hopping, drifting, and items. Expand it only as a new documented experiment.

Reward is newly attained ordered high-water checkpoint progress, measured in fractions of a lap, minus 0.0001 per emulated frame. Reverse movement reduces signed position. Revisiting the same checkpoint region earns no new reward. A valid lap needs a full net circuit traversal plus the game's lap evidence. The pipeline checks every frame and rejects unexpected jumps instead of assigning guessed progress. Unit tests cover exploits; the game mapping still needs validation.

## Comparable stages

Save the initial policy before learning, each approximately 900 additional active-training seconds, and the final policy. Evaluate every stage with stochastic policy actions using seeds 101, 202, 303, 404, and 505. Evaluate a hold-accelerate baseline with the same limits. Its behavior may be identical across seeds because it has no action sampling. The initial untrained policy is a randomly initialized PPO network, not a uniform random controller.

Each trial ends at a validated five-lap finish, invalid telemetry, native game termination, or 18,000 emulated action frames (nominally five minutes at the candidate 60 FPS). Failed/stalled trials remain in the denominator if they completed the trial protocol. A wall-time interruption is **incomplete**, not an ordinary failed race. Invalid telemetry excludes that evaluation from comparison and calls for investigation. No early collision heuristic is used.

Seeds change network/action randomness and initialize environment RNG; restoring the same emulator state does **not** create new tracks. Stochastic seeds provide action samples on one saved start, not independent track tests. Repeatable resets may make baseline trials duplicates. Report the trial count and individual results; five trials are descriptive and insufficient to prove reliability. For a later claim of reliable finishing, predeclare a target and uncertainty criterion before collecting a larger independent evaluation.

Final long-session evaluation adds ten seeds (6101 through 7010 as listed in config). These are held-out **action seeds**, not held-out tracks, drivers, or weather. Any future perturbed starting states are a separately versioned protocol and must have compatible action traces. Final audit results remain separate from the five-seed comparison chart.

## Outcomes versus reward

Publish valid laps, whether at least one valid lap was completed, five-lap race completion count/rate, finishing seconds for **completed races only**, and furthest ordered track progress in laps. A reward increase does not establish faster racing. Failure times must never be averaged into successful finishing times. Preserve per-trial data and both signed and maximum progress to show reversals. A higher maximum does not mean Mario ended there.

The current implementation's finish time is elapsed emulated action frames divided by the validated frame rate, from the chosen reset. It is not read directly from the game's HUD. Record any countdown offset and regional timing difference during validation. Reset advances one core frame in the tested Stable-Retro implementation; reset calls are counted separately from action frames.

## Evidence retained

- Model ZIP/SHA-256, parent model identifier, Git revision, code/configuration hashes, dependency freeze, validation identity, seeds, budget, and status.
- Full training decision traces compressed as JSONL; each has chosen action, reward, frame counts, lap/progress, terminal flags, and episode outcome fields. Terminal observations from SB3 may be included. Full evaluation decision traces are JSONL with a reset record and every action through the end or timeout. Raw frame telemetry comes from validation probes.
- All evaluation trials record the first 150 and last 75 decision images as GIF excerpts, plus exact start and final PNGs. These are comparable excerpts, **not full videos**. GIF durations approximate playback at action-repeat/FPS and are rounded; the final decision may contain fewer frames. Traces are authoritative for timing. Captions identify seed and beginning/ending; partial endings are not called completed races.
- Each stage's report gives measurement changes and links to clips/traces. Visual observations and failure locations are added after viewing evidence. Hypotheses must be labeled. Automatic reports explicitly say visual review is pending rather than inventing causes.

## Time and performance accounting

Active training is wall time inside `learn`, including rollout collection, inference, preprocessing, trace writing, and optimizer work. `rollout_seconds` includes collection overhead; `simulation_seconds` measures raw emulator stepping inside that collection. `learning_seconds` measures PPO `train()` calls. Actual optimizer steps are counted with an optimizer hook; update calls, decisions, frames, and reset calls are separate counters. Interrupted partial rollouts can contain decisions that never receive an update; they remain in the trace.

Evaluation process wall time includes startup, inference, trace I/O, and recording. Recording time inside evaluation separately covers image handling/encoding. Checkpoint save time is separate. Memory is peak observed parent+child RSS sampled every 100 ms, which can miss short peaks and double-count shared memory; it is not a hardware allocation guarantee. The pilot's paired same-model/seed recording-on/off tests estimate recording overhead only when both trials are complete with equal frame counts. Run-order, startup, cache, and thermal effects remain limitations.

The native Airstriker smoke test is not the Kart pilot and cannot estimate Kart throughput or a suitable longer budget. The pilot report must supply actual counts/rates and incomplete-test labels before the user chooses more training.
