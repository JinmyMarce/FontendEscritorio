import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as messagebox
from datetime import datetime
from src.core.config import INVENTORY_MANAGEMENT_ENDPOINTS
from src.shared.utils import APIHandler, SessionManager

class GestionCategoriasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurar layout responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # La tabla se expande
        
        # Variables de datos
        self.categorias = []
        self.categoria_seleccionada = None
        
        self.setup_ui()
        self.cargar_categorias()
        
    def setup_ui(self):
        # Título
        titulo = ctk.CTkLabel(self, text="Gestión de Categorías", 
                            font=("Quicksand", 24, "bold"),
                            text_color="#2E6B5C")
        titulo.grid(row=0, column=0, pady=20, sticky="ew")

        # Frame para el formulario
        form_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        form_frame.grid(row=1, column=0, pady=20, padx=20, sticky="ew")

        # ID Categoría (autoincremental, solo lectura)
        ctk.CTkLabel(form_frame, text="ID Categoría:", 
                    font=("Quicksand", 12)).grid(row=0, column=0, sticky="w", padx=20, pady=(15,5))
        self.id_entry = ctk.CTkEntry(form_frame, state="disabled", 
                                   font=("Quicksand", 12))
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=20, pady=(15,5))

        # Nombre
        ctk.CTkLabel(form_frame, text="Nombre:", 
                    font=("Quicksand", 12)).grid(row=1, column=0, sticky="w", padx=20, pady=5)
        self.nombre_entry = ctk.CTkEntry(form_frame, 
                                       font=("Quicksand", 12))
        self.nombre_entry.grid(row=1, column=1, sticky="ew", padx=20, pady=5)

        # Descripción
        ctk.CTkLabel(form_frame, text="Descripción:", 
                    font=("Quicksand", 12)).grid(row=2, column=0, sticky="nw", padx=20, pady=5)
        self.descripcion_text = ctk.CTkTextbox(form_frame, height=80, 
                                             font=("Quicksand", 12))
        self.descripcion_text.grid(row=2, column=1, sticky="ew", padx=20, pady=5)

        # Fecha de Creación
        ctk.CTkLabel(form_frame, text="Fecha de Creación:", 
                    font=("Quicksand", 12)).grid(row=3, column=0, sticky="w", padx=20, pady=5)
        self.fecha_entry = ctk.CTkEntry(form_frame, state="disabled",
                                      font=("Quicksand", 12))
        self.fecha_entry.grid(row=3, column=1, sticky="ew", padx=20, pady=(5,15))

        # Configurar columnas del formulario
        form_frame.grid_columnconfigure(1, weight=1)

        # Botones
        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.grid(row=2, column=0, pady=10, sticky="ew")

        # Botón Guardar
        self.guardar_btn = ctk.CTkButton(botones_frame, 
                                       text="Guardar Categoría",
                                       command=self.guardar_categoria,
                                       font=("Quicksand", 12),
                                       fg_color="#2E6B5C",
                                       hover_color="#24544A")
        self.guardar_btn.grid(row=0, column=0, padx=10)

        # Botón Actualizar
        self.actualizar_btn = ctk.CTkButton(botones_frame, 
                                          text="Actualizar Categoría",
                                          command=self.actualizar_categoria,
                                          font=("Quicksand", 12),
                                          fg_color="#4A934A",
                                          hover_color="#367832")
        self.actualizar_btn.grid(row=0, column=1, padx=10)

        # Botón Eliminar
        self.eliminar_btn = ctk.CTkButton(botones_frame, 
                                        text="Eliminar Categoría",
                                        command=self.eliminar_categoria,
                                        font=("Quicksand", 12),
                                        fg_color="#B22222",
                                        hover_color="#8B1A1A")
        self.eliminar_btn.grid(row=0, column=2, padx=10)

        # Botón Limpiar
        self.limpiar_btn = ctk.CTkButton(botones_frame, 
                                        text="Limpiar Campos",
                                        command=self.limpiar_campos,
                                        font=("Quicksand", 12),
                                        fg_color="#6B2E2E",
                                        hover_color="#542424")
        self.limpiar_btn.grid(row=0, column=3, padx=10)

        # Tabla de categorías
        self.setup_tabla()

    def setup_tabla(self):
        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        tabla_frame.grid(row=3, column=0, pady=20, padx=20, sticky="nsew")

        # Crear la tabla
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Categorias.Treeview",
                       background="#ffffff",
                       foreground="#2E6B5C",
                       rowheight=30,
                       fieldbackground="#ffffff")
        style.configure("Categorias.Treeview.Heading",
                       background="#2E6B5C",
                       foreground="white",
                       relief="flat",
                       font=("Quicksand", 12, "bold"))

        # Definir columnas
        columns = ("id", "nombre", "descripcion", "fecha_creacion", "productos_count")
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show='headings', style="Categorias.Treeview")
        
        # Configurar columnas
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("fecha_creacion", text="Fecha de Creación")
        self.tabla.heading("productos_count", text="N° Productos")
        
        self.tabla.column("id", width=50)
        self.tabla.column("nombre", width=150)
        self.tabla.column("descripcion", width=300)
        self.tabla.column("fecha_creacion", width=150)
        self.tabla.column("productos_count", width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Evento de selección
        self.tabla.bind('<<TreeviewSelect>>', self.on_select)

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
                    
                self.actualizar_tabla()
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
                "fecha_creacion": "2024-01-15",
                "productos_count": 3
            }
        ]
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Actualizar tabla de categorías"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Mostrar categorías
            for categoria in self.categorias:
                # Verificar que categoria sea un diccionario
                if not isinstance(categoria, dict):
                    continue
                    
                # Obtener datos según la estructura de la API
                id_categoria = categoria.get("id_categoria", "")
                nombre = categoria.get("nombre", "")
                descripcion = categoria.get("descripcion", "")
                fecha_creacion = categoria.get("fecha_creacion", "")
                productos_count = categoria.get("productos_count", 0)
                
                # Insertar en tabla
                self.tabla.insert("", "end", values=(
                    id_categoria,
                    nombre,
                    descripcion,
                    fecha_creacion,
                    productos_count
                ))
                
        except Exception as e:
            print(f"Error en actualizar_tabla: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al actualizar tabla de categorías: {str(e)}")

    def guardar_categoria(self):
        """Crear nueva categoría"""
        try:
            # Validar campos
            nombre = self.nombre_entry.get().strip()
            descripcion = self.descripcion_text.get("1.0", "end-1c").strip()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre de la categoría es obligatorio")
                return
                
            # Preparar datos
            data = {
                "nombre": nombre,
                "descripcion": descripcion
            }
            
            # Hacer petición a la API
            url = INVENTORY_MANAGEMENT_ENDPOINTS['categories']['create']
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('POST', url, data=data, headers=headers)
            
            if response['status_code'] in [200, 201]:
                messagebox.showinfo("Éxito", "Categoría creada exitosamente")
                self.limpiar_campos()
                self.cargar_categorias()  # Recargar la tabla
            else:
                error_msg = response.get('data', 'Error desconocido')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('message', 'Error desconocido')
                messagebox.showerror("Error", f"Error al crear categoría: {error_msg}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar categoría: {str(e)}")

    def actualizar_categoria(self):
        """Actualizar categoría existente"""
        try:
            if not self.categoria_seleccionada:
                messagebox.showerror("Error", "Debe seleccionar una categoría para actualizar")
                return
                
            # Validar campos
            nombre = self.nombre_entry.get().strip()
            descripcion = self.descripcion_text.get("1.0", "end-1c").strip()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre de la categoría es obligatorio")
                return
                
            # Preparar datos
            data = {
                "nombre": nombre,
                "descripcion": descripcion
            }
            
            # Hacer petición a la API
            url = INVENTORY_MANAGEMENT_ENDPOINTS['categories']['update'].format(id=self.categoria_seleccionada['id_categoria'])
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('PUT', url, data=data, headers=headers)
            
            if response['status_code'] == 200:
                messagebox.showinfo("Éxito", "Categoría actualizada exitosamente")
                self.limpiar_campos()
                self.cargar_categorias()  # Recargar la tabla
            else:
                error_msg = response.get('data', 'Error desconocido')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('message', 'Error desconocido')
                messagebox.showerror("Error", f"Error al actualizar categoría: {error_msg}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar categoría: {str(e)}")

    def eliminar_categoria(self):
        """Eliminar categoría seleccionada"""
        try:
            if not self.categoria_seleccionada:
                messagebox.showerror("Error", "Debe seleccionar una categoría para eliminar")
                return
                
            # Confirmar eliminación
            resultado = messagebox.askyesno(
                "Confirmar Eliminación", 
                f"¿Está seguro de eliminar la categoría '{self.categoria_seleccionada['nombre']}'?\n\n"
                "Esta acción no se puede deshacer."
            )
            
            if not resultado:
                return
                
            # Hacer petición a la API
            url = INVENTORY_MANAGEMENT_ENDPOINTS['categories']['delete'].format(id=self.categoria_seleccionada['id_categoria'])
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('DELETE', url, headers=headers)
            
            if response['status_code'] in [200, 204]:
                messagebox.showinfo("Éxito", "Categoría eliminada exitosamente")
                self.limpiar_campos()
                self.cargar_categorias()  # Recargar la tabla
            else:
                error_msg = response.get('data', 'Error desconocido')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('message', 'Error desconocido')
                messagebox.showerror("Error", f"Error al eliminar categoría: {error_msg}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar categoría: {str(e)}")

    def limpiar_campos(self):
        """Limpiar todos los campos del formulario"""
        self.nombre_entry.delete(0, "end")
        self.descripcion_text.delete("1.0", "end")
        
        # Limpiar ID y fecha
        self.id_entry.configure(state="normal")
        self.id_entry.delete(0, "end")
        self.id_entry.configure(state="disabled")
        
        self.fecha_entry.configure(state="normal")
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.configure(state="disabled")
        
        # Limpiar selección
        self.categoria_seleccionada = None
        
        # Limpiar selección de tabla
        for item in self.tabla.selection():
            self.tabla.selection_remove(item)

    def on_select(self, event):
        """Manejar selección de categoría en la tabla"""
        try:
            if not self.tabla.selection():
                return
                
            selected_item = self.tabla.selection()[0]
            categoria_values = self.tabla.item(selected_item)['values']
            
            # Buscar la categoría completa en la lista
            categoria_id = categoria_values[0]
            self.categoria_seleccionada = None
            
            for cat in self.categorias:
                if str(cat.get('id_categoria', '')) == str(categoria_id):
                    self.categoria_seleccionada = cat
                    break
            
            if self.categoria_seleccionada:
                # Llenar los campos con los datos seleccionados
                self.id_entry.configure(state="normal")
                self.id_entry.delete(0, "end")
                self.id_entry.insert(0, str(self.categoria_seleccionada.get('id_categoria', '')))
                self.id_entry.configure(state="disabled")
                
                self.nombre_entry.delete(0, "end")
                self.nombre_entry.insert(0, self.categoria_seleccionada.get('nombre', ''))
                
                self.descripcion_text.delete("1.0", "end")
                self.descripcion_text.insert("1.0", self.categoria_seleccionada.get('descripcion', ''))
                
                # Mostrar fecha de creación
                self.fecha_entry.configure(state="normal")
                self.fecha_entry.delete(0, "end")
                self.fecha_entry.insert(0, self.categoria_seleccionada.get('fecha_creacion', ''))
                self.fecha_entry.configure(state="disabled")
                
        except Exception as e:
            print(f"Error en on_select: {str(e)}")
            messagebox.showerror("Error", f"Error al seleccionar categoría: {str(e)}")