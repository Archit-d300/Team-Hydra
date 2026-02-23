from fastapi import APIRouter
from app.controllers.trend_controller import get_village_trends, get_all_trends

router = APIRouter(prefix="/api/trends", tags=["Trend Analysis"])

@router.get("/village/{village_id}")
async def village_trends(village_id: int):
    """Rainfall + groundwater trend analysis with recommendations"""
    return await get_village_trends(village_id)

@router.get("/all")
async def all_trends():
    """System-wide trend summary"""
    return await get_all_trends()