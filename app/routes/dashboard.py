from fastapi import APIRouter
from app.controllers.dashboard_controller import get_dashboard
from app.controllers.dashboard_controller import get_dashboard, get_enhanced_dashboard
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/")
async def dashboard():
    return await get_dashboard()
@router.get("/enhanced")
async def enhanced_dashboard():
    """
    Full system intelligence dashboard:
    stress scores + ML predictions + anomaly detection + trend analysis + route optimization
    """
    return await get_enhanced_dashboard()