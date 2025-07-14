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
            'success': True,
            'source': 'fallback',
            'data': {
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
            },
            'periodo': {
                'actual': {
                    'fecha_inicio': '2025-07-01',
                    'fecha_fin': '2025-07-31',
                    'dias': 31
                }
            },
            'mensaje': 'Datos de fallback cargados (Sin conexión a API)'
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
                "title": "Evolución de Ventas Diarias (Datos de Prueba)",
                "description": "Análisis de ingresos y volumen de transacciones por día",
                "source": "fallback",
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
                "title": "Evolución de Ventas Mensuales (Datos de Prueba)",
                "description": "Análisis de tendencias y estacionalidad de ingresos",
                "source": "fallback",
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
                "labels": [
                    "Frescura Familiar - 5kg",
                    "Doble Dulzura - 2kg", 
                    "Delicia Andina - 1kg"
                ],
                "datasets": [
                    {
                        "label": "Ingresos Generados ($)",
                        "data": [416.00, 161.00, 143.00],
                        "backgroundColor": [
                            "#10B981",
                            "#059669", 
                            "#047857",
                            "#065F46",
                            "#064E3B",
                            "#3B82F6",
                            "#2563EB",
                            "#1D4ED8",
                            "#1E40AF",
                            "#1E3A8A"
                        ],
                        "borderColor": "#374151",
                        "borderWidth": 1,
                        "yAxisID": "y"
                    }
                ],
                "chart_type": "horizontal_bar",
                "title": "Top 10 Productos por Ingresos (Datos de Prueba)",
                "description": "Ranking de productos más rentables del período",
                "source": "fallback",
                "additional_data": {
                    "unidades_vendidas": [8, 7, 11],
                    "pedidos_incluidos": [6, 6, 9],
                    "cantidad_promedio_por_pedido": [1.3, 1.2, 1.2]
                },
                "chart_config": {
                    "indexAxis": "y",
                    "responsive": True,
                    "plugins": {
                        "legend": {
                            "display": False
                        },
                        "tooltip": {
                            "callbacks": {
                                "afterLabel": "Mostrar unidades vendidas y pedidos"
                            }
                        }
                    }
                }
            },
            
            "estados_pedidos": {
                "labels": [
                    "Pendientes de Procesar",
                    "Confirmado", 
                    "Cancelados",
                    "En Camino al Cliente",
                    "Preparando",
                    "Entregados Exitosamente"
                ],
                "datasets": [
                    {
                        "label": "Pedidos por Estado",
                        "data": [4, 3, 2, 2, 2, 1],
                        "backgroundColor": [
                            "#FCD34D",
                            "#60A5FA",
                            "#34D399",
                            "#10B981", 
                            "#F87171",
                            "#F59E0B"
                        ],
                        "borderColor": "#FFFFFF",
                        "borderWidth": 2,
                        "hoverOffset": 4
                    }
                ],
                "chart_type": "doughnut",
                "title": "Distribución de Estados de Pedidos (Datos de Prueba)",
                "description": "Análisis del flujo operativo y eficiencia de entrega",
                "source": "fallback",
                "additional_data": {
                    "porcentajes": [28.6, 21.4, 14.3, 14.3, 14.3, 7.1],
                    "estados_originales": [
                        "pendiente",
                        "confirmado", 
                        "cancelado",
                        "en_camino",
                        "preparando",
                        "entregado"
                    ],
                    "total_pedidos": 14
                },
                "chart_config": {
                    "cutout": "60%",
                    "plugins": {
                        "legend": {
                            "position": "right",
                            "labels": {
                                "usePointStyle": True
                            }
                        },
                        "tooltip": {
                            "callbacks": {
                                "label": "Mostrar cantidad y porcentaje"
                            }
                        }
                    }
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
