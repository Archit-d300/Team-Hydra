from app.config import supabase
from app.services.stress_calculator import calculate_stress_score, get_severity, get_tankers_needed
from datetime import date, timedelta
import random

async def get_all_villages():
    villages = supabase.table("villages").select("*").execute()
    stress = supabase.table("water_stress_index").select("*").order("calculated_date", desc=True).execute()

    result = []
    for v in villages.data:
        village_stress = next((s for s in stress.data if s["village_id"] == v["id"]), None)
        result.append({**v, "stress_info": village_stress})

    return {"success": True, "data": result}


async def calculate_village_stress(village_id: int):
    # Fetch village info
    village_res = supabase.table("villages").select("*").eq("id", village_id).single().execute()
    if not village_res.data:
        return {"success": False, "error": "Village not found"}

    village = village_res.data

    # Fetch last 30 days of rainfall
    rainfall_res = supabase.table("rainfall_data")\
        .select("*")\
        .eq("village_id", village_id)\
        .order("recorded_date", desc=True)\
        .limit(30)\
        .execute()

    # Fetch last 10 groundwater readings
    gw_res = supabase.table("groundwater_levels")\
        .select("*")\
        .eq("village_id", village_id)\
        .order("recorded_date", desc=True)\
        .limit(10)\
        .execute()

    if not rainfall_res.data or not gw_res.data:
        return {"success": False, "error": "Not enough sensor data for this village"}

    # Run algorithm
    score = calculate_stress_score(rainfall_res.data, gw_res.data)
    severity = get_severity(score)
    tankers_needed = get_tankers_needed(score, village["population"])
    today = date.today().isoformat()

    # Save to DB (upsert = update if exists, insert if not)
    supabase.table("water_stress_index").upsert({
        "village_id": village_id,
        "calculated_date": today,
        "stress_score": score,
        "severity": severity,
        "tankers_needed": tankers_needed,
        "updated_at": date.today().isoformat()
    }, on_conflict="village_id,calculated_date").execute()

    return {
        "success": True,
        "data": {
            "village": village["name"],
            "district": village["district"],
            "score": score,
            "severity": severity,
            "tankers_needed": tankers_needed
        }
    }


async def calculate_all_stress():
    """Calculate stress for ALL villages at once — for bulk update"""
    villages = supabase.table("villages").select("*").execute()
    results = []
    for v in villages.data:
        res = await calculate_village_stress(v["id"])
        results.append(res)
    return {"success": True, "results": results}


async def seed_villages():
    villages = [
        {"name": "Wardha",     "district": "Wardha",     "taluka": "Wardha",     "population": 12000, "lat": 20.7453, "lng": 78.6022, "drought_level": "critical"},
        {"name": "Yavatmal",   "district": "Yavatmal",   "taluka": "Yavatmal",   "population": 8500,  "lat": 20.3888, "lng": 78.1204, "drought_level": "high"},
        {"name": "Amravati",   "district": "Amravati",   "taluka": "Amravati",   "population": 15000, "lat": 20.9374, "lng": 77.7796, "drought_level": "critical"},
        {"name": "Chandrapur", "district": "Chandrapur", "taluka": "Chandrapur", "population": 9200,  "lat": 19.9615, "lng": 79.2961, "drought_level": "medium"},
        {"name": "Buldhana",   "district": "Buldhana",   "taluka": "Buldhana",   "population": 6700,  "lat": 20.5292, "lng": 76.1842, "drought_level": "low"},
        {"name": "Akola",      "district": "Akola",      "taluka": "Akola",      "population": 11000, "lat": 20.7096, "lng": 77.0001, "drought_level": "high"},
        {"name": "Washim",     "district": "Washim",     "taluka": "Washim",     "population": 5300,  "lat": 20.1112, "lng": 77.1341, "drought_level": "medium"},
        {"name": "Gondia",     "district": "Gondia",     "taluka": "Gondia",     "population": 7800,  "lat": 21.4617, "lng": 80.1969, "drought_level": "low"},
    ]

    # Realistic rainfall profiles per drought level
    rainfall_profiles = {
        "critical": {"actual_range": (1, 8),   "normal_range": (40, 55)},  # 80-95% deficit
        "high":     {"actual_range": (5, 15),  "normal_range": (38, 50)},  # 60-80% deficit
        "medium":   {"actual_range": (15, 25), "normal_range": (35, 45)},  # 30-60% deficit
        "low":      {"actual_range": (25, 38), "normal_range": (35, 45)},  # 0-30% deficit
    }

    # Realistic groundwater profiles
    groundwater_profiles = {
        "critical": {"level_range": (1.5, 3.0)},  # Well below 5m safe threshold
        "high":     {"level_range": (2.5, 4.0)},
        "medium":   {"level_range": (3.5, 5.5)},
        "low":      {"level_range": (5.0, 7.5)},  # Above safe threshold
    }

    # Remove drought_level before inserting (not a DB column)
    db_villages = [{k: v for k, v in village.items() if k != "drought_level"} for village in villages]
    inserted = supabase.table("villages").insert(db_villages).execute()

    for i, village in enumerate(inserted.data):
        drought_level = villages[i]["drought_level"]
        rain_profile  = rainfall_profiles[drought_level]
        gw_profile    = groundwater_profiles[drought_level]

        rainfall_rows = []
        gw_rows       = []

        for j in range(30):
            day = (date.today() - timedelta(days=29 - j)).isoformat()

            # Add slight worsening trend for critical/high villages over time
            # (makes ML predictions more realistic and dramatic)
            worsening_factor = 1.0
            if drought_level in ("critical", "high"):
                worsening_factor = max(0.6, 1.0 - (j * 0.012))  # rainfall drops 1.2% per day

            actual_rain = random.uniform(*rain_profile["actual_range"]) * worsening_factor
            normal_rain = random.uniform(*rain_profile["normal_range"])

            rainfall_rows.append({
                "village_id": village["id"],
                "recorded_date": day,
                "rainfall_mm": round(actual_rain, 2),
                "normal_rainfall_mm": round(normal_rain, 2)
            })

            if j >= 20:  # 10 groundwater readings (last 10 days)
                # Groundwater also drops slightly over time for drought areas
                gw_drop = (j - 20) * 0.05 if drought_level in ("critical", "high") else 0
                level = random.uniform(*gw_profile["level_range"]) - gw_drop
                gw_rows.append({
                    "village_id": village["id"],
                    "recorded_date": day,
                    "level_meters": round(max(0.5, level), 2),
                    "safe_threshold_meters": 5.0
                })

        supabase.table("rainfall_data").insert(rainfall_rows).execute()
        supabase.table("groundwater_levels").insert(gw_rows).execute()

    return {
        "success": True,
        "message": f"Seeded {len(inserted.data)} Vidarbha villages with realistic drought profiles",
        "profiles": {v["name"]: villages[i]["drought_level"] for i, v in enumerate(inserted.data)}
    }