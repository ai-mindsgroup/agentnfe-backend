# 📁 Estrutura do Projeto

```
agentnfe-backend/
│
├── 📄 README.md                      # Documentação principal
├── 📄 CHANGELOG.md                   # Histórico de mudanças
├── 📄 LICENSE                        # Licença MIT
├── 📄 requirements.txt               # Dependências Python
├── 📄 requirements-auto-ingest.txt   # Dependências para auto-ingestão
│
├── 📁 .github/                       # Configurações GitHub
│   ├── copilot-instructions.md      # Instruções para GitHub Copilot
│   └── PULL_REQUEST_TEMPLATE.md     # Template de PR
│
├── 📁 src/                           # Código fonte principal
│   ├── 📁 agent/                    # Agentes do sistema multiagente
│   │   ├── base_agent.py
│   │   ├── csv_analysis_agent.py
│   │   ├── orchestrator_agent.py
│   │   ├── rag_agent.py
│   │   └── ...
│   │
│   ├── 📁 api/                      # Clientes de API externa
│   │   └── sonar_client.py
│   │
│   ├── 📁 data/                     # Gerenciamento de dados
│   │   ├── csv_file_manager.py
│   │   ├── data_loader.py
│   │   ├── data_processor.py
│   │   └── data_validator.py
│   │
│   ├── 📁 embeddings/               # Geração de embeddings
│   │   ├── async_generator.py
│   │   ├── chunker.py
│   │   ├── embedding_generator.py
│   │   └── vector_store.py
│   │
│   ├── 📁 integrations/             # Integrações externas
│   │   └── google_drive_client.py
│   │
│   ├── 📁 llm/                      # Gerenciamento de LLMs
│   │   ├── langchain_manager.py
│   │   ├── llm_router.py
│   │   └── manager.py
│   │
│   ├── 📁 memory/                   # Sistema de memória
│   │   ├── base_memory.py
│   │   ├── langchain_supabase_memory.py
│   │   ├── memory_types.py
│   │   └── supabase_memory.py
│   │
│   ├── 📁 prompts/                  # Gerenciamento de prompts
│   │   └── manager.py
│   │
│   ├── 📁 router/                   # Roteamento semântico
│   │   ├── query_refiner.py
│   │   ├── semantic_ontology.py
│   │   └── semantic_router.py
│   │
│   ├── 📁 services/                 # Serviços do sistema
│   │   └── auto_ingest_service.py
│   │
│   ├── 📁 tools/                    # Ferramentas auxiliares
│   │   ├── graph_generator.py
│   │   ├── guardrails.py
│   │   └── python_analyzer.py
│   │
│   ├── 📁 utils/                    # Utilitários
│   │   └── logging_config.py
│   │
│   ├── 📁 vectorstore/              # Armazenamento vetorial
│   │   └── supabase_client.py
│   │
│   └── 📄 settings.py               # Configurações globais
│
├── 📁 configs/                       # Arquivos de configuração
│   ├── .env.example                 # Exemplo de variáveis de ambiente
│   ├── README.md
│   ├── dados.md
│   ├── requirements-dev.txt
│   └── requirements-minimal.txt
│
├── 📁 scripts/                       # Scripts de utilidade
│   ├── run_migrations.py            # Executar migrations
│   ├── setup_database.py            # Configurar banco
│   ├── ingest_creditcard.py         # Ingerir dados
│   └── ...
│
├── 📁 tests/                         # Testes automatizados
│   ├── 📁 memory/                   # Testes de memória
│   ├── 📁 langchain/                # Testes LangChain
│   ├── test_orchestrator.py
│   ├── test_rag_system.py
│   └── ...
│
├── 📁 examples/                      # Exemplos de uso
│   ├── README.md
│   ├── analise_interativa.py
│   ├── demo_csv_agent.py
│   └── ...
│
├── 📁 docs/                          # Documentação técnica
│   ├── 📁 architecture/             # Documentos de arquitetura
│   ├── 📁 auditoria/                # Relatórios de auditoria
│   ├── 📁 guides/                   # Guias de uso
│   ├── 📁 troubleshooting/          # Solução de problemas
│   ├── 📁 archive/                  # Documentos antigos
│   └── INDEX.md                     # Índice da documentação
│
├── 📁 migrations/                    # Migrations SQL
│   ├── 0000_enable_pgcrypto.sql
│   ├── 0001_init_pgvector.sql
│   ├── 0002_schema.sql
│   └── ...
│
├── 📁 data/                          # Dados de exemplo
│   ├── creditcard_test_500.csv
│   └── demo_transacoes.csv
│
├── 📁 static/                        # Arquivos estáticos
│   └── 📁 histogramas/              # Gráficos gerados
│
├── 📁 logs/                          # Logs da aplicação
│   └── app-back-log-simon.log
│
└── 📁 .archive/                      # Arquivos arquivados
    ├── root_scripts/                # Scripts antigos da raiz
    ├── root_tests/                  # Testes antigos da raiz
    ├── old_guides/                  # Guias antigos
    ├── debug/                       # Debug antigo
    ├── temp/                        # Temporários
    └── outputs/                     # Outputs antigos
```

## 🎯 Principais Diretórios

### `src/` - Código Fonte
Contém toda a lógica do sistema multiagente, organizada por responsabilidade.

### `scripts/` - Scripts de Utilidade
Scripts para setup, migrations, ingestão de dados e outras tarefas administrativas.

### `tests/` - Testes
Testes automatizados organizados por módulo e funcionalidade.

### `docs/` - Documentação
Documentação técnica completa do sistema, incluindo arquitetura, guias e troubleshooting.

### `examples/` - Exemplos
Exemplos práticos de como usar o sistema.

### `.archive/` - Arquivo
Arquivos movidos da raiz para manter organização. Consultar apenas se necessário.

## 🚀 Quick Start

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar ambiente:**
   ```bash
   cp configs/.env.example configs/.env
   # Editar configs/.env com suas credenciais
   ```

3. **Executar migrations:**
   ```bash
   python scripts/run_migrations.py
   ```

4. **Testar sistema:**
   ```bash
   python examples/demo_csv_agent.py
   ```

## 📚 Documentação

Consulte [`docs/INDEX.md`](docs/INDEX.md) para índice completo da documentação.

