"""
Modal de vista detallada para gráficos
"""
import customtkinter as ctk
from typing import Dict, Any, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches


class ChartDetailModal(ctk.CTkToplevel):
    """Modal para mostrar gráficos en vista detallada"""
    
    def __init__(self, parent, chart_type: str, chart_data: Dict[str, Any], 
                 period: Tuple[str, str] = None):
        super().__init__(parent)
        
        self.chart_type = chart_type
        self.chart_data = chart_data
        self.period = period
        
        self.setup_window()
        self.setup_ui()
        self.create_detailed_chart()
    
    def setup_window(self):
        """Configura la ventana modal"""
        self.title("Vista Detallada - Gráfico Estadístico")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"1000x700+{x}+{y}")
        
        # Hacer modal
        self.transient(self.master)
        self.grab_set()
        self.focus()
    
    def setup_ui(self):
        """Configura la interfaz del modal"""
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        
        # Título y período
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=20, pady=15)
        
        chart_titles = {
            "ventas_diarias": "📈 Tendencia de Ventas Diarias",
            "ventas_mensuales": "📊 Comparativa de Ventas Mensuales",
            "productos_vendidos": "🏆 Productos Más Vendidos",
            "estados_pedidos": "📋 Distribución de Estados de Pedidos"
        }
        
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text=chart_titles.get(self.chart_type, "📊 Gráfico Estadístico"),
            font=("Arial", 24, "bold"),
            text_color="#1F2937"
        )
        self.title_label.pack(side="left")
        
        # Información del período
        if self.period:
            fecha_inicio, fecha_fin = self.period
            self.period_label = ctk.CTkLabel(
                self.title_frame,
                text=f"Período: {fecha_inicio} a {fecha_fin}",
                font=("Arial", 12),
                text_color="#6B7280"
            )
            self.period_label.pack(side="right")
        
        # Botón cerrar
        self.close_button = ctk.CTkButton(
            self.title_frame,
            text="✕ Cerrar",
            command=self.destroy,
            width=100,
            height=32,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            font=("Arial", 12)
        )
        self.close_button.pack(side="right", padx=(10, 0))
        
        # Área del gráfico
        self.chart_container = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Frame para estadísticas adicionales
        self.stats_frame = ctk.CTkFrame(self, fg_color="#F1F5F9")
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.create_stats_summary()
    
    def create_detailed_chart(self):
        """Crea el gráfico detallado"""
        try:
            # Configurar matplotlib
            plt.style.use('default')
            
            # Crear figura grande
            fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
            fig.patch.set_facecolor('#FFFFFF')
            ax.set_facecolor('#FFFFFF')
            
            # Obtener datos
            labels = self.chart_data.get('labels', [])
            datasets = self.chart_data.get('datasets', [])
            
            if not datasets:
                ax.text(0.5, 0.5, 'No hay datos disponibles para mostrar', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=16, color='#6B7280')
            else:
                # Crear gráfico según el tipo
                if self.chart_type == "estados_pedidos":
                    self._create_detailed_pie_chart(ax, labels, datasets[0])
                elif self.chart_type == "productos_vendidos":
                    self._create_detailed_bar_chart(ax, labels, datasets[0])
                else:
                    self._create_detailed_line_chart(ax, labels, datasets)
            
            # Mejorar apariencia
            self._style_chart(ax)
            
            plt.tight_layout()
            
            # Integrar en tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
            
            # Añadir barra de herramientas
            toolbar_frame = ctk.CTkFrame(self.chart_container, fg_color="transparent")
            toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))
            
            # Botones de exportación
            export_button = ctk.CTkButton(
                toolbar_frame,
                text="💾 Exportar PNG",
                command=lambda: self._export_chart(fig),
                height=32,
                fg_color="#16A34A",
                font=("Arial", 11)
            )
            export_button.pack(side="right")
            
        except Exception as e:
            print(f"Error al crear gráfico detallado: {str(e)}")
            self._show_error()
    
    def _create_detailed_pie_chart(self, ax, labels, dataset):
        """Crea un gráfico de torta detallado"""
        data = dataset.get('data', [])
        colors = dataset.get('backgroundColor', ['#16A34A', '#2563EB', '#F59E0B', '#DC2626'])
        
        if data and labels:
            # Calcular porcentajes
            total = sum(data)
            percentages = [d/total*100 for d in data]
            
            # Crear gráfico de torta
            wedges, texts, autotexts = ax.pie(
                data,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=[0.05] * len(data)  # Separar ligeramente las secciones
            )
            
            # Mejorar texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(12)
                autotext.set_weight('bold')
            
            # Título
            ax.set_title('Distribución de Estados de Pedidos', fontsize=16, fontweight='bold', pad=20)
    
    def _create_detailed_bar_chart(self, ax, labels, dataset):
        """Crea un gráfico de barras detallado"""
        data = dataset.get('data', [])
        colors = dataset.get('backgroundColor', ['#16A34A'] * len(data))
        
        if data and labels:
            # Crear gráfico de barras
            bars = ax.bar(labels, data, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
            
            # Añadir valores en las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(data)*0.01,
                       f'{int(height)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # Configurar ejes
            ax.set_xlabel('Productos', fontsize=14, fontweight='bold')
            ax.set_ylabel('Unidades Vendidas', fontsize=14, fontweight='bold')
            ax.set_title('Productos Más Vendidos', fontsize=16, fontweight='bold', pad=20)
            
            # Rotar etiquetas si son muchas
            if len(labels) > 5:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _create_detailed_line_chart(self, ax, labels, datasets):
        """Crea un gráfico de líneas detallado"""
        for i, dataset in enumerate(datasets):
            data = dataset.get('data', [])
            label = dataset.get('label', f'Serie {i+1}')
            color = self._parse_color(dataset.get('borderColor', '#16A34A'))
            
            if data:
                # Convertir datos a números
                numeric_data = []
                for val in data:
                    try:
                        numeric_data.append(float(val))
                    except (ValueError, TypeError):
                        numeric_data.append(0)
                
                # Crear línea
                line = ax.plot(labels, numeric_data, color=color, linewidth=3, 
                             label=label, marker='o', markersize=6, alpha=0.9)
                
                # Añadir área bajo la curva
                ax.fill_between(labels, numeric_data, alpha=0.2, color=color)
        
        # Configurar ejes
        ax.set_xlabel('Período', fontsize=14, fontweight='bold')
        
        if self.chart_type == "ventas_diarias":
            ax.set_ylabel('Ventas (S/.)', fontsize=14, fontweight='bold')
            ax.set_title('Tendencia de Ventas Diarias', fontsize=16, fontweight='bold', pad=20)
        else:
            ax.set_ylabel('Ventas (S/.)', fontsize=14, fontweight='bold')
            ax.set_title('Comparativa de Ventas Mensuales', fontsize=16, fontweight='bold', pad=20)
        
        # Leyenda
        if len(datasets) > 1:
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
        
        # Rotar etiquetas del eje X
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _style_chart(self, ax):
        """Aplica estilos profesionales al gráfico"""
        # Grid sutil
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Espinas más sutiles
        for spine in ax.spines.values():
            spine.set_edgecolor('#E5E7EB')
            spine.set_linewidth(1)
        
        # Colores de texto
        ax.tick_params(colors='#374151', labelsize=11)
        ax.xaxis.label.set_color('#374151')
        ax.yaxis.label.set_color('#374151')
        ax.title.set_color('#1F2937')
    
    def _parse_color(self, color_str: str) -> str:
        """Convierte colores rgba a hex"""
        if isinstance(color_str, str) and color_str.startswith('rgba'):
            # Mapeo simple para colores comunes
            color_map = {
                'rgba(54, 162, 235, 1)': '#36A2EB',
                'rgba(255, 99, 132, 1)': '#FF6384',
                'rgba(22, 163, 74, 1)': '#16A34A',
                'rgba(245, 158, 11, 1)': '#F59E0B'
            }
            return color_map.get(color_str, '#16A34A')
        return color_str
    
    def create_stats_summary(self):
        """Crea un resumen estadístico"""
        try:
            self.stats_title = ctk.CTkLabel(
                self.stats_frame,
                text="📊 Resumen Estadístico",
                font=("Arial", 16, "bold"),
                text_color="#1F2937"
            )
            self.stats_title.pack(pady=(15, 10))
            
            # Calcular estadísticas según el tipo de gráfico
            stats_text = self._calculate_stats()
            
            self.stats_label = ctk.CTkLabel(
                self.stats_frame,
                text=stats_text,
                font=("Arial", 12),
                text_color="#374151",
                justify="left"
            )
            self.stats_label.pack(pady=(0, 15))
            
        except Exception as e:
            print(f"Error al crear resumen estadístico: {str(e)}")
    
    def _calculate_stats(self) -> str:
        """Calcula estadísticas del gráfico"""
        try:
            datasets = self.chart_data.get('datasets', [])
            if not datasets:
                return "No hay datos disponibles para el análisis estadístico."
            
            stats = []
            
            for dataset in datasets:
                data = dataset.get('data', [])
                label = dataset.get('label', 'Serie')
                
                if data:
                    # Convertir a números
                    numeric_data = []
                    for val in data:
                        try:
                            numeric_data.append(float(val))
                        except (ValueError, TypeError):
                            numeric_data.append(0)
                    
                    if numeric_data:
                        total = sum(numeric_data)
                        avg = total / len(numeric_data)
                        max_val = max(numeric_data)
                        min_val = min(numeric_data)
                        
                        stats.append(f"• {label}:")
                        stats.append(f"  - Total: {total:,.2f}")
                        stats.append(f"  - Promedio: {avg:,.2f}")
                        stats.append(f"  - Máximo: {max_val:,.2f}")
                        stats.append(f"  - Mínimo: {min_val:,.2f}")
                        stats.append("")
            
            return "\n".join(stats) if stats else "No hay datos numéricos para analizar."
            
        except Exception as e:
            return f"Error al calcular estadísticas: {str(e)}"
    
    def _export_chart(self, fig):
        """Exporta el gráfico como PNG"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Guardar gráfico como..."
            )
            
            if filename:
                fig.savefig(filename, dpi=300, bbox_inches='tight', 
                          facecolor='white', edgecolor='none')
                
                # Mostrar confirmación
                confirmation = ctk.CTkToplevel(self)
                confirmation.title("Exportación Exitosa")
                confirmation.geometry("300x100")
                confirmation.transient(self)
                confirmation.grab_set()
                
                ctk.CTkLabel(
                    confirmation,
                    text="✅ Gráfico exportado exitosamente",
                    font=("Arial", 12)
                ).pack(expand=True)
                
                ctk.CTkButton(
                    confirmation,
                    text="OK",
                    command=confirmation.destroy,
                    width=80
                ).pack(pady=10)
                
        except Exception as e:
            print(f"Error al exportar gráfico: {str(e)}")
    
    def _show_error(self):
        """Muestra un mensaje de error"""
        error_label = ctk.CTkLabel(
            self.chart_container,
            text="❌ Error al cargar el gráfico detallado",
            font=("Arial", 16),
            text_color="#DC2626"
        )
        error_label.pack(expand=True)
    
    def show(self):
        """Muestra el modal"""
        self.deiconify()
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(lambda: self.attributes('-topmost', False))
