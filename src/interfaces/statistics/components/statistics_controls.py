"""
Componente de controles para la interfaz de estadísticas
"""
import customtkinter as ctk
from tkinter import StringVar
from ..icon_manager import icon_manager


class StatisticsControls(ctk.CTkFrame):
    """Componente para los controles de filtros y acciones"""
    
    def __init__(self, parent, on_period_changed=None, on_refresh=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_period_changed = on_period_changed
        self.on_refresh = on_refresh
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de controles"""
        try:
            # Título principal con icono
            self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.title_frame.pack(fill="x", pady=(20, 20))
            
            # Frame para icono y título
            self.title_icon_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
            self.title_icon_frame.pack(side="left")
            
            # Cargar icono de estadísticas
            try:
                stats_icon = icon_manager.load_icon("statistics", size=(32, 32))
                self.icon_label = ctk.CTkLabel(
                    self.title_icon_frame,
                    image=stats_icon,
                    text=""
                )
                self.icon_label.pack(side="left", padx=(0, 12))
            except Exception as e:
                print(f"No se pudo cargar el icono de estadísticas: {e}")
            
            # Título con paleta profesional
            self.title_label = ctk.CTkLabel(
                self.title_icon_frame,
                text="Estadísticas de Ventas",
                font=("Arial", 28, "bold"),
                text_color="#16A34A"  # Verde principal mantenido para el título
            )
            self.title_label.pack(side="left")
            
            # Frame para controles
            self.controls_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
            self.controls_frame.pack(side="right")
            
            # Label del período
            self.period_label = ctk.CTkLabel(
                self.controls_frame,
                text="Período:",
                font=("Arial", 14),
                text_color="#374151"  # Gris más suave
            )
            self.period_label.pack(side="left", padx=(0, 10))
            
            # Selector de período con azul profesional y opciones mejoradas
            self.periodo_var = StringVar(value="Mes actual")
            self.periodo_selector = ctk.CTkOptionMenu(
                self.controls_frame,
                variable=self.periodo_var,
                values=[
                    "Mes actual",
                    "Último mes", 
                    "Últimos 7 días",
                    "Últimos 30 días",
                    "Trimestre actual",
                    "Últimos 3 meses",
                    "Año actual"
                ],
                command=self._on_period_changed,
                width=170,
                fg_color="#2563EB",  # Azul profesional
                button_color="#1D4ED8",
                button_hover_color="#1E40AF"
            )
            self.periodo_selector.pack(side="left", padx=(0, 10))
            
            # Botón de actualizar con verde principal
            self.btn_refresh = ctk.CTkButton(
                self.controls_frame,
                text="Actualizar",
                command=self._on_refresh,
                width=120,
                height=35,
                fg_color="#16A34A",  # Verde principal
                hover_color="#15803D",
                font=("Arial", 14),
                corner_radius=12
            )
            self.btn_refresh.pack(side="left")
            
        except Exception as e:
            print(f"Error al configurar controles: {str(e)}")
    
    def _on_period_changed(self, value):
        """Maneja el cambio de período"""
        if self.on_period_changed:
            self.on_period_changed(value)
    
    def _on_refresh(self):
        """Maneja el clic del botón actualizar"""
        if self.on_refresh:
            self.on_refresh()
    
    def get_selected_period(self):
        """Obtiene el período seleccionado"""
        return self.periodo_var.get()
    
    def set_loading_state(self, is_loading=True):
        """Establece el estado de carga"""
        if is_loading:
            self.btn_refresh.configure(state="disabled", text="Cargando...")
        else:
            self.btn_refresh.configure(state="normal", text="Actualizar")
    
    def set_period(self, period):
        """Establece el período seleccionado programáticamente"""
        self.periodo_var.set(period)
    
    def get_selected_period_text(self):
        """Obtiene el texto del período seleccionado para mostrar en títulos"""
        return self.periodo_var.get()
