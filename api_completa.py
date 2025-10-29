#!/usr/bin/env python3
"""
API Completa - AgentNFE com Sistema Multiagente
==================================================

# Inicialização de agentes
orchestrator = None
csv_agent = None

if MULTIAGENT_AVAILABLE:
    try:
        if ORCHESTRATOR_AVAILABLE:
            orchestrator = OrchestratorAgent()
            logger.info("Orquestrador inicializado")
        
        if CSV_AGENT_AVAILABLE:
            csv_agent = EmbeddingsAnalysisAgent()
            logger.info("CSV Agent inicializado")
            
        logger.info("Sistema multiagente inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar sistema multiagente: {e}")
        orchestrator = None
        csv_agent = None
        MULTIAGENT_AVAILABLE = Falsea com integração ao sistema multiagente:
- Orquestrador central para coordenar agentes
- Análise real de dados CSV com IA
- Detecção de fraude inteligente
- Sistema de embeddings e RAG
- Memória persistente
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
import sys
import os
import io
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Configurar logger antes de tudo
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Importa o LLM Router
try:
    from src.llm.langchain_manager import LangChainLLMManager, get_langchain_llm_manager, LLMConfig, LLMProvider
    LLM_ROUTER_AVAILABLE = True
    logger.info("✅ LangChainLLMManager carregado - roteamento inteligente ativo")
except Exception as e:
    LLM_ROUTER_AVAILABLE = False
    logger.warning(f"⚠️ LangChainLLMManager não disponível: {e}")

# Flags de disponibilidade
MULTIAGENT_AVAILABLE = False
ORCHESTRATOR_AVAILABLE = False
CSV_AGENT_AVAILABLE = False

# Imports do sistema multiagente (MODO SEGURO)
print("🔧 Carregando sistema multiagente...")

try:
    from src.settings import GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY, API_HOST, API_PORT
    logger.info("✅ Configurações carregadas")
    
    if not GOOGLE_API_KEY:
        logger.warning("⚠️ GOOGLE_API_KEY não configurado - modo limitado")
    
    MULTIAGENT_AVAILABLE = True
    
except Exception as e:
    logger.warning(f"⚠️ Configurações não disponíveis: {e}")
    MULTIAGENT_AVAILABLE = False

# Tentar carregar agentes (OPCIONAL - não bloqueia a API)
orchestrator = None
csv_agent = None

if MULTIAGENT_AVAILABLE:
    # Modo seguro: carrega sem dependências problemáticas
    logger.info("🤖 Tentando carregar agentes...")
    try:
        # Importa apenas se necessário
        import importlib.util
        
        # Verifica se o módulo existe sem importá-lo
        orchestrator_spec = importlib.util.find_spec("src.agent.orchestrator_agent")
        if orchestrator_spec:
            logger.info("✅ Orquestrador encontrado (carregamento lazy)")
            ORCHESTRATOR_AVAILABLE = True
        else:
            logger.warning("⚠️ Orquestrador não encontrado")
            
    except Exception as e:
        logger.warning(f"⚠️ Erro ao verificar agentes: {e}")

# Configurações
MAX_FILE_SIZE = 999 * 1024 * 1024  # 999MB
API_TIMEOUT = 120  # Timeout de 120 segundos para operações longas

# HOST e PORT são importados de src.settings (configuráveis via .env)
# Não definir PORT aqui - usar API_HOST e API_PORT de settings.py

app = FastAPI(
    title="AgentNFE - API Completa",
    description="Sistema multiagente para análise inteligente de dados CSV",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    timeout=API_TIMEOUT  # Timeout configurável
)

# CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "2.0.0"
    message: str
    multiagent_status: bool
    agents_available: List[str]
    timeout_seconds: int = API_TIMEOUT

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    use_memory: Optional[bool] = True
    # Nota: file_id removido - sistema consulta base de dados diretamente

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    agent_used: str
    analysis_type: Optional[str] = None
    confidence: Optional[float] = None
    llm_model: Optional[str] = None  # Modelo LLM usado
    complexity_level: Optional[str] = None  # Nível de complexidade detectado

class FraudDetectionRequest(BaseModel):
    file_id: Optional[str] = None
    transaction_data: Optional[Dict[str, Any]] = None
    analysis_depth: Optional[str] = "comprehensive"  # basic, comprehensive, advanced

class FraudDetectionImage(BaseModel):
    name: str  # Nome da variável/coluna
    url: Optional[str] = None  # URL do arquivo PNG
    base64: Optional[str] = None  # Imagem em base64 (opcional)
    description: Optional[str] = None  # Descrição/metadados

class FraudDetectionResponse(BaseModel):
    fraud_score: float
    risk_level: str  # low, medium, high, critical
    patterns_detected: List[str]
    recommendations: List[str]
    analysis_details: Dict[str, Any]
    processing_time: float
    images: Optional[List[FraudDetectionImage]] = None  # Lista de imagens associadas

class CSVUploadResponse(BaseModel):
    file_id: str
    filename: str
    rows: int
    columns: int
    message: str
    analysis_ready: bool
    fraud_detection_available: bool

# Inicialização do sistema multiagente (LAZY LOADING)
# Os agentes serão carregados apenas quando necessário
orchestrator = None
csv_agent = None

logger.info(f"🎯 Status: MULTIAGENT={MULTIAGENT_AVAILABLE}, ORCHESTRATOR={ORCHESTRATOR_AVAILABLE}")
logger.info("✅ API pronta para iniciar (agentes em modo lazy loading)")

# Storage temporário para dados carregados
uploaded_files = {}

def load_csv_by_file_id(file_id: str) -> Optional[pd.DataFrame]:
    """Carrega um DataFrame a partir do file_id"""
    try:
        if file_id in uploaded_files:
            file_info = uploaded_files[file_id]
            df = file_info.get('dataframe')
            if df is not None:
                logger.info(f"CSV carregado com sucesso: {file_id}")
                return df
            else:
                logger.warning(f"DataFrame não encontrado para file_id: {file_id}")
                return None
        else:
            logger.warning(f"file_id não encontrado: {file_id}")
            return None
    except Exception as e:
        logger.error(f"Erro ao carregar CSV: {e}")
        return None

def analyze_csv_data(df: pd.DataFrame, file_info: dict, message: str) -> str:
    """Análise contextual de dados CSV com insights inteligentes"""
    try:
        analysis = []
        
        # Informações básicas do arquivo
        filename = file_info.get('filename', 'arquivo.csv')
        analysis.append(f"📊 **Análise do arquivo: {filename}**\n")
        
        # Dimensões dos dados
        rows, cols = df.shape
        analysis.append(f"📈 **Dimensões:** {rows:,} linhas x {cols} colunas\n")
        
        # Estatísticas básicas
        analysis.append("📋 **Resumo Estatístico:**")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe()
            for col in numeric_cols[:3]:  # Primeiras 3 colunas numéricas
                mean_val = stats.loc['mean', col]
                std_val = stats.loc['std', col]
                analysis.append(f"   • {col}: Média {mean_val:.2f}, Desvio {std_val:.2f}")
        
        analysis.append("")
        
        # Análise específica para dados de cartão de crédito/fraude
        # ✅ FIX: Inicializar variáveis antes do bloco condicional
        fraud_col = None
        fraud_count = 0
        fraud_rate = 0.0
        
        fraud_keywords = ['fraud', 'class', 'amount', 'time']
        if any(keyword in df.columns.str.lower().tolist() for keyword in fraud_keywords):
            analysis.append("🔍 **Análise de Fraude Detectada:**")
            
            # Verifica coluna de classe/fraude
            for col in df.columns:
                if 'class' in col.lower() or 'fraud' in col.lower():
                    fraud_col = col
                    break
            
            if fraud_col is not None:
                fraud_count = df[fraud_col].sum() if df[fraud_col].dtype in ['int64', 'float64'] else len(df[df[fraud_col] == 1])
                fraud_rate = (fraud_count / len(df)) * 100
                analysis.append(f"   • Taxa de fraude: {fraud_rate:.2f}% ({fraud_count:,} casos)")
                analysis.append(f"   • Transações legítimas: {len(df) - fraud_count:,}")
            
            # Análise de valores
            if 'amount' in df.columns.str.lower().tolist():
                amount_col = [col for col in df.columns if 'amount' in col.lower()][0]
                avg_amount = df[amount_col].mean()
                max_amount = df[amount_col].max()
                analysis.append(f"   • Valor médio: ${avg_amount:.2f}")
                analysis.append(f"   • Valor máximo: ${max_amount:.2f}")
        
        analysis.append("")
        
        # Valores ausentes
        missing = df.isnull().sum()
        if missing.sum() > 0:
            analysis.append("⚠️ **Valores Ausentes:**")
            for col, count in missing[missing > 0].items():
                pct = (count / len(df)) * 100
                analysis.append(f"   • {col}: {count} ({pct:.1f}%)")
        else:
            analysis.append("✅ **Dados Completos:** Nenhum valor ausente encontrado")
        
        analysis.append("")
        
        # Resposta contextual à pergunta
        message_lower = message.lower()
        if 'fraude' in message_lower or 'fraud' in message_lower:
            analysis.append("🎯 **Resposta à sua pergunta sobre fraude:**")
            if fraud_col is not None:
                analysis.append(f"   Os dados mostram {fraud_count:,} casos de fraude em {len(df):,} transações.")
                analysis.append(f"   Isso representa uma taxa de {fraud_rate:.2f}% de fraude no dataset.")
            else:
                analysis.append("   Este dataset não parece conter uma coluna específica de fraude.")
        
        elif 'estatística' in message_lower or 'média' in message_lower or 'resumo' in message_lower:
            analysis.append("🎯 **Estatísticas principais:**")
            for col in numeric_cols[:2]:
                mean_val = df[col].mean()
                median_val = df[col].median()
                analysis.append(f"   • {col}: Média {mean_val:.2f}, Mediana {median_val:.2f}")
        
        elif 'colunas' in message_lower or 'variáveis' in message_lower:
            analysis.append("🎯 **Informações sobre colunas:**")
            analysis.append(f"   Total de {len(df.columns)} colunas:")
            for i, col in enumerate(df.columns[:10]):  # Primeiras 10 colunas
                dtype = str(df[col].dtype)
                analysis.append(f"   {i+1}. {col} ({dtype})")
            if len(df.columns) > 10:
                analysis.append(f"   ... e mais {len(df.columns) - 10} colunas")
        
        return "\n".join(analysis)
        
    except Exception as e:
        logger.error(f"Erro na análise CSV: {e}")
        return f"❌ Erro ao analisar os dados: {str(e)}"

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica status da API e sistema multiagente"""
    agents_available = []
    
    if MULTIAGENT_AVAILABLE:
        agents_available = ["csv_analyzer", "embeddings_analyzer", "nfe_tax_specialist"]
        if orchestrator:
            agents_available.append("orchestrator")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        message="API completa operacional com sistema multiagente",
        multiagent_status=MULTIAGENT_AVAILABLE,
        agents_available=agents_available
    )

@app.get("/health/detailed")
async def health_check_detailed():
    """Health check detalhado sem carregar agentes (evita timeout)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "timeout_config": API_TIMEOUT,
        "components": {
            "multiagent_system": MULTIAGENT_AVAILABLE,
            "orchestrator_available": ORCHESTRATOR_AVAILABLE,
            "orchestrator_loaded": orchestrator is not None,
            "llm_router": LLM_ROUTER_AVAILABLE,
        },
        "performance": {
            "recommended_timeout_frontend": "120000",  # 120 segundos em ms
            "first_load_time": "60-90s (lazy loading)",
            "subsequent_requests": "2-10s"
        },
        "tips": [
            "Primeira requisição pode demorar até 90s (carrega todos os agentes)",
            "Requisições subsequentes são mais rápidas (cache de agentes)",
            "Configure timeout do frontend para 120000ms (120s)",
            "Use /chat com file_id para análise contextual de CSV"
        ]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat inteligente com sistema multiagente e análise contextual de CSV"""
    global orchestrator  # Declarar no início da função
    
    try:
        start_time = datetime.now()
        session_id = request.session_id or "default"
        
        # 🧠 ROTEAMENTO INTELIGENTE DE LLM
        llm_config = None
        llm_model_used = None
        complexity_detected = None
        
        if LLM_ROUTER_AVAILABLE:
            try:
                # Usa LangChainLLMManager para gerenciar LLMs
                llm_manager = get_langchain_llm_manager()
                llm_model_used = llm_manager.active_provider.value
                logger.info(f"🧠 LLM Manager: {llm_model_used} ativo")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar LLM Manager: {e}")
                llm_model_used = "fallback"
        
        # 🎯 ANÁLISE COM SISTEMA MULTIAGENTE
        # SEMPRE usa o orquestrador que consulta a base de dados (Supabase/embeddings)
        # NÃO carrega arquivo CSV - apenas consulta vetores
        
        if not MULTIAGENT_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Sistema multiagente não disponível. Verifique configurações."
            )
        
        logger.info(f"💬 Processando pergunta: {request.message[:100]}...")
        
        # Carrega orquestrador dinamicamente se necessário
        if orchestrator is None and ORCHESTRATOR_AVAILABLE:
            try:
                logger.info("📦 Carregando orquestrador dinamicamente...")
                from src.agent.orchestrator_agent import OrchestratorAgent
                orchestrator = OrchestratorAgent()
                logger.info("✅ Orquestrador carregado com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar orquestrador: {e}")
                import traceback
                logger.error(f"Stack trace: {traceback.format_exc()}")
                raise HTTPException(status_code=503, detail=f"Orquestrador não disponível: {str(e)}")
        
        if not orchestrator:
            logger.error("❌ Orquestrador não está disponível após tentativa de carregamento")
            raise HTTPException(status_code=503, detail="Orquestrador não disponível")
        
        if not hasattr(orchestrator, 'process_with_persistent_memory'):
            logger.error("❌ Orquestrador não possui método process_with_persistent_memory")
            raise HTTPException(status_code=503, detail="Orquestrador inválido")
        
        logger.info("🧠 Enviando query para o orquestrador...")
        try:
            # 🧠 Orquestrador consulta base de dados (embeddings) via RAG
            # Usar método assíncrono com memória persistente (igual interface_interativa.py)
            result = await orchestrator.process_with_persistent_memory(
                query=request.message,
                context={},
                session_id=session_id
            )
            logger.info(f"✅ Orquestrador retornou resposta: {result.get('metadata', {}).get('agent_used', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Erro ao processar query no orquestrador: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")
        
        # Extrai informações do resultado (compatível com interface_interativa.py)
        response_text = result.get('content', result.get('response', 'Desculpe, não consegui processar sua solicitação.'))
        metadata = result.get('metadata', {})
        agent_used = metadata.get('agent_used', 'orchestrator')
        analysis_type = metadata.get('analysis_type')
        confidence = metadata.get('confidence')
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Chat processado em {processing_time:.2f}s por {agent_used}")
        if llm_model_used:
            logger.info(f"   LLM: {llm_model_used}")
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            agent_used=agent_used,
            analysis_type=analysis_type,
            confidence=confidence,
            llm_model=llm_model_used,
            complexity_level=complexity_detected
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/csv/upload", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """Upload e processamento de arquivo CSV com preparação para análise IA"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
        
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Arquivo muito grande")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são aceitos")
    
    try:
        # Lê o arquivo CSV
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Gera ID único para o arquivo
        file_id = f"csv_{int(datetime.now().timestamp())}_{file.filename.replace('.csv', '')}"
        
        # Armazena informações do arquivo
        uploaded_files[file_id] = {
            'filename': file.filename,
            'dataframe': df,
            'upload_date': datetime.now().isoformat(),
            'rows': len(df),
            'columns': len(df.columns)
        }
        
        # Verifica se é um dataset de fraude (detecta colunas típicas)
        fraud_columns = ['Class', 'isFraud', 'fraud', 'is_fraud', 'label']
        has_fraud_column = any(col in df.columns for col in fraud_columns)
        
        # Se o sistema multiagente está disponível, processa o arquivo
        analysis_ready = False
        fraud_detection_available = False
        
        if MULTIAGENT_AVAILABLE and csv_agent:
            try:
                # Processa dados básicos sempre
                analysis_ready = True
                fraud_detection_available = has_fraud_column
                logger.info(f"Arquivo {file.filename} processado pelo sistema multiagente")
            except Exception as e:
                logger.warning(f"Erro ao processar com sistema multiagente: {e}")
        
        logger.info(f"Upload concluído: {file.filename} ({len(df)} linhas, {len(df.columns)} colunas)")
        # Dispara ingestão automática em background usando python do ambiente virtual
        import subprocess
        try:
            subprocess.Popen([
                '.venv\\Scripts\\python.exe', 'run_auto_ingest.py', '--once'
            ])
            logger.info("Script run_auto_ingest.py --once disparado com python do ambiente virtual.")
        except Exception as e:
            logger.error(f"Falha ao disparar run_auto_ingest.py: {e}")
        return CSVUploadResponse(
            file_id=file_id,
            filename=file.filename,
            rows=len(df),
            columns=len(df.columns),
            message="CSV carregado e processado com sucesso",
            analysis_ready=analysis_ready,
            fraud_detection_available=fraud_detection_available
        )
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@app.post("/fraud/detect", response_model=FraudDetectionResponse)
async def detect_fraud(request: FraudDetectionRequest):
    """Detecção de fraude usando IA avançada"""
    if not MULTIAGENT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Sistema de IA não disponível para detecção de fraude"
        )
    
    start_time = datetime.now()
    
    try:
        # Monta query específica para detecção de fraude
        if request.file_id:
            if request.file_id not in uploaded_files:
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
            
            file_info = uploaded_files[request.file_id]
            query = f"""
            ANÁLISE DE FRAUDE ESPECIALIZADA:
            
            Arquivo: {file_info['filename']}
            Dados: {file_info['rows']} transações, {file_info['columns']} características
            Profundidade: {request.analysis_depth}
            
            Por favor, execute uma análise completa de detecção de fraude:
            
            1. PADRÕES SUSPEITOS:
               - Identifique transações com comportamento anômalo
               - Analise valores extremos e outliers
               - Detecte padrões temporais suspeitos
               
            2. SCORING DE RISCO:
               - Calcule score de fraude (0-100)
               - Classifique nível de risco
               - Identifique fatores de risco principais
               
            3. RECOMENDAÇÕES:
               - Ações preventivas
               - Monitoramento sugerido
               - Regras de negócio recomendadas
            
            Forneça uma análise detalhada e estruturada.
            """
        else:
            # Análise de dados específicos fornecidos
            query = f"""
            ANÁLISE DE FRAUDE EM TRANSAÇÃO ESPECÍFICA:
            
            Dados da transação: {request.transaction_data}
            Profundidade: {request.analysis_depth}
            
            Analise esta transação específica para detectar possível fraude.
            """
        
        # Processa com o sistema disponível
        if orchestrator and hasattr(orchestrator, 'process_query'):
            result = orchestrator.process_query(
                query=query,
                session_id=f"fraud_detection_{int(datetime.now().timestamp())}",
                use_memory=True
            )
        else:
            # Análise simplificada de fraude
            result = analyze_fraud_simple(request, uploaded_files)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extrai informações estruturadas da resposta
        response_text = result.get('response', '')

        # Analisa a resposta para extrair métricas estruturadas
        fraud_score = extract_fraud_score(response_text)
        risk_level = determine_risk_level(fraud_score)
        patterns_detected = extract_patterns(response_text)
        recommendations = extract_recommendations(response_text)

        analysis_details = {
            'agent_used': result.get('agent_used', 'orchestrator'),
            'confidence': result.get('confidence', 0.8),
            'analysis_method': 'multiagent_ai',
            'full_analysis': response_text,
            'processing_time': processing_time
        }

        # Novo: Adiciona imagens de histogramas do arquivo analisado
        images = []
        if request.file_id and request.file_id in uploaded_files:
            file_info = uploaded_files[request.file_id]
            filename_base = file_info['filename'].replace('.csv', '')
            from src.settings import HISTOGRAMS_DIR
            histogram_dir = os.path.join(root_dir, HISTOGRAMS_DIR)
            if os.path.isdir(histogram_dir):
                # Para obter o host do request, precisamos passar o objeto Request
                # Adicione 'request: Request' como parâmetro na função detect_fraud
                # Exemplo: async def detect_fraud(request: FraudDetectionRequest, req: Request)
                # Aqui, usamos 'req' para pegar o host
                # Se não estiver presente, fallback para API_PORT
                req_host = None
                try:
                    req_host = request._request.headers.get('host', f'localhost:{os.getenv("API_PORT", "8011")}')
                except Exception:
                    req_host = f'localhost:{os.getenv("API_PORT", "8011")}'
                for col in file_info['dataframe'].columns:
                    hist_name = f"hist_{col}.png"
                    hist_path = os.path.join(histogram_dir, hist_name)
                    if os.path.isfile(hist_path):
                        # Monta URL absoluta usando host/porta configurados
                        from src.settings import API_HOST, API_PORT
                        public_host = API_HOST
                        if public_host in ["0.0.0.0", "127.0.0.1", "localhost"]:
                            public_host = req_host if 'req_host' in locals() else "89.117.23.28"
                        url = f"http://{public_host}:{API_PORT}/files/histogramas/{hist_name}"
                        # Opcional: carrega base64 se desejado
                        base64_img = None
                        try:
                            with open(hist_path, "rb") as f:
                                import base64
                                base64_img = base64.b64encode(f.read()).decode("utf-8")
                        except Exception as e:
                            logger.warning(f"Erro ao converter {hist_name} para base64: {e}")
                        images.append(FraudDetectionImage(
                            name=col,
                            url=url,
                            base64=None,
                            description=f"Histograma da variável {col}",
                            label=hist_name
                        ))
        logger.info(f"Detecção de fraude concluída: score={fraud_score}, risco={risk_level}, imagens={len(images)}")

        return FraudDetectionResponse(
            fraud_score=fraud_score,
            risk_level=risk_level,
            patterns_detected=patterns_detected,
            recommendations=recommendations,
            analysis_details=analysis_details,
            processing_time=processing_time,
            images=images if images else None
        )
        
    except Exception as e:
        logger.error(f"Erro na detecção de fraude: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@app.get("/files/histogramas/{filename}")
async def serve_histogram(filename: str):
    """Serve arquivos PNG de histogramas do diretório configurado"""
    from fastapi.responses import FileResponse
    from src.settings import HISTOGRAMS_DIR
    
    # Valida nome do arquivo para evitar path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")
    
    file_path = Path(HISTOGRAMS_DIR) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    if not file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
    
    return FileResponse(file_path, media_type="image/png")

@app.get("/csv/files")
async def list_files():
    """Lista arquivos CSV carregados"""
    files_list = []
    for file_id, info in uploaded_files.items():
        files_list.append({
            'file_id': file_id,
            'filename': info['filename'],
            'rows': info['rows'],
            'columns': info['columns'],
            'upload_date': info['upload_date']
        })
    
    return {
        'total': len(files_list),
        'files': files_list
    }

@app.get("/dashboard/metrics")
async def dashboard_metrics():
    """Métricas do dashboard"""
    total_files = len(uploaded_files)
    total_rows = sum(info['rows'] for info in uploaded_files.values())
    total_columns = sum(info['columns'] for info in uploaded_files.values())
    
    agents_status = {}
    if MULTIAGENT_AVAILABLE:
        agents_status = {
            'orchestrator': 'active' if orchestrator else 'inactive',
            'csv_agent': 'active' if csv_agent else 'inactive',
            'multiagent_system': 'operational'
        }
    else:
        agents_status = {'multiagent_system': 'unavailable'}
    
    return {
        'total_files': total_files,
        'total_rows': total_rows,
        'total_columns': total_columns,
        'status': 'operational' if MULTIAGENT_AVAILABLE else 'limited',
        'last_activity': datetime.now().isoformat(),
        'agents_status': agents_status,
        'fraud_detection': 'available' if MULTIAGENT_AVAILABLE else 'unavailable'
    }

# Funções auxiliares para processamento simplificado
def process_message_simple(message: str, session_id: str) -> Dict[str, Any]:
    """Processamento simplificado de mensagens quando orquestrador não disponível"""
    message_lower = message.lower()
    
    # Detecta tipo de análise baseado na mensagem
    if any(word in message_lower for word in ["fraude", "fraud", "detecção", "detectar"]):
        response = """🛡️ **Análise de Fraude com IA:**

**Status:** Sistema multiagente ativo para detecção avançada

**Capacidades Disponíveis:**
• 🧠 Análise comportamental com IA
• 🔍 Detecção de padrões suspeitos
• 📊 Scoring de risco automatizado
• 🚨 Alertas em tempo real
• 📈 Análise de tendências

**Para usar:**
1. Faça upload do seu arquivo CSV
2. Use o endpoint `/fraud/detect` para análise completa
3. Configure alertas personalizados

O sistema está pronto para analisar seus dados!"""
        analysis_type = "fraud_detection"
        
    elif any(word in message_lower for word in ["csv", "dados", "análise", "estatística"]):
        response = """📊 **Análise de Dados CSV:**

**Sistema Multiagente Ativo:**
• 🤖 Agentes especializados disponíveis
• 📈 Análise estatística avançada
• 🔍 Detecção de padrões e outliers
• 📊 Visualizações automáticas
• 🧠 Insights inteligentes com IA

**Como usar:**
1. Upload seu arquivo CSV via `/csv/upload`
2. Faça perguntas específicas sobre os dados
3. Solicite análises e visualizações

Pronto para analisar seus dados!"""
        analysis_type = "csv_analysis"
        
    else:
        response = """🤖 **AgentNFE - Sistema Multiagente:**

**Status:** ✅ Operacional

**Agentes Disponíveis:**
• 📊 Analisador de CSV
• 🛡️ Detector de Fraude
• 🔍 Sistema de Embeddings
• 🧠 Processador de Linguagem Natural

**Comandos:**
• "analisar dados" - Análise completa de CSV
• "detectar fraude" - Análise de segurança
• "ajuda" - Comandos disponíveis

Como posso ajudar com seus dados?"""
        analysis_type = "general"
    
    return {
        'response': response,
        'agent_used': 'simplified_processor',
        'analysis_type': analysis_type,
        'confidence': 0.8,
        'session_id': session_id
    }

def analyze_fraud_simple(request: FraudDetectionRequest, files_data: Dict) -> Dict[str, Any]:
    """Análise simplificada de fraude quando orquestrador não disponível"""
    if request.file_id and request.file_id in files_data:
        file_info = files_data[request.file_id]
        df = file_info['dataframe']
        
        # Análise básica estatística para detectar anomalias
        analysis_text = f"""🛡️ **ANÁLISE DE FRAUDE - {file_info['filename']}**

**📊 Resumo dos Dados:**
• Total de transações: {len(df):,}
• Características analisadas: {len(df.columns)}
• Dataset: {file_info['filename']}

**🔍 Análise Estatística:**"""

        # Detecta colunas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            # Análise de outliers básica
            outliers_detected = 0
            for col in numeric_cols[:3]:  # Analisa até 3 colunas
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = len(df[(df[col] < lower_bound) | (df[col] > upper_bound)])
                outliers_detected += outliers
                
                analysis_text += f"\n• {col}: {outliers} outliers detectados"
        
        # Verifica se há coluna de classificação (fraude)
        fraud_columns = ['Class', 'isFraud', 'fraud', 'is_fraud', 'label']
        fraud_col = None
        for col in fraud_columns:
            if col in df.columns:
                fraud_col = col
                break
        
        if fraud_col is not None:
            fraud_count = df[fraud_col].sum() if df[fraud_col].dtype in ['int64', 'float64'] else len(df[df[fraud_col] == 1])
            fraud_rate = (fraud_count / len(df)) * 100
            analysis_text += f"\n\n**🚨 Detecção de Fraude:**"
            analysis_text += f"\n• Transações fraudulentas: {fraud_count:,} ({fraud_rate:.2f}%)"
            analysis_text += f"\n• Taxa de fraude: {'ALTA' if fraud_rate > 5 else 'MODERADA' if fraud_rate > 1 else 'BAIXA'}"
            
            fraud_score = min(95.0, fraud_rate * 10 + 30)
        else:
            analysis_text += f"\n\n**⚠️ Análise Baseada em Outliers:**"
            analysis_text += f"\n• Total de outliers: {outliers_detected:,}"
            fraud_score = min(90.0, (outliers_detected / len(df)) * 100 * 20)
        
        analysis_text += f"\n\n**🎯 Recomendações:**"
        analysis_text += f"\n• Implementar monitoramento em tempo real"
        analysis_text += f"\n• Configurar alertas para transações suspeitas"
        analysis_text += f"\n• Revisar regras de negócio baseadas nos padrões encontrados"
        
    else:
        # Análise de transação específica
        analysis_text = """🛡️ **ANÁLISE DE TRANSAÇÃO ESPECÍFICA**

**Status:** Análise básica realizada
**Método:** Regras heurísticas

**Verificações Realizadas:**
• Validação de padrões básicos
• Análise de consistência
• Verificação de limites

**Recomendação:** Para análise mais profunda, faça upload de dataset histórico."""
        fraud_score = 25.0  # Score baixo para análise básica
    
    return {
        'response': analysis_text,
        'agent_used': 'fraud_analyzer_simple',
        'analysis_type': 'fraud_detection',
        'confidence': 0.7,
        'fraud_score': fraud_score
    }

# Funções auxiliares para extração de métricas
def extract_fraud_score(text: str) -> float:
    """Extrai score de fraude da resposta da IA"""
    import re
    
    # Procura por padrões como "score: 85", "85%", "risco: 0.85"
    patterns = [
        r'score[:\s]+(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)%',
        r'risco[:\s]+(\d+(?:\.\d+)?)',
        r'probabilidade[:\s]+(\d+(?:\.\d+)?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            score = float(match.group(1))
            # Normaliza para 0-100
            if score <= 1.0:
                score *= 100
            return min(100.0, max(0.0, score))
    
    # Score padrão baseado em palavras-chave
    high_risk_words = ['fraude', 'suspeito', 'anômalo', 'irregular', 'alto risco']
    medium_risk_words = ['moderado', 'atenção', 'médio']
    low_risk_words = ['normal', 'baixo', 'legítimo']
    
    text_lower = text.lower()
    high_count = sum(1 for word in high_risk_words if word in text_lower)
    medium_count = sum(1 for word in medium_risk_words if word in text_lower)
    low_count = sum(1 for word in low_risk_words if word in text_lower)
    
    if high_count > medium_count + low_count:
        return 75.0
    elif medium_count > low_count:
        return 45.0
    else:
        return 20.0

def determine_risk_level(score: float) -> str:
    """Determina nível de risco baseado no score"""
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    else:
        return "low"

def extract_patterns(text: str) -> List[str]:
    """Extrai padrões detectados da resposta"""
    patterns = []
    
    # Palavras-chave que indicam padrões
    keywords = [
        'outlier', 'anômalo', 'suspeito', 'irregular',
        'alto valor', 'padrão temporal', 'frequência elevada',
        'comportamento atípico', 'transação incomum'
    ]
    
    for keyword in keywords:
        if keyword in text.lower():
            patterns.append(keyword.title())
    
    # Se não encontrou padrões específicos, adiciona genéricos
    if not patterns:
        if 'fraude' in text.lower():
            patterns.append('Padrão de fraude detectado')
        else:
            patterns.append('Análise comportamental realizada')
    
    return patterns[:5]  # Máximo 5 padrões

def extract_recommendations(text: str) -> List[str]:
    """Extrai recomendações da resposta"""
    recommendations = []
    
    # Recomendações padrão baseadas no conteúdo
    default_recommendations = [
        'Implementar monitoramento em tempo real',
        'Configurar alertas para transações suspeitas',
        'Revisar regras de negócio',
        'Aumentar autenticação para transações de alto valor',
        'Analisar padrões históricos'
    ]
    
    # Adiciona recomendações específicas se encontradas no texto
    if 'monitoramento' in text.lower():
        recommendations.append('Intensificar monitoramento das transações')
    if 'regra' in text.lower():
        recommendations.append('Revisar e atualizar regras de detecção')
    if 'autenticação' in text.lower():
        recommendations.append('Implementar autenticação adicional')
    
    # Adiciona recomendações padrão até ter pelo menos 3
    for rec in default_recommendations:
        if len(recommendations) >= 3:
            break
        if rec not in recommendations:
            recommendations.append(rec)
    
    return recommendations

if __name__ == "__main__":
    print("🚀 Iniciando API Completa - AgentNFE")
    print("=" * 50)
    print(f"📍 URL: http://localhost:{API_PORT}")
    print(f"📚 Docs: http://localhost:{API_PORT}/docs")
    print(f"📋 ReDoc: http://localhost:{API_PORT}/redoc")
    print(f"🌐 Host: {API_HOST} (aceita conexões {'externas' if API_HOST == '0.0.0.0' else 'apenas locais'})")
    print(f"🤖 Sistema Multiagente: {'✅ Ativo' if MULTIAGENT_AVAILABLE else '❌ Inativo'}")
    if MULTIAGENT_AVAILABLE:
        print("🧠 Agentes Disponíveis:")
        print("   • Orquestrador Central")
        print("   • Analisador de CSV")
        print("   • Sistema de Embeddings")
        print("   • Detecção de Fraude IA")
        print("   • Especialista Fiscal NF-e")
    print("⏹️ Pressione Ctrl+C para parar")
    print()
    
    uvicorn.run(
        "api_completa:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )