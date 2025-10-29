#!/usr/bin/env python3
"""
🤖 Router dos Agentes Inteligentes - API Moderna
============================================

Endpoints para interação com o sistema multiagente:
- Orquestrador central
- Agente de análise CSV
- Agente RAG (busca semântica)
- Agente de detecção de fraude
- Sistema de chat inteligente

Versão: 3.0.0
Data: 2025-10-28
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import logging
import asyncio
from uuid import uuid4

# Imports do sistema multiagente
try:
    from src.agent.orchestrator_agent import OrchestratorAgent
    from src.agent.csv_analysis_agent import CSVAnalysisAgent
    from src.agent.rag_agent import RAGAgent
    from src.embeddings.embeddings_analysis_agent import EmbeddingsAnalysisAgent
except ImportError as e:
    logging.warning(f"Alguns agentes não estão disponíveis: {e}")

# Imports da API
from app.core.config import get_settings
from app.core.security import get_current_user
from app.models.agent_models import (
    ChatRequest,
    ChatResponse,
    AgentQueryRequest,
    AgentQueryResponse,
    AgentStatusResponse,
    StreamChatResponse
)
from app.services.agent_service import AgentService
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)
settings = get_settings()

# Inicialização do router
router = APIRouter()

# Serviços
agent_service = AgentService()
session_service = SessionService()

# ============================================================================
# SISTEMA DE CHAT INTELIGENTE
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agents(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    💬 Chat inteligente com sistema multiagente
    
    O orquestrador analisa a mensagem e roteia automaticamente
    para o agente mais adequado (CSV, RAG, Fraude, etc.).
    
    **Features:**
    - Roteamento automático inteligente
    - Memória de conversação persistente
    - Análise contextual de dados
    - Detecção de intent
    """
    try:
        start_time = datetime.now()
        user_id = current_user.get("user_id", "anonymous")
        
        logger.info(f"💬 Chat iniciado - User: {user_id}, Session: {request.session_id}")
        
        # Processa com o sistema multiagente
        result = await agent_service.process_chat(
            message=request.message,
            session_id=request.session_id or f"session_{user_id}_{uuid4().hex[:8]}",
            user_id=user_id,
            context=request.context or {},
            use_memory=request.use_memory
        )
        
        # Atualiza estatísticas em background
        background_tasks.add_task(
            session_service.update_session_stats,
            request.session_id,
            user_id,
            len(request.message),
            result.get('agent_used', 'unknown')
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            response=result.get('content', result.get('response', '')),
            session_id=result.get('session_id', request.session_id),
            timestamp=datetime.now().isoformat(),
            agent_used=result.get('metadata', {}).get('agent_used', 'orchestrator'),
            analysis_type=result.get('metadata', {}).get('analysis_type'),
            confidence=result.get('metadata', {}).get('confidence'),
            processing_time=processing_time,
            user_id=user_id,
            metadata=result.get('metadata', {})
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar chat: {str(e)}")

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    🔄 Chat com streaming de resposta em tempo real
    
    Retorna a resposta do agente em chunks conforme vai sendo gerada,
    permitindo uma experiência mais fluida para o usuário.
    """
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            user_id = current_user.get("user_id", "anonymous")
            
            async for chunk in agent_service.process_chat_stream(
                message=request.message,
                session_id=request.session_id or f"stream_{user_id}_{uuid4().hex[:8]}",
                user_id=user_id,
                context=request.context or {}
            ):
                # Formato Server-Sent Events
                yield f"data: {chunk}\n\n"
                
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield f"data: {{\"error\": \"{str(e)}\", \"type\": \"error\"}}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx buffering disable
        }
    )

# ============================================================================
# ORQUESTRADOR CENTRAL
# ============================================================================

@router.post("/orchestrator/query", response_model=AgentQueryResponse)
async def query_orchestrator(
    request: AgentQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    🎯 Consulta direta ao Orquestrador Central
    
    Envia uma query diretamente para o orquestrador, que irá
    coordenar com outros agentes conforme necessário.
    
    **Use Cases:**
    - Consultas complexas que envolvem múltiplos agentes
    - Análises que requerem coordenação de recursos
    - Queries que precisam de contexto global
    """
    try:
        result = await agent_service.query_orchestrator(
            query=request.query,
            context=request.context,
            session_id=request.session_id,
            user_id=current_user.get("user_id")
        )
        
        return AgentQueryResponse(
            result=result.get('content', ''),
            agent="orchestrator",
            confidence=result.get('metadata', {}).get('confidence', 0.8),
            processing_time=result.get('processing_time', 0),
            metadata=result.get('metadata', {}),
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Erro no orquestrador: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orchestrator/status", response_model=AgentStatusResponse)
async def orchestrator_status():
    """🔍 Status detalhado do Orquestrador"""
    try:
        status = await agent_service.get_orchestrator_status()
        return AgentStatusResponse(
            agent="orchestrator",
            status=status.get('status', 'unknown'),
            is_active=status.get('is_active', False),
            last_activity=status.get('last_activity'),
            capabilities=status.get('capabilities', []),
            performance_metrics=status.get('metrics', {}),
            metadata=status
        )
    except Exception as e:
        logger.error(f"Erro ao obter status do orquestrador: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AGENTE CSV
# ============================================================================

@router.post("/csv/analyze", response_model=AgentQueryResponse)
async def analyze_csv(
    request: AgentQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    📊 Análise Inteligente de Dados CSV
    
    Usa o agente especializado em CSV para analisar dados
    tabulares com inteligência artificial.
    
    **Capacidades:**
    - Análise estatística automatizada
    - Detecção de padrões e outliers
    - Geração de insights
    - Sugestões de limpeza de dados
    """
    try:
        result = await agent_service.analyze_csv(
            query=request.query,
            context=request.context,
            user_id=current_user.get("user_id")
        )
        
        return AgentQueryResponse(
            result=result.get('content', ''),
            agent="csv_agent",
            confidence=result.get('confidence', 0.8),
            processing_time=result.get('processing_time', 0),
            metadata=result.get('metadata', {}),
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Erro na análise CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/csv/capabilities")
async def csv_agent_capabilities():
    """📊 Capacidades do Agente CSV"""
    return {
        "agent": "csv_agent",
        "capabilities": [
            "Análise estatística descritiva",
            "Detecção de outliers",
            "Análise de correlações",
            "Sugestões de limpeza",
            "Identificação de padrões",
            "Geração de insights",
            "Visualizações recomendadas"
        ],
        "supported_formats": ["CSV", "Excel", "Parquet", "JSON"],
        "max_file_size": "500MB",
        "max_rows": 1000000,
        "analysis_types": [
            "descriptive",
            "correlation",
            "outlier_detection",
            "pattern_analysis",
            "data_quality"
        ]
    }

# ============================================================================
# AGENTE RAG (BUSCA SEMÂNTICA)
# ============================================================================

@router.post("/rag/search", response_model=AgentQueryResponse)
async def rag_search(
    request: AgentQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    🔍 Busca Semântica com RAG
    
    Realiza busca semântica em documentos e dados
    usando Retrieval-Augmented Generation.
    
    **Features:**
    - Busca por similaridade semântica
    - Contextualização inteligente
    - Ranking de relevância
    - Combinação de múltiplas fontes
    """
    try:
        result = await agent_service.rag_search(
            query=request.query,
            context=request.context,
            user_id=current_user.get("user_id"),
            top_k=request.context.get('top_k', 5)
        )
        
        return AgentQueryResponse(
            result=result.get('content', ''),
            agent="rag_agent",
            confidence=result.get('confidence', 0.8),
            processing_time=result.get('processing_time', 0),
            metadata={
                **result.get('metadata', {}),
                'sources': result.get('sources', []),
                'similarity_scores': result.get('scores', [])
            },
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Erro na busca RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rag/status")
async def rag_agent_status():
    """🔍 Status do Sistema RAG"""
    try:
        status = await agent_service.get_rag_status()
        return {
            "agent": "rag_agent",
            "vector_store_status": status.get('vector_store_connected', False),
            "embeddings_model": status.get('embedding_model', 'unknown'),
            "total_documents": status.get('document_count', 0),
            "total_chunks": status.get('chunk_count', 0),
            "last_ingestion": status.get('last_ingestion'),
            "performance_metrics": status.get('metrics', {})
        }
    except Exception as e:
        logger.error(f"Erro ao obter status RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AGENTE DE DETECÇÃO DE FRAUDE
# ============================================================================

@router.post("/fraud/analyze", response_model=AgentQueryResponse)
async def analyze_fraud(
    request: AgentQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    🛡️ Análise de Detecção de Fraude
    
    Usa IA especializada para detectar padrões suspeitos
    e possíveis fraudes em dados financeiros.
    
    **Capacidades:**
    - Detecção de anomalias
    - Scoring de risco
    - Análise comportamental
    - Padrões temporais suspeitos
    """
    try:
        result = await agent_service.analyze_fraud(
            query=request.query,
            context=request.context,
            user_id=current_user.get("user_id")
        )
        
        return AgentQueryResponse(
            result=result.get('content', ''),
            agent="fraud_agent",
            confidence=result.get('confidence', 0.8),
            processing_time=result.get('processing_time', 0),
            metadata={
                **result.get('metadata', {}),
                'risk_score': result.get('risk_score'),
                'fraud_indicators': result.get('indicators', []),
                'recommendations': result.get('recommendations', [])
            },
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Erro na análise de fraude: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GERENCIAMENTO DE SESSÕES
# ============================================================================

@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """📜 Histórico da sessão de conversação"""
    try:
        history = await session_service.get_session_history(
            session_id=session_id,
            user_id=current_user.get("user_id"),
            limit=limit
        )
        return {
            "session_id": session_id,
            "history": history,
            "total_messages": len(history)
        }
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def clear_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """🗺️ Limpar sessão de conversação"""
    try:
        await session_service.clear_session(
            session_id=session_id,
            user_id=current_user.get("user_id")
        )
        return {"message": "Sessão limpa com sucesso", "session_id": session_id}
    except Exception as e:
        logger.error(f"Erro ao limpar sessão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/user/{user_id}")
async def list_user_sessions(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """📁 Listar sessões do usuário"""
    # Verifica se o usuário pode acessar as sessões
    if current_user.get("user_id") != user_id and not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        sessions = await session_service.list_user_sessions(user_id)
        return {"user_id": user_id, "sessions": sessions}
    except Exception as e:
        logger.error(f"Erro ao listar sessões: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STATUS GERAL DOS AGENTES
# ============================================================================

@router.get("/status", response_model=Dict[str, Any])
async def agents_status():
    """
    🔍 Status completo do sistema multiagente
    
    Retorna o status de todos os agentes e componentes
    do sistema, incluindo métricas de performance.
    """
    try:
        status = await agent_service.get_system_status()
        return {
            "system_status": "operational",
            "timestamp": datetime.now().isoformat(),
            "agents": status.get('agents', {}),
            "overall_health": status.get('health_score', 0),
            "active_sessions": await session_service.get_active_sessions_count(),
            "performance_metrics": status.get('metrics', {}),
            "capabilities": {
                "chat": True,
                "streaming": True,
                "csv_analysis": status.get('agents', {}).get('csv_agent', {}).get('available', False),
                "rag_search": status.get('agents', {}).get('rag_agent', {}).get('available', False),
                "fraud_detection": status.get('agents', {}).get('fraud_agent', {}).get('available', False)
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter status dos agentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))