"""Script para remover todos os emojis do orchestrator_agent.py"""
import re
from pathlib import Path

def remove_emojis(text: str) -> str:
    """Remove todos os emojis de um texto."""
    # Padrão para detectar emojis Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "]+",
        flags=re.UNICODE
    )
    
    # Remove emojis
    text = emoji_pattern.sub('', text)
    
    # Remove espaços duplicados que podem ter sido deixados
    text = re.sub(r'  +', ' ', text)
    
    return text

def main():
    # Caminho do arquivo
    file_path = Path(__file__).parent.parent / "src" / "agent" / "orchestrator_agent.py"
    
    print(f"Lendo arquivo: {file_path}")
    
    # Ler conteúdo
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Contar emojis no original
    emoji_count_before = len(re.findall(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
        r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251'
        r'\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF]',
        original_content
    ))
    
    print(f"Emojis encontrados: {emoji_count_before}")
    
    # Remover emojis
    cleaned_content = remove_emojis(original_content)
    
    # Contar emojis após limpeza
    emoji_count_after = len(re.findall(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
        r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251'
        r'\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF]',
        cleaned_content
    ))
    
    print(f"Emojis após limpeza: {emoji_count_after}")
    
    if emoji_count_before > 0:
        # Salvar arquivo limpo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"\nArquivo atualizado com sucesso!")
        print(f"Removidos {emoji_count_before} emojis")
    else:
        print("\nNenhum emoji encontrado para remover.")
    
    return emoji_count_before, emoji_count_after

if __name__ == "__main__":
    main()
