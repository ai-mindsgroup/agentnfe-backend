"""Remove todos os emojis do arquivo linha por linha."""

def remove_all_emojis_safe():
    filepath = 'src/agent/orchestrator_agent.py'
    
    # Ler todas as linhas
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Emojis para remover
    emoji_replacements = {
        '⚠️': '[AVISO]',
        '✅': '[OK]',
        '❌': '[ERRO]',
        '🔥': '',
        '📊': '',
        '💡': '',
        '🚀': '',
        '🎯': '',
        '📝': '',
        '🎨': '',
        '🔧': '',
        '🤖': '',
        '📋': '',
    }
    
    # Processar cada linha
    new_lines = []
    count = 0
    for line_num, line in enumerate(lines, 1):
        new_line = line
        for emoji, replacement in emoji_replacements.items():
            if emoji in line:
                new_line = new_line.replace(emoji, replacement)
                count += 1
                print(f"Linha {line_num}: {emoji} -> {replacement}")
        new_lines.append(new_line)
    
    # Salvar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\nTotal de emojis removidos: {count}")

if __name__ == "__main__":
    remove_all_emojis_safe()
