#!/usr/bin/env python3
"""
💬 Session Service - API Moderna
================================

Serviço para gerenciar sessões de chat e histórico.

Versão: 3.0.0
Data: 2025-10-29
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class SessionService:
    """Serviço para gerenciar sessões de usuário"""
    
    def __init__(self):
        """Inicializa o serviço de sessões"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("✅ SessionService inicializado")
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Cria uma nova sessão
        
        Args:
            user_id: ID do usuário (opcional)
        
        Returns:
            ID da sessão criada
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id or "anonymous",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": [],
            "context": {}
        }
        
        logger.info(f"✅ Nova sessão criada: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém uma sessão pelo ID
        
        Args:
            session_id: ID da sessão
        
        Returns:
            Dados da sessão ou None se não existir
        """
        return self.sessions.get(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Adiciona uma mensagem ao histórico da sessão
        
        Args:
            session_id: ID da sessão
            role: Papel (user/assistant/system)
            content: Conteúdo da mensagem
            metadata: Metadados adicionais
        
        Returns:
            True se adicionado com sucesso
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"⚠️ Sessão não encontrada: {session_id}")
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        session["messages"].append(message)
        session["last_activity"] = datetime.now().isoformat()
        
        return True
    
    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém histórico de mensagens da sessão
        
        Args:
            session_id: ID da sessão
            limit: Limite de mensagens (opcional)
        
        Returns:
            Lista de mensagens
        """
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        messages = session["messages"]
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def update_context(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Atualiza contexto da sessão
        
        Args:
            session_id: ID da sessão
            context: Novo contexto
        
        Returns:
            True se atualizado com sucesso
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session["context"].update(context)
        session["last_activity"] = datetime.now().isoformat()
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Deleta uma sessão
        
        Args:
            session_id: ID da sessão
        
        Returns:
            True se deletado com sucesso
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"✅ Sessão deletada: {session_id}")
            return True
        
        return False
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista todas as sessões (opcionalmente filtrado por usuário)
        
        Args:
            user_id: ID do usuário para filtrar (opcional)
        
        Returns:
            Lista de sessões
        """
        sessions = list(self.sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s["user_id"] == user_id]
        
        return sessions
