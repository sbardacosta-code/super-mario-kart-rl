# Game file to supply

Supply your own **Super Mario Kart for SNES** cartridge image as an uncompressed `.sfc` file (or a byte-identical `.smc` file). This is the SNES game, not Mario Kart 64, Super Circuit, a video, a save file, or a modified ROM hack.

The candidate integrations both specify this exact SHA-1:

```text
47e103d8398cf5b7cbb42b95df3a3c270691163b
```

The checksum, rather than the filename or a guessed region label, is the compatibility requirement. Region/revision and cartridge-header details have not been independently verified from a user-supplied game. The importer compares the exact supplied bytes; it does not silently strip a copier header, patch the ROM, or accept an alternate revision. If your file differs, retain it locally and investigate the revision before adapting the integration.

Check locally without uploading the game:

```sh
shasum -a 1 /absolute/path/to/your-game.sfc
.venv/bin/python -m kart_rl.integration import-rom /absolute/path/to/your-game.sfc
```

The importer writes to `private/integrations/MarioKart-Snes-v0/rom.sfc`. `private/`, common ROM extensions, save states, emulator movies, and model archives are ignored by Git. The publication audit also rejects non-allowlisted files and non-text payloads. Never put game files in Releases or attach them to an issue.

You will also need a locally created, verified Stable-Retro save state selecting **Mario, Mario Circuit 1, Time Trial**. It will live beside the ROM as `MarioCircuit1-Mario-TimeTrial.state`. Save states are not published. A named state from another integration is not accepted as proof of its character, mode, or compatibility.

The reference repositories contain ROM entries in their trees. Only selected text metadata was inspected; their ROM files and save states were not downloaded or copied. The public classroom can read reports and watch clips without a ROM. To reproduce gameplay or use a downloaded checkpoint, a teacher needs their own compatible ROM and validated local state.
