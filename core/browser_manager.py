# core/browser_manager.py
import os
import random
import asyncio
from typing import List, Tuple
from playwright.async_api import Page
from camoufox.async_api import AsyncCamoufox
from playwright_captcha.utils.camoufox_add_init_script.add_init_script import get_addon_path

from utils.element_locator import setup_resource_blocking
from core.captcha_solver import solve_cloudflare_by_click
from search.address_searcher import search_and_fill
from config.settings import HEADLESS_MODE
from config.settings import URL

ADDON_PATH = get_addon_path()

async def search_loop_task_single_proxy(proxy_config: dict, addresses: List[Tuple[str, str]], results_queue: asyncio.Queue):
    """
    Cria uma instância COMPLETAMENTE SEPARADA do browser com seu próprio proxy
    e processa uma lista de endereços de forma isolada.
    """
    proxy_server = proxy_config["server"].split('//')[-1].split('@')[-1]
    print(f"🚀 Iniciando Browser com Proxy: {proxy_server}")
    
    try:
        async with AsyncCamoufox(
            headless=HEADLESS_MODE,
            humanize=True,
            proxy=proxy_config,
            window=(1280, 720),
            disable_coop=True,
            geoip=True,
            block_images=True,
            block_webrtc=True,
            block_webgl=False,
            enable_cache=True,
            main_world_eval=True,
            i_know_what_im_doing=True,
            addons=[os.path.abspath(ADDON_PATH)],
            config={'forceScopeAccess': True},
        ) as browser:
            
            context = await browser.new_context()
            page = await context.new_page()
            
            initial_url = URL
            print(f"[Proxy {proxy_server}] 🚀 Iniciando sessão...")
            
            await setup_resource_blocking(page)
            await page.goto(initial_url, wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(random.uniform(2.0, 5.0))
            
            success = await solve_cloudflare_by_click(page)
            if not success:
                print(f"❌ Falha no bypass inicial no proxy {proxy_server}")
                await page.close()
                await context.close()
                return
            
            await page.wait_for_selector('input[name="SearchCriteriaViewModel.AddressLine1"]', timeout=15000)
            print(f"✅ Bypass concluído no proxy {proxy_server}")
            
            for addr1, addr2 in addresses:
                result = await search_and_fill(page, addr1, addr2)
                await results_queue.put(result)
                await asyncio.sleep(random.uniform(1.0, 3.0))
            
            await page.close()
            await context.close()
            print(f"✅ Sessão finalizada no proxy {proxy_server}")
            
    except Exception as e:
        print(f"💥 ERRO no proxy {proxy_server}: {e}")