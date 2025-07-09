import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
from src.core.config import INVENTORY_MANAGEMENT_ENDPOINTS
from src.shared.utils import APIHandler, SessionManager
from src.interfaces.management.product_creation import abrir_ventana_crear_producto


class ProductsSection(ctk.CTkFrame):
    """Sección dedicada a la gestión de productos dentro del módulo de inventario"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variables de datos
        self.productos = []
        
        # Configurar layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar datos iniciales
        self.cargar_productos()
        
    def crear_interfaz(self):
        """Crear la interfaz completa de la sección de productos"""
        try:
            # Frame de búsqueda y filtros
            self.crear_frame_busqueda()
            
            # Crear tabla de productos
            self.crear_tabla_productos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear interfaz de productos: {str(e)}")
            
    def crear_frame_busqueda(self):
        """Crear el frame de búsqueda y acciones"""
        search_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
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
        
    def crear_tabla_productos(self):
        """Crear tabla para mostrar productos"""
        try:
            # Frame para la tabla
            table_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
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
            },
            {
                "id_producto": 2,
                "nombre": "Fresas Premium - 500g",
                "descripcion": "Fresas premium seleccionadas",
                "precio": "8.50",
                "estado": "activo",
                "categoria": {
                    "nombre": "Paquetes de Fresas"
                }
            },
            {
                "id_producto": 3,
                "nombre": "Mix Tropical - 2kg",
                "descripcion": "Mezcla de frutas tropicales",
                "precio": "25.00",
                "estado": "activo",
                "categoria": {
                    "nombre": "Frutas Mixtas"
                }
            }
        ]
        self.actualizar_tabla_productos()
        
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
            
    def filtrar_productos(self, *args):
        """Filtrar productos por búsqueda"""
        try:
            if hasattr(self, 'productos_search_var'):
                filtro = self.productos_search_var.get()
                self.actualizar_tabla_productos(filtro)
        except Exception as e:
            print(f"Error en filtrar_productos: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al filtrar productos: {str(e)}")
            
    def nuevo_producto(self):
        """Abrir ventana para crear nuevo producto"""
        try:
            ventana = abrir_ventana_crear_producto()
            if ventana:
                # Recargar productos después de crear
                self.cargar_productos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nuevo producto: {str(e)}")
            
    def refrescar_datos(self):
        """Método público para refrescar los datos desde el exterior"""
        self.cargar_productos()
        
    def obtener_producto_seleccionado(self):
        """Obtener el producto seleccionado en la tabla"""
        try:
            seleccion = self.tabla_productos.selection()
            if not seleccion:
                return None
                
            item = self.tabla_productos.item(seleccion[0])
            valores = item['values']
            
            # Buscar el producto completo por ID
            id_producto = valores[0]
            for producto in self.productos:
                if producto.get("id_producto") == id_producto:
                    return producto
                    
            return None
        except Exception as e:
            print(f"Error al obtener producto seleccionado: {str(e)}")
            return None


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
