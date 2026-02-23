from fastapi import APIRouter
from app.controllers.tanker_controller import (
    get_all_tankers, seed_tankers, run_allocation, get_allocations
)

router = APIRouter(prefix="/api/tankers", tags=["Tankers"])

@router.get("/")
async def list_tankers():
    return await get_all_tankers()

@router.post("/seed")
async def seed():
    return await seed_tankers()

@router.post("/allocate")
async def allocate():
    return await run_allocation()

@router.get("/allocations")
async def allocations():
    return await get_allocations()