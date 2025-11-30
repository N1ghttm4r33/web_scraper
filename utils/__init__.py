"""
Utilitários e helpers
"""
from .human_behavior import (
    add_human_noise,
    human_type_cf,
    perform_random_scroll
)
from .audio_processor import (
    download_file,
    process_audio_direct,
    process_audio_with_pydub
)
from .element_locator import (
    locate_element_robustly,
    setup_resource_blocking
)

__all__ = [
    'add_human_noise',
    'human_type_cf', 
    'perform_random_scroll',
    'download_file',
    'process_audio_direct',
    'process_audio_with_pydub',
    'locate_element_robustly',
    'setup_resource_blocking'
]