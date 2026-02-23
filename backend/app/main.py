from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import villages, tankers, dashboard

app = FastAPI(
    title="Drought Warning & Tanker Management System",
    description="SDG 6 - Clean Water & Sanitation | Maharashtra | PRERNA 18.0",
    version="1.0.0"
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(villages.router)
app.include_router(tankers.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {
        "message": "🚰 Drought Warning System API is live",
        "docs": "/docs",
        "project": "PRERNA 18.0 - Hack A Cause"
    }