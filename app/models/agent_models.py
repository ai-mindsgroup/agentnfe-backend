#!/usr/bin/env python3
"""
🤖 Modelos Pydantic para Agentes - API Moderna
==========================================

Modelos de dados para requests e responses
dos endpoints relacionados aos agentes inteligentes.

Versão: 3.0.0
Data: 2025-10-28
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    """Request para chat com agentes"""
    message: str = Field(..., description="Mensagem para o agente")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto adicional")
    use_memory: bool = Field(True, description="Usar memória da conversa")
    max_tokens: Optional[int] = Field(None, description="Limite de tokens na resposta")
    temperature: Optional[float] = Field(None, description="Criatividade da resposta (0-1)")

class ChatResponse(BaseModel):
    """Response do chat"""
    response: str = Field(..., description="Resposta do agente")
    session_id: str = Field(..., description="ID da sessão")
    timestamp: str = Field(..., description="Timestamp da resposta")
    agent_used: str = Field(..., description="Agente que processou a request")
    analysis_type: Optional[str] = Field(None, description="Tipo de análise realizada")
    confidence: Optional[float] = Field(None, description="Confiança da resposta (0-1)")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
    user_id: str = Field(..., description="ID do usuário")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")

class AgentQueryRequest(BaseModel):
    """Request para query específica de agente"""
    query: str = Field(..., description="Query para o agente")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parâmetros específicos")

class AgentQueryResponse(BaseModel):
    """Response de query de agente"""
    result: str = Field(..., description="Resultado da query")
    agent: str = Field(..., description="Agente que processou")
    confidence: float = Field(..., description="Confiança do resultado")
    processing_time: float = Field(..., description="Tempo de processamento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    session_id: Optional[str] = Field(None, description="ID da sessão")

class AgentStatusResponse(BaseModel):
    """Status de um agente específico"""
    agent: str = Field(..., description="Nome do agente")
    status: str = Field(..., description="Status atual")
    is_active: bool = Field(..., description="Se está ativo")
    last_activity: Optional[str] = Field(None, description="Última atividade")
    capabilities: List[str] = Field(default_factory=list, description="Capacidades")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas de performance")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")

class StreamChatResponse(BaseModel):
    """Response para streaming de chat"""
    chunk: str = Field(..., description="Chunk da resposta")
    is_final: bool = Field(False, description="Se é o chunk final")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados do chunk")