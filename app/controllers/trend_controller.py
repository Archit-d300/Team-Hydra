from app.config import supabase
from app.services.trend_analyzer import analyze_rainfall_trend, analyze_groundwater_trend


async def get_village_trends(village_id: int):
    """Full trend analysis for a village — rainfall + groundwater"""
    village_res = supabase.table("villages").select("*").eq("id", village_id).single().execute()
    if not village_res.data:
        return {"success": False, "error": "Village not found"}

    rainfall_res = supabase.table("rainfall_data")\
        .select("*").eq("village_id", village_id)\
        .order("recorded_date", desc=False).execute()

    gw_res = supabase.table("groundwater_levels")\
        .select("*").eq("village_id", village_id)\
        .order("recorded_date", desc=False).execute()

    rainfall_trend  = analyze_rainfall_trend(rainfall_res.data or [])
    groundwater_trend = analyze_groundwater_trend(gw_res.data or [])

    # Combined risk assessment
    is_worsening = rainfall_trend.get("trend") == "worsening" or groundwater_trend.get("trend") == "dropping"
    combined_risk = "HIGH" if is_worsening else "MEDIUM" if rainfall_trend.get("trend") == "stable" else "LOW"

    return {
        "success": True,
        "village": village_res.data["name"],
        "district": village_res.data["district"],
        "rainfall_trend": rainfall_trend,
        "groundwater_trend": groundwater_trend,
        "combined_risk": combined_risk,
        "recommendation": _get_recommendation(rainfall_trend, groundwater_trend)
    }


def _get_recommendation(rainfall_trend: dict, gw_trend: dict) -> str:
    if rainfall_trend.get("trend") == "worsening" and gw_trend.get("trend") == "dropping":
        return "🚨 URGENT: Deploy tankers immediately. Both rainfall deficit and groundwater are worsening."
    elif gw_trend.get("days_to_danger") and gw_trend["days_to_danger"] < 10:
        return f"⚠️ WARNING: Groundwater will hit danger level in ~{gw_trend['days_to_danger']} days. Preemptive tanker deployment recommended."
    elif rainfall_trend.get("trend") == "improving":
        return "✅ Conditions improving. Continue monitoring. Reduce tanker allocation gradually."
    else:
        return "📊 Stable conditions. Maintain current tanker allocation and monitor weekly."


async def get_all_trends():
    """Trend summary for all villages"""
    villages = supabase.table("villages").select("*").execute()
    results = []

    for v in villages.data:
        trend_data = await get_village_trends(v["id"])
        if trend_data["success"]:
            results.append({
                "village_id": v["id"],
                "village": v["name"],
                "district": v["district"],
                "rainfall_trend": trend_data["rainfall_trend"]["trend"],
                "groundwater_trend": trend_data["groundwater_trend"]["trend"],
                "combined_risk": trend_data["combined_risk"],
                "recommendation": trend_data["recommendation"]
            })

    worsening_count = sum(1 for r in results if r["combined_risk"] == "HIGH")

    return {
        "success": True,
        "total_villages": len(results),
        "worsening_villages": worsening_count,
        "trends": results
    }