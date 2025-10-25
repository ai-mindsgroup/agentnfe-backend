"""Cliente Supabase centralizado.

Uso:
    from src.vectorstore.supabase_client import supabase
"""
from __future__ import annotations
import os
from supabase import create_client, Client
from src.settings import SUPABASE_URL, SUPABASE_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL/SUPABASE_KEY não configurados. Veja configs/.env ou variáveis de ambiente.")

_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Exporte um singleton simples
supabase: Client = _supabase
