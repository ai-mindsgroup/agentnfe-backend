"""Modelos Pydantic da API.

Este módulo contém todos os modelos de dados da aplicação.
"""
from app.models.nfe_models import (
    CFOPValidationRequest,
    CFOPValidationResponse,
    NCMValidationRequest,
    NCMValidationResponse,
    NotaFiscalAnalysisRequest,
    NotaFiscalAnalysisResponse,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    TaxQueryRequest,
    TaxQueryResponse,
    SimilarNotasRequest,
    SimilarNotasResponse,
    ListNotasRequest,
    ListNotasResponse,
)

__all__ = [
    "CFOPValidationRequest",
    "CFOPValidationResponse",
    "NCMValidationRequest",
    "NCMValidationResponse",
    "NotaFiscalAnalysisRequest",
    "NotaFiscalAnalysisResponse",
    "AnomalyDetectionRequest",
    "AnomalyDetectionResponse",
    "TaxQueryRequest",
    "TaxQueryResponse",
    "SimilarNotasRequest",
    "SimilarNotasResponse",
    "ListNotasRequest",
    "ListNotasResponse",
]
