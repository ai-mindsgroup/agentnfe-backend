"""Exemplos de uso do Agente Especialista em Tributos.

Este script demonstra as funcionalidades do NFeTaxSpecialistAgent:
- Análise tributária completa de notas fiscais
- Validação de CFOP e NCM
- Consultas sobre legislação
- Detecção de anomalias fiscais
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.nfe_tax_specialist_agent import NFeTaxSpecialistAgent
from src.vectorstore.supabase_client import supabase
import json


def print_section(title: str):
    """Imprime título de seção."""
    print(f"\n{'='*80}")
    print(f"{title}")
    print('='*80)


def exemplo_1_analise_nota_completa():
    """Exemplo 1: Análise tributária completa de uma nota fiscal."""
    print("\n")
    print_section("EXEMPLO 1: Análise Tributária Completa")
    
    agent = NFeTaxSpecialistAgent()
    
    # Buscar uma nota fiscal para análise
    print("\n🔍 Buscando nota fiscal para análise...")
    result = supabase.table('nota_fiscal').select('chave_acesso').limit(1).execute()
    
    if not result.data:
        print("❌ Nenhuma nota fiscal encontrada no banco.")
        return
    
    chave_acesso = result.data[0]['chave_acesso']
    print(f"✅ Nota selecionada: {chave_acesso}")
    
    # Analisar nota
    print("\n📊 Executando análise tributária...")
    analise = agent.analyze_nota_fiscal(chave_acesso)
    
    if not analise['success']:
        print(f"❌ Erro: {analise['error']}")
        return
    
    # Exibir resultados
    dados = analise['analise']
    print(f"\n📄 Nota Fiscal #{dados['numero']}")
    print(f"   Data: {dados['data_emissao']}")
    print(f"\n🏢 Emitente:")
    print(f"   CNPJ: {dados['emitente']['cnpj']}")
    print(f"   Razão Social: {dados['emitente']['razao_social']}")
    print(f"   UF: {dados['emitente']['uf']}")
    print(f"\n👤 Destinatário:")
    print(f"   CNPJ: {dados['destinatario']['cnpj']}")
    print(f"   Nome: {dados['destinatario']['nome']}")
    print(f"   UF: {dados['destinatario']['uf']}")
    print(f"\n💰 Valores:")
    print(f"   Valor da Nota: R$ {dados['valores']['valor_nota']:,.2f}")
    print(f"   Soma dos Itens: R$ {dados['valores']['soma_itens']:,.2f}")
    print(f"   Divergência: R$ {dados['valores']['divergencia']:,.2f}")
    
    # Score fiscal
    score = dados['score_fiscal']
    emoji = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
    print(f"\n{emoji} Score Fiscal: {score:.1f}/100")
    
    # Alertas
    if dados['alertas']:
        print(f"\n⚠️ Alertas ({len(dados['alertas'])}):")
        for alerta in dados['alertas']:
            print(f"   • {alerta}")
    else:
        print("\n✅ Nenhum alerta identificado")
    
    # Recomendações
    print(f"\n💡 Recomendações:")
    for rec in dados['recomendacoes']:
        print(f"   • {rec}")
    
    # Validações detalhadas
    print(f"\n📋 Validações:")
    print(f"   CFOP: {len(dados['validacoes']['cfop'])} itens validados")
    print(f"   NCM: {len(dados['validacoes']['ncm'])} itens validados")
    print(f"   Valores: {dados['validacoes']['valores'][0]['status']}")
    
    input("\n\nPressione Enter para continuar...")


def exemplo_2_validar_cfop():
    """Exemplo 2: Validação e explicação de CFOPs."""
    print("\n")
    print_section("EXEMPLO 2: Validação de CFOP")
    
    agent = NFeTaxSpecialistAgent()
    
    # Exemplos de CFOPs para validar
    cfops = ['5102', '6102', '1102', '5949', '6949', '1234', 'XXXX']
    
    print("\n🔍 Validando códigos CFOP...\n")
    
    for cfop in cfops:
        print(f"\nCFOP: {cfop}")
        print("-" * 40)
        
        resultado = agent.validate_cfop(cfop)
        
        if resultado['valido']:
            print(f"✅ Válido")
            print(f"   Natureza: {resultado['natureza']}")
            print(f"   Tipo: {resultado['tipo_operacao']}")
            print(f"   Destino: {resultado['destino']}")
            print(f"   Descrição: {resultado['descricao_grupo']}")
            print(f"   Tributação: {resultado['tributacao']['tipo']}")
        else:
            print(f"❌ Inválido")
            print(f"   Erro: {resultado['erro']}")
    
    input("\n\nPressione Enter para continuar...")


def exemplo_3_validar_ncm():
    """Exemplo 3: Validação e classificação de NCMs."""
    print("\n")
    print_section("EXEMPLO 3: Validação de NCM")
    
    agent = NFeTaxSpecialistAgent()
    
    # Exemplos de NCMs para validar
    ncms = [
        '84145990',  # Ventiladores (máquinas)
        '8414.59.90',  # NCM formatado
        '39269090',  # Outras obras de plásticos
        '12345678',  # NCM genérico
        '123456',    # NCM curto (inválido)
        'ABCD1234',  # NCM com letras (inválido)
    ]
    
    print("\n🔍 Validando códigos NCM...\n")
    
    for ncm in ncms:
        print(f"\nNCM: {ncm}")
        print("-" * 40)
        
        resultado = agent.validate_ncm(ncm)
        
        if resultado['valido']:
            print(f"✅ Válido")
            print(f"   NCM Formatado: {resultado['ncm_formatado']}")
            print(f"   Capítulo: {resultado['capitulo']}")
            print(f"   Categoria: {resultado['categoria']}")
        else:
            print(f"❌ Inválido")
            print(f"   Erro: {resultado['erro']}")
    
    input("\n\nPressione Enter para continuar...")


def exemplo_4_consulta_tributaria():
    """Exemplo 4: Consulta sobre legislação tributária."""
    print("\n")
    print_section("EXEMPLO 4: Consulta Tributária")
    
    agent = NFeTaxSpecialistAgent()
    
    perguntas = [
        "Qual a diferença entre CFOP 5102 e 6102?",
        "Quando devo usar NCM do capítulo 84?",
        "Como calcular o ICMS em operação interestadual?",
    ]
    
    print("\n💬 Fazendo consultas ao especialista...\n")
    
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n{i}. Pergunta: {pergunta}")
        print("-" * 60)
        
        resultado = agent.query_tax_knowledge(pergunta)
        
        if resultado['success']:
            print(f"\n📚 Resposta:")
            print(f"{resultado['resposta']}")
        else:
            print(f"❌ Erro: {resultado['error']}")
        
        if i < len(perguntas):
            input("\nPressione Enter para próxima pergunta...")
    
    input("\n\nPressione Enter para continuar...")


def exemplo_5_detectar_anomalias():
    """Exemplo 5: Detecção de anomalias tributárias."""
    print("\n")
    print_section("EXEMPLO 5: Detecção de Anomalias")
    
    agent = NFeTaxSpecialistAgent()
    
    print("\n🔍 Detectando anomalias tributárias...")
    print("(Este exemplo requer implementação completa das queries SQL)\n")
    
    resultado = agent.detect_anomalies(limit=5)
    
    if resultado['success']:
        total = resultado['total_anomalias']
        print(f"✅ Análise concluída: {total} anomalias detectadas")
        
        if resultado['anomalias']:
            print("\n⚠️ Principais anomalias:")
            for i, anomalia in enumerate(resultado['anomalias'], 1):
                print(f"\n{i}. {anomalia.get('tipo', 'Anomalia')}")
                print(f"   Detalhes: {anomalia}")
        else:
            print("\n✅ Nenhuma anomalia detectada no conjunto analisado")
    else:
        print(f"❌ Erro: {resultado['error']}")
    
    input("\n\nPressione Enter para continuar...")


def exemplo_6_analise_por_uf():
    """Exemplo 6: Análise tributária por UF."""
    print("\n")
    print_section("EXEMPLO 6: Análise por UF")
    
    print("\n📊 Estatísticas de notas por UF...\n")
    
    # Buscar estatísticas de UF
    result = supabase.table('nota_fiscal')\
        .select('uf_emitente, valor_nota_fiscal')\
        .execute()
    
    if result.data:
        from collections import defaultdict
        
        stats_uf = defaultdict(lambda: {'count': 0, 'total_valor': 0})
        
        for nota in result.data:
            uf = nota['uf_emitente']
            valor = float(nota['valor_nota_fiscal'] or 0)
            stats_uf[uf]['count'] += 1
            stats_uf[uf]['total_valor'] += valor
        
        # Ordenar por quantidade
        stats_sorted = sorted(stats_uf.items(), 
                            key=lambda x: x[1]['count'], 
                            reverse=True)
        
        print("Top 10 UFs por quantidade de notas:\n")
        print(f"{'UF':<5} {'Qtd Notas':>12} {'Valor Total':>20} {'Ticket Médio':>20}")
        print("-" * 60)
        
        for uf, dados in stats_sorted[:10]:
            qtd = dados['count']
            total = dados['total_valor']
            media = total / qtd if qtd > 0 else 0
            print(f"{uf:<5} {qtd:>12,} {total:>20,.2f} {media:>20,.2f}")
    else:
        print("❌ Nenhuma nota fiscal encontrada")
    
    input("\n\nPressione Enter para continuar...")


def menu_principal():
    """Menu principal de exemplos."""
    agent = NFeTaxSpecialistAgent()
    
    while True:
        print("\n")
        print_section("EXEMPLOS - Agente Especialista em Tributos")
        
        print("\n1. Análise Tributária Completa de Nota Fiscal")
        print("2. Validar CFOPs")
        print("3. Validar NCMs")
        print("4. Consulta sobre Legislação Tributária")
        print("5. Detectar Anomalias Fiscais")
        print("6. Análise por UF")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            exemplo_1_analise_nota_completa()
        elif opcao == '2':
            exemplo_2_validar_cfop()
        elif opcao == '3':
            exemplo_3_validar_ncm()
        elif opcao == '4':
            exemplo_4_consulta_tributaria()
        elif opcao == '5':
            exemplo_5_detectar_anomalias()
        elif opcao == '6':
            exemplo_6_analise_por_uf()
        elif opcao == '0':
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")
            input("Pressione Enter para continuar...")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
