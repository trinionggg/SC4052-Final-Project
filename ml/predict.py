import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import shap

models = {
    role: joblib.load(f'ml/models/model_{role.lower()}.pkl')
    for role in ['TOP', 'JUNGLE', 'MID', 'BOT', 'SUPPORT']
}

# must match exactly: X.columns.tolist() from your notebook
FEATURES = [
    'duration', 'kills', 'deaths', 'assists', 'totdmgtochamp',
    'totheal', 'dmgselfmit', 'dmgtoobj', 'dmgtoturrets', 'visionscore',
    'timecc', 'totdmgtaken', 'goldearned', 'goldspent', 'turretkills',
    'inhibkills', 'ownjunglekills', 'enemyjunglekills', 'totcctimedealt',
    'champlvl', 'pinksbought', 'wardsbought', 'wardsplaced', 'wardskilled',
    'firstblood', 'cs_per_min'
]

FEATURE_LABELS = {
    'duration':         'Game duration',
    'kills':            'Kill contribution',
    'deaths':           'Deaths',
    'assists':          'Assist contribution',
    'totdmgtochamp':    'Damage to champions',
    'totheal':          'Total healing',
    'dmgselfmit':       'Damage self mitigated',
    'dmgtoobj':         'Damage to objectives',
    'dmgtoturrets':     'Damage to turrets',
    'visionscore':      'Vision score',
    'timecc':           'CC time dealt',
    'totdmgtaken':      'Damage taken',
    'goldearned':       'Gold earned',
    'goldspent':        'Gold spent',
    'turretkills':      'Turret kills',
    'inhibkills':       'Inhibitor kills',
    'ownjunglekills':   'Own jungle CS',
    'enemyjunglekills': 'Enemy jungle CS',
    'totcctimedealt':   'Total CC time dealt',
    'champlvl':         'Champion level',
    'pinksbought':      'Control wards bought',
    'wardsbought':      'Wards bought',
    'wardsplaced':      'Wards placed',
    'wardskilled':      'Wards killed',
    'firstblood':       'First blood',
    'cs_per_min':       'CS per minute',
}

# maps all Riot API role strings to model keys
ROLE_MAP = {
    'MIDDLE':  'MID',
    'UTILITY': 'SUPPORT',
    'BOTTOM':  'BOT',
    'TOP':     'TOP',
    'JUNGLE':  'JUNGLE',
    'FILL':    'MID',
    'MID':     'MID',
    'BOT':     'BOT',
    'SUPPORT': 'SUPPORT',
}

def predict(stats: dict) -> dict:
    role = ROLE_MAP.get(stats.get('role', 'FILL').upper(), 'MID')
    model = models.get(role, models['MID'])

    df = pd.DataFrame([stats])[FEATURES].fillna(0)
    dmatrix = xgb.DMatrix(df, feature_names=FEATURES)

    win_prob = float(model.predict(dmatrix)[0])

    # shap for single prediction
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(df)[0]

    shap_pairs = sorted(
        zip(FEATURES, shap_vals),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    top_positive = [
        {"feature": FEATURE_LABELS.get(f, f), "impact": round(float(v), 3)}
        for f, v in shap_pairs if v > 0
    ][:3]

    top_negative = [
        {"feature": FEATURE_LABELS.get(f, f), "impact": round(float(v), 3)}
        for f, v in shap_pairs if v < 0
    ][:3]

    return {
        "win_probability":   round(win_prob, 2),
        "actual_win":        stats.get("win", False),
        "performance_label": _label(win_prob, stats.get("win", False)),
        "grade":             _grade(win_prob, stats.get("win", False)),
        "top_positive":      top_positive,
        "top_negative":      top_negative,
    }

def _label(prob: float, won: bool) -> str:
    if won and prob >= 0.65:       return "Dominant win — stats strongly supported victory"
    if won and prob >= 0.45:       return "Earned win — performance was solid"
    if won:                        return "Lucky win — stats were against you"
    if not won and prob <= 0.35:   return "Expected loss — stats confirm a poor game"
    if not won and prob <= 0.55:   return "Close loss — small improvements would have changed this"
    return "Unlucky loss — stats actually supported a win"

def _grade(prob: float, won: bool) -> str:
    if won and prob >= 0.65:       return "S"
    if won and prob >= 0.45:       return "A"
    if won:                        return "B"
    if not won and prob >= 0.55:   return "C"
    if not won and prob >= 0.35:   return "D"
    return "F"