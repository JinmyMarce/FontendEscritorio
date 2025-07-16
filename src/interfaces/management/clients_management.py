import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
import hashlib
from datetime import datetime
from src.shared.image_handler import ImageHandler

class GestionClientes(ctk.CTkFrame):
    def __init__(self, parent, dashboard=None):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Referencia al dashboard para navegación
            self.dashboard = dashboard
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Inicializar variables de datos
            self.clientes = []
            self.clientes_originales = []  # Para mantener copia de todos los clientes
            self.clientes_filtrados = []  # Para almacenar resultados de búsqueda
            self.total_clientes = 0
            self.clientes_activos = 0
            self.clientes_inactivos = 0
            self.busqueda_timer = None  # Para debounce de búsqueda en API
            
            # Frame superior
            top_frame = ctk.CTkFrame(self, fg_color="transparent")
            top_frame.pack(fill="x", pady=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            title_frame.pack(side="left")
            
            # Cargar y mostrar icono
            icon = self.image_handler.load_image("usuarios.png", (32, 32))
            if icon:
                ctk.CTkLabel(
                    title_frame,
                    image=icon,
                    text=""
                ).pack(side="left", padx=(0, 10))
                
            ctk.CTkLabel(
                title_frame,
                text="Gestión de Clientes",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left")
            
            # Frame para búsqueda y filtros
            search_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            search_frame.pack(fill="x", pady=(0, 20))
            
            # Primera fila: Filtros de búsqueda
            filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
            filter_frame.pack(fill="x", padx=15, pady=(10, 5))
            
            # Filtro por tipo de búsqueda
            ctk.CTkLabel(
                filter_frame,
                text="Buscar por:",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left", padx=(0, 10))
            
            self.filtro_busqueda_var = ctk.StringVar(value="Nombre")
            filtro_menu = ctk.CTkOptionMenu(
                filter_frame,
                values=["Nombre", "Apellidos", "Email", "Teléfono"],
                variable=self.filtro_busqueda_var,
                width=120,
                fg_color="#2E6B5C",
                button_color="#1D4A3C",
                button_hover_color="#153A2C",
                dropdown_fg_color="#FFFFFF",
                dropdown_hover_color="#F5F5F5",
                dropdown_text_color="#2E6B5C"
            )
            filtro_menu.pack(side="left", padx=(0, 15))
            
            # Campo de búsqueda más corto
            self.search_var = ctk.StringVar()
            self.search_var.trace("w", self.on_search_change)
            search_entry = ctk.CTkEntry(
                filter_frame,
                textvariable=self.search_var,
                width=160,
                height=30,
                placeholder_text="Buscar...",
                border_width=1,
                border_color="#E0E0E0",
                fg_color="#F9F9F9",
                font=("Quicksand", 10)
            )
            search_entry.pack(side="left", padx=(0, 15))
            
            # Filtro de estado
            ctk.CTkLabel(
                filter_frame,
                text="Estado:",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left", padx=(0, 10))
            
            self.estado_var = ctk.StringVar(value="Todos")
            self.estado_var.trace("w", self.on_search_change)
            estado_menu = ctk.CTkOptionMenu(
                filter_frame,
                values=["Todos", "Activo", "Inactivo"],
                variable=self.estado_var,
                width=100,
                fg_color="#2E6B5C",
                button_color="#1D4A3C",
                button_hover_color="#153A2C",
                dropdown_fg_color="#FFFFFF",
                dropdown_hover_color="#F5F5F5",
                dropdown_text_color="#2E6B5C"
            )
            estado_menu.pack(side="left", padx=(0, 15))
            
            # Segunda fila: Botones de acción
            action_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
            action_frame.pack(fill="x", padx=15, pady=(5, 10))
            
            # Botón cambiar estado - más claro y adaptable
            self.btn_cambiar_estado = ctk.CTkButton(
                action_frame,
                text="Cambiar Estado",
                command=self.cambiar_estado_seleccionado,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                font=("Quicksand", 12, "bold")
            )
            self.btn_cambiar_estado.pack(side="left", padx=(0, 10), fill="x", expand=True)
            
            # Botón resetear contraseña - más claro y adaptable
            self.btn_resetear = ctk.CTkButton(
                action_frame,
                text="Resetear Contraseña",
                command=self.resetear_password,
                fg_color="#FFA000",
                hover_color="#F57C00",
                font=("Quicksand", 12, "bold")
            )
            self.btn_resetear.pack(side="left", padx=(0, 10), fill="x", expand=True)
            
            # Botón limpiar búsqueda
            btn_limpiar = ctk.CTkButton(
                action_frame,
                text="Limpiar Filtros",
                command=self.limpiar_filtros,
                fg_color="#757575",
                hover_color="#616161",
                font=("Quicksand", 12, "bold")
            )
            btn_limpiar.pack(side="left", fill="x", expand=True)
            
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
            self.tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            self.tabla_frame.pack(fill="both", expand=True)
            
            # Frame para tabla y botones de acción
            tabla_container = ctk.CTkFrame(self.tabla_frame, fg_color="#FFFFFF")
            tabla_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Tabla - Solo campos necesarios
            columns = ("nombre", "apellidos", "telefono", "estado")
            
            self.tabla = ttk.Treeview(
                tabla_container,
                columns=columns,
                show="headings",
                selectmode="browse",
                style="Custom.Treeview"
            )
            
            # Configurar columnas
            self.tabla.heading("nombre", text="Nombre")
            self.tabla.heading("apellidos", text="Apellidos")
            self.tabla.heading("telefono", text="Teléfono")
            self.tabla.heading("estado", text="Estado")
            
            # Configurar anchuras de columnas para que se adapten
            self.tabla.column("nombre", anchor="w", minwidth=150, width=200, stretch=True)
            self.tabla.column("apellidos", anchor="w", minwidth=150, width=250, stretch=True)
            self.tabla.column("telefono", anchor="center", minwidth=120, width=150, stretch=False)
            self.tabla.column("estado", anchor="center", minwidth=100, width=120, stretch=False)
            
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
            
            # Configurar colores de estado para los clientes
            self.tabla.tag_configure("activo", foreground="#2E7D32")
            self.tabla.tag_configure("inactivo", foreground="#C62828")
            
            # Configurar filas alternas para mejor visualización
            self.tabla.tag_configure("oddrow", background="#F8F9FA")
            self.tabla.tag_configure("evenrow", background="#FFFFFF")
            
            # Cargar datos
            self.cargar_datos()
            
            # Bind doble clic
            self.tabla.bind("<Double-1>", self.ver_detalles)
            
            # Bind tecla Enter
            self.tabla.bind("<Return>", self.ver_detalles)
            
            # Bind tecla Delete
            self.tabla.bind("<Delete>", self.eliminar_cliente)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar: {str(e)}")
            
    def normalizar_cliente(self, cliente_data):
        """Normalizar datos del cliente para consistencia interna"""
        return {
            "id_usuario": cliente_data.get('id_usuario'),
            "nombre": cliente_data.get('nombre', ''),
            "apellidos": cliente_data.get('apellidos', ''),
            "email": cliente_data.get('email', ''),
            "telefono": cliente_data.get('telefono', ''),
            "created_at": cliente_data.get('created_at', cliente_data.get('fecha_creacion', '')),
            "estado": "Activo" if cliente_data.get('estado') else "Inactivo",
            "roles_id_rol": cliente_data.get('roles_id_rol', 2)
        }
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
        
    def format_telefono(self, telefono):
        """Formatear teléfono para mostrar en la tabla"""
        if not telefono or telefono.strip() == '' or telefono.lower() == 'none':
            return "Sin teléfono"
        return telefono.strip()
        
    def cargar_datos(self):
        """Cargar datos reales desde la API"""
        try:
            from src.core.config import CLIENTS_ENDPOINTS
            from src.shared.utils import APIHandler
            
            print("Cargando clientes desde la API...")
            
            # Obtener clientes desde la API
            response = APIHandler.make_request('get', CLIENTS_ENDPOINTS['list'])
            
            print(f"Respuesta completa: {response}")
            
            # Validar que la respuesta sea válida
            if not isinstance(response, dict):
                print(f"Error: Respuesta no es un diccionario: {type(response)}")
                raise Exception("Respuesta de la API no válida")
                
            if response.get('status_code') == 200:
                # Validar que data sea un diccionario
                data = response.get('data', {})
                if not isinstance(data, dict):
                    print(f"Error: response['data'] no es un diccionario: {type(data)}")
                    raise Exception("Formato de respuesta de la API no válido")
                
                clients_data = data.get('clients', [])
                self.clientes = []
                
                if not isinstance(clients_data, list):
                    print(f"Error: clients_data no es una lista: {type(clients_data)}")
                    clients_data = []
                
                for client in clients_data:
                    if isinstance(client, dict):
                        cliente_procesado = self.normalizar_cliente(client)
                        self.clientes.append(cliente_procesado)
                
                # Guardar copia original para filtrado local
                self.clientes_originales = self.clientes.copy()
                
                print(f"Cargados {len(self.clientes)} clientes desde la API")
                
                # Actualizar estadísticas si están disponibles
                if 'statistics' in data and isinstance(data['statistics'], dict):
                    stats = data['statistics']
                    self.total_clientes = stats.get('total_clients', len(self.clientes))
                    self.clientes_activos = stats.get('active_clients', 0)
                    self.clientes_inactivos = stats.get('inactive_clients', 0)
                    print(f"Estadísticas: Total: {self.total_clientes}, Activos: {self.clientes_activos}, Inactivos: {self.clientes_inactivos}")
            else:
                error_msg = "Error desconocido"
                data = response.get('data', {})
                if isinstance(data, dict):
                    error_msg = data.get('error', error_msg)
                elif isinstance(data, str):
                    error_msg = data
                
                print(f"Error al cargar clientes (status {response.get('status_code')}): {error_msg}")
                messagebox.showerror("Error", f"No se pudieron cargar los datos de clientes desde el servidor\nError: {error_msg}")
                # Fallback a datos de ejemplo
                self.clientes = self.cargar_datos_ejemplo()
                self.clientes_originales = self.clientes.copy()
                
        except Exception as e:
            print(f"Excepción al cargar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al conectar con el servidor: {str(e)}")
            # Fallback a datos de ejemplo
            self.clientes = self.cargar_datos_ejemplo()
            self.clientes_originales = self.clientes.copy()
        
        # Limpiar tabla y mostrar datos
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar datos en la tabla - Solo campos necesarios
            for i, cliente in enumerate(self.clientes):
                # Configurar tags para el estado y filas alternas
                estado_tag = "activo" if cliente["estado"] == "Activo" else "inactivo"
                row_type = "evenrow" if i % 2 == 0 else "oddrow"
                tags = (estado_tag, row_type)
                
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente["nombre"],
                        cliente["apellidos"],
                        self.format_telefono(cliente.get("telefono")),
                        cliente["estado"]
                    ),
                    tags=tags
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar datos en la tabla: {str(e)}")
            
    def limpiar_filtros(self):
        """Limpiar todos los filtros de búsqueda"""
        try:
            # Cancelar búsqueda pendiente si existe
            if self.busqueda_timer:
                self.after_cancel(self.busqueda_timer)
                self.busqueda_timer = None
            
            # Resetear variables de filtro
            self.search_var.set("")
            self.estado_var.set("Todos")
            self.filtro_busqueda_var.set("Nombre")
            
            # Limpiar clientes filtrados
            self.clientes_filtrados = []
            
            # Recargar datos originales desde la API
            self.cargar_datos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar filtros: {str(e)}")
            
    def on_search_change(self, *args):
        """Manejar cambios en la búsqueda con debounce"""
        try:
            # Cancelar búsqueda pendiente si existe
            if self.busqueda_timer:
                self.after_cancel(self.busqueda_timer)
                self.busqueda_timer = None
            
            # Obtener valores actuales
            busqueda = self.search_var.get().strip()
            estado = self.estado_var.get()
            tipo_filtro = self.filtro_busqueda_var.get()
            
            # Si no hay búsqueda, mostrar filtrado solo por estado
            if not busqueda:
                self.filtrar_solo_localmente("", estado, tipo_filtro)
                return
            
            # Si la búsqueda es muy corta (menos de 2 caracteres), filtrar solo localmente
            if len(busqueda) < 2:
                self.filtrar_solo_localmente(busqueda, estado, tipo_filtro)
                return
            
            # Para búsquedas de 2+ caracteres, usar debounce antes de llamar a la API
            self.busqueda_timer = self.after(500, lambda: self.buscar_clientes(busqueda, estado, tipo_filtro))
            
        except Exception as e:
            print(f"Error en on_search_change: {str(e)}")
            messagebox.showerror("Error", f"Error al procesar búsqueda: {str(e)}")

    def filtrar_tabla(self, *args):
        """Método legacy - redirigido a on_search_change para compatibilidad"""
        self.on_search_change(*args)
            
    def filtrar_solo_localmente(self, busqueda, estado, tipo_filtro):
        """Filtrar solo localmente sin llamar a la API"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Usar datos originales para filtrar
            datos_para_filtrar = self.clientes_originales if self.clientes_originales else self.clientes
                
            # Filtrar y cargar datos
            for cliente in datos_para_filtrar:
                # Aplicar filtro de estado
                if estado != "Todos" and cliente["estado"] != estado:
                    continue
                
                # Aplicar filtro de búsqueda si hay texto
                if busqueda:
                    campo_valor = ""
                    if tipo_filtro == "Nombre":
                        campo_valor = cliente.get("nombre", "").lower()
                    elif tipo_filtro == "Apellidos":
                        campo_valor = cliente.get("apellidos", "").lower()
                    elif tipo_filtro == "Email":
                        campo_valor = cliente.get("email", "").lower()
                    elif tipo_filtro == "Teléfono":
                        campo_valor = str(cliente.get("telefono", "")).lower()
                    
                    # Si el campo no contiene la búsqueda, saltarlo
                    if busqueda.lower() not in campo_valor:
                        continue
                    
                # Configurar tags para el estado y filas alternas
                estado_tag = "activo" if cliente["estado"] == "Activo" else "inactivo"
                row_type = "evenrow" if len(self.tabla.get_children()) % 2 == 0 else "oddrow"
                tags = (estado_tag, row_type)
                
                # Insertar fila - Solo campos necesarios
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente["nombre"],
                        cliente["apellidos"],
                        self.format_telefono(cliente.get("telefono")),
                        cliente["estado"]
                    ),
                    tags=tags
                )
                
        except Exception as e:
            print(f"Error en filtrado local: {str(e)}")
            messagebox.showerror("Error", f"Error al filtrar datos localmente: {str(e)}")
            
    def buscar_clientes(self, query="", estado="Todos", tipo_filtro="Nombre"):
        """Buscar clientes con filtros específicos desde la API"""
        try:
            from src.core.config import CLIENTS_ENDPOINTS
            from src.shared.utils import APIHandler
            
            # Validar que la consulta tenga al menos 2 caracteres
            if query.strip() and len(query.strip()) < 2:
                print(f"Consulta muy corta ('{query}'), filtrando solo localmente")
                self.filtrar_solo_localmente(query, estado, tipo_filtro)
                return
            
            print(f"Buscando clientes: query='{query}', estado='{estado}', tipo='{tipo_filtro}'")
            
            # Preparar parámetros de búsqueda
            params = {}
            if query.strip() and len(query.strip()) >= 2:
                # Mapear el tipo de filtro al parámetro de la API
                if tipo_filtro == "Nombre":
                    params['query'] = query.strip()  # El backend busca en nombre por defecto
                elif tipo_filtro == "Apellidos":
                    params['query'] = query.strip()  # Usar query general, filtrar después localmente
                elif tipo_filtro == "Email":
                    params['query'] = query.strip()  # Usar query general, filtrar después localmente
                elif tipo_filtro == "Teléfono":
                    params['query'] = query.strip()  # Usar query general, filtrar después localmente
                else:
                    params['query'] = query.strip()  # Fallback a búsqueda general
            
            if estado != "Todos":
                params['estado'] = estado == "Activo"
            
            # Si no hay parámetros válidos, filtrar solo localmente
            if not params:
                self.filtrar_solo_localmente(query, estado, tipo_filtro)
                return
            
            # Realizar búsqueda
            response = APIHandler.make_request('get', CLIENTS_ENDPOINTS['list'], params=params)
            
            # Validar que la respuesta sea válida
            if not isinstance(response, dict):
                print(f"Error: Respuesta no es un diccionario: {type(response)}")
                raise Exception("Respuesta de la API no válida")
            
            if response.get('status_code') == 200:
                # Validar que data sea un diccionario
                data = response.get('data', {})
                if not isinstance(data, dict):
                    print(f"Error: response['data'] no es un diccionario: {type(data)}")
                    raise Exception("Formato de respuesta de la API no válido")
                
                clients_data = data.get('clients', [])
                
                # Procesar resultados de la API
                self.clientes_filtrados = []
                
                if not isinstance(clients_data, list):
                    print(f"Error: clients_data no es una lista: {type(clients_data)}")
                    clients_data = []
                
                for client in clients_data:
                    if isinstance(client, dict):
                        cliente_procesado = self.normalizar_cliente(client)
                        self.clientes_filtrados.append(cliente_procesado)
                
                # Si la API no devolvió resultados específicos para el filtro, filtrar localmente
                if tipo_filtro != "Nombre" and query.strip():
                    print(f"Filtrando localmente por {tipo_filtro}")
                    self.clientes_filtrados = self.aplicar_filtro_especifico(self.clientes_filtrados, query, tipo_filtro)
                
                print(f"Encontrados {len(self.clientes_filtrados)} clientes")
                
                # Actualizar tabla con resultados filtrados
                self.actualizar_tabla_con_filtrados()
                
            elif response.get('status_code') == 422:
                # Error de validación, filtrar solo localmente
                print(f"Error de validación del servidor, filtrando localmente")
                self.filtrar_solo_localmente(query, estado, tipo_filtro)
                
            else:
                error_msg = "Error desconocido"
                data = response.get('data', {})
                if isinstance(data, dict):
                    error_msg = data.get('error', error_msg)
                elif isinstance(data, str):
                    error_msg = data
                
                print(f"Error en búsqueda (status {response.get('status_code')}): {error_msg}")
                # En caso de error, filtrar localmente como fallback
                print("Usando filtrado local como fallback")
                self.filtrar_solo_localmente(query, estado, tipo_filtro)
                
        except Exception as e:
            print(f"Error en búsqueda: {str(e)}")
            import traceback
            traceback.print_exc()
            # En caso de excepción, filtrar localmente como fallback
            print("Usando filtrado local como fallback por excepción")
            self.filtrar_solo_localmente(query, estado, tipo_filtro)

    def aplicar_filtro_especifico(self, clientes_lista, query, tipo_filtro):
        """Aplicar filtro específico a una lista de clientes"""
        query_lower = query.lower()
        clientes_filtrados = []
        
        for cliente in clientes_lista:
            campo_valor = ""
            if tipo_filtro == "Nombre":
                campo_valor = cliente.get("nombre", "").lower()
            elif tipo_filtro == "Apellidos":
                campo_valor = cliente.get("apellidos", "").lower()
            elif tipo_filtro == "Email":
                campo_valor = cliente.get("email", "").lower()
            elif tipo_filtro == "Teléfono":
                campo_valor = str(cliente.get("telefono", "")).lower()
            
            # Si el campo contiene la búsqueda, agregarlo
            if query_lower in campo_valor:
                clientes_filtrados.append(cliente)
        
        return clientes_filtrados

    def actualizar_tabla_con_filtrados(self):
        """Actualizar tabla con clientes filtrados"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar datos filtrados
            for i, cliente in enumerate(self.clientes_filtrados):
                # Configurar tags para el estado y filas alternas
                estado_tag = "activo" if cliente["estado"] == "Activo" else "inactivo"
                row_type = "evenrow" if i % 2 == 0 else "oddrow"
                tags = (estado_tag, row_type)
                
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente["nombre"],
                        cliente["apellidos"],
                        self.format_telefono(cliente.get("telefono")),
                        cliente["estado"]
                    ),
                    tags=tags
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar tabla con filtrados: {str(e)}")

    def filtrar_localmente(self, query, tipo_filtro, estado):
        """Filtrar clientes localmente por tipo específico"""
        query_lower = query.lower()
        clientes_filtrados = []
        
        for cliente in self.clientes:
            # Aplicar filtro de estado
            if estado != "Todos" and cliente["estado"] != estado:
                continue
            
            # Aplicar filtro por tipo específico
            campo_valor = ""
            if tipo_filtro == "Nombre":
                campo_valor = cliente.get("nombre", "").lower()
            elif tipo_filtro == "Apellidos":
                campo_valor = cliente.get("apellidos", "").lower()
            elif tipo_filtro == "Email":
                campo_valor = cliente.get("email", "").lower()
            elif tipo_filtro == "Teléfono":
                campo_valor = str(cliente.get("telefono", "")).lower()
            
            # Si el campo contiene la búsqueda, agregarlo
            if query_lower in campo_valor:
                clientes_filtrados.append(cliente)
        
        # Actualizar la lista de clientes con los filtrados
        self.clientes = clientes_filtrados
        return clientes_filtrados

    def cargar_estadisticas_clientes(self):
        """Cargar estadísticas específicas de clientes"""
        try:
            from src.core.config import CLIENTS_ENDPOINTS
            from src.shared.utils import APIHandler
            
            print("Cargando estadísticas de clientes...")
            response = APIHandler.make_request('get', CLIENTS_ENDPOINTS['statistics'])
            
            # Validar que la respuesta sea válida
            if not isinstance(response, dict):
                print(f"Error: Respuesta no es un diccionario: {type(response)}")
                return {}, []
                
            if response.get('status_code') == 200:
                # Validar que data sea un diccionario
                data = response.get('data', {})
                if not isinstance(data, dict):
                    print(f"Error: response['data'] no es un diccionario: {type(data)}")
                    return {}, []
                
                stats = data.get('statistics', {})
                recent = data.get('recent_clients', [])
                
                if isinstance(stats, dict):
                    print(f"Estadísticas de clientes:")
                    print(f"- Total: {stats.get('total_clients', 0)}")
                    print(f"- Activos: {stats.get('active_clients', 0)}")
                    print(f"- Inactivos: {stats.get('inactive_clients', 0)}")
                    print(f"- Nuevos este mes: {stats.get('new_clients_this_month', 0)}")
                    
                    return stats, recent if isinstance(recent, list) else []
                else:
                    print(f"Error: stats no es un diccionario: {type(stats)}")
                    return {}, []
            else:
                error_msg = "Error desconocido"
                data = response.get('data', {})
                if isinstance(data, dict):
                    error_msg = data.get('error', error_msg)
                elif isinstance(data, str):
                    error_msg = data
                
                print(f"Error al cargar estadísticas (status {response.get('status_code')}): {error_msg}")
                return {}, []
                
        except Exception as e:
            print(f"Error al cargar estadísticas: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}, []

    def actualizar_tabla(self):
        """Actualizar solo la visualización de la tabla sin cargar datos"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar datos actuales - Solo campos necesarios
            for i, cliente in enumerate(self.clientes):
                # Configurar tags para el estado y filas alternas
                estado_tag = "activo" if cliente["estado"] == "Activo" else "inactivo"
                row_type = "evenrow" if i % 2 == 0 else "oddrow"
                tags = (estado_tag, row_type)
                
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente["nombre"],
                        cliente["apellidos"],
                        self.format_telefono(cliente.get("telefono")),
                        cliente["estado"]
                    ),
                    tags=tags
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar tabla: {str(e)}")
            
    def nuevo_cliente(self):
        try:
            # Ventana de nuevo cliente
            dialog = ClienteDialog(self, "Nuevo Cliente")
            if dialog.result:
                # Agregar nuevo cliente
                nuevo_id = max([c["id_usuario"] for c in self.clientes], default=0) + 1
                
                self.clientes.append({
                    "id_usuario": nuevo_id,
                    **dialog.result,
                    "password": self.hash_password("Temporal123*"),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "estado": "Activo",
                    "roles_id_rol": 2  # Rol por defecto
                })
                
                self.cargar_datos()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Cliente agregado correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nuevo cliente: {str(e)}")
            
    def resetear_password(self):
        """Resetear contraseña del cliente seleccionado usando la API del backend"""
        try:
            from src.core.config import CLIENTS_ENDPOINTS
            from src.shared.utils import APIHandler
            import traceback
            
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
                return
                
            # Obtener el índice de la fila seleccionada
            item_id = seleccion[0]
            children = self.tabla.get_children()
            indice_seleccionado = children.index(item_id)
            
            # Obtener el cliente directamente por índice
            if indice_seleccionado < len(self.clientes):
                cliente = self.clientes[indice_seleccionado]
            else:
                cliente = None
            
            if cliente:
                # Confirmar reseteo
                if messagebox.askyesno("Confirmar", 
                                     f"¿Está seguro de resetear la contraseña de {cliente['nombre']} {cliente['apellidos']}?\n\nSe generará una contraseña temporal: 'Temporal123*'"):
                    
                    # Preparar el endpoint con el ID del usuario
                    endpoint = CLIENTS_ENDPOINTS['reset_password'].format(id=cliente['id_usuario'])
                    
                    # Preparar datos para el request
                    payload = {
                        'new_password': 'Temporal123*',
                        'reason': f"Reset de contraseña por administrador desde la interfaz de gestión"
                    }
                    
                    print(f"Reseteando contraseña del usuario {cliente['id_usuario']}")
                    print(f"Endpoint: {endpoint}")
                    print(f"Payload: {payload}")
                    
                    # Realizar la petición al backend
                    response = APIHandler.make_request('patch', endpoint, data=payload)
                    
                    print(f"Respuesta de la API: {response}")
                    
                    # Validar que la respuesta sea válida
                    if not isinstance(response, dict):
                        print(f"Error: Respuesta no es un diccionario: {type(response)}")
                        raise Exception("Respuesta de la API no válida")
                    
                    if response.get('status_code') == 200:
                        # Obtener la nueva contraseña de la respuesta
                        data = response.get('data', {})
                        # El backend devuelve 'user' directamente en la respuesta
                        if isinstance(data, dict):
                            if 'user' in data:
                                nueva_password = data['user'].get('new_password', 'Temporal123*')
                            elif 'new_password' in data:
                                nueva_password = data.get('new_password', 'Temporal123*')
                            else:
                                nueva_password = 'Temporal123*'
                        else:
                            nueva_password = 'Temporal123*'
                        
                        # Mostrar mensaje de éxito con la nueva contraseña
                        messagebox.showinfo("Éxito", 
                                          f"Contraseña reseteada correctamente\n\nNueva contraseña temporal: {nueva_password}\n\nEl usuario deberá cambiar esta contraseña en su próximo inicio de sesión.")
                        
                        print(f"Contraseña reseteada exitosamente para el usuario {cliente['nombre']} {cliente['apellidos']}")
                        
                    else:
                        # Manejar errores del backend
                        error_msg = "Error desconocido"
                        data = response.get('data', {})
                        if isinstance(data, dict):
                            error_msg = data.get('error', error_msg)
                        elif isinstance(data, str):
                            error_msg = data
                        
                        print(f"Error al resetear contraseña (status {response.get('status_code')}): {error_msg}")
                        messagebox.showerror("Error", f"No se pudo resetear la contraseña\nError: {error_msg}")
                        
            else:
                messagebox.showerror("Error", "No se pudo encontrar la información del cliente")
                    
        except Exception as e:
            print(f"Excepción al resetear contraseña: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al resetear contraseña: {str(e)}")
            
    def cambiar_estado(self, cliente):
        """Cambiar estado del cliente usando la API del backend"""
        try:
            from src.core.config import CLIENTS_ENDPOINTS
            from src.shared.utils import APIHandler
            import traceback
            
            # Determinar el nuevo estado y el endpoint a usar
            estado_actual = cliente["estado"]
            if estado_actual == "Activo":
                nuevo_estado = "Inactivo"
                endpoint_key = 'deactivate'
                accion = "desactivar"
            else:
                nuevo_estado = "Activo"
                endpoint_key = 'reactivate'
                accion = "activar"
            
            # Confirmar cambio de estado
            if messagebox.askyesno("Confirmar", 
                                 f"¿Está seguro de {accion} la cuenta de {cliente['nombre']} {cliente['apellidos']}?"):
                
                # Preparar el endpoint con el ID del usuario
                endpoint = CLIENTS_ENDPOINTS[endpoint_key].format(id=cliente['id_usuario'])
                
                # Preparar datos para el request
                payload = {}
                if endpoint_key == 'deactivate':
                    # Para desactivar se requiere un motivo
                    payload['reason'] = f"Desactivado por administrador desde la interfaz de gestión"
                else:
                    # Para reactivar el motivo es opcional
                    payload['reason'] = f"Reactivado por administrador desde la interfaz de gestión"
                
                print(f"Cambiando estado del usuario {cliente['id_usuario']} a {nuevo_estado}")
                print(f"Endpoint: {endpoint}")
                print(f"Payload: {payload}")
                
                # Realizar la petición al backend
                response = APIHandler.make_request('patch', endpoint, data=payload)
                
                print(f"Respuesta de la API: {response}")
                
                # Validar que la respuesta sea válida
                if not isinstance(response, dict):
                    print(f"Error: Respuesta no es un diccionario: {type(response)}")
                    raise Exception("Respuesta de la API no válida")
                
                if response.get('status_code') == 200:
                    # Actualizar el estado en el cliente local
                    cliente["estado"] = nuevo_estado
                    
                    # Actualizar la tabla para reflejar los cambios
                    self.actualizar_tabla()
                    
                    # Mostrar mensaje de éxito
                    messagebox.showinfo("Éxito", f"Estado cambiado a {nuevo_estado} correctamente")
                    
                    print(f"Estado actualizado exitosamente para el usuario {cliente['nombre']} {cliente['apellidos']}")
                    
                else:
                    # Manejar errores del backend
                    error_msg = "Error desconocido"
                    data = response.get('data', {})
                    if isinstance(data, dict):
                        error_msg = data.get('error', error_msg)
                    elif isinstance(data, str):
                        error_msg = data
                    
                    print(f"Error al cambiar estado (status {response.get('status_code')}): {error_msg}")
                    messagebox.showerror("Error", f"No se pudo cambiar el estado del usuario\nError: {error_msg}")
                
        except Exception as e:
            print(f"Excepción al cambiar estado: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cambiar estado del usuario: {str(e)}")
            
    def cambiar_estado_seleccionado(self):
        """Cambiar estado del cliente seleccionado en la tabla"""
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
                return
                
            # Obtener el índice de la fila seleccionada
            item_id = seleccion[0]
            children = self.tabla.get_children()
            indice_seleccionado = children.index(item_id)
            
            # Obtener el cliente directamente por índice
            if indice_seleccionado < len(self.clientes):
                cliente = self.clientes[indice_seleccionado]
            else:
                cliente = None
            
            if cliente:
                # Llamar al método cambiar_estado existente
                self.cambiar_estado(cliente)
            else:
                messagebox.showerror("Error", "No se pudo encontrar la información del cliente")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
            
    def eliminar_cliente(self, event=None):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
                return
                
            # Obtener el índice de la fila seleccionada
            item_id = seleccion[0]
            children = self.tabla.get_children()
            indice_seleccionado = children.index(item_id)
            
            # Obtener el cliente directamente por índice
            if indice_seleccionado < len(self.clientes):
                cliente = self.clientes[indice_seleccionado]
            else:
                cliente = None
            
            if cliente:
                # Confirmar eliminación
                if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al cliente {cliente['nombre']} {cliente['apellidos']}?\n\nEsta acción no se puede deshacer."):
                    # Eliminar de la lista
                    self.clientes.remove(cliente)
                    # Actualizar tabla
                    self.actualizar_tabla()
                    # Guardar cambios
                    self.guardar_datos()
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
            else:
                messagebox.showerror("Error", "No se pudo encontrar la información del cliente")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")

    def guardar_datos(self):
        try:
            # Crear directorio si no existe
            os.makedirs("datos", exist_ok=True)
            
            # Guardar datos en archivo
            with open("datos/usuarios.json", "w", encoding="utf-8") as f:
                json.dump(self.clientes, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")

    def ver_detalles(self, event):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
                return
                
            # Obtener el índice de la fila seleccionada
            item_id = seleccion[0]
            children = self.tabla.get_children()
            indice_seleccionado = children.index(item_id)
            
            # Obtener el cliente directamente por índice
            if indice_seleccionado < len(self.clientes):
                cliente = self.clientes[indice_seleccionado]
            else:
                cliente = None
            
            if cliente:
                # Crear diálogo de detalles con diseño moderno
                dialog = DetallesClienteCompletoDialog(self, cliente)
            else:
                messagebox.showerror("Error", "No se pudo encontrar la información completa del cliente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
            
    def cambiar_estado_desde_detalles(self, cliente, ventana_detalles):
        """Cambiar estado del cliente desde la ventana de detalles"""
        try:
            self.cambiar_estado(cliente)
            # Actualizar la tabla
            self.actualizar_tabla()
            # Cerrar ventana de detalles
            ventana_detalles.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")

    def resetear_password_desde_detalles(self, cliente, ventana_detalles):
        """Resetear contraseña del cliente desde la ventana de detalles"""
        try:
            from src.core.config import CLIENTS_ENDPOINTS
            from src.shared.utils import APIHandler
            import traceback
            
            # Confirmar reseteo
            if messagebox.askyesno("Confirmar", 
                                 f"¿Está seguro de resetear la contraseña de {cliente['nombre']} {cliente['apellidos']}?\n\nSe generará una contraseña temporal: 'Temporal123*'"):
                
                # Preparar el endpoint con el ID del usuario
                endpoint = CLIENTS_ENDPOINTS['reset_password'].format(id=cliente['id_usuario'])
                
                # Preparar datos para el request
                payload = {
                    'new_password': 'Temporal123*',
                    'reason': f"Reset de contraseña por administrador desde la ventana de detalles"
                }
                
                print(f"Reseteando contraseña del usuario {cliente['id_usuario']}")
                print(f"Endpoint: {endpoint}")
                print(f"Payload: {payload}")
                
                # Realizar la petición al backend
                response = APIHandler.make_request('patch', endpoint, data=payload)
                
                print(f"Respuesta de la API: {response}")
                
                # Validar que la respuesta sea válida
                if not isinstance(response, dict):
                    print(f"Error: Respuesta no es un diccionario: {type(response)}")
                    raise Exception("Respuesta de la API no válida")
                
                if response.get('status_code') == 200:
                    # Obtener la nueva contraseña de la respuesta
                    data = response.get('data', {})
                    # El backend devuelve 'user' directamente en la respuesta
                    if isinstance(data, dict):
                        if 'user' in data:
                            nueva_password = data['user'].get('new_password', 'Temporal123*')
                        elif 'new_password' in data:
                            nueva_password = data.get('new_password', 'Temporal123*')
                        else:
                            nueva_password = 'Temporal123*'
                    else:
                        nueva_password = 'Temporal123*'
                    
                    # Mostrar mensaje de éxito con la nueva contraseña
                    messagebox.showinfo("Éxito", 
                                      f"Contraseña reseteada correctamente\n\nNueva contraseña temporal: {nueva_password}\n\nEl usuario deberá cambiar esta contraseña en su próximo inicio de sesión.")
                    
                    print(f"Contraseña reseteada exitosamente para el usuario {cliente['nombre']} {cliente['apellidos']}")
                    
                    # Cerrar ventana de detalles
                    ventana_detalles.destroy()
                    
                else:
                    # Manejar errores del backend
                    error_msg = "Error desconocido"
                    data = response.get('data', {})
                    if isinstance(data, dict):
                        error_msg = data.get('error', error_msg)
                    elif isinstance(data, str):
                        error_msg = data
                    
                    print(f"Error al resetear contraseña (status {response.get('status_code')}): {error_msg}")
                    messagebox.showerror("Error", f"No se pudo resetear la contraseña\nError: {error_msg}")
                    
        except Exception as e:
            print(f"Excepción al resetear contraseña: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al resetear contraseña: {str(e)}")

    def mostrar_historial_pedidos(self, cliente):
        try:
            # Crear ventana de diálogo
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Historial de Pedidos - {cliente['nombre']} {cliente['apellidos']}")
            dialog.geometry("800x600")
            
            # Hacer modal
            dialog.transient(self)
            dialog.grab_set()
            
            # Centrar ventana
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text=f"Historial de Pedidos de {cliente['nombre']} {cliente['apellidos']}",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Frame para tabla
            table_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
            table_frame.pack(fill="both", expand=True)
            
            # Tabla
            columns = (
                "id_pedido", "fecha", "monto_total", "estado", 
                "metodo_pago", "detalles"
            )
            
            tabla = ttk.Treeview(
                table_frame,
                columns=columns,
                show="headings",
                selectmode="browse",
                style="Treeview"
            )
            
            # Configurar columnas
            tabla.heading("id_pedido", text="ID")
            tabla.heading("fecha", text="Fecha")
            tabla.heading("monto_total", text="Monto Total")
            tabla.heading("estado", text="Estado")
            tabla.heading("metodo_pago", text="Método de Pago")
            tabla.heading("detalles", text="Detalles")
            
            # Configurar anchos
            tabla.column("id_pedido", width=50, anchor="center")
            tabla.column("fecha", width=150, anchor="center")
            tabla.column("monto_total", width=100, anchor="center")
            tabla.column("estado", width=100, anchor="center")
            tabla.column("metodo_pago", width=120, anchor="center")
            tabla.column("detalles", width=200)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(
                table_frame,
                orient="vertical",
                command=tabla.yview
            )
            tabla.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar tabla y scrollbar
            tabla.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # Cargar datos de ejemplo (esto debería reemplazarse con datos reales de la base de datos)
            pedidos_ejemplo = [
                {
                    "id_pedido": 1,
                    "fecha": "2024-03-15 10:00:00",
                    "monto_total": 150.00,
                    "estado": "Entregado",
                    "metodo_pago": "Tarjeta",
                    "detalles": "3 productos"
                },
                {
                    "id_pedido": 2,
                    "fecha": "2024-03-14 15:30:00",
                    "monto_total": 75.50,
                    "estado": "En Proceso",
                    "metodo_pago": "Efectivo",
                    "detalles": "2 productos"
                }
            ]
            
            # Cargar datos en la tabla
            for pedido in pedidos_ejemplo:
                # Configurar tags para el estado
                tags = (pedido["estado"].lower().replace(" ", "_"),)
                
                tabla.insert(
                    "",
                    "end",
                    values=(
                        pedido["id_pedido"],
                        pedido["fecha"],
                        f"S/. {pedido['monto_total']:.2f}",
                        pedido["estado"],
                        pedido["metodo_pago"],
                        pedido["detalles"]
                    ),
                    tags=tags
                )
            
            # Configurar colores de estado
            tabla.tag_configure("pendiente", foreground="#FFA000")
            tabla.tag_configure("en_proceso", foreground="#1976D2")
            tabla.tag_configure("enviado", foreground="#7B1FA2")
            tabla.tag_configure("entregado", foreground="#2E7D32")
            tabla.tag_configure("cancelado", foreground="#C62828")
            
            # Botón cerrar
            ctk.CTkButton(
                main_frame,
                text="Cerrar",
                command=dialog.destroy,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=100
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar historial de pedidos: {str(e)}")
    
    def ver_historial_pedidos_cliente(self, cliente):
        """Navegar a la gestión de pedidos filtrada por cliente"""
        try:
            if self.dashboard:
                # Cerrar cualquier diálogo abierto
                for child in self.winfo_children():
                    if isinstance(child, ctk.CTkToplevel):
                        child.destroy()
                
                # Navegar a pedidos con filtro de cliente
                self.dashboard.mostrar_pedidos_cliente(cliente)
            else:
                messagebox.showwarning(
                    "Funcionalidad no disponible",
                    "No se puede navegar al historial de pedidos desde este contexto."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir historial de pedidos: {str(e)}")

class ClienteDialog:
    def __init__(self, parent, title, cliente=None):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("400x620") 
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
                ("Nombre", "nombre"),
                ("Apellidos", "apellidos"),
                ("Email", "email"),
                ("Teléfono", "telefono")
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
                
                # Valor inicial si es edición
                if cliente:
                    entry.insert(0, cliente[field])
                    
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
            
    def guardar(self):
        try:
            # Validar campos
            datos = {}
            for field, entry in self.entries.items():
                valor = entry.get().strip()
                if not valor:
                    messagebox.showwarning("Advertencia", f"El campo {field} es requerido")
                    return
                datos[field] = valor
                
            # Validar email
            if "@" not in datos["email"] or "." not in datos["email"]:
                messagebox.showwarning("Advertencia", "El email no es válido")
                return
                
            # Validar teléfono
            if not datos["telefono"].isdigit() or len(datos["telefono"]) < 9:
                messagebox.showwarning("Advertencia", "El teléfono debe contener al menos 9 dígitos")
                return
                
            # Guardar resultado
            self.result = datos
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class DetallesClienteDialog:
    def __init__(self, parent, cliente):
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(f"Detalles del Cliente")
            self.dialog.geometry("500x500")
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
                text="Detalles del Cliente",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Información del cliente
            campos = [
                ("Nombre", "nombre"),
                ("Apellidos", "apellidos"),
                ("Email", "email"),
                ("Teléfono", "telefono"),
                ("Estado", "estado")
            ]
            
            for label, field in campos:
                frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5")
                frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(
                    frame,
                    text=f"{label}:",
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C",
                    width=100
                ).pack(side="left", padx=10)
                
                ctk.CTkLabel(
                    frame,
                    text=str(cliente[field]),
                    font=("Quicksand", 12),
                    text_color="#424242"
                ).pack(side="left", padx=10)
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            action_frame.pack(fill="x", pady=20)
            
            # Botón cambiar estado
            self.estado_btn = ctk.CTkButton(
                action_frame,
                text=f"Cambiar a {'Inactivo' if cliente['estado'] == 'Activo' else 'Activo'}",
                command=lambda: self.cambiar_estado(cliente),
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=200
            )
            self.estado_btn.pack(side="left", padx=5)
            
            # Botón resetear contraseña
            ctk.CTkButton(
                action_frame,
                text="Resetear Contraseña",
                command=lambda: self.resetear_password(cliente),
                fg_color="#FFA000",
                hover_color="#F57C00",
                width=150
            ).pack(side="left", padx=5)
            
            # Botón cerrar
            ctk.CTkButton(
                action_frame,
                text="Cerrar",
                command=self.dialog.destroy,
                fg_color="#757575",
                hover_color="#616161",
                width=100
            ).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
            self.dialog.destroy()
            
    def cambiar_estado(self, cliente):
        try:
            # Obtener referencia al frame padre
            parent = self.dialog.master
            
            # Llamar al método cambiar_estado del frame padre
            parent.cambiar_estado(cliente)
            
            # Actualizar el texto del botón
            nuevo_estado = "Inactivo" if cliente["estado"] == "Activo" else "Activo"
            self.estado_btn.configure(text=f"Cambiar a {nuevo_estado}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
            
    def resetear_password(self, cliente):
        try:
            # Obtener referencia al frame padre
            parent = self.dialog.master
            
            # Llamar al método resetear_password del frame padre
            parent.resetear_password()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al resetear contraseña: {str(e)}")
    
    def ver_historial_pedidos_cliente_desde_dialog(self, cliente):
        """Ver historial de pedidos del cliente desde el diálogo de detalles"""
        try:
            # Cerrar este diálogo y llamar al método del padre
            self.safe_close()
            self.parent.ver_historial_pedidos_cliente(cliente)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir historial de pedidos: {str(e)}")

# --- CLASES DE DIÁLOGO ---
class DetallesClienteCompletoDialog:
    """Diálogo mejorado para mostrar detalles completos de un cliente con diseño moderno"""
    
    def __init__(self, parent, cliente):
        self.dialog = None
        self.closed = False
        self.cliente = cliente
        self.parent = parent  # Este es el objeto GestionClientes
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("Cliente")
            self.dialog.geometry("750x600")  # Aumentado de 750x400 a 750x700
            self.dialog.resizable(True, True)
            self.dialog.minsize(650, 600)  # Aumentado el mínimo también

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

            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#F5F5F5")
            main_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Título principal compacto
            header_frame = ctk.CTkFrame(main_frame, fg_color="#2E6B5C", corner_radius=10)
            header_frame.pack(fill="x", padx=10, pady=(5, 8))
            
            ctk.CTkLabel(
                header_frame,
                text="👤 Cliente",
                font=("Quicksand", 16, "bold"),
                text_color="#FFFFFF"
            ).pack(pady=8)
            
            # SECCIÓN 1: CARDS DE INFORMACIÓN (2 columnas)
            self.crear_cards_cliente(main_frame, cliente)
            
            # SECCIÓN 2: INFORMACIÓN DETALLADA
            self.crear_seccion_detallada(main_frame, cliente)
            
            # SECCIÓN 3: BOTONES DE ACCIÓN
            self.crear_botones_accion(main_frame, cliente)

        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
            self.safe_close()
    
    def safe_close(self):
        """Cierre seguro del diálogo"""
        if self.closed:
            return
            
        self.closed = True
        try:
            if hasattr(self, 'dialog') and self.dialog:
                try:
                    if self.dialog.winfo_exists():
                        self.dialog.grab_release()
                        self.dialog.destroy()
                except:
                    pass
                self.dialog = None
        except Exception as e:
            print(f"Error al cerrar diálogo: {e}")
    
    def __del__(self):
        """Destructor para limpieza de recursos"""
        try:
            self.safe_close()
        except Exception:
            pass
    
    def crear_cards_cliente(self, parent, cliente):
        """Crear cards de información del cliente"""
        try:
            cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
            cards_frame.pack(fill="x", padx=10, pady=5)
            
            # CARD 1: Información Personal
            card_personal = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=10)
            card_personal.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            ctk.CTkLabel(
                card_personal,
                text="👤 INFORMACIÓN PERSONAL",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(15, 5))
            
            # Nombre completo
            nombre_completo = f"{cliente.get('nombre', '')} {cliente.get('apellidos', '')}".strip()
            ctk.CTkLabel(
                card_personal,
                text=nombre_completo if nombre_completo else "Sin nombre",
                font=("Quicksand", 14, "bold"),
                text_color="#000000"
            ).pack(pady=2)
            
            # Email
            ctk.CTkLabel(
                card_personal,
                text=cliente.get('email', 'No registrado'),
                font=("Quicksand", 12),
                text_color="#666666"
            ).pack(pady=2)
            
            # Teléfono
            ctk.CTkLabel(
                card_personal,
                text=f"Tel: {cliente.get('telefono', 'No registrado')}",
                font=("Quicksand", 12),
                text_color="#666666"
            ).pack(pady=(2, 15))
            
            # CARD 2: Estado y Acciones
            card_estado = ctk.CTkFrame(cards_frame, fg_color="#FFFFFF", corner_radius=10)
            card_estado.pack(side="left", fill="both", expand=True, padx=(5, 0))
            
            ctk.CTkLabel(
                card_estado,
                text="📊 ESTADO Y ACCIONES",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(15, 5))
            
            # Estado actual
            estado = cliente.get('estado', 'Desconocido')
            estado_color = self.obtener_color_estado(estado)
            ctk.CTkLabel(
                card_estado,
                text=estado.upper(),
                font=("Quicksand", 14, "bold"),
                text_color=estado_color
            ).pack(pady=2)
            
            # Fecha de registro (si está disponible)
            if 'fecha_registro' in cliente:
                ctk.CTkLabel(
                    card_estado,
                    text=f"Registrado: {cliente['fecha_registro']}",
                    font=("Quicksand", 10),
                    text_color="#666666"
                ).pack(pady=2)
            
            # Botón de acción rápida
            accion_texto = "Activar" if estado.lower() == "inactivo" else "Desactivar"
            accion_color = "#4CAF50" if estado.lower() == "inactivo" else "#F44336"
            hover_color = "#45A049" if estado.lower() == "inactivo" else "#DA190B"
            
            accion_btn = ctk.CTkButton(
                card_estado,
                text=accion_texto,
                font=("Quicksand", 12, "bold"),
                fg_color=accion_color,
                hover_color=hover_color,
                height=25,
                width=80,
                command=lambda: self.cambiar_estado_rapido()
            )
            accion_btn.pack(pady=(5, 15))
            
        except Exception as e:
            print(f"Error al crear cards de cliente: {str(e)}")
    
    def crear_seccion_detallada(self, parent, cliente):
        """Crear sección con información detallada del cliente"""
        try:
            detalle_frame = ctk.CTkFrame(parent, fg_color="transparent")
            detalle_frame.pack(fill="x", padx=10, pady=5)
            
            left_frame = ctk.CTkFrame(detalle_frame, fg_color="#FFFFFF", corner_radius=10)
            left_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(
                left_frame,
                text="📋 Información Detallada",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(10, 8))
            
            # Información del cliente
            cliente_info = [
                ("Nombre:", cliente.get('nombre', 'No registrado')),
                ("Apellidos:", cliente.get('apellidos', 'No registrado')),
                ("Email:", cliente.get('email', 'No registrado')),
                ("Teléfono:", cliente.get('telefono', 'No registrado')),
                ("Estado:", cliente.get('estado', 'Desconocido')),
            ]
            
            # Agregar información adicional si está disponible
            if 'fecha_registro' in cliente:
                cliente_info.append(("Fecha de registro:", cliente['fecha_registro']))
            if 'ultimo_acceso' in cliente:
                cliente_info.append(("Último acceso:", cliente['ultimo_acceso']))
            
            self.crear_lista_info_compacta(left_frame, cliente_info)
            
        except Exception as e:
            print(f"Error al crear sección detallada: {str(e)}")
    
    def crear_botones_accion(self, parent, cliente):
        """Crear botones de acción"""
        try:
            botones_frame = ctk.CTkFrame(parent, fg_color="transparent")
            botones_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            # Frame para los botones
            button_container = ctk.CTkFrame(botones_frame, fg_color="#FFFFFF", corner_radius=10)
            button_container.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                button_container,
                text="⚙️ Acciones",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(10, 5))
            
            # Frame para organizar botones
            buttons_frame = ctk.CTkFrame(button_container, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            # Botón Ver Historial de Pedidos
            historial_btn = ctk.CTkButton(
                buttons_frame,
                text="Ver Historial de Pedidos",
                font=("Quicksand", 12, "bold"),
                fg_color="#1976D2",
                hover_color="#1565C0",
                height=35,
                state="normal",
                command=lambda: self.ver_historial_pedidos_cliente_desde_dialog(cliente)
            )
            historial_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            # Botón Resetear Contraseña
            reset_btn = ctk.CTkButton(
                buttons_frame,
                text="Resetear Contraseña",
                font=("Quicksand", 12, "bold"),
                fg_color="#FFA000",
                hover_color="#F57C00",
                height=35,
                command=lambda: self.resetear_password()
            )
            reset_btn.pack(side="left", fill="x", expand=True, padx=5)
            
            # Botón Cerrar
            cerrar_btn = ctk.CTkButton(
                buttons_frame,
                text="Cerrar",
                font=("Quicksand", 12, "bold"),
                fg_color="#757575",
                hover_color="#616161",
                height=35,
                command=self.safe_close
            )
            cerrar_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
            
        except Exception as e:
            print(f"Error al crear botones de acción: {str(e)}")
    
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
        """Obtener color según el estado del cliente"""
        colors = {
            'activo': '#4CAF50',
            'inactivo': '#F44336',
            'pendiente': '#FFA000',
            'bloqueado': '#9E9E9E'
        }
        return colors.get(estado.lower(), '#666666')
    
    def cambiar_estado_rapido(self):
        """Cambiar estado del cliente rápidamente"""
        try:
            # Cerrar este diálogo y llamar al método del padre
            self.safe_close()
            self.parent.cambiar_estado_desde_detalles(self.cliente, None)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
    
    def cambiar_estado_completo(self):
        """Cambiar estado del cliente con opciones completas"""
        try:
                       # Cerrar este diálogo y llamar al método del padre
            self.safe_close()
            self.parent.cambiar_estado_desde_detalles(self.cliente, None)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
    
    def resetear_password(self):
        """Resetear contraseña del cliente"""
        try:
            # Cerrar este diálogo y llamar al método del padre
            self.safe_close()
            self.parent.resetear_password_desde_detalles(self.cliente, None)
        except Exception as e:
            messagebox.showerror("Error", f"Error al resetear contraseña: {str(e)}")
    
    def ver_historial_pedidos_cliente_desde_dialog(self, cliente):
        """Ver historial de pedidos del cliente desde el diálogo de detalles"""
        try:
            # Cerrar este diálogo y llamar al método del padre
            self.safe_close()
            self.parent.ver_historial_pedidos_cliente(cliente)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir historial de pedidos: {str(e)}")
