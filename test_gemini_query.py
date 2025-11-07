"""Teste rápido de query fiscal com Gemini"""
from src.agent.nfe_tax_specialist_agent import NFeTaxSpecialistAgent

print("Inicializando agente NFe...")
agent = NFeTaxSpecialistAgent()

print("\nTestando consulta fiscal: 'O que é CFOP?'\n")
result = agent.query_tax_knowledge('O que é CFOP?')

if result.get('success'):
    print("OK! Sucesso!")
    print(f"Provider: {result.get('llm_provider', 'N/A')}")
    print(f"Model: {result.get('model', 'N/A')}")
    print(f"\nResposta:\n{result.get('resposta', 'N/A')}")
else:
    print(f"ERRO: {result.get('error', 'N/A')}")
