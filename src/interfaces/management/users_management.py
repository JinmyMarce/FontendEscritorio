import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
from PIL import Image, ImageTk
from src.shared.image_handler import ImageHandler
from src.core.config import UI_CONFIG
from src.interfaces.reports.user_report import ReporteUsuario

class GestionUsuarios(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Frame superior
            top_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            top_frame.pack(fill="x", pady=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(top_frame, fg_color="#FFFFFF")
            title_frame.pack(side="left", padx=20, pady=20)
            
            try:
                # Cargar y redimensionar icono
                icon = Image.open(os.path.join("..", "..", "..", "assets", "images", "usuarios.png"))
                icon = icon.resize((32, 32))
                self.icon_image = ImageTk.PhotoImage(icon)
                ctk.CTkLabel(
                    title_frame,
                    image=self.icon_image,
                    text=""
                ).pack(side="left", padx=(0, 10))
            except:
                pass
                
            ctk.CTkLabel(
                title_frame,
                text="Gestión de Usuarios",
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
                placeholder_text="Buscar por nombre o email...",
                border_width=0,
                fg_color="#F5F5F5"
            )
            search_entry.pack(side="left", padx=5, pady=10)
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(search_frame, fg_color="#FFFFFF")
            action_frame.pack(side="right", padx=15, pady=10)
            
            # Botón de nuevo usuario
            new_user_button = ctk.CTkButton(
                action_frame,
                text="➕ Nuevo Usuario",
                command=self.mostrar_dialogo_usuario,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150,
                height=35,
                corner_radius=8,
                font=("Quicksand", 12)
            )
            new_user_button.pack(side="left", padx=5)
            
            # Botón de reporte de usuario
            report_button = ctk.CTkButton(
                action_frame,
                text="📊 Reporte de Usuario",
                command=self.mostrar_reporte_usuario,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150,
                height=35,
                corner_radius=8,
                font=("Quicksand", 12)
            )
            report_button.pack(side="left", padx=5)
            
            # Tabla de usuarios
            self.tabla_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            self.tabla_frame.pack(fill="both", expand=True)
            
            # Crear tabla
            self.tabla = ttk.Treeview(
                self.tabla_frame,
                columns=("id", "nombre", "apellidos", "email", "telefono", "rol", "estado"),
                show="headings",
                style="Custom.Treeview"
            )
            
            # Configurar columnas
            self.tabla.heading("id", text="ID")
            self.tabla.heading("nombre", text="Nombre")
            self.tabla.heading("apellidos", text="Apellidos")
            self.tabla.heading("email", text="Email")
            self.tabla.heading("telefono", text="Teléfono")
            self.tabla.heading("rol", text="Rol")
            self.tabla.heading("estado", text="Estado")
            
            self.tabla.column("id", width=50)
            self.tabla.column("nombre", width=150)
            self.tabla.column("apellidos", width=150)
            self.tabla.column("email", width=200)
            self.tabla.column("telefono", width=100)
            self.tabla.column("rol", width=100)
            self.tabla.column("estado", width=100)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(self.tabla_frame, orient="vertical", command=self.tabla.yview)
            self.tabla.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar tabla y scrollbar
            self.tabla.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Cargar datos
            self.cargar_usuarios()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar la gestión de usuarios: {str(e)}")
            
    def cargar_usuarios(self):
        try:
            # Aquí se cargarían los datos desde la base de datos
            # Por ahora usamos datos de ejemplo
            usuarios = [
                {
                    "id": 1,
                    "nombre": "Juan",
                    "apellidos": "Pérez",
                    "email": "juan@example.com",
                    "telefono": "123456789",
                    "rol": "Admin",
                    "estado": "Activo"
                },
                # Agregar más usuarios de ejemplo aquí
            ]
            
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Insertar datos
            for usuario in usuarios:
                self.tabla.insert("", "end", values=(
                    usuario["id"],
                    usuario["nombre"],
                    usuario["apellidos"],
                    usuario["email"],
                    usuario["telefono"],
                    usuario["rol"],
                    usuario["estado"]
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {str(e)}")
            
    def filtrar_tabla(self, *args):
        try:
            busqueda = self.search_var.get().lower()
            
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Filtrar y mostrar resultados
            for item in self.tabla.get_children():
                valores = self.tabla.item(item)["values"]
                if any(busqueda in str(valor).lower() for valor in valores):
                    self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar tabla: {str(e)}")
            
    def mostrar_dialogo_usuario(self, usuario=None):
        try:
            UsuarioDialog(self, "Nuevo Usuario" if not usuario else "Editar Usuario", usuario)
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar diálogo de usuario: {str(e)}")
            
    def mostrar_reporte_usuario(self):
        try:
            # Crear ventana de diálogo
            dialog = ctk.CTkToplevel(self)
            dialog.title("Reporte de Usuario")
            dialog.geometry("800x600")
            dialog.resizable(True, True)
            
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
            
            # Crear frame del reporte
            reporte = ReporteUsuario(dialog)
            reporte.pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar reporte de usuario: {str(e)}")

class UsuarioDialog:
    def __init__(self, parent, title, usuario=None):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("500x600")
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
            main_frame.pack(fill="both", expand=True, padx=30, pady=30)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text=title,
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 30))
            
            # Campos del formulario
            campos = [
                ("Nombre", "nombre"),
                ("Apellidos", "apellidos"),
                ("Email", "email"),
                ("Teléfono", "telefono"),
                ("Contraseña", "password"),
                ("Rol", "rol")
            ]
            
            self.entries = {}
            
            for i, (label, field) in enumerate(campos):
                # Frame para cada campo
                field_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
                field_frame.pack(fill="x", pady=(0, 20))
                
                # Label
                ctk.CTkLabel(
                    field_frame,
                    text=label,
                    font=("Quicksand", 14, "bold"),
                    text_color="#2E6B5C"
                ).pack(anchor="w", pady=(0, 5))
                
                if field == "rol":
                    # Combo box para rol
                    self.rol_var = ctk.StringVar(value="Usuario")
                    rol_menu = ctk.CTkOptionMenu(
                        field_frame,
                        values=["Admin", "Usuario", "Vendedor"],
                        variable=self.rol_var,
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
                    rol_menu.pack(fill="x")
                    self.entries[field] = self.rol_var
                else:
                    # Entry para otros campos
                    entry = ctk.CTkEntry(
                        field_frame,
                        width=400,
                        height=40,
                        placeholder_text=f"Ingrese {label.lower()}...",
                        border_width=0,
                        fg_color="#F5F5F5",
                        font=("Quicksand", 12)
                    )
                    entry.pack(fill="x")
                    self.entries[field] = entry
                    
                    # Si es edición, llenar campos
                    if usuario:
                        entry.insert(0, str(usuario[field]))
                        
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
            button_frame.pack(fill="x", pady=30)
            
            # Botón cancelar
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.dialog.destroy,
                fg_color="#E0E0E0",
                text_color="#2E6B5C",
                hover_color="#D0D0D0",
                width=150,
                height=40,
                corner_radius=8,
                font=("Quicksand", 12)
            ).pack(side="left", padx=5)
            
            # Botón guardar
            ctk.CTkButton(
                button_frame,
                text="Guardar",
                command=self.guardar_usuario,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150,
                height=40,
                corner_radius=8,
                font=("Quicksand", 12)
            ).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo de usuario: {str(e)}")
            
    def guardar_usuario(self):
        try:
            # Obtener valores
            datos = {
                field: entry.get() if isinstance(entry, ctk.CTkEntry) else entry.get()
                for field, entry in self.entries.items()
            }
            
            # Validar datos
            if not all(datos.values()):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
                
            # Aquí se guardaría en la base de datos
            # Por ahora solo cerramos el diálogo
            self.dialog.destroy()
            messagebox.showinfo("Éxito", "Usuario guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar usuario: {str(e)}") 