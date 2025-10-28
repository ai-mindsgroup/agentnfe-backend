-- ============================================================================
-- Migration: Schema para Notas Fiscais Eletrônicas (NF-e)
-- Versão: 0008
-- Data: 2025-10-28
-- Descrição: Cria tabelas para armazenar dados de NF-e (NotaFiscal e NotaFiscalItem)
--            com suporte a upload de arquivos CSV pelo usuário
-- ============================================================================

-- ============================================================================
-- 1. TABELA: uploads
-- Controla os uploads de arquivos CSV realizados pelos usuários
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'nota_fiscal' ou 'nota_fiscal_item'
    file_size_mb DECIMAL(10, 2),
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    rows_processed INTEGER DEFAULT 0,
    rows_total INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================================================
-- 2. TABELA: nota_fiscal
-- Cabeçalho/resumo de cada nota fiscal eletrônica
-- Baseado em: 202505_NFe_NotaFiscal.csv (21 colunas)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.nota_fiscal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID REFERENCES public.uploads(id) ON DELETE CASCADE,
    
    -- Identificação da Nota
    chave_acesso VARCHAR(44) NOT NULL UNIQUE, -- CHAVE DE ACESSO (44 dígitos)
    modelo VARCHAR(100), -- MODELO
    serie INTEGER, -- SÉRIE
    numero INTEGER, -- NÚMERO
    
    -- Dados da Operação
    natureza_operacao TEXT, -- NATUREZA DA OPERAÇÃO
    data_emissao DATE, -- DATA EMISSÃO
    evento_recente VARCHAR(100), -- EVENTO MAIS RECENTE
    data_hora_evento TIMESTAMP, -- DATA/HORA EVENTO MAIS RECENTE
    
    -- Dados do Emitente
    cpf_cnpj_emitente VARCHAR(18), -- CPF/CNPJ Emitente
    razao_social_emitente TEXT, -- RAZÃO SOCIAL EMITENTE
    ie_emitente VARCHAR(20), -- INSCRIÇÃO ESTADUAL EMITENTE
    uf_emitente VARCHAR(2), -- UF EMITENTE
    municipio_emitente VARCHAR(100), -- MUNICÍPIO EMITENTE
    
    -- Dados do Destinatário
    cnpj_destinatario VARCHAR(18), -- CNPJ DESTINATÁRIO
    nome_destinatario TEXT, -- NOME DESTINATÁRIO
    uf_destinatario VARCHAR(2), -- UF DESTINATÁRIO
    indicador_ie_destinatario VARCHAR(50), -- INDICADOR IE DESTINATÁRIO
    
    -- Características da Operação
    destino_operacao VARCHAR(50), -- DESTINO DA OPERAÇÃO
    consumidor_final VARCHAR(50), -- CONSUMIDOR FINAL
    presenca_comprador VARCHAR(100), -- PRESENÇA DO COMPRADOR
    
    -- Valores
    valor_nota_fiscal DECIMAL(15, 2), -- VALOR NOTA FISCAL
    
    -- Metadados
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 3. TABELA: nota_fiscal_item
-- Detalhamento linha a linha dos produtos/serviços de cada nota
-- Baseado em: 202505_NFe_NotaFiscalItem.csv (27 colunas)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.nota_fiscal_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID REFERENCES public.uploads(id) ON DELETE CASCADE,
    
    -- Relação com Nota Fiscal (FK)
    chave_acesso VARCHAR(44) NOT NULL REFERENCES public.nota_fiscal(chave_acesso) ON DELETE CASCADE,
    
    -- Identificação da Nota (redundante para facilitar queries)
    modelo VARCHAR(100), -- MODELO
    serie INTEGER, -- SÉRIE
    numero INTEGER, -- NÚMERO
    natureza_operacao TEXT, -- NATUREZA DA OPERAÇÃO
    data_emissao DATE, -- DATA EMISSÃO
    
    -- Dados do Emitente (redundante)
    cpf_cnpj_emitente VARCHAR(18), -- CPF/CNPJ Emitente
    razao_social_emitente TEXT, -- RAZÃO SOCIAL EMITENTE
    ie_emitente VARCHAR(20), -- INSCRIÇÃO ESTADUAL EMITENTE
    uf_emitente VARCHAR(2), -- UF EMITENTE
    municipio_emitente VARCHAR(100), -- MUNICÍPIO EMITENTE
    
    -- Dados do Destinatário (redundante)
    cnpj_destinatario VARCHAR(18), -- CNPJ DESTINATÁRIO
    nome_destinatario TEXT, -- NOME DESTINATÁRIO
    uf_destinatario VARCHAR(2), -- UF DESTINATÁRIO
    indicador_ie_destinatario VARCHAR(50), -- INDICADOR IE DESTINATÁRIO
    
    -- Características da Operação (redundante)
    destino_operacao VARCHAR(50), -- DESTINO DA OPERAÇÃO
    consumidor_final VARCHAR(50), -- CONSUMIDOR FINAL
    presenca_comprador VARCHAR(100), -- PRESENÇA DO COMPRADOR
    
    -- Dados Específicos do Item (COLUNAS EXCLUSIVAS)
    numero_produto INTEGER NOT NULL, -- NÚMERO PRODUTO (sequência dentro da nota)
    descricao_produto TEXT, -- DESCRIÇÃO DO PRODUTO/SERVIÇO
    codigo_ncm VARCHAR(10), -- CÓDIGO NCM/SH
    ncm_tipo_produto VARCHAR(200), -- NCM/SH (TIPO DE PRODUTO)
    cfop VARCHAR(10), -- CFOP
    quantidade DECIMAL(15, 4), -- QUANTIDADE
    unidade VARCHAR(10), -- UNIDADE
    valor_unitario DECIMAL(15, 4), -- VALOR UNITÁRIO
    valor_total DECIMAL(15, 2), -- VALOR TOTAL
    
    -- Metadados
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint de unicidade composta (uma nota não pode ter dois itens com mesmo número)
    CONSTRAINT uk_nota_item UNIQUE (chave_acesso, numero_produto)
);

-- ============================================================================
-- 4. ÍNDICES DE PERFORMANCE
-- ============================================================================

-- Índices para nota_fiscal
CREATE INDEX IF NOT EXISTS idx_nota_fiscal_chave ON public.nota_fiscal(chave_acesso);
CREATE INDEX IF NOT EXISTS idx_nota_fiscal_data_emissao ON public.nota_fiscal(data_emissao);
CREATE INDEX IF NOT EXISTS idx_nota_fiscal_cpf_cnpj_emitente ON public.nota_fiscal(cpf_cnpj_emitente);
CREATE INDEX IF NOT EXISTS idx_nota_fiscal_cnpj_destinatario ON public.nota_fiscal(cnpj_destinatario);
CREATE INDEX IF NOT EXISTS idx_nota_fiscal_uf_emitente ON public.nota_fiscal(uf_emitente);
CREATE INDEX IF NOT EXISTS idx_nota_fiscal_uf_destinatario ON public.nota_fiscal(uf_destinatario);
CREATE INDEX IF NOT EXISTS idx_nota_fiscal_upload_id ON public.nota_fiscal(upload_id);

-- Índices para nota_fiscal_item
CREATE INDEX IF NOT EXISTS idx_nota_item_chave ON public.nota_fiscal_item(chave_acesso);
CREATE INDEX IF NOT EXISTS idx_nota_item_numero_produto ON public.nota_fiscal_item(numero_produto);
CREATE INDEX IF NOT EXISTS idx_nota_item_codigo_ncm ON public.nota_fiscal_item(codigo_ncm);
CREATE INDEX IF NOT EXISTS idx_nota_item_cfop ON public.nota_fiscal_item(cfop);
CREATE INDEX IF NOT EXISTS idx_nota_item_data_emissao ON public.nota_fiscal_item(data_emissao);
CREATE INDEX IF NOT EXISTS idx_nota_item_uf_destinatario ON public.nota_fiscal_item(uf_destinatario);
CREATE INDEX IF NOT EXISTS idx_nota_item_upload_id ON public.nota_fiscal_item(upload_id);

-- Índice para uploads
CREATE INDEX IF NOT EXISTS idx_uploads_status ON public.uploads(status);
CREATE INDEX IF NOT EXISTS idx_uploads_uploaded_at ON public.uploads(uploaded_at);

-- ============================================================================
-- 5. VIEWS ÚTEIS
-- ============================================================================

-- View: Estatísticas por upload
CREATE OR REPLACE VIEW public.vw_upload_stats AS
SELECT 
    u.id,
    u.filename,
    u.file_type,
    u.uploaded_at,
    u.status,
    u.rows_processed,
    u.rows_total,
    CASE 
        WHEN u.file_type = 'nota_fiscal' THEN (SELECT COUNT(*) FROM public.nota_fiscal nf WHERE nf.upload_id = u.id)
        WHEN u.file_type = 'nota_fiscal_item' THEN (SELECT COUNT(*) FROM public.nota_fiscal_item nfi WHERE nfi.upload_id = u.id)
        ELSE 0
    END as rows_in_db,
    CASE 
        WHEN u.rows_total > 0 THEN ROUND((u.rows_processed::DECIMAL / u.rows_total::DECIMAL) * 100, 2)
        ELSE 0
    END as progress_percentage
FROM public.uploads u;

-- View: Resumo de notas fiscais com contagem de itens
CREATE OR REPLACE VIEW public.vw_nota_fiscal_resumo AS
SELECT 
    nf.chave_acesso,
    nf.numero,
    nf.serie,
    nf.data_emissao,
    nf.razao_social_emitente,
    nf.uf_emitente,
    nf.nome_destinatario,
    nf.uf_destinatario,
    nf.valor_nota_fiscal,
    COUNT(nfi.id) as qtd_itens,
    COALESCE(SUM(nfi.valor_total), 0) as valor_calculado_itens,
    CASE 
        WHEN ABS(nf.valor_nota_fiscal - COALESCE(SUM(nfi.valor_total), 0)) < 0.01 THEN 'OK'
        ELSE 'DIVERGENTE'
    END as validacao_valor
FROM public.nota_fiscal nf
LEFT JOIN public.nota_fiscal_item nfi ON nf.chave_acesso = nfi.chave_acesso
GROUP BY nf.chave_acesso, nf.numero, nf.serie, nf.data_emissao, 
         nf.razao_social_emitente, nf.uf_emitente, nf.nome_destinatario, 
         nf.uf_destinatario, nf.valor_nota_fiscal;

-- View: Top produtos mais vendidos
CREATE OR REPLACE VIEW public.vw_produtos_mais_vendidos AS
SELECT 
    nfi.codigo_ncm,
    nfi.ncm_tipo_produto,
    nfi.descricao_produto,
    COUNT(DISTINCT nfi.chave_acesso) as qtd_notas,
    SUM(nfi.quantidade) as quantidade_total,
    nfi.unidade,
    AVG(nfi.valor_unitario) as valor_unitario_medio,
    SUM(nfi.valor_total) as valor_total_vendido
FROM public.nota_fiscal_item nfi
GROUP BY nfi.codigo_ncm, nfi.ncm_tipo_produto, nfi.descricao_produto, nfi.unidade
ORDER BY valor_total_vendido DESC;

-- ============================================================================
-- 6. FUNÇÕES ÚTEIS
-- ============================================================================

-- Função: Validar integridade financeira de uma nota
CREATE OR REPLACE FUNCTION public.fn_validar_nota_fiscal(p_chave_acesso VARCHAR)
RETURNS TABLE (
    chave_acesso VARCHAR,
    valor_nota DECIMAL,
    soma_itens DECIMAL,
    diferenca DECIMAL,
    valido BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        nf.chave_acesso,
        nf.valor_nota_fiscal,
        COALESCE(SUM(nfi.valor_total), 0) as soma_itens,
        nf.valor_nota_fiscal - COALESCE(SUM(nfi.valor_total), 0) as diferenca,
        ABS(nf.valor_nota_fiscal - COALESCE(SUM(nfi.valor_total), 0)) < 0.01 as valido
    FROM public.nota_fiscal nf
    LEFT JOIN public.nota_fiscal_item nfi ON nf.chave_acesso = nfi.chave_acesso
    WHERE nf.chave_acesso = p_chave_acesso
    GROUP BY nf.chave_acesso, nf.valor_nota_fiscal;
END;
$$ LANGUAGE plpgsql;

-- Função: Obter estatísticas de um período
CREATE OR REPLACE FUNCTION public.fn_estatisticas_periodo(
    p_data_inicio DATE,
    p_data_fim DATE
)
RETURNS TABLE (
    total_notas BIGINT,
    total_itens BIGINT,
    valor_total DECIMAL,
    valor_medio_nota DECIMAL,
    itens_medio_por_nota DECIMAL,
    total_emitentes BIGINT,
    total_destinatarios BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT nf.chave_acesso)::BIGINT as total_notas,
        COUNT(nfi.id)::BIGINT as total_itens,
        SUM(nf.valor_nota_fiscal) as valor_total,
        AVG(nf.valor_nota_fiscal) as valor_medio_nota,
        (COUNT(nfi.id)::DECIMAL / NULLIF(COUNT(DISTINCT nf.chave_acesso), 0)) as itens_medio_por_nota,
        COUNT(DISTINCT nf.cpf_cnpj_emitente)::BIGINT as total_emitentes,
        COUNT(DISTINCT nf.cnpj_destinatario)::BIGINT as total_destinatarios
    FROM public.nota_fiscal nf
    LEFT JOIN public.nota_fiscal_item nfi ON nf.chave_acesso = nfi.chave_acesso
    WHERE nf.data_emissao BETWEEN p_data_inicio AND p_data_fim;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. COMENTÁRIOS NAS TABELAS
-- ============================================================================

COMMENT ON TABLE public.uploads IS 'Controle de uploads de arquivos CSV de NF-e realizados pelos usuários';
COMMENT ON TABLE public.nota_fiscal IS 'Cabeçalho/resumo das Notas Fiscais Eletrônicas (1 linha = 1 nota)';
COMMENT ON TABLE public.nota_fiscal_item IS 'Detalhamento dos itens/produtos de cada NF-e (N linhas por nota)';

COMMENT ON COLUMN public.nota_fiscal.chave_acesso IS 'Chave de acesso da NF-e (44 dígitos) - PK única';
COMMENT ON COLUMN public.nota_fiscal.valor_nota_fiscal IS 'Valor total da nota (deve ser igual à soma dos itens)';

COMMENT ON COLUMN public.nota_fiscal_item.chave_acesso IS 'FK para nota_fiscal.chave_acesso';
COMMENT ON COLUMN public.nota_fiscal_item.numero_produto IS 'Sequência do item dentro da nota (1, 2, 3...)';
COMMENT ON COLUMN public.nota_fiscal_item.valor_total IS 'Valor do item (quantidade × valor_unitario)';

-- ============================================================================
-- FIM DA MIGRATION
-- ============================================================================
