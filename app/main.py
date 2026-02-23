from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import villages, tankers, dashboard, predictions, routes, trends

app = FastAPI(
    title="Drought Warning & Tanker Management System",
    description="""
    🚰 SDG 6 - Clean Water & Sanitation | Maharashtra | PRERNA 18.0
    
    Features:
    - Real-time Water Stress Index calculation
    - ML-powered 7-day drought forecast (Linear Regression)
    - Groundwater anomaly detection (Z-Score + IQR)
    - Priority-based tanker allocation
    - Route optimization (Greedy Nearest Neighbor)
    - Rainfall & groundwater trend analysis
    """,
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(villages.router)
app.include_router(tankers.router)
app.include_router(dashboard.router)
app.include_router(predictions.router)
app.include_router(routes.router)
app.include_router(trends.router)

@app.get("/")
def root():
    return {
        "message": "🚰 Drought Warning System v2.0 — AI-Enhanced",
        "docs": "/docs",
        "endpoints": {
            "core": ["/api/villages", "/api/tankers", "/api/dashboard"],
            "ml":   ["/api/predictions/all", "/api/predictions/village/{id}"],
            "anomaly": ["/api/predictions/anomalies/all"],
            "routes": ["/api/routes/optimized"],
            "trends": ["/api/trends/all"],
            "god_mode": ["/api/dashboard/enhanced"]
        }
    }