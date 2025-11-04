"""Router API para NFe Tax Specialist.

Endpoints para análise tributária de Notas Fiscais Eletrônicas:
- Validação de CFOP e NCM
- Análise completa de notas fiscais
- Detecção de anomalias fiscais
- Consultas sobre legislação tributária
- Busca de notas similares
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.models.nfe_models import (
    CFOPValidationRequest, CFOPValidationResponse,
    NCMValidationRequest, NCMValidationResponse,
    NotaFiscalAnalysisRequest, NotaFiscalAnalysisResponse,
    AnomalyDetectionRequest, AnomalyDetectionResponse,
    TaxQueryRequest, TaxQueryResponse,
    SimilarNotasRequest, SimilarNotasResponse,
    ListNotasRequest, ListNotasResponse
)
from src.agent.nfe_tax_specialist_agent import NFeTaxSpecialistAgent
from src.vectorstore.supabase_client import supabase

logger = logging.getLogger(__name__)

# Criar router com prefix e tags
router = APIRouter(
    prefix="/nfe",
    tags=["NFe Tax Specialist"],
    responses={
        404: {"description": "Recurso não encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_nfe_agent() -> NFeTaxSpecialistAgent:
    """Cria instância do agente NFe Tax Specialist."""
    try:
        return NFeTaxSpecialistAgent()
    except Exception as e:
        logger.error(f"Erro ao criar agente NFe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao inicializar agente NFe: {str(e)}"
        )


# ============================================================================
# ENDPOINTS DE VALIDAÇÃO
# ============================================================================

@router.post(
    "/validate/cfop",
    response_model=CFOPValidationResponse,
    summary="Validar CFOP",
    description="Valida um código CFOP e retorna informações tributárias detalhadas"
)
async def validate_cfop(
    request: CFOPValidationRequest,
    agent: NFeTaxSpecialistAgent = Depends(get_nfe_agent)
):
    """
    Valida um código CFOP (Código Fiscal de Operações e Prestações).
    
    **Parâmetros:**
    - **cfop**: Código CFOP de 4 dígitos (ex: 5102, 6102)
    
    **Retorna:**
    - Validação do CFOP
    - Natureza da operação (ENTRADA/SAÍDA)
    - Descrição do grupo
    - Informações tributárias
    """
    try:
        logger.info(f"Validando CFOP: {request.cfop}")
        resultado = agent.validate_cfop(request.cfop)
        return CFOPValidationResponse(**resultado)
    except Exception as e:
        logger.error(f"Erro ao validar CFOP {request.cfop}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar CFOP: {str(e)}"
        )


@router.post(
    "/validate/ncm",
    response_model=NCMValidationResponse,
    summary="Validar NCM",
    description="Valida um código NCM e retorna categoria do produto"
)
async def validate_ncm(
    request: NCMValidationRequest,
    agent: NFeTaxSpecialistAgent = Depends(get_nfe_agent)
):
    """
    Valida um código NCM (Nomenclatura Comum do Mercosul).
    
    **Parâmetros:**
    - **ncm**: Código NCM de 8 dígitos (ex: 84714100)
    
    **Retorna:**
    - Validação do NCM
    - Capítulo e categoria do produto
    - NCM formatado
    """
    try:
        logger.info(f"Validando NCM: {request.ncm}")
        resultado = agent.validate_ncm(request.ncm)
        return NCMValidationResponse(**resultado)
    except Exception as e:
        logger.error(f"Erro ao validar NCM {request.ncm}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar NCM: {str(e)}"
        )


# ============================================================================
# ENDPOINT DE ANÁLISE DE NOTA FISCAL
# ============================================================================

@router.post(
    "/analyze",
    response_model=NotaFiscalAnalysisResponse,
    summary="Analisar Nota Fiscal",
    description="Análise tributária completa de uma NF-e com validações e score fiscal"
)
async def analyze_nota_fiscal(
    request: NotaFiscalAnalysisRequest,
    agent: NFeTaxSpecialistAgent = Depends(get_nfe_agent)
):
    """
    Realiza análise tributária completa de uma Nota Fiscal Eletrônica.
    
    **Parâmetros:**
    - **chave_acesso**: Chave de acesso da NF-e (44 caracteres)
    
    **Retorna:**
    - Dados da nota (emitente, destinatário, valores)
    - Validações de CFOP, NCM e valores
    - Alertas fiscais
    - Score de conformidade (0-100)
    - Recomendações
    
    **Score Fiscal:**
    - 90-100: Excelente conformidade
    - 70-89: Conformidade adequada
    - 50-69: Atenção necessária
    - 0-49: Problemas graves
    """
    try:
        logger.info(f"Analisando nota fiscal: {request.chave_acesso}")
        resultado = agent.analyze_nota_fiscal(request.chave_acesso)
        return NotaFiscalAnalysisResponse(**resultado)
    except Exception as e:
        logger.error(f"Erro ao analisar nota {request.chave_acesso}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao analisar nota fiscal: {str(e)}"
        )


# ============================================================================
# ENDPOINT DE DETECÇÃO DE ANOMALIAS
# ============================================================================

@router.post(
    "/anomalies",
    response_model=AnomalyDetectionResponse,
    summary="Detectar Anomalias Fiscais",
    description="Detecta anomalias e inconsistências tributárias em conjunto de notas"
)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    agent: NFeTaxSpecialistAgent = Depends(get_nfe_agent)
):
    """
    Detecta anomalias tributárias no conjunto de notas fiscais.
    
    **Filtros opcionais:**
    - **uf_emitente**: UF do emitente (ex: SP, RJ)
    - **data_inicio**: Data inicial (YYYY-MM-DD)
    - **data_fim**: Data final (YYYY-MM-DD)
    - **limit**: Limite de resultados (1-100)
    
    **Tipos de anomalias detectadas:**
    - Divergências de valores
    - CFOPs inconsistentes
    - NCMs inválidos
    - Inconsistências UF x CFOP
    
    **Retorna:**
    - Total de anomalias
    - Lista de anomalias com severidade
    - Descrição dos problemas
    """
    try:
        logger.info(f"Detectando anomalias: UF={request.uf_emitente}, periodo={request.data_inicio} a {request.data_fim}")
        resultado = agent.detect_anomalies(
            uf_emitente=request.uf_emitente,
            data_inicio=request.data_inicio,
            data_fim=request.data_fim,
            limit=request.limit
        )
        return AnomalyDetectionResponse(**resultado)
    except Exception as e:
        logger.error(f"Erro ao detectar anomalias: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao detectar anomalias: {str(e)}"
        )


# ============================================================================
# ENDPOINT DE CONSULTA TRIBUTÁRIA
# ============================================================================

@router.post(
    "/query",
    response_model=TaxQueryResponse,
    summary="Consultar Legislação Tributária",
    description="Consulta conhecimento sobre legislação tributária, CFOP, NCM e tributos"
)
async def query_tax_knowledge(
    request: TaxQueryRequest,
    agent: NFeTaxSpecialistAgent = Depends(get_nfe_agent)
):
    """
    Consulta especializada sobre legislação tributária brasileira.
    
    **Parâmetros:**
    - **query**: Pergunta sobre tributos (min 10 caracteres)
    - **context**: Contexto opcional (chave_acesso, cfop, ncm)
    
    **Exemplos de perguntas:**
    - "Qual a diferença entre CFOP 5102 e 6102?"
    - "Quando devo usar NCM do capítulo 84?"
    - "Como calcular ICMS em operação interestadual?"
    - "O que é substituição tributária?"
    
    **Retorna:**
    - Resposta técnica e detalhada
    - Contexto utilizado
    - Referências à legislação
    
    **Nota:** Requer SONAR_API_KEY configurada no .env
    """
    try:
        logger.info(f"Consulta tributária: {request.query[:50]}...")
        resultado = agent.query_tax_knowledge(request.query, request.context)
        return TaxQueryResponse(**resultado)
    except Exception as e:
        logger.error(f"Erro na consulta tributária: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na consulta: {str(e)}"
        )


# ============================================================================
# ENDPOINT DE BUSCA DE NOTAS SIMILARES
# ============================================================================

@router.get(
    "/similar/{chave_acesso}",
    response_model=SimilarNotasResponse,
    summary="Buscar Notas Similares",
    description="Busca notas fiscais similares usando embeddings vetoriais"
)
async def find_similar_notas(
    chave_acesso: str,
    limit: int = Query(5, ge=1, le=20, description="Número de notas similares"),
    agent: NFeTaxSpecialistAgent = Depends(get_nfe_agent)
):
    """
    Busca notas fiscais similares à nota de referência.
    
    **Parâmetros:**
    - **chave_acesso**: Chave de acesso da nota de referência (44 caracteres)
    - **limit**: Quantidade de notas similares (1-20)
    
    **Critérios de similaridade:**
    - Valores próximos
    - Mesmo emitente ou setor
    - CFOPs relacionados
    - NCMs da mesma categoria
    
    **Retorna:**
    - Nota de referência
    - Lista de notas similares ordenadas por relevância
    - Score de similaridade
    
    **Nota:** Requer embeddings das notas no banco vetorial
    """
    try:
        logger.info(f"Buscando notas similares a: {chave_acesso}")
        resultado = agent.find_similar_notas(chave_acesso, limit)
        return SimilarNotasResponse(**resultado)
    except Exception as e:
        logger.error(f"Erro ao buscar notas similares: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar notas similares: {str(e)}"
        )


# ============================================================================
# ENDPOINT DE LISTAGEM DE NOTAS
# ============================================================================

@router.get(
    "/list",
    response_model=ListNotasResponse,
    summary="Listar Notas Fiscais",
    description="Lista notas fiscais com filtros e paginação"
)
async def list_notas(
    data_inicio: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    uf: Optional[str] = Query(None, max_length=2, description="UF do emitente"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação")
):
    """
    Lista notas fiscais com filtros opcionais.
    
    **Filtros disponíveis:**
    - **data_inicio**: Filtrar por data inicial
    - **data_fim**: Filtrar por data final
    - **uf**: Filtrar por UF do emitente
    - **limit**: Número de resultados (1-1000)
    - **offset**: Paginação
    
    **Retorna:**
    - Total de notas encontradas
    - Lista de notas com dados principais
    - Suporta paginação
    
    **Exemplo de paginação:**
    - Página 1: offset=0, limit=100
    - Página 2: offset=100, limit=100
    - Página 3: offset=200, limit=100
    """
    try:
        logger.info(f"Listando notas: periodo={data_inicio} a {data_fim}, UF={uf}, limit={limit}, offset={offset}")
        
        # Construir query do Supabase
        query = supabase.table('nota_fiscal').select('*')
        
        # Aplicar filtros
        if data_inicio:
            query = query.gte('data_emissao', data_inicio)
        if data_fim:
            query = query.lte('data_emissao', data_fim)
        if uf:
            query = query.eq('uf_emitente', uf.upper())
        
        # Aplicar paginação
        query = query.range(offset, offset + limit - 1)
        
        # Executar query
        result = query.execute()
        
        # Contar total (sem paginação)
        count_query = supabase.table('nota_fiscal').select('id', count='exact')
        if data_inicio:
            count_query = count_query.gte('data_emissao', data_inicio)
        if data_fim:
            count_query = count_query.lte('data_emissao', data_fim)
        if uf:
            count_query = count_query.eq('uf_emitente', uf.upper())
        
        count_result = count_query.execute()
        total = count_result.count if hasattr(count_result, 'count') else len(result.data)
        
        return ListNotasResponse(
            success=True,
            total=total,
            notas=result.data
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar notas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar notas: {str(e)}"
        )


# ============================================================================
# ENDPOINT DE HEALTH CHECK
# ============================================================================

@router.get(
    "/health",
    summary="Health Check NFe",
    description="Verifica status do serviço NFe Tax Specialist"
)
async def health_check():
    """
    Health check do serviço NFe Tax Specialist.
    
    **Retorna:**
    - Status do agente
    - Conexão com banco de dados
    - Configurações disponíveis
    """
    try:
        # Testar criação do agente
        agent = NFeTaxSpecialistAgent()
        
        # Testar conexão Supabase
        result = supabase.table('nota_fiscal').select('id').limit(1).execute()
        db_connected = True if result.data is not None else False
        
        return {
            "status": "healthy",
            "service": "NFe Tax Specialist",
            "agent_available": True,
            "database_connected": db_connected,
            "features": {
                "cfop_validation": True,
                "ncm_validation": True,
                "nota_analysis": True,
                "anomaly_detection": True,
                "tax_query": True,
                "similar_search": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "NFe Tax Specialist",
            "error": str(e)
        }
