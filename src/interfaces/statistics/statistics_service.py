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
        """Obtiene datos específicos para gráficos desde la API"""
        try:
            # Construir URL con parámetros para gráficos
            url = f"{REPORTS_ENDPOINTS['data_charts']}?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}&tipo={chart_type}"
            print(f"Solicitando datos de gráfico desde: {url}")
            
            # Obtener token de sesión
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            # Hacer petición
            response = APIHandler.make_request('get', url, headers=headers)
            print(f"Respuesta de gráficos: {response}")
            
            if response['status_code'] == 200:
                data = response['data']
                
                # Validar estructura de respuesta
                if 'data' in data and isinstance(data['data'], dict):
                    return {
                        'success': True,
                        'data': data['data'],
                        'tipo': data.get('tipo', chart_type),
                        'periodo': data.get('periodo', {})
                    }
                else:
                    print("Estructura de datos inválida en respuesta de gráficos")
                    return {
                        'success': False,
                        'error': 'Estructura de datos inválida',
                        'data': StatisticsService.get_fallback_chart_data(chart_type)
                    }
            else:
                print(f"Error en API de gráficos: {response}")
                return {
                    'success': False,
                    'error': f"Error del servidor: {response.get('status_code', 'Desconocido')}",
                    'data': StatisticsService.get_fallback_chart_data(chart_type)
                }
                
        except Exception as e:
            print(f"Error al obtener datos de gráfico: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': StatisticsService.get_fallback_chart_data(chart_type)
            }
    
    @staticmethod
    def get_fallback_data():
        """Retorna datos de fallback cuando no se puede conectar a la API"""
        return {
            'total_ventas': {
                'valor': 0,
                'formato': 'currency',
                'crecimiento': {
                    'porcentaje': 0,
                    'tendencia': 'neutral',
                    'valor_anterior': 0,
                    'diferencia_absoluta': 0
                }
            },
            'total_pedidos': {
                'valor': 0,
                'formato': 'number',
                'crecimiento': {
                    'porcentaje': 0,
                    'tendencia': 'neutral',
                    'valor_anterior': 0,
                    'diferencia_absoluta': 0
                }
            },
            'ticket_promedio': {
                'valor': 0,
                'formato': 'currency',
                'crecimiento': {
                    'porcentaje': 0,
                    'tendencia': 'neutral',
                    'valor_anterior': 0,
                    'diferencia_absoluta': 0
                }
            },
            'conversion_rate': {
                'valor': 0,
                'formato': 'percentage',
                'contexto': {
                    'carritos_creados': 0,
                    'pedidos_completados': 0,
                    'descripcion': 'Sin datos de conversión disponibles'
                }
            }
        }
    
    @staticmethod
    def get_fallback_chart_data(chart_type):
        """Proporciona datos de respaldo para gráficos cuando la API falla"""
        if chart_type == "ventas_diarias":
            return {
                'labels': ['2025-07-01', '2025-07-02', '2025-07-03', '2025-07-04', '2025-07-05', '2025-07-06', '2025-07-07'],
                'datasets': [
                    {
                        'label': 'Ventas Diarias',
                        'data': [1250, 1680, 1420, 1890, 2100, 1750, 2300],
                        'backgroundColor': 'rgba(22, 163, 74, 0.2)',
                        'borderColor': 'rgba(22, 163, 74, 1)',
                        'borderWidth': 2
                    },
                    {
                        'label': 'Transacciones',
                        'data': [15, 22, 18, 25, 28, 21, 32],
                        'backgroundColor': 'rgba(37, 99, 235, 0.2)',
                        'borderColor': 'rgba(37, 99, 235, 1)',
                        'borderWidth': 2
                    }
                ]
            }
        
        elif chart_type == "ventas_mensuales":
            return {
                'labels': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07'],
                'datasets': [
                    {
                        'label': 'Ventas Mensuales',
                        'data': [45000, 52000, 48000, 58000, 62000, 59000, 65000],
                        'backgroundColor': 'rgba(16, 185, 129, 0.2)',
                        'borderColor': 'rgba(16, 185, 129, 1)',
                        'borderWidth': 2,
                        'fill': True
                    }
                ]
            }
        
        elif chart_type == "productos_vendidos":
            return {
                'labels': ['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E', 
                          'Producto F', 'Producto G', 'Producto H', 'Producto I', 'Producto J'],
                'datasets': [
                    {
                        'label': 'Unidades Vendidas',
                        'data': [850, 720, 650, 580, 480, 420, 380, 320, 280, 250],
                        'backgroundColor': [
                            '#16A34A', '#2563EB', '#F59E0B', '#EF4444', '#8B5CF6',
                            '#10B981', '#3B82F6', '#F97316', '#DC2626', '#A855F7'
                        ]
                    }
                ]
            }
        
        elif chart_type == "estados_pedidos":
            return {
                'labels': ['Completado', 'Pendiente', 'En Proceso', 'Cancelado'],
                'datasets': [
                    {
                        'data': [75, 15, 8, 2],
                        'backgroundColor': ['#28a745', '#ffc107', '#17a2b8', '#dc3545']
                    }
                ]
            }
        
        else:
            # Datos genéricos para tipos no reconocidos
            return {
                'labels': ['Sin datos'],
                'datasets': [
                    {
                        'label': 'Sin datos disponibles',
                        'data': [0],
                        'backgroundColor': '#6B7280'
                    }
                ]
            }
