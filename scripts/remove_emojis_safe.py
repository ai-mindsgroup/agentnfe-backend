"""
Script seguro para remover emojis preservando indentação
"""
import re
from pathlib import Path

def remove_emojis_safe(text: str) -> str:
    """Remove emojis preservando toda a estrutura do código"""
    # Pattern de emojis Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FAFF"  # Chess, Extended-A
        "]+", 
        flags=re.UNICODE
    )
    
    # Processar linha por linha para preservar indentação
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Capturar indentação inicial
        indentation = len(line) - len(line.lstrip())
        indent_chars = line[:indentation]
        
        # Remover emojis apenas do conteúdo (não da indentação)
        content = line[indentation:]
        cleaned_content = emoji_pattern.sub('', content)
        
        # Remover espaços duplos que podem ter ficado após remoção de emoji
        cleaned_content = re.sub(r'  +', ' ', cleaned_content)
        
        # Reconstruir linha com indentação original
        cleaned_line = indent_chars + cleaned_content
        cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines)

def main():
    file_path = Path("src/agent/orchestrator_agent.py")
    
    print(f"Lendo arquivo: {file_path.absolute()}")
    content = file_path.read_text(encoding='utf-8')
    
    # Contar emojis antes
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FAFF"
        "]+",
        flags=re.UNICODE
    )
    emojis_before = len(emoji_pattern.findall(content))
    
    # Limpar emojis
    cleaned_content = remove_emojis_safe(content)
    
    # Contar emojis depois
    emojis_after = len(emoji_pattern.findall(cleaned_content))
    
    print(f"Emojis encontrados: {emojis_before}")
    print(f"Emojis após limpeza: {emojis_after}")
    
    # Salvar arquivo
    file_path.write_text(cleaned_content, encoding='utf-8')
    print(f"Arquivo atualizado com sucesso! Removidos {emojis_before - emojis_after} emojis")

if __name__ == "__main__":
    main()
