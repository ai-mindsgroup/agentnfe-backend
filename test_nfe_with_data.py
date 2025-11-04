#!/usr/bin/env python3
"""
Script de teste da API NFe com dados reais dos CSVs
===================================================
Testa os endpoints NFe usando os dados em data/
"""

import sys
from pathlib import Path

# Adiciona o diretrio raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

import pandas as pd
from src.agent.nfe_tax_specialist_agent import NFeTaxSpecialistAgent

def load_nfe_data():
    """Carrega dados das notas fiscais"""
    print(" Carregando dados dos CSVs...")
    
    # Carrega nota fiscal
    nf_path = root_dir / "data" / "202505_NFe_NotaFiscal.csv"
    nf_items_path = root_dir / "data" / "202505_NFe_NotaFiscalItem.csv"
    
    # Tenta diferentes encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    if nf_path.exists():
        df_notas = None
        for encoding in encodings:
            try:
                df_notas = pd.read_csv(nf_path, encoding=encoding, sep=';')
                print(f" Notas fiscais carregadas: {len(df_notas)} registros (encoding: {encoding})")
                print(f"   Colunas: {list(df_notas.columns)[:5]}...")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                # Tenta com separador padro
                try:
                    df_notas = pd.read_csv(nf_path, encoding=encoding)
                    print(f" Notas fiscais carregadas: {len(df_notas)} registros (encoding: {encoding})")
                    print(f"   Colunas: {list(df_notas.columns)[:5]}...")
                    break
                except:
                    continue
        
        if df_notas is None:
            print(f" No foi possvel ler o arquivo com nenhum encoding testado")
            return None, None
    else:
        print(f" Arquivo no encontrado: {nf_path}")
        return None, None
    
    if nf_items_path.exists():
        df_items = None
        for encoding in encodings:
            try:
                df_items = pd.read_csv(nf_items_path, encoding=encoding, sep=';')
                print(f" Itens carregados: {len(df_items)} registros (encoding: {encoding})")
                print(f"   Colunas: {list(df_items.columns)[:5]}...")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                try:
                    df_items = pd.read_csv(nf_items_path, encoding=encoding)
                    print(f" Itens carregados: {len(df_items)} registros (encoding: {encoding})")
                    print(f"   Colunas: {list(df_items.columns)[:5]}...")
                    break
                except:
                    continue
        
        if df_items is None:
            print(f" No foi possvel ler arquivo de itens")
            return df_notas, None
    else:
        print(f" Arquivo no encontrado: {nf_items_path}")
        return df_notas, None
    
    return df_notas, df_items

def test_cfop_validation(agent, df_items):
    """Testa validao de CFOP"""
    print("\n" + "="*70)
    print(" TESTE 1: Validao de CFOP")
    print("="*70)
    
    if df_items is None or 'CFOP' not in df_items.columns:
        print(" Coluna CFOP no encontrada")
        print(f"   Colunas disponveis: {list(df_items.columns) if df_items is not None else 'N/A'}")
        return
    
    # Pega alguns CFOPs para testar
    cfops = df_items['CFOP'].dropna().unique()[:8]
    
    print(f" Testando {len(cfops)} CFOPs diferentes dos dados reais:\n")
    
    for cfop in cfops:
        try:
            cfop_str = str(int(cfop)) if pd.notna(cfop) else str(cfop)
            result = agent.validate_cfop(cfop_str)
            status = "" if result['valido'] else ""
            desc = result.get('descricao', 'Descrio no disponvel')
            natureza = result.get('natureza_operacao', 'N/A')
            print(f"{status} CFOP {cfop_str}:")
            print(f"   Descrio: {desc}")
            print(f"   Natureza: {natureza}\n")
        except Exception as e:
            print(f" Erro ao validar CFOP {cfop}: {e}\n")

def test_ncm_validation(agent, df_items):
    """Testa validao de NCM"""
    print("="*70)
    print(" TESTE 2: Validao de NCM")
    print("="*70)
    
    ncm_col = 'CDIGO NCM/SH' if 'CDIGO NCM/SH' in df_items.columns else 'NCM'
    
    if df_items is None or ncm_col not in df_items.columns:
        print(" Coluna NCM no encontrada")
        print(f"   Colunas disponveis: {list(df_items.columns) if df_items is not None else 'N/A'}")
        return
    
    # Pega alguns NCMs para testar
    ncms = df_items[ncm_col].dropna().unique()[:8]
    
    print(f" Testando {len(ncms)} NCMs diferentes dos dados reais:\n")
    
    for ncm in ncms:
        try:
            ncm_str = str(int(ncm)) if pd.notna(ncm) else str(ncm)
            result = agent.validate_ncm(ncm_str)
            status = "" if result['valido'] else ""
            desc = result.get('descricao', 'Descrio no disponvel')
            categoria = result.get('categoria', 'N/A')
            print(f"{status} NCM {ncm_str}:")
            print(f"   Descrio: {desc}")
            print(f"   Categoria: {categoria}\n")
        except Exception as e:
            print(f" Erro ao validar NCM {ncm}: {e}\n")

def test_nota_analysis(agent, df_notas, df_items):
    """Testa anlise completa de nota fiscal"""
    print("="*70)
    print(" TESTE 3: Anlise Completa de Nota Fiscal")
    print("="*70)
    
    if df_notas is None:
        print(" Dados de notas no disponveis")
        return
    
    # Pega a primeira nota com valor significativo
    # Converte valor para numrico
    df_notas['VALOR_NUM'] = pd.to_numeric(df_notas['VALOR NOTA FISCAL'].str.replace(',', '.'), errors='coerce')
    nota = df_notas[df_notas['VALOR_NUM'] > 1000].iloc[0].to_dict()
    
    chave = nota.get('CHAVE DE ACESSO', '')
    emitente = nota.get('RAZO SOCIAL EMITENTE', 'N/A')
    dest = nota.get('NOME DESTINATRIO', 'N/A')
    valor = nota.get('VALOR_NUM', 0)
    
    print(f"\n Analisando nota fiscal real:")
    print(f"   Chave: {chave[:44]}...")
    print(f"   Emitente: {emitente}")
    print(f"   Destinatrio: {dest}")
    print(f"   Valor: R$ {valor:,.2f}")
    print(f"   Data: {nota.get('DATA EMISSO', 'N/A')}")
    
    try:
        # Prepara dados da nota com nomes corretos
        nota_data = {
            'chave_acesso': chave,
            'numero_nota': int(nota.get('NMERO', 0)),
            'emitente_cnpj': nota.get('CPF/CNPJ Emitente', ''),
            'emitente_razao_social': emitente,
            'destinatario_cnpj': nota.get('CNPJ DESTINATRIO', ''),
            'destinatario_razao_social': dest,
            'valor_total': valor,
            'valor_icms': 0.0,  # No tem no CSV
            'data_emissao': str(nota.get('DATA EMISSO', ''))
        }
        
        # Adiciona itens se disponvel
        if df_items is not None and 'CHAVE DE ACESSO' in df_items.columns:
            items = df_items[df_items['CHAVE DE ACESSO'] == chave]
            
            if not items.empty:
                print(f"   Itens: {len(items)} produtos na nota")
                nota_data['itens'] = []
                for _, item in items.head(5).iterrows():
                    cfop_val = item.get('CFOP', '')
                    ncm_val = item.get('CDIGO NCM/SH', '')
                    valor_str = str(item.get('VALOR TOTAL', '0')).replace(',', '.')
                    nota_data['itens'].append({
                        'cfop': str(int(cfop_val)) if pd.notna(cfop_val) else '',
                        'ncm': str(int(ncm_val)) if pd.notna(ncm_val) else '',
                        'descricao': str(item.get('DESCRIO DO PRODUTO/SERVIO', '')),
                        'valor': float(valor_str) if valor_str else 0.0
                    })
        
        result = agent.analyze_nota_fiscal(nota_data)
        
        print(f"\n Resultado da Anlise:")
        print(f"   Score Fiscal: {result.get('score_fiscal', 0)}/100")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        if 'validacoes' in result and result['validacoes']:
            print(f"\n    Validaes:")
            for val in result['validacoes'][:5]:
                print(f"     - {val}")
        
        if 'recomendacoes' in result and result['recomendacoes']:
            print(f"\n    Recomendaes:")
            for rec in result['recomendacoes'][:5]:
                print(f"     - {rec}")
                
    except Exception as e:
        print(f" Erro na anlise: {e}")
        import traceback
        traceback.print_exc()

def test_anomaly_detection(agent, df_notas):
    """Testa deteco de anomalias"""
    print("\n" + "="*70)
    print(" TESTE 4: Deteco de Anomalias")
    print("="*70)
    
    if df_notas is None:
        print(" Dados de notas no disponveis")
        return
    
    # Pega algumas notas para anlise
    notas = df_notas.head(5).to_dict('records')
    
    try:
        result = agent.detect_anomalies(notas)
        
        if result.get('anomalias_detectadas', 0) > 0:
            print(f" {result['anomalias_detectadas']} anomalias detectadas:")
            
            for anomalia in result.get('anomalias', [])[:3]:
                print(f"\n    {anomalia.get('tipo', 'N/A')}")
                print(f"      Severidade: {anomalia.get('severidade', 'N/A')}")
                print(f"      Descrio: {anomalia.get('descricao', 'N/A')}")
        else:
            print(" Nenhuma anomalia detectada")
            
    except Exception as e:
        print(f" Erro na deteco: {e}")

def test_tax_query(agent):
    """Testa consultas fiscais"""
    print("\n" + "="*70)
    print(" TESTE 5: Consultas Fiscais (LLM)")
    print("="*70)
    
    queries = [
        "O que  CFOP?",
        "Qual a diferena entre operaes internas e interestaduais?",
        "Como funciona o clculo de ICMS?"
    ]
    
    for query in queries:
        print(f"\n Pergunta: {query}")
        try:
            result = agent.query_tax_knowledge(query)
            resposta = result.get('resposta', 'Sem resposta')
            print(f" Resposta: {resposta[:200]}...")
        except Exception as e:
            print(f" Erro (pode ser falta de API key): {e}")

def main():
    """Funo principal"""
    print("="*70)
    print(" TESTE DO AGENTE NFE COM DADOS REAIS")
    print("="*70)
    
    # Carrega dados
    df_notas, df_items = load_nfe_data()
    
    if df_notas is None:
        print("\n No foi possvel carregar os dados")
        return
    
    print(f"\n Estatsticas dos dados:")
    print(f"   Total de notas: {len(df_notas)}")
    if df_items is not None:
        print(f"   Total de itens: {len(df_items)}")
        print(f"   Mdia de itens por nota: {len(df_items)/len(df_notas):.1f}")
    
    # Inicializa agente
    print("\n Inicializando NFeTaxSpecialistAgent...")
    try:
        agent = NFeTaxSpecialistAgent()
        print(" Agente inicializado com sucesso")
    except Exception as e:
        print(f" Erro ao inicializar agente: {e}")
        return
    
    # Executa testes
    test_cfop_validation(agent, df_items)
    test_ncm_validation(agent, df_items)
    test_nota_analysis(agent, df_notas, df_items)
    test_anomaly_detection(agent, df_notas)
    test_tax_query(agent)
    
    print("\n" + "="*70)
    print(" TESTES CONCLUDOS")
    print("="*70)

if __name__ == "__main__":
    main()

