# core/shadow_dom.py
import logging
from typing import Union, List, Optional
from playwright.async_api import ElementHandle, Page, Frame

logger = logging.getLogger("camoufox")

async def get_shadow_roots(queryable: Union[Page, Frame, ElementHandle]) -> List[ElementHandle]:
    js = """
    () => {
        const roots = [];
        function collectShadowRoots(node) {
            if (!node) return;
            if (node.shadowRootUnl) {
                roots.push(node.shadowRootUnl);
                node = node.shadowRootUnl;
            }
            for (const el of node.querySelectorAll("*")) {
                if (el.shadowRootUnl) {
                    collectShadowRoots(el);
                }
            }
        }
        collectShadowRoots(document);
        return roots;
    }
    """
    handle = await queryable.evaluate_handle(js)
    properties = await handle.get_properties()
    shadow_roots = []
    for prop_handle in properties.values():
        element = prop_handle.as_element()
        if element:
            shadow_roots.append(element)
    return shadow_roots

async def search_shadow_root_elements(queryable: Union[Page, Frame, ElementHandle], selector: str) -> List[ElementHandle]:
    elements = []
    try:
        shadow_roots = await get_shadow_roots(queryable)
        for shadow_root in shadow_roots:
            element_handle = await shadow_root.evaluate_handle(f"shadow => shadow.querySelector('{selector}')")
            if not element_handle:
                continue
            element = element_handle.as_element()
            if element:
                elements.append(element)
    except Exception as e:
        logger.error(f'Error searching for elements: {e}')
    return elements

async def search_shadow_root_iframes(queryable: Union[Page, Frame, ElementHandle], src_filter: str) -> Optional[List[Frame]]:
    matched_iframes = []
    try:
        iframe_elements = await search_shadow_root_elements(queryable, 'iframe')
        for iframe_element in iframe_elements:
            src_prop = await iframe_element.get_property('src')
            src = await src_prop.json_value()
            if src_filter in src:
                cf_iframe = await iframe_element.content_frame()
                if cf_iframe and cf_iframe.is_detached():
                    continue
                matched_iframes.append(cf_iframe)
    except Exception as e:
        logger.error(f'Error searching for iframes: {e}')
    return matched_iframes