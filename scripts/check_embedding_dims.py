"""Verifica as dimensões da coluna embedding."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import psycopg
from src.settings import build_db_dsn

def check_embedding_dimensions():
    """Verifica dimensões da coluna embedding."""
    dsn = build_db_dsn()
    
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT atttypmod 
                FROM pg_attribute 
                WHERE attrelid = 'embeddings'::regclass 
                AND attname = 'embedding'
            """)
            result = cur.fetchone()
            
            if result:
                dimensions = result[0] - 4  # pgvector armazena dimensions + 4
                print(f"Dimensões da coluna embedding: {dimensions}")
            else:
                print("Coluna embedding não encontrada!")

if __name__ == '__main__':
    check_embedding_dimensions()
