"""
Gestor principal de gráficos estadísticos modular
"""
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from .chart_cards import ChartCardsGrid
from .chart_detail import ChartDetailModal
from ..statistics_service import StatisticsService


class ChartsManager(ctk.CTkFrame):
    """Gestor principal de gráficos estadísticos con vista en cuadrícula y detalle expandible"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.statistics_service = StatisticsService()
        self.current_period = None
        self.charts_data = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz principal de gráficos"""
        try:
            # Título de la sección más compacto
            self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.title_frame.pack(fill="x", pady=(10, 15))
            
            # Icono y título más compactos
            self.title_label = ctk.CTkLabel(
                self.title_frame,
                text="📊 Análisis Visual",
                font=("Arial", 18, "bold"),
                text_color="#16A34A"
            )
            self.title_label.pack(side="left")
            
            # Estado más discreto
            self.status_label = ctk.CTkLabel(
                self.title_frame,
                text="✅ Actualizado",
                font=("Arial", 11),
                text_color="#6B7280"
            )
            self.status_label.pack(side="right")
            
            # Grid de tarjetas de gráficos (sin controles redundantes)
            self.charts_grid = ChartCardsGrid(
                self,
                on_chart_expand=self.expand_chart
            )
            self.charts_grid.pack(fill="both", expand=True, pady=(0, 10))
            
            # Modal para vista detallada
            self.detail_modal = None
            
        except Exception as e:
            print(f"Error al configurar ChartsManager: {str(e)}")
    
    def update_period(self, fecha_inicio: str, fecha_fin: str):
        """Actualiza el período y recarga todos los gráficos"""
        self.current_period = (fecha_inicio, fecha_fin)
        print(f"📊 Actualizando gráficos para período: {fecha_inicio} a {fecha_fin}")
        
        # ¡IMPORTANTE! Limpiar caché de datos para forzar recarga desde la API
        self.charts_data.clear()
        print(f"🧹 Caché de gráficos limpiado - se recargarán desde la API")
        
        # Mostrar estado de carga
        self.set_loading_status(True)
        
        # Cargar datos de todos los tipos de gráficos
        chart_types = ["productos_vendidos", "ventas_diarias", "ventas_mensuales", "estados_pedidos"]
        for chart_type in chart_types:
            self.load_chart_data(chart_type, fecha_inicio, fecha_fin)
    
    def load_chart_data(self, chart_type: str, fecha_inicio: str, fecha_fin: str):
        """Carga los datos del gráfico especificado"""
        try:
            # Obtener datos desde el servicio
            result = self.statistics_service.fetch_chart_data(
                chart_type, fecha_inicio, fecha_fin
            )
            
            if result.get('success', True):
                self.charts_data[chart_type] = result.get('data', {})
                
                # Actualizar el grid con los nuevos datos
                self.charts_grid.update_chart_preview(chart_type, result.get('data', {}))
                
                # Actualizar estado
                self.set_loading_status(False, "✅ Datos actualizados")
                
            else:
                print(f"❌ Error al cargar gráfico {chart_type}: {result.get('error', 'Error desconocido')}")
                self.set_loading_status(False, "⚠️ Error al cargar datos")
                
        except Exception as e:
            print(f"💥 Error al cargar datos del gráfico: {str(e)}")
            self.set_loading_status(False, "❌ Error de conexión")
    
    def expand_chart(self, chart_type: str):
        """Expande un gráfico en vista detallada"""
        try:
            if chart_type in self.charts_data:
                # Crear y mostrar modal de detalle
                if self.detail_modal:
                    self.detail_modal.destroy()
                
                self.detail_modal = ChartDetailModal(
                    self.winfo_toplevel(),
                    chart_type=chart_type,
                    chart_data=self.charts_data[chart_type],
                    period=self.current_period
                )
                self.detail_modal.show()
            else:
                print(f"⚠️ No hay datos disponibles para el gráfico: {chart_type}")
                
        except Exception as e:
            print(f"Error al expandir gráfico: {str(e)}")
    
    def set_loading_status(self, is_loading: bool, message: str = None):
        """Actualiza el estado de carga de forma más sutil"""
        if is_loading:
            self.status_label.configure(
                text="🔄 Cargando...",
                text_color="#F59E0B"
            )
        else:
            if message:
                color = "#16A34A" if "✅" in message else "#DC2626" if "❌" in message else "#F59E0B"
                self.status_label.configure(
                    text=message,
                    text_color=color
                )
            else:
                self.status_label.configure(
                    text="✅ Actualizado",
                    text_color="#6B7280"
                )
    
    def get_chart_types_info(self) -> Dict[str, Dict[str, str]]:
        """Retorna información sobre los tipos de gráficos disponibles"""
        return {
            "ventas_diarias": {
                "title": "Ventas Diarias",
                "description": "Tendencia de ventas por día",
                "icon": "📈",
                "color": "#16A34A"
            },
            "ventas_mensuales": {
                "title": "Ventas Mensuales", 
                "description": "Comparativa mensual de ventas",
                "icon": "📊",
                "color": "#2563EB"
            },
            "productos_vendidos": {
                "title": "Productos Más Vendidos",
                "description": "Ranking de productos por ventas",
                "icon": "🏆",
                "color": "#F59E0B"
            },
            "estados_pedidos": {
                "title": "Estados de Pedidos",
                "description": "Distribución por estado",
                "icon": "📋",
                "color": "#7C3AED"
            }
        }
