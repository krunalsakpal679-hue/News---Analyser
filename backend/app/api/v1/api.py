# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import documents, websocket, health

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
