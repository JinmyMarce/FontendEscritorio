import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk, filedialog
import os
import json
import requests
from PIL import Image, ImageTk
from src.core.config import INVENTORY_MANAGEMENT_ENDPOINTS
from src.shared.utils import APIHandler, SessionManager

class ProductsSection(ctk.CTkFrame):
    """Sección dedicada a la gestión de productos dentro del módulo de inventario"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variables de datos
        self.productos = []
        self.productos_filtrados = []
        self.producto_seleccionado = None
        
        # Configurar layout responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # La tabla se expande
        
        self.setup_ui()
        self.cargar_productos()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Título
        titulo = ctk.CTkLabel(self, text="Gestión de Productos", 
                            font=("Quicksand", 24, "bold"),
                            text_color="#2E6B5C")
        titulo.grid(row=0, column=0, pady=20, sticky="ew")

        # Frame de controles (botones y filtros)
        controles_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        controles_frame.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")
        controles_frame.grid_columnconfigure(1, weight=1)  # El campo de búsqueda se expande

        # Botón Nuevo Producto
        nuevo_btn = ctk.CTkButton(
            controles_frame,
            text="➕ Nuevo Producto",
            command=self.abrir_modal_nuevo_producto,
            font=("Quicksand", 12, "bold"),
            fg_color="#2E6B5C",
            hover_color="#24544A",
            width=150,
            height=35
        )
        nuevo_btn.grid(row=0, column=0, padx=20, pady=15, sticky="w")

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
            values=["Nombre", "Descripción"],
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

        # Dropdown para estado
        self.estado_filter = ctk.CTkOptionMenu(
            estado_group,
            values=["Todos", "Activos", "Inactivos"],
            command=self.filtrar_productos,
            font=("Quicksand", 11),
            fg_color="#4A934A",
            button_color="#367832",
            width=120
        )
        self.estado_filter.grid(row=0, column=1, sticky="w")

        # Tabla de productos
        self.setup_tabla()

    def setup_tabla(self):
        """Configurar la tabla de productos"""
        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        tabla_frame.grid(row=2, column=0, pady=(0, 20), padx=20, sticky="nsew")

        # Crear la tabla
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Productos.Treeview",
                       background="#ffffff",
                       foreground="#2E6B5C",
                       rowheight=35,
                       fieldbackground="#ffffff",
                       font=("Quicksand", 11))
        style.configure("Productos.Treeview.Heading",
                       background="#2E6B5C",
                       foreground="white",
                       relief="flat",
                       font=("Quicksand", 12, "bold"))
        
        # Configurar selección de filas y hover effects
        style.map("Productos.Treeview",
                 background=[('selected', '#E8F5E8')],
                 foreground=[('selected', '#2E6B5C')])

        # Definir columnas optimizadas
        columns = ("id", "nombre", "descripcion", "categoria", "precio", "estado", "peso")
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show='headings', style="Productos.Treeview")
        
        # Configurar encabezados y columnas con anchos optimizados
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("peso", text="Peso")
        
        # Configurar anchos y alineación de columnas
        self.tabla.column("id", width=60, minwidth=50, anchor="center")
        self.tabla.column("nombre", width=180, minwidth=150, anchor="w")
        self.tabla.column("descripcion", width=220, minwidth=200, anchor="w")
        self.tabla.column("categoria", width=140, minwidth=120, anchor="w")
        self.tabla.column("precio", width=100, minwidth=80, anchor="center")
        self.tabla.column("estado", width=100, minwidth=80, anchor="center")
        self.tabla.column("peso", width=120, minwidth=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Eventos de la tabla
        self.tabla.bind('<<TreeviewSelect>>', self.on_select)
        self.tabla.bind('<Double-1>', self.on_double_click)
            
    def cargar_productos(self):
        """Cargar productos desde la API"""
        try:
            url = INVENTORY_MANAGEMENT_ENDPOINTS['products']['list']
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('GET', url, headers=headers)
            if response['status_code'] == 200:
                # Adaptar estructura de datos de la API
                api_data = response['data']
                if isinstance(api_data, dict) and 'data' in api_data:
                    self.productos = api_data['data']  # Extraer el array de productos
                else:
                    self.productos = api_data if isinstance(api_data, list) else []
                    
                self.productos_filtrados = self.productos.copy()
                self.actualizar_tabla()
            else:
                messagebox.showerror("Error", f"Error al cargar productos: {response.get('data', 'Error desconocido')}")
                self.cargar_productos_ejemplo()
                
        except Exception as e:
            print(f"Error al cargar productos: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
            self.cargar_productos_ejemplo()

    def cargar_productos_ejemplo(self):
        """Cargar datos de ejemplo para productos"""
        self.productos = [
            {
                "id_producto": 4,
                "nombre": "Combo Premiun V1",
                "descripcion": "Paquete de fresas con chocolate y cocoa",
                "precio": "32.00",
                "url_imagen": "https://ejemplo.com/combo-premiun.jpg",
                "estado": "activo",
                "peso": "500g por unidad",
                "fecha_creacion": "2025-07-09T03:02:46.000000Z",
                "categorias_id_categoria": 4,
                "categoria": {
                    "id_categoria": 4,
                    "nombre": "Combos Especiales",
                    "descripcion": "Combos especiales de fresas y otros productos seleccionados"
                }
            }
        ]
        self.productos_filtrados = self.productos.copy()
        self.actualizar_tabla()

    def filtrar_productos(self, event=None):
        """Filtrar productos según los criterios de búsqueda"""
        try:
            texto_busqueda = self.busqueda_entry.get().lower()
            tipo_busqueda = self.tipo_busqueda.get()
            estado_filtro = self.estado_filter.get()
            
            self.productos_filtrados = []
            
            for producto in self.productos:
                # Filtro por texto
                coincide_texto = True
                if texto_busqueda:
                    if tipo_busqueda == "Nombre":
                        coincide_texto = texto_busqueda in producto.get('nombre', '').lower()
                    elif tipo_busqueda == "Descripción":
                        coincide_texto = texto_busqueda in producto.get('descripcion', '').lower()
                
                # Filtro por estado
                coincide_estado = True
                if estado_filtro != "Todos":
                    estado_producto = producto.get('estado', '').lower()
                    if estado_filtro == "Activos":
                        coincide_estado = estado_producto == "activo"
                    elif estado_filtro == "Inactivos":
                        coincide_estado = estado_producto == "inactivo"
                
                if coincide_texto and coincide_estado:
                    self.productos_filtrados.append(producto)
            
            self.actualizar_tabla()
            
        except Exception as e:
            print(f"Error en filtrar_productos: {str(e)}")
            messagebox.showerror("Error", f"Error al filtrar productos: {str(e)}")

    def actualizar_tabla(self):
        """Actualizar tabla de productos"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Mostrar productos filtrados
            for producto in self.productos_filtrados:
                # Verificar que producto sea un diccionario
                if not isinstance(producto, dict):
                    continue
                    
                # Obtener datos según la estructura de la API
                id_producto = producto.get("id_producto", "")
                nombre = producto.get("nombre", "")
                descripcion = producto.get("descripcion", "")
                precio = producto.get("precio", "0")
                estado = producto.get("estado", "").title()
                peso = producto.get("peso", "N/A")
                
                # Obtener categoría (puede ser objeto o string)
                categoria_info = producto.get("categoria", {})
                if isinstance(categoria_info, dict):
                    categoria_nombre = categoria_info.get("nombre", "Sin categoría")
                else:
                    categoria_nombre = str(categoria_info) if categoria_info else "Sin categoría"
                
                # Formatear precio en soles peruanos
                try:
                    precio_formateado = f"S/ {float(precio):.2f}"
                except:
                    precio_formateado = f"S/ {precio}"
                
                # Insertar en tabla
                self.tabla.insert("", "end", values=(
                    id_producto,
                    nombre,
                    descripcion,
                    categoria_nombre,
                    precio_formateado,
                    estado,
                    peso
                ))
                
        except Exception as e:
            print(f"Error en actualizar_tabla: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al actualizar tabla de productos: {str(e)}")

    def abrir_modal_nuevo_producto(self):
        """Abrir modal para crear nuevo producto"""
        try:
            modal = ModalProducto(
                self, 
                "Nuevo Producto",
                callback_guardar=self.guardar_producto_modal
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir modal de nuevo producto: {str(e)}")

    def abrir_modal_editar_producto(self, event=None):
        """Abrir modal para editar/eliminar producto al hacer doble clic"""
        try:
            if not self.producto_seleccionado:
                messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
                return
                
            modal = ModalProducto(
                self,
                "Editar Producto",
                producto=self.producto_seleccionado,
                callback_guardar=self.actualizar_producto_modal,
                callback_eliminar=self.eliminar_producto_modal
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir modal de editar producto: {str(e)}")

    def guardar_producto_modal(self, datos_producto):
        """Callback para guardar producto desde modal"""
        try:
            url = INVENTORY_MANAGEMENT_ENDPOINTS['products']['create']
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            # Preparar datos para envío
            data = {
                'nombre': datos_producto['nombre'],
                'descripcion': datos_producto['descripcion'],
                'precio': datos_producto['precio'],
                'peso': datos_producto['peso'],
                'categorias_id_categoria': datos_producto['categoria_id'],
                'estado': '1'  # Por defecto activo
            }
            
            # Si hay stock, agregarlo
            if datos_producto.get('stock'):
                data['stock'] = datos_producto['stock']
            
            files = {}
            # Si hay imagen, prepararla para upload
            if datos_producto.get('imagen_path'):
                try:
                    with open(datos_producto['imagen_path'], 'rb') as f:
                        files['imagen'] = ('image.jpg', f, 'image/jpeg')
                        
                        # Usar requests directamente para multipart/form-data
                        response = requests.post(
                            url,
                            data=data,
                            files=files,
                            headers={'Authorization': f'Bearer {token}'} if token else {}
                        )
                        
                        if response.status_code == 201:
                            messagebox.showinfo("Éxito", "Producto creado exitosamente")
                            self.cargar_productos()
                            return True
                        else:
                            error_msg = response.json().get('message', 'Error al crear producto')
                            messagebox.showerror("Error", error_msg)
                            return False
                            
                except Exception as e:
                    messagebox.showerror("Error", f"Error al cargar imagen: {str(e)}")
                    return False
            else:
                # Sin imagen, usar APIHandler normal
                response = APIHandler.make_request('POST', url, headers=headers, data=data)
                if response['status_code'] == 201:
                    messagebox.showinfo("Éxito", "Producto creado exitosamente")
                    self.cargar_productos()
                    return True
                else:
                    error_msg = response.get('data', {}).get('message', 'Error al crear producto')
                    messagebox.showerror("Error", error_msg)
                    return False
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar producto: {str(e)}")
            return False

    def actualizar_producto_modal(self, producto_id, datos_producto):
        """Callback para actualizar producto desde modal"""
        try:
            # TODO: Implementar actualización de producto
            messagebox.showinfo("Info", f"Actualizar producto ID: {producto_id}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
            return False

    def eliminar_producto_modal(self, producto_id, nombre_producto):
        """Callback para eliminar producto desde modal"""
        try:
            # TODO: Implementar eliminación de producto
            messagebox.showinfo("Info", f"Eliminar producto: {nombre_producto}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
            return False

    def cargar_categorias_para_modal(self):
        """Cargar categorías disponibles para el modal"""
        try:
            url = INVENTORY_MANAGEMENT_ENDPOINTS['categories']['list']
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('GET', url, headers=headers)
            if response['status_code'] == 200:
                api_data = response['data']
                if isinstance(api_data, dict) and 'data' in api_data:
                    return api_data['data']
                else:
                    return api_data if isinstance(api_data, list) else []
            else:
                # Datos de ejemplo si falla la API
                return [
                    {"id_categoria": 1, "nombre": "Paquetes de Fresas"},
                    {"id_categoria": 2, "nombre": "Mermeladas"},
                    {"id_categoria": 3, "nombre": "Fresas Deshidratadas"},
                    {"id_categoria": 4, "nombre": "Combos Especiales"}
                ]
        except Exception as e:
            print(f"Error al cargar categorías: {str(e)}")
            return []

    def on_select(self, event):
        """Manejar selección de producto en la tabla"""
        try:
            seleccion = self.tabla.selection()
            if seleccion:
                item = self.tabla.item(seleccion[0])
                id_producto = item['values'][0]
                
                # Buscar el producto completo
                for producto in self.productos_filtrados:
                    if producto.get('id_producto') == id_producto:
                        self.producto_seleccionado = producto
                        break
            else:
                self.producto_seleccionado = None
                
        except Exception as e:
            print(f"Error en on_select: {str(e)}")

    def on_double_click(self, event):
        """Manejar doble clic en la tabla"""
        try:
            if self.producto_seleccionado:
                # Abrir modal de detalles del producto
                ModalDetalleProducto(self, self.producto_seleccionado)
        except Exception as e:
            print(f"Error en on_double_click: {str(e)}")

    # Métodos de compatibilidad con el sistema anterior
    def actualizar_tabla_productos(self, filtro=""):
        """Método legacy - redirige al nuevo método"""
        self.actualizar_tabla()

    def nuevo_producto(self):
        """Método legacy - redirige al modal"""
        self.abrir_modal_nuevo_producto()
        
    def refrescar_datos(self):
        """Método público para refrescar los datos desde el exterior"""
        self.cargar_productos()
        
    def obtener_producto_seleccionado(self):
        """Obtener el producto seleccionado en la tabla"""
        return self.producto_seleccionado


class ModalProducto(ctk.CTkToplevel):
    """Modal para crear/editar productos"""
    
    def __init__(self, parent, titulo, producto=None, callback_guardar=None, callback_eliminar=None):
        super().__init__(parent)
        
        self.producto = producto
        self.callback_guardar = callback_guardar
        self.callback_eliminar = callback_eliminar
        self.es_edicion = producto is not None
        self.imagen_path = None
        self.imagen_preview = None
        
        # Configurar ventana
        self.title(titulo)
        self.geometry("700x800")
        self.resizable(False, False)
        
        # Centrar ventana relativa al parent
        self.transient(parent)
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        
        # Cargar categorías
        self.categorias = parent.cargar_categorias_para_modal()
        
        self.setup_ui()
        
        # Si es edición, llenar campos
        if self.es_edicion:
            self.llenar_campos()
            
        # Hacer el grab de manera segura después de que la ventana esté lista
        self.after(10, self.configurar_modal)
    
    def setup_ui(self):
        # Título del modal
        titulo_label = ctk.CTkLabel(
            self,
            text="Nuevo Producto" if not self.es_edicion else "Editar Producto",
            font=("Quicksand", 20, "bold"),
            text_color="#2E6B5C"
        )
        titulo_label.grid(row=0, column=0, pady=20, sticky="ew")
        
        # Scrollable frame para el contenido
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#F8F9FA", corner_radius=10)
        self.scroll_frame.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # ID (solo en edición)
        if self.es_edicion:
            ctk.CTkLabel(
                self.scroll_frame,
                text="ID del Producto:",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
            
            self.id_entry = ctk.CTkEntry(
                self.scroll_frame,
                font=("Quicksand", 12),
                state="disabled"
            )
            self.id_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Nombre
        ctk.CTkLabel(
            self.scroll_frame,
            text="Nombre del Producto: *",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.nombre_entry = ctk.CTkEntry(
            self.scroll_frame,
            font=("Quicksand", 12),
            placeholder_text="Ingrese el nombre del producto"
        )
        self.nombre_entry.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Descripción
        ctk.CTkLabel(
            self.scroll_frame,
            text="Descripción: *",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.descripcion_text = ctk.CTkTextbox(
            self.scroll_frame,
            height=100,
            font=("Quicksand", 12)
        )
        self.descripcion_text.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Frame para precio y peso (en la misma fila)
        precio_peso_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        precio_peso_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 15))
        precio_peso_frame.grid_columnconfigure(0, weight=1)
        precio_peso_frame.grid_columnconfigure(1, weight=1)
        
        # Precio
        ctk.CTkLabel(
            precio_peso_frame,
            text="Precio (S/): *",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        
        self.precio_entry = ctk.CTkEntry(
            precio_peso_frame,
            font=("Quicksand", 12),
            placeholder_text="0.00"
        )
        self.precio_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        # Peso
        ctk.CTkLabel(
            precio_peso_frame,
            text="Peso: *",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        
        self.peso_entry = ctk.CTkEntry(
            precio_peso_frame,
            font=("Quicksand", 12),
            placeholder_text="ej: 500g, 1kg"
        )
        self.peso_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        
        # Frame para categoría y stock
        cat_stock_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        cat_stock_frame.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 15))
        cat_stock_frame.grid_columnconfigure(0, weight=1)
        cat_stock_frame.grid_columnconfigure(1, weight=1)
        
        # Categoría
        ctk.CTkLabel(
            cat_stock_frame,
            text="Categoría: *",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        
        # Preparar valores para el dropdown de categorías
        categoria_valores = ["Seleccionar categoría..."]
        categoria_valores.extend([cat.get('nombre', '') for cat in self.categorias])
        
        self.categoria_dropdown = ctk.CTkOptionMenu(
            cat_stock_frame,
            values=categoria_valores,
            font=("Quicksand", 12),
            fg_color="#4A934A",
            button_color="#367832"
        )
        self.categoria_dropdown.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        # Stock inicial (opcional)
        ctk.CTkLabel(
            cat_stock_frame,
            text="Stock Inicial:",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        
        self.stock_entry = ctk.CTkEntry(
            cat_stock_frame,
            font=("Quicksand", 12),
            placeholder_text="0"
        )
        self.stock_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        
        # Sección de imagen
        ctk.CTkLabel(
            self.scroll_frame,
            text="Imagen del Producto:",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=8, column=0, sticky="w", padx=20, pady=(0, 5))
        
        # Frame para imagen
        imagen_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=10)
        imagen_frame.grid(row=9, column=0, sticky="ew", padx=20, pady=(0, 15))
        imagen_frame.grid_columnconfigure(0, weight=1)
        
        # Botón para seleccionar imagen
        self.btn_seleccionar_imagen = ctk.CTkButton(
            imagen_frame,
            text="📷 Seleccionar Imagen",
            command=self.seleccionar_imagen,
            font=("Quicksand", 12, "bold"),
            fg_color="#4A934A",
            hover_color="#367832",
            width=200,
            height=35
        )
        self.btn_seleccionar_imagen.grid(row=0, column=0, padx=20, pady=15)
        
        # Label para preview de imagen
        self.imagen_label = ctk.CTkLabel(
            imagen_frame,
            text="No se ha seleccionado imagen",
            font=("Quicksand", 10),
            text_color="#666666"
        )
        self.imagen_label.grid(row=1, column=0, padx=20, pady=(0, 15))
        
        # Frame de botones
        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.grid(row=2, column=0, pady=20, sticky="ew")
        
        if self.es_edicion:
            # Botones para edición
            ctk.CTkButton(
                botones_frame,
                text="💾 Actualizar",
                command=self.actualizar_producto,
                font=("Quicksand", 12, "bold"),
                fg_color="#2E6B5C",
                hover_color="#24544A",
                width=120,
                height=35
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                botones_frame,
                text="🗑️ Eliminar",
                command=self.eliminar_producto,
                font=("Quicksand", 12, "bold"),
                fg_color="#DC3545",
                hover_color="#B02A37",
                width=120,
                height=35
            ).pack(side="left", padx=10)
        else:
            # Botón para crear
            ctk.CTkButton(
                botones_frame,
                text="💾 Crear Producto",
                command=self.guardar_producto,
                font=("Quicksand", 12, "bold"),
                fg_color="#2E6B5C",
                hover_color="#24544A",
                width=150,
                height=35
            ).pack(side="left", padx=10)
        
        # Botón cancelar
        ctk.CTkButton(
            botones_frame,
            text="❌ Cancelar",
            command=self.cerrar_modal,
            font=("Quicksand", 12, "bold"),
            fg_color="#6C757D",
            hover_color="#5A6268",
            width=120,
            height=35
        ).pack(side="right", padx=10)
    
    def seleccionar_imagen(self):
        """Seleccionar archivo de imagen"""
        try:
            tipos_archivo = [
                ("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Todos los archivos", "*.*")
            ]
            
            archivo = filedialog.askopenfilename(
                title="Seleccionar imagen del producto",
                filetypes=tipos_archivo
            )
            
            if archivo:
                self.imagen_path = archivo
                nombre_archivo = os.path.basename(archivo)
                self.imagen_label.configure(text=f"Imagen seleccionada: {nombre_archivo}")
                self.btn_seleccionar_imagen.configure(text="📷 Cambiar Imagen")
                
                # Mostrar preview si es posible
                self.mostrar_preview_imagen(archivo)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar imagen: {str(e)}")
    
    def mostrar_preview_imagen(self, ruta_imagen):
        """Mostrar preview de la imagen seleccionada"""
        try:
            # Cargar y redimensionar imagen para preview
            imagen = Image.open(ruta_imagen)
            imagen.thumbnail((150, 150), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            self.imagen_preview = ImageTk.PhotoImage(imagen)
            
            # Actualizar label con la imagen
            self.imagen_label.configure(image=self.imagen_preview, text="")
            
        except Exception as e:
            print(f"Error al mostrar preview: {str(e)}")
    
    def llenar_campos(self):
        """Llenar campos con datos de producto existente"""
        if not self.producto:
            return
            
        # ID
        if hasattr(self, 'id_entry'):
            self.id_entry.configure(state="normal")
            self.id_entry.delete(0, "end")
            self.id_entry.insert(0, str(self.producto.get('id_producto', '')))
            self.id_entry.configure(state="disabled")
        
        # Nombre
        self.nombre_entry.delete(0, "end")
        self.nombre_entry.insert(0, self.producto.get('nombre', ''))
        
        # Descripción
        self.descripcion_text.delete("1.0", "end")
        self.descripcion_text.insert("1.0", self.producto.get('descripcion', ''))
        
        # Precio
        self.precio_entry.delete(0, "end")
        self.precio_entry.insert(0, str(self.producto.get('precio', '')))
        
        # Peso
        self.peso_entry.delete(0, "end")
        self.peso_entry.insert(0, self.producto.get('peso', ''))
        
        # Categoría
        categoria_producto = self.producto.get('categoria', {})
        if isinstance(categoria_producto, dict):
            nombre_categoria = categoria_producto.get('nombre', '')
            if nombre_categoria:
                self.categoria_dropdown.set(nombre_categoria)
    
    def validar_campos(self):
        """Validar que todos los campos requeridos estén llenos"""
        errores = []
        
        # Nombre
        if not self.nombre_entry.get().strip():
            errores.append("El nombre es requerido")
        elif len(self.nombre_entry.get().strip()) < 3:
            errores.append("El nombre debe tener al menos 3 caracteres")
        
        # Descripción
        descripcion = self.descripcion_text.get("1.0", "end-1c").strip()
        if not descripcion:
            errores.append("La descripción es requerida")
        elif len(descripcion) < 10:
            errores.append("La descripción debe tener al menos 10 caracteres")
        
        # Precio
        try:
            precio = float(self.precio_entry.get().strip())
            if precio < 0:
                errores.append("El precio debe ser mayor o igual a 0")
        except ValueError:
            errores.append("El precio debe ser un número válido")
        
        # Peso
        if not self.peso_entry.get().strip():
            errores.append("El peso es requerido")
        
        # Categoría
        categoria_seleccionada = self.categoria_dropdown.get()
        if categoria_seleccionada == "Seleccionar categoría...":
            errores.append("Debe seleccionar una categoría")
        
        return errores
    
    def obtener_categoria_id(self):
        """Obtener el ID de la categoría seleccionada"""
        categoria_nombre = self.categoria_dropdown.get()
        for categoria in self.categorias:
            if categoria.get('nombre') == categoria_nombre:
                return categoria.get('id_categoria')
        return None
    
    def guardar_producto(self):
        """Guardar nuevo producto"""
        errores = self.validar_campos()
        if errores:
            messagebox.showerror("Error de validación", "\n".join(errores))
            return
        
        try:
            # Preparar datos
            datos_producto = {
                'nombre': self.nombre_entry.get().strip(),
                'descripcion': self.descripcion_text.get("1.0", "end-1c").strip(),
                'precio': self.precio_entry.get().strip(),
                'peso': self.peso_entry.get().strip(),
                'categoria_id': self.obtener_categoria_id(),
                'stock': self.stock_entry.get().strip() or '0'
            }
            
            # Agregar imagen si existe
            if self.imagen_path:
                datos_producto['imagen_path'] = self.imagen_path
            
            # Llamar callback
            if self.callback_guardar and self.callback_guardar(datos_producto):
                self.cerrar_modal()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar producto: {str(e)}")
    
    def actualizar_producto(self):
        """Actualizar producto existente"""
        errores = self.validar_campos()
        if errores:
            messagebox.showerror("Error de validación", "\n".join(errores))
            return
        
        try:
            # Preparar datos
            datos_producto = {
                'nombre': self.nombre_entry.get().strip(),
                'descripcion': self.descripcion_text.get("1.0", "end-1c").strip(),
                'precio': self.precio_entry.get().strip(),
                'peso': self.peso_entry.get().strip(),
                'categoria_id': self.obtener_categoria_id(),
                'stock': self.stock_entry.get().strip() or '0'
            }
            
            # Agregar imagen si existe
            if self.imagen_path:
                datos_producto['imagen_path'] = self.imagen_path
            
            # Llamar callback
            if self.callback_guardar:
                producto_id = self.producto.get('id_producto')
                if self.callback_guardar(producto_id, datos_producto):
                    self.cerrar_modal()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
    
    def eliminar_producto(self):
        """Eliminar producto"""
        if self.callback_eliminar:
            producto_id = self.producto.get('id_producto')
            nombre_producto = self.producto.get('nombre', '')
            if self.callback_eliminar(producto_id, nombre_producto):
                self.cerrar_modal()
    
    def cerrar_modal(self):
        """Cerrar el modal de forma segura"""
        try:
            self.grab_release()
        except:
            pass
        finally:
            self.destroy()
    
    def configurar_modal(self):
        """Configurar el modal de forma segura después de que esté visible"""
        try:
            self.center_window()
            if self.winfo_exists():
                self.grab_set()
        except Exception as e:
            print(f"Error al configurar modal: {str(e)}")
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        try:
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"Error al centrar ventana: {str(e)}")


class ModalDetalleProducto(ctk.CTkToplevel):
    """Modal para mostrar detalles completos de un producto"""
    
    def __init__(self, parent, producto):
        super().__init__(parent)
        
        self.producto = producto
        
        # Configurar ventana
        self.title(f"Detalles - {producto.get('nombre', 'Producto')}")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # Centrar ventana relativa al parent
        self.transient(parent)
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.cargar_imagen()
        
        # Configurar modal
        self.after(10, self.configurar_modal)
    
    def setup_ui(self):
        # Header del modal
        header_frame = ctk.CTkFrame(self, fg_color="#2E6B5C", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        titulo_label = ctk.CTkLabel(
            header_frame,
            text=f"Detalles del Producto",
            font=("Quicksand", 18, "bold"),
            text_color="white"
        )
        titulo_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Botones de acción
        botones_header_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        botones_header_frame.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Botón editar
        ctk.CTkButton(
            botones_header_frame,
            text="✏️ Editar",
            command=self.editar_producto,
            font=("Quicksand", 12, "bold"),
            fg_color="#4A934A",
            hover_color="#367832",
            width=80,
            height=30
        ).pack(side="left", padx=5)
        
        # Botón cerrar
        ctk.CTkButton(
            botones_header_frame,
            text="✕ Cerrar",
            command=self.cerrar_modal,
            font=("Quicksand", 12, "bold"),
            fg_color="#DC3545",
            hover_color="#B02A37",
            width=80,
            height=30
        ).pack(side="left", padx=5)
        
        # Scrollable frame para el contenido
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#F8F9FA", corner_radius=10)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Imagen del producto
        self.imagen_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=10)
        self.imagen_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        
        self.imagen_label = ctk.CTkLabel(
            self.imagen_frame,
            text="Cargando imagen...",
            font=("Quicksand", 12),
            text_color="#666666"
        )
        self.imagen_label.pack(pady=20)
        
        # Información básica
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=10)
        info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        info_frame.grid_columnconfigure(1, weight=1)
        
        # ID
        self.crear_campo_info(info_frame, 0, "ID:", str(self.producto.get('id_producto', 'N/A')))
        
        # Nombre
        self.crear_campo_info(info_frame, 1, "Nombre:", self.producto.get('nombre', 'N/A'))
        
        # Descripción
        self.crear_campo_info(info_frame, 2, "Descripción:", self.producto.get('descripcion', 'N/A'))
        
        # Precio
        precio = self.producto.get('precio', '0')
        try:
            precio_formateado = f"S/ {float(precio):.2f}"
        except:
            precio_formateado = f"S/ {precio}"
        self.crear_campo_info(info_frame, 3, "Precio:", precio_formateado)
        
        # Peso
        self.crear_campo_info(info_frame, 4, "Peso:", self.producto.get('peso', 'N/A'))
        
        # Estado
        estado = self.producto.get('estado', 'N/A').title()
        self.crear_campo_info(info_frame, 5, "Estado:", estado)
        
        # Categoría
        categoria_info = self.producto.get('categoria', {})
        if isinstance(categoria_info, dict):
            categoria_nombre = categoria_info.get('nombre', 'N/A')
        else:
            categoria_nombre = str(categoria_info) if categoria_info else 'N/A'
        self.crear_campo_info(info_frame, 6, "Categoría:", categoria_nombre)
        
        # Fechas
        fecha_creacion = self.producto.get('fecha_creacion', '')
        if fecha_creacion:
            try:
                from datetime import datetime
                fecha_obj = datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00'))
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_formateada = fecha_creacion
        else:
            fecha_formateada = 'N/A'
        self.crear_campo_info(info_frame, 7, "Fecha de Creación:", fecha_formateada)
    
    def crear_campo_info(self, parent, row, label, valor):
        """Crear un campo de información en el modal"""
        # Label
        ctk.CTkLabel(
            parent,
            text=label,
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C",
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=20, pady=10)
        
        # Valor
        ctk.CTkLabel(
            parent,
            text=str(valor),
            font=("Quicksand", 12),
            text_color="#333333",
            anchor="w",
            wraplength=300
        ).grid(row=row, column=1, sticky="ew", padx=(10, 20), pady=10)
    
    def cargar_imagen(self):
        """Cargar imagen del producto"""
        try:
            url_imagen = self.producto.get('url_imagen_completa') or self.producto.get('url_imagen')
            
            if url_imagen and url_imagen != 'productos/default.jpg':
                # Intentar cargar imagen desde URL
                import requests
                from io import BytesIO
                
                try:
                    response = requests.get(url_imagen, timeout=10)
                    if response.status_code == 200:
                        imagen_data = BytesIO(response.content)
                        imagen = Image.open(imagen_data)
                        
                        # Redimensionar imagen manteniendo proporción
                        imagen.thumbnail((250, 250), Image.Resampling.LANCZOS)
                        
                        # Convertir a PhotoImage
                        self.imagen_preview = ImageTk.PhotoImage(imagen)
                        
                        # Actualizar label con la imagen
                        self.imagen_label.configure(
                            image=self.imagen_preview,
                            text=""
                        )
                    else:
                        self.imagen_label.configure(text="No se pudo cargar la imagen")
                        
                except Exception as e:
                    print(f"Error al cargar imagen desde URL: {str(e)}")
                    self.imagen_label.configure(text="Error al cargar imagen")
            else:
                self.imagen_label.configure(text="Sin imagen disponible")
                
        except Exception as e:
            print(f"Error en cargar_imagen: {str(e)}")
            self.imagen_label.configure(text="Error al cargar imagen")
    
    def editar_producto(self):
        """Abrir modal de edición"""
        try:
            # Cerrar este modal primero
            self.cerrar_modal()
            
            # Abrir modal de edición
            # Necesitamos acceso al parent original
            if hasattr(self.master, 'abrir_modal_editar_producto'):
                self.master.producto_seleccionado = self.producto
                self.master.abrir_modal_editar_producto()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir editor: {str(e)}")
    
    def cerrar_modal(self):
        """Cerrar el modal de forma segura"""
        try:
            self.grab_release()
        except:
            pass
        finally:
            self.destroy()
    
    def configurar_modal(self):
        """Configurar el modal de forma segura después de que esté visible"""
        try:
            self.center_window()
            if self.winfo_exists():
                self.grab_set()
        except Exception as e:
            print(f"Error al configurar modal: {str(e)}")
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        try:
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"Error al centrar ventana: {str(e)}")

# Función para testing independiente
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("800x600")
    app.title("Test - Sección de Productos")
    
    # Configurar grid
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    
    # Crear sección de productos
    products_section = ProductsSection(app)
    products_section.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    app.mainloop()
