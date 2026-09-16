# SMB3 World 1-1 experiment protocol

## Learning task

Mario starts at x=24 in World 1-1. First aim: pass progressively farther obstacles. Primary outcome: finish the level, followed by repeatable finishing. Race laps from the earlier Kart plan do not apply. Report horizontal high-water displacement, milestone counts, level completion rate, and finishing time for successes only. Progress is in pixels, not a fabricated percentage of the level.

A fresh PPO CNN receives four 84×84 grayscale screenshots. Actions: coast, right, right+A, right+B, right+A+B. A is jump and B is run. Every decision advances up to four emulator frames, stopping immediately on a terminal/truncated frame. No pause, select, left, down, pipe entry, or menu actions are available. This small action set is easy to inspect but limits recovery and excludes alternative routes.

Initial PPO configuration: 512 rollout decisions; batch 64; four epochs; learning rate 0.00025; gamma 0.99; GAE 0.95; clip 0.2; entropy coefficient 0.01; target KL 0.02; seed 123; CPU/one thread. Parameters are starting choices, not proven optimal. The training model never receives validation-controller demonstrations or RAM features.

Reward per frame: 0.01 × newly attained horizontal pixels − 0.0001, with −1 on death and +5 on validated completion. Backtracking and revisiting an earlier x position earn no new progress. Map-return coordinates do not count as level progress. Score and powerups do not independently grant this shaped reward. The package's original reward is logged separately and not used for learning. A reward increase does not establish more completed levels.

## Outcome correction

The installed SMB3 environment initially misclassified a death fade-out as a clear when its timer became zero while life loss was not yet posted. This was observed at raw frame 369 near x=352. Our subclass requires the actual World 1-1 map-panel coordinates (y=0x20, x=0x40) in addition to the package's alive-return checks. The same sequence then terminates as a death, not success. A separate successful scripted traversal must show the goal sequence and map return. This correction is specific to World 1-1 and the restricted actions; do not reuse it on another level without validation.

## Fixed evaluation

Save the initial model before learning, checkpoints approximately every 900 additional active-training seconds, and the final model. The short pilot may have no 15-minute interior checkpoint; its end-of-training stage and final checkpoint can contain identical weights. Evaluate every checkpoint with stochastic policy seeds 101, 202, 303, 404 and 505. Use the same pixel wrappers, start, action set and episode limit. Evaluate hold-run-right (right+B, no jumping) as the platformer equivalent of hold-accelerate.

Each episode ends on confirmed death/clear, invalid telemetry, or 12,000 action frames (nominally 200 seconds). Package setup/reset frames are not action frames. Death animation frames before the life decrement remain included. Completion time is frames/60 from the reset, not the HUD clock or real wall time. Completed failed trials count in success-rate denominators; wall-time interrupted trials are incomplete and excluded from comparable aggregate charts. Invalid telemetry stops training and requires investigation.

Seeds change PPO action sampling and seed the environment RNG. They do not create different levels; the emulator restores the same start. The hold-run-right baseline can be identical across seeds. Five trials describe behavior but do not prove reliable or general play. An additional final audit uses ten held-out action seeds on the same level; it tests new action samples, not generalization to unseen levels.

## Evidence and timing

Every evaluation retains complete action traces, episode outcomes, initial/final PNGs, and the first 150 / last 75 decision images as GIF excerpts. These excerpts are not full videos; traces bridge the gap. GIF durations approximate 60-FPS game time at four-frame actions, with rounding. Every stage is preserved, including regressions and incomplete recordings. Seed 101 is displayed as the fixed comparison example, not selected for best behavior; all trials are linked.

Training also writes compressed full-decision JSONL traces. Stage manifests preserve model identifiers, source revision/hashes, dependency freeze, configuration, validation identity, seeds, parent model and actual budgets. Model weights plus optimizer state are in Release ZIPs; no ROM/state is included.

Active training is wall time inside `learn`, including rollout collection, inference, tracing and updates. Raw emulator stepping is a measured subset of collection. PPO train-call time and actual optimizer-step count are separate. Evaluation process time includes startup, trace writing and recording; image encoding time is separately reported within evaluation. Checkpoint save time and 100-ms-sampled peak parent+child RSS are recorded. Shared memory can be counted twice and very short peaks can be missed.

Paired same-model/seed recording-on/off tests estimate recording overhead only when both finish with equal frame counts. Cache, temperature, subprocess startup and run order remain limitations. Reports show measured rates rather than assuming a training speed. Additional training requires the user's post-pilot budget choice.
