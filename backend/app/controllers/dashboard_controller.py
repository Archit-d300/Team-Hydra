from app.config import supabase
from datetime import date

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