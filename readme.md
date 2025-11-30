# 🔍 Advanced Web Scraper

A high-performance web scraper with Cloudflare and DataDome bypass capabilities.

## 🚀 Features

- **Cloudflare Bypass**: Automatic challenge solving
- **DataDome Protection**: Audio captcha resolution  
- **Proxy Rotation**: Isolated browser instances per proxy
- **Human Simulation**: Realistic mouse movements and typing
- **Modular Architecture**: Clean, maintainable code structure

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/seu-usuario/scraper.git
cd scraper

# Copy environment template
cp .env.example .env

Configure Environment

Install Dependencies

pip install -r requirements.txt
playwright install chromium
pip install -U camoufox[geoip]
python -m camoufox fetch

sudo apt install -y libgtk-3-0 libx11-xcb1 libasound2

PROXY_USERNAME=your_proxy_username
PROXY_PASSWORD=your_proxy_password  
PROXY_SERVER=your_proxy_server
MAX_CONCURRENCY=5
HEADLESS_MODE=True

Run
bash

python main.py

Project Structure

scraper-project/
├── config/          # Configuration settings
├── core/            # Core functionality
├── detectors/       # Challenge detection
├── utils/           # Utilities & helpers
├── search/          # Search operations
└── results/         # Data handling

⚠️ Disclaimer

This project is for educational purposes only. Use responsibly and in compliance with target websites' Terms of Service.