"""
Servicio para manejar los datos de estadísticas
"""
from datetime import datetime, timedelta
from src.core.config import REPORTS_ENDPOINTS
from src.shared.utils import APIHandler, SessionManager
from .fallback_data import FallbackDataProvider


class StatisticsService:
    """Servicio para obtener y procesar datos de estadísticas"""
    
    @staticmethod
    def get_date_range(periodo):
        """Obtiene el rango de fechas según el período seleccionado con lógica mejorada"""
        try:
            today = datetime.now()
            
            if periodo == "Últimos 7 días":
                # Últimos 7 días completos (desde hace 7 días hasta ayer)
                start_date = today - timedelta(days=7)
                end_date = today - timedelta(days=1)
                
            elif periodo == "Último mes":
                # Mes pasado completo (1 al último día del mes anterior)
                if today.month == 1:
                    # Si es enero, el mes anterior es diciembre del año pasado
                    start_date = datetime(today.year - 1, 12, 1)
                    end_date = datetime(today.year, 1, 1) - timedelta(days=1)
                else:
                    # Primer día del mes anterior
                    start_date = datetime(today.year, today.month - 1, 1)
                    # Último día del mes anterior
                    end_date = datetime(today.year, today.month, 1) - timedelta(days=1)
                    
            elif periodo == "Mes actual":
                # Mes actual completo (desde el día 1 hasta el último día del mes)
                start_date = datetime(today.year, today.month, 1)
                # Último día del mes actual
                if today.month == 12:
                    end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
                    
            elif periodo == "Últimos 30 días":
                # Últimos 30 días desde hoy hacia atrás
                start_date = today - timedelta(days=30)
                end_date = today
                
            elif periodo == "Últimos 3 meses":
                # Últimos 3 meses completos
                if today.month <= 3:
                    # Si estamos en los primeros 3 meses, ir al año anterior
                    start_date = datetime(today.year - 1, today.month + 9, 1)
                else:
                    start_date = datetime(today.year, today.month - 3, 1)
                # Último día del mes anterior al actual
                end_date = datetime(today.year, today.month, 1) - timedelta(days=1)
                
            elif periodo == "Trimestre actual":
                # Trimestre actual completo
                current_quarter = (today.month - 1) // 3 + 1
                start_month = (current_quarter - 1) * 3 + 1
                start_date = datetime(today.year, start_month, 1)
                
                if current_quarter == 4:
                    end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_month = current_quarter * 3 + 1
                    end_date = datetime(today.year, end_month, 1) - timedelta(days=1)
                    
            elif periodo == "Año actual":
                # Todo el año actual hasta hoy
                start_date = datetime(today.year, 1, 1)
                end_date = today
                
            else:
                # Fallback: Últimos 30 días
                print(f"Período no reconocido: {periodo}, usando últimos 30 días")
                start_date = today - timedelta(days=30)
                end_date = today
            
            # Formatear las fechas para la API
            fecha_inicio = start_date.strftime("%Y-%m-%d")
            fecha_fin = end_date.strftime("%Y-%m-%d")
            
            print(f"📅 Período '{periodo}': {fecha_inicio} a {fecha_fin} ({(end_date - start_date).days + 1} días)")
            
            return fecha_inicio, fecha_fin
            
        except Exception as e:
            print(f"Error al obtener rango de fechas: {str(e)}")
            import traceback
            traceback.print_exc()
            # Retornar último mes por defecto
            today = datetime.now()
            start_date = today - timedelta(days=30)
            return start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    
    @staticmethod
    def fetch_kpis(fecha_inicio, fecha_fin):
        """Obtiene los KPIs desde la API"""
        try:
            # Construir URL con parámetros
            url = f"{REPORTS_ENDPOINTS['data_kpis']}?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}"
            print(f"🌐 Consultando KPIs: {fecha_inicio} a {fecha_fin}")
            
            # Obtener token de sesión
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            # Hacer petición
            response = APIHandler.make_request('get', url, headers=headers)
            
            if response.get('status_code') == 200:
                data = response.get('data', {})
                
                # Verificar la estructura exacta de los datos
                if 'data' in data:
                    kpi_data = data.get('data', {})
                else:
                    print("⚠️ No se encontró la clave 'data' en la respuesta")
                    kpi_data = {}
                
                # Procesar la nueva estructura de respuesta
                result = {
                    'success': True, 
                    'data': kpi_data,
                    'periodo': data.get('periodo', {}),
                    'mensaje': data.get('mensaje', '')
                }
                return result
            else:
                error_msg = response.get('message', 'Error desconocido')
                print(f"❌ Error en API: {error_msg} (Status: {response.get('status_code')})")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            print(f"💥 Error al conectar con la API: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def fetch_chart_data(chart_type, fecha_inicio, fecha_fin):
        """Obtiene datos específicos para gráficos desde la API con nuevo formato"""
        try:
            # Construir URL con parámetros para gráficos
            url = f"{REPORTS_ENDPOINTS['data_charts']}?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}&tipo={chart_type}"
            print(f"🌐 Solicitando datos de gráfico desde: {url}")
            
            # Obtener token de sesión
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            # Hacer petición
            response = APIHandler.make_request('get', url, headers=headers)
            
            if response.get('status_code') == 200:
                api_data = response.get('data', {})
                
                # Verificar si tenemos la nueva estructura de datos
                if 'chart_data' in api_data:
                    chart_data = api_data['chart_data']
                    
                    # Adaptar el formato de la nueva API al formato esperado por los componentes
                    adapted_data = {
                        'labels': chart_data.get('labels', []),
                        'datasets': chart_data.get('datasets', []),
                        'chart_type': chart_data.get('chart_type', 'line'),
                        'title': chart_data.get('title', ''),
                        'description': chart_data.get('description', ''),
                        'chart_config': chart_data.get('chart_config', {}),
                        'additional_data': chart_data.get('additional_data', {})
                    }
                    
                    # Procesar datasets para asegurar compatibilidad
                    for dataset in adapted_data['datasets']:
                        # Convertir strings numéricos a números
                        if 'data' in dataset:
                            numeric_data = []
                            for val in dataset['data']:
                                try:
                                    # Intentar convertir a float si es string
                                    if isinstance(val, str):
                                        numeric_data.append(float(val))
                                    else:
                                        numeric_data.append(val)
                                except (ValueError, TypeError):
                                    numeric_data.append(0)
                            dataset['data'] = numeric_data
                    
                    print(f"✅ Datos de gráfico adaptados correctamente: {chart_type}")
                    return adapted_data
                else:
                    print("⚠️ Estructura de datos no reconocida, usando fallback")
                    return FallbackDataProvider.get_chart_data(chart_type)
            else:
                error_msg = response.get('message', 'Error desconocido')
                print(f"❌ Error en API de gráficos: {error_msg}")
                return FallbackDataProvider.get_chart_data(chart_type)
                
        except Exception as e:
            print(f"💥 Error al obtener datos de gráfico: {str(e)}")
            return FallbackDataProvider.get_chart_data(chart_type)
    
    @staticmethod
    def get_fallback_data():
        """Retorna datos de fallback para KPIs cuando no se puede conectar a la API"""
        return FallbackDataProvider.get_kpi_data()
    
    @staticmethod
    def get_fallback_chart_data(chart_type):
        """Retorna datos de fallback para gráficos"""
        return FallbackDataProvider.get_chart_data(chart_type)
