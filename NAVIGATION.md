# 📚 Índice de Navegação do Projeto

## 🚀 Começando

| Documento | Descrição | Prioridade |
|-----------|-----------|------------|
| [README.md](README.md) | Visão geral do projeto e badges | ⭐⭐⭐ |
| [QUICKSTART.md](QUICKSTART.md) | Setup em 5 minutos | ⭐⭐⭐ |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Estrutura detalhada | ⭐⭐ |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de mudanças | ⭐ |

## 📁 Estrutura do Código

### Core (`src/`)

| Módulo | Descrição | Arquivos Principais |
|--------|-----------|---------------------|
| **agent/** | Sistema multiagente | `orchestrator_agent.py`, `rag_agent.py` |
| **embeddings/** | Geração embeddings | `embedding_generator.py`, `chunker.py` |
| **llm/** | Gerenciamento LLMs | `langchain_manager.py`, `llm_router.py` |
| **memory/** | Sistema de memória | `supabase_memory.py`, `base_memory.py` |
| **router/** | Roteamento semântico | `semantic_router.py`, `query_refiner.py` |
| **data/** | Manipulação dados | `csv_file_manager.py`, `data_loader.py` |
| **vectorstore/** | Banco vetorial | `supabase_client.py` |
| **tools/** | Ferramentas | `graph_generator.py`, `guardrails.py` |

### Scripts (`scripts/`)

| Script | Função | Uso |
|--------|--------|-----|
| `run_migrations.py` | Executar migrations SQL | Setup inicial |
| `setup_database.py` | Configurar banco | Setup inicial |
| `clean_database.py` | Limpar embeddings | Manutenção |

### Testes (`tests/`)

| Diretório | Cobertura |
|-----------|-----------|
| `memory/` | Sistema de memória |
| `langchain/` | Integração LangChain |
| `test_orchestrator.py` | Orquestrador |
| `test_rag_system.py` | Sistema RAG |

### Exemplos (`examples/`)

| Exemplo | Descrição |
|---------|-----------|
| `demo_csv_agent.py` | Demo básico |
| `analise_interativa.py` | Análise interativa |

## 📖 Documentação (`docs/`)

### Por Categoria

| Categoria | Subdiretório | Conteúdo |
|-----------|-------------|----------|
| **Arquitetura** | `architecture/` | Design e decisões técnicas |
| **Guias** | `guides/` | Como fazer X |
| **Auditoria** | `auditoria/` | Relatórios de auditoria |
| **Troubleshooting** | `troubleshooting/` | Solução de problemas |
| **Arquivo** | `archive/` | Documentos antigos |

### Documentos Principais

| Documento | Tópico |
|-----------|--------|
| [INDEX.md](docs/INDEX.md) | Índice completo da documentação |
| [ESTRUTURA_PROJETO.md](docs/ESTRUTURA_PROJETO.md) | Estrutura técnica |
| [STATUS-COMPLETO-PROJETO.md](docs/STATUS-COMPLETO-PROJETO.md) | Status atual |
| [RELATORIO-AGENTES-PROMPTS-GUARDRAILS.md](docs/RELATORIO-AGENTES-PROMPTS-GUARDRAILS.md) | Sistema de agentes |

## ⚙️ Configuração

| Arquivo | Localização | Propósito |
|---------|------------|-----------|
| `.env.example` | `configs/.env.example` | Template de variáveis |
| `requirements.txt` | raiz | Dependências Python |
| `requirements-auto-ingest.txt` | raiz | Deps auto-ingestão |

## 🗄️ Banco de Dados

| Tipo | Localização |
|------|------------|
| Migrations SQL | `migrations/*.sql` |
| Schema principal | `0002_schema.sql` |
| Funções vetoriais | `0003_vector_search_function.sql` |
| Sistema de memória | `0005_agent_memory_tables.sql` |

## 📊 Dados

| Diretório | Conteúdo |
|-----------|----------|
| `data/` | Datasets CSV de exemplo |
| `static/histogramas/` | Gráficos gerados |
| `logs/` | Logs da aplicação |

## 🗂️ Arquivo (`.archive/`)

Arquivos movidos da raiz para manter organização:

- `root_scripts/` - Scripts antigos
- `root_tests/` - Testes antigos
- `old_guides/` - Guias obsoletos
- `debug/` - Scripts de debug
- `outputs/` - Outputs antigos
- `temp/` - Arquivos temporários

> ⚠️ Consultar apenas se necessário. Preferir versões atualizadas em `scripts/`, `tests/` e `docs/`.

## 🔍 Como Encontrar

### "Preciso configurar o sistema"
→ [QUICKSTART.md](QUICKSTART.md)

### "Como funciona a arquitetura?"
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)  
→ [docs/architecture/](docs/architecture/)

### "Como usar o sistema multiagente?"
→ [examples/](examples/)  
→ [docs/guides/](docs/guides/)

### "Estou com um erro"
→ [docs/troubleshooting/](docs/troubleshooting/)  
→ [CHANGELOG.md](CHANGELOG.md) (problemas conhecidos)

### "Como contribuir?"
→ [.github/copilot-instructions.md](.github/copilot-instructions.md)  
→ [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)

### "Onde estão os testes?"
→ [tests/](tests/)  
→ [tests/README.md](tests/README.md)

### "Como funciona o RAG?"
→ [src/agent/rag_agent.py](src/agent/rag_agent.py)  
→ [docs/ARQUITETURA-RAG-VETORIAL-CORRIGIDA.md](docs/ARQUITETURA-RAG-VETORIAL-CORRIGIDA.md)

### "Como configurar LLMs?"
→ [src/llm/langchain_manager.py](src/llm/langchain_manager.py)  
→ [configs/.env.example](configs/.env.example)

## 🎯 Fluxos Comuns

### 1. Setup Inicial
```
QUICKSTART.md → configs/.env → scripts/run_migrations.py → examples/demo_csv_agent.py
```

### 2. Desenvolvimento
```
.github/copilot-instructions.md → src/ → tests/ → commit
```

### 3. Debug
```
logs/ → docs/troubleshooting/ → .archive/debug/ (se necessário)
```

### 4. Documentação
```
docs/INDEX.md → categoria específica → documento
```

## 📞 Suporte

- 📖 Documentação: [docs/](docs/)
- 🐛 Issues: GitHub Issues
- 💬 Discussões: GitHub Discussions

---

**Última atualização:** 2025-10-25  
**Versão da estrutura:** 2.0 (Reorganizada)

