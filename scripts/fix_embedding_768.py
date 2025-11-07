"""Atualiza dimensões da coluna embedding para 768 via psycopg."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import psycopg
from src.settings import build_db_dsn

def fix_embedding_dimensions():
    """Atualiza dimensões para 768."""
    dsn = build_db_dsn()
    
    print("Conectando ao banco...")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            print("1. Truncando tabela embeddings...")
            cur.execute("TRUNCATE TABLE public.embeddings CASCADE")
            
            print("2. Removendo índice HNSW...")
            cur.execute("DROP INDEX IF EXISTS idx_embeddings_embedding_hnsw")
            
            print("3. Alterando tipo da coluna embedding para vector(768)...")
            cur.execute("ALTER TABLE public.embeddings ALTER COLUMN embedding TYPE vector(768)")
            
            print("4. Recriando índice HNSW...")
            cur.execute("CREATE INDEX idx_embeddings_embedding_hnsw ON public.embeddings USING hnsw (embedding vector_cosine_ops)")
            
            print("5. Dropando função match_embeddings antiga...")
            cur.execute("DROP FUNCTION IF EXISTS match_embeddings(vector, float, int)")
            
            print("6. Criando nova função match_embeddings...")
            cur.execute("""
                CREATE OR REPLACE FUNCTION match_embeddings(
                    query_embedding vector(768),
                    similarity_threshold float DEFAULT 0.5,
                    match_count int DEFAULT 10
                )
                RETURNS TABLE (
                    id uuid,
                    chunk_text text,
                    metadata jsonb,
                    similarity float
                )
                LANGUAGE sql STABLE
                AS $$
                    SELECT
                        embeddings.id,
                        embeddings.chunk_text,
                        embeddings.metadata,
                        1 - (embeddings.embedding <=> query_embedding) as similarity
                    FROM embeddings
                    WHERE 1 - (embeddings.embedding <=> query_embedding) > similarity_threshold
                    ORDER BY similarity DESC
                    LIMIT match_count;
                $$;
            """)
            
            conn.commit()
            print("✓ Atualização completa!")
            
            # Verifica
            cur.execute("""
                SELECT atttypmod 
                FROM pg_attribute 
                WHERE attrelid = 'embeddings'::regclass 
                AND attname = 'embedding'
            """)
            result = cur.fetchone()
            if result:
                dimensions = result[0] - 4
                print(f"\nVerificação: Dimensões = {dimensions}")

if __name__ == '__main__':
    fix_embedding_dimensions()
