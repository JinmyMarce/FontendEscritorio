import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as messagebox
from datetime import datetime
import os
from src.core.config import INVENTORY_MANAGEMENT_ENDPOINTS
from src.shared.utils import APIHandler, SessionManager

def es_wayland():
    """Detectar si estamos ejecutando en Wayland"""
    return os.environ.get('WAYLAND_DISPLAY') is not None or os.environ.get('XDG_SESSION_TYPE') == 'wayland'

class GestionCategoriasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurar layout responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # La tabla se expande
        
        # Variables de datos
        self.categorias = []
        self.categorias_filtradas = []
        self.categoria_seleccionada = None
        
        self.setup_ui()
        self.cargar_categorias()
        
    def setup_ui(self):
        # Título
        titulo = ctk.CTkLabel(self, text="Gestión de Categorías", 
                            font=("Quicksand", 24, "bold"),
                            text_color="#2E6B5C")
        titulo.grid(row=0, column=0, pady=20, sticky="ew")

        # Frame de controles (botones y filtros)
        controles_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        controles_frame.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")
        controles_frame.grid_columnconfigure(1, weight=1)  # El campo de búsqueda se expande

        # Botón Nueva Categoría
        nueva_btn = ctk.CTkButton(
            controles_frame,
            text="➕ Nueva Categoría",
            command=self.abrir_modal_nueva_categoria,
            font=("Quicksand", 12, "bold"),
            fg_color="#2E6B5C",
            hover_color="#24544A",
            width=150,
            height=35
        )
        nueva_btn.grid(row=0, column=0, padx=20, pady=15, sticky="w")

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
            values=["Nombre"],
            font=("Quicksand", 11),
            fg_color="#4A934A",
            button_color="#367832",
            width=100
        )
        self.tipo_busqueda.grid(row=0, column=1, padx=(0, 10), sticky="w")

        # Campo de búsqueda junto al dropdown
        self.busqueda_entry = ctk.CTkEntry(
            filtros_frame,
            placeholder_text="Buscar categorías...",
            font=("Quicksand", 12),
            width=250
        )
        self.busqueda_entry.grid(row=0, column=2, padx=(10, 20), sticky="ew")
        self.busqueda_entry.bind("<KeyRelease>", self.filtrar_categorias)

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
            values=["Todos", "Con productos", "Sin productos"],
            command=self.filtrar_categorias,
            font=("Quicksand", 11),
            fg_color="#4A934A",
            button_color="#367832",
            width=150
        )
        self.estado_filter.grid(row=0, column=1, sticky="w")

        # Tabla de categorías
        self.setup_tabla()

    def setup_tabla(self):
        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        tabla_frame.grid(row=2, column=0, pady=(0, 20), padx=20, sticky="nsew")

        # Crear la tabla
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Categorias.Treeview",
                       background="#ffffff",
                       foreground="#2E6B5C",
                       rowheight=35,  # Aumentar altura de filas
                       fieldbackground="#ffffff",
                       font=("Quicksand", 11))
        style.configure("Categorias.Treeview.Heading",
                       background="#2E6B5C",
                       foreground="white",
                       relief="flat",
                       font=("Quicksand", 12, "bold"))
        
        # Configurar selección de filas y hover effects
        style.map("Categorias.Treeview",
                 background=[('selected', '#E8F5E8')],
                 foreground=[('selected', '#2E6B5C')])

        # Definir columnas con estructura optimizada (sin columna extra)
        columns = ("id", "nombre", "descripcion", "fecha_creacion", "productos_count")
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show='headings', style="Categorias.Treeview")
        
        # Configurar encabezados y columnas con anchos optimizados
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("fecha_creacion", text="Fecha de Creación")
        self.tabla.heading("productos_count", text="N° Productos 🔍")  # Añadir indicador visual
        
        # Configurar anchos y alineación de columnas
        self.tabla.column("id", width=60, minwidth=50, anchor="center")
        self.tabla.column("nombre", width=200, minwidth=150, anchor="w")
        self.tabla.column("descripcion", width=380, minwidth=300, anchor="w")  # Más espacio sin la columna extra
        self.tabla.column("fecha_creacion", width=140, minwidth=120, anchor="center")
        self.tabla.column("productos_count", width=140, minwidth=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Eventos de la tabla (después de crear self.tabla)
        self.tabla.bind('<<TreeviewSelect>>', self.on_select)
        self.tabla.bind('<Double-1>', self.on_double_click)
        self.tabla.bind('<Button-1>', self.on_click)
        self.tabla.bind('<Motion>', self.on_mouse_motion)

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
                    
                self.categorias_filtradas = self.categorias.copy()
                self.actualizar_tabla()
            else:
                print(f"Error al cargar categorías desde API: {response.get('data', 'Error desconocido')}")
                self.cargar_categorias_ejemplo()
                
        except Exception as e:
            print(f"Error al cargar categorías: {str(e)}")  # Para debugging
            self.cargar_categorias_ejemplo()

    def cargar_categorias_ejemplo(self):
        """Cargar datos de ejemplo para categorías"""
        self.categorias = [
            {
                "id_categoria": 1,
                "nombre": "Paquetes de Fresas",
                "descripcion": "Frutas frescas y de temporada",
                "fecha_creacion": "2025-07-02T21:56:48.000000Z",
                "productos_count": 0
            },
            {
                "id_categoria": 2,
                "nombre": "Mermeladas",
                "descripcion": "Mermeladas artesanales elaboradas con fresas frescas y naturales",
                "fecha_creacion": "2025-07-02T21:56:48.000000Z",
                "productos_count": 0
            },
            {
                "id_categoria": 3,
                "nombre": "Fresas Deshidratadas",
                "descripcion": "Fresas deshidratadas, perfectas para snacks saludables",
                "fecha_creacion": "2025-07-02T21:56:48.000000Z",
                "productos_count": 0
            },
            {
                "id_categoria": 4,
                "nombre": "Combos Especiales",
                "descripcion": "Combos especiales de fresas y otros productos seleccionados",
                "fecha_creacion": "2025-07-02T21:56:48.000000Z",
                "productos_count": 1
            }
        ]
        self.categorias_filtradas = self.categorias.copy()
        self.actualizar_tabla()

    def filtrar_categorias(self, event=None):
        """Filtrar categorías según los criterios de búsqueda"""
        try:
            # Obtener valores de filtros
            texto_busqueda = self.busqueda_entry.get().lower().strip()
            estado_seleccionado = self.estado_filter.get()
            
            # Comenzar con todas las categorías
            categorias_filtradas = self.categorias.copy()
            
            # Filtrar por texto de búsqueda
            if texto_busqueda:
                categorias_filtradas = [
                    cat for cat in categorias_filtradas
                    if texto_busqueda in cat.get('nombre', '').lower()
                ]
            
            # Filtrar por estado
            if estado_seleccionado == "Con productos":
                categorias_filtradas = [
                    cat for cat in categorias_filtradas
                    if cat.get('productos_count', 0) > 0
                ]
            elif estado_seleccionado == "Sin productos":
                categorias_filtradas = [
                    cat for cat in categorias_filtradas
                    if cat.get('productos_count', 0) == 0
                ]
            # "Todos" no necesita filtro adicional
            
            self.categorias_filtradas = categorias_filtradas
            self.actualizar_tabla()
            
        except Exception as e:
            print(f"Error al filtrar categorías: {str(e)}")

    def abrir_modal_nueva_categoria(self):
        """Abrir modal para crear nueva categoría"""
        try:
            modal = ModalCategoria(self, "Nueva Categoría", None, self.guardar_categoria_modal)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir modal: {str(e)}")

    def abrir_modal_editar_categoria(self, event=None):
        """Abrir modal para editar/eliminar categoría al hacer doble clic"""
        try:
            if not self.tabla.selection():
                return
                
            selected_item = self.tabla.selection()[0]
            categoria_values = self.tabla.item(selected_item)['values']
            
            # Buscar la categoría completa en la lista
            categoria_id = categoria_values[0]
            categoria_seleccionada = None
            
            for cat in self.categorias:
                if str(cat.get('id_categoria', '')) == str(categoria_id):
                    categoria_seleccionada = cat
                    break
            
            if categoria_seleccionada:
                modal = ModalCategoria(
                    self, 
                    "Editar Categoría", 
                    categoria_seleccionada, 
                    self.actualizar_categoria_modal,
                    self.eliminar_categoria_modal
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir modal de edición: {str(e)}")

    def actualizar_tabla(self):
        """Actualizar tabla de categorías"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Usar categorías filtradas si existen, sino todas las categorías
            categorias_a_mostrar = self.categorias_filtradas if hasattr(self, 'categorias_filtradas') and self.categorias_filtradas else self.categorias
            
            print(f"Actualizando tabla con {len(categorias_a_mostrar)} categorías")  # Debug
                
            # Mostrar categorías
            for categoria in categorias_a_mostrar:
                # Verificar que categoria sea un diccionario
                if not isinstance(categoria, dict):
                    continue
                    
                # Obtener datos según la estructura de la API
                id_categoria = categoria.get("id_categoria", "")
                nombre = categoria.get("nombre", "")
                descripcion = categoria.get("descripcion", "")
                fecha_creacion = categoria.get("fecha_creacion", "")
                productos_count = categoria.get("productos_count", 0)
                
                # Formatear fecha si viene en formato ISO
                if fecha_creacion and "T" in fecha_creacion:
                    try:
                        fecha_obj = datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00'))
                        fecha_creacion = fecha_obj.strftime('%d/%m/%Y')
                    except:
                        fecha_creacion = fecha_creacion.split('T')[0]
                
                # Truncar descripción si es muy larga
                if len(descripcion) > 50:
                    descripcion = descripcion[:47] + "..."
                
                # Crear indicador visual para productos con funcionalidad
                if productos_count > 0:
                    productos_display = f"🔍 {productos_count}"  # Emoji de lupa para indicar que es clickeable
                else:
                    productos_display = str(productos_count)  # Solo el número para cero
                
                # Insertar en tabla (sin columna extra)
                self.tabla.insert("", "end", values=(
                    id_categoria,
                    nombre,
                    descripcion,
                    fecha_creacion,
                    productos_display
                ))
                
        except Exception as e:
            print(f"Error en actualizar_tabla: {str(e)}")  # Para debugging
            messagebox.showerror("Error", f"Error al actualizar tabla de categorías: {str(e)}")

    def guardar_categoria_modal(self, nombre, descripcion):
        """Callback para guardar categoría desde modal"""
        try:
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
                self.cargar_categorias()  # Recargar la tabla
                return True
            else:
                error_msg = response.get('data', 'Error desconocido')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('message', 'Error desconocido')
                messagebox.showerror("Error", f"Error al crear categoría: {error_msg}")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar categoría: {str(e)}")
            return False

    def actualizar_categoria_modal(self, categoria_id, nombre, descripcion):
        """Callback para actualizar categoría desde modal"""
        try:
            # Preparar datos
            data = {
                "nombre": nombre,
                "descripcion": descripcion
            }
            
            # Hacer petición a la API
            url = INVENTORY_MANAGEMENT_ENDPOINTS['categories']['update'].format(id=categoria_id)
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('PUT', url, data=data, headers=headers)
            
            if response['status_code'] == 200:
                messagebox.showinfo("Éxito", "Categoría actualizada exitosamente")
                self.cargar_categorias()  # Recargar la tabla
                return True
            else:
                error_msg = response.get('data', 'Error desconocido')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('message', 'Error desconocido')
                messagebox.showerror("Error", f"Error al actualizar categoría: {error_msg}")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar categoría: {str(e)}")
            return False

    def eliminar_categoria_modal(self, categoria_id, nombre_categoria):
        """Callback para eliminar categoría desde modal"""
        try:
            # Confirmar eliminación
            resultado = messagebox.askyesno(
                "Confirmar Eliminación", 
                f"¿Está seguro de eliminar la categoría '{nombre_categoria}'?\n\n"
                "Esta acción no se puede deshacer."
            )
            
            if not resultado:
                return False
                
            # Hacer petición a la API
            url = INVENTORY_MANAGEMENT_ENDPOINTS['categories']['delete'].format(id=categoria_id)
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            response = APIHandler.make_request('DELETE', url, headers=headers)
            
            if response['status_code'] in [200, 204]:
                messagebox.showinfo("Éxito", "Categoría eliminada exitosamente")
                self.cargar_categorias()  # Recargar la tabla
                return True
            else:
                error_msg = response.get('data', 'Error desconocido')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('message', 'Error desconocido')
                messagebox.showerror("Error", f"Error al eliminar categoría: {error_msg}")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar categoría: {str(e)}")
            return False

    # Métodos simplificados (mantener para compatibilidad)
    def guardar_categoria(self):
        """Método legacy - redirige al modal"""
        self.abrir_modal_nueva_categoria()

    def actualizar_categoria(self):
        """Método legacy - redirige al modal"""
        self.abrir_modal_editar_categoria()

    def eliminar_categoria(self):
        """Método legacy - redirige al modal"""
        self.abrir_modal_editar_categoria()

    def limpiar_campos(self):
        """Método legacy - ya no necesario con modales"""
        pass

    def on_select(self, event):
        """Manejar selección de categoría en la tabla"""
        try:
            if not self.tabla.selection():
                self.categoria_seleccionada = None
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
                
        except Exception as e:
            print(f"Error en on_select: {str(e)}")

    def on_click(self, event):
        """Manejar clic simple en la tabla"""
        try:
            # Identificar qué columna fue clickeada
            item = self.tabla.identify('item', event.x, event.y)
            column = self.tabla.identify('column', event.x, event.y)
            
            if item and column == '#5':  # Columna de "N° Productos" (índice 5)
                # Obtener datos del item clickeado
                categoria_values = self.tabla.item(item)['values']
                productos_count = categoria_values[4]
                
                # Solo abrir modal si hay productos (detectar por el emoji 🔍)
                if isinstance(productos_count, str) and '🔍' in productos_count:
                    self.ver_productos_categoria(item)
                elif isinstance(productos_count, int) and productos_count > 0:
                    self.ver_productos_categoria(item)
                
        except Exception as e:
            print(f"Error en on_click: {str(e)}")

    def on_double_click(self, event):
        """Manejar doble clic en la tabla"""
        try:
            # Identificar qué columna fue clickeada
            item = self.tabla.identify('item', event.x, event.y)
            column = self.tabla.identify('column', event.x, event.y)
            
            if item and column == '#5':  # Columna de "N° Productos"
                # Obtener datos del item clickeado
                categoria_values = self.tabla.item(item)['values']
                productos_count = categoria_values[4]
                
                # Solo abrir modal si hay productos
                if isinstance(productos_count, str) and '🔍' in productos_count:
                    self.ver_productos_categoria(item)
                elif isinstance(productos_count, int) and productos_count > 0:
                    self.ver_productos_categoria(item)
            else:
                # Para otras columnas, abrir modal de edición
                self.abrir_modal_editar_categoria(event)
                
        except Exception as e:
            print(f"Error en on_double_click: {str(e)}")

    def ver_productos_categoria(self, item):
        """Ver productos asociados a una categoría"""
        try:
            if not item:
                return
                
            categoria_values = self.tabla.item(item)['values']
            categoria_id = categoria_values[0]
            productos_count_display = categoria_values[4]
            
            # Extraer el número real de productos del display
            if isinstance(productos_count_display, str) and '🔍' in productos_count_display:
                productos_count = int(productos_count_display.replace('🔍', '').strip())
            else:
                productos_count = int(productos_count_display) if str(productos_count_display).isdigit() else 0
            
            # Buscar la categoría completa
            categoria_seleccionada = None
            for cat in self.categorias:
                if str(cat.get('id_categoria', '')) == str(categoria_id):
                    categoria_seleccionada = cat
                    break
            
            if not categoria_seleccionada:
                messagebox.showerror("Error", "No se pudo encontrar la categoría seleccionada")
                return
            
            # Si no hay productos, mostrar mensaje
            if productos_count == 0:
                messagebox.showinfo(
                    "Sin productos", 
                    f"La categoría '{categoria_seleccionada.get('nombre', '')}' no tiene productos asociados."
                )
                return
            
            # Abrir modal con productos
            modal = ModalProductosCategoria(self, categoria_seleccionada)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ver productos: {str(e)}")

    def on_mouse_motion(self, event):
        """Cambiar cursor cuando está sobre productos clickeables"""
        try:
            # Identificar si está sobre un item y qué columna
            item = self.tabla.identify('item', event.x, event.y)
            column = self.tabla.identify('column', event.x, event.y)
            
            if item and column == '#5':  # Columna de "N° Productos"
                # Obtener datos del item
                categoria_values = self.tabla.item(item)['values']
                productos_count = categoria_values[4]
                
                # Cambiar cursor si hay productos (detectar por el emoji 🔍)
                if isinstance(productos_count, str) and '🔍' in productos_count:
                    self.tabla.config(cursor="hand2")
                else:
                    self.tabla.config(cursor="")
            else:
                self.tabla.config(cursor="")
                
        except Exception as e:
            # En caso de error, restaurar cursor normal
            self.tabla.config(cursor="")

class ModalCategoria(ctk.CTkToplevel):
    """Modal para crear/editar categorías"""
    
    def __init__(self, parent, titulo, categoria=None, callback_guardar=None, callback_eliminar=None):
        super().__init__(parent)
        
        self.categoria = categoria
        self.callback_guardar = callback_guardar
        self.callback_eliminar = callback_eliminar
        self.es_edicion = categoria is not None
        
        # Configurar ventana
        self.title(titulo)
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Centrar ventana relativa al parent
        self.transient(parent)
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        
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
            text="Nueva Categoría" if not self.es_edicion else "Editar Categoría",
            font=("Quicksand", 20, "bold"),
            text_color="#2E6B5C"
        )
        titulo_label.grid(row=0, column=0, pady=20, sticky="ew")
        
        # Frame del formulario
        form_frame = ctk.CTkFrame(self, fg_color="#F8F9FA", corner_radius=10)
        form_frame.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        # ID (solo en edición)
        if self.es_edicion:
            ctk.CTkLabel(
                form_frame,
                text="ID Categoría:",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
            
            self.id_entry = ctk.CTkEntry(
                form_frame,
                state="disabled",
                font=("Quicksand", 12)
            )
            self.id_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Nombre
        ctk.CTkLabel(
            form_frame,
            text="Nombre de la Categoría: *",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(0 if not self.es_edicion else 0, 5))
        
        self.nombre_entry = ctk.CTkEntry(
            form_frame,
            font=("Quicksand", 12),
            placeholder_text="Ingrese el nombre de la categoría"
        )
        self.nombre_entry.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Descripción
        ctk.CTkLabel(
            form_frame,
            text="Descripción:",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.descripcion_text = ctk.CTkTextbox(
            form_frame,
            height=100,
            font=("Quicksand", 12)
        )
        self.descripcion_text.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Fecha de creación (solo en edición)
        if self.es_edicion:
            ctk.CTkLabel(
                form_frame,
                text="Fecha de Creación:",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).grid(row=6, column=0, sticky="w", padx=20, pady=(0, 5))
            
            self.fecha_entry = ctk.CTkEntry(
                form_frame,
                state="disabled",
                font=("Quicksand", 12)
            )
            self.fecha_entry.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Frame de botones
        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.grid(row=2, column=0, pady=20, sticky="ew")
        
        if self.es_edicion:
            # Botones para edición
            actualizar_btn = ctk.CTkButton(
                botones_frame,
                text="💾 Actualizar",
                command=self.actualizar_categoria,
                font=("Quicksand", 12, "bold"),
                fg_color="#4A934A",
                hover_color="#367832",
                width=120
            )
            actualizar_btn.grid(row=0, column=0, padx=10)
            
            eliminar_btn = ctk.CTkButton(
                botones_frame,
                text="🗑️ Eliminar",
                command=self.eliminar_categoria,
                font=("Quicksand", 12, "bold"),
                fg_color="#DC3545",
                hover_color="#B02A37",
                width=120
            )
            eliminar_btn.grid(row=0, column=1, padx=10)
            
            cancelar_btn = ctk.CTkButton(
                botones_frame,
                text="❌ Cancelar",
                command=self.cerrar_modal,
                font=("Quicksand", 12, "bold"),
                fg_color="#6C757D",
                hover_color="#545B62",
                width=120
            )
            cancelar_btn.grid(row=0, column=2, padx=10)
        else:
            # Botones para nueva categoría
            guardar_btn = ctk.CTkButton(
                botones_frame,
                text="💾 Guardar",
                command=self.guardar_categoria,
                font=("Quicksand", 12, "bold"),
                fg_color="#2E6B5C",
                hover_color="#24544A",
                width=120
            )
            guardar_btn.grid(row=0, column=0, padx=10)
            
            cancelar_btn = ctk.CTkButton(
                botones_frame,
                text="❌ Cancelar",
                command=self.cerrar_modal,
                font=("Quicksand", 12, "bold"),
                fg_color="#6C757D",
                hover_color="#545B62",
                width=120
            )
            cancelar_btn.grid(row=0, column=1, padx=10)
    
    def llenar_campos(self):
        """Llenar campos con datos de categoría existente"""
        if not self.categoria:
            return
            
        # ID
        if hasattr(self, 'id_entry'):
            self.id_entry.configure(state="normal")
            self.id_entry.delete(0, "end")
            self.id_entry.insert(0, str(self.categoria.get('id_categoria', '')))
            self.id_entry.configure(state="disabled")
        
        # Nombre
        self.nombre_entry.delete(0, "end")
        self.nombre_entry.insert(0, self.categoria.get('nombre', ''))
        
        # Descripción
        self.descripcion_text.delete("1.0", "end")
        self.descripcion_text.insert("1.0", self.categoria.get('descripcion', ''))
        
        # Fecha de creación
        if hasattr(self, 'fecha_entry'):
            fecha = self.categoria.get('fecha_creacion', '')
            if fecha and "T" in fecha:
                try:
                    fecha_obj = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    fecha = fecha_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    fecha = fecha.split('T')[0]
            
            self.fecha_entry.configure(state="normal")
            self.fecha_entry.delete(0, "end")
            self.fecha_entry.insert(0, fecha)
            self.fecha_entry.configure(state="disabled")
    
    def guardar_categoria(self):
        """Guardar nueva categoría"""
        # Validar campos
        nombre = self.nombre_entry.get().strip()
        descripcion = self.descripcion_text.get("1.0", "end-1c").strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre de la categoría es obligatorio")
            return
        
        # Llamar callback
        if self.callback_guardar:
            if self.callback_guardar(nombre, descripcion):
                self.cerrar_modal()
    
    def actualizar_categoria(self):
        """Actualizar categoría existente"""
        # Validar campos
        nombre = self.nombre_entry.get().strip()
        descripcion = self.descripcion_text.get("1.0", "end-1c").strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre de la categoría es obligatorio")
            return
        
        # Llamar callback
        if self.callback_guardar:
            if self.es_edicion:
                categoria_id = self.categoria.get('id_categoria')
                if self.callback_guardar(categoria_id, nombre, descripcion):
                    self.cerrar_modal()
            else:
                if self.callback_guardar(nombre, descripcion):
                    self.cerrar_modal()
    
    def eliminar_categoria(self):
        """Eliminar categoría"""
        if self.callback_eliminar:
            categoria_id = self.categoria.get('id_categoria')
            nombre_categoria = self.categoria.get('nombre', '')
            if self.callback_eliminar(categoria_id, nombre_categoria):
                self.cerrar_modal()
    
    def cerrar_modal(self):
        """Cerrar el modal de forma segura"""
        try:
            # Liberar grab si existe
            if self.grab_current() == self:
                self.grab_release()
        except:
            pass
        finally:
            self.destroy()
    
    def configurar_modal(self):
        """Configurar el modal de forma segura después de que esté visible"""
        try:
            # Centrar la ventana en la pantalla
            self.center_window()
            
            # Configurar según el entorno gráfico
            if es_wayland():
                # En Wayland, ser más conservador con el grab
                self.focus_set()
                self.lift()  # Traer al frente
                self.attributes('-topmost', True)  # Mantener arriba
                
                # Intentar grab con timeout
                try:
                    self.after(50, lambda: self.grab_set())
                except:
                    print("Info: Grab no disponible en Wayland, usando focus solamente")
            else:
                # En X11, usar el método tradicional
                self.focus_set()
                self.grab_set()
                
        except Exception as e:
            print(f"Warning: No se pudo configurar el modal correctamente: {e}")
            # Continuar sin el grab si hay problemas
            self.focus_set()
            self.lift()
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        try:
            self.update_idletasks()  # Asegurar que la ventana tenga su tamaño final
            
            # Obtener dimensiones de la pantalla
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # Obtener dimensiones de la ventana
            window_width = self.winfo_reqwidth()
            window_height = self.winfo_reqheight()
            
            # Calcular posición centrada
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Aplicar posición
            self.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            print(f"Warning: No se pudo centrar la ventana: {e}")


class ModalProductosCategoria(ctk.CTkToplevel):
    """Modal para mostrar productos asociados a una categoría"""
    
    def __init__(self, parent, categoria):
        super().__init__(parent)
        
        self.categoria = categoria
        self.productos = []
        
        # Configurar ventana
        self.title(f"Productos - {categoria.get('nombre', 'Categoría')}")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Centrar ventana relativa al parent
        self.transient(parent)
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        self.cargar_productos()
        
        # Configurar modal
        self.after(10, self.configurar_modal)
    
    def setup_ui(self):
        # Header del modal
        header_frame = ctk.CTkFrame(self, fg_color="#2E6B5C", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Título
        titulo_label = ctk.CTkLabel(
            header_frame,
            text=f"Productos de la categoría: {self.categoria.get('nombre', '')}",
            font=("Quicksand", 18, "bold"),
            text_color="white"
        )
        titulo_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Botón cerrar
        cerrar_btn = ctk.CTkButton(
            header_frame,
            text="✕ Cerrar",
            command=self.cerrar_modal,
            font=("Quicksand", 12, "bold"),
            fg_color="#DC3545",
            hover_color="#B02A37",
            width=80,
            height=30
        )
        cerrar_btn.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Información de la categoría
        info_frame = ctk.CTkFrame(self, fg_color="#F8F9FA", corner_radius=10)
        info_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        descripcion = self.categoria.get('descripcion', '')
        productos_count = self.categoria.get('productos_count', 0)
        if descripcion:
            info_text = f"Descripción: {descripcion}"
            if productos_count > 0:
                info_text += f" | Productos registrados: {productos_count}"
        else:
            info_text = f"Productos registrados en la categoría: {productos_count}"
            
        if descripcion or productos_count > 0:
            descripcion_label = ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=("Quicksand", 12),
                text_color="#2E6B5C",
                wraplength=700
            )
            descripcion_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Frame para la tabla de productos
        tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        tabla_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        # Crear tabla de productos
        style = ttk.Style()
        style.configure("Productos.Treeview",
                       background="#ffffff",
                       foreground="#2E6B5C",
                       rowheight=30,
                       fieldbackground="#ffffff",
                       font=("Quicksand", 10))
        style.configure("Productos.Treeview.Heading",
                       background="#2E6B5C",
                       foreground="white",
                       relief="flat",
                       font=("Quicksand", 11, "bold"))
        
        # Definir columnas para productos con información adicional
        columns = ("id", "nombre", "precio", "peso", "estado")
        self.tabla_productos = ttk.Treeview(tabla_frame, columns=columns, show='headings', style="Productos.Treeview")
        
        # Configurar encabezados y columnas
        self.tabla_productos.heading("id", text="ID")
        self.tabla_productos.heading("nombre", text="Nombre del Producto")
        self.tabla_productos.heading("precio", text="Precio")
        self.tabla_productos.heading("peso", text="Peso/Tamaño")
        self.tabla_productos.heading("estado", text="Estado")
        
        self.tabla_productos.column("id", width=60, minwidth=50, anchor="center")
        self.tabla_productos.column("nombre", width=280, minwidth=200, anchor="w")
        self.tabla_productos.column("precio", width=100, minwidth=80, anchor="center")
        self.tabla_productos.column("peso", width=120, minwidth=100, anchor="center")
        self.tabla_productos.column("estado", width=120, minwidth=80, anchor="center")
        
        # Scrollbar para productos
        scrollbar_productos = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=scrollbar_productos.set)
        
        self.tabla_productos.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar_productos.pack(side="right", fill="y")
        
        # Frame para estadísticas
        stats_frame = ctk.CTkFrame(self, fg_color="#E8F5E8", corner_radius=10)
        stats_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="🔄 Cargando productos desde la API...",
            font=("Quicksand", 12, "bold"),
            text_color="#2E6B5C"
        )
        self.stats_label.grid(row=0, column=0, padx=20, pady=10)
    
    def cargar_productos(self):
        """Cargar productos de la categoría desde la API"""
        try:
            categoria_id = self.categoria.get('id_categoria')
            token = SessionManager.get_token()
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            
            print(f"Cargando productos para categoría ID: {categoria_id}")  # Debug
            
            # Usar directamente el endpoint de lista de productos y filtrar localmente
            # ya que el endpoint by_category no está funcionando correctamente
            url_all = INVENTORY_MANAGEMENT_ENDPOINTS['products']['list']
            print(f"Cargando todos los productos desde: {url_all}")  # Debug
            
            response = APIHandler.make_request('GET', url_all, headers=headers)
            
            if response['status_code'] == 200:
                self.procesar_respuesta_productos_real(response['data'], categoria_id)
            else:
                print(f"Error al cargar productos desde API: {response.get('data', 'Error desconocido')}")
                self.cargar_productos_ejemplo()
                
        except Exception as e:
            print(f"Error al cargar productos: {str(e)}")
            self.cargar_productos_ejemplo()
        
        self.actualizar_tabla_productos()

    def procesar_respuesta_productos_real(self, api_data, categoria_id):
        """Procesar la respuesta real de la API con la estructura conocida"""
        try:
            print(f"Procesando respuesta API real: {type(api_data)}")  # Debug
            
            # La API devuelve: {"message": "...", "data": [productos...]}
            if isinstance(api_data, dict) and 'data' in api_data:
                productos_api = api_data['data']
            elif isinstance(api_data, list):
                productos_api = api_data
            else:
                print(f"Estructura inesperada de API: {api_data}")
                productos_api = []
            
            print(f"Total productos en API: {len(productos_api)}")  # Debug
            
            # Filtrar productos por categoría usando la estructura real
            productos_categoria = []
            for producto in productos_api:
                if isinstance(producto, dict):
                    # Usar el campo correcto de la API: categorias_id_categoria
                    producto_categoria_id = (
                        producto.get('categorias_id_categoria') or 
                        producto.get('categoria_id') or 
                        producto.get('id_categoria') or
                        (producto.get('categoria', {}).get('id_categoria') if isinstance(producto.get('categoria'), dict) else None)
                    )
                    
                    # Debug: mostrar relaciones encontradas
                    if producto_categoria_id:
                        print(f"Producto '{producto.get('nombre', 'Sin nombre')}' -> Categoría ID: {producto_categoria_id}")
                    
                    if str(producto_categoria_id) == str(categoria_id):
                        # Normalizar datos del producto según la estructura real de la API
                        producto_normalizado = {
                            "id": producto.get('id_producto', 'N/A'),
                            "nombre": producto.get('nombre', 'Sin nombre'),
                            "precio": self.convertir_precio(producto.get('precio', 0)),
                            "stock": producto.get('stock', 0),  # Si no viene stock, usar 0
                            "estado": self.normalizar_estado(producto.get('estado', 'activo')),
                            "descripcion": producto.get('descripcion', ''),
                            "peso": producto.get('peso', ''),
                            "imagen": producto.get('url_imagen', ''),
                            "fecha_creacion": producto.get('fecha_creacion', ''),
                            "categoria_info": producto.get('categoria', {})
                        }
                        productos_categoria.append(producto_normalizado)
            
            self.productos = productos_categoria
            print(f"Productos filtrados para categoría {categoria_id}: {len(self.productos)}")  # Debug
            
            # Si no se encontraron productos pero la API respondió correctamente,
            # mostrar un mensaje específico en lugar de datos de ejemplo
            if len(self.productos) == 0:
                print("No se encontraron productos en la API para esta categoría")
                # Cargar ejemplo si productos_count > 0 (puede ser inconsistencia temporal)
                if self.categoria.get('productos_count', 0) > 0:
                    print("Pero productos_count > 0, cargando ejemplos como fallback...")
                    self.cargar_productos_ejemplo()
                    
        except Exception as e:
            print(f"Error al procesar respuesta de productos: {str(e)}")
            self.cargar_productos_ejemplo()

    def convertir_precio(self, precio):
        """Convertir precio de string a float de manera segura"""
        try:
            if isinstance(precio, str):
                # Remover caracteres no numéricos excepto punto y coma
                precio_limpio = precio.replace(',', '').replace('$', '').strip()
                return float(precio_limpio)
            elif isinstance(precio, (int, float)):
                return float(precio)
            else:
                return 0.0
        except (ValueError, AttributeError):
            return 0.0

    def normalizar_estado(self, estado):
        """Normalizar el estado del producto para mostrar"""
        if isinstance(estado, str):
            estado_lower = estado.lower()
            if estado_lower == 'activo':
                return 'Disponible'
            elif estado_lower == 'inactivo':
                return 'No disponible'
            elif estado_lower == 'agotado':
                return 'Agotado'
            else:
                return estado.capitalize()
        return 'Estado desconocido'
    
    def cargar_productos_ejemplo(self):
        """Cargar productos de ejemplo cuando la API no está disponible"""
        categoria_id = self.categoria.get('id_categoria')
        productos_count = self.categoria.get('productos_count', 0)
        categoria_nombre = self.categoria.get('nombre', '').lower()
        
        print(f"Cargando datos de ejemplo para categoría: {categoria_nombre}")  # Debug
        
        if productos_count == 0:
            self.productos = []
        else:
            # Generar productos de ejemplo más realistas según la categoría
            if 'fresa' in categoria_nombre or 'paquete' in categoria_nombre:
                self.productos = [
                    {
                        "id": 1,
                        "nombre": "Fresas Premium 500g",
                        "precio": 15000,
                        "stock": 25,
                        "estado": "Disponible",
                        "descripcion": "Fresas frescas de la mejor calidad"
                    },
                    {
                        "id": 2,
                        "nombre": "Fresas Orgánicas 1kg",
                        "precio": 28000,
                        "stock": 15,
                        "estado": "Disponible",
                        "descripcion": "Fresas cultivadas sin químicos"
                    },
                    {
                        "id": 7,
                        "nombre": "Paquete Familiar 2kg",
                        "precio": 45000,
                        "stock": 8,
                        "estado": "Limitado",
                        "descripcion": "Ideal para familias numerosas"
                    }
                ][:productos_count]  # Limitar según productos_count
                
            elif 'mermelada' in categoria_nombre:
                self.productos = [
                    {
                        "id": 3,
                        "nombre": "Mermelada de Fresa Artesanal 250g",
                        "precio": 12000,
                        "stock": 30,
                        "estado": "Disponible",
                        "descripcion": "Mermelada casera sin conservantes"
                    },
                    {
                        "id": 8,
                        "nombre": "Mermelada de Fresa Light 200g",
                        "precio": 14000,
                        "stock": 18,
                        "estado": "Disponible",
                        "descripcion": "Versión reducida en azúcar"
                    }
                ][:productos_count]
                
            elif 'combo' in categoria_nombre:
                self.productos = [
                    {
                        "id": 4,
                        "nombre": "Combo Familiar - Fresas + Mermelada",
                        "precio": 35000,
                        "stock": 8,
                        "estado": "Limitado",
                        "descripcion": "Paquete especial con descuento"
                    }
                ][:productos_count]
                
            elif 'deshidrat' in categoria_nombre:
                self.productos = [
                    {
                        "id": 9,
                        "nombre": "Fresas Deshidratadas Snack 100g",
                        "precio": 8000,
                        "stock": 45,
                        "estado": "Disponible",
                        "descripcion": "Perfecto para snack saludable"
                    },
                    {
                        "id": 10,
                        "nombre": "Mix Fresas Deshidratadas 250g",
                        "precio": 18000,
                        "stock": 22,
                        "estado": "Disponible",
                        "descripcion": "Mezcla gourmet para postres"
                    }
                ][:productos_count]
            else:
                # Productos genéricos para otras categorías
                self.productos = [
                    {
                        "id": 5,
                        "nombre": f"Producto de {categoria_nombre}",
                        "precio": 10000,
                        "stock": 10,
                        "estado": "Disponible",
                        "descripcion": f"Producto relacionado con {categoria_nombre}"
                    }
                ][:productos_count]
    
    def actualizar_tabla_productos(self):
        """Actualizar tabla de productos"""
        try:
            # Limpiar tabla
            for item in self.tabla_productos.get_children():
                self.tabla_productos.delete(item)
            
            # Agregar productos
            total_productos = len(self.productos)
            valor_total = 0
            
            for producto in self.productos:
                # Obtener datos con valores por defecto seguros
                id_producto = producto.get('id', 'N/A')
                nombre = producto.get('nombre', 'Producto sin nombre')
                precio = producto.get('precio', 0)
                peso = producto.get('peso', 'No especificado')
                estado = producto.get('estado', 'N/A')
                
                # Convertir precio a número seguro
                try:
                    precio_num = float(precio) if precio else 0
                except (ValueError, TypeError):
                    precio_num = 0
                
                # Formatear precio
                precio_formateado = f"${precio_num:,.0f}" if precio_num > 0 else "Sin precio"
                
                # Acumular para estadísticas (sin stock, solo contar productos)
                valor_total += precio_num
                
                # Formatear peso/tamaño
                peso_display = peso if peso and peso != 'No especificado' else '-'
                
                # Truncar nombre si es muy largo
                if len(nombre) > 35:
                    nombre = nombre[:32] + "..."
                
                self.tabla_productos.insert("", "end", values=(
                    id_producto,
                    nombre,
                    precio_formateado,
                    peso_display,
                    estado
                ))
            
            # Actualizar estadísticas (adaptadas para datos sin stock)
            if total_productos == 0:
                # Verificar si se esperaban productos
                productos_esperados = self.categoria.get('productos_count', 0)
                if productos_esperados > 0:
                    stats_text = f"⚠️ Se esperaban {productos_esperados} productos, pero no se encontraron en la API"
                else:
                    stats_text = "📭 No hay productos en esta categoría"
            else:
                # Estadísticas sin stock (la API no incluye stock)
                precio_promedio = valor_total / total_productos if total_productos > 0 else 0
                stats_text = (f"📊 Total: {total_productos} productos | "
                            f"� Precio promedio: ${precio_promedio:,.0f} | "
                            f"🏷️ Valor total catálogo: ${valor_total:,.0f}")
            
            self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            print(f"Error al actualizar tabla de productos: {str(e)}")
            # En caso de error, mostrar mensaje
            self.stats_label.configure(text="❌ Error al cargar estadísticas de productos")
    
    def cerrar_modal(self):
        """Cerrar el modal de forma segura"""
        try:
            if self.grab_current() == self:
                self.grab_release()
        except:
            pass
        finally:
            self.destroy()
    
    def configurar_modal(self):
        """Configurar el modal de forma segura"""
        try:
            # Centrar la ventana
            self.center_window()
            
            # Configurar según el entorno gráfico
            if es_wayland():
                self.focus_set()
                self.lift()
                self.attributes('-topmost', True)
                try:
                    self.after(50, lambda: self.grab_set())
                except:
                    print("Info: Grab no disponible en Wayland")
            else:
                self.focus_set()
                self.grab_set()
                
        except Exception as e:
            print(f"Warning: No se pudo configurar el modal: {e}")
            self.focus_set()
            self.lift()
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        try:
            self.update_idletasks()
            
            # Obtener dimensiones de la pantalla
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # Obtener dimensiones de la ventana
            window_width = self.winfo_reqwidth()
            window_height = self.winfo_reqheight()
            
            # Calcular posición centrada
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Aplicar posición
            self.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            print(f"Warning: No se pudo centrar la ventana: {e}")