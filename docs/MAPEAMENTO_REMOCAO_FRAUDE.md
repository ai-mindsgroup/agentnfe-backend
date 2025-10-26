# 🗺️ Mapeamento Completo - Remoção do Módulo de Fraude

**Data de Mapeamento:** 25 de Outubro de 2025  
**Status (FASE 1):** Remoções seguras de arquivos de exemplo e atualização de documentação realizadas em 2025-10-26. Alguns artefatos já estavam arquivados; próximos passos focam em refatoração de código.
**Objetivo:** Identificar todos os artefatos relacionados a detecção de fraude/creditcard para remoção sistemática

---

## 📊 Resumo Executivo

### Estatísticas do Mapeamento
- **Arquivos de dados:** 2 arquivos CSV identificados
- **Scripts:** 8 scripts específicos de fraude
- **Exemplos:** 5 arquivos de exemplo
- **Código fonte (src/):** ~100+ referências em múltiplos módulos
- **Testes:** ~50+ referências em arquivos de teste
- **Arquivos arquivados:** ~20+ arquivos no `.archive/`

### Categorização por Impacto
| Categoria | Impacto | Ação Recomendada |
|-----------|---------|------------------|
| Dados CSV | Baixo | ✅ Remover diretamente |
| Scripts específicos | Baixo | ✅ Remover diretamente |
| Exemplos | Baixo | ✅ Remover diretamente |
| Código-fonte (src/) | **ALTO** | ⚠️ Refatorar com cuidado |
| Testes | Médio | 🔄 Refatorar/Remover |
| Arquivos arquivados | Muito Baixo | ✅ Pode manter no .archive/ |

---

## 🎯 Inventário Detalhado

### 1. ARQUIVOS DE DADOS (data/)

#### ✅ Remoção Direta - Impacto Baixo
```
data/
├── creditcard_test_500.csv          # Arquivo de teste - REMOVER
└── demo_transacoes.csv              # Verificar se é relacionado - MANTER (genérico)
```

**Ação:** Deletar `creditcard_test_500.csv`

---

### 2. SCRIPTS (scripts/)

#### ✅ Remoção Direta - Scripts Específicos de Fraude
```python
scripts/
├── ingest_creditcard.py             # REMOVER - Ingestão específica creditcard
├── query_creditcard_agent.py        # REMOVER - Consultas específicas creditcard
├── ingest_completo.py               # REMOVER - Refs creditcard.csv (284,807 registros)
├── balanced_ingest.py               # REMOVER - Ingestão balanceada creditcard
├── ultra_fast_ingest.py             # REMOVER - Ingestão rápida creditcard
├── batch_ingest.py                  # REMOVER - Ingestão batch creditcard
├── test_corrected_ingestion.py      # REMOVER - Teste específico creditcard
└── populate_intent_embeddings.py    # ⚠️ REFATORAR - Contém categoria "fraud_detection"
```

#### 🔄 Refatorar - Scripts com Referências Parciais
```python
scripts/
├── populate_intent_embeddings.py
│   └── Remover categoria "fraud_detection" e exemplos relacionados
└── expand_intent_categories.py
    └── Remover queries relacionadas a fraude
```

---

### 3. EXEMPLOS (examples/)

#### ✅ Remoção Direta
```python
examples/
├── creditcard_fraud_analysis.py     # REMOVER
├── fraud_detection_llm_simple.py    # REMOVER
├── fraud_detection_llm_advanced.py  # REMOVER
├── teste_deteccao_fraude.py         # REMOVER
├── teste_fraude.csv                 # REMOVER
├── README_CREDITCARD_ANALYSIS.md    # REMOVER
├── README_CREDITCARD_DATASET.md     # REMOVER
└── README_FRAUD_DETECTION_LLM.md    # REMOVER
```

---

### 4. CÓDIGO-FONTE (src/) - ⚠️ CRÍTICO - REFATORAÇÃO NECESSÁRIA

#### 4.1. Agentes (src/agent/)

##### **orchestrator_agent.py** - Impacto ALTO
```python
# Referências encontradas:
- Linha 630: Comentário sobre 'fraud_detection' removido
- Linha 670: Lista de palavras-chave inclui 'fraude'
- Linhas 1020, 1054, 1367, 1387, 1489, 1495: Exemplos de uso mencionam fraude
- Linha 1516, 1520: Exemplos com contexto de fraude
```
**Ação:** Remover exemplos e referências de fraude nos prompts e documentação inline

##### **csv_analysis_agent.py**
```python
- Linha 554: Comentário "SEM detecção de fraude"
```
**Ação:** Revisar se é apenas comentário ou há lógica relacionada

##### **rag_synthesis_agent.py**
```python
- Linhas 38, 153: Descrição hard-coded da coluna "Class" como fraude
```
**Ação:** CRÍTICO - Remover referências hard-coded à coluna Class e fraude

##### **rag_data_agent.py**
```python
- Linha 718: Template hard-coded descrevendo Class como variável de fraude
```
**Ação:** CRÍTICO - Remover template específico de fraude

##### **google_llm_agent.py**
```python
# Referências encontradas:
- Linha 183: System prompt "especialista em detecção de fraudes"
- Linha 187: "Detectar anomalias e possíveis fraudes"
- Linhas 212-214: Contexto "fraud_data"
- Linhas 295-313: Método detect_fraud_patterns()
- Linhas 413-414: Metadata fraud_count
```
**Ação:** 
- Generalizar system prompt para análise de dados
- REMOVER método `detect_fraud_patterns()`
- Remover lógica específica de fraud_data

##### **groq_llm_agent.py**
```python
# Referências similares ao google_llm_agent.py:
- Linha 182: System prompt com fraudes
- Linhas 211-213: Contexto fraud_data
- Linhas 373-388: Método detect_fraud_patterns()
- Linhas 326-327: Metadata fraud_count
```
**Ação:** Mesmas refatorações do google_llm_agent.py

##### **grok_llm_agent.py**
```python
# Referências similares:
- Linha 163: System prompt com fraudes
- Linhas 192-194: Contexto fraud_data
- Linhas 287-304: Método detect_fraud_patterns()
```
**Ação:** Mesmas refatorações do google_llm_agent.py

#### 4.2. Prompts (src/prompts/)

##### **manager.py**
```python
- Linha 21: PromptType.FRAUD_DETECTIVE = "fraud_detective"
- Linhas 146-160: Template "fraud_detection_context"
```
**Ação:** 
- Remover PromptType.FRAUD_DETECTIVE
- Remover template fraud_detection_context

#### 4.3. Router (src/router/)

##### **semantic_router.py**
```python
- Linha 210: Exemplo "Detecte fraudes no dataset."
```
**Ação:** Remover exemplo específico de fraude

#### 4.4. Tools (src/tools/)

##### **guardrails.py**
```python
- Linha 435: Regex para detectar "class 1|fraude"
- Linha 503: Keywords de fraude: 'fraude', 'fraud', 'cartão', 'crédito', 'credit', 'card'
```
**Ação:** 
- Revisar se guardrails devem ser genéricos ou específicos
- Remover keywords específicas de fraude/cartão

#### 4.5. Data Loader (src/data/)

##### **data_loader.py** - Impacto MÉDIO
```python
- Linha 378: Método create_synthetic_data() com tipo "fraud_detection"
- Linha 401-402: Condição para criar dados de fraude
- Linhas 465-491: Método _create_fraud_data()
```
**Ação:** 
- Opção 1: Remover completamente tipo "fraud_detection"
- Opção 2: Manter genérico para testes, mas renomear (ex: "anomaly_detection")
- **Recomendação:** Remover completamente - não é necessário para MVP fiscal

---

### 5. TESTES (tests/)

#### ✅ Remoção Direta - Testes Específicos
```python
tests/
├── test_small_ingest.py            # Refs creditcard_test_500.csv
├── test_distribuicao_classes.py    # Query específica sobre fraude
├── test_novo_csv.py                # Validação sobre creditcard.csv
├── test_verificacao_dados.py       # Carrega creditcard_test_500.csv
└── test_workflow_completo.py       # Refs creditcard.csv
```

#### 🔄 Refatorar - Testes com Referências Parciais
```python
tests/
├── test_rag_mock.py                # Exemplos de texto sobre fraude
├── test_orchestrator.py            # Queries sobre fraude nos testes
├── test_orchestrator_basic.py      # Query "busque informações sobre fraude"
├── test_semantic_router.py         # Pergunta "Detecte fraudes no dataset"
├── test_sistema_corrigido.py       # Query sobre distribuição de classes de fraude
├── test_rag_system.py              # Mock data sobre fraude em cartão
├── test_data_loading_system.py     # Testes com tipo "fraud_detection"
└── test_correcoes_base_dados.py    # Context com creditcard_test_500.csv
```

#### 🔄 Testes de Memória
```python
tests/memory/
├── test_memory_system.py           # Embedding sobre "analisar fraudes"
└── test_memory_integration.py      # Múltiplas refs a fraude/creditcard.csv
```

**Ação:** 
- Substituir exemplos de fraude por exemplos genéricos ou fiscais
- Manter estrutura dos testes, apenas trocar os dados de exemplo

---

### 6. ARQUIVOS ARQUIVADOS (.archive/)

#### 📦 Manter no Arquivo (Histórico)
```
.archive/
├── debug/
│   ├── test_generic_csv.py
│   ├── analise_creditcard_dataset.py
│   ├── comparacao_perplexity_vs_agent.py
│   ├── analise_rapida.py
│   └── [outros arquivos debug]
└── root_scripts/
    ├── clear_creditcard_embeddings.py
    ├── check_metadata_chunks.py
    └── api_simple.py
```

**Ação:** ✅ MANTER - São arquivos de debug/histórico já arquivados

---

### 7. BANCO DE DADOS (Supabase)

#### 🗄️ Limpeza Necessária

**Tabela:** `embeddings`

```sql
-- Identificar embeddings relacionados a fraude/creditcard
SELECT COUNT(*) FROM embeddings 
WHERE metadata->>'source' LIKE '%creditcard%'
   OR metadata->>'source_id' LIKE '%creditcard%'
   OR chunk_text ILIKE '%fraude%'
   OR chunk_text ILIKE '%fraud%';

-- Script de limpeza (EXECUTAR COM CUIDADO)
DELETE FROM embeddings 
WHERE metadata->>'source' LIKE '%creditcard%'
   OR metadata->>'source_id' LIKE '%creditcard%';
```

**Tabela:** `chunks` (se existir)
```sql
-- Verificar e limpar chunks relacionados
DELETE FROM chunks 
WHERE metadata->>'source' LIKE '%creditcard%';
```

**Ação:** Criar script SQL seguro para limpeza seletiva

---

### 8. DOCUMENTAÇÃO

#### 🔄 Atualizar Documentação
```markdown
├── QUICKSTART.md                   # Linha 87-88: Refs ingest_creditcard.py
├── NAVIGATION.md                   # Linhas 33, 51: Refs creditcard e fraud_detection
└── README.md                       # Verificar se há referências
```

**Ação:** Atualizar exemplos para contexto fiscal

---

## 🚨 PONTOS CRÍTICOS DE ATENÇÃO

### 1. **Hard-coding de Colunas**
⚠️ **CRÍTICO:** Vários agentes têm hard-coding da coluna "Class" como indicador de fraude
- `rag_synthesis_agent.py` linha 38, 153
- `rag_data_agent.py` linha 718

**Impacto:** Pode quebrar o sistema se não refatorado corretamente

### 2. **Métodos de Detecção de Fraude**
⚠️ **ALTO:** Três agentes LLM têm método `detect_fraud_patterns()`
- `google_llm_agent.py`
- `groq_llm_agent.py`
- `grok_llm_agent.py`

**Impacto:** Remoção é segura se nenhum outro módulo chama esses métodos

### 3. **System Prompts Especializados**
⚠️ **MÉDIO:** Prompts mencionam "especialista em fraudes"
- Todos os agentes LLM principais

**Impacto:** Deve ser generalizado para "análise de dados" ou "análise fiscal"

### 4. **Data Loader Sintético**
⚠️ **MÉDIO:** Tipo "fraud_detection" no gerador de dados sintéticos
- `src/data/data_loader.py`

**Impacto:** Se removido, verificar se algum teste depende disso

---

## 📋 CHECKLIST DE VALIDAÇÃO PÓS-REMOÇÃO

Após executar as remoções, validar:

- [ ] Sistema inicia sem erros
- [ ] Upload de CSV genérico funciona
- [ ] Chat básico funciona sem referências a fraude
- [ ] Testes principais passam (refatorados)
- [ ] API Swagger não tem endpoints de fraude
- [ ] Banco de dados limpo (verificar embeddings)
- [ ] Documentação atualizada
- [ ] Nenhum import quebrado
- [ ] Logs não mostram erros relacionados a módulos removidos

---

## 🎯 RECOMENDAÇÃO DE EXECUÇÃO

### Ordem Sugerida de Remoção:

1. **FASE 1 - Remoção Segura (Baixo Risco)**
   - Deletar arquivos de dados CSV
   - Deletar scripts específicos
   - Deletar exemplos
   - Atualizar documentação

2. **FASE 2 - Refatoração de Código (Médio Risco)**
   - Refatorar agentes LLM (remover métodos detect_fraud_patterns)
   - Generalizar system prompts
   - Remover templates de prompts específicos
   - Refatorar data_loader

3. **✅ FASE 3 - Refatoração de Testes (CONCLUÍDA)**
   - ✅ Substituir dados de exemplo nos testes
   - ✅ Atualizar queries de teste
   - ✅ Refatorar test_rag_mock.py
   - ✅ Refatorar test_orchestrator_basic.py
   - ✅ Refatorar test_verificacao_dados.py
   - ✅ Refatorar test_workflow_completo.py
   - ✅ Refatorar test_small_ingest.py
   - ✅ Refatorar test_correcoes_base_dados.py
   - ✅ Refatorar tests/memory/test_memory_integration.py

4. **FASE 4 - Limpeza de Banco (Médio Risco)**
   - Executar script SQL de limpeza
   - Validar integridade do banco

5. **FASE 5 - Validação Completa (Crítico)**
   - Executar todos os testes
   - Validar funcionalidade básica
   - Verificar logs

---

## 📊 MÉTRICAS ATUALIZADAS

- **Arquivos deletados (Fase 1):** 20+ arquivos ✅
- **Arquivos refatorados (Fase 2):** 15 arquivos ✅
- **Arquivos de teste refatorados (Fase 3):** 7 arquivos ✅
- **Linhas de código removidas:** ~800+ linhas
- **Tempo total até Fase 3:** ~3-4 horas
- **Risco geral:** Baixo (com planejamento adequado)

---

## ✅ STATUS ATUAL - 26/10/2025

### Fases Concluídas:
1. ✅ **FASE 1**: Remoção de arquivos CSV, scripts e exemplos específicos de fraude
2. ✅ **FASE 2**: Refatoração de agentes LLM e generalização de prompts
3. ✅ **FASE 3**: Refatoração completa de testes

### Arquivos Modificados na Fase 3:
- `tests/test_rag_mock.py` - Exemplos fiscais substituindo fraude
- `tests/test_orchestrator_basic.py` - Query sobre ICMS ao invés de fraude
- `tests/test_verificacao_dados.py` - Usando demo_transacoes.csv
- `tests/test_workflow_completo.py` - Removidas referências a creditcard.csv
- `tests/test_small_ingest.py` - Usando demo_transacoes.csv
- `tests/test_correcoes_base_dados.py` - Contexto genérico
- `tests/memory/test_memory_integration.py` - Exemplos de documentos fiscais e análise de dados genéricos

### Próximos Passos:
1. Executar FASE 4 (Limpeza de Banco)
2. Executar FASE 5 (Validação Completa)
3. Merge para main

**Gostaria de proceder com a execução ou prefere revisar/ajustar o plano primeiro?**

```
