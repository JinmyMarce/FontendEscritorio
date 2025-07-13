"""
Componente KPI Card para mostrar métricas individuales
"""
import customtkinter as ctk


class KPICard(ctk.CTkFrame):
    """Componente reutilizable para mostrar un KPI individual"""
    
    def __init__(self, parent, title, icon, color, **kwargs):
        super().__init__(
            parent,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E9ECEF",
            **kwargs
        )
        
        self.title = title
        self.icon = icon
        self.color = color
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del componente KPI"""
        try:
            # Frame superior con icono y título
            self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            # Icono
            self.icon_label = ctk.CTkLabel(
                self.header_frame,
                text=self.icon,
                font=("Arial", 24)
            )
            self.icon_label.pack(side="left")
            
            # Título
            self.title_label = ctk.CTkLabel(
                self.header_frame,
                text=self.title,
                font=("Arial", 14, "bold"),
                text_color="#495057"
            )
            self.title_label.pack(side="right")
            
            # Valor principal
            self.value_label = ctk.CTkLabel(
                self,
                text="Cargando...",
                font=("Arial", 28, "bold"),
                text_color=self.color
            )
            self.value_label.pack(pady=(0, 10))
            
            # Frame para crecimiento
            self.growth_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.growth_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            self.growth_label = ctk.CTkLabel(
                self.growth_frame,
                text="",
                font=("Arial", 12),
                text_color="#6C757D"
            )
            self.growth_label.pack()
            
        except Exception as e:
            print(f"Error al configurar KPI card: {str(e)}")
    
    def update_value(self, value, format_type='number'):
        """Actualiza el valor mostrado en el KPI"""
        try:
            if format_type == 'currency':
                formatted_value = f"S/. {value:,.2f}"
            elif format_type == 'percentage':
                formatted_value = f"{value:.1f}%"
            else:
                formatted_value = f"{value:,}"
            
            self.value_label.configure(text=formatted_value)
        except Exception as e:
            print(f"Error al actualizar valor KPI: {str(e)}")
            self.value_label.configure(text="Error")
    
    def update_growth(self, growth_value):
        """Actualiza el indicador de crecimiento"""
        try:
            if growth_value > 0:
                growth_text = f"↗ +{growth_value}% vs período anterior"
                growth_color = "#28A745"
            elif growth_value < 0:
                growth_text = f"↘ {growth_value}% vs período anterior"
                growth_color = "#DC3545"
            else:
                growth_text = "→ Sin cambios vs período anterior"
                growth_color = "#6C757D"
            
            self.growth_label.configure(
                text=growth_text,
                text_color=growth_color
            )
        except Exception as e:
            print(f"Error al actualizar crecimiento: {str(e)}")
    
    def clear_growth(self):
        """Limpia el indicador de crecimiento"""
        self.growth_label.configure(text="")
    
    def set_loading(self):
        """Muestra estado de carga"""
        self.value_label.configure(text="Cargando...")
        self.clear_growth()
    
    def set_error(self, message="Sin datos"):
        """Muestra estado de error"""
        self.value_label.configure(text=message)
        self.clear_growth()
