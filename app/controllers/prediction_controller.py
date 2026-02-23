from app.config import supabase
from app.services.ml_predictor import train_and_predict, get_model_accuracy
from app.services.anomaly_detector import detect_groundwater_anomalies


async def predict_village_stress(village_id: int, days: int = 7):
    """Predict next N days stress score for a village using ML"""

    # Fetch village
    village_res = supabase.table("villages").select("*").eq("id", village_id).single().execute()
    if not village_res.data:
        return {"success": False, "error": "Village not found"}

    village = village_res.data

    # Fetch historical data (more data = better ML)
    rainfall_res = supabase.table("rainfall_data")\
        .select("*")\
        .eq("village_id", village_id)\
        .order("recorded_date", desc=False)\
        .execute()

    gw_res = supabase.table("groundwater_levels")\
        .select("*")\
        .eq("village_id", village_id)\
        .order("recorded_date", desc=False)\
        .execute()

    if not rainfall_res.data or not gw_res.data:
        return {"success": False, "error": "Insufficient historical data for ML prediction"}

    # Get ML predictions
    predictions = train_and_predict(
        rainfall_res.data,
        gw_res.data,
        village["population"],
        forecast_days=days
    )

    if not predictions:
        return {"success": False, "error": "Could not generate predictions (need more data)"}

    # Get model accuracy
    accuracy = get_model_accuracy(rainfall_res.data, gw_res.data)

    # Compute trend: is it getting worse?
    scores = [p["predicted_stress_score"] for p in predictions]
    trend = "worsening" if scores[-1] > scores[0] else "improving" if scores[-1] < scores[0] else "stable"
    peak_day = predictions[scores.index(max(scores))]

    return {
        "success": True,
        "village": village["name"],
        "district": village["district"],
        "forecast_days": days,
        "trend": trend,
        "peak_stress_day": peak_day,
        "predictions": predictions,
        "model_accuracy": accuracy
    }


async def predict_all_villages(days: int = 7):
    """Predict stress for all villages — gives judges the full picture"""
    villages = supabase.table("villages").select("*").execute()

    all_predictions = []
    critical_alert = []

    for v in villages.data:
        result = await predict_village_stress(v["id"], days)
        if result["success"]:
            max_score = max(p["predicted_stress_score"] for p in result["predictions"])
            all_predictions.append({
                "village_id": v["id"],
                "village": v["name"],
                "district": v["district"],
                "trend": result["trend"],
                "max_predicted_score": max_score,
                "max_severity": result["peak_stress_day"]["severity"],
                "predictions": result["predictions"]
            })
            # Alert if any day is critical
            if max_score >= 8:
                critical_alert.append(v["name"])

    return {
        "success": True,
        "forecast_days": days,
        "villages_forecasted": len(all_predictions),
        "critical_alerts": critical_alert,
        "alert_message": f"{len(critical_alert)} villages predicted to hit CRITICAL in {days} days!" if critical_alert else "No critical alerts",
        "forecasts": all_predictions
    }


async def get_village_anomalies(village_id: int):
    """Detect groundwater anomalies for a village"""

    village_res = supabase.table("villages").select("*").eq("id", village_id).single().execute()
    if not village_res.data:
        return {"success": False, "error": "Village not found"}

    gw_res = supabase.table("groundwater_levels")\
        .select("*")\
        .eq("village_id", village_id)\
        .order("recorded_date", desc=False)\
        .execute()

    if not gw_res.data:
        return {"success": False, "error": "No groundwater data found"}

    anomaly_report = detect_groundwater_anomalies(gw_res.data)

    return {
        "success": True,
        "village": village_res.data["name"],
        "district": village_res.data["district"],
        "anomaly_report": anomaly_report
    }


async def get_all_anomalies():
    """Run anomaly detection across all villages — gives system-wide alert"""
    villages = supabase.table("villages").select("*").execute()
    results = []
    alert_villages = []

    for v in villages.data:
        gw_res = supabase.table("groundwater_levels")\
            .select("*")\
            .eq("village_id", v["id"])\
            .order("recorded_date", desc=False)\
            .execute()

        if gw_res.data:
            report = detect_groundwater_anomalies(gw_res.data)
            results.append({
                "village_id": v["id"],
                "village": v["name"],
                "district": v["district"],
                "risk_level": report.get("risk_level", "UNKNOWN"),
                "anomalies_detected": report.get("anomalies_detected", 0),
                "trend": report.get("trend", "unknown"),
                "alert": report.get("alert", False)
            })
            if report.get("alert"):
                alert_villages.append(v["name"])

    return {
        "success": True,
        "total_villages": len(results),
        "villages_with_anomalies": len(alert_villages),
        "alert_villages": alert_villages,
        "results": results
    }