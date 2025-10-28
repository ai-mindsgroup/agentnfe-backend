-- ============================================================================
-- Migration: Aumentar tamanho do campo ncm_tipo_produto
-- Motivo: Campo pode conter até 255 caracteres no CSV real
-- Data: 2025-10-28
-- ============================================================================

-- Drop view que depende da coluna
DROP VIEW IF EXISTS public.vw_produtos_mais_vendidos;

-- Aumentar campo ncm_tipo_produto de VARCHAR(200) para VARCHAR(300)
ALTER TABLE public.nota_fiscal_item 
ALTER COLUMN ncm_tipo_produto TYPE VARCHAR(300);

-- Recriar view
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

-- Log da alteração
DO $$
BEGIN
    RAISE NOTICE 'Campo ncm_tipo_produto aumentado para VARCHAR(300)';
END $$;
