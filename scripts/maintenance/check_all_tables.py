"""Verifica todas as tabelas existentes no banco de dados."""
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
    print("VERIFICANDO TABELAS NO BANCO DE DADOS")
    print("=" * 70)
    
    dsn = build_db_dsn()
    
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # Listar todas as tabelas no schema public
            cur.execute("""
                SELECT table_name, 
                       pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            tables = cur.fetchall()
            
            if not tables:
                print("\n❌ Nenhuma tabela encontrada no schema 'public'")
                return
            
            print(f"\n✅ Encontradas {len(tables)} tabelas:\n")
            print(f"{'Tabela':<40} {'Tamanho':<15}")
            print("-" * 70)
            
            nfe_tables = []
            for table_name, size in tables:
                print(f"{table_name:<40} {size:<15}")
                if 'nfe' in table_name.lower() or 'nota' in table_name.lower() or 'fiscal' in table_name.lower():
                    nfe_tables.append(table_name)
            
            # Verificar contagem de registros nas tabelas relacionadas a NFe
            if nfe_tables:
                print("\n" + "=" * 70)
                print("TABELAS DE NOTAS FISCAIS ENCONTRADAS:")
                print("=" * 70)
                
                for table in nfe_tables:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cur.fetchone()[0]
                        
                        # Pegar algumas colunas
                        cur.execute(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' 
                            ORDER BY ordinal_position 
                            LIMIT 5
                        """)
                        columns = [row[0] for row in cur.fetchall()]
                        
                        print(f"\n📋 Tabela: {table}")
                        print(f"   Registros: {count:,}")
                        print(f"   Primeiras colunas: {', '.join(columns)}")
                        
                    except Exception as e:
                        print(f"\n⚠️  Erro ao acessar {table}: {e}")
            else:
                print("\n⚠️  Nenhuma tabela de Notas Fiscais encontrada")
                print("   (Procurando por nomes com: 'nfe', 'nota', 'fiscal')")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
