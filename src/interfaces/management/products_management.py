import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
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
                
                # Formatear precio
                try:
                    precio_formateado = f"${float(precio):.2f}"
                except:
                    precio_formateado = f"${precio}"
                
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
            # TODO: Implementar modal de nuevo producto
            messagebox.showinfo("Info", "Funcionalidad de nuevo producto en desarrollo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir modal de nuevo producto: {str(e)}")

    def abrir_modal_editar_producto(self, event=None):
        """Abrir modal para editar/eliminar producto al hacer doble clic"""
        try:
            if not self.producto_seleccionado:
                messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
                return
                
            # TODO: Implementar modal de editar producto
            messagebox.showinfo("Info", f"Editar producto: {self.producto_seleccionado.get('nombre', '')}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir modal de editar producto: {str(e)}")

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
            self.abrir_modal_editar_producto()
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
