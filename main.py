import sys
from datetime import datetime
from scraper import obtener_noticias_del_dia
from notifier import TelegramNotifier

def ejecutar_recordatorio_diario():
    """Envía el resumen del día a las 07:00 AM"""
    print("="*50)
    print(" RECORDATORIO DIARIO")
    print("="*50)
    
    dia_data = obtener_noticias_del_dia()
    
    if not dia_data:
        print("No hay noticias para hoy.")
        notifier = TelegramNotifier()
        notifier.enviar_mensaje("⚪ Hoy no hay noticias importantes programadas.")
        sys.exit(0)
    
    print(f" {len(dia_data['noticias'])} noticias para hoy")
    
    notifier = TelegramNotifier()
    notifier.enviar_resumen_dia(
        semana=dia_data['semana'],
        dia=dia_data['dia'],
        fecha=dia_data['fecha'],
        noticias=dia_data['noticias']
    )
    
    print("✅ Resumen enviado a Telegram")
    sys.exit(0)

def ejecutar_alerta_pre_noticia():
    """Envía alerta 30 minutos antes de la noticia"""
    print("="*50)
    print("⏰ ALERTA PRE-NOTICIA")
    print("="*50)
    
    dia_data = obtener_noticias_del_dia()
    
    if not dia_data or not dia_data['noticias']:
        print("No hay noticias para hoy.")
        sys.exit(0)
    
    notifier = TelegramNotifier()
    
    for noticia in dia_data['noticias']:
        notifier.enviar_alerta_pre_noticia(noticia, minutos=30)
    
    print("✅ Alertas enviadas a Telegram")
    sys.exit(0)

if __name__ == "__main__":
    # Determinar qué función ejecutar según el argumento
    if len(sys.argv) > 1:
        modo = sys.argv[1]
    else:
        modo = 'resumen'
    
    if modo == 'alerta':
        ejecutar_alerta_pre_noticia()
    else:
        ejecutar_recordatorio_diario()