import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def __init__(self):
        self.url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        self.chat_id = TELEGRAM_CHAT_ID

    def send_signal(self, event_name: str, direction: str, deviation: float, actual: str, forecast: str):
        """Envía la alerta de trading formateada"""
        
        # Emojis según la dirección
        if direction == "LONG":
            emoji = "🟢"
            text_dir = "COMPRAR (LONG)"
        elif direction == "SHORT":
            emoji = ""
            text_dir = "VENDER (SHORT)"
        else:
            emoji = ""
            text_dir = "NEUTRAL"

        # Mensaje formateado en Markdown para Telegram
        message = f"""
🚨 *ALERTA DE TRADING* 🚨

📅 *Evento:* {event_name}
{emoji} *Acción:* {text_dir}
📊 *Desvío:* {deviation}%

📈 *Dato Real:* {actual}
 *Previsión:* {forecast}

 *Activos:* Oro y EURUSD
️ *Riesgo:* 1% del capital
⏱️ *Entrar en el cierre de la vela de 5m*
        """

        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(self.url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Mensaje enviado a Telegram: {event_name}")
            else:
                print(f"❌ Error de Telegram: {response.text}")
        except Exception as e:
            print(f"❌ Fallo de conexión: {e}")