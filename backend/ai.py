from openai import OpenAI

def ai_coaching_report(stats: dict, openai_key: str) -> str:
    client = OpenAI(api_key=openai_key)
    prompt = f"""You are an expert League of Legends coach.
Champion: {stats['champion']} ({stats['role']}) | Result: {'WIN' if stats['win'] else 'LOSS'}
KDA: {stats['kills']}/{stats['deaths']}/{stats['assists']} ({stats['kda']}) | CS/min: {stats['cs_per_min']}
Vision: {stats['vision_score']} | Damage: {stats['damage_dealt']:,} | Wards: {stats['wards_placed']}

Write a coaching report with:
1. Performance Summary (2-3 sentences)
2. Top 2 Strengths (cite specific stats)
3. Top 2 Areas to Improve (actionable)
4. One Drill for Next Game"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return res.choices[0].message.content

def ai_team_report(team_stats: list[dict], won: bool, openai_key: str) -> str:
    client = OpenAI(api_key=openai_key)
    lines = "\n".join([
        f"- {p['role']}: {p['champion']} | {p['kills']}/{p['deaths']}/{p['assists']} KDA "
        f"| {p['cs_per_min']} cs/m | {p['vision_score']} vision | {p['damage_dealt']//1000}k dmg"
        for p in team_stats
    ])
    prompt = f"""You are an expert LoL analyst. Team result: {'WIN' if won else 'LOSS'}
{lines}

Write:
1. Team Performance Summary (3-4 sentences)
2. Strongest Player and why (cite stats)
3. Weakest Link and specific improvement advice
4. One team-wide strategic focus for next game"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return res.choices[0].message.content
