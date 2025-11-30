# detectors/cloudflare_detector.py
from typing import Union, Optional
from playwright.async_api import ElementHandle, Page, Frame
from config.settings import CF_INTERSTITIAL_INDICATORS_SELECTORS, CF_TURNSTILE_INDICATORS_SELECTORS

async def detect_cloudflare_challenge(
    queryable: Union[Page, Frame, ElementHandle],
    challenge_type: str = 'turnstile'
) -> bool:
    selectors = CF_TURNSTILE_INDICATORS_SELECTORS if challenge_type == 'turnstile' else CF_INTERSTITIAL_INDICATORS_SELECTORS
    for selector in selectors:
        element = await queryable.query_selector(selector)
        if not element:
            continue
        return True
    return False

async def detect_expected_content(queryable: Union[Page, Frame, ElementHandle], expected_content_selector: Optional[str] = None) -> bool:
    if not expected_content_selector:
        return False
    element = await queryable.query_selector(expected_content_selector)
    return bool(element)