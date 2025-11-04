"""Script simplificado para executar migrations essenciais via Supabase REST API."""
from pathlib import Path
from dotenv import load_dotenv
import os
import requests

# Carregar .env
ROOT = Path(__file__).parent
ENV_PATH = ROOT / "configs" / ".env"
load_dotenv(ENV_PATH)

MIGRATIONS_DIR = ROOT / "migrations"

def execute_sql_via_rest(sql: str, supabase_url: str, service_key: str):
    """Tenta executar SQL via REST API do Supabase."""
    # Supabase REST API não executa SQL arbitrário por segurança
    # Esta função é apenas ilustrativa
    print("⚠️  Supabase REST API não permite execução de SQL arbitrário")
    return False

def main():
    print("=" * 70)
    print("CRIAR SCHEMA DO BANCO DE DADOS - INSTRUÇÕES")
    print("=" * 70)
    
    supabase_url = os.getenv("SUPABASE_URL")
    
    print(f"\n🎯 Seu projeto Supabase: {supabase_url}")
    print("\n📋 PASSO A PASSO para criar as tabelas:")
    print()
    print("1️⃣  Acesse o SQL Editor do Supabase:")
    print(f"   https://supabase.com/dashboard/project/ncefmfiulpwssaajybtl/sql/new")
    print()
    print("2️⃣  Cole e execute este SQL (clique em RUN):")
    print()
    print("-" * 70)
    
    # SQL consolidado essencial
    sql = """
-- Habilitar extensões
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de embeddings
CREATE TABLE IF NOT EXISTS public.embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de chunks
CREATE TABLE IF NOT EXISTS public.chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_chunks_source FOREIGN KEY (source_id) 
        REFERENCES public.embeddings(id) ON DELETE CASCADE
);

-- Tabela de metadata
CREATE TABLE IF NOT EXISTS public.metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    content TEXT,
    key TEXT,
    value JSONB DEFAULT '{}'::jsonb,
    timestamp TEXT,
    source TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de memória de conversação
CREATE TABLE IF NOT EXISTS public.conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_embeddings_embedding_hnsw 
    ON public.embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_embeddings_metadata_gin 
    ON public.embeddings USING gin (metadata);
CREATE INDEX IF NOT EXISTS idx_chunks_metadata_gin 
    ON public.chunks USING gin (metadata);
CREATE INDEX IF NOT EXISTS idx_metadata_value_gin 
    ON public.metadata USING gin (value);
CREATE INDEX IF NOT EXISTS idx_conversation_session 
    ON public.conversation_memory (session_id);

-- Função de busca vetorial
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    chunk_text TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.chunk_text,
        e.metadata,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM embeddings e
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
"""
    
    print(sql)
    print("-" * 70)
    print()
    print("3️⃣  Após executar, teste novamente a conexão:")
    print("   python test_db_connection.py")
    print()
    print("=" * 70)
    
    # Salvar SQL em arquivo para facilitar
    output_file = ROOT / "setup_database.sql"
    output_file.write_text(sql, encoding="utf-8")
    print(f"✅ SQL salvo em: {output_file}")
    print(f"   Você pode copiar deste arquivo e colar no Supabase SQL Editor")
    print()

if __name__ == "__main__":
    main()
