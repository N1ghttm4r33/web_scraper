# search/address_searcher.py
import json
import random
from typing import List, Tuple, Optional
from faker import Faker
from playwright.async_api import Page
from utils.element_locator import locate_element_robustly
from utils.human_behavior import human_type_cf
import asyncio

fake = Faker('en_US')

def generate_addresses(num=20):
    """Gera endereços fictícios para busca"""
    return [(fake.street_address(), f"{fake.city()}") for _ in range(num)]

async def search_and_fill(page: Page, address_line1: str, address_line2: str) -> Tuple[str, Optional[str], Optional[str]]:
    """Executa busca por endereço e extrai dados"""
    full_address = f"{address_line1}, {address_line2}"
    ADDRESS_1_SELECTORS = [
        'input[name="SearchCriteriaViewModel.AddressLine1"]', 
        '#SearchByAddress_AddressLine1', 
        'input[id="#SearchByAddress_AddressLine1"]',
        'input[placeholder="Street Address, Apt/Unit"]'
    ]
    ADDRESS_2_SELECTORS = [
        'input[name="SearchCriteriaViewModel.AddressLine2"]', 
        '#SearchByAddress_AddressLine2', 
        'input[id="#SearchByAddress_AddressLine2"]',
    ]
    search_button_selector = '#button-search-by-address'
    
    try:
        print(f"📝 Preenchendo formulário para: {full_address}")
        input1_locator = await locate_element_robustly(page, ADDRESS_1_SELECTORS)
        input2_locator = await locate_element_robustly(page, ADDRESS_2_SELECTORS)
        
        await human_type_cf(page, input1_locator, address_line1)
        await asyncio.sleep(random.uniform(0.2, 0.5))
        await human_type_cf(page, input2_locator, address_line2)
        
        await page.locator(search_button_selector).click()
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        json_elements = await page.locator('script[type="application/ld+json"]').all()
        names, phones = [], []
        
        for elem in json_elements:
            try:
                json_text = await elem.inner_text()
                data = json.loads(json_text)
                if not isinstance(data, list): 
                    data = [data]
                for item in data:
                    if item.get("@type") == "Person":
                        if name := item.get("name"): 
                            names.append(name)
                        if tel := item.get("telephone"):
                            if isinstance(tel, list): 
                                phones.extend(tel)
                            else: 
                                phones.append(tel)
            except: 
                continue
        
        if not names:
            print("❌ Nenhum dado JSON encontrado.")
            return full_address, None, None
        
        name_result = names[0]
        phone_clean = ", ".join(set(phones)) if phones else "N/A"
        print(f"✅ SUCESSO: {name_result} | {phone_clean}")
        return full_address, name_result, phone_clean
            
    except Exception as e:
        print(f"❌ Falha na busca de {full_address}: {e}")
        return full_address, None, None