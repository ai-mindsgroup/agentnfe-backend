"""
Script simplificado para iniciar a API FastAPI do AgentNFe.

Este script é o entrypoint principal para desenvolvimento.
"""

import subprocess
import sys
import os

def main():
    """Inicia o servidor FastAPI."""
    
    # Configuração
    PORT = 8000
    HOST = "0.0.0.0"
    
    print(f'\n{"="*60}')
    print(f'🚀 AgentNFe - API REST Multiagente')
    print(f'{"="*60}')
    print(f'📝 Documentação Swagger: http://localhost:{PORT}/docs')
    print(f'📚 Documentação Redoc:   http://localhost:{PORT}/redoc')
    print(f'💚 Health Check:         http://localhost:{PORT}/health')
    print(f'🔍 Endpoints NFe:        http://localhost:{PORT}/nfe/')
    print(f'{"="*60}')
    print(f'\n⚡ Servidor rodando em modo DESENVOLVIMENTO')
    print(f'   Auto-reload: ATIVO')
    print(f'   Porta: {PORT}')
    print(f'\n⏸️  Pressione CTRL+C para parar\n')
    
    try:
        # Inicia uvicorn
        subprocess.run([
            sys.executable,
            '-m', 'uvicorn',
            'api_completa:app',
            '--host', HOST,
            '--port', str(PORT),
            '--reload',
            '--reload-exclude', '*.log',
            '--reload-exclude', '*.pyc',
            '--reload-exclude', '__pycache__',
        ])
    except KeyboardInterrupt:
        print(f'\n\n{"="*60}')
        print('✅ Servidor parado com sucesso')
        print(f'{"="*60}\n')
    except Exception as e:
        print(f'\n❌ Erro ao iniciar servidor: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
