"""
Servicio para manejar los datos de estadísticas
"""
from datetime import datetime, timedelta
from src.core.config import REPORTS_ENDPOINTS
from src.shared.utils import APIHandler, SessionManager


class StatisticsService:
    """Servicio para obtener y procesar datos de estadísticas"""
    
    @staticmethod
    def get_date_range(periodo):
        """Obtiene el rango de fechas según el período seleccionado"""
        try:
            today = datetime.now()
            
            if periodo == "Últimos 7 días":
                start_date = today - timedelta(days=7)
            elif periodo == "Último mes":
                start_date = today - timedelta(days=30)
            elif periodo == "Últimos 3 meses":
                start_date = today - timedelta(days=90)
            elif periodo == "Año actual":
                start_date = datetime(today.year, 1, 1)
            else:
                start_date = today - timedelta(days=30)
            
            return start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
            
        except Exception as e:
            print(f"Error al obtener rango de fechas: {str(e)}")
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
            print(f"Solicitando KPIs desde: {url}")
            
            # Obtener token de sesión
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            # Hacer petición
            response = APIHandler.make_request('get', url, headers=headers)
            print(f"Respuesta de KPIs: {response}")
            
            if response.get('status_code') == 200:
                data = response.get('data', {})
                return {'success': True, 'data': data.get('data', {})}
            else:
                error_msg = response.get('message', 'Error desconocido')
                print(f"Error en API: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            print(f"Error al conectar con la API: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_fallback_data():
        """Retorna datos de fallback cuando no se puede conectar a la API"""
        return {
            'total_ventas': {
                'valor': 0,
                'formato': 'currency',
                'crecimiento': 0
            },
            'total_pedidos': {
                'valor': 0,
                'formato': 'number',
                'crecimiento': 0
            },
            'ticket_promedio': {
                'valor': 0,
                'formato': 'currency'
            },
            'conversion_rate': {
                'valor': 0,
                'formato': 'percentage'
            }
        }
