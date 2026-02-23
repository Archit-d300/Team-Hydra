from typing import List, Dict

def allocate_tankers(villages: List[Dict], available_tankers: List[Dict]) -> List[Dict]:
    """
    Priority-Based Tanker Allocation Algorithm

    Priority Order:
    1. Severity (CRITICAL > HIGH > MEDIUM > LOW)
    2. Stress Score (higher first)
    3. Population (higher first)

    Only villages with tankers_needed > 0 are considered.
    Allocation continues until tankers run out.
    """

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    # Filter villages that actually need tankers
    needy_villages = [
        v for v in villages
        if v.get("tankers_needed", 0) > 0
    ]

    # Sort villages by priority
    prioritized = sorted(
        needy_villages,
        key=lambda v: (
            severity_order.get(v.get("severity"), 4),
            -v.get("stress_score", 0),
            -v.get("population", 0)
        )
    )

    tanker_pool = list(available_tankers)  # Copy list
    allocations = []

    for village in prioritized:
        if not tanker_pool:
            break  # Stop if no tankers left

        needed = village.get("tankers_needed", 0)

        # Assign available tankers (may be partial if limited)
        assigned = tanker_pool[:needed]
        tanker_pool = tanker_pool[needed:]

        assigned_count = len(assigned)

        allocations.append({
            "village_id": village.get("id", village.get("village_id", "UNKNOWN")),
            "village_name": village.get("name", "Unknown"),
            "district": village.get("district", "Unknown"),
            "severity": village.get("severity", "Unknown"),
            "stress_score": village.get("stress_score", 0),
            "population": village.get("population", 0),
            "tankers_needed": needed,
            "tankers_assigned": [t.get("id") for t in assigned],
            "tankers_count": assigned_count,
            "fully_covered": assigned_count >= needed,
            "coverage_percent": (
                round((assigned_count / needed) * 100)
                if needed > 0 else 100
            )
        })

    return allocations