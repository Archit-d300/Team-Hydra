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
    """Seed realistic Maharashtra Vidarbha village data"""

    
    villages = [
        {"name": "Wardha", "district": "Wardha", "taluka": "Wardha", "population": 12000, "lat": 20.7453, "lng": 78.6022},
        {"name": "Yavatmal", "district": "Yavatmal", "taluka": "Yavatmal", "population": 8500, "lat": 20.3888, "lng": 78.1204},
        {"name": "Amravati", "district": "Amravati", "taluka": "Amravati", "population": 15000, "lat": 20.9374, "lng": 77.7796},
        {"name": "Chandrapur", "district": "Chandrapur", "taluka": "Chandrapur", "population": 9200, "lat": 19.9615, "lng": 79.2961},
        {"name": "Buldhana", "district": "Buldhana", "taluka": "Buldhana", "population": 6700, "lat": 20.5292, "lng": 76.1842},
        {"name": "Akola", "district": "Akola", "taluka": "Akola", "population": 11000, "lat": 20.7096, "lng": 77.0001},
        {"name": "Washim", "district": "Washim", "taluka": "Washim", "population": 5300, "lat": 20.1112, "lng": 77.1341},
        {"name": "Gondia", "district": "Gondia", "taluka": "Gondia", "population": 7800, "lat": 21.4617, "lng": 80.1969},
    ]

    inserted = supabase.table("villages").insert(villages).execute()

    # Generate 30 days of mock rainfall + 10 days groundwater per village
    for village in inserted.data:
        rainfall_rows = []
        gw_rows = []

        for i in range(30):
            day = (date.today() - timedelta(days=i)).isoformat()
            rainfall_rows.append({
                "village_id": village["id"],
                "recorded_date": day,
                # Drought simulation: actual << normal
                "rainfall_mm": round(random.uniform(2, 15), 2),
                "normal_rainfall_mm": round(random.uniform(35, 55), 2)
            })

        for i in range(10):
            day = (date.today() - timedelta(days=i)).isoformat()
            gw_rows.append({
                "village_id": village["id"],
                "recorded_date": day,
                "level_meters": round(random.uniform(2.5, 6.5), 2),
                "safe_threshold_meters": 5.0
            })

        supabase.table("rainfall_data").insert(rainfall_rows).execute()
        supabase.table("groundwater_levels").insert(gw_rows).execute()

    return {"success": True, "message": f"Seeded {len(inserted.data)} villages with mock sensor data"}