#!/usr/bin/env python3
"""
🚀 API Moderna - AgentNFE Backend
==================================

API RESTful completa e moderna para o sistema multiagente AgentNFE.
Arquitetura modular, segura e escalável com FastAPI.

Features:
- Sistema multiagente integrado
- Autenticação JWT
- Rate limiting
- WebSocket para tasks longas
- Documentação automática
- Monitoramento e analytics
- Processamento assíncrono

Versão: 3.0.0
Data: 2025-10-28
"""

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Imports dos roteadores
from app.routers import (
    agents,
    data_processing,
    embeddings,
    fraud_detection,
    analytics,
    tasks,
    health
)

# Imports dos middlewares
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware

# Imports das configurações
from app.core.config import Settings, get_settings
from app.core.database import init_database, close_database
from app.core.security import get_current_user

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_moderna.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Lifecycle da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando API Moderna - AgentNFE Backend")
    await init_database()
    logger.info("✅ Sistema inicializado com sucesso")
    
    yield
    
    # Shutdown
    logger.info("🔄 Encerrando aplicação")
    await close_database()
    logger.info("✅ Aplicação encerrada com sucesso")

# Configurações
settings = get_settings()

# Inicialização do FastAPI
app = FastAPI(
    title="AgentNFE Backend - API Moderna",
    description="""
    🤖 **Sistema Multiagente para Análise Inteligente de Dados**
    
    Esta API moderna oferece:
    - 🧠 **Agentes Inteligentes**: RAG, CSV, Orquestrador
    - 🛡️ **Detecção de Fraude**: IA avançada para segurança
    - 📊 **Análise de Dados**: Processamento inteligente de CSV
    - 🔍 **Busca Semântica**: Sistema RAG com embeddings
    - 📈 **Analytics**: Monitoramento e métricas em tempo real
    - 🔐 **Segurança**: JWT, Rate limiting, Validação
    - ⚡ **Performance**: Processamento assíncrono e WebSocket
    
    **Versão**: 3.0.0 | **Ambiente**: {env}
    """.format(env=settings.environment),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    terms_of_service="/terms",
    contact={
        "name": "AI Minds Group",
        "url": "https://github.com/ai-mindsgroup/agentnfe-backend",
        "email": "contact@aiminds.group",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# ============================================================================
# MIDDLEWARES - Configuração de segurança e performance
# ============================================================================

# Security Headers
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# CORS - Configurável por ambiente
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Task-ID", "X-Rate-Limit-Remaining"]
)

# Compressão GZIP
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middlewares customizados
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# ============================================================================
# STATIC FILES - Servir arquivos estáticos
# ============================================================================

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/histogramas", StaticFiles(directory="outputs/histogramas"), name="histogramas")

# ============================================================================
# ROUTERS - Endpoints organizados por funcionalidade
# ============================================================================

# Health Check (sem autenticação)
app.include_router(
    health.router,
    prefix="/health",
    tags=["🔋 Health & Status"]
)

# API v1 - Endpoints principais
api_v1_prefix = "/api/v1"

# Agentes inteligentes
app.include_router(
    agents.router,
    prefix=f"{api_v1_prefix}/agents",
    tags=["🤖 Agentes Inteligentes"],
    dependencies=[Depends(get_current_user)]
)

# Processamento de dados
app.include_router(
    data_processing.router,
    prefix=f"{api_v1_prefix}/data",
    tags=["📊 Processamento de Dados"],
    dependencies=[Depends(get_current_user)]
)

# Sistema RAG/Embeddings
app.include_router(
    embeddings.router,
    prefix=f"{api_v1_prefix}/embeddings",
    tags=["🔍 Sistema RAG"],
    dependencies=[Depends(get_current_user)]
)

# Detecção de fraude
app.include_router(
    fraud_detection.router,
    prefix=f"{api_v1_prefix}/fraud",
    tags=["🛡️ Detecção de Fraude"],
    dependencies=[Depends(get_current_user)]
)

# Analytics e monitoramento
app.include_router(
    analytics.router,
    prefix=f"{api_v1_prefix}/analytics",
    tags=["📈 Analytics & Monitoramento"],
    dependencies=[Depends(get_current_user)]
)

# Sistema de tasks assíncronas
app.include_router(
    tasks.router,
    prefix=f"{api_v1_prefix}/tasks",
    tags=["⚡ Tasks Assíncronas"],
    dependencies=[Depends(get_current_user)]
)

# ============================================================================
# WEBSOCKET - Para atualizações em tempo real
# ============================================================================

@app.websocket("/ws/tasks/{task_id}")
async def websocket_task_updates(websocket: WebSocket, task_id: str):
    """WebSocket para atualizações de tasks em tempo real"""
    await websocket.accept()
    try:
        # Implementar lógica de updates de tasks
        from app.services.task_service import TaskService
        task_service = TaskService()
        
        async for update in task_service.get_task_updates(task_id):
            await websocket.send_json(update)
            
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        await websocket.close(code=1000)

@app.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    """WebSocket para monitoramento do sistema em tempo real"""
    await websocket.accept()
    try:
        from app.services.monitoring_service import MonitoringService
        monitoring = MonitoringService()
        
        async for metrics in monitoring.get_real_time_metrics():
            await websocket.send_json(metrics)
            
    except Exception as e:
        logger.error(f"Erro no WebSocket de monitoramento: {e}")
        await websocket.close(code=1000)

# ============================================================================
# ROOT ENDPOINTS - Endpoints principais
# ============================================================================

@app.get("/", include_in_schema=False)
async def root():
    """Redirect para documentação"""
    return RedirectResponse(url="/docs")

@app.get("/info", response_model=Dict[str, Any])
async def api_info():
    """Informações da API"""
    return {
        "name": "AgentNFE Backend - API Moderna",
        "version": "3.0.0",
        "description": "Sistema multiagente para análise inteligente de dados",
        "environment": settings.environment,
        "timestamp": datetime.now().isoformat(),
        "features": {
            "authentication": "JWT Bearer Token",
            "rate_limiting": "Configurável por usuário",
            "async_tasks": "Redis + WebSocket",
            "agents": ["Orchestrator", "CSV", "RAG", "Fraud Detection"],
            "data_formats": ["CSV", "Excel", "JSON", "Parquet"],
            "ai_providers": ["OpenAI", "Google Gemini", "Groq"]
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "api_v1": "/api/v1"
        },
        "support": {
            "github": "https://github.com/ai-mindsgroup/agentnfe-backend",
            "issues": "https://github.com/ai-mindsgroup/agentnfe-backend/issues"
        }
    }

@app.get("/terms")
async def terms_of_service():
    """Termos de serviço"""
    return {
        "terms": "Termos de Uso - AgentNFE Backend",
        "version": "1.0",
        "effective_date": "2025-10-28",
        "description": "API para uso interno e desenvolvimento. Respeite os limites de rate limiting e use autenticação adequada.",
        "contact": "contact@aiminds.group"
    }

# ============================================================================
# ERROR HANDLERS - Tratamento global de erros
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "O endpoint solicitado não existe",
            "suggestion": "Consulte /docs para ver endpoints disponíveis",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Erro interno: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Erro interno do servidor",
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )

# ============================================================================
# STARTUP EVENT - Validações iniciais
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Validações e configurações no startup"""
    logger.info("🔍 Executando validações de startup...")
    
    # Validar configurações críticas
    if not settings.secret_key:
        logger.error("❌ SECRET_KEY não configurado!")
        raise ValueError("SECRET_KEY é obrigatório")
    
    # Validar conexões com banco de dados
    try:
        from app.core.database import test_connection
        await test_connection()
        logger.info("✅ Conexão com banco de dados validada")
    except Exception as e:
        logger.error(f"❌ Erro na conexão com banco: {e}")
    
    # Validar sistema multiagente
    try:
        from src.agent.orchestrator_agent import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        logger.info("✅ Sistema multiagente carregado")
    except Exception as e:
        logger.warning(f"⚠️ Sistema multiagente limitado: {e}")
    
    logger.info("🎯 API Moderna iniciada com sucesso!")

# ============================================================================
# MAIN - Execução da aplicação
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AgentNFE Backend - API Moderna v3.0.0")
    print("=" * 60)
    print(f"📍 Servidor: http://{settings.host}:{settings.port}")
    print(f"📚 Documentação: http://{settings.host}:{settings.port}/docs")
    print(f"🔍 ReDoc: http://{settings.host}:{settings.port}/redoc")
    print(f"🌍 Ambiente: {settings.environment.upper()}")
    print(f"🔐 Autenticação: {'✅ Ativa' if settings.enable_auth else '❌ Desabilitada'}")
    print(f"⚡ Rate Limiting: {'✅ Ativo' if settings.enable_rate_limiting else '❌ Desabilitado'}")
    print("\n🎯 Recursos Disponíveis:")
    print("   • Sistema Multiagente (RAG, CSV, Fraude)")
    print("   • Processamento Assíncrono de Dados")
    print("   • WebSocket para Updates em Tempo Real")
    print("   • Analytics e Monitoramento Avançado")
    print("   • Autenticação JWT e Rate Limiting")
    print("\n⏹️ Pressione Ctrl+C para parar\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=True,
        reload_dirs=["app", "src"] if settings.debug else None
    )