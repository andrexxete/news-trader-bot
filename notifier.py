import requests
import json
from datetime import datetime, timezone
from pathlib import Path
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, FORECAST_LOG, TIMEZONE

class TelegramNotifier:
    def __init__(self):
        self.url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        self.chat_id = TELEGRAM_CHAT_ID

    def enviar_mensaje(self, texto):
        """Envía un mensaje genérico a Telegram"""
        if not self.chat_id or not TELEGRAM_TOKEN:
            print("❌ Configura TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en .env")
            return False
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

    def enviar_resumen_dia(self, semana, dia, fecha, noticias, panorama_semanal=""):
        """Envía el resumen del día a las 07:00 AM"""
        lista_noticias = ""
        for n in noticias:
            impacto_emoji = "🔴" if n.get('impacto') == 'alto' else "🟡"
            lista_noticias += f"{impacto_emoji} *{n['hora']}* - {n['evento']}\n"
            lista_noticias += f"   Previsión: {n.get('prevision', 'N/A')} | Anterior: {n.get('anterior', 'N/A')}\n"
            lista_noticias += f"   Proyección: {n.get('tu_analisis', 'Pendiente de completar')}\n\n"
        
        mensaje = f"""
📅 *RESUMEN DEL DÍA*

*Semana:* {semana}
*Hoy:* {dia.capitalize()} {fecha} ({TIMEZONE})

📊 *Noticias importantes:*

{lista_noticias}

🧭 *Panorama semanal:*
{panorama_semanal or 'Sin panorama semanal cargado.'}

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
        analisis = noticia.get('tu_analisis', 'Proyección pendiente de completar.')
        alcista = noticia.get('escenario_alcista', 'Completar el escenario para el oro.')
        bajista = noticia.get('escenario_bajista', 'Completar el escenario para el oro.')
        confirmacion = noticia.get('confirmacion', 'Esperar confirmación del precio y observar dólar/rendimientos.')
        invalidacion = noticia.get('invalidacion', 'Sin condición de invalidación definida; considerar esperar.')
        fuente = noticia.get('fuente', 'No especificada')
        confianza = noticia.get('confianza', 'No definida')
        
        mensaje = f"""
 *ORO | NOTICIA EN {minutos} MINUTOS*

📊 *{evento}*
⏱️ Hora local ({TIMEZONE}): {hora}

📈 *Datos:*
Previsión: {prevision}
Anterior: {anterior}

🧭 *Proyección:*
{analisis}

🟢 *Escenario favorable al oro:*
{alcista}

🔴 *Escenario desfavorable al oro:*
{bajista}

📍 *Confirmación:* {confirmacion}
⛔ *Invalidación / esperar:* {invalidacion}
📊 *Confianza:* {confianza}
🔗 *Fuente:* {fuente}

⚠️ El sesgo es condicional. Comparar el dato publicado con el consenso y evaluar la reacción del precio; no operar solo por el titular.

Abre tu gráfico y verifica la publicación en la fuente oficial.
        """
        enviado = self.enviar_mensaje(mensaje)
        if enviado:
            self._registrar_proyeccion(noticia)
        return enviado

    @staticmethod
    def _registrar_proyeccion(noticia):
        """Guarda una copia de la proyección tal como se envió, para auditarla."""
        ruta = Path(FORECAST_LOG)
        if not ruta.is_absolute():
            ruta = Path(__file__).resolve().parent / ruta
        registro = {
            "enviado_utc": datetime.now(timezone.utc).isoformat(),
            "evento": noticia.get("evento"),
            "fecha": noticia.get("fecha"),
            "hora": noticia.get("hora"),
            "consenso": noticia.get("prevision"),
            "anterior": noticia.get("anterior"),
            "proyeccion": noticia.get("tu_analisis"),
            "escenario_alcista": noticia.get("escenario_alcista"),
            "escenario_bajista": noticia.get("escenario_bajista"),
            "confirmacion": noticia.get("confirmacion"),
            "invalidacion": noticia.get("invalidacion"),
            "confianza": noticia.get("confianza"),
            "fuente": noticia.get("fuente"),
        }
        try:
            with ruta.open("a", encoding="utf-8") as archivo:
                archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
        except OSError as error:
            print(f"⚠️ No se pudo guardar el historial de proyecciones: {error}")

    def enviar_recordatorio_generico(self, mensaje_texto):
        """Envía un mensaje genérico"""
        return self.enviar_mensaje(mensaje_texto)
