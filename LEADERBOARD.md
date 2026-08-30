# GitHub Pages leaderboard bridge

VRChat string loading downloads response text; it does not run JavaScript from
an `index.html`. This bridge therefore publishes an intentionally plain-text
`leaderboard/index.html` on GitHub Pages. A scheduled GitHub Action fetches the
public rankings API and rebuilds that file.

## Installed in `stefanus-ai-tech/emychess-eval-feed`

The repository keeps its existing Stockfish feed on the `gh-pages` branch. The
leaderboard workflow lives on the default `main` branch, fetches the rankings
API, and commits only `leaderboard/index.html` into `gh-pages`.

1. Commit and push `leaderboard-proxy/generate_leaderboard.py`, this README, and
   `.github/workflows/update-vrchat-leaderboard.yml` to `main`.
2. In GitHub, open **Settings > Secrets and variables > Actions > Variables**
   and add `LEADERBOARD_API_URL`. Its value must be the complete public endpoint,
   for example `https://your-api.example/index.php?rankings=1`.
3. Keep GitHub Pages deployed from the `gh-pages` branch root.
4. Run **Update VRChat leaderboard** once from the Actions tab.

The published URL expected by the Unity installer is:

`https://stefanus-ai-tech.github.io/emychess-eval-feed/leaderboard/index.html`

The workflow republishes every ten minutes. The public read endpoint needs no
API token. Do not put a mutation/admin token in this Pages output.

## Wire the Unity prefab

After Unity finishes importing the package, stop ClientSim/Play Mode and run:

`Tools > EmyChess > Install Remote Leaderboard`

The installer uses the URL above, shows ten rows, refreshes every five minutes,
and adds a manual refresh button. The `RemoteLeaderboard` component exposes the
URL, row limit, placement-independent display references, and refresh interval
for world-specific changes.

## Published text format

The file is named `index.html` only so the requested GitHub Pages route ends in
that name. Its body is tab-separated text, not an HTML application:

```text
EMYCHESS_LEADERBOARD_V1
updated_at	2026-08-30T12:00:00Z
rank	username	rating	games	wins	draws	losses
1	Alice	1520	15	10	2	3
```

The generator accepts ranking arrays under `rankings`, `players`, or `data`,
including a nested `data` object. Player fields may use `username`, `name`, or
`player`; game count may use `games_played`, `total_matches`, or `games`.
