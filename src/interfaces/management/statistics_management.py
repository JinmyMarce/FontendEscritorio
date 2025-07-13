import customtkinter as ctk
import tkinter as tk
from tkinter import StringVar
from datetime import datetime, timedelta
from src.core.config import REPORTS_ENDPOINTS, UI_CONFIG
from src.shared.utils import APIHandler, SessionManager
import tkinter.messagebox as messagebox


class EstadisticasVentas(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)
        self.parent = parent
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Variables para almacenar los datos
        self.kpis_data = {}
        
        try:
            self.setup_ui()
            self.cargar_datos_iniciales()
        except Exception as e:
            print(f"Error al inicializar EstadisticasVentas: {str(e)}")
            messagebox.showerror("Error", f"Error al inicializar estadísticas: {str(e)}")
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        try:
            # Título principal
            title_frame = ctk.CTkFrame(self, fg_color="transparent")
            title_frame.pack(fill="x", pady=(20, 20))
            
            title_label = ctk.CTkLabel(
                title_frame,
                text="📊 Estadísticas de Ventas",
                font=("Arial", 28, "bold"),
                text_color="#2D5A27"
            )
            title_label.pack(side="left")
            
            # Frame para el selector de fechas
            date_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
            date_frame.pack(side="right")
            
            period_label = ctk.CTkLabel(
                date_frame,
                text="Período:",
                font=("Arial", 14)
            )
            period_label.pack(side="left", padx=(0, 10))
            
            # Selector de período predefinido
            self.periodo_var = StringVar(value="Último mes")
            self.periodo_selector = ctk.CTkOptionMenu(
                date_frame,
                variable=self.periodo_var,
                values=["Último mes", "Últimos 7 días", "Últimos 3 meses", "Año actual"],
                command=self.on_periodo_changed,
                width=150,
                fg_color="#2D5A27",
                button_color="#367832"
            )
            self.periodo_selector.pack(side="left", padx=(0, 10))
            
            # Botón de actualizar
            self.btn_refresh = ctk.CTkButton(
                date_frame,
                text="Actualizar",
                command=self.actualizar_datos,
                width=120,
                height=35,
                fg_color="#4A90C2",
                hover_color="#357ABD",
                font=("Arial", 14),
                corner_radius=8
            )
            self.btn_refresh.pack(side="left")
            
            # Frame para los KPIs
            self.kpis_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.kpis_frame.pack(fill="x", pady=(0, 30))
            
            # Configurar grid para los KPIs
            for i in range(4):
                self.kpis_frame.grid_columnconfigure(i, weight=1)
            
            # Crear los widgets de KPIs
            self.create_kpi_widgets()
            
            # Frame para contenido adicional (futuras gráficas)
            self.content_frame = ctk.CTkFrame(self, fg_color="#F8F9FA", corner_radius=15)
            self.content_frame.pack(fill="both", expand=True)
            
            # Placeholder para futuras funcionalidades
            placeholder_label = ctk.CTkLabel(
                self.content_frame,
                text="📈 Próximamente: Gráficos detallados de ventas\n\n"
                     "Aquí se mostrarán gráficos interactivos con:\n"
                     "• Tendencias de ventas\n"
                     "• Productos más vendidos\n"
                     "• Análisis por categorías\n"
                     "• Comparativas por períodos",
                font=("Arial", 16),
                text_color="#6C757D",
                justify="center"
            )
            placeholder_label.pack(expand=True)
            
        except Exception as e:
            print(f"Error al configurar la interfaz: {str(e)}")
            # Crear una interfaz mínima en caso de error
            error_label = ctk.CTkLabel(
                self,
                text="Error al cargar la interfaz de estadísticas",
                font=("Arial", 16),
                text_color="#DC3545"
            )
            error_label.pack(expand=True)
    
    def create_kpi_widgets(self):
        """Crea los widgets para mostrar los KPIs"""
        try:
            # Definir los KPIs con sus configuraciones
            kpis_config = [
                {
                    'key': 'total_ventas',
                    'title': 'Total Ventas',
                    'icon': '💰',
                    'color': '#28A745',
                    'row': 0,
                    'col': 0
                },
                {
                    'key': 'total_pedidos',
                    'title': 'Total Pedidos',
                    'icon': '📦',
                    'color': '#007BFF',
                    'row': 0,
                    'col': 1
                },
                {
                    'key': 'ticket_promedio',
                    'title': 'Ticket Promedio',
                    'icon': '🎫',
                    'color': '#FFC107',
                    'row': 0,
                    'col': 2
                },
                {
                    'key': 'conversion_rate',
                    'title': 'Tasa de Conversión',
                    'icon': '📊',
                    'color': '#6F42C1',
                    'row': 0,
                    'col': 3
                }
            ]
            
            # Crear los widgets de KPI
            self.kpi_widgets = {}
            for kpi_config in kpis_config:
                try:
                    kpi_widget = self.create_kpi_card(
                        self.kpis_frame,
                        kpi_config['title'],
                        kpi_config['icon'],
                        kpi_config['color']
                    )
                    
                    if kpi_widget:
                        kpi_widget.grid(
                            row=kpi_config['row'],
                            column=kpi_config['col'],
                            padx=10,
                            pady=10,
                            sticky="ew"
                        )
                        self.kpi_widgets[kpi_config['key']] = kpi_widget
                except Exception as e:
                    print(f"Error al crear widget KPI {kpi_config['key']}: {str(e)}")
                    continue
                
        except Exception as e:
            print(f"Error al crear widgets KPI: {str(e)}")
            self.kpi_widgets = {}
    
    def create_kpi_card(self, parent, title, icon, color):
        """Crea una tarjeta individual para un KPI"""
        try:
            # Frame principal de la tarjeta
            card = ctk.CTkFrame(
                parent,
                fg_color="#FFFFFF",
                corner_radius=15,
                border_width=1,
                border_color="#E9ECEF"
            )
            
            # Frame superior con icono y título
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            # Icono
            try:
                icon_label = ctk.CTkLabel(
                    header_frame,
                    text=icon,
                    font=("Arial", 24)  # Cambiar fuente para evitar problemas
                )
                icon_label.pack(side="left")
            except Exception as e:
                print(f"Error al crear icono: {str(e)}")
                # Icono de fallback
                icon_label = ctk.CTkLabel(
                    header_frame,
                    text="📊",
                    font=("Arial", 24)
                )
                icon_label.pack(side="left")
            
            # Título
            title_label = ctk.CTkLabel(
                header_frame,
                text=title,
                font=("Arial", 14, "bold"),
                text_color="#495057"
            )
            title_label.pack(side="right")
            
            # Valor principal
            value_label = ctk.CTkLabel(
                card,
                text="Cargando...",
                font=("Arial", 28, "bold"),
                text_color=color
            )
            value_label.pack(pady=(0, 10))
            
            # Frame para crecimiento (si aplica)
            growth_frame = ctk.CTkFrame(card, fg_color="transparent")
            growth_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            growth_label = ctk.CTkLabel(
                growth_frame,
                text="",
                font=("Arial", 12),
                text_color="#6C757D"
            )
            growth_label.pack()
            
            # Almacenar referencias a los labels
            card.value_label = value_label
            card.growth_label = growth_label
            
            return card
            
        except Exception as e:
            print(f"Error al crear tarjeta KPI: {str(e)}")
            # Retornar un frame básico en caso de error
            return ctk.CTkFrame(parent, fg_color="#FFFFFF")
    
    def get_date_range(self, periodo):
        """Obtiene el rango de fechas según el período seleccionado"""
        try:
            today = datetime.now()
            
            if periodo == "Últimos 7 días":
                start_date = today - timedelta(days=7)
            elif periodo == "Último mes":
                start_date = today - timedelta(days=30)
            elif periodo == "Últimos 3 meses":
                start_date = today - timedelta(days=90)
            elif periodo == "Año actual":
                start_date = datetime(today.year, 1, 1)
            else:
                start_date = today - timedelta(days=30)
            
            return start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
            
        except Exception as e:
            print(f"Error al obtener rango de fechas: {str(e)}")
            # Retornar último mes por defecto
            today = datetime.now()
            start_date = today - timedelta(days=30)
            return start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales"""
        self.actualizar_datos()
    
    def on_periodo_changed(self, value):
        """Se ejecuta cuando cambia el período seleccionado"""
        self.actualizar_datos()
    
    def actualizar_datos(self):
        """Actualiza los datos de los KPIs"""
        try:
            # Deshabilitar botón mientras carga
            if hasattr(self, 'btn_refresh'):
                self.btn_refresh.configure(state="disabled", text="Cargando...")
            
            # Obtener rango de fechas
            fecha_inicio, fecha_fin = self.get_date_range(self.periodo_var.get())
            
            # Hacer petición a la API
            self.cargar_kpis(fecha_inicio, fecha_fin)
            
        except Exception as e:
            print(f"Error al actualizar datos: {str(e)}")
            messagebox.showerror("Error", f"Error al actualizar datos: {str(e)}")
        finally:
            # Habilitar botón nuevamente
            if hasattr(self, 'btn_refresh'):
                self.btn_refresh.configure(state="normal", text="Actualizar")
    
    def cargar_kpis(self, fecha_inicio, fecha_fin):
        """Carga los KPIs desde la API"""
        try:
            # Construir URL con parámetros
            url = f"{REPORTS_ENDPOINTS['data_kpis']}?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}"
            print(f"Solicitando KPIs desde: {url}")
            
            # Obtener token de sesión
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            # Hacer petición
            response = APIHandler.make_request('get', url, headers=headers)
            print(f"Respuesta de KPIs: {response}")
            
            if response.get('status_code') == 200:
                data = response.get('data', {})
                self.kpis_data = data.get('data', {})
                self.actualizar_widgets_kpis()
            else:
                error_msg = response.get('message', 'Error desconocido')
                print(f"Error en API: {error_msg}")
                # No mostrar error, solo usar datos vacíos
                self.kpis_data = {}
                self.mostrar_datos_fallback()
                
        except Exception as e:
            print(f"Error al conectar con la API: {str(e)}")
            # No mostrar error, solo usar datos de fallback
            self.kpis_data = {}
            self.mostrar_datos_fallback()
    
    def mostrar_datos_fallback(self):
        """Muestra datos de ejemplo cuando no se puede conectar a la API"""
        try:
            # Datos de ejemplo
            self.kpis_data = {
                'total_ventas': {
                    'valor': 0,
                    'formato': 'currency',
                    'crecimiento': 0
                },
                'total_pedidos': {
                    'valor': 0,
                    'formato': 'number',
                    'crecimiento': 0
                },
                'ticket_promedio': {
                    'valor': 0,
                    'formato': 'currency'
                },
                'conversion_rate': {
                    'valor': 0,
                    'formato': 'percentage'
                }
            }
            self.actualizar_widgets_kpis()
        except Exception as e:
            print(f"Error en datos fallback: {str(e)}")
    
    def actualizar_widgets_kpis(self):
        """Actualiza los widgets con los datos de los KPIs"""
        try:
            if not hasattr(self, 'kpi_widgets') or not self.kpi_widgets:
                print("No hay widgets KPI disponibles")
                return
                
            for kpi_key, widget in self.kpi_widgets.items():
                if not widget or not hasattr(widget, 'value_label'):
                    continue
                    
                if kpi_key in self.kpis_data:
                    kpi_data = self.kpis_data[kpi_key]
                    
                    # Formatear valor según el tipo
                    valor = kpi_data.get('valor', 0)
                    formato = kpi_data.get('formato', 'number')
                    
                    if formato == 'currency':
                        formatted_value = f"S/. {valor:,.2f}"
                    elif formato == 'percentage':
                        formatted_value = f"{valor:.1f}%"
                    else:
                        formatted_value = f"{valor:,}"
                    
                    # Actualizar valor
                    widget.value_label.configure(text=formatted_value)
                    
                    # Actualizar crecimiento si existe
                    if hasattr(widget, 'growth_label') and 'crecimiento' in kpi_data:
                        crecimiento = kpi_data['crecimiento']
                        if crecimiento > 0:
                            growth_text = f"↗ +{crecimiento}% vs período anterior"
                            growth_color = "#28A745"
                        elif crecimiento < 0:
                            growth_text = f"↘ {crecimiento}% vs período anterior"
                            growth_color = "#DC3545"
                        else:
                            growth_text = "→ Sin cambios vs período anterior"
                            growth_color = "#6C757D"
                        
                        widget.growth_label.configure(
                            text=growth_text,
                            text_color=growth_color
                        )
                    elif hasattr(widget, 'growth_label'):
                        widget.growth_label.configure(text="")
                else:
                    # Si no hay datos, mostrar mensaje
                    widget.value_label.configure(text="Sin datos")
                    if hasattr(widget, 'growth_label'):
                        widget.growth_label.configure(text="")
                    
        except Exception as e:
            print(f"Error al actualizar widgets: {str(e)}")
            # No mostrar messagebox para evitar interrumpir la UI


def main():
    """Función principal para pruebas"""
    root = ctk.CTk()
    root.title("Estadísticas de Ventas")
    root.geometry("1200x800")
    
    app = EstadisticasVentas(root)
    
    root.mainloop()


if __name__ == "__main__":
    main()
