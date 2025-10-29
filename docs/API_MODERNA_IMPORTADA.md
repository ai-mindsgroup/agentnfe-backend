# 🚀 API Moderna Importada - AgentNFE Backend

**Data de Importação:** 29 de Outubro de 2025  
**Fonte:** `ai-mindsgroup/agentnfe-backend` branch `feature/api-moderna`  
**Destino:** `roberto-fgv/agentnfe-backend` branch `main`

---

## 📦 O Que Foi Importado?

### Arquivos Principais

**APIs Legadas (para comparação):**
- ✅ `api_completa.py` (997 linhas) - API completa porta 8001
- ✅ `api_simple.py` (720 linhas) - API simples porta 8000

**Nova Estrutura Modular (app/):**
- ✅ `app/main.py` (401 linhas) - API moderna v3.0.0
- ✅ `app/core/` - Configurações e segurança
- ✅ `app/middleware/` - Middlewares (auth, logging, rate limiting)
- ✅ `app/models/` - Modelos Pydantic
- ✅ `app/routers/` - Rotas modulares

---

## 🏗️ Arquitetura da API Moderna

### Estrutura Modular

```
app/
├── main.py                 # 🚀 Aplicação principal
├── core/
│   ├── config.py          # Configurações centralizadas
│   ├── database.py        # Gerenciamento de conexões DB
│   └── security.py        # JWT, hashing, autenticação
├── middleware/
│   ├── auth.py            # Autenticação JWT
│   ├── error_handler.py   # Tratamento de erros global
│   ├── logging.py         # Logging estruturado
│   └── rate_limiting.py   # Controle de taxa de requisições
├── models/
│   └── agent_models.py    # Modelos Pydantic para agentes
└── routers/
    ├── agents.py          # Endpoints de agentes IA
    ├── data_processing.py # Processamento de dados
    ├── embeddings.py      # Gerenciamento de embeddings
    ├── fraud_detection.py # Detecção de fraude
    └── health.py          # Health checks e status
```

---

## 🆚 Comparação: API Legada vs API Moderna

| Aspecto | api_completa.py | api_simple.py | app/main.py (v3.0) |
|---------|-----------------|---------------|---------------------|
| **Linhas** | 997 | 720 | 401 (modular) |
| **Porta** | 8001 | 8000 | Configurável |
| **Arquitetura** | Monolítica | Monolítica | Modular |
| **Autenticação** | ❌ | ❌ | ✅ JWT |
| **Rate Limiting** | ❌ | ❌ | ✅ |
| **WebSocket** | ❌ | ❌ | ✅ |
| **Middlewares** | Básico | Básico | Completo |
| **Segurança** | Básica | Básica | Avançada |
| **Escalabilidade** | Baixa | Baixa | Alta |
| **Manutenibilidade** | Baixa | Baixa | Alta |

---

## 📋 Rotas Disponíveis

### API Legada (api_completa.py)

```
GET  /health              → Status da API
POST /chat                → Chat com IA
POST /csv/upload          → Upload CSV
GET  /csv/files           → Lista arquivos
POST /fraud/detect        → Detecção de fraude
GET  /dashboard/metrics   → Métricas
GET  /agents/status       → Status dos agentes
POST /agents/reload       → Recarregar agentes
```

### API Moderna (app/main.py)

```
🏥 Health & Status
GET  /api/v1/health       → Health check
GET  /api/v1/status       → Status detalhado do sistema

🤖 Agentes IA
GET  /api/v1/agents       → Lista todos os agentes
POST /api/v1/agents/query → Consulta inteligente
GET  /api/v1/agents/{id}  → Detalhes de um agente

📊 Processamento de Dados
POST /api/v1/data/upload  → Upload de arquivos
GET  /api/v1/data/files   → Lista arquivos processados
GET  /api/v1/data/{id}    → Detalhes de um arquivo

🧠 Embeddings & RAG
POST /api/v1/embeddings/generate → Gerar embeddings
GET  /api/v1/embeddings/search   → Busca vetorial
DELETE /api/v1/embeddings/{id}   → Remover embeddings

🛡️ Detecção de Fraude
POST /api/v1/fraud/analyze       → Análise de fraude
GET  /api/v1/fraud/reports       → Relatórios de fraude

🔐 Autenticação
POST /api/v1/auth/login          → Login JWT
POST /api/v1/auth/refresh        → Renovar token
GET  /api/v1/auth/me             → Dados do usuário

📈 Analytics
GET  /api/v1/analytics/dashboard → Dashboard completo
GET  /api/v1/analytics/metrics   → Métricas em tempo real

🔄 Tasks Assíncronas
POST /api/v1/tasks/run           → Executar task
GET  /api/v1/tasks/{id}/status   → Status da task
WS   /ws/tasks/{id}              → WebSocket para atualizações
```

---

## 🚀 Como Usar

### 1. API Legada (Testes Rápidos)

```bash
# API Simples (sem multiagente)
python api_simple.py
# http://localhost:8000/docs

# API Completa (com multiagente)
python api_completa.py
# http://localhost:8001/docs
```

### 2. API Moderna (Produção)

```bash
# Configurar ambiente
cp configs/.env.example configs/.env
# Editar configs/.env com suas credenciais

# Instalar dependências
pip install -r requirements.txt

# Executar API moderna
python app/main.py
# ou
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload

# Acessar
# http://localhost:8011/docs
```

---

## 🔑 Funcionalidades da API Moderna

### 1. ✅ Autenticação JWT

```python
# Login
POST /api/v1/auth/login
{
    "username": "admin",
    "password": "senha"
}
# Resposta: { "access_token": "eyJ...", "token_type": "bearer" }

# Usar token
Headers: { "Authorization": "Bearer eyJ..." }
```

### 2. ✅ Rate Limiting

```python
# Limites padrão:
# - 100 requisições por minuto por IP
# - 1000 requisições por hora por usuário

# Headers de resposta:
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 97
X-RateLimit-Reset: 1698585600
```

### 3. ✅ WebSocket para Tasks Longas

```javascript
// Frontend
const ws = new WebSocket('ws://localhost:8011/ws/tasks/task-123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`Progresso: ${data.progress}%`);
};
```

### 4. ✅ Middlewares Personalizados

- **Auth Middleware:** Valida JWT em rotas protegidas
- **Error Handler:** Trata erros globalmente
- **Logging:** Log estruturado de todas as requisições
- **Rate Limiting:** Controle de taxa por IP/usuário
- **CORS:** Configuração flexível
- **GZip:** Compressão automática
- **TrustedHost:** Proteção contra host poisoning

### 5. ✅ Modelos Pydantic Validados

```python
# Exemplo de modelo
class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    agent_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    temperature: float = Field(0.7, ge=0, le=2)
```

---

## 📊 Monitoramento e Analytics

### Métricas Disponíveis

```python
GET /api/v1/analytics/metrics
# Resposta:
{
    "requests_total": 15234,
    "requests_per_minute": 42,
    "active_users": 128,
    "active_agents": 5,
    "embeddings_count": 321000,
    "fraud_detections_today": 23,
    "avg_response_time_ms": 145,
    "error_rate": 0.02,
    "uptime_seconds": 86400
}
```

---

## 🔒 Segurança

### Recursos Implementados

1. **Autenticação JWT**
   - Tokens com expiração configurável
   - Refresh tokens para renovação
   - Revogação de tokens

2. **Hashing de Senhas**
   - bcrypt para senhas
   - Salt automático

3. **Rate Limiting**
   - Proteção contra DDoS
   - Limites por IP e usuário

4. **CORS**
   - Configuração de origens permitidas
   - Headers seguros

5. **Validação de Input**
   - Pydantic models
   - Sanitização automática

6. **HTTPS Ready**
   - Suporte TLS/SSL
   - Strict-Transport-Security

---

## 📚 Documentação Automática

### Swagger UI
```
http://localhost:8011/docs
```

### ReDoc
```
http://localhost:8011/redoc
```

### OpenAPI JSON
```
http://localhost:8011/openapi.json
```

---

## 🧪 Testes

### Testar Health Check

```bash
curl http://localhost:8011/api/v1/health

# Resposta:
{
    "status": "healthy",
    "timestamp": "2025-10-29T10:30:00Z",
    "version": "3.0.0",
    "agents": {
        "total": 5,
        "active": 5,
        "inactive": 0
    },
    "database": {
        "connected": true,
        "latency_ms": 12
    }
}
```

### Testar Autenticação

```bash
# Login
curl -X POST http://localhost:8011/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha"}'

# Usar token
curl http://localhost:8011/api/v1/agents \
  -H "Authorization: Bearer eyJ..."
```

---

## 🔄 Migração da API Legada

### Equivalência de Endpoints

| API Legada | API Moderna | Notas |
|------------|-------------|-------|
| `/health` | `/api/v1/health` | Versionamento |
| `/chat` | `/api/v1/agents/query` | Renomeado |
| `/csv/upload` | `/api/v1/data/upload` | Organizado |
| `/fraud/detect` | `/api/v1/fraud/analyze` | Renomeado |
| `/agents/status` | `/api/v1/agents` | GET em vez de status |

### Script de Migração

```python
# Exemplo de adaptação
# ANTES (api_completa.py)
response = requests.post('http://localhost:8001/chat', json={'message': 'olá'})

# DEPOIS (API moderna)
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:8011/api/v1/agents/query',
    headers=headers,
    json={'query': 'olá'}
)
```

---

## 📈 Roadmap

### ✅ Implementado
- Sistema multiagente integrado
- Autenticação JWT
- Rate limiting
- WebSocket para tasks
- Middlewares completos
- Documentação automática
- Modelos Pydantic validados

### 🔄 Em Desenvolvimento
- Cache Redis
- Message queue (Celery)
- Métricas Prometheus
- Tracing distribuído
- API Gateway
- Service mesh

### 📋 Planejado
- GraphQL endpoint
- gRPC para comunicação interna
- Multi-tenancy
- API versioning v2
- Kubernetes deployment
- CI/CD completo

---

## 🛠️ Configuração Avançada

### Variáveis de Ambiente

```env
# API
API_HOST=0.0.0.0
API_PORT=8011
API_ENV=production

# Segurança
SECRET_KEY=sua_chave_secreta_super_segura
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Database
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave

# LLMs
GOOGLE_API_KEY=sua_chave
SONAR_API_KEY=sua_chave

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true
LOG_LEVEL=INFO
```

---

## 💡 Boas Práticas

### 1. Sempre use a API moderna em produção
```python
# ❌ Não use em produção
python api_simple.py

# ✅ Use a API moderna
python app/main.py
```

### 2. Configure autenticação corretamente
```python
# Sempre proteja rotas sensíveis
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "Acesso autorizado"}
```

### 3. Use rate limiting apropriado
```python
# Ajuste limites por endpoint
@router.post("/expensive-operation")
@limiter.limit("10/minute")
async def expensive_op():
    pass
```

### 4. Monitore métricas constantemente
```python
# Acompanhe health checks
while True:
    health = requests.get('/api/v1/health').json()
    if health['status'] != 'healthy':
        alert_team()
```

---

## 📞 Suporte

### Documentação
- 📄 README principal: `README.md`
- 📊 Backlog: `docs/Backlog do Projeto.md`
- 🔍 Auditoria: `docs/AUDITORIA_BACKLOG_28-10-2025.md`

### Issues
- GitHub Issues: `https://github.com/roberto-fgv/agentnfe-backend/issues`

---

## 🎉 Conclusão

A API moderna traz uma arquitetura profissional e escalável, pronta para produção. Com autenticação, rate limiting, WebSocket e arquitetura modular, o sistema está preparado para crescer e atender demandas complexas.

**Próximos Passos:**
1. Testar a API moderna localmente
2. Configurar variáveis de ambiente
3. Migrar frontend para novos endpoints
4. Deploy em ambiente de produção
5. Configurar monitoramento e alerts

---

**Última Atualização:** 29 de Outubro de 2025  
**Versão da API:** 3.0.0  
**Status:** ✅ Importada e Pronta para Uso
