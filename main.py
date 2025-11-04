# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

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
# MODELOS CORRIGIDOS
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

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {"message": "API NFe Tax Specialist está funcionando!", "status": "online"}

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
        }
    }
    
    return ncms_validos.get(ncm, {
        "valido": False,
        "ncm": ncm,
        "erro": f"NCM {ncm} não encontrado"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)