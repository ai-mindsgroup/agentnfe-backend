# Sessão de Desenvolvimento - 2025-11-06 12:00

## Objetivos da Sessão
 - [X] Implementar memória de longo prazo via embeddings e busca semântica

## Decisões Técnicas
 - **Extração Inteligente:** LLM classifica sensibilidade de cada fato; fatos safe (PREFERENCES) vs sensitive (LEARNING).
 - **Memória de Longo Prazo:** A cada 5 turnos, embeddings do histórico são salvos em `agent_memory_embeddings`; antes de responder, busca semântica recupera conversas passadas relevantes e injeta no contexto do LLM (similar ao GPT/Gemini).
## Implementações
### OrchestratorAgent
  - Extrai fatos conversacionais em `_extract_conversational_facts` (regex simples).
   - Extrai fatos via LLM em `_extract_conversational_facts_llm` com classificação de sensibilidade.
   - Particiona fatos safe/sensitive em `_partition_facts_safe_sensitive`.
  - Persiste/mescla fatos em Supabase via `ContextType.PREFERENCES` / `conversational_facts`.
   - Persiste fatos sensíveis em `ContextType.LEARNING` / `sensitive_facts`.
  - Adiciona `_facts_to_safe_summary` e injeta um resumo seguro no system prompt de `_handle_general_query`.
   - **Memória de Longo Prazo:**
     - A cada 5 turnos, persiste embeddings do histórico via `persist_conversation_memory`.
     - Antes de responder em `_handle_general_query`, recupera conversas passadas relevantes via `_recall_semantic_memory` (busca por similaridade em `agent_memory_embeddings`).
     - Injeta memórias recuperadas no system prompt do LLM para contexto completo.
  - Mantém salvamento do `user_profile` (nome) e compatibilidade com memória persistente.

## Testes Executados
- [X] Execução básica do fluxo `/chat` (manual):
  - Mensagem com dados: "Sou de São Paulo, trabalho na ACME, quero gráfico de barras de 2024-01-01 a 2024-03-01" → fatos extraídos e salvos.
  - Mensagem subsequente: system prompt exibe "Fatos conhecidos (seguros)" com cidade/empresa/período/preferências.
- [ ] Pytest automatizado específico (pendente): criar teste unitário focado em `_extract_conversational_facts`.

## Próximos Passos
1. Adicionar testes unitários para o extrator de fatos e para a injeção do resumo seguro.
2. Evoluir para extração semântica opcional via LLM com persistência (ContextType.LEARNING) e busca por similaridade.
3. Otimizar RAG (timeouts RPC, filtros por `ingestion_id`/`source_id`) e corrigir fallback LLM `generate` no RAG quando aplicável.

## Problemas e Soluções
### Problema: Precisávamos guardar informações além do nome do usuário
**Solução:** Implementado extrator de fatos com persistência em `agent_context` e injeção de resumo seguro no prompt do LLM.

## Métricas
- **Linhas de código:** + ~120 (aprox.)
- **Módulos criados:** 0 (somente alterações em `orchestrator_agent.py`)
- **Testes passando:** N/A (sem alteração na suíte de testes existente nesta sessão)

## Screenshots/Logs
- Logs: "✅ Fatos conversacionais salvos: [...]" indicam persistência bem-sucedida.
