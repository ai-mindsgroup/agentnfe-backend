"""Script de Teste para NFeTaxSpecialistAgent.

Testa todas as funcionalidades do agente especialista em análise tributária de NF-e:
- Validação de CFOP
- Validação de NCM
- Análise de nota fiscal específica
- Detecção de anomalias
- Consultas sobre legislação tributária
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.nfe_tax_specialist_agent import NFeTaxSpecialistAgent
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def print_section(title: str):
    """Imprime título de seção."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_cfop_validation():
    """Testa validação de códigos CFOP."""
    print_section("TESTE 1: Validação de CFOP")
    
    agent = NFeTaxSpecialistAgent()
    
    # Casos de teste
    cfops_test = [
        ("5102", "Venda de mercadoria adquirida ou recebida de terceiros"),
        ("6102", "Venda de mercadoria para outro estado"),
        ("1102", "Compra para comercialização"),
        ("5405", "Venda de mercadoria para depósito fechado"),
        ("9999", "CFOP inválido"),
        ("123", "CFOP com tamanho incorreto"),
    ]
    
    for cfop, descricao_esperada in cfops_test:
        print(f"Testando CFOP: {cfop} ({descricao_esperada})")
        resultado = agent.validate_cfop(cfop)
        
        print(f"  ✓ Válido: {resultado.get('valido', False)}")
        print(f"  ✓ Natureza: {resultado.get('natureza', 'N/A')}")
        print(f"  ✓ Descrição: {resultado.get('descricao', resultado.get('erro', 'N/A'))}")
        print()


def test_ncm_validation():
    """Testa validação de códigos NCM."""
    print_section("TESTE 2: Validação de NCM")
    
    agent = NFeTaxSpecialistAgent()
    
    # Casos de teste
    ncms_test = [
        ("84714100", "Máquinas automáticas para processamento de dados"),
        ("02071400", "Pedaços e miudezas, comestíveis de galos/galinhas"),
        ("22030000", "Cerveja de malte"),
        ("87032310", "Automóveis com motor a gasolina"),
        ("999999", "NCM com formato incorreto"),
        ("12345", "NCM com tamanho incorreto"),
    ]
    
    for ncm, descricao_esperada in ncms_test:
        print(f"Testando NCM: {ncm} ({descricao_esperada})")
        resultado = agent.validate_ncm(ncm)
        
        print(f"  ✓ Válido: {resultado.get('valido', False)}")
        print(f"  ✓ Capítulo: {resultado.get('capitulo', 'N/A')}")
        print(f"  ✓ Categoria: {resultado.get('categoria', resultado.get('erro', 'N/A'))}")
        print()


def test_nota_fiscal_analysis():
    """Testa análise de nota fiscal específica."""
    print_section("TESTE 3: Análise de Nota Fiscal")
    
    agent = NFeTaxSpecialistAgent()
    
    # Buscar uma chave de acesso real do banco
    print("Buscando nota fiscal de exemplo no banco...")
    
    try:
        from src.vectorstore.supabase_client import supabase
        
        response = supabase.table('nota_fiscal').select('chave_acesso').limit(1).execute()
        
        if response.data and len(response.data) > 0:
            chave_acesso = response.data[0]['chave_acesso']
            print(f"Nota encontrada: {chave_acesso}")
            print()
            
            # Analisar nota
            resultado = agent.analyze_nota_fiscal(chave_acesso)
            
            if resultado.get('success'):
                analise = resultado['analise']
                
                print("📄 INFORMAÇÕES DA NOTA:")
                print(f"  Número: {analise.get('numero')}")
                print(f"  Data Emissão: {analise.get('data_emissao')}")
                print(f"  Emitente: {analise.get('emitente', {}).get('razao_social')}")
                print(f"  UF: {analise.get('emitente', {}).get('uf')}")
                print()
                
                print("💰 VALORES:")
                valores = analise.get('valores', {})
                print(f"  Valor NF-e: R$ {valores.get('valor_nota', 0):.2f}")
                print(f"  Soma Itens: R$ {valores.get('soma_itens', 0):.2f}")
                print(f"  Divergência: R$ {valores.get('divergencia', 0):.2f}")
                print()
                
                print("✅ VALIDAÇÕES:")
                validacoes = analise.get('validacoes', {})
                print(f"  CFOP: {len(validacoes.get('cfop', []))} validações")
                print(f"  NCM: {len(validacoes.get('ncm', []))} validações")
                print(f"  Valores: {len(validacoes.get('valores', []))} validações")
                print()
                
                print("⚠️  ALERTAS:")
                alertas = analise.get('alertas', [])
                if alertas:
                    for alerta in alertas:
                        print(f"  • {alerta}")
                else:
                    print("  Nenhum alerta encontrado")
                print()
                
                print(f"📊 SCORE FISCAL: {analise.get('score_fiscal', 100):.1f}/100")
                print()
                
                print("💡 RECOMENDAÇÕES:")
                recomendacoes = analise.get('recomendacoes', [])
                if recomendacoes:
                    for rec in recomendacoes:
                        print(f"  • {rec}")
                else:
                    print("  Nenhuma recomendação")
                
            else:
                print(f"❌ Erro na análise: {resultado.get('error')}")
        else:
            print("⚠️  Nenhuma nota fiscal encontrada no banco de dados")
            print("   Execute primeiro a ingestão de dados NFe")
            
    except Exception as e:
        print(f"❌ Erro ao buscar nota: {str(e)}")


def test_anomaly_detection():
    """Testa detecção de anomalias tributárias."""
    print_section("TESTE 4: Detecção de Anomalias")
    
    agent = NFeTaxSpecialistAgent()
    
    print("Buscando anomalias tributárias...")
    print()
    
    resultado = agent.detect_anomalies(
        uf_emitente='SP',
        limit=5
    )
    
    if resultado.get('success'):
        anomalias = resultado.get('anomalias', [])
        
        print(f"🔍 Encontradas {len(anomalias)} anomalias potenciais:")
        print()
        
        for i, anomalia in enumerate(anomalias, 1):
            print(f"{i}. Nota: {anomalia.get('chave_acesso', 'N/A')[:20]}...")
            print(f"   Tipo: {anomalia.get('tipo', 'N/A')}")
            print(f"   Severidade: {anomalia.get('severidade', 'N/A')}")
            print(f"   Descrição: {anomalia.get('descricao', 'N/A')}")
            print()
    else:
        print(f"❌ Erro: {resultado.get('error')}")


def test_tax_knowledge_query():
    """Testa consultas sobre conhecimento tributário."""
    print_section("TESTE 5: Consultas sobre Legislação Tributária")
    
    agent = NFeTaxSpecialistAgent()
    
    perguntas = [
        "O que é CFOP e qual sua importância?",
        "Quando devo usar CFOP 5102?",
        "Qual a diferença entre operações internas e interestaduais?",
        "O que significa NCM?",
    ]
    
    for pergunta in perguntas:
        print(f"❓ Pergunta: {pergunta}")
        
        resultado = agent.query_tax_knowledge(pergunta)
        
        if resultado.get('success'):
            print(f"💡 Resposta: {resultado.get('resposta', 'N/A')[:300]}...")
        else:
            print(f"❌ Erro: {resultado.get('error')}")
        print()


def test_rag_search():
    """Testa busca vetorial (RAG) em notas fiscais."""
    print_section("TESTE 6: Busca Vetorial (RAG)")
    
    agent = NFeTaxSpecialistAgent()
    
    print("🔎 Testando busca de notas similares...")
    print()
    
    try:
        from src.vectorstore.supabase_client import supabase
        
        # Buscar uma chave de acesso para usar como referência
        response = supabase.table('nota_fiscal').select('chave_acesso').limit(1).execute()
        
        if response.data and len(response.data) > 0:
            chave_referencia = response.data[0]['chave_acesso']
            print(f"Usando nota de referência: {chave_referencia[:20]}...")
            
            resultado = agent.find_similar_notas(chave_referencia, limit=3)
            
            if resultado.get('success'):
                similares = resultado.get('similares', [])
                print(f"✓ Encontradas {len(similares)} notas similares")
                
                for i, nota in enumerate(similares, 1):
                    print(f"   {i}. Chave: {nota.get('chave_acesso', 'N/A')[:20]}...")
                    print(f"      Valor: R$ {nota.get('valor_nota_fiscal', 0):.2f}")
            else:
                print(f"   ❌ Erro: {resultado.get('error')}")
        else:
            print("⚠️  Nenhuma nota fiscal disponível para teste de similaridade")
            
    except Exception as e:
        print(f"❌ Erro ao testar RAG: {str(e)}")
    
    print()


def test_process_method():
    """Testa o método process() com diferentes tipos de query."""
    print_section("TESTE 7: Método Process (Interface Geral)")
    
    agent = NFeTaxSpecialistAgent()
    
    # Teste 1: Validação de CFOP via process
    print("1. Validação de CFOP via process:")
    resultado = agent.process("validar cfop", context={'cfop': '5102'})
    print(f"   Resultado: {resultado.get('valido', False)}")
    print(f"   Natureza: {resultado.get('natureza', 'N/A')}")
    print()
    
    # Teste 2: Validação de NCM via process
    print("2. Validação de NCM via process:")
    resultado = agent.process("validar ncm", context={'ncm': '84714100'})
    print(f"   Resultado: {resultado.get('valido', False)}")
    print(f"   Capítulo: {resultado.get('capitulo', 'N/A')}")
    print()
    
    # Teste 3: Consulta geral
    print("3. Consulta sobre tributos:")
    resultado = agent.process("Explique o que é substituição tributária")
    if resultado.get('success'):
        print(f"   Resposta: {resultado.get('resposta', 'N/A')[:200]}...")
    print()


def main():
    """Executa todos os testes."""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "TESTE DO AGENTE NFE TAX SPECIALIST")
    print("=" * 80)
    
    try:
        # Executar testes
        test_cfop_validation()
        test_ncm_validation()
        test_nota_fiscal_analysis()
        test_anomaly_detection()
        test_tax_knowledge_query()
        test_rag_search()
        test_process_method()
        
        print_section("✅ TODOS OS TESTES CONCLUÍDOS")
        print("Verifique os resultados acima para identificar eventuais problemas.")
        
    except Exception as e:
        print_section("❌ ERRO DURANTE EXECUÇÃO DOS TESTES")
        print(f"Erro: {str(e)}")
        logger.exception("Erro durante testes do agente NFe")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
