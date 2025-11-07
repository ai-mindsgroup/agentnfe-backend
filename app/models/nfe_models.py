"""Modelos Pydantic para API NFe Tax Specialist.

Modelos de request e response para os endpoints de análise tributária.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# MODELOS DE VALIDAÇÃO CFOP
# ============================================================================

class CFOPValidationRequest(BaseModel):
    """Request para validação de CFOP."""
    cfop: str = Field(
        ..., 
        min_length=4, 
        max_length=4,
        description="Código CFOP de 4 dígitos",
        example="5102"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "cfop": "5102"
            }
        }


class CFOPValidationResponse(BaseModel):
    """Response da validação de CFOP."""
    valido: bool = Field(..., description="Se o CFOP é válido")
    cfop: str = Field(..., description="CFOP validado")
    natureza: Optional[str] = Field(None, description="Natureza da operação (ENTRADA/SAÍDA)")
    descricao_grupo: Optional[str] = Field(None, description="Descrição do grupo CFOP")
    destino: Optional[str] = Field(None, description="Destino da operação")
    tributacao: Optional[Dict[str, Any]] = Field(None, description="Informações tributárias")
    erro: Optional[str] = Field(None, description="Mensagem de erro se inválido")

    class Config:
        json_schema_extra = {
            "example": {
                "valido": True,
                "cfop": "5102",
                "natureza": "SAÍDA",
                "descricao_grupo": "Saída ou prestação de serviços para o estado",
                "destino": "Dentro do estado",
                "tributacao": {
                    "tipo": "Saída",
                    "gera_credito": False,
                    "gera_debito": True,
                    "icms": "Incide normalmente"
                }
            }
        }


# ============================================================================
# MODELOS DE VALIDAÇÃO NCM
# ============================================================================

class NCMValidationRequest(BaseModel):
    """Request para validação de NCM."""
    ncm: str = Field(
        ...,
        min_length=8,
        max_length=8,
        description="Código NCM de 8 dígitos",
        example="84714100"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ncm": "84714100"
            }
        }


class NCMValidationResponse(BaseModel):
    """Response da validação de NCM."""
    valido: bool = Field(..., description="Se o NCM é válido")
    ncm: str = Field(..., description="NCM validado")
    ncm_formatado: Optional[str] = Field(None, description="NCM formatado (XX.XX.XX.XX)")
    capitulo: Optional[str] = Field(None, description="Capítulo NCM (primeiros 2 dígitos)")
    categoria: Optional[str] = Field(None, description="Categoria do produto")
    erro: Optional[str] = Field(None, description="Mensagem de erro se inválido")

    class Config:
        json_schema_extra = {
            "example": {
                "valido": True,
                "ncm": "84714100",
                "ncm_formatado": "8471.41.00",
                "capitulo": "84",
                "categoria": "Máquinas e equipamentos elétricos"
            }
        }


# ============================================================================
# MODELOS DE ANÁLISE DE NOTA FISCAL
# ============================================================================

class NotaFiscalAnalysisRequest(BaseModel):
    """Request para análise de nota fiscal."""
    chave_acesso: str = Field(
        ...,
        min_length=44,
        max_length=44,
        description="Chave de acesso da NF-e (44 caracteres)",
        example="33250517579278000168550000000103531030943310"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chave_acesso": "33250517579278000168550000000103531030943310"
            }
        }


class NotaFiscalAnalysisResponse(BaseModel):
    """Response da análise de nota fiscal."""
    success: bool = Field(..., description="Se a análise foi bem-sucedida")
    analise: Optional[Dict[str, Any]] = Field(None, description="Dados da análise tributária")
    error: Optional[str] = Field(None, description="Mensagem de erro se falhou")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "analise": {
                    "chave_acesso": "33250517579278000168550000000103531030943310",
                    "numero": "10353",
                    "data_emissao": "2025-05-17",
                    "emitente": {
                        "cnpj": "17579278000168",
                        "razao_social": "EPI EQUIPAMENTO DE PROTECAO INTELIGENTE LTDA",
                        "uf": "RJ"
                    },
                    "valores": {
                        "valor_nota": 9.00,
                        "soma_itens": 9.00,
                        "divergencia": 0.00
                    },
                    "validacoes": {
                        "cfop": [],
                        "ncm": [],
                        "valores": [],
                        "consistencia": []
                    },
                    "alertas": [],
                    "score_fiscal": 100.0,
                    "recomendacoes": ["✅ Nota fiscal em conformidade tributária"]
                }
            }
        }


# ============================================================================
# MODELOS DE DETECÇÃO DE ANOMALIAS
# ============================================================================

class AnomalyDetectionRequest(BaseModel):
    """Request para detecção de anomalias fiscais."""
    uf_emitente: Optional[str] = Field(
        None,
        max_length=2,
        description="UF do emitente para filtro",
        example="SP"
    )
    data_inicio: Optional[str] = Field(
        None,
        description="Data inicial (YYYY-MM-DD)",
        example="2025-01-01"
    )
    data_fim: Optional[str] = Field(
        None,
        description="Data final (YYYY-MM-DD)",
        example="2025-12-31"
    )
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Limite de resultados",
        example=10
    )

    class Config:
        json_schema_extra = {
            "example": {
                "uf_emitente": "SP",
                "data_inicio": "2025-01-01",
                "data_fim": "2025-12-31",
                "limit": 10
            }
        }


class AnomalyDetectionResponse(BaseModel):
    """Response da detecção de anomalias."""
    success: bool = Field(..., description="Se a detecção foi bem-sucedida")
    total_anomalias: int = Field(..., description="Total de anomalias encontradas")
    anomalias: List[Dict[str, Any]] = Field(..., description="Lista de anomalias detectadas")
    error: Optional[str] = Field(None, description="Mensagem de erro se falhou")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_anomalias": 2,
                "anomalias": [
                    {
                        "tipo": "divergencia_valores",
                        "chave_acesso": "33250517579278000168550000000103531030943310",
                        "severidade": "ALTA",
                        "descricao": "Divergência de valores entre nota e itens: R$ 150.00"
                    }
                ]
            }
        }


# ============================================================================
# MODELOS DE CONSULTA TRIBUTÁRIA
# ============================================================================

class TaxQueryRequest(BaseModel):
    """Request para consulta sobre legislação tributária."""
    query: str = Field(
        ...,
        min_length=10,
        description="Pergunta sobre tributação, CFOP, NCM, etc",
        example="Qual a diferença entre CFOP 5102 e 6102?"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Contexto adicional (chave_acesso, cfop, ncm)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Qual a diferença entre CFOP 5102 e 6102?",
                "context": {
                    "cfop": "5102"
                }
            }
        }


class TaxQueryResponse(BaseModel):
    """Response da consulta tributária."""
    success: bool = Field(..., description="Se a consulta foi bem-sucedida")
    resposta: Optional[str] = Field(None, description="Resposta da consulta")
    contexto: Optional[str] = Field(None, description="Contexto utilizado")
    error: Optional[str] = Field(None, description="Mensagem de erro se falhou")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "resposta": "O CFOP 5102 é usado para vendas dentro do estado...",
                "contexto": "CFOP 5102: Venda de mercadoria dentro do estado"
            }
        }


# ============================================================================
# MODELOS DE BUSCA DE NOTAS SIMILARES
# ============================================================================

class SimilarNotasRequest(BaseModel):
    """Request para busca de notas similares."""
    chave_acesso: str = Field(
        ...,
        min_length=44,
        max_length=44,
        description="Chave de acesso da nota de referência"
    )
    limit: int = Field(
        5,
        ge=1,
        le=20,
        description="Número de notas similares a retornar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chave_acesso": "33250517579278000168550000000103531030943310",
                "limit": 5
            }
        }


class SimilarNotasResponse(BaseModel):
    """Response da busca de notas similares."""
    success: bool = Field(..., description="Se a busca foi bem-sucedida")
    nota_referencia: Optional[str] = Field(None, description="Chave da nota de referência")
    similares: List[Dict[str, Any]] = Field(..., description="Notas similares encontradas")
    error: Optional[str] = Field(None, description="Mensagem de erro se falhou")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "nota_referencia": "33250517579278000168550000000103531030943310",
                "similares": [
                    {
                        "chave_acesso": "33250517579278000168550000000103541030943311",
                        "valor_nota_fiscal": 15.00,
                        "razao_social_emitente": "EMPRESA SIMILAR LTDA"
                    }
                ]
            }
        }


# ============================================================================
# MODELOS DE LISTAGEM DE NOTAS
# ============================================================================

class ListNotasRequest(BaseModel):
    """Request para listagem de notas fiscais."""
    data_inicio: Optional[str] = Field(None, description="Data inicial (YYYY-MM-DD)")
    data_fim: Optional[str] = Field(None, description="Data final (YYYY-MM-DD)")
    uf: Optional[str] = Field(None, max_length=2, description="UF para filtro")
    limit: int = Field(100, ge=1, le=1000, description="Limite de resultados")
    offset: int = Field(0, ge=0, description="Offset para paginação")

    class Config:
        json_schema_extra = {
            "example": {
                "data_inicio": "2025-05-01",
                "data_fim": "2025-05-31",
                "uf": "SP",
                "limit": 100,
                "offset": 0
            }
        }


class ListNotasResponse(BaseModel):
    """Response da listagem de notas fiscais."""
    success: bool = Field(..., description="Se a listagem foi bem-sucedida")
    total: int = Field(..., description="Total de notas encontradas")
    notas: List[Dict[str, Any]] = Field(..., description="Lista de notas fiscais")
    error: Optional[str] = Field(None, description="Mensagem de erro se falhou")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total": 150,
                "notas": [
                    {
                        "chave_acesso": "33250517579278000168550000000103531030943310",
                        "numero": "10353",
                        "data_emissao": "2025-05-17",
                        "valor_nota_fiscal": 9.00,
                        "razao_social_emitente": "EPI LTDA",
                        "uf_emitente": "RJ"
                    }
                ]
            }
        }
