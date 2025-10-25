# **Backlog do Projeto: Agente IA Especializado em Documentos Fiscais (Detalhado para MVP)**

Este backlog detalha as funcionalidades e tarefas prioritárias para construir um MVP (Minimum Viable Product) funcional do agente fiscal, alinhado à proposta original.

**Legenda:**

* **AC:** Critério de Aceite (Com mais detalhes para clareza na validação)

## **Backend (agentnfe-backend)**

### **1\. Especialização Fiscal (Core) \- A base da inteligência do Agente**

* **\[Épico\] Implementar Parsing de Documentos Fiscais (XML):** Objetivo: Capacitar o sistema a ler e interpretar a estrutura rica dos XMLs de NF-e, transformando-os em dados úteis para análise e consulta.  
  * **AC:** O sistema processa XMLs de NF-e válidos, extrai com precisão um conjunto definido de campos chave (cabeçalho, emitente, destinatário, totais, itens e impostos principais por item), e armazena esses dados de forma relacional no Supabase. O processo de ingestão identifica NF-e e aplica o parser correto, registrando erros de forma informativa. *(CT-e fica para V2)*  
  * **\[Tarefa Técnica\] Desenvolver módulo de parsing robusto para XML de NF-e.** (Foco nos campos essenciais: Chave de Acesso, CNPJ Emitente/Destinatário, Data Emissão, Valor Total, Valor ICMS/ST/IPI, e detalhes básicos dos itens como CFOP, NCM, Valor).  
    * AC: Extrai os campos definidos com exatidão; Retorna um objeto Pydantic validado; Lida com namespaces XML; Reporta erros específicos (ex: tag vNF não encontrada).  
  * **\[Tarefa Técnica\] Adaptar o processo de ingestão (data\_ingestor.py) para orquestrar o uso do parser de NF-e.**  
    * AC: Identifica arquivos .xml durante o upload; Chama o parser de NF-e; Encaminha os dados estruturados para armazenamento; Registra falhas de parsing sem interromper o lote.  
  * **\[Tarefa Técnica\] Modelar e implementar o armazenamento dos dados estruturados de NF-e no Supabase.**  
    * AC: Tabelas nfe\_header e nfe\_items criadas no PostgreSQL/Supabase com tipos de dados corretos; Ingestão insere dados com sucesso, mantendo relação header-items; Embeddings (se mantidos) são associados ao ID do nfe\_header.  
* **\[Épico\] Implementar Validações Fiscais Essenciais (MVP):** Objetivo: Agregar valor inicial detectando inconsistências óbvias nos documentos processados, ajudando o usuário a identificar problemas rapidamente.  
  * **AC:** O sistema aplica um pequeno conjunto de regras de validação cruciais (ex: CFOP vs. Natureza da Operação básica, Total da Nota vs. Soma dos Itens) aos dados extraídos das NF-e. Inconsistências são registradas e podem ser consultadas via API.  
  * **\[Tarefa\] Definir e implementar 2-3 regras de validação iniciais críticas.** (Ex: Soma dos itens bate com total da nota? CFOP indica operação interna/externa corretamente com base nos CNPJs?).  
    * AC: Regras documentadas; Implementação em Python correta; Considera apenas cenário mais comum inicialmente.  
  * **\[Tarefa\] Integrar validações no fluxo de ingestão de NF-e.**  
    * AC: Validações executadas após parsing; Resultado (OK/Falha \+ mensagem) armazenado na tabela nfe\_header.  
  * **\[Tarefa\] Criar API para consultar inconsistências por documento.**  
    * AC: Endpoint /nfe/{id}/inconsistencias retorna a lista de problemas registrados para aquela NF-e.  
* **\[Épico\] Base de Conhecimento Fiscal (Legislação \- MVP Focado):** Objetivo: Criar uma base inicial mínima de legislação para permitir que o RAG responda perguntas básicas sobre ICMS ou Simples Nacional, validando o mecanismo.  
  * **AC:** O sistema possui uma base vetorial carregada com alguns textos chave (ex: Lei Complementar 123/2006 \- Simples Nacional, alguns capítulos do RICMS do estado principal). O RAG consegue usar essa base para responder perguntas diretas sobre esses temas. Processo de atualização manual documentado.  
  * **\[Tarefa Técnica\] Definir e adquirir conteúdo inicial da base legal** (ex: LC 123/2006, seções principais do RICMS-SP).  
    * AC: Arquivos de texto/PDF com o conteúdo selecionado preparados.  
  * **\[Tarefa Técnica\] Estruturar e carregar a base inicial para RAG** (chunking simples, metadados básicos como "LC 123" ou "RICMS-SP").  
    * AC: Conteúdo segmentado (ex: por artigo); Carregado no Supabase/pgvector com metadados mínimos.  
  * **\[Tarefa Técnica\] Documentar processo manual para futuras atualizações.**  
    * AC: Guia simples descrevendo como carregar novos documentos na base vetorial.  
  * **\[Tarefa Técnica\] Ajustar prompts do rag\_agent para consultas de legislação.**  
    * AC: Prompt incentiva o uso da base carregada; Testes com perguntas sobre Simples Nacional mostram que o contexto relevante é recuperado e utilizado.

### **2\. Geração de Relatórios (MVP)**

* **\[Épico\] Módulo de Geração de Relatório Fiscal Básico:**  
  * **AC:** A API oferece um endpoint funcional para gerar um relatório pré-definido essencial (ex: Listagem de NF-e Recebidas/Emitidas no período com totais), retornando dados formatados.  
  * **\[Tarefa\] Definir formato e parâmetros do relatório inicial** (ex: Listagem de NF-e por período \- colunas: Chave Acesso, Emitente, Data Emissão, Valor Total).  
    * AC: Especificação clara do layout e filtros (data início/fim).  
  * **\[Tarefa Técnica\] Criar serviço backend para gerar o relatório** (consultando a tabela nfe\_header).  
    * AC: Lógica SQL/ORM implementada para buscar dados filtrados por período; Retorna JSON com a lista de NF-e.  
  * **\[Tarefa Técnica\] Criar endpoint na API para o relatório.**  
    * AC: Endpoint /relatorios/listagem\_nfe funcional; Recebe data\_inicio/data\_fim; Retorna dados; Documentação Swagger OK.

### **5\. Melhorias Gerais Backend (Foco MVP)**

* **\[Tarefa Técnica\] Refatorar agentes para integração mínima da lógica fiscal.**  
  * AC: orchestrator\_agent consegue direcionar perguntas sobre "listar notas de Maio" para a consulta estruturada (novo endpoint de relatório); rag\_agent usa base de legislação.  
* **\[Tarefa Técnica\] Revisar prompts principais (orquestrador, RAG) para contexto fiscal.**  
  * AC: Prompts ajustados com exemplos fiscais básicos; Respostas mais alinhadas ao domínio.  
* **\[Tarefa Técnica\] Criar testes unitários essenciais para parsing de NF-e e geração do relatório básico.**  
  * AC: Testes cobrem parser com XML válido/inválido e o endpoint do relatório com dados mockados.

## **Frontend (agentnfe-frontend)**

### **1\. Visualização de Dados e Relatórios (MVP)**

* **\[Épico\] Seção Básica de Relatórios:**  
  * **AC:** Usuário acessa uma nova seção e visualiza o relatório de Listagem de NF-e, podendo filtrar por período.  
  * **\[Tarefa UI/UX\] Desenhar interface simples para o relatório de listagem.**  
    * AC: Mockup simples aprovado (seletores de data, tabela de resultados).  
  * **\[Tarefa Técnica\] Criar rota/página React para Relatórios.**  
    * AC: Rota /relatorios funcional; Componente base criado.  
  * **\[Tarefa Técnica\] Implementar componente de Tabela (shadcn/ui/table) para exibir o relatório.**  
    * AC: Tabela exibe colunas definidas; Inclui paginação básica se muitos resultados.  
  * **\[Tarefa Técnica\] Integrar com API do relatório de listagem.**  
    * AC: Seletores de data funcionam; Chamada API busca dados e preenche a tabela; Loading/erro tratados.

### **4\. Melhorias Gerais Frontend (Foco MVP)**

* **\[Épico\] UX Funcional para MVP:**  
  * **AC:** A interface permite upload de XML de NF-e e interação básica com o chat e o relatório de listagem de forma clara.  
  * **\[Tarefa UI/UX\] Ajustar fluxo de upload para aceitar XML explicitamente.**  
    * AC: Interface de upload (FileUploader.tsx) permite selecionar/arrastar arquivos .xml; Feedback visual claro.  
  * **\[Tarefa Técnica\] Adicionar filtro de período no Frontend para o relatório.**  
    * AC: Componentes de seleção de data (ex: Calendar do shadcn) adicionados à página de relatórios; Valores enviados à API.  
* **\[Tarefa Técnica\] Garantir responsividade básica das novas telas.**  
  * AC: Tela de relatório é usável em desktop; Não quebra visualmente em telas menores (pode ter scroll horizontal na tabela se necessário no MVP).

## **Refatoração e Limpeza (Prioridade Alta)**

### **1\. Isolamento da Funcionalidade de Fraude (Cartão de Crédito)**

* **\[Épico\] Isolar/Remover Módulo de Detecção de Fraude:** Objetivo: Remover código não relacionado ao core fiscal para simplificar a manutenção e o desenvolvimento do MVP.  
  * **AC:** Código, APIs, dados de exemplo e dados no DB relacionados à fraude são completamente removidos do projeto principal. Funcionalidades restantes (upload, chat básico) continuam operando.  
  * **\[Tarefa Técnica \- Análise\] Mapear código/dados de fraude.**  
    * AC: Lista completa de artefatos a serem removidos.  
  * **\[Tarefa Técnica \- Execução\] Remover código/arquivos no backend e frontend.** (Estratégia: Remoção completa).  
    * AC: Código removido; Projeto compila/inicia sem erros relacionados à fraude.  
  * **\[Tarefa Técnica\] Remover endpoints da API FastAPI de fraude.**  
    * AC: Rotas removidas; Swagger atualizado.  
  * **\[Tarefa Técnica\] Remover arquivos de dados/scripts de exemplo/teste.**  
    * AC: Arquivos deletados do repositório.  
  * **\[Tarefa Técnica \- Banco Vetorial\] Limpar dados de fraude do Supabase/pgvector.**  
    * AC: Script SQL (DELETE FROM embeddings WHERE metadata-\>\>'type' \= 'creditcard'; ou similar) executado; Verificação confirma remoção.  
  * **\[Tarefa Técnica\] Testar funcionalidade básica (upload genérico, chat) após remoção.**  
    * AC: Testes manuais confirmam que as operações básicas não foram quebradas.

## **Próximos Passos Sugeridos (Revisados para MVP)**

1. **Validação do Escopo do MVP:** Confirmar se os Épicos e Tarefas marcados como MVP são suficientes e realistas para a primeira entrega.  
2. **Priorização Fina:** Dentro do MVP, priorizar o Isolamento da Fraude e o fluxo essencial: Upload XML \-\> Parsing NF-e \-\> Armazenamento \-\> Relatório Básico \-\> Chat Básico com RAG sobre Legislação Mínima.  
3. **Estimativa e Planejamento:** Estimar o esforço para os itens do MVP e planejar as Sprints focadas nessas entregas.  
4. **Ferramenta de Gestão:** Utilizar a ferramenta escolhida para acompanhar o progresso do MVP.