"""Remove emojis APENAS de strings em logger calls, preservando todo resto."""
import re

def remove_emojis_from_logs():
    filepath = 'src/agent/orchestrator_agent.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar logger calls com emojis
    patterns = [
        (r'logger\.info\("([^"]*)"', 'info'),
        (r'logger\.warning\(f?"([^"]*)"', 'warning'),
        (r'logger\.error\("([^"]*)"', 'error'),
        (r'logger\.debug\("([^"]*)"', 'debug'),
        (r'print\(f?"([^"]*)"', 'print'),
    ]
    
    # Mapeamento de emojis
    emoji_map = {
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
    
    def replace_emojis_in_match(match):
        text = match.group(0)
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        return text
    
    # Aplicar substituições apenas em logger calls
    for pattern, log_type in patterns:
        content = re.sub(pattern, replace_emojis_in_match, content)
    
    # Salvar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Emojis removidos dos logs!")

if __name__ == "__main__":
    remove_emojis_from_logs()
