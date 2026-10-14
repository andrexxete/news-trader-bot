import time
from notifier import TelegramNotifier
from config import MIN_DEVIATION_PERCENT
from scraper import obtener_noticias_reales
import time
from datetime import datetime

def esperar_hora_ejecucion(hora_objetivo="07:35"):
    """Espera hasta la hora exacta para ejecutar el análisis"""
    print(f"⏰ Bot en espera. Se ejecutará a las {hora_objetivo}")
    print(f"   Hora actual: {datetime.now().strftime('%H:%M')}")
    
    while True:
        ahora = datetime.now().strftime("%H:%M")
        if ahora >= hora_objetivo:
            print(f"\n🔔 ¡Son las {ahora}! Ejecutando análisis...")
            break
        time.sleep(60)  # Revisa cada minuto

def analizar_noticia(evento, actual, prevision):
    """Calcula el desvío entre dato real y previsión"""
    try:
        # Limpiar datos
        val_actual_str = str(actual).replace('%', '').replace('M', '').replace('K', '').strip()
        val_prevision_str = str(prevision).replace('%', '').replace('M', '').replace('K', '').strip()
        
        if not val_actual_str or val_actual_str == '' or val_actual_str == 'None':
            return None  # Aún no hay dato real
        
        val_actual = float(val_actual_str)
        val_prevision = float(val_prevision_str)
        
        if val_prevision == 0:
            return None

        # Calcular desvío
        desvio = ((val_actual - val_prevision) / abs(val_prevision)) * 100
        
        # Lógica de trading
        if desvio > 0.5:  # Dato mayor que previsión → USD fuerte
            return {'direccion': 'SHORT', 'desvio': round(desvio, 2)}
        elif desvio < -0.5:  # Dato menor que previsión → USD débil
            return {'direccion': 'LONG', 'desvio': round(desvio, 2)}
        else:
            return None
            
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def ejecutar_trader():
    print("="*50)
    print(" 🚀 INICIANDO NEWS TRADER BOT (MODO REAL)")
    print("="*50)
    
    # 1. Obtener noticias reales de la web
    noticias = obtener_noticias_reales()
    
    if not noticias:
        print("❌ No hay noticias para procesar.")
        return

    notifier = TelegramNotifier()
    señales_encontradas = 0

    # 2. Analizar cada noticia
    for noticia in noticias:
        # Adaptamos los nombres de columnas según lo que devuelva el scraper
        evento = noticia.get('Event', noticia.get('evento', 'Desconocido'))
        prevision = noticia.get('Forecast', noticia.get('prevision', '0'))
        actual = noticia.get('Actual', noticia.get('real', '0'))
        
        print(f"\n🔍 Analizando: {evento}")
        print(f"   Previsión: {prevision} | Actual: {actual}")
        
        resultado = analizar_noticia(evento, actual, prevision)
        
        if resultado:
            print(f"   ⚡ ¡SEÑAL DETECTADA! -> {resultado['direccion']} (Desvío: {resultado['desvio']}%)")
            
            # Enviar al celular
            notifier.send_signal(
                event_name=evento,
                direction=resultado['direccion'],
                deviation=resultado['desvio'],
                actual=str(actual),
                forecast=str(prevision)
            )
            señales_encontradas += 1
            time.sleep(2) # Pausa para no saturar Telegram
        else:
            print("   ⚪ Sin señal clara.")

    print("\n" + "="*50)
    print(f"✅ Proceso terminado. Señales enviadas: {señales_encontradas}")
    print("="*50)

if __name__ == "__main__":
    # Descomenta la siguiente línea el miércoles para que espere automáticamente:
    # esperar_hora_ejecucion("07:35")
    
    ejecutar_trader()