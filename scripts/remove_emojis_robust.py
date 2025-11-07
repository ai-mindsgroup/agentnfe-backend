"""Remove emojis do orchestrator_agent.py de forma robusta."""

def remove_all_emojis():
    filepath = 'src/agent/orchestrator_agent.py'
    
    # Ler como bytes para evitar problemas de encoding
    with open(filepath, 'rb') as f:
        content = f.read().decode('utf-8')
    
    # Lista completa de emojis para remover com suas substituições
    emoji_replacements = {
        '\u26A0\uFE0F': '[AVISO]',  # ⚠️
        '\u2705': '[OK]',            # ✅
        '\u274C': '[ERRO]',          # ❌
        '\U0001F525': '',            # 🔥
        '\U0001F4CA': '',            # 📊
        '\U0001F4A1': '',            # �💡
        '\U0001F680': '',            # 🚀
        '\U0001F3AF': '',            # 🎯
        '\U0001F4DD': '',            # 📝
        '\U0001F3A8': '',            # 🎨
        '\U0001F527': '',            # 🔧
        '\U0001F916': '',            # 🤖
        '\U0001F4CB': '',            # 📋
    }
    
    # Aplicar substituições
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Escrever de volta
    with open(filepath, 'wb') as f:
        f.write(content.encode('utf-8'))
    
    print(f"Processado: {filepath}")
    print(f"Substituições: {len(emoji_replacements)}")

if __name__ == "__main__":
    remove_all_emojis()
