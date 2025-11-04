"""Script para limpar completamente o banco de dados (DROP ALL TABLES).

⚠️  ATENÇÃO: Este script irá DELETAR TODAS as tabelas e dados!
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# Carregar .env
ROOT = Path(__file__).parent
ENV_PATH = ROOT / "configs" / ".env"
load_dotenv(ENV_PATH)

import psycopg
from src.settings import build_db_dsn

def main():
    print("=" * 70)
    print("⚠️  LIMPEZA COMPLETA DO BANCO DE DADOS")
    print("=" * 70)
    print()
    print("Este script irá:")
    print("  ❌ DELETAR todas as tabelas")
    print("  ❌ DELETAR todos os dados")
    print("  ❌ REMOVER todas as extensões")
    print()
    
    resposta = input("Tem CERTEZA que deseja continuar? Digite 'SIM' para confirmar: ")
    
    if resposta.strip().upper() != "SIM":
        print("\n✅ Operação cancelada. Nenhuma alteração foi feita.")
        return 0
    
    print("\n🔄 Conectando ao banco de dados...")
    dsn = build_db_dsn()
    
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Listar todas as tabelas
            print("\n📋 Listando tabelas existentes...")
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            
            if not tables:
                print("   ℹ️  Nenhuma tabela encontrada")
            else:
                print(f"   Encontradas {len(tables)} tabelas:")
                for table in tables:
                    print(f"      - {table}")
            
            # Dropar todas as tabelas em cascata
            if tables:
                print(f"\n🗑️  Deletando {len(tables)} tabelas...")
                for table in tables:
                    try:
                        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                        print(f"   ✅ Tabela '{table}' deletada")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao deletar '{table}': {e}")
                
                conn.commit()
            
            # Listar e remover extensões (exceto as do sistema)
            print("\n📋 Listando extensões...")
            cur.execute("""
                SELECT extname, extversion
                FROM pg_extension
                WHERE extname NOT IN ('plpgsql')
                ORDER BY extname;
            """)
            
            extensions = cur.fetchall()
            
            if extensions:
                print(f"   Encontradas {len(extensions)} extensões:")
                for extname, extversion in extensions:
                    print(f"      - {extname} (v{extversion})")
                
                print("\n🗑️  Removendo extensões...")
                for extname, _ in extensions:
                    try:
                        cur.execute(f"DROP EXTENSION IF EXISTS {extname} CASCADE")
                        print(f"   ✅ Extensão '{extname}' removida")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao remover '{extname}': {e}")
                
                conn.commit()
            
            # Verificar resultado final
            print("\n🔍 Verificando limpeza...")
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE';
            """)
            
            remaining = cur.fetchone()[0]
            
            if remaining == 0:
                print("   ✅ Banco de dados completamente limpo!")
                print("\n" + "=" * 70)
                print("✅ LIMPEZA CONCLUÍDA COM SUCESSO")
                print("=" * 70)
                print("\nPróximos passos:")
                print("  1. Execute as migrations:")
                print("     python scripts/run_migrations.py")
                print()
                print("  2. Teste a conexão:")
                print("     python test_db_connection.py")
            else:
                print(f"   ⚠️  Ainda existem {remaining} tabelas no banco")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
