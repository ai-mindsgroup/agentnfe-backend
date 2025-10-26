"""Agente LLM usando Groq
=======================

Este agente utiliza a API do Groq para análises inteligentes e insights.
Integra com o sistema multiagente para fornecer capacidades avançadas de NLP.
"""

from __future__ import annotations
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from typing import Dict, Any, Optional, List
import json
from dataclasses import dataclass

from src.agent.base_agent import BaseAgent, AgentError
from src.settings import GROQ_API_KEY
from src.utils.logging_config import get_logger

# Import da biblioteca oficial do Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

# Import condicional do sistema RAG
try:
    from src.embeddings.vector_store import VectorStore
    from src.embeddings.generator import EmbeddingGenerator, EmbeddingProvider
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    VectorStore = None
    EmbeddingGenerator = None

logger = get_logger(__name__)


@dataclass
class GroqRequest:
    """Request para o Groq."""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    temperature: float = 0.3
    max_tokens: int = 1000
    system_prompt: Optional[str] = None


@dataclass 
class GroqResponse:
    """Resposta do Groq."""
    content: str
    usage: Dict[str, Any]
    model: str
    success: bool = True
    error: Optional[str] = None


class GroqLLMAgent(BaseAgent):
    """Agente que utiliza Groq para análises inteligentes."""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        super().__init__(
            name="groq_llm",
            description="Agente LLM usando Groq para análises inteligentes e insights"
        )
        
        self.model_name = model
        
        # Verificar disponibilidade da biblioteca
        if not GROQ_AVAILABLE:
            raise AgentError(
                self.name,
                "Biblioteca groq não instalada. Execute: pip install groq"
            )
        
        # Verificar API key
        if not GROQ_API_KEY:
            raise AgentError(
                self.name, 
                "GROQ_API_KEY não configurado. Configure em configs/.env"
            )
        
        # Inicializar cliente Groq
        try:
            self.client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            raise AgentError(self.name, f"Erro ao inicializar cliente Groq: {e}")
        
        # Inicializar sistema RAG se disponível
        self.rag_enabled = False
        self.vector_store = None
        self.embedding_generator = None
        
        if RAG_AVAILABLE:
            try:
                self.vector_store = VectorStore()
                self.embedding_generator = EmbeddingGenerator(EmbeddingProvider.SENTENCE_TRANSFORMER)
                self.rag_enabled = True
                self.logger.info("RAG integrado ao Groq LLM Agent")
            except Exception as e:
                self.logger.warning(f"RAG não disponível: {e}")
        
        self.logger.info(f"Groq LLM inicializado: {model}")

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Processa consulta usando busca RAG + Groq (sistema híbrido).
        
        Fluxo:
        1. Se RAG disponível, busca consultas similares no banco vetorial
        2. Se encontrar resposta relevante, usa ela (cache inteligente)  
        3. Se não encontrar, chama Groq
        4. Salva consulta + resposta LLM no banco vetorial
        
        Args:
            query: Consulta/prompt para o LLM
            context: Contexto adicional (dados, configurações, etc.)
            
        Returns:
            Resposta estruturada do LLM ou cache
        """
        try:
            # 1. BUSCAR NO CACHE VETORIAL (se disponível)
            if self.rag_enabled:
                cached_response = self._search_cached_response(query)
                if cached_response:
                    self.logger.info("💾 Usando resposta em cache (RAG)")
                    return self._build_response(
                        cached_response["content"],
                        metadata={
                            "model": "cache_rag", 
                            "llm_used": False,
                            "cache_used": True,
                            "similarity_score": cached_response.get("similarity", 0.0),
                            "success": True
                        }
                    )
            
            # 2. GERAR NOVA RESPOSTA COM GROQ
            self.logger.info("🚀 Gerando nova resposta com Groq")
            
            # Preparar request
            groq_request = self._prepare_request(query, context)
            
            # Enviar para Groq
            response = self._call_groq(groq_request)
            
            # 3. SALVAR NO BANCO VETORIAL (se disponível)
            if self.rag_enabled and response.success:
                self._save_to_vector_store(query, response.content, context)
            
            # Processar resposta
            return self._build_response(
                response.content,
                metadata={
                    "model": response.model,
                    "usage": response.usage,
                    "llm_used": True,
                    "cache_used": False,
                    "success": response.success
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro no processamento LLM híbrido: {e}")
            return self._build_response(
                f"Erro no processamento: {str(e)}",
                metadata={"error": True, "llm_used": False, "cache_used": False}
            )

    def _prepare_request(self, query: str, context: Optional[Dict[str, Any]]) -> GroqRequest:
        """Prepara request para o LLM com contexto e system prompt."""
        
        # System prompt para análise de dados (genérico para múltiplos domínios)
        system_prompt = """Você é um especialista em análise de dados e insights de negócio.
        
Suas responsabilidades:
- Analisar dados CSV e identificar padrões
- Detectar anomalias e outliers nos dados
- Fornecer insights estratégicos baseados em dados
- Explicar correlações e tendências
- Sugerir ações para melhorar processos

Diretrizes:
- Seja preciso e baseie-se nos dados fornecidos
- Use linguagem técnica mas acessível
- Destaque descobertas importantes
- Forneça recomendações práticas
- Seja conciso mas completo
"""
        
        # Construir prompt com contexto
        if context:
            prompt_parts = [system_prompt, "\nContexto dos dados:"]
            
            # Adicionar informações do contexto
            if "file_path" in context:
                prompt_parts.append(f"Arquivo: {context['file_path']}")
            
            if "data_info" in context:
                data_info = context["data_info"]
                prompt_parts.append(f"Dimensões: {data_info.get('rows', 'N/A')} linhas × {data_info.get('columns', 'N/A')} colunas")
            
            # Adicionar consulta do usuário
            prompt_parts.extend(["\nConsulta do usuário:", query])
            
            full_prompt = "\n".join(prompt_parts)
        else:
            full_prompt = f"{system_prompt}\n\nConsulta do usuário:\n{query}"
        
        return GroqRequest(
            prompt=full_prompt,
            context=context,
            system_prompt=system_prompt
        )

    def _call_groq(self, request: GroqRequest) -> GroqResponse:
        """Chama a API do Groq usando a biblioteca oficial."""
        try:
            # Preparar mensagens para o chat completion
            messages = [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.prompt}
            ]
            
            # Fazer chamada para o Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            
            # Extrair resposta
            content = chat_completion.choices[0].message.content
            
            # Construir resposta estruturada
            usage = {
                "prompt_tokens": chat_completion.usage.prompt_tokens if chat_completion.usage else 0,
                "completion_tokens": chat_completion.usage.completion_tokens if chat_completion.usage else 0,
                "total_tokens": chat_completion.usage.total_tokens if chat_completion.usage else 0,
            }
            
            return GroqResponse(
                content=content,
                usage=usage,
                model=self.model_name,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Erro na chamada do Groq: {e}")
            return GroqResponse(
                content="",
                usage={},
                model=self.model_name,
                success=False,
                error=str(e)
            )

    def _search_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """Busca resposta similar no banco vetorial (cache inteligente)."""
        if not self.rag_enabled:
            return None
            
        try:
            # Gerar embedding da consulta
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Buscar respostas similares
            results = self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=1,
                similarity_threshold=0.85  # Similaridade alta para cache
            )
            
            if results:
                return results[0]
                
        except Exception as e:
            self.logger.warning(f"Erro na busca RAG: {e}")
            
        return None

    def _save_to_vector_store(self, query: str, response: str, context: Optional[Dict[str, Any]]):
        """Salva consulta e resposta no banco vetorial com metadata enriquecido."""
        if not self.rag_enabled:
            return
            
        try:
            from datetime import datetime
            
            # Preparar dados para salvar
            combined_text = f"Consulta: {query}\nResposta: {response}"
            embedding = self.embedding_generator.generate_embedding(combined_text)
            
            # Metadados enriquecidos para contexto de busca
            metadata = {
                "query": query,
                "response": response[:500],  # Truncar resposta longa
                "model": self.model_name,
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
                "query_type": "llm_analysis",
                "embedding_type": "conversation",
                "session_id": getattr(self, '_current_session_id', None),
            }
            
            # Adicionar contexto relevante se disponível
            if context:
                if "file_path" in context:
                    metadata["source_file"] = context["file_path"]
                if "data_info" in context:
                    metadata["data_dimensions"] = f"{context['data_info'].get('rows', 0)}x{context['data_info'].get('columns', 0)}"
                if "fraud_data" in context:
                    metadata["fraud_count"] = context["fraud_data"].get("count", 0)
                
                # Adicionar palavras-chave do contexto para facilitar busca
                metadata["context_keys"] = list(context.keys())
            
            # Salvar no banco vetorial
            self.vector_store.add_document(
                text=combined_text,
                embedding=embedding,
                metadata=metadata
            )
            
            self.logger.debug(f"Resposta salva no banco vetorial com metadata enriquecido: {list(metadata.keys())}")
            
        except Exception as e:
            self.logger.warning(f"Erro ao salvar no banco vetorial: {e}")

    def _build_response(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói resposta padronizada do agente."""
        return {
            "agent": self.name,
            "content": content,
            "success": metadata.get("success", True),
            "metadata": metadata,
            "type": "llm_response"
        }

    # Métodos especializados para diferentes tipos de análise
    
    def analyze_data_insights(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa dados e gera insights específicos."""
        query = f"""
        Analise os seguintes dados e forneça insights detalhados:
        
        Resumo dos dados:
        {json.dumps(data_summary, indent=2, ensure_ascii=False)}
        
        Forneça:
        1. Principais padrões identificados
        2. Anomalias ou outliers importantes
        3. Correlações relevantes
        4. Recomendações baseadas nos dados
        """
        
        return self.process(query, {"data_summary": data_summary})

    def explain_correlations(self, correlation_matrix: Dict[str, Any]) -> Dict[str, Any]:
        """Explica correlações encontradas nos dados."""
        query = f"""
        Explique as correlações encontradas na matriz de correlação:
        
        Matriz de correlação:
        {json.dumps(correlation_matrix, indent=2, ensure_ascii=False)}
        
        Explique:
        1. Correlações mais significativas
        2. Implicações práticas
        3. Possíveis relações causais
        4. Recomendações baseadas nas correlações
        """
        
        return self.process(query, {"correlation_matrix": correlation_matrix})

    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponíveis no Groq."""
        return [
            "llama-3.3-70b-versatile",  # Modelo principal recomendado
            "llama-3.1-8b-instant",     # Modelo rápido
            "meta-llama/llama-guard-4-12b",  # Modelo de moderação
            "openai/gpt-oss-120b",      # Modelo experimental
            "openai/gpt-oss-20b"        # Modelo experimental menor
        ]

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo atual."""
        return {
            "model": self.model_name,
            "provider": "Groq",
            "capabilities": [
                "text_generation",
                "data_analysis", 
                "fraud_detection",
                "pattern_recognition",
                "insight_generation"
            ],
            "rag_enabled": self.rag_enabled,
            "api_base": "https://api.groq.com"
        }