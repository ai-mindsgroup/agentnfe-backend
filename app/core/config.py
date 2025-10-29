#!/usr/bin/env python3
"""
🔧 Configurações da API Moderna - AgentNFE Backend
================================================

Sistema de configurações baseado em Pydantic Settings com suporte
a múltiplos ambientes e configuração via variáveis de ambiente.

Ambientes suportados:
- development: Desenvolvimento local
- staging: Ambiente de homologação
- production: Produção

Versão: 3.0.0 - Fixed for Pydantic v2
Data: 2025-10-29
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from pathlib import Path
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    model_config = SettingsConfigDict(
        env_file="configs/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ========================================================================
    # CONFIGURAÇÕES BÁSICAS
    # ========================================================================
    
    # Aplicação
    app_name: str = Field(default="AgentNFE Backend - API Moderna", validation_alias="APP_NAME")
    app_version: str = Field(default="3.0.0", validation_alias="APP_VERSION")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    
    # Servidor
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8012, validation_alias="PORT")
    
    # Segurança
    secret_key: str = Field(default="", validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # ========================================================================
    # CORS E HOSTS PERMITIDOS
    # ========================================================================
    
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"]
    )
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    # ========================================================================
    # BANCO DE DADOS
    # ========================================================================
    
    # PostgreSQL/Supabase
    database_url: str = Field(default="")
    supabase_url: str = Field(default="")
    supabase_key: str = Field(default="")
    supabase_service_key: str = Field(default="")
    
    # Configurações de conexão
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)
    db_pool_timeout: int = Field(default=30)
    
    # ========================================================================
    # REDIS (Para tasks assíncronas e cache)
    # ========================================================================
    
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_password: Optional[str] = Field(default=None)
    redis_db: int = Field(default=0)
    
    # ========================================================================
    # PROVEDORES DE IA/LLM
    # ========================================================================
    
    # OpenAI
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    openai_max_tokens: int = Field(default=4096)
    
    # Google Gemini
    google_api_key: str = Field(default="")
    google_model: str = Field(default="gemini-1.5-flash")
    
    # Groq
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="llama-3.1-70b-versatile")
    
    # Perplexity/Sonar
    sonar_api_key: str = Field(default="")
    sonar_model: str = Field(default="llama-3.1-sonar-large-128k-online")
    
    # ========================================================================
    # SISTEMA MULTIAGENTE
    # ========================================================================
    
    # Configurações dos agentes
    enable_orchestrator: bool = Field(default=True)
    enable_csv_agent: bool = Field(default=True)
    enable_rag_agent: bool = Field(default=True)
    enable_fraud_agent: bool = Field(default=True)
    
    # Embeddings
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    
    # ========================================================================
    # RATE LIMITING E SEGURANÇA
    # ========================================================================
    
    enable_auth: bool = Field(default=False)  # False para dev
    enable_rate_limiting: bool = Field(default=True)
    
    # Rate limits por endpoint
    rate_limit_requests_per_minute: int = Field(default=60)
    rate_limit_requests_per_hour: int = Field(default=1000)
    rate_limit_upload_per_hour: int = Field(default=10)
    
    # Limites de arquivo
    max_file_size_mb: int = Field(default=500)
    max_files_per_user: int = Field(default=50)
    
    # ========================================================================
    # DIRETÓRIOS E ARQUIVOS
    # ========================================================================
    
    data_dir: str = Field(default="data")
    upload_dir: str = Field(default="data/uploads")
    processed_dir: str = Field(default="data/processed")
    temp_dir: str = Field(default="data/temp")
    logs_dir: str = Field(default="logs")
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    enable_file_logging: bool = Field(default=True)
    log_rotation: str = Field(default="1 day")
    log_retention: str = Field(default="30 days")
    
    # ========================================================================
    # MONITORAMENTO E MÉTRICAS
    # ========================================================================
    
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=False)
    metrics_port: int = Field(default=9090)
    
    # Sentry (Error tracking)
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: str = Field(default="development")
    
    # ========================================================================
    # WEBSOCKET
    # ========================================================================
    
    enable_websocket: bool = Field(default=True)
    ws_heartbeat_interval: int = Field(default=30)
    ws_max_connections: int = Field(default=100)
    
    # ========================================================================
    # TAREFAS ASSÍNCRONAS
    # ========================================================================
    
    enable_celery: bool = Field(default=False)
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")
    
    # ========================================================================
    # HELPERS E VALIDAÇÕES
    # ========================================================================
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.environment == "production"
    
    @property
    def is_staging(self) -> bool:
        """Verifica se está em ambiente de staging"""
        return self.environment == "staging"
    
    def get_upload_path(self, filename: str) -> Path:
        """Retorna caminho completo para arquivo de upload"""
        upload_path = Path(self.upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path / filename
    
    def get_processed_path(self, filename: str) -> Path:
        """Retorna caminho completo para arquivo processado"""
        processed_path = Path(self.processed_dir)
        processed_path.mkdir(parents=True, exist_ok=True)
        return processed_path / filename
    
    def get_temp_path(self, filename: str) -> Path:
        """Retorna caminho completo para arquivo temporário"""
        temp_path = Path(self.temp_dir)
        temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path / filename


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações.
    Cached para evitar recarregamento desnecessário.
    """
    return Settings()


# Instância global para facilitar imports
settings = get_settings()
