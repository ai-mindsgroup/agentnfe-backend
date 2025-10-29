#!/usr/bin/env python3
"""
📝 Middleware de Loading - API Moderna
====================================

Middleware para logging estruturado de requests.

Versão: 3.0.0
Data: 2025-10-28
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware de logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        # Adiciona request_id ao estado da request
        request.state.request_id = request_id
        
        if settings.enable_request_logging:
            logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        if settings.enable_request_logging:
            logger.info(
                f"Request {request_id} completed: "
                f"{response.status_code} in {process_time:.3f}s"
            )
        
        # Adiciona headers de resposta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response