import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
from datetime import datetime
import os
from src.core.config import INVENTORY_MANAGEMENT_ENDPOINTS, STOCK_OPERATIONS_CONFIG
from src.shared.utils import APIHandler, SessionManager

def es_wayland():
    """Detectar si estamos ejecutando en Wayland"""
    return os.environ.get('WAYLAND_DISPLAY') is not None or os.environ.get('XDG_SESSION_TYPE') == 'wayland'

class StockManagementSection(ctk.CTkFrame):
    """Sección dedicada al control de stock e inventario"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variables de datos
        self.productos_stock = []
        self.productos_filtrados = []
        self.producto_seleccionado = None
        
        # Configurar layout responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # La tabla se expande
        
        self.setup_ui()
        self.cargar_inventario()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Título
        titulo = ctk.CTkLabel(self, text="Control de Stock e Inventario", 
                            font=("Quicksand", 24, "bold"),
                            text_color="#2E6B5C")
        titulo.grid(row=0, column=0, pady=20, sticky="ew")

        # Frame de controles (botones y filtros)
        controles_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        controles_frame.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")
        controles_frame.grid_columnconfigure(1, weight=1)  # El campo de búsqueda se expande

        # Botón Actualizar Stock
        actualizar_btn = ctk.CTkButton(
            controles_frame,
            text="📈 Actualizar Stock",
            command=self.gestionar_stock_general,
            font=("Quicksand", 12, "bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=150,
            height=35
        )
        actualizar_btn.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Frame de filtros reorganizado para mejor alineación
        filtros_frame = ctk.CTkFrame(controles_frame, fg_color="transparent")
        filtros_frame.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        filtros_frame.grid_columnconfigure(2, weight=1)  # El campo de búsqueda se expande

        # Sección de búsqueda agrupada
        busqueda_group = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        busqueda_group.grid(row=0, column=0, sticky="w")

        # Label "Buscar por:"
        ctk.CTkLabel(
            busqueda_group,
            text="Buscar por:",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        # Dropdown para tipo de búsqueda
        self.tipo_busqueda = ctk.CTkOptionMenu(
            busqueda_group,
            values=["Producto", "Categoría"],
            font=("Quicksand", 11),
            fg_color="#4A934A",
            button_color="#367832",
            width=120
        )
        self.tipo_busqueda.grid(row=0, column=1, padx=(0, 10), sticky="w")

        # Campo de búsqueda junto al dropdown
        self.busqueda_entry = ctk.CTkEntry(
            filtros_frame,
            placeholder_text="Buscar productos...",
            font=("Quicksand", 12),
            width=250
        )
        self.busqueda_entry.grid(row=0, column=2, padx=(10, 20), sticky="ew")
        self.busqueda_entry.bind("<KeyRelease>", self.filtrar_productos)

        # Sección de estado agrupada
        estado_group = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        estado_group.grid(row=0, column=3, sticky="w")

        # Label "Estado:"
        ctk.CTkLabel(
            estado_group,
            text="Estado:",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        # Dropdown para estado de stock
        self.estado_filter = ctk.CTkOptionMenu(
            estado_group,
            values=["Todos", "Stock Bajo", "Sin Stock", "Stock Normal"],
            command=self.filtrar_productos,
            font=("Quicksand", 11),
            fg_color="#4A934A",
            button_color="#367832",
            width=150
        )
        self.estado_filter.grid(row=0, column=1, sticky="w")

        # Tabla de stock
        self.setup_tabla()

    def setup_tabla(self):
        """Configurar la tabla de stock"""
        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        tabla_frame.grid(row=2, column=0, pady=(0, 20), padx=20, sticky="nsew")

        # Crear la tabla
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Stock.Treeview",
                       background="#ffffff",
                       foreground="#2E6B5C",
                       rowheight=35,
                       fieldbackground="#ffffff",
                       font=("Quicksand", 11))
        style.configure("Stock.Treeview.Heading",
                       background="#367832",
                       foreground="white",
                       relief="flat",
                       font=("Quicksand", 12, "bold"))
        
        # Configurar selección de filas y hover effects
        style.map("Stock.Treeview",
                 background=[('selected', '#E8F5E8')],
                 foreground=[('selected', '#2E6B5C')])

        # Definir columnas optimizadas para stock
        columns = ("id", "producto", "categoria", "stock_actual", "precio", "estado_stock", "valor_inventario")
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show='headings', style="Stock.Treeview")
        
        # Tags para colorear estados de stock
        self.tabla.tag_configure('stock_bajo', background='#FFF3CD', foreground='#856404')
        self.tabla.tag_configure('sin_stock', background='#F8D7DA', foreground='#721C24')
        self.tabla.tag_configure('stock_normal', background='#D4EDDA', foreground='#155724')
        
        # Configurar encabezados y columnas
        self.tabla.heading("id", text="ID")
        self.tabla.heading("producto", text="Producto")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.heading("stock_actual", text="Stock Actual")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("estado_stock", text="Estado")
        self.tabla.heading("valor_inventario", text="Valor Inventario")
        
        # Configurar anchos y alineación de columnas
        self.tabla.column("id", width=60, minwidth=50, anchor="center")
        self.tabla.column("producto", width=200, minwidth=150, anchor="w")
        self.tabla.column("categoria", width=140, minwidth=120, anchor="center")
        self.tabla.column("stock_actual", width=100, minwidth=80, anchor="center")
        self.tabla.column("precio", width=100, minwidth=80, anchor="center")
        self.tabla.column("estado_stock", width=120, minwidth=100, anchor="center")
        self.tabla.column("valor_inventario", width=140, minwidth=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Eventos de la tabla
        self.tabla.bind('<<TreeviewSelect>>', self.on_select)
        self.tabla.bind('<Double-1>', self.on_double_click)
        self.tabla.bind('<Button-3>', self.on_right_click)

        # Frame para estadísticas
        stats_frame = ctk.CTkFrame(self, fg_color="#E8F5E8", corner_radius=10)
        stats_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="🔄 Cargando estadísticas de inventario...",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        )
        self.stats_label.grid(row=0, column=0, padx=20, pady=10)
            
    def cargar_inventario(self):
        """Cargar inventario desde la API y fusionar con datos de productos para obtener info adicional (imagen, peso, etc.)"""
        try:
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}

            # Obtener inventario (stock, categoría, etc.)
            url_inventario = INVENTORY_MANAGEMENT_ENDPOINTS['inventory']['products_list']
            response_inv = APIHandler.make_request('GET', url_inventario, headers=headers)

            # Obtener productos (imagen, peso, descripción, etc.)
            url_productos = INVENTORY_MANAGEMENT_ENDPOINTS['products']['list']
            response_prod = APIHandler.make_request('GET', url_productos, headers=headers)

            if response_inv['status_code'] == 200 and response_prod['status_code'] == 200:
                # Crear diccionario de productos por id
                productos_api = response_prod['data']['data'] if isinstance(response_prod['data'], dict) and 'data' in response_prod['data'] else response_prod['data']
                productos_dict = {}
                for prod in productos_api:
                    prod_id = prod.get('id') or prod.get('id_producto')
                    if prod_id is not None:
                        productos_dict[prod_id] = prod

                # Fusionar datos de inventario con datos de producto
                self.procesar_respuesta_inventario(response_inv['data'], productos_dict)
            else:
                print(f"Error al cargar inventario/productos: {response_inv.get('data', 'Error inventario')} | {response_prod.get('data', 'Error productos')}")
                self.cargar_inventario_ejemplo()
        except Exception as e:
            print(f"Error al cargar inventario: {str(e)}")
            self.cargar_inventario_ejemplo()
        self.actualizar_tabla()

    def procesar_respuesta_inventario(self, api_data, productos_dict=None):
        """Procesar la respuesta de la API para inventario y fusionar con info de productos si está disponible"""
        try:
            if isinstance(api_data, dict) and 'data' in api_data:
                productos_api = api_data['data']
            elif isinstance(api_data, list):
                productos_api = api_data
            else:
                productos_api = []

            self.productos_stock = []
            for producto in productos_api:
                if not isinstance(producto, dict):
                    continue
                prod_id = producto.get('id_producto') or producto.get('id')
                prod_extra = productos_dict.get(prod_id) if productos_dict else {}
                inventario = producto.get('inventario', {})
                producto_stock = {
                    "id": prod_id,
                    "nombre": producto.get('nombre_producto', producto.get('nombre', 'Sin nombre')),
                    "categoria": self.obtener_categoria_nombre(producto),
                    "stock_actual": inventario.get('cantidad_disponible', 0),
                    "precio": self.convertir_precio(producto.get('precio', 0)),
                    "estado": producto.get('estado_producto', producto.get('estado', 'activo')),
                    "descripcion": prod_extra.get('descripcion', ''),
                    "peso": prod_extra.get('peso', ''),
                    "imagen": prod_extra.get('url_imagen', ''),
                    "fecha_creacion": prod_extra.get('fecha_creacion', ''),
                    "categoria_info": producto.get('categoria', {})
                }
                producto_stock['estado_stock'] = self.calcular_estado_stock(producto_stock['stock_actual'])
                producto_stock['valor_inventario'] = producto_stock['stock_actual'] * producto_stock['precio']
                self.productos_stock.append(producto_stock)
            self.productos_filtrados = self.productos_stock.copy()
        except Exception as e:
            print(f"Error al procesar respuesta de inventario: {str(e)}")
            self.cargar_inventario_ejemplo()

    def obtener_categoria_nombre(self, producto):
        """Obtener nombre de categoría del producto (acepta string o dict)"""
        categoria = producto.get('categoria', None)
        if isinstance(categoria, dict):
            return categoria.get('nombre', 'Sin categoría')
        elif isinstance(categoria, str):
            return categoria
        return 'Sin categoría'

    def convertir_precio(self, precio):
        """Convertir precio de string a float de manera segura"""
        try:
            if isinstance(precio, str):
                precio_limpio = precio.replace(',', '').replace('$', '').replace('S/.', '').strip()
                return float(precio_limpio)
            elif isinstance(precio, (int, float)):
                return float(precio)
            else:
                return 0.0
        except (ValueError, AttributeError):
            return 0.0

    def calcular_estado_stock(self, stock):
        """Calcular estado del stock basado en la cantidad"""
        if stock == 0:
            return "Sin Stock"
        elif stock <= 10:  # Umbral configurable
            return "Stock Bajo"
        else:
            return "Stock Normal"

    def cargar_inventario_ejemplo(self):
        """Cargar datos de ejemplo para el inventario"""
        self.productos_stock = [
            {
                "id": 1,
                "nombre": "Fresas Premium 500g",
                "categoria": "Paquetes de Fresas",
                "stock_actual": 25,
                "precio": 15.0,
                "estado": "activo",
                "estado_stock": "Stock Normal",
                "valor_inventario": 375.0
            },
            {
                "id": 2,
                "nombre": "Fresas Orgánicas 1kg",
                "categoria": "Paquetes de Fresas",
                "stock_actual": 5,
                "precio": 28.0,
                "estado": "activo",
                "estado_stock": "Stock Bajo",
                "valor_inventario": 140.0
            },
            {
                "id": 3,
                "nombre": "Mermelada de Fresa Artesanal",
                "categoria": "Mermeladas",
                "stock_actual": 0,
                "precio": 12.0,
                "estado": "activo",
                "estado_stock": "Sin Stock",
                "valor_inventario": 0.0
            },
            {
                "id": 4,
                "nombre": "Combo Familiar",
                "categoria": "Combos Especiales",
                "stock_actual": 15,
                "precio": 35.0,
                "estado": "activo",
                "estado_stock": "Stock Normal",
                "valor_inventario": 525.0
            }
        ]
        self.productos_filtrados = self.productos_stock.copy()

    def filtrar_productos(self, event=None):
        """Filtrar productos según los criterios de búsqueda"""
        try:
            busqueda = self.busqueda_entry.get().lower()
            tipo_busqueda = self.tipo_busqueda.get()
            estado_filtro = self.estado_filter.get()
            
            self.productos_filtrados = []
            
            for producto in self.productos_stock:
                # Filtro por texto de búsqueda
                if busqueda:
                    if tipo_busqueda == "Producto":
                        if busqueda not in producto['nombre'].lower():
                            continue
                    elif tipo_busqueda == "Categoría":
                        if busqueda not in producto['categoria'].lower():
                            continue
                
                # Filtro por estado de stock
                if estado_filtro != "Todos":
                    if estado_filtro == "Stock Bajo" and producto['estado_stock'] != "Stock Bajo":
                        continue
                    elif estado_filtro == "Sin Stock" and producto['estado_stock'] != "Sin Stock":
                        continue
                    elif estado_filtro == "Stock Normal" and producto['estado_stock'] != "Stock Normal":
                        continue
                
                self.productos_filtrados.append(producto)
            
            self.actualizar_tabla()
            
        except Exception as e:
            print(f"Error al filtrar productos: {str(e)}")

    def actualizar_tabla(self):
        """Actualizar tabla de stock"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            
            # Estadísticas
            total_productos = len(self.productos_filtrados)
            valor_total_inventario = sum(p['valor_inventario'] for p in self.productos_filtrados)
            productos_sin_stock = len([p for p in self.productos_filtrados if p['estado_stock'] == "Sin Stock"])
            productos_stock_bajo = len([p for p in self.productos_filtrados if p['estado_stock'] == "Stock Bajo"])
            
            # Agregar productos a la tabla
            for producto in self.productos_filtrados:
                # Formatear precio en soles peruanos
                precio_formateado = f"S/. {producto['precio']:,.2f}"
                valor_inventario_formateado = f"S/. {producto['valor_inventario']:,.2f}"
                
                # Determinar tag para colorear
                tag = ""
                if producto['estado_stock'] == "Sin Stock":
                    tag = "sin_stock"
                elif producto['estado_stock'] == "Stock Bajo":
                    tag = "stock_bajo"
                else:
                    tag = "stock_normal"
                
                # Truncar nombre si es muy largo
                nombre = producto['nombre']
                if len(nombre) > 30:
                    nombre = nombre[:27] + "..."
                
                item = self.tabla.insert("", "end", values=(
                    producto['id'],
                    nombre,
                    producto['categoria'],
                    producto['stock_actual'],
                    precio_formateado,
                    producto['estado_stock'],
                    valor_inventario_formateado
                ), tags=(tag,))
            
            # Actualizar estadísticas
            stats_text = (f"📊 Total: {total_productos} productos | "
                         f"💰 Valor inventario: S/. {valor_total_inventario:,.2f} | "
                         f"⚠️ Stock bajo: {productos_stock_bajo} | "
                         f"❌ Sin stock: {productos_sin_stock}")
            
            self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            print(f"Error al actualizar tabla: {str(e)}")
            self.stats_label.configure(text="❌ Error al cargar estadísticas")

    def gestionar_stock_general(self):
        """Abrir modal para gestión general de stock"""
        try:
            if not self.productos_filtrados:
                messagebox.showwarning("Advertencia", "No hay productos para gestionar")
                return
                
            # Crear modal para gestión de stock
            modal = ModalGestionStock(self, self.productos_filtrados, self.actualizar_stock_callback)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir gestión de stock: {str(e)}")

    def actualizar_stock_callback(self, producto_id, nuevo_stock):
        """Callback para actualizar stock de un producto: actualiza en API y recarga inventario para máxima consistencia"""
        try:
            # Actualizar en la API primero
            self.actualizar_stock_api(producto_id, nuevo_stock)
            # Recargar inventario desde la API para máxima consistencia
            self.cargar_inventario()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar stock: {str(e)}")

    def actualizar_stock_api(self, producto_id, nuevo_stock):
        """Actualizar stock en la API"""
        try:
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            # Usar el endpoint de actualización de stock correcto
            url = INVENTORY_MANAGEMENT_ENDPOINTS['inventory']['update_stock'].format(id=producto_id)
            payload = {
                'cantidad_disponible': nuevo_stock,
                'accion': 'establecer'
            }
            
            response = APIHandler.make_request('PATCH', url, headers=headers, data=payload)
            
            if response['status_code'] == 200:
                print(f"Stock actualizado exitosamente para producto {producto_id}")
            else:
                print(f"Error al actualizar stock en API: {response.get('data', 'Error desconocido')}")
                
        except Exception as e:
            print(f"Error al actualizar stock en API: {str(e)}")

    def on_select(self, event):
        """Manejar selección de fila"""
        try:
            selection = self.tabla.selection()
            if selection:
                item = self.tabla.item(selection[0])
                producto_id = item['values'][0]
                
                # Buscar producto completo
                self.producto_seleccionado = None
                for producto in self.productos_filtrados:
                    if producto['id'] == producto_id:
                        self.producto_seleccionado = producto
                        break
                        
        except Exception as e:
            print(f"Error al seleccionar producto: {str(e)}")

    def on_double_click(self, event):
        """Manejar doble clic para editar stock"""
        try:
            if self.producto_seleccionado:
                # Abrir modal para editar stock específico
                modal = ModalEditarStock(self, self.producto_seleccionado, self.actualizar_stock_callback)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir editor de stock: {str(e)}")

    def on_right_click(self, event):
        """Manejar clic derecho para menú contextual"""
        try:
            # Identificar item bajo el cursor
            item = self.tabla.identify_row(event.y)
            if item:
                self.tabla.selection_set(item)
                self.on_select(event)
                
                # Crear menú contextual
                context_menu = tk.Menu(self, tearoff=0)
                context_menu.add_command(label="📝 Editar Stock", command=lambda: self.on_double_click(event))
                context_menu.add_command(label="📊 Ver Detalles", command=self.ver_detalles_producto)
                context_menu.add_separator()
                context_menu.add_command(label="➕ Aumentar Stock", command=self.aumentar_stock)
                context_menu.add_command(label="➖ Reducir Stock", command=self.reducir_stock)
                
                # Mostrar menú
                context_menu.tk_popup(event.x_root, event.y_root)
                
        except Exception as e:
            print(f"Error en menú contextual: {str(e)}")

    def ver_detalles_producto(self):
        """Ver detalles completos del producto"""
        if self.producto_seleccionado:
            modal = ModalDetalleStock(self, self.producto_seleccionado)

    def aumentar_stock(self):
        """Aumentar stock del producto seleccionado"""
        if self.producto_seleccionado:
            modal = ModalCambiarStock(self, self.producto_seleccionado, "aumentar", self.actualizar_stock_callback)

    def reducir_stock(self):
        """Reducir stock del producto seleccionado"""
        if self.producto_seleccionado:
            modal = ModalCambiarStock(self, self.producto_seleccionado, "reducir", self.actualizar_stock_callback)


class ModalGestionStock(ctk.CTkToplevel):
    """Modal para gestión general de stock"""
    
    def __init__(self, parent, productos, callback):
        super().__init__(parent)
        self.parent = parent
        self.productos = productos
        self.callback = callback
        
        self.configurar_modal()
        self.setup_ui()
        
    def configurar_modal(self):
        """Configurar propiedades del modal"""
        self.title("Gestión de Stock")
        self.geometry("800x600")
        self.resizable(False, False)
        self.transient(self.parent)
        self.after_idle(self.grab_set)
        self.center_window()
        
    def setup_ui(self):
        """Configurar interfaz del modal"""
        from PIL import Image, ImageTk
        import requests
        from io import BytesIO

        # Título
        titulo = ctk.CTkLabel(self, text="Gestión General de Stock", font=("Quicksand", 20, "bold"))
        titulo.pack(pady=20)

        # Información
        info_text = "Selecciona productos y actualiza su stock de manera masiva"
        info_label = ctk.CTkLabel(self, text=info_text, font=("Quicksand", 12))
        info_label.pack(pady=(0, 20))

        # Lista de productos (con imagen y campos)
        products_frame = ctk.CTkFrame(self)
        products_frame.pack(fill="both", expand=True, padx=20, pady=20)

        for idx, producto in enumerate(self.productos):
            row_frame = ctk.CTkFrame(products_frame, fg_color="#F5F5F5", corner_radius=10)
            row_frame.pack(fill="x", pady=8, padx=8)
            row_frame.grid_columnconfigure(0, weight=0)
            row_frame.grid_columnconfigure(1, weight=1)

            # Imagen
            image_label = ctk.CTkLabel(row_frame, text="Cargando imagen...", width=60, height=60)
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
            imagen_preview = None
            url_imagen = producto.get('url_imagen') or producto.get('imagen')
            if url_imagen and url_imagen != 'productos/default.jpg':
                try:
                    if url_imagen.startswith('http'):
                        response = requests.get(url_imagen, timeout=8)
                        if response.status_code == 200:
                            imagen_data = BytesIO(response.content)
                            imagen = Image.open(imagen_data)
                            imagen.thumbnail((60, 60), Image.Resampling.LANCZOS)
                            imagen_preview = ImageTk.PhotoImage(imagen)
                            image_label.configure(image=imagen_preview, text="")
                            image_label.image = imagen_preview
                        else:
                            image_label.configure(text="No imagen")
                    else:
                        imagen = Image.open(url_imagen)
                        imagen.thumbnail((60, 60), Image.Resampling.LANCZOS)
                        imagen_preview = ImageTk.PhotoImage(imagen)
                        image_label.configure(image=imagen_preview, text="")
                        image_label.image = imagen_preview
                except Exception:
                    image_label.configure(text="No imagen")
            else:
                image_label.configure(text="Sin imagen")

            # Info producto
            info_text = f"{producto['nombre']}\nCategoría: {producto.get('categoria', '-')}\nStock: {producto['stock_actual']} | Precio: S/. {producto['precio']:,.2f}"
            ctk.CTkLabel(row_frame, text=info_text, font=("Quicksand", 12), anchor="w", justify="left").grid(row=0, column=1, sticky="w", padx=5, pady=(10, 0))

        # Botones
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(buttons_frame, text="Cerrar", command=self.destroy).pack(side="right", padx=5)
        
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


class ModalEditarStock(ctk.CTkToplevel):
    """Modal para editar stock de un producto específico"""
    
    def __init__(self, parent, producto, callback):
        super().__init__(parent)
        self.parent = parent
        self.producto = producto
        self.callback = callback
        
        self.configurar_modal()
        self.setup_ui()
        
    def configurar_modal(self):
        """Configurar propiedades del modal"""
        self.title("Editar Stock")
        self.geometry("600x340")  # Más compacto
        self.resizable(False, False)
        self.transient(self.parent)
        self.after_idle(self.grab_set)
        self.center_window()
        
    def setup_ui(self):
        """Configurar interfaz del modal"""
        from PIL import Image, ImageTk
        import requests
        from io import BytesIO

        # Título
        titulo = ctk.CTkLabel(self, text="Editar Stock del Producto", font=("Quicksand", 20, "bold"))
        titulo.pack(pady=(20, 10))

        # Frame principal para info y preview
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="x", padx=30, pady=10)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=2)

        # Info producto (izquierda)
        info_frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=10)
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        ctk.CTkLabel(info_frame, text=f"Producto:", font=("Quicksand", 13, "bold"), anchor="w").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(info_frame, text=self.producto['nombre'], font=("Quicksand", 13), anchor="w", justify="left").pack(anchor="w", padx=10, pady=(0, 0))
        ctk.CTkLabel(info_frame, text=f"Categoría: {self.producto.get('categoria', '-')}", font=("Quicksand", 12), anchor="w").pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkLabel(info_frame, text=f"Stock actual: {self.producto['stock_actual']}", font=("Quicksand", 12), anchor="w").pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkLabel(info_frame, text=f"Precio: S/. {self.producto['precio']:,.2f}", font=("Quicksand", 12), anchor="w").pack(anchor="w", padx=10, pady=(5, 10))

        # Imagen producto (derecha)
        image_frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=10, width=150, height=150)
        image_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        image_frame.grid_propagate(False)
        self.imagen_label = ctk.CTkLabel(image_frame, text="Cargando imagen...", width=140, height=140)
        self.imagen_label.pack(expand=True, fill="both", padx=5, pady=5)
        self.imagen_preview = None

        # Cargar imagen del producto
        url_imagen = self.producto.get('url_imagen') or self.producto.get('imagen')
        if url_imagen and url_imagen != 'productos/default.jpg':
            try:
                if url_imagen.startswith('http'):
                    response = requests.get(url_imagen, timeout=8)
                    if response.status_code == 200:
                        imagen_data = BytesIO(response.content)
                        imagen = Image.open(imagen_data)
                        imagen.thumbnail((140, 140), Image.Resampling.LANCZOS)
                        self.imagen_preview = ImageTk.PhotoImage(imagen)
                        self.imagen_label.configure(image=self.imagen_preview, text="")
                    else:
                        self.imagen_label.configure(text="No se pudo cargar la imagen")
                else:
                    # Intentar cargar local
                    imagen = Image.open(url_imagen)
                    imagen.thumbnail((140, 140), Image.Resampling.LANCZOS)
                    self.imagen_preview = ImageTk.PhotoImage(imagen)
                    self.imagen_label.configure(image=self.imagen_preview, text="")
            except Exception as e:
                self.imagen_label.configure(text="No se pudo cargar la imagen")
        else:
            self.imagen_label.configure(text="Sin imagen")

        # Campo de nuevo stock y botones en la misma fila
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(10, 0))
        action_frame.grid_columnconfigure(0, weight=2)
        action_frame.grid_columnconfigure(1, weight=1)
        # Nuevo stock (izquierda)
        entry_inner = ctk.CTkFrame(action_frame, fg_color="transparent")
        entry_inner.grid(row=0, column=0, sticky="w", padx=(0, 10))
        ctk.CTkLabel(entry_inner, text="Nuevo stock:", font=("Quicksand", 13, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.stock_entry = ctk.CTkEntry(entry_inner, width=120, font=("Quicksand", 13))
        self.stock_entry.pack(anchor="w", padx=5, pady=(0, 10))
        self.stock_entry.insert(0, str(self.producto['stock_actual']))
        # Botones (derecha)
        btns_inner = ctk.CTkFrame(action_frame, fg_color="transparent")
        btns_inner.grid(row=0, column=1, sticky="e", padx=(10, 0))
        btn_actualizar = ctk.CTkButton(
            btns_inner, text="Actualizar", command=self.actualizar_stock,
            fg_color="#4CAF50", hover_color="#388E3C",
            font=("Quicksand", 13, "bold"), height=38, width=110, corner_radius=8
        )
        btn_actualizar.pack(side="left", padx=(0, 8))
        btn_cancelar = ctk.CTkButton(
            btns_inner, text="Cancelar", command=self.destroy,
            font=("Quicksand", 13, "bold"), height=38, width=110,
            fg_color="#E0E0E0", text_color="#2E6B5C", hover_color="#BDBDBD", corner_radius=8
        )
        btn_cancelar.pack(side="left")
        
    def actualizar_stock(self):
        """Actualizar stock del producto usando la API set_stock"""
        try:
            nuevo_stock = int(self.stock_entry.get())
            if nuevo_stock < 0:
                raise ValueError("El stock no puede ser negativo")

            # Llamada a la API para establecer el stock
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            url = INVENTORY_MANAGEMENT_ENDPOINTS['inventory']['update_stock'].format(id=self.producto['id'])
            payload = {'cantidad_disponible': nuevo_stock, 'accion': 'establecer'}
            response = APIHandler.make_request('PATCH', url, headers=headers, data=payload)

            if response['status_code'] == 200:
                self.callback(self.producto['id'], nuevo_stock)
                messagebox.showinfo("Éxito", "Stock actualizado correctamente")
                self.destroy()
            else:
                msg = response.get('data', 'Error desconocido')
                messagebox.showerror("Error", f"Error al actualizar stock: {msg}")
        except ValueError as e:
            messagebox.showerror("Error", f"Valor inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar stock: {str(e)}")
            
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


class ModalCambiarStock(ctk.CTkToplevel):
    """Modal para aumentar/reducir stock"""
    
    def __init__(self, parent, producto, accion, callback):
        super().__init__(parent)
        self.parent = parent
        self.producto = producto
        self.accion = accion  # "aumentar" o "reducir"
        self.callback = callback
        
        self.configurar_modal()
        self.setup_ui()
        
    def configurar_modal(self):
        """Configurar propiedades del modal"""
        titulo = "Aumentar Stock" if self.accion == "aumentar" else "Reducir Stock"
        self.title(titulo)
        self.geometry("600x340")  # Más compacto
        self.resizable(False, False)
        self.transient(self.parent)
        self.after_idle(self.grab_set)
        self.center_window()
        
    def setup_ui(self):
        """Configurar interfaz del modal"""
        from PIL import Image, ImageTk
        import requests
        from io import BytesIO

        # Título
        titulo_text = f"{'Aumentar' if self.accion == 'aumentar' else 'Reducir'} Stock"
        titulo = ctk.CTkLabel(self, text=titulo_text, font=("Quicksand", 20, "bold"))
        titulo.pack(pady=(20, 10))

        # Frame principal para info y preview
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="x", padx=30, pady=10)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=2)

        # Info producto (izquierda)
        info_frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=10)
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        ctk.CTkLabel(info_frame, text=f"Producto:", font=("Quicksand", 13, "bold"), anchor="w").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(info_frame, text=self.producto['nombre'], font=("Quicksand", 13), anchor="w", justify="left").pack(anchor="w", padx=10, pady=(0, 0))
        ctk.CTkLabel(info_frame, text=f"Categoría: {self.producto.get('categoria', '-')}", font=("Quicksand", 12), anchor="w").pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkLabel(info_frame, text=f"Stock actual: {self.producto['stock_actual']}", font=("Quicksand", 12), anchor="w").pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkLabel(info_frame, text=f"Precio: S/. {self.producto['precio']:,.2f}", font=("Quicksand", 12), anchor="w").pack(anchor="w", padx=10, pady=(5, 10))

        # Imagen producto (derecha)
        image_frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5", corner_radius=10, width=150, height=150)
        image_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        image_frame.grid_propagate(False)
        self.imagen_label = ctk.CTkLabel(image_frame, text="Cargando imagen...", width=140, height=140)
        self.imagen_label.pack(expand=True, fill="both", padx=5, pady=5)
        self.imagen_preview = None

        # Cargar imagen del producto
        url_imagen = self.producto.get('url_imagen') or self.producto.get('imagen')
        if url_imagen and url_imagen != 'productos/default.jpg':
            try:
                if url_imagen.startswith('http'):
                    response = requests.get(url_imagen, timeout=8)
                    if response.status_code == 200:
                        imagen_data = BytesIO(response.content)
                        imagen = Image.open(imagen_data)
                        imagen.thumbnail((140, 140), Image.Resampling.LANCZOS)
                        self.imagen_preview = ImageTk.PhotoImage(imagen)
                        self.imagen_label.configure(image=self.imagen_preview, text="")
                    else:
                        self.imagen_label.configure(text="No se pudo cargar la imagen")
                else:
                    # Intentar cargar local
                    imagen = Image.open(url_imagen)
                    imagen.thumbnail((140, 140), Image.Resampling.LANCZOS)
                    self.imagen_preview = ImageTk.PhotoImage(imagen)
                    self.imagen_label.configure(image=self.imagen_preview, text="")
            except Exception as e:
                self.imagen_label.configure(text="No se pudo cargar la imagen")
        else:
            self.imagen_label.configure(text="Sin imagen")

        # Campo de cantidad y botones en la misma fila
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(10, 0))
        action_frame.grid_columnconfigure(0, weight=2)
        action_frame.grid_columnconfigure(1, weight=1)
        # Cantidad (izquierda)
        entry_inner = ctk.CTkFrame(action_frame, fg_color="transparent")
        entry_inner.grid(row=0, column=0, sticky="w", padx=(0, 10))
        cantidad_text = f"Cantidad a {'aumentar' if self.accion == 'aumentar' else 'reducir'}:"
        ctk.CTkLabel(entry_inner, text=cantidad_text, font=("Quicksand", 13, "bold")).pack(anchor="w", padx=5, pady=(0, 5))
        self.cantidad_entry = ctk.CTkEntry(entry_inner, width=120, font=("Quicksand", 13))
        self.cantidad_entry.pack(anchor="w", padx=5, pady=(0, 10))
        # Botones (derecha)
        btns_inner = ctk.CTkFrame(action_frame, fg_color="transparent")
        btns_inner.grid(row=0, column=1, sticky="e", padx=(10, 0))
        color = "#4CAF50" if self.accion == "aumentar" else "#FF6B6B"
        hover_color = "#388E3C" if self.accion == "aumentar" else "#C62828"
        btn_aplicar = ctk.CTkButton(
            btns_inner, text="Aplicar", command=self.aplicar_cambio,
            fg_color=color, hover_color=hover_color,
            font=("Quicksand", 13, "bold"), height=38, width=110, corner_radius=8
        )
        btn_aplicar.pack(side="left", padx=(0, 8))
        btn_cancelar = ctk.CTkButton(
            btns_inner, text="Cancelar", command=self.destroy,
            font=("Quicksand", 13, "bold"), height=38, width=110,
            fg_color="#E0E0E0", text_color="#2E6B5C", hover_color="#BDBDBD", corner_radius=8
        )
        btn_cancelar.pack(side="left")
        
    def aplicar_cambio(self):
        """Aplicar cambio en el stock usando la API correspondiente"""
        try:
            cantidad = int(self.cantidad_entry.get())
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")

            stock_actual = self.producto['stock_actual']
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}

            url = INVENTORY_MANAGEMENT_ENDPOINTS['inventory']['update_stock'].format(id=self.producto['id'])
            if self.accion == "aumentar":
                payload = {'cantidad_disponible': cantidad, 'accion': 'aumentar'}
                nuevo_stock = stock_actual + cantidad
            else:  # reducir
                if cantidad > stock_actual:
                    raise ValueError("No se puede reducir más stock del disponible")
                payload = {'cantidad_disponible': cantidad, 'accion': 'reducir'}
                nuevo_stock = stock_actual - cantidad

            response = APIHandler.make_request('PATCH', url, headers=headers, data=payload)

            if response['status_code'] == 200:
                self.callback(self.producto['id'], nuevo_stock)
                messagebox.showinfo("Éxito", f"Stock {'aumentado' if self.accion == 'aumentar' else 'reducido'} correctamente")
                self.destroy()
            else:
                msg = response.get('data', 'Error desconocido')
                messagebox.showerror("Error", f"Error al cambiar stock: {msg}")
        except ValueError as e:
            messagebox.showerror("Error", f"Valor inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar stock: {str(e)}")
            
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


class ModalDetalleStock(ctk.CTkToplevel):
    """Modal para ver detalles completos del producto en stock"""
    
    def __init__(self, parent, producto):
        super().__init__(parent)
        self.parent = parent
        self.producto = producto
        
        self.configurar_modal()
        self.setup_ui()
        
    def configurar_modal(self):
        """Configurar propiedades del modal"""
        self.title("Detalles del Producto")
        self.geometry("500x400")
        self.resizable(False, False)
        self.transient(self.parent)
        self.after_idle(self.grab_set)
        self.center_window()
        
    def setup_ui(self):
        """Configurar interfaz del modal"""
        # Título
        titulo = ctk.CTkLabel(self, text="Detalles del Producto", 
                             font=("Quicksand", 18, "bold"))
        titulo.pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Detalles del producto
        detalles = [
            ("ID:", self.producto['id']),
            ("Nombre:", self.producto['nombre']),
            ("Categoría:", self.producto['categoria']),
            ("Stock Actual:", self.producto['stock_actual']),
            ("Precio:", f"S/. {self.producto['precio']:,.2f}"),
            ("Estado Stock:", self.producto['estado_stock']),
            ("Valor Inventario:", f"S/. {self.producto['valor_inventario']:,.2f}"),
            ("Estado:", self.producto['estado'])
        ]
        
        for i, (label, value) in enumerate(detalles):
            row_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5, padx=10)
            
            ctk.CTkLabel(row_frame, text=label, font=("Quicksand", 12, "bold")).pack(side="left")
            ctk.CTkLabel(row_frame, text=str(value), font=("Quicksand", 12)).pack(side="right")
        
        # Botón cerrar grande y centrado, con relleno
        btn_cerrar = ctk.CTkButton(
            self, text="Cerrar", command=self.destroy,
            font=("Quicksand", 16, "bold"), height=54,
            fg_color="#E0E0E0", text_color="#2E6B5C", hover_color="#BDBDBD", corner_radius=10
        )
        btn_cerrar.pack(pady=40, padx=80, fill="x")
        
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


# Función para testing independiente
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1200x800")
    app.title("Test - Sección de Stock")
    
    # Configurar grid
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    
    # Crear sección de stock
    stock_section = StockManagementSection(app)
    stock_section.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    app.mainloop()
