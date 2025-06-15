import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
from image_handler import ImageHandler

class GestionNotificaciones(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Datos de ejemplo
            self.notificaciones = self.cargar_datos_ejemplo()
            
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
            
            # Botón nueva notificación
            ctk.CTkButton(
                action_frame,
                text="➕ Nueva Notificación",
                command=self.nueva_notificacion,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150
            ).pack(side="left", padx=5)
            
            # Botón marcar como leída
            ctk.CTkButton(
                action_frame,
                text="✓ Marcar como Leída",
                command=self.marcar_leida,
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
            
            # Cargar datos
            self.cargar_datos()
            
            # Bind doble clic
            self.tabla.bind("<Double-1>", self.ver_detalles)
            
            # Bind tecla Enter
            self.tabla.bind("<Return>", self.ver_detalles)
            
            # Bind tecla Delete
            self.tabla.bind("<Delete>", self.eliminar_notificacion)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar: {str(e)}")
            
    def cargar_datos_ejemplo(self):
        return [
            {
                "id": 1,
                "tipo": "Campana",
                "contenido": "Nuevo pedido recibido #123",
                "estado": "Pendiente",
                "fecha": "2024-03-15 10:00:00",
                "usuario": "admin@example.com"
            },
            {
                "id": 2,
                "tipo": "Correo Electrónico",
                "contenido": "Confirmación de pago #456",
                "estado": "Enviado",
                "fecha": "2024-03-15 09:30:00",
                "usuario": "cliente@example.com"
            }
        ]
        
    def cargar_datos(self):
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar datos
            for notif in self.notificaciones:
                # Configurar tags para el estado
                tags = ("leida" if notif["estado"] == "Leído" else "no_leida",)
                
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
                
            # Configurar colores de estado
            self.tabla.tag_configure("leida", foreground="#757575")
            self.tabla.tag_configure("no_leida", foreground="#2E6B5C", font=("Quicksand", 10, "bold"))
                
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
            
    def nueva_notificacion(self):
        try:
            # Ventana de nueva notificación
            dialog = NotificacionDialog(self, "Nueva Notificación")
            if dialog.result:
                # Agregar nueva notificación
                nuevo_id = max([n["id"] for n in self.notificaciones], default=0) + 1
                
                self.notificaciones.append({
                    "id": nuevo_id,
                    **dialog.result,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "estado": "Pendiente"
                })
                
                self.cargar_datos()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Notificación creada correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nueva notificación: {str(e)}")
            
    def marcar_leida(self):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione una notificación")
                return
                
            # Obtener notificación seleccionada
            item = self.tabla.item(seleccion[0])
            notif_id = item["values"][0]
            notif = next((n for n in self.notificaciones if n["id"] == notif_id), None)
            
            if notif:
                # Marcar como leída
                notif["estado"] = "Leído"
                self.cargar_datos()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Notificación marcada como leída")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al marcar como leída: {str(e)}")
            
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
                # Eliminar notificación
                self.notificaciones = [n for n in self.notificaciones if n["id"] != notif_id]
                self.cargar_datos()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Notificación eliminada correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar notificación: {str(e)}")
            
    def guardar_datos(self):
        try:
            # Crear directorio si no existe
            os.makedirs("datos", exist_ok=True)
            
            # Guardar datos en archivo
            with open("datos/notificaciones.json", "w", encoding="utf-8") as f:
                json.dump(self.notificaciones, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
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
    def __init__(self, parent, title):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("600x600")
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
            title_frame.pack(fill="x", pady=(20, 30))
            
            ctk.CTkLabel(
                title_frame,
                text="📝 " + title,
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack()
            
            # Frame para el formulario
            form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            form_frame.pack(fill="both", expand=True, padx=40)
            
            # Campos del formulario
            campos = [
                ("Tipo", "tipo"),
                ("Contenido", "contenido"),
                ("Usuario", "usuario")
            ]
            
            self.entries = {}
            
            for i, (label, field) in enumerate(campos):
                # Frame para cada campo
                field_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
                field_frame.pack(fill="x", pady=(0, 20))
                
                # Label con icono
                icon = "🏷️" if field == "tipo" else "💬" if field == "contenido" else "👤"
                ctk.CTkLabel(
                    field_frame,
                    text=f"{icon} {label}",
                    font=("Quicksand", 14, "bold"),
                    text_color="#2E6B5C"
                ).pack(anchor="w", pady=(0, 5))
                
                if field == "tipo":
                    # Combo box para tipo
                    self.tipo_var = ctk.StringVar(value="Campana")
                    tipo_menu = ctk.CTkOptionMenu(
                        field_frame,
                        values=["Campana", "Correo Electrónico"],
                        variable=self.tipo_var,
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
                    tipo_menu.pack(fill="x")
                    self.entries[field] = self.tipo_var
                elif field == "contenido":
                    # Text box para contenido
                    text_box = ctk.CTkTextbox(
                        field_frame,
                        width=400,
                        height=120,
                        border_width=0,
                        fg_color="#F5F5F5",
                        font=("Quicksand", 12)
                    )
                    text_box.pack(fill="x")
                    self.entries[field] = text_box
                else:
                    # Entry para usuario
                    entry = ctk.CTkEntry(
                        field_frame,
                        width=400,
                        height=40,
                        placeholder_text="Ingrese email del usuario...",
                        border_width=0,
                        fg_color="#F5F5F5",
                        font=("Quicksand", 12)
                    )
                    entry.pack(fill="x")
                    self.entries[field] = entry
            
            # Frame para botones con estilo mejorado
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(side="bottom", fill="x", pady=(30, 20))
            
            # Botón Guardar con icono y estilo mejorado
            guardar_btn = ctk.CTkButton(
                button_frame,
                text="💾 Guardar Notificación",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=200,
                height=45,
                font=("Quicksand", 14, "bold"),
                corner_radius=10
            )
            guardar_btn.pack(side="left", padx=10)
            
            # Botón Cancelar con icono y estilo mejorado
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
            
    def guardar(self):
        try:
            # Validar campos
            datos = {}
            for field, entry in self.entries.items():
                if isinstance(entry, ctk.StringVar):
                    valor = entry.get()
                elif isinstance(entry, ctk.CTkTextbox):
                    valor = entry.get("1.0", "end-1c").strip()
                else:
                    valor = entry.get().strip()
                    
                if not valor:
                    messagebox.showwarning("Advertencia", f"El campo {field} es requerido")
                    return
                    
                datos[field] = valor
                
            # Guardar resultado
            self.result = datos
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class DetallesNotificacionDialog:
    def __init__(self, parent, notif):
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(f"Detalles de la Notificación {notif['id']}")
            self.dialog.geometry("500x400")
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
                text="Detalles de la Notificación",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Información de la notificación
            campos = [
                ("ID", "id"),
                ("Tipo", "tipo"),
                ("Contenido", "contenido"),
                ("Estado", "estado"),
                ("Fecha", "fecha"),
                ("Usuario", "usuario")
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
                
                valor = notif[field]
                if field == "estado":
                    valor = "Leído" if valor else "Pendiente"
                    
                ctk.CTkLabel(
                    frame,
                    text=str(valor),
                    font=("Quicksand", 12),
                    text_color="#424242"
                ).pack(side="left", padx=10)
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            action_frame.pack(fill="x", pady=20)
            
            # Botón marcar como leída
            if notif["estado"] == "Pendiente":
                ctk.CTkButton(
                    action_frame,
                    text="Marcar como Leída",
                    command=lambda: self.marcar_leida(notif),
                    fg_color="#2E6B5C",
                    hover_color="#1D4A3C",
                    width=150
                ).pack(side="left", padx=5)
            
            # Botón eliminar
            ctk.CTkButton(
                action_frame,
                text="Eliminar",
                command=lambda: self.eliminar(notif),
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=100
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
            
    def marcar_leida(self, notif):
        try:
            # Obtener referencia al frame padre
            parent = self.dialog.master
            
            # Marcar como leída
            notif["estado"] = "Leído"
            
            # Actualizar datos
            parent.cargar_datos()
            parent.guardar_datos()
            
            # Cerrar diálogo
            self.dialog.destroy()
            
            # Mostrar mensaje
            messagebox.showinfo("Éxito", "Notificación marcada como leída")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al marcar como leída: {str(e)}")
            
    def eliminar(self, notif):
        try:
            # Obtener referencia al frame padre
            parent = self.dialog.master
            
            # Confirmar eliminación
            if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la notificación #{notif['id']}?"):
                # Eliminar notificación
                parent.notificaciones = [n for n in parent.notificaciones if n["id"] != notif["id"]]
                
                # Actualizar datos
                parent.cargar_datos()
                parent.guardar_datos()
                
                # Cerrar diálogo
                self.dialog.destroy()
                
                # Mostrar mensaje
                messagebox.showinfo("Éxito", "Notificación eliminada correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("800x600")
    GestionNotificaciones(app)
    app.mainloop()
