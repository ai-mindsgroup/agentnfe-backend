"""
Teste de busca vetorial com embeddings de notas fiscais.

Testa a funcionalidade de similaridade semântica usando os embeddings gerados.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logging_config import get_logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.settings import GOOGLE_API_KEY
import psycopg
from src.settings import build_db_dsn
import json

logger = get_logger(__name__)


def test_vector_search(query: str, top_k: int = 5, threshold: float = 0.5):
    """
    Testa busca vetorial com uma query.
    
    Args:
        query: Texto da query
        top_k: Número de resultados
        threshold: Threshold de similaridade
    """
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}\n")
    
    # Gera embedding da query
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    
    print("Gerando embedding da query...")
    query_embedding = embeddings_model.embed_query(query)
    print(f"✓ Embedding gerado ({len(query_embedding)} dimensões)")
    
    # Busca no banco
    print(f"\nBuscando top {top_k} resultados similares (threshold={threshold})...")
    
    dsn = build_db_dsn()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Usa a função match_embeddings
            cur.execute("""
                SELECT * FROM match_embeddings(%s::vector(768), %s, %s)
            """, (str(query_embedding), threshold, top_k))
            
            results = cur.fetchall()
            
            if not results:
                print("\n❌ Nenhum resultado encontrado!")
                return
            
            print(f"\n✓ {len(results)} resultado(s) encontrado(s):\n")
            
            for idx, row in enumerate(results, 1):
                embedding_id, chunk_text, metadata, similarity = row
                
                print(f"{'─'*80}")
                print(f"RESULTADO #{idx}")
                print(f"{'─'*80}")
                print(f"Similaridade: {similarity:.4f}")
                print(f"ID: {embedding_id}")
                
                if metadata:
                    meta = metadata if isinstance(metadata, dict) else json.loads(metadata)
                    print(f"\nMetadados:")
                    print(f"  Nota: {meta.get('numero_nota', 'N/A')}")
                    print(f"  Série: {meta.get('serie', 'N/A')}")
                    print(f"  Emitente: {meta.get('nome_emitente', 'N/A')}")
                    print(f"  CNPJ: {meta.get('cnpj_emitente', 'N/A')}")
                    print(f"  Valor: R$ {meta.get('valor_total', 0):.2f}")
                    print(f"  CFOP: {meta.get('cfop', 'N/A')}")
                    print(f"  Chunk: {meta.get('chunk_index', 0) + 1}/{meta.get('total_chunks', 1)}")
                
                print(f"\nConteúdo (primeiros 300 chars):")
                print(f"{chunk_text[:300]}...")
                print()


def main():
    """Testa diferentes queries de busca vetorial."""
    
    # Verifica quantos embeddings temos
    dsn = build_db_dsn()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM embeddings")
            count = cur.fetchone()[0]
            print(f"\n{'='*80}")
            print(f"BANCO VETORIAL")
            print(f"{'='*80}")
            print(f"Total de embeddings: {count}")
            
            if count == 0:
                print("\n❌ Nenhum embedding encontrado no banco!")
                print("Execute primeiro: python scripts/generate_nfe_embeddings.py --test")
                return
    
    # Testes de busca
    print(f"\n{'='*80}")
    print("TESTES DE BUSCA VETORIAL")
    print(f"{'='*80}")
    
    # Teste 1: Busca por tipo de operação
    test_vector_search(
        query="notas fiscais de venda para fora do estado",
        top_k=3,
        threshold=0.3
    )
    
    # Teste 2: Busca por produtos
    test_vector_search(
        query="produtos eletrônicos e equipamentos de informática",
        top_k=3,
        threshold=0.3
    )
    
    # Teste 3: Busca por impostos
    test_vector_search(
        query="notas com alto valor de ICMS",
        top_k=3,
        threshold=0.3
    )
    
    # Teste 4: Busca por valor
    test_vector_search(
        query="notas fiscais de alto valor acima de R$ 10.000",
        top_k=3,
        threshold=0.3
    )
    
    print(f"\n{'='*80}")
    print("TESTES CONCLUÍDOS")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
