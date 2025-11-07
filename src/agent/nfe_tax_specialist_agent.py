"""Agente RAG Especialista em Tributos e Validação Fiscal de NF-e.

Este agente combina:
- Conhecimento especializado em legislação tributária brasileira
- Análise de CFOP, NCM, impostos e validações fiscais
- Busca vetorial em base de notas fiscais
- Detecção de inconsistências e anomalias tributárias
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd

from src.agent.base_agent import BaseAgent, AgentError
from src.agent.rag_agent import RAGAgent
from src.embeddings.generator import EmbeddingProvider
from src.vectorstore.supabase_client import supabase
from src.llm.langchain_manager import get_langchain_llm_manager


class NFeTaxSpecialistAgent(BaseAgent):
    """Agente especialista em análise tributária de Notas Fiscais Eletrônicas.
    
    Funcionalidades:
    - Validação de CFOP (Código Fiscal de Operações e Prestações)
    - Análise de NCM (Nomenclatura Comum do Mercosul)
    - Verificação de consistência tributária
    - Detecção de anomalias fiscais
    - Consultas inteligentes sobre legislação
    - Busca vetorial em histórico de notas
    """
    
    # CFOP válidos mais comuns (simplificado)
    CFOP_VALIDOS = {
        # Entradas
        '1': 'Entrada ou aquisição de serviços do estado',
        '2': 'Entrada ou aquisição de serviços de outros estados',
        '3': 'Entrada ou aquisição de serviços do exterior',
        # Saídas
        '5': 'Saída ou prestação de serviços para o estado',
        '6': 'Saída ou prestação de serviços para outros estados',
        '7': 'Saída ou prestação de serviços para o exterior',
    }
    
    # NCM: primeiros dígitos representam capítulos
    NCM_CAPITULOS = {
        '01-05': 'Animais vivos e produtos do reino animal',
        '06-14': 'Produtos do reino vegetal',
        '15': 'Gorduras e óleos',
        '16-24': 'Produtos alimentícios',
        '25-27': 'Produtos minerais',
        '28-38': 'Produtos das indústrias químicas',
        '39-40': 'Plásticos e borrachas',
        '41-43': 'Peles e couros',
        '44-46': 'Madeira e cortiça',
        '47-49': 'Papel e cartão',
        '50-63': 'Têxteis',
        '64-67': 'Calçados e chapéus',
        '68-70': 'Pedras, vidros e cerâmica',
        '71': 'Pérolas e metais preciosos',
        '72-83': 'Metais comuns',
        '84-85': 'Máquinas e equipamentos elétricos',
        '86-89': 'Veículos e material de transporte',
        '90-92': 'Instrumentos de precisão, música',
        '93': 'Armas e munições',
        '94-96': 'Móveis, brinquedos e diversos',
    }
    
    def __init__(self):
        """Inicializa o agente especialista em tributos."""
        super().__init__(
            name="nfe_tax_specialist",
            description="Especialista em análise tributária e fiscal de NF-e",
            enable_memory=True
        )
        
        # Inicializar agente RAG para busca vetorial
        self.rag_agent = RAGAgent(
            embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMER,
            chunk_size=512,
            chunk_overlap=50
        )
        
        self.logger.info("Agente NFe Tax Specialist inicializado com sucesso")
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Processa uma consulta tributária (método abstrato de BaseAgent).
        
        Args:
            query: Consulta do usuário
            context: Contexto adicional (chave_acesso, comando, etc)
        
        Returns:
            Resposta processada
        """
        context = context or {}
        
        # Detectar tipo de comando
        query_lower = query.lower()
        
        # Análise de nota específica
        if 'analisar' in query_lower or 'análise' in query_lower:
            if 'chave_acesso' in context:
                return self.analyze_nota_fiscal(context['chave_acesso'])
            else:
                return {
                    'success': False,
                    'error': 'Chave de acesso não fornecida para análise'
                }
        
        # Validação de CFOP
        elif 'cfop' in query_lower:
            if 'cfop' in context:
                return self.validate_cfop(context['cfop'])
            else:
                return {
                    'success': False,
                    'error': 'CFOP não fornecido'
                }
        
        # Validação de NCM
        elif 'ncm' in query_lower:
            if 'ncm' in context:
                return self.validate_ncm(context['ncm'])
            else:
                return {
                    'success': False,
                    'error': 'NCM não fornecido'
                }
        
        # Detecção de anomalias
        elif 'anomalia' in query_lower or 'inconsistência' in query_lower:
            return self.detect_anomalies(
                uf_emitente=context.get('uf'),
                data_inicio=context.get('data_inicio'),
                data_fim=context.get('data_fim'),
                limit=context.get('limit', 10)
            )
        
        # Consulta geral sobre tributos
        else:
            return self.query_tax_knowledge(query, context)
    
    def analyze_nota_fiscal(self, chave_acesso: str) -> Dict[str, Any]:
        """Analisa uma nota fiscal específica com foco tributário.
        
        Args:
            chave_acesso: Chave de acesso da nota fiscal (44 caracteres)
        
        Returns:
            Análise completa com validações tributárias
        """
        self.logger.info(f"Analisando nota fiscal: {chave_acesso}")
        
        try:
            # Buscar nota e itens
            nota = self._get_nota_fiscal(chave_acesso)
            if not nota:
                return {
                    'success': False,
                    'error': f'Nota fiscal {chave_acesso} não encontrada'
                }
            
            itens = self._get_nota_fiscal_itens(chave_acesso)
            
            # Análises especializadas
            analise = {
                'chave_acesso': chave_acesso,
                'numero': nota.get('numero'),
                'data_emissao': nota.get('data_emissao'),
                'emitente': {
                    'cnpj': nota.get('cpf_cnpj_emitente'),
                    'razao_social': nota.get('razao_social_emitente'),
                    'uf': nota.get('uf_emitente'),
                },
                'destinatario': {
                    'cnpj': nota.get('cnpj_destinatario'),
                    'nome': nota.get('nome_destinatario'),
                    'uf': nota.get('uf_destinatario'),
                },
                'valores': {
                    'valor_nota': float(nota.get('valor_nota_fiscal', 0)),
                    'soma_itens': sum(float(item.get('valor_total', 0)) for item in itens),
                    'divergencia': 0.0
                },
                'validacoes': {
                    'cfop': [],
                    'ncm': [],
                    'valores': [],
                    'consistencia': []
                },
                'alertas': [],
                'score_fiscal': 100.0
            }
            
            # Calcular divergência
            analise['valores']['divergencia'] = abs(
                analise['valores']['valor_nota'] - analise['valores']['soma_itens']
            )
            
            # Executar validações
            self._validar_cfop(itens, analise)
            self._validar_ncm(itens, analise)
            self._validar_valores(analise)
            self._validar_consistencia_operacao(nota, itens, analise)
            
            # Calcular score fiscal final
            analise['score_fiscal'] = self._calcular_score_fiscal(analise)
            
            # Gerar recomendações
            analise['recomendacoes'] = self._gerar_recomendacoes(analise)
            
            return {
                'success': True,
                'analise': analise
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar nota fiscal: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_cfop(self, cfop: str) -> Dict[str, Any]:
        """Valida e explica um código CFOP.
        
        Args:
            cfop: Código CFOP (4 dígitos)
        
        Returns:
            Informações sobre o CFOP
        """
        if not cfop or len(cfop) != 4:
            return {
                'valido': False,
                'erro': 'CFOP deve ter exatamente 4 dígitos'
            }
        
        primeiro_digito = cfop[0]
        grupo = self.CFOP_VALIDOS.get(primeiro_digito)
        
        # Determinar natureza da operação
        if primeiro_digito in ['1', '2', '3']:
            natureza = 'ENTRADA'
            tipo_operacao = 'Aquisição/Compra'
        elif primeiro_digito in ['5', '6', '7']:
            natureza = 'SAÍDA'
            tipo_operacao = 'Venda/Transferência'
        else:
            return {
                'valido': False,
                'erro': f'Primeiro dígito {primeiro_digito} inválido'
            }
        
        # Análise detalhada
        return {
            'valido': True,
            'cfop': cfop,
            'natureza': natureza,
            'tipo_operacao': tipo_operacao,
            'descricao_grupo': grupo,
            'destino': self._determinar_destino_cfop(primeiro_digito),
            'tributacao': self._analisar_tributacao_cfop(cfop)
        }
    
    def validate_ncm(self, ncm: str) -> Dict[str, Any]:
        """Valida e classifica um código NCM.
        
        Args:
            ncm: Código NCM (8 dígitos)
        
        Returns:
            Informações sobre o NCM
        """
        if not ncm:
            return {
                'valido': False,
                'erro': 'NCM não pode ser vazio'
            }
        
        # Remover pontos e espaços
        ncm_limpo = ncm.replace('.', '').replace(' ', '')
        
        if len(ncm_limpo) != 8:
            return {
                'valido': False,
                'erro': f'NCM deve ter 8 dígitos, fornecido: {len(ncm_limpo)}'
            }
        
        try:
            int(ncm_limpo)
        except ValueError:
            return {
                'valido': False,
                'erro': 'NCM deve conter apenas números'
            }
        
        # Extrair componentes
        capitulo = ncm_limpo[:2]
        posicao = ncm_limpo[:4]
        subposicao = ncm_limpo[:6]
        item = ncm_limpo
        
        # Determinar categoria
        categoria = self._determinar_categoria_ncm(capitulo)
        
        return {
            'valido': True,
            'ncm': ncm_limpo,
            'ncm_formatado': f'{ncm_limpo[:4]}.{ncm_limpo[4:6]}.{ncm_limpo[6:]}',
            'capitulo': capitulo,
            'posicao': posicao,
            'subposicao': subposicao,
            'item': item,
            'categoria': categoria
        }
    
    def query_tax_knowledge(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Consulta conhecimento especializado sobre tributos e legislação.
        
        Args:
            query: Pergunta sobre tributos, CFOP, NCM, etc.
            context: Contexto adicional (chave_acesso, cfop, ncm)
        
        Returns:
            Resposta especializada do LLM
        """
        self.logger.info(f"Consulta tributária: {query}")
        
        # Construir contexto enriquecido
        contexto_especializado = self._build_tax_context(context)
        
        # Prompt especializado
        system_prompt = """
Você é Carlos, Especialista em Tributação Fiscal e Notas Fiscais Eletrônicas (NF-e).

══════════════════════════════════════════════════════════════════
🎯 SUA FUNÇÃO ESPECÍFICA (NFE TAX SPECIALIST AGENT)
══════════════════════════════════════════════════════════════════

VOCÊ É ESPECIALIZADO EM:
- 📋 CFOP (Códigos Fiscais de Operações e Prestações): Validação, interpretação e recomendação
- 🏷️ NCM (Nomenclatura Comum do Mercosul): Classificação fiscal de produtos
- 💰 Tributos: ICMS, IPI, PIS, COFINS (cálculos, alíquotas, regimes)
- ⚖️ Legislação Tributária: Federal, estadual e municipal
- 🔍 Compliance Fiscal: Validações, inconsistências e anomalias
- 🚨 Detecção de Irregularidades: Padrões suspeitos, valores incompatíveis

CONHECIMENTO-BASE:
✅ CFOP: Entradas (1xxx, 2xxx, 3xxx) e Saídas (5xxx, 6xxx, 7xxx)
✅ NCM: 8 dígitos (Capítulo.Posição.Subposição.Item.Subitem)
✅ Alíquotas por UF: ICMS varia conforme origem/destino
✅ Substituição Tributária (ST): Responsabilidade solidária
✅ Regimes Especiais: Simples Nacional, Lucro Real, Presumido
✅ Obrigações Acessórias: SPED, EFD, NFC-e

VOCÊ PODE:
✅ Validar CFOP e NCM de notas fiscais
✅ Explicar significado de códigos fiscais
✅ Calcular tributos com base em operações
✅ Detectar inconsistências tributárias
✅ Recomendar ações de compliance

VOCÊ NÃO PODE:
❌ Fornecer consultoria jurídica (apenas orientações técnicas)
❌ Garantir compliance 100% sem auditoria profissional
❌ Substituir contador ou advogado tributarista

══════════════════════════════════════════════════════════════════
🛡️ GUARDRAILS OBRIGATÓRIOS
══════════════════════════════════════════════════════════════════

1. SEGURANÇA: Não exponha estrutura interna do banco de dados
2. PRIVACIDADE: Não revele dados confidenciais de empresas específicas
3. PRECISÃO: Cite legislação quando possível (ex: "Conforme art. X da Lei Y")
4. DISCLAIMER: Sempre lembre: "Consulte um contador para validação final"
5. CLAREZA: Respostas técnicas mas acessíveis

══════════════════════════════════════════════════════════════════
📋 FORMATO DE RESPOSTA
══════════════════════════════════════════════════════════════════

- 📏 BREVE: 2-4 parágrafos (máximo 250 palavras)
- 💬 HUMANIZADO: Tom profissional mas acessível
- 🎯 PRÁTICO: Orientações aplicáveis
- ⚠️ DISCLAIMERS: Sempre incluir quando necessário
- 🤝 FINALIZAR: "Para análise aprofundada, consulte seu contador"

Forneça respostas técnicas, precisas e práticas sobre legislação tributária brasileira!
"""
        
        user_query = f"Contexto: {contexto_especializado}\n\nPergunta: {query}"
        
        try:
            # Usa LangChain LLM Manager com fallback automático (Groq -> Gemini -> OpenAI)
            from src.llm.langchain_manager import LLMConfig
            
            llm_manager = get_langchain_llm_manager()
            config = LLMConfig(temperature=0.2, max_tokens=1000)
            
            # Invoca o LLM com system prompt especializado
            response = llm_manager.chat(
                prompt=user_query,
                system_prompt=system_prompt,
                config=config
            )
            
            if response.success:
                return {
                    'success': True,
                    'resposta': response.content,
                    'contexto': contexto_especializado,
                    'llm_provider': response.provider.value,
                    'model': response.model
                }
            else:
                return {
                    'success': False,
                    'error': response.error
                }
            
        except Exception as e:
            self.logger.error(f"Erro na consulta tributária: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def find_similar_notas(self, chave_acesso: str, limit: int = 5) -> Dict[str, Any]:
        """Encontra notas fiscais similares usando busca vetorial.
        
        Args:
            chave_acesso: Chave de acesso da nota de referência
            limit: Número de notas similares a retornar
        
        Returns:
            Lista de notas similares com scores de similaridade
        """
        self.logger.info(f"Buscando notas similares a: {chave_acesso}")
        
        try:
            # Buscar nota de referência
            nota = self._get_nota_fiscal(chave_acesso)
            if not nota:
                return {
                    'success': False,
                    'error': 'Nota fiscal não encontrada'
                }
            
            itens = self._get_nota_fiscal_itens(chave_acesso)
            
            # Criar descrição textual para embedding
            descricao = self._create_nota_description(nota, itens)
            
            # Buscar similares no vector store
            # (assumindo que as notas já foram indexadas)
            similar = self._search_similar_by_description(descricao, limit)
            
            return {
                'success': True,
                'nota_referencia': chave_acesso,
                'similares': similar
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar notas similares: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_anomalies(self, 
                        uf_emitente: Optional[str] = None,
                        data_inicio: Optional[str] = None,
                        data_fim: Optional[str] = None,
                        limit: int = 10) -> Dict[str, Any]:
        """Detecta anomalias tributárias em conjunto de notas.
        
        Args:
            uf_emitente: Filtrar por UF do emitente
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
            limit: Número máximo de anomalias a retornar
        
        Returns:
            Lista de notas com possíveis anomalias
        """
        self.logger.info("Detectando anomalias tributárias")
        
        try:
            anomalias = []
            
            # Buscar notas com divergência de valores
            notas_divergentes = self._find_value_divergences(uf_emitente, data_inicio, data_fim, limit)
            if notas_divergentes:
                anomalias.extend(notas_divergentes)
            
            # Buscar CFOPs inconsistentes
            cfop_inconsistentes = self._find_cfop_inconsistencies(uf_emitente, data_inicio, data_fim, limit)
            if cfop_inconsistentes:
                anomalias.extend(cfop_inconsistentes)
            
            # Buscar NCMs inválidos
            ncm_invalidos = self._find_invalid_ncms(uf_emitente, data_inicio, data_fim, limit)
            if ncm_invalidos:
                anomalias.extend(ncm_invalidos)
            
            return {
                'success': True,
                'total_anomalias': len(anomalias),
                'anomalias': anomalias[:limit]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar anomalias: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Métodos privados auxiliares
    
    def _get_nota_fiscal(self, chave_acesso: str) -> Optional[Dict]:
        """Busca nota fiscal no banco."""
        try:
            result = supabase.table('nota_fiscal')\
                .select('*')\
                .eq('chave_acesso', chave_acesso)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Erro ao buscar nota: {str(e)}")
            return None
    
    def _get_nota_fiscal_itens(self, chave_acesso: str) -> List[Dict]:
        """Busca itens da nota fiscal."""
        try:
            result = supabase.table('nota_fiscal_item')\
                .select('*')\
                .eq('chave_acesso', chave_acesso)\
                .execute()
            return result.data or []
        except Exception as e:
            self.logger.error(f"Erro ao buscar itens: {str(e)}")
            return []
    
    def _validar_cfop(self, itens: List[Dict], analise: Dict):
        """Valida CFOPs dos itens."""
        for item in itens:
            cfop = item.get('cfop', '')
            validacao = self.validate_cfop(cfop)
            
            if not validacao['valido']:
                analise['validacoes']['cfop'].append({
                    'item': item.get('numero_produto'),
                    'cfop': cfop,
                    'status': 'INVÁLIDO',
                    'erro': validacao.get('erro')
                })
                analise['alertas'].append(f"CFOP inválido no item {item.get('numero_produto')}: {cfop}")
            else:
                analise['validacoes']['cfop'].append({
                    'item': item.get('numero_produto'),
                    'cfop': cfop,
                    'status': 'VÁLIDO',
                    'natureza': validacao['natureza']
                })
    
    def _validar_ncm(self, itens: List[Dict], analise: Dict):
        """Valida NCMs dos itens."""
        for item in itens:
            ncm = item.get('codigo_ncm', '')
            validacao = self.validate_ncm(ncm)
            
            if not validacao['valido']:
                analise['validacoes']['ncm'].append({
                    'item': item.get('numero_produto'),
                    'ncm': ncm,
                    'status': 'INVÁLIDO',
                    'erro': validacao.get('erro')
                })
                analise['alertas'].append(f"NCM inválido no item {item.get('numero_produto')}: {ncm}")
            else:
                analise['validacoes']['ncm'].append({
                    'item': item.get('numero_produto'),
                    'ncm': validacao['ncm_formatado'],
                    'status': 'VÁLIDO',
                    'categoria': validacao['categoria']
                })
    
    def _validar_valores(self, analise: Dict):
        """Valida consistência de valores."""
        divergencia = analise['valores']['divergencia']
        valor_nota = analise['valores']['valor_nota']
        
        # Tolerância de 0.1% ou R$ 1,00
        tolerancia = max(valor_nota * 0.001, 1.0)
        
        if divergencia > tolerancia:
            analise['validacoes']['valores'].append({
                'status': 'DIVERGENTE',
                'divergencia': round(divergencia, 2),
                'percentual': round((divergencia / valor_nota) * 100, 2) if valor_nota > 0 else 0
            })
            analise['alertas'].append(
                f"Divergência de valores: R$ {divergencia:.2f} "
                f"({(divergencia/valor_nota)*100:.2f}%)"
            )
        else:
            analise['validacoes']['valores'].append({
                'status': 'CONSISTENTE',
                'divergencia': round(divergencia, 2)
            })
    
    def _validar_consistencia_operacao(self, nota: Dict, itens: List[Dict], analise: Dict):
        """Valida consistência da operação fiscal."""
        # Verificar consistência de UFs com CFOPs
        uf_emitente = nota.get('uf_emitente')
        uf_destinatario = nota.get('uf_destinatario')
        
        for item in itens:
            cfop = item.get('cfop', '')
            if len(cfop) == 4:
                primeiro_digito = cfop[0]
                
                # CFOP 5.xxx = operação dentro do estado
                if primeiro_digito == '5' and uf_emitente != uf_destinatario:
                    analise['validacoes']['consistencia'].append({
                        'item': item.get('numero_produto'),
                        'status': 'INCONSISTENTE',
                        'motivo': f'CFOP {cfop} indica operação interna mas UFs são diferentes'
                    })
                    analise['alertas'].append(
                        f"Inconsistência: CFOP {cfop} com UFs diferentes "
                        f"({uf_emitente} → {uf_destinatario})"
                    )
                
                # CFOP 6.xxx = operação interestadual
                elif primeiro_digito == '6' and uf_emitente == uf_destinatario:
                    analise['validacoes']['consistencia'].append({
                        'item': item.get('numero_produto'),
                        'status': 'INCONSISTENTE',
                        'motivo': f'CFOP {cfop} indica operação interestadual mas UFs são iguais'
                    })
                    analise['alertas'].append(
                        f"Inconsistência: CFOP {cfop} com mesma UF ({uf_emitente})"
                    )
    
    def _calcular_score_fiscal(self, analise: Dict) -> float:
        """Calcula score de conformidade fiscal (0-100)."""
        score = 100.0
        
        # Penalidades por problemas
        for validacao in analise['validacoes']['cfop']:
            if validacao['status'] == 'INVÁLIDO':
                score -= 10.0
        
        for validacao in analise['validacoes']['ncm']:
            if validacao['status'] == 'INVÁLIDO':
                score -= 10.0
        
        for validacao in analise['validacoes']['valores']:
            if validacao['status'] == 'DIVERGENTE':
                percentual = validacao.get('percentual', 0)
                score -= min(percentual, 20.0)  # Máximo 20 pontos
        
        for validacao in analise['validacoes']['consistencia']:
            if validacao['status'] == 'INCONSISTENTE':
                score -= 15.0
        
        return max(0.0, score)
    
    def _gerar_recomendacoes(self, analise: Dict) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recomendacoes = []
        
        if analise['score_fiscal'] < 70:
            recomendacoes.append("⚠️ Score fiscal baixo - revisar nota com urgência")
        
        if any(v['status'] == 'INVÁLIDO' for v in analise['validacoes']['cfop']):
            recomendacoes.append("Corrigir CFOPs inválidos antes de transmitir")
        
        if any(v['status'] == 'INVÁLIDO' for v in analise['validacoes']['ncm']):
            recomendacoes.append("Verificar códigos NCM com tabela oficial")
        
        if any(v['status'] == 'DIVERGENTE' for v in analise['validacoes']['valores']):
            recomendacoes.append("Revisar cálculos - soma dos itens não confere com total da nota")
        
        if any(v['status'] == 'INCONSISTENTE' for v in analise['validacoes']['consistencia']):
            recomendacoes.append("Verificar consistência entre CFOP e UFs da operação")
        
        if not recomendacoes:
            recomendacoes.append("✅ Nota fiscal em conformidade tributária")
        
        return recomendacoes
    
    def _determinar_destino_cfop(self, primeiro_digito: str) -> str:
        """Determina destino baseado no primeiro dígito do CFOP."""
        mapa = {
            '1': 'Dentro do estado',
            '2': 'Outros estados',
            '3': 'Exterior',
            '5': 'Dentro do estado',
            '6': 'Outros estados',
            '7': 'Exterior'
        }
        return mapa.get(primeiro_digito, 'Desconhecido')
    
    def _analisar_tributacao_cfop(self, cfop: str) -> Dict[str, Any]:
        """Analisa implicações tributárias do CFOP."""
        # Simplificado - em produção consultar tabela completa
        primeiro = cfop[0]
        
        if primeiro in ['5', '6']:
            return {
                'tipo': 'Saída',
                'gera_credito': False,
                'gera_debito': True,
                'icms': 'Incide normalmente'
            }
        else:
            return {
                'tipo': 'Entrada',
                'gera_credito': True,
                'gera_debito': False,
                'icms': 'Gera crédito'
            }
    
    def _determinar_categoria_ncm(self, capitulo: str) -> str:
        """Determina categoria do produto pelo capítulo NCM."""
        cap_num = int(capitulo)
        
        if 1 <= cap_num <= 5:
            return 'Animais vivos e produtos do reino animal'
        elif 6 <= cap_num <= 14:
            return 'Produtos do reino vegetal'
        elif cap_num == 15:
            return 'Gorduras e óleos'
        elif 16 <= cap_num <= 24:
            return 'Produtos alimentícios'
        elif 25 <= cap_num <= 27:
            return 'Produtos minerais'
        elif 28 <= cap_num <= 38:
            return 'Produtos das indústrias químicas'
        elif 39 <= cap_num <= 40:
            return 'Plásticos e borrachas'
        elif 84 <= cap_num <= 85:
            return 'Máquinas e equipamentos elétricos'
        else:
            return 'Outros produtos'
    
    def _build_tax_context(self, context: Optional[Dict]) -> str:
        """Constrói contexto especializado para consultas tributárias."""
        if not context:
            return "Contexto geral de tributação NF-e"
        
        partes = []
        
        if 'chave_acesso' in context:
            nota = self._get_nota_fiscal(context['chave_acesso'])
            if nota:
                partes.append(f"Nota fiscal {nota.get('numero')}")
                partes.append(f"Emitente: {nota.get('razao_social_emitente')} ({nota.get('uf_emitente')})")
                partes.append(f"Valor: R$ {nota.get('valor_nota_fiscal')}")
        
        if 'cfop' in context:
            cfop_info = self.validate_cfop(context['cfop'])
            if cfop_info['valido']:
                partes.append(f"CFOP {context['cfop']}: {cfop_info['descricao_grupo']}")
        
        if 'ncm' in context:
            ncm_info = self.validate_ncm(context['ncm'])
            if ncm_info['valido']:
                partes.append(f"NCM {ncm_info['ncm_formatado']}: {ncm_info['categoria']}")
        
        return ' | '.join(partes) if partes else "Contexto fiscal geral"
    
    def _create_nota_description(self, nota: Dict, itens: List[Dict]) -> str:
        """Cria descrição textual da nota para embedding."""
        descricao_partes = [
            f"Nota fiscal {nota.get('numero')}",
            f"Emitente: {nota.get('razao_social_emitente')}",
            f"UF: {nota.get('uf_emitente')}",
            f"Valor total: R$ {nota.get('valor_nota_fiscal')}",
            f"Operação: {nota.get('natureza_operacao')}",
        ]
        
        # Adicionar descrição dos produtos
        produtos = [item.get('descricao_produto', '') for item in itens[:5]]  # Primeiros 5
        if produtos:
            descricao_partes.append(f"Produtos: {', '.join(filter(None, produtos))}")
        
        return ' | '.join(descricao_partes)
    
    def _search_similar_by_description(self, descricao: str, limit: int) -> List[Dict]:
        """Busca notas similares por descrição textual."""
        # Placeholder - implementar busca vetorial real
        # TODO: Indexar notas como embeddings e usar vector_store.search()
        return []
    
    def _find_value_divergences(self, uf: Optional[str], data_inicio: Optional[str], 
                                data_fim: Optional[str], limit: int) -> List[Dict]:
        """Encontra notas com divergência de valores."""
        # Placeholder - implementar query SQL
        return []
    
    def _find_cfop_inconsistencies(self, uf: Optional[str], data_inicio: Optional[str], 
                                   data_fim: Optional[str], limit: int) -> List[Dict]:
        """Encontra inconsistências em CFOPs."""
        # Placeholder - implementar query SQL
        return []
    
    def _find_invalid_ncms(self, uf: Optional[str], data_inicio: Optional[str], 
                          data_fim: Optional[str], limit: int) -> List[Dict]:
        """Encontra NCMs inválidos."""
        # Placeholder - implementar query SQL
        return []
