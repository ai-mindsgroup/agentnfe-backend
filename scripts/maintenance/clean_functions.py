"""Remove todas as funções personalizadas do banco."""
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent
ENV_PATH = ROOT / "configs" / ".env"
load_dotenv(ENV_PATH)

import psycopg
from src.settings import build_db_dsn

def main():
    print("🗑️  Removendo funções personalizadas...")
    
    dsn = build_db_dsn()
    
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Listar funções
            cur.execute("""
                SELECT routine_name, routine_type
                FROM information_schema.routines
                WHERE routine_schema = 'public'
                ORDER BY routine_name;
            """)
            
            functions = cur.fetchall()
            
            if not functions:
                print("   ℹ️  Nenhuma função encontrada")
                return 0
            
            print(f"   Encontradas {len(functions)} funções:")
            for func_name, func_type in functions:
                print(f"      - {func_name} ({func_type})")
            
            # Dropar função match_embeddings especificamente
            try:
                cur.execute("DROP FUNCTION IF EXISTS match_embeddings CASCADE")
                print("   ✅ Função 'match_embeddings' removida")
            except Exception as e:
                print(f"   ⚠️  Erro: {e}")
            
            conn.commit()
            print("\n✅ Funções removidas com sucesso")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
