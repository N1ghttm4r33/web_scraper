# 🔍 Web Scraper Avançado

Um web scraper de alta performance desenvolvido especificamente para o site ***, com bypass de proteções Cloudflare e DataDome.

## ⚠️ AVISO LEGAL IMPORTANTE

**Este projeto foi desenvolvido APENAS para fins educacionais e de pesquisa.** 

- Desenvolvido especificamente para o site cyberbackgroundchecks.com
- **NÃO me responsabilizo** pelo uso indevido deste software
- O uso deste código é de **total responsabilidade do usuário**
- Pode violar os Termos de Serviço do site alvo
- Use por sua conta e risco

## 🚀 Funcionalidades Principais

### 🛡️ Bypass de Proteções
- **Cloudflare Challenge**: Resolução automática de desafios interstitial e turnstile
- **DataDome CAPTCHA**: Sistema de resolução de captcha por áudio
- **Detecção Inteligente**: Identificação automática do tipo de proteção

### 🔄 Gerenciamento Avançado
- **Proxy Rotativo**: Instâncias isoladas do navegador por proxy
- **Sessões Isoladas**: Cada instância tem seu próprio IP e contexto
- **Balanceamento de Carga**: Distribuição inteligente de requisições

### 🎭 Simulação Humana
- **Movimentos Realistas**: Padrões de mouse humanos e aleatórios
- **Digitação Natural**: Variações de velocidade e pausas
- **Comportamento Orgânico**: Scrolls, clicks e tempo entre ações

### 🏗️ Arquitetura Profissional
- **Código Modular**: Estrutura organizada em módulos especializados
- **Configuração por Ambiente**: Variáveis sensíveis protegidas
- **Logs Detalhados**: Monitoramento completo da execução

## 📋 Pré-requisitos

### Sistema Operacional (Linux/Ubuntu recomendado)
```bash
# Dependências do sistema
sudo apt update
sudo apt install -y \
    libgtk-3-0 \
    libx11-xcb1 \
    libasound2 \
    libnss3 \
    libxss1 \
    libxrandr2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    ffmpeg \
    portaudio19-dev
```

## ⚡ Instalação Rápida

### 1. Clonar o Repositório
```bash
git clone https://github.com/N1ghttm4r33/web_scraper.git
cd web_scraper
```

### 2. Configurar Ambiente
```bash
# Copiar template de configuração
cp .env.example .env

# Editar com suas credenciais
nano .env
```

### 3. Configurar Variáveis de Ambiente
```env
# .env - CONFIGURAÇÕES OBRIGATÓRIAS
PROXY_USERNAME=seu_username_do_proxy
PROXY_PASSWORD=sua_senha_do_proxy
PROXY_SERVER=servidor_do_proxy

# CONFIGURAÇÕES OPCIONAIS
MAX_CONCURRENCY=5              # Número de instâncias paralelas
HEADLESS_MODE=True            # Execução em modo headless
TIMEOUT=40000                 # Timeout em milissegundos
SOLVE_ATTEMPTS=6              # Tentativas de resolver captchas
```

### 4. Instalar Dependências
```bash
# Instalar pacotes Python
pip install -r requirements.txt

# Instalar e configurar Playwright
playwright install chromium
playwright install-deps

# Instalar e configurar Camoufox
pip install -U camoufox[geoip]
python -m camoufox fetch
```

## 🎯 Como Usar

### Execução Básica
```bash
python main.py
```

### Execução com Parâmetros Personalizados
```bash
# Modo debug com mais logs
DEBUG=true python main.py

# Modo headless desativado para debugging
HEADLESS_MODE=false python main.py
```

## 🏗️ Estrutura do Projeto

```
web_scraper/
├── 📁 config/                 # Configurações e variáveis
│   ├── __init__.py
│   └── settings.py           # Configurações principais
├── 📁 core/                  # Núcleo do sistema
│   ├── __init__.py
│   ├── browser_manager.py    # Gerenciador de navegadores
│   ├── captcha_solver.py     # Resolvedor de captchas
│   └── shadow_dom.py         # Manipulação de Shadow DOM
├── 📁 detectors/             # Detectores de proteções
│   ├── __init__.py
│   ├── cloudflare_detector.py
│   └── datadome_detector.py
├── 📁 utils/                 # Utilitários
│   ├── __init__.py
│   ├── human_behavior.py     # Simulação humana
│   ├── audio_processor.py    # Processamento de áudio
│   └── element_locator.py    # Localização de elementos
├── 📁 search/                # Módulo de busca
│   ├── __init__.py
│   └── address_searcher.py   # Busca por endereços
├── 📁 results/               # Processamento de resultados
│   └── __init__.py
├── 🔧 main.py                # Script principal
├── 📄 requirements.txt       # Dependências
├── 📄 .env.example           # Template de configuração
└── 📄 README.md              # Este arquivo
```

## 🔧 Como Funciona

### 1. **Inicialização e Configuração**
Cada instância cria seu próprio ambiente isolado com proxy único, garantindo que cada sessão tenha IP diferente e seja completamente independente.

### 2. **Detecção de Desafios**
O sistema verifica automaticamente a presença de proteções:
- Cloudflare (interstitial/turnstile)
- DataDome CAPTCHA
- Prioriza a resolução baseada no tipo de desafio detectado

### 3. **Resolução de Cloudflare**
- Localiza elementos via Shadow DOM
- Aguarda checkbox ficar clicável
- Executa click com ruído humano incorporado
- Verifica automaticamente o sucesso do bypass

### 4. **Resolução de DataDome**
- Alterna automaticamente para desafio de áudio
- Baixa e processa o áudio do captcha
- Usa reconhecimento de voz para transcrição
- Preenche e submete a resposta automaticamente

### 5. **Execução da Busca**
- Preenche formulário com endereços fictícios
- Simula digitação humana com variações de velocidade
- Extrai dados estruturados via JSON-LD
- Processa e salva resultados automaticamente

## 🛠️ Customização

### Ajuste de Performance
```python
# Em config/settings.py
MAX_CONCURRENCY = 3           # Reduzir para menos instâncias
SOLVE_ATTEMPTS = 10           # Mais tentativas para captchas
ATTEMPT_DELAY = 30            # Mais tempo entre tentativas
```

### Configuração de Proxy
```python
# Suporta diversos formatos de proxy
PROXY_CONFIG = {
    "server": "http://proxy-server:port",
    "username": "user",
    "password": "pass"
}
```

## 🐛 Solução de Problemas

### Erros Comuns

**Problema:** `Timeout em desafio Cloudflare`
```bash
# Solução: Aumentar timeouts
TIMEOUT=60000 python main.py
```

**Problema:** `Falha no reconhecimento de áudio`
```bash
# Solução: Verificar dependências de áudio
sudo apt install ffmpeg portaudio19-dev
pip install --force-reinstall pyaudio
```

**Problema:** `Proxy não conecta`
```bash
# Solução: Verificar credenciais no .env
# Testar proxy externamente primeiro
```

### Logs e Debug
```bash
# Ativar modo verbose
DEBUG=true python main.py

# Ver logs em tempo real
tail -f scraper.log
```

## 📊 Resultados e Output

Os resultados são salvos em `resultados_proxies_rotativos.csv` com formato:
```csv
Endereço,Nome,Telefone
"123 Main St, New York","John Doe","555-0123"
```

## 🔒 Segurança e Privacidade

- Credenciais em variáveis de ambiente
- Nenhum dado sensível no código
- Conexões via proxy
- Sessões isoladas e descartáveis

## ⚖️ Isenção de Responsabilidade

### AVISO LEGAL EXPLÍCITO

1. **Uso Educacional**: Desenvolvido apenas para fins de pesquisa e aprendizado
2. **Site Específico**: Criado especificamente para cyberbackgroundchecks.com
3. **Sem Garantias**: Não há garantias de funcionamento ou suporte
4. **Responsabilidade do Usuário**: Você é totalmente responsável pelo uso
5. **Conformidade Legal**: Verifique leis locais antes de usar
6. **Termos de Serviço**: Pode violar ToS do site alvo

**EU NÃO ME RESPONSABILIZO POR:**
- Mau uso deste software
- Consequências legais do uso
- Danos a sistemas terceiros
- Violação de termos de serviço

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:
1. Reporte bugs via issues
2. Sugira melhorias
3. Mantenha o código bem documentado

---

**Desenvolvido com fins educacionais. Use com responsabilidade.**
