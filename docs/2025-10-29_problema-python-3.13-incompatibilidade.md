# 🐍 Problema: Incompatibilidade Python 3.13 com Transformers

**Data:** 29 de Outubro de 2025  
**Status:** ⚠️ CRÍTICO - Ambiente incompatível  
**Impacto:** API não pode ser executada

---

## 🔴 Problema Identificado

### Erro ao Executar API

```bash
python app/main.py
python api_completa.py

# Erro:
File "transformers\utils\import_utils.py", line 2588
    with open(os.path.join(directory, module_name), encoding="utf-8") as f:
KeyboardInterrupt
```

### Causa Raiz

**Python 3.13.2** está instalado, mas o projeto requer **Python 3.10-3.12**.

A biblioteca `transformers==4.56.2` (usada por sentence-transformers e langchain) **NÃO é compatível com Python 3.13**.

### Verificação da Versão

```bash
python --version
# Output: Python 3.13.2
```

---

## 📋 Requisitos do Projeto

Conforme documentação do projeto:

```
Python 3.10+ requerido devido a type annotations (str | None)
```

**Versões recomendadas:**
- ✅ Python 3.10.x
- ✅ Python 3.11.x
- ✅ Python 3.12.x
- ❌ Python 3.13.x (incompatível com transformers)

---

## 🔧 Soluções Possíveis

### Opção 1: Instalar Python 3.12 (RECOMENDADO)

**Passos:**

1. **Baixar Python 3.12:**
   - Site: https://www.python.org/downloads/
   - Versão: Python 3.12.x (latest stable)

2. **Instalar lado a lado com Python 3.13:**
   ```bash
   # Durante instalação, marcar:
   # ☑ Add Python 3.12 to PATH
   # ☑ Install for all users
   ```

3. **Criar ambiente virtual com Python 3.12:**
   ```powershell
   # Remover ambiente antigo
   Remove-Item -Recurse -Force .venv
   
   # Criar novo ambiente com Python 3.12
   py -3.12 -m venv .venv
   
   # Ativar
   .venv\Scripts\Activate.ps1
   
   # Verificar versão
   python --version
   # Output esperado: Python 3.12.x
   ```

4. **Reinstalar dependências:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Testar API:**
   ```powershell
   python app/main.py
   # ou
   python api_completa.py
   ```

---

### Opção 2: Downgrade Temporário para Python 3.11

```powershell
# Instalar Python 3.11
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Opção 3: Usar pyenv (Gerenciamento de Múltiplas Versões)

**Windows (pyenv-win):**

```powershell
# Instalar pyenv-win
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

# Instalar Python 3.12
pyenv install 3.12.0

# Definir como padrão para o projeto
pyenv local 3.12.0

# Criar ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

---

### Opção 4: Atualizar Transformers (NÃO RECOMENDADO)

⚠️ **Não funciona ainda** - transformers 5.x ainda não foi lançado com suporte Python 3.13.

```powershell
# Não executar - apenas para referência futura
pip install --upgrade transformers
```

---

## 📊 Tabela de Compatibilidade

| Componente | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 |
|------------|-------------|-------------|-------------|-------------|
| **transformers 4.56.2** | ✅ | ✅ | ✅ | ❌ |
| **sentence-transformers 5.1.1** | ✅ | ✅ | ✅ | ❌ |
| **langchain 0.3.27** | ✅ | ✅ | ✅ | ⚠️ |
| **torch 2.8.0** | ✅ | ✅ | ✅ | ⚠️ |
| **FastAPI 0.111.0** | ✅ | ✅ | ✅ | ✅ |
| **Pandas 2.2.3** | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 Ação Recomendada

### Curto Prazo (AGORA)

1. **Instalar Python 3.12:**
   ```powershell
   # Baixar e instalar Python 3.12
   # https://www.python.org/downloads/release/python-3120/
   ```

2. **Recriar ambiente virtual:**
   ```powershell
   Remove-Item -Recurse -Force .venv
   py -3.12 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Reinstalar dependências:**
   ```powershell
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

4. **Testar API:**
   ```powershell
   python api_completa.py
   ```

### Longo Prazo

1. **Documentar versão Python em README:**
   ```markdown
   ## Requisitos
   - Python 3.12.x (recomendado)
   - Python 3.10-3.12 (suportado)
   - ❌ Python 3.13+ (incompatível)
   ```

2. **Adicionar verificação de versão no código:**
   ```python
   import sys
   if sys.version_info >= (3, 13):
       raise RuntimeError(
           "Python 3.13+ não é suportado. "
           "Use Python 3.10-3.12"
       )
   ```

3. **Configurar CI/CD para testar em Python 3.10, 3.11, 3.12**

---

## 📝 Checklist de Resolução

- [ ] Instalar Python 3.12.x
- [ ] Remover ambiente virtual antigo (.venv)
- [ ] Criar novo ambiente com Python 3.12
- [ ] Ativar novo ambiente
- [ ] Verificar versão do Python (`python --version`)
- [ ] Atualizar pip, setuptools, wheel
- [ ] Instalar requirements.txt
- [ ] Testar api_completa.py
- [ ] Testar app/main.py
- [ ] Atualizar documentação README
- [ ] Adicionar verificação de versão Python
- [ ] Commit das alterações

---

## 🔍 Verificação Pós-Instalação

```powershell
# 1. Verificar versão Python
python --version
# Esperado: Python 3.12.x

# 2. Verificar pip
pip --version
# Esperado: pip 24.x (python 3.12)

# 3. Verificar instalação transformers
python -c "import transformers; print(transformers.__version__)"
# Esperado: 4.56.2

# 4. Verificar sentence-transformers
python -c "import sentence_transformers; print(sentence_transformers.__version__)"
# Esperado: 5.1.1

# 5. Verificar langchain
python -c "import langchain; print(langchain.__version__)"
# Esperado: 0.3.27

# 6. Testar API
python api_completa.py
# Esperado: API subindo na porta 8011
```

---

## 📚 Referências

- **Python Releases:** https://www.python.org/downloads/
- **Transformers Compatibility:** https://github.com/huggingface/transformers/issues/
- **Sentence Transformers:** https://www.sbert.net/docs/installation.html
- **pyenv-win:** https://github.com/pyenv-win/pyenv-win

---

## 🚨 Notas Importantes

1. **Não delete Python 3.13** - Pode ser útil para outros projetos
2. **Use py launcher** - `py -3.12` para selecionar versão específica
3. **Configure IDE** - VSCode deve usar Python 3.12 do .venv
4. **CI/CD** - Configure para usar Python 3.12 em produção

---

**Última Atualização:** 29 de Outubro de 2025  
**Status:** ⏳ Aguardando instalação Python 3.12  
**Próximo Passo:** Instalar Python 3.12 e recriar ambiente virtual
