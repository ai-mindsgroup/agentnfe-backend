"""Agente LLM usando Google Generative AI (Gemini)
===============================================

Este agente utiliza o Google Gemini para análises inteligentes e insights.
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
from src.settings import GOOGLE_API_KEY
from src.utils.logging_config import get_logger

# Import condicional do sistema RAG
try:
    from src.embeddings.vector_store import VectorStore
    from src.embeddings.generator import EmbeddingGenerator, EmbeddingProvider
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    VectorStore = None
    EmbeddingGenerator = None

# Import condicional do Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    genai = None

logger = get_logger(__name__)


@dataclass
class LLMRequest:
    """Request para o LLM."""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    temperature: float = 0.3
    max_tokens: int = 1000
    system_prompt: Optional[str] = None


@dataclass 
class LLMResponse:
    """Resposta do LLM."""
    content: str
    usage: Dict[str, Any]
    model: str
    success: bool = True
    error: Optional[str] = None


class GoogleLLMAgent(BaseAgent):
    """Agente que utiliza Google Generative AI (Gemini) para análises inteligentes."""
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        super().__init__(
            name="google_llm",
            description="Agente LLM usando Google Gemini para análises inteligentes e insights"
        )
        
        self.model_name = model
        self.model = None
        
        # Verificar disponibilidade
        if not GOOGLE_AI_AVAILABLE:
            raise AgentError(
                self.name,
                "Google Generative AI não disponível. Execute: pip install google-generativeai"
            )
        
        if not GOOGLE_API_KEY:
            raise AgentError(
                self.name, 
                "GOOGLE_API_KEY não configurado. Configure em configs/.env"
            )
        
        # Inicializar sistema RAG se disponível
        self.rag_enabled = False
        self.vector_store = None
        self.embedding_generator = None
        
        if RAG_AVAILABLE:
            try:
                self.vector_store = VectorStore()
                self.embedding_generator = EmbeddingGenerator(EmbeddingProvider.SENTENCE_TRANSFORMER)
                self.rag_enabled = True
                self.logger.info("RAG integrado ao Google LLM Agent")
            except Exception as e:
                self.logger.warning(f"RAG não disponível: {e}")
        
        # Configurar e inicializar Google Gemini
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(model)
            self.logger.info(f"Google LLM inicializado: {model}")
            
        except Exception as e:
            raise AgentError(self.name, f"Erro na inicialização do Google LLM: {e}")
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Processa consulta usando busca RAG + Google Gemini (sistema híbrido).
        
        Fluxo:
        1. Se RAG disponível, busca consultas similares no banco vetorial
        2. Se encontrar resposta relevante, usa ela (cache inteligente)  
        3. Se não encontrar, chama Google Gemini
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
            
            # 2. GERAR NOVA RESPOSTA COM LLM
            self.logger.info("🤖 Gerando nova resposta com Google Gemini")
            
            # Preparar request
            llm_request = self._prepare_request(query, context)
            
            # Enviar para Google Gemini
            response = self._call_gemini(llm_request)
            
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
    
    def _prepare_request(self, query: str, context: Optional[Dict[str, Any]]) -> LLMRequest:
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
            full_prompt = f"{system_prompt}\n\nConsulta: {query}"
        
        return LLMRequest(
            prompt=full_prompt,
            context=context,
            temperature=0.3,  # Mais determinístico para análise de dados
            max_tokens=1000
        )
    
    def _call_gemini(self, request: LLMRequest) -> LLMResponse:
        """Chama Google Gemini API."""
        try:
            # Configurar parâmetros de geração
            generation_config = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
                "candidate_count": 1,
            }
            
            # Gerar resposta
            response = self.model.generate_content(
                request.prompt,
                generation_config=generation_config
            )
            
            # Extrair conteúdo
            content = response.text if response.text else "Sem resposta gerada"
            
            # Metadados de uso (Gemini não fornece tokens detalhados via API gratuita)
            usage = {
                "prompt_tokens": len(request.prompt.split()),  # Aproximado
                "completion_tokens": len(content.split()),     # Aproximado  
                "total_tokens": len(request.prompt.split()) + len(content.split())
            }
            
            return LLMResponse(
                content=content,
                usage=usage,
                model=self.model_name,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Erro na chamada Gemini: {e}")
            return LLMResponse(
                content=f"Erro na geração: {str(e)}",
                usage={},
                model=self.model_name,
                success=False,
                error=str(e)
            )
    
    def analyze_data_insights(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa dados e gera insights inteligentes."""
        
        # Construir prompt especializado para análise de dados
        prompt = f"""Analise os seguintes dados e forneça insights estratégicos:

RESUMO DOS DADOS:
{json.dumps(data_summary, indent=2, ensure_ascii=False)}

Por favor, forneça:
1. **Principais Descobertas**: 3-5 insights mais importantes
2. **Padrões Identificados**: Tendências ou correlações relevantes  
3. **Riscos Potenciais**: Possíveis problemas ou anomalias
4. **Recomendações**: 3-5 ações estratégicas específicas
5. **Próximos Passos**: Sugestões para análises adicionais

Formato: Use markdown para estruturar a resposta de forma clara."""
        
        context = {"analysis_type": "data_insights", "data_summary": data_summary}
        
        return self.process(prompt, context)
    
    def explain_correlations(self, correlation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explica correlações de forma acessível para negócios."""
        
        prompt = f"""Explique as correlações nos dados de forma acessível para stakeholders de negócio:

CORRELAÇÕES ENCONTRADAS:
{json.dumps(correlation_data, indent=2, ensure_ascii=False)}

Explique:
1. **O que significam** essas correlações em termos práticos
2. **Implicações de negócio** de cada correlação importante
3. **Oportunidades** identificadas através das correlações
4. **Riscos** potenciais revelados pelos dados
5. **Ações recomendadas** baseadas nessas descobertas

Use linguagem acessível e evite jargão estatístico excessivo."""
        
        context = {"analysis_type": "correlation_analysis", "correlation_data": correlation_data}
        
        return self.process(prompt, context)

    def _search_cached_response(self, query: str, similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """Busca respostas similares no cache vetorial.
        
        Args:
            query: Consulta para buscar
            similarity_threshold: Limite mínimo de similaridade (0-1)
            
        Returns:
            Resposta em cache se encontrada, senão None
        """
        if not self.rag_enabled:
            return None
            
        try:
            # Gerar embedding da consulta
            query_result = self.embedding_generator.generate_embedding(query)
            query_embedding = query_result.embedding  # Extrair lista de floats
            
            # Buscar consultas similares
            results = self.vector_store.search_similar(
                query_embedding=query_embedding,
                limit=1,
                similarity_threshold=similarity_threshold
            )
            
            if results and len(results) > 0:
                best_match = results[0]
                self.logger.info(f"🎯 Cache hit! Similaridade: {best_match.similarity_score:.3f}")
                
                return {
                    "content": best_match.metadata.get("response", ""),
                    "similarity": best_match.similarity_score,
                    "original_query": best_match.chunk_text
                }
                
        except Exception as e:
            self.logger.warning(f"Erro na busca de cache: {e}")
            
        return None
    
    def _save_to_vector_store(self, query: str, response: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Salva consulta e resposta no banco vetorial para cache futuro com metadata enriquecido.
        
        Args:
            query: Consulta original
            response: Resposta do LLM
            context: Contexto adicional
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        if not self.rag_enabled:
            return False
            
        try:
            from datetime import datetime
            
            # Preparar metadados enriquecidos para busca contextual
            metadata = {
                "agent": self.name,
                "model": self.model_name,
                "response_content": response[:500],  # Truncar resposta longa
                "timestamp": datetime.now().isoformat(),
                "query_type": "llm_analysis",
                "embedding_type": "conversation",
                "session_id": getattr(self, '_current_session_id', None),
                "context_keys": list(context.keys()) if context else [],
            }
            
            # Adicionar contexto relevante se disponível
            if context:
                if "file_path" in context:
                    metadata["source_file"] = context["file_path"]
                if "data_info" in context:
                    metadata["data_dimensions"] = f"{context['data_info'].get('rows', 0)}x{context['data_info'].get('columns', 0)}"
                if "fraud_data" in context:
                    metadata["fraud_count"] = context["fraud_data"].get("count", 0)
            
            # Gerar e salvar embedding
            query_result = self.embedding_generator.generate_embedding(query)
            query_embedding = query_result.embedding  # Extrair lista de floats
            
            result = self.vector_store.store_embedding(
                query=query,
                response=response,
                embedding=query_embedding,
                metadata=metadata  # Passar metadata enriquecido
            )
            
            if result:
                self.logger.info(f"💾 Consulta salva no cache vetorial com metadata enriquecido: {list(metadata.keys())}")
                return True
            else:
                self.logger.warning("Falha ao salvar no cache vetorial")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar no cache: {e}")
            return False