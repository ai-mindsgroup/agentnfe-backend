#!/usr/bin/env python3
"""
🔐 Middleware de Autenticação - API Moderna
=========================================

Middleware para autenticação JWT e controle de acesso.

Versão: 3.0.0
Data: 2025-10-28
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
import time

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware de autenticação"""
    
    def __init__(self, app):
        super().__init__(app)
        self.exempt_paths = {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/",
            "/info"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Pula autenticação se desabilitada ou para paths isentos
        if not settings.enable_auth or any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Implementar lógica de autenticação JWT aqui
        # Por enquanto, permite todas as requests
        
        return await call_next(request)