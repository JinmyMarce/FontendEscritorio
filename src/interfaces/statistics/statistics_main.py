"""
Interfaz principal de estadísticas de venta            # Placeholder para futuras funcionalidades
            self.placeholder_label = ctk.CTkLabel(
                self.content_frame,
                text="📈 Próximamente: Gráficos detallados de ventas\n\n"
                     "Aquí se mostrarán gráficos interactivos con:\n"
                     "• Tendencias de ventas por período\n"
                     "• Productos más vendidos\n"
                     "• Análisis por categorías\n"
                     "• Comparativas entre períodos\n"
                     "• Análisis de rendimiento\n\n"
                     "✨ Interfaz modularizada con colores mejorados",
                font=("Arial", 16),
                text_color="#16A34A",
                justify="center"
            )ular
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from .components.statistics_controls import StatisticsControls
from .components.kpi_grid import KPIGrid
from .statistics_service import StatisticsService


class EstadisticasVentas(ctk.CTkFrame):
    """Interfaz principal de estadísticas usando componentes modulares"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)
        self.parent = parent
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Servicio de datos
        self.statistics_service = StatisticsService()
        
        try:
            self.setup_ui()
            self.cargar_datos_iniciales()
        except Exception as e:
            print(f"Error al inicializar EstadisticasVentas: {str(e)}")
            messagebox.showerror("Error", f"Error al inicializar estadísticas: {str(e)}")
    
    def setup_ui(self):
        """Configura la interfaz de usuario usando componentes"""
        try:
            # Componente de controles
            self.controls = StatisticsControls(
                self,
                on_period_changed=self.on_period_changed,
                on_refresh=self.actualizar_datos
            )
            self.controls.pack(fill="x", pady=(0, 20))
            
            # Componente de grid de KPIs
            self.kpi_grid = KPIGrid(self)
            self.kpi_grid.pack(fill="x", pady=(0, 30))
            
            # NUEVO: Componente de gráficos estadísticos
            from .components.charts_manager import ChartsManager
            self.charts_manager = ChartsManager(self)
            self.charts_manager.pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Error al configurar la interfaz: {str(e)}")
            self.show_error_interface()
    
    def show_error_interface(self):
        """Muestra una interfaz mínima en caso de error"""
        error_label = ctk.CTkLabel(
            self,
            text="Error al cargar la interfaz de estadísticas",
            font=("Arial", 16),
            text_color="#DC3545"
        )
        error_label.pack(expand=True)
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales"""
        self.actualizar_datos()
    
    def on_period_changed(self, value):
        """Se ejecuta cuando cambia el período seleccionado"""
        self.actualizar_datos()
    
    def actualizar_datos(self):
        """Actualiza los datos de los KPIs y gráficos usando el servicio"""
        try:
            # Establecer estado de carga
            self.controls.set_loading_state(True)
            self.kpi_grid.set_loading_state()
            
            # Obtener rango de fechas
            periodo = self.controls.get_selected_period()
            fecha_inicio, fecha_fin = self.statistics_service.get_date_range(periodo)
            
            # Hacer petición a la API para KPIs
            self.cargar_kpis(fecha_inicio, fecha_fin)
            
            # Actualizar gráficos si existe el componente
            if hasattr(self, 'charts_manager'):
                self.charts_manager.update_period(fecha_inicio, fecha_fin)
            
        except Exception as e:
            print(f"Error al actualizar datos: {str(e)}")
        finally:
            # Restaurar estado normal
            self.controls.set_loading_state(False)
    
    def cargar_kpis(self, fecha_inicio, fecha_fin):
        """Carga los KPIs desde la API usando el servicio"""
        try:
            # Hacer petición usando el servicio
            result = self.statistics_service.fetch_kpis(fecha_inicio, fecha_fin)
            
            if result['success']:
                # Actualizar KPIs con datos reales
                self.kpi_grid.update_kpi_data(result['data'])
            else:
                print(f"Error en API: {result.get('error', 'Error desconocido')}")
                # Usar datos de fallback
                fallback_data = self.statistics_service.get_fallback_data()
                self.kpi_grid.update_kpi_data(fallback_data)
                
        except Exception as e:
            print(f"Error al cargar KPIs: {str(e)}")
            # Usar datos de fallback en caso de error
            fallback_data = self.statistics_service.get_fallback_data()
            self.kpi_grid.update_kpi_data(fallback_data)
    
    def get_kpi_card(self, kpi_key):
        """Obtiene una tarjeta KPI específica (para extensiones futuras)"""
        return self.kpi_grid.get_kpi_card(kpi_key)
    
    def add_custom_component(self, component, **pack_options):
        """Permite agregar componentes personalizados (para extensiones futuras)"""
        try:
            # Remover placeholder si existe
            if hasattr(self, 'placeholder_label'):
                self.placeholder_label.destroy()
            
            # Agregar nuevo componente
            component.pack(**pack_options)
        except Exception as e:
            print(f"Error al agregar componente personalizado: {str(e)}")


def main():
    """Función principal para pruebas"""
    import customtkinter as ctk
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    root = ctk.CTk()
    root.title("Estadísticas de Ventas - Modular")
    root.geometry("1200x800")
    
    app = EstadisticasVentas(root)
    
    root.mainloop()


if __name__ == "__main__":
    main()
