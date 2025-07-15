import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter as tk
from tkinter import ttk
from src.core.config import PAYMENTS_ENDPOINTS, UI_CONFIG, ORDERS_ENDPOINTS
from src.core.status_config import (
    EstadosPago, obtener_color_estado, obtener_label_estado,
    EstadosDeprecados, FiltrosUI
)
from src.shared.utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from src.shared.image_handler import ImageHandler
from src.interfaces.management.orders_management import DetallesPedidoDialog

# --- COLORES ---
PRIMARY_COLOR = "#3A6B5D"
ACCENT_COLOR = "#EC0617"
SECONDARY_COLOR = "#3E526B"
HIGHLIGHT_COLOR = "#3F4F2A"
TEXT_COLOR = "#000000"

# --- CONFIGURACIÓN DE UI ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# --- FUNCIONES DE API ---
def obtener_pagos():
    """Obtener todos los pagos desde la API"""
    try:
        # Verificar usuario autenticado antes de hacer la petición
        user_data = SessionManager.get_user_data()
        token = SessionManager.get_token()
        print(f"🔍 Usuario en obtener_pagos: {user_data}")
        print(f"🔍 Rol del usuario: {user_data.get('roles_id_rol') if user_data else 'N/A'}")
        
        url = PAYMENTS_ENDPOINTS['list']
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', url, headers=headers)
        if response['status_code'] == 200:
            return response['data'].get('pagos', [])
    except Exception as e:
        print("Error al obtener pagos:", e)
    return []

def obtener_estadisticas_pagos():
    """Obtener estadísticas de pagos desde la API"""
    try:
        url = PAYMENTS_ENDPOINTS['statistics']
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', url, headers=headers)
        if response['status_code'] == 200:
            return response['data'].get('statistics', {})
    except Exception as e:
        print("Error al obtener estadísticas de pagos:", e)
    return {}

def obtener_metodos_pago():
    """Obtener métodos de pago disponibles"""
    try:
        url = PAYMENTS_ENDPOINTS['payment_methods']
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', url, headers=headers)
        if response['status_code'] == 200:
            return response['data'].get('payment_methods', [])
    except Exception as e:
        print("Error al obtener métodos de pago:", e)
    return []

def obtener_pedido_completo_backend(pedido_id):
    from src.core.config import ORDERS_ENDPOINTS
    from src.shared.utils import APIHandler, SessionManager
    try:
        url = ORDERS_ENDPOINTS['detail'].format(id=pedido_id)
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', url, headers=headers)
        if response.get('status_code') == 200:
            return response.get('data')
    except Exception as e:
        print(f"Error al obtener pedido completo: {e}")
    return None

# --- CLASE PRINCIPAL DE INTERFAZ ---
class GestionPagos(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Inicializar variables de datos
            self.pagos = []
            self.pagos_originales = []
            self.pagos_filtrados = []
            self.estadisticas = {}
            self.metodos_pago = []
            self.tabla_pago_map = {}  # Mapa para vincular filas de tabla con IDs de pago
            self._dialog_abierto = False  # Flag para prevenir múltiples diálogos
            
            # Frame superior
            top_frame = ctk.CTkFrame(self, fg_color="transparent")
            top_frame.pack(fill="x", pady=(0, 20))
            
            # Contenedor izquierdo para título y búsqueda
            left_container = ctk.CTkFrame(top_frame, fg_color="transparent")
            left_container.pack(side="left", fill="both", expand=True, padx=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(left_container, fg_color="#FFFFFF", corner_radius=10)
            title_frame.pack(fill="x", pady=(0, 10))
            
            title_content = ctk.CTkFrame(title_frame, fg_color="#FFFFFF")
            title_content.pack(side="left", padx=20, pady=15)
            
            try:
                # Cargar y redimensionar icono
                icon = Image.open(os.path.join("assets", "images", "icons", "pagos.png"))
                icon = icon.resize((32, 32))
                self.icon_image = ctk.CTkImage(light_image=icon, dark_image=icon, size=(32, 32))
                ctk.CTkLabel(
                    title_content,
                    image=self.icon_image,
                    text=""
                ).pack(side="left", padx=(0, 10))
            except:
                pass
                
            ctk.CTkLabel(
                title_content,
                text="💳 Gestión de Pagos",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left")
            
            # Frame para búsqueda y filtros (ahora en el contenedor izquierdo)
            search_frame = ctk.CTkFrame(left_container, fg_color="#FFFFFF", corner_radius=10)
            search_frame.pack(fill="x")
            
            # Búsqueda
            search_label = ctk.CTkLabel(
                search_frame,
                text="🔍",
                font=("Quicksand", 16)
            )
            search_label.pack(side="left", padx=(15, 5), pady=10)
            
            self.search_var = ctk.StringVar()
            self.search_var.trace("w", self.filtrar_tabla)
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=self.search_var,
                width=300,
                placeholder_text="Buscar por cliente, número de pedido, referencia o monto...",
                border_width=0,
                fg_color="#F5F5F5"
            )
            search_entry.pack(side="left", padx=5, pady=10)
            
            # Filtro por estado
            ctk.CTkLabel(
                search_frame,
                text="Estado:",
                font=("Quicksand", 12)
            ).pack(side="left", padx=(20, 5), pady=10)
            
            self.estado_var = ctk.StringVar(value="Todos")
            self.estado_var.trace("w", self.filtrar_tabla)
            estado_menu = ctk.CTkOptionMenu(
                search_frame,
                values=FiltrosUI.OPCIONES_FILTRO_PAGOS,
                variable=self.estado_var,
                width=120,
                fg_color="#2E6B5C",
                button_color="#1D4A3C",
                button_hover_color="#153A2C",
                dropdown_fg_color="#FFFFFF",
                dropdown_hover_color="#F5F5F5",
                dropdown_text_color="#2E6B5C"
            )
            estado_menu.pack(side="left", padx=5, pady=10)
            
            # Panel de estadísticas (ahora a la derecha)
            stats_frame = ctk.CTkFrame(top_frame, fg_color="#FFFFFF", corner_radius=10)
            stats_frame.pack(side="right")
            
            self.crear_panel_estadisticas(stats_frame)
            
            # Tabla de pagos
            self.tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            self.tabla_frame.pack(fill="both", expand=True)
            
            # Frame para tabla y botones de acción
            tabla_container = ctk.CTkFrame(self.tabla_frame, fg_color="#FFFFFF")
            tabla_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Crear tabla con columnas simplificadas
            self.tabla = ttk.Treeview(
                tabla_container,
                columns=("cliente", "monto", "estado", "metodo", "fecha"),
                show="headings",
                style="Custom.Treeview"
            )
            
            # Configurar columnas
            self.tabla.heading("cliente", text="Cliente")
            self.tabla.heading("monto", text="Monto")
            self.tabla.heading("estado", text="Estado")
            self.tabla.heading("metodo", text="Método de Pago")
            self.tabla.heading("fecha", text="Fecha")
            
            # Configurar anchuras de columnas para que se adapten
            self.tabla.column("cliente", anchor="w", minwidth=150, stretch=True)
            self.tabla.column("monto", anchor="center", minwidth=100, width=120, stretch=False)
            self.tabla.column("estado", anchor="center", minwidth=100, width=120, stretch=False)
            self.tabla.column("metodo", anchor="center", minwidth=140, width=160, stretch=False)
            self.tabla.column("fecha", anchor="center", minwidth=130, width=150, stretch=False)
            
            
            # Scrollbar vertical
            scrollbar_v = ttk.Scrollbar(
                tabla_container,
                orient="vertical",
                command=self.tabla.yview
            )
            self.tabla.configure(yscrollcommand=scrollbar_v.set)
            
            # Scrollbar horizontal
            scrollbar_h = ttk.Scrollbar(
                tabla_container,
                orient="horizontal",
                command=self.tabla.xview
            )
            self.tabla.configure(xscrollcommand=scrollbar_h.set)
            
            # Empaquetar tabla y scrollbars
            self.tabla.grid(row=0, column=0, sticky="nsew")
            scrollbar_v.grid(row=0, column=1, sticky="ns")
            scrollbar_h.grid(row=1, column=0, sticky="ew")
            
            # Configurar grid weights para redimensionamiento
            tabla_container.grid_rowconfigure(0, weight=1)
            tabla_container.grid_columnconfigure(0, weight=1)
            
            # Bind de eventos
            self.tabla.bind("<Double-1>", self.mostrar_detalles_completos)
            
            # Cargar datos
            self.cargar_datos()
            
            # Configurar estilos de la tabla
            style = ttk.Style()
            style.theme_use("clam")
            
            # Configurar el estilo de la tabla
            style.configure("Custom.Treeview",
                           background="#FFFFFF",
                           foreground="#000000",
                           fieldbackground="#FFFFFF",
                           borderwidth=1,
                           relief="solid",
                           rowheight=35)
            
            style.configure("Custom.Treeview.Heading",
                           background="#2E6B5C",
                           foreground="#FFFFFF",
                           font=("Quicksand", 12, "bold"),
                           relief="flat",
                           borderwidth=1)
            
            # Configurar colores de selección y estados
            style.map("Custom.Treeview",
                     background=[('selected', '#C8E6C9'),
                                ('focus', '#E8F5E8')],
                     foreground=[('selected', '#1B5E20'),
                                ('focus', '#2E7D32')])
            
            # Configurar estilo del encabezado cuando está seleccionado
            style.map("Custom.Treeview.Heading",
                     background=[('active', '#1D4A3C'),
                                ('pressed', '#153A2C')],
                     foreground=[('active', '#FFFFFF'),
                                ('pressed', '#FFFFFF')])
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar: {str(e)}")
    
    def crear_panel_estadisticas(self, parent):
        """Crear panel de estadísticas"""
        try:
            ctk.CTkLabel(
                parent,
                text="📊 Estadísticas",
                font=("Quicksand", 16, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(15, 10))
            
            stats_grid = ctk.CTkFrame(parent, fg_color="#FFFFFF")
            stats_grid.pack(padx=15, pady=(0, 15))
            
            # Inicializar labels de estadísticas
            self.stats_labels = {}
            
            stats_info = [
                ("total_pagos", "Total Pagos:", "0"),
                ("completados", "Completados:", "0"),
                ("pendientes", "Pendientes:", "0"),
                ("monto_total", "Monto Total:", "S/ 0.00")
            ]
            
            for i, (key, label, default) in enumerate(stats_info):
                ctk.CTkLabel(
                    stats_grid,
                    text=label,
                    font=("Quicksand", 10, "bold"),
                    text_color="#2E6B5C"
                ).grid(row=i, column=0, sticky="w", padx=(10, 5), pady=2)
                
                self.stats_labels[key] = ctk.CTkLabel(
                    stats_grid,
                    text=default,
                    font=("Quicksand", 10),
                    text_color="#000000"
                )
                self.stats_labels[key].grid(row=i, column=1, sticky="e", padx=(5, 10), pady=2)
                
        except Exception as e:
            print(f"Error al crear panel de estadísticas: {str(e)}")
    
    def actualizar_estadisticas(self):
        """Actualizar las estadísticas mostradas"""
        try:
            self.estadisticas = obtener_estadisticas_pagos()
            
            if self.estadisticas:
                overview = self.estadisticas.get('overview', {})
                
                self.stats_labels['total_pagos'].configure(
                    text=str(overview.get('total_payments', 0))
                )
                self.stats_labels['completados'].configure(
                    text=str(len([p for p in self.pagos if p.get('estado_pago') == EstadosPago.COMPLETADO]))
                )
                self.stats_labels['pendientes'].configure(
                    text=str(len([p for p in self.pagos if p.get('estado_pago') == 'pendiente']))
                )
                self.stats_labels['monto_total'].configure(
                    text=f"S/ {overview.get('total_amount', 0):.2f}"
                )
                
        except Exception as e:
            print(f"Error al actualizar estadísticas: {str(e)}")
    
    def cargar_datos(self):
        """Cargar datos de pagos desde la API"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar pagos
            self.pagos = obtener_pagos()
            self.pagos_originales = self.pagos.copy()
            
            # Cargar datos en la tabla
            for i, pago in enumerate(self.pagos):
                # Configurar tags para el estado y filas alternas
                estado = pago.get('estado_pago', '').lower()
                row_type = "evenrow" if i % 2 == 0 else "oddrow"
                tags = (estado, row_type)
                
                # Obtener información del método de pago desde la API
                metodo_nombre = pago.get('metodo_pago_nombre_snapshot', 'N/A')
                if not metodo_nombre or metodo_nombre == 'N/A':
                    metodo_info = pago.get('metodos_pago', {})
                    metodo_nombre = metodo_info.get('nombre', 'N/A')
                
                # Obtener información del cliente y pedido
                pedido_info = pago.get('pedido', {})
                usuario_info = pedido_info.get('usuario', {})
                nombre = usuario_info.get('nombre', '')
                apellidos = usuario_info.get('apellidos', '')
                cliente_nombre = f"{nombre} {apellidos}".strip()
                if not cliente_nombre:
                    cliente_nombre = usuario_info.get('email', 'Cliente desconocido')
                
                # Insertar fila en la tabla
                fila_id = self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente_nombre,
                        f"S/ {float(pago.get('monto_pago', 0)):.2f}",
                        pago.get('estado_pago', '').title(),
                        metodo_nombre,
                        DateTimeHelper.format_datetime(pago.get('fecha_pago', ''))
                    ),
                    tags=tags
                )
                
                # Vincular ID de pago con fila de tabla
                self.tabla_pago_map[fila_id] = pago.get('id_pago')
                
            # Configurar colores de estado usando la configuración estandarizada
            for estado in EstadosPago.get_all():
                color = obtener_color_estado('pago', estado)
                self.tabla.tag_configure(estado, foreground=color)
            
            # Configurar filas alternas para mejor visualización
            self.tabla.tag_configure("oddrow", background="#F8F9FA")
            self.tabla.tag_configure("evenrow", background="#FFFFFF")
            
            # Actualizar estadísticas
            self.actualizar_estadisticas()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def filtrar_tabla(self, *args):
        """Filtrar tabla según los criterios de búsqueda"""
        try:
            # Obtener valores de filtro
            busqueda = self.search_var.get().lower()
            estado = self.estado_var.get()
            
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Filtrar y cargar datos
            filtered_count = 0
            for pago in self.pagos:
                # Aplicar filtros
                if estado != "Todos" and pago.get('estado_pago', '').lower() != estado.lower():
                    continue
                    
                # Obtener información del cliente y pedido para búsqueda
                pedido_info = pago.get('pedido', {})
                usuario_info = pedido_info.get('usuario', {})
                nombre = usuario_info.get('nombre', '')
                apellidos = usuario_info.get('apellidos', '')
                cliente_nombre = f"{nombre} {apellidos}".strip()
                if not cliente_nombre:
                    cliente_nombre = usuario_info.get('email', 'Cliente desconocido')
                numero_pedido = pedido_info.get('numero_pedido', '') or f"PED-{pedido_info.get('id_pedido', '')}"
                    
                if busqueda and not any(
                    busqueda in str(valor).lower()
                    for valor in [
                        cliente_nombre,
                        numero_pedido,
                        str(pago.get('monto_pago', '')),
                        pago.get('referencia_pago', ''),
                        pago.get('estado_pago', '')
                    ]
                ):
                    continue
                    
                # Configurar tags para el estado y filas alternas
                estado_pago = pago.get('estado_pago', '').lower()
                row_type = "evenrow" if filtered_count % 2 == 0 else "oddrow"
                tags = (estado_pago, row_type)
                
                # Obtener información del método de pago
                metodo_nombre = pago.get('metodo_pago_nombre_snapshot', 'N/A')
                if not metodo_nombre or metodo_nombre == 'N/A':
                    metodo_info = pago.get('metodos_pago', {})
                    metodo_nombre = metodo_info.get('nombre', 'N/A')
                
                # Insertar fila
                fila_id = self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente_nombre,
                        f"S/ {float(pago.get('monto_pago', 0)):.2f}",
                        pago.get('estado_pago', '').title(),
                        metodo_nombre,
                        DateTimeHelper.format_datetime(pago.get('fecha_pago', ''))
                    ),
                    tags=tags
                )
                
                # Vincular ID de pago con fila de tabla
                self.tabla_pago_map[fila_id] = pago.get('id_pago')
                filtered_count += 1
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar datos: {str(e)}")
    
    def mostrar_detalles_completos(self, event):
        """Mostrar detalles completos del pago con doble clic"""
        try:
            # Prevenir múltiples llamadas rápidas
            if hasattr(self, '_dialog_abierto') and self._dialog_abierto:
                return
                
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                return
                
            # Obtener ID del pago desde el mapa
            fila_id = seleccion[0]
            pago_id = self.tabla_pago_map.get(fila_id)
            
            if not pago_id:
                messagebox.showwarning("Advertencia", "No se pudo identificar el pago seleccionado")
                return
                
            # Marcar que hay un diálogo abierto
            self._dialog_abierto = True
            
            # Buscar el pago completo en los datos
            pago = next((p for p in self.pagos if p.get('id_pago') == pago_id), None)
            
            if pago:
                # Crear diálogo de detalles completos usando la nueva API
                self.cargar_detalles_completos(pago_id)
            else:
                messagebox.showerror("Error", "No se encontraron los datos del pago")
            
            # Restablecer el flag después de un breve delay
            self.after(1000, lambda: setattr(self, '_dialog_abierto', False))
                    
        except Exception as e:
            # Asegurar que se restablezca el flag en caso de error
            self._dialog_abierto = False
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
    
    def cargar_detalles_completos(self, pago_id):
        """Cargar detalles completos del pago desde la nueva API"""
        try:
            # Validar que el widget principal aún existe
            if not self.winfo_exists():
                return
                
            from src.shared.utils import APIHandler, SessionManager
            
            # Hacer petición a la nueva API de detalles completos
            url = PAYMENTS_ENDPOINTS['details'].format(id=pago_id)
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('get', url, headers=headers)
            
            if response['status_code'] == 200:
                # La estructura de respuesta cambió
                data = response['data']
                pago_completo = data.get('data', {}).get('pago') or data.get('pago')
                
                if pago_completo:
                    # Agregar los datos adicionales al pago
                    if 'data' in data and data['data']:
                        pago_completo['pedido_items_extra'] = data['data'].get('pedido_items', [])
                        pago_completo['envios_extra'] = data['data'].get('envios', [])
                    
                    # Validar nuevamente que el widget existe antes de crear el diálogo
                    if self.winfo_exists():
                        # Mostrar diálogo con los detalles completos
                        dialog = DetallesPagoCompletoDialog(self, pago_completo)
                        # Restablecer el flag cuando se cierre el diálogo
                        def on_dialog_close():
                            self._dialog_abierto = False
                        if hasattr(dialog, 'dialog') and dialog.dialog is not None and hasattr(dialog.dialog, 'bind'):
                            dialog.dialog.bind('<Destroy>', lambda e: on_dialog_close())
                    else:
                        messagebox.showerror("Error", "Estructura de datos de pago inválida")
            else:
                error_data = response.get('data', {})
                error_msg = error_data.get('debug', error_data.get('error', 'Error desconocido'))
                if self.winfo_exists():
                    messagebox.showerror("Error", f"No se pudieron cargar los detalles del pago: {error_msg}")
                
        except Exception as e:
            if self.winfo_exists():
                messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
        finally:
            # Asegurar que se restablezca el flag
            self._dialog_abierto = False
    
    def crear_mensaje_sin_envio(self, parent, pago):
        """Crear mensaje cuando no hay información de envío"""
        try:
            envio_frame = ctk.CTkFrame(parent, fg_color="#FFF3E0", corner_radius=10)
            envio_frame.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                envio_frame,
                text="📦 Información de Envío",
                font=("Quicksand", 16, "bold"),
                text_color="#FF8C00"
            ).pack(pady=(15, 10))
            
            ctk.CTkLabel(
                envio_frame,
                text="ℹ️ Este pedido aún no tiene información de envío asignada",
                font=("Quicksand", 12),
                text_color="#FF8C00"
            ).pack(pady=(0, 15))
            
        except Exception as e:
            print(f"Error al crear mensaje sin envío: {str(e)}")

# --- CLASES DE DIÁLOGO ---
class DetallesPagoCompletoDialog:
    """Diálogo mejorado para mostrar detalles completos de un pago con diseño compacto y eficiente"""
    
    def __init__(self, parent, pago):
        self.parent = parent  # Guarda el parent para usarlo en los botones
        self.dialog = None
        self.closed = False
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("Pago")
            self.dialog.geometry("750x560")  # Aumentado de 750x450 a 850x550
            self.dialog.resizable(True, True)
            self.dialog.minsize(750, 560)  # Aumentado el mínimo también

            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()

            # Proteger contra cierre abrupto
            self.dialog.protocol("WM_DELETE_WINDOW", self.safe_close)

            # Centrar ventana de forma segura
            try:
                self.dialog.update_idletasks()
                width = self.dialog.winfo_width()
                height = self.dialog.winfo_height()
                x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
                self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            except:
                pass

            # Frame principal sin scroll (eliminar scroll innecesario)
            scrollable_frame = ctk.CTkFrame(self.dialog, fg_color="#F5F5F5")
            scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Título principal compacto (solo 'Pago')
            header_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2E6B5C", corner_radius=10)
            header_frame.pack(fill="x", padx=10, pady=(5, 8))
            
            ctk.CTkLabel(
                header_frame,
                text="💳 Pago",
                font=("Quicksand", 16, "bold"),
                text_color="#FFFFFF"
            ).pack(pady=8)
            
            # SECCIÓN 1: CARDS DE INFORMACIÓN RÁPIDA (3 columnas)
            self.crear_cards_resumen(scrollable_frame, pago)
            
            # SECCIÓN 2: INFORMACIÓN DETALLADA (2 columnas)
            self.crear_seccion_detallada(scrollable_frame, pago)
            

        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
            self.safe_close()
    
    def safe_close(self):
        """Cierre seguro del diálogo"""
        try:
            if hasattr(self, 'dialog') and self.dialog is not None:
                try:
                    if self.dialog.winfo_exists():
                        self.dialog.grab_release()
                        self.dialog.destroy()
                except Exception as e:
                    # Evitar error si la app ya fue destruida
                    if 'application has been destroyed' not in str(e):
                        print(f"Error al cerrar diálogo: {e}")
                self.dialog = None
        except Exception as e:
            print(f"Error al cerrar diálogo: {e}")
    
    def __del__(self):
        """Destructor para limpieza de recursos"""
        try:
            self.safe_close()
        except Exception:
            pass  # Ignorar errores en el destructor
    
    def crear_cards_resumen(self, parent, pago):
        """Crear cards de resumen con información clave"""
        try:
            cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
            cards_frame.pack(fill="x", padx=10, pady=5)
            
            # Obtener datos del pago y pedido
            pedido = pago.get('pedido', {})
            usuario = pedido.get('usuario', {})
            
            # CARD 1: Información del Pago
            card_pago = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=10)
            card_pago.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            ctk.CTkLabel(
                card_pago,
                text="💳 PAGO",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(15, 5))
            
            estado_color = self.obtener_color_estado(pago.get('estado_pago', ''))
            ctk.CTkLabel(
                card_pago,
                text=f"S/ {float(pago.get('monto_pago', 0)):.2f}",
                font=("Quicksand", 14, "bold"),
                text_color="#000000"
            ).pack(pady=2)
            
            ctk.CTkLabel(
                card_pago,
                text=pago.get('estado_pago', 'N/A').upper(),
                font=("Quicksand", 12, "bold"),
                text_color=estado_color
            ).pack(pady=2)
            
            ctk.CTkLabel(
                card_pago,
                text=pago.get('metodo_pago_nombre_snapshot', 
                           pago.get('metodos_pago', {}).get('nombre', 'N/A')),
                font=("Quicksand", 12),
                text_color="#666666"
            ).pack(pady=(2, 15))
            
            # CARD 2: Información del Pedido
            card_pedido = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=10)
            card_pedido.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(
                card_pedido,
                text="📦 PEDIDO",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                card_pedido,
                text=f"#{pedido.get('id_pedido', 'N/A')}",
                font=("Quicksand", 14, "bold"),
                text_color="#000000"
            ).pack(pady=2)
            
            ctk.CTkLabel(
                card_pedido,
                text=pedido.get('estado', 'N/A').upper(),
                font=("Quicksand", 12, "bold"),
                text_color="#FF8C00"
            ).pack(pady=2)
            
            # Botón "Ver Pedido" debajo del estado (funcionalidad deshabilitada temporalmente)
            ver_pedido_btn = ctk.CTkButton(
                card_pedido,
                text="Ver Pedido",
                font=("Quicksand", 12, "bold"),
                fg_color="#3A6B5D",
                hover_color="#3F4F2A",
                text_color="#FFFFFF",
                height=25,
                width=80,
                command=lambda p=pedido: self.abrir_detalle_pedido_local(p)
            )
            ver_pedido_btn.pack(pady=(5, 15))
            
            # CARD 3: Información del Cliente
            card_cliente = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=10)
            card_cliente.pack(side="left", fill="both", expand=True, padx=(5, 0))
            
            ctk.CTkLabel(
                card_cliente,
                text="👤 CLIENTE",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(15, 5))

            # Mostrar nombre completo y apellidos (campo 'apellidos')
            nombre = usuario.get('nombre', '')
            apellidos = usuario.get('apellidos', '')
            nombre_completo = f"{nombre} {apellidos}".strip()
            if not nombre_completo:
                nombre_completo = usuario.get('email', 'Cliente desconocido')

            # Truncar nombre si es muy largo
            if len(nombre_completo) > 30:
                nombre_display = nombre_completo[:27] + "..."
            else:
                nombre_display = nombre_completo

            ctk.CTkLabel(
                card_cliente,
                text=nombre_display,
                font=("Quicksand", 14, "bold"),
                text_color="#000000"
            ).pack(pady=2)

            ctk.CTkLabel(
                card_cliente,
                text=f"Tel: {usuario.get('telefono', 'N/A')}",
                font=("Quicksand", 12),
                text_color="#666666"
            ).pack(pady=2)

            ctk.CTkLabel(
                card_cliente,
                text=usuario.get('email', 'N/A')[:35] + "..." if len(usuario.get('email', '')) > 35 else usuario.get('email', 'N/A'),
                font=("Quicksand", 12),
                text_color="#666666"
            ).pack(pady=(2, 15))
            
        except Exception as e:
            print(f"Error al crear cards de resumen: {str(e)}")
    
    def crear_seccion_detallada(self, parent, pago):
        """Crear sección con información detallada de pago en el orden clásico solicitado"""
        try:
            detalle_frame = ctk.CTkFrame(parent, fg_color="transparent")
            detalle_frame.pack(fill="x", padx=10, pady=5)
            
            left_frame = ctk.CTkFrame(detalle_frame, fg_color="#FFFFFF", corner_radius=10)
            left_frame.pack(fill="both", expand=True)
            
            # Título de la sección
            ctk.CTkLabel(
                left_frame,
                text="📋 Detalles del Pago",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(15, 10))
            
            # Obtener datos necesarios
            monto_pago = float(pago.get('monto_pago', 0))
            metodo_pago = pago.get('metodo_pago_nombre_snapshot', pago.get('metodos_pago', {}).get('nombre', 'N/A'))
            fecha_pago = DateTimeHelper.format_datetime(pago.get('fecha_pago', ''))
            
            # Calcular monto de envío
            monto_envio = 0
            if pago.get('envios_extra') and len(pago['envios_extra']) > 0:
                monto_envio = float(pago['envios_extra'][0].get('monto_envio', 0))
            elif pago.get('pedido', {}).get('envios') and len(pago['pedido']['envios']) > 0:
                monto_envio = float(pago['pedido']['envios'][0].get('monto_envio', 0))
            
            # Calcular subtotal de items
            pedido_items = []
            if pago.get('pedido_items_extra'):
                pedido_items = pago['pedido_items_extra']
            elif pago.get('pedido', {}).get('pedido_items'):
                pedido_items = pago['pedido']['pedido_items']
            subtotal_items = sum(float(item.get('subtotal', 0)) for item in pedido_items)
            
            # Total del pedido
            pedido = pago.get('pedido', {})
            monto_total = float(pedido.get('monto_total', 0))
            
            # ORDEN CLÁSICO SOLICITADO:
            # 1. Fecha de Pago
            self.crear_fila_detalle_clasica(left_frame, "Fecha de Pago:", fecha_pago)
            
            # 2. Método de Pago
            self.crear_fila_detalle_clasica(left_frame, "Método de Pago:", metodo_pago)
            
            # 3. Monto del Pago
            self.crear_fila_detalle_clasica(left_frame, "Monto del Pago:", f"S/ {monto_pago:.2f}")
            
            # 4. Subtotal de Items
            self.crear_fila_detalle_clasica(left_frame, "Subtotal de Items:", f"S/ {subtotal_items:.2f}")
            
            # 5. Monto de Envío
            self.crear_fila_detalle_clasica(left_frame, "Monto de Envío:", f"S/ {monto_envio:.2f}")
            
            # Separador
            separador = ctk.CTkFrame(left_frame, fg_color="#E0E0E0", height=2)
            separador.pack(fill="x", padx=15, pady=10)
            
            # 6. Total del Pedido (RESALTADO AL FINAL)
            total_frame = ctk.CTkFrame(left_frame, fg_color="#E8F5E8", corner_radius=8)
            total_frame.pack(fill="x", padx=15, pady=(5, 15))
            
            total_container = ctk.CTkFrame(total_frame, fg_color="transparent")
            total_container.pack(fill="x", padx=15, pady=12)
            
            ctk.CTkLabel(
                total_container,
                text="Total del Pedido:",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C",
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                total_container,
                text=f"S/ {monto_total:.2f}",
                font=("Quicksand", 14, "bold"),
                text_color="#1B5E20",
                anchor="e"
            ).pack(side="right")
            
        except Exception as e:
            print(f"Error al crear sección detallada: {str(e)}")
    
    def crear_fila_detalle_clasica(self, parent, label, value):
        """Crear una fila de información con el estilo clásico"""
        try:
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=4)
            
            ctk.CTkLabel(
                row_frame,
                text=label,
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C",
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=("Quicksand", 12),
                text_color="#000000",
                anchor="e"
            ).pack(side="right")
            
        except Exception as e:
            print(f"Error al crear fila de detalle clásica: {str(e)}")
    
    def crear_seccion_items_mejorada(self, parent, pedido_items):
        """Ya no se muestra la sección de items del pedido."""
        pass
    
    def crear_seccion_envio(self, parent, envios):
        """Oculta la sección de información de envío, ya no se muestra nada aquí."""
        pass
    
    def crear_fila_info_envio(self, parent, label, value, color="#666666"):
        """Crear una fila de información para la sección de envío"""
        try:
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row_frame,
                text=label,
                font=("Quicksand", 11, "bold"),
                text_color=color,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=("Quicksand", 11),
                text_color="#000000",
                anchor="e"
            ).pack(side="right")
            
        except Exception as e:
            print(f"Error al crear fila de información de envío: {str(e)}")
    
    def crear_botones_accion(self, parent, pago):
        """No mostrar botones de acción (cerrar/exportar) en el diálogo."""
        pass
    
    def crear_lista_info_compacta(self, parent, info_list):
        """Crear una lista de información en formato compacto"""
        try:
            for label, value in info_list:
                row_frame = ctk.CTkFrame(parent, fg_color="transparent")
                row_frame.pack(fill="x", padx=10, pady=3)
                
                ctk.CTkLabel(
                    row_frame,
                    text=label,
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C",
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    font=("Quicksand", 12),
                    text_color="#000000",
                    anchor="e"
                ).pack(side="right")
                
        except Exception as e:
            print(f"Error al crear lista de información: {str(e)}")
    
    def obtener_color_estado(self, estado):
        """Obtener color según el estado del pago"""
        return obtener_color_estado('pago', estado)
    
    def ver_detalles_pedido(self, pedido):
        """Mostrar detalles del pedido en un diálogo temporal"""
        try:
            from tkinter import messagebox
            # Por ahora, mostrar información básica del pedido
            info = f"Pedido #{pedido.get('id_pedido', 'N/A')}\n"
            info += f"Estado: {pedido.get('estado', 'N/A')}\n"
            info += f"Fecha: {DateTimeHelper.format_datetime(pedido.get('fecha_pedido', ''))}\n"
            info += f"Total: S/ {float(pedido.get('monto_total', 0)):.2f}\n"
            
            items = pedido.get('pedido_items', [])
            if items:
                info += f"\nItems ({len(items)}):\n"
                for item in items[:5]:  # Mostrar máximo 5 items
                    nombre = item.get('producto_nombre_snapshot', 'Producto')
                    cantidad = item.get('cantidad', 0)
                    precio = float(item.get('precio_unitario', 0))
                    info += f"• {nombre} x{cantidad} - S/ {precio:.2f}\n"
                if len(items) > 5:
                    info += f"... y {len(items) - 5} items más"
            
            messagebox.showinfo("Detalles del Pedido", info)
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error al mostrar detalles del pedido: {str(e)}")
    
    def exportar_detalles(self, pago):
        """Exportar detalles del pago a archivo"""
        try:
            # Implementar exportación de detalles
            messagebox.showinfo("Información", "Función de exportación en desarrollo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def actualizar_estado(self, pago):
        """Actualizar estado del pago desde el diálogo de detalles completo"""
        try:
            # Guardar referencia al parent antes de cerrar
            parent_window = self.parent if hasattr(self, 'parent') else None
            self.safe_close()
            # Crear diálogo de actualización de estado
            if parent_window:
                dialog = EstadoPagoDialog(parent_window, pago)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")

    def abrir_detalle_pedido_local(self, pedido_snapshot):
        from tkinter import messagebox
        pedido_id = pedido_snapshot.get('id_pedido') or pedido_snapshot.get('id') or pedido_snapshot.get('id_pedido_snapshot')
        if not pedido_id:
            messagebox.showerror("Error", "No se encontró el ID del pedido.")
            return
        
        # Buscar en la lista local de pedidos (como en la gestión de pedidos)
        try:
            # Importar la función que obtiene pedidos localmente
            from src.interfaces.management.orders_management import obtener_pedidos
            
            # Obtener la lista actualizada de pedidos
            pedidos = obtener_pedidos()
            
            # Buscar el pedido por ID
            pedido_completo = None
            for pedido in pedidos:
                if str(pedido.get("id_pedido")) == str(pedido_id):
                    pedido_completo = pedido
                    break
            
            if pedido_completo:
                from src.interfaces.management.orders_management import DetallesPedidoDialog
                DetallesPedidoDialog(self.parent, pedido_completo)
            else:
                messagebox.showerror("Error", f"No se encontró el pedido #{pedido_id} en la lista local.")
                
        except Exception as e:
            print(f"Error al buscar pedido local: {e}")
            messagebox.showerror("Error", f"Error al obtener el detalle del pedido: {str(e)}")

    def abrir_detalle_pedido_backend(self, pedido_snapshot):
        from tkinter import messagebox
        pedido_id = pedido_snapshot.get('id_pedido') or pedido_snapshot.get('id') or pedido_snapshot.get('id_pedido_snapshot')
        if not pedido_id:
            messagebox.showerror("Error", "No se encontró el ID del pedido.")
            return
        print(f"[Pagos] Solicitando detalle de pedido con ID: {pedido_id}")
        pedido_completo = obtener_pedido_completo_backend(pedido_id)
        print(f"[Pagos] Respuesta del backend para pedido {pedido_id}: {pedido_completo}")
        if pedido_completo:
            # Validar que el pedido tenga datos clave (usuario, items, etc.)
            if not pedido_completo.get('usuario') or not pedido_completo.get('pedido_items'):
                messagebox.showwarning(
                    "Advertencia",
                    "El pedido no tiene todos los datos necesarios (usuario, productos, etc.).\n\nVerifica que el backend devuelva el pedido con todas las relaciones."
                )
            from src.interfaces.management.orders_management import DetallesPedidoDialog
            DetallesPedidoDialog(self.parent, pedido_completo)
        else:
            messagebox.showerror("Error", "No se pudo obtener el detalle completo del pedido.")

class EstadoPagoDialog:
    """Diálogo para actualizar el estado de un pago"""
    
    def __init__(self, parent, pago):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(f"Actualizar Estado - Pago #{pago.get('id_pago', 'N/A')}")
            self.dialog.geometry("400x350")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Proteger contra cierre abrupto
            self.dialog.protocol("WM_DELETE_WINDOW", self.safe_close)
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF", corner_radius=15)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text=f"Actualizar Estado del Pago",
                font=("Quicksand", 18, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(20, 30))
            
            # Información actual
            info_frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5")
            info_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            ctk.CTkLabel(
                info_frame,
                text=f"Pago #{pago.get('id_pago', 'N/A')} - Pedido #{pago.get('pedidos_id_pedido', pago.get('pedido', {}).get('id_pedido', 'N/A'))}",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=f"Estado actual: {pago.get('estado_pago', 'N/A').title()}",
                font=("Quicksand", 12),
                text_color="#000000"
            ).pack(pady=(0, 10))
            
            # Nuevo estado
            ctk.CTkLabel(
                main_frame,
                text="Nuevo Estado:",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(10, 5))
            
            self.estado_var = ctk.StringVar(value=pago.get('estado_pago', 'pendiente'))
            estado_menu = ctk.CTkOptionMenu(
                main_frame,
                values=EstadosPago.get_all(),
                variable=self.estado_var,
                width=300,
                fg_color="#2E6B5C",
                button_color="#1D4A3C",
                button_hover_color="#153A2C",
                dropdown_fg_color="#FFFFFF",
                dropdown_hover_color="#F5F5F5",
                dropdown_text_color="#2E6B5C"
            )
            estado_menu.pack(pady=10)
            
            # Referencia adicional (opcional)
            ctk.CTkLabel(
                main_frame,
                text="Referencia adicional (opcional):",
                font=("Quicksand", 12),
                text_color="#2E6B5C"
            ).pack(pady=(10, 5))
            
            self.referencia_var = ctk.StringVar()
            referencia_entry = ctk.CTkEntry(
                main_frame,
                textvariable=self.referencia_var,
                width=300,
                placeholder_text="Ej: Confirmado por administrador",
                border_width=1,
                fg_color="#F5F5F5"
            )
            referencia_entry.pack(pady=5)
            
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=30)
            
            ctk.CTkButton(
                button_frame,
                text="Actualizar",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.safe_close,
                fg_color="#E0E0E0",
                text_color="#2E6B5C",
                hover_color="#D0D0D0",
                width=120
            ).pack(side="left", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
    
    def guardar(self):
        """Guardar los cambios"""
        try:
            estado = self.estado_var.get()
            referencia = self.referencia_var.get().strip()
            
            if not estado:
                messagebox.showerror("Error", "Debe seleccionar un estado")
                return
            
            # Guardar resultado
            self.result = {
                'estado': estado,
                'referencia': referencia if referencia else None
            }
            
            # Cerrar diálogo
            self.safe_close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def safe_close(self):
        """Cierre seguro del diálogo"""
        try:
            if hasattr(self, 'dialog') and self.dialog is not None:
                try:
                    if self.dialog.winfo_exists():
                        self.dialog.grab_release()
                        self.dialog.destroy()
                except Exception as e:
                    # Evitar error si la app ya fue destruida
                    if 'application has been destroyed' not in str(e):
                        print(f"Error al cerrar diálogo: {e}")
                self.dialog = None
        except Exception as e:
            print(f"Error al cerrar diálogo: {e}")
    
    def __del__(self):
        """Destructor para limpieza de recursos"""
        try:
            self.safe_close()
        except Exception:
            pass  # Ignorar errores en el destructor

    def crear_mensaje_sin_envio(self, parent, pago):
        """Crear mensaje informativo cuando no hay información de envío"""
        try:
            envio_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=10)
            envio_frame.pack(fill="x", padx=15, pady=10)
            
            # Header informativo
            header_frame = ctk.CTkFrame(envio_frame, fg_color="#FFF3E0", corner_radius=8)
            header_frame.pack(fill="x", padx=15, pady=(15, 0))
            
            ctk.CTkLabel(
                header_frame,
                text="📋 Información de Envío",
                font=("Quicksand", 16, "bold"),
                text_color="#FF8C00"
            ).pack(pady=12)
            
            # Contenido informativo
            content_frame = ctk.CTkFrame(envio_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=15)
            
            # Mensaje según el estado del pago
            estado_pago = pago.get('estado_pago', '').lower()
            
            if estado_pago == 'pendiente':
                mensaje = ("ℹ️ El envío aún no ha sido creado.\n\n"
                          "Esto es normal para pagos pendientes. Una vez que el pago "
                          "sea confirmado y procesado, se generará automáticamente "
                          "la información de envío correspondiente.")
                color = "#FF8C00"
            elif estado_pago == 'fallido':
                mensaje = ("❌ No se creó información de envío.\n\n"
                          "El pago falló, por lo que no se procesó el envío. "
                          "Contacte al cliente para resolver el problema de pago.")
                color = "#F44336"
            elif estado_pago == 'cancelado':
                mensaje = ("🚫 Envío cancelado.\n\n"
                          "El pago fue cancelado, por lo que no se procesará el envío.")
                color = "#9E9E9E"
            else:
                mensaje = ("⚠️ Información de envío no disponible.\n\n"
                          "Los datos de envío no están disponibles en este momento. "
                          "Verifique el estado del pedido o contacte al administrador.")
                color = "#9E9E9E"
            
            info_frame = ctk.CTkFrame(content_frame, fg_color="#F8F9FA", corner_radius=8)
            info_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=mensaje,
                font=("Quicksand", 12),
                text_color=color,
                justify="center",
                wraplength=400
            ).pack(pady=20, padx=20)
            
        except Exception as e:
            print(f"Error al crear mensaje sin envío: {str(e)}")
