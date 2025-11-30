# core/captcha_solver.py
import random
import asyncio
import logging
from typing import Union, Optional, Literal, List, Tuple
import speech_recognition as sr
import os
import io
import requests
from pydub import AudioSegment
from playwright.async_api import Page, Frame, ElementHandle
from core.shadow_dom import search_shadow_root_iframes, search_shadow_root_elements
from detectors.cloudflare_detector import detect_cloudflare_challenge, detect_expected_content
from detectors.datadome_detector import detect_datadome_challenge
from utils.human_behavior import add_human_noise
from utils.audio_processor import process_audio_direct, process_audio_with_pydub

logger = logging.getLogger("camoufox")

async def get_ready_checkbox(
        iframes: List[Frame],
        delay: int,
        attempts: int
) -> Optional[Tuple[Frame, ElementHandle]]:
    """
    Accepts a list of Cloudflare iframes, sorts out detached ones, collects checkboxes from the remaining iframes,
    and waits until at least one checkbox is found and ready to be clicked (visible)

    :param iframes: Cloudflare iframes
    :param delay: Delay in seconds between attempts to find the checkbox
    :param attempts: Maximum number of attempts to find the checkbox
    :return: [checkboxes Frame, checkboxes ElementHandle] if checkbox is found and ready, None otherwise
    """

    # ensure at least one attempt
    if attempts <= 0:
        attempts = 1

    for attempt in range(attempts):
        try:
            checkboxes = []

            # search for checkboxes in each iframe
            for iframe in iframes:
                try:
                    if iframe.is_detached():  # skip detached iframes
                        continue

                    iframe_checkboxes = await search_shadow_root_elements(iframe, 'input[type="checkbox"]')

                    # add found checkboxes to the list with their parent iframe
                    checkboxes += [(iframe, iframe_checkbox) for iframe_checkbox in iframe_checkboxes]
                except Exception as e:
                    logger.error(f'Error searching for checkboxes in iframe: {e}')

            logger.info(f'Found {len(checkboxes)} checkboxes in {len(iframes)} Cloudflare iframes')

            # filter checkboxes that are visible and ready to be clicked
            visible_checkboxes = []
            for iframe, checkbox in checkboxes:
                if await checkbox.is_visible():
                    visible_checkboxes.append((iframe, checkbox))

            if visible_checkboxes:
                logger.info('Checkbox input is ready to be clicked')
                return visible_checkboxes[0]  # return the first visible checkbox

            logger.info('Waiting for Cloudflare checkbox input...')
            await asyncio.sleep(delay)
        except Exception as e:
            logger.error(f'Error while waiting for checkbox: {e}')

    logger.error('Max attempts reached while waiting for Cloudflare checkbox input')
    return None

async def wait_for_verifying_hidden(iframes: List[Frame], timeout: int = 20000) -> bool:
    """
    Espera até que a div #verifying (spinner) dentro do Iframe do Captcha
    fique invisível, sinalizando que a checkbox está pronta.

    :param iframes: Lista de objetos Frame (os iframes do Cloudflare).
    :param timeout: Tempo máximo de espera em milissegundos.
    :return: True se a div sumir/ficar oculta, False se timeout.
    """
    
    # Se a lista estiver vazia, não há iframe, então não há captcha visível.
    if not iframes:
        logger.info("Nenhum iframe de desafio encontrado.")
        return True 

    # 🛑 Executamos o script no PRIMEIRO frame encontrado.
    iframe = iframes[0] 
    
    # Script JavaScript que será executado DENTRO do iframe (no contexto dele)
    js = """
    (timeout, pollInterval) => {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            const VERIFYING_ID = '#verifying';
            
            function checkVerifying() {
                // Seleciona o elemento dentro do CONTEXTO ATUAL (o iframe)
                const verifyingDiv = document.querySelector(VERIFYING_ID);
                
                if (!verifyingDiv) {
                    // Se a div não existe no iframe, consideramos que está "hidden"
                    resolve(true);
                    return;
                }
                
                // Checa a visibilidade (CSS)
                const computedStyle = window.getComputedStyle(verifyingDiv);
                const visibility = computedStyle.getPropertyValue('visibility');
                const display = computedStyle.getPropertyValue('display');
                
                // Condição de sucesso: Visibilidade e Display devem estar hidden/none
                if (visibility === 'hidden' || display === 'none') {
                    resolve(true);
                } else if (Date.now() - startTime >= timeout) {
                    // Falha por timeout
                    reject(new Error(`Timeout: ${VERIFYING_ID} still visible/active.`));
                } else {
                    // Continua verificando no próximo intervalo
                    setTimeout(checkVerifying, pollInterval);
                }
            }
            
            // Inicia a verificação
            checkVerifying();
        });
    }
    """
    
    try:
        # 🛑 EXECUTA O SCRIPT DENTRO DO IFRAME ESPECÍFICO
        await iframe.evaluate(js, timeout)
        
        logger.info('#verifying div is now hidden - checkbox should be ready.')
        return True
        
    except Exception as e:
        logger.warning(f'Timeout or error waiting for #verifying to hide: {e}')
        return False
    
async def solve_datadome_audio(page: Page):
    """Solves a DataDome audio challenge on the current page."""
    
    try:
        print("🎯 Tentando resolver DataDome CAPTCHA por áudio...")
        
        # Step 1 - Localizar o iframe do DataDome
        datadome_iframe = None
        for frame in page.frames:
            if "captcha-delivery.com" in (frame.url or ""):
                datadome_iframe = frame
                break
        
        if not datadome_iframe:
            datadome_iframe = await page.query_selector('iframe[src*="captcha-delivery.com"]')
            if datadome_iframe:
                datadome_iframe = await datadome_iframe.content_frame()
        
        if not datadome_iframe:
            raise Exception("Iframe do DataDome não encontrado")
        
        print("✅ Iframe do DataDome encontrado")
        
        # Step 2 - Clicar no botão de áudio
        audio_selectors = [
            'button[title*="audio"]',
            'button[aria-label*="audio"]',
            'button#audio',
            'button.audio',
        ]
        
        audio_button = None
        for selector in audio_selectors:
            audio_button = await datadome_iframe.query_selector(selector)
            if audio_button:
                print(f"✅ Botão de áudio encontrado: {selector}")
                break
        
        if audio_button:
            await audio_button.click()
            print("✅ Clicou no botão de áudio")
            await asyncio.sleep(3)
        
        # Step 3 - Tentar diferentes métodos para obter o áudio
        audio_src = None
        
        # Método 1: Via elemento audio
        audio_elements = await datadome_iframe.query_selector_all('audio')
        for audio in audio_elements:
            src = await audio.get_attribute('src')
            if src and 'audio' in src:
                audio_src = src
                break
        
        # Método 2: Via requests da rede (mais confiável)
        if not audio_src:
            print("🔍 Procurando URL do áudio nos requests...")
            
            # Espera por requests de áudio
            audio_requests = []
            
            def capture_audio_requests(request):
                if 'audio' in request.url and any(ext in request.url for ext in ['.mp3', '.wav', '.ogg']):
                    audio_requests.append(request.url)
            
            page.on('request', capture_audio_requests)
            await asyncio.sleep(5)  # Aguarda possíveis requests
            page.remove_listener('request', capture_audio_requests)
            
            if audio_requests:
                audio_src = audio_requests[0]
                print(f"✅ URL do áudio capturada via request: {audio_src}")
        
        # Método 3: Via JavaScript - pega a URL diretamente do player
        if not audio_src:
            print("🔍 Procurando URL do áudio via JavaScript...")
            audio_src = await datadome_iframe.evaluate("""
                () => {
                    // Procura elemento audio
                    const audio = document.querySelector('audio');
                    if (audio && audio.src) return audio.src;
                    
                    // Procura em elementos de source
                    const source = document.querySelector('source[src*="audio"]');
                    if (source && source.src) return source.src;
                    
                    // Procura em eventos/atributos
                    const elements = document.querySelectorAll('[src*="audio"]');
                    for (let el of elements) {
                        if (el.src && (el.src.includes('.mp3') || el.src.includes('.wav'))) {
                            return el.src;
                        }
                    }
                    
                    return null;
                }
            """)
        
        if not audio_src:
            raise Exception("Source do áudio não encontrado")
        
        print(f"✅ URL do áudio: {audio_src[:80]}...")
        
        # Step 4 - Tentar diferentes métodos de processamento
        text = None
        
        # Método A: Tentar com requests diretamente
        try:
            text = await process_audio_direct(audio_src)
            if text:
                print(f"✅ Áudio transcrito (método direto): {text}")
        except Exception as e:
            print(f"❌ Método direto falhou: {e}")
        
        # Método B: Tentar com pydub (se disponível)
        if not text:
            try:
                text = await process_audio_with_pydub(audio_src)
                if text:
                    print(f"✅ Áudio transcrito (método pydub): {text}")
            except Exception as e:
                print(f"❌ Método pydub falhou: {e}")
        
        # Método C: Tentar com speech_recognition direto do URL
        if not text:
            try:
                text = await process_audio_speech_recognition(audio_src)
                if text:
                    print(f"✅ Áudio transcrito (método speech_recognition): {text}")
            except Exception as e:
                print(f"❌ Método speech_recognition falhou: {e}")
        
        if not text:
            # Método de emergência: Digitar código manual ou padrão
            print("⚠️ Todos os métodos automáticos falharam, usando fallback...")
            text = "123456"  # Fallback - você pode tentar escutar manualmente
        
        # Step 5 - Encontrar campo de input e enviar resposta
        input_selectors = [
            'input[type="text"]',
            'input[name*="response"]',
            'input#response',
        ]
        
        input_field = None
        for selector in input_selectors:
            input_field = await datadome_iframe.query_selector(selector)
            if input_field:
                break
        
        if input_field:
            await input_field.fill(text)
            print(f"✅ Resposta '{text}' inserida no campo")
        else:
            raise Exception("Campo de input não encontrado")
        
        # Step 6 - Submeter
        submit_selectors = [
            'button[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Verify")',
        ]
        
        submit_button = None
        for selector in submit_selectors:
            submit_button = await datadome_iframe.query_selector(selector)
            if submit_button:
                break
        
        if submit_button:
            await submit_button.click()
            print("✅ Submeteu a resposta")
        else:
            await input_field.press('Enter')
            print("✅ Pressionou Enter")
        
        # Step 7 - Aguardar e verificar
        await asyncio.sleep(3)
        
        datadome_still_there = await detect_datadome_challenge(page)
        if not datadome_still_there:
            print("🎉 DataDome CAPTCHA resolvido com sucesso!")
            return True
        else:
            print("❌ DataDome ainda presente")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao resolver DataDome: {e}")
        return False

async def process_audio_speech_recognition(audio_url: str) -> str:
    """Tenta usar speech_recognition diretamente do URL"""
    import requests
    
    # Baixa o áudio
    response = requests.get(audio_url, timeout=30)
    
    # Salva temporariamente
    temp_file = f"/tmp/datadome_audio_{random.randint(1000,9999)}.mp3"
    with open(temp_file, 'wb') as f:
        f.write(response.content)
    
    try:
        recognizer = sr.Recognizer()
        
        # Tenta abrir como MP3
        try:
            with sr.AudioFile(temp_file) as source:
                audio = recognizer.record(source)
            return recognizer.recognize_google(audio, language='en-US')
        except:
            pass
        
        # Se falhar, tenta forçar como WAV
        try:
            import subprocess
            wav_file = temp_file.replace('.mp3', '.wav')
            
            # Converte usando ffmpeg com parâmetros diferentes
            subprocess.run([
                'ffmpeg', '-y', '-i', temp_file, 
                '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000',
                wav_file
            ], check=True, capture_output=True)
            
            with sr.AudioFile(wav_file) as source:
                audio = recognizer.record(source)
            return recognizer.recognize_google(audio, language='en-US')
            
        except:
            pass
            
    finally:
        # Limpa arquivos temporários
        try:
            os.unlink(temp_file)
            if 'wav_file' in locals():
                os.unlink(wav_file)
        except:
            pass
    
    return None
    
async def verify_challenge_bypassed(queryable, expected_content_selector=None, timeout=10000):
    """
    Verifica se realmente passou pelos desafios
    """
    try:
        # 1. Verifica se o conteúdo esperado aparece
        if expected_content_selector:
            element = await queryable.wait_for_selector(expected_content_selector, timeout=timeout)
            if element:
                return True

        # 2. Verifica se os desafios sumiram
        cloudflare_gone = not await detect_cloudflare_challenge(queryable)
        datadome_gone = not await detect_datadome_challenge(queryable)

        # 3. Verifica se a URL mudou (sinal de sucesso)
        current_url = queryable.url
        if "challenges.cloudflare.com" not in current_url and "captcha-delivery.com" not in current_url:
            return True

        return cloudflare_gone and datadome_gone

    except Exception as e:
        logger.warning(f"Challenge verification failed: {e}")
        return False

async def solve_cloudflare_by_click(
        queryable: Union[Page, Frame, ElementHandle],
        challenge_type: Literal["interstitial", "turnstile"] = "interstitial",
        expected_content_selector: Optional[str] = None,
        solve_attempts: int = 6,
        solve_click_delay: int = 6,
        wait_checkbox_attempts: int = 10,
        wait_checkbox_delay: int = 10,
        checkbox_click_attempts: int = 6,
        attempt_delay: int = 20
) -> bool:

    logger.info(f'Starting Cloudflare {challenge_type} challenge solving by click...')

    for attempt in range(solve_attempts):
        if attempt > 0:
            await asyncio.sleep(attempt_delay/2)
            logger.warning(f'Retrying to solve ({attempt + 1}/{solve_attempts})...')

        # 1. Verifica primeiro se já passou
        expected_ok = await detect_expected_content(queryable, expected_content_selector)
        if expected_ok:
            logger.info("Expected content detected - challenge solved")
            return True

        # 2. Detecta qual desafio está presente
        cloudflare_detected = await detect_cloudflare_challenge(queryable, challenge_type)
        datadome_detected = await detect_datadome_challenge(queryable)

        # 3. Trata DataDome primeiro (mais prioritário)
        if datadome_detected:
            logger.warning("DataDome challenge detected - attempting audio solution")
            try:
                solved = await solve_datadome_audio(queryable)
                if solved:
                    logger.info("Audio captcha resolvido com sucesso")
                    return True
                else:
                    logger.error("Falha ao resolver audio captcha do DataDome")
                    continue
            except Exception as e:
                logger.error(f"Erro ao resolver DataDome: {e}")
                continue

        # 4. Trata Cloudflare
        elif cloudflare_detected:
            logger.info('Cloudflare challenge detected, proceeding to solve...')
            
            try:
                logger.info('Waiting for main div that contains iframe to be displayed as grid and be visible')
                DIV_SELECTOR = '#GjRM0'

                await queryable.wait_for_function(
                    f"document.querySelector('{DIV_SELECTOR}') && document.querySelector('{DIV_SELECTOR}').style.display === 'grid'",
                    timeout=60000
                )

                # Encontra iframes do Cloudflare
                cf_iframes = await search_shadow_root_iframes(
                    queryable, 'https://challenges.cloudflare.com/cdn-cgi/challenge-platform/'
                )
                if not cf_iframes:
                    logger.error(f'Cloudflare iframes not found')
                    continue

                # Aguarda verificações
                verifying_data = await wait_for_verifying_hidden(cf_iframes)
                if not verifying_data:
                    logger.error(f'Cloudflare #verifying did not become hidden in time')
                    continue

                # Busca checkbox
                checkbox_data = await get_ready_checkbox(
                    cf_iframes,
                    delay=wait_checkbox_delay,
                    attempts=wait_checkbox_attempts
                )
                if not checkbox_data:
                    logger.error(f'Cloudflare checkbox not found or not ready')
                    continue
                    
                iframe, checkbox = checkbox_data
                logger.info('Found checkbox in Cloudflare iframe')

                # Click no checkbox
                for checkbox_click_attempt in range(checkbox_click_attempts):
                    try:
                        await asyncio.sleep(random.uniform(0.5, 1.5))  # ✅ CORRIGIDO
                        await checkbox.click()
                        logger.info('Checkbox clicked successfully')
                        break
                    except Exception as e:
                        logger.error(f'Error clicking checkbox ({checkbox_click_attempt + 1}/{checkbox_click_attempts} attempt): {e}')
                else:
                    logger.error(f'Failed to click checkbox after maximum attempts')
                    continue

                # Aguarda processamento
                await asyncio.sleep(solve_click_delay)

                # Verifica sucesso
                expected_content_detected = await detect_expected_content(queryable, expected_content_selector)
                if expected_content_detected:
                    logger.info('Solved successfully - expected content found')
                    return True

                logger.warning('Failed to solve Cloudflare challenge in this attempt')

            except Exception as e:
                logger.error(f'Error during Cloudflare solving: {e}')
                continue

        else:
            # Nenhum desafio detectado
            logger.info('No protection challenges detected')
            return True

    logger.error('Max solving attempts reached, giving up')
    return False