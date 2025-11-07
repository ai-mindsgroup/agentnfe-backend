import subprocess
import sys
import os
import socket

# Caminhos
venv_dir = os.path.join(os.getcwd(), '.venv')
activate_script = os.path.join(venv_dir, 'Scripts', 'Activate.ps1')
requirements = os.path.join(os.getcwd(), 'requirements.txt')
api_file = os.path.join(os.getcwd(), 'api_completa.py')

# Configuração de porta
DEFAULT_PORT = 8000

# 1. Cria ambiente virtual se não existir
def create_venv():
    if not os.path.exists(venv_dir):
        print('Criando ambiente virtual...')
        subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
    else:
        print('Ambiente virtual já existe.')

# 2. Instala requirements
def install_requirements():
    print('Instalando dependências...')
    subprocess.run([os.path.join(venv_dir, 'Scripts', 'python.exe'), '-m', 'pip', 'install', '-r', requirements, '--quiet'], check=True)

# 3. Verifica se porta está livre
def is_port_free(port):
    """Verifica se a porta está disponível."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def find_free_port(start_port=8000, max_attempts=10):
    """Encontra uma porta livre começando pela porta especificada."""
    for port in range(start_port, start_port + max_attempts):
        if is_port_free(port):
            return port
    raise RuntimeError(f"Nenhuma porta livre encontrada entre {start_port} e {start_port + max_attempts}")

# 4. Sobe FastAPI (uvicorn)
def run_fastapi():
    # Encontra porta livre
    port = find_free_port(DEFAULT_PORT)
    # Parametrização de embeddings por ambiente (evita mismatches com DB)
    os.environ.setdefault('VECTOR_DIMENSIONS', os.getenv('VECTOR_DIMENSIONS', '768'))
    os.environ.setdefault('TARGET_EMBEDDING_DIMENSION', os.getenv('TARGET_EMBEDDING_DIMENSION', '768'))
    # Modelo coerente com 768D por padrão; pode ser sobrescrito via EMBEDDING_MODEL
    os.environ.setdefault('EMBEDDING_MODEL', os.getenv('EMBEDDING_MODEL', 'all-mpnet-base-v2'))
    print(f'\n{"="*60}')
    print(f'🚀 Subindo FastAPI na porta {port}...')
    print(f'{"="*60}')
    print(f'📝 Documentação: http://localhost:{port}/docs')
    print(f'📊 Health Check: http://localhost:{port}/health')
    print(f'🔍 Endpoints NFe: http://localhost:{port}/nfe/')
    print(f'{"="*60}\n')
    
    subprocess.run([
        os.path.join(venv_dir, 'Scripts', 'python.exe'), 
        '-m', 'uvicorn', 
        'api_completa:app', 
        '--host', '0.0.0.0', 
        '--port', str(port),
        '--reload'  # Auto-reload em modo desenvolvimento
    ], check=True)

if __name__ == '__main__':
    create_venv()
    install_requirements()
    run_fastapi()
