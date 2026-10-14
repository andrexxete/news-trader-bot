import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def __init__(self):
        self.url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        self.chat_id = TELEGRAM_CHAT_ID

    def send_test_message(self):
        """Envía un mensaje de prueba para verificar que Telegram funciona"""
        message = f"""
 *BOT DE TRADING ACTIVO*

✅ El bot se ejecutó correctamente
📅 Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}
⏰ Hora de ejecución automática: Miércoles 07:35 AM

Si recibes este mensaje, Telegram funciona correctamente.
        """
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ Mensaje de prueba enviado a Telegram")
                return True
            else:
                print(f"❌ Error de Telegram: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Fallo de conexión: {e}")
            return False

    def send_signal(self, event_name: str, direction: str, deviation: float, actual: str, forecast: str):
        """Envía la alerta de trading formateada"""
        
        if direction == "LONG":
            emoji = "🟢"
            text_dir = "COMPRAR (LONG)"
        elif direction == "SHORT":
            emoji = ""
            text_dir = "VENDER (SHORT)"
        else:
            emoji = ""
            text_dir = "NEUTRAL"

        message = f"""
🚨 *ALERTA DE TRADING* 🚨

 *Evento:* {event_name}
{emoji} *Acción:* {text_dir}
 *Desvío:* {deviation}%

 *Dato Real:* {actual}
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
            response = requests.post(self.url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Mensaje enviado a Telegram: {event_name}")
                return True
            else:
                print(f"❌ Error de Telegram: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Fallo de conexión: {e}")
            return False

    def send_summary(self, total_eventos: int, senales: int):
        """Envía un resumen al final de la ejecución"""
        message = f"""
📊 *RESUMEN DE EJECUCIÓN*

✅ Bot completado exitosamente
📅 Eventos analizados: {total_eventos}
🎯 Señales generadas: {senales}
⏰ Hora: {datetime.now().strftime("%H:%M")}

{'🔔 Hay señales activas - Revisa los mensajes anteriores' if senales > 0 else '⚪ Sin señales claras hoy - El mercado está en línea con las previsiones'}
        """
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            requests.post(self.url, json=payload, timeout=10)
            print("✅ Resumen enviado a Telegram")
        except:
            pass