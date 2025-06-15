import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
import hashlib
from image_handler import ImageHandler

class GestionClientes(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Datos de ejemplo
            self.clientes = self.cargar_datos_ejemplo()
            
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
                placeholder_text="Buscar por nombre, email o teléfono...",
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
                values=["Todos", "Activo", "Inactivo"],
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
            
            # Botón nuevo cliente
            ctk.CTkButton(
                action_frame,
                text="➕ Nuevo Cliente",
                command=self.nuevo_cliente,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            
            # Botón resetear contraseña
            ctk.CTkButton(
                action_frame,
                text="🔑 Resetear Contraseña",
                command=self.resetear_password,
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
                "id_usuario", "nombre", "apellidos", "email", 
                "telefono", "estado", "fecha_creacion", "roles_id_rol"
            )
            
            self.tabla = ttk.Treeview(
                table_frame,
                columns=columns,
                show="headings",
                selectmode="browse",
                style="Treeview"
            )
            
            # Configurar columnas
            self.tabla.heading("id_usuario", text="ID")
            self.tabla.heading("nombre", text="Nombre")
            self.tabla.heading("apellidos", text="Apellidos")
            self.tabla.heading("email", text="Email")
            self.tabla.heading("telefono", text="Teléfono")
            self.tabla.heading("estado", text="Estado")
            self.tabla.heading("fecha_creacion", text="Fecha Creación")
            self.tabla.heading("roles_id_rol", text="Rol")
            
            # Configurar anchos
            self.tabla.column("id_usuario", width=50, anchor="center")
            self.tabla.column("nombre", width=150)
            self.tabla.column("apellidos", width=150)
            self.tabla.column("email", width=200)
            self.tabla.column("telefono", width=100, anchor="center")
            self.tabla.column("estado", width=100, anchor="center")
            self.tabla.column("fecha_creacion", width=150, anchor="center")
            self.tabla.column("roles_id_rol", width=100, anchor="center")
            
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
            self.tabla.bind("<Delete>", self.eliminar_cliente)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar: {str(e)}")
            
    def cargar_datos_ejemplo(self):
        return [
            {
                "id_usuario": 1,
                "nombre": "Juan",
                "apellidos": "Pérez García",
                "email": "juan@example.com",
                "password": self.hash_password("Temporal123*"),
                "telefono": "123456789",
                "fecha_creacion": "2024-03-15 10:00:00",
                "estado": "Activo",
                "roles_id_rol": 1
            },
            {
                "id_usuario": 2,
                "nombre": "María",
                "apellidos": "López Sánchez",
                "email": "maria@example.com",
                "password": self.hash_password("Temporal123*"),
                "telefono": "987654321",
                "fecha_creacion": "2024-03-15 11:00:00",
                "estado": "Inactivo",
                "roles_id_rol": 2
            }
        ]
        
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
        
    def cargar_datos(self):
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar datos
            for cliente in self.clientes:
                # Configurar tags para el estado
                tags = ("activo" if cliente["estado"] == "Activo" else "inactivo",)
                
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente["id_usuario"],
                        cliente["nombre"],
                        cliente["apellidos"],
                        cliente["email"],
                        cliente["telefono"],
                        cliente["estado"],
                        cliente["fecha_creacion"],
                        cliente["roles_id_rol"]
                    ),
                    tags=tags
                )
                
            # Configurar colores de estado
            self.tabla.tag_configure("activo", foreground="#2E7D32")
            self.tabla.tag_configure("inactivo", foreground="#C62828")
                
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
            for cliente in self.clientes:
                # Aplicar filtros
                if estado != "Todos" and cliente["estado"] != estado:
                    continue
                    
                if busqueda and not any(
                    busqueda in str(valor).lower()
                    for valor in [
                        cliente["nombre"],
                        cliente["apellidos"],
                        cliente["email"],
                        cliente["telefono"]
                    ]
                ):
                    continue
                    
                # Configurar tags para el estado
                tags = ("activo" if cliente["estado"] == "Activo" else "inactivo",)
                
                # Insertar fila
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente["id_usuario"],
                        cliente["nombre"],
                        cliente["apellidos"],
                        cliente["email"],
                        cliente["telefono"],
                        cliente["estado"],
                        cliente["fecha_creacion"],
                        cliente["roles_id_rol"]
                    ),
                    tags=tags
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar datos: {str(e)}")
            
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
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "estado": "Activo",
                    "roles_id_rol": 2  # Rol por defecto
                })
                
                self.cargar_datos()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Cliente agregado correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nuevo cliente: {str(e)}")
            
    def resetear_password(self):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
                return
                
            # Obtener cliente seleccionado
            item = self.tabla.item(seleccion[0])
            cliente_id = item["values"][0]
            cliente = next((c for c in self.clientes if c["id_usuario"] == cliente_id), None)
            
            if cliente:
                # Confirmar reseteo
                if messagebox.askyesno("Confirmar", f"¿Está seguro de resetear la contraseña de {cliente['nombre']}?"):
                    # Simular reseteo de contraseña
                    nueva_password = "Temporal123*"
                    cliente["password"] = self.hash_password(nueva_password)
                    messagebox.showinfo("Éxito", f"Contraseña reseteada correctamente a: {nueva_password}")
                    # Guardar cambios
                    self.guardar_datos()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al resetear contraseña: {str(e)}")
            
    def cambiar_estado(self, cliente):
        try:
            # Confirmar cambio de estado
            nuevo_estado = "Inactivo" if cliente["estado"] == "Activo" else "Activo"
            if messagebox.askyesno("Confirmar", f"¿Está seguro de cambiar el estado de {cliente['nombre']} a {nuevo_estado}?"):
                # Actualizar el estado directamente en el cliente existente
                cliente["estado"] = nuevo_estado
                # Actualizar la tabla sin recargar todos los datos
                for item in self.tabla.get_children():
                    if self.tabla.item(item)["values"][0] == cliente["id_usuario"]:
                        values = list(self.tabla.item(item)["values"])
                        values[5] = nuevo_estado  # Índice 5 es la columna de estado
                        self.tabla.item(item, values=values, tags=("activo" if nuevo_estado == "Activo" else "inactivo",))
                        break
                messagebox.showinfo("Éxito", "Estado actualizado correctamente")
                # Guardar cambios
                self.guardar_datos()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
            
    def eliminar_cliente(self, event=None):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
                return
                
            # Obtener cliente seleccionado
            item = self.tabla.item(seleccion[0])
            cliente_id = item["values"][0]
            cliente = next((c for c in self.clientes if c["id_usuario"] == cliente_id), None)
            
            if cliente:
                # Confirmar eliminación
                if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al cliente {cliente['nombre']}?"):
                    # Eliminar cliente
                    self.clientes = [c for c in self.clientes if c["id_usuario"] != cliente_id]
                    self.cargar_datos()
                    self.guardar_datos()
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    
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
            # Obtener item seleccionado
            item = self.tabla.selection()[0]
            cliente_id = self.tabla.item(item)["values"][0]
            cliente = next((c for c in self.clientes if c["id_usuario"] == cliente_id), None)
            
            if cliente:
                # Mostrar detalles
                DetallesClienteDialog(self, cliente)
                
                # Mostrar historial de pedidos
                self.mostrar_historial_pedidos(cliente)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")

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

class ClienteDialog:
    def __init__(self, parent, title, cliente=None):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("400x500")
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
            self.dialog.title(f"Detalles del Cliente {cliente['id_usuario']}")
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
                ("ID", "id_usuario"),
                ("Nombre", "nombre"),
                ("Apellidos", "apellidos"),
                ("Email", "email"),
                ("Teléfono", "telefono"),
                ("Estado", "estado"),
                ("Fecha Creación", "fecha_creacion"),
                ("Rol", "roles_id_rol")
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
                fg_color="#E64A19",
                hover_color="#BF360C",
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

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = GestionClientes(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error en la aplicación: {str(e)}")
