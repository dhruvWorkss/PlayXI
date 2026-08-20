from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

NON_BOWLER_WICKETS = {"run out", "retired hurt", "retired out", "obstructing the field"}


@dataclass(frozen=True)
class SelectionRules:
    team_size: int = 11
    max_from_one_team: int = 7
    min_batting_options: int = 3
    min_bowling_options: int = 3


def load_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    deliveries = pd.read_csv(data_dir / "deliveries_updated_ipl_upto_2025.csv").drop_duplicates()
    matches = pd.read_csv(data_dir / "matches_updated_ipl_upto_2025.csv").rename(columns={"`season": "season"})
    deliveries["date"] = pd.to_datetime(deliveries["date"], errors="coerce")
    for column in ("isWide", "isNoBall", "Byes", "LegByes", "Penalty", "extras"):
        deliveries[column] = pd.to_numeric(deliveries[column], errors="coerce").fillna(0)
    deliveries["dismissal_kind"] = deliveries["dismissal_kind"].fillna("none")
    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")
    return deliveries, matches


def build_player_features(deliveries: pd.DataFrame) -> pd.DataFrame:
    legal = deliveries["isWide"].eq(0)
    batting = deliveries.groupby(["matchId", "date", "batting_team", "batsman"], as_index=False).agg(
        runs=("batsman_runs", "sum"), boundaries=("batsman_runs", lambda x: x.eq(4).sum()),
        sixes=("batsman_runs", lambda x: x.eq(6).sum()),
    ).rename(columns={"batting_team": "team", "batsman": "player"})
    balls = deliveries[legal].groupby(["matchId", "batsman"]).size().rename("balls_faced").reset_index()
    batting = batting.merge(balls, left_on=["matchId", "player"], right_on=["matchId", "batsman"], how="left")
    batting["strike_rate"] = batting["runs"].div(batting["balls_faced"].clip(lower=1)).mul(100)
    batting["batting_points"] = batting["runs"] + batting["boundaries"] + batting["sixes"] * 2
    batting.loc[batting["runs"].ge(50), "batting_points"] += 8
    batting.loc[batting["runs"].ge(100), "batting_points"] += 8
    sr_ok = batting["balls_faced"].ge(10)
    batting.loc[sr_ok & batting["strike_rate"].ge(170), "batting_points"] += 6
    batting.loc[sr_ok & batting["strike_rate"].between(150, 170, inclusive="left"), "batting_points"] += 4
    batting.loc[sr_ok & batting["strike_rate"].between(130, 150, inclusive="left"), "batting_points"] += 2

    bowling_rows = deliveries[legal].copy()
    bowling_rows["runs_charged"] = bowling_rows["batsman_runs"] + bowling_rows["isNoBall"]
    bowling = bowling_rows.groupby(["matchId", "date", "bowling_team", "bowler"], as_index=False).agg(
        runs_conceded=("runs_charged", "sum"), balls_bowled=("ball", "size")
    ).rename(columns={"bowling_team": "team", "bowler": "player"})
    credited = deliveries[~deliveries["dismissal_kind"].isin(NON_BOWLER_WICKETS | {"none"})]
    wickets = credited.groupby(["matchId", "bowler"]).size().rename("wickets").reset_index()
    bowling = bowling.merge(wickets, left_on=["matchId", "player"], right_on=["matchId", "bowler"], how="left")
    bowling["wickets"] = bowling["wickets"].fillna(0)
    bowling["economy"] = bowling["runs_conceded"].div(bowling["balls_bowled"]).mul(6)
    bowling["bowling_points"] = bowling["wickets"] * 25
    bowling.loc[bowling["wickets"].ge(3), "bowling_points"] += 4
    bowling.loc[bowling["wickets"].ge(4), "bowling_points"] += 4
    eco_ok = bowling["balls_bowled"].ge(12)
    bowling.loc[eco_ok & bowling["economy"].le(5), "bowling_points"] += 6
    bowling.loc[eco_ok & bowling["economy"].gt(5) & bowling["economy"].le(6), "bowling_points"] += 4
    bowling.loc[eco_ok & bowling["economy"].gt(6) & bowling["economy"].le(7), "bowling_points"] += 2

    combined = batting[["matchId", "date", "team", "player", "batting_points"]].merge(
        bowling[["matchId", "date", "team", "player", "bowling_points"]],
        on=["matchId", "player"], how="outer", suffixes=("_bat", "_bowl")
    )
    combined["date"] = combined["date_bat"].fillna(combined["date_bowl"])
    combined["team"] = combined["team_bat"].fillna(combined["team_bowl"])
    combined = combined.drop(columns=["date_bat", "date_bowl", "team_bat", "team_bowl"])
    combined[["batting_points", "bowling_points"]] = combined[["batting_points", "bowling_points"]].fillna(0)
    combined["fantasy_points"] = combined["batting_points"] + combined["bowling_points"]
    combined = combined.sort_values(["player", "date", "matchId"])
    combined["predicted_points"] = combined.groupby("player")["fantasy_points"].transform(
        lambda x: x.shift(1).rolling(5, min_periods=1).mean()
    ).fillna(combined["fantasy_points"].median())
    return combined


def player_pool(features: pd.DataFrame, teams: tuple[str, str]) -> pd.DataFrame:
    chosen = features[features["team"].isin(teams)].copy()
    recent = chosen.sort_values(["date", "matchId"]).groupby(["team", "player"], as_index=False).tail(1)
    appearances = chosen.groupby(["team", "player"]).size().rename("appearances").reset_index()
    rates = chosen.groupby(["team", "player"]).agg(
        bat_rate=("batting_points", lambda x: x.gt(0).mean()), bowl_rate=("bowling_points", lambda x: x.gt(0).mean())
    ).reset_index()
    recent = recent.merge(appearances, on=["team", "player"]).merge(rates, on=["team", "player"])
    recent["role"] = "batter"
    recent.loc[recent["bowl_rate"].gt(0.2), "role"] = "bowler"
    recent.loc[recent["bat_rate"].gt(0.2) & recent["bowl_rate"].gt(0.2), "role"] = "all-rounder"
    return recent[["team", "player", "role", "predicted_points", "appearances", "date"]].sort_values("predicted_points", ascending=False)


def optimize_team(pool: pd.DataFrame, rules: SelectionRules = SelectionRules()) -> pd.DataFrame:
    if len(pool) < rules.team_size or pool["team"].nunique() != 2:
        raise ValueError("Select at least 11 players across two teams.")
    first_team = pool["team"].iloc[0]
    # State: (players, first-team players, batting options, bowling options).
    # Dynamic programming avoids enumerating all 22-choose-11 combinations.
    states: dict[tuple[int, int, int, int], tuple[float, tuple[int, ...]]] = {(0, 0, 0, 0): (0.0, ())}
    for index, row in pool.iterrows():
        next_states = dict(states)
        is_bat = int(row["role"] in ("batter", "all-rounder"))
        is_bowl = int(row["role"] in ("bowler", "all-rounder"))
        for (size, first_count, bat_count, bowl_count), (score, selected) in states.items():
            if size == rules.team_size:
                continue
            new_first = first_count + int(row["team"] == first_team)
            new_size = size + 1
            second_count = new_size - new_first
            if new_first > rules.max_from_one_team or second_count > rules.max_from_one_team:
                continue
            key = (new_size, new_first, min(rules.min_batting_options, bat_count + is_bat),
                   min(rules.min_bowling_options, bowl_count + is_bowl))
            candidate = (score + float(row["predicted_points"]), selected + (index,))
            if key not in next_states or candidate[0] > next_states[key][0]:
                next_states[key] = candidate
        states = next_states
    valid = [value for key, value in states.items()
             if key[0] == rules.team_size and key[2] == rules.min_batting_options and key[3] == rules.min_bowling_options]
    if not valid:
        raise ValueError("No valid XI satisfies the current role and team constraints.")
    _, selected = max(valid, key=lambda value: value[0])
    result = pool.loc[list(selected)].sort_values("predicted_points", ascending=False).reset_index(drop=True)
    result["designation"] = ""
    result.loc[0, "designation"] = "Captain"
    result.loc[1, "designation"] = "Vice-captain"
    return result


def head_to_head(matches: pd.DataFrame, team1: str, team2: str, limit: int = 5) -> pd.DataFrame:
    mask = matches["team1"].isin([team1, team2]) & matches["team2"].isin([team1, team2])
    return matches.loc[mask].sort_values("date", ascending=False).head(limit)[["date", "team1", "team2", "winner"]]


def team_form(deliveries: pd.DataFrame, team: str, limit: int = 5) -> pd.DataFrame:
    innings = deliveries[deliveries["batting_team"].eq(team)].groupby(["matchId", "date"], as_index=False).agg(
        runs=("batsman_runs", "sum"), extras=("extras", "sum")
    )
    innings["score"] = innings["runs"] + innings["extras"]
    return innings.sort_values("date", ascending=False).head(limit)[["date", "score"]]


def build_and_save(data_dir: Path) -> Path:
    deliveries, _ = load_data(data_dir)
    output = data_dir / "player_features.csv"
    build_player_features(deliveries).to_csv(output, index=False)
    return output


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(build_and_save(root / "data"))
