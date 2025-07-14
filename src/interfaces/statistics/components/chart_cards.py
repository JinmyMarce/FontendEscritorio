"""
Grid de tarjetas de gráficos en vista previa
"""
import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
from PIL import Image, ImageTk
import io


class ChartCard(ctk.CTkFrame):
    """Tarjeta individual de gráfico con vista previa"""
    
    def __init__(self, parent, chart_type: str, chart_info: Dict[str, str], 
                 on_expand: Callable = None, **kwargs):
        super().__init__(
            parent,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=2,
            border_color="#E5E7EB",
            **kwargs
        )
        
        self.chart_type = chart_type
        self.chart_info = chart_info
        self.on_expand = on_expand
        self.chart_data = None
        
        self.setup_ui()
        self.bind_hover_effects()
    
    def setup_ui(self):
        """Configura la interfaz de la tarjeta más compacta"""
        # Header con título e icono más compacto
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=12, pady=(12, 8))
        
        # Icono más pequeño
        self.icon_label = ctk.CTkLabel(
            self.header_frame,
            text=self.chart_info.get("icon", "📊"),
            font=("Arial", 20)
        )
        self.icon_label.pack(side="left")
        
        # Título y descripción
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))
        
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text=self.chart_info.get("title", "Gráfico"),
            font=("Arial", 13, "bold"),
            text_color="#1F2937",
            anchor="w"
        )
        self.title_label.pack(fill="x")
        
        self.desc_label = ctk.CTkLabel(
            self.title_frame,
            text=self.chart_info.get("description", ""),
            font=("Arial", 10),
            text_color="#6B7280",
            anchor="w"
        )
        self.desc_label.pack(fill="x")
        
        # Área del gráfico en miniatura más pequeña
        self.chart_frame = ctk.CTkFrame(
            self,
            fg_color="#F9FAFB",
            corner_radius=8,
            height=100
        )
        self.chart_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.chart_frame.pack_propagate(False)
        
        # Placeholder inicial
        self.placeholder_label = ctk.CTkLabel(
            self.chart_frame,
            text="🔄 Cargando...",
            font=("Arial", 11),
            text_color="#9CA3AF"
        )
        self.placeholder_label.pack(expand=True)
        
        # Botón de expandir más pequeño
        self.expand_button = ctk.CTkButton(
            self,
            text="Ver Detalle 🔍",
            command=self.expand_chart,
            height=30,
            fg_color=self.chart_info.get("color", "#16A34A"),
            hover_color=self._darken_color(self.chart_info.get("color", "#16A34A")),
            font=("Arial", 11),
            corner_radius=6
        )
        self.expand_button.pack(fill="x", padx=12, pady=(0, 12))
    
    def bind_hover_effects(self):
        """Añade efectos de hover a la tarjeta"""
        def on_enter(event):
            self.configure(border_color="#3B82F6")
        
        def on_leave(event):
            self.configure(border_color="#E5E7EB")
        
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
    
    def update_chart_preview(self, chart_data: Dict[str, Any]):
        """Actualiza la vista previa del gráfico"""
        try:
            self.chart_data = chart_data
            
            # Limpiar placeholder
            self.placeholder_label.destroy()
            
            # Crear gráfico en miniatura
            self.create_mini_chart(chart_data)
            
        except Exception as e:
            print(f"Error al actualizar preview del gráfico {self.chart_type}: {str(e)}")
            self.show_error()
    
    def create_mini_chart(self, chart_data: Dict[str, Any]):
        """Crea un gráfico en miniatura más compacto"""
        try:
            # Configurar matplotlib para el modo oscuro/claro
            plt.style.use('default')
            
            # Crear figura más pequeña
            fig, ax = plt.subplots(figsize=(3.0, 1.5), dpi=70)
            fig.patch.set_facecolor('#F9FAFB')
            ax.set_facecolor('#F9FAFB')
            
            # Obtener datos
            labels = chart_data.get('labels', [])
            datasets = chart_data.get('datasets', [])
            
            if not datasets:
                ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=9, color='#6B7280')
            else:
                # Crear gráfico según el tipo
                if self.chart_type == "estados_pedidos":
                    self._create_mini_pie_chart(ax, labels, datasets[0])
                else:
                    self._create_mini_line_chart(ax, labels, datasets)
            
            # Configurar ejes (completamente ocultos)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            plt.tight_layout(pad=0.1)
            
            # Convertir a imagen
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)
            
            plt.close(fig)  # Cerrar para liberar memoria
            
        except Exception as e:
            print(f"Error al crear mini gráfico: {str(e)}")
            self.show_error()
    
    def _create_mini_pie_chart(self, ax, labels, dataset):
        """Crea un gráfico de torta en miniatura"""
        data = dataset.get('data', [])
        colors = dataset.get('backgroundColor', ['#16A34A', '#2563EB', '#F59E0B', '#DC2626'])
        
        if data:
            ax.pie(data, colors=colors, startangle=90)
    
    def _create_mini_line_chart(self, ax, labels, datasets):
        """Crea un gráfico de líneas en miniatura"""
        for i, dataset in enumerate(datasets[:2]):  # Máximo 2 líneas para el preview
            data = dataset.get('data', [])
            label = dataset.get('label', f'Serie {i+1}')
            color = dataset.get('borderColor', '#16A34A')
            
            if isinstance(color, str) and color.startswith('rgba'):
                # Convertir rgba a hex aproximado
                color = '#16A34A' if i == 0 else '#2563EB'
            
            if data:
                x_range = range(len(data))
                # Convertir datos a números
                numeric_data = []
                for val in data:
                    try:
                        numeric_data.append(float(val))
                    except (ValueError, TypeError):
                        numeric_data.append(0)
                
                ax.plot(x_range, numeric_data, color=color, linewidth=2, alpha=0.8)
                ax.fill_between(x_range, numeric_data, alpha=0.2, color=color)
    
    def show_error(self):
        """Muestra un mensaje de error"""
        error_label = ctk.CTkLabel(
            self.chart_frame,
            text="⚠️ Error al cargar",
            font=("Arial", 11),
            text_color="#DC2626"
        )
        error_label.pack(expand=True)
    
    def expand_chart(self):
        """Expande el gráfico en vista detallada"""
        if self.on_expand:
            self.on_expand(self.chart_type)
    
    def _darken_color(self, hex_color: str) -> str:
        """Oscurece un color hex para el efecto hover"""
        try:
            # Convertir hex a RGB
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Oscurecer (reducir cada componente)
            darker_rgb = tuple(max(0, c - 40) for c in rgb)
            
            # Convertir de vuelta a hex
            return '#{:02x}{:02x}{:02x}'.format(*darker_rgb)
        except:
            return "#115E3A"  # Verde oscuro por defecto


class ChartCardsGrid(ctk.CTkFrame):
    """Grid de tarjetas de gráficos"""
    
    def __init__(self, parent, on_chart_expand: Callable = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_chart_expand = on_chart_expand
        self.chart_cards = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la cuadrícula de tarjetas más compacta"""
        # Configurar grid (2x2) con mejor distribución
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Información de los gráficos con descripciones más cortas
        charts_info = {
            "ventas_diarias": {
                "title": "Ventas Diarias",
                "description": "Tendencia por día",
                "icon": "📈",
                "color": "#16A34A"
            },
            "ventas_mensuales": {
                "title": "Ventas Mensuales",
                "description": "Comparativa mensual",
                "icon": "📊",
                "color": "#2563EB"
            },
            "productos_vendidos": {
                "title": "Top Productos",
                "description": "Más vendidos",
                "icon": "🏆",
                "color": "#F59E0B"
            },
            "estados_pedidos": {
                "title": "Estados",
                "description": "Distribución pedidos",
                "icon": "📋",
                "color": "#7C3AED"
            }
        }
        
        # Crear tarjetas con tamaño fijo más pequeño
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        chart_types = list(charts_info.keys())
        
        for i, chart_type in enumerate(chart_types):
            if i < len(positions):
                row, col = positions[i]
                
                card = ChartCard(
                    self,
                    chart_type=chart_type,
                    chart_info=charts_info[chart_type],
                    on_expand=self.on_chart_expand,
                    width=250,
                    height=180
                )
                
                card.grid(
                    row=row,
                    column=col,
                    padx=8,
                    pady=8,
                    sticky="nsew"
                )
                
                self.chart_cards[chart_type] = card
    
    def update_chart_preview(self, chart_type: str, chart_data: Dict[str, Any]):
        """Actualiza la vista previa de un gráfico específico"""
        if chart_type in self.chart_cards:
            self.chart_cards[chart_type].update_chart_preview(chart_data)
    
    def update_all_charts(self, charts_data: Dict[str, Dict[str, Any]]):
        """Actualiza todas las vistas previas"""
        for chart_type, data in charts_data.items():
            self.update_chart_preview(chart_type, data)
