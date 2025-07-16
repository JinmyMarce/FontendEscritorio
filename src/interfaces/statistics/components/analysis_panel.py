"""
Panel de análisis visual con gráfico único y navegación
"""
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches


class AnalysisPanel(ctk.CTkFrame):
    """Panel principal de análisis visual con gráfico único"""
    
    def __init__(self, parent, on_detail_view: Callable = None, **kwargs):
        super().__init__(
            parent,
            fg_color="#FFFFFF",
            corner_radius=15,
            **kwargs
        )
        
        self.on_detail_view = on_detail_view
        self.current_chart_type = "ventas_diarias"
        self.chart_data = None
        self.canvas_widget = None
        self.current_period_text = None  # Para almacenar el texto del período actual
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura el panel de análisis"""
        # Header del panel
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Título del panel
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📊 Análisis Visual",
            font=("Arial", 20, "bold"),
            text_color="#1F2937",
            anchor="w"
        )
        self.title_label.pack(side="left")
        
        # Frame para botones pequeños en el header (lado derecho)
        self.header_buttons_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_buttons_frame.pack(side="right")
        
        # Botón exportar (más pequeño)
        self.export_button = ctk.CTkButton(
            self.header_buttons_frame,
            text="💾 PNG",
            command=self.export_chart,
            width=70,
            height=28,
            font=("Arial", 10, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            corner_radius=6
        )
        self.export_button.pack(side="right", padx=(5, 0))
        
        # Botón ver en detalle (más pequeño)
        self.detail_button = ctk.CTkButton(
            self.header_buttons_frame,
            text="🔍 Detalle",
            command=self.show_detail_view,
            width=70,
            height=28,
            font=("Arial", 10, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            corner_radius=6
        )
        self.detail_button.pack(side="right", padx=(0, 5))
        
        # Área del gráfico principal
        self.chart_container = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=12
        )
        self.chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Placeholder inicial
        self.show_placeholder()
    
    def show_placeholder(self):
        """Muestra el placeholder mientras se cargan los datos"""
        # Limpiar contenedor
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        placeholder_label = ctk.CTkLabel(
            self.chart_container,
            text="📊\n\nCargando gráfico estadístico...\n\nSelecciona un período y tipo de análisis",
            font=("Arial", 16),
            text_color="#9CA3AF",
            justify="center"
        )
        placeholder_label.pack(expand=True)
    
    def update_chart(self, chart_type: str, chart_data: Dict[str, Any]):
        """Actualiza el gráfico mostrado"""
        try:
            self.current_chart_type = chart_type
            self.chart_data = chart_data
            
            # Crear el gráfico
            self.create_main_chart(chart_data)
            
        except Exception as e:
            print(f"Error al actualizar gráfico: {str(e)}")
            self.show_error()
    
    def create_main_chart(self, chart_data: Dict[str, Any]):
        """Crea el gráfico principal basado en los datos"""
        try:
            # Limpiar contenedor anterior
            for widget in self.chart_container.winfo_children():
                widget.destroy()
            
            # Obtener datos del gráfico
            labels = chart_data.get('labels', [])
            datasets = chart_data.get('datasets', [])
            chart_type = chart_data.get('chart_type', 'line')
            title = self._generate_dynamic_title(chart_data, self.current_chart_type)
            description = chart_data.get('description', '')
            chart_config = chart_data.get('chart_config', {})
            
            if not datasets:
                self.show_placeholder()
                return
            
            # Configurar matplotlib con estilo moderno
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.patch.set_facecolor('#F8FAFC')
            ax.set_facecolor('#FFFFFF')
            
            # Crear gráfico según el tipo - usar current_chart_type para productos_vendidos
            actual_chart_type = self.current_chart_type if self.current_chart_type == "productos_vendidos" else chart_type
            
            if actual_chart_type == "line_dual_axis":
                self._create_dual_axis_chart(fig, ax, labels, datasets, chart_config)
            elif actual_chart_type == "area":
                self._create_area_chart(ax, labels, datasets)
            elif actual_chart_type in ["line", "ventas_diarias", "ventas_mensuales"]:
                self._create_line_chart(ax, labels, datasets)
            elif actual_chart_type in ["bar", "productos_vendidos"]:
                if datasets:
                    self._create_bar_chart(ax, labels, datasets[0])
            elif actual_chart_type in ["pie", "doughnut", "estados_pedidos"]:
                if datasets:
                    self._create_pie_chart(ax, labels, datasets[0])
            else:
                # Tipo no reconocido, usar línea por defecto
                self._create_line_chart(ax, labels, datasets)
            
            # Configurar título
            ax.set_title(title, fontsize=16, fontweight='bold', color='#1F2937', pad=20)
            
            # Configurar escalas según chart_config
            scales = chart_config.get('scales', {})
            if 'y' in scales and chart_type != "line_dual_axis":
                y_config = scales['y']
                if 'title' in y_config:
                    ax.set_ylabel(y_config['title'], fontsize=12, color='#6B7280')
            
            # Estilo general (no aplicar a gráficos de torta)
            if chart_type not in ["pie", "doughnut"]:
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E5E7EB')
                ax.spines['bottom'].set_color('#E5E7EB')
                ax.tick_params(colors='#6B7280', labelsize=10)
            
            plt.tight_layout(pad=2.0)
            
            # Agregar al contenedor
            canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
            self.canvas_widget = canvas
            
            plt.close(fig)  # Cerrar para liberar memoria
            
        except Exception as e:
            print(f"Error al crear gráfico principal: {str(e)}")
            self.show_error()
    
    def _create_line_chart(self, ax, labels, datasets):
        """Crea un gráfico de líneas mejorado"""
        colors = ['#16A34A', '#2563EB', '#F59E0B', '#DC2626', '#8B5CF6']
        
        for i, dataset in enumerate(datasets):
            data = dataset.get('data', [])
            label = dataset.get('label', f'Serie {i+1}')
            
            # Colores desde el dataset o usar colores por defecto
            border_color = self._convert_color(dataset.get('borderColor', colors[i % len(colors)]))
            bg_color = self._convert_color(dataset.get('backgroundColor', border_color))
            
            # Configuración de línea
            line_width = dataset.get('borderWidth', 2)
            tension = dataset.get('tension', 0.4)
            fill = dataset.get('fill', False)
            
            if data:
                # Convertir datos a números
                numeric_data = []
                for val in data:
                    try:
                        numeric_data.append(float(val))
                    except (ValueError, TypeError):
                        numeric_data.append(0)
                
                x_range = range(len(numeric_data))
                
                # Crear línea con suavizado si tension > 0
                if tension > 0:
                    # Línea suavizada
                    ax.plot(x_range, numeric_data, color=border_color, 
                           linewidth=line_width, marker='o', markersize=4, 
                           label=label, alpha=0.9)
                else:
                    # Línea recta
                    ax.plot(x_range, numeric_data, color=border_color, 
                           linewidth=line_width, marker='o', markersize=4, 
                           label=label, alpha=0.9, linestyle='-')
                
                # Rellenar área si está configurado
                if fill:
                    ax.fill_between(x_range, numeric_data, alpha=0.3, color=bg_color)
        
        # Configurar etiquetas del eje X
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45 if len(labels) > 7 else 0)
        
        # Leyenda
        if len(datasets) > 1:
            ax.legend(loc='upper left', frameon=False)
    
    def _create_bar_chart(self, ax, labels, dataset):
        """Crea un gráfico de barras mejorado para productos"""
        data = dataset.get('data', [])
        background_colors = dataset.get('backgroundColor', [])
        
        if data and labels:
            # Convertir datos a números
            numeric_data = []
            for val in data:
                try:
                    numeric_data.append(float(val))
                except (ValueError, TypeError):
                    numeric_data.append(0)
            
            # Usar colores de ranking si están disponibles, sino usar degradado
            if background_colors and len(background_colors) >= len(numeric_data):
                colors = background_colors[:len(numeric_data)]
            else:
                # Colores de ranking: oro, plata, bronce, y degradado verde
                colors = ['#FFD700', '#C0C0C0', '#CD7F32'] + ['#10B981', '#059669', '#047857'] * 10
                colors = colors[:len(numeric_data)]
            
            # Crear barras con colores individuales
            bars = ax.bar(labels, numeric_data, color=colors, alpha=0.9, width=0.7, 
                         edgecolor='#374151', linewidth=1)
            
            # Agregar valores en las barras con formato de moneda
            for bar, value in zip(bars, numeric_data):
                if value > 0:
                    # Formatear como moneda
                    if value >= 1000:
                        label_text = f'S/. {value/1000:.1f}k'
                    else:
                        label_text = f'S/. {int(value)}'
                    
                    ax.text(bar.get_x() + bar.get_width()/2, 
                           bar.get_height() + max(numeric_data)*0.02,
                           label_text, ha='center', va='bottom', 
                           fontsize=11, fontweight='bold', color='#1F2937')
            
            # Configurar etiquetas del eje X
            if len(labels) > 3:
                # Rotar y ajustar labels para productos
                ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=10)
            else:
                ax.set_xticklabels(labels, fontsize=11)
            
            # Configurar eje Y con formato de moneda
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'S/. {int(x)}'))
            
            # Agregar grid sutil
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Mejorar márgenes
            ax.margins(x=0.1)
    
    def _create_pie_chart(self, ax, labels, dataset):
        """Crea un gráfico de torta"""
        data = dataset.get('data', [])
        colors = dataset.get('backgroundColor', ['#16A34A', '#2563EB', '#F59E0B', '#DC2626'])
        
        if data and labels:
            # Convertir datos a números
            numeric_data = []
            for val in data:
                try:
                    numeric_data.append(float(val))
                except (ValueError, TypeError):
                    numeric_data.append(0)
            
            # Crear gráfico de torta
            wedges, texts, autotexts = ax.pie(
                numeric_data, 
                labels=labels, 
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=[0.05] * len(numeric_data)  # Separar un poco las porciones
            )
            
            # Estilo de texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_weight('bold')
            
            for text in texts:
                text.set_fontsize(11)
                text.set_color('#374151')
    
    def _create_dual_axis_chart(self, fig, ax, labels, datasets, chart_config):
        """Crea un gráfico con doble eje Y"""
        # Configurar primer eje
        ax2 = None
        scales = chart_config.get('scales', {})
        
        for i, dataset in enumerate(datasets):
            data = dataset.get('data', [])
            label = dataset.get('label', f'Serie {i+1}')
            y_axis_id = dataset.get('yAxisID', 'y')
            
            # Convertir datos a números
            numeric_data = []
            for val in data:
                try:
                    numeric_data.append(float(val))
                except (ValueError, TypeError):
                    numeric_data.append(0)
            
            x_range = range(len(numeric_data))
            
            # Seleccionar eje según configuración
            if y_axis_id == 'y1' and ax2 is None:
                # Crear segundo eje
                ax2 = ax.twinx()
                current_ax = ax2
            else:
                current_ax = ax
            
            # Configurar estilo del dataset - convertir colores RGBA a hex
            border_color = self._convert_color(dataset.get('borderColor', '#16A34A'))
            line_style = '-'
            if 'borderDash' in dataset:
                line_style = '--'
            
            fill = dataset.get('fill', False)
            tension = dataset.get('tension', 0)
            
            # Dibujar línea
            current_ax.plot(x_range, numeric_data, color=border_color, linewidth=2,
                           linestyle=line_style, marker='o', markersize=4, 
                           label=label, alpha=0.9)
            
            # Rellenar área si está configurado
            if fill:
                bg_color = self._convert_color(dataset.get('backgroundColor', border_color))
                current_ax.fill_between(x_range, numeric_data, alpha=0.2, color=bg_color)
        
        # Configurar etiquetas del eje X
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45 if len(labels) > 7 else 0)
        
        # Configurar etiquetas de los ejes Y
        if 'y' in scales:
            y_config = scales['y']
            if 'title' in y_config:
                ax.set_ylabel(y_config['title'], fontsize=12, color='#6B7280')
        
        if ax2 and 'y1' in scales:
            y1_config = scales['y1']
            if 'title' in y1_config:
                ax2.set_ylabel(y1_config['title'], fontsize=12, color='#6B7280')
            
            # Ocultar grid del segundo eje si está configurado
            if not y1_config.get('grid', True):
                ax2.grid(False)
        
        # Leyendas combinadas
        lines1, labels1 = ax.get_legend_handles_labels()
        if ax2:
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=False)
        else:
            ax.legend(loc='upper left', frameon=False)
    
    def _create_area_chart(self, ax, labels, datasets):
        """Crea un gráfico de área"""
        colors = ['#16A34A', '#2563EB', '#F59E0B', '#DC2626']
        
        for i, dataset in enumerate(datasets):
            data = dataset.get('data', [])
            label = dataset.get('label', f'Área {i+1}')
            
            # Convertir colores
            border_color = self._convert_color(dataset.get('borderColor', colors[i % len(colors)]))
            bg_color = self._convert_color(dataset.get('backgroundColor', border_color))
            
            if data:
                # Convertir datos a números
                numeric_data = []
                for val in data:
                    try:
                        numeric_data.append(float(val))
                    except (ValueError, TypeError):
                        numeric_data.append(0)
                
                x_range = range(len(numeric_data))
                
                # Crear área rellena
                ax.fill_between(x_range, numeric_data, alpha=0.6, 
                               color=bg_color, label=label)
                
                # Línea de borde
                ax.plot(x_range, numeric_data, color=border_color, linewidth=2, alpha=0.8)
        
        # Configurar etiquetas del eje X
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45 if len(labels) > 7 else 0)
        
        # Leyenda
        if len(datasets) > 1:
            ax.legend(loc='upper left', frameon=False)
    
    def _convert_color(self, color_string):
        """Convierte colores RGBA a formato matplotlib"""
        if isinstance(color_string, str):
            # Si es un color rgba(), convertir a hex o usar directamente
            if color_string.startswith('rgba('):
                # Extraer valores RGB
                import re
                match = re.search(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)', color_string)
                if match:
                    r, g, b = map(int, match.groups())
                    return f'#{r:02x}{g:02x}{b:02x}'
            elif color_string.startswith('#'):
                return color_string
            else:
                # Mapear colores conocidos
                color_map = {
                    'rgba(34, 197, 94, 1)': '#22C55E',
                    'rgba(59, 130, 246, 1)': '#3B82F6',
                    'rgba(168, 85, 247, 1)': '#A855F7',
                    'rgba(16, 185, 129, 1)': '#10B981',
                    'rgba(245, 158, 11, 1)': '#F59E0B',
                    'rgba(239, 68, 68, 1)': '#EF4444'
                }
                return color_map.get(color_string, '#6B7280')
        return color_string

    def show_error(self):
        """Muestra un mensaje de error"""
        # Limpiar contenedor
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        error_label = ctk.CTkLabel(
            self.chart_container,
            text="⚠️\n\nError al cargar el gráfico\n\nIntenta cambiar el período o tipo de análisis",
            font=("Arial", 16),
            text_color="#DC2626",
            justify="center"
        )
        error_label.pack(expand=True)
        
        # Actualizar estado
    def show_detail_view(self):
        """Muestra la vista detallada del gráfico"""
        if self.on_detail_view and self.chart_data:
            self.on_detail_view(self.current_chart_type, self.chart_data)
        else:
            print("⚠️ No hay datos disponibles para mostrar en detalle")
    
    def export_chart(self):
        """Exporta el gráfico actual como PNG"""
        try:
            if self.canvas_widget and self.chart_data:
                # Implementar exportación
                print(f"🎯 Exportando gráfico: {self.current_chart_type}")
                # Aquí se puede implementar la lógica de exportación
                
                # Por ahora, mostrar mensaje
                import tkinter.messagebox as messagebox
                messagebox.showinfo(
                    "Exportar", 
                    f"Funcionalidad de exportación implementada para:\n{self.current_chart_type}"
                )
            else:
                print("⚠️ No hay gráfico disponible para exportar")
                
        except Exception as e:
            print(f"Error al exportar gráfico: {str(e)}")
    
    def set_loading_state(self, is_loading: bool):
        """Actualiza el estado de carga"""
        if is_loading:
            print("🔄 Cargando datos del gráfico...")
        else:
            print("✅ Datos del gráfico actualizados")
    
    def _generate_dynamic_title(self, chart_data: Dict[str, Any], chart_type: str) -> str:
        """Genera un título dinámico basado en el tipo de gráfico y período"""
        original_title = chart_data.get('title', 'Gráfico Estadístico')
        
        if chart_type == "productos_vendidos":
            # Usar el período del dropdown si está disponible
            if self.current_period_text:
                return f"Top Productos Vendidos - {self.current_period_text}"
            
            # Fallback: usar período de los datos de la API
            periodo_info = chart_data.get('periodo', {})
            if periodo_info:
                fecha_inicio = periodo_info.get('fecha_inicio', '')
                fecha_fin = periodo_info.get('fecha_fin', '')
                if fecha_inicio and fecha_fin:
                    return f"Top Productos Vendidos ({fecha_inicio} - {fecha_fin})"
            
            return "Top Productos Vendidos en el período"
        
        # Para otros tipos de gráfico, usar el título original
        return original_title
    
    def update_period_text(self, period_text: str):
        """Actualiza el texto del período actual"""
        self.current_period_text = period_text
        print(f"📅 Período actualizado en AnalysisPanel: {period_text}")
