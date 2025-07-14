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
                    return StatisticsService.get_fallback_chart_data(chart_type)
            else:
                error_msg = response.get('message', 'Error desconocido')
                print(f"❌ Error en API de gráficos: {error_msg}")
                return StatisticsService.get_fallback_chart_data(chart_type)
                
        except Exception as e:
            print(f"💥 Error al obtener datos de gráfico: {str(e)}")
            return StatisticsService.get_fallback_chart_data(chart_type)
    
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
        """Retorna datos de fallback para gráficos con formato mejorado"""
        fallback_data = {
            "ventas_diarias": {
                "labels": [
                    "2025-07-03",
                    "2025-07-10",
                    "2025-07-11", 
                    "2025-07-12",
                    "2025-07-13"
                ],
                "datasets": [
                    {
                        "label": "Ingresos Diarios ($)",
                        "data": ["52.00", "98.00", "117.00", "153.00", "106.00"],
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        "borderColor": "rgba(34, 197, 94, 1)",
                        "borderWidth": 3,
                        "fill": True,
                        "tension": 0.4,
                        "yAxisID": "y"
                    },
                    {
                        "label": "Número de Transacciones",
                        "data": [1, 1, 1, 3, 2],
                        "backgroundColor": "rgba(59, 130, 246, 0.1)",
                        "borderColor": "rgba(59, 130, 246, 1)",
                        "borderWidth": 2,
                        "borderDash": [5, 5],
                        "fill": False,
                        "yAxisID": "y1"
                    },
                    {
                        "label": "Ticket Promedio por Día ($)",
                        "data": [52, 98, 117, 51, 53],
                        "backgroundColor": "rgba(168, 85, 247, 0.1)",
                        "borderColor": "rgba(168, 85, 247, 1)",
                        "borderWidth": 2,
                        "pointRadius": 4,
                        "fill": False,
                        "yAxisID": "y"
                    }
                ],
                "chart_type": "line_dual_axis",
                "title": "Evolución de Ventas Diarias",
                "description": "Análisis de ingresos y volumen de transacciones por día",
                "chart_config": {
                    "scales": {
                        "y": {"title": "Ingresos ($)", "position": "left"},
                        "y1": {"title": "Transacciones", "position": "right", "grid": False}
                    }
                }
            },
            "ventas_mensuales": {
                "labels": ["Julio 2025"],
                "datasets": [
                    {
                        "label": "Ingresos Mensuales ($)",
                        "data": ["526.00"],
                        "backgroundColor": "rgba(16, 185, 129, 0.3)",
                        "borderColor": "rgba(16, 185, 129, 1)",
                        "borderWidth": 3,
                        "fill": True,
                        "tension": 0.4,
                        "pointBackgroundColor": "rgba(16, 185, 129, 1)",
                        "pointBorderColor": "#FFFFFF",
                        "pointBorderWidth": 2,
                        "pointRadius": 5
                    }
                ],
                "chart_type": "area",
                "title": "Evolución de Ventas Mensuales",
                "description": "Análisis de tendencias y estacionalidad de ingresos",
                "additional_data": {
                    "transacciones_por_mes": [8],
                    "dias_con_ventas": [5],
                    "ticket_promedio_mes": ["65.75"],
                    "años_meses": ["2025-07"]
                },
                "chart_config": {
                    "scales": {
                        "x": {"title": "Período"},
                        "y": {"title": "Ingresos ($)", "beginAtZero": True}
                    },
                    "plugins": {
                        "legend": {"display": True, "position": "top"},
                        "tooltip": {
                            "mode": "index",
                            "intersect": False,
                            "callbacks": {
                                "afterLabel": "Mostrar transacciones y días activos"
                            }
                        }
                    },
                    "interaction": {
                        "mode": "nearest",
                        "axis": "x",
                        "intersect": False
                    }
                }
            },
            "productos_vendidos": {
                "labels": ["Producto A", "Producto B", "Producto C", "Producto D", "Producto E"],
                "datasets": [
                    {
                        "label": "Unidades Vendidas",
                        "data": [245, 189, 156, 134, 98],
                        "backgroundColor": "rgba(251, 191, 36, 0.8)",
                        "borderColor": "rgba(251, 191, 36, 1)",
                        "borderWidth": 2
                    }
                ],
                "chart_type": "bar",
                "title": "Productos Más Vendidos",
                "description": "Ranking de productos por unidades vendidas"
            },
            "estados_pedidos": {
                "labels": ["Completado", "Pendiente", "En Proceso", "Cancelado"],
                "datasets": [
                    {
                        "label": "Estados de Pedidos",
                        "data": [68, 18, 10, 4],
                        "backgroundColor": [
                            "rgba(34, 197, 94, 0.8)",
                            "rgba(251, 191, 36, 0.8)",
                            "rgba(59, 130, 246, 0.8)",
                            "rgba(239, 68, 68, 0.8)"
                        ]
                    }
                ],
                "chart_type": "pie",
                "title": "Distribución de Estados de Pedidos",
                "description": "Porcentaje de pedidos por estado"
            }
        }
        
        return fallback_data.get(chart_type, {
            "labels": ["Sin datos"],
            "datasets": [{"label": "N/A", "data": [0]}],
            "chart_type": "line",
            "title": "Datos no disponibles",
            "description": "No se pudieron cargar los datos"
        })
