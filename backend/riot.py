import requests
from fastapi import HTTPException

def riot_get(url: str, riot_key: str):
    res = requests.get(url, headers={"X-Riot-Token": riot_key})
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=f"Riot API error: {res.text}")
    return res.json()

def get_puuid(name: str, tag: str, region: str, riot_key: str) -> str:
    return riot_get(
        f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}",
        riot_key,
    )["puuid"]

def get_recent_match_id(puuid: str, region: str, riot_key: str) -> str:
    return riot_get(
        f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=1",
        riot_key,
    )[0]

def get_match_data(match_id: str, region: str, riot_key: str) -> dict:
    return riot_get(
        f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}",
        riot_key,
    )

# def extract_stats(player: dict, duration_min: float) -> dict:
#     cs = player["totalMinionsKilled"] + player["neutralMinionsKilled"]
#     return {
#         "name":         player.get("riotIdGameName", player.get("summonerName", "Unknown")),
#         "champion":     player["championName"],
#         "role":         player.get("teamPosition", "FILL"),
#         "win":          player["win"],
#         "kills":        player["kills"],
#         "deaths":       player["deaths"],
#         "assists":      player["assists"],
#         "kda":          round((player["kills"] + player["assists"]) / max(player["deaths"], 1), 2),
#         "cs_per_min":   round(cs / max(duration_min, 1), 1),
#         "vision_score": player["visionScore"],
#         "damage_dealt": player["totalDamageDealtToChampions"],
#         "gold_earned":  player["goldEarned"],
#         "wards_placed": player.get("wardsPlaced", 0),
#         "team_id":      player["teamId"],
#         "puuid":        player["puuid"],
#     }

def extract_stats(player: dict, duration_min: float) -> dict:
    cs = player["totalMinionsKilled"] + player["neutralMinionsKilled"]
    return {
        # model features — must match training columns exactly
        "kills":            player["kills"],
        "deaths":           player["deaths"],
        "assists":          player["assists"],
        "totdmgtochamp":    player["totalDamageDealtToChampions"],
        "totheal":          player.get("totalHeal", 0),
        "dmgselfmit":       player.get("damageSelfMitigated", 0),
        "dmgtoobj":         player.get("damageDealtToObjectives", 0),
        "dmgtoturrets":     player.get("damageDealtToTurrets", 0),
        "visionscore":      player["visionScore"],
        "timecc":           player.get("timeCCingOthers", 0),
        "totdmgtaken":      player["totalDamageTaken"],
        "goldearned":       player["goldEarned"],
        "goldspent":        player.get("goldSpent", 0),
        "turretkills":      player.get("turretKills", 0),
        "inhibkills":       player.get("inhibitorKills", 0),
        "ownjunglekills":   player.get("totalAllyJungleMinionsKilled", 0),
        "enemyjunglekills": player.get("totalEnemyJungleMinionsKilled", 0),
        "totcctimedealt":   player.get("totalTimeCCDealt", 0),
        "champlvl":         player["champLevel"],
        "pinksbought":      player.get("visionWardsBoughtInGame", 0),
        "wardsbought":      player.get("sightWardsBoughtInGame", 0),
        "wardsplaced":      player.get("wardsPlaced", 0),
        "wardskilled":      player.get("wardsKilled", 0),
        "firstblood":       int(player.get("firstBloodKill", False)),
        "cs_per_min":       round(cs / max(duration_min, 1), 2),
        "duration":         duration_min * 60,  # model trained on seconds

        # display only — not fed into model
        "name":         player.get("riotIdGameName", player.get("summonerName", "Unknown")),
        "champion":     player["championName"],
        "role":         player.get("teamPosition", "FILL"),
        "win":          player["win"],
        "kda":          round((player["kills"] + player["assists"]) / max(player["deaths"], 1), 2),
        "damage_dealt": player["totalDamageDealtToChampions"],
        "gold_earned":  player["goldEarned"],
        "wards_placed": player.get("wardsPlaced", 0),
        "team_id":      player["teamId"],
        "puuid":        player["puuid"],
    }