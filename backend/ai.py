from openai import OpenAI
from ml.predict import predict
import json

def ai_coaching_report(stats: dict, openai_key: str) -> dict:
    client = OpenAI(api_key=openai_key)

    pos = "\n".join([
        f"  - {p['feature']}: +{p['impact']} impact on win probability"
        for p in stats['top_positive']
    ])
    neg = "\n".join([
        f"  - {p['feature']}: {p['impact']} impact on win probability"
        for p in stats['top_negative']
    ])

    prompt = f"""
Player: {stats['champion']} ({stats['role']})
Result: {'WIN' if stats['win'] else 'LOSS'}
Grade: {stats['grade']}
Model Assessment: {stats['performance_label']} (win probability: {stats['win_probability']:.0%})

Raw Stats:
- KDA: {stats['kills']}/{stats['deaths']}/{stats['assists']} ({stats['kda']})
- CS/min: {stats['cs_per_min']}
- Vision Score: {stats['visionscore']}
- Damage to Champions: {stats['damage_dealt']:,}
- Gold Earned: {stats['gold_earned']:,}
- Wards Placed: {stats['wards_placed']}

What drove this result (from XGBoost model):
Helped win probability:
{pos}

Hurt win probability:
{neg}

Using the grade, model assessment, and SHAP factors as your primary reference, respond in this exact JSON:
{{
    "summary": "2-3 sentences referencing the grade and model assessment directly",
    "strengths": [
        {{"stat": "stat name", "observation": "why this was good, cite the number"}},
        {{"stat": "stat name", "observation": "why this was good, cite the number"}}
    ],
    "improvements": [
        {{"area": "area name", "advice": "specific actionable advice referencing the SHAP factor"}},
        {{"area": "area name", "advice": "specific actionable advice referencing the SHAP factor"}}
    ],
    "drill": "one specific drill for next game targeting the biggest weakness"
}}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert League of Legends coach. Be specific, cite stats directly, keep advice actionable. Always ground your analysis in the model assessment and SHAP factors provided."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},  # uncommented
        temperature=0.2,
    )

    return json.loads(res.choices[0].message.content)  # parse to dict

# def ai_coaching_report(stats: dict, openai_key: str) -> dict:
#     # run xgboost prediction first
#     # prediction = predict(stats)

#     client = OpenAI(api_key=openai_key)

#     pos = "\n".join([
#         f"  - {p['feature']}: +{p['impact']} impact on win probability"
#         for p in stats['top_positive']
#     ])
#     neg = "\n".join([
#         f"  - {p['feature']}: {p['impact']} impact on win probability"
#         for p in stats['top_negative']
#     ])

#     prompt = f"""
# Player: {stats['champion']} ({stats['role']})
# Result: {'WIN' if stats['win'] else 'LOSS'}
# Grade: {stats['grade']}
# Model Assessment: {stats['performance_label']} (win probability: {stats['win_probability']:.0%})

# Raw Stats:
# - KDA: {stats['kills']}/{stats['deaths']}/{stats['assists']} ({stats['kda']})
# - CS/min: {stats['cs_per_min']}
# - Vision Score: {stats['visionscore']}
# - Damage to Champions: {stats['damage_dealt']:,}
# - Gold Earned: {stats['gold_earned']:,}
# - Wards Placed: {stats['wards_placed']}

# What drove this result (from XGBoost model):
# Helped win probability:
# {pos}

# Hurt win probability:
# {neg}

# Using the grade, model assessment, and SHAP factors as your primary reference, respond in this exact JSON:
# {{
#     "summary": "2-3 sentences referencing the grade and model assessment directly",
#     "strengths": [
#         {{"stat": "stat name", "observation": "why this was good, cite the number"}},
#         {{"stat": "stat name", "observation": "why this was good, cite the number"}}
#     ],
#     "improvements": [
#         {{"area": "area name", "advice": "specific actionable advice referencing the SHAP factor"}},
#         {{"area": "area name", "advice": "specific actionable advice referencing the SHAP factor"}}
#     ],
#     "drill": "one specific drill for next game targeting the biggest weakness"
# }}
# """

#     res = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are an expert League of Legends coach. Be specific, cite stats directly, keep advice actionable. Always ground your analysis in the model assessment and SHAP factors provided."},
#             {"role": "user", "content": prompt}
#         ],
#         # response_format={"type": "json_object"},
#         temperature=0.2,
#     )
    
#     return res.choices[0].message.content

# def ai_coaching_report(stats: dict, openai_key: str) -> str:
#     client = OpenAI(api_key=openai_key)
#     prompt = f"""You are an expert League of Legends coach.
# Champion: {stats['champion']} ({stats['role']}) | Result: {'WIN' if stats['win'] else 'LOSS'}
# KDA: {stats['kills']}/{stats['deaths']}/{stats['assists']} ({stats['kda']}) | CS/min: {stats['cs_per_min']}
# Vision: {stats['vision_score']} | Damage: {stats['damage_dealt']:,} | Wards: {stats['wards_placed']}

# Write a coaching report with:
# 1. Performance Summary (2-3 sentences)
# 2. Top 2 Strengths (cite specific stats)
# 3. Top 2 Areas to Improve (actionable)
# 4. One Drill for Next Game"""
#     res = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.7,
#     )
#     return res.choices[0].message.content

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
