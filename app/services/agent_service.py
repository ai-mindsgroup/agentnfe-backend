#!/usr/bin/env python3
"""
🤖 Agent Service - API Moderna
==============================

Serviço para gerenciar agentes inteligentes.

Versão: 3.0.0
Data: 2025-10-29
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentService:
    """Serviço para gerenciar agentes inteligentes"""
    
    def __init__(self):
        """Inicializa o serviço de agentes"""
        self.orchestrator = None
        self._load_orchestrator()
    
    def _load_orchestrator(self):
        """Carrega o orquestrador de agentes"""
        try:
            from src.agent.orchestrator_agent import OrchestratorAgent
            self.orchestrator = OrchestratorAgent()
            logger.info("✅ OrchestratorAgent carregado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar OrchestratorAgent: {e}")
            self.orchestrator = None
    
    async def query(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa uma consulta usando os agentes
        
        Args:
            message: Mensagem/pergunta do usuário
            context: Contexto adicional
            agent_id: ID do agente específico (opcional)
        
        Returns:
            Resposta do agente
        """
        if not self.orchestrator:
            return {
                "response": "Sistema de agentes não disponível no momento.",
                "agent": "fallback",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Processa a consulta usando o orquestrador
            result = self.orchestrator.process_query(message, context or {})
            
            return {
                "response": result.get("response", "Sem resposta"),
                "agent": result.get("agent", "orchestrator"),
                "metadata": result.get("metadata", {}),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erro ao processar query: {e}")
            return {
                "response": f"Erro ao processar consulta: {str(e)}",
                "agent": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_agents_status(self) -> Dict[str, Any]:
        """
        Retorna status de todos os agentes
        
        Returns:
            Status dos agentes
        """
        if not self.orchestrator:
            return {
                "available": False,
                "agents": [],
                "message": "Sistema de agentes não disponível"
            }
        
        try:
            # Tenta obter status do orquestrador
            if hasattr(self.orchestrator, 'get_status'):
                return self.orchestrator.get_status()
            
            return {
                "available": True,
                "agents": [
                    {
                        "id": "orchestrator",
                        "name": "Orquestrador Central",
                        "status": "active"
                    }
                ],
                "message": "Sistema operacional"
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter status dos agentes: {e}")
            return {
                "available": False,
                "agents": [],
                "error": str(e)
            }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Lista todos os agentes disponíveis
        
        Returns:
            Lista de agentes
        """
        if not self.orchestrator:
            return []
        
        try:
            if hasattr(self.orchestrator, 'list_agents'):
                return self.orchestrator.list_agents()
            
            return [
                {
                    "id": "orchestrator",
                    "name": "Orquestrador Central",
                    "description": "Coordena e distribui tarefas entre agentes",
                    "status": "active"
                }
            ]
        except Exception as e:
            logger.error(f"❌ Erro ao listar agentes: {e}")
            return []
