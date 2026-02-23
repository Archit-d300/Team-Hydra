from app.config import supabase
from app.services.tanker_allocator import allocate_tankers
from datetime import date


async def get_all_tankers():
    res = supabase.table("tankers").select("*").execute()
    return {"success": True, "data": res.data}


async def seed_tankers():
    tankers = [
        {
            "registration_no": f"MH-NK-{1001 + i}",
            "capacity_liters": 10000,
            "current_district": "Nagpur",
            "status": "available"
        }
        for i in range(12)
    ]

    res = supabase.table("tankers").insert(tankers).execute()
    return {"success": True, "data": res.data, "message": "12 tankers seeded"}


async def run_allocation():
    today = date.today().isoformat()

    stress_res = supabase.table("water_stress_index")\
        .select("*, villages(name, population, district)")\
        .eq("calculated_date", today)\
        .execute()

    if not stress_res.data:
        return {
            "success": False,
            "error": "No stress data for today. Run /api/villages/calculate-all-stress first."
        }

    tanker_res = supabase.table("tankers")\
        .select("*")\
        .eq("status", "available")\
        .execute()

    villages_for_alloc = [
        {
            "id": s["village_id"],
            "name": s.get("villages", {}).get("name"),
            "district": s.get("villages", {}).get("district"),
            "population": s.get("villages", {}).get("population"),
            "stress_score": s["stress_score"],
            "severity": s["severity"],
            "tankers_needed": s["tankers_needed"]
        }
        for s in stress_res.data
    ]

    allocations = allocate_tankers(villages_for_alloc, tanker_res.data or [])

    for alloc in allocations:
        for tanker_id in alloc["tankers_assigned"]:
            supabase.table("tanker_allocations").insert({
                "tanker_id": tanker_id,
                "village_id": alloc["village_id"],
                "allocated_date": today,
                "status": "active"
            }).execute()

            supabase.table("tankers")\
                .update({"status": "deployed"})\
                .eq("id", tanker_id)\
                .execute()

    return {
        "success": True,
        "total_tankers_used": sum(a["tankers_count"] for a in allocations),
        "villages_covered": len([a for a in allocations if a["tankers_count"] > 0]),
        "allocations": allocations
    }


async def get_allocations():
    today = date.today().isoformat()

    res = supabase.table("tanker_allocations")\
        .select("*, tankers(registration_no, capacity_liters), villages(name, district)")\
        .eq("allocated_date", today)\
        .execute()

    return {"success": True, "data": res.data}