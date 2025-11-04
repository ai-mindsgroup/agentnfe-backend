"""Executa migrations usando Supabase Client (contorna problema de autenticação PostgreSQL).

Uso:
    python run_migrations_supabase.py
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# Carregar .env
ROOT = Path(__file__).parent
ENV_PATH = ROOT / "configs" / ".env"
load_dotenv(ENV_PATH)

from supabase import create_client

MIGRATIONS_DIR = ROOT / "migrations"

def main():
    print("=" * 60)
    print("EXECUTANDO MIGRATIONS VIA SUPABASE CLIENT")
    print("=" * 60)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ ERRO: Credenciais Supabase não configuradas no .env")
        return 1
    
    print(f"\n📡 Conectando ao Supabase: {supabase_url[:50]}...")
    supabase = create_client(supabase_url, supabase_key)
    
    # Listar migrations
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        print("❌ Nenhum arquivo .sql encontrado em migrations/")
        return 1
    
    print(f"\n📋 Encontradas {len(files)} migrations:")
    for fp in files:
        print(f"   - {fp.name}")
    
    print("\n⚠️  ATENÇÃO: Supabase Client não executa SQL direto por questões de segurança.")
    print("Para executar migrations, você tem 3 opções:")
    print()
    print("OPÇÃO 1 - Supabase Dashboard (SQL Editor):")
    print("   1. Acesse: https://supabase.com/dashboard/project/ncefmfiulpwssaajybtl/editor")
    print("   2. Vá em SQL Editor")
    print("   3. Cole e execute cada migration na ordem:")
    
    for fp in files:
        print(f"      - {fp.name}")
    
    print()
    print("OPÇÃO 2 - Usar psql (linha de comando):")
    print("   Instale PostgreSQL client e execute:")
    print("   psql \"postgresql://postgres:[senha]@aws-1-sa-east-1.pooler.supabase.com:6543/postgres\" < migrations/0000_enable_pgcrypto.sql")
    
    print()
    print("OPÇÃO 3 - Corrigir autenticação PostgreSQL:")
    print("   1. Verifique a senha em DB_PASSWORD no .env")
    print("   2. Use a senha do modo 'Transaction' do Connection Pooler")
    print("   3. Execute: python scripts/run_migrations.py")
    
    print()
    print("=" * 60)
    print("Para facilitar, vou mostrar o conteúdo das migrations principais:")
    print("=" * 60)
    
    # Mostrar migrations essenciais
    essential = ["0000_enable_pgcrypto.sql", "0001_init_pgvector.sql", "0002_schema.sql"]
    
    for name in essential:
        fp = MIGRATIONS_DIR / name
        if fp.exists():
            print(f"\n📄 {name}:")
            print("-" * 60)
            content = fp.read_text(encoding="utf-8")
            print(content[:500] + ("..." if len(content) > 500 else ""))
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
