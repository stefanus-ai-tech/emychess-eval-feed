#!/usr/bin/env python3
"""Fetch VRChess rankings and emit compact JSON for VRChat string loading."""

from __future__ import annotations

import json
import pathlib
import sys
import urllib.request
from datetime import datetime, timezone
from typing import Any


FORMAT_MARKER = "EMYCHESS_LEADERBOARD_V1"


def find_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if not isinstance(value, dict):
        return []

    for key in ("rankings", "players"):
        rows = value.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]

    nested = value.get("data")
    if nested is not None:
        return find_rows(nested)
    return []


def first(row: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return default


def clean_text(value: Any, default: str = "") -> str:
    text = str(default if value is None else value)
    return text.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def clean_integer(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError, OverflowError):
        return default


def build_output(payload: Any) -> str:
    rows = find_rows(payload)
    if not rows:
        raise ValueError("API response did not contain a rankings/player array")

    players: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        players.append(
            {
                "rank": clean_integer(first(row, "rank", "position", default=index), index),
                "username": clean_text(first(row, "username", "name", "player", default="Unknown"), "Unknown"),
                "rating": clean_integer(first(row, "rating", "elo", default=0)),
                "games": clean_integer(first(row, "games_played", "total_matches", "games", default=0)),
                "wins": clean_integer(first(row, "wins", default=0)),
                "draws": clean_integer(first(row, "draws", default=0)),
                "losses": clean_integer(first(row, "losses", default=0)),
            }
        )

    output = {
        "format": FORMAT_MARKER,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "players": players,
    }
    return json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: generate_leaderboard.py API_URL OUTPUT_FILE", file=sys.stderr)
        return 2

    api_url = sys.argv[1].strip()
    destination = pathlib.Path(sys.argv[2])
    if not api_url.startswith(("https://", "http://")):
        print("LEADERBOARD_API_URL must be a complete HTTP(S) URL", file=sys.stderr)
        return 2

    request = urllib.request.Request(
        api_url,
        headers={"Accept": "application/json", "User-Agent": "VRChessIndonesia-GitHub-Pages-Bridge/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_output(payload), encoding="utf-8", newline="\n")
    print(f"published {len(find_rows(payload))} leaderboard rows to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
