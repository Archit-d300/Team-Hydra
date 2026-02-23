import numpy as np
from typing import List, Dict


def detect_groundwater_anomalies(groundwater_data: List[Dict]) -> Dict:
    """
    Z-Score + IQR based anomaly detection.
    
    Z-Score: How many standard deviations away from the mean is a reading?
    IQR: Is the value below the lower quartile fence (Q1 - 1.5 * IQR)?
    
    Both methods combined = reliable anomaly flag.
    """

    if len(groundwater_data) < 4:
        return {"error": "Need at least 4 readings for anomaly detection"}

    levels = np.array([float(d["level_meters"]) for d in groundwater_data])
    dates  = [d["recorded_date"] for d in groundwater_data]

    # --- Z-Score Method ---
    mean = np.mean(levels)
    std  = np.std(levels)
    z_scores = [(l - mean) / std if std > 0 else 0 for l in levels]

    # --- IQR Method ---
    q1, q3 = np.percentile(levels, 25), np.percentile(levels, 75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr

    # --- Tag each reading ---
    anomalies = []
    normal_readings = []

    for i, (level, date, z) in enumerate(zip(levels, dates, z_scores)):
        is_z_anomaly   = z < -1.5       # significantly below mean
        is_iqr_anomaly = level < lower_fence
        is_below_safe  = level < float(groundwater_data[i].get("safe_threshold_meters", 5.0))

        reading = {
            "date": date,
            "level_meters": round(float(level), 2),
            "z_score": round(float(z), 3),
            "is_anomaly": bool(is_z_anomaly or is_iqr_anomaly),
            "below_safe_threshold": bool(is_below_safe)
        }

        if is_z_anomaly or is_iqr_anomaly:
            anomalies.append({**reading, "reason": _get_anomaly_reason(is_z_anomaly, is_iqr_anomaly, is_below_safe)})
        else:
            normal_readings.append(reading)

    # Overall risk assessment
    anomaly_ratio = len(anomalies) / len(groundwater_data)
    if anomaly_ratio > 0.4:
        risk_level = "CRITICAL"
    elif anomaly_ratio > 0.2:
        risk_level = "HIGH"
    elif anomaly_ratio > 0:
        risk_level = "MEDIUM"
    else:
        risk_level = "NORMAL"

    # Trend: is level dropping?
    recent   = float(np.mean(levels[-3:]))
    older    = float(np.mean(levels[:3]))
    trend    = "dropping" if recent < older - 0.3 else "rising" if recent > older + 0.3 else "stable"

    return {
        "total_readings": len(groundwater_data),
        "anomalies_detected": len(anomalies),
        "anomaly_ratio": round(anomaly_ratio, 3),
        "risk_level": risk_level,
        "trend": trend,
        "mean_level": round(float(mean), 2),
        "std_deviation": round(float(std), 3),
        "q1": round(float(q1), 2),
        "q3": round(float(q3), 2),
        "iqr_lower_fence": round(float(lower_fence), 2),
        "anomalies": anomalies,
        "alert": len(anomalies) > 0
    }


def _get_anomaly_reason(is_z: bool, is_iqr: bool, is_below_safe: bool) -> str:
    reasons = []
    if is_z:
        reasons.append("Z-score significantly below mean")
    if is_iqr:
        reasons.append("Below IQR lower fence (statistical outlier)")
    if is_below_safe:
        reasons.append("Below safe threshold")
    return " | ".join(reasons) if reasons else "Flagged by detection algorithm"