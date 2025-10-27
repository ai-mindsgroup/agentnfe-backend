# 🧾 AgentNFe Backend - Sistema Multiagente para Validação Fiscal

Sistema multiagente inteligente para validação de Notas Fiscais Eletrônicas (NF-e) com inferência automática de estrutura CSV, validações fiscais e relatórios detalhados.

## ✨ Funcionalidades

- ✅ Validação inteligente de NF-e
- ✅ Inferência de estrutura CSV sem headers via LLM
- ✅ Validações fiscais: CNPJ, CFOP, chave de acesso, soma de itens
- ✅ Relatórios JSON estruturados com estatísticas

## 🚀 Início Rápido

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar
cp configs/.env.example configs/.env
# Editar configs/.env com suas credenciais

# Executar migrations
python scripts/run_migrations.py
```

## 📖 Uso

```python
from src.agent.nfe_validator_agent import NFeValidatorAgent
import asyncio

validator = NFeValidatorAgent(llm_provider="google")
result = asyncio.run(validator.validate(
    csv_path="data/notas_fiscais.csv",
    has_headers=False
))
```

## 📚 Documentação

- [Agente Validador](docs/2025-10-27_agente-validacao-nfe.md)
- [Roadmap](docs/PROXIMAS_ETAPAS_PRIORIZADAS.md)

## 📝 Licença

MIT License
