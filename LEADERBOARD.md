# GitHub Pages leaderboard bridge

VRChat string loading downloads a response body; it does not run JavaScript
from an `index.html`. This bridge therefore publishes compact JSON inside
`leaderboard/index.html` on GitHub Pages. A scheduled GitHub Action fetches the
public rankings API and rebuilds that file.

## Installed in `stefanus-ai-tech/emychess-eval-feed`

The repository keeps its existing Stockfish feed on the `gh-pages` branch. The
leaderboard workflow lives on the default `main` branch, fetches the rankings
API, and commits only `leaderboard/index.html` into `gh-pages`.

1. Commit and push `leaderboard-proxy/generate_leaderboard.py`, this README, and
   `.github/workflows/update-vrchat-leaderboard.yml` to `main`.
2. Optionally set the repository Actions variable `LEADERBOARD_API_URL`. When it
   is absent, the workflow uses the public VRChess Indonesia rankings endpoint.
3. Keep GitHub Pages deployed from the `gh-pages` branch root.
4. Run **Update VRChat leaderboard** once from the Actions tab.

The published URL expected by the Unity installer is:

`https://stefanus-ai-tech.github.io/emychess-eval-feed/leaderboard/index.html`

The workflow republishes every ten minutes. The public read endpoint needs no
API token. Do not put a mutation/admin token in this Pages output.

## Wire the Unity prefab

After Unity finishes importing the package, stop ClientSim/Play Mode, select
the intended EmyChess board in the Hierarchy, then run:

`Tools > EmyChess > Install Remote Leaderboard`

The installer creates `Runtime/Prefabs/RemoteLeaderboard.prefab`, places one
instance in the active scene, shows ten rows, refreshes every five minutes, and
adds a manual refresh button.

## Published JSON format

The file is named `index.html` only so the requested GitHub Pages route ends in
that name. Its response body is JSON, not an HTML application:

```json
{
  "format": "EMYCHESS_LEADERBOARD_V1",
  "updated_at": "2026-08-30T12:00:00Z",
  "players": [
    {
      "rank": 1,
      "username": "Alice",
      "rating": 1520,
      "games": 15,
      "wins": 10,
      "draws": 2,
      "losses": 3
    }
  ]
}
```

The generator accepts ranking arrays under `rankings`, `players`, or `data`,
including a nested `data` object. Player fields may use `username`, `name`, or
`player`; game count may use `games_played`, `total_matches`, or `games`.
