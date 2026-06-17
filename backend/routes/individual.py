from fastapi import APIRouter, Header
from typing import Optional
from backend.config import ENV_RIOT_KEY, ENV_OPENAI_KEY
from backend.models import PlayerRequest
from backend.riot import get_puuid, get_recent_match_id, get_match_data, extract_stats
from backend.grading import grade_player
from backend.ai import ai_coaching_report
from fastapi import HTTPException
from ml.predict import predict

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
    print("here")
    stats = extract_stats(raw_player, duration)
    print("Extracted stats:", stats)

    # predict from ml model
    prediction = predict(stats)
    stats["win_probability"] = prediction["win_probability"]
    stats["performance_label"] = prediction["performance_label"]
    stats["grade"] = prediction["grade"]
    stats["top_positive"] = prediction["top_positive"]
    stats["top_negative"] = prediction["top_negative"]

    # stats["grade"]           = grade_player(stats, win_probability)

    stats["duration"] = duration
    stats["match_id"] = match_id

    print("Stats used for ai coaching report:", stats)
    stats["coaching_report"] = ai_coaching_report(stats, openai_key)
    print("Generated coaching report:", stats["coaching_report"])
    return {"status": "ok", 
            "data": {
                    # identity
                    "name":         stats["name"],
                    "champion":     stats["champion"],
                    "role":         stats["role"],
                    "win":          stats["win"],
                    "match_id":     stats.get("match_id", "N/A"),
                    "duration":     stats["duration"],  # convert to minutes

                    # stats — named exactly as frontend expects
                    "kills":        stats["kills"],
                    "deaths":       stats["deaths"],
                    "assists":      stats["assists"],
                    "kda":          stats["kda"],
                    "cs_per_min":   stats["cs_per_min"],
                    "vision_score": stats["visionscore"],        # rename here
                    "damage_dealt": stats["damage_dealt"],
                    "wards_placed": stats["wards_placed"],

                    # model output
                    "grade":             prediction["grade"],
                    "win_probability":   prediction["win_probability"],
                    "performance_label": prediction["performance_label"],
                    "top_positive":      prediction["top_positive"],
                    "top_negative":      prediction["top_negative"],

                    # llm report
                    "coaching_report": stats["coaching_report"],
                }
            }