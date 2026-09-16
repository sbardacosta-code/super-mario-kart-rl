# Publication and permanent access

Use this URL for every class, including future training sessions:

**https://github.com/sbardacosta-code/super-mario-kart-rl/blob/main/docs/classroom/README.md**

It is a public GitHub Markdown index. No account is needed to read it. Keeping the repository name, `main` branch, and this path stable keeps the index stable. Each session lives in `sessions/SESSION/`; append new sessions instead of replacing old results. Models are separate Release downloads; local model files are Git-ignored. No placeholder models or fictional clips are published.

## Publish source, reports, and gameplay samples

From this repository, review the files, then:

```sh
.venv/bin/python -m kart_rl.report
.venv/bin/python -m kart_rl.publish audit
git add README.md .gitignore pyproject.toml requirements-lock.txt THIRD_PARTY_LICENSES.txt kart_rl tests configs integrations docs sessions
git diff --cached --check
git diff --cached --stat
git commit -m 'Archive classroom experiment evidence'
git push origin main
```

The audit rejects common game/model payloads, non-allowlisted binary files, broken local Markdown links, invalid image files, and credential-like text. It is defense in depth, not a guarantee against all mistakes. Review newly staged paths. Do not use `git add -f` for ignored files. Do not upload local save states or emulator movies.

## Publish real model checkpoints

After a session has created model stages:

```sh
.venv/bin/python -m kart_rl.publish release --session SESSION
```

This explicitly invokes GitHub release publication outside the gameplay loop. The script validates model hashes and ZIP members, refuses an existing release, uploads every saved stage including regressions, downloads all assets to a temporary directory, and checks their SHA-256 hashes. It writes `sessions/SESSION/release.json` only after verification. Add a link to that file and the Release in the session report, then commit and push. It never uploads arbitrary ZIPs, ROMs, save states, or the private folder. Do not count publication as complete if the command fails or download hashes disagree.

## Verify before saying “published”

Compare local `git rev-parse HEAD` with `gh api repos/sbardacosta-code/super-mario-kart-rl/commits/main --jq .sha`. Fetch the public index through GitHub and confirm its links point to the committed session paths. Run the local Markdown-link audit on that same revision. Check all new images/traces are in the remote tree. For a Release, use its verified downloads and manifest. Archive the verification result and identify the verified commit. If access is interrupted, say publication is pending rather than inferring success.

No GitHub Actions training job, paid hosting service, or paid cloud machine is configured. The public index is GitHub's existing repository view, not a separate website requiring deployment.
