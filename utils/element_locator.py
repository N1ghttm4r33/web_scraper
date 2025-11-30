# utils/element_locator.py
import re
from typing import List
from playwright.async_api import Page, Locator

async def locate_element_robustly(page: Page, selectors: List[str], timeout: int = 10000) -> Locator:
    combined_selector = ", ".join(selectors)
    try:
        await page.wait_for_selector(combined_selector, state="attached", timeout=timeout)
        element = page.locator(combined_selector).first
        await element.wait_for(state="visible", timeout=5000)
        return element
    except Exception as e:
        raise Exception(f"Elemento não encontrado com seletores: {selectors}.")

async def setup_resource_blocking(page: Page):
    await page.route(re.compile(r"(\.png|\.jpg|\.jpeg|\.gif|\.svg|\.webp|\.mp4|\.woff2?|\.ttf|\.css)"), lambda route: route.abort())
    await page.route(re.compile(r"google-analytics\.com|doubleclick\.net|ads\.|\/ad\."), lambda route: route.abort())
    print("🚦 Bloqueio de recursos ativado.")