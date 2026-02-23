from app.config import supabase
from datetime import date
from app.services.anomaly_detector import detect_groundwater_anomalies
from app.services.trend_analyzer import analyze_rainfall_trend, analyze_groundwater_trend
from app.services.ml_predictor import train_and_predict
from app.services.route_optimizer import greedy_nearest_neighbor
from app.controllers.route_controller import DEPOT
async def get_dashboard():
    today = date.today().isoformat()

    # Run all queries in parallel concept (Supabase is fast)
    villages = supabase.table("villages").select("*", count="exact").execute()
    tankers = supabase.table("tankers").select("*").execute()
    stress_today = supabase.table("water_stress_index")\
        .select("*")\
        .eq("calculated_date", today)\
        .execute()
    allocations_today = supabase.table("tanker_allocations")\
        .select("*")\
        .eq("allocated_date", today)\
        .execute()

    tanker_list = tankers.data or []
    stress_list = stress_today.data or []

    severity_counts = {
        "CRITICAL": len([s for s in stress_list if s["severity"] == "CRITICAL"]),
        "HIGH": len([s for s in stress_list if s["severity"] == "HIGH"]),
        "MEDIUM": len([s for s in stress_list if s["severity"] == "MEDIUM"]),
        "LOW": len([s for s in stress_list if s["severity"] == "LOW"]),
    }

    return {
        "success": True,
        "data": {
            "summary": {
                "total_villages": villages.count,
                "villages_assessed_today": len(stress_list),
                "critical_villages": severity_counts["CRITICAL"],
                "high_risk_villages": severity_counts["HIGH"],
                "medium_risk_villages": severity_counts["MEDIUM"],
                "low_risk_villages": severity_counts["LOW"],
            },
            "tankers": {
                "total": len(tanker_list),
                "available": len([t for t in tanker_list if t["status"] == "available"]),
                "deployed": len([t for t in tanker_list if t["status"] == "deployed"]),
            },
            "allocations_today": len(allocations_today.data or []),
            "village_stress_map": [
                {
                    "village_id": s["village_id"],
                    "score": s["stress_score"],
                    "severity": s["severity"],
                    "tankers_needed": s["tankers_needed"]
                }
                for s in stress_list
            ]
        }
    }

async def get_enhanced_dashboard():
    """
    God-level dashboard: stress + ML predictions + anomalies + trends + routes.
    All in one response for the frontend.
    """
    today = date.today().isoformat()

    # --- Base data ---
    villages    = supabase.table("villages").select("*").execute().data or []
    tankers     = supabase.table("tankers").select("*").execute().data or []
    stress_data = supabase.table("water_stress_index").select("*").eq("calculated_date", today).execute().data or []

    # --- Per village enrichment ---
    enriched_villages = []
    system_alerts     = []
    worsening_count   = 0
    anomaly_count     = 0

    for v in villages:
        vid = v["id"]

        # Stress score today
        stress = next((s for s in stress_data if s["village_id"] == vid), None)

        # Rainfall data
        rain = supabase.table("rainfall_data").select("*")\
            .eq("village_id", vid).order("recorded_date", desc=False).execute().data or []

        # Groundwater data
        gw = supabase.table("groundwater_levels").select("*")\
            .eq("village_id", vid).order("recorded_date", desc=False).execute().data or []

        # Trends
        rain_trend = analyze_rainfall_trend(rain)
        gw_trend   = analyze_groundwater_trend(gw)

        # Anomalies
        anomaly_report = detect_groundwater_anomalies(gw) if gw else {}
        has_anomaly    = anomaly_report.get("alert", False)
        if has_anomaly:
            anomaly_count += 1

        # ML 3-day forecast (light — keeps response fast)
        forecast = []
        if rain and gw:
            forecast = train_and_predict(rain, gw, v["population"], forecast_days=3)

        # Is worsening?
        is_worsening = rain_trend.get("trend") == "worsening" or gw_trend.get("trend") == "dropping"
        if is_worsening:
            worsening_count += 1

        # Build alerts
        if stress and stress["severity"] == "CRITICAL":
            system_alerts.append(f"🚨 {v['name']}: CRITICAL stress score today ({stress['stress_score']}/10)")
        if has_anomaly:
            system_alerts.append(f"⚠️ {v['name']}: Groundwater anomaly detected")
        if gw_trend.get("days_to_danger") and gw_trend["days_to_danger"] < 7:
            system_alerts.append(f"💧 {v['name']}: Groundwater danger in ~{gw_trend['days_to_danger']} days")

        enriched_villages.append({
            "id": vid,
            "name": v["name"],
            "district": v["district"],
            "population": v["population"],
            "lat": float(v["lat"]),
            "lng": float(v["lng"]),
            "stress_today": stress,
            "rainfall_trend": rain_trend.get("trend", "unknown"),
            "groundwater_trend": gw_trend.get("trend", "unknown"),
            "days_to_gw_danger": gw_trend.get("days_to_danger"),
            "anomaly_detected": has_anomaly,
            "anomaly_count": anomaly_report.get("anomalies_detected", 0),
            "forecast_3day": forecast
        })

    # --- Optimized route for today ---
    priority = [v for v in enriched_villages if v["stress_today"] and v["stress_today"]["severity"] in ("CRITICAL", "HIGH", "MEDIUM")]
    for p in priority:
        p["severity"]      = p["stress_today"]["severity"]
        p["tankers_needed"] = p["stress_today"]["tankers_needed"]

    route_data = greedy_nearest_neighbor(DEPOT, priority) if priority else None

    # --- Summary stats ---
    severity_counts = {
        "CRITICAL": len([s for s in stress_data if s["severity"] == "CRITICAL"]),
        "HIGH":     len([s for s in stress_data if s["severity"] == "HIGH"]),
        "MEDIUM":   len([s for s in stress_data if s["severity"] == "MEDIUM"]),
        "LOW":      len([s for s in stress_data if s["severity"] == "LOW"]),
    }

    return {
        "success": True,
        "generated_at": date.today().isoformat(),
        "system_alerts": system_alerts,
        "summary": {
            "total_villages": len(villages),
            "assessed_today": len(stress_data),
            "worsening_villages": worsening_count,
            "villages_with_anomalies": anomaly_count,
            **severity_counts,
        },
        "tankers": {
            "total": len(tankers),
            "available": len([t for t in tankers if t["status"] == "available"]),
            "deployed":  len([t for t in tankers if t["status"] == "deployed"]),
        },
        "optimized_route": route_data,
        "villages": enriched_villages,
    }