# SMB3 validation

The current validation evidence is [here](../sessions/2026-09-16-smb3-validation/REPORT.md). It includes real gameplay and the upstream false-clear regression. The previous Kart checklist is retained [in the archive](../archive/kart/docs/VALIDATION.md).

Before training, `smb3_rl.common.require_validated` checks a passing record against the current configuration, adapter hash, bundled ROM SHA-256, installed environment source, and dependency versions. Validation scripts check controls, repeated resets, pixel stacks, death, genuine goal/map return, timeout and progress-reuse defenses. Fingerprints detect stale evidence; they do not replace visual review.

The successful scripted controller is used only to validate the completion signal. It is neither the untrained baseline nor a demonstration used by PPO. Preserve its action sequence and distinguish its success from learned-model results.
