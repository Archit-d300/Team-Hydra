import numpy as np
from typing import List, Dict


def analyze_rainfall_trend(rainfall_data: List[Dict]) -> Dict:
    """
    Analyze if rainfall is trending up (recovery) or down (worsening drought).
    Uses linear regression slope on rainfall deviation over time.
    """
    if len(rainfall_data) < 5:
        return {"trend": "unknown", "reason": "Insufficient data"}

    sorted_data = sorted(rainfall_data, key=lambda x: x["recorded_date"])
    deviations = []
    for r in sorted_data:
        normal = float(r["normal_rainfall_mm"])
        actual = float(r["rainfall_mm"])
        dev = (normal - actual) / normal if normal > 0 else 0
        deviations.append(dev)

    x = np.arange(len(deviations))
    slope = float(np.polyfit(x, deviations, 1)[0])

    # Positive slope = deviation increasing = drought worsening
    if slope > 0.005:
        direction = "worsening"
        description = "Rainfall deficit is growing — drought conditions intensifying"
    elif slope < -0.005:
        direction = "improving"
        description = "Rainfall deficit is reducing — conditions slowly recovering"
    else:
        direction = "stable"
        description = "Drought conditions are holding steady"

    return {
        "trend": direction,
        "slope": round(slope, 5),
        "description": description,
        "data_points": len(deviations),
        "avg_deviation_pct": round(float(np.mean(deviations)) * 100, 1)
    }


def analyze_groundwater_trend(gw_data: List[Dict]) -> Dict:
    """Analyze groundwater level trend over time."""
    if len(gw_data) < 3:
        return {"trend": "unknown", "reason": "Insufficient data"}

    sorted_data = sorted(gw_data, key=lambda x: x["recorded_date"])
    levels = [float(d["level_meters"]) for d in sorted_data]

    x = np.arange(len(levels))
    slope = float(np.polyfit(x, levels, 1)[0])

    # Negative slope = water table dropping = bad
    if slope < -0.1:
        direction = "dropping"
        description = "Groundwater table is falling — critical depletion risk"
    elif slope > 0.1:
        direction = "rising"
        description = "Groundwater table is recovering — positive trend"
    else:
        direction = "stable"
        description = "Groundwater table is stable"

    safe_threshold = float(sorted_data[0].get("safe_threshold_meters", 5.0))
    current_level  = levels[-1]
    days_to_danger = None

    if slope < 0 and current_level > safe_threshold:
        # Estimate days until level drops below safe threshold
        gap = current_level - safe_threshold
        days_to_danger = round(abs(gap / slope)) if slope != 0 else None

    return {
        "trend": direction,
        "slope_per_day": round(slope, 4),
        "description": description,
        "current_level_m": round(current_level, 2),
        "safe_threshold_m": safe_threshold,
        "days_to_danger": days_to_danger,
        "is_below_safe": current_level < safe_threshold
    }