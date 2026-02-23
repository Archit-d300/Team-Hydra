from typing import List, Dict


def allocate_tankers(villages: List[Dict], available_tankers: List[Dict]) -> List[Dict]:
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    needy_villages = [v for v in villages if v.get("tankers_needed", 0) > 0]

    prioritized = sorted(
        needy_villages,
        key=lambda v: (
            severity_order.get(v.get("severity"), 4),
            -v.get("stress_score", 0),
            -v.get("population", 0)
        )
    )

    tanker_pool = list(available_tankers)
    allocations = []

    for village in prioritized:
        if not tanker_pool:
            break

        needed = village.get("tankers_needed", 0)
        assigned = tanker_pool[:needed]
        tanker_pool = tanker_pool[needed:]

        allocations.append({
            "village_id": village.get("id", "UNKNOWN"),
            "village_name": village.get("name", "Unknown"),
            "district": village.get("district", "Unknown"),
            "severity": village.get("severity", "Unknown"),
            "stress_score": village.get("stress_score", 0),
            "population": village.get("population", 0),
            "tankers_needed": needed,
            "tankers_assigned": [t.get("id") for t in assigned],
            "tankers_count": len(assigned),
            "fully_covered": len(assigned) >= needed,
            "coverage_percent": round((len(assigned) / needed) * 100) if needed > 0 else 100
        })

    return allocations