import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Configuración de Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configuración de Trading
RISK_PER_TRADE = 0.01  # 1% de riesgo
ASSETS = ['XAUUSD (Oro)', 'EURUSD']

# Umbrales de desvío para generar señal
MIN_DEVIATION_PERCENT = 0.5  # Si el desvío es menor a 0.5%, no operamos