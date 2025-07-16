"""
Navegación para los diferentes tipos de gráficos
"""
import customtkinter as ctk
from typing import Dict, Callable


class ChartNavigation(ctk.CTkFrame):
    """Barra de navegación para seleccionar tipos de gráficos"""
    
    def __init__(self, parent, on_chart_selected: Callable = None, **kwargs):
        super().__init__(
            parent, 
            fg_color="#E5F3E5",
            corner_radius=12,
            height=60,
            **kwargs
        )
        
        self.on_chart_selected = on_chart_selected
        self.current_selection = "productos_vendidos"  # Cambiar default a Top productos
        self.nav_buttons = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la navegación"""
        # Configurar para que no se redimensione
        self.pack_propagate(False)
        
        # Frame interno para centrar los botones
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(expand=True, fill="both", padx=15, pady=10)
        
        # Información de los tipos de gráficos (cambiado el orden)
        self.chart_types = {
            "productos_vendidos": {
                "title": "Top productos",
                "icon": "🏆",
                "color": "#F59E0B"
            },
            "ventas_diarias": {
                "title": "Ventas diarias",
                "icon": "�",
                "color": "#16A34A"
            },
            "ventas_mensuales": {
                "title": "Ventas mensuales",
                "icon": "📊", 
                "color": "#2563EB"
            },
            "estados_pedidos": {
                "title": "Estados de pedidos",
                "icon": "📋",
                "color": "#7C3AED"
            }
        }
        
        # Crear botones de navegación con mejor espaciado
        for i, (chart_type, info) in enumerate(self.chart_types.items()):
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"{info['icon']} {info['title']}",
                command=lambda ct=chart_type: self.select_chart(ct),
                width=170,
                height=40,
                font=("Arial", 12, "bold"),
                corner_radius=8,
                fg_color="#FFFFFF" if chart_type != self.current_selection else info['color'],
                hover_color="#F3F4F6" if chart_type != self.current_selection else self._darken_color(info['color']),
                text_color="#374151" if chart_type != self.current_selection else "#FFFFFF",
                border_width=2,
                border_color="#E5E7EB" if chart_type != self.current_selection else info['color']
            )
            
            btn.pack(side="left", padx=8)
            self.nav_buttons[chart_type] = btn
    
    def select_chart(self, chart_type: str):
        """Selecciona un tipo de gráfico"""
        if chart_type == self.current_selection:
            return
        
        # Actualizar botón anterior
        old_info = self.chart_types[self.current_selection]
        old_btn = self.nav_buttons[self.current_selection]
        old_btn.configure(
            fg_color="#FFFFFF",
            hover_color="#F3F4F6",
            text_color="#374151",
            border_color="#E5E7EB"
        )
        
        # Actualizar botón actual
        new_info = self.chart_types[chart_type]
        new_btn = self.nav_buttons[chart_type]
        new_btn.configure(
            fg_color=new_info['color'],
            hover_color=self._darken_color(new_info['color']),
            text_color="#FFFFFF",
            border_color=new_info['color']
        )
        
        self.current_selection = chart_type
        
        # Notificar el cambio
        if self.on_chart_selected:
            self.on_chart_selected(chart_type)
    
    def _darken_color(self, hex_color: str) -> str:
        """Oscurece un color hex"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darker_rgb = tuple(max(0, c - 30) for c in rgb)
            return '#{:02x}{:02x}{:02x}'.format(*darker_rgb)
        except:
            return "#115E3A"
    
    def get_selected_chart(self) -> str:
        """Retorna el tipo de gráfico seleccionado"""
        return self.current_selection
    
    def update_period_constraints(self, period_months: int):
        """Actualiza las restricciones de los botones basándose en el período seleccionado"""
        try:
            # Deshabilitar "Ventas mensuales" si el período es menor a 3 meses
            if "ventas_mensuales" in self.nav_buttons:
                button = self.nav_buttons["ventas_mensuales"]
                
                if period_months < 3:
                    # Deshabilitar botón
                    button.configure(
                        fg_color="#9CA3AF",  # Color gris
                        hover_color="#9CA3AF",
                        text_color="#6B7280",
                        border_color="#9CA3AF",
                        state="disabled"
                    )
                    
                    # Si estaba seleccionado, cambiar a "productos_vendidos"
                    if self.current_selection == "ventas_mensuales":
                        self.select_chart("productos_vendidos")
                        
                else:
                    # Rehabilitar botón con colores originales
                    chart_info = self.chart_types["ventas_mensuales"]
                    button.configure(
                        fg_color=chart_info['color'],
                        hover_color=self._darken_color(chart_info['color']),
                        text_color="#FFFFFF",
                        border_color=chart_info['color'],
                        state="normal"
                    )
            
            print(f"📊 Restricciones de período actualizadas: {period_months} meses")
            
        except Exception as e:
            print(f"Error al actualizar restricciones de período: {str(e)}")
    
    def _calculate_months_difference(self, start_date: str, end_date: str) -> int:
        """Calcula la diferencia en meses entre dos fechas"""
        try:
            from datetime import datetime
            
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Calcular diferencia en meses
            months_diff = (end.year - start.year) * 12 + (end.month - start.month)
            
            # Si la diferencia incluye días adicionales, considerar como mes completo
            if end.day > start.day:
                months_diff += 1
                
            return max(1, months_diff)  # Mínimo 1 mes
            
        except Exception as e:
            print(f"Error al calcular diferencia de meses: {str(e)}")
            return 1
    
    def update_period_from_dates(self, start_date: str, end_date: str):
        """Actualiza las restricciones basándose en fechas de inicio y fin"""
        months_diff = self._calculate_months_difference(start_date, end_date)
        self.update_period_constraints(months_diff)
