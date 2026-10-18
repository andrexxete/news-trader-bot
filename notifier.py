import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def __init__(self):
        self.url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        self.chat_id = TELEGRAM_CHAT_ID

    def enviar_mensaje(self, texto):
        """Envía un mensaje genérico a Telegram"""
        payload = {
            'chat_id': self.chat_id,
            'text': texto,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Mensaje enviado")
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def enviar_resumen_dia(self, semana, dia, fecha, noticias):
        """Envía el resumen del día a las 07:00 AM"""
        lista_noticias = ""
        for n in noticias:
            impacto_emoji = "" if n.get('impacto') == 'alto' else "🟡"
            lista_noticias += f"{impacto_emoji} *{n['hora']}* - {n['evento']}\n"
            lista_noticias += f"   Previsión: {n.get('prevision', 'N/A')} | Anterior: {n.get('anterior', 'N/A')}\n"
            lista_noticias += f"    {n.get('tu_analisis', '')}\n\n"
        
        mensaje = f"""
📅 *RESUMEN DEL DÍA*

*Semana:* {semana}
*Hoy:* {dia.capitalize()} {fecha}

📊 *Noticias importantes:*

{lista_noticias}

⚠️ *Recuerda:*
- Esperar confirmación del precio
- No operar antes de la noticia
- Gestión de riesgo: 1% del capital
        """
        
        return self.enviar_mensaje(mensaje)

    def enviar_alerta_pre_noticia(self, noticia, minutos=30):
        """Envía alerta 30 minutos antes de la noticia"""
        evento = noticia.get('evento', '')
        hora = noticia.get('hora', '')
        prevision = noticia.get('prevision', 'N/A')
        anterior = noticia.get('anterior', 'N/A')
        analisis = noticia.get('tu_analisis', '')
        sesgo = noticia.get('sesgo', '')
        
        mensaje = f"""
 *ALERTA: EN {minutos} MINUTOS*

📊 *{evento}*
⏱️ Hora: {hora}

📈 *Datos:*
Previsión: {prevision}
Anterior: {anterior}

💭 *Tu análisis:*
{analisis}

🎯 *Sesgo:*
{sesgo}

️ *Qué observar:*
- Esperar vela de 5m cerrada
- Confirmar con volumen
- Respetar niveles clave

 *Abre tu gráfico ahora*
        """
        
        return self.enviar_mensaje(mensaje)

    def enviar_recordatorio_generico(self, mensaje_texto):
        """Envía un mensaje genérico"""
        return self.enviar_mensaje(mensaje_texto)