# 🏗️ Plano de Organização do Projeto - Melhores Práticas

**Data:** 03/11/2025  
**Branch:** test/nfe-zero-hardcode  
**Status:** Em execução

---

## 🎯 Objetivos

1. **Separação clara de responsabilidades** (Separation of Concerns)
2. **Estrutura modular e escalável**
3. **Facilitar manutenção e testes**
4. **Remover código duplicado e scripts soltos**
5. **Melhorar navegabilidade do projeto**

---

## 📊 Estado Atual vs Estado Desejado

### ❌ Problemas Identificados

1. **Scripts soltos na raiz** (50+ arquivos)
   - `test_*.py`, `teste_*.py`, `check_*.py`, `clean_*.py`
   - `add_*.py`, `debug_*.py`, `diagnostico_*.py`
   - `temp_*.csv`, `verificar_*.py`

2. **Diretórios vazios ou mal utilizados**
   - `app/` - apenas `__pycache__`
   - `static/` - não utilizado
   - `temp/` - arquivos temporários na raiz

3. **Falta de `__init__.py`** em módulos Python

4. **Documentação espalhada**
   - Docs na raiz (`.md`)
   - Docs em `docs/`
   - Guides misturados

5. **Testes não organizados**
   - Testes na raiz
   - Testes em `tests/`
   - Nomenclatura inconsistente

---

## 🏗️ Nova Estrutura Proposta

```
agentnfe-backend/
│
├── 📁 src/                          # Código fonte principal
│   ├── __init__.py
│   ├── settings.py                  # ✅ Já existe
│   │
│   ├── 📁 agent/                    # Agentes IA
│   │   ├── __init__.py
│   │   ├── base_agent.py           # ✅ Já existe
│   │   ├── nfe_tax_specialist_agent.py  # ✅ Já existe
│   │   ├── orchestrator_agent.py   # ✅ Já existe
│   │   └── rag_agent.py            # ✅ Já existe
│   │
│   ├── 📁 api/                      # APIs e clientes externos
│   │   ├── __init__.py
│   │   └── sonar_client.py         # ✅ Já existe
│   │
│   ├── 📁 data/                     # Processamento de dados
│   │   ├── __init__.py
│   │   └── nfe_uploader.py         # ✅ Já existe
│   │
│   ├── 📁 embeddings/               # Sistema de embeddings
│   │   ├── __init__.py
│   │   ├── generator.py            # ✅ Já existe
│   │   └── vector_store.py         # ✅ Já existe
│   │
│   ├── 📁 integrations/             # Integrações externas
│   │   ├── __init__.py
│   │   └── google_drive/
│   │       ├── __init__.py
│   │       └── client.py
│   │
│   ├── 📁 llm/                      # Gerenciamento de LLMs
│   │   ├── __init__.py
│   │   ├── langchain_manager.py    # ✅ Já existe
│   │   └── manager.py              # ✅ Já existe
│   │
│   ├── 📁 memory/                   # Sistema de memória
│   │   ├── __init__.py
│   │   └── supabase_memory.py      # ✅ Já existe
│   │
│   ├── 📁 prompts/                  # Templates de prompts
│   │   ├── __init__.py
│   │   └── nfe_prompts.py
│   │
│   ├── 📁 router/                   # Roteamento semântico
│   │   ├── __init__.py
│   │   ├── semantic_router.py      # ✅ Já existe
│   │   └── query_refiner.py        # ✅ Já existe
│   │
│   ├── 📁 services/                 # Lógica de negócio
│   │   ├── __init__.py
│   │   └── nfe_service.py          # 🆕 CRIAR
│   │
│   ├── 📁 tools/                    # Ferramentas e utilitários
│   │   ├── __init__.py
│   │   └── visualization.py        # ✅ Já existe
│   │
│   ├── 📁 utils/                    # Utilidades gerais
│   │   ├── __init__.py
│   │   └── logging_config.py       # ✅ Já existe
│   │
│   └── 📁 vectorstore/              # Banco vetorial
│       ├── __init__.py
│       └── supabase_client.py      # ✅ Já existe
│
├── 📁 app/                          # Aplicação FastAPI (modular)
│   ├── __init__.py
│   ├── main.py                      # 🆕 CRIAR
│   │
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   └── 📁 v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── health.py       # 🆕 CRIAR
│   │       │   ├── nfe.py          # 🆕 CRIAR
│   │       │   ├── chat.py         # 🆕 CRIAR
│   │       │   └── fraud.py        # 🆕 CRIAR
│   │       └── deps.py             # Dependências
│   │
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   ├── config.py               # 🆕 CRIAR
│   │   └── security.py             # 🆕 CRIAR
│   │
│   └── 📁 models/
│       ├── __init__.py
│       ├── nfe_models.py           # 🆕 CRIAR
│       └── response_models.py      # 🆕 CRIAR
│
├── 📁 tests/                        # Testes organizados
│   ├── __init__.py
│   ├── conftest.py                 # Fixtures pytest
│   │
│   ├── 📁 unit/                     # Testes unitários
│   │   ├── __init__.py
│   │   ├── test_nfe_agent.py       # ✅ Mover
│   │   ├── test_cfop_validation.py
│   │   └── test_ncm_validation.py
│   │
│   ├── 📁 integration/              # Testes de integração
│   │   ├── __init__.py
│   │   ├── test_api_nfe.py
│   │   └── test_supabase.py
│   │
│   └── 📁 e2e/                      # Testes end-to-end
│       ├── __init__.py
│       └── test_nfe_workflow.py
│
├── 📁 scripts/                      # Scripts utilitários
│   ├── __init__.py
│   ├── 📁 setup/                    # Setup e instalação
│   │   ├── setup_database.py       # ✅ Mover
│   │   └── run_migrations.py       # ✅ Mover
│   │
│   ├── 📁 maintenance/              # Manutenção
│   │   ├── clean_database.py       # ✅ Mover
│   │   └── verify_data.py
│   │
│   └── 📁 development/              # Desenvolvimento
│       └── run_dev_server.py
│
├── 📁 migrations/                   # Migrações de banco
│   ├── README.md
│   └── *.sql                        # ✅ Já existe
│
├── 📁 docs/                         # Documentação
│   ├── README.md
│   ├── 📁 api/                      # Docs da API
│   │   ├── endpoints.md
│   │   └── authentication.md
│   │
│   ├── 📁 architecture/             # Arquitetura
│   │   ├── system_design.md
│   │   └── database_schema.md
│   │
│   ├── 📁 guides/                   # Guias
│   │   ├── quickstart.md
│   │   └── development.md
│   │
│   └── 📁 reports/                  # Relatórios
│       ├── STATUS_API_NFE.md       # ✅ Já existe
│       └── TESTE_AGENTE_NFE_RELATORIO.md  # ✅ Já existe
│
├── 📁 examples/                     # Exemplos de uso
│   ├── README.md
│   └── nfe_examples.py             # ✅ Já existe
│
├── 📁 configs/                      # Configurações
│   ├── .env.example                # ✅ Já existe
│   └── README.md                   # ✅ Já existe
│
├── 📁 data/                         # Dados (não versionados)
│   ├── .gitkeep
│   └── README.md
│
├── 📁 logs/                         # Logs
│   ├── .gitkeep
│   └── README.md
│
├── 📁 outputs/                      # Outputs (gráficos, etc)
│   ├── .gitkeep
│   └── README.md
│
├── 📁 .github/                      # GitHub configs
│   ├── workflows/
│   │   ├── tests.yml               # CI/CD
│   │   └── lint.yml
│   └── PULL_REQUEST_TEMPLATE.md    # ✅ Já existe
│
├── .gitignore                       # ✅ Já existe
├── .env                             # ❌ Não versionar
├── LICENSE                          # ✅ Já existe
├── README.md                        # ✅ Já existe
├── requirements.txt                 # ✅ Já existe
├── requirements-dev.txt             # 🆕 CRIAR
├── pytest.ini                       # 🆕 CRIAR
├── pyproject.toml                   # 🆕 CRIAR
└── CHANGELOG.md                     # ✅ Já existe
```

---

## 🔄 Ações de Refatoração

### Fase 1: Limpeza (PRIORIDADE ALTA)

#### 1.1 Mover scripts de teste
```bash
# Mover para tests/unit/
test_nfe_agent.py → tests/unit/test_nfe_agent.py
test_*.py → tests/integration/

# Mover scripts "teste_" (português)
teste_*.py → scripts/development/ ou remover se obsoletos
```

#### 1.2 Mover scripts de manutenção
```bash
check_*.py → scripts/maintenance/
clean_*.py → scripts/maintenance/
verify_*.py → scripts/maintenance/
diagnostico_*.py → scripts/maintenance/
```

#### 1.3 Mover scripts de setup
```bash
setup_database*.py → scripts/setup/
run_migrations*.py → scripts/setup/
```

#### 1.4 Limpar arquivos temporários
```bash
temp_*.csv → remover ou mover para data/temp/
add_*.py → scripts/maintenance/ ou remover
```

### Fase 2: Criar __init__.py (PRIORIDADE ALTA)

```bash
# Criar em todos os diretórios Python
src/__init__.py
src/agent/__init__.py
src/api/__init__.py
src/data/__init__.py
# ... etc
```

### Fase 3: Modularizar API (PRIORIDADE MÉDIA)

1. Criar `app/main.py` (FastAPI principal)
2. Criar routers em `app/api/v1/endpoints/`
3. Criar modelos Pydantic em `app/models/`
4. Migrar lógica de `api_completa.py`

### Fase 4: Organizar Documentação (PRIORIDADE MÉDIA)

```bash
# Mover guias para docs/guides/
QUICKSTART_*.md → docs/guides/
GUIA_*.md → docs/guides/

# Mover specs técnicas para docs/architecture/
FLUXO_*.md → docs/architecture/
```

### Fase 5: Configurações e DevOps (PRIORIDADE BAIXA)

1. Criar `pyproject.toml` (PEP 518)
2. Criar `pytest.ini`
3. Criar `requirements-dev.txt`
4. Configurar GitHub Actions (CI/CD)
5. Adicionar pre-commit hooks

---

## 📝 Arquivos de Configuração Novos

### `pyproject.toml`
```toml
[tool.poetry]
name = "agentnfe-backend"
version = "2.0.0"
description = "Sistema multiagente para análise tributária de NF-e"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"

[tool.black]
line-length = 100

[tool.isort]
profile = "black"
```

### `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### `requirements-dev.txt`
```txt
# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Linting
black==23.12.0
isort==5.13.0
flake8==6.1.0
mypy==1.7.1

# Documentation
mkdocs==1.5.3
mkdocs-material==9.5.2
```

---

## 🎯 Benefícios Esperados

1. **Manutenibilidade** ⬆️ 80%
   - Código mais fácil de encontrar e modificar

2. **Testabilidade** ⬆️ 60%
   - Testes organizados e isolados

3. **Onboarding** ⬆️ 70%
   - Novos desenvolvedores encontram o que precisam rapidamente

4. **CI/CD** ⬆️ 90%
   - Automação de testes e deploy

5. **Performance** ⬆️ 20%
   - Menos arquivos na raiz, imports mais limpos

---

## ✅ Checklist de Execução

### Fase 1: Limpeza ☑️
- [ ] Mover `test_nfe_agent.py` → `tests/unit/`
- [ ] Mover outros `test_*.py` → `tests/integration/`
- [ ] Mover `teste_*.py` → `scripts/development/`
- [ ] Mover `check_*.py` → `scripts/maintenance/`
- [ ] Mover `clean_*.py` → `scripts/maintenance/`
- [ ] Mover `setup_*.py` → `scripts/setup/`
- [ ] Remover `temp_*.csv`
- [ ] Mover guias `.md` → `docs/guides/`

### Fase 2: Estrutura ☑️
- [ ] Criar todos `__init__.py` necessários
- [ ] Criar `app/main.py`
- [ ] Criar `app/api/v1/endpoints/nfe.py`
- [ ] Criar `app/models/nfe_models.py`
- [ ] Criar `tests/conftest.py`

### Fase 3: Configuração ☑️
- [ ] Criar `pyproject.toml`
- [ ] Criar `pytest.ini`
- [ ] Criar `requirements-dev.txt`
- [ ] Atualizar `.gitignore`

### Fase 4: CI/CD ☑️
- [ ] Criar `.github/workflows/tests.yml`
- [ ] Criar `.github/workflows/lint.yml`
- [ ] Configurar pre-commit hooks

### Fase 5: Documentação ☑️
- [ ] Atualizar `README.md`
- [ ] Criar `docs/guides/quickstart.md`
- [ ] Criar `docs/architecture/system_design.md`

---

## 🚀 Ordem de Execução

1. **AGORA:** Fase 1 (Limpeza) - 1-2h
2. **HOJE:** Fase 2 (Estrutura) - 2-3h
3. **AMANHÃ:** Fase 3 (Configuração) - 1h
4. **ESTA SEMANA:** Fase 4 (CI/CD) - 2-3h
5. **PRÓXIMA SEMANA:** Fase 5 (Documentação) - 2-3h

**TOTAL ESTIMADO:** 8-12 horas

---

**Status:** 🟡 Iniciando Fase 1  
**Próxima Ação:** Executar limpeza de arquivos
