"""
Script para iniciar a API em modo PRODUÇÃO.

Sem auto-reload, otimizado para performance.
"""

import subprocess
import sys

def main():
    """Inicia o servidor FastAPI em modo produção."""
    
    # Configuração
    PORT = 8000
    HOST = "0.0.0.0"
    WORKERS = 4  # Número de workers (ajustar conforme CPU)
    
    print(f'\n{"="*60}')
    print(f'🚀 AgentNFe - API REST (PRODUÇÃO)')
    print(f'{"="*60}')
    print(f'⚡ Workers: {WORKERS}')
    print(f'🌐 Porta: {PORT}')
    print(f'📝 Documentação: http://localhost:{PORT}/docs')
    print(f'{"="*60}\n')
    
    try:
        # Inicia uvicorn com múltiplos workers
        subprocess.run([
            sys.executable,
            '-m', 'uvicorn',
            'api_completa:app',
            '--host', HOST,
            '--port', str(PORT),
            '--workers', str(WORKERS),
            '--log-level', 'info',
            '--no-access-log',  # Desabilita logs de acesso (usar nginx/proxy)
        ])
    except KeyboardInterrupt:
        print(f'\n\n{"="*60}')
        print('✅ Servidor parado')
        print(f'{"="*60}\n')
    except Exception as e:
        print(f'\n❌ Erro: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
