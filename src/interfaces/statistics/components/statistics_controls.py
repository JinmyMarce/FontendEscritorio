"""
Componente de control            # Título con icono mejorado
            self.title_label = ctk.CTkLabel(
                self.title_frame,
                text="📊 Análisis de Ventas",
                font=("Arial", 28, "bold"),
                text_color="#16A34A"  # Verde principal
            ) la interfaz de estadísticas
"""
import customtkinter as ctk
from tkinter import StringVar


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
            # Título principal
            self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.title_frame.pack(fill="x", pady=(20, 20))
            
            # Título
            self.title_label = ctk.CTkLabel(
                self.title_frame,
                text="� Estadísticas de Ventas",
                font=("Arial", 28, "bold"),
                text_color="#1A365D"
            )
            self.title_label.pack(side="left")
            
            # Frame para controles
            self.controls_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
            self.controls_frame.pack(side="right")
            
            # Label del período
            self.period_label = ctk.CTkLabel(
                self.controls_frame,
                text="Período:",
                font=("Arial", 14)
            )
            self.period_label.pack(side="left", padx=(0, 10))
            
            # Selector de período con colores verde
            self.periodo_var = StringVar(value="Último mes")
            self.periodo_selector = ctk.CTkOptionMenu(
                self.controls_frame,
                variable=self.periodo_var,
                values=["Último mes", "Últimos 7 días", "Últimos 3 meses", "Año actual"],
                command=self._on_period_changed,
                width=150,
                fg_color="#16A34A",
                button_color="#059669",
                button_hover_color="#047857"
            )
            self.periodo_selector.pack(side="left", padx=(0, 10))
            
            # Botón de actualizar con verde suave
            self.btn_refresh = ctk.CTkButton(
                self.controls_frame,
                text="Actualizar",
                command=self._on_refresh,
                width=120,
                height=35,
                fg_color="#10B981",
                hover_color="#059669",
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
