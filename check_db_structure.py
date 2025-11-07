"""Verifica estrutura do banco vetorial"""
from src.vectorstore.supabase_client import supabase

tables = [
    'embeddings',
    'chunks', 
    'metadata',
    'nota_fiscal',
    'nota_fiscal_item',
    'conversation_history'
]

print("=" * 60)
print("ESTRUTURA DO BANCO VETORIAL")
print("=" * 60)

for table in tables:
    try:
        result = supabase.table(table).select('*', count='exact').limit(1).execute()
        print(f"✅ {table:30} {result.count:>10} registros")
    except Exception as e:
        print(f"❌ {table:30} ERRO: {str(e)[:30]}")

print("=" * 60)
