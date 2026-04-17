from fastapi import APIRouter, Header
from typing import Optional
from config import ENV_RIOT_KEY, ENV_OPENAI_KEY
from models import PlayerRequest
from riot import get_puuid, get_recent_match_id, get_match_data, extract_stats
from grading import grade_player
from ai import ai_coaching_report
from fastapi import HTTPException

router = APIRouter()

@router.post("/individual")
def analyze_individual(
    req: PlayerRequest,
    x_riot_key:   Optional[str] = Header(default=None),
    x_openai_key: Optional[str] = Header(default=None),
):
    riot_key   = x_riot_key   or ENV_RIOT_KEY
    openai_key = x_openai_key or ENV_OPENAI_KEY
    print("RIOT KEY:", repr(riot_key))
    print("OPENAI KEY:", repr(openai_key))
    if not riot_key or not openai_key:
        raise HTTPException(status_code=400, detail="Missing API keys.")

    puuid      = get_puuid(req.summoner, req.tag, req.region, riot_key)
    match_id   = get_recent_match_id(puuid, req.region, riot_key)
    match_data = get_match_data(match_id, req.region, riot_key)
    duration   = round(match_data["info"]["gameDuration"] / 60, 1)
    raw_player = next(p for p in match_data["info"]["participants"] if p["puuid"] == puuid)
    stats      = extract_stats(raw_player, duration)
    stats["grade"]           = grade_player(stats)
    stats["duration"]        = duration
    stats["match_id"]        = match_id
    stats["coaching_report"] = ai_coaching_report(stats, openai_key)
    return {"status": "ok", "data": stats}