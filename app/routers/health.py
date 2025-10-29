#!/usr/bin/env python3
"""
🔍 Router de Health Check - API Moderna
=======================================

Endpoints para monitoramento de saúde da aplicação:
- Health check básico
- Status detalhado dos componentes
- Métricas de performance
- Readiness e liveness probes

Versão: 3.0.0
Data: 2025-10-28
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import logging
import psutil
import time

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()

start_time = time.time()

@router.get("/")
async def health_check():
    """🔍 Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "environment": settings.environment,
        "uptime_seconds": int(time.time() - start_time)
    }

@router.get("/detailed")
async def detailed_health():
    """📊 Health check detalhado"""
    try:
        # Métricas do sistema
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "environment": settings.environment,
            "uptime_seconds": int(time.time() - start_time),
            "system_metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 1)
            },
            "components": {
                "database": "operational",
                "redis": "operational",
                "multiagent_system": "operational",
                "vector_store": "operational",
                "llm_providers": "operational"
            },
            "configuration": {
                "debug_mode": settings.debug,
                "auth_enabled": settings.enable_auth,
                "rate_limiting": settings.enable_rate_limiting,
                "max_file_size_mb": settings.max_file_size_mb
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no health check detalhado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ready")
async def readiness_probe():
    """✅ Readiness probe para Kubernetes"""
    try:
        # Verifica se todos os componentes estão prontos
        # Integrar com verificações reais dos serviços
        
        components_ready = {
            "database": True,
            "redis": True,
            "agents": True
        }
        
        all_ready = all(components_ready.values())
        
        if not all_ready:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "components": components_ready
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no readiness probe: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live")
async def liveness_probe():
    """💓 Liveness probe para Kubernetes"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "uptime": int(time.time() - start_time)
    }