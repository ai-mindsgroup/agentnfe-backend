# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
import uuid
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NFe Tax Specialist API",
    description="API para análise e validação tributária de notas fiscais",
    version="1.0.0"
)

# Configure CORS para permitir o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELOS CORRIGIDOS E EXPANDIDOS
# ============================================================================

class CFOPValidationRequest(BaseModel):
    cfop: str = Field(..., min_length=4, max_length=4)

    class Config:
        json_schema_extra = {
            "example": {
                "cfop": "5102"
            }
        }

class CFOPValidationResponse(BaseModel):
    valido: bool
    cfop: str
    natureza: Optional[str] = None
    descricao_grupo: Optional[str] = None
    destino: Optional[str] = None
    tributacao: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None

class NCMValidationRequest(BaseModel):
    ncm: str = Field(..., min_length=8, max_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "ncm": "84714100"
            }
        }

class NCMValidationResponse(BaseModel):
    valido: bool
    ncm: str
    ncm_formatado: Optional[str] = None
    capitulo: Optional[str] = None
    categoria: Optional[str] = None
    erro: Optional[str] = None

# Novos modelos para suportar mais funcionalidades
class TaxQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Pergunta sobre tributação")
    context: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Qual a diferença entre CFOP 5102 e 6102?",
                "context": {"tipo": "consulta"}
            }
        }

class TaxQueryResponse(BaseModel):
    success: bool
    resposta: str
    contexto: Optional[str] = None
    error: Optional[str] = None

class FileInfo(BaseModel):
    file_id: str
    filename: str
    rows: int
    columns: int
    upload_date: str
    size_kb: Optional[int] = None

class FileListResponse(BaseModel):
    files: List[FileInfo]
    total: int

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    message: str
    version: str

# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "API NFe Tax Specialist está funcionando!", 
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "validation": {
                "cfop": "/api/validar-cfop",
                "ncm": "/api/validar-ncm"
            },
            "consultation": "/api/consultar-tributacao",
            "files": "/api/files"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check para o frontend"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        message="API funcionando normalmente",
        version="1.0.0"
    )

@app.post("/api/validar-cfop", response_model=CFOPValidationResponse)
async def validar_cfop(request: CFOPValidationRequest):
    try:
        logger.info(f"Validando CFOP: {request.cfop}")
        
        # Lógica mock de validação
        cfop_valido = await validar_cfop_impl(request.cfop)
        return CFOPValidationResponse(**cfop_valido)
        
    except Exception as e:
        logger.error(f"Erro ao validar CFOP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/api/validar-ncm", response_model=NCMValidationResponse)
async def validar_ncm(request: NCMValidationRequest):
    try:
        logger.info(f"Validando NCM: {request.ncm}")
        
        # Lógica mock de validação
        ncm_valido = await validar_ncm_impl(request.ncm)
        return NCMValidationResponse(**ncm_valido)
        
    except Exception as e:
        logger.error(f"Erro ao validar NCM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/api/consultar-tributacao", response_model=TaxQueryResponse)
async def consultar_tributacao(request: TaxQueryRequest):
    """Endpoint para consultas sobre legislação tributária"""
    try:
        logger.info(f"Consulta tributária: {request.query}")
        
        resposta = await processar_consulta_tributaria(request.query, request.context)
        return TaxQueryResponse(
            success=True,
            resposta=resposta,
            contexto="Consulta processada com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro na consulta tributária: {str(e)}")
        return TaxQueryResponse(
            success=False,
            resposta="",
            error=f"Erro ao processar consulta: {str(e)}"
        )

# ============================================================================
# ENDPOINTS DE ARQUIVOS (PARA O FILESLIST)
# ============================================================================

@app.get("/api/files", response_model=FileListResponse)
async def list_files():
    """Lista arquivos disponíveis para análise"""
    try:
        logger.info("Listando arquivos disponíveis")
        
        files = await get_available_files()
        return FileListResponse(
            files=files,
            total=len(files)
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/csv/files", response_model=FileListResponse)
async def list_csv_files():
    """Endpoint alternativo para compatibilidade com o frontend existente"""
    return await list_files()

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para upload de arquivos CSV"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Apenas arquivos CSV são permitidos")
        
        file_id = str(uuid.uuid4())
        file_content = await file.read()
        
        # Simula processamento do arquivo
        rows = len(file_content.decode('utf-8').split('\n')) - 1  # Exclui header
        columns = len(file_content.decode('utf-8').split('\n')[0].split(',')) if rows > 0 else 0
        
        logger.info(f"Arquivo {file.filename} uploadado com {rows} linhas e {columns} colunas")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "rows": rows,
            "columns": columns,
            "upload_date": datetime.now().isoformat(),
            "message": "Arquivo processado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")
    

@app.get("/api/metrics")
async def get_metrics():
    """Endpoint específico para métricas do dashboard"""
    files = await get_available_files()
    
    total_files = len(files)
    total_rows = sum(file.rows for file in files)
    total_columns = sum(file.columns for file in files)
    
    return {
        "total_files": total_files,
        "total_rows": total_rows,
        "total_columns": total_columns,
        "status": "healthy",
        "backend_version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "average_rows_per_file": total_rows / total_files if total_files > 0 else 0
    }

# ============================================================================
# IMPLEMENTAÇÕES MOCK
# ============================================================================

async def validar_cfop_impl(cfop: str) -> Dict[str, Any]:
    cfops_validos = {
        "5102": {
            "valido": True,
            "cfop": cfop,
            "natureza": "SAÍDA",
            "descricao_grupo": "Venda de mercadoria dentro do estado",
            "destino": "Dentro do estado",
            "tributacao": {
                "tipo": "Saída",
                "gera_credito": False,
                "gera_debito": True,
                "icms": "Incide normalmente"
            }
        },
        "6102": {
            "valido": True,
            "cfop": cfop,
            "natureza": "ENTRADA",
            "descricao_grupo": "Compra de mercadoria dentro do estado",
            "destino": "Dentro do estado",
            "tributacao": {
                "tipo": "Entrada",
                "gera_credito": True,
                "gera_debito": False,
                "icms": "Incide normalmente"
            }
        },
        "5405": {
            "valido": True,
            "cfop": cfop,
            "natureza": "SAÍDA",
            "descricao_grupo": "Venda de mercadoria para outros estados",
            "destino": "Fora do estado",
            "tributacao": {
                "tipo": "Saída interestadual",
                "gera_credito": False,
                "gera_debito": True,
                "icms": "Diferencial de alíquota"
            }
        },
        "1403": {
            "valido": True,
            "cfop": cfop,
            "natureza": "ENTRADA",
            "descricao_grupo": "Entrada para industrialização",
            "destino": "Dentro do estado",
            "tributacao": {
                "tipo": "Entrada com benefício",
                "gera_credito": True,
                "gera_debito": False,
                "icms": "Com redução de base"
            }
        }
    }
    
    return cfops_validos.get(cfop, {
        "valido": False,
        "cfop": cfop,
        "erro": f"CFOP {cfop} não encontrado"
    })

async def validar_ncm_impl(ncm: str) -> Dict[str, Any]:
    ncms_validos = {
        "84714100": {
            "valido": True,
            "ncm": ncm,
            "ncm_formatado": "8471.41.00",
            "capitulo": "84",
            "categoria": "Máquinas e equipamentos elétricos"
        },
        "22030000": {
            "valido": True,
            "ncm": ncm,
            "ncm_formatado": "2203.00.00",
            "capitulo": "22",
            "categoria": "Bebidas, líquidos alcoólicos e vinagres"
        },
        "87032300": {
            "valido": True,
            "ncm": ncm,
            "ncm_formatado": "8703.23.00",
            "capitulo": "87",
            "categoria": "Veículos automóveis"
        },
        "30049099": {
            "valido": True,
            "ncm": ncm,
            "ncm_formatado": "3004.90.99",
            "capitulo": "30",
            "categoria": "Medicamentos"
        }
    }
    
    return ncms_validos.get(ncm, {
        "valido": False,
        "ncm": ncm,
        "erro": f"NCM {ncm} não encontrado"
    })

async def processar_consulta_tributaria(query: str, context: Optional[Dict] = None) -> str:
    """Processa consultas sobre legislação tributária"""
    query_lower = query.lower()
    
    if 'cfop' in query_lower and '5102' in query_lower:
        return """O CFOP 5102 é utilizado para venda de mercadoria dentro do estado (operacao interestadual).
        
Características principais:
• Natureza: SAÍDA
• Destino: Dentro do estado
• Tributação: ICMS incide normalmente
• Gera débito fiscal para o vendedor
• Não gera crédito fiscal para o comprador

É um dos CFOPs mais comuns para vendas no mesmo estado."""

    elif 'cfop' in query_lower and '6102' in query_lower:
        return """O CFOP 6102 é utilizado para compra de mercadoria dentro do estado.
        
Características principais:
• Natureza: ENTRADA  
• Destino: Dentro do estado
• Tributação: ICMS incide normalmente
• Gera crédito fiscal para o comprador
• Não gera débito fiscal para o vendedor

Utilizado quando a empresa adquire mercadorias de fornecedor do mesmo estado."""

    elif 'diferença' in query_lower and '5102' in query_lower and '6102' in query_lower:
        return """Principais diferenças entre CFOP 5102 e 6102:

CFOP 5102 - VENDA (Saída):
• Operação de venda/saída de mercadoria
• Empresa emite a nota fiscal
• Gera débito fiscal (empresa deve pagar ICMS)
• Não gera crédito fiscal

CFOP 6102 - COMPRA (Entrada):
• Operação de compra/entrada de mercadoria  
• Empresa recebe a nota fiscal
• Gera crédito fiscal (empresa pode compensar ICMS)
• Não gera débito fiscal

Resumo: 5102 = Venda, 6102 = Compra (ambos dentro do estado)."""

    else:
        return f"""Consulta sobre: {query}

Esta é uma resposta simulada do assistente tributário. Em uma implementação real, esta funcionalidade seria integrada com um sistema de IA ou base de dados legislativa.

Para validações específicas, recomendo:
• Use /api/validar-cfop para validar códigos CFOP
• Use /api/validar-ncm para validar códigos NCM
• Consulte a legislação específica para casos complexos"""

async def get_available_files() -> List[FileInfo]:
    """Retorna lista de arquivos disponíveis (mock)"""
    return [
        FileInfo(
            file_id="demo-cfop-001",
            filename="dados_cfop_demonstracao.csv",
            rows=150,
            columns=8,
            upload_date="2024-01-15",
            size_kb=45
        ),
        FileInfo(
            file_id="demo-ncm-002", 
            filename="dados_ncm_amostra.csv",
            rows=89,
            columns=6,
            upload_date="2024-01-15",
            size_kb=28
        ),
        FileInfo(
            file_id="notas-fiscais-003",
            filename="notas_fiscais_2024.csv",
            rows=245,
            columns=12,
            upload_date="2024-01-10",
            size_kb=78
        ),
        FileInfo(
            file_id="analise-tributaria-004",
            filename="analise_tributaria_setembro.csv",
            rows=512,
            columns=15,
            upload_date="2024-01-08",
            size_kb=156
        )
    ]

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)