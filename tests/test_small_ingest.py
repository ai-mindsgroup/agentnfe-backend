#!/usr/bin/env python3
"""
Teste rápido: Ingestão das primeiras 500 linhas para validar correção
"""
import sys
import pandas as pd
sys.path.append('src')

from src.agent.rag_agent import RAGAgent

def test_small_ingest():
    print("🧪 Teste rápido: Ingestão de dados de teste")
    
    # Criar dataset de teste com dados limitados
    print("📁 Lendo arquivo de demonstração...")
    df_full = pd.read_csv("data/demo_transacoes.csv")
    
    # Pegar apenas as primeiras linhas (se o arquivo for grande)
    max_rows = min(500, len(df_full))
    df_test = df_full.head(max_rows)
    
    # Salvar arquivo de teste
    test_file = "data/demo_test_limited.csv"
    df_test.to_csv(test_file, index=False)
    print(f"✅ Arquivo de teste criado: {test_file} ({len(df_test)} linhas)")
    
    # Executar ingestão
    print("\n🚀 Iniciando ingestão de teste...")
    agent = RAGAgent()
    
    result = agent.ingest_csv_file(
        file_path=test_file,
        source_id="demo_test_limited"
    )
    
    print(f"\n📊 Resultado: {result.get('response', 'Sem resposta')}")
    
    return result

if __name__ == "__main__":
    test_small_ingest()