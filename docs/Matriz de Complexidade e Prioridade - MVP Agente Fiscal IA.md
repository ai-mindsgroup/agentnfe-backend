# **Matriz de Complexidade e Prioridade \- MVP Agente Fiscal IA**

Esta matriz visa auxiliar na priorização e planejamento do desenvolvimento do MVP (Minimum Viable Product) do Agente Fiscal IA, classificando os principais Épicos e Tarefas Técnicas do backlog quanto à sua complexidade estimada e importância para a primeira entrega funcional.

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

| Item do Backlog | Complexidade | Prioridade MVP | Notas / Justificativa |
| :---- | :---- | :---- | :---- |
| **Backend (agentnfe-backend)** |  |  |  |
| **Épico: Isolar/Remover Módulo de Fraude** | **Média** | **Essencial** | Refatoração pode ter efeitos colaterais. Requer cuidado para não quebrar o que fica. Limpeza do DB exige atenção. |
| ↳ Tarefa: Mapear código/dados | Baixa | Essencial |  |
| ↳ Tarefa: Remover código/arquivos (Backend/Frontend) | Média | Essencial | Requer busca cuidadosa e remoção em múltiplos locais. |
| ↳ Tarefa: Remover Endpoints API | Baixa | Essencial |  |
| ↳ Tarefa: Limpar DB Vetorial | Baixa | Essencial | Script SQL simples, mas requer confirmação. |
| ↳ Tarefa: Testar funcionalidade básica pós-remoção | Baixa | Essencial |  |
| **Épico: Parsing de Documentos Fiscais (XML NF-e)** | **Alta** | **Essencial** | Lidar com a complexidade do XML NF-e, namespaces e variações é desafiador. Base para todo o resto. |
| ↳ Tarefa: Desenvolver parser XML NF-e (campos MVP) | Alta | Essencial | Exige conhecimento do layout XML e tratamento robusto de erros/variações. |
| ↳ Tarefa: Adaptar ingestão (data\_ingestor.py) | Média | Essencial | Integrar o novo parser no fluxo existente. |
| ↳ Tarefa: Modelar/Implementar armazenamento (Supabase) | Média | Essencial | Definir schema relacional adequado para NF-e e itens. |
| **Épico: Validações Fiscais Essenciais (MVP)** | **Média** | **Importante** | A complexidade depende das regras escolhidas, mas a integração no fluxo e API são de esforço moderado. |
| ↳ Tarefa: Definir/Implementar 2-3 regras | Média | Importante | Requer algum conhecimento fiscal para definir regras úteis e corretas. |
| ↳ Tarefa: Integrar validações na ingestão | Baixa | Importante |  |
| ↳ Tarefa: Criar API para inconsistências | Baixa | Importante | Endpoint de consulta simples. |
| **Épico: Base de Conhecimento Fiscal (Legislação MVP)** | **Média** | **Importante** | O carregamento inicial é Média (chunking, metadados). A resposta do RAG depende da qualidade do carregamento/prompts. |
| ↳ Tarefa: Definir/Adquirir conteúdo inicial | Baixa | Importante |  |
| ↳ Tarefa: Estruturar/Carregar base inicial (RAG) | Média | Importante | Chunking e metadados requerem atenção para boa performance do RAG. |
| ↳ Tarefa: Documentar processo manual atualização | Baixa | Importante |  |
| ↳ Tarefa: Ajustar prompts rag\_agent | Média | Importante | Engenharia de prompt pode exigir iterações. |
| **Épico: Geração de Relatório Fiscal Básico (MVP)** | **Média** | **Essencial** | Envolve consulta ao DB estruturado e formatação de saída via API. |
| ↳ Tarefa: Definir formato/parâmetros relatório | Baixa | Essencial |  |
| ↳ Tarefa: Criar serviço backend relatório | Média | Essencial | Lógica de consulta SQL/ORM nos dados parseados. |
| ↳ Tarefa: Criar endpoint API relatório | Baixa | Essencial |  |
| Tarefa: Refatorar agentes (integração mínima) | Média | Essencial | Ajustar orquestrador e RAG para usar novas fontes de dados (DB estruturado, base legal). |
| Tarefa: Revisar prompts principais (contexto fiscal) | Baixa | Importante | Ajustes iniciais nos prompts existentes. |
| Tarefa: Criar testes unitários essenciais (MVP) | Média | Importante | Criar infraestrutura de testes para novas funcionalidades (parsing, relatório). |
| **Frontend (agentnfe-frontend)** |  |  |  |
| **Épico: Seção Básica de Relatórios (MVP)** | **Média** | **Essencial** | Criar nova seção, componente de tabela e integrar com API. |
| ↳ Tarefa: Desenhar interface simples relatório | Baixa | Essencial |  |
| ↳ Tarefa: Criar rota/página React Relatórios | Baixa | Essencial |  |
| ↳ Tarefa: Implementar Tabela (shadcn/ui/table) | Média | Essencial | Configurar colunas, dados, talvez paginação. |
| ↳ Tarefa: Integrar com API relatório | Média | Essencial | Lógica de fetch, tratamento de estado (loading/erro), filtros de data. |
| **Épico: UX Funcional para MVP** | **Baixa** | **Essencial** | Ajustes pontuais na UI existente para suportar o fluxo MVP. |
| ↳ Tarefa: Ajustar upload para XML | Baixa | Essencial | Permitir extensão .xml e dar feedback. |
| ↳ Tarefa: Adicionar filtro período (Frontend) | Baixa | Essencial | Usar componentes de calendário/data. |
| Tarefa: Garantir responsividade básica | Baixa | Importante | Verificar novas telas em diferentes resoluções. |

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