"""Rank a Premier League gameweek from most to least worth watching, without spoilers.

Match data comes from the Fantasy Premier League API. Jev sees the results; you only see the order.
"""

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from urllib.request import urlopen

from typesafe_sdk import Score, TypeSafeClient

FPL = "https://fantasy.premierleague.com/api"
ENV_FILE = Path(__file__).with_name(".env")
RANKINGS_DIR = Path(__file__).with_name("rankings")

COUNTED_STATS = ["red_cards", "yellow_cards", "own_goals", "penalties_missed", "penalties_saved", "saves"]

QUESTION = Score(
    instructions=(
        "How worthwhile would it be for a neutral fan who does not know the result "
        "to watch this already-played Premier League match in full?"
    ),
    criteria=[
        "Skip it: few goals, little at stake, nothing happened",
        "Routine: a normal game with little drama",
        "Decent: some goals or moments worth seeing",
        "Entertaining: plenty of goals, drama or a surprise result",
        "Unmissable: a classic, a huge upset or wild drama",
    ],
)


def load_env():
    """Read KEY=value lines from .env next to this script; real environment variables win."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep and not key.lstrip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip())


def fetch(path):
    with urlopen(f"{FPL}/{path}") as response:
        return json.load(response)


def positions_before(gameweek, fixtures, teams):
    """League positions from matches finished in earlier gameweeks, so they don't reflect this round's results."""
    points, goal_diff, goals_for = Counter(), Counter(), Counter()
    for fixture in fixtures:
        if not (fixture["finished"] and fixture["event"] and fixture["event"] < gameweek):
            continue
        for us, them in (("h", "a"), ("a", "h")):
            team = fixture[f"team_{us}"]
            scored, conceded = fixture[f"team_{us}_score"], fixture[f"team_{them}_score"]
            if scored > conceded:
                points[team] += 3
            elif scored == conceded:
                points[team] += 1
            goal_diff[team] += scored - conceded
            goals_for[team] += scored

    order = sorted(teams, key=lambda t: (-points[t], -goal_diff[t], -goals_for[t], teams[t]["name"]))
    return {team: position for position, team in enumerate(order, 1)}


def describe(fixture, teams, positions):
    stats = {s["identifier"]: s for s in fixture["stats"]}

    def side(key, venue):
        team = teams[fixture[f"team_{key}"]]
        scorers = stats["goals_scored"][key]
        return {
            "team": team["name"],
            "league_position_before_round": positions[team["id"]],
            "team_strength": team[f"strength_overall_{venue}"],
            "goals": fixture[f"team_{key}_score"],
            "hat_trick": any(p["value"] >= 3 for p in scorers),
            **{name: sum(p["value"] for p in stats[name][key]) for name in COUNTED_STATS},
        }

    return {"home": side("h", "home"), "away": side("a", "away")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gameweek", type=int, help="defaults to the latest gameweek with final stats")
    args = parser.parse_args()
    load_env()

    bootstrap = fetch("bootstrap-static/")
    teams = {t["id"]: t for t in bootstrap["teams"]}
    gameweek = args.gameweek or max(
        (e["id"] for e in bootstrap["events"] if e["finished"] and e["data_checked"]), default=None
    )
    if gameweek is None:
        print("No gameweek has final stats yet.")
        return
    output = RANKINGS_DIR / f"gw{gameweek}.txt"
    if output.exists():
        print(f"Gameweek {gameweek} is already ranked in {output}.")
        return

    season = fetch("fixtures/")
    fixtures = [f for f in season if f["event"] == gameweek and f["finished"]]
    if not fixtures:
        raise SystemExit(f"No finished matches in gameweek {gameweek}.")
    positions = positions_before(gameweek, season, teams)

    scores = {}
    with TypeSafeClient(model="jev-latest") as client:
        for fixture in fixtures:
            state = describe(fixture, teams, positions)
            response = client.system_one(state=state, questions={"interest": QUESTION})
            scores[fixture["id"]] = response.scores["interest"].score

    ranked = sorted(fixtures, key=lambda f: scores[f["id"]], reverse=True)
    lines = [f"Gameweek {gameweek}, most to least worth watching:", ""]
    for rank, fixture in enumerate(ranked, 1):
        home = teams[fixture["team_h"]]["name"]
        away = teams[fixture["team_a"]]["name"]
        lines.append(f"{rank:>2}. {home} v {away}")

    text = "\n".join(lines) + "\n"
    RANKINGS_DIR.mkdir(exist_ok=True)
    output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
