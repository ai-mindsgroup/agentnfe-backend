# **Matriz de Complexidade e Prioridade \- MVP Agente Fiscal IA**

**Última Atualização:** 28 de Outubro de 2025

## 📊 Resumo do Status

| Métrica | Valor | Observação |
|---------|-------|------------|
| **Progresso Geral** | **25%** | 8 de 32 tarefas concluídas |
| **Backend Core** | **54%** | 7/13 tarefas concluídas |
| **Backend Relatórios** | **0%** | 0/3 tarefas (não iniciado) |
| **Frontend** | **0%** | 0/7 tarefas (não iniciado) |
| **Refatoração** | **0%** | 0/6 tarefas (não iniciado) |

### 🎯 Conquistas Recentes
- ✅ **NFeTaxSpecialistAgent implementado** (754 linhas + 316 exemplos)
- ✅ **Upload CSV NF-e funcional** (321K registros processados)
- ✅ **Schema banco completo** (3 tabelas + views + functions)
- ✅ **Validações fiscais** (CFOP, NCM, valores, consistência)

### ⏳ Bloqueadores Críticos
1. 🔴 **Módulo de fraude não removido** - Código legado presente
2. 🔴 **Endpoints de relatórios ausentes** - Funcionalidade essencial MVP
3. 🔴 **Frontend não iniciado** - Interface zero

---

Esta matriz visa auxiliar na priorização e planejamento do desenvolvimento do MVP (Minimum Viable Product) do Agente Fiscal IA, classificando os principais Épicos e Tarefas Técnicas do backlog quanto à sua complexidade estimada e importância para a primeira entrega funcional.

**Legenda de Status:**
* ✅ **CONCLUÍDO:** Implementado e testado
* 🟡 **PARCIAL:** Parcialmente implementado ou com pendências
* ⏳ **PENDENTE:** Não iniciado

**Legenda:**

* **Complexidade:**  
  * **Baixa:** Tarefa relativamente simples, com requisitos bem definidos e poucas dependências. Envolve tecnologia conhecida.  
  * **Média:** Tarefa com alguma complexidade técnica ou de requisitos, pode envolver integrações ou lógica de negócio moderada.  
  * **Alta:** Tarefa complexa, envolvendo lógica de negócio intrincada, novas tecnologias, integrações desafiadoras ou requisitos ainda não totalmente definidos. Alto risco ou incerteza.  
* **Prioridade MVP:**  
  * **Essencial:** Funcionalidade *core* sem a qual o MVP não entrega o valor mínimo proposto.  
  * **Importante:** Funcionalidade que agrega valor significativo ao MVP, mas poderia ser adiada em caso extremo.  
  * **Desejável:** Funcionalidade interessante, mas não crítica para a validação inicial do produto.

**Observação:** Esta é uma estimativa inicial e deve ser revisada e ajustada pela equipe de desenvolvimento.

| Item do Backlog | Complexidade | Prioridade MVP | Status | Notas / Justificativa |
| :---- | :---- | :---- | :---- | :---- |
| **Backend (agentnfe-backend)** |  |  |  |  |
| **Épico: Isolar/Remover Módulo de Fraude** | **Média** | **Essencial** | ⏳ **PENDENTE** | Refatoração pode ter efeitos colaterais. Requer cuidado para não quebrar o que fica. Limpeza do DB exige atenção. |
| ↳ Tarefa: Mapear código/dados | Baixa | Essencial | ⏳ PENDENTE |  |
| ↳ Tarefa: Remover código/arquivos (Backend/Frontend) | Média | Essencial | ⏳ PENDENTE | Requer busca cuidadosa e remoção em múltiplos locais. |
| ↳ Tarefa: Remover Endpoints API | Baixa | Essencial | ⏳ PENDENTE |  |
| ↳ Tarefa: Limpar DB Vetorial | Baixa | Essencial | ⏳ PENDENTE | Script SQL simples, mas requer confirmação. |
| ↳ Tarefa: Testar funcionalidade básica pós-remoção | Baixa | Essencial | ⏳ PENDENTE |  |
| **Épico: Parsing de Documentos Fiscais (XML NF-e)** | **Alta** | **Essencial** | 🟡 **PARCIAL** | ✅ CSV implementado (321K registros). ⏳ XML NF-e pendente. |
| ↳ Tarefa: Desenvolver parser XML NF-e (campos MVP) | Alta | Essencial | 🟡 PARCIAL | ✅ CSV completo. ⏳ XML com namespaces pendente. |
| ↳ Tarefa: Adaptar ingestão (data\_ingestor.py) | Média | Essencial | ✅ **CONCLUÍDO** | ✅ `NFeUploader` implementado com detecção automática. |
| ↳ Tarefa: Modelar/Implementar armazenamento (Supabase) | Média | Essencial | ✅ **CONCLUÍDO** | ✅ Migration 0008: 3 tabelas + views + functions + índices. |
| **Épico: Validações Fiscais Essenciais (MVP)** | **Média** | **Importante** | 🟡 **PARCIAL** | ✅ Validações implementadas. ⏳ Integração no upload e API pendentes. |
| ↳ Tarefa: Definir/Implementar 2-3 regras | Média | Importante | ✅ **CONCLUÍDO** | ✅ CFOP, NCM, valores, consistência UF implementados. |
| ↳ Tarefa: Integrar validações na ingestão | Baixa | Importante | ⏳ PENDENTE | Validações existem mas não integradas no upload. |
| ↳ Tarefa: Criar API para inconsistências | Baixa | Importante | ⏳ PENDENTE | Endpoint `/nfe/{id}/inconsistencias` não criado. |
| **Épico: Base de Conhecimento Fiscal (Legislação MVP)** | **Média** | **Importante** | 🟡 **PARCIAL** | ✅ Infraestrutura RAG pronta. ⏳ Conteúdo legislação pendente. |
| ↳ Tarefa: Definir/Adquirir conteúdo inicial | Baixa | Importante | ⏳ PENDENTE | LC 123/2006, RICMS não carregados. |
| ↳ Tarefa: Estruturar/Carregar base inicial (RAG) | Média | Importante | 🟡 PARCIAL | ✅ Sistema RAG funcional. ⏳ Legislação específica ausente. |
| ↳ Tarefa: Documentar processo manual atualização | Baixa | Importante | ⏳ PENDENTE |  |
| ↳ Tarefa: Ajustar prompts rag\_agent | Média | Importante | 🟡 PARCIAL | ✅ Prompts fiscais em NFeTaxSpecialistAgent. |
| **Épico: Geração de Relatório Fiscal Básico (MVP)** | **Média** | **Essencial** | ⏳ **PENDENTE** | Dados estruturados prontos, mas endpoint não implementado. |
| ↳ Tarefa: Definir formato/parâmetros relatório | Baixa | Essencial | ⏳ PENDENTE | Especificação de layout não criada. |
| ↳ Tarefa: Criar serviço backend relatório | Média | Essencial | ⏳ PENDENTE | Lógica SQL/ORM para filtro por período ausente. |
| ↳ Tarefa: Criar endpoint API relatório | Baixa | Essencial | ⏳ PENDENTE | Rota `/relatorios/listagem_nfe` não existe. |
| Tarefa: Refatorar agentes (integração mínima) | Média | Essencial | 🟡 PARCIAL | ✅ NFeTaxSpecialistAgent criado. ⏳ Orquestrador não integrado. |
| Tarefa: Revisar prompts principais (contexto fiscal) | Baixa | Importante | ✅ **CONCLUÍDO** | ✅ Prompts fiscais implementados em specialist agent. |
| Tarefa: Criar testes unitários essenciais (MVP) | Média | Importante | ⏳ PENDENTE | Testes para parsing/relatório não criados. |
| **Frontend (agentnfe-frontend)** |  |  |  |  |
| **Épico: Seção Básica de Relatórios (MVP)** | **Média** | **Essencial** | ⏳ **PENDENTE** | Backend pronto, frontend não iniciado. |
| ↳ Tarefa: Desenhar interface simples relatório | Baixa | Essencial | ⏳ PENDENTE |  |
| ↳ Tarefa: Criar rota/página React Relatórios | Baixa | Essencial | ⏳ PENDENTE |  |
| ↳ Tarefa: Implementar Tabela (shadcn/ui/table) | Média | Essencial | ⏳ PENDENTE | Configurar colunas, dados, talvez paginação. |
| ↳ Tarefa: Integrar com API relatório | Média | Essencial | ⏳ PENDENTE | Lógica de fetch, tratamento de estado (loading/erro), filtros de data. |
| **Épico: UX Funcional para MVP** | **Baixa** | **Essencial** | ⏳ **PENDENTE** | Ajustes pontuais na UI existente para suportar o fluxo MVP. |
| ↳ Tarefa: Ajustar upload para XML | Baixa | Essencial | ⏳ PENDENTE | Permitir extensão .xml e dar feedback. |
| ↳ Tarefa: Adicionar filtro período (Frontend) | Baixa | Essencial | ⏳ PENDENTE | Usar componentes de calendário/data. |
| Tarefa: Garantir responsividade básica | Baixa | Importante | ⏳ PENDENTE | Verificar novas telas em diferentes resoluções. |

**Análise Preliminar para MVP:**

* **Essenciais (Alta Prioridade):** O isolamento da fraude, o parsing de NF-e, o armazenamento estruturado, o relatório básico (backend e frontend) e a integração mínima dos agentes são cruciais. Sem eles, o sistema não funciona ou não entrega o valor fiscal mínimo.  
* **Importantes:** As validações fiscais e a base de conhecimento RAG, embora muito valiosas, podem talvez ter uma implementação *muito* simplificada no primeiríssimo MVP, focando em demonstrar o *mecanismo* em vez da *abrangência*. Os testes também são importantes, mas podem começar focados no caminho feliz.  
* **Complexidade Alta:** O parsing do XML NF-e é provavelmente o maior desafio técnico individual.

**Recomendação:**

1. Iniciar pelo **Isolamento da Fraude** para limpar a base de código.  
2. Focar no fluxo **Parsing NF-e \-\> Armazenamento \-\> Relatório Básico (Backend \+ Frontend)**.  
3. Implementar a **Base de Conhecimento Mínima** e ajustar o **RAG/Orquestrador**.  
4. Adicionar as **Validações Fiscais Essenciais**.  
5. Reforçar com **Testes Unitários**.

Esta matriz deve ser o ponto de partida para a discussão da equipe, que poderá refinar as estimativas de complexidade e ajustar as prioridades com base no conhecimento técnico e na visão de negócio.