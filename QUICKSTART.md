# 🚀 Guia de Início Rápido

## ⚡ Setup em 5 Minutos

### 1️⃣ Pré-requisitos

- Python 3.10 ou superior
- Git
- Conta Supabase (para banco vetorial)
- Chaves de API (opcional, mas recomendado):
  - OpenAI API Key
  - Google AI API Key
  - Perplexity Sonar API Key

### 2️⃣ Instalação

```bash
# Clone o repositório
git clone https://github.com/roberto-fgv/agentnfe-backend.git
cd agentnfe-backend

# Crie ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 3️⃣ Configuração

```bash
# Copie o arquivo de exemplo
cp configs/.env.example configs/.env

# Edite configs/.env com suas credenciais
# Use seu editor favorito
nano configs/.env  # ou vim, code, etc.
```

**Variáveis essenciais em `configs/.env`:**

```env
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
DB_HOST=db.your-project.supabase.co
DB_PASSWORD=your_database_password

# LLMs (pelo menos uma)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
SONAR_API_KEY=pplx-...

# Configuração
LOG_LEVEL=INFO
```

### 4️⃣ Setup do Banco de Dados

```bash
# Execute as migrations
python scripts/run_migrations.py

# Verifique a conexão
python -c "from src.vectorstore.supabase_client import supabase; print('✅ Conexão OK!')"
```

### 5️⃣ Teste Básico

```bash
# Execute um exemplo simples
python examples/demo_csv_agent.py

# Ou teste a análise interativa
python examples/analise_interativa_console.py
```

## 📊 Carregar Dados de Exemplo

```bash
# Carregar seus próprios dados CSV
# Use a interface web ou API para fazer upload de arquivos CSV

# Verificar carga
python -c "from src.vectorstore.supabase_client import supabase; print(supabase.table('embeddings').select('count').execute())"
```

## 🎯 Exemplos de Uso

### Análise Interativa

```python
from src.agent.orchestrator_agent import OrchestratorAgent
import pandas as pd

# Carregue seus dados
df = pd.read_csv("data/seu_arquivo.csv")

# Crie o agente orquestrador
agent = OrchestratorAgent()

# Faça perguntas
resposta = agent.process_query(
    query="Qual a distribuição de valores neste dataset?",
    context={"dataframe": df}
)

print(resposta)
```

### API REST (FastAPI)

```bash
# Inicie a API (se disponível)
uvicorn api_completa:app --reload

# Acesse a documentação
# http://localhost:8000/docs
```

## 📁 Estrutura Importante

```
agentnfe-backend/
├── src/              # Código fonte principal
│   ├── agent/       # Agentes do sistema
│   ├── embeddings/  # Geração de embeddings
│   ├── llm/         # Gerenciamento LLMs
│   └── ...
├── scripts/         # Scripts de utilidade
├── examples/        # Exemplos práticos
├── tests/           # Testes automatizados
└── docs/            # Documentação completa
```

## 🔧 Comandos Úteis

```bash
# Executar testes
pytest tests/ -v

# Ver logs
tail -f logs/app-back-log-simon.log

# Limpar embeddings
python scripts/clean_database.py

# Recarregar dados

# Use scripts disponíveis para carregar seus próprios dados. Alguns scripts de ingestão
# específicos de datasets de fraude foram removidos para focar no fluxo genérico.
# Exemplos de utilitários úteis: `scripts/run_utils.py`, `examples/demo_data_loading.py`.
```

## 🐛 Solução de Problemas

### Erro de conexão Supabase
```bash
# Verifique as credenciais
python -c "from src.settings import SUPABASE_URL, SUPABASE_KEY; print(f'URL: {SUPABASE_URL[:20]}...')"
```

### Erro de dependências
```bash
# Reinstale dependências
pip install -r requirements.txt --upgrade
```

### Erro de migrations
```bash
# Execute migrations individualmente
python scripts/run_migrations.py --verbose
```

## 📚 Próximos Passos

1. **Leia a documentação:** [`docs/INDEX.md`](docs/INDEX.md)
2. **Explore exemplos:** [`examples/README.md`](examples/README.md)
3. **Entenda a arquitetura:** [`docs/architecture/`](docs/architecture/)
4. **Configure integrações:** [`docs/guides/`](docs/guides/)

## 🆘 Precisa de Ajuda?

- 📖 Documentação completa: [`docs/`](docs/)
- 🐛 Troubleshooting: [`docs/troubleshooting/`](docs/troubleshooting/)
- 💬 Problemas conhecidos: [`CHANGELOG.md`](CHANGELOG.md)

## ✅ Checklist de Setup

- [ ] Python 3.10+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Migrations executadas
- [ ] Conexão Supabase funcionando
- [ ] Pelo menos 1 LLM configurado
- [ ] Teste básico executado com sucesso

---

**🎉 Pronto! Você está pronto para começar a usar o sistema multiagente!**

Para informações detalhadas, consulte [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) e [`docs/INDEX.md`](docs/INDEX.md).

