# 🚨 AUDITORIA CRÍTICA DE GUARDRAILS - Sistema EDA AI Minds

**Data:** 2025-11-06  
**Analista:** GitHub Copilot  
**Severidade:** 🔴 CRÍTICA - Violações de Segurança e Privacidade Detectadas

---

## 📋 RESUMO EXECUTIVO

O sistema apresenta **MÚLTIPLAS VIOLAÇÕES** dos guardrails de segurança definidos, permitindo:
1. ❌ Exposição de nomes de tabelas internas (`embeddings`, `agent_context`)
2. ❌ Exposição de estrutura técnica de banco de dados
3. ❌ Respostas extremamente longas (>500 palavras quando deveria ser 2-4 parágrafos curtos)
4. ❌ Informações técnicas não solicitadas pelo usuário
5. ❌ Falha em proteger metadados do sistema

---

## 🔍 ANÁLISE DETALHADA

### 1. RESPOSTA PROBLEMÁTICA ANALISADA

**Pergunta do Usuário:** "Sobre o que é o dataset?"

**Resposta Gerada (Resumo das Violações):**
```
"O dataset fornecido é um conjunto de dados estruturados, representado por um 
DataFrame, que foi reconstruído a partir da coluna `chunk_text` da tabela 
`embeddings`. As estatísticas fornecidas refletem os dados reais, não a estrutura 
da tabela `embeddings`."
```

**Problemas Identificados:**
- ❌ Mencionou explicitamente `tabela embeddings`
- ❌ Mencionou campo `chunk_text`
- ❌ Expôs arquitetura interna (DataFrame reconstruído)
- ❌ Resposta com >300 palavras (deveria ser 2-4 parágrafos curtos)
- ❌ Listou "VARIÁVEIS NUMÉRICAS" e "VARIÁVEIS CATEGÓRICAS" vazias
- ❌ Forneceu estrutura técnica do sistema

---

### 2. GUARDRAILS VIOLADOS

#### ✅ Guardrails Definidos no `orchestrator_agent.py` (linhas 1571-1600):

```python
🛡️ GUARDRAILS OBRIGATÓRIOS (Segurança e Privacidade):
1) Somente leitura: não crie, altere, exclua ou atualize dados, tabelas, índices, 
   views ou arquivos.

2) Não revele informações sensíveis: NUNCA INFORME nomes de tabelas internas, 
   senhas, chaves de API, tokens, DSNs, strings de conexão, caminhos/paths de 
   arquivos, diretórios do sistema, variáveis de ambiente, IPs, provedores de 
   hospedagem, configurações do servidor ou detalhes do ambiente de desenvolvimento.

3) Não compartilhe dados confidenciais/pessoais; quando necessário, responda com 
   agregados ou exemplos genéricos.

6) Nunca finja executar ações de escrita (DELETE/INSERT/UPDATE/MIGRATE). Nunca 
   prometa alterar o banco ou arquivos.
```

**Status:** 🔴 VIOLADO - Guardrail #2 completamente ignorado

---

### 3. ORIGEM DO PROBLEMA

#### Arquivo: `src/agent/rag_data_agent.py`

**Linha 354-368: System Prompt SEM Guardrails**

```python
system_prompt = """
Você é um agente EDA especializado. Sua tarefa é apresentar resultados 
analíticos de forma clara e estruturada.

Você receberá:
1. Pergunta do usuário
2. Resultados de análises executadas (JSON estruturado)
3. Chunks analíticos do CSV (contexto adicional)
4. Histórico conversacional (se houver)

Sua resposta deve:
- Iniciar com: "Pergunta feita: [pergunta]"
- Apresentar resultados de forma humanizada e estruturada
- Usar tabelas Markdown quando apropriado
- Destacar insights relevantes
- Finalizar com: "Se precisar de mais detalhes, é só perguntar!"
"""
```

**Problemas:**
- ❌ ZERO menção a guardrails de segurança
- ❌ Não proíbe exposição de tabelas/campos
- ❌ Não limita tamanho de resposta
- ❌ Não instrui sobre proteção de metadados
- ❌ Permite resposta técnica sobre estrutura interna

---

### 4. ANÁLISE DO FLUXO DE ROTEAMENTO

**Classificação da Query:** "Sobre o que é o dataset?"

1. **orchestrator_agent.py** → `_classify_query()` → detecta `QueryType.CSV_ANALYSIS`
2. **orchestrator_agent.py** → `_handle_csv_analysis()` → delega para `RAGDataAgent`
3. **rag_data_agent.py** → `process()` → executa análise
4. **rag_data_agent.py** → `_synthesize_response()` (linha 350-410) → **FALHA AQUI**

**Ponto de Falha:** O `RAGDataAgent` NÃO recebe nem aplica os guardrails do `OrchestratorAgent`

---

### 5. VERIFICAÇÃO DE MIGRATIONS (Estrutura de Dados)

**Migration `0002_schema.sql` - Tabela embeddings:**

```sql
create table if not exists public.embeddings (
    id uuid primary key default gen_random_uuid(),
    chunk_text text not null,
    embedding vector(1536) not null,
    metadata jsonb default '{}'::jsonb,
    created_at timestamp with time zone default now()
);
```

**Observação:**
- ✅ A tabela `embeddings` é GENÉRICA (não específica para NFe)
- ✅ O campo `metadata` armazena informações do domínio (NFe, transações, etc)
- ⚠️ O sistema DEVE inferir o domínio via LLM analisando `metadata`, NÃO expor estrutura

---

### 6. MÉTODO `_get_dataset_info()` - ANÁLISE

**Localização:** `orchestrator_agent.py`, linhas 2008-2050

**Implementação Atual (Corrigida Anteriormente):**
```python
def _get_dataset_info(self) -> str:
    """Obtém informações sobre o dataset através da LLM, sem hardcode."""
    
    # Buscar amostra de metadata
    result = supabase.table('embeddings').select('metadata').limit(5).execute()
    
    # LLM analisa e descreve de forma segura
    prompt = f"""Analise esta amostra de metadados e descreva o tipo de dataset 
    de forma GENÉRICA e SEGURA.

    REGRAS OBRIGATÓRIAS:
    - NÃO mencione nomes de tabelas, campos, colunas ou arquivos
    - NÃO exponha estrutura técnica ou paths
    - Descreva apenas o DOMÍNIO/TEMA dos dados
    - Seja breve (máximo 1 frase)
    """
```

**Status:** ✅ CORRETO - Método protege estrutura via prompt para LLM

---

### 7. PROBLEMA CRÍTICO: `RAGDataAgent` IGNORA GUARDRAILS

#### System Prompts no RAGDataAgent:

**Prompt 1 (linha 354):** Sem guardrails  
**Prompt 2 (linha 440):** "Você é um agente EDA. Responda à pergunta usando os chunks fornecidos." - Sem guardrails  
**Prompt 3 (linha 1259):** Sem guardrails específicos de proteção

**Consequência:**
Quando `OrchestratorAgent` delega para `RAGDataAgent`, os guardrails NÃO são propagados.

---

## 🎯 RECOMENDAÇÕES CRÍTICAS

### ✅ AÇÃO IMEDIATA NECESSÁRIA

#### 1. **Adicionar Guardrails Globais ao RAGDataAgent**

Criar método centralizado que SEMPRE aplica guardrails:

```python
def _get_security_guardrails(self) -> str:
    """Retorna string de guardrails obrigatórios para TODOS os prompts."""
    return """
🛡️ GUARDRAILS OBRIGATÓRIOS:
- NUNCA mencione nomes de tabelas (embeddings, chunks, metadata, agent_*)
- NUNCA exponha campos/colunas do banco de dados
- NUNCA revele paths, configurações, estrutura técnica interna
- Respostas BREVES: 2-4 parágrafos curtos (máximo 200 palavras)
- EXCEÇÃO: análises estatísticas podem ser mais longas quando necessário
- Descreva domínio/tema dos dados de forma genérica
- Exemplo BOM: "Este dataset contém informações fiscais"
- Exemplo RUIM: "Tabela embeddings com campo chunk_text contém..."
"""
```

#### 2. **Refatorar TODOS os System Prompts**

Modificar `rag_data_agent.py` linhas 354, 440, 1259 para incluir:

```python
system_prompt = f"""
Você é um agente EDA especializado.

{self._get_security_guardrails()}

[... resto do prompt específico ...]
"""
```

#### 3. **Validação Pós-Geração (Guardrail Enforcement)**

Adicionar método de validação após LLM gerar resposta:

```python
def _validate_response_security(self, response: str) -> str:
    """Valida resposta e sanitiza exposições acidentais."""
    
    # Lista de termos proibidos
    forbidden_terms = [
        'embeddings', 'chunks', 'metadata', 'agent_sessions',
        'agent_conversations', 'agent_context', 'chunk_text',
        'embedding vector', 'supabase', 'postgres', 'tabela'
    ]
    
    # Detectar violações
    violations = [term for term in forbidden_terms if term.lower() in response.lower()]
    
    if violations:
        self.logger.error(f"🚨 VIOLAÇÃO DE GUARDRAILS: {violations}")
        # Forçar LLM a reescrever de forma genérica
        return self._regenerate_secure_response(response)
    
    return response
```

#### 4. **Limitar Tamanho de Resposta**

Adicionar validação de comprimento:

```python
def _enforce_response_length(self, response: str, max_words: int = 200) -> str:
    """Garante resposta breve conforme guardrails."""
    
    words = response.split()
    if len(words) > max_words:
        self.logger.warning(f"⚠️ Resposta muito longa: {len(words)} palavras (limite: {max_words})")
        # Truncar ou pedir LLM resumir
        return self._llm_summarize(response, max_words)
    
    return response
```

---

## 📊 MÉTRICAS DE SEGURANÇA

### Estado Atual (ANTES da Correção):

| Métrica | Status | Severidade |
|---------|--------|-----------|
| Exposição de tabelas | ❌ FALHA | 🔴 CRÍTICA |
| Exposição de campos | ❌ FALHA | 🔴 CRÍTICA |
| Tamanho de resposta | ❌ FALHA | 🟡 MÉDIA |
| Proteção de metadados | ❌ FALHA | 🔴 CRÍTICA |
| Propagação de guardrails | ❌ FALHA | 🔴 CRÍTICA |
| **Score Geral** | **20%** | 🔴 REPROVADO |

### Estado Esperado (APÓS Correção):

| Métrica | Status | Severidade |
|---------|--------|-----------|
| Exposição de tabelas | ✅ OK | 🟢 SEGURO |
| Exposição de campos | ✅ OK | 🟢 SEGURO |
| Tamanho de resposta | ✅ OK | 🟢 SEGURO |
| Proteção de metadados | ✅ OK | 🟢 SEGURO |
| Propagação de guardrails | ✅ OK | 🟢 SEGURO |
| **Score Geral** | **100%** | 🟢 APROVADO |

---

## 🔧 PLANO DE IMPLEMENTAÇÃO

### Fase 1: Correção Imediata (URGENTE)
- [ ] Adicionar `_get_security_guardrails()` ao `RAGDataAgent`
- [ ] Refatorar system prompts (linhas 354, 440, 1259)
- [ ] Adicionar validação pós-geração `_validate_response_security()`
- [ ] Implementar limite de tamanho `_enforce_response_length()`

### Fase 2: Testes e Validação
- [ ] Testar query: "Sobre o que é o dataset?"
- [ ] Validar que resposta NÃO menciona tabelas/campos
- [ ] Validar resposta breve (2-4 parágrafos)
- [ ] Testar outras queries que possam expor estrutura

### Fase 3: Documentação
- [ ] Atualizar documentação de segurança
- [ ] Criar guia de guardrails para novos agentes
- [ ] Adicionar testes automatizados de segurança

---

## 📝 CONCLUSÃO

**Situação Crítica Identificada:**
O sistema atual **NÃO GARANTE** a segurança dos dados conforme especificado nos guardrails. 

**Risco:**
Exposição de arquitetura interna, estrutura de banco de dados e metadados sensíveis.

**Ação Requerida:**
Implementação **IMEDIATA** das correções propostas antes de qualquer deploy em produção.

**Prioridade:** 🔴 CRÍTICA  
**Prazo Recomendado:** Implementar correções nas próximas 2 horas

---

**Responsável pela Auditoria:** GitHub Copilot  
**Data/Hora:** 2025-11-06 16:30:00 BRT
