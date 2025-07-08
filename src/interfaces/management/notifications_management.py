import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
from src.shared.image_handler import ImageHandler
from src.services.notifications_service import NotificationsService

class GestionNotificaciones(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Lista de notificaciones
            self.notificaciones = []
            self.usuarios = []
            
            # Frame superior
            top_frame = ctk.CTkFrame(self, fg_color="transparent")
            top_frame.pack(fill="x", pady=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            title_frame.pack(side="left")
            
            # Cargar y mostrar icono
            icon = self.image_handler.load_image("notificaciones.png", (32, 32))
            if icon:
                ctk.CTkLabel(
                    title_frame,
                    image=icon,
                    text=""
                ).pack(side="left", padx=(0, 10))
                
            ctk.CTkLabel(
                title_frame,
                text="Gestión de Notificaciones",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left")
            
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
                placeholder_text="Buscar por contenido...",
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
                values=["Todos", "Pendiente", "Leído", "Enviado"],
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
            
            # Botones de acción
            action_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
            action_frame.pack(side="right", padx=15)
            
            # Botón enviar notificación
            ctk.CTkButton(
                action_frame,
                text="📤 Enviar Notificación",
                command=self.enviar_notificacion,
                fg_color="#FF6B35",
                hover_color="#E55A2B",
                width=160,
                font=("Quicksand", 12, "bold")
            ).pack(side="left", padx=5)
            
            # Botón nueva notificación
            ctk.CTkButton(
                action_frame,
                text="➕ Nueva Notificación",
                command=self.nueva_notificacion,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150
            ).pack(side="left", padx=5)
            
            # Botón refrescar
            ctk.CTkButton(
                action_frame,
                text="🔄 Refrescar",
                command=self.cargar_datos_desde_api,
                fg_color="#367832",
                hover_color="#2D5A27",
                width=120
            ).pack(side="left", padx=5)
            
            # Contador de notificaciones y estadísticas
            stats_frame = ctk.CTkFrame(action_frame, fg_color="#E8F5E8", corner_radius=8)
            stats_frame.pack(side="left", padx=15)
            
            self.contador_label = ctk.CTkLabel(
                stats_frame,
                text="Total: 0 | No leídas: 0",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            )
            self.contador_label.pack(padx=10, pady=5)
            
            # Botón estadísticas
            ctk.CTkButton(
                action_frame,
                text="📊 Estadísticas",
                command=self.mostrar_estadisticas,
                fg_color="#17a2b8",
                hover_color="#138496",
                width=120
            ).pack(side="right", padx=5)
            
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
                "id", "tipo", "contenido", "estado", 
                "fecha", "usuario"
            )
            
            self.tabla = ttk.Treeview(
                table_frame,
                columns=columns,
                show="headings",
                selectmode="browse",
                style="Treeview"
            )
            
            # Configurar columnas
            self.tabla.heading("id", text="ID")
            self.tabla.heading("tipo", text="Tipo")
            self.tabla.heading("contenido", text="Contenido")
            self.tabla.heading("estado", text="Estado")
            self.tabla.heading("fecha", text="Fecha")
            self.tabla.heading("usuario", text="Usuario")
            
            # Configurar anchos
            self.tabla.column("id", width=50, anchor="center")
            self.tabla.column("tipo", width=100, anchor="center")
            self.tabla.column("contenido", width=300)
            self.tabla.column("estado", width=100, anchor="center")
            self.tabla.column("fecha", width=150, anchor="center")
            self.tabla.column("usuario", width=150, anchor="center")
            
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
            
            # Cargar datos desde la API
            self.cargar_datos_desde_api()
            
            # Bind doble clic
            self.tabla.bind("<Double-1>", self.ver_detalles)
            
            # Bind tecla Enter
            self.tabla.bind("<Return>", self.ver_detalles)
            
            # Bind tecla Delete
            self.tabla.bind("<Delete>", self.eliminar_notificacion)
            
            # Bind clic derecho para menú contextual
            self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
            
            # Crear menú contextual
            self.crear_menu_contextual()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar: {str(e)}")
            
    def cargar_datos_desde_api(self):
        """Cargar notificaciones desde la API"""
        try:
            # Mostrar indicador de carga
            self.mostrar_loading(True)
            
            # Obtener notificaciones de la API
            result = NotificationsService.get_all_notifications()
            
            if result['success']:
                self.notificaciones = result['notifications']
                print(f"✅ {len(self.notificaciones)} notificaciones cargadas correctamente")
            else:
                messagebox.showerror("Error", f"Error al cargar notificaciones: {result['error']}")
                # Usar datos vacíos si hay error
                self.notificaciones = []
            
            # Cargar lista de usuarios también
            users_result = NotificationsService.get_users_list()
            if users_result['success']:
                self.usuarios = users_result['users']
            else:
                print(f"Advertencia: No se pudieron cargar usuarios: {users_result['error']}")
                self.usuarios = []
            
            # Actualizar la tabla
            self.cargar_datos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con la API: {str(e)}")
            self.notificaciones = []
        finally:
            self.mostrar_loading(False)
    
    def mostrar_loading(self, show):
        """Mostrar u ocultar indicador de carga"""
        try:
            if show:
                # Crear overlay de carga si no existe
                if not hasattr(self, 'loading_frame'):
                    self.loading_frame = ctk.CTkFrame(self, fg_color="rgba(0,0,0,0.5)")
                    self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
                    
                    ctk.CTkLabel(
                        self.loading_frame,
                        text="⏳ Cargando datos...",
                        font=("Quicksand", 16, "bold"),
                        text_color="#FFFFFF"
                    ).place(relx=0.5, rely=0.5, anchor="center")
                
                self.loading_frame.lift()
            else:
                # Ocultar overlay de carga
                if hasattr(self, 'loading_frame'):
                    self.loading_frame.place_forget()
        except Exception as e:
            print(f"Error en loading: {e}")
        
    def cargar_datos(self):
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar datos
            for notif in self.notificaciones:
                # Configurar tags para el estado
                tags = ("leida" if notif["estado"] == "Leído" else "no_leida",)
                
                # Truncar contenido si es muy largo
                contenido = notif["contenido"]
                if len(contenido) > 80:
                    contenido = contenido[:77] + "..."
                
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        notif["id"],
                        notif["tipo"],
                        contenido,
                        notif["estado"],
                        notif["fecha"],
                        notif["usuario"]
                    ),
                    tags=tags
                )
                
            # Configurar colores de estado
            self.tabla.tag_configure("leida", foreground="#757575")
            self.tabla.tag_configure("no_leida", foreground="#2E6B5C", font=("Quicksand", 10, "bold"))
            
            # Actualizar contador
            total = len(self.notificaciones)
            no_leidas = len([n for n in self.notificaciones if n["estado"] != "Leído"])
            self.actualizar_contador(total, no_leidas)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def actualizar_contador(self, total, no_leidas):
        """Actualizar contador de notificaciones"""
        try:
            if not hasattr(self, 'contador_label'):
                return
            
            texto = f"Total: {total} | No leídas: {no_leidas}"
            self.contador_label.configure(text=texto)
        except Exception as e:
            print(f"Error actualizando contador: {e}")
    
    def mostrar_estadisticas(self):
        """Mostrar diálogo con estadísticas de notificaciones"""
        try:
            EstadisticasDialog(self, self.notificaciones, self.usuarios)
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar estadísticas: {str(e)}")
    
    def crear_menu_contextual(self):
        """Crear menú contextual para la tabla"""
        import tkinter as tk
        
        self.menu_contextual = tk.Menu(self, tearoff=0)
        self.menu_contextual.add_command(
            label="👁️ Ver Detalles",
            command=lambda: self.ver_detalles(None)
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="🗑️ Eliminar",
            command=lambda: self.eliminar_notificacion(None)
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="🔄 Refrescar",
            command=self.cargar_datos_desde_api
        )
    
    def mostrar_menu_contextual(self, event):
        """Mostrar menú contextual en la posición del cursor"""
        try:
            # Seleccionar el item bajo el cursor
            item = self.tabla.identify_row(event.y)
            if item:
                self.tabla.selection_set(item)
                self.tabla.focus(item)
                
                # Mostrar menú
                self.menu_contextual.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error al mostrar menú contextual: {e}")
            
    def filtrar_tabla(self, *args):
        try:
            # Obtener valores de filtro
            busqueda = self.search_var.get().lower()
            estado = self.estado_var.get()
            
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Filtrar y cargar datos
            for notif in self.notificaciones:
                # Aplicar filtros
                if estado != "Todos" and notif["estado"] != estado:
                    continue
                    
                if busqueda and not any(
                    busqueda in str(valor).lower()
                    for valor in [
                        str(notif["id"]),
                        notif["contenido"],
                        notif["tipo"]
                    ]
                ):
                    continue
                    
                # Configurar tags para el estado
                tags = ("leida" if notif["estado"] == "Leído" else "no_leida",)
                
                # Insertar fila
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        notif["id"],
                        notif["tipo"],
                        notif["contenido"],
                        notif["estado"],
                        notif["fecha"],
                        notif["usuario"]
                    ),
                    tags=tags
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar datos: {str(e)}")
            
    def enviar_notificacion(self):
        """
        Método específico para el botón 'Enviar Notificación' con UI optimizada
        """
        try:
            # Ventana de envío de notificación
            dialog = NotificacionDialog(self, "Enviar Notificación", self.usuarios)
            if dialog.result:
                # Mostrar indicador de carga
                self.mostrar_loading(True)
                
                # Enviar notificación a través de la API
                if dialog.result['tipo_envio'] == 'usuario_especifico':
                    # Envío a usuario específico (campanita + email)
                    result = NotificationsService.send_notification_to_user(
                        user_id=dialog.result['usuario_id'],
                        asunto=dialog.result['asunto'],
                        contenido=dialog.result['contenido'],
                        tipo='campanita_email',
                        prioridad=dialog.result.get('prioridad', 'normal')
                    )
                else:
                    # Envío masivo (solo campanita)
                    result = NotificationsService.send_notification_to_all_users(
                        asunto=dialog.result['asunto'],
                        contenido=dialog.result['contenido'],
                        prioridad=dialog.result.get('prioridad', 'normal')
                    )
                
                if result['success']:
                    messagebox.showinfo("Éxito", f"Notificación enviada exitosamente: {result['message']}")
                    # Recargar datos
                    self.cargar_datos_desde_api()
                else:
                    messagebox.showerror("Error", f"Error al enviar notificación: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar notificación: {str(e)}")
        finally:
            self.mostrar_loading(False)
            
    def nueva_notificacion(self):
        try:
            # Ventana de nueva notificación
            dialog = NotificacionDialog(self, "Nueva Notificación", self.usuarios)
            if dialog.result:
                # Mostrar indicador de carga
                self.mostrar_loading(True)
                
                # Enviar notificación a través de la API
                if dialog.result['tipo_envio'] == 'usuario_especifico':
                    # Envío a usuario específico (campanita + email)
                    result = NotificationsService.send_notification_to_user(
                        user_id=dialog.result['usuario_id'],
                        asunto=dialog.result['asunto'],
                        contenido=dialog.result['contenido'],
                        tipo='campanita_email',
                        prioridad=dialog.result.get('prioridad', 'normal')
                    )
                else:
                    # Envío masivo (solo campanita)
                    result = NotificationsService.send_notification_to_all_users(
                        asunto=dialog.result['asunto'],
                        contenido=dialog.result['contenido'],
                        prioridad=dialog.result.get('prioridad', 'normal')
                    )
                
                if result['success']:
                    messagebox.showinfo("Éxito", result['message'])
                    # Recargar datos
                    self.cargar_datos_desde_api()
                else:
                    messagebox.showerror("Error", f"Error al enviar notificación: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nueva notificación: {str(e)}")
        finally:
            self.mostrar_loading(False)
            
    def eliminar_notificacion(self, event=None):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione una notificación")
                return
                
            # Obtener notificación seleccionada
            item = self.tabla.item(seleccion[0])
            notif_id = item["values"][0]
            
            # Confirmar eliminación
            if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la notificación #{notif_id}?"):
                # Mostrar indicador de carga
                self.mostrar_loading(True)
                
                # Eliminar a través de la API
                result = NotificationsService.delete_notification(notif_id)
                
                if result['success']:
                    messagebox.showinfo("Éxito", result['message'])
                    # Recargar datos
                    self.cargar_datos_desde_api()
                else:
                    messagebox.showerror("Error", f"Error al eliminar: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar notificación: {str(e)}")
        finally:
            self.mostrar_loading(False)
            
    def ver_detalles(self, event):
        try:
            # Obtener item seleccionado
            item = self.tabla.selection()[0]
            notif_id = self.tabla.item(item)["values"][0]
            notif = next((n for n in self.notificaciones if n["id"] == notif_id), None)
            
            if notif:
                # Mostrar detalles
                DetallesNotificacionDialog(self, notif)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")

class NotificacionDialog:
    def __init__(self, parent, title, usuarios):
        try:
            self.result = None
            self.usuarios = usuarios
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("650x800")  # Aumentamos la altura
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
            
            # Frame principal con sombra
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF", corner_radius=15)
            main_frame.pack(fill="both", expand=True, padx=30, pady=30)
            
            # Título con icono
            title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(20, 20))
            
            ctk.CTkLabel(
                title_frame,
                text="📝 " + title,
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack()
            
            # Frame scrollable para el formulario
            self.form_scroll_frame = ctk.CTkScrollableFrame(
                main_frame, 
                fg_color="transparent",
                height=400  # Altura fija para permitir scroll
            )
            self.form_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Tipo de envío
            self.crear_campo_tipo_envio(self.form_scroll_frame)
            
            # Asunto
            self.crear_campo_asunto(self.form_scroll_frame)
            
            # Contenido
            self.crear_campo_contenido(self.form_scroll_frame)
            
            # Selector de usuario (solo visible para envío específico)
            self.crear_campo_usuario(self.form_scroll_frame)
            
            # Prioridad
            self.crear_campo_prioridad(self.form_scroll_frame)
            
            # Aplicar configuración inicial de visibilidad
            self.on_tipo_envio_change()
            
            # Frame para botones (SIEMPRE VISIBLE en la parte inferior)
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(side="bottom", fill="x", pady=(10, 20))
            
            # Botón Enviar
            guardar_btn = ctk.CTkButton(
                button_frame,
                text="📤 Enviar Notificación",
                command=self.enviar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=200,
                height=45,
                font=("Quicksand", 14, "bold"),
                corner_radius=10
            )
            guardar_btn.pack(side="left", padx=10)
            
            # Botón Cancelar
            cancelar_btn = ctk.CTkButton(
                button_frame,
                text="❌ Cancelar",
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=200,
                height=45,
                font=("Quicksand", 14, "bold"),
                corner_radius=10
            )
            cancelar_btn.pack(side="right", padx=10)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
    
    def crear_campo_tipo_envio(self, parent):
        """Crear campo para seleccionar tipo de envío"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            field_frame,
            text="🎯 Tipo de Envío",
            font=("Quicksand", 14, "bold"),
            text_color="#2E6B5C"
        ).pack(anchor="w", pady=(0, 5))
        
        self.tipo_envio_var = ctk.StringVar(value="usuario_especifico")
        
        # Radio buttons para tipo de envío
        radio_frame = ctk.CTkFrame(field_frame, fg_color="#F5F5F5", corner_radius=10)
        radio_frame.pack(fill="x", pady=5)
        
        ctk.CTkRadioButton(
            radio_frame,
            text="👤 Usuario Específico (Email + Campanita)",
            variable=self.tipo_envio_var,
            value="usuario_especifico",
            command=self.on_tipo_envio_change,
            font=("Quicksand", 12),
            text_color="#2E6B5C"
        ).pack(anchor="w", padx=15, pady=10)
        
        ctk.CTkRadioButton(
            radio_frame,
            text="📢 Todos los Usuarios (Solo Campanita)",
            variable=self.tipo_envio_var,
            value="todos_usuarios",
            command=self.on_tipo_envio_change,
            font=("Quicksand", 12),
            text_color="#2E6B5C"
        ).pack(anchor="w", padx=15, pady=(0, 10))
    
    def crear_campo_asunto(self, parent):
        """Crear campo para asunto"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            field_frame,
            text="📧 Asunto",
            font=("Quicksand", 14, "bold"),
            text_color="#2E6B5C"
        ).pack(anchor="w", pady=(0, 5))
        
        self.asunto_entry = ctk.CTkEntry(
            field_frame,
            width=400,
            height=40,
            placeholder_text="Ingrese el asunto de la notificación...",
            border_width=0,
            fg_color="#F5F5F5",
            font=("Quicksand", 12)
        )
        self.asunto_entry.pack(fill="x")
    
    def crear_campo_contenido(self, parent):
        """Crear campo para contenido"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            field_frame,
            text="💬 Contenido del Mensaje",
            font=("Quicksand", 14, "bold"),
            text_color="#2E6B5C"
        ).pack(anchor="w", pady=(0, 5))
        
        self.contenido_text = ctk.CTkTextbox(
            field_frame,
            width=400,
            height=120,
            border_width=0,
            fg_color="#F5F5F5",
            font=("Quicksand", 12)
        )
        self.contenido_text.pack(fill="x")
        self.contenido_text.insert("1.0", "Escriba aquí el contenido de la notificación...")
    
    def crear_campo_usuario(self, parent):
        """Crear campo para seleccionar usuario"""
        self.usuario_frame = ctk.CTkFrame(parent, fg_color="transparent")
        # NO hacer pack aquí, se controlará desde on_tipo_envio_change
        
        ctk.CTkLabel(
            self.usuario_frame,
            text="👤 Seleccionar Usuario",
            font=("Quicksand", 14, "bold"),
            text_color="#2E6B5C"
        ).pack(anchor="w", pady=(0, 5))
        
        # Combo box para usuarios
        usuario_values = ["Seleccionar usuario..."]
        if self.usuarios:
            usuario_values.extend([f"{u['nombre']} ({u['email']})" for u in self.usuarios])
        else:
            usuario_values.append("No hay usuarios disponibles")
        
        self.usuario_var = ctk.StringVar(value=usuario_values[0])
        self.usuario_combo = ctk.CTkOptionMenu(
            self.usuario_frame,
            values=usuario_values,
            variable=self.usuario_var,
            width=400,
            height=40,
            fg_color="#2E6B5C",
            button_color="#1D4A3C",
            button_hover_color="#153A2C",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F5F5F5",
            dropdown_text_color="#2E6B5C",
            font=("Quicksand", 12)
        )
        self.usuario_combo.pack(fill="x")
        
        # Contador de usuarios
        if self.usuarios:
            ctk.CTkLabel(
                self.usuario_frame,
                text=f"👥 {len(self.usuarios)} usuarios disponibles",
                font=("Quicksand", 10),
                text_color="#757575"
            ).pack(anchor="w", pady=(5, 0))
        
        # Guardar referencia al parent para reposicionamiento
        self.usuario_parent = parent
    
    def crear_campo_prioridad(self, parent):
        """Crear campo para prioridad"""
        self.prioridad_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.prioridad_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            self.prioridad_frame,
            text="⚡ Prioridad",
            font=("Quicksand", 14, "bold"),
            text_color="#2E6B5C"
        ).pack(anchor="w", pady=(0, 5))
        
        self.prioridad_var = ctk.StringVar(value="normal")
        prioridad_combo = ctk.CTkOptionMenu(
            self.prioridad_frame,
            values=["baja", "normal", "alta", "urgente"],
            variable=self.prioridad_var,
            width=200,
            height=40,
            fg_color="#2E6B5C",
            button_color="#1D4A3C",
            button_hover_color="#153A2C",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F5F5F5",
            dropdown_text_color="#2E6B5C",
            font=("Quicksand", 12)
        )
        prioridad_combo.pack(anchor="w")
    
    def on_tipo_envio_change(self):
        """Manejar cambio en tipo de envío"""
        if self.tipo_envio_var.get() == "usuario_especifico":
            # Mostrar campo de usuario
            self.usuario_frame.pack(fill="x", pady=(0, 20), before=self.prioridad_frame)
        else:
            # Ocultar campo de usuario
            self.usuario_frame.pack_forget()
    
    def enviar(self):
        try:
            # Validar campos
            asunto = self.asunto_entry.get().strip()
            if not asunto:
                messagebox.showwarning("Advertencia", "El asunto es requerido")
                return
            
            contenido = self.contenido_text.get("1.0", "end-1c").strip()
            if not contenido or contenido == "Escriba aquí el contenido de la notificación...":
                messagebox.showwarning("Advertencia", "El contenido es requerido")
                return
            
            # Preparar datos
            datos = {
                'tipo_envio': self.tipo_envio_var.get(),
                'asunto': asunto,
                'contenido': contenido,
                'prioridad': self.prioridad_var.get()
            }
            
            # Validar usuario si es envío específico
            if self.tipo_envio_var.get() == "usuario_especifico":
                usuario_seleccionado = self.usuario_var.get()
                if usuario_seleccionado == "Seleccionar usuario..." or not usuario_seleccionado:
                    messagebox.showwarning("Advertencia", "Debe seleccionar un usuario")
                    return
                
                # Encontrar ID del usuario
                usuario_id = None
                for usuario in self.usuarios:
                    if f"{usuario['nombre']} ({usuario['email']})" == usuario_seleccionado:
                        usuario_id = usuario['id']
                        break
                
                if not usuario_id:
                    messagebox.showerror("Error", "Usuario no encontrado")
                    return
                
                datos['usuario_id'] = usuario_id
            
            # Guardar resultado
            self.result = datos
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al preparar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class DetallesNotificacionDialog:
    def __init__(self, parent, notif):
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(f"Detalles de la Notificación #{notif['id']}")
            self.dialog.geometry("600x500")
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
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF", corner_radius=15)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título con icono
            title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(20, 30))
            
            # Icono de estado
            estado_icon = "✅" if notif["estado"] == "Leído" else "📬"
            ctk.CTkLabel(
                title_frame,
                text=f"{estado_icon} Detalles de la Notificación #{notif['id']}",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack()
            
            # Scroll frame para el contenido
            scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
            scroll_frame.pack(fill="both", expand=True, padx=20)
            
            # Información de la notificación
            campos = [
                ("ID", "id", "🆔"),
                ("Tipo", "tipo", "🏷️"),
                ("Asunto", "asunto", "📧"),
                ("Contenido", "contenido", "💬"),
                ("Estado", "estado", "📊"),
                ("Fecha", "fecha", "📅"),
                ("Usuario", "usuario", "👤"),
                ("Prioridad", "prioridad", "⚡")
            ]
            
            for label, field, icon in campos:
                # Skip si el campo no existe
                if field not in notif:
                    continue
                
                # Frame para cada campo
                field_frame = ctk.CTkFrame(scroll_frame, fg_color="#F8F9FA", corner_radius=10)
                field_frame.pack(fill="x", pady=8)
                
                # Header del campo
                header_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
                header_frame.pack(fill="x", padx=15, pady=(10, 5))
                
                ctk.CTkLabel(
                    header_frame,
                    text=f"{icon} {label}",
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).pack(side="left")
                
                # Valor del campo
                valor = notif[field]
                
                # Formatear valores especiales
                if field == "estado":
                    color = "#4CAF50" if valor == "Leído" else "#FF9800"
                    badge_text = f"● {valor}"
                elif field == "prioridad":
                    priority_colors = {
                        "baja": "#4CAF50",
                        "normal": "#2196F3", 
                        "alta": "#FF9800",
                        "urgente": "#F44336"
                    }
                    color = priority_colors.get(valor, "#757575")
                    badge_text = f"● {valor.upper()}"
                else:
                    color = "#424242"
                    badge_text = str(valor)
                
                # Contenido largo en textbox
                if field == "contenido" and len(str(valor)) > 100:
                    content_text = ctk.CTkTextbox(
                        field_frame,
                        height=80,
                        fg_color="#FFFFFF",
                        border_width=1,
                        border_color="#E0E0E0",
                        font=("Quicksand", 11)
                    )
                    content_text.pack(fill="x", padx=15, pady=(0, 10))
                    content_text.insert("1.0", str(valor))
                    content_text.configure(state="disabled")
                else:
                    ctk.CTkLabel(
                        field_frame,
                        text=badge_text,
                        font=("Quicksand", 11),
                        text_color=color,
                        wraplength=500
                    ).pack(anchor="w", padx=15, pady=(0, 10))
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            action_frame.pack(fill="x", pady=20)
            
            # Botón eliminar
            ctk.CTkButton(
                action_frame,
                text="🗑️ Eliminar",
                command=lambda: self.eliminar(notif, parent),
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=120,
                height=40,
                font=("Quicksand", 12, "bold")
            ).pack(side="left", padx=10)
            
            # Botón refrescar
            ctk.CTkButton(
                action_frame,
                text="🔄 Refrescar",
                command=lambda: self.refrescar(parent),
                fg_color="#367832",
                hover_color="#2D5A27",
                width=120,
                height=40,
                font=("Quicksand", 12, "bold")
            ).pack(side="left", padx=5)
            
            # Botón cerrar
            ctk.CTkButton(
                action_frame,
                text="✖️ Cerrar",
                command=self.dialog.destroy,
                fg_color="#757575",
                hover_color="#616161",
                width=120,
                height=40,
                font=("Quicksand", 12, "bold")
            ).pack(side="right", padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
            self.dialog.destroy()
    
    def eliminar(self, notif, parent):
        try:
            # Confirmar eliminación
            if messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Está seguro de eliminar la notificación #{notif['id']}?\n\n"
                                 f"Asunto: {notif.get('asunto', 'Sin asunto')}\n"
                                 f"Esta acción no se puede deshacer."):
                
                # Mostrar indicador de carga en el parent
                parent.mostrar_loading(True)
                
                # Eliminar a través de la API
                result = NotificationsService.delete_notification(notif['id'])
                
                if result['success']:
                    messagebox.showinfo("Éxito", result['message'])
                    # Cerrar diálogo
                    self.dialog.destroy()
                    # Recargar datos en el parent
                    parent.cargar_datos_desde_api()
                else:
                    messagebox.showerror("Error", f"Error al eliminar: {result['error']}")
                    parent.mostrar_loading(False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
            parent.mostrar_loading(False)
    
    def refrescar(self, parent):
        try:
            # Cerrar diálogo actual
            self.dialog.destroy()
            # Recargar datos en el parent
            parent.cargar_datos_desde_api()
        except Exception as e:
            messagebox.showerror("Error", f"Error al refrescar: {str(e)}")

class EstadisticasDialog:
    def __init__(self, parent, notificaciones, usuarios):
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("📊 Estadísticas de Notificaciones")
            self.dialog.geometry("700x600")
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
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF", corner_radius=15)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(20, 30))
            
            ctk.CTkLabel(
                title_frame,
                text="📊 Estadísticas del Sistema de Notificaciones",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack()
            
            # Calcular estadísticas
            stats = self.calcular_estadisticas(notificaciones, usuarios)
            
            # Crear scroll frame
            scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
            scroll_frame.pack(fill="both", expand=True, padx=20)
            
            # Estadísticas generales
            self.crear_seccion_general(scroll_frame, stats)
            
            # Estadísticas por tipo
            self.crear_seccion_tipos(scroll_frame, stats)
            
            # Estadísticas por estado
            self.crear_seccion_estados(scroll_frame, stats)
            
            # Estadísticas de usuarios
            self.crear_seccion_usuarios(scroll_frame, stats)
            
            # Botón cerrar
            ctk.CTkButton(
                main_frame,
                text="✖️ Cerrar",
                command=self.dialog.destroy,
                fg_color="#757575",
                hover_color="#616161",
                width=120,
                height=40,
                font=("Quicksand", 12, "bold")
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar estadísticas: {str(e)}")
            self.dialog.destroy()
    
    def calcular_estadisticas(self, notificaciones, usuarios):
        """Calcular todas las estadísticas"""
        stats = {
            'total_notificaciones': len(notificaciones),
            'total_usuarios': len(usuarios),
            'no_leidas': len([n for n in notificaciones if n['estado'] != 'Leído']),
            'leidas': len([n for n in notificaciones if n['estado'] == 'Leído']),
            'por_tipo': {},
            'por_estado': {},
            'por_prioridad': {},
            'usuarios_activos': len([u for u in usuarios if u.get('estado', 'activo') == 'activo'])
        }
        
        # Estadísticas por tipo
        for notif in notificaciones:
            tipo = notif.get('tipo', 'desconocido')
            stats['por_tipo'][tipo] = stats['por_tipo'].get(tipo, 0) + 1
        
        # Estadísticas por estado
        for notif in notificaciones:
            estado = notif.get('estado', 'desconocido')
            stats['por_estado'][estado] = stats['por_estado'].get(estado, 0) + 1
        
        # Estadísticas por prioridad
        for notif in notificaciones:
            prioridad = notif.get('prioridad', 'normal')
            stats['por_prioridad'][prioridad] = stats['por_prioridad'].get(prioridad, 0) + 1
        
        return stats
    
    def crear_seccion_general(self, parent, stats):
        """Crear sección de estadísticas generales"""
        section_frame = ctk.CTkFrame(parent, fg_color="#F0F8FF", corner_radius=10)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="📈 Estadísticas Generales",
            font=("Quicksand", 16, "bold"),
            text_color="#2E6B5C"
        ).pack(pady=(15, 10))
        
        # Grid de estadísticas
        grid_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        stats_items = [
            ("📧", "Total Notificaciones", stats['total_notificaciones'], "#2196F3"),
            ("👥", "Total Usuarios", stats['total_usuarios'], "#4CAF50"),
            ("📬", "No Leídas", stats['no_leidas'], "#FF9800"),
            ("✅", "Leídas", stats['leidas'], "#4CAF50"),
        ]
        
        for i, (icon, label, value, color) in enumerate(stats_items):
            col = i % 2
            row = i // 2
            
            stat_frame = ctk.CTkFrame(grid_frame, fg_color="#FFFFFF", corner_radius=8)
            stat_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            
            grid_frame.columnconfigure(col, weight=1)
            
            ctk.CTkLabel(
                stat_frame,
                text=f"{icon} {label}",
                font=("Quicksand", 12, "bold"),
                text_color="#424242"
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                stat_frame,
                text=str(value),
                font=("Quicksand", 20, "bold"),
                text_color=color
            ).pack(pady=(0, 10))
    
    def crear_seccion_tipos(self, parent, stats):
        """Crear sección de estadísticas por tipo"""
        if not stats['por_tipo']:
            return
            
        section_frame = ctk.CTkFrame(parent, fg_color="#F0FFF0", corner_radius=10)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="🏷️ Notificaciones por Tipo",
            font=("Quicksand", 16, "bold"),
            text_color="#2E6B5C"
        ).pack(pady=(15, 10))
        
        for tipo, cantidad in stats['por_tipo'].items():
            item_frame = ctk.CTkFrame(section_frame, fg_color="#FFFFFF", corner_radius=5)
            item_frame.pack(fill="x", padx=20, pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text=tipo.capitalize(),
                font=("Quicksand", 12),
                text_color="#424242"
            ).pack(side="left", padx=15, pady=8)
            
            ctk.CTkLabel(
                item_frame,
                text=str(cantidad),
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(side="right", padx=15, pady=8)
        
        ctk.CTkFrame(section_frame, height=10, fg_color="transparent").pack()
    
    def crear_seccion_estados(self, parent, stats):
        """Crear sección de estadísticas por estado"""
        if not stats['por_estado']:
            return
            
        section_frame = ctk.CTkFrame(parent, fg_color="#FFF8E1", corner_radius=10)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="📊 Notificaciones por Estado",
            font=("Quicksand", 16, "bold"),
            text_color="#2E6B5C"
        ).pack(pady=(15, 10))
        
        estado_colors = {
            "Leído": "#4CAF50",
            "No leído": "#FF9800",
            "Pendiente": "#FF9800",
            "Enviado": "#2196F3"
        }
        
        for estado, cantidad in stats['por_estado'].items():
            item_frame = ctk.CTkFrame(section_frame, fg_color="#FFFFFF", corner_radius=5)
            item_frame.pack(fill="x", padx=20, pady=2)
            
            color = estado_colors.get(estado, "#757575")
            
            ctk.CTkLabel(
                item_frame,
                text=f"● {estado}",
                font=("Quicksand", 12),
                text_color=color
            ).pack(side="left", padx=15, pady=8)
            
            ctk.CTkLabel(
                item_frame,
                text=str(cantidad),
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(side="right", padx=15, pady=8)
        
        ctk.CTkFrame(section_frame, height=10, fg_color="transparent").pack()
    
    def crear_seccion_usuarios(self, parent, stats):
        """Crear sección de estadísticas de usuarios"""
        section_frame = ctk.CTkFrame(parent, fg_color="#F3E5F5", corner_radius=10)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="👥 Información de Usuarios",
            font=("Quicksand", 16, "bold"),
            text_color="#2E6B5C"
        ).pack(pady=(15, 10))
        
        user_stats = [
            ("Total de usuarios registrados", stats['total_usuarios']),
            ("Usuarios activos", stats['usuarios_activos']),
            ("Promedio notif. por usuario", 
             round(stats['total_notificaciones'] / max(stats['total_usuarios'], 1), 2))
        ]
        
        for label, value in user_stats:
            item_frame = ctk.CTkFrame(section_frame, fg_color="#FFFFFF", corner_radius=5)
            item_frame.pack(fill="x", padx=20, pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text=label,
                font=("Quicksand", 12),
                text_color="#424242"
            ).pack(side="left", padx=15, pady=8)
            
            ctk.CTkLabel(
                item_frame,
                text=str(value),
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(side="right", padx=15, pady=8)
        
        ctk.CTkFrame(section_frame, height=10, fg_color="transparent").pack()

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("800x600")
    GestionNotificaciones(app)
    app.mainloop()
