# Required pre-training validation

**Status: pending ROM.** Synthetic accounting tests do not validate the game. Every row below needs real emulator evidence before `kart_rl.session` is permitted to run.

| Check identifier | Required evidence and acceptance condition |
|---|---|
| character_track_mode | Start screenshots show Mario, Mario Circuit 1, and Time Trial; no CPU opponents; correct initial lap. |
| controls | Separate coast, accelerate, accelerate-left, accelerate-right traces and clips; verify the B button and steering direction from actual behavior. Exclude pause, reset, menu, contradictory directions. |
| reset_repeatability | At least 10 resets; compare raw pixel/RAM hashes, then replay identical actions for 120 frames. Same state/action sequence produces matching traces. Seeds do not silently change the track. |
| screen_observations | Gymnasium checker passes; uint8 stack is `(4,84,84)`; stack clears on reset; policy receives pixels only, not RAM features. |
| checkpoint_order | A controlled full forward lap reveals every contiguous cyclic checkpoint in order. Document count, numbering, wrap, direction, and no skipped regions at frame-level sampling. |
| backward_no_reward | Controlled reverse traversal and reverse finish-line crossing receive no new positive progress; no valid lap or completion. |
| oscillation_no_reward | Repeatedly cross one boundary and the finish line both ways; previously rewarded progress cannot be earned again. |
| lap_vs_hud | At least two full laps: ordered traversal and RAM lap change agree with visible HUD; initial counter offset and update delay documented. |
| five_lap_finish | A manually controlled completed Time Trial confirms five valid laps and the finish display; no premature finish from an isolated counter jump. |
| termination_and_timeout | Verify success termination, failed/corrupt telemetry truncation, fixed frame timeout, reset after each, and correct final observation/trace. |
| frame_timing | Verify region/core frame rate and start timing; explain elapsed emulated time versus HUD timer; retain frame-by-frame evidence. |

## Probe without training

A plan is a JSON list, for example `[ {"buttons": ["B"], "frames": 120} ]`. Do not use this example to infer that B has been verified. Run:

```sh
.venv/bin/python -m kart_rl.integration probe --plan private/plan.json --output private/probe-001
```

The probe stores raw frame-level telemetry, the button list, start/end images, and images every 60 frames. Use a separate configuration with `state: null` to boot the game before making a state:

```sh
.venv/bin/python -m kart_rl.integration --config private/boot.json probe \
  --plan private/menu-plan.json --output private/menu-probe-001 \
  --save-state private/integrations/MarioKart-Snes-v0/MarioCircuit1-Mario-TimeTrial.state
```

Construct menu plans incrementally from screenshots. A saved state is a gzip-compressed `env.em.get_state()` from the same installed core. There is no verified menu macro yet. The probe intentionally has no arbitrary RAM writes.

## Validation record

After reviewing evidence, create `private/validation.json` with `identity` from `kart_rl.common.identity(config)` and a `checks` mapping containing **every identifier above**. Each entry must have `passed: true` and a nonempty `evidence` list of `{ "path": "private/relative-file", "sha256": "actual-file-digest" }`. Include a reviewer name/date and prose observations in the record. Archive a ROM-free summary and shareable screenshots/traces in that session's report. The validation file itself is retained locally and copied into session provenance as metadata; it does not include ROM bytes.

The gate checks the ROM/state/configuration/source/integration hashes and every evidence-file digest. This prevents accidental stale validation. It cannot prove that a reviewer made a correct judgment: visual and controlled replay review remains essential. Do not set `passed` merely to unblock a command.

Changes to code, dependencies, checkpoint mapping, action set, state, or ROM require renewed validation. The present tracker assumes adjacent, increasing, cyclic checkpoint IDs; nonadjacent jumps or disagreement with the backward flag invalidate the episode. Real-game failures of this assumption require an adapter change with fresh tests and a journal entry.
