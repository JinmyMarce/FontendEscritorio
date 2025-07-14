"""
Componente KPI Card para mostrar métricas individuales
"""
import customtkinter as ctk
from ..icon_manager import icon_manager


class KPICard(ctk.CTkFrame):
    """Componente reutilizable para mostrar un KPI individual"""
    
    def __init__(self, parent, title, icon_name, color, **kwargs):
        super().__init__(
            parent,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=2,
            border_color="#F1F5F9",
            **kwargs
        )
        
        self.title = title
        self.icon_name = icon_name  # Cambiar de icon a icon_name
        self.color = color
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del componente KPI"""
        try:
            # Frame superior con icono y título
            self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.header_frame.pack(fill="x", padx=25, pady=(25, 15))
            
            # Icono usando el gestor de iconos
            try:
                icon_image = icon_manager.load_icon(self.icon_name, size=(28, 28), color=self.color)
                self.icon_label = ctk.CTkLabel(
                    self.header_frame,
                    text="",
                    image=icon_image
                )
            except Exception as e:
                print(f"Error al cargar icono {self.icon_name}: {str(e)}")
                # Fallback a texto simple
                icon_text = self._get_fallback_icon_text()
                self.icon_label = ctk.CTkLabel(
                    self.header_frame,
                    text=icon_text,
                    font=("Arial", 24),
                    text_color=self.color
                )
            
            self.icon_label.pack(side="left")
            
            # Título
            self.title_label = ctk.CTkLabel(
                self.header_frame,
                text=self.title,
                font=("Arial", 15, "bold"),
                text_color="#374151"
            )
            self.title_label.pack(side="right")
            
            # Valor principal
            self.value_label = ctk.CTkLabel(
                self,
                text="Cargando...",
                font=("Arial", 32, "bold"),
                text_color=self.color
            )
            self.value_label.pack(pady=(5, 15))
            
            # Frame para crecimiento
            self.growth_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.growth_frame.pack(fill="x", padx=25, pady=(0, 25))
            
            self.growth_label = ctk.CTkLabel(
                self.growth_frame,
                text="",
                font=("Arial", 13),
                text_color="#6B7280"
            )
            self.growth_label.pack()
            
        except Exception as e:
            print(f"Error al configurar KPI card: {str(e)}")
    
    def update_value(self, value, format_type='number'):
        """Actualiza el valor mostrado en el KPI"""
        try:
            # Convertir valor a número si viene como string
            if isinstance(value, str):
                try:
                    value = float(value)
                except ValueError:
                    value = 0
            
            if format_type == 'currency':
                formatted_value = f"S/. {value:,.2f}"
            elif format_type == 'percentage':
                formatted_value = f"{value:.1f}%"
            else:
                formatted_value = f"{int(value):,}"
            
            self.value_label.configure(text=formatted_value)
        except Exception as e:
            print(f"Error al actualizar valor KPI: {str(e)}")
            self.value_label.configure(text="Error")
    
    def update_growth(self, growth_data):
        """Actualiza el indicador de crecimiento con datos más detallados"""
        try:
            if isinstance(growth_data, dict):
                # Nueva estructura con más información
                porcentaje = growth_data.get('porcentaje', 0)
                tendencia = growth_data.get('tendencia', 'neutral')
                valor_anterior = growth_data.get('valor_anterior', 0)
                
                if porcentaje > 0:
                    # Formatear diferentes rangos de crecimiento
                    if porcentaje >= 1000:
                        growth_text = f"🚀 +{porcentaje:.0f}% vs período anterior"
                        growth_color = "#059669"  # Verde más intenso para crecimientos enormes
                    elif porcentaje >= 100:
                        growth_text = f"🔥 +{porcentaje:.0f}% vs período anterior"
                        growth_color = "#16A34A"  # Verde brillante
                    elif porcentaje >= 50:
                        growth_text = f"📈 +{porcentaje:.1f}% vs período anterior"
                        growth_color = "#22C55E"  # Verde normal
                    else:
                        growth_text = f"↗ +{porcentaje:.1f}% vs período anterior"
                        growth_color = "#22C55E"
                        
                elif porcentaje < 0:
                    if abs(porcentaje) >= 50:
                        growth_text = f"📉 {porcentaje:.1f}% vs período anterior"
                        growth_color = "#DC2626"  # Rojo más intenso
                    else:
                        growth_text = f"↘ {porcentaje:.1f}% vs período anterior"
                        growth_color = "#F87171"  # Rojo suave
                else:
                    growth_text = "→ Sin cambios vs período anterior"
                    growth_color = "#9CA3AF"  # Gris neutro
                    
            else:
                # Compatibilidad con estructura simple (número)
                growth_value = growth_data if isinstance(growth_data, (int, float)) else 0
                
                if growth_value > 0:
                    growth_text = f"↗ +{growth_value:.1f}% vs período anterior"
                    growth_color = "#22C55E"
                elif growth_value < 0:
                    growth_text = f"↘ {growth_value:.1f}% vs período anterior"
                    growth_color = "#F87171"
                else:
                    growth_text = "→ Sin cambios vs período anterior"
                    growth_color = "#9CA3AF"
            
            self.growth_label.configure(
                text=growth_text,
                text_color=growth_color
            )
        except Exception as e:
            print(f"Error al actualizar crecimiento: {str(e)}")
            self.growth_label.configure(
                text="Sin datos de comparación",
                text_color="#9CA3AF"
            )
    
    def update_context(self, context_data):
        """Actualiza con información contextual (para casos como conversion_rate)"""
        try:
            if isinstance(context_data, dict):
                descripcion = context_data.get('descripcion', '')
                if descripcion:
                    self.growth_label.configure(
                        text=descripcion,
                        text_color="#6B7280"
                    )
                else:
                    # Construir descripción desde los datos
                    carritos = context_data.get('carritos_creados', 0)
                    pedidos = context_data.get('pedidos_completados', 0)
                    if carritos > 0:
                        context_text = f"De {carritos} carritos, {pedidos} se convirtieron"
                        self.growth_label.configure(
                            text=context_text,
                            text_color="#6B7280"
                        )
        except Exception as e:
            print(f"Error al actualizar contexto: {str(e)}")
    
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
    
    def _get_fallback_icon_text(self):
        """Obtiene un icono de texto como respaldo"""
        icon_map = {
            'sales': '💰',
            'orders': '📦', 
            'target': '🎯',
            'conversion': '📈'
        }
        return icon_map.get(self.icon_name, '📊')
