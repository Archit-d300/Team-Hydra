from app.config import supabase
from app.services.route_optimizer import greedy_nearest_neighbor
from datetime import date

# Nagpur district headquarters as tanker depot
DEPOT = {
    "name": "Nagpur District HQ",
    "lat": 21.1458,
    "lng": 79.0882
}


async def get_optimized_routes():
    """
    Compute optimized tanker dispatch routes for today's critical villages.
    Uses greedy nearest-neighbor algorithm with severity weighting.
    """
    today = date.today().isoformat()

    # Get villages with today's stress scores
    stress_res = supabase.table("water_stress_index")\
        .select("*, villages(id, name, district, lat, lng, population)")\
        .eq("calculated_date", today)\
        .execute()

    if not stress_res.data:
        return {
            "success": False,
            "error": "No stress data for today. Run /api/villages/calculate-all-stress first."
        }

    # Only route to HIGH and CRITICAL villages (don't waste tankers on LOW)
    priority_villages = []
    for s in stress_res.data:
        if s["severity"] in ("CRITICAL", "HIGH", "MEDIUM"):
            priority_villages.append({
                "id": s["villages"]["id"],
                "name": s["villages"]["name"],
                "district": s["villages"]["district"],
                "lat": s["villages"]["lat"],
                "lng": s["villages"]["lng"],
                "population": s["villages"]["population"],
                "severity": s["severity"],
                "stress_score": s["stress_score"],
                "tankers_needed": s["tankers_needed"]
            })

    if not priority_villages:
        return {
            "success": True,
            "message": "No HIGH/CRITICAL villages today — no urgent routing needed",
            "route": None
        }

    # Run optimization
    optimized = greedy_nearest_neighbor(DEPOT, priority_villages)

    # Estimated travel time (avg 60 km/h in rural Maharashtra)
    avg_speed_kmh = 60
    total_hours = round(optimized["total_distance_km"] / avg_speed_kmh, 1)

    return {
        "success": True,
        "date": today,
        "depot": DEPOT["name"],
        "villages_in_route": len(priority_villages),
        "total_distance_km": optimized["total_distance_km"],
        "estimated_travel_hours": total_hours,
        "optimization_method": optimized["optimization"],
        "route": optimized["route"]
    }