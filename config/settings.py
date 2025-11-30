# config/settings.py
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configurações do Proxy
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD') 
PROXY_SERVER = os.getenv('PROXY_SERVER')

# Validação das variáveis de ambiente
if not all([PROXY_USERNAME, PROXY_PASSWORD, PROXY_SERVER]):
    raise ValueError("❌ Variáveis de ambiente do proxy não configuradas!")

DATAIMPULSE_PROXY = {
    "server": f"https://{PROXY_SERVER}", 
    "username": PROXY_USERNAME, 
    "password": PROXY_PASSWORD
}

# Outras configurações com fallback
MAX_CONCURRENCY = int(os.getenv('MAX_CONCURRENCY', '5'))
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
TIMEOUT = int(os.getenv('TIMEOUT', '40000'))
URL = os.getenv('URL', 'https://www.example.com/address')

# Cloudflare selectors 
CF_INTERSTITIAL_INDICATORS_SELECTORS = [
    'script[src*="/cdn-cgi/challenge-platform/"]',
]

CF_TURNSTILE_INDICATORS_SELECTORS = [
    'input[name="cf-turnstile-response"]',
    'script[src*="challenges.cloudflare.com/turnstile/v0"]',
]

# DataDome selectors
DD_CAPTCHA_INDICATORS_SELECTORS = [
    'iframe[src*="captcha-delivery.com"]',
    'iframe[title="DataDome CAPTCHA"]',
    'script[src*="captcha-delivery.com"]',
    'script[src*="ct.captcha-delivery.com"]',
]