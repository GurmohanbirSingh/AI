"""Aggregated API router."""

from fastapi import APIRouter

from app.api.routes import auth, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(auth.router)
