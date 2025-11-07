import subprocess
import sys
import os
from pathlib import Path
import platform

# Detecta caminhos com base na localização deste script (robusto mesmo fora do repo root)
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]
SRC_DIR = REPO_ROOT / "src"
VENV_DIR = REPO_ROOT / ".venv"
REQUIREMENTS_TXT = REPO_ROOT / "requirements.txt"
REQUIREMENTS_DEV = REPO_ROOT / "requirements-dev.txt"


def get_venv_python() -> Path:
    """Retorna o executável do Python dentro da venv, compatível com Windows/Linux/macOS."""
    if platform.system().lower().startswith("win"):
        candidate = VENV_DIR / "Scripts" / "python.exe"
        if candidate.exists():
            return candidate
        # fallback raro
        candidate = VENV_DIR / "Scripts" / "python"
        if candidate.exists():
            return candidate
    else:
        # Unix-like
        for name in ("python3", "python"):
            candidate = VENV_DIR / "bin" / name
            if candidate.exists():
                return candidate
    # Último recurso: usar o próprio Python do sistema (não recomendado)
    return Path(sys.executable)


def find_interface_entrypoint() -> Path:
    """Determina o melhor arquivo de interface interativa disponível.

    Ordem de preferência:
      1) scripts/development/interface_interativa.py (dev mais recente)
      2) examples/interface_interativa.py (exemplo funcional)
      3) interface_interativa.py na raiz (fallback legado)
    """
    candidates = [
        REPO_ROOT / "scripts" / "development" / "interface_interativa.py",
        REPO_ROOT / "examples" / "interface_interativa.py",
        REPO_ROOT / "interface_interativa.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "Nenhum arquivo de interface_interativa.py encontrado em scripts/development/, examples/ ou raiz do projeto."
    )


# 1) Cria ambiente virtual se não existir
def create_venv() -> None:
    if not VENV_DIR.exists():
        print("Criando ambiente virtual em .venv ...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    else:
        print("Ambiente virtual já existe.")


# 2) Instala requirements
def resolve_requirements_file() -> Path:
    """Determina o arquivo de requisitos a ser instalado.

    Prioridade:
      1) CLI flag --req <path>
      2) ENV REQUIREMENTS_FILE
      3) requirements.txt
      4) requirements-dev.txt
    """
    # 1) CLI flag
    if "--req" in sys.argv:
        try:
            idx = sys.argv.index("--req")
            cand = Path(sys.argv[idx + 1]).resolve()
            if cand.exists():
                return cand
            else:
                print(f"Aviso: arquivo passado em --req não existe: {cand}")
        except Exception:
            print("Aviso: uso de --req inválido. Ignorando.")

    # 2) ENV var
    env_req = os.environ.get("REQUIREMENTS_FILE")
    if env_req:
        cand = Path(env_req).resolve()
        if cand.exists():
            return cand
        else:
            print(f"Aviso: REQUIREMENTS_FILE aponta para arquivo inexistente: {cand}")

    # 3) Defaults
    if REQUIREMENTS_TXT.exists():
        return REQUIREMENTS_TXT
    elif REQUIREMENTS_DEV.exists():
        print("Aviso: requirements.txt não encontrado. Usando requirements-dev.txt.")
        return REQUIREMENTS_DEV
    else:
        raise FileNotFoundError("Nenhum arquivo de requisitos encontrado (requirements.txt, requirements-dev.txt, ou o fornecido por --req/REQUIREMENTS_FILE).")


def install_requirements() -> None:
    if os.environ.get("SKIP_INSTALL") == "1":
        print("Pulando instalação de dependências (SKIP_INSTALL=1).")
        return

    req_file = resolve_requirements_file()

    print(f"Instalando dependências de {req_file.name} ...")
    # Removido '--quiet' para dar visibilidade de progresso e evitar sensação de travamento
    venv_python = str(get_venv_python())
    subprocess.run([venv_python, "-m", "pip", "install", "-r", str(req_file)], check=True)


# 3) Executa interface_interativa.py selecionada
def run_interface() -> None:
    entrypoint = find_interface_entrypoint()
    print(f"Executando {entrypoint.relative_to(REPO_ROOT)} ...")

    # Garantir que imports funcionem tanto para 'src.*' quanto para módulos dentro de src/
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    composed_pp = os.pathsep.join([p for p in [str(REPO_ROOT), str(SRC_DIR), existing_pp] if p])
    env["PYTHONPATH"] = composed_pp

    venv_python = str(get_venv_python())
    subprocess.run([venv_python, str(entrypoint)], check=True, env=env)


if __name__ == "__main__":
    try:
        create_venv()
        install_requirements()
        run_interface()
    except subprocess.CalledProcessError as cpe:
        print(f"❌ Erro ao executar comando: {cpe}")
        raise
    except Exception as exc:
        print(f"❌ Falha ao configurar/rodar interface: {exc}")
        raise
