"""
Módulo core - Funcionalidades centrais do scraper
"""
from .browser_manager import search_loop_task_single_proxy
from .captcha_solver import (
    solve_cloudflare_by_click,
    solve_datadome_audio,
    get_ready_checkbox,
    wait_for_verifying_hidden
)
from .shadow_dom import (
    get_shadow_roots,
    search_shadow_root_elements,
    search_shadow_root_iframes
)

__all__ = [
    'search_loop_task_single_proxy',
    'solve_cloudflare_by_click',
    'solve_datadome_audio', 
    'get_ready_checkbox',
    'wait_for_verifying_hidden',
    'get_shadow_roots',
    'search_shadow_root_elements',
    'search_shadow_root_iframes'
]