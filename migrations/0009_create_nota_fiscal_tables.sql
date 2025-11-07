-- ============================================================================
-- Migration 0009: Criação de Tabelas Estruturadas para Nota Fiscal
-- ============================================================================
-- Descrição: Cria tabelas relacionais para armazenar dados estruturados
--            de Notas Fiscais Eletrônicas (NFe), permitindo queries SQL
--            diretas, análises agregadas e relatórios.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- TABELA: nota_fiscal
-- Descrição: Armazena dados principais da Nota Fiscal Eletrônica
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.nota_fiscal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificadores da NFe
    chave_acesso VARCHAR(44) UNIQUE NOT NULL,  -- Chave de 44 dígitos
    numero_nota VARCHAR(20),
    serie INTEGER,
    modelo VARCHAR(2) DEFAULT '55',  -- 55 = NFe
    
    -- Datas
    data_emissao TIMESTAMP WITH TIME ZONE,
    data_entrada_saida TIMESTAMP WITH TIME ZONE,
    
    -- Dados do Emitente
    cnpj_emitente VARCHAR(14),
    nome_emitente TEXT,
    razao_social_emitente TEXT,
    ie_emitente VARCHAR(20),  -- Inscrição Estadual
    uf_emitente VARCHAR(2),
    municipio_emitente TEXT,
    
    -- Dados do Destinatário
    cnpj_cpf_destinatario VARCHAR(14),
    nome_destinatario TEXT,
    razao_social_destinatario TEXT,
    ie_destinatario VARCHAR(20),
    uf_destinatario VARCHAR(2),
    municipio_destinatario TEXT,
    
    -- Natureza da Operação
    cfop VARCHAR(4),  -- Código Fiscal de Operações e Prestações
    natureza_operacao TEXT,
    
    -- Valores Totais (NUMERIC para precisão financeira)
    valor_total NUMERIC(15, 2) DEFAULT 0.00,
    valor_produtos NUMERIC(15, 2) DEFAULT 0.00,
    valor_desconto NUMERIC(15, 2) DEFAULT 0.00,
    valor_frete NUMERIC(15, 2) DEFAULT 0.00,
    valor_seguro NUMERIC(15, 2) DEFAULT 0.00,
    valor_outras_despesas NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Impostos
    base_calculo_icms NUMERIC(15, 2) DEFAULT 0.00,
    valor_icms NUMERIC(15, 2) DEFAULT 0.00,
    valor_icms_st NUMERIC(15, 2) DEFAULT 0.00,  -- Substituição Tributária
    valor_ipi NUMERIC(15, 2) DEFAULT 0.00,
    valor_pis NUMERIC(15, 2) DEFAULT 0.00,
    valor_cofins NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Status e Informações Adicionais
    situacao VARCHAR(50),  -- Autorizada, Cancelada, Denegada
    protocolo_autorizacao VARCHAR(50),
    informacoes_complementares TEXT,
    
    -- Metadados e Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    source_file TEXT,  -- Nome do arquivo CSV de origem
    metadata JSONB DEFAULT '{}'::jsonb  -- Campos adicionais flexíveis
);

-- ---------------------------------------------------------------------------
-- TABELA: nota_fiscal_item
-- Descrição: Armazena os itens/produtos de cada Nota Fiscal
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.nota_fiscal_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relacionamento com Nota Fiscal
    nota_fiscal_id UUID NOT NULL,
    numero_item INTEGER NOT NULL,  -- Número sequencial do item na NFe
    
    -- Identificação do Produto
    codigo_produto VARCHAR(60),
    ean VARCHAR(14),  -- Código de barras
    descricao TEXT NOT NULL,
    ncm VARCHAR(8),  -- Nomenclatura Comum do Mercosul
    cest VARCHAR(7),  -- Código Especificador da Substituição Tributária
    cfop VARCHAR(4),
    
    -- Unidades e Quantidades
    unidade_comercial VARCHAR(6),
    quantidade_comercial NUMERIC(15, 4) DEFAULT 0.0000,
    valor_unitario_comercial NUMERIC(15, 10) DEFAULT 0.0000000000,
    
    unidade_tributavel VARCHAR(6),
    quantidade_tributavel NUMERIC(15, 4) DEFAULT 0.0000,
    valor_unitario_tributavel NUMERIC(15, 10) DEFAULT 0.0000000000,
    
    -- Valores do Item
    valor_total_bruto NUMERIC(15, 2) DEFAULT 0.00,
    valor_desconto NUMERIC(15, 2) DEFAULT 0.00,
    valor_frete NUMERIC(15, 2) DEFAULT 0.00,
    valor_seguro NUMERIC(15, 2) DEFAULT 0.00,
    valor_outras_despesas NUMERIC(15, 2) DEFAULT 0.00,
    valor_total NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Tributos do Item - ICMS
    cst_icms VARCHAR(3),  -- Código de Situação Tributária
    origem_mercadoria INTEGER,
    base_calculo_icms NUMERIC(15, 2) DEFAULT 0.00,
    aliquota_icms NUMERIC(5, 2) DEFAULT 0.00,
    valor_icms NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Tributos do Item - IPI
    cst_ipi VARCHAR(2),
    base_calculo_ipi NUMERIC(15, 2) DEFAULT 0.00,
    aliquota_ipi NUMERIC(5, 2) DEFAULT 0.00,
    valor_ipi NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Tributos do Item - PIS
    cst_pis VARCHAR(2),
    base_calculo_pis NUMERIC(15, 2) DEFAULT 0.00,
    aliquota_pis NUMERIC(5, 4) DEFAULT 0.0000,
    valor_pis NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Tributos do Item - COFINS
    cst_cofins VARCHAR(2),
    base_calculo_cofins NUMERIC(15, 2) DEFAULT 0.00,
    aliquota_cofins NUMERIC(5, 4) DEFAULT 0.0000,
    valor_cofins NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Informações Adicionais
    informacoes_adicionais TEXT,
    
    -- Metadados e Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Chave estrangeira
    CONSTRAINT fk_nota_fiscal FOREIGN KEY (nota_fiscal_id) 
        REFERENCES public.nota_fiscal(id) ON DELETE CASCADE,
    
    -- Constraint para garantir unicidade de itens por nota
    CONSTRAINT uk_nota_item UNIQUE (nota_fiscal_id, numero_item)
);

-- ---------------------------------------------------------------------------
-- TABELA: conversation_history
-- Descrição: Armazena histórico de conversas com usuários para contexto
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.conversation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificação da Sessão
    session_id UUID NOT NULL,
    user_id VARCHAR(255),  -- Opcional: identificador do usuário
    
    -- Conteúdo da Mensagem
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    
    -- Contexto e Metadados
    tokens_used INTEGER,
    model_used VARCHAR(50),
    temperature NUMERIC(3, 2),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    
    -- Rastreamento de Query
    query_type VARCHAR(50),  -- 'search', 'aggregate', 'chat', etc.
    sql_executed TEXT,  -- Se foi executada uma query SQL
    embeddings_used BOOLEAN DEFAULT FALSE,
    
    -- Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ---------------------------------------------------------------------------
-- ÍNDICES PARA PERFORMANCE
-- ---------------------------------------------------------------------------

-- Índices para nota_fiscal
CREATE INDEX IF NOT EXISTS idx_nf_chave_acesso ON public.nota_fiscal(chave_acesso);
CREATE INDEX IF NOT EXISTS idx_nf_cnpj_emitente ON public.nota_fiscal(cnpj_emitente);
CREATE INDEX IF NOT EXISTS idx_nf_cnpj_destinatario ON public.nota_fiscal(cnpj_cpf_destinatario);
CREATE INDEX IF NOT EXISTS idx_nf_data_emissao ON public.nota_fiscal(data_emissao);
CREATE INDEX IF NOT EXISTS idx_nf_uf_emitente ON public.nota_fiscal(uf_emitente);
CREATE INDEX IF NOT EXISTS idx_nf_valor_total ON public.nota_fiscal(valor_total);
CREATE INDEX IF NOT EXISTS idx_nf_cfop ON public.nota_fiscal(cfop);
CREATE INDEX IF NOT EXISTS idx_nf_metadata_gin ON public.nota_fiscal USING gin(metadata);

-- Índices para nota_fiscal_item
CREATE INDEX IF NOT EXISTS idx_nfi_nota_fiscal_id ON public.nota_fiscal_item(nota_fiscal_id);
CREATE INDEX IF NOT EXISTS idx_nfi_codigo_produto ON public.nota_fiscal_item(codigo_produto);
CREATE INDEX IF NOT EXISTS idx_nfi_descricao ON public.nota_fiscal_item USING gin(to_tsvector('portuguese', descricao));
CREATE INDEX IF NOT EXISTS idx_nfi_ncm ON public.nota_fiscal_item(ncm);
CREATE INDEX IF NOT EXISTS idx_nfi_cfop ON public.nota_fiscal_item(cfop);
CREATE INDEX IF NOT EXISTS idx_nfi_valor_total ON public.nota_fiscal_item(valor_total);
CREATE INDEX IF NOT EXISTS idx_nfi_metadata_gin ON public.nota_fiscal_item USING gin(metadata);

-- Índices para conversation_history
CREATE INDEX IF NOT EXISTS idx_conv_session_id ON public.conversation_history(session_id);
CREATE INDEX IF NOT EXISTS idx_conv_user_id ON public.conversation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_conv_created_at ON public.conversation_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conv_role ON public.conversation_history(role);
CREATE INDEX IF NOT EXISTS idx_conv_metadata_gin ON public.conversation_history USING gin(metadata);

-- ---------------------------------------------------------------------------
-- FUNÇÕES AUXILIARES
-- ---------------------------------------------------------------------------

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar updated_at
DROP TRIGGER IF EXISTS update_nota_fiscal_updated_at ON public.nota_fiscal;
CREATE TRIGGER update_nota_fiscal_updated_at
    BEFORE UPDATE ON public.nota_fiscal
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_nota_fiscal_item_updated_at ON public.nota_fiscal_item;
CREATE TRIGGER update_nota_fiscal_item_updated_at
    BEFORE UPDATE ON public.nota_fiscal_item
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ---------------------------------------------------------------------------
-- VIEWS ÚTEIS PARA ANÁLISES
-- ---------------------------------------------------------------------------

-- View: Resumo de Notas Fiscais por UF do Emitente
CREATE OR REPLACE VIEW vw_nf_por_uf_emitente AS
SELECT 
    uf_emitente,
    COUNT(*) as total_notas,
    SUM(valor_total) as valor_total,
    AVG(valor_total) as valor_medio,
    MIN(data_emissao) as data_primeira_nota,
    MAX(data_emissao) as data_ultima_nota
FROM public.nota_fiscal
WHERE situacao = 'Autorizada'
GROUP BY uf_emitente
ORDER BY valor_total DESC;

-- View: Top Produtos Mais Vendidos
CREATE OR REPLACE VIEW vw_top_produtos AS
SELECT 
    nfi.codigo_produto,
    nfi.descricao,
    nfi.ncm,
    COUNT(*) as quantidade_vendas,
    SUM(nfi.quantidade_comercial) as quantidade_total,
    SUM(nfi.valor_total) as valor_total_vendido,
    AVG(nfi.valor_unitario_comercial) as valor_medio_unitario
FROM public.nota_fiscal_item nfi
JOIN public.nota_fiscal nf ON nfi.nota_fiscal_id = nf.id
WHERE nf.situacao = 'Autorizada'
GROUP BY nfi.codigo_produto, nfi.descricao, nfi.ncm
ORDER BY quantidade_vendas DESC;

-- View: Análise de CFOP
CREATE OR REPLACE VIEW vw_analise_cfop AS
SELECT 
    nf.cfop,
    nf.natureza_operacao,
    COUNT(*) as total_operacoes,
    SUM(nf.valor_total) as valor_total,
    AVG(nf.valor_total) as valor_medio
FROM public.nota_fiscal nf
WHERE nf.situacao = 'Autorizada'
GROUP BY nf.cfop, nf.natureza_operacao
ORDER BY valor_total DESC;

-- ---------------------------------------------------------------------------
-- COMENTÁRIOS NAS TABELAS (Documentação no Banco)
-- ---------------------------------------------------------------------------

COMMENT ON TABLE public.nota_fiscal IS 'Tabela principal de Notas Fiscais Eletrônicas (NFe) - dados estruturados para queries SQL diretas';
COMMENT ON TABLE public.nota_fiscal_item IS 'Itens/produtos de cada Nota Fiscal - relacionamento 1:N com nota_fiscal';
COMMENT ON TABLE public.conversation_history IS 'Histórico de conversas com o agente AI para contexto e auditoria';

COMMENT ON COLUMN public.nota_fiscal.chave_acesso IS 'Chave de acesso única da NFe (44 dígitos)';
COMMENT ON COLUMN public.nota_fiscal.valor_total IS 'Valor total da nota fiscal em R$';
COMMENT ON COLUMN public.nota_fiscal_item.nota_fiscal_id IS 'Referência para a nota fiscal pai';

-- ---------------------------------------------------------------------------
-- GRANTS (Permissões)
-- ---------------------------------------------------------------------------

-- Conceder permissões para o role padrão do Supabase
-- IMPORTANTE: Ajustar conforme o role usado na sua aplicação
-- GRANT ALL ON public.nota_fiscal TO authenticated;
-- GRANT ALL ON public.nota_fiscal_item TO authenticated;
-- GRANT ALL ON public.conversation_history TO authenticated;

-- ---------------------------------------------------------------------------
-- FIM DA MIGRATION
-- ---------------------------------------------------------------------------
