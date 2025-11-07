"""Script para testar conexão com Supabase."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env
env_path = Path(__file__).parent / "configs" / ".env"
load_dotenv(env_path)

print("=" * 60)
print("TESTE DE CONEXÃO COM BANCO DE DADOS")
print("=" * 60)

# Verificar variáveis de ambiente
print("\n1. Verificando variáveis de ambiente:")
print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NÃO ENCONTRADA')[:50]}...")
print(f"   SUPABASE_KEY: {'✅ CONFIGURADA' if os.getenv('SUPABASE_KEY') else '❌ NÃO ENCONTRADA'}")
print(f"   DB_HOST: {os.getenv('DB_HOST', 'NÃO ENCONTRADO')}")
print(f"   DB_PASSWORD: {'✅ CONFIGURADA' if os.getenv('DB_PASSWORD') else '❌ NÃO ENCONTRADA'}")

# Teste 1: Conexão Supabase Client
print("\n2. Testando Supabase Client (API):")
try:
    from supabase import create_client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("   ❌ Credenciais Supabase não configuradas")
    else:
        supabase = create_client(supabase_url, supabase_key)
        # Testar query simples
        result = supabase.table('embeddings').select("id").limit(1).execute()
        print(f"   ✅ Conexão Supabase Client OK (encontradas {len(result.data)} registros)")
except Exception as e:
    print(f"   ❌ Erro Supabase Client: {str(e)[:100]}")

# Teste 2: Conexão PostgreSQL direta
print("\n3. Testando PostgreSQL direto:")
try:
    import psycopg
    
    db_host = os.getenv("DB_HOST")
    db_password = os.getenv("DB_PASSWORD")
    db_user = os.getenv("DB_USER", "postgres")
    db_name = os.getenv("DB_NAME", "postgres")
    db_port = os.getenv("DB_PORT", "5432")
    
    if not db_host or not db_password:
        print("   ❌ Credenciais PostgreSQL não configuradas")
    else:
        dsn = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_password}"
        
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT version()')
                version = cur.fetchone()[0]
                print(f"   ✅ Conexão PostgreSQL OK")
                print(f"   📊 Versão: {version[:80]}...")
                
                # Verificar extensão pgvector
                cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
                vector_ext = cur.fetchone()
                if vector_ext:
                    print(f"   ✅ Extensão pgvector instalada (versão {vector_ext[1]})")
                else:
                    print(f"   ⚠️  Extensão pgvector não encontrada")
                
                # Contar embeddings
                cur.execute("SELECT COUNT(*) FROM embeddings")
                count = cur.fetchone()[0]
                print(f"   📊 Total de embeddings: {count}")
                
except Exception as e:
    print(f"   ❌ Erro PostgreSQL: {str(e)[:100]}")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
