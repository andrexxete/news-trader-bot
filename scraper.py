import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import TIMEZONE

DATA_FILE = Path(__file__).with_name("weekly_news.json")
DIAS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")


def cargar_noticias_semanales():
    """Lee la agenda semanal; retorna None si el archivo no es JSON válido."""
    try:
        with DATA_FILE.open(encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if not isinstance(datos.get("dias"), dict):
            raise ValueError("Falta el objeto 'dias'.")
        return datos
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"❌ No se pudo cargar {DATA_FILE.name}: {error}")
        return None


def ahora_local():
    return datetime.now(ZoneInfo(TIMEZONE))


def obtener_dia_actual():
    return DIAS[ahora_local().weekday()]


def _noticias_validas(noticias):
    """Evita alertas incompletas o con horas/fechas mal formadas."""
    validas = []
    for noticia in noticias if isinstance(noticias, list) else []:
        if not isinstance(noticia, dict) or not noticia.get("evento"):
            continue
        try:
            datetime.strptime(noticia.get("hora", ""), "%H:%M")
        except ValueError:
            print(f"⚠️ Hora inválida para el evento: {noticia.get('evento')}")
            continue
        validas.append(noticia)
    return sorted(validas, key=lambda noticia: noticia["hora"])


def obtener_noticias_del_dia(fecha=None):
    """Retorna eventos de la fecha local actual (o de una fecha dada)."""
    datos = cargar_noticias_semanales()
    if not datos:
        return None

    fecha = fecha or ahora_local().date()
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
    dia = DIAS[fecha.weekday()]
    dias = datos["dias"]

    # El formato con fechas ISO es la fuente de verdad. El legado se acepta
    # solo si no especifica fecha, para evitar alertas de semanas anteriores.
    dia_data = next(
        (item for item in dias.values()
         if isinstance(item, dict) and item.get("fecha") == fecha.isoformat()),
        None,
    )
    if dia_data is None:
        item = dias.get(dia)
        if isinstance(item, dict) and not item.get("fecha"):
            dia_data = item
    if not dia_data:
        return None

    return {
        "semana": datos.get("semana", ""),
        "panorama_semanal": datos.get("panorama_semanal", ""),
        "dia": dia,
        "fecha": fecha.isoformat(),
        "noticias": _noticias_validas(dia_data.get("noticias", [])),
    }


def obtener_proxima_noticia():
    """Retorna la primera noticia futura de hoy y los minutos restantes."""
    dia_data = obtener_noticias_del_dia()
    if not dia_data:
        return None
    ahora = ahora_local()
    for noticia in dia_data["noticias"]:
        hora = datetime.strptime(noticia["hora"], "%H:%M").time()
        momento = datetime.combine(ahora.date(), hora, tzinfo=ahora.tzinfo)
        minutos = int((momento - ahora).total_seconds() // 60)
        if minutos >= 0:
            mismo_horario = [
                dict(item, fecha=dia_data["fecha"])
                for item in dia_data["noticias"]
                if item["hora"] == noticia["hora"]
            ]
            return {
                "dia_data": dia_data,
                "noticia": dict(noticia, fecha=dia_data["fecha"]),
                "noticias": mismo_horario,
                "minutos": minutos,
            }
    return None
