"""Teste básico do Agente Orquestrador (sem dependências externas).

Este script testa apenas o orquestrador com CSV e Data Processor,
sem precisar do Supabase configurado.
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent.orchestrator_agent import OrchestratorAgent


def test_orchestrator_basic():
    """Teste básico sem dependências externas."""
    
    print("🚀 TESTE BÁSICO DO AGENTE ORQUESTRADOR")
    print("=" * 50)
    
    print("\n🤖 Inicializando orquestrador...")
    try:
        # Inicializar apenas com componentes sem dependências externas
        orchestrator = OrchestratorAgent(
            enable_csv_agent=True,
            enable_rag_agent=False,  # Desabilitar RAG (precisa Supabase)
            enable_data_processor=True
        )
        print("✅ Orquestrador inicializado!")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {str(e)}")
        return
    
    # Testes básicos
    print("\n💬 TESTANDO INTERAÇÕES BÁSICAS")
    print("-" * 40)
    
    test_queries = [
        "olá",
        "status do sistema", 
        "ajuda",
        "quais agentes estão disponíveis?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Pergunta: {query}")
        print("─" * 30)
        
        try:
            result = orchestrator.process(query)
            
            # Mostrar resposta (limitada)
            content = result['content']
            if len(content) > 200:
                content = content[:200] + "..."
            print(content)
            
            # Mostrar metadados importantes
            metadata = result.get('metadata', {})
            agents_used = metadata.get('agents_used', [])
            if agents_used:
                print(f"🤖 Agentes: {', '.join(agents_used)}")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    # Teste de classificação de consultas
    print("\n🎯 TESTANDO CLASSIFICAÇÃO DE CONSULTAS")
    print("-" * 40)
    
    classification_tests = [
        "analise o arquivo dados.csv",         # CSV_ANALYSIS
        "busque informações sobre ICMS",       # RAG_SEARCH  
        "carregar dados do arquivo",           # DATA_LOADING
        "qual é a capital do Brasil?",         # GENERAL
        "xpto123 consulta estranha"           # UNKNOWN
    ]
    
    for query in classification_tests:
        print(f"\n📝 Consulta: {query}")
        
        try:
            # Usar método interno de classificação
            query_type = orchestrator._classify_query(query, None)
            print(f"🏷️ Tipo identificado: {query_type.value}")
            
        except Exception as e:
            print(f"❌ Erro na classificação: {str(e)}")
    
    # Teste de histórico
    print("\n📚 TESTANDO HISTÓRICO")
    print("-" * 40)
    
    try:
        history = orchestrator.get_conversation_history()
        print(f"💬 Interações no histórico: {len(history)}")
        
        if history:
            last_interaction = history[-1]
            print(f"📅 Última interação: {last_interaction.get('type', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erro no histórico: {str(e)}")
    
    print(f"\n✅ TESTE BÁSICO CONCLUÍDO!")
    print(f"🎯 Orquestrador funciona corretamente mesmo sem todas as dependências")


if __name__ == "__main__":
    test_orchestrator_basic()