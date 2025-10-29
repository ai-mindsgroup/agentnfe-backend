"""Teste rápido do Gemini para responder 'Oi' de um usuário."""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.settings import GOOGLE_API_KEY

if not GOOGLE_API_KEY:
    print("❌ GOOGLE_API_KEY não está configurada!")
    sys.exit(1)

print(f"✅ GOOGLE_API_KEY configurada: {GOOGLE_API_KEY[:20]}...")

# Testa com LangChain
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    print("\n🧠 Inicializando Gemini via LangChain...")
    # Modelo atualizado - gemini-pro foi descontinuado
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # ou gemini-1.5-pro para respostas mais elaboradas
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )
    
    print("✅ Gemini 1.5 Flash inicializado com sucesso!")
    
    # Testa uma mensagem simples
    print("\n💬 Testando resposta para: 'Oi'")
    print("-" * 50)
    
    response = llm.invoke("Oi")
    
    print("\n🤖 Resposta do Gemini:")
    print(response.content)
    print("-" * 50)
    
    # Testa uma pergunta mais específica
    print("\n💬 Testando: 'Qual é a capital do Brasil?'")
    print("-" * 50)
    
    response2 = llm.invoke("Qual é a capital do Brasil?")
    
    print("\n🤖 Resposta do Gemini:")
    print(response2.content)
    print("-" * 50)
    
    print("\n✅ Gemini está funcionando perfeitamente!")
    
except ImportError as e:
    print(f"❌ Erro ao importar LangChain Google GenAI: {e}")
    print("\nInstale com: pip install langchain-google-genai")
except Exception as e:
    print(f"❌ Erro ao testar Gemini: {e}")
    import traceback
    traceback.print_exc()
