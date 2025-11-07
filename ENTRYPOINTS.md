# 🚪 Guia de Entrypoints - AgentNFe Backend

Este documento lista todos os entrypoints disponíveis no projeto e como usá-los.

---

## 🎯 Entrypoints Principais (ATUALIZADOS)

### ✅ 1. **API REST - Desenvolvimento** (RECOMENDADO)

```powershell
python run_api.py
```

**Características:**
- ✅ Auto-reload ativo (detecta mudanças em código)
- ✅ Porta: 8000
- ✅ Modo desenvolvimento
- ✅ Logs detalhados
- ✅ Interface amigável

**Acessos:**
- 📝 Swagger UI: http://localhost:8000/docs
- 📚 Redoc: http://localhost:8000/redoc
- 💚 Health Check: http://localhost:8000/health
- 🔍 Endpoints NFe: http://localhost:8000/nfe/

---

### 🚀 2. **API REST - Produção**

```powershell
python run_api_production.py
```

**Características:**
- ⚡ 4 workers (multiprocessing)
- 🔒 Sem auto-reload
- 📊 Logs otimizados
- 🎯 Alta performance

**Use quando:**
- Deploy em servidor
- Alta carga de requisições
- Ambiente de produção

---

### 🛠️ 3. **API REST - Setup Completo** (Com Instalação)

```powershell
python scripts\setup_and_run_fastapi.py
```

**O que faz:**
1. Cria ambiente virtual (se não existir)
2. Instala dependências do requirements.txt
3. Inicia servidor FastAPI
4. Detecta porta livre automaticamente

**Use quando:**
- Primeiro setup do projeto
- Precisa reinstalar dependências
- Migrou de máquina/ambiente

---

## 📊 Scripts de Processamento de Dados

### 4. **Geração de Embeddings Vetoriais**

```powershell
# Teste rápido (5 notas)
python scripts/generate_nfe_embeddings.py --test

# Processar batch específico
python scripts/generate_nfe_embeddings.py --max-notas 100 --batch-size 50

# Processar todas as notas do banco (94k)
python scripts/generate_nfe_embeddings.py
```

**Parâmetros:**
- `--test`: Modo teste (5 notas)
- `--max-notas N`: Limita processamento a N notas
- `--batch-size N`: Tamanho do batch (padrão: 100)

---

### 5. **Migrations de Banco de Dados**

```powershell
python scripts/run_migrations.py
```

**O que faz:**
- Executa migrations SQL em ordem
- Cria schema pgvector
- Configura índices HNSW
- Atualiza funções de busca

---

## 🧪 Scripts de Teste

### 6. **Teste Completo com Dados Reais**

```powershell
python test_nfe_with_data.py
```

**Testes incluídos:**
- ✅ Validação CFOP (8 testes)
- ✅ Validação NCM (8 testes)
- ✅ Análise de nota fiscal
- ✅ Detecção de anomalias
- ✅ Consultas fiscais LLM

**Dados:** Usa CSVs com 150k+ notas reais

---

### 7. **Teste de Busca Vetorial**

```powershell
python test_vector_search.py
```

**Cenários testados:**
- Notas interestaduais
- Produtos eletrônicos
- Alto valor de ICMS
- Notas acima de R$ 10.000

**Métricas:** Scores de similaridade (0-1)

---

### 8. **Teste Rápido do Gemini**

```powershell
python test_gemini_query.py
```

**Valida:**
- Integração Gemini 2.0 Flash
- Consultas fiscais via LLM
- Temperatura e parâmetros

---

### 9. **Teste Unitário do Agente**

```powershell
python test_nfe_agent.py
```

**7 testes unitários:**
- Inicialização do agente
- Validações CFOP/NCM
- Análise de nota
- Detecção de anomalias
- Consultas fiscais
- Busca de similaridade

---

## 🔧 Scripts de Manutenção

### 10. **Verificar Conexão com Banco**

```powershell
python check_db.py
```

**Verifica:**
- Conexão Supabase/PostgreSQL
- Credenciais válidas
- Extensão pgvector instalada

---

### 11. **Verificar Estrutura do Banco**

```powershell
python check_db_structure.py
```

**Mostra:**
- Contagem de registros por tabela
- Tabelas: embeddings, chunks, metadata, nota_fiscal, nota_fiscal_item

---

### 12. **Verificar Dimensões de Embeddings**

```powershell
python scripts/check_embedding_dims.py
```

**Valida:**
- Dimensões da coluna embedding
- Configuração pgvector (768D)

---

### 13. **Corrigir Schema de Embeddings**

```powershell
python scripts/fix_embedding_768.py
```

**Corrige:**
- Atualiza para 768 dimensões (Gemini)
- Recria índices HNSW
- Atualiza função match_embeddings

---

## 🎯 Fluxo de Trabalho Recomendado

### **Primeira Vez (Setup Inicial):**

```powershell
# 1. Clonar repositório
git clone https://github.com/ai-mindsgroup/agentnfe-backend.git
cd agentnfe-backend

# 2. Configurar ambiente
python scripts\setup_and_run_fastapi.py
# Pressione CTRL+C após iniciar
```

### **Desenvolvimento Diário:**

```powershell
# 1. Ativar ambiente virtual
.venv\Scripts\Activate.ps1

# 2. Iniciar API
python run_api.py
```

### **Processar Novas Notas:**

```powershell
# 1. Gerar embeddings
python scripts/generate_nfe_embeddings.py --max-notas 100

# 2. Testar busca
python test_vector_search.py
```

### **Deploy em Produção:**

```powershell
# 1. Migrations
python scripts/run_migrations.py

# 2. Gerar embeddings
python scripts/generate_nfe_embeddings.py

# 3. Iniciar servidor
python run_api_production.py
```

---

## 📝 Resumo Rápido

| Ação | Comando |
|------|---------|
| **Iniciar API (dev)** | `python run_api.py` |
| **Iniciar API (prod)** | `python run_api_production.py` |
| **Setup completo** | `python scripts\setup_and_run_fastapi.py` |
| **Gerar embeddings** | `python scripts/generate_nfe_embeddings.py` |
| **Testar tudo** | `python test_nfe_with_data.py` |
| **Testar busca** | `python test_vector_search.py` |
| **Verificar banco** | `python check_db.py` |
| **Migrations** | `python scripts/run_migrations.py` |

---

## 🆕 Novos Entrypoints Adicionados

Comparado ao projeto original EDA AI Minds:

✅ **`run_api.py`** - Novo entrypoint simplificado (desenvolvimento)  
✅ **`run_api_production.py`** - Novo entrypoint para produção  
✅ **`scripts/setup_and_run_fastapi.py`** - Atualizado com detecção de porta livre  
✅ **`scripts/generate_nfe_embeddings.py`** - Substitui run_auto_ingest.py  
✅ **`test_nfe_with_data.py`** - Teste completo com dados reais  
✅ **`test_vector_search.py`** - Teste de busca semântica  

❌ **Removidos do original:**
- `interface_interativa.py` - Não há CLI interativa no AgentNFe
- `run_auto_ingest.py` - Substituído por generate_nfe_embeddings.py

---

**Atualizado em:** 03/11/2025  
**Versão AgentNFe:** 2.1.0
