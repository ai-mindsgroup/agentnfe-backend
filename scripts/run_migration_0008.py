"""Script para executar a migration 0008."""
import sys
from pathlib import Path

# Adiciona src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import psycopg
from src.settings import build_db_dsn

def run_migration():
    """Executa a migration 0008."""
    dsn = build_db_dsn()
    migration_file = Path(__file__).parent.parent / 'migrations' / '0008_update_embedding_768d_gemini.sql'
    
    print(f"Conectando ao banco...")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            print(f"Executando migration: {migration_file.name}")
            sql = migration_file.read_text(encoding='utf-8')
            cur.execute(sql)
            conn.commit()
            print("✓ Migration executada com sucesso!")

if __name__ == '__main__':
    run_migration()
