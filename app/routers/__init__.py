"""Routers da API FastAPI.

Este módulo contém todos os routers da aplicação.
"""
from app.routers.nfe import router as nfe_router

__all__ = ["nfe_router"]
