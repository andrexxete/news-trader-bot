import time
import sys
from datetime import datetime
from notifier import TelegramNotifier
from scraper import obtener_noticias_reales
from config import MIN_DEVIATION_PERCENT

def analizar_noticia(evento, actual, prevision):
    """Calcula el desvío entre dato real y previsión"""
    try:
        val_actual_str = str(actual).replace('%', '').replace('M', '').replace('K', '').strip()
        val_prevision_str = str(prevision).replace('%', '').replace('M', '').replace('K', '').strip()
        
        if not val_actual_str or val_actual_str == '':
            return None
        
        val_actual = float(val_actual_str)
        val_prevision = float(val_prevision_str)
        
        if val_prevision == 0:
            return None

        desvio = ((val_actual - val_prevision) / abs(val_prevision)) * 100
        
        if desvio > 0.5:
            return {'direccion': 'SHORT', 'desvio': round(desvio, 2)}
        elif desvio < -0.5:
            return {'direccion': 'LONG', 'desvio': round(desvio, 2)}
        else:
            return None
            
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def ejecutar_trader():
    print("="*50)
    print("🚀 INICIANDO NEWS TRADER BOT (AUTOMÁTICO)")
    print("="*50)
    
    # Enviar mensaje de prueba PRIMERO
    print("\n📱 Enviando mensaje de prueba a Telegram...")
    notifier = TelegramNotifier()
    notifier.send_test_message()
    time.sleep(2)
    
    # Obtener noticias
    noticias = obtener_noticias_reales()
    
    if not noticias:
        print(" No hay noticias para procesar.")
        notifier.send_summary(0, 0)
        sys.exit(0)  # Salir sin error

    señales_encontradas = 0

    for noticia in noticias:
        evento = noticia.get('Event', 'Desconocido')
        prevision = noticia.get('Forecast', '0')
        actual = noticia.get('Actual', '0')
        
        print(f"\n🔍 Analizando: {evento}")
        print(f"   Previsión: {prevision} | Actual: {actual}")
        
        resultado = analizar_noticia(evento, actual, prevision)
        
        if resultado:
            print(f"    ¡SEÑAL DETECTADA! -> {resultado['direccion']} (Desvío: {resultado['desvio']}%)")
            
            notifier.send_signal(
                event_name=evento,
                direction=resultado['direccion'],
                deviation=resultado['desvio'],
                actual=str(actual),
                forecast=str(prevision)
            )
            señales_encontradas += 1
            time.sleep(2)
        else:
            print("   ⚪ Sin señal clara.")

    # Enviar resumen final
    print("\n" + "="*50)
    print(f"✅ Proceso terminado. Señales enviadas: {señales_encontradas}")
    print("="*50)
    
    notifier.send_summary(len(noticias), señales_encontradas)
    
    sys.exit(0)  # Salir siempre sin error

if __name__ == "__main__":
    try:
        ejecutar_trader()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)