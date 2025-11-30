"""
Módulo de busca e extração de dados
"""
from .address_searcher import (
    search_and_fill,
    generate_addresses
)

__all__ = [
    'search_and_fill',
    'generate_addresses'
]