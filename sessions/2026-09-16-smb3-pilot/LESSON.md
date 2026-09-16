# Watching Mario learn — Super Mario Bros. 3

## Use this in class

1. Watch the initial policy and predict where Mario will fail.
2. Compare the same seed’s beginning and ending at each checkpoint.
3. Check your impression against every trial, including regressions.
4. Separate what the clips show from hypotheses about why it happened.

[Detailed measurements and all trials](REPORT.md) · [Visual analysis](ANALYSIS.md)

## Learning timeline

Longer sessions save checkpoints approximately every **15 minutes of additional active training**, plus the initial and final models. Evaluation and recording time are measured separately. The table uses actual times, not rounded checkpoint targets. Seeds change sampled actions on the same World 1-1; they do not create new levels.

| Stage | Active minutes in this session | Cumulative model decisions | Mean progress | Median | Min–max | Clears |
|---|---:|---:|---:|---:|---:|---:|
| Initial policy | 0.00 | 0 | 573.6 | 553.0 | 326–887 | 0/5 |
| 01-stage | 9.46 | 78,581 | 754.4 | 760.0 | 319–1373 | 0/5 |
| Final saved policy | 9.46 | 78,581 | 754.4 | 760.0 | 319–1373 | 0/5 |

Progress is furthest horizontal displacement in pixels, not a completion percentage. Missing or incompatible evaluations are excluded, never scored as zero. Cumulative model decisions include previous sessions when resuming.

![Progress, completion and reward across checkpoints](progress.png)

Range bars show trial variability, not confidence intervals. Reward is a separate training signal; it does not establish successful play.

## Initial policy · 0.00 active minutes

Saved stage: `00-untrained`. Model identifier: `e9aeb87e3dcc21c80362ebfad73600a11a8b4ce83cca7621b6d545e90f655d0b`.

**What changed:** No training yet: this is the fresh PPO policy. It samples button combinations from screen observations.

**What visibly improved or happened:** Seed 101 gets past the opening area, reaches the first plant pipe and dies. Some untrained action sequences travel farther; that alone does not demonstrate a learned strategy. See the [reviewed analysis](ANALYSIS.md#initial-untrained-policy).

**What still fails:** All five trials die; none completes the level. Mean progress is 573.6 pixels.

**Hypotheses and limits:** The clip does not establish whether the network recognizes the plant. Random action sequences can make progress.

| Beginning · seed 101 · decisions 1–103 | Ending · seed 101 · decisions 29–103 |
|---|---|
| ![Beginning, seed 101](00-untrained/trial-101-beginning.gif) | ![Ending, seed 101](00-untrained/trial-101-ending.gif) |

These excerpts overlap; they are two views of the same trial.

[All trial measurements](00-untrained/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## 01-stage · 9.46 active minutes

Saved stage: `01-stage`. Model identifier: `5faa99a153ae7a3d1e26bc02a50e84f1e6e66f2a8074847a282f1cabc0a27722`.

**Measured change:** mean progress +180.8 pixels; 0/5 level clears.

| Seed | Progress change since previous stage |
|---|---:|
| 101 | +437 |
| 202 | -7 · regression |
| 303 | -127 · regression |
| 404 | +597 |
| 505 | +4 |

Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.

**What changed:** 9.46 minutes of active training: 78,581 decisions and 4,726 optimizer steps. PPO adjusted its weights using screen observations and the progress/death reward; no scripted demonstrations were supplied.

**What visibly improved or happened:** Seed 101 now passes the first pipe that ended its initial trial and reaches a later area with walking enemies. Mean progress rises to 754.4 pixels. See the [reviewed stage analysis](ANALYSIS.md#trained-stage-01-stage).

**What still fails:** Still 0/5 clears. Seeds 202 and 303 regress. [Seed 202](01-stage/trial-202-ending.gif) still dies near the first plant pipe; [seed 404](01-stage/trial-404-ending.gif) reaches raised platforms and flying enemies, then dies.

**Hypotheses and limits:** Better jump timing is a hypothesis, not a demonstrated cause. More run-and-jump actions appear in these traces, but routes and episode lengths also differ.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 164–238 |
|---|---|
| ![Beginning, seed 101](01-stage/trial-101-beginning.gif) | ![Ending, seed 101](01-stage/trial-101-ending.gif) |

The middle of this trial is omitted from these excerpts; the full action trace is retained.

[All trial measurements](01-stage/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## Final saved policy · 9.46 active minutes

Saved stage: `final`. Model identifier: `2e8a5244bad04fcc92f378637b62bb9a7484186b174de05ee82bd4ccfe87f878`.

**Measured change:** mean progress +0.0 pixels; 0/5 level clears.

| Seed | Progress change since previous stage |
|---|---:|
| 101 | +0 |
| 202 | +0 |
| 303 | +0 |
| 404 | +0 |
| 505 | +0 |

Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.

**What changed:** No additional learning after 01-stage. The final model has identical policy weights, and the repeated five-seed results match. It is an archived final save, not another improvement.

**What visibly improved or happened:** The same behavior replays in the comparable clips. The pilot shows increased average progress, not learned reliable completion.

**What still fails:** Ten additional action seeds yield 0/10 clears, mean progress 667.9 pixels. [Seed 6707](final-additional-trials/trial-6707-ending.gif) still dies near the first walking enemy. See the [final analysis](ANALYSIS.md#final-checkpoint).

**Hypotheses and limits:** These additional trials use the same level. They do not test generalization; neither extra training nor a different action set has yet been tested.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 164–238 |
|---|---|
| ![Beginning, seed 101](final/trial-101-beginning.gif) | ![Ending, seed 101](final/trial-101-ending.gif) |

The middle of this trial is omitted from these excerpts; the full action trace is retained.

[All trial measurements](final/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## Read the failures, too

The detailed report preserves the hold-run-right baseline and the final additional-seed evaluation. Additional seeds test action variation on this same level, not generalization to unseen levels. A final save at the same training time is not another learning interval.

Regenerate this page locally with `python -m smb3_rl.report sessions/SESSION_ID`. Reviewed explanations live in `stage-notes.json`, keyed to the checkpoint hash; generation preserves them and refuses to reuse notes for another model. Future stages are explicitly marked pending visual review until their saved evidence has been inspected.

