"""
Módulo de APIs e clientes externos.

Contém clientes para APIs de terceiros e serviços externos.
"""

from src.api.sonar_client import send_sonar_query

__all__ = ["send_sonar_query"]
