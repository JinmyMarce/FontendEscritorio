import customtkinter as ctk
import tkinter.messagebox as messagebox
import customtkinter as ctk
import tkinter
from tkinter import messagebox
from tkinter import ttk
import inspect
import json
import os
from src.core.config import ORDERS_ENDPOINTS, SHIPPING_ENDPOINTS, UI_CONFIG
from src.core.status_config import (
    EstadosPedido, EstadosPago, EstadosEnvio,
    FlujoEstados, MensajesEstado, TransicionesEstado,
    FiltrosUI, EstadosDeprecados,
    obtener_color_estado, obtener_label_estado,
    sincronizar_estado_envio
)
from src.shared.utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper
import json
import os
from datetime import datetime, timedelta
import random
from PIL import Image, ImageTk
from src.shared.image_handler import ImageHandler

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
def obtener_pedidos():
    """
    Obtiene la lista de pedidos desde la API de admin y maneja errores de forma robusta.
    Devuelve una lista vacía si hay problemas.
    """
    try:
        url = ORDERS_ENDPOINTS['list']  # Ahora apunta a /admin/orders para admin
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', url, headers=headers)
        if response.get('status_code') == 200:
            data = response.get('data', [])
            if isinstance(data, dict) and 'orders' in data:
                return data['orders']
            elif isinstance(data, list):
                return data
            else:
                message = data if isinstance(data, str) else str(data)
                messagebox.showerror("Error", f"Respuesta inesperada de la API de pedidos:\n{message}")
                return []
        else:
            message = response.get('data') or response.get('message') or str(response)
            messagebox.showerror("Error", f"No se pudo obtener pedidos:\n{message}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener pedidos: {str(e)}")
    return []

def obtener_pedidos_por_cliente(cliente_id):
    """
    Obtiene los pedidos de un cliente específico desde la API de admin.
    Devuelve una lista vacía si hay problemas.
    """
    try:
        # Construir URL para pedidos por cliente usando la configuración
        url = ORDERS_ENDPOINTS['by_client'].format(client_id=cliente_id)
        
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', url, headers=headers)
        
        if response.get('status_code') == 200:
            data = response.get('data', [])
            if isinstance(data, dict) and 'orders' in data:
                return data['orders']
            elif isinstance(data, list):
                return data
            else:
                message = data if isinstance(data, str) else str(data)
                messagebox.showerror("Error", f"Respuesta inesperada de la API de pedidos por cliente:\n{message}")
                return []
        else:
            message = response.get('data') or response.get('message') or str(response)
            messagebox.showerror("Error", f"No se pudo obtener pedidos del cliente:\n{message}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener pedidos del cliente: {str(e)}")
    return []

def actualizar_estado(pedido_id, nuevo_estado, return_error=False):
    """
    Actualiza el estado de un pedido mediante la API con validaciones mejoradas.
    Utiliza la configuración de estados estandarizados.
    Devuelve una tupla (exito, mensaje_error) si return_error=True.
    """
    try:
        # Validar que el nuevo estado sea válido
        if nuevo_estado not in EstadosPedido.get_all():
            error_msg = f"Estado '{nuevo_estado}' no es válido"
            if not return_error:
                messagebox.showerror("Error de Validación", error_msg)
            return (False, error_msg) if return_error else False
        
        # --- MODO LOCAL ---
        frame = None
        import inspect
        # Buscar instancia de GestionPedidos para acceder a self.pedidos
        for frame_info in inspect.stack():
            local_self = frame_info.frame.f_locals.get('self')
            if hasattr(local_self, 'modo_local') and hasattr(local_self, 'pedidos'):
                frame = local_self
                break
        if frame and getattr(frame, 'modo_local', False):
            for pedido in frame.pedidos:
                if str(pedido.get("id_pedido")) == str(pedido_id):
                    pedido["estado"] = nuevo_estado
                    if not return_error:
                        label_estado = obtener_label_estado('pedido', nuevo_estado)
                        messagebox.showinfo("Éxito", f"Estado cambiado a {label_estado}")
                    return True if not return_error else (True, None)
            if not return_error:
                messagebox.showerror("Error", "No se encontró el pedido localmente.")
            return (False, "No se encontró el pedido localmente.") if return_error else False

        # --- MODO REMOTO (API REAL) ---
        url = ORDERS_ENDPOINTS['update'].format(id=pedido_id)
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        response = APIHandler.make_request('patch', url, data={"estado": nuevo_estado}, headers=headers)
        
        if response.get('status_code') == 200:
            # Actualización exitosa del pedido
            # Ahora sincronizar el estado del envío
            estado_envio_sincronizado = sincronizar_estado_envio(nuevo_estado)
            
            # Intentar actualizar el estado del envío
            exito_envio, error_envio = actualizar_estado_envio(pedido_id, estado_envio_sincronizado, return_error=True)
            
            if not exito_envio:
                # Si falla la actualización del envío, mostrar advertencia pero no fallar completamente
                print(f"Advertencia: Pedido actualizado pero envío no se pudo sincronizar: {error_envio}")
                if not return_error:
                    label_estado = obtener_label_estado('pedido', nuevo_estado)
                    messagebox.showwarning("Éxito parcial", 
                                         f"Estado del pedido actualizado a '{label_estado}' exitosamente.\n\n"
                                         f"Advertencia: No se pudo sincronizar el estado del envío.")
            else:
                # Todo exitoso
                if not return_error:
                    label_estado = obtener_label_estado('pedido', nuevo_estado)
                    messagebox.showinfo("Éxito", f"Estado actualizado a '{label_estado}' exitosamente")
            
            return True if not return_error else (True, None)
        else:
            error_msg = None
            if isinstance(response.get('data'), dict):
                error_msg = response['data'].get('error') or response['data'].get('mensaje')
            if not error_msg:
                error_msg = response.get('message') or str(response)
            if not return_error:
                messagebox.showerror("Error al actualizar pedido", f"No se pudo actualizar el estado: {error_msg}")
            return (False, error_msg) if return_error else False
    except Exception as e:
        if not return_error:
            messagebox.showerror("Error inesperado", f"Ocurrió un error inesperado: {str(e)}")
        return (False, str(e)) if return_error else False

def actualizar_estado_envio(pedido_id, nuevo_estado_envio, return_error=False):
    """
    Actualiza el estado del envío asociado a un pedido.
    """
    try:
        # Primero, buscar el envío en los datos del pedido ya cargados
        # para evitar llamadas innecesarias al backend
        pedido_actual = None
        
        # Buscar instancia de GestionPedidos para acceder a self.pedidos
        import inspect
        for frame_info in inspect.stack():
            local_self = frame_info.frame.f_locals.get('self')
            if hasattr(local_self, 'pedidos'):
                for pedido in local_self.pedidos:
                    if str(pedido.get("id_pedido")) == str(pedido_id):
                        pedido_actual = pedido
                        break
                break
        
        if pedido_actual and 'envios' in pedido_actual and pedido_actual['envios']:
            # Usar el ID del envío que ya tenemos
            envio = pedido_actual['envios'][0]  # Tomar el primer envío
            envio_id = envio.get('id_envio') or envio.get('id')
            
            if envio_id:
                # Actualizar directamente con el ID que ya tenemos
                url_update = SHIPPING_ENDPOINTS['update_status'].format(id=envio_id)
                token = SessionManager.get_token()
                headers = {'Authorization': f'Bearer {token}'} if token else {}
                
                response_update = APIHandler.make_request('patch', url_update, data={"estado": nuevo_estado_envio}, headers=headers)
                
                if response_update.get('status_code') == 200:
                    return True if not return_error else (True, None)
                else:
                    error_msg = f"No se pudo actualizar el estado del envío: {response_update.get('message', 'Error desconocido')}"
                    if not return_error:
                        print(f"Error: {error_msg}")
                    return (False, error_msg) if return_error else False
        
        # Si no encontramos el envío en los datos locales, intentar consultar al backend
        url_envio = SHIPPING_ENDPOINTS['by_order'].format(order_id=pedido_id)
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        # Obtener información del envío
        response_envio = APIHandler.make_request('get', url_envio, headers=headers)
        
        if response_envio.get('status_code') != 200:
            error_msg = f"No se pudo obtener información del envío para el pedido {pedido_id}"
            if not return_error:
                print(f"Warning: {error_msg}")
            return (False, error_msg) if return_error else False
        
        # Extraer el ID del envío
        envio_data = response_envio.get('data')
        if not envio_data:
            error_msg = f"No se encontró envío para el pedido {pedido_id}"
            if not return_error:
                print(f"Warning: {error_msg}")
            return (False, error_msg) if return_error else False
        
        # Determinar el ID del envío (puede estar en diferentes estructuras)
        envio_id = None
        if isinstance(envio_data, dict):
            envio_id = envio_data.get('id_envio') or envio_data.get('id')
        elif isinstance(envio_data, list) and len(envio_data) > 0:
            envio_id = envio_data[0].get('id_envio') or envio_data[0].get('id')
        
        if not envio_id:
            error_msg = f"No se pudo determinar el ID del envío para el pedido {pedido_id}"
            if not return_error:
                print(f"Warning: {error_msg}")
            return (False, error_msg) if return_error else False
        
        # Actualizar el estado del envío
        url_update = SHIPPING_ENDPOINTS['update_status'].format(id=envio_id)
        response_update = APIHandler.make_request('patch', url_update, data={"estado": nuevo_estado_envio}, headers=headers)
        
        if response_update.get('status_code') == 200:
            return True if not return_error else (True, None)
        else:
            error_msg = f"No se pudo actualizar el estado del envío: {response_update.get('message', 'Error desconocido')}"
            if not return_error:
                print(f"Error: {error_msg}")
            return (False, error_msg) if return_error else False
            
    except Exception as e:
        error_msg = f"Error al actualizar estado del envío: {str(e)}"
        if not return_error:
            print(f"Error: {error_msg}")
        return (False, error_msg) if return_error else False

# --- CLASE PRINCIPAL DE INTERFAZ ---
class GestionPedidos(ctk.CTkFrame):
    def __init__(self, parent, cliente_filtro=None, dashboard=None):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar lista de pedidos (se cargan desde el backend en cargar_datos)
            self.pedidos = []
            self.cliente_filtro = cliente_filtro  # Cliente específico para filtrar
            self.dashboard = dashboard  # Referencia al dashboard para navegación
            
            # Frame superior
            top_frame = ctk.CTkFrame(self, fg_color="transparent")
            top_frame.pack(fill="x", pady=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            title_frame.pack(side="left")
            
            try:
                # Cargar y redimensionar icono
                icon = Image.open("imagen/pedidos.png")
                icon = icon.resize((32, 32))
                self.icon_image = ctk.CTkImage(light_image=icon, dark_image=icon, size=(32, 32))
                ctk.CTkLabel(
                    title_frame,
                    image=self.icon_image,
                    text=""
                ).pack(side="left", padx=(0, 10))
            except:
                pass
                
            # Título dinámico basado en si hay filtro de cliente
            titulo_texto = "Gestión de Pedidos"
            if self.cliente_filtro:
                titulo_texto += f" - {self.cliente_filtro['nombre']} {self.cliente_filtro['apellidos']}"
            
            ctk.CTkLabel(
                title_frame,
                text=titulo_texto,
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left")
            
            # Botón Volver si hay filtro de cliente
            if self.cliente_filtro:
                volver_btn = ctk.CTkButton(
                    top_frame,
                    text="← Volver a Clientes",
                    font=("Quicksand", 12, "bold"),
                    fg_color="#757575",
                    hover_color="#616161",
                    height=35,
                    command=self.volver_a_clientes
                )
                volver_btn.pack(side="right")
            
            # Frame para búsqueda y filtros
            search_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            search_frame.pack(fill="x", pady=(0, 20))
            
            # Búsqueda
            search_label = ctk.CTkLabel(
                search_frame,
                text="🔍",
                font=("Quicksand", 16)
            )
            search_label.pack(side="left", padx=(15, 5))
            
            self.search_var = ctk.StringVar()
            self.search_var.trace("w", self.filtrar_tabla)
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=self.search_var,
                width=300,
                placeholder_text="Buscar por ID, cliente o estado...",
                border_width=0,
                fg_color="#F5F5F5"
            )
            search_entry.pack(side="left", padx=5, pady=10)
            
            # Separador
            ctk.CTkFrame(
                search_frame,
                width=1,
                height=30,
                fg_color="#E0E0E0"
            ).pack(side="left", padx=15)
            
            # Filtro de estado
            ctk.CTkLabel(
                search_frame,
                text="Estado:",
                font=("Quicksand", 12)
            ).pack(side="left", padx=5)
            
            self.estado_var = ctk.StringVar(value="Todos")
            self.estado_var.trace("w", self.filtrar_tabla)
            estado_menu = ctk.CTkOptionMenu(
                search_frame,
                values=FiltrosUI.OPCIONES_FILTRO_PEDIDOS,
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
            
            # Botón de acción: solo actualizar estado
            action_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
            action_frame.pack(side="right", padx=15)
            ctk.CTkButton(
                action_frame,
                text="Actualizar Estado",
                command=self.mostrar_dialogo_estado,
                fg_color="#FFA000",
                hover_color="#F57C00",
                width=150
            ).pack(side="left", padx=5)
            
            # Tabla con estilo
            style = ttk.Style()
            style.configure(
                "Treeview",
                background="#FFFFFF",
                foreground="#2E6B5C",
                rowheight=30,
                fieldbackground="#FFFFFF",
                borderwidth=0
            )
            style.configure(
                "Treeview.Heading",
                background="#F5F5F5",
                foreground="#2E6B5C",
                relief="flat",
                font=("Quicksand", 10, "bold")
            )
            style.map(
                "Treeview.Heading",
                background=[("active", "#E0E0E0")]
            )
            
            # Frame para tabla
            table_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            table_frame.pack(fill="both", expand=True)

            # Tabla
            columns = (
                "id_pedido", "codigo_pedido", "cliente", "productos", "cantidades", "monto_total", "estado"
            )
            self.tabla = ttk.Treeview(
                table_frame,
                columns=columns,
                show="headings",
                selectmode="browse",
                style="Treeview"
            )
            # Configurar columnas
            self.tabla.heading("id_pedido", text="")
            self.tabla.heading("codigo_pedido", text="Código de Pedido")
            self.tabla.heading("cliente", text="Cliente")
            self.tabla.heading("productos", text="Productos")
            self.tabla.heading("cantidades", text="Cantidades")
            self.tabla.heading("monto_total", text="Monto Total")
            self.tabla.heading("estado", text="Estado del Pedido")
            # Configurar anchos
            self.tabla.column("id_pedido", width=0, stretch=False)  # Oculta visualmente
            self.tabla.column("codigo_pedido", width=150, anchor="center")
            self.tabla.column("cliente", width=180)
            self.tabla.column("productos", width=200)
            self.tabla.column("cantidades", width=100, anchor="center")
            self.tabla.column("monto_total", width=100, anchor="center")
            self.tabla.column("estado", width=120, anchor="center")

            # Scrollbar personalizado
            scrollbar = ttk.Scrollbar(
                table_frame,
                orient="vertical",
                command=self.tabla.yview
            )
            self.tabla.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar tabla y scrollbar
            self.tabla.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # Cargar datos
            self.cargar_datos()
            
            # Bind doble clic
            self.tabla.bind("<Double-1>", self.ver_detalles)
            
            # Bind tecla Enter
            self.tabla.bind("<Return>", self.ver_detalles)
            
            # Bind tecla Delete
            self.tabla.bind("<Delete>", self.cancelar_pedido)
            
            self.modo_local = False  # Cambia a True para usar datos locales de prueba
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar: {str(e)}")
            
    # El método cargar_datos_ejemplo ya no se usará, pero se deja para referencia.
        
    def cargar_datos(self):
        try:
            # Obtener datos según si hay filtro de cliente o no
            if self.cliente_filtro:
                self.pedidos = obtener_pedidos_por_cliente(self.cliente_filtro['id_usuario'])
            else:
                self.pedidos = obtener_pedidos()
            
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            # Cargar datos
            for pedido in self.pedidos:
                # Extraer productos y cantidades de los items
                productos = []
                cantidades = []
                # Buscar los items del pedido en 'pedido_items' o 'items'
                items = pedido.get("pedido_items") or pedido.get("items") or []
                for item in items:
                    # Extraer el nombre real del producto
                    nombre_producto = item.get("producto")
                    if isinstance(nombre_producto, dict):
                        nombre_producto = nombre_producto.get("nombre", "")
                    if not nombre_producto:
                        nombre_producto = item.get("producto_nombre_snapshot")
                    if not nombre_producto and "producto_snapshot" in item:
                        nombre_producto = item["producto_snapshot"].get("nombre", "")
                    productos.append(nombre_producto or "")
                    # Cantidad real
                    cantidad = item.get("cantidad", 1)
                    if not cantidad:
                        cantidad = 1
                    cantidades.append(str(cantidad))
                productos_str = ", ".join(productos)
                cantidades_str = ", ".join(cantidades)
                # Construir nombre del cliente
                cliente = ""
                if "usuario" in pedido:
                    nombre = pedido["usuario"].get("nombre", "")
                    apellidos = pedido["usuario"].get("apellidos", "")
                    cliente = f"{nombre} {apellidos}".strip()
                # Configurar tags para el estado
                estado_migrado = EstadosDeprecados.migrar_estado(pedido["estado"])
                tags = (estado_migrado.replace(" ", "_"),)
                
                # Obtener código del pedido o generar uno temporal si no existe
                codigo_pedido = pedido.get("codigo_pedido", f"PED-{pedido.get('id_pedido', '')}")
                
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        pedido.get("id_pedido", ""),
                        codigo_pedido,
                        cliente,
                        productos_str,
                        cantidades_str,
                        f"S/. {pedido['monto_total']:.2f}",
                        obtener_label_estado('pedido', estado_migrado)
                    ),
                    tags=tags
                )
            
            # Configurar colores de estado usando la configuración estandarizada
            for estado in EstadosPedido.get_all():
                color = obtener_color_estado('pedido', estado)
                self.tabla.tag_configure(estado, foreground=color)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            
    def filtrar_tabla(self, *args):
        try:
            # Obtener valores de filtro
            busqueda = self.search_var.get().lower()
            estado = self.estado_var.get()
            
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Filtrar y cargar datos
            for pedido in self.pedidos:
                # Extraer productos y cantidades de los items
                productos = []
                cantidades = []
                items = pedido.get("pedido_items") or pedido.get("items") or []
                for item in items:
                    nombre_producto = item.get("producto")
                    if isinstance(nombre_producto, dict):
                        nombre_producto = nombre_producto.get("nombre", "")
                    if not nombre_producto:
                        nombre_producto = item.get("producto_nombre_snapshot")
                    if not nombre_producto and "producto_snapshot" in item:
                        nombre_producto = item["producto_snapshot"].get("nombre", "")
                    productos.append(nombre_producto or "")
                    cantidad = item.get("cantidad", 1)
                    if not cantidad:
                        cantidad = 1
                    cantidades.append(str(cantidad))
                productos_str = ", ".join(productos)
                cantidades_str = ", ".join(cantidades)
                
                # Construir nombre del cliente
                cliente = ""
                if "usuario" in pedido:
                    nombre = pedido["usuario"].get("nombre", "")
                    apellidos = pedido["usuario"].get("apellidos", "")
                    cliente = f"{nombre} {apellidos}".strip()
                
                # Aplicar filtros
                estado_migrado = EstadosDeprecados.migrar_estado(pedido["estado"])
                if estado != "Todos" and estado_migrado != estado:
                    continue
                
                # Obtener código del pedido o generar uno temporal si no existe
                codigo_pedido = pedido.get("codigo_pedido", f"PED-{pedido.get('id_pedido', '')}")
                    
                valores_busqueda = [
                    pedido.get("id_pedido", ""),
                    codigo_pedido,
                    cliente,
                    productos_str,
                    cantidades_str,
                    f"S/. {pedido['monto_total']:.2f}",
                    obtener_label_estado('pedido', estado_migrado)
                ]
                if busqueda and not any(busqueda in str(valor).lower() for valor in valores_busqueda):
                    continue
                
                # Configurar tags para el estado
                tags = (estado_migrado.replace(" ", "_"),)
                
                # Insertar fila
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        pedido.get("id_pedido", ""),
                        codigo_pedido,
                        cliente,
                        productos_str,
                        cantidades_str,
                        f"S/. {pedido['monto_total']:.2f}",
                        obtener_label_estado('pedido', estado_migrado)
                    ),
                    tags=tags
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar datos: {str(e)}")
            
    def nuevo_pedido(self):
        try:
            # Ventana de nuevo pedido
            dialog = PedidoDialog(self, "Nuevo Pedido")
            if dialog.result:
                # Agregar nuevo pedido
                nuevo_id = max([p["id_pedido"] for p in self.pedidos], default=0) + 1
                
                self.pedidos.append({
                    "id_pedido": nuevo_id,
                    **dialog.result,
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "estado": "Pendiente"
                })
                
                self.cargar_datos()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Pedido creado correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nuevo pedido: {str(e)}")
            
    def mostrar_dialogo_estado(self):
        try:
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
                return
            
            item = self.tabla.item(seleccion[0])
            pedido_id = item["values"][0]
            pedido = next((p for p in self.pedidos if str(p.get("id_pedido", "")) == str(pedido_id)), None)
            
            if not pedido:
                messagebox.showerror("Error", "No se pudo encontrar el pedido seleccionado.")
                return
            
            # Migrar estado actual si es necesario
            estado_actual = EstadosDeprecados.migrar_estado(pedido["estado"])
            
            # Verificar si el pedido está en estado final
            if estado_actual in [EstadosPedido.ENTREGADO, EstadosPedido.CANCELADO]:
                messagebox.showinfo("Información", f"El pedido ya está en estado final: '{obtener_label_estado('pedido', estado_actual)}'.")
                return
            
            # Obtener estados válidos para la transición
            estados_siguientes = TransicionesEstado.get_estados_siguientes(estado_actual)
            if not estados_siguientes:
                messagebox.showinfo("Información", f"No hay transiciones válidas desde el estado '{obtener_label_estado('pedido', estado_actual)}'.")
                return
            
            # Crear diálogo
            dialog = ctk.CTkToplevel(self)
            dialog.title("Actualizar Estado del Pedido")
            dialog.geometry("400x250")
            dialog.grab_set()
            
            # Centrar el diálogo en la pantalla
            dialog.update_idletasks()
            w = dialog.winfo_width()
            h = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (w // 2)
            y = (dialog.winfo_screenheight() // 2) - (h // 2)
            dialog.geometry(f"400x250+{x}+{y}")
            
            # Información del pedido
            pedido_info = self.obtener_pedido_por_id(pedido_id)
            codigo_pedido = pedido_info.get("codigo_pedido", f"PED-{pedido_id}") if pedido_info else f"PED-{pedido_id}"
            
            ctk.CTkLabel(
                dialog, 
                text=f"Pedido {codigo_pedido}", 
                font=("Quicksand", 16, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=10)
            
            ctk.CTkLabel(
                dialog, 
                text=f"Estado actual: {obtener_label_estado('pedido', estado_actual)}", 
                font=("Quicksand", 12)
            ).pack(pady=5)
            
            ctk.CTkLabel(
                dialog, 
                text="Selecciona nuevo estado:", 
                font=("Quicksand", 12, "bold")
            ).pack(pady=(15, 5))
            
            # Crear opciones con labels legibles
            opciones_labels = [obtener_label_estado('pedido', estado) for estado in estados_siguientes]
            estado_var = ctk.StringVar(value=opciones_labels[0] if opciones_labels else "")
            
            combo = ctk.CTkOptionMenu(
                dialog, 
                variable=estado_var, 
                values=opciones_labels,
                width=250
            )
            combo.pack(pady=5)
            
            def confirmar():
                opcion_label = estado_var.get()
                if not opcion_label:
                    messagebox.showwarning("Advertencia", "Selecciona un estado válido para actualizar.", parent=dialog)
                    return
                
                # Encontrar el estado correspondiente al label seleccionado
                estado_seleccionado = None
                for estado in estados_siguientes:
                    if obtener_label_estado('pedido', estado) == opcion_label:
                        estado_seleccionado = estado
                        break
                
                if not estado_seleccionado:
                    messagebox.showerror("Error", "Estado seleccionado no válido.", parent=dialog)
                    return
                
                # Mostrar mensaje específico según el flujo
                mensaje_confirmacion = f"¿Deseas cambiar el estado del pedido #{pedido_id} a '{opcion_label}'?"
                mensaje_usuario = MensajesEstado.get_mensaje(estado_seleccionado)
                if mensaje_usuario:
                    mensaje_confirmacion += f"\n\nMensaje para el usuario: {mensaje_usuario}"
                
                respuesta = messagebox.askyesno("Confirmar Cambio de Estado", mensaje_confirmacion, parent=dialog)
                if not respuesta:
                    return
                
                exito, error_msg = actualizar_estado(pedido_id, estado_seleccionado, return_error=True)
                if exito:
                    self.cargar_datos()
                    messagebox.showinfo("Éxito", f"Estado cambiado a '{opcion_label}' exitosamente", parent=dialog)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", error_msg or "No se pudo actualizar el estado del pedido.", parent=dialog)
            
            # Botones
            button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ctk.CTkButton(
                button_frame, 
                text="Actualizar Estado", 
                command=confirmar, 
                fg_color="#2E6B5C", 
                hover_color="#1D4A3C",
                width=150
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame, 
                text="Cancelar", 
                command=dialog.destroy, 
                fg_color="#E64A19", 
                hover_color="#BF360C",
                width=100
            ).pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar diálogo: {str(e)}")

    def cancelar_pedido(self, event=None):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
                return
                
            # Obtener pedido seleccionado
            item = self.tabla.item(seleccion[0])
            pedido_id = item["values"][0]
            pedido = next((p for p in self.pedidos if str(p.get("id_pedido", "")) == str(pedido_id)), None)
            
            if pedido:
                # Verificar si el pedido puede ser cancelado
                estado_actual = EstadosDeprecados.migrar_estado(pedido["estado"])
                if estado_actual in [EstadosPedido.ENTREGADO, EstadosPedido.CANCELADO]:
                    messagebox.showinfo("Información", f"El pedido ya está en estado '{obtener_label_estado('pedido', estado_actual)}' y no puede ser cancelado.")
                    return
                
                # Confirmar cancelación
                if messagebox.askyesno("Confirmar Cancelación", f"¿Está seguro de cancelar el pedido #{pedido_id}?\n\nEsta acción no se puede deshacer."):
                    # Cancelar pedido usando el estado estandarizado
                    exito, error_msg = actualizar_estado(pedido_id, EstadosPedido.CANCELADO, return_error=True)
                    if exito:
                        self.cargar_datos()
                        messagebox.showinfo("Éxito", "Pedido cancelado correctamente")
                    else:
                        messagebox.showerror("Error", error_msg or "No se pudo cancelar el pedido")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cancelar pedido: {str(e)}")

    def guardar_datos(self):
        try:
            # Crear directorio si no existe
            os.makedirs("datos", exist_ok=True)
            
            # Guardar datos en archivo
            with open("datos/pedidos.json", "w", encoding="utf-8") as f:
                json.dump(self.pedidos, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")

    def ver_detalles(self, event):
        try:
            # Obtener item seleccionado
            if not self.tabla.selection():
                return
                
            item = self.tabla.selection()[0]
            pedido_id = self.tabla.item(item)["values"][0]
            pedido = next((p for p in self.pedidos if str(p.get("id_pedido", "")) == str(pedido_id)), None)
            
            if pedido:
                # Mostrar detalles
                DetallesPedidoDialog(self, pedido)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")

    def volver_a_clientes(self):
        """Volver a la gestión de clientes"""
        try:
            if self.dashboard:
                self.dashboard.mostrar_clientes()
            else:
                messagebox.showwarning(
                    "Navegación no disponible",
                    "No se puede volver a clientes desde este contexto."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error al volver a clientes: {str(e)}")
    
    def obtener_pedido_por_id(self, pedido_id):
        """Obtener un pedido específico por ID de la lista cargada"""
        for pedido in self.pedidos:
            if str(pedido.get("id_pedido")) == str(pedido_id):
                return pedido
        return None

class PedidoDialog:
    def __init__(self, parent, title):
        try:
            self.result = None
            self.items = []  # Lista para almacenar los items del pedido
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("500x600")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text=title,
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Campos del formulario
            campos = [
                ("Cliente", "cliente"),
                ("Método de Pago", "metodo_pago")
            ]
            
            self.entries = {}
            
            for i, (label, field) in enumerate(campos):
                # Label
                ctk.CTkLabel(
                    main_frame,
                    text=label,
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).pack(pady=(20 if i == 0 else 10, 0))
                
                if field == "metodo_pago":
                    # Combo box para método de pago
                    self.metodo_pago_var = ctk.StringVar(value="Tarjeta")
                    metodo_pago_menu = ctk.CTkOptionMenu(
                        main_frame,
                        values=["Tarjeta", "Efectivo", "Transferencia"],
                        variable=self.metodo_pago_var,
                        width=300,
                        fg_color="#2E6B5C",
                        button_color="#1D4A3C",
                        button_hover_color="#153A2C",
                        dropdown_fg_color="#FFFFFF",
                        dropdown_hover_color="#F5F5F5",
                        dropdown_text_color="#2E6B5C"
                    )
                    metodo_pago_menu.pack(pady=5)
                    self.entries[field] = self.metodo_pago_var
                else:
                    # Entry para cliente
                    entry = ctk.CTkEntry(
                        main_frame,
                        width=300,
                        placeholder_text=f"Ingrese {label.lower()}...",
                        border_width=0,
                        fg_color="#F5F5F5"
                    )
                    entry.pack(pady=5)
                    self.entries[field] = entry
            # Frame para items
            self.items_frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5")
            self.items_frame.pack(fill="x", pady=20)

            # Botón para agregar producto
            ctk.CTkButton(
                self.items_frame,
                text="➕ Agregar Producto",
                command=self.agregar_item,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=200
            ).pack(pady=10)

            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            ctk.CTkButton(
                button_frame,
                text="Guardar",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=120
            ).pack(side="left", padx=5)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
            
    def agregar_item(self):
        try:
            # Ventana de nuevo item
            dialog = ItemDialog(self.dialog)
            if dialog.result:
                # Agregar item
                self.items.append(dialog.result)
                
                # Actualizar lista
                self.actualizar_lista()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar item: {str(e)}")
            
    def actualizar_lista(self):
        try:
            # Limpiar frame de items
            for widget in self.items_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.destroy()
                    
            # Mostrar items
            for i, item in enumerate(self.items):
                frame = ctk.CTkFrame(self.items_frame, fg_color="#FFFFFF")
                frame.pack(fill="x", pady=5, padx=10)
                
                # Producto
                ctk.CTkLabel(
                    frame,
                    text=item["producto"],
                    font=("Quicksand", 12)
                ).pack(side="left", padx=10)
                
                # Cantidad
                ctk.CTkLabel(
                    frame,
                    text=f"Cantidad: {item['cantidad']}",
                    font=("Quicksand", 12)
                ).pack(side="left", padx=10)
                
                # Precio
                ctk.CTkLabel(
                    frame,
                    text=f"S/. {item['precio']:.2f}",
                    font=("Quicksand", 12)
                ).pack(side="left", padx=10)
                
                # Subtotal
                ctk.CTkLabel(
                    frame,
                    text=f"Subtotal: S/. {item['subtotal']:.2f}",
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).pack(side="right", padx=10)
                
                # Botón eliminar
                ctk.CTkButton(
                    frame,
                    text="❌",
                    command=lambda idx=i: self.eliminar_item(idx),
                    fg_color="#E64A19",
                    hover_color="#BF360C",
                    width=30
                ).pack(side="right", padx=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar lista: {str(e)}")
            
    def eliminar_item(self, idx):
        try:
            # Eliminar item
            self.items.pop(idx)
            
            # Actualizar lista
            self.actualizar_lista()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar item: {str(e)}")
            
    def guardar(self):
        try:
            # Validar campos
            datos = {}
            for field, entry in self.entries.items():
                if isinstance(entry, ctk.StringVar):
                    valor = entry.get()
                else:
                    valor = entry.get().strip()
                if not valor:
                    messagebox.showwarning("Advertencia", f"El campo {field} es requerido")
                    return
                datos[field] = valor
                
            # Validar items
            if not self.items:
                messagebox.showwarning("Advertencia", "Debe agregar al menos un producto")
                return
                
            # Calcular monto total
            monto_total = sum(item["subtotal"] for item in self.items)
            
            # Guardar resultado
            self.result = {
                **datos,
                "monto_total": monto_total,
                "items": self.items
            }
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class ItemDialog:
    def __init__(self, parent):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("Nuevo Producto")
            self.dialog.geometry("400x300")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text="Nuevo Producto",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Campos del formulario
            campos = [
                ("Producto", "producto"),
                ("Cantidad", "cantidad"),
                ("Precio", "precio")
            ]
            
            self.entries = {}
            
            for i, (label, field) in enumerate(campos):
                # Label
                ctk.CTkLabel(
                    main_frame,
                    text=label,
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).pack(pady=(20 if i == 0 else 10, 0))
                
                # Entry
                entry = ctk.CTkEntry(
                    main_frame,
                    width=300,
                    placeholder_text=f"Ingrese {label.lower()}...",
                    border_width=0,
                    fg_color="#F5F5F5"
                )
                entry.pack(pady=5)
                self.entries[field] = entry
                
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ctk.CTkButton(
                button_frame,
                text="Agregar",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=120
            ).pack(side="left", padx=5)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
            
    def guardar(self):
        try:
            # Validar campos
            datos = {}
            for field, entry in self.entries.items():
                valor = entry.get().strip()
                if not valor:
                    messagebox.showwarning("Advertencia", f"El campo {field} es requerido")
                    return
                    
                # Convertir a número si es necesario
                if field in ["cantidad", "precio"]:
                    try:
                        valor = float(valor)
                        if valor <= 0:
                            messagebox.showwarning("Advertencia", f"El {field} debe ser mayor a 0")
                            return
                    except:
                        messagebox.showwarning("Advertencia", f"El {field} debe ser un número válido")
                        return
                        
                datos[field] = valor
                
            # Calcular subtotal
            datos["subtotal"] = datos["cantidad"] * datos["precio"]
            
            # Guardar resultado
            self.result = datos
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class EstadoDialog:
    def __init__(self, parent, pedido):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("Actualizar Estado")
            self.dialog.geometry("400x200")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text="Actualizar Estado",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Estado actual
            ctk.CTkLabel(
                main_frame,
                text=f"Estado actual: {pedido['estado']}",
                font=("Quicksand", 12),
                text_color="#424242"
            ).pack(pady=(0, 10))
            
            # Nuevo estado
            ctk.CTkLabel(
                main_frame,
                text="Nuevo estado:",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(10, 0))
            
            self.estado_var = ctk.StringVar(value=pedido["estado"].lower())
            estado_menu = ctk.CTkOptionMenu(
                main_frame,
                values=['pendiente', 'cancelado', 'completado'],
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
            
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            
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
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=120
            ).pack(side="left", padx=5)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
            
    def guardar(self):
        try:
            # Guardar resultado
            self.result = self.estado_var.get()
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class DetallesPedidoDialog:
    def __init__(self, parent, pedido):
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            codigo_pedido = pedido.get('codigo_pedido', f"PED-{pedido.get('id_pedido', '')}")
            self.dialog.title(f"Detalles del Pedido {codigo_pedido}")
            self.dialog.geometry("600x500")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (300)
            y = (self.dialog.winfo_screenheight() // 2) - (250)
            self.dialog.geometry(f"600x500+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=12, pady=12)
            
            # Título centrado y más abajo del borde superior
            codigo_pedido = pedido.get('codigo_pedido', f"PED-{pedido.get('id_pedido', '')}")
            ctk.CTkLabel(
                main_frame,
                text=f"Detalles del Pedido {codigo_pedido}",
                font=("Quicksand", 18, "bold"),
                text_color="#2E6B5C"
            ).pack(anchor="center", pady=(12, 4))

            # --- NOMBRE DEL CLIENTE ABAJO DEL TÍTULO ---
            usuario = pedido.get('usuario')
            if usuario:
                nombre_cliente = f"{usuario.get('nombre', '')} {usuario.get('apellidos', '')}".strip()
            else:
                nombre_cliente = pedido.get('cliente', '-')
            
            cliente_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            cliente_frame.pack(fill="x", pady=(0, 8))
            # Icono de usuario (puedes cambiar la ruta por un icono real si tienes uno)
            icono_usuario = None
            try:
                from PIL import Image, ImageTk
                icon_img = Image.open("assets/images/icons/user.png") if os.path.exists("assets/images/icons/user.png") else None
                if icon_img:
                    icon_img = icon_img.resize((32, 32))
                    icono_usuario = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(32, 32))
            except:
                pass
            if icono_usuario:
                ctk.CTkLabel(cliente_frame, image=icono_usuario, text="").pack(side="left", padx=(0, 10))
            else:
                ctk.CTkLabel(cliente_frame, text="👤", font=("Arial", 22), text_color="#2E6B5C").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                cliente_frame,
                text=nombre_cliente,
                font=("Quicksand", 16, "bold"),
                text_color="#2E6B5C",
                anchor="w"
            ).pack(side="left", padx=(0,10), pady=8)

            # --- CAMPOS EN DOS COLUMNAS (sin cliente, con dirección) ---
            # Dirección
            direccion = "-"
            if 'envios' in pedido and pedido['envios']:
                envio = pedido['envios'][0]
                if 'direccion' in envio and envio['direccion']:
                    dir_obj = envio['direccion']
                    calle = dir_obj.get('calle', '')
                    numero = dir_obj.get('numero', '')
                    distrito = dir_obj.get('distrito', '')
                    ciudad = dir_obj.get('ciudad', '')
                    ref = dir_obj.get('referencia', '')
                    direccion = f"{calle} {numero}, {distrito}, {ciudad}"
                    if ref:
                        direccion += f" ({ref})"
                else:
                    # Si no hay objeto direccion, usar snapshots
                    linea1 = envio.get('direccion_linea1_snapshot', '')
                    linea2 = envio.get('direccion_linea2_snapshot', '')
                    ciudad = envio.get('direccion_ciudad_snapshot', '')
                    estado = envio.get('direccion_estado_snapshot', '')
                    direccion = f"{linea1}, {linea2}, {ciudad}, {estado}"
                    direccion = direccion.strip(', ').replace(',,', ',')
                    if not any([linea1, linea2, ciudad, estado]):
                        direccion = "-"
            campos_2col = [
                ("Monto Total", "monto_total"),
                ("Estado del pedido", "estado"),
                ("Estado del pago", "estado_pago"),
                ("Método de Pago", "metodo_pago"),
                ("Precio Productos", "precio_productos"),
                ("Costo de Envío", "costo_envio"),
                ("Dirección", "direccion")
            ]
            # --- Bloque visual mejorado para los detalles generales en dos columnas ---
            grid_frame = ctk.CTkFrame(main_frame, fg_color="#FAFFF6", corner_radius=12, border_width=1, border_color="#FAFFF6")
            grid_frame.pack(fill="x", pady=(0, 10), padx=2)
            # Calcular monto total real (productos + envío)
            items = pedido.get("pedido_items") or pedido.get("items") or []
            total_productos = 0
            for item in items:
                cantidad = item.get("cantidad", 1)
                precio = item.get("precio")
                if precio is None:
                    if "producto" in item and isinstance(item["producto"], dict):
                        precio = item["producto"].get("precio")
                    if isinstance(precio, str):
                        try:
                            precio = float(precio)
                        except:
                            precio = 0
                subtotal = item.get("subtotal")
                if subtotal is None and precio is not None:
                    subtotal = cantidad * precio
                if subtotal is not None:
                    total_productos += subtotal
            monto_envio = 0
            if 'envios' in pedido and pedido['envios']:
                envio = pedido['envios'][0]
                monto_envio = envio.get('monto_envio', 0)
                if isinstance(monto_envio, str):
                    try:
                        monto_envio = float(monto_envio)
                    except:
                        monto_envio = 0
            monto_total_calculado = total_productos + monto_envio

            for idx in range(0, len(campos_2col), 2):
                row = idx // 2
                for col in range(2):
                    if idx + col >= len(campos_2col):
                        continue
                    label, field = campos_2col[idx + col]
                    # Label
                    lbl = ctk.CTkLabel(
                        grid_frame,
                        text=f"{label}",
                        font=("Quicksand", 12, "bold"),
                        text_color="#2E6B5C",
                        anchor="w"
                    )
                    lbl.grid(row=row, column=col*2, sticky="w", padx=(15,5), pady=(8 if row==0 else 4, 4))
                    # Valor
                    if field == "monto_total":
                        valor = f"S/. {monto_total_calculado:.2f}"
                    elif field == "estado":
                        # Migrar estado antiguo a nuevo y mostrar con label legible
                        estado_actual = EstadosDeprecados.migrar_estado(pedido.get("estado", ""))
                        valor = obtener_label_estado('pedido', estado_actual)
                        # Cambiar color según el estado
                        color_estado = obtener_color_estado('pedido', estado_actual)
                    elif field == "estado_pago":
                        valor = "-"
                        if 'pagos' in pedido and pedido['pagos']:
                            estado_pago = pedido['pagos'][0].get('estado_pago', '-')
                            if estado_pago != '-':
                                valor = obtener_label_estado('pago', estado_pago)
                            else:
                                valor = estado_pago
                    elif field == "metodo_pago":
                        valor = "-"
                        if 'pagos' in pedido and pedido['pagos']:
                            pago = pedido['pagos'][0]
                            valor = pago.get('metodo_pago_nombre_snapshot') or (pago.get('metodos_pago', {}) or {}).get('nombre', '-')
                    elif field == "precio_productos":
                        valor = f"S/. {total_productos:.2f}"
                    elif field == "costo_envio":
                        valor = f"S/. {monto_envio:.2f}" if monto_envio > 0 else "Gratis"
                    elif field == "direccion":
                        valor = direccion
                        val_lbl = ctk.CTkLabel(
                            grid_frame,
                            text=str(valor),
                            font=("Quicksand", 12),
                            text_color="#424242",
                            anchor="w",
                            wraplength=450,
                            justify="left"
                        )
                        val_lbl.grid(row=row, column=col*2+1, columnspan=3, sticky="we", padx=(5,15), pady=(8 if row==0 else 4, 4))
                        # FECHA DEL PEDIDO DEBAJO DE DIRECCIÓN
                        fecha_pedido_raw = pedido.get('fecha_creacion', '-')
                        fecha_pedido = DateTimeHelper.format_datetime(fecha_pedido_raw) if fecha_pedido_raw != '-' else '-'
                        fecha_lbl = ctk.CTkLabel(
                            grid_frame,
                            text=f"🗓️ Fecha del pedido: {fecha_pedido}",
                            font=("Quicksand", 13, "bold"),
                            text_color="#424242",
                            anchor="w"
                        )
                        fecha_lbl.grid(row=row+1, column=0, columnspan=4, sticky="w", padx=(15,5), pady=(0, 8))
                        continue
                    else:
                        valor = pedido.get(field, '-')
                    
                    # Crear label con color especial para estados
                    if field == "estado":
                        val_lbl = ctk.CTkLabel(
                            grid_frame,
                            text=str(valor),
                            font=("Quicksand", 12, "bold"),
                            text_color=color_estado,
                            anchor="w",
                            wraplength=100,
                            justify="left"
                        )
                    else:
                        val_lbl = ctk.CTkLabel(
                            grid_frame,
                            text=str(valor),
                            font=("Quicksand", 12),
                            text_color="#424242",
                            anchor="w",
                            wraplength=100,
                            justify="left"
                        )
                    val_lbl.grid(row=row, column=col*2+1, sticky="w", padx=(5,15), pady=(8 if row==0 else 4, 4))
            # Ajustar columnas y filas para separación y estética
            for col in range(4):
                grid_frame.grid_columnconfigure(col, weight=1 if col%2==1 else 0, minsize=100 if col%2==0 else 120)
            for i in range((len(campos_2col)+1)//2):
                grid_frame.grid_rowconfigure(i, pad=6)

            # --- Productos del pedido (mejorado, tarjetas anchas con scroll) ---
            ctk.CTkLabel(
                main_frame,
                text="Productos del pedido",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(anchor="w", padx=4, pady=(0, 6))

            items = pedido.get("pedido_items") or pedido.get("items") or []
            if not items:
                ctk.CTkLabel(
                    main_frame,
                    text="No hay productos en este pedido",
                    font=("Quicksand", 14, "italic"),
                    text_color="#2E6B5C"
                ).pack(anchor="w", padx=14, pady=12)
            else:
                # Frame contenedor para productos con scroll
                productos_container = ctk.CTkFrame(main_frame, fg_color="#FAFFF6")
                productos_container.pack(fill="both", expand=True, padx=0, pady=0)
                
                # Canvas para scroll
                productos_canvas = ctk.CTkCanvas(productos_container, bg="#FAFFF6", highlightthickness=0, height=250)
                productos_canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)
                
                # Scrollbar
                scrollbar = ctk.CTkScrollbar(productos_container, orientation="vertical", command=productos_canvas.yview)
                scrollbar.pack(side="right", fill="y")
                
                productos_canvas.configure(yscrollcommand=scrollbar.set)
                
                # Frame interno para los productos
                productos_frame = ctk.CTkFrame(productos_container, fg_color="#FAFFF6")
                productos_inner_id = productos_canvas.create_window((0, 0), window=productos_frame, anchor="nw", width=productos_canvas.winfo_width())
                
                # Configurar scroll y ancho
                def configure_scroll(event):
                    productos_canvas.configure(scrollregion=productos_canvas.bbox("all"))
                    # Asegurar que el frame interno ocupe todo el ancho del canvas
                    canvas_width = productos_canvas.winfo_width()
                    if canvas_width > 1:
                        productos_canvas.itemconfig(productos_inner_id, width=canvas_width)
                
                productos_frame.bind("<Configure>", configure_scroll)
                
                # Scroll con mouse
                def on_mousewheel(event):
                    productos_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
                productos_canvas.bind_all("<MouseWheel>", on_mousewheel)
                for item in items:
                    try:
                        prod_card = ctk.CTkFrame(productos_frame, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E0E0E0")
                        prod_card.pack(fill="x", padx=2, pady=3)
                        # Extraer datos
                        nombre_producto = item.get("producto")
                        if isinstance(nombre_producto, dict):
                            nombre_producto = nombre_producto.get("nombre", "-")
                        if not nombre_producto:
                            nombre_producto = item.get("producto_nombre_snapshot", "-")
                        cantidad = item.get("cantidad", 1)
                        precio = item.get("precio")
                        if precio is None:
                            if "producto" in item and isinstance(item["producto"], dict):
                                precio = item["producto"].get("precio")
                            if isinstance(precio, str):
                                try:
                                    precio = float(precio)
                                except:
                                    precio = 0
                        subtotal = item.get("subtotal")
                        if subtotal is None and precio is not None:
                            subtotal = cantidad * precio
                        categoria = None
                        descripcion = None
                        peso = None
                        if "producto" in item and isinstance(item["producto"], dict):
                            producto_obj = item["producto"]
                            categoria = producto_obj.get("categoria", {}).get("nombre") if producto_obj.get("categoria") else None
                            descripcion = producto_obj.get("descripcion")
                            peso = producto_obj.get("peso")
                        # Layout horizontal
                        content_row = ctk.CTkFrame(prod_card, fg_color="transparent")
                        content_row.pack(fill="x", padx=4, pady=4)
                        # Imagen (placeholder)
                        img_label = ctk.CTkLabel(content_row, text="🛒", font=("Arial", 24), text_color="#E0E0E0", width=50, height=50)
                        img_label.pack(side="left", padx=(0, 12), pady=0)
                        # Info principal
                        info_col = ctk.CTkFrame(content_row, fg_color="transparent")
                        info_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
                        ctk.CTkLabel(info_col, text=nombre_producto or "-", font=("Quicksand", 13, "bold"), text_color="#2E6B5C").pack(anchor="w", pady=(0,2))
                        if categoria:
                            ctk.CTkLabel(info_col, text=f"{categoria}", font=("Quicksand", 12, "italic"), text_color="#2E6B5C").pack(anchor="w")
                        if descripcion:
                            ctk.CTkLabel(info_col, text=descripcion, font=("Quicksand", 11), text_color="#424242", wraplength=450, anchor="w").pack(anchor="w", pady=(0,3))
                        # Info secundaria
                        info_sec = ctk.CTkFrame(info_col, fg_color="transparent")
                        info_sec.pack(anchor="w", pady=(1,0))
                        ctk.CTkLabel(info_sec, text=f"Cantidad: {cantidad}", font=("Quicksand", 11, "bold"), text_color="#424242").pack(side="left", padx=(0,10))
                        ctk.CTkLabel(info_sec, text=f"Precio Unitario: S/. {precio:.2f}" if precio is not None else "Precio: -", font=("Quicksand", 11), text_color="#424242").pack(side="left", padx=(0,10))
                        ctk.CTkLabel(info_sec, text=f"Subtotal: S/. {subtotal:.2f}" if subtotal is not None else "Subtotal: -", font=("Quicksand", 11, "bold"), text_color="#2E6B5C").pack(side="left", padx=(0,10))
                        if peso:
                            ctk.CTkLabel(info_sec, text=f"Peso: {peso}", font=("Quicksand", 11), text_color="#424242").pack(side="left", padx=(0,10))
                    except Exception as prod_err:
                        print(f"Error al renderizar producto: {prod_err}")
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
            self.dialog.destroy()