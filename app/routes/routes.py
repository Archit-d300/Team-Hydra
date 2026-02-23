from fastapi import APIRouter
from app.controllers.route_controller import get_optimized_routes

router = APIRouter(prefix="/api/routes", tags=["Route Optimization"])

@router.get("/optimized")
async def optimized_tanker_routes():
    """
    Greedy nearest-neighbor route optimization for tanker dispatch.
    Balances distance efficiency with village severity priority.
    """
    return await get_optimized_routes()