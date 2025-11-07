"""
Script para gerar embeddings das notas fiscais e popular tabelas vetoriais.

Este script:
1. Carrega notas fiscais do banco de dados Supabase
2. Cria chunks significativos de cada nota (com itens agregados)
3. Gera embeddings usando OpenAI via LangChain
4. Popula tabelas embeddings, chunks e metadata
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Adiciona src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vectorstore.supabase_client import supabase
from src.llm.langchain_manager import LangChainLLMManager
from src.utils.logging_config import get_logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.settings import GOOGLE_API_KEY, build_db_dsn
import psycopg
import uuid

logger = get_logger(__name__)


class NFeEmbeddingGenerator:
    """Gerador de embeddings para notas fiscais."""
    
    def __init__(self, batch_size: int = 100):
        """
        Inicializa o gerador de embeddings.
        
        Args:
            batch_size: Quantidade de notas a processar por batch
        """
        self.batch_size = batch_size
        
        # Usa Gemini para embeddings (768 dimensões)
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        self.embedding_dimensions = 768  # Gemini embedding-001
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", ", ", " "]
        )
        logger.info(f"NFeEmbeddingGenerator inicializado com batch_size={batch_size} (Gemini embeddings)")
    
    def fetch_notas_batch(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Busca um batch de notas fiscais do banco.
        
        Args:
            offset: Offset para paginação
            limit: Limite de registros
            
        Returns:
            Lista de notas fiscais
        """
        try:
            logger.info(f"Buscando batch de notas: offset={offset}, limit={limit}")
            
            result = supabase.table('nota_fiscal').select(
                '*, nota_fiscal_item(*)'
            ).range(offset, offset + limit - 1).execute()
            
            if not result.data:
                logger.warning(f"Nenhuma nota encontrada no range {offset}-{offset+limit}")
                return []
            
            logger.info(f"Retornadas {len(result.data)} notas")
            return result.data
            
        except Exception as e:
            logger.error(f"Erro ao buscar batch de notas: {e}", exc_info=True)
            return []
    
    def create_nota_text_representation(self, nota: Dict[str, Any]) -> str:
        """
        Cria representação textual completa de uma nota para embedding.
        
        Args:
            nota: Dicionário com dados da nota fiscal
            
        Returns:
            Texto formatado da nota
        """
        items = nota.get('nota_fiscal_item', [])
        
        # Cabeçalho da nota
        text_parts = [
            f"NOTA FISCAL ELETRÔNICA",
            f"Número: {nota.get('numero_nota', 'N/A')}",
            f"Série: {nota.get('serie', 'N/A')}",
            f"Data Emissão: {nota.get('data_emissao', 'N/A')}",
            f"",
            f"EMITENTE",
            f"CNPJ: {nota.get('cnpj_emitente', 'N/A')}",
            f"Nome: {nota.get('nome_emitente', 'N/A')}",
            f"UF: {nota.get('uf_emitente', 'N/A')}",
            f"",
            f"DESTINATÁRIO",
            f"CNPJ/CPF: {nota.get('cnpj_cpf_destinatario', 'N/A')}",
            f"UF: {nota.get('uf_destinatario', 'N/A')}",
            f"",
            f"VALORES",
            f"Valor Total: R$ {nota.get('valor_total', 0):.2f}",
            f"Base de Cálculo ICMS: R$ {nota.get('base_calculo_icms', 0):.2f}",
            f"Valor ICMS: R$ {nota.get('valor_icms', 0):.2f}",
            f"Valor IPI: R$ {nota.get('valor_ipi', 0):.2f}",
            f"Valor PIS: R$ {nota.get('valor_pis', 0):.2f}",
            f"Valor COFINS: R$ {nota.get('valor_cofins', 0):.2f}",
            f"",
            f"CFOP: {nota.get('cfop', 'N/A')}",
            f"Natureza Operação: {nota.get('natureza_operacao', 'N/A')}",
            f""
        ]
        
        # Adiciona itens
        if items:
            text_parts.append("ITENS DA NOTA:")
            for idx, item in enumerate(items, 1):
                text_parts.extend([
                    f"",
                    f"Item {idx}:",
                    f"  Descrição: {item.get('descricao_produto', 'N/A')}",
                    f"  NCM: {item.get('ncm', 'N/A')}",
                    f"  CFOP: {item.get('cfop', 'N/A')}",
                    f"  Quantidade: {item.get('quantidade', 0)}",
                    f"  Valor Unitário: R$ {item.get('valor_unitario', 0):.2f}",
                    f"  Valor Total: R$ {item.get('valor_total', 0):.2f}",
                    f"  Alíquota ICMS: {item.get('aliquota_icms', 0)}%",
                    f"  CST: {item.get('cst', 'N/A')}"
                ])
        
        return "\n".join(text_parts)
    
    def create_metadata(self, nota: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria metadados estruturados da nota.
        
        Args:
            nota: Dicionário com dados da nota fiscal
            
        Returns:
            Dicionário de metadados
        """
        items = nota.get('nota_fiscal_item', [])
        
        return {
            "type": "nota_fiscal",
            "numero_nota": nota.get('numero_nota'),
            "serie": nota.get('serie'),
            "data_emissao": nota.get('data_emissao'),
            "cnpj_emitente": nota.get('cnpj_emitente'),
            "nome_emitente": nota.get('nome_emitente'),
            "uf_emitente": nota.get('uf_emitente'),
            "cnpj_cpf_destinatario": nota.get('cnpj_cpf_destinatario'),
            "uf_destinatario": nota.get('uf_destinatario'),
            "valor_total": float(nota.get('valor_total', 0)),
            "cfop": nota.get('cfop'),
            "natureza_operacao": nota.get('natureza_operacao'),
            "num_items": len(items),
            "chave_acesso": nota.get('chave_acesso'),
            "processed_at": datetime.now().isoformat()
        }
    
    def generate_and_store_embeddings(
        self, 
        nota: Dict[str, Any]
    ) -> bool:
        """
        Gera embeddings e armazena no banco.
        
        Args:
            nota: Dicionário com dados da nota fiscal
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Cria representação textual
            text = self.create_nota_text_representation(nota)
            metadata = self.create_metadata(nota)
            
            # Split em chunks se necessário
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                chunks = [text]
            
            logger.info(f"Nota {nota.get('numero_nota')}: {len(chunks)} chunk(s) criado(s)")
            
            # Para cada chunk, gera embedding e armazena
            for chunk_idx, chunk_text in enumerate(chunks):
                # Gera embedding
                embedding_vector = self.embeddings_model.embed_query(chunk_text)
                
                # Metadados do chunk
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = chunk_idx
                chunk_metadata['total_chunks'] = len(chunks)
                
                # Insere diretamente usando psycopg (evita cache do Supabase REST API)
                dsn = build_db_dsn()
                with psycopg.connect(dsn) as conn:
                    with conn.cursor() as cur:
                        embedding_id = str(uuid.uuid4())
                        
                        # Insere na tabela embeddings
                        cur.execute("""
                            INSERT INTO embeddings (id, chunk_text, embedding, metadata)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            embedding_id,
                            chunk_text,
                            str(embedding_vector),  # pgvector aceita array como string
                            json.dumps(chunk_metadata)
                        ))
                        
                        # Insere na tabela chunks
                        cur.execute("""
                            INSERT INTO chunks (source_id, content, metadata)
                            VALUES (%s, %s, %s)
                        """, (
                            embedding_id,
                            chunk_text,
                            json.dumps(chunk_metadata)
                        ))
                        
                        # Insere na tabela metadata
                        cur.execute("""
                            INSERT INTO metadata (title, content, key, value, timestamp, source, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            f"Nota Fiscal {nota.get('numero_nota')}",
                            chunk_text[:500],
                            f"nfe_{nota.get('numero_nota')}_{chunk_idx}",
                            json.dumps(chunk_metadata),
                            datetime.now().isoformat(),
                            'nota_fiscal_table',
                            json.dumps(chunk_metadata)
                        ))
                        
                        conn.commit()
            
            logger.info(f"✓ Nota {nota.get('numero_nota')}: embeddings gerados e armazenados")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar nota {nota.get('numero_nota', 'UNKNOWN')}: {e}", exc_info=True)
            return False
    
    def process_all_notas(self, max_notas: int = None) -> Dict[str, int]:
        """
        Processa todas as notas do banco gerando embeddings.
        
        Args:
            max_notas: Número máximo de notas a processar (None = todas)
            
        Returns:
            Dicionário com estatísticas do processamento
        """
        stats = {
            'total_processed': 0,
            'success': 0,
            'errors': 0,
            'total_time': 0
        }
        
        start_time = datetime.now()
        offset = 0
        
        logger.info(f"Iniciando processamento de notas fiscais (max={max_notas or 'TODAS'})")
        
        while True:
            # Busca batch
            notas = self.fetch_notas_batch(offset=offset, limit=self.batch_size)
            
            if not notas:
                logger.info("Nenhuma nota restante para processar")
                break
            
            # Processa cada nota do batch
            for nota in notas:
                if max_notas and stats['total_processed'] >= max_notas:
                    logger.info(f"Limite de {max_notas} notas atingido")
                    break
                
                success = self.generate_and_store_embeddings(nota)
                
                stats['total_processed'] += 1
                if success:
                    stats['success'] += 1
                else:
                    stats['errors'] += 1
                
                # Log de progresso
                if stats['total_processed'] % 10 == 0:
                    logger.info(f"Progresso: {stats['total_processed']} notas processadas")
            
            if max_notas and stats['total_processed'] >= max_notas:
                break
            
            offset += self.batch_size
        
        end_time = datetime.now()
        stats['total_time'] = (end_time - start_time).total_seconds()
        
        logger.info(f"""
Processamento concluído:
  Total processado: {stats['total_processed']}
  Sucesso: {stats['success']}
  Erros: {stats['errors']}
  Tempo total: {stats['total_time']:.2f}s
  Tempo médio/nota: {stats['total_time']/stats['total_processed']:.2f}s
""")
        
        return stats


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera embeddings de notas fiscais')
    parser.add_argument('--max-notas', type=int, default=None,
                        help='Número máximo de notas a processar (padrão: todas)')
    parser.add_argument('--batch-size', type=int, default=100,
                        help='Tamanho do batch (padrão: 100)')
    parser.add_argument('--test', action='store_true',
                        help='Modo teste: processa apenas 5 notas')
    
    args = parser.parse_args()
    
    # Modo teste
    if args.test:
        logger.info("MODO TESTE: processando apenas 5 notas")
        max_notas = 5
    else:
        max_notas = args.max_notas
    
    # Cria gerador
    generator = NFeEmbeddingGenerator(batch_size=args.batch_size)
    
    # Processa notas
    stats = generator.process_all_notas(max_notas=max_notas)
    
    # Resultado final
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    print(f"Total processado: {stats['total_processed']}")
    print(f"Sucesso: {stats['success']}")
    print(f"Erros: {stats['errors']}")
    print(f"Taxa de sucesso: {stats['success']/stats['total_processed']*100:.1f}%")
    print(f"Tempo total: {stats['total_time']:.2f}s")
    print("="*60)


if __name__ == '__main__':
    main()
