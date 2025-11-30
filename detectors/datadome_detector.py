# detectors/datadome_detector.py
from typing import Union
from playwright.async_api import ElementHandle, Page, Frame

async def detect_datadome_challenge(queryable, check_content=True):
    # 1. Check iframes
    dd_iframes = await queryable.query_selector_all('iframe')
    for iframe in dd_iframes:
        src = await iframe.get_attribute('src') or ''
        title = await iframe.get_attribute('title') or ''
        if any(pattern in src for pattern in ["captcha-delivery.com", "geo.captcha-delivery.com"]):
            return True
        if "DataDome CAPTCHA" in title:
            return True

    # 2. Check scripts
    dd_scripts = await queryable.query_selector_all('script[src*="captcha-delivery.com"], script[src*="ct.captcha-delivery.com"]')
    if dd_scripts:
        return True

    # 3. Check page content
    if check_content:
        try:
            content = await queryable.content()
            datadome_indicators = [
                "captcha-delivery.com", "DataDome", "var dd=", "AHrlqAAAA",
            ]
            if any(indicator in content for indicator in datadome_indicators):
                return True
        except:
            pass
    return False