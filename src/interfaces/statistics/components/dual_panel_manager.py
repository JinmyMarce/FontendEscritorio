"""
Manager principal con dos paneles: Análisis Visual y Generar Reportes
"""
import customtkinter as ctk
from typing import Dict, Any, Optional, Tuple
from .chart_navigation import ChartNavigation
from .analysis_panel import AnalysisPanel
from .reports_panel import ReportsPanel
from .chart_detail import ChartDetailModal
from ..statistics_service import StatisticsService


class DualPanelManager(ctk.CTkFrame):
    """Manager principal con dos paneles side-by-side"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.statistics_service = StatisticsService()
        self.current_period = None
        self.charts_data = {}
        self.detail_modal = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz con dos paneles"""
        try:
            # Container principal para los dos paneles
            self.panels_container = ctk.CTkFrame(self, fg_color="transparent")
            self.panels_container.pack(fill="both", expand=True)
            
            # Configurar grid para dos columnas
            self.panels_container.grid_columnconfigure(0, weight=3)  # Panel izquierdo más grande
            self.panels_container.grid_columnconfigure(1, weight=2)  # Panel derecho más pequeño
            self.panels_container.grid_rowconfigure(0, weight=1)
            
            # PANEL IZQUIERDO: Análisis Visual
            self.create_analysis_section()
            
            # PANEL DERECHO: Generar Reportes
            self.create_reports_section()
            
        except Exception as e:
            print(f"Error al configurar DualPanelManager: {str(e)}")
    
    def create_analysis_section(self):
        """Crea la sección de análisis visual"""
        # Frame principal del análisis
        self.analysis_frame = ctk.CTkFrame(
            self.panels_container,
            fg_color="transparent"
        )
        self.analysis_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        
        # Navegación de gráficos
        self.chart_navigation = ChartNavigation(
            self.analysis_frame,
            on_chart_selected=self.on_chart_type_changed
        )
        self.chart_navigation.pack(fill="x", pady=(0, 15))
        
        # Panel de análisis principal
        self.analysis_panel = AnalysisPanel(
            self.analysis_frame,
            on_detail_view=self.show_detail_modal
        )
        self.analysis_panel.pack(fill="both", expand=True)
    
    def create_reports_section(self):
        """Crea la sección de reportes"""
        # Panel de reportes
        self.reports_panel = ReportsPanel(self.panels_container)
        self.reports_panel.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
    
    def update_period(self, fecha_inicio: str, fecha_fin: str):
        """Actualiza el período y recarga los datos"""
        self.current_period = (fecha_inicio, fecha_fin)
        print(f"📊 Actualizando análisis dual para período: {fecha_inicio} a {fecha_fin}")
        
        # Mostrar estado de carga
        self.analysis_panel.set_loading_state(True)
        
        # Cargar datos del gráfico actual
        current_chart = self.chart_navigation.get_selected_chart()
        self.load_chart_data(current_chart, fecha_inicio, fecha_fin)
    
    def on_chart_type_changed(self, chart_type: str):
        """Maneja el cambio de tipo de gráfico desde la navegación"""
        print(f"📈 Cambiando a gráfico: {chart_type}")
        
        if self.current_period:
            fecha_inicio, fecha_fin = self.current_period
            self.load_chart_data(chart_type, fecha_inicio, fecha_fin)
        else:
            # Si no hay período, mostrar placeholder
            self.analysis_panel.show_placeholder()
    
    def load_chart_data(self, chart_type: str, fecha_inicio: str, fecha_fin: str):
        """Carga los datos del gráfico especificado"""
        try:
            # Mostrar estado de carga
            self.analysis_panel.set_loading_state(True)
            
            # Verificar si ya tenemos los datos en caché
            if chart_type in self.charts_data:
                print(f"📊 Usando datos en caché para: {chart_type}")
                self.analysis_panel.update_chart(chart_type, self.charts_data[chart_type])
                return
            
            # Obtener datos desde el servicio
            result = self.statistics_service.fetch_chart_data(
                chart_type, fecha_inicio, fecha_fin
            )
            
            if result.get('success', True):
                chart_data = result.get('data', {})
                self.charts_data[chart_type] = chart_data
                
                # Actualizar el panel de análisis
                self.analysis_panel.update_chart(chart_type, chart_data)
                
                print(f"✅ Gráfico {chart_type} cargado exitosamente")
                
            else:
                print(f"❌ Error al cargar gráfico {chart_type}: {result.get('error', 'Error desconocido')}")
                # Usar datos de fallback
                fallback_data = self.get_fallback_chart_data(chart_type)
                self.charts_data[chart_type] = fallback_data
                self.analysis_panel.update_chart(chart_type, fallback_data)
                
        except Exception as e:
            print(f"💥 Error al cargar datos del gráfico: {str(e)}")
            # Usar datos de fallback en caso de error
            fallback_data = self.get_fallback_chart_data(chart_type)
            self.charts_data[chart_type] = fallback_data
            self.analysis_panel.update_chart(chart_type, fallback_data)
    
    def get_fallback_chart_data(self, chart_type: str) -> Dict[str, Any]:
        """Retorna datos de fallback para el tipo de gráfico"""
        fallback_data = {
            "ventas_diarias": {
                "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
                "datasets": [{
                    "label": "Ventas Diarias",
                    "data": [850, 1200, 980, 1400, 1650, 1900, 1300],
                    "borderColor": "#16A34A",
                    "backgroundColor": "#16A34A"
                }]
            },
            "ventas_mensuales": {
                "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
                "datasets": [{
                    "label": "Ventas 2024",
                    "data": [18000, 22000, 19500, 26000, 28500, 31000],
                    "borderColor": "#2563EB",
                    "backgroundColor": "#2563EB"
                }]
            },
            "productos_vendidos": {
                "labels": ["Producto A", "Producto B", "Producto C", "Producto D", "Producto E"],
                "datasets": [{
                    "label": "Unidades Vendidas",
                    "data": [245, 189, 156, 134, 98],
                    "borderColor": "#F59E0B",
                    "backgroundColor": "#F59E0B"
                }]
            },
            "estados_pedidos": {
                "labels": ["Completado", "Pendiente", "En Proceso", "Cancelado"],
                "datasets": [{
                    "label": "Estados",
                    "data": [68, 18, 10, 4],
                    "backgroundColor": ["#16A34A", "#F59E0B", "#2563EB", "#DC2626"]
                }]
            }
        }
        
        return fallback_data.get(chart_type, {
            "labels": ["Sin datos"],
            "datasets": [{"label": "N/A", "data": [0]}]
        })
    
    def show_detail_modal(self, chart_type: str, chart_data: Dict[str, Any]):
        """Muestra el modal de vista detallada"""
        try:
            if self.detail_modal:
                self.detail_modal.destroy()
            
            self.detail_modal = ChartDetailModal(
                self.winfo_toplevel(),
                chart_type=chart_type,
                chart_data=chart_data,
                period=self.current_period
            )
            self.detail_modal.show()
            
        except Exception as e:
            print(f"Error al mostrar modal de detalle: {str(e)}")
    
    def preload_all_charts(self, fecha_inicio: str, fecha_fin: str):
        """Precarga todos los tipos de gráficos para mejor UX"""
        chart_types = ["ventas_diarias", "ventas_mensuales", "productos_vendidos", "estados_pedidos"]
        
        for chart_type in chart_types:
            if chart_type not in self.charts_data:
                # Cargar en background
                try:
                    result = self.statistics_service.fetch_chart_data(
                        chart_type, fecha_inicio, fecha_fin
                    )
                    
                    if result.get('success', True):
                        self.charts_data[chart_type] = result.get('data', {})
                    else:
                        self.charts_data[chart_type] = self.get_fallback_chart_data(chart_type)
                        
                except Exception as e:
                    print(f"Error precargando {chart_type}: {str(e)}")
                    self.charts_data[chart_type] = self.get_fallback_chart_data(chart_type)
    
    def get_current_chart_type(self) -> str:
        """Retorna el tipo de gráfico actualmente seleccionado"""
        return self.chart_navigation.get_selected_chart()
    
    def refresh_all_data(self):
        """Refresca todos los datos"""
        if self.current_period:
            fecha_inicio, fecha_fin = self.current_period
            self.charts_data.clear()  # Limpiar caché
            self.load_chart_data(self.get_current_chart_type(), fecha_inicio, fecha_fin)
            self.preload_all_charts(fecha_inicio, fecha_fin)
