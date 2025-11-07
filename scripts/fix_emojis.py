import codecs

# Ler o arquivo
with codecs.open('src/agent/orchestrator_agent.py', 'r', 'utf-8') as f:
    lines = f.readlines()

# Substituições diretas
replacements = {
    '✅ ': '[OK] ',
    '⚠️ ': '[AVISO] ',
    '❌ ': '[ERRO] ',
    '🔥 ': '',
    '📊 ': '',
    '🎯 ': '',
    '📝 ': '',
    '🎨 ': '',
    '🔧 ': '',
    '🤖 ': '',
    '🚀 ': '',
    '📋 ': '',
}

# Processar cada linha
new_lines = []
count = 0
for line in lines:
    new_line = line
    for old, new in replacements.items():
        if old in new_line:
            new_line = new_line.replace(old, new)
            count += 1
    new_lines.append(new_line)

# Salvar
with codecs.open('src/agent/orchestrator_agent.py', 'w', 'utf-8') as f:
    f.writelines(new_lines)

print(f"Total de substituições: {count}")
