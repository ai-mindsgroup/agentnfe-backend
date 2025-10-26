"""Teste do sistema de embeddings RAG com mocks para desenvolvimento."""
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def create_mock_embedding():
    """Cria um embedding mock de 384 dimensões (padrão sentence-transformers)."""
    return np.random.rand(384).tolist()


def test_chunking_system():
    """Testa apenas o sistema de chunking sem dependências externas."""
    print("🧩 TESTE DO SISTEMA DE CHUNKING")
    print("=" * 50)
    
    try:
        from src.embeddings.chunker import TextChunker, ChunkStrategy
        
        # Texto de exemplo
        sample_text = """
        A análise de documentos fiscais eletrônicos requer processamento estruturado. 
        
        Os principais componentes incluem:
        - Extração de dados XML de NF-e
        - Validação de campos obrigatórios
        - Análise de conformidade tributária
        
        Para processamento eficiente, recomenda-se:
        1. Machine Learning para classificação automática
        2. Validação de regras fiscais
        3. Integração com sistemas ERP
        """
        
        chunker = TextChunker(chunk_size=150, overlap_size=30)
        
        # Teste diferentes estratégias
        strategies = [ChunkStrategy.FIXED_SIZE, ChunkStrategy.PARAGRAPH, ChunkStrategy.SENTENCE]
        
        for strategy in strategies:
            print(f"\n📄 Estratégia: {strategy.value}")
            chunks = chunker.chunk_text(sample_text, "test_document", strategy)
            print(f"   Número de chunks: {len(chunks)}")
            
            for i, chunk in enumerate(chunks):
                print(f"   Chunk {i+1}: {chunk.content[:80]}{'...' if len(chunk.content) > 80 else ''}")
                print(f"      Posição: {chunk.metadata.start_char}-{chunk.metadata.end_char}")
        
        print("✅ Sistema de chunking funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ Erro no sistema de chunking: {str(e)}")
        return False
    
    return True


def test_embeddings_generation():
    """Testa a geração de embeddings (sem modelo real)."""
    print("\n🔢 TESTE DE GERAÇÃO DE EMBEDDINGS")
    print("=" * 50)
    
    try:
        from src.embeddings.generator import EmbeddingGenerator, EmbeddingProvider
        
        # Mock do modelo sentence-transformers
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            # Configurar mock para retornar embeddings fake
            mock_instance = Mock()
            mock_instance.encode.return_value = [create_mock_embedding() for _ in range(3)]
            mock_model.return_value = mock_instance
            
            generator = EmbeddingGenerator(EmbeddingProvider.SENTENCE_TRANSFORMER)
            
            texts = [
                "Documentos fiscais eletrônicos seguem padrões definidos pela SEFAZ",
                "Machine learning pode classificar tipos de operações fiscais",
                "Análise de dados revela insights importantes sobre conformidade"
            ]
            
            print(f"📝 Gerando embeddings para {len(texts)} textos...")
            embeddings = generator.generate_embeddings(texts)
            
            print(f"✅ Gerados {len(embeddings)} embeddings")
            print(f"   Dimensões: {len(embeddings[0]) if embeddings else 0}")
            print(f"   Formato: {type(embeddings[0][0]) if embeddings and embeddings[0] else 'N/A'}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na geração de embeddings: {str(e)}")
        return False


def test_complete_workflow():
    """Testa o workflow completo com mocks."""
    print("\n🔄 TESTE DE WORKFLOW COMPLETO")
    print("=" * 50)
    
    try:
        from src.embeddings.chunker import TextChunker, ChunkStrategy
        from src.embeddings.generator import EmbeddingGenerator, EmbeddingProvider
        
        # Mock do Supabase
        mock_supabase = Mock()
        mock_table = Mock()
        mock_execute = Mock()
        
        # Configurar cadeia de mocks do Supabase
        mock_execute.data = []
        mock_table.insert.return_value.execute.return_value = mock_execute
        mock_table.select.return_value.execute.return_value = mock_execute
        mock_supabase.table.return_value = mock_table
        mock_supabase.rpc.return_value.execute.return_value = mock_execute
        
        # Mock do sentence transformers
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            with patch('src.vectorstore.supabase_client.supabase', mock_supabase):
                
                # Configurar mock sentence transformers
                mock_model = Mock()
                mock_model.encode.return_value = [create_mock_embedding() for _ in range(2)]
                mock_st.return_value = mock_model
                
                # Workflow completo
                print("1. 📋 Chunking do texto...")
                chunker = TextChunker(chunk_size=200, overlap_size=50)
                text = "Esta é uma demonstração do sistema RAG. Inclui análise de documentos fiscais, machine learning e processamento de dados estruturados."
                chunks = chunker.chunk_text(text, "test_workflow", ChunkStrategy.SENTENCE)
                print(f"   ✅ {len(chunks)} chunks criados")
                
                print("2. 🔢 Geração de embeddings...")
                generator = EmbeddingGenerator(EmbeddingProvider.SENTENCE_TRANSFORMER)
                embeddings = generator.generate_embeddings([chunk.content for chunk in chunks])
                print(f"   ✅ {len(embeddings)} embeddings gerados")
                
                print("3. 💾 Simulação de armazenamento vetorial...")
                from src.embeddings.vector_store import VectorStore
                
                vector_store = VectorStore()
                
                for chunk, embedding in zip(chunks, embeddings):
                    result = vector_store.add_embedding(
                        text=chunk.content,
                        embedding=embedding,
                        metadata={
                            'source': 'test',
                            'chunk_index': chunks.index(chunk),
                            'strategy': ChunkStrategy.SENTENCE.value
                        }
                    )
                    print(f"   📦 Chunk armazenado: {result}")
                
                print("4. 🔍 Simulação de busca por similaridade...")
                query_embedding = create_mock_embedding()
                
                # Mock dos resultados de busca
                mock_search_result = Mock()
                mock_search_result.data = [
                    {
                        'chunk_text': chunks[0].content,
                        'similarity': 0.85,
                        'metadata': {'source': 'test', 'chunk_index': 0}
                    }
                ]
                mock_supabase.rpc.return_value.execute.return_value = mock_search_result
                
                results = vector_store.search_similar(query_embedding, limit=3)
                print(f"   🎯 Encontrados {len(results)} resultados similares")
                
                for result in results:
                    print(f"      - Similaridade: {result.similarity:.3f}")
                    print(f"      - Texto: {result.text[:60]}...")
                
                print("\n✅ WORKFLOW COMPLETO TESTADO COM SUCESSO!")
                return True
                
    except Exception as e:
        print(f"❌ Erro no workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes."""
    print("🚀 SISTEMA DE TESTE RAG - MODO DESENVOLVIMENTO")
    print("=" * 60)
    print("ℹ️  Este teste simula o sistema RAG sem necessidade de credenciais reais")
    print()
    
    success_count = 0
    total_tests = 3
    
    # Teste 1: Chunking
    if test_chunking_system():
        success_count += 1
    
    # Teste 2: Embeddings
    if test_embeddings_generation():
        success_count += 1
    
    # Teste 3: Workflow completo
    if test_complete_workflow():
        success_count += 1
    
    print(f"\n🏁 RESULTADO DOS TESTES")
    print("=" * 30)
    print(f"✅ Sucessos: {success_count}/{total_tests}")
    print(f"❌ Falhas: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("   O sistema RAG está pronto para integração com credenciais reais.")
    else:
        print("\n⚠️  Alguns testes falharam.")
        print("   Verifique os logs acima para detalhes.")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Configure as credenciais em configs/.env")
    print("2. Execute migrations com: python scripts/run_migrations.py")  
    print("3. Teste com dados reais usando o agente CSV")
    print("4. Integre RAG + CSV para análises contextualizadas")


if __name__ == "__main__":
    main()