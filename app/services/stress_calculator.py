from typing import List, Dict

def calculate_stress_score(rainfall_data: List[Dict], groundwater_data: List[Dict]) -> float:
    """
    Water Stress Index: Score from 0 (safe) to 10 (critical)
    
    Two factors:
    1. Rainfall Deviation (0-5): How far below normal is the rainfall?
    2. Groundwater Score (0-5): How close to the danger threshold?
    """

    # --- Factor 1: Rainfall Deviation ---
    if not rainfall_data:
        rainfall_score = 2.5  # default mid score if no data
    else:
        avg_actual = sum(r["rainfall_mm"] for r in rainfall_data) / len(rainfall_data)
        avg_normal = sum(r["normal_rainfall_mm"] for r in rainfall_data) / len(rainfall_data)

        if avg_normal > 0:
            deviation = (avg_normal - avg_actual) / avg_normal  # 0 to 1+
        else:
            deviation = 0

        # Scale to 0-5 range
        rainfall_score = min(deviation * 5, 5.0)

    # --- Factor 2: Groundwater Level ---
    if not groundwater_data:
        gw_score = 2.5  # default if no data
    else:
        latest = groundwater_data[0]  # most recent reading
        level = latest["level_meters"]
        threshold = latest["safe_threshold_meters"]

        # If level < threshold => danger
        # Higher the level relative to threshold = safer
        danger_ratio = threshold / level if level > 0 else 2
        gw_score = min(danger_ratio * 2.5, 5.0)

    total_score = round(rainfall_score + gw_score, 2)
    return min(total_score, 10.0)


def get_severity(score: float) -> str:
    if score >= 8:
        return "CRITICAL"
    elif score >= 6:
        return "HIGH"
    elif score >= 4:
        return "MEDIUM"
    else:
        return "LOW"


def get_tankers_needed(score: float, population: int) -> int:
    """
    Estimate tankers needed:
    - Based on population and severity
    - 1 tanker per 500 people at full crisis (score=10)
    - Scaled proportionally by score
    """
    base = population / 500
    factor = score / 10
    return max(1, round(base * factor))