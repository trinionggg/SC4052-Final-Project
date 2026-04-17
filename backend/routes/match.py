from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from config import ENV_RIOT_KEY, ENV_OPENAI_KEY
from models import PlayerRequest
from riot import get_puuid, get_recent_match_id, get_match_data, extract_stats
from grading import grade_player
from ai import ai_team_report
import storage

router = APIRouter()

@router.post("/match")
def analyze_match(
    req: PlayerRequest,
    x_riot_key:   Optional[str] = Header(default=None),
    x_openai_key: Optional[str] = Header(default=None),
):
    riot_key   = x_riot_key   or ENV_RIOT_KEY
    openai_key = x_openai_key or ENV_OPENAI_KEY
    if not riot_key or not openai_key:
        raise HTTPException(status_code=400, detail="Missing API keys.")

    puuid      = get_puuid(req.summoner, req.tag, req.region, riot_key)
    match_id   = get_recent_match_id(puuid, req.region, riot_key)
    match_data = get_match_data(match_id, req.region, riot_key)
    duration   = round(match_data["info"]["gameDuration"] / 60, 1)

    all_stats  = [extract_stats(p, duration) for p in match_data["info"]["participants"]]
    blue_team  = [s for s in all_stats if s["team_id"] == 100]
    red_team   = [s for s in all_stats if s["team_id"] == 200]
    blue_won   = blue_team[0]["win"]

    for p in all_stats:
        p["grade"] = grade_player(p)

    research_entries = [
        {k: v for k, v in p.items() if k not in ["name", "puuid"]}
        for p in all_stats
    ]

    storage.save_match(match_id, duration, research_entries)  
    
    return {
        "status":           "ok",
        "match_id":         match_id,
        "duration":         duration,
        "blue_team":        blue_team,
        "red_team":         red_team,
        "blue_won":         blue_won,
        "blue_report":      ai_team_report(blue_team, blue_won, openai_key),
        "red_report":       ai_team_report(red_team, not blue_won, openai_key),
        "research_entries": research_entries,
    }