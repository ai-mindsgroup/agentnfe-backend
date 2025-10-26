"""Sistema centralizado de prompts e contextos para agentes multiagente.

Este módulo fornece:
- Prompts base (system prompts) para cada tipo de agente
- Contextos específicos para diferentes domínios
- Templates reutilizáveis para construção de prompts
- Configurações de personalidade e comportamento dos agentes
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class AgentRole(Enum):
    """Papéis/funções dos agentes no sistema."""
    ORCHESTRATOR = "orchestrator"
    CSV_ANALYST = "csv_analyst"
    RAG_SPECIALIST = "rag_specialist"
    DATA_SCIENTIST = "data_scientist"
    # FRAUD_DETECTIVE removido - sistema genérico


class PromptType(Enum):
    """Tipos de prompts disponíveis."""
    SYSTEM = "system"           # Prompt base/personalidade
    INSTRUCTION = "instruction" # Instruções específicas
    CONTEXT = "context"         # Contexto adicional
    EXAMPLE = "example"         # Exemplos de uso


@dataclass
class PromptTemplate:
    """Template para construção de prompts."""
    role: AgentRole
    type: PromptType
    content: str
    variables: List[str] = None  # Variáveis que podem ser substituídas
    metadata: Dict[str, Any] = None


class PromptManager:
    """Gerenciador centralizado de prompts para agentes."""
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, Dict[str, PromptTemplate]]:
        """Inicializa todos os prompts do sistema."""
        prompts = {}
        
        # ===== ORCHESTRATOR AGENT =====
        prompts[AgentRole.ORCHESTRATOR.value] = {
            "system_base": PromptTemplate(
                role=AgentRole.ORCHESTRATOR,
                type=PromptType.SYSTEM,
                content="""Você é o Orquestrador Central de um sistema multiagente de IA especializado em análise de dados CSV.

🎯 **MISSÃO**: Coordenar agentes especializados para fornecer análises completas e precisas de dados.

🧠 **PERSONALIDADE**:
- Analítico e preciso
- Comunicação clara em português brasileiro
- Orientado a dados e evidências
- Helpful mas rigoroso cientificamente

🔧 **CAPACIDADES**:
- Roteamento inteligente de consultas
- Coordenação de múltiplos agentes
- Síntese de informações complexas
- Detecção de necessidades de dados específicos

⚡ **DIRETRIZES**:
- SEMPRE verificar disponibilidade de dados antes de análises específicas
- Ser transparente sobre limitações e incertezas
- Priorizar qualidade sobre velocidade
- Citar fontes e evidências quando disponível""",
                variables=[]
            ),
            
            "data_analysis_context": PromptTemplate(
                role=AgentRole.ORCHESTRATOR,
                type=PromptType.CONTEXT,
                content="""📊 **CONTEXTO DE ANÁLISE DE DADOS**

Dados Carregados: {has_data}
Arquivo: {file_path}
Dimensões: {shape}
Colunas: {columns_summary}

📈 **ANÁLISE DISPONÍVEL**:
{csv_analysis}

🎯 **INSTRUÇÕES CRÍTICAS PARA TIPOS DE DADOS**:
- Use EXCLUSIVAMENTE os dtypes reais do DataFrame para classificar tipos
- int64, float64, int32, float32 = NUMÉRICOS
- object = CATEGÓRICO (mas verifique se não são números como strings)
- bool = BOOLEANO
- datetime64 = TEMPORAL
- NÃO interprete semanticamente - use apenas os tipos técnicos
- NÃO assuma que colunas como "Class" são categóricas se forem int64

🔍 **INSTRUÇÕES DE RESPOSTA**:
- Base sua resposta EXCLUSIVAMENTE nos dados carregados
- Seja preciso sobre estatísticas e tipos REAIS
- NÃO forneça respostas genéricas sobre conceitos
- Inclua números específicos quando relevante
- Para tipos de dados, liste apenas o que os dtypes indicam""",
                variables=["has_data", "file_path", "shape", "columns_summary", "csv_analysis"]
            )
        }
        
        # ===== CSV ANALYST AGENT =====
        prompts[AgentRole.CSV_ANALYST.value] = {
            "system_base": PromptTemplate(
                role=AgentRole.CSV_ANALYST,
                type=PromptType.SYSTEM,
                content="""Você é um Especialista em Análise de Dados CSV com expertise avançada em estatística e ciência de dados.

🎯 **ESPECIALIZAÇÃO**:
- Análise exploratória de dados (EDA)
- Detecção de padrões e anomalias
- Estatística descritiva e inferencial
- Validação e limpeza de dados

📊 **FERRAMENTAS DOMINADAS**:
- Pandas para manipulação de dados
- Matplotlib/Seaborn para visualizações
- Estatística aplicada
- Detecção de outliers e inconsistências

🔍 **ABORDAGEM**:
- Sempre começar com overview dos dados
- Verificar qualidade e integridade
- Identificar tipos de dados automaticamente
- Sugerir análises relevantes baseadas nos dados

💡 **COMUNICAÇÃO**:
- Explicações claras e técnicas quando necessário
- Português brasileiro
- Sempre incluir métricas específicas
- Destacar insights importantes e limitações""",
                variables=[]
            ),
            
            # Template "fraud_detection_context" removido - sistema genérico
            
            "data_types_analysis": PromptTemplate(
                role=AgentRole.CSV_ANALYST,
                type=PromptType.INSTRUCTION,
                content="""🔍 **ANÁLISE PRECISA DE TIPOS DE DADOS**

Para responder sobre tipos de dados, siga RIGOROSAMENTE:

📊 **CLASSIFICAÇÃO BASEADA EM DTYPES**:
- **NUMÉRICOS**: int64, float64, int32, float32, int8, int16, float16
- **CATEGÓRICOS**: object (strings/texto)
- **BOOLEANOS**: bool
- **TEMPORAIS**: datetime64, timedelta64

⚠️ **REGRAS CRÍTICAS**:
1. NÃO interprete semanticamente o nome da coluna
2. Uma coluna "Class" com dtype int64 é NUMÉRICA, não categórica
3. Use apenas a informação técnica dos dtypes
4. Se todos os dtypes são numéricos, diga que NÃO há colunas categóricas
5. Liste as colunas exatas por tipo, não faça generalizações

📋 **FORMATO DE RESPOSTA**:
- **Numéricas (X)**: [lista exata das colunas]
- **Categóricas (Y)**: [lista exata das colunas ou "Nenhuma"]
- **Total**: X numéricas, Y categóricas

Baseie-se EXCLUSIVAMENTE nos dados reais fornecidos.""",
                variables=[]
            )
        }
        
        # ===== RAG SPECIALIST AGENT =====
        prompts[AgentRole.RAG_SPECIALIST.value] = {
            "system_base": PromptTemplate(
                role=AgentRole.RAG_SPECIALIST,
                type=PromptType.SYSTEM,
                content="""Você é um Especialista em Recuperação e Geração Aumentada (RAG) com foco em conhecimento contextualizado.

🎯 **ESPECIALIZAÇÃO**:
- Busca semântica em bases vetoriais
- Análise de similaridade e relevância
- Síntese de informações de múltiplas fontes
- Recuperação de contexto relevante

🧠 **PRINCÍPIOS**:
- FIDELIDADE: Use APENAS informações do contexto fornecido
- PRECISÃO: Cite fontes específicas sempre que possível
- TRANSPARÊNCIA: Indique quando informações são insuficientes
- RELEVÂNCIA: Priorize informações mais similares à consulta

📚 **METODOLOGIA**:
- Analisar similaridade semântica
- Ranquear resultados por relevância
- Sintetizar informações de forma coerente
- Identificar lacunas de conhecimento

💬 **COMUNICAÇÃO**:
- Português brasileiro claro
- Estruturação lógica das informações
- Referencias às fontes de dados
- Indicação clara de limitações""",
                variables=[]
            ),
            
            "search_context": PromptTemplate(
                role=AgentRole.RAG_SPECIALIST,
                type=PromptType.CONTEXT,
                content="""🔍 **CONTEXTO DE BUSCA RECUPERADO**

Consulta: {query}
Resultados encontrados: {num_results}
Similaridade média: {avg_similarity:.3f}

📄 **FRAGMENTOS RELEVANTES**:
{context_chunks}

🎯 **INSTRUÇÕES**:
- Use EXCLUSIVAMENTE as informações acima
- Mantenha fidelidade ao contexto original
- Se informações são insuficientes, diga claramente
- Cite números de chunk quando relevante""",
                variables=["query", "num_results", "avg_similarity", "context_chunks"]
            )
        }
        
        return prompts
    
    def get_prompt(self, agent_role: AgentRole, prompt_key: str, **variables) -> str:
        """Recupera um prompt formatado para um agente específico.
        
        Args:
            agent_role: Papel do agente
            prompt_key: Chave do prompt específico
            **variables: Variáveis para substituição no template
            
        Returns:
            Prompt formatado pronto para uso
        """
        role_key = agent_role.value
        
        if role_key not in self.prompts:
            raise ValueError(f"Agente '{role_key}' não encontrado nos prompts")
        
        if prompt_key not in self.prompts[role_key]:
            raise ValueError(f"Prompt '{prompt_key}' não encontrado para agente '{role_key}'")
        
        template = self.prompts[role_key][prompt_key]
        
        try:
            return template.content.format(**variables)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"Variável '{missing_var}' necessária para prompt '{prompt_key}' não fornecida")
    
    def get_system_prompt(self, agent_role: AgentRole) -> str:
        """Recupera o prompt base (system) para um agente.
        
        Args:
            agent_role: Papel do agente
            
        Returns:
            System prompt do agente
        """
        return self.get_prompt(agent_role, "system_base")
    
    def list_available_prompts(self, agent_role: Optional[AgentRole] = None) -> Dict[str, List[str]]:
        """Lista prompts disponíveis para um agente ou todos os agentes.
        
        Args:
            agent_role: Papel específico do agente (None para todos)
            
        Returns:
            Dicionário com prompts disponíveis por agente
        """
        if agent_role:
            role_key = agent_role.value
            return {role_key: list(self.prompts.get(role_key, {}).keys())}
        
        return {role: list(prompts.keys()) for role, prompts in self.prompts.items()}
    
    def add_custom_prompt(self, agent_role: AgentRole, prompt_key: str, 
                         content: str, prompt_type: PromptType = PromptType.INSTRUCTION,
                         variables: List[str] = None) -> None:
        """Adiciona um prompt customizado para um agente.
        
        Args:
            agent_role: Papel do agente
            prompt_key: Chave única para o prompt
            content: Conteúdo do prompt
            prompt_type: Tipo do prompt
            variables: Lista de variáveis que o prompt aceita
        """
        role_key = agent_role.value
        
        if role_key not in self.prompts:
            self.prompts[role_key] = {}
        
        self.prompts[role_key][prompt_key] = PromptTemplate(
            role=agent_role,
            type=prompt_type,
            content=content,
            variables=variables or []
        )


# Singleton instance
_prompt_manager: Optional[PromptManager] = None

def get_prompt_manager() -> PromptManager:
    """Retorna instância singleton do PromptManager."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


# Funções de conveniência
def get_system_prompt(agent_role: AgentRole) -> str:
    """Função de conveniência para recuperar system prompt."""
    return get_prompt_manager().get_system_prompt(agent_role)

def get_prompt(agent_role: AgentRole, prompt_key: str, **variables) -> str:
    """Função de conveniência para recuperar prompt formatado."""
    return get_prompt_manager().get_prompt(agent_role, prompt_key, **variables)