import math
from typing import List, Dict, Tuple


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return round(R * c, 2)


def greedy_nearest_neighbor(
    depot: Dict,          # tanker depot: {"name": "...", "lat": ..., "lng": ...}
    villages: List[Dict]  # villages with lat/lng and priority score
) -> List[Dict]:
    """
    Greedy Nearest Neighbor route optimization.
    
    Algorithm:
    1. Start from depot
    2. Always go to the highest-priority unvisited village next
       (priority = severity weight / distance — balances urgency + efficiency)
    3. Return optimized visit order with distances
    
    This is a classic TSP approximation — fast and good enough for real-world use.
    """

    severity_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

    unvisited = list(villages)
    route = []
    current_pos = (float(depot["lat"]), float(depot["lng"]))
    total_distance = 0.0

    while unvisited:
        # Score each unvisited village: higher severity + closer distance = go first
        best_score = -1
        best_village = None
        best_distance = 0

        for v in unvisited:
            dist = haversine_km(
                current_pos[0], current_pos[1],
                float(v["lat"]), float(v["lng"])
            )
            # Avoid division by zero
            dist_factor = 1 / (dist + 0.1)
            severity_weight = severity_weights.get(v.get("severity", "LOW"), 1)

            # Priority score: urgency × proximity
            score = severity_weight * dist_factor

            if score > best_score:
                best_score = score
                best_village = v
                best_distance = dist

        if best_village:
            route.append({
                "stop": len(route) + 1,
                "village_id": best_village["id"],
                "village": best_village["name"],
                "district": best_village["district"],
                "lat": float(best_village["lat"]),
                "lng": float(best_village["lng"]),
                "severity": best_village.get("severity", "UNKNOWN"),
                "distance_from_prev_km": best_distance,
                "tankers_needed": best_village.get("tankers_needed", 1),
                "priority_score": round(best_score, 4)
            })
            total_distance += best_distance
            current_pos = (float(best_village["lat"]), float(best_village["lng"]))
            unvisited.remove(best_village)

    # Return to depot distance
    return_dist = haversine_km(
        current_pos[0], current_pos[1],
        float(depot["lat"]), float(depot["lng"])
    )

    return {
        "depot": depot["name"],
        "depot_lat": float(depot["lat"]),
        "depot_lng": float(depot["lng"]),
        "total_stops": len(route),
        "total_distance_km": round(total_distance + return_dist, 2),
        "route": route,
        "optimization": "Greedy Nearest Neighbor with Severity Weighting"
    }