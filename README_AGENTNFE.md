# 🎯 AgentNFe - Sistema Multiagente para Análise de Notas Fiscais Eletrônicas

<div align="center">

![Status](https://img.shields.io/badge/Status-Produção-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Version](https://img.shields.io/badge/Version-2.1.0-blue?style=for-the-badge)

**Sistema multiagente inteligente para análise fiscal de Notas Fiscais Eletrônicas (NF-e)**

*Validação CFOP/NCM • Análise Tributária • Detecção de Anomalias • Consultas Fiscais via IA*

</div>

---

## 🛠️ Stack Tecnológica

### Core & Framework
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/🦜_LangChain-0.3.27-1C3C3C?style=for-the-badge)
![Pydantic](https://img.shields.io/badge/Pydantic-2.11.7-E92063?style=for-the-badge)

### AI & LLMs
![Gemini](https://img.shields.io/badge/Gemini_2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Fallback-FF6B00?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-Fallback-412991?style=for-the-badge&logo=openai&logoColor=white)

### Data & Analysis
![Pandas](https://img.shields.io/badge/Pandas-2.2.3-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-2.3.2-013243?style=for-the-badge&logo=numpy&logoColor=white)

### Database & Vector Store
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-Embeddings-336791?style=for-the-badge)

---

## ✨ Funcionalidades Principais

### 🤖 Agente Especialista em Tributação (NFeTaxSpecialistAgent)

#### Validações Fiscais
- ✅ **Validação CFOP**: 8 dígitos primários cobertos (entradas/saídas)
- ✅ **Validação NCM**: Análise por capítulos e categorias de produtos
- ✅ **Análise Tributária**: ICMS, IPI, PIS, COFINS
- ✅ **Score Fiscal**: Avaliação de 0-100 pontos

#### Análise Inteligente
- ✅ **Análise Completa de NF-e**: Validação de campos obrigatórios
- ✅ **Detecção de Anomalias**: Inconsistências tributárias
- ✅ **Consultas Fiscais**: Perguntas sobre legislação via Gemini 2.0
- ✅ **Busca Vetorial**: Notas similares via embeddings

#### Dados Reais Testados
- ✅ **150.976 notas fiscais** processadas
- ✅ **549.431 itens** analisados  
- ✅ **Média 3.6 itens/nota**
- ✅ **100% de sucesso** nos testes

### 🌐 API RESTful Completa

#### 7 Endpoints NFe Disponíveis

```http
POST   /nfe/validate/cfop          # Valida código CFOP
POST   /nfe/validate/ncm           # Valida código NCM
POST   /nfe/analyze                # Análise completa da nota
POST   /nfe/anomalies              # Detecta anomalias
POST   /nfe/query                  # Consultas fiscais via IA
GET    /nfe/similar/{chave_acesso} # Busca notas similares
GET    /nfe/list                   # Lista notas com filtros
GET    /nfe/health                 # Health check do serviço
```

#### Documentação Automática
- 🔗 **Swagger UI**: `http://localhost:8011/docs`
- 🔗 **ReDoc**: `http://localhost:8011/redoc`

---

## 🚀 Início Rápido

### 1. Pré-requisitos
```bash
Python 3.10+
PostgreSQL com pgvector (via Supabase)
Google API Key (Gemini)
```

### 2. Instalação
```powershell
# Clonar repositório
git clone https://github.com/roberto-fgv/agentnfe-backend.git
cd agentnfe-backend

# Criar ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração
```powershell
# Copiar arquivo de configuração
copy configs\.env.example configs\.env

# Editar configs\.env com suas credenciais:
```

```env
# Supabase (obrigatório)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_anon_key

# Google Gemini (obrigatório para queries fiscais)
GOOGLE_API_KEY=your_google_api_key

# Database (obrigatório)
DB_HOST=db.xyz.supabase.co
DB_PASSWORD=your_db_password

# Opcional
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key

# Configurações
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8011
```

### 4. Iniciar Servidor
```powershell
# Modo desenvolvimento
python api_completa.py

# Ou com uvicorn
uvicorn api_completa:app --reload --host 0.0.0.0 --port 8011
```

🌐 Acesse: **http://localhost:8011/docs**

---

## 📊 Exemplos de Uso

### Validação de CFOP
```python
import requests

response = requests.post("http://localhost:8011/nfe/validate/cfop", json={
    "cfop": "5101"
})

print(response.json())
# {
#   "valido": true,
#   "cfop": "5101",
#   "descricao": "Venda de produção do estabelecimento",
#   "natureza_operacao": "Saída"
# }
```

### Análise Completa de Nota
```python
response = requests.post("http://localhost:8011/nfe/analyze", json={
    "chave_acesso": "13250505914165000192550030000116841779221343",
    "numero_nota": 11684,
    "emitente_cnpj": "05914165000192",
    "emitente_razao_social": "CARBOXI INDUSTRIA",
    "valor_total": 4603.42,
    "data_emissao": "01/05/2025",
    "itens": [
        {
            "cfop": "6107",
            "ncm": "28044000",
            "descricao": "OXIGENIO MEDICINAL",
            "valor": 602.64
        }
    ]
})

print(response.json()["score_fiscal"])  # 85/100
```

### Consulta Fiscal via IA
```python
response = requests.post("http://localhost:8011/nfe/query", json={
    "query": "O que é CFOP e como funciona?",
    "context": {}
})

print(response.json()["resposta"])
# "O CFOP (Código Fiscal de Operações e Prestações) é um código 
#  numérico que identifica a natureza da operação fiscal..."
```

---

## 🧪 Testes

### Testes Automatizados
```powershell
# Teste do agente NFe
python tests/integration/test_nfe_agent.py

# Teste com dados reais (150k+ notas)
python test_nfe_with_data.py

# Teste rápido de query Gemini
python test_gemini_query.py
```

### Resultados dos Testes
```
✅ Validação CFOP: 8/8 códigos validados
✅ Validação NCM: 2/8 válidos (outros incompletos nos dados)
✅ Análise de Nota: Score 100/100
✅ Detecção de Anomalias: Nenhuma anomalia detectada
✅ Consultas Fiscais: 3/3 respostas via Gemini
```

---

## 🏗️ Arquitetura

### Estrutura do Projeto
```
agentnfe-backend/
├── app/
│   ├── models/          # Modelos Pydantic (16 classes)
│   │   └── nfe_models.py
│   └── routers/         # Endpoints da API
│       └── nfe.py       # 7 endpoints NFe
├── src/
│   ├── agent/           # Agentes inteligentes
│   │   ├── base_agent.py
│   │   ├── nfe_tax_specialist_agent.py  # ⭐ Agente NFe
│   │   ├── rag_agent.py
│   │   └── orchestrator_agent.py
│   ├── llm/             # Gerenciamento de LLMs
│   │   └── langchain_manager.py  # Fallback automático
│   ├── embeddings/      # Sistema de embeddings
│   ├── vectorstore/     # Supabase + pgvector
│   └── memory/          # Memória persistente
├── data/                # Dados NF-e
│   ├── 202505_NFe_NotaFiscal.csv      # 150k notas
│   └── 202505_NFe_NotaFiscalItem.csv  # 549k itens
├── tests/               # Testes automatizados
│   └── integration/
│       ├── test_nfe_agent.py
│       └── test_nfe_api.py
├── docs/                # Documentação técnica
├── api_completa.py      # ⭐ API principal
└── requirements.txt
```

### Fluxo de Processamento
```
1. Requisição HTTP → FastAPI Router
2. Validação Pydantic → Models
3. NFeTaxSpecialistAgent → Processamento
4. LangChain LLM Manager → Gemini 2.0 Flash
5. Supabase/pgvector → Busca Vetorial
6. Response JSON → Cliente
```

### Sistema de Fallback LLM
```
1ª Opção: Groq (llama-3.1-8b-instant)
2ª Opção: Google Gemini (gemini-2.0-flash-exp) ✅ ATIVO
3ª Opção: OpenAI (gpt-3.5-turbo)
```

---

## 📚 Documentação Técnica

- 📋 **Relatório de Testes**: `docs/TESTE_AGENTE_NFE_RELATORIO.md`
- 📊 **Status da API**: `docs/STATUS_API_NFE.md`
- 🏗️ **Arquitetura**: `docs/ARQUITETURA-RAG-VETORIAL-CORRIGIDA.md`
- 🔍 **Auditoria**: `docs/auditoria/`

---

## 🎯 Próximos Passos

- [ ] Expandir base de CFOP/NCM com tabela completa
- [ ] Implementar cálculos tributários automáticos
- [ ] Dashboard de visualização de análises
- [ ] Integração com SEFAZ para validação online
- [ ] Exportação de relatórios em PDF
- [ ] API de lote para processar múltiplas notas

---

## 📝 Changelog

### v2.1.0 (2025-11-03)
- ✅ Integração completa com Gemini 2.0 Flash
- ✅ 7 endpoints NFe implementados
- ✅ 16 modelos Pydantic para validação
- ✅ Testes com 150k+ notas reais
- ✅ Fallback automático entre LLMs
- ✅ Consultas fiscais via IA funcionais

### v2.0.0 (2025-11-02)
- ✅ Agente NFeTaxSpecialistAgent implementado
- ✅ Validação CFOP e NCM
- ✅ Sistema de análise fiscal
- ✅ Detecção de anomalias
- ✅ Reorganização completa do projeto

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

**Roberto Santos** - [GitHub](https://github.com/roberto-fgv)

---

## 🙏 Agradecimentos

- Dados NF-e fornecidos para fins educacionais
- Comunidade LangChain
- Google Gemini AI
- Supabase pgvector

---

<div align="center">

**Desenvolvido com ❤️ para análise inteligente de Notas Fiscais Eletrônicas**

</div>
