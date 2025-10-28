# 🚀 Guia Rápido de Configuração - Upload de NF-e

## ⚠️ Problema: "SUPABASE_URL/SUPABASE_KEY não configurados"

Você precisa configurar as credenciais do Supabase antes de usar o sistema.

---

## 📋 Solução Rápida (3 passos)

### Passo 1: Copiar arquivo de configuração

```powershell
# No diretório raiz do projeto
cd C:\Users\rsant\OneDrive\Documentos\Projects\agentnfe-backend

# Copiar .env.example para .env
Copy-Item configs\.env.example configs\.env
```

### Passo 2: O arquivo `.env` já está pré-configurado! ✅

O arquivo `configs/.env.example` já contém as configurações do Supabase:

```env
SUPABASE_URL=https://ncefmfiulpwssaajybtl.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DB_HOST=aws-1-sa-east-1.pooler.supabase.com
DB_PASSWORD=Alder1310
```

**Basta copiar para `.env` e está pronto!**

### Passo 3: Executar a migration

```powershell
# Criar as tabelas de NF-e no banco
python scripts/setup_nfe.py
```

---

## ✅ Teste de Configuração

```powershell
# Testar se a configuração está funcionando
python -c "from src.vectorstore.supabase_client import supabase; print('✅ Conexão OK')"
```

Se aparecer "✅ Conexão OK", está tudo certo!

---

## 🎯 Usar o Sistema de Upload

### Opção 1: Executar setup completo

```powershell
python scripts/setup_nfe.py
```

Este script irá:
1. ✅ Verificar conexão com banco
2. ✅ Criar tabelas (nota_fiscal, nota_fiscal_item, uploads)
3. ✅ Criar índices de performance
4. ✅ Criar views e funções
5. ✅ (Opcional) Fazer upload dos arquivos CSV

### Opção 2: Upload direto de arquivo

```powershell
# Upload automático (detecta tipo)
python -m src.data.nfe_uploader data/202505_NFe_NotaFiscal.csv usuario

# Upload dos dois arquivos via Python
python
>>> from src.data.nfe_uploader import upload_nfe_files
>>> results = upload_nfe_files(
...     nota_fiscal_path="data/202505_NFe_NotaFiscal.csv",
...     nota_fiscal_item_path="data/202505_NFe_NotaFiscalItem.csv"
... )
```

### Opção 3: Exemplos interativos

```powershell
python examples/nfe_upload_examples.py
```

---

## 🔍 Verificar se as tabelas existem

```powershell
python -c "from src.vectorstore.supabase_client import supabase; tables = supabase.table('uploads').select('*').limit(1).execute(); print('✅ Tabelas existem!')"
```

Se der erro "relation does not exist", você precisa executar a migration primeiro:

```powershell
python scripts/setup_nfe.py
```

---

## 📝 Resumo dos Comandos

```powershell
# 1. Copiar configurações
Copy-Item configs\.env.example configs\.env

# 2. Executar setup (cria tabelas)
python scripts/setup_nfe.py

# 3. Testar conexão
python -c "from src.vectorstore.supabase_client import supabase; print('✅ OK')"

# 4. Fazer upload
python -m src.data.nfe_uploader data/202505_NFe_NotaFiscal.csv
```

---

## ❓ Problemas Comuns

### Erro: "relation 'uploads' does not exist"
**Solução:** Execute a migration primeiro
```powershell
python scripts/setup_nfe.py
```

### Erro: "SUPABASE_URL/SUPABASE_KEY não configurados"
**Solução:** Copie o arquivo .env
```powershell
Copy-Item configs\.env.example configs\.env
```

### Erro: "ModuleNotFoundError: No module named 'src'"
**Solução:** Execute sempre do diretório raiz
```powershell
cd C:\Users\rsant\OneDrive\Documentos\Projects\agentnfe-backend
python -m src.data.nfe_uploader <arquivo>
```

---

## 🎉 Pronto!

Agora você pode fazer upload dos arquivos de NF-e:
- `data/202505_NFe_NotaFiscal.csv`
- `data/202505_NFe_NotaFiscalItem.csv`

E consultar os dados no Supabase! 🚀
