import sys
import json
from pathlib import Path
from scraper import obtener_noticias_del_dia, obtener_proxima_noticia
from notifier import TelegramNotifier
from config import ALERT_STATE

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
        noticias=dia_data['noticias'],
        panorama_semanal=dia_data.get('panorama_semanal', '')
    )
    
    print("✅ Resumen enviado a Telegram")
    sys.exit(0)

def ejecutar_alerta_pre_noticia():
    """Envía alerta 30 minutos antes de la noticia"""
    print("="*50)
    print("⏰ ALERTA PRE-NOTICIA")
    print("="*50)
    
    proxima = obtener_proxima_noticia()
    if not proxima:
        print("No hay noticias futuras para hoy.")
        sys.exit(0)

    minutos = proxima["minutos"]
    if minutos > 30:
        print(f"La próxima noticia es en {minutos} minutos; aún no corresponde alertar.")
        sys.exit(0)

    ruta_estado = Path(ALERT_STATE)
    if not ruta_estado.is_absolute():
        ruta_estado = Path(__file__).resolve().parent / ruta_estado
    noticias = proxima.get("noticias", [proxima["noticia"]])
    try:
        estado = json.loads(ruta_estado.read_text(encoding="utf-8")) if ruta_estado.exists() else {}
    except (OSError, json.JSONDecodeError):
        estado = {}
    alertadas = set(estado.get("alertadas", []))
    # Compatibilidad con el estado de la versión anterior.
    if estado.get("ultima_alerta"):
        alertadas.add(estado["ultima_alerta"])
    pendientes = [
        noticia for noticia in noticias
        if f"{noticia['fecha']}|{noticia['hora']}|{noticia['evento']}" not in alertadas
    ]
    if not pendientes:
        print("Esta noticia ya recibió su alerta previa.")
        sys.exit(0)

    notifier = TelegramNotifier()
    enviados = 0
    for noticia in pendientes:
        if notifier.enviar_alerta_pre_noticia(noticia, minutos=minutos):
            alertadas.add(f"{noticia['fecha']}|{noticia['hora']}|{noticia['evento']}")
            enviados += 1
    if enviados:
        ruta_estado.write_text(json.dumps({"alertadas": sorted(alertadas)[-500:]}, ensure_ascii=False), encoding="utf-8")
        print(f"✅ {enviados} alerta(s) enviada(s) a Telegram")
    else:
        print("❌ No se pudo enviar la alerta")
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
