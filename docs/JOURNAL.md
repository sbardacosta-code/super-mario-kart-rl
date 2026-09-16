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

## 2026-09-16 — Bounded SMB3 pilot completed

The pilot ran for 622.09 seconds overall (10.37 minutes), including 567.54 seconds of active training. It collected 313,478 action frames / 78,581 decisions and made 153 PPO train calls / 4,726 optimizer steps. All planned baseline, checkpoint and ten additional-seed evaluations completed. [Session report](../sessions/2026-09-16-smb3-pilot/REPORT.md) · [Visual analysis](../sessions/2026-09-16-smb3-pilot/ANALYSIS.md).

Fixed-seed mean progress rose from 573.6 to 754.4 pixels, but completion remained 0/5. Two paired trials regressed. The final additional action seeds produced 0/10 clears; this is not a reliable level solver. The validation controller's success is not counted as PPO success. The stage and final policy weights are identical because no learning occurred between those saves.

Raw emulator stepping measured about 1,401 frames/s; end-to-end active training about 552 frames/s; learning updates took 222.26 seconds. The matched one-trial recording test added about 0.220 seconds of wall time, with 0.431 seconds attributed internally to image handling/encoding; cache/scheduling effects mean these values need not equal. Full evaluation subprocess time was 52.68 seconds.

The original memory thread failed on a macOS PermissionError while enumerating children. Training was unaffected, but its peak field is unavailable, not zero. An independent monitor sampled the final 371.8 seconds and observed 495.3 MiB combined parent/child RSS. Early samples cannot be recovered. After the run, the sampler was fixed to retain parent RSS when children are inaccessible, and a regression test was added. Source-change consent for documented runner fixes was added to resume; environment/configuration checks remain strict.

The complete run used source revision `ed371874407e8d96d95e973cc3f26847300265b4`. Later reporting/memory robustness edits did not change its saved models or gameplay results. No longer training budget has been assumed, launched or scheduled.

## 2026-09-16 — Classroom report adapted from the SMB1 teaching format

Read the separate Mario Bros. 1 reporting code and classroom report without modifying that project. Added a teaching-first SMB3 timeline, median/range alongside mean progress, paired seed regression tables, side-by-side beginning/end GIFs with exact decision ranges, and checkpoint-specific observed behavior, remaining failures and hypotheses. Reviewed notes are preserved separately and bound to model hashes; new or unmatched stages explicitly await visual review. All original measurements, models and clips are unchanged.

The existing runner already checkpoints approximately every 900 seconds of additional active training. The short pilot is labeled with its actual 9.46 minutes; no fictional 15-minute interval was inserted and no further training was launched.
