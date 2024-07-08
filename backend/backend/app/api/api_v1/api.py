from app.api.api_v1.endpoints import configs, artifacts
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(configs.router, prefix="/configs", tags=["configs"])
api_router.include_router(artifacts.router, prefix="/artifacts", tags=["artifacts"])
