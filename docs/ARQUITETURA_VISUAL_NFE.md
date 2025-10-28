# Arquitetura Visual do Sistema de Upload NF-e

## 🏗️ Fluxo Completo de Upload

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUÁRIO                                  │
│                                                                  │
│  Arquivos CSV:                                                   │
│  • 202505_NFe_NotaFiscal.csv (67 MB, 21 colunas)                │
│  • 202505_NFe_NotaFiscalItem.csv (296 MB, 27 colunas)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              MÓDULO: NFeUploader (Python)                        │
│                                                                  │
│  1. Detecta tipo de arquivo automaticamente                     │
│  2. Lê CSV com encoding latin-1 e separador ;                   │
│  3. Limpa e converte dados:                                     │
│     • Datas: DD/MM/YYYY → DATE                                  │
│     • Valores: vírgula → ponto                                  │
│     • NaN → NULL                                                │
│  4. Cria registro de upload                                     │
│  5. Processa em lotes de 1000 registros                         │
│  6. Atualiza progresso em tempo real                            │
│  7. Registra erros e conclusão                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              BANCO DE DADOS (PostgreSQL/Supabase)                │
│                                                                  │
│  ┌────────────────┐                                             │
│  │    uploads     │  ← Controle de uploads                      │
│  │  ──────────    │                                             │
│  │  • id (PK)     │                                             │
│  │  • filename    │                                             │
│  │  • file_type   │                                             │
│  │  • status      │                                             │
│  │  • progress    │                                             │
│  └────────┬───────┘                                             │
│           │                                                      │
│           ├──────────────────┬──────────────────┐               │
│           │                  │                  │               │
│           ↓                  ↓                  │               │
│  ┌─────────────────┐  ┌──────────────────┐     │               │
│  │  nota_fiscal    │  │ nota_fiscal_item │     │               │
│  │  ───────────    │  │  ────────────    │     │               │
│  │  • chave_acesso │←─│  • chave_acesso  │ (FK)│               │
│  │    (PK, 44 chr) │  │  • numero_produto│     │               │
│  │  • numero       │  │  • descricao     │     │               │
│  │  • data_emissao │  │  • codigo_ncm    │     │               │
│  │  • emitente     │  │  • quantidade    │     │               │
│  │  • destinatario │  │  • valor_unit    │     │               │
│  │  • valor_total  │  │  • valor_total   │     │               │
│  │  • upload_id    │──┘  • upload_id     │─────┘               │
│  └─────────────────┘  └──────────────────┘                      │
│                                                                  │
│  Relacionamento: 1 Nota → N Itens                               │
│  Integridade: FK + UNIQUE(chave_acesso, numero_produto)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Mapeamento de Colunas

### NotaFiscal.csv → Tabela nota_fiscal

```
CSV (21 colunas)                    BANCO (21 colunas + metadados)
───────────────────                 ──────────────────────────────
CHAVE DE ACESSO              →      chave_acesso (PK, VARCHAR 44)
MODELO                       →      modelo
SÉRIE                        →      serie (INTEGER)
NÚMERO                       →      numero (INTEGER)
NATUREZA DA OPERAÇÃO         →      natureza_operacao (TEXT)
DATA EMISSÃO                 →      data_emissao (DATE) ⚙️ conversão
EVENTO MAIS RECENTE          →      evento_recente
DATA/HORA EVENTO             →      data_hora_evento (TIMESTAMP) ⚙️ conversão
CPF/CNPJ Emitente            →      cpf_cnpj_emitente
RAZÃO SOCIAL EMITENTE        →      razao_social_emitente
INSCRIÇÃO ESTADUAL           →      ie_emitente
UF EMITENTE                  →      uf_emitente (CHAR 2)
MUNICÍPIO EMITENTE           →      municipio_emitente
CNPJ DESTINATÁRIO            →      cnpj_destinatario
NOME DESTINATÁRIO            →      nome_destinatario
UF DESTINATÁRIO              →      uf_destinatario (CHAR 2)
INDICADOR IE DESTINATÁRIO    →      indicador_ie_destinatario
DESTINO DA OPERAÇÃO          →      destino_operacao
CONSUMIDOR FINAL             →      consumidor_final
PRESENÇA DO COMPRADOR        →      presenca_comprador
VALOR NOTA FISCAL            →      valor_nota_fiscal (DECIMAL) ⚙️ conversão
                                    + upload_id (UUID, FK)
                                    + created_at (TIMESTAMP)
                                    + updated_at (TIMESTAMP)
```

### NotaFiscalItem.csv → Tabela nota_fiscal_item

```
CSV (27 colunas)                    BANCO (27 colunas + metadados)
───────────────────                 ──────────────────────────────
[18 colunas compartilhadas]  →      [mesmas colunas da nota_fiscal]
NÚMERO PRODUTO               →      numero_produto (INTEGER, PK composta)
DESCRIÇÃO PRODUTO            →      descricao_produto (TEXT)
CÓDIGO NCM/SH                →      codigo_ncm (VARCHAR 10)
NCM/SH (TIPO)                →      ncm_tipo_produto
CFOP                         →      cfop (VARCHAR 10)
QUANTIDADE                   →      quantidade (DECIMAL) ⚙️ conversão
UNIDADE                      →      unidade (VARCHAR 10)
VALOR UNITÁRIO               →      valor_unitario (DECIMAL) ⚙️ conversão
VALOR TOTAL                  →      valor_total (DECIMAL) ⚙️ conversão
                                    + upload_id (UUID, FK)
                                    + created_at (TIMESTAMP)
                                    + updated_at (TIMESTAMP)

Constraint: UNIQUE (chave_acesso, numero_produto)
```

---

## 🔄 Processo de Conversão de Dados

```
┌─────────────────────────┐
│   DADOS BRUTOS (CSV)    │
│   encoding: latin-1     │
│   separator: ;          │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  LEITURA (Pandas)       │
│  • detecta colunas      │
│  • identifica tipo      │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  LIMPEZA E CONVERSÃO    │
│                         │
│  Datas:                 │
│  "01/05/2025"           │
│     ↓                   │
│  DATE('2025-05-01')     │
│                         │
│  Decimais:              │
│  "4.603,42"             │
│     ↓                   │
│  4603.42                │
│                         │
│  Nulos:                 │
│  NaN / ""               │
│     ↓                   │
│  NULL                   │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  VALIDAÇÃO              │
│  • chave_acesso única   │
│  • FK válidas           │
│  • tipos corretos       │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  INSERÇÃO EM LOTES      │
│  batch_size = 1000      │
│  com tracking           │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  DADOS NO BANCO         │
│  prontos para análise   │
└─────────────────────────┘
```

---

## 🎯 Fluxo de Validação de Integridade

```
┌──────────────────┐
│  nota_fiscal     │
│  chave: ABC123   │
│  valor: 1000,00  │
└────────┬─────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
         ↓                  ↓                  ↓
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Item 1         │  │ Item 2         │  │ Item 3         │
│ valor: 300,00  │  │ valor: 400,00  │  │ valor: 300,00  │
└────────────────┘  └────────────────┘  └────────────────┘

VALIDAÇÃO:
  SUM(itens.valor_total) = 300 + 400 + 300 = 1000,00
  nota.valor_nota_fiscal = 1000,00
  DIFERENÇA = |1000 - 1000| = 0,00 < 0,01
  ✅ VÁLIDO
```

---

## 📈 Modelo de Views e Funções

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE DADOS                          │
│                                                             │
│  nota_fiscal  ←→  nota_fiscal_item  ←→  uploads            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA DE VISUALIZAÇÃO                     │
│                                                             │
│  ┌──────────────────────┐   ┌──────────────────────┐       │
│  │ vw_upload_stats      │   │ vw_nota_fiscal_resumo│       │
│  │ ────────────────     │   │ ─────────────────    │       │
│  │ • progresso          │   │ • nota + qtd_itens   │       │
│  │ • status             │   │ • validação valor    │       │
│  │ • métricas           │   │ • agregações         │       │
│  └──────────────────────┘   └──────────────────────┘       │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ vw_produtos_mais_vendidos                     │          │
│  │ ──────────────────────────────────            │          │
│  │ • ranking por NCM                             │          │
│  │ • quantidade e valores                        │          │
│  │ • agregações por categoria                    │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 CAMADA DE FUNÇÕES                           │
│                                                             │
│  fn_validar_nota_fiscal(chave)                             │
│     → retorna integridade financeira                        │
│                                                             │
│  fn_estatisticas_periodo(data_inicio, data_fim)            │
│     → retorna métricas agregadas do período                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Fluxo de Uso pelo Usuário

```
PASSO 1: Setup Inicial (uma vez)
┌──────────────────────────────────┐
│  python scripts/setup_nfe.py    │
│                                  │
│  → Cria tabelas                  │
│  → Cria índices                  │
│  → Cria views e funções          │
└──────────────────────────────────┘
                 │
                 ↓
PASSO 2: Upload de Arquivos
┌──────────────────────────────────────────────────────┐
│  OPÇÃO A: Linha de comando                           │
│  $ python -m src.data.nfe_uploader arquivo.csv user  │
│                                                       │
│  OPÇÃO B: Script Python                              │
│  >>> from src.data.nfe_uploader import upload_nfe... │
│  >>> results = upload_nfe_files(...)                 │
│                                                       │
│  OPÇÃO C: Exemplos interativos                       │
│  $ python examples/nfe_upload_examples.py            │
└──────────────────────────────────────────────────────┘
                 │
                 ↓
PASSO 3: Monitoramento
┌──────────────────────────────────┐
│  SELECT * FROM uploads;          │
│  SELECT * FROM vw_upload_stats;  │
│                                  │
│  → Acompanha progresso           │
│  → Verifica erros                │
└──────────────────────────────────┘
                 │
                 ↓
PASSO 4: Análises
┌────────────────────────────────────────────┐
│  • Queries diretas nas tabelas             │
│  • Uso de views pré-configuradas           │
│  • Chamada de funções SQL                  │
│  • Integração com sistema multiagente/RAG  │
└────────────────────────────────────────────┘
```

---

## 🎨 Exemplo Real com Dados Visuais

```
┌─────────────────────────────────────────────────────────────┐
│  NOTA FISCAL #11684                                         │
│  Chave: 13250505914165000192550030000116841779221343        │
├─────────────────────────────────────────────────────────────┤
│  Emitente:                                                  │
│    CARBOXI INDUSTRIA E COMERCIO DE GASES LTDA               │
│    CNPJ: 05.914.165/0001-92                                 │
│    UF: AM - Manaus                                          │
│                                                             │
│  Destinatário:                                              │
│    DISTRITO SANITARIO ESPECIAL INDIGENA YANOMAMI            │
│    CNPJ: 394.544.003.362                                    │
│    UF: RR                                                   │
│                                                             │
│  Data: 01/05/2025                                           │
│  Operação: 2 - OPERAÇÃO INTERESTADUAL                       │
│  Consumidor Final: SIM                                      │
├─────────────────────────────────────────────────────────────┤
│  ITENS:                                                     │
│                                                             │
│  [1] OXIGENIO MEDICINAL - 1M3 /ONU:1072                    │
│      NCM: 28044000 | CFOP: 6107                             │
│      4,00 M3 × R$ 150,66 = R$ 602,64                        │
│                                                             │
│  [2] OXIGENIO MEDICINAL - 2M3/ ONU: 1072                   │
│      NCM: 28044000 | CFOP: 6107                             │
│      6,00 M3 × R$ 150,66 = R$ 903,96                        │
│                                                             │
│  [3] OXIGENIO MEDICINAL - 3,5M3 /ONU 1072                  │
│      NCM: 28044000 | CFOP: 6107                             │
│      28,00 M3 × R$ 71,25 = R$ 1.995,00                      │
├─────────────────────────────────────────────────────────────┤
│  TOTAL DA NOTA: R$ 4.603,42                                 │
│  SOMA DOS ITENS: R$ 4.603,42                                │
│  VALIDAÇÃO: ✅ OK (diferença: R$ 0,00)                      │
└─────────────────────────────────────────────────────────────┘

REPRESENTAÇÃO NO BANCO:

nota_fiscal (1 linha)
┌───────────────┬─────────┬──────────────┬──────────┐
│ chave_acesso  │ numero  │ data_emissao │ valor_nf │
├───────────────┼─────────┼──────────────┼──────────┤
│ 132505...     │ 11684   │ 2025-05-01   │ 4603.42  │
└───────────────┴─────────┴──────────────┴──────────┘

nota_fiscal_item (3 linhas)
┌───────────────┬───────────┬─────────────┬──────────┬──────────┐
│ chave_acesso  │ num_prod  │ descricao   │ qtd      │ valor    │
├───────────────┼───────────┼─────────────┼──────────┼──────────┤
│ 132505...     │ 1         │ OXIGENIO... │ 4.00     │ 602.64   │
│ 132505...     │ 2         │ OXIGENIO... │ 6.00     │ 903.96   │
│ 132505...     │ 3         │ OXIGENIO... │ 28.00    │ 1995.00  │
└───────────────┴───────────┴─────────────┴──────────┴──────────┘
```

---

## 📊 Estatísticas de Performance

```
ARQUIVO: 202505_NFe_NotaFiscal.csv
├─ Tamanho: 67.09 MB
├─ Linhas estimadas: ~50.000 - 100.000
├─ Tempo de upload: ~2-5 minutos
└─ Batch size: 1000 registros

ARQUIVO: 202505_NFe_NotaFiscalItem.csv
├─ Tamanho: 296.30 MB
├─ Linhas estimadas: ~200.000 - 500.000
├─ Tempo de upload: ~10-20 minutos
└─ Batch size: 1000 registros

ÍNDICES CRIADOS: 15
VIEWS CRIADAS: 3
FUNÇÕES CRIADAS: 2

ESPAÇO EM BANCO: ~400-500 MB (com índices)
```

---

**Documento Visual:** Arquitetura e Fluxos do Sistema NF-e  
**Versão:** 1.0  
**Data:** 28 de Outubro de 2025
