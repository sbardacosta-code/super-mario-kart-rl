# Chronological experiment journal

## 2026-09-16 — Kart preparation (historical)

The native Stable-Retro stack and classroom workflow were prepared, but the Super Mario Kart ROM was missing. No Kart learning occurred. The complete original journal, source, configuration and setup report are preserved [in the archive](../archive/kart/docs/JOURNAL.md).

## 2026-09-16 — User-directed migration to SMB3

The user chose Super Mario Bros. 3 and explicitly requested reuse of the Kart folder, repository and permanent classroom index. The Mario Bros. 1 repository and task are excluded from edits. The active package is now `smb3_rl`; the public URL keeps its original name so teacher bookmarks remain valid.

Installed gym-super-mario-bros 9.1.0 and nes-py 9.0.1 in this project's own virtual environment. Stable-Retro's pyglet constraint conflicted with nes-py; removed Stable-Retro from the active environment and preserved its dependency lock in the archive. NES package installation provides the local game data; no ROM is committed or uploaded.

Started with World 1-1, a fresh screen-based PPO policy, five rightward actions, four-frame repeat, and CPU/one thread. Task outcomes changed from racing laps to horizontal progress and level completion. The initial baseline is now hold right+B, without jumping. A 12-minute pilot target retains the original user-authorized 10–15-minute scope; further training needs a new budget choice.

## 2026-09-16 — False-clear failure found before training

A scripted validation sequence produced `clear=true` at frame 369 near x=352, while screenshots showed death/fade-out by the first pipe. The installed environment tested timer zero and nonzero map fields before a life decrement appeared. The adapter now also requires the actual World 1-1 map-panel coordinates for completion. The same sequence is then classified as death at frame 370. This is a concrete example of a measurement bug that could reward failure.

Periodic button probes and a bounded scripted action search were used to find a genuine goal traversal for validation. These are environment checks, not PPO learning; their actions are not demonstrations supplied to PPO. See the validation report for the final successful replay and its limits.

## Pilot results

The pilot session's manifest, report and visual analysis will be linked from the permanent index. Record actual training/update/evaluation time and outcome changes, including regressions. Do not replace requested minutes with assumed active time, or interpret successful validation-controller play as learned-policy skill.
