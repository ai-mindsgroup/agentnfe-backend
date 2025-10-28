"""
Script para executar migration de NF-e e testar upload dos arquivos
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para imports funcionarem
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.utils.logging_config import get_logger
from src.vectorstore.supabase_client import supabase

logger = get_logger(__name__)


def run_nfe_migration():
    """Executa a migration do schema de NF-e"""
    migration_file = Path("migrations/0008_nfe_schema.sql")
    
    if not migration_file.exists():
        logger.error(f"Arquivo de migration não encontrado: {migration_file}")
        return False
    
    try:
        logger.info("Executando migration 0008_nfe_schema.sql...")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Usa psycopg para executar o SQL diretamente
        from src.settings import build_db_dsn
        import psycopg
        
        dsn = build_db_dsn()
        
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                # Executa todo o SQL de uma vez
                cur.execute(sql_content)
                conn.commit()
                logger.info("✅ Migration executada com sucesso!")
                return True
        
    except Exception as e:
        error_msg = str(e)
        # Ignora erros de "já existe" (idempotência)
        if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
            logger.info("⚠️  Algumas tabelas já existem (ignorando)")
            return True
        else:
            logger.error(f"❌ Erro ao executar migration: {error_msg}")
            return False


def test_upload():
    """Testa upload dos arquivos de exemplo"""
    from src.data.nfe_uploader import upload_nfe_files
    
    nota_fiscal_path = "data/202505_NFe_NotaFiscal.csv"
    nota_fiscal_item_path = "data/202505_NFe_NotaFiscalItem.csv"
    
    if not Path(nota_fiscal_path).exists():
        logger.warning(f"Arquivo {nota_fiscal_path} não encontrado")
        nota_fiscal_path = None
    
    if not Path(nota_fiscal_item_path).exists():
        logger.warning(f"Arquivo {nota_fiscal_item_path} não encontrado")
        nota_fiscal_item_path = None
    
    if not nota_fiscal_path and not nota_fiscal_item_path:
        logger.error("Nenhum arquivo de NF-e encontrado para teste")
        return False
    
    try:
        logger.info("Iniciando teste de upload...")
        results = upload_nfe_files(
            nota_fiscal_path=nota_fiscal_path,
            nota_fiscal_item_path=nota_fiscal_item_path,
            uploaded_by="test_script"
        )
        
        print("\n" + "="*80)
        print("RESULTADOS DO TESTE DE UPLOAD")
        print("="*80)
        
        for file_type, result in results.items():
            print(f"\n📄 {file_type.upper()}")
            print(f"   Arquivo: {result['filename']}")
            print(f"   Total: {result['total_rows']} linhas")
            print(f"   Inseridas: {result['rows_inserted']} linhas")
            print(f"   Status: {'✅ Sucesso' if result['success'] else '❌ Falha'}")
            
            if result['errors']:
                print(f"   Erros: {len(result['errors'])}")
                for error in result['errors'][:3]:
                    print(f"      - {error}")
        
        print("="*80)
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de upload: {str(e)}")
        return False


def check_database_connection():
    """Verifica conexão com banco de dados"""
    try:
        # Tenta fazer uma query simples em uma tabela que sempre existe (ou cria)
        result = supabase.rpc('version').execute()
        logger.info("✅ Conexão com banco de dados OK")
        return True
    except Exception as e:
        # Se a função version não existe, tenta outra abordagem
        try:
            # Tenta listar schemas - isso sempre funciona se conectado
            from src.settings import build_db_dsn
            import psycopg
            
            dsn = build_db_dsn()
            with psycopg.connect(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    logger.info("✅ Conexão com banco de dados OK")
                    return True
        except Exception as e2:
            logger.error(f"❌ Erro de conexão com banco: {str(e2)}")
            logger.info("Certifique-se de que as variáveis SUPABASE_URL e SUPABASE_KEY estão configuradas")
            return False


def main():
    """Função principal"""
    print("="*80)
    print("SETUP DE NF-e - Migração e Teste de Upload")
    print("="*80)
    
    # 1. Verifica conexão
    print("\n1️⃣  Verificando conexão com banco de dados...")
    if not check_database_connection():
        print("❌ Falha na conexão. Verifique as configurações.")
        return 1
    
    # 2. Executa migration
    print("\n2️⃣  Executando migration do schema de NF-e...")
    if not run_nfe_migration():
        print("❌ Falha na migration.")
        return 1
    
    # 3. Pergunta se quer fazer teste de upload
    if len(sys.argv) > 1 and sys.argv[1] == '--skip-upload':
        print("\n⏭️  Upload ignorado (flag --skip-upload)")
        return 0
    
    print("\n3️⃣  Deseja fazer o teste de upload dos arquivos CSV?")
    print("   (Isso pode demorar vários minutos para arquivos grandes)")
    
    response = input("   Continuar? [s/N]: ").strip().lower()
    
    if response == 's':
        print("\n🚀 Iniciando teste de upload...")
        if test_upload():
            print("\n✅ Teste concluído com sucesso!")
            return 0
        else:
            print("\n❌ Teste falhou.")
            return 1
    else:
        print("\n⏭️  Upload ignorado pelo usuário")
        print("\nPara fazer upload posteriormente, use:")
        print("  python -m src.data.nfe_uploader <caminho_arquivo.csv>")
        return 0


if __name__ == "__main__":
    sys.exit(main())
