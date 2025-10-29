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

Versão: 3.0.0
Data: 2025-10-28
"""

from pydantic import BaseSettings, Field, validator
from typing import List, Optional, Union
from pathlib import Path
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Configurações principais da aplicação"""
    
    # ========================================================================
    # CONFIGURAÇÕES BÁSICAS
    # ========================================================================
    
    # Aplicação
    app_name: str = Field("AgentNFE Backend - API Moderna", env="APP_NAME")
    app_version: str = Field("3.0.0", env="APP_VERSION")
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    # Servidor
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8012, env="PORT")
    
    # Segurança
    secret_key: str = Field("", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # ========================================================================
    # CORS E HOSTS PERMITIDOS
    # ========================================================================
    
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"],
        env="ALLOWED_HOSTS"
    )
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    # ========================================================================
    # BANCO DE DADOS
    # ========================================================================
    
    # PostgreSQL/Supabase
    database_url: str = Field("", env="DATABASE_URL")
    supabase_url: str = Field("", env="SUPABASE_URL")
    supabase_key: str = Field("", env="SUPABASE_KEY")
    supabase_service_key: str = Field("", env="SUPABASE_SERVICE_KEY")
    
    # Configurações de conexão
    db_pool_size: int = Field(10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(30, env="DB_POOL_TIMEOUT")
    
    # ========================================================================
    # REDIS (Para tasks assíncronas e cache)
    # ========================================================================
    
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = Field(0, env="REDIS_DB")
    
    # ========================================================================
    # PROVEDORES DE IA/LLM
    # ========================================================================
    
    # OpenAI
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(4096, env="OPENAI_MAX_TOKENS")
    
    # Google Gemini
    google_api_key: str = Field("", env="GOOGLE_API_KEY")
    google_model: str = Field("gemini-1.5-flash", env="GOOGLE_MODEL")
    
    # Groq
    groq_api_key: str = Field("", env="GROQ_API_KEY")
    groq_model: str = Field("llama-3.1-70b-versatile", env="GROQ_MODEL")
    
    # Perplexity/Sonar
    sonar_api_key: str = Field("", env="SONAR_API_KEY")
    sonar_model: str = Field("llama-3.1-sonar-large-128k-online", env="SONAR_MODEL")
    
    # ========================================================================
    # SISTEMA MULTIAGENTE
    # ========================================================================
    
    # Configurações dos agentes
    enable_orchestrator: bool = Field(True, env="ENABLE_ORCHESTRATOR")
    enable_csv_agent: bool = Field(True, env="ENABLE_CSV_AGENT")
    enable_rag_agent: bool = Field(True, env="ENABLE_RAG_AGENT")
    enable_fraud_agent: bool = Field(True, env="ENABLE_FRAUD_AGENT")
    
    # Embeddings
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    embedding_dimension: int = Field(384, env="EMBEDDING_DIMENSION")
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    
    # ========================================================================
    # RATE LIMITING E SEGURANÇA
    # ========================================================================
    
    enable_auth: bool = Field(True, env="ENABLE_AUTH")
    enable_rate_limiting: bool = Field(True, env="ENABLE_RATE_LIMITING")
    
    # Rate limits por endpoint
    rate_limit_requests_per_minute: int = Field(60, env="RATE_LIMIT_RPM")
    rate_limit_requests_per_hour: int = Field(1000, env="RATE_LIMIT_RPH")
    rate_limit_upload_per_hour: int = Field(10, env="RATE_LIMIT_UPLOAD_PER_HOUR")
    
    # Limites de arquivo
    max_file_size_mb: int = Field(500, env="MAX_FILE_SIZE_MB")
    max_files_per_user: int = Field(50, env="MAX_FILES_PER_USER")
    
    # ========================================================================
    # DIRETÓRIOS E ARQUIVOS
    # ========================================================================
    
    # Diretórios
    upload_dir: str = Field("uploads", env="UPLOAD_DIR")
    static_dir: str = Field("static", env="STATIC_DIR")
    logs_dir: str = Field("logs", env="LOGS_DIR")
    temp_dir: str = Field("temp", env="TEMP_DIR")
    outputs_dir: str = Field("outputs", env="OUTPUTS_DIR")
    histograms_dir: str = Field("outputs/histogramas", env="HISTOGRAMS_DIR")
    
    # ========================================================================
    # MONITORAMENTO E LOGGING
    # ========================================================================
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")  # json ou text
    enable_request_logging: bool = Field(True, env="ENABLE_REQUEST_LOGGING")
    
    # Métricas
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(9090, env="METRICS_PORT")
    
    # ========================================================================
    # CONFIGURAÇÕES POR AMBIENTE
    # ========================================================================
    
    @validator('debug')
    def set_debug_mode(cls, v, values):
        environment = values.get('environment', 'development')
        if environment == 'development':
            return True
        return v
    
    @validator('log_level')
    def set_log_level_by_env(cls, v, values):
        environment = values.get('environment', 'development')
        debug = values.get('debug', False)
        
        if debug or environment == 'development':
            return 'DEBUG'
        elif environment == 'staging':
            return 'INFO'
        elif environment == 'production':
            return 'WARNING'
        return v
    
    @validator('enable_auth')
    def disable_auth_in_dev(cls, v, values):
        environment = values.get('environment', 'development')
        if environment == 'development':
            return False  # Desabilita auth em desenvolvimento por padrão
        return v
    
    # ========================================================================
    # PROPRIEDADES COMPUTADAS
    # ========================================================================
    
    @property
    def is_development(self) -> bool:
        return self.environment == 'development'
    
    @property
    def is_production(self) -> bool:
        return self.environment == 'production'
    
    @property
    def is_staging(self) -> bool:
        return self.environment == 'staging'
    
    @property
    def database_config(self) -> dict:
        """Configuração completa do banco de dados"""
        return {
            "url": self.database_url or self.supabase_url,
            "supabase_key": self.supabase_key,
            "service_key": self.supabase_service_key,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout
        }
    
    @property
    def llm_config(self) -> dict:
        """Configuração dos provedores LLM"""
        return {
            "openai": {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "max_tokens": self.openai_max_tokens,
                "enabled": bool(self.openai_api_key)
            },
            "google": {
                "api_key": self.google_api_key,
                "model": self.google_model,
                "enabled": bool(self.google_api_key)
            },
            "groq": {
                "api_key": self.groq_api_key,
                "model": self.groq_model,
                "enabled": bool(self.groq_api_key)
            },
            "sonar": {
                "api_key": self.sonar_api_key,
                "model": self.sonar_model,
                "enabled": bool(self.sonar_api_key)
            }
        }
    
    @property
    def agent_config(self) -> dict:
        """Configuração dos agentes"""
        return {
            "orchestrator": self.enable_orchestrator,
            "csv_agent": self.enable_csv_agent,
            "rag_agent": self.enable_rag_agent,
            "fraud_agent": self.enable_fraud_agent,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
    
    @property
    def security_config(self) -> dict:
        """Configuração de segurança"""
        return {
            "enable_auth": self.enable_auth,
            "enable_rate_limiting": self.enable_rate_limiting,
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "token_expire_minutes": self.access_token_expire_minutes,
            "rate_limits": {
                "per_minute": self.rate_limit_requests_per_minute,
                "per_hour": self.rate_limit_requests_per_hour,
                "upload_per_hour": self.rate_limit_upload_per_hour
            },
            "file_limits": {
                "max_size_mb": self.max_file_size_mb,
                "max_files_per_user": self.max_files_per_user
            }
        }
    
    # ========================================================================
    # MÉTODOS UTILITÁRIOS
    # ========================================================================
    
    def create_directories(self):
        """Cria diretórios necessários se não existirem"""
        directories = [
            self.upload_dir,
            self.static_dir,
            self.logs_dir,
            self.temp_dir,
            self.outputs_dir,
            self.histograms_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate_required_settings(self):
        """Valida configurações obrigatórias"""
        errors = []
        
        if self.enable_auth and not self.secret_key:
            errors.append("SECRET_KEY é obrigatório quando autenticação está habilitada")
        
        if self.enable_rag_agent and not self.supabase_url:
            errors.append("SUPABASE_URL é obrigatório para o agente RAG")
        
        # Verifica se pelo menos um provedor LLM está configurado
        llm_providers = [self.openai_api_key, self.google_api_key, self.groq_api_key, self.sonar_api_key]
        if not any(llm_providers):
            errors.append("Pelo menos um provedor LLM deve estar configurado")
        
        if errors:
            raise ValueError("Configurações inválidas:\n" + "\n".join(f"- {error}" for error in errors))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True

# ============================================================================
# CONFIGURAÇÕES ESPECÍFICAS POR AMBIENTE
# ============================================================================

class DevelopmentSettings(Settings):
    """Configurações para ambiente de desenvolvimento"""
    environment: str = "development"
    debug: bool = True
    enable_auth: bool = False
    log_level: str = "DEBUG"
    enable_request_logging: bool = True
    
class StagingSettings(Settings):
    """Configurações para ambiente de staging/homologação"""
    environment: str = "staging"
    debug: bool = False
    enable_auth: bool = True
    log_level: str = "INFO"
    
class ProductionSettings(Settings):
    """Configurações para ambiente de produção"""
    environment: str = "production"
    debug: bool = False
    enable_auth: bool = True
    log_level: str = "WARNING"
    enable_request_logging: bool = False
    
    # Rate limits mais restritivos em produção
    rate_limit_requests_per_minute: int = 30
    rate_limit_requests_per_hour: int = 500
    rate_limit_upload_per_hour: int = 5

# ============================================================================
# FACTORY FUNCTION
# ============================================================================

@lru_cache()
def get_settings() -> Settings:
    """Factory function para obter configurações baseado no ambiente"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    settings_map = {
        "development": DevelopmentSettings,
        "staging": StagingSettings,
        "production": ProductionSettings
    }
    
    settings_class = settings_map.get(environment, DevelopmentSettings)
    settings = settings_class()
    
    # Cria diretórios necessários
    settings.create_directories()
    
    # Valida configurações obrigatórias (apenas em produção)
    if settings.is_production:
        settings.validate_required_settings()
    
    return settings

# ============================================================================
# CONFIGURAÇÕES GLOBAIS - Para compatibilidade com código existente
# ============================================================================

# Instância global das configurações
_settings = get_settings()

# Exporta variáveis para compatibilidade com código existente
SECRET_KEY = _settings.secret_key
SUPABASE_URL = _settings.supabase_url
SUPABASE_KEY = _settings.supabase_key
GOOGLE_API_KEY = _settings.google_api_key
OPENAI_API_KEY = _settings.openai_api_key
GROQ_API_KEY = _settings.groq_api_key
SONAR_API_KEY = _settings.sonar_api_key

API_HOST = _settings.host
API_PORT = _settings.port

HISTOGRAMS_DIR = _settings.histograms_dir
UPLOAD_DIR = _settings.upload_dir
LOGS_DIR = _settings.logs_dir