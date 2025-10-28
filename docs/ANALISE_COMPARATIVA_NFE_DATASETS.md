# Análise Comparativa: Datasets de Notas Fiscais Eletrônicas (NF-e)

**Data da Análise:** 28 de Outubro de 2025  
**Arquivos Analisados:**
- `data/202505_NFe_NotaFiscal.csv`
- `data/202505_NFe_NotaFiscalItem.csv`

---

## 📊 Visão Geral dos Arquivos

### Tamanhos e Características

| Arquivo | Tamanho | Colunas | Tipo |
|---------|---------|---------|------|
| **202505_NFe_NotaFiscal.csv** | 67.09 MB | 21 | Cabeçalho da NF-e |
| **202505_NFe_NotaFiscalItem.csv** | 296.30 MB | 27 | Detalhamento de Itens |

**Proporção:** O arquivo de itens é **4.4x maior**, indicando que cada nota possui em média múltiplos produtos.

**Encoding:** `latin-1` (ISO-8859-1)  
**Separador:** `;` (ponto e vírgula)

---

## 🏗️ Estrutura dos Arquivos

### 202505_NFe_NotaFiscal.csv (21 colunas)

**Representa:** Dados consolidados do **cabeçalho** de cada nota fiscal eletrônica.

#### Colunas:

1. **CHAVE DE ACESSO** - Identificador único da NF-e (44 dígitos)
2. **MODELO** - Modelo da nota (ex: "55 - NF-E EMITIDA EM SUBSTITUIÇÃO AO MODELO 1 OU 1A")
3. **SÉRIE** - Série da nota fiscal
4. **NÚMERO** - Número sequencial da nota
5. **NATUREZA DA OPERAÇÃO** - Tipo de operação fiscal
6. **DATA EMISSÃO** - Data de emissão da nota
7. **EVENTO MAIS RECENTE** - Último evento da nota (ex: "Autorização de Uso")
8. **DATA/HORA EVENTO MAIS RECENTE** - Timestamp do último evento
9. **CPF/CNPJ Emitente** - Documento do emitente
10. **RAZÃO SOCIAL EMITENTE** - Nome empresarial do emitente
11. **INSCRIÇÃO ESTADUAL EMITENTE** - IE do emitente
12. **UF EMITENTE** - Estado do emitente
13. **MUNICÍPIO EMITENTE** - Cidade do emitente
14. **CNPJ DESTINATÁRIO** - Documento do destinatário
15. **NOME DESTINATÁRIO** - Nome do destinatário
16. **UF DESTINATÁRIO** - Estado do destinatário
17. **INDICADOR IE DESTINATÁRIO** - Tipo de contribuinte
18. **DESTINO DA OPERAÇÃO** - Interno/Interestadual/Internacional
19. **CONSUMIDOR FINAL** - Flag de consumidor final
20. **PRESENÇA DO COMPRADOR** - Modalidade de compra
21. **VALOR NOTA FISCAL** - **Valor total da nota**

#### Exemplo de Registro:

```
CHAVE: 13250505914165000192550030000116841779221343
EMITENTE: CARBOXI INDUSTRIA E COMERCIO DE GASES LTDA (AM)
DESTINATÁRIO: DISTRITO SANITARIO ESPECIAL INDIGENA YANOMAMI (RR)
VALOR TOTAL: R$ 4.603,42
DATA: 01/05/2025
```

---

### 202505_NFe_NotaFiscalItem.csv (27 colunas)

**Representa:** Detalhamento **linha a linha** de cada produto/serviço da nota fiscal.

#### Colunas (18 em comum + 9 exclusivas):

**Colunas Compartilhadas (1-18):**
- Mesmas colunas de identificação da nota (CHAVE, MODELO, SÉRIE, etc.)
- Dados do emitente e destinatário

**Colunas Exclusivas de Itens (19-27):**

19. **NÚMERO PRODUTO** - Sequência do item na nota (1, 2, 3...)
20. **DESCRIÇÃO DO PRODUTO/SERVIÇO** - Descrição completa do item
21. **CÓDIGO NCM/SH** - Nomenclatura Comum do Mercosul
22. **NCM/SH (TIPO DE PRODUTO)** - Categoria fiscal do produto
23. **CFOP** - Código Fiscal de Operações e Prestações
24. **QUANTIDADE** - Quantidade comercializada
25. **UNIDADE** - Unidade de medida (M3, KG, UN, LT, etc.)
26. **VALOR UNITÁRIO** - Preço por unidade
27. **VALOR TOTAL** - Valor total do item (quantidade × valor unitário)

#### Exemplo de Registro:

```
CHAVE: 13250505914165000192550030000116841779221343
ITEM 1: OXIGENIO MEDICINAL - 1M3 /ONU:1072
NCM: 28044000 (Oxigênio)
CFOP: 6107
QUANTIDADE: 4,00 M3 × R$ 150,66 = R$ 602,64
```

---

## 🔗 Relacionamento entre Arquivos

### Modelo de Dados: 1:N (Um para Muitos)

```
┌──────────────────────────┐
│  NotaFiscal (Cabeçalho)  │
│  1 linha = 1 nota        │
└────────────┬─────────────┘
             │ CHAVE DE ACESSO
             │
             ↓ 1:N
┌──────────────────────────┐
│  NotaFiscalItem (Itens)  │
│  N linhas = N produtos   │
└──────────────────────────┘
```

### 18 Colunas em Comum (Chaves de Relacionamento):

✅ **CHAVE DE ACESSO** ← **Chave primária/estrangeira**
- MODELO, SÉRIE, NÚMERO
- NATUREZA DA OPERAÇÃO, DATA EMISSÃO
- CPF/CNPJ Emitente, RAZÃO SOCIAL EMITENTE
- INSCRIÇÃO ESTADUAL EMITENTE, UF EMITENTE, MUNICÍPIO EMITENTE
- CNPJ DESTINATÁRIO, NOME DESTINATÁRIO, UF DESTINATÁRIO
- INDICADOR IE DESTINATÁRIO
- DESTINO DA OPERAÇÃO, CONSUMIDOR FINAL, PRESENÇA DO COMPRADOR

---

## 📌 Diferenças Estruturais

### Colunas Exclusivas de NotaFiscal (3):

| Coluna | Descrição | Uso |
|--------|-----------|-----|
| **EVENTO MAIS RECENTE** | Status da nota (Autorização, Cancelamento, etc.) | Controle de ciclo de vida |
| **DATA/HORA EVENTO MAIS RECENTE** | Timestamp do último evento | Auditoria temporal |
| **VALOR NOTA FISCAL** | Soma total dos itens | **Consolidação financeira** |

### Colunas Exclusivas de NotaFiscalItem (9):

| Coluna | Descrição | Uso |
|--------|-----------|-----|
| **NÚMERO PRODUTO** | Sequência do item | Identificação dentro da nota |
| **DESCRIÇÃO DO PRODUTO/SERVIÇO** | Nome completo do produto | Análise de catálogo |
| **CÓDIGO NCM/SH** | Código fiscal | Classificação tributária |
| **NCM/SH (TIPO DE PRODUTO)** | Categoria do NCM | Agrupamento por tipo |
| **CFOP** | Código de operação | Análise fiscal |
| **QUANTIDADE** | Qtd comercializada | Análise de volume |
| **UNIDADE** | Unidade de medida | Padronização |
| **VALOR UNITÁRIO** | Preço unitário | Análise de precificação |
| **VALOR TOTAL** | Subtotal do item | Composição do valor da nota |

---

## 💡 Caso de Uso Prático

### Exemplo Real do Dataset:

**Nota Fiscal #11684 (CHAVE: 13250505914165000192550030000116841779221343)**

#### No arquivo NotaFiscal.csv (1 linha):
```
Emitente: CARBOXI INDUSTRIA E COMERCIO DE GASES LTDA (AM - Manaus)
Destinatário: DISTRITO SANITARIO ESPECIAL INDIGENA YANOMAMI (RR)
Operação: Interestadual | Consumidor Final
VALOR TOTAL DA NOTA: R$ 4.603,42
Data: 01/05/2025
```

#### No arquivo NotaFiscalItem.csv (3 linhas):
```
Item 1: OXIGENIO MEDICINAL - 1M3 /ONU:1072
        NCM: 28044000 (Oxigênio) | CFOP: 6107
        4,00 M3 × R$ 150,66 = R$ 602,64

Item 2: OXIGENIO MEDICINAL - 2M3/ ONU: 1072
        NCM: 28044000 (Oxigênio) | CFOP: 6107
        6,00 M3 × R$ 150,66 = R$ 903,96

Item 3: OXIGENIO MEDICINAL - 3,5M3 /ONU 1072
        NCM: 28044000 (Oxigênio) | CFOP: 6107
        28,00 M3 × R$ 71,25 = R$ 1.995,00

SOMA DOS ITENS: R$ 4.603,42 ✓ (confere com VALOR NOTA FISCAL)
```

---

## 🎯 Quando Usar Cada Arquivo

### Use **NotaFiscal.csv** para:
- ✅ Análise quantitativa de notas fiscais
- ✅ Agregações por emitente/destinatário
- ✅ Análises geográficas (UF origem/destino)
- ✅ Análises temporais (notas por período)
- ✅ Valores totais por operação
- ✅ Métricas de consumidor final vs. B2B

### Use **NotaFiscalItem.csv** para:
- ✅ Análise de produtos mais vendidos
- ✅ Análise por NCM/categoria fiscal
- ✅ Estudos de precificação
- ✅ Análise de volumes e unidades
- ✅ Composição detalhada das notas
- ✅ Análise de CFOP (natureza das operações)

### Use **JOIN entre ambos** para:
- ✅ Análise completa: "Quais produtos mais vendidos para RR?"
- ✅ Comparação: "Valor médio de nota por tipo de produto"
- ✅ Detecção de anomalias: "Notas com valor total divergente da soma dos itens"
- ✅ Análises cross-dimensionais: "NCM × UF Destinatário × Período"

---

## 🔍 Consulta SQL Conceitual (JOIN)

```sql
SELECT 
    nf.CHAVE_DE_ACESSO,
    nf.RAZAO_SOCIAL_EMITENTE,
    nf.UF_DESTINATARIO,
    nf.VALOR_NOTA_FISCAL,
    nfi.NUMERO_PRODUTO,
    nfi.DESCRICAO_DO_PRODUTO,
    nfi.QUANTIDADE,
    nfi.VALOR_TOTAL
FROM 
    NotaFiscal nf
INNER JOIN 
    NotaFiscalItem nfi 
    ON nf.CHAVE_DE_ACESSO = nfi.CHAVE_DE_ACESSO
WHERE 
    nf.UF_DESTINATARIO = 'RR'
    AND nfi.NCM_SH_TIPO_PRODUTO LIKE '%Oxigênio%'
ORDER BY 
    nf.DATA_EMISSAO DESC;
```

---

## 📊 Resumo Estatístico

| Métrica | NotaFiscal | NotaFiscalItem |
|---------|-----------|----------------|
| **Tamanho** | 67.09 MB | 296.30 MB |
| **Colunas** | 21 | 27 |
| **Colunas Compartilhadas** | 18 | 18 |
| **Colunas Exclusivas** | 3 | 9 |
| **Granularidade** | Nota (agregado) | Item (detalhado) |
| **Cardinalidade** | 1 por nota | N por nota |
| **Chave Primária** | CHAVE DE ACESSO | CHAVE DE ACESSO + NÚMERO PRODUTO |

---

## 🎓 Conclusão

Estes arquivos representam um **modelo relacional clássico de nota fiscal eletrônica**:

1. **NotaFiscal.csv** = **Cabeçalho/Master** (dados consolidados da nota)
2. **NotaFiscalItem.csv** = **Detalhe/Detail** (linha de produtos)

**Relacionamento:** 1:N via `CHAVE DE ACESSO`

**Proporção média:** ~4.4 itens por nota (296MB / 67MB)

**Integridade referencial:** Toda linha em `NotaFiscalItem` deve ter correspondência em `NotaFiscal`

**Validação financeira:** `SUM(NotaFiscalItem.VALOR_TOTAL)` deve igualar `NotaFiscal.VALOR_NOTA_FISCAL` para cada chave

---

## 📝 Recomendações para Análise

### Para Análise de Dados (Pandas/Python):
```python
import pandas as pd

# Carregar apenas cabeçalhos
nf = pd.read_csv('data/202505_NFe_NotaFiscal.csv', 
                 encoding='latin-1', sep=';')

nfi = pd.read_csv('data/202505_NFe_NotaFiscalItem.csv', 
                  encoding='latin-1', sep=';')

# JOIN
df_completo = nf.merge(nfi, on='CHAVE DE ACESSO', how='inner')

# Validação de integridade
validacao = nfi.groupby('CHAVE DE ACESSO')['VALOR TOTAL'].sum()
```

### Para Ingestão em Banco de Dados:
- Criar tabela `nota_fiscal` com PK em `CHAVE DE ACESSO`
- Criar tabela `nota_fiscal_item` com PK composta `(CHAVE DE ACESSO, NUMERO PRODUTO)`
- Estabelecer FK de `nota_fiscal_item` → `nota_fiscal`
- Indexar colunas de busca frequente: `DATA EMISSAO`, `UF DESTINATARIO`, `CODIGO NCM/SH`

### Para Sistema Multiagente (LangChain/RAG):
- Embeddings separados por tipo de dado (nota vs. item)
- Metadata incluindo `CHAVE DE ACESSO` para navegação entre documentos
- Chunks contextualizados: incluir dados do cabeçalho em cada item
- Queries vetoriais com filtros por UF, período, NCM

---

**Documento gerado automaticamente via script `compare_csvs.py`**  
**Projeto:** agentnfe-backend  
**Repositório:** roberto-fgv/agentnfe-backend
