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
| Initial policy | 0.00 | 78,581 | 754.4 | 760.0 | 319–1373 | 0/5 |
| 01-stage | 15.01 | 229,622 | 805.8 | 824.0 | 84–1629 | 0/5 |
| 02-stage | 30.01 | 404,899 | 1645.4 | 1629.0 | 1406–2061 | 0/5 |
| 03-stage | 45.01 | 584,549 | 1161.8 | 1121.0 | 887–1498 | 0/5 |
| 04-stage | 60.00 | 752,019 | 2211.6 | 2220.0 | 1628–2769 | 0/5 |
| Final saved policy | 60.00 | 752,019 | 2211.6 | 2220.0 | 1628–2769 | 0/5 |

Progress is furthest horizontal displacement in pixels, not a completion percentage. Missing or incompatible evaluations are excluded, never scored as zero. Cumulative model decisions include previous sessions when resuming.

![Progress, completion and reward across checkpoints](progress.png)

Range bars show trial variability, not confidence intervals. Reward is a separate training signal; it does not establish successful play.

## Initial policy · 0.00 active minutes

Saved stage: `00-resumed`. Model identifier: `37b34760f34bc1101afbf3022c2a009544d0fdba75e132c1501f064ece2de1f2`.

**What changed:** Resumed the pilot final policy and optimizer state. No additional training yet. The five evaluation outcomes exactly reproduce the pilot final evaluation.

**What visibly improved or happened:** The same seed 101 replay passes the first pipe and dies later among walking enemies. The [pilot visual analysis](../2026-09-16-smb3-pilot/ANALYSIS.md) remains applicable to this repeated starting evaluation.

**What still fails:** 0/5 level clears; mean progress 754.4 pixels. The starting policy is still unreliable.

**Hypotheses and limits:** The emulator resets and random state is not restored as a continuous replay during training. This is continued learning from saved weights and optimizer state.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 164–238 |
|---|---|
| ![Beginning, seed 101](00-resumed/trial-101-beginning.gif) | ![Ending, seed 101](00-resumed/trial-101-ending.gif) |

The middle of this trial is omitted from these excerpts; the full action trace is retained.

[All trial measurements](00-resumed/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## 01-stage · 15.01 active minutes

Saved stage: `01-stage`. Model identifier: `c8942d9d616f78297ef12a176793d703026f7a37c85353915aff9fd7951d6e4d`.

**Measured change:** mean progress +51.4 pixels; 0/5 level clears.

| Seed | Progress change since previous stage |
|---|---:|
| 101 | +642 |
| 202 | +505 |
| 303 | -673 · regression |
| 404 | +256 |
| 505 | -473 · regression |

Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.

**What changed:** 15.01 additional active minutes with unchanged PPO settings; cumulative decisions increased from 78,581 to 229,622.

**What visibly improved or happened:** Seed 101 now reaches the raised colored platforms and flying enemies before dying ([contact sheet](review/01-stage-101-ending.png)). Seed 404 crosses the gap before the wooden steps, then falls into the gap between wooden structures ([contact sheet](review/01-stage-404-ending.png)). Mean progress increases from 754.4 to 805.8 pixels.

**What still fails:** 0/5 clears, all deaths. Seeds 303 and 505 regress to only 87 and 84 pixels: their clips show an early jump, contact near the first walking enemy, and death ([303](01-stage/trial-303-ending.gif), [505](01-stage/trial-505-ending.gif)). Improved average progress hides these opening failures.

**Hypotheses and limits:** The clips show different trajectories, not why the network chose them. Five action seeds on the same level cannot establish a stable improvement or reliable completion. Longer jumps or better timing are hypotheses, not established explanations.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 182–256 |
|---|---|
| ![Beginning, seed 101](01-stage/trial-101-beginning.gif) | ![Ending, seed 101](01-stage/trial-101-ending.gif) |

The middle of this trial is omitted from these excerpts; the full action trace is retained.

[All trial measurements](01-stage/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## 02-stage · 30.01 active minutes

Saved stage: `02-stage`. Model identifier: `9ac37ce26177cd7b4ac5f313c0cf46c95130f763a50fad0b207d2002385b251b`.

**Measured change:** mean progress +839.6 pixels; 0/5 level clears.

| Seed | Progress change since previous stage |
|---|---:|
| 101 | +1 |
| 202 | +1237 |
| 303 | +1414 |
| 404 | +0 |
| 505 | +1546 |

Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.

**What changed:** 30.01 additional active minutes, 404,899 cumulative model decisions. PPO settings, observations, actions and reward remain unchanged.

**What visibly improved or happened:** All five trials now reach at least 1,406 pixels. Mean progress rises from 805.8 to 1,645.4 pixels; no paired trial loses progress versus the 15-minute checkpoint. Seed 202 reaches the later brick structures and a red winged enemy ([contact sheet](review/02-stage-202-ending.png)).

**What still fails:** Still 0/5 clears, all deaths. Seed 101 dies among flying enemies near the colored platforms; seed 303 falls into the gap before the wooden steps; seeds 404 and 505 fall into the gap between wooden structures ([404](02-stage/trial-404-ending.gif), [505](02-stage/trial-505-ending.gif)). Seed 202 dies near the winged enemy on a narrow brick column.

**Hypotheses and limits:** The disappearance of opening failures in this five-trial sample is encouraging but does not prove they are eliminated. Repeated falls suggest a location worth testing; the clips do not establish whether timing, perception or the limited action set is responsible.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 189–263 |
|---|---|
| ![Beginning, seed 101](02-stage/trial-101-beginning.gif) | ![Ending, seed 101](02-stage/trial-101-ending.gif) |

The middle of this trial is omitted from these excerpts; the full action trace is retained.

[All trial measurements](02-stage/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## 03-stage · 45.01 active minutes

Saved stage: `03-stage`. Model identifier: `677364433c0fe787d1e67d24030e829d5c3bac677baa16b3ee2e46d054b819db`.

**Measured change:** mean progress -483.6 pixels; 0/5 level clears.

| Seed | Progress change since previous stage |
|---|---:|
| 101 | +9 |
| 202 | -1174 · regression |
| 303 | -3 · regression |
| 404 | -741 · regression |
| 505 | -509 · regression |

Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.

**What changed:** 45.01 additional active minutes, 584,549 cumulative model decisions. Continued PPO with the same settings; no intervention was made after the 30-minute stage.

**What visibly improved or happened:** This stage regresses in evaluation: mean progress falls from 1,645.4 to 1,161.8 pixels. Seed 101 travels only nine pixels farther and still dies near flying enemies; four other seeds lose progress.

**What still fails:** 0/5 clears, all deaths. Seeds 202 and 404 die near the red winged enemy in the open area before the gaps ([202 review](review/03-stage-202-ending.png), [404 review](review/03-stage-404-ending.png)). Seed 303 again falls into the gap before the wooden steps; seed 505 falls in an earlier gap.

**Hypotheses and limits:** A worse checkpoint demonstrates non-monotonic performance on this fixed sample; it does not identify catastrophic forgetting or prove that the learning rate is wrong. Additional action samples and training runs would be needed to characterize the regression.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 125–199 |
|---|---|
| ![Beginning, seed 101](03-stage/trial-101-beginning.gif) | ![Ending, seed 101](03-stage/trial-101-ending.gif) |

These excerpts overlap; they are two views of the same trial.

[All trial measurements](03-stage/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## 04-stage · 60.00 active minutes

Saved stage: `04-stage`. Model identifier: `79b6df4826090153f2fe39a9a55fd0bd6f8c0a664505c5e6671462b948e956cc`.

**Measured change:** mean progress +1049.8 pixels; 0/5 level clears.

| Seed | Progress change since previous stage |
|---|---:|
| 101 | +213 |
| 202 | +1335 |
| 303 | +1271 |
| 404 | +1332 |
| 505 | +1098 |

Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.

**What changed:** 60.00 additional active minutes, 752,019 cumulative model decisions. This completes the approved hour with unchanged settings.

**What visibly improved or happened:** Mean progress recovers to 2,211.6 pixels, versus 1,161.8 at 45 minutes. All five paired trials improve in distance. Seed 303 reaches the goal-card area but remains at the far-right edge until the episode frame limit ([review](review/04-stage-303-ending.png)).

**What still fails:** 0/5 clears: four deaths and one frame limit. Seed 101 falls between wooden structures; seeds 202, 404 and 505 fall at the narrow gap beside the tall pipes. The final additional seeds also yield 0/10 clears (seven deaths, three frame limits), including an opening failure in seed 7010.

**Hypotheses and limits:** The goal-card clip shows Mario to the right of the uncollected card. The last 750 decisions of seed 303 keep x=2792. With no left action he cannot return to it; this is a concrete action-set limitation, not proof that adding left alone will solve the task. The other collision and gap failures remain.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 178–252 |
|---|---|
| ![Beginning, seed 101](04-stage/trial-101-beginning.gif) | ![Ending, seed 101](04-stage/trial-101-ending.gif) |

The middle of this trial is omitted from these excerpts; the full action trace is retained.

[All trial measurements](04-stage/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## Final saved policy · 60.00 active minutes

Saved stage: `final`. Model identifier: `2086c553c2f2f795861a991e8c5b0253154526fdca5524a27833fa890c12b2fa`.

**Measured change:** mean progress +0.0 pixels; 0/5 level clears.

| Seed | Progress change since previous stage |
|---|---:|
| 101 | +0 |
| 202 | +0 |
| 303 | +0 |
| 404 | +0 |
| 505 | +0 |

Paired seeds are reproducible comparisons, but changed policies can consume randomness differently. Five trials cannot establish reliability.

**What changed:** No learning after 04-stage. Its policy weights and this final save have identical SHA-256; the repeated five-seed evaluation matches. This save is not another improvement.

**What visibly improved or happened:** Mean progress recovers to 2,211.6 pixels, versus 1,161.8 at 45 minutes. All five paired trials improve in distance. Seed 303 reaches the goal-card area but remains at the far-right edge until the episode frame limit ([review](review/04-stage-303-ending.png)).

**What still fails:** 0/5 clears: four deaths and one frame limit. Seed 101 falls between wooden structures; seeds 202, 404 and 505 fall at the narrow gap beside the tall pipes. The final additional seeds also yield 0/10 clears (seven deaths, three frame limits), including an opening failure in seed 7010.

**Hypotheses and limits:** The goal-card clip shows Mario to the right of the uncollected card. The last 750 decisions of seed 303 keep x=2792. With no left action he cannot return to it; this is a concrete action-set limitation, not proof that adding left alone will solve the task. The other collision and gap failures remain.

| Beginning · seed 101 · decisions 1–150 | Ending · seed 101 · decisions 178–252 |
|---|---|
| ![Beginning, seed 101](final/trial-101-beginning.gif) | ![Ending, seed 101](final/trial-101-ending.gif) |

The middle of this trial is omitted from these excerpts; the full action trace is retained.

[All trial measurements](final/evaluation.json) · [Every trial’s clips and traces](REPORT.md)

**Discuss:** What changed visibly? Did every trial improve? What extra evidence would distinguish better jump timing from a favorable action sequence?

## Read the failures, too

The detailed report preserves the hold-run-right baseline and the final additional-seed evaluation. Additional seeds test action variation on this same level, not generalization to unseen levels. A final save at the same training time is not another learning interval.

Regenerate this page locally with `python -m smb3_rl.report sessions/SESSION_ID`. Reviewed explanations live in `stage-notes.json`, keyed to the checkpoint hash; generation preserves them and refuses to reuse notes for another model. Future stages are explicitly marked pending visual review until their saved evidence has been inspected.

