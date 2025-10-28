# Implementação de Upload de Notas Fiscais Eletrônicas (NF-e)

**Data:** 28 de Outubro de 2025  
**Versão:** 1.0  
**Status:** ✅ Implementado e pronto para uso

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Banco de Dados](#arquitetura-do-banco-de-dados)
3. [Aderência aos CSVs](#aderência-aos-csvs)
4. [Módulo de Upload](#módulo-de-upload)
5. [Como Usar](#como-usar)
6. [Validações e Integridade](#validações-e-integridade)
7. [Queries e Análises](#queries-e-análises)

---

## 🎯 Visão Geral

Sistema completo para **upload, armazenamento e análise** de arquivos CSV de Notas Fiscais Eletrônicas (NF-e), suportando:

- ✅ Upload de `202505_NFe_NotaFiscal.csv` (cabeçalho das notas)
- ✅ Upload de `202505_NFe_NotaFiscalItem.csv` (detalhamento de itens)
- ✅ Detecção automática do tipo de arquivo
- ✅ Processamento em lotes (batch) para arquivos grandes
- ✅ Rastreamento de progresso de upload
- ✅ Validação de integridade financeira
- ✅ Views e funções SQL para análises

---

## 🗄️ Arquitetura do Banco de Dados

### Estrutura de Tabelas

```
┌─────────────────┐
│    uploads      │ ← Controle de uploads
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ↓                 ↓
┌──────────────┐  ┌─────────────────┐
│ nota_fiscal  │  │ nota_fiscal_item│
│ (cabeçalho)  │  │   (detalhes)    │
└──────┬───────┘  └────────┬────────┘
       │                   │
       └───────┬───────────┘
               │ FK: chave_acesso
               ↓
        Relacionamento 1:N
```

### Tabela: `uploads`

Controla todos os uploads realizados pelos usuários.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | Identificador único |
| `filename` | VARCHAR | Nome do arquivo original |
| `file_type` | VARCHAR | `nota_fiscal` ou `nota_fiscal_item` |
| `file_size_mb` | DECIMAL | Tamanho do arquivo em MB |
| `uploaded_by` | VARCHAR | Identificador do usuário |
| `uploaded_at` | TIMESTAMP | Data/hora do upload |
| `status` | VARCHAR | `pending`, `processing`, `completed`, `failed` |
| `rows_processed` | INTEGER | Linhas processadas |
| `rows_total` | INTEGER | Total de linhas |
| `error_message` | TEXT | Mensagem de erro (se houver) |
| `metadata` | JSONB | Metadados adicionais |

### Tabela: `nota_fiscal` (21 colunas)

Cabeçalho/resumo de cada nota fiscal.

**Chave Primária:** `chave_acesso` (VARCHAR 44)

#### Colunas de Identificação:
- `chave_acesso` - Chave única da NF-e (44 dígitos)
- `modelo` - Modelo da nota
- `serie` - Série da nota
- `numero` - Número sequencial

#### Dados da Operação:
- `natureza_operacao` - Tipo de operação
- `data_emissao` - Data de emissão
- `evento_recente` - Último evento (ex: "Autorização de Uso")
- `data_hora_evento` - Timestamp do evento

#### Dados do Emitente:
- `cpf_cnpj_emitente`
- `razao_social_emitente`
- `ie_emitente` - Inscrição Estadual
- `uf_emitente`
- `municipio_emitente`

#### Dados do Destinatário:
- `cnpj_destinatario`
- `nome_destinatario`
- `uf_destinatario`
- `indicador_ie_destinatario`

#### Características da Operação:
- `destino_operacao` - Interno/Interestadual/Internacional
- `consumidor_final` - Flag consumidor final
- `presenca_comprador` - Modalidade de compra

#### Valores:
- `valor_nota_fiscal` - **Valor total da nota** (DECIMAL 15,2)

### Tabela: `nota_fiscal_item` (27 colunas)

Detalhamento linha a linha dos produtos/serviços.

**Chave Primária:** `id` (UUID)  
**Chave Estrangeira:** `chave_acesso` → `nota_fiscal.chave_acesso`  
**Constraint Única:** `(chave_acesso, numero_produto)`

#### Colunas Compartilhadas (18):
- Mesmas colunas de identificação da `nota_fiscal`
- Dados do emitente e destinatário (redundantes para facilitar queries)

#### Colunas Exclusivas (9):
- `numero_produto` - Sequência do item na nota (1, 2, 3...)
- `descricao_produto` - Descrição completa do produto
- `codigo_ncm` - NCM/SH (classificação fiscal)
- `ncm_tipo_produto` - Categoria do produto
- `cfop` - Código Fiscal de Operações
- `quantidade` - Quantidade comercializada
- `unidade` - Unidade de medida (M3, KG, UN, etc.)
- `valor_unitario` - Preço por unidade
- `valor_total` - Valor do item (quantidade × valor_unitario)

### Índices de Performance

```sql
-- Índices para buscas rápidas
CREATE INDEX idx_nota_fiscal_chave ON nota_fiscal(chave_acesso);
CREATE INDEX idx_nota_fiscal_data_emissao ON nota_fiscal(data_emissao);
CREATE INDEX idx_nota_fiscal_uf_destinatario ON nota_fiscal(uf_destinatario);

CREATE INDEX idx_nota_item_chave ON nota_fiscal_item(chave_acesso);
CREATE INDEX idx_nota_item_codigo_ncm ON nota_fiscal_item(codigo_ncm);
CREATE INDEX idx_nota_item_cfop ON nota_fiscal_item(cfop);
```

---

## ✅ Aderência aos CSVs

### Mapeamento Completo: CSV → Banco de Dados

#### NotaFiscal.csv (21 colunas) → `nota_fiscal`

| Coluna CSV | Coluna Banco | Tipo | Observações |
|------------|--------------|------|-------------|
| CHAVE DE ACESSO | chave_acesso | VARCHAR(44) | PK única |
| MODELO | modelo | VARCHAR(100) | |
| SÉRIE | serie | INTEGER | |
| NÚMERO | numero | INTEGER | |
| NATUREZA DA OPERAÇÃO | natureza_operacao | TEXT | |
| DATA EMISSÃO | data_emissao | DATE | Conversão DD/MM/YYYY |
| EVENTO MAIS RECENTE | evento_recente | VARCHAR(100) | |
| DATA/HORA EVENTO MAIS RECENTE | data_hora_evento | TIMESTAMP | Conversão DD/MM/YYYY HH:MM:SS |
| CPF/CNPJ Emitente | cpf_cnpj_emitente | VARCHAR(18) | |
| RAZÃO SOCIAL EMITENTE | razao_social_emitente | TEXT | |
| INSCRIÇÃO ESTADUAL EMITENTE | ie_emitente | VARCHAR(20) | |
| UF EMITENTE | uf_emitente | VARCHAR(2) | |
| MUNICÍPIO EMITENTE | municipio_emitente | VARCHAR(100) | |
| CNPJ DESTINATÁRIO | cnpj_destinatario | VARCHAR(18) | |
| NOME DESTINATÁRIO | nome_destinatario | TEXT | |
| UF DESTINATÁRIO | uf_destinatario | VARCHAR(2) | |
| INDICADOR IE DESTINATÁRIO | indicador_ie_destinatario | VARCHAR(50) | |
| DESTINO DA OPERAÇÃO | destino_operacao | VARCHAR(50) | |
| CONSUMIDOR FINAL | consumidor_final | VARCHAR(50) | |
| PRESENÇA DO COMPRADOR | presenca_comprador | VARCHAR(100) | |
| VALOR NOTA FISCAL | valor_nota_fiscal | DECIMAL(15,2) | Conversão vírgula→ponto |

**✅ 100% de aderência** - Todas as 21 colunas mapeadas

#### NotaFiscalItem.csv (27 colunas) → `nota_fiscal_item`

| Coluna CSV | Coluna Banco | Tipo | Observações |
|------------|--------------|------|-------------|
| *(18 colunas compartilhadas)* | *(mesmas da nota_fiscal)* | | Redundância intencional |
| NÚMERO PRODUTO | numero_produto | INTEGER | Sequência do item |
| DESCRIÇÃO DO PRODUTO/SERVIÇO | descricao_produto | TEXT | |
| CÓDIGO NCM/SH | codigo_ncm | VARCHAR(10) | |
| NCM/SH (TIPO DE PRODUTO) | ncm_tipo_produto | VARCHAR(200) | |
| CFOP | cfop | VARCHAR(10) | |
| QUANTIDADE | quantidade | DECIMAL(15,4) | Conversão vírgula→ponto |
| UNIDADE | unidade | VARCHAR(10) | |
| VALOR UNITÁRIO | valor_unitario | DECIMAL(15,4) | Conversão vírgula→ponto |
| VALOR TOTAL | valor_total | DECIMAL(15,2) | Conversão vírgula→ponto |

**✅ 100% de aderência** - Todas as 27 colunas mapeadas

### Tratamento de Dados

#### Conversões Automáticas:
- **Datas:** `DD/MM/YYYY` → `DATE`
- **Timestamps:** `DD/MM/YYYY HH:MM:SS` → `TIMESTAMP`
- **Valores decimais:** Vírgula → Ponto, espaços removidos
- **Valores nulos:** `NaN` → `NULL` (PostgreSQL)

#### Encoding e Separador:
- **Encoding:** `latin-1` (ISO-8859-1) ✅
- **Separador:** `;` (ponto e vírgula) ✅

---

## 📦 Módulo de Upload

### Classe: `NFeUploader`

Localização: `src/data/nfe_uploader.py`

#### Métodos Principais:

```python
# Detecta automaticamente o tipo de arquivo
file_type = uploader.detect_file_type(df)  # 'nota_fiscal' ou 'nota_fiscal_item'

# Upload de NotaFiscal.csv
result = uploader.upload_nota_fiscal(
    file_path="data/202505_NFe_NotaFiscal.csv",
    uploaded_by="user@example.com"
)

# Upload de NotaFiscalItem.csv
result = uploader.upload_nota_fiscal_item(
    file_path="data/202505_NFe_NotaFiscalItem.csv",
    uploaded_by="user@example.com"
)

# Upload automático (detecta tipo)
result = uploader.upload_auto(
    file_path="data/arquivo.csv",
    uploaded_by="user@example.com"
)
```

#### Características:
- ✅ **Processamento em lotes** (batch_size=1000)
- ✅ **Rastreamento de progresso** em tempo real
- ✅ **Tratamento de erros** com registro detalhado
- ✅ **Idempotência** (pode reexecutar sem duplicar)
- ✅ **Logging estruturado** com níveis INFO/DEBUG/ERROR

---

## 🚀 Como Usar

### 1. Executar Migration

```bash
# Via script automatizado
python scripts/setup_nfe.py

# Ou via scripts/run_migrations.py
python scripts/run_migrations.py
```

### 2. Upload Via Script

```bash
# Upload automático (detecta tipo)
python -m src.data.nfe_uploader data/202505_NFe_NotaFiscal.csv usuario@email.com

# Upload dos dois arquivos
python scripts/setup_nfe.py
```

### 3. Upload Via Código Python

```python
from src.data.nfe_uploader import upload_nfe_files

results = upload_nfe_files(
    nota_fiscal_path="data/202505_NFe_NotaFiscal.csv",
    nota_fiscal_item_path="data/202505_NFe_NotaFiscalItem.csv",
    uploaded_by="api_user"
)

print(f"NotaFiscal: {results['nota_fiscal']['rows_inserted']} linhas")
print(f"NotaFiscalItem: {results['nota_fiscal_item']['rows_inserted']} linhas")
```

### 4. Monitoramento de Upload

```python
from src.vectorstore.supabase_client import supabase

# Ver todos os uploads
uploads = supabase.table('uploads').select('*').execute()

# Ver uploads em andamento
processing = supabase.table('uploads')\
    .select('*')\
    .eq('status', 'processing')\
    .execute()

# Estatísticas de um upload
stats = supabase.table('vw_upload_stats')\
    .select('*')\
    .eq('id', 'uuid-do-upload')\
    .execute()
```

---

## ✅ Validações e Integridade

### 1. Integridade Referencial

```sql
-- Constraint FK: NotaFiscalItem → NotaFiscal
ALTER TABLE nota_fiscal_item 
ADD CONSTRAINT fk_item_nota 
FOREIGN KEY (chave_acesso) 
REFERENCES nota_fiscal(chave_acesso) 
ON DELETE CASCADE;
```

**Garantia:** Todo item tem uma nota fiscal correspondente.

### 2. Validação Financeira

```sql
-- Validar se soma dos itens = valor da nota
SELECT * FROM public.fn_validar_nota_fiscal('13250505914165000192550030000116841779221343');

-- Resultado:
-- chave_acesso | valor_nota | soma_itens | diferenca | valido
-- 13250...     | 4603.42    | 4603.42    | 0.00      | true
```

### 3. View de Resumo com Validação

```sql
SELECT * FROM vw_nota_fiscal_resumo 
WHERE validacao_valor = 'DIVERGENTE';
```

Identifica notas com valor total divergente da soma dos itens.

---

## 📊 Queries e Análises

### Análises Básicas

```sql
-- Top 10 produtos mais vendidos
SELECT * FROM vw_produtos_mais_vendidos LIMIT 10;

-- Notas por UF destinatário
SELECT 
    uf_destinatario,
    COUNT(*) as qtd_notas,
    SUM(valor_nota_fiscal) as valor_total
FROM nota_fiscal
GROUP BY uf_destinatario
ORDER BY valor_total DESC;

-- Emitentes mais ativos
SELECT 
    razao_social_emitente,
    COUNT(*) as qtd_notas,
    SUM(valor_nota_fiscal) as valor_total
FROM nota_fiscal
GROUP BY razao_social_emitente
ORDER BY qtd_notas DESC
LIMIT 20;
```

### Análises Temporais

```sql
-- Estatísticas de maio/2025
SELECT * FROM fn_estatisticas_periodo('2025-05-01', '2025-05-31');

-- Vendas por dia
SELECT 
    data_emissao,
    COUNT(*) as qtd_notas,
    SUM(valor_nota_fiscal) as valor_total
FROM nota_fiscal
WHERE data_emissao BETWEEN '2025-05-01' AND '2025-05-31'
GROUP BY data_emissao
ORDER BY data_emissao;
```

### Análises por Produto (NCM)

```sql
-- Produtos mais vendidos para um estado específico
SELECT 
    nfi.ncm_tipo_produto,
    nfi.codigo_ncm,
    COUNT(DISTINCT nfi.chave_acesso) as qtd_notas,
    SUM(nfi.quantidade) as quantidade_total,
    SUM(nfi.valor_total) as valor_total
FROM nota_fiscal_item nfi
WHERE nfi.uf_destinatario = 'RR'
GROUP BY nfi.ncm_tipo_produto, nfi.codigo_ncm
ORDER BY valor_total DESC;
```

### Join Completo

```sql
-- Análise completa: nota + itens
SELECT 
    nf.chave_acesso,
    nf.razao_social_emitente,
    nf.uf_destinatario,
    nf.data_emissao,
    nf.valor_nota_fiscal,
    nfi.numero_produto,
    nfi.descricao_produto,
    nfi.quantidade,
    nfi.unidade,
    nfi.valor_total
FROM nota_fiscal nf
INNER JOIN nota_fiscal_item nfi ON nf.chave_acesso = nfi.chave_acesso
WHERE nf.uf_destinatario = 'RR'
  AND nf.data_emissao >= '2025-05-01'
ORDER BY nf.data_emissao DESC, nfi.numero_produto;
```

---

## 🔧 Configuração Necessária

### Variáveis de Ambiente

```env
# configs/.env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon
```

### Dependências Python

```python
pandas>=2.2.3
supabase>=2.20.0
```

---

## 📈 Performance

### Otimizações Implementadas:

1. **Processamento em Lotes:** 1000 registros por batch
2. **Índices Estratégicos:** Cobertura em chaves de busca frequentes
3. **Redundância Controlada:** Campos duplicados em `nota_fiscal_item` para evitar JOINs
4. **Views Materializadas:** Para análises complexas frequentes

### Recomendações:

- Para datasets >1GB: Considere `batch_size=500`
- Para queries frequentes: Crie índices adicionais conforme necessário
- Para análises históricas: Particionar tabelas por mês/ano

---

## 🎯 Próximos Passos

### Funcionalidades Futuras:

- [ ] API REST para upload via HTTP
- [ ] Interface web para upload e monitoramento
- [ ] Validação avançada (duplicatas, chaves inválidas)
- [ ] Export para formatos analíticos (Parquet, Arrow)
- [ ] Dashboards de visualização (Grafana, Metabase)
- [ ] Integração com sistema de embeddings/RAG

---

## 📝 Checklist de Implementação

- [x] Schema SQL completo (migration 0008)
- [x] Tabelas: `uploads`, `nota_fiscal`, `nota_fiscal_item`
- [x] Índices de performance
- [x] Views úteis: `vw_upload_stats`, `vw_nota_fiscal_resumo`, `vw_produtos_mais_vendidos`
- [x] Funções SQL: `fn_validar_nota_fiscal`, `fn_estatisticas_periodo`
- [x] Módulo Python: `NFeUploader`
- [x] Detecção automática de tipo de arquivo
- [x] Processamento em lotes com progresso
- [x] Tratamento de encoding (latin-1) e separador (;)
- [x] Conversões de tipos (datas, decimais)
- [x] Logging estruturado
- [x] Script de setup: `scripts/setup_nfe.py`
- [x] Documentação técnica completa

---

**Status Final:** ✅ **Sistema pronto para produção**

**Arquivos Criados:**
- `migrations/0008_nfe_schema.sql`
- `src/data/nfe_uploader.py`
- `scripts/setup_nfe.py`
- `docs/IMPLEMENTACAO_UPLOAD_NFE.md` (este arquivo)
