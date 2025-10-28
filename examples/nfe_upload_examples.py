"""
Script de exemplo para upload de arquivos NF-e
Demonstra todas as formas de uso do sistema
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para imports funcionarem
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.data.nfe_uploader import NFeUploader, upload_nfe_files
from src.vectorstore.supabase_client import supabase
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def exemplo_1_upload_automatico():
    """
    Exemplo 1: Upload automático (detecta tipo de arquivo)
    Recomendado para uso geral
    """
    print("\n" + "="*80)
    print("EXEMPLO 1: Upload Automático")
    print("="*80)
    
    uploader = NFeUploader()
    
    # Faz upload de um arquivo (detecta automaticamente se é NotaFiscal ou NotaFiscalItem)
    result = uploader.upload_auto(
        file_path="data/202505_NFe_NotaFiscal.csv",
        uploaded_by="usuario@exemplo.com"
    )
    
    print(f"\n✅ Upload concluído!")
    print(f"   Arquivo: {result['filename']}")
    print(f"   Tipo: {result['file_type']}")
    print(f"   Linhas inseridas: {result['rows_inserted']}/{result['total_rows']}")
    print(f"   Sucesso: {'Sim' if result['success'] else 'Não'}")


def exemplo_2_upload_especifico():
    """
    Exemplo 2: Upload específico por tipo
    Use quando você souber exatamente qual é o tipo do arquivo
    """
    print("\n" + "="*80)
    print("EXEMPLO 2: Upload Específico por Tipo")
    print("="*80)
    
    uploader = NFeUploader()
    
    # Upload de NotaFiscal
    result_nf = uploader.upload_nota_fiscal(
        file_path="data/202505_NFe_NotaFiscal.csv",
        uploaded_by="api_user"
    )
    print(f"\n✅ NotaFiscal: {result_nf['rows_inserted']} linhas")
    
    # Upload de NotaFiscalItem
    result_nfi = uploader.upload_nota_fiscal_item(
        file_path="data/202505_NFe_NotaFiscalItem.csv",
        uploaded_by="api_user"
    )
    print(f"✅ NotaFiscalItem: {result_nfi['rows_inserted']} linhas")


def exemplo_3_upload_ambos():
    """
    Exemplo 3: Upload dos dois arquivos de uma vez
    Função helper para facilitar o upload completo
    """
    print("\n" + "="*80)
    print("EXEMPLO 3: Upload dos Dois Arquivos")
    print("="*80)
    
    results = upload_nfe_files(
        nota_fiscal_path="data/202505_NFe_NotaFiscal.csv",
        nota_fiscal_item_path="data/202505_NFe_NotaFiscalItem.csv",
        uploaded_by="batch_user"
    )
    
    for file_type, result in results.items():
        print(f"\n✅ {file_type.upper()}")
        print(f"   Linhas: {result['rows_inserted']}/{result['total_rows']}")
        print(f"   Status: {'Sucesso' if result['success'] else 'Falha'}")


def exemplo_4_monitorar_upload():
    """
    Exemplo 4: Monitorar progresso de uploads
    """
    print("\n" + "="*80)
    print("EXEMPLO 4: Monitorar Uploads")
    print("="*80)
    
    # Listar todos os uploads
    uploads = supabase.table('uploads').select('*').order('uploaded_at', desc=True).limit(10).execute()
    
    print("\n📊 Últimos 10 uploads:")
    for upload in uploads.data:
        status_icon = {
            'completed': '✅',
            'processing': '⏳',
            'failed': '❌',
            'pending': '⏸️'
        }.get(upload['status'], '❓')
        
        progress = (upload['rows_processed'] / upload['rows_total'] * 100) if upload['rows_total'] > 0 else 0
        
        print(f"\n{status_icon} {upload['filename']}")
        print(f"   ID: {upload['id']}")
        print(f"   Tipo: {upload['file_type']}")
        print(f"   Status: {upload['status']}")
        print(f"   Progresso: {upload['rows_processed']}/{upload['rows_total']} ({progress:.1f}%)")
        print(f"   Data: {upload['uploaded_at']}")


def exemplo_5_validar_integridade():
    """
    Exemplo 5: Validar integridade financeira de notas
    """
    print("\n" + "="*80)
    print("EXEMPLO 5: Validar Integridade")
    print("="*80)
    
    # Buscar uma nota para validar
    notas = supabase.table('nota_fiscal').select('chave_acesso').limit(5).execute()
    
    if not notas.data:
        print("\n⚠️  Nenhuma nota encontrada no banco")
        return
    
    print("\n🔍 Validando integridade das primeiras 5 notas:")
    
    for nota in notas.data:
        chave = nota['chave_acesso']
        
        # Buscar nota e seus itens
        nota_data = supabase.table('nota_fiscal').select('*').eq('chave_acesso', chave).single().execute()
        itens = supabase.table('nota_fiscal_item').select('*').eq('chave_acesso', chave).execute()
        
        valor_nota = float(nota_data.data['valor_nota_fiscal'] or 0)
        soma_itens = sum(float(item['valor_total'] or 0) for item in itens.data)
        diferenca = abs(valor_nota - soma_itens)
        valido = diferenca < 0.01
        
        status = '✅ OK' if valido else '❌ DIVERGENTE'
        
        print(f"\n{status} Nota {nota_data.data['numero']}")
        print(f"   Chave: {chave[:20]}...")
        print(f"   Valor Nota: R$ {valor_nota:,.2f}")
        print(f"   Soma Itens: R$ {soma_itens:,.2f}")
        print(f"   Diferença: R$ {diferenca:,.2f}")
        print(f"   Qtd Itens: {len(itens.data)}")


def exemplo_6_analises_basicas():
    """
    Exemplo 6: Queries de análise básicas
    """
    print("\n" + "="*80)
    print("EXEMPLO 6: Análises Básicas")
    print("="*80)
    
    # Total de notas
    total_notas = supabase.table('nota_fiscal').select('*', count='exact').execute()
    count_notas = total_notas.count or 0
    print(f"\n📊 Total de notas: {count_notas}")
    
    # Total de itens
    total_itens = supabase.table('nota_fiscal_item').select('*', count='exact').execute()
    count_itens = total_itens.count or 0
    print(f"📦 Total de itens: {count_itens}")
    
    # Média de itens por nota
    if count_notas > 0:
        media = count_itens / count_notas
        print(f"📈 Média de itens por nota: {media:.2f}")
    
    # Top 5 UFs destinatárias
    print("\n🌎 Top 5 UFs Destinatárias:")
    try:
        # Busca todas as notas e agrupa no Python (funciona mesmo sem dados)
        notas_uf = supabase.table('nota_fiscal')\
            .select('uf_destinatario')\
            .execute()
        
        if notas_uf.data:
            from collections import Counter
            uf_counts = Counter(n['uf_destinatario'] for n in notas_uf.data if n.get('uf_destinatario'))
            for uf, qtd in uf_counts.most_common(5):
                print(f"   {uf}: {qtd} notas")
        else:
            print("   (Nenhum dado disponível)")
    except Exception as e:
        print(f"   ⚠️  Erro ao buscar UFs: {str(e)[:100]}")
    
    # Top 5 produtos
    print("\n🏆 Top 5 Produtos Mais Vendidos:")
    try:
        # Busca todos os itens e agrupa no Python
        itens = supabase.table('nota_fiscal_item')\
            .select('ncm_tipo_produto, quantidade, chave_acesso')\
            .execute()
        
        if itens.data:
            from collections import defaultdict
            produto_stats = defaultdict(lambda: {'notas': set(), 'qtd_total': 0})
            
            for item in itens.data:
                produto = item.get('ncm_tipo_produto')
                if produto:
                    produto_stats[produto]['notas'].add(item.get('chave_acesso'))
                    try:
                        qtd = float(item.get('quantidade', 0) or 0)
                        produto_stats[produto]['qtd_total'] += qtd
                    except (ValueError, TypeError):
                        pass
            
            # Ordena por quantidade total
            sorted_produtos = sorted(
                produto_stats.items(), 
                key=lambda x: x[1]['qtd_total'], 
                reverse=True
            )[:5]
            
            for produto, stats in sorted_produtos:
                print(f"   {produto}: {len(stats['notas'])} notas, {stats['qtd_total']:.2f} unidades")
        else:
            print("   (Nenhum dado disponível)")
    except Exception as e:
        print(f"   ⚠️  Erro ao buscar produtos: {str(e)[:100]}")


def menu_principal():
    """Menu interativo para escolher exemplos"""
    while True:
        print("\n" + "="*80)
        print("EXEMPLOS DE USO - Sistema de Upload de NF-e")
        print("="*80)
        print("\n1. Upload Automático (detecta tipo)")
        print("2. Upload Específico por Tipo")
        print("3. Upload dos Dois Arquivos")
        print("4. Monitorar Uploads")
        print("5. Validar Integridade")
        print("6. Análises Básicas")
        print("0. Sair")
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        try:
            if escolha == '1':
                exemplo_1_upload_automatico()
            elif escolha == '2':
                exemplo_2_upload_especifico()
            elif escolha == '3':
                exemplo_3_upload_ambos()
            elif escolha == '4':
                exemplo_4_monitorar_upload()
            elif escolha == '5':
                exemplo_5_validar_integridade()
            elif escolha == '6':
                exemplo_6_analises_basicas()
            elif escolha == '0':
                print("\n👋 Até logo!")
                break
            else:
                print("\n❌ Opção inválida")
        except Exception as e:
            logger.error(f"Erro ao executar exemplo: {str(e)}")
            print(f"\n❌ Erro: {str(e)}")
        
        input("\n\nPressione Enter para continuar...")


if __name__ == "__main__":
    # Modo interativo
    menu_principal()
    
    # Para executar um exemplo específico diretamente:
    # exemplo_1_upload_automatico()
    # exemplo_4_monitorar_upload()
    # exemplo_6_analises_basicas()
