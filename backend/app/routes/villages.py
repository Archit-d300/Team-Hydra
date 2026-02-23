from fastapi import APIRouter
from app.controllers.village_controller import (
    get_all_villages,
    calculate_village_stress,
    calculate_all_stress,
    seed_villages
)

router = APIRouter(prefix="/api/villages", tags=["Villages"])

@router.get("/")
async def list_villages():
    return await get_all_villages()

@router.post("/seed")
async def seed():
    return await seed_villages()

@router.get("/{village_id}/stress")
async def village_stress(village_id: int):
    return await calculate_village_stress(village_id)

@router.post("/calculate-all-stress")
async def all_stress():
    return await calculate_all_stress()