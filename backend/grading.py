ROLE_WEIGHTS = {
    "TOP":     {"kda": 12, "cs": 12, "vision": 6,  "damage": 10, "win": 10},
    "JUNGLE":  {"kda": 12, "cs": 8,  "vision": 12, "damage": 8,  "win": 10},
    "MIDDLE":  {"kda": 12, "cs": 10, "vision": 6,  "damage": 12, "win": 10},
    "BOTTOM":  {"kda": 10, "cs": 12, "vision": 4,  "damage": 14, "win": 10},
    "UTILITY": {"kda": 8,  "cs": 2,  "vision": 20, "damage": 4,  "win": 10},
    "FILL":    {"kda": 10, "cs": 8,  "vision": 10, "damage": 10, "win": 10},
}

def grade_player(stats: dict) -> str:
    role = stats.get("role", "FILL")
    w    = ROLE_WEIGHTS.get(role, ROLE_WEIGHTS["FILL"])

    score  = min(stats["kda"]          * (w["kda"]    / 3),  w["kda"]    * 4)
    score += min(stats["cs_per_min"]   * (w["cs"]     / 2),  w["cs"]     * 5)
    score += min(stats["vision_score"] * (w["vision"] / 10), w["vision"] * 2)
    score += min(stats["damage_dealt"] / (1500 * (14 / max(w["damage"], 1))), w["damage"])
    score += w["win"] if stats["win"] else 0

    if score >= 85: return "S"
    if score >= 70: return "A"
    if score >= 55: return "B"
    if score >= 40: return "C"
    return "D"