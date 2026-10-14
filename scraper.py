import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def obtener_dia_semana():
    """Retorna el nombre del día en formato clave del JSON"""
    dias = {
        0: 'lunes', 1: 'martes', 2: 'miercoles', 
        3: 'jueves', 4: 'viernes'
    }
    return dias.get(datetime.now().weekday(), 'miercoles')

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

def obtener_noticias_reales():
    """
    Sistema híbrido:
    - Previsiones: desde forecasts.json
    - Datos reales: desde FRED API (si está disponible)
    - Fallback: datos simulados para pruebas
    """
    print("🌐 Cargando previsiones del mercado...")
    previsiones = cargar_previsiones()
    
    if not previsiones:
        print("️ No hay previsiones para hoy.")
        return []
    
    print(f"📊 {len(previsiones)} eventos programados para hoy")
    print("🌐 Intentando obtener datos reales de FRED API...")
    
    # Intentar usar FRED
    try:
        from fredapi import Fred
        FRED_API_KEY = os.getenv("FRED_API_KEY")
        fred = Fred(api_key=FRED_API_KEY)
        
        noticias = []
        for prev in previsiones:
            nombre = prev['event']
            forecast = prev['forecast']
            previous = prev['previous']
            unit = prev.get('unit', '')
            
            # Intentar obtener dato real de FRED
            dato_real = None
            try:
                serie_id = None
                if 'IPC' in nombre or 'CPI' in nombre:
                    serie_id = 'CPIAUCSL'
                elif 'vivienda' in nombre.lower():
                    serie_id = 'EXHOSLUSM495S'
                elif 'minorista' in nombre.lower() or 'retail' in nombre.lower():
                    serie_id = 'RSXFS'
                
                if serie_id:
                    datos = fred.get_series(serie_id, observation_start='2026-09-01')
                    if not datos.empty and len(datos) >= 2:
                        ultimo = datos.iloc[-1]
                        anterior = datos.iloc[-2]
                        if anterior != 0:
                            dato_real = round(((ultimo - anterior) / anterior) * 100, 2)
            except:
                pass
            
            if dato_real is not None:
                actual_str = f"{dato_real}"
                print(f"   ✅ {nombre}: Real={actual_str}{unit}")
            else:
                # FALLBACK: Usar dato simulado para pruebas
                try:
                    forecast_num = float(forecast)
                    dato_simulado = round(forecast_num * 1.2, 2)
                    actual_str = f"{dato_simulado}"
                    print(f"   ⚠️ {nombre}: FRED no disponible, usando simulado={actual_str}{unit}")
                except:
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
        
    except Exception as e:
        print(f"❌ Error con FRED API: {e}")
        print("🔄 Usando datos de respaldo con valores simulados...")
        return obtener_datos_respaldo()


def obtener_datos_respaldo():
    """Datos de respaldo con valores 'Actual' simulados para pruebas"""
    print("📋 Usando datos de respaldo (SIMULACIÓN)")
    return [
        {
            "Time": "07:30", 
            "Currency": "USD", 
            "Event": "IPC subyacente (Mensual)", 
            "Actual": "0.3",
            "Forecast": "0.2%", 
            "Previous": "0.3%"
        },
        {
            "Time": "07:30", 
            "Currency": "USD", 
            "Event": "IPC (Mensual)", 
            "Actual": "0.7",
            "Forecast": "0.6%", 
            "Previous": "0.4%"
        },
        {
            "Time": "07:30", 
            "Currency": "USD", 
            "Event": "IPC (Anual)", 
            "Actual": "3.8",
            "Forecast": "3.6%", 
            "Previous": "3.4%"
        },
    ]