"""
Gestor de gráficos estadísticos usando matplotlib
"""
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from ..statistics_service import StatisticsService


class ChartsManager(ctk.CTkFrame):
    """Componente principal para mostrar gráficos estadísticos de ventas"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#F8F9FA", corner_radius=15, **kwargs)
        
        # Configurar tema de matplotlib para que coincida con nuestro diseño
        plt.style.use('default')
        plt.rcParams.update({
            'font.size': 10,
            'axes.labelsize': 11,
            'axes.titlesize': 14,
            'legend.fontsize': 10,
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': '#E5E7EB',
            'axes.linewidth': 0.5,
            'grid.color': '#F3F4F6',
            'grid.linewidth': 0.5,
            'text.color': '#374151'
        })
        
        self.current_period = ("2025-07-01", "2025-07-31")  # Período por defecto
        self.charts_data = {}  # Cache de datos de gráficos
        
        self.setup_ui()
        self.load_initial_charts()
    
    def setup_ui(self):
        """Configura la interfaz principal de gráficos"""
        try:
            # Título de la sección
            self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.title_frame.pack(fill="x", pady=(15, 20))
            
            self.section_title = ctk.CTkLabel(
                self.title_frame,
                text="📊 Gráficos Estadísticos de Ventas",
                font=("Arial", 20, "bold"),
                text_color="#16A34A"
            )
            self.section_title.pack(side="left")
            
            # Frame para controles de gráficos
            self.controls_frame = ctk.CTkFrame(self, height=60, fg_color="white")
            self.controls_frame.pack(fill="x", pady=(0, 15), padx=15)
            self.controls_frame.pack_propagate(False)
            
            # Selector de tipo de gráfico
            self.chart_type_var = ctk.StringVar(value="ventas_diarias")
            self.chart_type_label = ctk.CTkLabel(
                self.controls_frame,
                text="Tipo de Gráfico:",
                font=("Arial", 12),
                text_color="#374151"
            )
            self.chart_type_label.pack(side="left", padx=(15, 5), pady=15)
            
            self.chart_selector = ctk.CTkOptionMenu(
                self.controls_frame,
                values=[
                    "ventas_diarias", 
                    "ventas_mensuales", 
                    "productos_vendidos", 
                    "estados_pedidos"
                ],
                variable=self.chart_type_var,
                command=self.on_chart_type_changed,
                width=180,
                fg_color="#16A34A",
                button_color="#16A34A",
                button_hover_color="#15803D"
            )
            self.chart_selector.pack(side="left", padx=(0, 15), pady=15)
            
            # Botón de actualizar
            self.refresh_btn = ctk.CTkButton(
                self.controls_frame,
                text="🔄 Actualizar",
                command=self.refresh_current_chart,
                width=120,
                height=35,
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                font=("Arial", 12)
            )
            self.refresh_btn.pack(side="left", padx=(0, 15), pady=15)
            
            # Estado de carga
            self.loading_label = ctk.CTkLabel(
                self.controls_frame,
                text="",
                font=("Arial", 11),
                text_color="#6B7280"
            )
            self.loading_label.pack(side="right", padx=(0, 15), pady=15)
            
            # Frame principal para gráficos con scroll
            self.charts_container = ctk.CTkScrollableFrame(
                self, 
                fg_color="white",
                corner_radius=12
            )
            self.charts_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
        except Exception as e:
            print(f"Error al configurar interfaz de gráficos: {str(e)}")
    
    def load_initial_charts(self):
        """Carga los gráficos iniciales"""
        self.load_chart("ventas_diarias")
    
    def on_chart_type_changed(self, chart_type):
        """Se ejecuta cuando cambia el tipo de gráfico seleccionado"""
        self.load_chart(chart_type)
    
    def load_chart(self, chart_type):
        """Carga un gráfico específico"""
        try:
            self.set_loading_state(True, f"Cargando {chart_type}...")
            
            # Limpiar contenedor
            for widget in self.charts_container.winfo_children():
                widget.destroy()
            
            # Obtener datos del servicio
            fecha_inicio, fecha_fin = self.current_period
            result = StatisticsService.fetch_chart_data(chart_type, fecha_inicio, fecha_fin)
            
            if result.get('success'):
                chart_data = result['data']
                self.charts_data[chart_type] = chart_data
                
                # Crear gráfico según el tipo
                if chart_type == "ventas_diarias":
                    self.create_daily_sales_chart(chart_data)
                elif chart_type == "ventas_mensuales":
                    self.create_monthly_sales_chart(chart_data)
                elif chart_type == "productos_vendidos":
                    self.create_top_products_chart(chart_data)
                elif chart_type == "estados_pedidos":
                    self.create_order_status_chart(chart_data)
                
                self.set_loading_state(False, "✅ Datos actualizados")
            else:
                # Usar datos de fallback
                chart_data = result.get('data', {})
                self.charts_data[chart_type] = chart_data
                
                if chart_type == "ventas_diarias":
                    self.create_daily_sales_chart(chart_data)
                elif chart_type == "ventas_mensuales":
                    self.create_monthly_sales_chart(chart_data)
                elif chart_type == "productos_vendidos":
                    self.create_top_products_chart(chart_data)
                elif chart_type == "estados_pedidos":
                    self.create_order_status_chart(chart_data)
                
                self.set_loading_state(False, "⚠️ Usando datos de ejemplo")
                
        except Exception as e:
            print(f"Error al cargar gráfico {chart_type}: {str(e)}")
            self.set_loading_state(False, "❌ Error al cargar")
    
    def create_daily_sales_chart(self, data):
        """Crea gráfico de ventas diarias con doble eje Y"""
        try:
            # Crear figura
            fig = Figure(figsize=(14, 8), facecolor='white')
            
            # Obtener datos
            labels = data.get('labels', [])
            datasets = data.get('datasets', [])
            
            if not labels or not datasets:
                self.create_no_data_chart("ventas_diarias")
                return
            
            # Crear ejes
            ax1 = fig.add_subplot(111)
            ax2 = ax1.twinx()
            
            # Procesar fechas
            dates = [datetime.strptime(label, '%Y-%m-%d') for label in labels]
            
            # Primer dataset (Ventas)
            if len(datasets) > 0:
                sales_data = datasets[0].get('data', [])
                line1 = ax1.plot(dates, sales_data, 
                               color='#16A34A', linewidth=3, marker='o', markersize=6,
                               label=datasets[0].get('label', 'Ventas'), alpha=0.9)
                ax1.fill_between(dates, sales_data, alpha=0.2, color='#16A34A')
            
            # Segundo dataset (Transacciones)
            if len(datasets) > 1:
                transactions_data = datasets[1].get('data', [])
                line2 = ax2.plot(dates, transactions_data, 
                               color='#2563EB', linewidth=3, marker='s', markersize=6,
                               label=datasets[1].get('label', 'Transacciones'), alpha=0.9)
            
            # Configurar ejes
            ax1.set_xlabel('Fecha', fontsize=12, color='#374151', fontweight='bold')
            ax1.set_ylabel('Ventas (S/.)', fontsize=12, color='#16A34A', fontweight='bold')
            ax2.set_ylabel('Transacciones', fontsize=12, color='#2563EB', fontweight='bold')
            
            # Título
            ax1.set_title('Tendencia de Ventas Diarias', fontsize=16, fontweight='bold', 
                         color='#1F2937', pad=20)
            
            # Formatear fechas en eje X
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            fig.autofmt_xdate()
            
            # Grids y estilo
            ax1.grid(True, alpha=0.3, color='#E5E7EB')
            ax1.set_facecolor('#FAFAFA')
            
            # Leyenda combinada
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
                      frameon=True, fancybox=True, shadow=True)
            
            # Ajustar layout
            fig.tight_layout()
            
            # Integrar con tkinter
            canvas = FigureCanvasTkAgg(fig, self.charts_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error al crear gráfico de ventas diarias: {str(e)}")
            self.create_error_chart("ventas_diarias", str(e))
    
    def create_monthly_sales_chart(self, data):
        """Crea gráfico de ventas mensuales"""
        try:
            fig = Figure(figsize=(14, 7), facecolor='white')
            ax = fig.add_subplot(111)
            
            labels = data.get('labels', [])
            datasets = data.get('datasets', [])
            
            if not labels or not datasets:
                self.create_no_data_chart("ventas_mensuales")
                return
            
            # Datos del primer dataset
            sales_data = datasets[0].get('data', [])
            
            # Crear gráfico de barras
            x_pos = range(len(labels))
            bars = ax.bar(x_pos, sales_data, color='#16A34A', alpha=0.8, 
                         edgecolor='white', linewidth=2)
            
            # Agregar valores en las barras
            for i, (bar, value) in enumerate(zip(bars, sales_data)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'S/. {value:,.0f}', ha='center', va='bottom', 
                       fontweight='bold', fontsize=10)
            
            # Configurar gráfico
            ax.set_title('Evolución de Ventas Mensuales', fontsize=16, fontweight='bold', 
                        color='#1F2937', pad=20)
            ax.set_xlabel('Período', fontsize=12, color='#374151', fontweight='bold')
            ax.set_ylabel('Ventas (S/.)', fontsize=12, color='#374151', fontweight='bold')
            
            # Personalizar ejes
            ax.set_xticks(x_pos)
            ax.set_xticklabels(labels, rotation=45)
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_facecolor('#FAFAFA')
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.charts_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error al crear gráfico de ventas mensuales: {str(e)}")
            self.create_error_chart("ventas_mensuales", str(e))
    
    def create_top_products_chart(self, data):
        """Crea gráfico de productos más vendidos"""
        try:
            fig = Figure(figsize=(14, 8), facecolor='white')
            ax = fig.add_subplot(111)
            
            labels = data.get('labels', [])
            datasets = data.get('datasets', [])
            
            if not labels or not datasets:
                self.create_no_data_chart("productos_vendidos")
                return
            
            # Datos y colores
            products_data = datasets[0].get('data', [])
            colors = datasets[0].get('backgroundColor', [
                '#16A34A', '#2563EB', '#F59E0B', '#EF4444', '#8B5CF6',
                '#10B981', '#3B82F6', '#F97316', '#DC2626', '#A855F7'
            ])
            
            # Crear gráfico horizontal para mejor legibilidad
            y_pos = range(len(labels))
            bars = ax.barh(y_pos, products_data, color=colors[:len(labels)], 
                          alpha=0.8, edgecolor='white', linewidth=2)
            
            # Agregar valores
            for i, (bar, value) in enumerate(zip(bars, products_data)):
                width = bar.get_width()
                ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2.,
                       f'{value:,.0f} und.', ha='left', va='center', 
                       fontweight='bold', fontsize=10)
            
            # Configurar
            ax.set_title('Top 10 Productos Más Vendidos', fontsize=16, fontweight='bold', 
                        color='#1F2937', pad=20)
            ax.set_xlabel('Unidades Vendidas', fontsize=12, color='#374151', fontweight='bold')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels)
            ax.grid(True, alpha=0.3, axis='x')
            ax.set_facecolor('#FAFAFA')
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.charts_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error al crear gráfico de productos: {str(e)}")
            self.create_error_chart("productos_vendidos", str(e))
    
    def create_order_status_chart(self, data):
        """Crea gráfico de estados de pedidos (pie chart)"""
        try:
            fig = Figure(figsize=(12, 8), facecolor='white')
            ax = fig.add_subplot(111)
            
            labels = data.get('labels', [])
            datasets = data.get('datasets', [])
            
            if not labels or not datasets:
                self.create_no_data_chart("estados_pedidos")
                return
            
            # Datos
            status_data = datasets[0].get('data', [])
            colors = datasets[0].get('backgroundColor', ['#28a745', '#ffc107', '#17a2b8', '#dc3545'])
            
            # Crear gráfico de pastel
            wedges, texts, autotexts = ax.pie(status_data, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90,
                                             explode=(0.05, 0.05, 0.05, 0.05),
                                             shadow=True, textprops={'fontsize': 11, 'fontweight': 'bold'})
            
            # Mejorar textos
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Distribución de Estados de Pedidos', fontsize=16, fontweight='bold', 
                        color='#1F2937', pad=20)
            
            # Leyenda
            ax.legend(wedges, [f'{label}: {value}' for label, value in zip(labels, status_data)],
                     title="Estados", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            canvas = FigureCanvasTkAgg(fig, self.charts_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error al crear gráfico de estados: {str(e)}")
            self.create_error_chart("estados_pedidos", str(e))
    
    def create_no_data_chart(self, chart_type):
        """Crea un gráfico cuando no hay datos"""
        fig = Figure(figsize=(12, 6), facecolor='white')
        ax = fig.add_subplot(111)
        
        ax.text(0.5, 0.5, f'📊\n\nNo hay datos disponibles\npara {chart_type.replace("_", " ").title()}', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=16, color='#6B7280',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#F3F4F6', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        canvas = FigureCanvasTkAgg(fig, self.charts_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_error_chart(self, chart_type, error):
        """Crea un gráfico de error"""
        fig = Figure(figsize=(12, 6), facecolor='white')
        ax = fig.add_subplot(111)
        
        ax.text(0.5, 0.5, f'❌\n\nError al cargar {chart_type}\n\n{error}', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=14, color='#DC2626',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#FEE2E2', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        canvas = FigureCanvasTkAgg(fig, self.charts_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def set_loading_state(self, is_loading, message=""):
        """Actualiza el estado de carga"""
        if is_loading:
            self.refresh_btn.configure(state="disabled", text="🔄 Cargando...")
            self.loading_label.configure(text=message)
        else:
            self.refresh_btn.configure(state="normal", text="🔄 Actualizar")
            self.loading_label.configure(text=message)
    
    def refresh_current_chart(self):
        """Refresca el gráfico actual"""
        current_type = self.chart_type_var.get()
        self.load_chart(current_type)
    
    def update_period(self, fecha_inicio, fecha_fin):
        """Actualiza el período de los gráficos"""
        self.current_period = (fecha_inicio, fecha_fin)
        # Recargar gráfico actual
        current_type = self.chart_type_var.get()
        self.load_chart(current_type)
    
    def get_current_chart_data(self):
        """Obtiene los datos del gráfico actual para reportes"""
        current_type = self.chart_type_var.get()
        return self.charts_data.get(current_type, {})
