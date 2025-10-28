"""
Módulo para upload e processamento de arquivos CSV de Notas Fiscais Eletrônicas
Suporta os dois tipos de arquivo:
- 202505_NFe_NotaFiscal.csv (cabeçalho)
- 202505_NFe_NotaFiscalItem.csv (itens)
"""

import pandas as pd
import uuid
from datetime import datetime
from typing import Literal, Optional, Dict, Any
from pathlib import Path
import logging

from src.vectorstore.supabase_client import supabase
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class NFeUploader:
    """Classe para upload e processamento de arquivos CSV de NF-e"""
    
    # Mapeamento de colunas CSV -> colunas do banco
    NOTA_FISCAL_COLUMNS_MAP = {
        'CHAVE DE ACESSO': 'chave_acesso',
        'MODELO': 'modelo',
        'SÉRIE': 'serie',
        'NÚMERO': 'numero',
        'NATUREZA DA OPERAÇÃO': 'natureza_operacao',
        'DATA EMISSÃO': 'data_emissao',
        # 'EVENTO MAIS RECENTE' e 'DATA/HORA EVENTO MAIS RECENTE' não existem no schema - ignoradas
        'CPF/CNPJ Emitente': 'cpf_cnpj_emitente',
        'RAZÃO SOCIAL EMITENTE': 'razao_social_emitente',
        'INSCRIÇÃO ESTADUAL EMITENTE': 'ie_emitente',
        'UF EMITENTE': 'uf_emitente',
        'MUNICÍPIO EMITENTE': 'municipio_emitente',
        'CNPJ DESTINATÁRIO': 'cnpj_destinatario',
        'NOME DESTINATÁRIO': 'nome_destinatario',
        'UF DESTINATÁRIO': 'uf_destinatario',
        'INDICADOR IE DESTINATÁRIO': 'indicador_ie_destinatario',
        'DESTINO DA OPERAÇÃO': 'destino_operacao',
        'CONSUMIDOR FINAL': 'consumidor_final',
        'PRESENÇA DO COMPRADOR': 'presenca_comprador',
        'VALOR NOTA FISCAL': 'valor_nota_fiscal',
    }
    
    NOTA_FISCAL_ITEM_COLUMNS_MAP = {
        'CHAVE DE ACESSO': 'chave_acesso',
        'MODELO': 'modelo',
        'SÉRIE': 'serie',
        'NÚMERO': 'numero',
        'NATUREZA DA OPERAÇÃO': 'natureza_operacao',
        'DATA EMISSÃO': 'data_emissao',
        'CPF/CNPJ Emitente': 'cpf_cnpj_emitente',
        'RAZÃO SOCIAL EMITENTE': 'razao_social_emitente',
        'INSCRIÇÃO ESTADUAL EMITENTE': 'ie_emitente',
        'UF EMITENTE': 'uf_emitente',
        'MUNICÍPIO EMITENTE': 'municipio_emitente',
        'CNPJ DESTINATÁRIO': 'cnpj_destinatario',
        'NOME DESTINATÁRIO': 'nome_destinatario',
        'UF DESTINATÁRIO': 'uf_destinatario',
        'INDICADOR IE DESTINATÁRIO': 'indicador_ie_destinatario',
        'DESTINO DA OPERAÇÃO': 'destino_operacao',
        'CONSUMIDOR FINAL': 'consumidor_final',
        'PRESENÇA DO COMPRADOR': 'presenca_comprador',
        'NÚMERO PRODUTO': 'numero_produto',
        'DESCRIÇÃO DO PRODUTO/SERVIÇO': 'descricao_produto',
        'CÓDIGO NCM/SH': 'codigo_ncm',
        'NCM/SH (TIPO DE PRODUTO)': 'ncm_tipo_produto',
        'CFOP': 'cfop',
        'QUANTIDADE': 'quantidade',
        'UNIDADE': 'unidade',
        'VALOR UNITÁRIO': 'valor_unitario',
        'VALOR TOTAL': 'valor_total',
    }
    
    def __init__(self):
        self.encoding = 'latin-1'
        self.separator = ';'
    
    def detect_file_type(self, df: pd.DataFrame) -> Literal['nota_fiscal', 'nota_fiscal_item']:
        """Detecta automaticamente o tipo de arquivo baseado nas colunas"""
        columns = set(df.columns)
        
        # Colunas exclusivas de NotaFiscal
        nota_fiscal_exclusive = {'EVENTO MAIS RECENTE', 'DATA/HORA EVENTO MAIS RECENTE', 'VALOR NOTA FISCAL'}
        
        # Colunas exclusivas de NotaFiscalItem
        nota_fiscal_item_exclusive = {'NÚMERO PRODUTO', 'DESCRIÇÃO DO PRODUTO/SERVIÇO', 'CÓDIGO NCM/SH'}
        
        if nota_fiscal_exclusive.issubset(columns):
            return 'nota_fiscal'
        elif nota_fiscal_item_exclusive.issubset(columns):
            return 'nota_fiscal_item'
        else:
            raise ValueError("Arquivo CSV não reconhecido como NotaFiscal ou NotaFiscalItem")
    
    def create_upload_record(
        self, 
        filename: str, 
        file_type: str, 
        file_size_mb: float,
        rows_total: int,
        uploaded_by: Optional[str] = None
    ) -> str:
        """Cria registro de upload no banco"""
        upload_data = {
            'filename': filename,
            'file_type': file_type,
            'file_size_mb': file_size_mb,
            'uploaded_by': uploaded_by or 'system',
            'status': 'processing',
            'rows_total': rows_total,
            'rows_processed': 0
        }
        
        result = supabase.table('uploads').insert(upload_data).execute()
        upload_id = result.data[0]['id']
        logger.info(f"Upload criado: {upload_id} ({filename})")
        return upload_id
    
    def update_upload_progress(
        self, 
        upload_id: str, 
        rows_processed: int, 
        status: str = 'processing'
    ):
        """Atualiza progresso do upload"""
        supabase.table('uploads').update({
            'rows_processed': rows_processed,
            'status': status
        }).eq('id', upload_id).execute()
    
    def update_upload_error(self, upload_id: str, error_message: str):
        """Marca upload como falhado"""
        supabase.table('uploads').update({
            'status': 'failed',
            'error_message': error_message
        }).eq('id', upload_id).execute()
    
    def clean_dataframe(self, df: pd.DataFrame, file_type: str) -> pd.DataFrame:
        """Limpa e transforma o DataFrame para inserção no banco"""
        df = df.copy()
        
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        # Renomeia colunas
        column_map = (self.NOTA_FISCAL_COLUMNS_MAP if file_type == 'nota_fiscal' 
                     else self.NOTA_FISCAL_ITEM_COLUMNS_MAP)
        df = df.rename(columns=column_map)
        
        # Remove colunas não mapeadas (que não existem no schema)
        expected_cols = set(column_map.values())
        expected_cols.add('upload_id')  # Coluna que será adicionada depois
        current_cols = set(df.columns)
        cols_to_drop = current_cols - expected_cols
        if cols_to_drop:
            logger.info(f"Removendo colunas não mapeadas: {cols_to_drop}")
            df = df.drop(columns=list(cols_to_drop))
        
        # Converte tipos de dados
        if file_type == 'nota_fiscal':
            df['data_emissao'] = pd.to_datetime(df['data_emissao'], format='%d/%m/%Y', errors='coerce')
            
            # Limpa valor_nota_fiscal (remove espaços e converte vírgula para ponto)
            if 'valor_nota_fiscal' in df.columns:
                df['valor_nota_fiscal'] = df['valor_nota_fiscal'].astype(str).str.replace(' ', '').str.replace(',', '.')
                df['valor_nota_fiscal'] = pd.to_numeric(df['valor_nota_fiscal'], errors='coerce')
        
        else:  # nota_fiscal_item
            df['data_emissao'] = pd.to_datetime(df['data_emissao'], format='%d/%m/%Y', errors='coerce')
            
            # Limpa valores numéricos
            numeric_cols = ['quantidade', 'valor_unitario', 'valor_total']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(' ', '').str.replace(',', '.')
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Converte NaN e NaT para None (NULL no PostgreSQL)
        df = df.where(pd.notnull(df), None)
        
        # Converte explicitamente colunas de data/timestamp para garantir que NaT vire None
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].apply(lambda x: None if pd.isna(x) else x)
        
        return df
    
    def upload_nota_fiscal(
        self, 
        file_path: str, 
        uploaded_by: Optional[str] = None,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Faz upload do arquivo NotaFiscal.csv
        
        Args:
            file_path: Caminho do arquivo CSV
            uploaded_by: Identificador do usuário (opcional)
            batch_size: Tamanho do lote para inserção
            
        Returns:
            Dict com estatísticas do upload
        """
        try:
            file_path = Path(file_path)
            logger.info(f"Iniciando upload de NotaFiscal: {file_path}")
            
            # Lê CSV
            df = pd.read_csv(file_path, encoding=self.encoding, sep=self.separator)
            file_type = self.detect_file_type(df)
            
            if file_type != 'nota_fiscal':
                raise ValueError("Arquivo não é do tipo NotaFiscal")
            
            # Cria registro de upload
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            upload_id = self.create_upload_record(
                filename=file_path.name,
                file_type=file_type,
                file_size_mb=round(file_size_mb, 2),
                rows_total=len(df),
                uploaded_by=uploaded_by
            )
            
            # Limpa dados
            df = self.clean_dataframe(df, file_type)
            df['upload_id'] = upload_id
            
            # Insere em lotes
            total_rows = len(df)
            rows_inserted = 0
            errors = []
            
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i+batch_size]
                records = batch.to_dict('records')
                
                try:
                    supabase.table('nota_fiscal').insert(records).execute()
                    rows_inserted += len(records)
                    self.update_upload_progress(upload_id, rows_inserted)
                    logger.info(f"Lote {i//batch_size + 1}: {rows_inserted}/{total_rows} linhas inseridas")
                except Exception as e:
                    error_msg = f"Erro no lote {i//batch_size + 1}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Finaliza upload
            if rows_inserted == total_rows:
                self.update_upload_progress(upload_id, rows_inserted, status='completed')
                logger.info(f"Upload concluído: {rows_inserted} linhas inseridas")
            else:
                error_summary = "; ".join(errors[:3])  # Primeiros 3 erros
                self.update_upload_error(upload_id, f"Parcialmente concluído. Erros: {error_summary}")
            
            return {
                'upload_id': upload_id,
                'filename': file_path.name,
                'file_type': file_type,
                'total_rows': total_rows,
                'rows_inserted': rows_inserted,
                'success': rows_inserted == total_rows,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Erro fatal no upload: {str(e)}")
            if 'upload_id' in locals():
                self.update_upload_error(upload_id, str(e))
            raise
    
    def upload_nota_fiscal_item(
        self, 
        file_path: str, 
        uploaded_by: Optional[str] = None,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Faz upload do arquivo NotaFiscalItem.csv
        
        Args:
            file_path: Caminho do arquivo CSV
            uploaded_by: Identificador do usuário (opcional)
            batch_size: Tamanho do lote para inserção
            
        Returns:
            Dict com estatísticas do upload
        """
        try:
            file_path = Path(file_path)
            logger.info(f"Iniciando upload de NotaFiscalItem: {file_path}")
            
            # Lê CSV
            df = pd.read_csv(file_path, encoding=self.encoding, sep=self.separator)
            file_type = self.detect_file_type(df)
            
            if file_type != 'nota_fiscal_item':
                raise ValueError("Arquivo não é do tipo NotaFiscalItem")
            
            # Cria registro de upload
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            upload_id = self.create_upload_record(
                filename=file_path.name,
                file_type=file_type,
                file_size_mb=round(file_size_mb, 2),
                rows_total=len(df),
                uploaded_by=uploaded_by
            )
            
            # Limpa dados
            df = self.clean_dataframe(df, file_type)
            df['upload_id'] = upload_id
            
            # Insere em lotes
            total_rows = len(df)
            rows_inserted = 0
            errors = []
            
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i+batch_size]
                records = batch.to_dict('records')
                
                try:
                    supabase.table('nota_fiscal_item').insert(records).execute()
                    rows_inserted += len(records)
                    self.update_upload_progress(upload_id, rows_inserted)
                    
                    if (i // batch_size) % 10 == 0:  # Log a cada 10 lotes
                        logger.info(f"Progresso: {rows_inserted}/{total_rows} linhas inseridas")
                        
                except Exception as e:
                    error_msg = f"Erro no lote {i//batch_size + 1}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Finaliza upload
            if rows_inserted == total_rows:
                self.update_upload_progress(upload_id, rows_inserted, status='completed')
                logger.info(f"Upload concluído: {rows_inserted} linhas inseridas")
            else:
                error_summary = "; ".join(errors[:3])
                self.update_upload_error(upload_id, f"Parcialmente concluído. Erros: {error_summary}")
            
            return {
                'upload_id': upload_id,
                'filename': file_path.name,
                'file_type': file_type,
                'total_rows': total_rows,
                'rows_inserted': rows_inserted,
                'success': rows_inserted == total_rows,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Erro fatal no upload: {str(e)}")
            if 'upload_id' in locals():
                self.update_upload_error(upload_id, str(e))
            raise
    
    def upload_auto(
        self, 
        file_path: str, 
        uploaded_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detecta automaticamente o tipo de arquivo e faz o upload
        
        Args:
            file_path: Caminho do arquivo CSV
            uploaded_by: Identificador do usuário (opcional)
            
        Returns:
            Dict com estatísticas do upload
        """
        # Lê apenas primeiras linhas para detectar tipo
        df_sample = pd.read_csv(file_path, encoding=self.encoding, sep=self.separator, nrows=5)
        file_type = self.detect_file_type(df_sample)
        
        logger.info(f"Tipo de arquivo detectado: {file_type}")
        
        if file_type == 'nota_fiscal':
            return self.upload_nota_fiscal(file_path, uploaded_by)
        else:
            return self.upload_nota_fiscal_item(file_path, uploaded_by)


# Função auxiliar para uso direto
def upload_nfe_files(
    nota_fiscal_path: Optional[str] = None,
    nota_fiscal_item_path: Optional[str] = None,
    uploaded_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Função helper para fazer upload dos dois arquivos de NF-e
    
    Args:
        nota_fiscal_path: Caminho do arquivo NotaFiscal.csv
        nota_fiscal_item_path: Caminho do arquivo NotaFiscalItem.csv
        uploaded_by: Identificador do usuário
        
    Returns:
        Dict com resultados de ambos os uploads
    """
    uploader = NFeUploader()
    results = {}
    
    if nota_fiscal_path:
        logger.info("=== Iniciando upload de NotaFiscal ===")
        results['nota_fiscal'] = uploader.upload_nota_fiscal(nota_fiscal_path, uploaded_by)
    
    if nota_fiscal_item_path:
        logger.info("=== Iniciando upload de NotaFiscalItem ===")
        results['nota_fiscal_item'] = uploader.upload_nota_fiscal_item(nota_fiscal_item_path, uploaded_by)
    
    return results


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python nfe_uploader.py <caminho_arquivo_csv> [usuario]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    user = sys.argv[2] if len(sys.argv) > 2 else None
    
    uploader = NFeUploader()
    result = uploader.upload_auto(file_path, user)
    
    print("\n" + "="*80)
    print("RESULTADO DO UPLOAD")
    print("="*80)
    print(f"Arquivo: {result['filename']}")
    print(f"Tipo: {result['file_type']}")
    print(f"Total de linhas: {result['total_rows']}")
    print(f"Linhas inseridas: {result['rows_inserted']}")
    print(f"Sucesso: {'✅ SIM' if result['success'] else '❌ NÃO'}")
    if result['errors']:
        print(f"\nErros encontrados: {len(result['errors'])}")
        for error in result['errors'][:5]:
            print(f"  - {error}")
    print("="*80)
