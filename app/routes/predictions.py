from fastapi import APIRouter, Query
from app.controllers.prediction_controller import predict_village_stress, predict_all_villages
from app.controllers.prediction_controller import (
    predict_village_stress, predict_all_villages,
    get_village_anomalies, get_all_anomalies     
)

router = APIRouter(prefix="/api/predictions", tags=["ML Predictions"])

@router.get("/village/{village_id}")
async def village_forecast(
    village_id: int,
    days: int = Query(default=7, ge=1, le=14, description="Forecast days (1-14)")
):
    """
    ML-powered 7-day drought stress forecast for a single village.
    Uses Linear Regression trained on historical rainfall + groundwater data.
    """
    return await predict_village_stress(village_id, days)


@router.get("/all")
async def all_villages_forecast(
    days: int = Query(default=7, ge=1, le=14)
):
    """
    Forecast stress for ALL villages. Highlights which will go CRITICAL.
    """
    return await predict_all_villages(days)

@router.get("/anomalies/village/{village_id}")
async def village_anomalies(village_id: int):
    """
    Z-Score + IQR anomaly detection on groundwater readings.
    Identifies sudden dangerous drops in water levels.
    """
    return await get_village_anomalies(village_id)


@router.get("/anomalies/all")
async def all_anomalies():
    """System-wide groundwater anomaly scan across all villages."""
    return await get_all_anomalies()