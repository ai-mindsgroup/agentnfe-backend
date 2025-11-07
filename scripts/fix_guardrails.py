"""
Script para corrigir e consolidar os guardrails no orchestrator_agent.py
Converte a seção de segurança em itens numerados 7-15 dos guardrails
"""

def fix_guardrails():
    file_path = r"c:\workstashion\nfe-aiminds-back\src\agent\orchestrator_agent.py"
    
    # Ler o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Texto antigo a ser substituído
    old_text = """   - NÃO responda perguntas sobre: receitas, saúde, programação genérica, entretenimento, etc.

🔐 SEGURANÇA - PROIBIÇÕES ABSOLUTAS:
- NUNCA execute, sugira ou mencione operações de UPDATE, DELETE, INSERT ou DROP no banco de dados
- NUNCA revele nomes de tabelas, colunas ou estrutura do banco de dados
- NUNCA forneça senhas, tokens, API keys ou credenciais
- NUNCA informe caminhos de arquivos, diretórios do sistema ou localização de código
- NUNCA revele informações técnicas: servidores, IPs, portas, hospedagem
- NUNCA mencione desenvolvedores, nomes de equipe ou informações internas
- NUNCA compartilhe dados confidenciais, pessoais ou sensíveis de terceiros
- NUNCA modifique, delete ou insira dados no dataset
- Sua função é APENAS LEITURA e ANÁLISE - você NÃO tem permissão para alterar dados

📋 COMPORTAMENTO:"""
    
    # Novo texto consolidado
    new_text = """   - NÃO responda perguntas sobre: receitas, saúde, programação genérica, entretenimento, etc.
7. NUNCA execute, sugira ou mencione operações de UPDATE, DELETE, INSERT ou DROP no banco de dados
8. NUNCA revele nomes de tabelas, colunas ou estrutura do banco de dados
9. NUNCA forneça senhas, tokens, API keys ou credenciais de qualquer tipo
10. NUNCA informe caminhos de arquivos, diretórios do sistema ou localização de código-fonte
11. NUNCA revele informações técnicas sobre infraestrutura: servidores, IPs, portas, hospedagem
12. NUNCA mencione nomes de desenvolvedores, equipe técnica ou informações internas da empresa
13. NUNCA compartilhe dados confidenciais, pessoais ou sensíveis de terceiros
14. NUNCA modifique, delete ou insira dados no dataset - sua função é APENAS LEITURA e ANÁLISE
15. Se usuário pedir modificações em dados ou banco: responda "Não tenho permissão para modificar dados. Posso apenas realizar análises e consultas."

📋 COMPORTAMENTO:"""
    
    # Verificar se encontrou o texto
    if old_text in content:
        print("✅ Texto encontrado! Realizando substituição...")
        content = content.replace(old_text, new_text)
        
        # Salvar o arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Arquivo atualizado com sucesso!")
        print("\n🎯 Guardrails consolidados em 15 itens numerados")
    else:
        print("❌ Texto antigo não encontrado")
        print("\n🔍 Buscando variações...")
        
        # Tentar sem o emoji problemático
        old_text_no_emoji = old_text.replace("🔐", "�").replace("📋", "�📋")
        if old_text_no_emoji in content:
            print("✅ Encontrado com emojis corrompidos! Corrigindo...")
            content = content.replace(old_text_no_emoji, new_text)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Arquivo atualizado e emojis corrigidos!")
        else:
            print("❌ Nenhuma variação encontrada")
            # Mostrar trecho do arquivo para debug
            idx = content.find("entretenimento, etc.")
            if idx > 0:
                print("\n📄 Trecho atual do arquivo:")
                print(content[idx:idx+500])

if __name__ == "__main__":
    fix_guardrails()
