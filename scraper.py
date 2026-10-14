import json
import os
from fredapi import Fred
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Conectar a FRED API
FRED_API_KEY = os.getenv("FRED_API_KEY")
fred = Fred(api_key=FRED_API_KEY)

# Mapeo de eventos a series de FRED
FRED_SERIES = {
    'Ventas de viviendas': 'EXHOSLUSM495S',
    'IPC': 'CPIAUCSL',
    'CPI': 'CPIAUCSL',
    'Ventas minoristas': 'RSXFS',
    'Retail': 'RSXFS',
    'IPP': 'IPMAN',
    'Philly Fed': 'GACDFSA066MSFRBPHI',
    'Desempleo': 'ICSA',
    'Unemployment': 'ICSA'
}

def obtener_dia_semana():
    """Retorna el nombre del día en formato clave del JSON"""
    dias = {
        0: 'lunes_07', 1: 'martes_13', 2: 'miercoles_14', 
        3: 'jueves_15', 4: 'viernes_16'
    }
    return dias.get(datetime.now().weekday(), 'miercoles_14')

def cargar_previsiones():
    """Carga las previsiones del mercado desde el JSON"""
    try:
        with open('forecasts.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        dia = obtener_dia_semana()
        return datos.get(dia, [])
    except Exception as e:
        print(f"⚠️ Error cargando previsiones: {e}")
        return []

def obtener_dato_real_fred(nombre_evento):
    """Obtiene el dato REAL más reciente de FRED"""
    try:
        # Buscar la serie de FRED correspondiente
        serie_id = None
        for keyword, sid in FRED_SERIES.items():
            if keyword.lower() in nombre_evento.lower():
                serie_id = sid
                break
        
        if not serie_id:
            return None
        
        # Obtener últimos datos
        datos = fred.get_series(serie_id, observation_start='2026-09-01')
        
        if datos.empty:
            return None
        
        ultimo = datos.iloc[-1]
        anterior = datos.iloc[-2] if len(datos) > 1 else ultimo
        
        # Calcular cambio porcentual (para datos en índice)
        if 'IPC' in nombre_evento or 'CPI' in nombre_evento:
            if 'Anual' in nombre_evento or 'y/y' in nombre_evento:
                # Cambio interanual
                if len(datos) >= 12:
                    hace_un_ano = datos.iloc[-12]
                    cambio = ((ultimo - hace_un_ano) / hace_un_ano) * 100
                else:
                    cambio = ((ultimo - anterior) / anterior) * 100
            else:
                # Cambio mensual
                cambio = ((ultimo - anterior) / anterior) * 100
        else:
            # Para otros datos, cambio simple
            cambio = ((ultimo - anterior) / anterior) * 100
        
        return round(cambio, 2)
        
    except Exception as e:
        print(f"   ⚠️ Error FRED para {nombre_evento}: {e}")
        return None

def obtener_noticias_reales():
    """
    Sistema híbrido:
    - Previsiones: desde forecasts.json (manual, 2 min/semana)
    - Datos reales: desde FRED API (automático)
    """
    print("🌐 Cargando previsiones del mercado...")
    previsiones = cargar_previsiones()
    
    if not previsiones:
        print("⚠️ No hay previsiones para hoy. Actualiza forecasts.json")
        return []
    
    print(f"📊 {len(previsiones)} eventos programados para hoy")
    print("🌐 Obteniendo datos reales de FRED API...")
    
    noticias = []
    for prev in previsiones:
        nombre = prev['event']
        forecast = prev['forecast']
        previous = prev['previous']
        unit = prev.get('unit', '')
        
        # Intentar obtener dato real de FRED
        dato_real = obtener_dato_real_fred(nombre)
        
        if dato_real is not None:
            actual_str = f"{dato_real}{unit}"
            print(f"   ✅ {nombre}: Real={actual_str}, Forecast={forecast}{unit}")
        else:
            # Si FRED falla, usar dato vacío (el bot esperará)
            actual_str = ""
            print(f"   ⏳ {nombre}: Esperando dato real...")
        
        noticias.append({
            'Time': prev['time'],
            'Currency': 'USD',
            'Event': nombre,
            'Actual': actual_str,
            'Forecast': f"{forecast}{unit}",
            'Previous': f"{previous}{unit}"
        })
    
    return noticias


def obtener_datos_respaldo():
    """Datos de respaldo para pruebas"""
    print("📋 Usando datos de respaldo (SIMULACIÓN)")
    return [
        {
            "Time": "07:30", 
            "Currency": "USD", 
            "Event": "IPC (Mensual)", 
            "Actual": "0.7",
            "Forecast": "0.6", 
            "Previous": "0.4",
            "unit": "%"
        },
        {
            "Time": "07:30", 
            "Currency": "USD", 
            "Event": "IPC (Anual)", 
            "Actual": "3.8",
            "Forecast": "3.6", 
            "Previous": "3.4",
            "unit": "%"
        },
    ]