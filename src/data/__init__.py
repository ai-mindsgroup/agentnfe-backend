"""Pacote de dados: carregamento, validação e gerenciamento de arquivos.

Evite imports pesados aqui para não quebrar quando apenas ``src.data`` for importado.
Exponha apenas objetos existentes e estáveis.
"""

from .data_processor import DataProcessor  # noqa: F401
from .data_loader import DataLoader  # noqa: F401
from .data_validator import DataValidator  # noqa: F401
from .csv_file_manager import CSVFileManager  # noqa: F401

__all__ = [
	"DataProcessor",
	"DataLoader",
	"DataValidator",
	"CSVFileManager",
]
