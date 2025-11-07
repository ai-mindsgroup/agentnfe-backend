"""Script de teste rápido para API NFe Endpoints.

Testa todos os endpoints da API NFe Tax Specialist via HTTP.
"""
import requests
import json
from datetime import datetime

# Configuração
API_BASE_URL = "http://localhost:8000"
NFE_BASE_URL = f"{API_BASE_URL}/nfe"


def print_section(title: str):
    """Imprime título de seção."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_health_check():
    """Testa health check da API NFe."""
    print_section("TESTE 1: Health Check NFe")
    
    try:
        response = requests.get(f"{NFE_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Serviço: {data.get('service')}")
            print(f"✅ Agente disponível: {data.get('agent_available')}")
            print(f"✅ Banco conectado: {data.get('database_connected')}")
            print(f"✅ Features: {json.dumps(data.get('features', {}), indent=2)}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")


def test_validate_cfop():
    """Testa validação de CFOP."""
    print_section("TESTE 2: Validação de CFOP")
    
    cfops_test = ["5102", "6102", "1102", "9999"]
    
    for cfop in cfops_test:
        try:
            payload = {"cfop": cfop}
            response = requests.post(f"{NFE_BASE_URL}/validate/cfop", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nCFOP {cfop}:")
                print(f"  ✅ Válido: {data.get('valido')}")
                print(f"  ✅ Natureza: {data.get('natureza', 'N/A')}")
                print(f"  ✅ Destino: {data.get('destino', 'N/A')}")
            else:
                print(f"❌ Erro ao validar {cfop}: {response.text}")
        except Exception as e:
            print(f"❌ Erro: {e}")


def test_validate_ncm():
    """Testa validação de NCM."""
    print_section("TESTE 3: Validação de NCM")
    
    ncms_test = ["84714100", "02071400", "99999999"]
    
    for ncm in ncms_test:
        try:
            payload = {"ncm": ncm}
            response = requests.post(f"{NFE_BASE_URL}/validate/ncm", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nNCM {ncm}:")
                print(f"  ✅ Válido: {data.get('valido')}")
                print(f"  ✅ Capítulo: {data.get('capitulo', 'N/A')}")
                print(f"  ✅ Categoria: {data.get('categoria', 'N/A')}")
            else:
                print(f"❌ Erro ao validar {ncm}: {response.text}")
        except Exception as e:
            print(f"❌ Erro: {e}")


def test_analyze_nota():
    """Testa análise de nota fiscal."""
    print_section("TESTE 4: Análise de Nota Fiscal")
    
    # Usar uma chave de acesso de exemplo
    chave_acesso = "33250517579278000168550000000103531030943310"
    
    try:
        payload = {"chave_acesso": chave_acesso}
        response = requests.post(f"{NFE_BASE_URL}/analyze", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                analise = data.get('analise', {})
                print(f"✅ Nota: {analise.get('numero')}")
                print(f"✅ Emitente: {analise.get('emitente', {}).get('razao_social')}")
                print(f"✅ Valor: R$ {analise.get('valores', {}).get('valor_nota', 0):.2f}")
                print(f"✅ Score Fiscal: {analise.get('score_fiscal', 0):.1f}/100")
                print(f"✅ Alertas: {len(analise.get('alertas', []))}")
            else:
                print(f"❌ Erro: {data.get('error')}")
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_detect_anomalies():
    """Testa detecção de anomalias."""
    print_section("TESTE 5: Detecção de Anomalias")
    
    try:
        payload = {
            "uf_emitente": "SP",
            "limit": 5
        }
        response = requests.post(f"{NFE_BASE_URL}/anomalies", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total anomalias: {data.get('total_anomalias', 0)}")
            print(f"✅ Anomalias detectadas: {len(data.get('anomalias', []))}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_list_notas():
    """Testa listagem de notas."""
    print_section("TESTE 6: Listagem de Notas")
    
    try:
        params = {
            "limit": 5,
            "offset": 0
        }
        response = requests.get(f"{NFE_BASE_URL}/list", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total: {data.get('total', 0)}")
            print(f"✅ Notas retornadas: {len(data.get('notas', []))}")
            
            for i, nota in enumerate(data.get('notas', [])[:3], 1):
                print(f"\n  Nota {i}:")
                print(f"    Número: {nota.get('numero')}")
                print(f"    Emitente: {nota.get('razao_social_emitente')}")
                print(f"    Valor: R$ {nota.get('valor_nota_fiscal', 0):.2f}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")


def test_api_health():
    """Testa health check geral da API."""
    print_section("TESTE 0: Health Check Geral")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Agentes disponíveis: {', '.join(data.get('agents_available', []))}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n⚠️  A API não está rodando!")
        print("   Execute: python api_completa.py")
        return False
    
    return True


def main():
    """Executa todos os testes."""
    print("\n")
    print("=" * 80)
    print("         TESTE DA API NFE TAX SPECIALIST")
    print("=" * 80)
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Testar se API está rodando
    if not test_api_health():
        return 1
    
    # Executar testes
    test_health_check()
    test_validate_cfop()
    test_validate_ncm()
    test_analyze_nota()
    test_detect_anomalies()
    test_list_notas()
    
    print_section("✅ TODOS OS TESTES CONCLUÍDOS")
    print("Verifique os resultados acima para identificar eventuais problemas.\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
