# Session 02 — more experience with unchanged PPO settings

The user approved **60 additional active training minutes** after the pilot, with checkpoints approximately every 15 active minutes. Evaluation, recording and publication add wall-clock time. This session resumes the pilot final model; it does not start a new random policy.

## Question

Does more experience with the existing observations, actions and reward improve World 1-1 performance? Preserve failures and regressions. Judge completion separately from horizontal progress and shaped reward.

## Fixed conditions

PPO CNN, stacked screen observations, five rightward/coast actions, four-frame repeat, learning rate 0.00025, 512 rollout decisions, batch size 64 and up to four learning epochs. The configuration and validation identity are checked against the parent before training. No reward, game-adapter or algorithm change is introduced.

The post-pilot source changes were reviewed before resuming: a parent-RSS fallback for restricted macOS child-process enumeration, an explicit source-change provenance flag, and the classroom report generator. These do not alter the policy architecture or learning settings. The manifest records both source fingerprints and the exact parent model hash.

## Evidence protocol

Save an initial resumed model, approximately 15/30/45/60-minute checkpoints and a final save. Evaluate the same five action seeds at each stage. Retain beginning/end GIFs, complete decision traces and episode outcomes. Repeat the hold-run-right baseline and evaluate the final model with ten additional action seeds on the same level. These are not new tracks or independent training runs.

Review saved clips in batches. Explain observed changes, remaining failures and untested hypotheses separately. Pending reviews stay labeled pending. Publish all stages and verified model assets through the permanent classroom index, while retaining the pilot archive.

## Timing and limitations

Active time includes rollout collection and learning; evaluation time is recorded separately. Checkpoint boundaries may slightly overshoot while an optimizer update finishes. The emulator and random state reset on resume, so this is continuation rather than bit-for-bit replay. Memory readings use a documented parent-only fallback if macOS blocks child enumeration.

No training beyond this additional hour is authorized. No paid services or GPT/API calls are used in the gameplay loop.
