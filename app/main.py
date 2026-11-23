
from fastapi import FastAPI

from app.api.v1.contracts import router as contracts_router
from app.api.v1.applications import router as applications_router


app = FastAPI(
    title="Recommendation Gateway",
    description=(
        "A generic, application-independent and "
        "recommendation-engine-independent gateway."
    ),
    version="1.0.0",
)


@app.get("/", tags=["General"])
async def root():
    return {
        "application": "Recommendation Gateway",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/v1/health", tags=["General"])
async def health():
    return {
        "status": "healthy",
        "module": "Module 1 - Gateway Foundation"
    }


app.include_router(
    contracts_router,
    prefix="/api/v1"
)

app.include_router(
    applications_router,
    prefix="/api/v1"
)
