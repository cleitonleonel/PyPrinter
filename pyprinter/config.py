from pathlib import Path

def get_project_root():
    """
    Retorna o diretório raiz do projeto.
    """
    return Path(__file__).resolve().parents[1]