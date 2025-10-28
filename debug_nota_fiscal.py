"""
Debug: Testar inserção de uma única linha de NotaFiscal
"""
import pandas as pd
from pathlib import Path
from src.data.nfe_uploader import NFeUploader
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_single_insert():
    """Testa inserção de 1 linha para ver o erro exato"""
    
    # Usa o uploader para processar corretamente
    uploader = NFeUploader()
    
    # Lê o CSV
    csv_path = Path('data/202505_NFe_NotaFiscal.csv')
    df = pd.read_csv(csv_path, encoding='latin-1', sep=';', nrows=1)
    
    print(f"\n📋 Colunas do CSV ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # Limpa usando a função do uploader
    file_type = uploader.detect_file_type(df)
    print(f"\n✅ Tipo detectado: {file_type}")
    
    df = uploader.clean_dataframe(df, file_type)
    df['upload_id'] = '00000000-0000-0000-0000-000000000000'
    
    print(f"\n📋 Colunas após limpeza ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # Mostra os dados
    print(f"\n📄 Dados da primeira linha:")
    record = df.iloc[0].to_dict()
    for key, value in record.items():
        tipo = type(value).__name__
        valor_str = str(value)[:50]  # Limita exibição
        print(f"  {key}: {valor_str} ({tipo})")
    
    # Tenta inserir
    from src.vectorstore.supabase_client import supabase
    print(f"\n🔄 Tentando inserir no banco...")
    try:
        result = supabase.table('nota_fiscal').insert([record]).execute()
        print(f"✅ Sucesso! Inserido: {result.data}")
    except Exception as e:
        print(f"❌ ERRO: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        
        # Tenta pegar mais detalhes
        if hasattr(e, 'message'):
            print(f"   Detalhes: {e.message}")
        if hasattr(e, 'details'):
            print(f"   Details: {e.details}")
        if hasattr(e, 'hint'):
            print(f"   Hint: {e.hint}")

if __name__ == '__main__':
    test_single_insert()
