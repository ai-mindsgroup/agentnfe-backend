"""Teste direto do Gemini usando google-generativeai."""
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

# Testa com biblioteca oficial do Google
try:
    import google.generativeai as genai
    
    print("\n🧠 Configurando Gemini com biblioteca oficial...")
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Lista modelos disponíveis
    print("\n📋 Listando modelos disponíveis:")
    print("-" * 50)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  • {m.name}")
    print("-" * 50)
    
    # Usa o modelo correto (Gemini 2.5 Flash - mais recente)
    print("\n🧠 Inicializando Gemini 2.5 Flash...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("✅ Gemini 2.5 Flash inicializado com sucesso!")
    
    # Testa uma mensagem simples
    print("\n💬 Testando resposta para: 'Oi'")
    print("-" * 50)
    
    response = model.generate_content("Oi")
    
    print("\n🤖 Resposta do Gemini:")
    print(response.text)
    print("-" * 50)
    
    # Testa uma pergunta mais específica
    print("\n💬 Testando: 'Qual é a capital do Brasil?'")
    print("-" * 50)
    
    response2 = model.generate_content("Qual é a capital do Brasil?")
    
    print("\n🤖 Resposta do Gemini:")
    print(response2.text)
    print("-" * 50)
    
    # Testa pergunta sobre análise de dados
    print("\n💬 Testando: 'Como você pode ajudar na análise de dados CSV?'")
    print("-" * 50)
    
    response3 = model.generate_content("Como você pode ajudar na análise de dados CSV?")
    
    print("\n🤖 Resposta do Gemini:")
    print(response3.text)
    print("-" * 50)
    
    print("\n✅ Gemini está funcionando perfeitamente!")
    
except ImportError as e:
    print(f"❌ Erro ao importar google-generativeai: {e}")
    print("\nInstale com: pip install google-generativeai")
except Exception as e:
    print(f"❌ Erro ao testar Gemini: {e}")
    import traceback
    traceback.print_exc()
