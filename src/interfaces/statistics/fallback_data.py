"""
Datos de fallback para estadísticas cuando no hay conexión a la API
"""
from typing import Dict, Any


class FallbackDataProvider:
    """Proveedor de datos de fallback para estadísticas"""
    
    @staticmethod
    def get_kpi_data() -> Dict[str, Any]:
        """Retorna datos de fallback para KPIs"""
        return {
            'total_ventas': {
                'valor': 526.00,
                'formato': 'currency',
                'crecimiento': {
                    'porcentaje': 100.0,
                    'tendencia': 'positivo',
                    'valor_anterior': 0,
                    'diferencia_absoluta': 526.00
                }
            },
            'total_pedidos': {
                'valor': 14,
                'formato': 'number',
                'crecimiento': {
                    'porcentaje': 600.0,
                    'tendencia': 'positivo',
                    'valor_anterior': 0,
                    'diferencia_absoluta': 14
                }
            },
            'ticket_promedio': {
                'valor': 37.57,
                'formato': 'currency',
                'crecimiento': {
                    'porcentaje': 292.7,
                    'tendencia': 'positivo',
                    'valor_anterior': 0,
                    'diferencia_absoluta': 37.57
                }
            },
            'conversion_rate': {
                'valor': 11.1,
                'formato': 'percentage',
                'contexto': {
                    'carritos_creados': 9,
                    'pedidos_completados': 1,
                    'descripcion': 'De 9 carritos, 1 se convirtieron en pedidos'
                }
            }
        }
    
    @staticmethod
    def get_chart_data(chart_type: str) -> Dict[str, Any]:
        """Retorna datos de fallback para gráficos específicos"""
        
        chart_data_catalog = {
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
                        "data": [52.00, 98.00, 117.00, 153.00, 106.00],
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
                        "data": [526.00],
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
                    "ticket_promedio_mes": [65.75],
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
                "labels": ["Fresa Orgánica 500g", "Lechuga Hidropónica", "Tomate Cherry 250g", "Espinaca Baby 200g", "Apio Fresco 300g"],
                "datasets": [
                    {
                        "label": "Unidades Vendidas",
                        "data": [45, 38, 32, 28, 22],
                        "backgroundColor": [
                            "rgba(239, 68, 68, 0.8)",   # Rojo para fresas
                            "rgba(34, 197, 94, 0.8)",   # Verde para lechuga
                            "rgba(245, 158, 11, 0.8)",  # Naranja para tomate
                            "rgba(16, 185, 129, 0.8)",  # Verde esmeralda para espinaca
                            "rgba(59, 130, 246, 0.8)"   # Azul para apio
                        ],
                        "borderColor": [
                            "rgba(239, 68, 68, 1)",
                            "rgba(34, 197, 94, 1)",
                            "rgba(245, 158, 11, 1)",
                            "rgba(16, 185, 129, 1)",
                            "rgba(59, 130, 246, 1)"
                        ],
                        "borderWidth": 2
                    }
                ],
                "chart_type": "bar",
                "title": "Top 5 Productos Más Vendidos",
                "description": "Ranking de productos orgánicos por cantidad de ventas",
                "additional_data": {
                    "precios_promedio": [12.50, 8.90, 15.30, 11.20, 7.80],
                    "ingresos_por_producto": [562.50, 338.20, 489.60, 313.60, 171.60]
                }
            },
            
            "estados_pedidos": {
                "labels": ["Completado", "En Proceso", "Pendiente", "Cancelado"],
                "datasets": [
                    {
                        "label": "Distribución de Estados",
                        "data": [8, 3, 2, 1],
                        "backgroundColor": [
                            "rgba(34, 197, 94, 0.8)",   # Verde para completado
                            "rgba(59, 130, 246, 0.8)",  # Azul para en proceso
                            "rgba(245, 158, 11, 0.8)",  # Naranja para pendiente
                            "rgba(239, 68, 68, 0.8)"    # Rojo para cancelado
                        ],
                        "borderColor": [
                            "rgba(34, 197, 94, 1)",
                            "rgba(59, 130, 246, 1)",
                            "rgba(245, 158, 11, 1)",
                            "rgba(239, 68, 68, 1)"
                        ],
                        "borderWidth": 2
                    }
                ],
                "chart_type": "pie",
                "title": "Distribución de Estados de Pedidos",
                "description": "Porcentaje de pedidos por estado en el período",
                "additional_data": {
                    "total_pedidos": 14,
                    "porcentajes": [57.1, 21.4, 14.3, 7.1],
                    "valores_monetarios": [425.20, 68.40, 25.90, 6.50]
                }
            },
            
            "clientes_activos": {
                "labels": ["Nuevos", "Recurrentes", "VIP", "Inactivos"],
                "datasets": [
                    {
                        "label": "Segmentación de Clientes",
                        "data": [12, 28, 8, 15],
                        "backgroundColor": [
                            "rgba(16, 185, 129, 0.8)",
                            "rgba(59, 130, 246, 0.8)",
                            "rgba(168, 85, 247, 0.8)",
                            "rgba(156, 163, 175, 0.8)"
                        ]
                    }
                ],
                "chart_type": "doughnut",
                "title": "Segmentación de Clientes",
                "description": "Distribución de la base de clientes por tipo"
            },
            
            "tendencia_semanal": {
                "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
                "datasets": [
                    {
                        "label": "Pedidos por Día",
                        "data": [2, 3, 1, 4, 2, 1, 1],
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        "borderColor": "rgba(34, 197, 94, 1)",
                        "borderWidth": 2,
                        "fill": True,
                        "tension": 0.4
                    }
                ],
                "chart_type": "area",
                "title": "Tendencia Semanal de Pedidos",
                "description": "Distribución de pedidos por día de la semana"
            }
        }
        
        return chart_data_catalog.get(chart_type, FallbackDataProvider._get_default_chart_data())
    
    @staticmethod
    def _get_default_chart_data() -> Dict[str, Any]:
        """Retorna datos por defecto cuando no se encuentra el tipo de gráfico"""
        return {
            "labels": ["Sin datos"],
            "datasets": [{
                "label": "N/A", 
                "data": [0],
                "backgroundColor": "rgba(156, 163, 175, 0.5)",
                "borderColor": "rgba(156, 163, 175, 1)"
            }],
            "chart_type": "line",
            "title": "Datos no disponibles",
            "description": "No se pudieron cargar los datos para este tipo de gráfico"
        }
    
    @staticmethod
    def get_available_chart_types() -> list:
        """Retorna la lista de tipos de gráficos disponibles"""
        return [
            "ventas_diarias",
            "ventas_mensuales", 
            "productos_vendidos",
            "estados_pedidos",
            "clientes_activos",
            "tendencia_semanal"
        ]
    
    @staticmethod
    def get_demo_period() -> Dict[str, str]:
        """Retorna el período de demostración utilizado en los datos de fallback"""
        return {
            "fecha_inicio": "2025-07-01",
            "fecha_fin": "2025-07-31",
            "descripcion": "Período de demostración - Julio 2025"
        }
    
    @staticmethod
    def is_demo_mode() -> bool:
        """Indica si los datos mostrados son de demostración"""
        return True
