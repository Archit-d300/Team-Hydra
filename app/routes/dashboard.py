from fastapi import APIRouter
from app.controllers.dashboard_controller import get_dashboard

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/")
async def dashboard():
    return await get_dashboard()