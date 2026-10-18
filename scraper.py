import json
from datetime import datetime

def cargar_noticias_semanales():
    """Carga las noticias de la semana desde weekly_news.json"""
    try:
        with open('weekly_news.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return datos
    except Exception as e:
        print(f"❌ Error cargando weekly_news.json: {e}")
        return None

def obtener_dia_actual():
    """Retorna el nombre del día en español"""
    dias = {
        0: 'lunes',
        1: 'martes',
        2: 'miercoles',
        3: 'jueves',
        4: 'viernes',
        5: 'sabado',
        6: 'domingo'
    }
    return dias.get(datetime.now().weekday(), 'lunes')

def obtener_noticias_del_dia():
    """Retorna las noticias del día actual"""
    datos = cargar_noticias_semanales()
    
    if not datos:
        return None
    
    dia = obtener_dia_actual()
    dia_data = datos.get('dias', {}).get(dia)
    
    if not dia_data:
        return None
    
    return {
        'semana': datos.get('semana', ''),
        'dia': dia,
        'fecha': dia_data.get('fecha', ''),
        'noticias': dia_data.get('noticias', [])
    }

def obtener_proxima_noticia():
    """Retorna la próxima noticia del día (para alerta 30 min antes)"""
    dia_data = obtener_noticias_del_dia()
    
    if not dia_data or not dia_data['noticias']:
        return None
    
    ahora = datetime.now().strftime("%H:%M")
    
    for noticia in dia_data['noticias']:
        hora_noticia = noticia.get('hora', '')
        # Calcular si faltan 30 minutos
        # Por simplicidad, retornamos la primera noticia del día
        return {
            'dia_data': dia_data,
            'noticia': noticia
        }
    
    return None