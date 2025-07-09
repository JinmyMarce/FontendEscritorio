import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
from src.core.config import INVENTORY_MANAGEMENT_ENDPOINTS, UI_CONFIG
from src.shared.utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper
from src.interfaces.management.product_creation import abrir_ventana_crear_producto
from PIL import Image, ImageTk
from src.shared.image_handler import ImageHandler

class GestionInventario(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            
            # Configurar layout responsivo con grid
            self.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            
            # Configurar grid del parent para que se expanda
            if hasattr(parent, 'grid_rowconfigure'):
                parent.grid_rowconfigure(0, weight=1)
                parent.grid_columnconfigure(0, weight=1)
            
            # Configurar grid interno
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(2, weight=1)  # El contenido principal se expande
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Variables de datos
            self.productos = []
            self.categorias = []
            self.inventario = []
            
            # Variable para rastrear la sección actual
            self.seccion_actual = "productos"  # productos, categorias, stock
            
            self.crear_interfaz_principal()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar gestión de inventario: {str(e)}")
            
    def crear_interfaz_principal(self):
        """Crear la interfaz principal con navegación por pestañas"""
        try:
            # Frame superior con título
            top_frame = ctk.CTkFrame(self, fg_color="transparent")
            top_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            title_frame.pack(side="left")
            
            # Cargar y mostrar icono de inventario
            icon = self.image_handler.load_image("inventory.png", (32, 32))
            if icon:
                ctk.CTkLabel(
                    title_frame,
                    image=icon,
                    text=""
                ).pack(side="left", padx=(0, 10))
                
            ctk.CTkLabel(
                title_frame,
                text="Gestión de Inventario",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left")
            
            # Frame de navegación con pestañas
            nav_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            nav_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 20))
            
            # Botones de navegación
            buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=20, pady=15)
            
            # Botón Productos
            self.btn_productos = ctk.CTkButton(
                buttons_frame,
                text="📦 Productos",
                command=lambda: self.cambiar_seccion("productos"),
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150,
                height=35,
                font=("Quicksand", 14, "bold")
            )
            self.btn_productos.pack(side="left", padx=5)
            
            # Botón Categorías
            self.btn_categorias = ctk.CTkButton(
                buttons_frame,
                text="🏷️ Categorías",
                command=lambda: self.cambiar_seccion("categorias"),
                fg_color="#4A934A",
                hover_color="#367832",
                width=150,
                height=35,
                font=("Quicksand", 14, "bold")
            )
            self.btn_categorias.pack(side="left", padx=5)
            
            # Botón Stock
            self.btn_stock = ctk.CTkButton(
                buttons_frame,
                text="📊 Control de Stock",
                command=lambda: self.cambiar_seccion("stock"),
                fg_color="#367832",
                hover_color="#2D5A27",
                width=150,
                height=35,
                font=("Quicksand", 14, "bold")
            )
            self.btn_stock.pack(side="left", padx=5)
            
            # Frame de contenido principal (aquí se cargarán las diferentes secciones)
            self.content_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
            self.content_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
            self.content_frame.grid_columnconfigure(0, weight=1)
            self.content_frame.grid_rowconfigure(0, weight=1)
            
            # Cargar la sección por defecto
            self.cambiar_seccion("productos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear interfaz principal: {str(e)}")
            
    def cambiar_seccion(self, seccion):
        """Cambiar entre las diferentes secciones del inventario"""
        try:
            # Actualizar variable de sección actual
            self.seccion_actual = seccion
            
            # Actualizar colores de botones para mostrar el activo
            self.actualizar_botones_navegacion()
            
            # Limpiar frame de contenido
            for widget in self.content_frame.winfo_children():
                widget.destroy()
                
            # Cargar la sección correspondiente
            if seccion == "productos":
                self.crear_seccion_productos()
            elif seccion == "categorias":
                self.crear_seccion_categorias()
            elif seccion == "stock":
                self.crear_seccion_stock()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar sección: {str(e)}")
            
    def actualizar_botones_navegacion(self):
        """Actualizar colores de botones según la sección activa"""
        # Reset todos los botones a color inactivo
        self.btn_productos.configure(fg_color="#6B6B6B", hover_color="#5A5A5A")
        self.btn_categorias.configure(fg_color="#6B6B6B", hover_color="#5A5A5A")
        self.btn_stock.configure(fg_color="#6B6B6B", hover_color="#5A5A5A")
        
        # Destacar botón activo
        if self.seccion_actual == "productos":
            self.btn_productos.configure(fg_color="#2E6B5C", hover_color="#1D4A3C")
        elif self.seccion_actual == "categorias":
            self.btn_categorias.configure(fg_color="#4A934A", hover_color="#367832")
        elif self.seccion_actual == "stock":
            self.btn_stock.configure(fg_color="#367832", hover_color="#2D5A27")
            
    def crear_seccion_productos(self):
        """Crear la sección de gestión de productos"""
        try:
            # Frame principal de productos
            productos_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            productos_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            productos_frame.grid_columnconfigure(0, weight=1)
            productos_frame.grid_rowconfigure(2, weight=1)
            
            # Frame de búsqueda y filtros
            search_frame = ctk.CTkFrame(productos_frame, fg_color="#FFFFFF", corner_radius=10)
            search_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
            search_frame.grid_columnconfigure(1, weight=1)
            
            # Búsqueda
            search_label = ctk.CTkLabel(
                search_frame,
                text="🔍",
                font=("Quicksand", 16)
            )
            search_label.grid(row=0, column=0, padx=(15, 5), pady=10)
            
            self.productos_search_var = ctk.StringVar()
            self.productos_search_var.trace("w", self.filtrar_productos)
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=self.productos_search_var,
                placeholder_text="Buscar productos por nombre o código...",
                border_width=0,
                fg_color="#F5F5F5"
            )
            search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
            
            # Botones de acción
            action_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
            action_frame.grid(row=0, column=2, padx=15, pady=10)
            
            ctk.CTkButton(
                action_frame,
                text="➕ Nuevo Producto",
                command=self.nuevo_producto,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=140
            ).pack(side="left", padx=2)
            
            # Placeholder para tabla de productos
            self.crear_tabla_productos(productos_frame)
            self.cargar_productos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear sección de productos: {str(e)}")
            
    def crear_seccion_categorias(self):
        """Crear la sección de gestión de categorías"""
        try:
            # Frame principal de categorías
            categorias_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            categorias_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            categorias_frame.grid_columnconfigure(0, weight=1)
            categorias_frame.grid_rowconfigure(1, weight=1)
            
            # Información y botones
            info_frame = ctk.CTkFrame(categorias_frame, fg_color="#FFFFFF", corner_radius=10)
            info_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
            
            ctk.CTkLabel(
                info_frame,
                text="🏷️ Gestión de Categorías de Productos",
                font=("Quicksand", 18, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=20)
            
            # Botones de categorías
            cat_buttons_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            cat_buttons_frame.pack(pady=(0, 20))
            
            ctk.CTkButton(
                cat_buttons_frame,
                text="➕ Nueva Categoría",
                command=self.nueva_categoria,
                fg_color="#4A934A",
                hover_color="#367832",
                width=150
            ).pack(side="left", padx=10)
            
            # Placeholder para tabla de categorías
            self.crear_tabla_categorias(categorias_frame)
            self.cargar_categorias()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear sección de categorías: {str(e)}")
            
    def crear_seccion_stock(self):
        """Crear la sección de control de stock"""
        try:
            # Frame principal de stock
            stock_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            stock_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            stock_frame.grid_columnconfigure(0, weight=1)
            stock_frame.grid_rowconfigure(1, weight=1)
            
            # Frame de información de stock
            info_frame = ctk.CTkFrame(stock_frame, fg_color="#FFFFFF", corner_radius=10)
            info_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
            
            ctk.CTkLabel(
                info_frame,
                text="📊 Control de Stock e Inventario",
                font=("Quicksand", 18, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=20)
            
            # Botones de acciones de stock
            stock_buttons_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            stock_buttons_frame.pack(pady=(0, 20))
            
            ctk.CTkButton(
                stock_buttons_frame,
                text="📈 Actualizar Stock",
                command=self.gestionar_stock_general,
                fg_color="#4CAF50",
                hover_color="#45a049",
                width=150
            ).pack(side="left", padx=5)
            
            # Tabla de inventario
            self.crear_tabla_stock(stock_frame)
            self.cargar_inventario()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear sección de stock: {str(e)}")
            
    def crear_tabla_productos(self, parent):
        """Crear tabla para mostrar productos"""
        try:
            # Frame para la tabla
            table_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=10)
            table_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
            
            # Configurar estilo de la tabla
            style = ttk.Style()
            style.configure(
                "Productos.Treeview",
                background="#FFFFFF",
                foreground="#2E6B5C",
                rowheight=30,
                fieldbackground="#FFFFFF",
                borderwidth=0
            )
            style.configure(
                "Productos.Treeview.Heading",
                background="#2E6B5C",
                foreground="white",
                font=("Quicksand", 12, "bold")
            )
            
            # Crear Treeview
            columns = ("id", "nombre", "categoria", "precio", "stock")
            self.tabla_productos = ttk.Treeview(
                table_frame, 
                columns=columns, 
                show="headings",
                style="Productos.Treeview"
            )
            
            # Configurar columnas
            self.tabla_productos.heading("id", text="ID")
            self.tabla_productos.heading("nombre", text="Nombre")
            self.tabla_productos.heading("categoria", text="Categoría")
            self.tabla_productos.heading("precio", text="Precio")
            self.tabla_productos.heading("stock", text="Stock")
            
            # Configurar anchos
            self.tabla_productos.column("id", width=50)
            self.tabla_productos.column("nombre", width=250)
            self.tabla_productos.column("categoria", width=120)
            self.tabla_productos.column("precio", width=100)
            self.tabla_productos.column("stock", width=80)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_productos.yview)
            self.tabla_productos.configure(yscrollcommand=v_scrollbar.set)
            
            # Empaquetar
            self.tabla_productos.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            v_scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear tabla de productos: {str(e)}")
            
    def crear_tabla_categorias(self, parent):
        """Crear tabla para mostrar categorías"""
        try:
            # Frame para la tabla
            table_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=10)
            table_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            
            # Configurar estilo
            style = ttk.Style()
            style.configure(
                "Categorias.Treeview",
                background="#FFFFFF",
                foreground="#4A934A",
                rowheight=30,
                fieldbackground="#FFFFFF"
            )
            style.configure(
                "Categorias.Treeview.Heading",
                background="#4A934A",
                foreground="white",
                font=("Quicksand", 12, "bold")
            )
            
            # Crear Treeview
            columns = ("id", "nombre", "descripcion", "productos_count")
            self.tabla_categorias = ttk.Treeview(
                table_frame, 
                columns=columns, 
                show="headings",
                style="Categorias.Treeview"
            )
            
            # Configurar columnas
            self.tabla_categorias.heading("id", text="ID")
            self.tabla_categorias.heading("nombre", text="Nombre")
            self.tabla_categorias.heading("descripcion", text="Descripción")
            self.tabla_categorias.heading("productos_count", text="N° Productos")
            
            # Configurar anchos
            self.tabla_categorias.column("id", width=50)
            self.tabla_categorias.column("nombre", width=150)
            self.tabla_categorias.column("descripcion", width=300)
            self.tabla_categorias.column("productos_count", width=120)
            
            # Scrollbars
            v_scrollbar_cat = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_categorias.yview)
            self.tabla_categorias.configure(yscrollcommand=v_scrollbar_cat.set)
            
            # Empaquetar
            self.tabla_categorias.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            v_scrollbar_cat.pack(side="right", fill="y")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear tabla de categorías: {str(e)}")
            
    def crear_tabla_stock(self, parent):
        """Crear tabla para control de stock"""
        try:
            # Frame para la tabla
            table_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=10)
            table_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            
            # Configurar estilo
            style = ttk.Style()
            style.configure(
                "Stock.Treeview",
                background="#FFFFFF",
                foreground="#367832",
                rowheight=30,
                fieldbackground="#FFFFFF"
            )
            style.configure(
                "Stock.Treeview.Heading",
                background="#367832",
                foreground="white",
                font=("Quicksand", 12, "bold")
            )
            
            # Crear Treeview
            columns = ("id", "producto", "stock_actual", "estado")
            self.tabla_stock = ttk.Treeview(
                table_frame, 
                columns=columns, 
                show="headings",
                style="Stock.Treeview"
            )
            
            # Configurar columnas
            self.tabla_stock.heading("id", text="ID")
            self.tabla_stock.heading("producto", text="Producto")
            self.tabla_stock.heading("stock_actual", text="Stock Actual")
            self.tabla_stock.heading("estado", text="Estado")
            
            # Configurar anchos
            self.tabla_stock.column("id", width=50)
            self.tabla_stock.column("producto", width=200)
            self.tabla_stock.column("stock_actual", width=100)
            self.tabla_stock.column("estado", width=100)
            
            # Scrollbars
            v_scrollbar_stock = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_stock.yview)
            self.tabla_stock.configure(yscrollcommand=v_scrollbar_stock.set)
            
            # Empaquetar
            self.tabla_stock.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            v_scrollbar_stock.pack(side="right", fill="y")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear tabla de stock: {str(e)}")
            
    # =================================================================================
    # MÉTODOS DE CARGA DE DATOS
    # =================================================================================
    
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
                    
                self.actualizar_tabla_productos()
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
                "id_producto": 1,
                "nombre": "Delicia Andina - 1kg",
                "descripcion": "Fresas frescas de invernadero",
                "precio": "13.00",
                "estado": "activo",
                "categoria": {
                    "nombre": "Paquetes de Fresas"
                }
            }
        ]
        self.actualizar_tabla_productos()
            
    def cargar_categorias(self):
        """Cargar categorías desde la API"""
        try:
            url = INVENTORY_MANAGEMENT_ENDPOINTS['categories']['list']
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('GET', url, headers=headers)
            if response['status_code'] == 200:
                # Adaptar estructura de datos de la API
                api_data = response['data']
                if isinstance(api_data, dict) and 'data' in api_data:
                    self.categorias = api_data['data']  # Extraer el array de categorías
                else:
                    self.categorias = api_data if isinstance(api_data, list) else []
                    
                self.actualizar_tabla_categorias()
            else:
                messagebox.showerror("Error", f"Error al cargar categorías: {response.get('data', 'Error desconocido')}")
                self.cargar_categorias_ejemplo()
                
        except Exception as e:
            print(f"Error al cargar categorías: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al cargar categorías: {str(e)}")
            self.cargar_categorias_ejemplo()
            
    def cargar_categorias_ejemplo(self):
        """Cargar datos de ejemplo para categorías"""
        self.categorias = [
            {
                "id_categoria": 1,
                "nombre": "Paquetes de Fresas",
                "descripcion": "Frutas frescas y de temporada",
                "productos_count": 3
            }
        ]
        self.actualizar_tabla_categorias()
            
    def cargar_inventario(self):
        """Cargar inventario desde la API"""
        try:
            url = INVENTORY_MANAGEMENT_ENDPOINTS['inventory']['products_list']
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('GET', url, headers=headers)
            if response['status_code'] == 200:
                # Adaptar estructura de datos de la API
                api_data = response['data']
                if isinstance(api_data, dict) and 'data' in api_data:
                    self.inventario = api_data['data']  # Extraer el array de inventario
                else:
                    self.inventario = api_data if isinstance(api_data, list) else []
                    
                self.actualizar_tabla_stock()
            else:
                messagebox.showerror("Error", f"Error al cargar inventario: {response.get('data', 'Error desconocido')}")
                self.cargar_inventario_ejemplo()
                
        except Exception as e:
            print(f"Error al cargar inventario: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al cargar inventario: {str(e)}")
            self.cargar_inventario_ejemplo()
            
    def cargar_inventario_ejemplo(self):
        """Cargar datos de ejemplo para inventario"""
        self.inventario = [
            {
                "id_producto": 1,
                "nombre_producto": "Delicia Andina - 1kg",
                "precio": "13.00",
                "categoria": "Paquetes de Fresas",
                "inventario": {
                    "cantidad_disponible": 0,
                    "estado_inventario": "sin_inventario"
                }
            }
        ]
        self.actualizar_tabla_stock()
            
    # =================================================================================
    # MÉTODOS DE ACTUALIZACIÓN DE TABLAS
    # =================================================================================
    
    def actualizar_tabla_productos(self, filtro=""):
        """Actualizar tabla de productos"""
        try:
            if hasattr(self, 'tabla_productos'):
                # Limpiar tabla
                for item in self.tabla_productos.get_children():
                    self.tabla_productos.delete(item)
                    
                # Filtrar y mostrar productos
                for producto in self.productos:
                    # Verificar que producto sea un diccionario
                    if not isinstance(producto, dict):
                        continue
                        
                    # Obtener datos según la estructura de la API
                    id_producto = producto.get("id_producto", "")
                    nombre = producto.get("nombre", "")
                    precio = producto.get("precio", "0")
                    
                    # Obtener categoría (puede ser objeto o string)
                    categoria_info = producto.get("categoria", {})
                    if isinstance(categoria_info, dict):
                        categoria_nombre = categoria_info.get("nombre", "Sin categoría")
                    else:
                        categoria_nombre = str(categoria_info) if categoria_info else "Sin categoría"
                    
                    # Aplicar filtro de búsqueda
                    if filtro and filtro.lower() not in nombre.lower():
                        continue
                    
                    # Insertar en tabla
                    self.tabla_productos.insert("", "end", values=(
                        id_producto,
                        nombre,
                        categoria_nombre,
                        f"${float(precio):.2f}" if precio else "$0.00",
                        "N/A"  # Stock no está disponible en este endpoint
                    ))
                    
        except Exception as e:
            print(f"Error en actualizar_tabla_productos: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al actualizar tabla de productos: {str(e)}")
            
    def actualizar_tabla_categorias(self):
        """Actualizar tabla de categorías"""
        try:
            if hasattr(self, 'tabla_categorias'):
                # Limpiar tabla
                for item in self.tabla_categorias.get_children():
                    self.tabla_categorias.delete(item)
                    
                # Mostrar categorías
                for categoria in self.categorias:
                    # Verificar que categoria sea un diccionario
                    if not isinstance(categoria, dict):
                        continue
                        
                    # Obtener datos según la estructura de la API
                    id_categoria = categoria.get("id_categoria", "")
                    nombre = categoria.get("nombre", "")
                    descripcion = categoria.get("descripcion", "")
                    productos_count = categoria.get("productos_count", 0)
                    
                    # Insertar en tabla
                    self.tabla_categorias.insert("", "end", values=(
                        id_categoria,
                        nombre,
                        descripcion,
                        productos_count
                    ))
                    
        except Exception as e:
            print(f"Error en actualizar_tabla_categorias: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al actualizar tabla de categorías: {str(e)}")
            
    def actualizar_tabla_stock(self):
        """Actualizar tabla de stock"""
        try:
            if hasattr(self, 'tabla_stock'):
                # Limpiar tabla
                for item in self.tabla_stock.get_children():
                    self.tabla_stock.delete(item)
                    
                # Mostrar inventario
                for item in self.inventario:
                    # Verificar que item sea un diccionario
                    if not isinstance(item, dict):
                        continue
                        
                    # Obtener datos según la estructura de la API
                    id_producto = item.get("id_producto", "")
                    nombre_producto = item.get("nombre_producto", "")
                    
                    # Obtener información del inventario
                    inventario_info = item.get("inventario", {})
                    if isinstance(inventario_info, dict):
                        cantidad_disponible = inventario_info.get("cantidad_disponible", 0)
                        estado_inventario = inventario_info.get("estado_inventario", "sin_inventario")
                    else:
                        cantidad_disponible = 0
                        estado_inventario = "sin_inventario"
                    
                    # Determinar estado para mostrar
                    if estado_inventario == "sin_inventario":
                        estado_display = "Sin Inventario"
                    elif cantidad_disponible == 0:
                        estado_display = "Sin Stock"
                    elif cantidad_disponible <= 10:  # Umbral de stock bajo
                        estado_display = "Stock Bajo"
                    else:
                        estado_display = "Normal"
                    
                    # Insertar en tabla
                    self.tabla_stock.insert("", "end", values=(
                        id_producto,
                        nombre_producto,
                        cantidad_disponible,
                        estado_display
                    ))
                    
        except Exception as e:
            print(f"Error en actualizar_tabla_stock: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al actualizar tabla de stock: {str(e)}")
            
    # =================================================================================
    # MÉTODOS DE FILTRADO
    # =================================================================================
    
    def filtrar_productos(self, *args):
        """Filtrar productos por búsqueda"""
        try:
            if hasattr(self, 'productos_search_var'):
                filtro = self.productos_search_var.get()
                self.actualizar_tabla_productos(filtro)
        except Exception as e:
            print(f"Error en filtrar_productos: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al filtrar productos: {str(e)}")
            
    # =================================================================================
    # MÉTODOS DE ACCIONES
    # =================================================================================
    
    def nuevo_producto(self):
        """Abrir ventana para crear nuevo producto"""
        try:
            ventana = abrir_ventana_crear_producto()
            if ventana:
                # Recargar productos después de crear
                self.cargar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nuevo producto: {str(e)}")
            
    def nueva_categoria(self):
        """Crear nueva categoría"""
        try:
            # TODO: Implementar ventana de creación de categoría
            messagebox.showinfo("Info", "Funcionalidad de nueva categoría en desarrollo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nueva categoría: {str(e)}")
            
    def gestionar_stock_general(self):
        """Gestión general de stock"""
        try:
            # TODO: Implementar gestión de stock
            messagebox.showinfo("Info", "Funcionalidad de gestión de stock en desarrollo")
        except Exception as e:
            messagebox.showerror("Error", f"Error en gestión de stock: {str(e)}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1000x650")
    frame = GestionInventario(app)
    app.mainloop()
