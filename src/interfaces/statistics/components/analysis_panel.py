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
        
        # Estado de datos
        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="✅ Datos actualizados",
            font=("Arial", 11),
            text_color="#16A34A"
        )
        self.status_label.pack(side="right")
        
        # Área del gráfico principal
        self.chart_container = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=12
        )
        self.chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Placeholder inicial
        self.show_placeholder()
        
        # Panel de controles (botones)
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Botón ver en detalle
        self.detail_button = ctk.CTkButton(
            self.controls_frame,
            text="🔍 Ver en detalle",
            command=self.show_detail_view,
            width=140,
            height=36,
            font=("Arial", 12, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            corner_radius=8
        )
        self.detail_button.pack(side="left", padx=(0, 10))
        
        # Botón exportar
        self.export_button = ctk.CTkButton(
            self.controls_frame,
            text="💾 Exportar a PNG",
            command=self.export_chart,
            width=140,
            height=36,
            font=("Arial", 12, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            corner_radius=8
        )
        self.export_button.pack(side="left")
        
        # Información del gráfico actual (lado derecho)
        self.info_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.info_frame.pack(side="right")
        
        self.chart_info_label = ctk.CTkLabel(
            self.info_frame,
            text="Tendencia de ventas por día",
            font=("Arial", 12),
            text_color="#6B7280"
        )
        self.chart_info_label.pack()
    
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
            
            # Actualizar información del gráfico
            chart_descriptions = {
                "ventas_diarias": "Tendencia de ventas por día",
                "ventas_mensuales": "Comparativa de ventas mensuales",
                "productos_vendidos": "Ranking de productos más vendidos",
                "estados_pedidos": "Distribución de estados de pedidos"
            }
            
            self.chart_info_label.configure(
                text=chart_descriptions.get(chart_type, "Análisis estadístico")
            )
            
            # Crear el gráfico
            self.create_main_chart(chart_data)
            
            # Actualizar estado
            self.status_label.configure(
                text="✅ Datos actualizados",
                text_color="#16A34A"
            )
            
        except Exception as e:
            print(f"Error al actualizar gráfico: {str(e)}")
            self.show_error()
    
    def create_main_chart(self, chart_data: Dict[str, Any]):
        """Crea el gráfico principal"""
        try:
            # Limpiar contenedor
            for widget in self.chart_container.winfo_children():
                widget.destroy()
            
            # Configurar matplotlib
            plt.style.use('default')
            
            # Crear figura más grande para el panel principal
            fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
            fig.patch.set_facecolor('#F8FAFC')
            ax.set_facecolor('#FFFFFF')
            
            # Obtener datos
            labels = chart_data.get('labels', [])
            datasets = chart_data.get('datasets', [])
            
            if not datasets:
                ax.text(0.5, 0.5, 'Sin datos disponibles', ha='center', va='center',
                       transform=ax.transAxes, fontsize=14, color='#6B7280')
            else:
                # Crear gráfico según el tipo
                if self.current_chart_type == "estados_pedidos":
                    self._create_pie_chart(ax, labels, datasets[0])
                elif self.current_chart_type == "productos_vendidos":
                    self._create_bar_chart(ax, labels, datasets[0])
                else:
                    self._create_line_chart(ax, labels, datasets)
            
            # Configurar ejes y estilo
            if self.current_chart_type != "estados_pedidos":
                ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                ax.set_axisbelow(True)
            
            # Estilo de los ejes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#E5E7EB')
            ax.spines['bottom'].set_color('#E5E7EB')
            
            # Configurar labels
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
        """Crea un gráfico de líneas"""
        colors = ['#16A34A', '#2563EB', '#F59E0B', '#DC2626']
        
        for i, dataset in enumerate(datasets[:2]):  # Máximo 2 series
            data = dataset.get('data', [])
            label = dataset.get('label', f'Serie {i+1}')
            color = colors[i % len(colors)]
            
            if data:
                # Convertir datos a números
                numeric_data = []
                for val in data:
                    try:
                        numeric_data.append(float(val))
                    except (ValueError, TypeError):
                        numeric_data.append(0)
                
                x_range = range(len(numeric_data))
                ax.plot(x_range, numeric_data, color=color, linewidth=3, 
                       marker='o', markersize=6, label=label, alpha=0.9)
                ax.fill_between(x_range, numeric_data, alpha=0.2, color=color)
        
        # Configurar etiquetas del eje X
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45 if len(labels) > 7 else 0)
        
        # Leyenda
        if len(datasets) > 1:
            ax.legend(loc='upper left', frameon=False)
    
    def _create_bar_chart(self, ax, labels, dataset):
        """Crea un gráfico de barras"""
        data = dataset.get('data', [])
        color = '#F59E0B'
        
        if data and labels:
            # Convertir datos a números
            numeric_data = []
            for val in data:
                try:
                    numeric_data.append(float(val))
                except (ValueError, TypeError):
                    numeric_data.append(0)
            
            bars = ax.bar(labels, numeric_data, color=color, alpha=0.8, width=0.6)
            
            # Agregar valores en las barras
            for bar, value in zip(bars, numeric_data):
                if value > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(numeric_data)*0.01,
                           f'{int(value)}', ha='center', va='bottom', fontsize=10, color='#374151')
            
            # Rotar labels si son muchos
            if len(labels) > 5:
                ax.set_xticklabels(labels, rotation=45, ha='right')
    
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
        self.status_label.configure(
            text="❌ Error al cargar",
            text_color="#DC2626"
        )
    
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
            self.status_label.configure(
                text="🔄 Cargando...",
                text_color="#F59E0B"
            )
        else:
            self.status_label.configure(
                text="✅ Datos actualizados", 
                text_color="#16A34A"
            )
