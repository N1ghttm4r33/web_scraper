# utils/human_behavior.py
import random
import asyncio
from playwright.async_api import Page

async def perform_random_scroll(page: Page):
    scroll_amount = random.randint(10, 50)
    direction = random.choice([-1, 1])
    await page.evaluate(f'window.scrollBy(0, {scroll_amount * direction})')

async def add_human_noise(page: Page, duration: float):
    viewport_size = page.viewport_size or {'width': 1280, 'height': 720}
    num_events = int(round(duration * random.uniform(1.0, 3.0)))
    if num_events <= 0:
        num_events = 1
    time_per_event = duration / num_events

    for _ in range(num_events):
        action_choice = random.choices(
            ['MOVE', 'SCROLL', 'IDLE'], 
            weights=[40, 25, 35], k=1
        )[0]
        
        if action_choice == 'MOVE':
            target_x = random.randint(50, viewport_size['width'] - 50)
            target_y = random.randint(50, viewport_size['height'] - 50)
            await page.mouse.move(target_x, target_y)
        elif action_choice == 'SCROLL':
            await perform_random_scroll(page)
        elif action_choice == 'IDLE':
            await asyncio.sleep(time_per_event)
            
        await asyncio.sleep(time_per_event)
    
    print(f"[{page.url[-8:]}] Ruído humano injetado por {duration:.1f}s.")

async def human_type_cf(page: Page, locator, text: str):
    await locator.click()
    await locator.clear()
    for char in text:
        await locator.press(char, delay=random.randint(10, 30))
        if random.random() < 0.03:
            await asyncio.sleep(random.uniform(0.1, 0.3))