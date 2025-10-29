#!/usr/bin/env python3
"""
🔐 Módulo de Segurança - API Moderna
==================================

Funções de autenticação, autorização e segurança.

Versão: 3.0.0
Data: 2025-10-28
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Obtém usuário atual baseado no token JWT"""
    
    # Se autenticação está desabilitada, retorna usuário padrão
    if not settings.enable_auth:
        return {
            "user_id": "dev_user",
            "username": "developer",
            "is_admin": True,
            "permissions": ["read", "write", "admin"]
        }
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação necessário",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Implementar validação JWT real aqui
    # Por enquanto, aceita qualquer token
    
    return {
        "user_id": "authenticated_user",
        "username": "user",
        "is_admin": False,
        "permissions": ["read", "write"]
    }

def verify_admin_permission(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verifica se usuário tem permissões de admin"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões de administrador necessárias"
        )
    return current_user