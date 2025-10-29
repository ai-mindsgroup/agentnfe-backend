#!/usr/bin/env python3
"""
🚨 Middleware de Tratamento de Erros - API Moderna
================================================

Middleware para tratamento global de erros e exceções.

Versão: 3.0.0
Data: 2025-10-28
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
import traceback
from datetime import datetime

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware de tratamento de erros"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # HTTPException já é tratada pelo FastAPI
            raise e
        except Exception as e:
            # Log do erro
            request_id = getattr(request.state, 'request_id', 'unknown')
            logger.error(
                f"Unhandled error in request {request_id}: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            
            # Response de erro padronizada
            error_response = {
                "error": "Internal Server Error",
                "message": "Um erro interno ocorreu no servidor",
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            }
            
            # Em desenvolvimento, inclui detalhes do erro
            if settings.debug:
                error_response["detail"] = str(e)
                error_response["traceback"] = traceback.format_exc()
            
            return JSONResponse(
                status_code=500,
                content=error_response
            )